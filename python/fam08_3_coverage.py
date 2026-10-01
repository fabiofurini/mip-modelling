"""Problem 8.3 -- Signal coverage with interference (maximum profit).

An "if and only if" as in scheduling problem 7.6: one direction (threshold +
interference => covered) is imposed by two families of link constraints; the
other direction (covered => conditions satisfied) follows from the objective.
"""
from itertools import combinations as combinazioni

import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi,
                 stampa_soluzione, valuta)
from stile import intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------

intestazione("3. Coverage with interference: signal threshold and at most one strong location")
s3 = [[6, 0, 5, 3, 1], [4, 5, 2, 0, 0], [0, 7, 5, 4, 2]]   # signal location l -> client c
p3 = [10, 20, 5, 15, 25]     # profit if client c is covered
t3, b3, k3 = 5, 4, 2         # signal threshold, interference limit, budget of locations
m, n = 3, 5
L3 = [[l for l in R(m) if s3[l][c] >= b3] for c in R(n)]   # L_c: "strong" locations for client c
salva_dati(pd.DataFrame([{"location": l + 1, "client": c + 1, "s": s3[l][c]}
                         for l in R(m) for c in R(n)]), "fam08_3_segnale")
salva_dati(pd.DataFrame({"client": R(1, n + 1), "p": p3}), "fam08_3_clienti")


def modello_3(s, p, t, b, k):
    m, n = len(s), len(p)
    L = [[l for l in R(m) if s[l][c] >= b] for c in R(n)]
    mod = nuovo_modello("coverage_interference")
    x = mod.addVars(m, vtype=GRB.BINARY, name="x")
    y = mod.addVars(n, vtype=GRB.BINARY, name="y")
    mod.setObjective(gp.quicksum(p[c] * y[c] for c in R(n)), GRB.MAXIMIZE)
    mod.addConstrs((-gp.quicksum(s[l][c] * x[l] for l in R(m)) + t * y[c] <= 0 for c in R(n)),
                   name="threshold")
    mod.addConstrs((gp.quicksum(x[l] for l in L[c]) + (m - 1) * y[c] <= m for c in R(n)),
                   name="interference")
    mod.addConstr(x.sum() <= k, name="budget")
    return mod, x, y, L


def duale_3(s, p, t, b, k):
    """min sum m lam_c + k mu;  -sum_c s_lc pi_c + sum_{c in C_l} lam_c + mu >= 0;
    t pi_c + (m-1) lam_c >= p_c;  pi,lam,mu >= 0."""
    m, n = len(s), len(p)
    L = [[l for l in R(m) if s[l][c] >= b] for c in R(n)]
    C = [[c for c in R(n) if l in L[c]] for l in R(m)]
    dl = nuovo_modello("duale_coverage")
    pi = dl.addVars(n, name="pi")
    lam = dl.addVars(n, name="lam")
    mu = dl.addVar(name="mu")
    dl.setObjective(m * lam.sum() + k * mu, GRB.MINIMIZE)
    dl.addConstrs((-gp.quicksum(s[l][c] * pi[c] for c in R(n)) + gp.quicksum(lam[c] for c in C[l]) + mu >= 0
                  for l in R(m)), name="rc_x")
    dl.addConstrs((t * pi[c] + (m - 1) * lam[c] >= p[c] for c in R(n)), name="rc_y")
    return dl


