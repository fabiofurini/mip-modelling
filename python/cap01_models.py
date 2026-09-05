"""Chapter 1 -- What is a MIP model: relaxation, rounding, bounds.

Numerical check of the chapter's examples: the rounding counterexample, the two
relaxations (pure and with the bounds kept), the integer optimum and the trace
of the branch-and-bound carried out by hand in the text. Every number quoted in
the notes and on the website comes from here.
"""
import gurobipy as gp
import numpy as np
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, frazione, nuovo_modello, rilassamento, risolvi,
                 stampa_soluzione, valuta, viola_interezza)
from stile import BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. THE MODEL OF THE EXAMPLE ----------
intestazione("1. max x1 + x2  s.t.  2x1 + 2x2 <= 3,  x1, x2 binary")


def modello_esempio(binarie=True, superiore=True):
    """Model (1.1) of the chapter.

    binarie=True   -> MILP;  binarie=False -> continuous relaxation
    superiore=True -> the bound x <= 1 is kept (relaxation LP+); False -> only x >= 0
    """
    m = nuovo_modello("rounding")
    tipo = GRB.BINARY if binarie else GRB.CONTINUOUS
    ub = 1.0 if superiore else GRB.INFINITY
    x = m.addVars(2, vtype=tipo, lb=0.0, ub=ub, name="x")
    m.setObjective(x[0] + x[1], GRB.MAXIMIZE)
    m.addConstr(2 * x[0] + 2 * x[1] <= 3, name="resource")
    return m, x


# ---------- 2. THE TWO RELAXATIONS ----------
intestazione("2. The two relaxations: pure (x >= 0) and with the bounds kept (x <= 1)")
m_lp, x_lp = modello_esempio(binarie=False, superiore=False)
zlp = risolvi(m_lp)
print(f"Relaxation without the bounds   z(LP)  = {frazione(zlp)}   solution returned by the solver:")
stampa_soluzione(m_lp)
m_lpp, x_lpp = modello_esempio(binarie=False, superiore=True)
zlpp = risolvi(m_lpp)
vertice = (x_lpp[0].X, x_lpp[1].X)
print(f"Relaxation LP+    z(LP+) = {frazione(zlpp)}   solution returned by the solver: "
      f"({frazione(vertice[0])}, {frazione(vertice[1])})")
print("Both are worth 3/2: the resource constraint already gives x1 + x2 <= 3/2, and")
print("the bound x <= 1 cuts off no point of that segment.")

# every optimal solution of LP+ lies on the segment x1 + x2 = 3/2 inside [0,1]^2
for punto in [(0.75, 0.75), (1.0, 0.5), (0.5, 1.0)]:
    z, viol = valuta(m_lpp, {"x[0]": punto[0], "x[1]": punto[1]})
    assert viol <= 1e-9 and abs(z - 1.5) <= 1e-9
    print(f"  ({frazione(punto[0])}, {frazione(punto[1])}) is feasible for LP+ and is worth "
          f"{frazione(z)}: one of infinitely many optimal solutions.")

# ---------- 3. WHY ROUNDING FAILS ----------
intestazione("3. Rounding the fractional solutions")
m_mip, x_mip = modello_esempio(binarie=True)
for base in [(0.75, 0.75), (1.0, 0.5)]:
    for verso, arr in [("to nearest", lambda v: round(v)), ("downwards", int)]:
        cand = {"x[0]": float(arr(base[0])), "x[1]": float(arr(base[1]))}
        z, viol = valuta(m_mip, cand)
        ok = ammissibile(m_mip, cand)
        print(f"  from ({frazione(base[0])}, {frazione(base[1])}) rounding {verso:11s} -> "
              f"({frazione(cand['x[0]'])}, {frazione(cand['x[1]'])})  "
              f"{'feasible, value ' + frazione(z) if ok else f'INFEASIBLE (violation {viol:g})'}")
assert not ammissibile(m_mip, {"x[0]": 1.0, "x[1]": 1.0})
assert ammissibile(m_mip, {"x[0]": 1.0, "x[1]": 0.0})
# the integrality check really is needed: (1, 1/2) satisfies the linear constraints
assert valuta(m_mip, {"x[0]": 1.0, "x[1]": 0.5})[1] <= 1e-9
assert viola_interezza(m_mip, {"x[0]": 1.0, "x[1]": 0.5}) == 0.5
assert not ammissibile(m_mip, {"x[0]": 1.0, "x[1]": 0.5})
print("  (1, 1/2) satisfies the linear constraints but violates integrality by 1/2:")
print("  continuous feasibility alone does not certify an integer primal bound.")

# ---------- 4. THE INTEGER OPTIMUM ----------
intestazione("4. The integer optimum")
zmilp = risolvi(m_mip)
print(f"z(MILP) = {frazione(zmilp)}   optimal solution:")
stampa_soluzione(m_mip)
print(f"Difference between relaxation and integer optimum: {frazione(zlpp)} - {frazione(zmilp)} = "
      f"{frazione(zlpp - zmilp)}")
