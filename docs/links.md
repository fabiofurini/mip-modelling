# Links between variables

**Class:** modelling techniques · **Script:** `python/cap03_links.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap03_links.ipynb)

[Chapter 2](modelling-2.md) links variables that are **all binary**. Here we
link **different** families: binary with continuous, binary with integer,
continuous with each other. There are fourteen techniques, and they are the real
content of MIP modelling.

!!! note "How to read each technique"
    (a) the **link in words**; (b) the **linear constraints** that say it, with
    their count; (c) the **proof** — in both directions if both are imposed by
    the constraints, with an exchange argument if one follows from optimality,
    with a *counterexample* when a converse is false; (d) the **strength of the
    relaxation** on a minimal instance solved by the script; (e) the `gurobipy`
    line and the pointers to the Part II problems.

!!! warning "Two properties never to be confused"
    A property **imposed by the constraints** holds for *every* feasible
    solution, optimal or not, and is proved by looking at the constraints alone.
    A property **of optimality** holds only in optimal solutions, and is proved
    by an *exchange argument*: take a feasible solution that violates it, build
    a modified solution, check that it stays feasible and compare the values. If
    the value improves **strictly** the conclusion is "in every optimum"; if it
    merely does not worsen it is "there exists an optimum", which is weaker.
    Writing "in every optimum" when the coefficient is only non-negative is the
    commonest mistake in this chapter.

<div class="grid cards" markdown>

-   **3.1 Activation**

    ---

    $x_{ij} \le y_j$ or $\sum_i x_{ij} \le k_j y_j$: more rows, tighter
    relaxation.

    [:octicons-arrow-right-24: aggregated or disaggregated](links-01.md)

-   **3.2 Fixed cost**

    ---

    $q_j \le C_j y_j$ with the **right** coefficient: the capacity, not a big-M.

    [:octicons-arrow-right-24: fixed cost and flow](links-02.md)

-   **3.3 Minimum lot**

    ---

    $\ell y_j \le q_j \le C_j y_j$: the semicontinuous variable, and why it is
    invisible in the relaxation.

    [:octicons-arrow-right-24: minimum lot](links-03.md)

-   **3.4 Integer counts**

    ---

    $\sum_i a_i x_i \le K w$ with $w$ integer: rounding up, written without
    writing it.

    [:octicons-arrow-right-24: how many boxes](links-04.md)

-   **3.5 Maximum variable**

    ---

    $z \ge t_j x_j$: the constraint gives $\ge$, the objective gives equality —
    if $z$ appears nowhere else.

    [:octicons-arrow-right-24: the maximum auxiliary](links-05.md)

-   **3.6 Min-max and max-min**

    ---

    Three fairness objectives describing the same solution with different
    numbers, and not comparable.

    [:octicons-arrow-right-24: min-max, max-min, range](links-06.md)

-   **3.7 Absolute value**

    ---

    In the objective it costs two constraints and no binary; as a $\ge$
    constraint it is a disjunction, and the binary is needed.

    [:octicons-arrow-right-24: the absolute value](links-07.md)

-   **3.8 Big-M**

    ---

    $a'x \le b + M(1-y)$: valid, improvable, smallest proved. And what happens
    if $M$ is too small.

    [:octicons-arrow-right-24: conditional constraints](links-08.md)

-   **3.9 Precedences**

    ---

    "Either one first or the other", with $M$ equal to the sum of the durations
    and the horizon declared.

    [:octicons-arrow-right-24: sequencing](links-09.md)

-   **3.10 If and only if**

    ---

    One direction from the constraint, the other from the objective — and what
    happens when the bonus is zero.

    [:octicons-arrow-right-24: if and only if](links-10.md)

-   **3.11 Counting types**

    ---

    "At least two different types": without the threshold $\ell$ the count says
    nothing.

    [:octicons-arrow-right-24: counting types](links-11.md)

-   **3.12 Alldiff and expansion**

    ---

    Double partitioning (exact relaxation) and binary expansion (which tightens
    nothing).

    [:octicons-arrow-right-24: alldiff](links-12.md)

-   **3.13 Soft constraints**

    ---

    $a'x + s^- - s^+ = \beta$ with penalties: from an infeasible model to a
    useful one.

    [:octicons-arrow-right-24: penalties](links-13.md)

-   **3.14 Piecewise functions**

    ---

    Convex combination plus adjacency: without it, one ends up below the graph.

    [:octicons-arrow-right-24: cost brackets](links-14.md)

</div>

## The map of techniques

Read from the first column ("what I want to say") to the second ("how it is
written"); the last two recall what must be declared and where the technique is
seen at work.

| Technique | Formulation | To be declared | Seen again in |
|---|---|---|---|
| [3.1 activation](links-01.md) | $x_{ij} \le y_j$ (disagg.) or $\sum_i x_{ij} \le k_j y_j$ (agg.) | which form and why; sign of $f_j$ for the optimality direction | 7.2, 7.3, 7.5, 8.4 |
| [3.2 fixed cost](links-02.md) | $q_j \le C_j y_j$ | that $C_j$ is the capacity, not a big-M | 8.1, ch. 9 |
| [3.3 minimum lot](links-03.md) | $\ell y_j \le q_j \le C_j y_j$ | that $\ell \le C_j$; that the relaxation is unaffected | 7.2.2, 9.1, 9.3 |
| [3.4 integer count](links-04.md) | $\sum_i a_i x_i \le K w$, $w$ integer | that integrality realises the ceiling | 9.2, 12.1, 12.2 |
| [3.5 maximum auxiliary](links-05.md) | $z \ge t_j x_j$, $z \ge 0$ | that $z$ appears nowhere else; its sign in the objective | 7.4, 7.7, 8.4, 11.4 |
| [3.6 min-max / max-min](links-06.md) | $T \ge L_k$ and $\min T$; $U \le L_k$ and $\max U$ | which of the three objectives, and that they are not comparable | 7.4.1, 11.2, 11.3 |
| [3.7 absolute value](links-07.md) | $d \ge \pm(u-v)$ in the objective; disjunction if $\ge k$ | whether it is objective or constraint, and in which direction | 11.2, 11.3 |
| [3.8 big-M](links-08.md) | $a'x \le b + M(1-y)$ | the value of $M$ computed from the data | 7.7, 3.9 |
| [3.9 precedences](links-09.md) | $s_{ij}+s_{ji}=1$, $\kappa_i \ge \kappa_j + t_i - M(1-s_{ij})$ | the horizon and $M = \sum_h t_h$ | 7.7 |
| [3.10 if and only if](links-10.md) | $y \le x_j$ and $y \ge \sum_j x_j - (p-1)$ | whether the second direction is needed or follows from optimality | 7.6, 9.3 |
| [3.11 counting types](links-11.md) | $\ell y_j \le q_j \le C_j y_j$, $\sum_j y_j \ge p$ | that without the threshold $\ell$ the count is empty | 9.3, 10.2, 12.1 |
| [3.12 alldiff / expansion](links-12.md) | double partitioning; $v = \sum_k 2^k b_k$ | that alldiff has an exact relaxation | EX 9, EX 15 |
| [3.13 soft constraints](links-13.md) | $a'x + s^- - s^+ = \beta$ with penalties | the two signs of the penalties | 9.1, EX 15 |
| [3.14 piecewise function](links-14.md) | convex combination $+$ adjacency | whether $g$ is convex; otherwise adjacency is mandatory | 10.1 |

!!! tip "The three questions to ask about a new link"
    1. **Which direction is imposed by the constraints and which is not?**
       Answered by looking at the constraints alone, one case per value of the
       binary.
    2. **Does the missing direction follow from optimality?** Answered by the
       exchange argument, and the answer depends on the *sign* of the
       coefficient in the objective: strictly nonzero gives "in every optimum",
       zero gives at most "there exists an optimum".
    3. **How strong is the relaxation?** Answered by comparing
       $z(\mathit{LP}^+)$ with $z(\mathit{MILP})$ on a small instance and, when
       there are two formulations, by comparing them with each other — after
       proving them equivalent on integer points.

## Code

Every minimal instance of these fourteen pages is solved by
[`python/cap03_links.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/cap03_links.py),
which saves the summary table to `data/cap03_tecniche.csv`. The notebook is
[`notebooks/cap03_links.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/cap03_links.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/cap03_links.py` (490 lines)"

    ```python
    """Chapter 3 -- Links between variables: one checked example per technique.

    Fourteen techniques for linking families of variables. For each one: a minimal
    instance, the model, the integer optimum, the LP+ relaxation and --- where two
    formulations of the same integer set exist --- the comparison of their strength.
    Every numerical claim of the chapter comes from here, and every equivalence
    between formulations is checked by enumeration.
    """
    from itertools import product

    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from mip import (ammissibile, frazione, nuovo_modello, rilassamento, risolvi,
                     stampa_soluzione, valuta, viola_interezza)
    from stile import (ARANCIO, BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione,
                       plt, salva_dati, salva_figura)

    R = range
    TAV = []          # one row per technique: (section, technique, z(MILP), z(LP+) of each form)


    def registra(sezione, tecnica, zmilp, forme):
        """forme: {name of the formulation: z(LP+)}."""
        riga = {"section": sezione, "technique": tecnica, "z_milp": zmilp}
        for i, (nome, z) in enumerate(forme.items(), 1):
            riga[f"formulation_{i}"] = nome
            riga[f"z_lp_{i}"] = z
        TAV.append(riga)
        testo = "   ".join(f"{n}: z(LP+) = {frazione(z)}" for n, z in forme.items())
        print(f"  z(MILP) = {frazione(zmilp)}      {testo}")


    # ---------- 1. ACTIVATION: AGGREGATED OR DISAGGREGATED ----------
    intestazione("3.1  Activation: the aggregated link and the disaggregated one")
    f31 = [8, 6]                                   # activation cost of the 2 facilities
    c31 = [[2, 5], [4, 1], [3, 3]]                 # cost of serving customer i from facility j
    n31, m31 = 3, 2


    def modello_attivazione(disaggregato):
        m = nuovo_modello("activation")
        x = m.addVars(n31, m31, vtype=GRB.BINARY, name="x")
        y = m.addVars(m31, vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(f31[j] * y[j] for j in R(m31))
                       + gp.quicksum(c31[i][j] * x[i, j] for i in R(n31) for j in R(m31)),
                       GRB.MINIMIZE)
        m.addConstrs((x.sum(i, "*") == 1 for i in R(n31)), name="assign")
        if disaggregato:
            m.addConstrs((x[i, j] <= y[j] for i in R(n31) for j in R(m31)), name="link")
        else:
            m.addConstrs((x.sum("*", j) <= n31 * y[j] for j in R(m31)), name="link")
        return m, x, y


    forme = {}
    for nome, dis in [("aggregated", False), ("disaggregated", True)]:
        m, x, y = modello_attivazione(dis)
        z31 = risolvi(m)
        forme[nome], _, _ = rilassamento(m, rafforzato=True)
    print("  The two formulations have the same integer set (checked by enumeration):")
    for valori in product((0, 1), repeat=n31 * m31 + m31):
        xv = {(i, j): valori[i * m31 + j] for i in R(n31) for j in R(m31)}
        yv = {j: valori[n31 * m31 + j] for j in R(m31)}
        agg = all(sum(xv[i, j] for i in R(n31)) <= n31 * yv[j] for j in R(m31))
        dis = all(xv[i, j] <= yv[j] for i in R(n31) for j in R(m31))
        assert agg == dis                        # on binary points the two forms coincide
    registra("3.1", "activation, aggregated / disaggregated", z31, forme)
    print("  The number of link constraints is m = 2 in the aggregated form and n m = 6 in")
    print("  the disaggregated one: more rows, tighter relaxation.")

    # ---------- 2. FIXED COST, CAPACITY AND CONTINUOUS FLOW ----------
    intestazione("3.2  Fixed cost, capacity and continuous flow")
    f32, c32, cap32, D32 = [10, 14], [3, 2], [6, 7], 9


    def modello_costofisso(M=None):
        m = nuovo_modello("fixed_cost")
        q = m.addVars(2, name="q")
        y = m.addVars(2, vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(f32[j] * y[j] + c32[j] * q[j] for j in R(2)), GRB.MINIMIZE)
        m.addConstr(q.sum() >= D32, name="demand")
        limite = cap32 if M is None else [M, M]
        m.addConstrs((q[j] <= limite[j] * y[j] for j in R(2)), name="link")
        if M is not None:
            m.addConstrs((q[j] <= cap32[j] for j in R(2)), name="capacity")
        return m, q, y


    forme = {}
    for nome, M in [("with the capacity as coefficient", None), ("with a big-M = 100", 100)]:
        m, q, y = modello_costofisso(M)
        z32 = risolvi(m)
        forme[nome], _, _ = rilassamento(m, rafforzato=True)
    registra("3.2", "fixed cost with capacity", z32, forme)
    print("  Same integer set, same optimum: but the smallest coefficient that works (the")
    print("  capacity) gives a far tighter relaxation than the big-M.")

    # ---------- 3. MINIMUM LOT SIZE AND SEMICONTINUOUS VARIABLE ----------
    intestazione("3.3  Minimum lot size: the semicontinuous variable")
    ell33 = 5


    def modello_lotto(con_soglia=True):
        m = nuovo_modello("minimum_lot")
        q = m.addVars(2, name="q")
        y = m.addVars(2, vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(f32[j] * y[j] + c32[j] * q[j] for j in R(2)), GRB.MINIMIZE)
        m.addConstr(q.sum() >= D32, name="demand")
        m.addConstrs((q[j] <= cap32[j] * y[j] for j in R(2)), name="capacity")
        if con_soglia:
            m.addConstrs((q[j] >= ell33 * y[j] for j in R(2)), name="lot")
        return m, q, y


    esiti33 = {}
    for nome, soglia in [("without minimum lot", False), ("with minimum lot l = 5", True)]:
        m, q, y = modello_lotto(soglia)
        z = risolvi(m)
        zr, _, _ = rilassamento(m, rafforzato=True)
        esiti33[nome] = (z, zr)
        print(f"  {nome:24s} z(MILP) = {frazione(z):>5}   z(LP+) = {frazione(zr):>7}   "
              f"q = ({frazione(q[0].X)}, {frazione(q[1].X)})  y = ({int(y[0].X)}, {int(y[1].X)})")
    z33 = esiti33["with minimum lot l = 5"][0]
    registra("3.3", "minimum lot size / semicontinuous", z33,
             {"with minimum lot": esiti33["with minimum lot l = 5"][1]})
    print("  These are two different problems, not two formulations of the same one: the")
    print("  threshold changes the feasible set and the optimum goes from 44 to 49. The LP+")
    print("  relaxation, however, does not change: with y fractional the constraint")
    print("  q_j >= l y_j never bites, because y_j can drop as far as needed. The threshold")
    print("  is paid entirely on integrality.")

    # ---------- 4. INTEGER COUNTS, MULTIPLE CAPACITY, ROUNDING UP ----------
    intestazione("3.4  Integer counts: how many boxes are needed")
    pezzi34, capienza34 = 17, 5
    m = nuovo_modello("boxes")
    w = m.addVar(vtype=GRB.INTEGER, name="w")
    m.setObjective(w, GRB.MINIMIZE)
    m.addConstr(capienza34 * w >= pezzi34, name="capacity")
    z34 = risolvi(m)
    zr34, _, _ = rilassamento(m, rafforzato=True)
    print(f"  {pezzi34} items, capacity {capienza34}: w >= {pezzi34}/{capienza34} = "
          f"{frazione(pezzi34 / capienza34)}, and w integer gives w = {int(z34)}")
    assert z34 == -(-pezzi34 // capienza34)        # ceil
    registra("3.4", "integer count (rounding up)", z34, {"capacity constraint": zr34})
    print("  The relaxation is 17/5: integrality alone raises the bound by 3/5.")

    # ---------- 5. THE MAXIMUM AUXILIARY VARIABLE ----------
    intestazione("3.5  The variable that equals the maximum")
    t35 = [4, 7, 3]                                # durations of the three jobs
    m = nuovo_modello("maximum")
    xm = m.addVars(3, vtype=GRB.BINARY, name="x")
    zmax = m.addVar(name="z")
    m.setObjective(zmax, GRB.MINIMIZE)
    m.addConstr(xm.sum() >= 2, name="at_least_two")
    m.addConstrs((zmax >= t35[j] * xm[j] for j in R(3)), name="maximum")
    z35 = risolvi(m)
    zr35, _, _ = rilassamento(m, rafforzato=True)
    scelti35 = [j + 1 for j in R(3) if xm[j].X > 0.5]
    print(f"  Jobs chosen {scelti35}; z = {frazione(zmax.X)} = max of the chosen durations "
          f"= {max(t35[j] for j in R(3) if xm[j].X > 0.5)}")
    assert abs(zmax.X - max(t35[j] for j in R(3) if xm[j].X > 0.5)) < 1e-9
    registra("3.5", "maximum auxiliary variable", z35, {"z >= t_j x_j": zr35})
    print("  The constraint only imposes z >= max; it is the objective, which minimises z,")
    print("  that turns it into an equality in every optimal solution.")

    # ---------- 6. MIN-MAX, MAX-MIN AND RANGE ----------
    intestazione("3.6  Min-max, max-min and the range between maximum and minimum")
    p36 = [3, 5, 2, 4, 7]                          # weights to split between 2 workers (total 21)


    def modello_bilanciamento(criterio):
        m = nuovo_modello("balancing")
        a = m.addVars(len(p36), 2, vtype=GRB.BINARY, name="a")
        car = m.addVars(2, name="load")
        m.addConstrs((a.sum(i, "*") == 1 for i in R(len(p36))), name="assign")
        m.addConstrs((car[k] == gp.quicksum(p36[i] * a[i, k] for i in R(len(p36))) for k in R(2)),
                     name="load_def")
        if criterio == "minmax":
            T = m.addVar(name="T")
            m.addConstrs((T >= car[k] for k in R(2)), name="max")
            m.setObjective(T, GRB.MINIMIZE)
        elif criterio == "maxmin":
            L = m.addVar(name="L")
            m.addConstrs((L <= car[k] for k in R(2)), name="min")
            m.setObjective(L, GRB.MAXIMIZE)
        else:                                       # range: maximum minus minimum
            T = m.addVar(name="T")
            L = m.addVar(name="L")
            m.addConstrs((T >= car[k] for k in R(2)), name="max")
            m.addConstrs((L <= car[k] for k in R(2)), name="min")
            m.setObjective(T - L, GRB.MINIMIZE)
        return m, car


    risultati36 = {}
    for criterio in ["minmax", "maxmin", "range"]:
        m, car = modello_bilanciamento(criterio)
        z = risolvi(m)
        risultati36[criterio] = (z, (car[0].X, car[1].X))
        print(f"  {criterio:7s} z = {frazione(z):>5}   loads = "
              f"({frazione(car[0].X)}, {frazione(car[1].X)})   total {sum(p36)}")
    zr36, _, _ = rilassamento(modello_bilanciamento("minmax")[0], rafforzato=True)
    registra("3.6", "min-max / max-min / range", risultati36["minmax"][0], {"min-max": zr36})
    assert risultati36["minmax"][0] == 11 and risultati36["maxmin"][0] == 10
    assert risultati36["range"][0] == 1
    print("  The total 21 is odd: a perfect split does not exist and the best possible is")
    print("  (11, 10). The three versions choose the same split, but their objectives are")
    print("  worth 11, 10 and 1: three different numbers describing the same solution, and")
    print("  they cannot be compared with each other.")

    # ---------- 7. ABSOLUTE VALUE ----------
    intestazione("3.7  The absolute value: in the objective and in a constraint")
    obiettivo37 = list(p36)          # the same instance as the previous section
    m = nuovo_modello("absolute_value")
    a = m.addVars(len(obiettivo37), 2, vtype=GRB.BINARY, name="a")
    car = m.addVars(2, name="load")
    d = m.addVar(name="d")                          # d >= |load_1 - load_2|
    m.addConstrs((a.sum(i, "*") == 1 for i in R(len(obiettivo37))), name="assign")
    m.addConstrs((car[k] == gp.quicksum(obiettivo37[i] * a[i, k] for i in R(len(obiettivo37)))
                  for k in R(2)), name="load_def")
    m.addConstr(d >= car[0] - car[1], name="abs_plus")
    m.addConstr(d >= car[1] - car[0], name="abs_minus")
    m.setObjective(d, GRB.MINIMIZE)
    z37 = risolvi(m)
    zr37, _, _ = rilassamento(m, rafforzato=True)
    print(f"  min |load_1 - load_2| = {frazione(z37)}, with loads "
          f"({frazione(car[0].X)}, {frazione(car[1].X)})")
    assert abs(z37 - abs(car[0].X - car[1].X)) < 1e-9
    registra("3.7", "absolute value in the objective", z37, {"two constraints, d >= +/-(u-v)": zr37})
    m2 = nuovo_modello("abs_constraint")
    u = m2.addVar(ub=10, name="u")
    v = m2.addVar(ub=10, name="v")
    b = m2.addVar(vtype=GRB.BINARY, name="b")
    m2.setObjective(u + v, GRB.MINIMIZE)
    m2.addConstr(u + v >= 6, name="sum")
    m2.addConstr(u - v >= 4 - 20 * (1 - b), name="disj_plus")     # b = 1 -> u - v >= 4
    m2.addConstr(v - u >= 4 - 20 * b, name="disj_minus")          # b = 0 -> v - u >= 4
    z37b = risolvi(m2)
    print(f"  |u - v| >= 4 with u + v >= 6, min u + v: z = {frazione(z37b)}, "
          f"u = {frazione(u.X)}, v = {frazione(v.X)}, b = {int(b.X)}")
    print("  In the objective (minimisation) the absolute value costs two constraints and")
    print("  no binary; as a >= constraint it becomes a disjunction, and the binary is needed.")

    # ---------- 8. BIG-M: CONDITIONAL CONSTRAINTS AND DISJUNCTIONS ----------
    intestazione("3.8  Big-M: how large, and what it changes in the relaxation")
    a38, b38 = [3, 4, 5], 6      # y = 1  =>  3x1 + 4x2 + 5x3 <= 6


    def modello_bigm(M):
        m = nuovo_modello("bigM")
        xb = m.addVars(3, vtype=GRB.BINARY, name="x")
        y = m.addVar(vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(xb[j] for j in R(3)) + y, GRB.MAXIMIZE)
        m.addConstr(gp.quicksum(a38[j] * xb[j] for j in R(3)) <= b38 + M * (1 - y), name="cond")
        return m


    Mmin = sum(a38) - b38        # the smallest valid M: max of the left-hand side minus b
    forme = {}
    for etichetta, M in [(f"smallest M = {Mmin}", Mmin), ("M = 20", 20), ("M = 1000", 1000)]:
        m = modello_bigm(M)
        z38 = risolvi(m)
        forme[etichetta], _, _ = rilassamento(m, rafforzato=True)
        print(f"  {etichetta:18s} z(MILP) = {frazione(z38)}   z(LP+) = {frazione(forme[etichetta])}")
    m = modello_bigm(Mmin - 1)   # M too small: it cuts off feasible solutions
    z_troppo = risolvi(m)
    print(f"  M = {Mmin - 1} (too small) gives z(MILP) = {frazione(z_troppo)} instead of "
          f"{frazione(z38)}:")
    print("  with y = 0 the constraint should disappear and instead 3x1 + 4x2 + 5x3 <= 11")
    print("  remains, which excludes x = (1,1,1). An invalid M does not make the model a")
    print("  little different: it removes feasible solutions from it.")
    assert z_troppo < z38
    registra("3.8", "big-M in a conditional constraint", z38, forme)

    # ---------- 9. PRECEDENCES AND SEQUENCING ----------
    intestazione("3.9  Precedences: the 'either one first or the other' disjunction")
    t39 = [3, 2, 4]
    M39 = sum(t39)
    m = nuovo_modello("sequencing")
    kap = m.addVars(3, name="kappa")                 # completion time
    s = m.addVars(3, 3, vtype=GRB.BINARY, name="s")  # s[i,j] = 1 if j precedes i
    Cmax = m.addVar(name="Cmax")
    m.setObjective(Cmax, GRB.MINIMIZE)
    m.addConstrs((kap[j] >= t39[j] for j in R(3)), name="minimum")
    m.addConstrs((Cmax >= kap[j] for j in R(3)), name="makespan")
    for i in R(3):
        for j in R(i):
            m.addConstr(s[i, j] + s[j, i] == 1, name=f"disj{i}{j}")
            m.addConstr(kap[i] >= kap[j] + t39[i] - M39 * (1 - s[i, j]), name=f"prec{i}{j}")
            m.addConstr(kap[j] >= kap[i] + t39[j] - M39 * (1 - s[j, i]), name=f"prec{j}{i}")
    z39 = risolvi(m)
    zr39, _, _ = rilassamento(m, rafforzato=True)
    print(f"  Three jobs of duration {t39} on one machine: makespan = {frazione(z39)} = "
          f"sum of the durations = {sum(t39)}")
    print("  Completion times: " + ", ".join(f"kappa_{j+1} = {frazione(kap[j].X)}" for j in R(3)))
    assert z39 == sum(t39)
    registra("3.9", "precedences and sequencing (big-M)", z39, {f"M = sum t_j = {M39}": zr39})
    print(f"  The smallest M that works is the sum of the durations, {M39}: a larger M leaves")
    print("  the same integer set and a weaker relaxation.")

    # ---------- 10. IF AND ONLY IF ----------
    intestazione("3.10  'If and only if': one direction from the constraint, one from the objective")
    premio = 9
    ric = [2, 2, 2]


    def modello_iff(entrambi_i_versi, v):
        m = nuovo_modello("iff")
        xj = m.addVars(3, vtype=GRB.BINARY, name="x")
        yc = m.addVar(vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(ric[j] * xj[j] for j in R(3)) + v * yc, GRB.MAXIMIZE)
        m.addConstr(gp.quicksum(xj[j] for j in R(3)) <= 3, name="capacity")
        m.addConstrs((yc <= xj[j] for j in R(3)), name="bonus_up")     # y = 1 => all chosen
        if entrambi_i_versi:                                           # all chosen => y = 1
            m.addConstr(yc >= gp.quicksum(xj[j] for j in R(3)) - 2, name="bonus_down")
        return m, xj, yc


    for v in (premio, 0):
        for nome, versi in [("only y <= x_j", False), ("also y >= sum x_j - 2", True)]:
            m, xj, yc = modello_iff(versi, v)
            z310 = risolvi(m)
            zr310, _, _ = rilassamento(m, rafforzato=True)
            tutti = all(xj[j].X > 0.5 for j in R(3))
            fedele = (round(yc.X) == 1) == tutti
            print(f"  bonus = {v}   {nome:24s} z(MILP) = {frazione(z310):>4}   "
                  f"y = {int(yc.X)}   x = {[int(xj[j].X) for j in R(3)]}   "
                  f"y faithful to 'class complete': {'yes' if fedele else 'NO'}")
    m, xj, yc = modello_iff(True, premio)
    z310 = risolvi(m)
    zr310, _, _ = rilassamento(m, rafforzato=True)
    registra("3.10", "if and only if", z310, {"both directions imposed": zr310})
    print("  With a bonus > 0 the missing direction follows from optimality: in every")
    print("  optimum y = 1 when the three jobs are done, because raising y increases the")
    print("  objective. With bonus = 0 that argument fails and the constraint y <= x_j alone")
    print("  leaves y = 0 with all jobs done: if y must *mean* 'class complete' outside the")
    print("  optimum too, the second constraint has to be written.")

    # ---------- 11. COUNTING THE DIFFERENT TYPES ----------
    intestazione("3.11  Counting how many different types are produced")
    q_max = [10, 10, 10]
    ric311 = [4, 3, 5]
    m = nuovo_modello("types")
    qq = m.addVars(3, name="q")
    yy = m.addVars(3, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(ric311[j] * qq[j] for j in R(3)), GRB.MAXIMIZE)
    m.addConstr(qq.sum() <= 12, name="resource")
    m.addConstrs((qq[j] <= q_max[j] * yy[j] for j in R(3)), name="activate")
    m.addConstr(yy.sum() >= 2, name="at_least_two_types")
    m.addConstrs((qq[j] >= 3 * yy[j] for j in R(3)), name="lot")
    z311 = risolvi(m)
    zr311, _, _ = rilassamento(m, rafforzato=True)
    print("  At least two types in production, minimum lot 3: q = "
          + ", ".join(frazione(qq[j].X) for j in R(3))
          + f"   active types = {int(sum(yy[j].X for j in R(3)))}")
    registra("3.11", "counting the different types", z311, {"activation + threshold": zr311})
    print("  Without the minimum lot, y_j = 1 with q_j = 0 would be feasible and the")
    print("  'at least two types' threshold would say nothing: the two techniques go together.")

    # ---------- 12. ALLDIFF AND BINARY EXPANSION ----------
    intestazione("3.12  Alldiff and binary expansion of an integer variable")
    costo312 = [[4, 2, 5], [3, 6, 1], [7, 3, 2]]
    m = nuovo_modello("alldiff")
    p = m.addVars(3, 3, vtype=GRB.BINARY, name="p")   # p[i,v] = 1 if object i takes value v
    m.setObjective(gp.quicksum(costo312[i][v] * p[i, v] for i in R(3) for v in R(3)), GRB.MINIMIZE)
    m.addConstrs((p.sum(i, "*") == 1 for i in R(3)), name="one_value")
    m.addConstrs((p.sum("*", v) == 1 for v in R(3)), name="alldiff")
    z312 = risolvi(m)
    zr312, _, _ = rilassamento(m, rafforzato=True)
    print("  Alldiff = one set partitioning per row and one per column; z = " + frazione(z312))
    me = nuovo_modello("expansion")
    bb = me.addVars(3, vtype=GRB.BINARY, name="b")
    vv = me.addVar(vtype=GRB.INTEGER, ub=7, name="v")
    me.addConstr(vv == gp.quicksum(2 ** k * bb[k] for k in R(3)), name="expansion")
    me.addConstr(vv >= 5, name="threshold")
    me.setObjective(vv, GRB.MINIMIZE)
    z312b = risolvi(me)
    print(f"  Binary expansion: v = {int(z312b)} = "
          + " + ".join(f"{2 ** k}" for k in R(3) if bb[k].X > 0.5)
          + f"   (b = {[int(bb[k].X) for k in R(3)]})")
    assert z312b == 5 and sum(2 ** k * round(bb[k].X) for k in R(3)) == 5
    registra("3.12", "alldiff / binary expansion", z312, {"double partitioning": zr312})
    assert abs(zr312 - z312) < 1e-9
    print("  Here z(LP+) = z(MILP): the matrix of the double partitioning is totally")
    print("  unimodular, the relaxation already has integer vertices and integrality is free.")

    # ---------- 13. SOFT CONSTRAINTS AND PENALTIES ----------
    intestazione("3.13  Soft constraints: positive and negative deviations with penalties")
    target = [6, 6, 6]
    disp = 15
    pen_su, pen_giu = 3, 2
    m = nuovo_modello("penalties")
    qv = m.addVars(3, name="q")
    su = m.addVars(3, name="s_plus")
    giu = m.addVars(3, name="s_minus")
    m.setObjective(gp.quicksum(pen_su * su[j] + pen_giu * giu[j] for j in R(3)), GRB.MINIMIZE)
    m.addConstr(qv.sum() <= disp, name="resource")
    m.addConstrs((qv[j] + giu[j] - su[j] == target[j] for j in R(3)), name="target")
    z313 = risolvi(m)
    zr313, _, _ = rilassamento(m, rafforzato=True)
    print("  Demand 6 per period, availability 15: q = "
          + ", ".join(frazione(qv[j].X) for j in R(3))
          + "   shortfall = " + ", ".join(frazione(giu[j].X) for j in R(3)))
    print(f"  total penalty = {frazione(z313)}")
    assert abs(sum(giu[j].X for j in R(3)) - 3) < 1e-9
    registra("3.13", "soft constraints with penalties", z313, {"deviations +/-": zr313})
    print("  The two deviations are never both positive in an optimum: the penalties are")
    print("  positive, and reducing both by the same amount stays feasible.")

    # ---------- 14. PIECEWISE LINEAR FUNCTIONS ----------
    intestazione("3.14  Piecewise linear function: cost brackets")
    nodi = [0, 4, 10, 16]                     # breakpoints
    costi = [0, 12, 30, 36]                   # cumulative cost at each breakpoint (quantity discount)
    domanda314 = 13


    def modello_tratti(adiacenza=True):
        """Convex combination with piece binaries (explicit adjacency)."""
        m = nuovo_modello("pieces")
        lam = m.addVars(len(nodi), name="lambda")
        w = m.addVars(len(nodi) - 1, vtype=GRB.BINARY, name="w")
        qtot = m.addVar(name="q")
        m.addConstr(lam.sum() == 1, name="convex")
        m.addConstr(qtot == gp.quicksum(nodi[k] * lam[k] for k in R(len(nodi))), name="abscissa")
        m.setObjective(gp.quicksum(costi[k] * lam[k] for k in R(len(nodi))), GRB.MINIMIZE)
        m.addConstr(qtot >= domanda314, name="demand")
        if adiacenza:
            m.addConstr(w.sum() == 1, name="one_piece")
            for k in R(len(nodi)):
                vicini = [t for t in R(len(nodi) - 1) if t == k or t == k - 1]
                m.addConstr(lam[k] <= gp.quicksum(w[t] for t in vicini), name=f"adjacency{k}")
        return m, lam, w, qtot


    forme = {}
    for nome, adj in [("without adjacency (free convex combination)", False),
                      ("with adjacency (SOS2 written by hand)", True)]:
        m, lam, w, qtot = modello_tratti(adj)
        z314 = risolvi(m)
        forme[nome], _, _ = rilassamento(m, rafforzato=True)
        attivi = [k for k in R(len(nodi)) if lam[k].X > 1e-9]
        print(f"  {nome:44s} z = {frazione(z314)}   nonzero lambdas at nodes {attivi}")
    registra("3.14", "piecewise linear function", z314, forme)
    print("  Careful with the relaxation: with w fractional the adjacency constraint no")
    print("  longer bites, and the two formulations have the same z(LP+). Adjacency changes")
    print("  the integer set, not the strength of the relaxation.")
    esatto = costi[2] + (costi[3] - costi[2]) * (domanda314 - nodi[2]) / (nodi[3] - nodi[2])
    print(f"  The exact value of the piecewise function at q = {domanda314} is {frazione(esatto)}.")
    print("  Without adjacency the convex combination may mix nodes 0 and 3, which are not")
    print("  endpoints of the same piece: the result is a point below the graph, that is,")
    print("  the lower convex envelope, and a cost the function never attains.")

    # ---------- 15. THE TABLE OF TECHNIQUES ----------
    intestazione("3.15  The summary table")
    tav = pd.DataFrame(TAV)
    salva_dati(tav, "cap03_tecniche")
    for riga in TAV:
        print(f"  {riga['section']:5s} {riga['technique'][:44]:46s} z(MILP) = {frazione(riga['z_milp'])}")

    # ---------- 16. FIGURES ----------
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    ax.plot(nodi, costi, "o-", color=TEAL, lw=2, label="piecewise function $g(q)$")
    for k in R(len(nodi) - 1):
        ax.annotate(f"piece {k + 1}", ((nodi[k] + nodi[k + 1]) / 2, (costi[k] + costi[k + 1]) / 2),
                    textcoords="offset points", xytext=(-16, 10), fontsize=8, color=GRIGIO)
    ax.plot([domanda314], [esatto], "s", color=ROSSO, ms=9, label=f"$q = {domanda314}$, $g = {esatto:g}$")
    ax.plot([nodi[0], nodi[-1]], [costi[0], costi[-1]], "--", color=GRIGIO, lw=1,
            label="chord between nodes 0 and 3 (without adjacency)")
    ax.set_xlabel("quantity $q$")
    ax.set_ylabel("cost $g(q)$")
    ax.set_title("Cost brackets: a non-convex piecewise linear function")
    ax.legend(fontsize=8)
    salva_figura(fig, "cap03_tratti")

    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    etichette = ["aggregated", "disaggregated"]
    valori = [TAV[0]["z_lp_1"], TAV[0]["z_lp_2"]]
    ax.bar(etichette, valori, color=[ARANCIO, TEAL], width=0.5)
    ax.axhline(TAV[0]["z_milp"], color=ROSSO, lw=1.6, ls="--")
    ax.annotate(f"$z(\\mathrm{{MILP}}) = {TAV[0]['z_milp']:g}$", (1.35, TAV[0]["z_milp"]),
                ha="right", va="bottom", fontsize=9, color=ROSSO)
    for i, v in enumerate(valori):
        ax.annotate(f"{v:.3f}", (i, v), ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("$z(\\mathrm{LP}^+)$")
    ax.set_ylim(0, TAV[0]["z_milp"] * 1.25)
    ax.set_title("Activation: the disaggregated form gives a tighter relaxation")
    salva_figura(fig, "cap03_attivazione")
    print("Done.")
    ```

<!-- embedded-script: end -->
