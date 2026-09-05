"""Chapter 6 -- From the model to Python/Gurobi: how it is written and read.

The four classes of variables, one addConstrs per family of constraints, and
above all how to read the results: Status, SolCount, ObjVal, ObjBound, MIPGap,
NodeCount, the time limit, the tolerances and relax(). It closes with the full
protocol of the course on a minimal instance.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from euristiche import best_fit
from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 rilassamento, risolvi, stampa_lp, stampa_soluzione, valuta, viola_interezza)
from stile import (ARANCIO, BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione,
                   plt, salva_dati, salva_figura)

R = range

# ---------- 1. THE FOUR CLASSES OF VARIABLES ----------
intestazione("1. The four classes of variables and their domains")
m = nuovo_modello("variable_types")
b = m.addVar(vtype=GRB.BINARY, name="binary")
i = m.addVar(vtype=GRB.INTEGER, lb=0, ub=10, name="integer")
c = m.addVar(lb=0.0, ub=GRB.INFINITY, name="continuous")
l = m.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="free")
m.update()
for v in m.getVars():
    print(f"  {v.VarName:9s} VType = {v.VType}   lb = {v.LB:>6.1f}   ub = "
          f"{'+inf' if v.UB >= GRB.INFINITY else f'{v.UB:.1f}':>6s}")
print("  GRB.BINARY already implies lb = 0 and ub = 1: there is no need to state them.")
print("  A continuous variable has lb = 0 by default: free variables must be declared")
print("  explicitly with lb = -GRB.INFINITY (the duals of an equality constraint).")

# ---------- 2. A MODEL, ONE FAMILY OF CONSTRAINTS AT A TIME ----------
intestazione("2. The model is written one family of constraints per block")
t = [[2, 1, 3], [3, 4, 2], [4, 5, 3]]
co = [[5, 10, 2], [5, 4, 6], [5, 4, 6]]
a = [5, 6, 7]
n, k = 3, 3


def modello(t, co, a):
    """Problem 7.1: one addConstrs per family, with the label as its name."""
    mm = nuovo_modello("assignment")
    x = mm.addVars(n, k, vtype=GRB.BINARY, name="x")          # data -> variables
    mm.setObjective(gp.quicksum(co[j][h] * x[j, h] for j in R(n) for h in R(k)), GRB.MINIMIZE)
    mm.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assign")
    mm.addConstrs((gp.quicksum(t[j][h] * x[j, h] for j in R(n)) <= a[h] for h in R(k)),
                  name="availability")
    return mm, x


m2, x2 = modello(t, co, a)
m2.update()
print(f"  Variables: {m2.NumVars}   constraints: {m2.NumConstrs}   nonzeros: {m2.NumNZs}")
print("  Constraint names (the same labels as the mathematical model):")
print("   " + ", ".join(cc.ConstrName for cc in m2.getConstrs()))
print("  The instance model in LP format, to check the tables in the notes:")
import io
import os
import tempfile
with tempfile.TemporaryDirectory() as d:
    percorso = os.path.join(d, "modello.lp")
    m2.write(percorso)
    testo_lp = open(percorso).read()
for riga in [r for r in testo_lp.splitlines() if r.strip()][:8]:
    print("    " + riga)
print("    ...")

# ---------- 3. READING THE RESULTS: THE NORMAL CASE ----------
intestazione("3. Reading the results when everything goes well")
m2.optimize()
print(f"  Status   = {m2.Status}   (2 = OPTIMAL)")
print(f"  SolCount = {m2.SolCount}   (how many integer solutions were found)")
print(f"  ObjVal   = {frazione(m2.ObjVal)}   ObjBound = {frazione(m2.ObjBound)}   "
      f"MIPGap = {m2.MIPGap:.6f}")
print(f"  NodeCount = {int(m2.NodeCount)}   Runtime = {m2.Runtime:.3f} s")
print("  Optimal solution (nonzero variables only):")
stampa_soluzione(m2, solo_non_nulle=True)
z_ott = m2.ObjVal

# ---------- 4. READING THE RESULTS WHEN THINGS GO WRONG ----------
intestazione("4. The three cases in which ObjVal cannot be read")
# (a) infeasible
m3, x3 = modello(t, co, [1, 1, 1])          # insufficient availability
m3.optimize()
print(f"  (a) availability (1,1,1): Status = {m3.Status} (3 = INFEASIBLE), "
      f"SolCount = {m3.SolCount}")
print("      ObjVal does not exist: reading it raises an error. Read Status first, always.")
assert m3.Status == GRB.INFEASIBLE
# (b) time limit with no solution found
m4, x4 = modello(t, co, a)
m4.Params.TimeLimit = 0.0
m4.optimize()
print(f"  (b) TimeLimit = 0: Status = {m4.Status} (9 = TIME_LIMIT), SolCount = {m4.SolCount}")
print(f"      ObjBound = {m4.ObjBound if m4.ObjBound > -GRB.INFINITY else '-inf'}: "
      f"not even the bound has been computed.")
# (c) stopped with one solution found: the useful case
m5, x5 = modello(t, co, a)
m5.Params.SolutionLimit = 1                 # stops at the first integer solution
m5.optimize()
print(f"  (c) SolutionLimit = 1: Status = {m5.Status} (10 = SOLUTION_LIMIT), "
      f"SolCount = {m5.SolCount}")
if m5.SolCount > 0:
    print(f"      ObjVal = {frazione(m5.ObjVal)}  ObjBound = {frazione(m5.ObjBound)}  "
          f"MIPGap = {m5.MIPGap:.4f}")
    print("      This is the only case in which an interval is reported: the optimum")
    print("      lies between ObjBound and ObjVal, and MIPGap measures its width.")
salva_dati(pd.DataFrame([
    {"case": "optimal", "status": m2.Status, "sol_count": m2.SolCount, "obj_val": m2.ObjVal,
     "obj_bound": m2.ObjBound, "mip_gap": m2.MIPGap},
    {"case": "infeasible", "status": m3.Status, "sol_count": m3.SolCount,
     "obj_val": None, "obj_bound": None, "mip_gap": None},
    {"case": "time limit, no solution", "status": m4.Status,
     "sol_count": m4.SolCount, "obj_val": None, "obj_bound": None, "mip_gap": None},
    {"case": "first solution", "status": m5.Status, "sol_count": m5.SolCount,
     "obj_val": m5.ObjVal if m5.SolCount else None,
     "obj_bound": m5.ObjBound, "mip_gap": m5.MIPGap if m5.SolCount else None},
]), "cap06_stati")

# ---------- 5. TOLERANCES ----------
intestazione("5. Tolerances: 'integer' means 'integer within IntFeasTol'")
m6, x6 = modello(t, co, a)
print(f"  IntFeasTol  = {m6.Params.IntFeasTol:g}  (how far a binary may be from 0 or 1)")
print(f"  FeasibilityTol = {m6.Params.FeasibilityTol:g}  (violation allowed on the constraints)")
print(f"  OptimalityTol  = {m6.Params.OptimalityTol:g}  (tolerance on the reduced costs)")
print(f"  MIPGap (target) = {m6.Params.MIPGap:g}  (it stops when the gap falls below)")
m6.optimize()
peggiore = max(min(abs(v.X - round(v.X)), 1) for v in m6.getVars())
print(f"  On the returned solution, the largest distance from an integer is {peggiore:.2e}")
print("  In the text one writes 1, not 0.9999999997: values are rounded when they are")
print("  reported, and comparisons use a tolerance (1e-6 in this course).")

# ---------- 6. THE RELAXATION WITH relax() ----------
intestazione("6. relax(): the relaxation of the model we wrote")
zlp_r, sol_r, pi_r = rilassamento(m6, rafforzato=True)
zlp_p, _, _ = rilassamento(m6, rafforzato=False)
print(f"  z(LP+) = {frazione(zlp_r)}   (relax(): the binaries become 0 <= x <= 1)")
print(f"  z(LP)  = {frazione(zlp_p)}   (relaxation without the bounds: x <= 1 is dropped too)")
print("  Relaxation duals read from Gurobi:")
for nome, valore in pi_r.items():
    if abs(valore) > 1e-9:
        print(f"    {nome}: {valore:.4f}")
print("  relax() copies the model: pending changes must be applied first with")
print("  m.update(), otherwise an old version is relaxed.")

# ---------- 7. THE COURSE PROTOCOL, FROM START TO FINISH ----------
intestazione("7. The protocol: data -> model -> heuristic -> LP and dual -> MIP -> table")
# (1) data  ->  (2) model
m7, x7 = modello(t, co, a)
# (3) heuristic and its check
e = best_fit(t, a, lambda j, h, ra: co[j][h], "cost")
ub = sum(co[j][h] for (j, h) in e.x)
sol_eur = {f"x[{j},{h}]": 1 for (j, h) in e.x}
assert ammissibile(m7, sol_eur), "the heuristic solution must be feasible AND integer"
print(f"  (3) best-fit heuristic: ub = {frazione(ub)}, feasibility checked "
      f"(constraints, bounds and integrality)")
# (4) LP and the dual written by hand
d = nuovo_modello("dual")
mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
d.setObjective(mu.sum() + gp.quicksum(a[h] * pi[h] for h in R(k)), GRB.MAXIMIZE)
d.addConstrs((mu[j] + t[j][h] * pi[h] <= co[j][h] for j in R(n) for h in R(k)), name="rc")
mano = {f"mu[{j}]": min(co[j]) for j in R(n)}
lb, viol = valuta(d, mano)
assert viol <= 1e-9
print(f"  (4) dual solution by hand: lb = {frazione(lb)}, feasible for the dual")
zlp, zlp_raff, _ = due_rilassamenti(m7, d)
# (5) the MIP
z = risolvi(m7)
# (6) the table
riga = registra_bound("7.1 assignment", ub, lb, zlp, zlp_raff, z)
salva_dati(pd.DataFrame([riga]), "cap06_protocollo")
assert lb <= zlp <= z <= ub + 1e-9
print("  (7) the table row is the one above, and it is saved to CSV: that is where")
print("      the notes, the website and check_numbers.py read it from.")

# ---------- 8. FIGURE: THE FOUR NUMBERS OF THE PROTOCOL ----------
fig, ax = plt.subplots(figsize=(7.2, 2.6))
ax.plot([lb, ub], [0, 0], color=GRIGIO, lw=3, solid_capstyle="round")
for valore, colore, testo, dy in [(lb, TEAL, "$\\mathrm{lb}$ (dual by hand)", 14),
                                  (zlp, BLU, "$z(\\mathrm{LP})$", -20),
                                  (z, ROSSO, "$z(\\mathrm{MILP})$", 14),
                                  (ub, ARANCIO, "$\\mathrm{ub}$ (heuristic)", -20)]:
    ax.plot(valore, 0, "o", color=colore, ms=10)
    ax.annotate(f"{testo}\n{frazione(valore)}", (valore, 0), textcoords="offset points",
                xytext=(0, dy), ha="center", fontsize=9, color=colore)
ax.set_yticks([])
ax.set_ylim(-0.8, 0.8)
ax.set_xlim(lb - 0.5, ub + 0.5)
ax.set_xlabel("objective value")
ax.set_title("The four numbers every Part II exercise produces")
ax.spines["left"].set_visible(False)
ax.grid(False)
salva_figura(fig, "cap06_protocollo")
print("Done.")
