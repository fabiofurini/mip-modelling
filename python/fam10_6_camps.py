"""Problem 10.6 -- Summer camps: children of several nationalities in several camps.

Counting variables (not binary), a capacity per camp and two composition
constraints: in every camp the girls must not be fewer than the boys, and
nationality c must not be fewer than any other. The second is written once only
because there are two nationalities; with s > 2 one needs s - 1 inequalities.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.6 Summer camps: accepting the largest number of children")
f1 = [8, 10]        # girls available per nationality
g1 = [4, 12]        # boys available per nationality
d1 = [15, 8]        # capacity of the camps
c1 = 0              # nationality that must be the majority (index 0 = nationality 1)
s1, r1 = len(f1), len(d1)
salva_dati(pd.DataFrame({"nationality": R(1, s1 + 1), "girls": f1, "boys": g1}),
           "fam10_6_dati")
salva_dati(pd.DataFrame({"camp": R(1, r1 + 1), "capacity": d1}), "fam10_6_capacita")


def modello_1(f, g, d, c):
    s, r = len(f), len(d)
    m = nuovo_modello("camps")
    x = m.addVars(s, r, vtype=GRB.INTEGER, name="x")    # girls of nationality i in camp j
    y = m.addVars(s, r, vtype=GRB.INTEGER, name="y")    # boys of nationality i in camp j
    m.setObjective(gp.quicksum(x[i, j] + y[i, j] for i in R(s) for j in R(r)), GRB.MAXIMIZE)
    m.addConstrs((x.sum(i, "*") <= f[i] for i in R(s)), name="girls")
    m.addConstrs((y.sum(i, "*") <= g[i] for i in R(s)), name="boys")
    m.addConstrs((gp.quicksum(x[i, j] + y[i, j] for i in R(s)) <= d[j] for j in R(r)),
                 name="capacity")
    m.addConstrs((gp.quicksum(x[i, j] - y[i, j] for i in R(s)) >= 0 for j in R(r)),
                 name="balance")
    m.addConstrs((x[c, j] + y[c, j]
                  - gp.quicksum(x[i, j] + y[i, j] for i in R(s) if i != c) >= 0 for j in R(r)),
                 name="majority")
    return m, x, y


def duale_1(f, g, d, c):
    """min sum_i f_i alpha_i + sum_i g_i beta_i + sum_j d_j gamma_j

    with alpha, beta, gamma >= 0 for the three <= constraints, and delta_j, eps_j >= 0
    for the two composition constraints (written as >= 0, so they enter the dual
    constraints with a minus sign). The sign multiplying eps_j depends on i: it is -1
    for the majority nationality c and +1 for all the others.
    """
    s, r = len(f), len(d)
    dl = nuovo_modello("dual_camps")
    alpha = dl.addVars(s, name="alpha")
    beta = dl.addVars(s, name="beta")
    gamma = dl.addVars(r, name="gamma")
    delta = dl.addVars(r, name="delta")
    eps = dl.addVars(r, name="eps")
    dl.setObjective(gp.quicksum(f[i] * alpha[i] for i in R(s))
                    + gp.quicksum(g[i] * beta[i] for i in R(s))
                    + gp.quicksum(d[j] * gamma[j] for j in R(r)), GRB.MINIMIZE)
    for i in R(s):
        segno = -1 if i == c else 1
        for j in R(r):
            dl.addConstr(alpha[i] + gamma[j] - delta[j] + segno * eps[j] >= 1,
                         name=f"rcx[{i},{j}]")
            dl.addConstr(beta[i] + gamma[j] + delta[j] + segno * eps[j] >= 1,
                         name=f"rcy[{i},{j}]")
    return dl


m1, x1, y1 = modello_1(f1, g1, d1, c1)
salva_modello(m1, "fam10_6_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp1, zlp1r, _ = rilassamenti(m1)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
dl1 = duale_1(f1, g1, d1, c1)
salva_modello(dl1, "fam10_6_duale")
# recipe: alpha = beta = delta = eps = 0 and gamma_j = 1, that is only the capacity is
# priced: every accepted child takes one place, so no more than sum_j d_j can be accepted
mano = {f"gamma[{j}]": 1.0 for j in R(r1)}
ub1, viol = valuta(dl1, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: alpha = beta = delta = eps = 0 and gamma_j = 1 (every child takes")
print("  one place). All the dual constraints become gamma_j >= 1 and are satisfied:")
print(f"  ub = sum_j d_j = {' + '.join(map(str, d1))} = {frazione(ub1)}")
dualita_forte(dl1, zlp1)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# constructive heuristic camp by camp: the current camp is filled taking first the majority
# nationality (girls and boys) and then the others, never violating capacity,
# balance and majority.
def euristica(f, g, d, c):
    s, r = len(f), len(d)
    x = {(i, j): 0 for i in R(s) for j in R(r)}
    y = {(i, j): 0 for i in R(s) for j in R(r)}
    rf, rg = list(f), list(g)
    passi = []
    ordine = [c] + [i for i in R(s) if i != c]
    for j in R(r):
        for i in ordine:
            for quale, res, var in (("girls", rf, x), ("boys", rg, y)):
                while res[i] > 0:
                    var[i, j] += 1
                    tot = sum(x[k, j] + y[k, j] for k in R(s))
                    par = sum(x[k, j] - y[k, j] for k in R(s))
                    magg = (x[c, j] + y[c, j]
                            - sum(x[k, j] + y[k, j] for k in R(s) if k != c))
                    if tot > d[j] or par < 0 or magg < 0:
                        var[i, j] -= 1
                        break
                    res[i] -= 1
        occupati = sum(x[k, j] + y[k, j] for k in R(s))
        passi.append(f"camp {j + 1} (capacity {d[j]}): "
                     + ", ".join(f"nat. {i + 1} -> {x[i, j]} girls and {y[i, j]} boys"
                                 for i in R(s))
                     + f"; {occupati} places used")
    return x, y, passi


x_eur, y_eur, passi = euristica(f1, g1, d1, c1)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
lb1 = sum(x_eur[i, j] + y_eur[i, j] for i in R(s1) for j in R(r1))
sol_eur = ({f"x[{i},{j}]": x_eur[i, j] for i in R(s1) for j in R(r1)}
           | {f"y[{i},{j}]": y_eur[i, j] for i in R(s1) for j in R(r1)})
assert ammissibile(m1, sol_eur), sol_eur
print(f"  Children accepted by the heuristic: lb = {frazione(lb1)}")
print("  The heuristic uses up the majority nationality in the first camp: in the second one")
print("  nobody is left who can form the majority, and the camp stays empty.")

# ---------- 5. THE REAL LIMIT IS THE MAJORITY NATIONALITY ----------
intestazione("10.6 Two combinatorial arguments on the bounds")
tot_c = f1[c1] + g1[c1]
print(f"  In every camp nationality {c1 + 1} is not fewer than all the others together, so in")
print(f"  every camp it takes at least half of the places. It has {tot_c} children in total:")
print(f"  at most 2 * {tot_c} = {2 * tot_c} children can be accepted. This is a second upper")
print(f"  bound, worse than the capacity one ({frazione(ub1)}) on this instance but not in")
print("  general.")
print(f"  Likewise the girls are {sum(f1)}: with girls >= boys in every camp, the accepted")
print(f"  children are at most 2 * {sum(f1)} = {2 * sum(f1)}.")
salva_dati(pd.DataFrame([{"argument": "capacity of the camps", "bound": ub1},
                         {"argument": "majority nationality", "bound": 2 * tot_c},
                         {"argument": "girls available", "bound": 2 * sum(f1)}]),
           "fam10_6_argomenti")

# ---------- 6. OPTIMUM OF THE MILP ----------
z1 = risolvi(m1)
print("  Optimal solution:")
for j in R(r1):
    tot = sum(x1[i, j].X + y1[i, j].X for i in R(s1))
    print(f"    camp {j + 1}: " + ", ".join(
        f"nat. {i + 1} -> {int(x1[i, j].X)} girls and {int(y1[i, j].X)} boys" for i in R(s1))
        + f"; {int(tot)} places out of {d1[j]}")
riga = registra_bound("1 camps", ub1, lb1, zlp1, zlp1r, z1, senso="max")
salva_dati(pd.DataFrame([riga]), "fam10_6_bound")
assert lb1 <= z1 <= zlp1 <= ub1 + 1e-9
print(f"  The dual bound {frazione(ub1)} coincides with the optimum: the capacity is")
print("  saturated and the certificate closes the gap. The whole gap was on the heuristic side.")

# ---------- 7. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 1a: camp 1 grows; the limit moves from the capacity to nationality 1
m, x, y = modello_1(f1, g1, [20, d1[1]], c1)
varianti["1a"] = variante("1a. Camp 1 grows to 20 places (d1 = 20)", m)
print(f"       the total capacity is now 28 but the optimum stops at 2 * {f1[c1] + g1[c1]} = "
      f"{2 * (f1[c1] + g1[c1])}: the majority nationality is in charge.")
# 1b: the majority nationality cannot be split between several camps
m, x, y = modello_1(f1, g1, d1, c1)
M1 = f1[c1] + g1[c1]
w = m.addVars(r1, vtype=GRB.BINARY, name="w")
m.addConstrs((x[c1, j] + y[c1, j] - M1 * w[j] <= 0 for j in R(r1)), name="single_camp")
m.addConstr(w.sum() <= 1, name="at_most_one_camp")
varianti["1b"] = variante("1b. Nationality 1 cannot be split between several camps", m)
print("       this is exactly what the heuristic does: the second camp stays empty and we")
print(f"       are back to the value {frazione(lb1)}.")
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "fam10_6_varianti")

# ---------- 8. THE SANDWICH ON THE VARIANT 1a ----------
intestazione("10.6a The sandwich on the variant: camp 1 goes up to 20 places")
d1a = [20] + list(d1[1:])

# A capacity changes, not the structure: same model, same dual, same recipe.
# The bound 'every child takes a place' follows the places available.
m1a, x1a, y1a = modello_1(f1, g1, d1a, c1)
salva_modello(m1a, "fam10_6a_primale")
dl1a = duale_1(f1, g1, d1a, c1)
salva_modello(dl1a, "fam10_6a_duale")

# -- feasible heuristic: the same rule, with the new places --
x_1a, y_1a, passi_1a = euristica(f1, g1, d1a, c1)
for k, s in enumerate(passi_1a, 1):
    print(f"  Step {k}. {s}")
lb1a = sum(x_1a[i, j] + y_1a[i, j] for i in R(s1) for j in R(r1))
sol_1a = ({f"x[{i},{j}]": x_1a[i, j] for i in R(s1) for j in R(r1)}
          | {f"y[{i},{j}]": y_1a[i, j] for i in R(s1) for j in R(r1)})
assert ammissibile(m1a, sol_1a), "the heuristic solution of the variant must be feasible"
print(f"  lb = {frazione(lb1a)}")

# -- dual certificate: the same recipe, on the new places --
mano_1a = {f"gamma[{j}]": 1.0 for j in R(r1)}
ub1a, viol_1a = valuta(dl1a, mano_1a)
assert viol_1a <= 1e-9, viol_1a
print("Dual solution by hand: alpha = beta = delta = eps = 0 and gamma_j = 1, as in the")
print("  base problem: every child accepted takes a place, so no more than sum_j d_j can")
print(f"  be accepted = {' + '.join(map(str, d1a))} = {frazione(ub1a)}.")
print("  The certificate does not change shape: the datum it adds up does.")
zlp1a, zlp1ar, _ = due_rilassamenti(m1a, dl1a)
z1a_val = risolvi(m1a)
riga_1a = registra_bound("1a camp 1 at 20 places", ub1a, lb1a, zlp1a, zlp1ar, z1a_val, senso="max")
salva_dati(pd.DataFrame([riga_1a]), "fam10_6a_bound")
assert lb1a <= z1a_val <= zlp1a + 1e-9 <= ub1a + 1e-9

# ---------- 9. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
etichette = [f"camp {j + 1}" for j in R(r1)]
for k, (nome, sol) in enumerate([("heuristic", (x_eur, y_eur)),
                                 ("optimum", ({(i, j): x1[i, j].X for i in R(s1) for j in R(r1)},
                                              {(i, j): y1[i, j].X for i in R(s1)
                                               for j in R(r1)}))]):
    xs, ys = sol
    off = -0.2 + 0.4 * k
    for j in R(r1):
        naz1 = xs[c1, j] + ys[c1, j]
        altre = sum(xs[i, j] + ys[i, j] for i in R(s1) if i != c1)
        ax.bar(j + off, naz1, 0.36, color=TEAL if k else ARANCIO)
        ax.bar(j + off, altre, 0.36, bottom=naz1, color=BLU if k else GRIGIO)
        ax.annotate(nome, (j + off, -1.2), ha="center", fontsize=7)
for j in R(r1):
    ax.plot([j - 0.45, j + 0.45], [d1[j], d1[j]], color="black", lw=1.4, ls="--")
ax.plot([], [], color=ARANCIO, lw=6, label="heuristic: majority nat.")
ax.plot([], [], color=GRIGIO, lw=6, label="heuristic: others")
ax.plot([], [], color=TEAL, lw=6, label="optimum: majority nat.")
ax.plot([], [], color=BLU, lw=6, label="optimum: others")
ax.plot([], [], color="black", ls="--", label="capacity")
ax.set_xticks(R(r1))
ax.set_xticklabels(etichette)
ax.set_ylim(-2, max(d1) + 2)
ax.set_ylabel("children accepted")
ax.set_title(f"10.6: heuristic {frazione(lb1)} against optimum {frazione(z1)}")
ax.legend(fontsize=7, ncol=2)
salva_figura(fig, "cap10_campi_ottimo")
print("Done.")
