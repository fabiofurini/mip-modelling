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
from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi,
                 stampa_soluzione, valuta)
from stile import CICLO, ROSSO, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("4. Parallel jobs: y_m = maximum of the times of the assigned jobs")
t4 = [[6, 5, 3], [5, 10, 2], [20, 13, 10]]
p4 = [1, 2, 2]
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t4[j][m]}
                         for j in R(3) for m in R(3)]), "fam07_4_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "p": p4}), "fam07_4_macchine")


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
salva_modello(m4, "fam07_4_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp4, zlp4r, _ = rilassamenti(m4)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
d4 = duale_4(t4, p4)
salva_modello(d4, "fam07_4_duale")
mano = {f"lam[{j},{mm}]": 1 / 3 for j in R(3) for mm in R(3)}
mano.update({f"mu[{j}]": min(t4[j][mm] / 3 for mm in R(3)) for j in R(3)})
lb4, viol = valuta(d4, mano)
assert viol <= 1e-9
print("Hand-built dual solution: lam_jm = 1/3, pi = 0, mu_j = min_m t_jm/3 = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  lb = {frazione(lb4)}")
dualita_forte(d4, zlp4)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
xe, ye, passi = euristica_4(t4, p4)
print("Next-fit heuristic on the cardinalities:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub4 = sum(ye)
print(f"  ub = {frazione(ub4)}")

# ---------- 5. OPTIMAL SOLUTION OF THE MILP ----------
z4 = risolvi(m4)
print("Optimal solution of the MILP:")
stampa_soluzione(m4, solo_non_nulle=True)
riga = registra_bound("4 parallel", ub4, lb4, zlp4, zlp4r, z4)
salva_dati(pd.DataFrame([riga]), "fam07_4_bound")

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------


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
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "fam07_4_varianti")

# ---------- 7. THE SANDWICH ON THE VARIANT 4a ----------
intestazione("4a. The sandwich on the variant: minimising the maximum of the times")


def modello_4a(t, p):
    mm_, xx, yy = modello_4(t, p)
    ww = mm_.addVar(name="w")
    mm_.addConstrs((ww - yy[mz] >= 0 for mz in R(len(p))), name="minmax")
    mm_.setObjective(ww, GRB.MINIMIZE)
    return mm_, xx, yy, ww


def duale_4a(t, p):
    """Two things change with respect to the dual of 7.4: y_m no longer has a
    cost, and nu_m >= 0 arrives for the constraint w - y_m >= 0. The columns
    become  x_jm: mu_j + pi_m - t_jm lam_jm <= 0;  y_m: sum_j lam_jm - nu_m <= 0;
    w: sum_m nu_m <= 1."""
    nn, kk = len(t), len(p)
    d = nuovo_modello("duale_parallelo_4a")
    mu = d.addVars(nn, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(kk, lb=-GRB.INFINITY, ub=0.0, name="pi")
    lam = d.addVars(nn, kk, name="lam")
    nu = d.addVars(kk, name="nu")
    d.setObjective(mu.sum() + gp.quicksum(p[mz] * pi[mz] for mz in R(kk)), GRB.MAXIMIZE)
    d.addConstrs((mu[j] + pi[mz] - t[j][mz] * lam[j, mz] <= 0
                  for j in R(nn) for mz in R(kk)), name="rc_x")
    d.addConstrs((lam.sum("*", mz) - nu[mz] <= 0 for mz in R(kk)), name="rc_y")
    d.addConstr(nu.sum() <= 1, name="rc_w")
    return d


m4a, x4a, y4a, w4a = modello_4a(t4, p4)
salva_modello(m4a, "fam07_4a_primale")

# -- feasible heuristic: the same assignment, read with the new objective --
print("Constructive heuristic: the assignment of the base problem is feasible here too;")
print("only its evaluation changes, because now the maximum counts and not the sum.")
assegnazione = sorted(xe)
carichi = [max([t4[j][mz] for (j, q) in assegnazione if q == mz] + [0]) for mz in R(3)]
ub4a = max(carichi)
sol_4a = ({f"x[{j},{mz}]": 1 for (j, mz) in assegnazione}
          | {f"y[{mz}]": carichi[mz] for mz in R(3)} | {"w": ub4a})
assert ammissibile(m4a, sol_4a), "the heuristic solution of the variant must be feasible"
print(f"  times per machine {carichi}  ->  ub = {frazione(ub4a)}")

# -- dual certificate: all the weight on the longest job --
d4a = duale_4a(t4, p4)
salva_modello(d4a, "fam07_4a_duale")
# with a single job priced, lam_jm = nu_m and mu_j <= min_m t_jm nu_m: the nu that
# maximises that minimum makes t_jm nu_m constant, that is nu_m proportional to 1/t_jm
lungo = max(R(3), key=lambda j: min(t4[j]))
somma_inversi = sum(1 / t4[lungo][mz] for mz in R(3))
nu_b = {mz: (1 / t4[lungo][mz]) / somma_inversi for mz in R(3)}
mano_4a = {f"nu[{mz}]": nu_b[mz] for mz in R(3)}
mano_4a.update({f"lam[{lungo},{mz}]": nu_b[mz] for mz in R(3)})
mano_4a[f"mu[{lungo}]"] = 1 / somma_inversi
lb4a, viol_4a = valuta(d4a, mano_4a)
assert viol_4a <= 1e-9, viol_4a
print(f"Dual solution by hand: only job {lungo + 1} is priced, the longest one on every")
print("  machine. With lam_jm = nu_m the column of w gives sum_m nu_m <= 1, and")
print("  the nu maximising min_m t_jm nu_m makes that product constant: nu_m is")
print("  proportional to 1/t_jm. The bound is the harmonic mean of the times of that job,")
print(f"  1 / sum_m (1/t_jm) = {frazione(lb4a)}.")
zlp4a, zlp4ar, _ = due_rilassamenti(m4a, d4a)
z4a = risolvi(m4a)
riga_4a = registra_bound("4a min-max of the times", ub4a, lb4a, zlp4a, zlp4ar, z4a)
salva_dati(pd.DataFrame([riga_4a]), "fam07_4a_bound")
assert lb4a <= zlp4a <= z4a <= ub4a + 1e-9


print("Fine.")


print("Done.")