m3, x3, y3, L3m = modello_3(s3, p3, t3, b3, k3)
salva_modello(m3, "fam08_3_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp3, zlp3r, _ = rilassamenti(m3)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------

d3 = duale_3(s3, p3, t3, b3, k3)
salva_modello(d3, "fam08_3_duale")
mano = {"mu": 0.0}
mano.update({f"pi[{c}]": 0.0 for c in R(n)})
mano.update({f"lam[{c}]": p3[c] / 2 for c in R(n)})
ub3, viol = valuta(d3, mano)
assert viol <= 1e-9, viol
print("Hand-built dual solution: pi = 0, mu = 0, lam_c = p_c/2 = "
      + ", ".join(frazione(p3[c] / 2) for c in R(n)) + f"  ->  ub = {frazione(ub3)}")
dualita_forte(d3, zlp3)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------

print("Heuristic: the first k locations are opened; a client is covered if the total")
print("signal reaches the threshold and at most one strong location reaches it.")


def euristica_3(s, p, t, b, k):
    m, n = len(s), len(p)
    x = [1 if l < k else 0 for l in R(m)]
    y, passi = [0] * n, []
    for c in R(n):
        ts = sum(s[l][c] for l in R(k))
        ni = sum(1 for l in R(k) if s[l][c] >= b)
        y[c] = 1 if (ts >= t and ni <= 1) else 0
        passi.append(f"Client {c + 1}: total signal = {ts}, strong locations = {ni}; "
                     f"{'covered' if y[c] else 'not covered'}.")
    return x, y, passi


xe, ye, passi = euristica_3(s3, p3, t3, b3, k3)
print(f"  The first k = {k3} locations are opened: x = {xe}.")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
lb3 = sum(p3[c] * ye[c] for c in R(n))
print(f"  lb = {lb3}")

# ---------- 5. OPTIMAL SOLUTION OF THE MILP ----------

z3 = risolvi(m3)
print("Optimal solution of the MILP:")
stampa_soluzione(m3, solo_non_nulle=True)
riga = registra_bound("3 coverage", ub3, lb3, zlp3, zlp3r, z3, senso="max")
salva_dati(pd.DataFrame([riga]), "fam08_3_bound")

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------

varianti = {}


def variante(nome, mod):
    z = risolvi(mod)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 3a: at least 3 clients must be covered
mod, x, y, L = modello_3(s3, p3, t3, b3, k3)
mod.addConstr(y.sum() >= 3, name="minimum_coverage")
varianti["3a"] = variante("3a. At least 3 clients covered (sum y_c >= 3)", mod)
# 3b: if location 1 is opened, location 3 must also be opened
mod, x, y, L = modello_3(s3, p3, t3, b3, k3)
mod.addConstr(x[0] <= x[2], name="1_implies_3")
varianti["3b"] = variante("3b. If location 1 opens, location 3 also opens (x_1 <= x_3)", mod)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "fam08_3_varianti")

# ---------- 7. THE SANDWICH ON THE VARIANT 3a ----------
intestazione("3a. The sandwich on the variant: at least 3 clients covered")


def modello_3a(s, p, t, b, k, minimo=3):
    mod_, xx, yy, LL = modello_3(s, p, t, b, k)
    mod_.addConstr(yy.sum() >= minimo, name="copertura_minima")
    return mod_, xx, yy, LL


def duale_3a(s, p, t, b, k, minimo=3):
    """To the dual of 8.3 one adds omega <= 0 for the constraint sum_c y_c >= minimo
    (a >= direction in a maximisation): it enters the objective with its
    right-hand side and the columns of the y_c."""
    mm, nn = len(s), len(p)
    L = [[l for l in R(mm) if s[l][c] >= b] for c in R(nn)]
    C = [[c for c in R(nn) if l in L[c]] for l in R(mm)]
    dl = nuovo_modello("duale_copertura_3a")
    pi = dl.addVars(nn, name="pi")
    lam = dl.addVars(nn, name="lam")
    mu = dl.addVar(name="mu")
    om = dl.addVar(lb=-GRB.INFINITY, ub=0.0, name="omega")
    dl.setObjective(mm * lam.sum() + k * mu + minimo * om, GRB.MINIMIZE)
    dl.addConstrs((-gp.quicksum(s[l][c] * pi[c] for c in R(nn))
                   + gp.quicksum(lam[c] for c in C[l]) + mu >= 0 for l in R(mm)), name="rc_x")
    dl.addConstrs((t * pi[c] + (mm - 1) * lam[c] + om >= p[c] for c in R(nn)), name="rc_y")
    return dl


