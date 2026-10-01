"""Problem 10.7 -- Antitrust split: two companies as similar as possible.

The branches must be divided into two groups minimising, over the worst product,
the revenue difference between the two groups. It is technique 3.6 (min-max)
applied to an absolute value (3.7): two inequalities per product around the same
variable z.

The point of the problem is that the linear relaxation is worth zero: half a
branch to each company balances every product. The useful lower bound does not
come from the dual but from a combinatorial argument, product by product.
"""
import itertools

import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi, valuta)
from stile import ARANCIO, BLU, TEAL, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.7 Antitrust: splitting the branches minimising the worst imbalance")
v2 = [[3, 3, 2],      # revenue of branch i on product j (millions)
      [6, 8, 5],
      [3, 4, 4],
      [2, 7, 9]]
s2, r2 = len(v2), len(v2[0])
salva_dati(pd.DataFrame(v2, columns=[f"product_{j + 1}" for j in R(r2)],
                        index=[f"branch_{i + 1}" for i in R(s2)]).reset_index(),
           "fam10_7_dati")


def modello_2(v):
    """A single family of binaries: x_i = 1 if branch i goes to company A.

    The source uses two families x_i and y_i with x_i + y_i = 1. They are
    equivalent: y_i = 1 - x_i. Here we keep the aggregated form, which is more
    compact; the disaggregated one follows by substitution, and it is the one
    needed when the companies become more than two.
    """
    s, r = len(v), len(v[0])
    m = nuovo_modello("antitrust")
    x = m.addVars(s, vtype=GRB.BINARY, name="x")
    z = m.addVar(lb=-GRB.INFINITY, name="z")
    m.setObjective(z, GRB.MINIMIZE)
    for j in R(r):
        tot = sum(v[i][j] for i in R(s))
        # difference between A and B on product j: 2 * sum_i v_ij x_i - tot
        m.addConstr(z - 2 * gp.quicksum(v[i][j] * x[i] for i in R(s)) + tot >= 0,
                    name=f"above[{j}]")
        m.addConstr(z + 2 * gp.quicksum(v[i][j] * x[i] for i in R(s)) - tot >= 0,
                    name=f"below[{j}]")
    return m, x, z


def duale_2(v):
    """max sum_j T_j (mu_j - lam_j)  with  sum_j (lam_j + mu_j) = 1  (column of z, free)
       and  2 sum_j v_ij (mu_j - lam_j) <= 0 for every branch i (column of x_i >= 0)."""
    s, r = len(v), len(v[0])
    dl = nuovo_modello("dual_antitrust")
    lam = dl.addVars(r, name="lam")     # "above" constraints
    mu = dl.addVars(r, name="mu")       # "below" constraints
    tot = [sum(v[i][j] for i in R(s)) for j in R(r)]
    dl.setObjective(gp.quicksum(tot[j] * (mu[j] - lam[j]) for j in R(r)), GRB.MAXIMIZE)
    dl.addConstr(gp.quicksum(lam[j] + mu[j] for j in R(r)) == 1, name="rcz")
    dl.addConstrs((2 * gp.quicksum(v[i][j] * (mu[j] - lam[j]) for j in R(r)) <= 0
                   for i in R(s)), name="rcx")
    return dl


m2, x2, z2v = modello_2(v2)
salva_modello(m2, "fam10_7_primale")
tot2 = [sum(v2[i][j] for i in R(s2)) for j in R(r2)]
print("  Total revenue per product: "
      + ", ".join(f"product {j + 1} = {tot2[j]}" for j in R(r2)))

# ---------- 2. THE LP RELAXATION ----------
zlp2, zlp2r, _ = rilassamenti(m2)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
dl2 = duale_2(v2)
salva_modello(dl2, "fam10_7_duale")
mano = {"lam[0]": 0.5, "mu[0]": 0.5}      # lam_1 = mu_1 = 1/2, everything else zero
lb_lp, viol = valuta(dl2, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: lam_1 = mu_1 = 1/2 and everything else zero -> value "
      f"{frazione(lb_lp)}.")
