"""Problem 7.5 -- One machine, job classes with setup.

The disaggregated activation link derived step by step from the CNF of a
Boolean implication: (OR of jobs) => class activated.
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
intestazione("5. Job classes with setup cost and time: y_c activates the class")
r5 = [10, 6, 8, 6, 7, 9, 5]
t5 = [5, 10, 8, 6, 9, 5, 6]
J5 = [[0, 1], [2, 3], [4, 5, 6]]       # classes (0-based)
f5 = [10, 5, 4]
s5 = [10, 12, 6]
a5 = 50
salva_dati(pd.DataFrame({"job": R(1, 8), "r": r5, "t": t5,
                         "class": [c + 1 for j in R(7) for c in R(3) if j in J5[c]]}), "sched5_lavori")
salva_dati(pd.DataFrame({"class": R(1, 4), "f": f5, "s": s5}), "sched5_classi")


def modello_5(r, t, J, f, s, a):
    n, q = len(r), len(J)
    m = nuovo_modello("classi_setup")
    x = m.addVars(n, vtype=GRB.BINARY, name="x")
    y = m.addVars(q, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(r[j] * x[j] for j in R(n)) - gp.quicksum(f[c] * y[c] for c in R(q)),
                   GRB.MAXIMIZE)
    m.addConstr(gp.quicksum(t[j] * x[j] for j in R(n)) + gp.quicksum(s[c] * y[c] for c in R(q)) <= a,
                name="disponibilita")
    m.addConstrs((x[j] - y[c] <= 0 for c in R(q) for j in J[c]), name="link")
    return m, x, y


def duale_5(r, t, J, f, s, a):
    """min a pi;  t_j pi + lam_j >= r_j;  s_c pi - sum_{j in J_c} lam_j >= -f_c;  pi, lam >= 0."""
    n, q = len(r), len(J)
    d = nuovo_modello("duale_classi_setup")
    pi = d.addVar(name="pi")
    lam = d.addVars(n, name="lam")
    d.setObjective(a * pi, GRB.MINIMIZE)
    d.addConstrs((t[j] * pi + lam[j] >= r[j] for j in R(n)), name="rc_x")
    d.addConstrs((s[c] * pi - gp.quicksum(lam[j] for j in J[c]) >= -f[c] for c in R(q)), name="rc_y")
    return d


def euristica_5(r, t, J, f, s, a):
    """Class by class: the first job also pays the setup, if it fits."""
    n, q = len(r), len(J)
    x, y, ra, passi = [0] * n, [0] * q, a, []
    for c in R(q):
        for j in J[c]:
            if y[c] == 0:
                if s[c] + t[j] <= ra:
                    y[c], x[j] = 1, 1
                    passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c]} + {t[j]} = "
                                 f"{s[c] + t[j]} <= ra = {ra}; y[{c + 1}] = 1, x[{j + 1}] = 1, ra = {ra - s[c] - t[j]}.")
                    ra -= s[c] + t[j]
                else:
                    passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c] + t[j]} > ra = {ra}; "
                                 f"job {j + 1} is skipped.")
            else:
                if t[j] <= ra:
                    x[j] = 1
                    passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} <= ra = {ra}; x[{j + 1}] = 1, ra = {ra - t[j]}.")
                    ra -= t[j]
                else:
                    passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} > ra = {ra}; job {j + 1} is skipped.")
    return x, y, passi


m5, x5, y5 = modello_5(r5, t5, J5, f5, s5, a5)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
xe, ye, passi = euristica_5(r5, t5, J5, f5, s5, a5)
print("Class-by-class heuristic:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
lb5 = sum(r5[j] * xe[j] for j in R(7)) - sum(f5[c] * ye[c] for c in R(3))
print(f"  lb = {lb5}  (x = {xe}, y = {ye})")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d5 = duale_5(r5, t5, J5, f5, s5, a5)
pi_mano = max(r5[j] / t5[j] for j in R(7))
ub5, viol = valuta(d5, {"pi": pi_mano})
assert viol <= 1e-9
print(f"Hand-built dual solution: lam = 0, pi = max_j r_j/t_j = {frazione(pi_mano)}  ->  ub = {frazione(ub5)}")
zlp5, zlp5r, _ = due_rilassamenti(m5, d5)

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
z5 = risolvi(m5)
print("Optimal solution of the MILP:")
stampa_soluzione(m5, solo_non_nulle=True)
riga = registra_bound("5 classes setup", ub5, lb5, zlp5, zlp5r, z5, senso="max")
salva_dati(pd.DataFrame([riga]), "sched5_bound")

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z

# 5a: a single active class
m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
m.addConstr(y.sum() <= 1, name="one_class")
varianti["5a"] = variante("5a. At most one class activated (sum y_c <= 1)", m)
# 5b: class 3 only if class 1
m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
m.addConstr(y[2] <= y[0], name="3_only_if_1")
varianti["5b"] = variante("5b. Class 3 is activated only if class 1 is (y_3 <= y_1)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched5_varianti")

print("Done.")
