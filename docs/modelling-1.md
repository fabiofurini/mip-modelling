# What is a MIP model

**Class:** LP · ILP · BIP · MILP · **Script:** `python/cap01_models.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap01_models.ipynb)

## Data, variables, objective, constraints

A *mathematical programming* model translates a decision into four ingredients,
always in the same order: the **data** (the numbers known before deciding), the
**variables** (what the decision maker controls), the **objective** (a function
of the variables to minimise or maximise) and the **constraints** (the equations
and inequalities that make a solution feasible).

!!! note "Notation for optimal values"
    $X$ is the **feasible set** (the points satisfying all constraints, domains
    included); $z(\mathrm{MILP})$, $z(\mathrm{LP})$, $z(\mathrm{D})$ are the
    optimal values of the MILP, of its relaxation and of the dual of the
    relaxation. Solutions **built by hand** carry a bar ($\bar x$), **optimal**
    ones a tilde ($\tilde x$). The bounds are called $LB$ and
    $UB$, whatever the direction of the objective. We always write
    $z(\mathrm{MILP})$ and never $z^\star$: which model is being optimised must
    be explicit.

**Classes of models.** **LP** if objective and constraints are linear and the
variables continuous; **ILP** if all variables are integer; **BIP** if all are
$0/1$; **MILP** if some are integer or binary and others continuous. This course
works almost exclusively with MILPs.

## Why integrality matters

$$
\begin{aligned}
\max ~~ x_1 + x_2 & & \\
\text{subject to} \quad 2x_1 + 2x_2 &\le 3, & \\
x_1,\ x_2 &\in \{0,1\}. &
\end{aligned}
$$

The LP relaxation replaces $x_1, x_2 \in \{0,1\}$ by $0 \le x_1, x_2 \le 1$ and
is worth $z(\mathrm{LP}^+) = 3/2$. That value is attained by **infinitely many**
optimal solutions — every point of the segment $x_1 + x_2 = 3/2$ inside the
square — among them $(3/4, 3/4)$, $(1, 1/2)$ and $(1/2, 1)$. Which one the
solver returns depends on the algorithm: on our installation Gurobi gives
$(1/2, 1)$.

Rounding $(3/4, 3/4)$ to the nearest integer gives $(1,1)$, which violates the
constraint ($2+2 = 4 > 3$): it is **not even feasible**. Rounding $(1, 1/2)$
gives $(1, 0)$, feasible with value $1$ — which is exactly the integer optimum,
$z(\mathrm{MILP}) = 1$.

![The relaxation and the integer points](img/cap01_rilassamento.png)

Two distinct lessons: rounding can produce **infeasible** points, and when it
produces feasible ones there is no guarantee on their value; and the difference
$3/2 - 1 = 1/2$ is not the fault of rounding — no feasible integer point is
worth more than $1$.

## The two relaxations, and which side they are on

!!! note "Two versions not to be confused"
    - **relaxation without the bounds** $z(\mathrm{LP})$: $x \in \{0,1\}$ becomes $x \ge 0$
      alone. This is the one whose dual the exercises write by hand.
    - **relaxation with the bounds** $z(\mathrm{LP}^+)$: $x \in \{0,1\}$
      becomes $0 \le x \le 1$. This is Gurobi's `relax()` and the root
      relaxation of branch-and-bound.

    In a maximisation
    $z(\mathrm{LP}) \ge z(\mathrm{LP}^+) \ge z(\mathrm{MILP})$; in a
    minimisation the directions are reversed. The two coincide when the other
    constraints already imply $x \le 1$ — for instance with an assignment
    constraint $\sum_m x_{jm} = 1$.

The relaxation **removes** constraints, hence

$$X_{\mathrm{MILP}} \subseteq X_{\mathrm{LP}^+} \subseteq X_{\mathrm{LP}},$$

and optimising over a larger set cannot give a worse value. In a maximisation
the relaxation is an *upper* bound, in a minimisation a *lower* bound: in both
cases it is an **optimistic** bound.

!!! warning "Which side each bound comes from"
    The dual of the relaxation does **not** give a bound "from the other side".
    By weak duality, in a minimisation every feasible dual solution is worth at
    most $z(\mathrm{LP})$, hence at most $z(\mathrm{MILP})$: it sits on the
    *same* side as the relaxation. The bound from the other side — the
    *pessimistic* one — comes only from a feasible solution of the MILP, that
    is, from a heuristic or from the solver. In a **minimisation**:

    $$z(\mathrm{D}) \le z(\mathrm{LP}) \le z(\mathrm{LP}^+) \le z(\mathrm{MILP}) \le c'\bar x$$

    for every feasible integer $\bar x$; in a **maximisation** all directions
    are reversed.

## Three "gaps" not to be confused

1. **Heuristic gap**, when the optimum is known:
   $|z_{\text{heur}} - z(\mathrm{MILP})| / |z(\mathrm{MILP})|$. It is the one
   reported in the exercise tables.
2. **Certified gap** between two known bounds, without knowing the optimum:
   $(\mathit{UB} - \mathit{LB})/|\mathit{UB}|$ for a minimisation with
   $\mathit{UB} > 0$. It guarantees the optimum lies in the interval, not that
   it is close to either end.
3. **The solver's `MIPGap`**: the same idea, computed by Gurobi from its own
   `ObjVal` and `ObjBound` and with its tolerances.

The numerator is always taken in absolute value; if the denominator is zero the
relative gap is not written and the absolute difference is reported.

## Three patterns that keep coming back

| Name | Constraint | Meaning |
|---|---|---|
| **set partitioning** | $\sum_{i \in I} x_i = 1$ | exactly one element of $I$ |
| **set packing** | $\sum_{i \in I} x_i \le 1$ | at most one element of $I$ |
| **set covering** | $\sum_{i \in I} x_i \ge 1$ | at least one element of $I$ |

Problem [7.1](scheduling-1.md) uses a *partitioning* for every job,
[7.3](scheduling-3.md) a *packing*, and [chapter 2](modelling-2.md) shows
*covering* as the direct translation of an OR clause.

## Branch-and-bound in one page

For a **minimisation** problem:

1. solve the LP relaxation of the subproblem: if infeasible, discard it; if the
   solution is integer it becomes a candidate **incumbent**;
2. otherwise choose a fractional variable $x_j = v$ and **branch** into
   $x_j \le \lfloor v \rfloor$ and $x_j \ge \lceil v \rceil$: every integer
   solution satisfies one of the two, and none both;
3. **prune** a subproblem whose relaxation is worth more than the incumbent;
4. terminate when no open subproblems remain.

With binary variables the tree has at most $2^n$ leaves and the algorithm
certainly terminates; with unbounded integer variables termination is not
guaranteed.

!!! example "The trace on the example (a maximisation: prune what is worth *less*)"
    - **Root.** $z(\mathrm{LP}^+) = 3/2$ with $(1/2, 1)$: $x_1$ is fractional.
    - **Branch $x_1 \le 0$.** Optimum $x_2 = 1$, value $1$, integer: incumbent.
    - **Branch $x_1 \ge 1$.** Optimum $x_2 = 1/2$, value $3/2$: still
      fractional. The sub-branch $x_2 \le 0$ gives $(1,0)$ of value $1$, which
      does not improve; the sub-branch $x_2 \ge 1$ is infeasible.
    - **End.** $z(\mathrm{MILP}) = 1$, proved. The five relaxations are solved by
      the script and saved in `data/cap01_branch.csv`.

## What this chapter leaves open

| Question | Where it is answered |
|---|---|
| How are logical conditions translated into linear constraints? | [Chapter 2](modelling-2.md) |
| How are different families of variables linked to each other? | [Chapter 3](links.md) |
| How is an optimistic bound built by hand? | [Chapter 4](modelling-4.md) |
| How is a feasible solution built quickly? | [Chapter 5](modelling-5.md) |
| How is all of this written in Python/Gurobi, and how are the results read? | [Chapter 6](modelling-6.md) |

## Code

The complete script — the two relaxations, the rounding, the branch-and-bound
trace and the figure — is
[`python/cap01_models.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/cap01_models.py)
(reproducible with `python3 python/cap01_models.py` from the `python/` folder).
The same code is available as a notebook —
[`notebooks/cap01_models.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/cap01_models.ipynb)
— which opens in Colab from the badge at the top of the page.

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/cap01_models.py` (155 lines)"

    ```python
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
    ```

<!-- embedded-script: end -->
