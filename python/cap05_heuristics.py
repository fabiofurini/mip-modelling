"""Chapter 5 -- Constructive heuristics: the six families, with trace and bound.

Every heuristic of the course on a minimal instance: the step-by-step trace (the
same text that ends up in the notes), the feasibility check of the solution
produced --- constraints, bounds *and* integrality --- and the comparison with
the optimum of the corresponding MILP. It ends with a local-search step and with
the case where the constructive heuristic fails although the problem is feasible.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from euristiche import (best_fit, first_fit, euristica_copertura, euristica_lotti, euristica_zaino,
                        lpt, matrice, next_fit)
from mip import (ammissibile, frazione, nuovo_modello, rilassamento, risolvi,
                 stampa_soluzione, valuta, viola_interezza)
from stile import (ARANCIO, BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione,
                   plt, salva_dati, salva_figura)

R = range
CONFRONTO = []


def confronta(nome, senso, valore_eur, zmilp, note=""):
    gap = abs(valore_eur - zmilp) / abs(zmilp) if abs(zmilp) > 1e-9 else 0.0
    ruolo = "ub" if senso == "min" else "lb"
    print(f"  {nome:34s} heuristic = {frazione(valore_eur):>6} ({ruolo})   "
          f"z(MILP) = {frazione(zmilp):>6}   gap = {100 * gap:.1f}%  {note}")
    CONFRONTO.append({"heuristic": nome, "sense": senso, "heuristic_value": valore_eur,
                      "role": ruolo, "z_milp": zmilp, "gap": gap})


# ---------- 1. BIN PACKING: NEXT-FIT, FIRST-FIT, BEST-FIT ----------
intestazione("5.1  The three bin-packing heuristics on jobs and machines")
t51 = [[2, 1, 3], [3, 4, 2], [4, 5, 3]]
c51 = [[5, 10, 2], [5, 4, 6], [5, 4, 6]]
a51 = [5, 6, 7]


def modello_assegnamento(t, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("assignment")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(c[j][mm] * x[j, mm] for j in R(n) for mm in R(k)), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assign")
    m.addConstrs((gp.quicksum(t[j][mm] * x[j, mm] for j in R(n)) <= a[mm] for mm in R(k)),
                 name="availability")
    return m, x


m51, x51 = modello_assegnamento(t51, c51, a51)
z51 = risolvi(m51)
for nome, e in [("next-fit", next_fit(t51, a51)),
                ("first-fit", first_fit(t51, a51)),
                ("best-fit (minimum cost)", best_fit(t51, a51, lambda j, mm, ra: c51[j][mm], "cost"))]:
    valore = sum(c51[j][mm] for (j, mm) in e.x)
    sol = {f"x[{j},{mm}]": 1 for (j, mm) in e.x}
    assert ammissibile(m51, sol), nome           # constraints, bounds AND integrality
    confronta(f"5.1 {nome}", "min", valore, z51)
print("  Trace of the best-fit (the text that appears in the notes):")
best_fit(t51, a51, lambda j, mm, ra: c51[j][mm], "cost").traccia.stampa()

# ---------- 2. LPT: BALANCING OVER IDENTICAL MACHINES ----------
intestazione("5.2  LPT: the makespan on identical machines")
t52 = [5, 5, 4, 4, 3, 3, 3]
k52 = 3
e52 = lpt(t52, k52)
e52.traccia.stampa()
m52 = nuovo_modello("makespan")
x52 = m52.addVars(len(t52), k52, vtype=GRB.BINARY, name="x")
T52 = m52.addVar(name="T")
m52.setObjective(T52, GRB.MINIMIZE)
m52.addConstrs((x52.sum(j, "*") == 1 for j in R(len(t52))), name="assign")
m52.addConstrs((T52 >= gp.quicksum(t52[j] * x52[j, mm] for j in R(len(t52))) for mm in R(k52)),
               name="max")
z52 = risolvi(m52)
sol52 = {f"x[{j},{mm}]": 1 for (j, mm) in e52.x} | {"T": e52.makespan}
assert ammissibile(m52, sol52)
confronta("5.2 LPT (makespan)", "min", e52.makespan, z52,
          f"loads {[int(c) for c in e52.carichi]}, total {sum(t52)}")
print(f"  Elementary bound: the makespan is at least max(max_j t_j, total/k) = "
      f"max({max(t52)}, {frazione(sum(t52) / k52)}) = {frazione(max(max(t52), sum(t52) / k52))}")

# ---------- 3. COVERING GREEDY ----------
intestazione("5.3  Constructive covering heuristic")
c53 = [4, 3, 5, 3]
S53 = [[0, 1], [1, 2], [0, 2], [0, 3], [1, 3], [2, 3]]
e53 = euristica_copertura(c53, S53)
e53.traccia.stampa()
m53 = nuovo_modello("covering")
x53 = m53.addVars(len(c53), vtype=GRB.BINARY, name="x")
m53.setObjective(gp.quicksum(c53[j] * x53[j] for j in R(len(c53))), GRB.MINIMIZE)
m53.addConstrs((gp.quicksum(x53[j] for j in S53[i]) >= 1 for i in R(len(S53))), name="cover")
z53 = risolvi(m53)
assert ammissibile(m53, {f"x[{j}]": e53.y[j] for j in R(len(c53))})
confronta("5.3 covering constructive heuristic", "min", e53.valore, z53,
          f"chosen {[j + 1 for j in R(len(c53)) if e53.y[j]]}")

# ---------- 4. KNAPSACK GREEDY: A LOWER BOUND ----------
intestazione("5.4  Knapsack constructive heuristic: in a maximisation the heuristic gives a lower bound")
p54, w54, C54 = [10, 7, 6, 4], [5, 4, 3, 3], 9
e54 = euristica_zaino(p54, w54, C54)
e54.traccia.stampa()
m54 = nuovo_modello("knapsack")
x54 = m54.addVars(4, vtype=GRB.BINARY, name="x")
m54.setObjective(gp.quicksum(p54[j] * x54[j] for j in R(4)), GRB.MAXIMIZE)
m54.addConstr(gp.quicksum(w54[j] * x54[j] for j in R(4)) <= C54, name="capacity")
z54 = risolvi(m54)
assert ammissibile(m54, {f"x[{j}]": e54.y[j] for j in R(4)})
confronta("5.4 constructive heuristic by ratio p/w", "max", e54.valore, z54,
          f"taken {[j + 1 for j in R(4) if e54.y[j]]}, residual {e54.residuo:g}")

# ---------- 5. LOT SIZING GREEDY ----------
intestazione("5.5  Lot sizing: least unit cost period covering")
d55 = [20, 10, 30, 40, 10]
setup55, hold55 = 50, 1
e55 = euristica_lotti(d55, setup55, hold55)
e55.traccia.stampa()
T55 = len(d55)
m55 = nuovo_modello("lot_sizing")
q55 = m55.addVars(T55, name="q")
I55 = m55.addVars(T55, name="I")
y55 = m55.addVars(T55, vtype=GRB.BINARY, name="y")
Mtot = sum(d55)
m55.setObjective(gp.quicksum(setup55 * y55[t] + hold55 * I55[t] for t in R(T55)), GRB.MINIMIZE)
for t in R(T55):
    m55.addConstr((I55[t - 1] if t else 0) + q55[t] - I55[t] == d55[t], name=f"bilancio{t}")
    m55.addConstr(q55[t] <= Mtot * y55[t], name=f"link{t}")
z55 = risolvi(m55)
sol55 = {}
for t in R(T55):
    sol55[f"q[{t}]"] = e55.lanci.get(t, 0)
    sol55[f"y[{t}]"] = 1 if t in e55.lanci else 0
scorta = 0
for t in R(T55):
    scorta += sol55[f"q[{t}]"] - d55[t]
    sol55[f"I[{t}]"] = scorta
assert ammissibile(m55, sol55)
confronta("5.5 lot sizing (least unit cost)", "min", e55.valore, z55,
          f"runs in periods {[t + 1 for t in sorted(e55.lanci)]}")
print("  Wagner-Whitin solves this very model *to optimality* by dynamic programming:")
print(f"  its value is {frazione(z55)}, not the heuristic one.")

# ---------- 6. A LOCAL SEARCH STEP ----------
intestazione("5.6  A local-search step on the LPT solution")
carichi = list(e52.carichi)
assegn = {j: mm for (j, mm) in e52.x}
migliorato = True
passi = 0
while migliorato:
    migliorato = False
    for j, mm in list(assegn.items()):
        for nuovo in R(k52):
            if nuovo == mm:
                continue
            prova = list(carichi)
            prova[mm] -= t52[j]
            prova[nuovo] += t52[j]
            if max(prova) < max(carichi) - 1e-9:
                print(f"  Moving job {j + 1} from machine {mm + 1} to {nuovo + 1}: "
                      f"makespan {max(carichi):g} -> {max(prova):g}")
                carichi, assegn[j], migliorato, passi = prova, nuovo, True, passi + 1
                break
        if migliorato:
            break
if passi == 0:
    print(f"  No single move improves the makespan {max(carichi):g}: the LPT solution")
    print(f"  is a local optimum for this move. The global optimum is {frazione(z52)}.")
print("  A local optimum is not a global optimum, and local search produces no bound")
print("  better than that of the solution it returns.")

# ---------- 7. WHEN THE GREEDY FAILS ----------
intestazione("5.7  A failure of the constructive heuristic does not prove infeasibility")
t57 = matrice([3, 3, 2], 2)
a57 = [5, 3]
e57 = next_fit(t57, a57)
e57.traccia.stampa()
print(f"  next-fit: ok = {e57.ok}")
m57, x57 = modello_assegnamento(t57, [[1, 1], [1, 1], [1, 1]], a57)
z57 = risolvi(m57)
print(f"  The MILP, however, is feasible, with optimum {frazione(z57)}: solution "
      + ", ".join(f"x[{j+1}][{mm+1}]" for j in R(3) for mm in R(2) if x57[j, mm].X > 0.5))
print("  The constructive heuristic fails because it is myopic, not because the problem has no")
print("  solution: 'no solution found' is not 'no solution exists'.")
assert not e57.ok

# ---------- 8. THE OVERVIEW ----------
intestazione("5.8  The overview")
tab = pd.DataFrame(CONFRONTO)
salva_dati(tab, "cap05_euristiche")
fig, ax = plt.subplots(figsize=(7.6, 3.6))
etichette = [r["heuristic"].split(" ", 1)[1][:22] for r in CONFRONTO]
gap = [100 * r["gap"] for r in CONFRONTO]
colori = [TEAL if r["sense"] == "min" else ARANCIO for r in CONFRONTO]
ax.barh(etichette, gap, color=colori)
for i, g in enumerate(gap):
    ax.annotate(f"{g:.1f}%", (g, i), textcoords="offset points", xytext=(4, -3), fontsize=9)
ax.set_xlabel("heuristic gap with respect to the MILP optimum (%)")
ax.set_title("How good each constructive heuristic is")
ax.invert_yaxis()
ax.set_xlim(0, max(gap) * 1.25 + 1)
salva_figura(fig, "cap05_gap")
print("Done.")