print("  Every feasible dual solution here is worth at most zero: the objective contains the")
print("  difference mu_j - lam_j, and the constraints on the columns x_i force it to be")
print("  non-positive on every branch.")
dualita_forte(dl2, zlp2)

meta = {f"x[{i}]": 0.5 for i in R(s2)} | {"z": 0.0}
val_meta, viol_meta = valuta(m2, meta)
assert viol_meta <= 1e-9 and abs(val_meta) <= 1e-9
print(f"  And indeed z(LP) = {frazione(zlp2)}: it is enough to put half of every branch in")
print("  each company (x_i = 1/2, z = 0) and every product is balanced exactly. It is")
print("  feasible for the relaxation and useless for the real problem: branches are indivisible.")
assert abs(zlp2) <= 1e-9

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# constructive heuristic: the branches in decreasing order of total revenue, each one to the company
# that currently has the smaller total
def euristica(v):
    s, r = len(v), len(v[0])
    tot_i = [sum(v[i]) for i in R(s)]
    gruppo = {}
    somme = [0, 0]
    passi = [f"total revenue of the branches: "
             + ", ".join(f"{i + 1} -> {tot_i[i]}" for i in R(s))]
    for i in sorted(R(s), key=lambda i: (-tot_i[i], i)):
        k = 0 if somme[0] <= somme[1] else 1
        gruppo[i] = k
        somme[k] += tot_i[i]
        passi.append(f"branch {i + 1} ({tot_i[i]}) to company "
                     f"{'AB'[k]}; now A = {somme[0]}, B = {somme[1]}")
    diff = [abs(sum(v[i][j] for i in R(s) if gruppo[i] == 0)
                - sum(v[i][j] for i in R(s) if gruppo[i] == 1)) for j in R(r)]
    passi.append("differences per product: "
                 + ", ".join(f"product {j + 1} -> {diff[j]}" for j in R(r)))
    return gruppo, max(diff), passi


gruppo, ub2, passi = euristica(v2)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
sol_eur = {f"x[{i}]": 1 - gruppo[i] for i in R(s2)} | {"z": ub2}
assert ammissibile(m2, sol_eur), sol_eur
print("  Company A = " + str([i + 1 for i in R(s2) if gruppo[i] == 0])
      + ", company B = " + str([i + 1 for i in R(s2) if gruppo[i] == 1])
      + f"   ub = {frazione(ub2)}")

# ---------- 5. A COMBINATORIAL BOUND, PRODUCT BY PRODUCT ----------
intestazione("10.7 The lower bound comes from a combinatorial argument")
# for every product, the smallest imbalance obtainable looking at that product alone
def minimo_squilibrio(colonna, tot):
    s = len(colonna)
    return min(abs(2 * sum(colonna[i] for i in sotto) - tot)
               for k in R(s + 1) for sotto in itertools.combinations(R(s), k))


gj = [minimo_squilibrio([v2[i][j] for i in R(s2)], tot2[j]) for j in R(r2)]
for j in R(r2):
    print(f"  Product {j + 1}: total {tot2[j]}, best imbalance achievable looking at this")
    print(f"    product alone = {gj[j]}")
lb2 = max(gj)
print(f"  Every partition must respect all the products at once, so z >= max_j g_j = "
      f"{frazione(lb2)}.")
print("  It is a valid bound that the linear relaxation cannot see: it comes from")
print("  integrality, not from the constraints.")
salva_dati(pd.DataFrame({"product": R(1, r2 + 1), "total": tot2, "g_j": gj}),
           "fam10_7_argomento")

# ---------- 6. OPTIMUM OF THE MILP ----------
z2 = risolvi(m2)
A = [i + 1 for i in R(s2) if x2[i].X > 0.5]
B = [i + 1 for i in R(s2) if x2[i].X <= 0.5]
diff_ott = [abs(sum(v2[i - 1][j] for i in A) - sum(v2[i - 1][j] for i in B)) for j in R(r2)]
print(f"  Optimal solution: company A = {A}, company B = {B}")
print("  differences per product: "
      + ", ".join(f"product {j + 1} -> {diff_ott[j]}" for j in R(r2))
      + f"   z = {frazione(z2)}")
