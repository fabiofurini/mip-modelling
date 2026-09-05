"""Chapter 4 -- Relaxations, duality and bounds: the checked examples.

A minimisation and a maximisation problem, written with their duals; a dual
solution built by hand and the check of weak duality; the comparison between the
relaxation without the bounds and the one with the bounds kept; a cover cut; the
bound read from Gurobi at the end of the solve; and the counterexample showing why the
LP duals are not the marginal prices of the MILP.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 rilassamento, risolvi, stampa_soluzione, valuta, viola_interezza)
from stile import (ARANCIO, BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione,
                   plt, salva_dati, salva_figura)

R = range

# ---------- 1. A MINIMISATION, ITS DUAL, A DUAL SOLUTION BUILT BY HAND ----------
intestazione("4.1  Minimum-cost covering: primal, dual and a bound built by hand")
# min sum c_j x_j   s.t.  sum_{j in S_i} x_j >= 1 for every i,  x binary
c41 = [4, 3, 5, 3]                       # cost of the four teams
# six zones, each on the border between two districts: zone i is covered by the
# two teams of the districts it borders
S41 = [[0, 1], [1, 2], [0, 2], [0, 3], [1, 3], [2, 3]]
n41, m41 = len(c41), len(S41)


def primale_41():
    m = nuovo_modello("covering")
    x = m.addVars(n41, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(c41[j] * x[j] for j in R(n41)), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(x[j] for j in S41[i]) >= 1 for i in R(m41)), name="cover")
    return m, x


def duale_41():
    """max sum u_i  s.t.  sum_{i : j in S_i} u_i <= c_j,  u >= 0."""
    d = nuovo_modello("dual_covering")
    u = d.addVars(m41, name="u")
    d.setObjective(u.sum(), GRB.MAXIMIZE)
    d.addConstrs((gp.quicksum(u[i] for i in R(m41) if j in S41[i]) <= c41[j] for j in R(n41)),
                 name="rc")
    return d, u


m41p, x41 = primale_41()
z41 = risolvi(m41p)
scelte41 = [j + 1 for j in R(n41) if x41[j].X > 0.5]
print(f"  Integer optimum: z(MILP) = {frazione(z41)}, teams chosen {scelte41}")

# dual solution built by hand: each zone gets the smallest unit cost still
# available, respecting the dual constraints one column at a time (dual constructive heuristic)
u_mano = {i: 0.0 for i in R(m41)}
residuo = {j: c41[j] for j in R(n41)}
for i in R(m41):
    incremento = min(residuo[j] for j in S41[i])
    u_mano[i] = incremento
    for j in S41[i]:
        residuo[j] -= incremento
d41, u41 = duale_41()
lb41, viol = valuta(d41, {f"u[{i}]": u_mano[i] for i in R(m41)})
assert viol <= 1e-9, viol
print("  Dual solution by hand (constructive heuristic on the zones): u = "
      + ", ".join(f"u_{i+1} = {frazione(u_mano[i])}" for i in R(m41))
      + f"   ->  lb = {frazione(lb41)}")
zlp41, zlp41r, pi41 = due_rilassamenti(m41p, d41)
print(f"  Weak duality checked: {frazione(lb41)} <= {frazione(zlp41)} <= "
      f"{frazione(z41)}")
assert lb41 <= zlp41 + 1e-9 <= z41 + 1e-9
# primal upper bound: the covering constructive heuristic (one uncovered zone at a time)
scoperte = set(R(m41))
presi41 = []
while scoperte:
    j = min(R(n41), key=lambda j: c41[j] / max(1, len({i for i in scoperte if j in S41[i]}))
            if any(j in S41[i] for i in scoperte) else float("inf"))
    presi41.append(j)
    scoperte -= {i for i in scoperte if j in S41[i]}
ub41_primale = sum(c41[j] for j in presi41)
assert ammissibile(m41p, {f"x[{j}]": 1 for j in presi41})
print(f"  Constructive covering heuristic heuristic: teams {sorted(j + 1 for j in presi41)}, "
      f"ub = {frazione(ub41_primale)}")
riga41 = registra_bound("minimum-cost covering", ub41_primale, lb41, zlp41, zlp41r, z41)
salva_dati(pd.DataFrame([riga41]), "cap04_copertura")

# ---------- 2. A MAXIMISATION: THE ROLES SWAP ----------
intestazione("4.2  A knapsack: the heuristic gives the lower bound, the dual the upper")
p42 = [10, 7, 6, 4]                      # values
w42 = [5, 4, 3, 3]                       # weights
C42 = 9


def primale_42():
    m = nuovo_modello("knapsack")
    x = m.addVars(4, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(p42[j] * x[j] for j in R(4)), GRB.MAXIMIZE)
    m.addConstr(gp.quicksum(w42[j] * x[j] for j in R(4)) <= C42, name="capacity")
    return m, x


def duale_42():
    """Dual of the relaxation without the bounds (x >= 0): min C v  s.t.  w_j v >= p_j, v >= 0."""
    d = nuovo_modello("dual_knapsack")
    v = d.addVar(name="v")
    d.setObjective(C42 * v, GRB.MINIMIZE)
    d.addConstrs((w42[j] * v >= p42[j] for j in R(4)), name="rc")
    return d, v


m42, x42 = primale_42()
z42 = risolvi(m42)
scelte42 = [j + 1 for j in R(4) if x42[j].X > 0.5]
print(f"  Integer optimum: z(MILP) = {frazione(z42)}, items {scelte42}, "
      f"weight {sum(w42[j] for j in R(4) if x42[j].X > 0.5)} out of {C42}")
# constructive heuristic heuristic by value/weight ratio: gives a LOWER bound
ordine = sorted(R(4), key=lambda j: -p42[j] / w42[j])
carico, presi = 0, []
for j in ordine:
    if carico + w42[j] <= C42:
        presi.append(j)
        carico += w42[j]
lb42 = sum(p42[j] for j in presi)
assert ammissibile(m42, {f"x[{j}]": 1 for j in presi})
print(f"  Constructive heuristic by ratio p_j/w_j: takes {sorted(j + 1 for j in presi)}, "
      f"lb = {frazione(lb42)}")
# dual by hand: v = max_j p_j / w_j  (the best ratio) is feasible
v_mano = max(p42[j] / w42[j] for j in R(4))
d42, v42 = duale_42()
ub42, viol = valuta(d42, {"v": v_mano})
assert viol <= 1e-9, viol
print(f"  Dual solution by hand: v = max_j p_j/w_j = {frazione(v_mano)}  ->  "
      f"ub = C v = {frazione(ub42)}")
zlp42, zlp42r, _ = due_rilassamenti(m42, d42)
print(f"  The maximisation sandwich: {frazione(lb42)} <= z(MILP) = {frazione(z42)} <= "
      f"z(LP) = {frazione(zlp42)} <= ub = {frazione(ub42)}")
assert lb42 <= z42 <= zlp42 + 1e-9 <= ub42 + 1e-9
riga42 = registra_bound("knapsack", ub42, lb42, zlp42, zlp42r, z42, senso="max")
salva_dati(pd.DataFrame([riga42]), "cap04_zaino")

# ---------- 3. A COVER CUT ----------
intestazione("4.3  A valid inequality: the cover cut")
from itertools import combinations
tutte = [s for k in R(2, 5) for s in combinations(R(4), k) if sum(w42[j] for j in s) > C42]
coperture = [s for s in tutte                                   # only the minimal ones
             if all(sum(w42[j] for j in t) <= C42
                    for t in combinations(s, len(s) - 1))]
print("  Minimal covers found: "
      + "; ".join("{" + ", ".join(str(j + 1) for j in s) + "}" for s in coperture))
m43, x43 = primale_42()
zlp43_prima, sol43, _ = rilassamento(m43, rafforzato=True)
print("  Optimal solution of the relaxation without cuts: "
      + ", ".join(f"x_{j+1} = {frazione(sol43[f'x[{j}]'])}" for j in R(4)))
for s in coperture:
    somma = sum(sol43[f"x[{j}]"] for j in s)
    stato = "VIOLATED" if somma > len(s) - 1 + 1e-9 else "satisfied"
    print(f"    cut on {{{', '.join(str(j + 1) for j in s)}}}: "
          f"sum = {frazione(somma)} against {len(s) - 1}  ->  {stato}")
for s in coperture:
    m43.addConstr(gp.quicksum(x43[j] for j in s) <= len(s) - 1, name="cover" + "".join(map(str, s)))
z43 = risolvi(m43)
zlp43_dopo, _, _ = rilassamento(m43, rafforzato=True)
print(f"  z(LP+) without cuts = {frazione(zlp43_prima)}   with the cover cuts = "
      f"{frazione(zlp43_dopo)}   z(MILP) = {frazione(z43)}")
assert z43 == z42, "the cuts must not change the integer optimum"
assert zlp43_dopo <= zlp43_prima + 1e-9
salva_dati(pd.DataFrame([{"model": "knapsack", "z_lp_without_cuts": zlp43_prima,
                          "z_lp_with_cuts": zlp43_dopo, "z_milp": z43}]), "cap04_tagli")

# ---------- 4. WHAT THE SOLVER DOES: relax() AND ObjBound ----------
intestazione("4.4  The first relaxation and the solver's final bound")
m44, x44 = primale_41()          # the covering: here the solver has work to do
m44.Params.OutputFlag = 0
m44.optimize()
print(f"  Status = {m44.Status} (2 = OPTIMAL), SolCount = {m44.SolCount}")
print(f"  ObjVal   = {frazione(m44.ObjVal)}   (the best integer solution found)")
print(f"  ObjBound = {frazione(m44.ObjBound)} (the best bound proved)")
print(f"  MIPGap   = {m44.MIPGap:.4f}          NodeCount = {int(m44.NodeCount)}")
zrad, _, _ = rilassamento(m44, rafforzato=True)
print(f"  Relaxation of the model as we wrote it, with relax(): {frazione(zrad)}")
assert abs(m44.ObjBound - m44.ObjVal) <= 1e-6
assert zrad <= m44.ObjVal + 1e-9         # minimisation: the relaxation lies below the optimum
print(f"  The relaxation is {frazione(zrad)} and the integer optimum {frazione(m44.ObjVal)}:")
print("  the gap is there, but NodeCount = 0. Gurobi closes it *at the root*, with")
print("  presolve, its own cuts and heuristics, without ever splitting the problem.")
# to see the solver at work, switch off presolve, cuts and heuristics
m45, x45 = primale_41()
m45.Params.Presolve = 0
m45.Params.Cuts = 0
m45.Params.Heuristics = 0
m45.optimize()
print(f"  With Presolve = Cuts = Heuristics = 0: z = {frazione(m45.ObjVal)}, "
      f"NodeCount = {int(m45.NodeCount)}")
print("  Same optimum, but now the nodes count: 'how hard a model is' is not a")
print("  property of the model alone, it also depends on what the solver brings.")
assert m45.ObjVal == m44.ObjVal
salva_dati(pd.DataFrame([{"configuration": "default settings", "z": m44.ObjVal,
                          "z_lp_written": zrad, "nodes": int(m44.NodeCount)},
                         {"configuration": "no presolve, cuts or heuristics",
                          "z": m45.ObjVal, "z_lp_written": zrad,
                          "nodes": int(m45.NodeCount)}]), "cap04_solver")

# ---------- 5. LP DUALS ARE NOT THE MARGINAL PRICES OF THE MILP ----------
intestazione("4.5  Why the LP duals are not the marginal prices of the MILP")
righe = []
for C in (8, 9, 10, 11, 12):
    m = nuovo_modello("knapsack_C")
    x = m.addVars(4, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(p42[j] * x[j] for j in R(4)), GRB.MAXIMIZE)
    con = m.addConstr(gp.quicksum(w42[j] * x[j] for j in R(4)) <= C, name="capacity")
    z = risolvi(m)
    zr, _, pi = rilassamento(m, rafforzato=True)
    righe.append({"capacity": C, "z_milp": z, "z_lp": zr, "lp_dual": pi["capacity"]})
print("   C   z(MILP)   z(LP+)   LP dual   true change in z(MILP)")
for k, r in enumerate(righe):
    delta = "" if k == 0 else frazione(r["z_milp"] - righe[k - 1]["z_milp"])
    print(f"  {r['capacity']:2d}    {frazione(r['z_milp']):>5}   {frazione(r['z_lp']):>6}   "
          f"{r['lp_dual']:>10.4f}      {delta:>6}")
salva_dati(pd.DataFrame(righe), "cap04_prezzi")
print("  The LP dual is the p_j/w_j ratio of the 'critical' item: 2 when the capacity")
print("  runs out on item 1, 7/4 when there is room left for item 2. It says how much an")
print("  extra unit of capacity is worth *in the continuous problem*. On the integer")
print("  problem the true change is in jumps (1, 0, 3, 3) and never matches that value:")
print("  going from C = 9 to C = 10 the integer optimum does not change at all, while")
print("  the dual keeps promising 7/4. The LP dual is not the marginal price of the")
print("  MILP, and using it as such is a mistake, not an approximation.")

# ---------- 6. FIGURE: THE SANDWICH OF THE TWO PROBLEMS ----------
fig, ax = plt.subplots(figsize=(7.2, 3.4))
etichette = ["covering (min)", "knapsack (max)"]
lb = [lb41, lb42]
ub = [ub41_primale, ub42]
zl = [zlp41, zlp42]
zm = [z41, z42]
for i in R(2):
    ax.plot([lb[i], ub[i]], [i, i], color=GRIGIO, lw=2, solid_capstyle="round")
    ax.plot(lb[i], i, "|", color=TEAL, ms=18, mew=2.5)
    ax.plot(ub[i], i, "|", color=ARANCIO, ms=18, mew=2.5)
    ax.plot(zl[i], i, "d", color=BLU, ms=8)
    ax.plot(zm[i], i, "o", color=ROSSO, ms=9)
ax.plot([], [], "|", color=TEAL, ms=12, mew=2.5, label="lower bound")
ax.plot([], [], "|", color=ARANCIO, ms=12, mew=2.5, label="upper bound")
ax.plot([], [], "d", color=BLU, ms=7, label="$z(\\mathrm{LP})$")
ax.plot([], [], "o", color=ROSSO, ms=8, label="$z(\\mathrm{MILP})$")
ax.set_yticks(R(2))
ax.set_yticklabels(etichette)
ax.set_xlabel("objective value")
ax.set_title("The sandwich: the dual is left in a min, right in a max")
ax.legend(fontsize=8, ncols=4, loc="lower center", bbox_to_anchor=(0.5, -0.42))
ax.set_ylim(-0.6, 1.6)
salva_figura(fig, "cap04_sandwich")
print("Done.")
