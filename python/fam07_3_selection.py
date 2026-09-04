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

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("3. Job selection: maximum profit = revenues - fixed costs")
t3 = [25, 40, 75]
r3 = [10, 15, 30]
c3 = [20, 30, 15]
a3 = [105, 110, 100]
salva_dati(pd.DataFrame({"job": R(1, 4), "t": t3, "r": r3}), "sched3_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "c": c3, "a": a3}), "sched3_macchine")


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
salva_dati(pd.DataFrame([riga]), "sched3_bound")

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
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched3_varianti")

print("Done.")
