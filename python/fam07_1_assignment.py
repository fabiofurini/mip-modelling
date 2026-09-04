"""Problem 7.1 -- Minimum-cost assignment with availability (GAP).

A BIP model with a single family of variables: no link to prove, only an
assignment constraint and a per-machine capacity constraint. Next/first/
best-fit heuristics for the upper bound, dual of the LP relaxation with a
hand-built solution for the lower bound.
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
intestazione("1. Minimum-cost assignment: n jobs, k machines, availability a_m")
t1 = [[2, 1, 3], [3, 4, 2], [4, 5, 3]]
c1 = [[5, 10, 2], [5, 4, 6], [5, 4, 6]]
a1 = [5, 6, 7]
n, k = 3, 3
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t1[j][m], "c": c1[j][m]}
                         for j in R(n) for m in R(k)]), "sched1_lavori")
salva_dati(pd.DataFrame({"machine": R(1, k + 1), "a": a1}), "sched1_macchine")


def modello_1(t, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("assegnamento")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(c[j][mm] * x[j, mm] for j in R(n) for mm in R(k)), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
    m.addConstrs((gp.quicksum(t[j][mm] * x[j, mm] for j in R(n)) <= a[mm] for mm in R(k)),
                 name="disponibilita")
    return m, x


def duale_1(t, c, a):
    """Dual of the LP relaxation: max sum mu_j + sum a_m pi_m, mu_j + t_jm pi_m <= c_jm, pi <= 0."""
    n, k = len(t), len(a)
    d = nuovo_modello("duale_assegnamento")
    mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
    d.setObjective(mu.sum() + gp.quicksum(a[mm] * pi[mm] for mm in R(k)), GRB.MAXIMIZE)
    d.addConstrs((mu[j] + t[j][mm] * pi[mm] <= c[j][mm] for j in R(n) for mm in R(k)), name="rc")
    return d


def valore_1(e, c):
    return sum(c[j][mm] for (j, mm) in e.x)


m1, x1 = modello_1(t1, c1, a1)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
print("Constructive heuristics:")
e_next = next_fit(t1, a1)
e_first = first_fit(t1, a1)
e_best = best_fit(t1, a1, lambda j, mm, ra: c1[j][mm], "cost")
for nome, e in [("next-fit", e_next), ("first-fit", e_first), ("best-fit (minimum cost)", e_best)]:
    print(f"  {nome:26s} ub = {valore_1(e, c1)}   assignment "
          + ", ".join(f"x[{j + 1}][{mm + 1}]" for (j, mm) in sorted(e.x)))
print("Step-by-step run of the best-fit:")
e_best.traccia.stampa()
ub1 = valore_1(e_best, c1)
sol_eur = {f"x[{j},{mm}]": 1 for (j, mm) in e_best.x}
assert ammissibile(m1, sol_eur)

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
d1 = duale_1(t1, c1, a1)
mano = {f"mu[{j}]": min(c1[j]) for j in R(n)}
lb1, viol = valuta(d1, mano)
assert viol <= 1e-9, viol
print(f"Hand-built dual solution: pi = 0, mu_j = min_m c_jm = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(n)) + f"  ->  lb = {frazione(lb1)}")
zlp1, zlp1r, pi_lp = due_rilassamenti(m1, d1)
print("Duals of the relaxation read from Gurobi:", {kk: round(v, 4) for kk, v in pi_lp.items()})

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
z1 = risolvi(m1)
print("Optimal solution of the MILP:")
stampa_soluzione(m1, solo_non_nulle=True)
riga = registra_bound("1 assignment", ub1, lb1, zlp1, zlp1r, z1)
salva_dati(pd.DataFrame([riga]), "sched1_bound")
ott1 = {(j, mm) for j in R(n) for mm in R(k) if x1[j, mm].X > 0.5}

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z

# 1a: jobs 1 and 3 must be on the same machine
m, x = modello_1(t1, c1, a1)
m.addConstrs((x[0, mm] == x[2, mm] for mm in R(3)), name="together")
varianti["1a"] = variante("1a. Jobs 1 and 3 on the same machine (x_1m = x_3m)", m)
# 1b: fixed cost g_m per used machine (activation)
g1 = [3, 3, 3]
m, x = modello_1(t1, c1, a1)
y = m.addVars(3, vtype=GRB.BINARY, name="y")
m.addConstrs((x[j, mm] <= y[mm] for j in R(3) for mm in R(3)), name="activate")
m.update()
m.setObjective(m.getObjective() + gp.quicksum(g1[mm] * y[mm] for mm in R(3)), GRB.MINIMIZE)
varianti["1b"] = variante("1b. Fixed cost g_m = 3 per used machine (x_jm <= y_m)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched1_varianti")

# ---------- 6. FIGURES ----------


def barre_macchine(assegn, t, a, titolo, nome):
    """Every machine: bar of the times of the assigned jobs and availability."""
    k = len(a)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for mm in R(k):
        inizio = 0
        for (j, m2) in sorted(assegn):
            if m2 == mm:
                ax.barh(mm, t[j][mm], left=inizio, color=CICLO[j % len(CICLO)], edgecolor="white")
                ax.text(inizio + t[j][mm] / 2, mm, f"{j + 1}", ha="center", va="center", color="white",
                        fontsize=9, fontweight="bold")
                inizio += t[j][mm]
        ax.plot([a[mm], a[mm]], [mm - 0.4, mm + 0.4], color=ROSSO, lw=2)
    ax.set_yticks(R(k))
    ax.set_yticklabels([f"machine {mm + 1}" for mm in R(k)])
    ax.set_xlabel("time (minutes); in red the availability $a_m$")
    ax.set_title(titolo)
    ax.invert_yaxis()
    salva_figura(fig, nome)

barre_macchine(e_best.x, t1, a1, "Assignment: best-fit solution (ub = 11)", "cap07_gap_euristica")
barre_macchine(ott1, t1, a1, f"Assignment: optimal solution (z = {frazione(z1)})", "cap07_gap_ottimo")
print("Done.")
