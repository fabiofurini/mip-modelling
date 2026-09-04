"""Problem 7.4 -- Parallel jobs: the processing time as a maximum.

The maximum-variable pattern in three steps: imposed by the constraint (one
side), imposed by the optimum (the other side), synthesis that characterises
y_m as the maximum of the times of the assigned jobs.
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
intestazione("4. Parallel jobs: y_m = maximum of the times of the assigned jobs")
t4 = [[6, 5, 3], [5, 10, 2], [20, 13, 10]]
p4 = [1, 2, 2]
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t4[j][m]}
                         for j in R(3) for m in R(3)]), "sched4_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "p": p4}), "sched4_macchine")


def modello_4(t, p):
    n, k = len(t), len(p)
    m = nuovo_modello("parallelo")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, name="y")
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
    m.addConstrs((x.sum("*", mm) <= p[mm] for mm in R(k)), name="cardinalita")
    m.addConstrs((-t[j][mm] * x[j, mm] + y[mm] >= 0 for j in R(n) for mm in R(k)), name="massimo")
    return m, x, y


def duale_4(t, p):
    """max sum mu_j + sum p_m pi_m;  mu_j + pi_m - t_jm lam_jm <= 0;  sum_j lam_jm <= 1."""
    n, k = len(t), len(p)
    d = nuovo_modello("duale_parallelo")
    mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
    lam = d.addVars(n, k, name="lam")
    d.setObjective(mu.sum() + gp.quicksum(p[mm] * pi[mm] for mm in R(k)), GRB.MAXIMIZE)
    d.addConstrs((mu[j] + pi[mm] - t[j][mm] * lam[j, mm] <= 0 for j in R(n) for mm in R(k)), name="rc_x")
    d.addConstrs((lam.sum("*", mm) <= 1 for mm in R(k)), name="rc_y")
    return d


def euristica_4(t, p):
    """Next-fit on the number of jobs: a machine is filled up to p_m jobs, then the next one."""
    n, k = len(t), len(p)
    x, y, cm, cnt, passi = {}, [0.0] * k, 0, 0, []
    for j in R(n):
        if cnt == p[cm]:
            if cm == k - 1:
                return None
            cm, cnt = cm + 1, 0
        x[(j, cm)] = 1
        cnt += 1
        y[cm] = max(y[cm], t[j][cm])
        passi.append(f"Job {j + 1} on machine {cm + 1} (assigned jobs {cnt} <= p = {p[cm]}): "
                     f"y[{cm + 1}] = max(y[{cm + 1}], t[{j + 1}][{cm + 1}] = {t[j][cm]}) = {y[cm]:g}.")
    return x, y, passi


m4, x4, y4 = modello_4(t4, p4)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
xe, ye, passi = euristica_4(t4, p4)
print("Next-fit heuristic on the cardinalities:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub4 = sum(ye)
print(f"  ub = {frazione(ub4)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
d4 = duale_4(t4, p4)
mano = {f"lam[{j},{mm}]": 1 / 3 for j in R(3) for mm in R(3)}
mano.update({f"mu[{j}]": min(t4[j][mm] / 3 for mm in R(3)) for j in R(3)})
lb4, viol = valuta(d4, mano)
assert viol <= 1e-9
print("Hand-built dual solution: lam_jm = 1/3, pi = 0, mu_j = min_m t_jm/3 = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  lb = {frazione(lb4)}")
zlp4, zlp4r, _ = due_rilassamenti(m4, d4)

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
z4 = risolvi(m4)
print("Optimal solution of the MILP:")
stampa_soluzione(m4, solo_non_nulle=True)
riga = registra_bound("4 parallel", ub4, lb4, zlp4, zlp4r, z4)
salva_dati(pd.DataFrame([riga]), "sched4_bound")

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z

# 4a: minimise the makespan (maximum of the machine times)
m, x, y = modello_4(t4, p4)
w = m.addVar(name="w")
m.addConstrs((w >= y[mm] for mm in R(3)), name="makespan")
m.setObjective(w, GRB.MINIMIZE)
varianti["4a"] = variante("4a. Minimise the maximum of the times (min-max: w >= y_m)", m)
# 4b: fixed cost if a machine works (y_m > 0 => v_m = 1, big-M = max_j t_jm)
g4 = [4, 4, 4]
m, x, y = modello_4(t4, p4)
vv = m.addVars(3, vtype=GRB.BINARY, name="v")
m.addConstrs((y[mm] <= max(t4[j][mm] for j in R(3)) * vv[mm] for mm in R(3)), name="activate")
m.setObjective(y.sum() + gp.quicksum(g4[mm] * vv[mm] for mm in R(3)), GRB.MINIMIZE)
varianti["4b"] = variante("4b. Fixed cost 4 if the machine works (y_m <= M_m v_m)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched4_varianti")

print("Done.")