riga = registra_bound("2 antitrust", ub2, lb2, zlp2, zlp2r, z2)
salva_dati(pd.DataFrame([riga]), "fam10_7_bound")
assert lb2 <= z2 <= ub2 + 1e-9
print(f"  Sandwich: {frazione(lb2)} <= z(MILP) = {frazione(z2)} <= {frazione(ub2)}. Careful:")
print(f"  here lb is not the value of the dual ({frazione(lb_lp)}) but the combinatorial bound.")

# ---------- 7. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: branches 1 and 2 must stay in the same company
m, x, zz = modello_2(v2)
m.addConstr(x[0] - x[1] == 0, name="together")
varianti["2a"] = variante("2a. Branches 1 and 2 must stay together (x1 = x2)", m)
# 2b: minimise the sum of the differences instead of the worst one
m = nuovo_modello("antitrust_sum")
x = m.addVars(s2, vtype=GRB.BINARY, name="x")
zj = m.addVars(r2, name="z")
m.setObjective(zj.sum(), GRB.MINIMIZE)
for j in R(r2):
    m.addConstr(zj[j] - 2 * gp.quicksum(v2[i][j] * x[i] for i in R(s2)) + tot2[j] >= 0,
                name=f"above[{j}]")
    m.addConstr(zj[j] + 2 * gp.quicksum(v2[i][j] * x[i] for i in R(s2)) - tot2[j] >= 0,
                name=f"below[{j}]")
varianti["2b"] = variante("2b. Minimise the sum of the differences (min-sum, not min-max)", m)
A_somma = sorted(min(([i + 1 for i in R(s2) if x[i].X > 0.5],
                      [i + 1 for i in R(s2) if x[i].X <= 0.5])))
A_max = sorted(min((A, B)))
print(f"       min-sum partition: {A_somma} against the rest; min-max partition: {A_max}.")
print("       The two objectives are not comparable in value: the function changes, not")
print("       the feasible set.")
assert A_somma == A_max, (A_somma, A_max)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "fam10_7_varianti")

# ---------- 8. THE SANDWICH ON THE VARIANT 2a ----------
intestazione("10.7a The sandwich on the variant: branches 1 and 2 stay together")


def modello_2a(v):
    mm, xx, zz = modello_2(v)
    mm.addConstr(xx[0] - xx[1] == 0, name="insieme")
    return mm, xx, zz


def duale_2a(v):
    """To the dual of 10.7 one adds a free sigma for the equality x_1 - x_2 = 0: it
    appears in the column of branch 1 with a plus sign and in that of branch 2
    with a minus sign. The right-hand side is zero: the objective does not change."""
    ss, rr = len(v), len(v[0])
    dl = nuovo_modello("duale_antitrust_2a")
    lam = dl.addVars(rr, name="lam")
    mu = dl.addVars(rr, name="mu")
    sg = dl.addVar(lb=-GRB.INFINITY, name="sigma")
    tot = [sum(v[i][j] for i in R(ss)) for j in R(rr)]
    dl.setObjective(gp.quicksum(tot[j] * (mu[j] - lam[j]) for j in R(rr)), GRB.MAXIMIZE)
    dl.addConstr(gp.quicksum(lam[j] + mu[j] for j in R(rr)) == 1, name="rcz")
    for i in R(ss):
        extra = sg if i == 0 else (-sg if i == 1 else 0)
        dl.addConstr(2 * gp.quicksum(v[i][j] * (mu[j] - lam[j]) for j in R(rr)) + extra <= 0,
                     name=f"rcx[{i}]")
    return dl


m2a, x2a, z2a = modello_2a(v2)
salva_modello(m2a, "fam10_7a_primale")

