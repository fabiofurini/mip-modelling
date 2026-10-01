"""Problem 7.3 -- Job selection with revenues and fixed-cost machines.

The same activation link as problem 7.2, read in a maximisation problem: the
heuristic gives a lower bound, the dual an upper bound -- the roles swap
with respect to minimisation problems.
"""
import gurobipy as gp
import numpy as np
import pandas as pd
from gurobipy import GRB

from euristiche import best_fit, first_fit, matrice, next_fit
from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello,
                 registra_bound, risolvi, stampa_soluzione, valuta)
from stile import CICLO, ROSSO, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("3. Job selection: maximum profit = revenues - fixed costs")
t3 = [25, 40, 75]
r3 = [10, 15, 30]
c3 = [20, 30, 15]
a3 = [105, 110, 100]
salva_dati(pd.DataFrame({"job": R(1, 4), "t": t3, "r": r3}), "fam07_3_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "c": c3, "a": a3}), "fam07_3_macchine")


def modello_3(t, r, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("selezione")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(r[j] * x[j, mm] for j in R(n) for mm in R(k))
                   - gp.quicksum(c[mm] * y[mm] for mm in R(k)), GRB.MAXIMIZE)
    m.addConstrs((x.sum(j, "*") <= 1 for j in R(n)), name="al_piu_una")
    m.addConstrs((gp.quicksum(t[j] * x[j, mm] for j in R(n)) - a[mm] * y[mm] <= 0 for mm in R(k)),
                 name="link")
    return m, x, y


def duale_3(t, r, c, a):
    """min sum mu_j;  mu_j + t_j pi_m >= r_j;  -a_m pi_m >= -c_m;  mu, pi >= 0."""
    n, k = len(t), len(a)
    d = nuovo_modello("duale_selezione")
    mu = d.addVars(n, name="mu")
    pi = d.addVars(k, name="pi")
    d.setObjective(mu.sum(), GRB.MINIMIZE)
    d.addConstrs((mu[j] + t[j] * pi[mm] >= r[j] for j in R(n) for mm in R(k)), name="rc_x")
    d.addConstrs((-a[mm] * pi[mm] >= -c[mm] for mm in R(k)), name="rc_y")
    return d


def valore_3(e, r, c):
    return sum(r[j] for (j, mm) in e.x) - sum(c[mm] * y for mm, y in enumerate(e.y))


m3, x3, y3 = modello_3(t3, r3, c3, a3)
salva_modello(m3, "fam07_3_primale")

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
T3 = matrice(t3, 3)
eur3 = [("next-fit (skips if it does not fit)", next_fit(T3, a3, salta=True)),
        ("first-fit", first_fit(T3, a3, salta=True)),
        ("best-fit (fullest machine)", best_fit(T3, a3, lambda j, mm, ra: ra[mm], "ra", salta=True))]
print("Constructive heuristics (here they give a LOWER bound: maximisation problem):")
for nome, e in eur3:
    print(f"  {nome:32s} lb = {valore_3(e, r3, c3):3d}")
print("Step-by-step run of the best-fit:")
eur3[2][1].traccia.stampa()
lb3 = max(valore_3(e, r3, c3) for _, e in eur3)

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d3 = duale_3(t3, r3, c3, a3)
salva_modello(d3, "fam07_3_duale")
mano = {f"pi[{mm}]": c3[mm] / a3[mm] for mm in R(3)}
mano.update({f"mu[{j}]": max([0] + [r3[j] - t3[j] * c3[mm] / a3[mm] for mm in R(3)]) for j in R(3)})
ub3, viol = valuta(d3, mano)
assert viol <= 1e-9
print("Hand-built dual solution: pi_m = c_m/a_m; mu_j = max{0, r_j - t_j pi_m} = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  ub = {frazione(ub3)}")
zlp3, zlp3r, _ = due_rilassamenti(m3, d3)

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
z3 = risolvi(m3)
print("Optimal solution of the MILP:")
stampa_soluzione(m3, solo_non_nulle=True)
riga = registra_bound("3 selection", ub3, lb3, zlp3, zlp3r, z3, senso="max")
salva_dati(pd.DataFrame([riga]), "fam07_3_bound")

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z

# 3a: all jobs must be executed (the assignment constraint is back)
m, x, y = modello_3(t3, r3, c3, a3)
m.addConstrs((x.sum(j, "*") == 1 for j in R(3)), name="all")
varianti["3a"] = variante("3a. All jobs executed (sum_m x_jm = 1)", m)
# 3b: job 3 only if job 2
m, x, y = modello_3(t3, r3, c3, a3)
m.addConstr(x.sum(2, "*") <= x.sum(1, "*"), name="3_only_if_2")
varianti["3b"] = variante("3b. Job 3 is executed only if job 2 is executed", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "fam07_3_varianti")
# ---------- 5bis. THE SANDWICH ON THE VARIANT 3b ----------
intestazione("3b. The sandwich on the variant: job 3 only if job 2 as well")


def modello_3b(t, r, c, a):
    mm_, xx, yy = modello_3(t, r, c, a)
    mm_.addConstr(xx.sum(2, "*") - xx.sum(1, "*") <= 0, name="3_solo_se_2")
    return mm_, xx, yy


def duale_3b(t, r, c, a):
    """To the dual of 7.3 one adds lambda >= 0 for the constraint
    sum_m x_3m - sum_m x_2m <= 0: it appears with a plus sign in the columns of
    job 3 and with a minus sign in those of job 2. The right-hand side is zero,
    so the objective stays min sum_j mu_j."""
    nn, kk = len(t), len(a)
    d = nuovo_modello("duale_selezione_3b")
    mu = d.addVars(nn, name="mu")
    pi = d.addVars(kk, name="pi")
    lam = d.addVar(name="lambda")
    d.setObjective(mu.sum(), GRB.MINIMIZE)
    for mz in R(kk):
        d.addConstr(mu[0] + t[0] * pi[mz] >= r[0], name=f"rc_x0{mz}")
        d.addConstr(mu[1] + t[1] * pi[mz] - lam >= r[1], name=f"rc_x1{mz}")
        d.addConstr(mu[2] + t[2] * pi[mz] + lam >= r[2], name=f"rc_x2{mz}")
    d.addConstrs((-a[mz] * pi[mz] >= -c[mz] for mz in R(kk)), name="rc_y")
    return d


m3b, x3b, y3b = modello_3b(t3, r3, c3, a3)
salva_modello(m3b, "fam07_3b_primale")

# -- feasible heuristic: the base one, repaired by dropping job 3 when job 2 is missing --
print("Constructive heuristic: start from the solution of the base problem and, if it runs")
print("job 3 without job 2, drop job 3 (the repair is always feasible).")
e_base3 = max((e for _, e in eur3), key=lambda e: valore_3(e, r3, c3))
scelti = {j for (j, _) in e_base3.x}
print(f"  base solution: jobs {sorted(j + 1 for j in scelti)}, value "
      f"{frazione(valore_3(e_base3, r3, c3))}")
tenuti = [(j, mz) for (j, mz) in e_base3.x if not (j == 2 and 1 not in scelti)]
macchine = sorted({mz for (_, mz) in tenuti})
lb3b = sum(r3[j] for (j, _) in tenuti) - sum(c3[mz] for mz in macchine)
sol_3b = {f"x[{j},{mz}]": 1 for (j, mz) in tenuti} | {f"y[{mz}]": 1 for mz in macchine}
assert ammissibile(m3b, sol_3b), "the heuristic solution of the variant must be feasible"
print(f"  after the repair: jobs {sorted(j + 1 for (j, _) in tenuti)}  ->  "
      f"lb = {frazione(lb3b)}")

# -- dual certificate: lambda moves value from job 3 to job 2 --
d3b = duale_3b(t3, r3, c3, a3)
salva_modello(d3b, "fam07_3b_duale")
pi_b = {mz: c3[mz] / a3[mz] for mz in R(3)}
# the largest lambda that does not force mu_2 up: mu_2 stays at zero
# while lambda <= min_m (t_2 pi_m - r_2); beyond that, what is gained on mu_3
# is paid back on mu_2, so one stops there.
lam_b = max(0.0, min(t3[1] * pi_b[mz] - r3[1] for mz in R(3)))
mano_3b = {f"pi[{mz}]": pi_b[mz] for mz in R(3)} | {"lambda": lam_b}
mano_3b["mu[0]"] = max([0] + [r3[0] - t3[0] * pi_b[mz] for mz in R(3)])
mano_3b["mu[1]"] = max([0] + [r3[1] + lam_b - t3[1] * pi_b[mz] for mz in R(3)])
mano_3b["mu[2]"] = max([0] + [r3[2] - lam_b - t3[2] * pi_b[mz] for mz in R(3)])
ub3b, viol_3b = valuta(d3b, mano_3b)
assert viol_3b <= 1e-9, viol_3b
print("Dual solution by hand: pi_m = c_m/a_m as in the base problem; then lambda is raised")
print("  as far as job 2 can bear it for free, that is lambda = min_m (t_2 pi_m - r_2).")
if lam_b > 0:
    print(f"  Here lambda = {frazione(lam_b)}: it discounts job 3 without pushing mu_2 up.")
else:
    print("  Here that minimum is negative, so lambda stays at zero: job 2 leaves no")
    print("  margin to spend, and the certificate of the variant coincides with the one of")
    print("  the base problem. The implication raises the integer optimum but not the relaxation.")
print(f"  ->  ub = {frazione(ub3b)}")
zlp3b, zlp3br, _ = due_rilassamenti(m3b, d3b)
z3b = risolvi(m3b)
riga_3b = registra_bound("3b job 3 only with job 2", ub3b, lb3b, zlp3b, zlp3br, z3b,
                         senso="max")
salva_dati(pd.DataFrame([riga_3b]), "fam07_3b_bound")
assert lb3b <= z3b <= zlp3b + 1e-9 <= ub3b + 1e-9


print("Fine.")


print("Done.")