m3a, x3a, y3a, L3a = modello_3a(s3, p3, t3, b3, k3)
salva_modello(m3a, "fam08_3a_primale")

# -- feasible heuristic: every choice of k sites is tried and the best is kept --
print("Constructive heuristic: the sites are few, so every choice of k sites is tried and")
print("the one covering at least 3 clients with the highest profit is kept.")
migliore_3a = None
for scelta in combinazioni(R(m), k3):
    cop = []
    for c in R(n):
        segnale = sum(s3[l][c] for l in scelta)
        forti = sum(1 for l in scelta if s3[l][c] >= b3)
        if segnale >= t3 and forti <= 1:
            cop.append(c)
    valore = sum(p3[c] for c in cop)
    print(f"  sites {[l + 1 for l in scelta]}: clients covered {[c + 1 for c in cop]}, "
          f"profit {valore}" + ("" if len(cop) >= 3 else "  (fewer than 3: not feasible)"))
    if len(cop) >= 3 and (migliore_3a is None or valore > migliore_3a[0]):
        migliore_3a = (valore, scelta, cop)
lb3a, sedi_3a, cop_3a = migliore_3a
sol_3a = ({f"x[{l}]": (1 if l in sedi_3a else 0) for l in R(m)}
          | {f"y[{c}]": (1 if c in cop_3a else 0) for c in R(n)})
assert ammissibile(m3a, sol_3a), "the heuristic solution of the variant must be feasible"
print(f"  the best is {[l + 1 for l in sedi_3a]}  ->  lb = {frazione(lb3a)}")

# -- dual certificate: omega stays at zero, and the arithmetic shows it --
d3a = duale_3a(s3, p3, t3, b3, k3)
salva_modello(d3a, "fam08_3a_duale")
mano_3a = {"mu": 0.0, "omega": 0.0}
mano_3a.update({f"pi[{c}]": 0.0 for c in R(n)})
mano_3a.update({f"lam[{c}]": p3[c] / (m - 1) for c in R(n)})
ub3a, viol_3a = valuta(d3a, mano_3a)
assert viol_3a <= 1e-9, viol_3a
print("Dual solution by hand: pi = 0, mu = 0 and lam_c = p_c/(m-1) as in the base problem.")
print("  The new omega is best left at zero: lowering it forces every lam_c up by")
print("  -omega/(m-1) for each of the n clients, and in the objective those m lam weigh")
print("  m*n/(m-1) times more than the right-hand side saves.")
print(f"  ->  ub = {frazione(ub3a)}")
zlp3a, zlp3ar, _ = due_rilassamenti(m3a, d3a)
z3a = risolvi(m3a)
riga_3a = registra_bound("3a at least 3 clients covered", ub3a, lb3a, zlp3a, zlp3ar, z3a, senso="max")
salva_dati(pd.DataFrame([riga_3a]), "fam08_3a_bound")
assert lb3a <= z3a <= zlp3a + 1e-9 <= ub3a + 1e-9

# ---------- 8. FIGURES ----------

fig, ax = plt.subplots(figsize=(7.2, 3.2))
ott_x = [l for l in R(m) if x3[l].X > 0.5]
larghezza = 0.6
for c in R(n):
    colore = "#1E8449" if y3[c].X > 0.5 else "#C0392B"
    ax.bar(c, p3[c], color=colore, width=larghezza)
    ax.text(c, p3[c] + 0.5, "covered" if y3[c].X > 0.5 else "not covered", ha="center", fontsize=8)
ax.set_xticks(R(n))
ax.set_xticklabels([f"client {c + 1}" for c in R(n)])
ax.set_ylabel("profit $p_c$")
ax.set_title(f"Coverage: optimal solution with open locations {[l + 1 for l in ott_x]} (z = {frazione(z3)})")
salva_figura(fig, "cap08_copertura_ottimo")
print("Fine.")
