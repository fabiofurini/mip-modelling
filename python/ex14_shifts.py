"""EX 14 -- Shifts in an emergency department (family 12).

Cyclic covering: seven shift patterns, one per starting day, each with four full
days, one half-service day and two rest days. It is a set covering with
coefficients 1 and 1/2 and integer, non-binary variables.

The dual is written once and solved by hand with the best-ratio recipe: all the
days at the same price, the highest one that no pattern can beat.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, stampa_lp, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. DATA, COSTS AND COVERING MATRIX ----------
intestazione("EX 14. Emergency department shifts: covering the demand at minimum cost")
GIORNI = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
b13 = [10, 8, 12, 9, 9, 7, 8]          # full-time equivalents required
costo_giorno = [100, 100, 100, 100, 100, 110, 130]
ng = 7

# pattern starting on day j: full on days j..j+3, half service on j+4
a13 = [[0.0] * ng for _ in R(ng)]      # a13[i][j] = share of day i covered by pattern j
for j in R(ng):
    for k in R(4):
        a13[(j + k) % ng][j] = 1.0
    a13[(j + 4) % ng][j] = 0.5
c13 = [sum(costo_giorno[(j + k) % ng] for k in R(4)) + costo_giorno[(j + 4) % ng] / 2
       for j in R(ng)]
print("  Weekly cost of each shift pattern:")
for j in R(ng):
    pieni = ", ".join(GIORNI[(j + k) % ng] for k in R(4))
    print(f"    pattern {j + 1} (starts {GIORNI[j]}): full {pieni}; half service "
          f"{GIORNI[(j + 4) % ng]}  ->  {frazione(c13[j])} euros")
salva_dati(pd.DataFrame({"pattern": R(1, ng + 1), "start": GIORNI, "cost": c13}),
           "ex14_schemi")
salva_dati(pd.DataFrame({"day": GIORNI, "demand": b13}), "ex14_fabbisogno")


def modello(a, b, c):
    n = len(c)
    m = nuovo_modello("shifts")
    x = m.addVars(n, vtype=GRB.INTEGER, name="x")
    m.setObjective(gp.quicksum(c[j] * x[j] for j in R(n)), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(a[i][j] * x[j] for j in R(n)) >= b[i] for i in R(len(b))),
                 name="day")
    return m, x


def duale(a, b, c):
    """max sum_i b_i pi_i  s.t.  sum_i a_ij pi_i <= c_j,  pi >= 0."""
    n = len(c)
    d = nuovo_modello("dual_shifts")
    pi = d.addVars(len(b), name="pi")
    d.setObjective(gp.quicksum(b[i] * pi[i] for i in R(len(b))), GRB.MAXIMIZE)
    d.addConstrs((gp.quicksum(a[i][j] * pi[i] for i in R(len(b))) <= c[j] for j in R(n)),
                 name="rc")
    return d


m13, x13 = modello(a13, b13, c13)
print("  The model of the instance:")
stampa_lp(m13)

# ---------- 2. COVERING HEURISTIC (UPPER BOUND) ----------
# constructive heuristic: while some demand is uncovered, one more copy of the pattern with the lowest
# cost per unit of demand actually covered is added
def euristica(a, b, c):
    n, ng = len(c), len(b)
    x = [0] * n
    residuo = list(map(float, b))
    passi = []
    while max(residuo) > 1e-9:
        def utile(j):
            return sum(min(a[i][j], residuo[i]) for i in R(ng))
        cand = [j for j in R(n) if utile(j) > 1e-9]
        j = min(cand, key=lambda j: (c[j] / utile(j), j))
        x[j] += 1
        coperto = utile(j)
        for i in R(ng):
            residuo[i] = max(0.0, residuo[i] - a[i][j])
        passi.append(f"pattern {j + 1}: covers {frazione(coperto)} of demand at "
                     f"{frazione(c[j])} euros ({frazione(c[j] / coperto)} per unit); "
                     f"residual " + " ".join(frazione(r) for r in residuo))
    return x, passi


x_eur, passi = euristica(a13, b13, c13)
print(f"  The constructive heuristic adds {len(passi)} shifts; here are the first three, one in the middle "
      "and the last one:")
for k in (1, 2, 3, len(passi) // 2, len(passi)):
    print(f"    Step {k}. {passi[k - 1]}")
ub13 = sum(c13[j] * x_eur[j] for j in R(ng))
sol_eur = {f"x[{j}]": x_eur[j] for j in R(ng)}
assert ammissibile(m13, sol_eur), sol_eur
print("  Heuristic solution: " + ", ".join(f"{x_eur[j]} of pattern {j + 1}" for j in R(ng)
                                           if x_eur[j])
      + f"   ub = {frazione(ub13)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
d13 = duale(a13, b13, c13)
# best-ratio recipe: the same price t on all the days. Every pattern covers
# 4 + 1/2 = 9/2 person-days, so the dual constraint is (9/2) t <= c_j: the largest
# feasible t is min_j c_j / (9/2).
copertura = sum(a13[i][0] for i in R(ng))
t = min(c13[j] / copertura for j in R(ng))
mano = {f"pi[{i}]": t for i in R(ng)}
lb13, viol = valuta(d13, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: every pattern covers {frazione(copertura)} person-days, so the")
print(f"  dual constraint is {frazione(copertura)} * t <= c_j for every pattern. The largest")
print(f"  feasible value is t = min_j c_j / ({frazione(copertura)}):")
for j in R(ng):
    print(f"    pattern {j + 1}: {frazione(c13[j])} / ({frazione(copertura)}) = "
          f"{frazione(c13[j] / copertura)}")
print(f"  that is t = {frazione(t)}, and lb = t * sum_i b_i = {frazione(t)} * {sum(b13)} = "
      f"{frazione(lb13)}")
zlp13, zlp13r, _ = due_rilassamenti(m13, d13)

# ---------- 4. OPTIMUM OF THE MILP ----------
z13 = risolvi(m13)
print("  Optimal solution: " + ", ".join(f"{int(x13[j].X)} of pattern {j + 1}"
                                         for j in R(ng) if x13[j].X > 0.5))
copertura_ott = [sum(a13[i][j] * x13[j].X for j in R(ng)) for i in R(ng)]
print("  Coverage per day: " + ", ".join(
    f"{GIORNI[i]} {frazione(copertura_ott[i])} out of {b13[i]}" for i in R(ng)))
riga = registra_bound("EX 14 shifts", ub13, lb13, zlp13, zlp13r, z13)
salva_dati(pd.DataFrame([riga]), "ex14_bound")
assert lb13 <= zlp13 <= z13 <= ub13 + 1e-9

# ---------- 5. TWO READINGS OF THE RESULT ----------
intestazione("EX 14. Two readings of the result")
print(f"  z(LP) = {frazione(zlp13)} and z(MILP) = {frazione(z13)}: the difference "
      f"{frazione(z13 - zlp13)} is the price of integrality, that is of the fact that people")
print("  are hired one at a time.")
# without the half-service day: four full days and three rest days
a_senza = [[0.0] * ng for _ in R(ng)]
for j in R(ng):
    for k in R(4):
        a_senza[(j + k) % ng][j] = 1.0
c_senza = [sum(costo_giorno[(j + k) % ng] for k in R(4)) for j in R(ng)]
m_s, x_s = modello(a_senza, b13, c_senza)
z_senza = risolvi(m_s)
rapporto_con = min(c13[j] / copertura for j in R(ng))
rapporto_senza = min(c_senza[j] / 4 for j in R(ng))
print("  Without the half-service day (four full days and three rest days) the optimal cost")
print(f"  becomes {frazione(z_senza)}, against {frazione(z13)}. The minimum price per day")
print(f"  covered is the same in the two contracts ({frazione(rapporto_con)} with the half")
print(f"  service, {frazione(rapporto_senza)} without), but the half day falls on a fixed day")
print("  and often ends up where the coverage is already there: the flexibility lost costs")
print("  more than the extra coverage is worth.")
assert z_senza < z13
salva_dati(pd.DataFrame([{"variant": "pattern with half service", "z": z13},
                         {"variant": "pattern without half service", "z": z_senza}]),
           "ex14_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
idx = list(R(ng))
ax.bar(idx, b13, 0.55, color=GRIGIO, label="demand")
ax.plot(idx, copertura_ott, marker="o", color=TEAL, lw=1.6, label="coverage at the optimum")
ax.plot(idx, [sum(a13[i][j] * x_eur[j] for j in R(ng)) for i in idx], marker="^",
        color=ARANCIO, lw=1.2, ls="--", label="coverage of the heuristic")
ax.set_xticks(idx)
ax.set_xticklabels(GIORNI)
ax.set_ylabel("full-time equivalents")
ax.set_title(f"EX 14: cost {frazione(z13)} against heuristic {frazione(ub13)}")
ax.legend(fontsize=8)
salva_figura(fig, "ex14_copertura")
print("Done.")
