"""Problem 7.7 -- Total tardiness on one machine: sequencing with big-M.

The disjunction "either j before i or i before j" linearised with a binary
variable and the smallest big-M justifiable from the data (M = sum of the
times).
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
t7 = [5, 4, 6]
d7 = [3, 4, 10]
salva_dati(pd.DataFrame({"job": R(1, 4), "t": t7, "d": d7}), "sched7_lavori")


def modello_7(t, d):
    n = len(t)
    M = sum(t)
    m = nuovo_modello("ritardo")
    s = m.addVars([(j, i) for j in R(n) for i in R(n) if j != i], vtype=GRB.BINARY, name="s")
    kappa = m.addVars(n, name="kappa")
    tau = m.addVars(n, name="tau")
    m.setObjective(tau.sum(), GRB.MINIMIZE)
    m.addConstrs((s[j, i] + s[i, j] == 1 for j in R(n) for i in R(j + 1, n)), name="ordine")
    m.addConstrs((-M * s[j, i] - kappa[j] + kappa[i] >= t[i] - M for j in R(n) for i in R(n) if j != i),
                 name="precedenza")
    m.addConstrs((-kappa[j] + tau[j] >= -d[j] for j in R(n)), name="ritardo")
    m.addConstrs((kappa[j] >= t[j] for j in R(n)), name="inizio")
    return m, s, kappa, tau, M


def duale_7(t, d):
    """Dual with alpha (free), beta, gamma, delta >= 0 — see the lecture notes."""
    n = len(t)
    M = sum(t)
    D = nuovo_modello("duale_ritardo")
    alpha = D.addVars([(j, i) for j in R(n) for i in R(j + 1, n)], lb=-GRB.INFINITY, name="alpha")
    beta = D.addVars([(j, i) for j in R(n) for i in R(n) if j != i], name="beta")
    gamma = D.addVars(n, name="gamma")
    delta = D.addVars(n, name="delta")
    D.setObjective(alpha.sum() + gp.quicksum((t[i] - M) * beta[j, i] for (j, i) in beta)
                   - gp.quicksum(d[j] * gamma[j] for j in R(n)) + gp.quicksum(t[j] * delta[j] for j in R(n)),
                   GRB.MAXIMIZE)
    D.addConstrs((alpha[j, i] - M * beta[j, i] <= 0 for (j, i) in alpha), name="rc_s_ji")
    D.addConstrs((alpha[j, i] - M * beta[i, j] <= 0 for (j, i) in alpha), name="rc_s_ij")
    D.addConstrs((-gp.quicksum(beta[j, i] for i in R(n) if i != j) + gp.quicksum(beta[i, j] for i in R(n) if i != j)
                  - gamma[j] + delta[j] <= 0 for j in R(n)), name="rc_kappa")
    D.addConstrs((gamma[j] <= 1 for j in R(n)), name="rc_tau")
    return D


def euristica_7(t, d, ordine=None):
    """Sequence in the given order (natural if absent): completions and tardiness."""
    n = len(t)
    ordine = list(R(n)) if ordine is None else ordine
    kappa, tau, fine, passi = [0] * n, [0] * n, 0, []
    for j in ordine:
        fine += t[j]
        kappa[j] = fine
        tau[j] = max(0, fine - d[j])
        passi.append(f"Job {j + 1}: kappa = {fine}, tau = max(0, {fine} - {d[j]}) = {tau[j]}.")
    return kappa, tau, passi


m7, s7, k7, tau7, M7 = modello_7(t7, d7)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
print(f"Big-M = sum of the times = {M7}")
kappa_e, tau_e, passi = euristica_7(t7, d7)
print("Heuristic: natural order 1 -> 2 -> 3")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub7 = sum(tau_e)
print(f"  ub = {ub7}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
D7 = duale_7(t7, d7)
lb7, viol = valuta(D7, {"gamma[0]": 1, "delta[0]": 1})
assert viol <= 1e-9
print(f"Hand-built dual solution: gamma_1 = 1, delta_1 = 1, all the rest 0  ->  lb = {frazione(lb7)}")
zlp7, zlp7r, _ = due_rilassamenti(m7, D7)

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
z7 = risolvi(m7)
print("Optimal solution of the MILP:")
stampa_soluzione(m7, solo_non_nulle=True)
riga = registra_bound("7 tardiness", ub7, lb7, zlp7, zlp7r, z7)
salva_dati(pd.DataFrame([riga]), "sched7_bound")
ordine_ott = sorted(R(3), key=lambda j: k7[j].X)
riga = registra_bound("7 tardiness", ub7, lb7, zlp7, zlp7r, z7)
salva_dati(pd.DataFrame([riga]), "sched7_bound")
print("Optimal sequence:", " -> ".join(str(j + 1) for j in ordine_ott))

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z

# 7a: release dates
rho7 = [0, 2, 0]
m, s, kappa, tau, M = modello_7(t7, d7)
m.addConstrs((kappa[j] >= rho7[j] + t7[j] for j in R(3)), name="release")
varianti["7a"] = variante("7a. Job 2 available from time 2 (kappa_j >= rho_j + t_j)", m)
# 7b: minimise the maximum tardiness
m, s, kappa, tau, M = modello_7(t7, d7)
T = m.addVar(name="T")
m.addConstrs((T >= tau[j] for j in R(3)), name="max_tardiness")
m.setObjective(T, GRB.MINIMIZE)
varianti["7b"] = variante("7b. Minimise the maximum tardiness (min-max: T >= tau_j)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched7_varianti")

# ---------- 6. FIGURES ----------
# tardiness: Gantt of the natural and of the optimal sequence
fig, ax = plt.subplots(figsize=(7.2, 3.0))
for riga, (etichetta, ordine) in enumerate([("natural order (ub = 12)", list(R(3))),
                                             (f"optimal sequence (z = {frazione(z7)})", ordine_ott)]):
    fine = 0
    for j in ordine:
        ax.barh(riga, t7[j], left=fine, color=CICLO[j], edgecolor="white")
        ax.text(fine + t7[j] / 2, riga, f"job {j + 1}", ha="center", va="center", color="white", fontsize=9)
        fine += t7[j]
        ax.plot([d7[j], d7[j]], [riga - 0.45, riga + 0.45], color=CICLO[j], lw=1.5, ls="--")
ax.set_yticks([0, 1])
ax.set_yticklabels(["natural order", "optimal sequence"])
ax.set_xlabel("time; dashed the due dates $d_j$ (same colour as the job)")
ax.set_title("Total tardiness on one machine")
ax.invert_yaxis()
salva_figura(fig, "cap07_ritardo_gantt")

print("Done.")