# -- feasible heuristic: the branches are few, every partition is tried --
print("Constructive heuristic: the branches are few, so the partitions keeping 1 and 2")
print("together are enumerated and the one with the lowest maximum imbalance is kept. With")
print("a constraint tying two branches, the greedy rule of the base problem no longer does:")
print("it would put the two branches in different groups.")
migliore_2a = None
for k in R(s2 + 1):
    for sotto in itertools.combinations(R(s2), k):
        if (0 in sotto) != (1 in sotto):
            continue
        squilibrio = max(abs(2 * sum(v2[i][j] for i in sotto) - tot2[j]) for j in R(r2))
        if migliore_2a is None or squilibrio < migliore_2a[0]:
            migliore_2a = (squilibrio, sotto)
ub2a, gruppo_A = migliore_2a
print(f"  best partition: company A = branches {[i + 1 for i in gruppo_A]}, "
      f"B = {[i + 1 for i in R(s2) if i not in gruppo_A]}")
sol_2a = {f"x[{i}]": (1 if i in gruppo_A else 0) for i in R(s2)} | {"z": ub2a}
assert ammissibile(m2a, sol_2a), "the heuristic solution of the variant must be feasible"
print(f"  ub = {frazione(ub2a)}")

# -- dual certificate: the relaxation stays silent, the bound comes from integrality --
dl2a = duale_2a(v2)
salva_modello(dl2a, "fam10_7a_duale")
mano_2a = {"lam[0]": 0.5, "mu[0]": 0.5, "sigma": 0.0}
lb_lp_2a, viol_2a = valuta(dl2a, mano_2a)
assert viol_2a <= 1e-9, viol_2a
print("Dual solution by hand: lam_1 = mu_1 = 1/2, sigma = 0 and everything else zero. As in")
print("  the base problem the value is zero, and for the same reason: the objective contains")
print("  the difference mu_j - lam_j, which the column constraints force to be")
print("  non-positive. The new sigma does not change it, because its right-hand side is zero.")
print(f"  ->  relaxation: {frazione(lb_lp_2a)}")
zlp2a, zlp2ar, _ = due_rilassamenti(m2a, dl2a)
# the real bound comes from the same combinatorial argument as the base problem,
# restricted to the partitions that keep branches 1 and 2 together
def minimo_squilibrio_legato(colonna, tot):
    ss = len(colonna)
    return min(abs(2 * sum(colonna[i] for i in sotto) - tot)
               for k in R(ss + 1) for sotto in itertools.combinations(R(ss), k)
               if (0 in sotto) == (1 in sotto))


gj_2a = [minimo_squilibrio_legato([v2[i][j] for i in R(s2)], tot2[j]) for j in R(r2)]
lb2a = max(gj_2a)
for j in R(r2):
    print(f"  product {j + 1}: with 1 and 2 tied the best possible imbalance is {gj_2a[j]}")
print(f"  Every feasible partition must respect them all: z >= max_j g_j = {frazione(lb2a)}")
print("  (with the branches free it was " + frazione(lb2) + ": tying two branches raises the bound)")
z2a_val = risolvi(m2a)
riga_2a = registra_bound("2a branches 1 and 2 together", ub2a, lb2a, zlp2a, zlp2ar, z2a_val,
                         certificato="smallest imbalance with branches 1 and 2 tied")
salva_dati(pd.DataFrame([riga_2a]), "fam10_7a_bound")
assert lb2a <= z2a_val <= ub2a + 1e-9

# ---------- 9. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
larg = 0.35
idx = list(R(r2))
ax.bar([j - larg / 2 for j in idx], [sum(v2[i - 1][j] for i in A) for j in idx], larg,
       color=TEAL, label="company A")
ax.bar([j + larg / 2 for j in idx], [sum(v2[i - 1][j] for i in B) for j in idx], larg,
       color=BLU, label="company B")
for j in idx:
    ax.annotate(f"|diff| = {diff_ott[j]}", (j, max(tot2) / 2 + 1), ha="center", fontsize=8,
                color=ARANCIO)
ax.set_xticks(idx)
ax.set_xticklabels([f"product {j + 1}" for j in idx])
ax.set_ylabel("revenue (millions)")
ax.set_title(f"10.7: optimal partition, worst imbalance {frazione(z2)}")
ax.legend(fontsize=8)
salva_figura(fig, "cap10_antitrust_ottimo")
print("Done.")
