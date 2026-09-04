"""Shared utilities of the course: solver, LP relaxation, dual, bounds and checks.

Every chapter script imports from here. One solver only: Gurobi.
(Function names are shared with the Italian version, so the two scripts stay parallel.)
"""
from fractions import Fraction

import gurobipy as gp
from gurobipy import GRB

TOL = 1e-6


def nuovo_modello(nome: str = "model") -> gp.Model:
    """A silent Gurobi model."""
    m = gp.Model(nome)
    m.Params.OutputFlag = 0
    return m


def risolvi(m: gp.Model) -> float:
    """Solves to optimality and returns the optimal value (error if not optimal)."""
    m.optimize()
    if m.Status != GRB.OPTIMAL:
        raise RuntimeError(f"{m.ModelName}: Gurobi status {m.Status}, expected OPTIMAL")
    return m.ObjVal


def rilassamento(m: gp.Model, rafforzato: bool = True):
    """Solves the LP relaxation of a MILP.

    With `rafforzato=True` (what the solver does with m.relax()) the binary
    variables stay in [0, 1]; with `rafforzato=False` the upper bounds are dropped
    too, i.e. x in {0,1} is relaxed to x >= 0 only: this is the relaxation whose
    dual the lecture notes write by hand, and its optimum equals the optimum of
    that dual (strong duality).

    Returns (z_lp, solution, duals): the solution is {variable name: value},
    the duals are {constraint name: Pi}.
    """
    m.update()               # relax() copies the model: pending changes must be applied first
    r = m.relax()
    r.Params.OutputFlag = 0
    if not rafforzato:
        for v, v0 in zip(r.getVars(), m.getVars()):
            if v0.VType in (GRB.BINARY, GRB.INTEGER) and v0.LB == 0 and v0.UB == 1:
                v.UB = GRB.INFINITY
    r.optimize()
    if r.Status != GRB.OPTIMAL:
        raise RuntimeError(f"relaxation of {m.ModelName}: Gurobi status {r.Status}")
    sol = {v.VarName: v.X for v in r.getVars()}
    pi = {c.ConstrName: c.Pi for c in r.getConstrs()}
    return r.ObjVal, sol, pi


def valuta(m: gp.Model, sol: dict):
    """Objective value and maximum violation of a given solution.

    `sol` is {variable name: value}; variables not named are 0.
    Used for heuristic (primal) solutions and for hand-built dual solutions:
    the dual is written as a Gurobi model and evaluated here.
    """
    m.update()
    val = {v.VarName: float(sol.get(v.VarName, 0.0)) for v in m.getVars()}
    obj = m.getObjective()
    z = obj.getConstant() + sum(obj.getCoeff(i) * val[obj.getVar(i).VarName]
                                for i in range(obj.size()))
    viol = 0.0
    for v in m.getVars():
        viol = max(viol, v.LB - val[v.VarName], val[v.VarName] - v.UB)
    for c in m.getConstrs():
        riga = m.getRow(c)
        lhs = sum(riga.getCoeff(i) * val[riga.getVar(i).VarName] for i in range(riga.size()))
        if c.Sense == GRB.LESS_EQUAL:
            viol = max(viol, lhs - c.RHS)
        elif c.Sense == GRB.GREATER_EQUAL:
            viol = max(viol, c.RHS - lhs)
        else:
            viol = max(viol, abs(lhs - c.RHS))
    return z, viol


def ammissibile(m: gp.Model, sol: dict) -> bool:
    return valuta(m, sol)[1] <= TOL


def frazione(x: float) -> str:
    """A number as a reduced fraction (or integer), as in the notes: 25/4, 7, 5/6."""
    f = Fraction(x).limit_denominator(10_000)
    return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def tabella_bound(ub, lb, zlp, zmilp, senso: str = "min", zlp_r=None) -> str:
    """Summary line of the bounds: ub, lb, z(LP), [z(LP+)], z(MILP) and heuristic gap.

    For a minimisation ub comes from the heuristic and lb from the dual; for a
    maximisation the roles swap (the heuristic gives a lower bound). `senso`
    only affects the gap, which is always |heuristic value - optimum| / |optimum|.
    z(LP) is the "pure" relaxation (x >= 0), z(LP+) the strengthened one (x <= 1).
    """
    eur = ub if senso == "min" else lb
    gap = abs(eur - zmilp) / abs(zmilp) if abs(zmilp) > TOL else 0.0
    extra = f"   z(LP+) = {frazione(zlp_r):>8}" if zlp_r is not None else ""
    return (f"  ub = {frazione(ub):>8}   lb = {frazione(lb):>8}   z(LP) = {frazione(zlp):>8}{extra}"
            f"   z(MILP) = {frazione(zmilp):>6}   heuristic gap = {100 * gap:.1f}%")


def stampa_soluzione(m: gp.Model, solo_non_nulle: bool = False) -> None:
    """Prints the variables of a solved model (x~ = optimal solution)."""
    for v in m.getVars():
        if solo_non_nulle and abs(v.X) < TOL:
            continue
        print(f"    {v.VarName} = {frazione(v.X)}")


def stampa_lp(m: gp.Model) -> None:
    """The instance model in LP format (to check the tabulars of the notes)."""
    import os
    import tempfile
    m.update()
    with tempfile.TemporaryDirectory() as d:
        percorso = os.path.join(d, "model.lp")
        m.write(percorso)
        print(open(percorso).read())


def due_rilassamenti(m, d):
    """Pure z(LP) (= optimum of the hand-written dual) and the solver's strengthened z(LP+).

    `m` is the primal model, `d` its dual (hand-written, as a stand-alone
    Gurobi model): the function checks that the two optima coincide (strong
    duality) and prints both relaxations.
    """
    zlp, _, pi = rilassamento(m, rafforzato=False)
    zlp_r, _, _ = rilassamento(m, rafforzato=True)
    zd = risolvi(d)
    assert abs(zlp - zd) <= 1e-6, (zlp, zd)
    print(f"Dual optimum = z(LP) (strong duality): {frazione(zd)};  strengthened relaxation "
          f"with x <= 1: z(LP+) = {frazione(zlp_r)}")
    return zlp, zlp_r, pi


def registra_bound(nome, ub, lb, zlp, zlp_r, zmilp, senso="min"):
    """Print the bound row and return the record to save as CSV."""
    print(tabella_bound(ub, lb, zlp, zmilp, senso, zlp_r))
    return {"problem": nome, "ub": ub, "lb": lb, "z_lp": zlp, "z_lp_rafforzato": zlp_r,
            "z_milp": zmilp}