salva_dati(pd.DataFrame([{"model": "example 1.1", "z_lp": zlp, "z_lp_rafforzato": zlpp,
                          "z_milp": zmilp}]), "cap01_bound")


# ---------- 5. BRANCH-AND-BOUND BY HAND ----------
intestazione("5. Branch-and-bound: the trace reported in the chapter")


def nodo(fissa: dict):
    """LP+ relaxation of the subproblem whose variables are bounded by `fissa`.

    `fissa` is {index: (lb, ub)}: these are the branches x_j <= floor(v) and
    x_j >= ceil(v).
    """
    m, x = modello_esempio(binarie=False, superiore=True)
    for j, (lo, hi) in fissa.items():
        x[j].LB, x[j].UB = lo, hi
    m.optimize()
    if m.Status != GRB.OPTIMAL:
        return None, None
    return m.ObjVal, (x[0].X, x[1].X)


passi = []
for etichetta, fissa in [("root", {}),
                         ("x1 <= 0", {0: (0.0, 0.0)}),
                         ("x1 >= 1", {0: (1.0, 1.0)}),
                         ("x1 >= 1, x2 <= 0", {0: (1.0, 1.0), 1: (0.0, 0.0)}),
                         ("x1 >= 1, x2 >= 1", {0: (1.0, 1.0), 1: (1.0, 1.0)})]:
    z, sol = nodo(fissa)
    if z is None:
        print(f"  {etichetta:20s} infeasible: the branch is discarded")
        passi.append({"node": etichetta, "z_lp": None, "x1": None, "x2": None, "integer": False})
        continue
    intera = all(abs(v - round(v)) <= 1e-9 for v in sol)
    print(f"  {etichetta:20s} z(LP+) = {frazione(z):>4}   x = ({frazione(sol[0])}, "
          f"{frazione(sol[1])}){'   integer solution: candidate incumbent' if intera else '   fractional: branch'}")
    passi.append({"node": etichetta, "z_lp": z, "x1": sol[0], "x2": sol[1], "integer": intera})
salva_dati(pd.DataFrame(passi), "cap01_branch")
assert passi[0]["z_lp"] == 1.5 and passi[1]["z_lp"] == 1.0 and passi[2]["z_lp"] == 1.5
assert passi[3]["z_lp"] == 1.0 and passi[4]["z_lp"] is None
print("  The final incumbent is worth 1: it is the optimum, and no subproblem is left open.")

# ---------- 6. FIGURE: THE FEASIBLE REGION AND THE INTEGER POINTS ----------
fig, ax = plt.subplots(figsize=(5.4, 5.0))
poligono = [(0, 0), (1, 0), (1, 0.5), (0.5, 1), (0, 1)]
ax.fill(*zip(*poligono), color=TEAL, alpha=0.16, zorder=1, label="relaxation LP$^+$")
ax.plot([0.25, 1.5], [1.25, 0.0], color=TEAL, lw=1.6, zorder=2, label="$2x_1 + 2x_2 = 3$")
for (p, q) in [(0, 0), (1, 0), (0, 1)]:
    ax.plot(p, q, "o", color=VERDE, ms=11, zorder=4)
    ax.annotate(f"({p},{q})", (p, q), textcoords="offset points", xytext=(9, 9),
                fontsize=9, color=VERDE)
ax.plot(1, 1, "X", color=ROSSO, ms=12, zorder=4)
ax.annotate("(1,1): $2+2 > 3$", (1, 1), textcoords="offset points", xytext=(-92, 10),
            fontsize=9, color=ROSSO)
for (p, q), testo in [((0.75, 0.75), "$(3/4,3/4)$"), ((1.0, 0.5), "$(1,1/2)$")]:
    ax.plot(p, q, "s", color=BLU, ms=7, zorder=4)
    ax.annotate(testo, (p, q), textcoords="offset points", xytext=(8, -14), fontsize=9, color=BLU)
ax.plot([], [], "o", color=VERDE, ms=9, label="feasible integer points")
ax.plot([], [], "X", color=ROSSO, ms=9, label="infeasible integer point")
ax.plot([], [], "s", color=BLU, ms=6, label="optimal solutions of the relaxation")
ax.set_xlim(-0.15, 1.45)
ax.set_ylim(-0.15, 1.45)
ax.set_xlabel("$x_1$")
ax.set_ylabel("$x_2$")
ax.set_title("Relaxation LP$^+$ and integer points\n$z(\\mathrm{LP}^+) = 3/2$, $z(\\mathrm{MILP}) = 1$")
ax.legend(loc="upper right", fontsize=8)
ax.set_aspect("equal")
salva_figura(fig, "cap01_rilassamento")
print("Done.")
