"""EX 1 -- An eight-seat van: which group of tourists to accept (family 10).

A knapsack with two extra constraints: at most two groups accepted, and the
implication "if I accept group 2 I must also accept group 4". It is the chance to
see, on a tiny case, the three techniques of chapter 3 that are needed here:
capacity (3.1), counting (3.4) and logical precedence (3.9).
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, stampa_lp, valuta)
from stile import ARANCIO, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 1. An eight-seat van: which groups to accept")
a0 = [2, 3, 4, 5]          # people in each group
p0 = [30, 50, 80, 70]      # offer in euros
K0 = 8                     # seats of the van
G0 = 2                     # at most two groups
IMP = (1, 3)               # accepting group 2 (index 1) forces group 4 (index 3)
n0 = len(a0)
salva_dati(pd.DataFrame({"group": R(1, n0 + 1), "people": a0, "offer": p0}), "ex01_dati")


def modello(a, p, K, G, imp):
    n = len(a)
    m = nuovo_modello("van")
    x = m.addVars(n, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(p[j] * x[j] for j in R(n)), GRB.MAXIMIZE)
    m.addConstr(gp.quicksum(a[j] * x[j] for j in R(n)) <= K, name="seats")
    m.addConstr(gp.quicksum(x[j] for j in R(n)) <= G, name="groups")
    m.addConstr(x[imp[0]] - x[imp[1]] <= 0, name="implication")
    return m, x


def duale(a, p, K, G, imp):
    """min K alpha + G beta  s.t.  a_j alpha + beta (+gamma if j=2, -gamma if j=4) >= p_j."""
    n = len(a)
    d = nuovo_modello("dual_van")
    alpha = d.addVar(name="alpha")     # seats
    beta = d.addVar(name="beta")       # number of groups
    gamma = d.addVar(name="gamma")     # implication
    d.setObjective(K * alpha + G * beta, GRB.MINIMIZE)
    for j in R(n):
        segno = 1 if j == imp[0] else (-1 if j == imp[1] else 0)
        d.addConstr(a[j] * alpha + beta + segno * gamma >= p[j], name=f"rc[{j}]")
    return d


m0, x0 = modello(a0, p0, K0, G0, IMP)
print("  The model of the instance:")
stampa_lp(m0)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
# constructive heuristic on the decreasing offer: a group is accepted only if all the constraints stay
# satisfied, the implication included (group 2 enters only with group 4 already in)
def euristica(a, p, K, G, imp):
    n = len(a)
    x = [0] * n
    passi = []
    for j in sorted(R(n), key=lambda j: (-p[j], j)):
        x[j] = 1
        posti = sum(a[k] * x[k] for k in R(n))
        gruppi = sum(x)
        ok_imp = x[imp[0]] <= x[imp[1]]
        motivi = []
        if posti > K:
            motivi.append(f"{posti} seats would be needed out of {K}")
        if gruppi > G:
            motivi.append(f"there would be {gruppi} groups out of {G}")
        if not ok_imp:
            motivi.append(f"group {imp[0] + 1} forces accepting group {imp[1] + 1}")
        if motivi:
            x[j] = 0
            passi.append(f"group {j + 1} (offer {p[j]}): rejected, " + "; ".join(motivi))
        else:
            passi.append(f"group {j + 1} (offer {p[j]}): accepted "
                         f"({posti} seats taken, {gruppi} groups)")
    return x, passi


x_eur, passi = euristica(a0, p0, K0, G0, IMP)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
lb0 = sum(p0[j] * x_eur[j] for j in R(n0))
sol_eur = {f"x[{j}]": x_eur[j] for j in R(n0)}
assert ammissibile(m0, sol_eur), sol_eur
print(f"  Heuristic solution: groups {[j + 1 for j in R(n0) if x_eur[j]]}   "
      f"lb = {frazione(lb0)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d0 = duale(a0, p0, K0, G0, IMP)
# recipe: only the seats are priced (beta = gamma = 0), at the highest price per seat
alpha_min = max(p0[j] / a0[j] for j in R(n0))
mano = {"alpha": alpha_min, "beta": 0.0, "gamma": 0.0}
ub0, viol = valuta(d0, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: beta = gamma = 0 and alpha = max_j p_j / a_j (a seat is worth what")
print("  the group paying best pays for it), so every constraint a_j alpha >= p_j holds:")
for j in R(n0):
    print(f"    group {j + 1}: {p0[j]} / {a0[j]} = {frazione(p0[j] / a0[j])}")
print(f"  alpha = {frazione(alpha_min)}  ->  ub = {K0} * alpha = {frazione(ub0)}")
zlp0, zlp0r, _ = due_rilassamenti(m0, d0)

# ---------- 4. OPTIMUM OF THE MILP AND BOUND TABLE ----------
z0 = risolvi(m0)
acc = [j + 1 for j in R(n0) if x0[j].X > 0.5]
print(f"  Optimal solution: groups {acc}, "
      f"{int(sum(a0[j] * x0[j].X for j in R(n0)))} seats taken out of {K0}, revenue "
      f"{frazione(z0)}")
riga = registra_bound("EX 1 van", ub0, lb0, zlp0, zlp0r, z0, senso="max")
salva_dati(pd.DataFrame([riga]), "ex01_bound")
assert lb0 <= z0 <= zlp0r <= zlp0 <= ub0 + 1e-9

# ---------- 5. WHAT EACH CONSTRAINT CONTRIBUTES ----------
intestazione("EX 1. The contribution of each constraint")
prove = []
for nome, togli in [("complete model", []), ("without the limit on groups", ["groups"]),
                    ("without the implication", ["implication"]),
                    ("without both", ["groups", "implication"])]:
    m, x = modello(a0, p0, K0, G0, IMP)
    m.update()
    for c in list(m.getConstrs()):
        if c.ConstrName in togli:
            m.remove(c)
    m.update()
    z = risolvi(m)
    scelti = [j + 1 for j in R(n0) if x[j].X > 0.5]
    print(f"  {nome:32s} z = {frazione(z):>4}   groups {scelti}")
    prove.append({"variant": nome, "z": z, "groups": " ".join(map(str, scelti))})
salva_dati(pd.DataFrame(prove), "ex01_vincoli")
assert prove[0]["z"] <= prove[1]["z"] and prove[0]["z"] <= prove[2]["z"]

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.4, 2.9))
idx = list(R(n0))
colori = [TEAL if x0[j].X > 0.5 else GRIGIO for j in idx]
ax.bar(idx, p0, 0.55, color=colori)
for j in idx:
    if x_eur[j]:
        ax.plot(j, p0[j] + 3, marker="v", color=ARANCIO, ms=8)
    ax.annotate(f"{a0[j]} seats", (j, 3), ha="center", fontsize=8, color="white")
ax.plot([], [], marker="v", ls="", color=ARANCIO, label="chosen by the heuristic")
ax.bar([], [], color=TEAL, label="accepted at the optimum")
ax.bar([], [], color=GRIGIO, label="rejected at the optimum")
ax.set_xticks(idx)
ax.set_xticklabels([f"group {j + 1}" for j in idx])
ax.set_ylabel("offer (euros)")
ax.set_title(f"EX 1: heuristic {frazione(lb0)} <= optimum {frazione(z0)} <= dual "
             f"{frazione(ub0)}")
ax.legend(fontsize=8, loc="upper left")
salva_figura(fig, "ex01_ottimo")
print("Done.")
