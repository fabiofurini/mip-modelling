# EX 9 — Queens on the chessboard

[:material-file-pdf-box: Lecture notes (PDF)](pdf/notes-2-numerical.pdf) · [:material-presentation: Slides (PDF)](pdf/slides-07-numerical-models-2.pdf)

**Class:** BIP · **Links:** set packing, [alldiff](links-12.md) · **Script:** `python/ex09_queens.py`<br>
**Difficulty:** ★★☆☆☆ · **Time:** 30–45 min
{ .scheda }

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex09_queens.ipynb)

One of the [fifteen numerical models](numerical.md): the one where the dual bound
is written in a single line, and is worth exactly as much as the optimum.

!!! abstract "EX 9"
    On a $4 \times 4$ chessboard the **maximum number of queens** is to be
    placed so that none can capture another in one move. In chess a queen moves
    any number of squares along the same row, the same column or either diagonal.

## Model

With $x_{ij} = 1$ if there is a queen on square $(i,j)$: sixteen binary
variables, one per square.

<!-- modello-esteso: ex09_primale -->

<div class="modello-esteso largo" markdown>

$$
\begin{array}{rrrrrrrrrrrrrrrrr c l}
\max & x_{11} & +x_{12} & +x_{13} & +x_{14} & +x_{21} & +x_{22} & +x_{23} & +x_{24} & +x_{31} & +x_{32} & +x_{33} & +x_{34} & +x_{41} & +x_{42} & +x_{43} & +x_{44} &  & \\
\text{subject to} & x_{11} & +x_{12} & +x_{13} & +x_{14} &  &  &  &  &  &  &  &  &  &  &  &  & \le & 1\\
 &  &  &  &  & x_{21} & +x_{22} & +x_{23} & +x_{24} &  &  &  &  &  &  &  &  & \le & 1\\
 &  &  &  &  &  &  &  &  & x_{31} & +x_{32} & +x_{33} & +x_{34} &  &  &  &  & \le & 1\\
 &  &  &  &  &  &  &  &  &  &  &  &  & x_{41} & +x_{42} & +x_{43} & +x_{44} & \le & 1\\
 & x_{11} &  &  &  & +x_{21} &  &  &  & +x_{31} &  &  &  & +x_{41} &  &  &  & \le & 1\\
 &  & x_{12} &  &  &  & +x_{22} &  &  &  & +x_{32} &  &  &  & +x_{42} &  &  & \le & 1\\
 &  &  & x_{13} &  &  &  & +x_{23} &  &  &  & +x_{33} &  &  &  & +x_{43} &  & \le & 1\\
 &  &  &  & x_{14} &  &  &  & +x_{24} &  &  &  & +x_{34} &  &  &  & +x_{44} & \le & 1\\
 &  &  & x_{13} &  &  &  &  & +x_{24} &  &  &  &  &  &  &  &  & \le & 1\\
 &  & x_{12} &  &  &  &  & +x_{23} &  &  &  &  & +x_{34} &  &  &  &  & \le & 1\\
 & x_{11} &  &  &  &  & +x_{22} &  &  &  &  & +x_{33} &  &  &  &  & +x_{44} & \le & 1\\
 &  &  &  &  & x_{21} &  &  &  &  & +x_{32} &  &  &  &  & +x_{43} &  & \le & 1\\
 &  &  &  &  &  &  &  &  & x_{31} &  &  &  &  & +x_{42} &  &  & \le & 1\\
 &  & x_{12} &  &  & +x_{21} &  &  &  &  &  &  &  &  &  &  &  & \le & 1\\
 &  &  & x_{13} &  &  & +x_{22} &  &  & +x_{31} &  &  &  &  &  &  &  & \le & 1\\
 &  &  &  & x_{14} &  &  & +x_{23} &  &  & +x_{32} &  &  & +x_{41} &  &  &  & \le & 1\\
 &  &  &  &  &  &  &  & x_{24} &  &  & +x_{33} &  &  & +x_{42} &  &  & \le & 1\\
 &  &  &  &  &  &  &  &  &  &  &  & x_{34} &  &  & +x_{43} &  & \le & 1\\
 & x_{11}, & x_{12}, & x_{13}, & x_{14}, & x_{21}, & x_{22}, & x_{23}, & x_{24}, & x_{31}, & x_{32}, & x_{33}, & x_{34}, & x_{41}, & x_{42}, & x_{43}, & x_{44} & \in & \{0, 1\}
\end{array}
$$

</div>

<!-- modello-esteso: fine -->

A **set packing** over four families of lines — the $4$ rows, the $4$ columns and
the diagonals in both directions — $18$ constraints in all. The indexing trick is
all here: the
"descending" diagonals are the sets with $i - j$ constant, the "ascending" ones
those with $i + j$ constant.

!!! tip "Diagonals with a single square do not become constraints"
    Each of the four corners sits on a diagonal that touches nothing else.
    Writing its constraint would give $x_{ij} \le 1$ on an already binary
    variable: a row that forbids nothing. What remains is $5 + 5$ diagonals with
    at least two squares, and the model loses ten rows without losing a single
    solution.

## Constructive heuristic: the primal bound

This is a **maximisation**. Row-by-row heuristic: in row $i$ the first free
column not attacked by the queens already placed is chosen; if there is none, the
row stays empty. There is no backtracking.

On the instance the heuristic places the queens at $(1,1)$ and $(2,3)$; row $3$
has no free square left and is skipped; in row $4$ it takes $(4,2)$.

$$\mathit{LB} = 3.$$

## LP relaxation and dual: the dual bound

The dual is a **set covering**: one non-negative variable per line — $\alpha_i$
for row $i$, $\beta_j$ for column $j$, $\gamma_k$ and $\delta_k$ for the two
families of diagonals — and every square must be covered by at least one of the
four lines crossing it.

<!-- modello-esteso: ex09_duale -->

<div class="modello-esteso largo" markdown>

$$
\begin{array}{rrrrrrrrrrrrrrrrrrr c l}
\min & \alpha_1 & +\alpha_2 & +\alpha_3 & +\alpha_4 & +\beta_1 & +\beta_2 & +\beta_3 & +\beta_4 & +\gamma_{-1} & +\gamma_0 & +\gamma_1 & +\gamma_2 & +\gamma_3 & +\delta_2 & +\delta_3 & +\delta_4 & +\delta_5 & +\delta_6 &  & \\
\text{subject to} & \alpha_1 &  &  &  & +\beta_1 &  &  &  &  &  & +\gamma_1 &  &  &  &  &  &  &  & \ge & 1\\
 & \alpha_1 &  &  &  &  & +\beta_2 &  &  &  & +\gamma_0 &  &  &  & +\delta_2 &  &  &  &  & \ge & 1\\
 & \alpha_1 &  &  &  &  &  & +\beta_3 &  & +\gamma_{-1} &  &  &  &  &  & +\delta_3 &  &  &  & \ge & 1\\
 & \alpha_1 &  &  &  &  &  &  & +\beta_4 &  &  &  &  &  &  &  & +\delta_4 &  &  & \ge & 1\\
 &  & \alpha_2 &  &  & +\beta_1 &  &  &  &  &  &  & +\gamma_2 &  & +\delta_2 &  &  &  &  & \ge & 1\\
 &  & \alpha_2 &  &  &  & +\beta_2 &  &  &  &  & +\gamma_1 &  &  &  & +\delta_3 &  &  &  & \ge & 1\\
 &  & \alpha_2 &  &  &  &  & +\beta_3 &  &  & +\gamma_0 &  &  &  &  &  & +\delta_4 &  &  & \ge & 1\\
 &  & \alpha_2 &  &  &  &  &  & +\beta_4 & +\gamma_{-1} &  &  &  &  &  &  &  & +\delta_5 &  & \ge & 1\\
 &  &  & \alpha_3 &  & +\beta_1 &  &  &  &  &  &  &  & +\gamma_3 &  & +\delta_3 &  &  &  & \ge & 1\\
 &  &  & \alpha_3 &  &  & +\beta_2 &  &  &  &  &  & +\gamma_2 &  &  &  & +\delta_4 &  &  & \ge & 1\\
 &  &  & \alpha_3 &  &  &  & +\beta_3 &  &  &  & +\gamma_1 &  &  &  &  &  & +\delta_5 &  & \ge & 1\\
 &  &  & \alpha_3 &  &  &  &  & +\beta_4 &  & +\gamma_0 &  &  &  &  &  &  &  & +\delta_6 & \ge & 1\\
 &  &  &  & \alpha_4 & +\beta_1 &  &  &  &  &  &  &  &  &  &  & +\delta_4 &  &  & \ge & 1\\
 &  &  &  & \alpha_4 &  & +\beta_2 &  &  &  &  &  &  & +\gamma_3 &  &  &  & +\delta_5 &  & \ge & 1\\
 &  &  &  & \alpha_4 &  &  & +\beta_3 &  &  &  &  & +\gamma_2 &  &  &  &  &  & +\delta_6 & \ge & 1\\
 &  &  &  & \alpha_4 &  &  &  & +\beta_4 &  &  & +\gamma_1 &  &  &  &  &  &  &  & \ge & 1\\
 & \alpha_1, & \alpha_2, & \alpha_3, & \alpha_4 &  &  &  &  &  &  &  &  &  &  &  &  &  &  & \ge & 0\\
 &  &  &  &  & \beta_1, & \beta_2, & \beta_3, & \beta_4 &  &  &  &  &  &  &  &  &  &  & \ge & 0\\
 &  &  &  &  &  &  &  &  & \gamma_{-1}, & \gamma_0, & \gamma_1, & \gamma_2, & \gamma_3 &  &  &  &  &  & \ge & 0\\
 &  &  &  &  &  &  &  &  &  &  &  &  &  & \delta_2, & \delta_3, & \delta_4, & \delta_5, & \delta_6 & \ge & 0
\end{array}
$$

</div>

<!-- modello-esteso: fine -->

**The recipe:** use a single family. With $\bar\alpha_i = 1$ for every row and
everything else zero, every square $(i,j)$ has $\alpha_i = 1 \ge 1$: the solution
is feasible and is worth $n$. It is the dual translation of the sentence "in each
row there is at most one queen".

$$\mathit{UB} = 4.$$

## Optimum and comparison

| $\mathit{LB}$ | $\mathit{UB}$ | $z(\mathit{LP})$ | $z(\mathit{LP}^+)$ | $z(\mathit{MILP})$ |
|---:|---:|---:|---:|---:|
| 3 | 4 | 4 | 4 | 4 |

The dual bound is attained: the solution found is optimal, and this is known
**without trusting the solver**. The heuristic instead stops at $3$: it is the
heuristic, not the bound, that leaves the $25\%$ gap.

!!! tip "Two variants"
    On $n \times n$ boards with $n = 5$ and $n = 6$ the optimum is always $n$,
    and the certificate $\bar\alpha_i = 1$ proves it. For $n = 2$ and $n = 3$
    instead the optimum is $1$ and $2$: the bound $n$ stays valid but is not
    attainable, and it is the first case where this dual recipe does not close
    the problem. The $4 \times 4$ board of the exercise is the smallest on which
    $n$ queens actually fit, and therefore the smallest on which the certificate
    closes.

    Dropping the diagonal constraints gives **rooks** instead of queens: the
    model becomes an assignment, the matrix is totally unimodular and the LP
    relaxation already gives an integer value.

![The optimal board](img/ex09_scacchiera.png)

## Code

The full script is
[`python/ex09_queens.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/ex09_queens.py);
the notebook is
[`notebooks/ex09_queens.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/ex09_queens.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/ex09_queens.py` (183 lines)"

    ```python
    """EX 9 -- Queens on the chessboard (family 11).

    Set packing on four families of lines: rows, columns and the two diagonals. The
    dual of the relaxation is built by hand in a single line (one pays 1 per row) and
    is worth exactly as much as the optimum: a case in which the certificate settles
    the problem. The constructive heuristic, on the other hand, stops below n queens.

    The instance is 4x4, the smallest board on which n queens fit: sixteen binaries
    and eighteen constraints, so the model is written out in full like every other
    one of the chapter. The classic 8x8 case stays among the variants.

    Diagonals with a single square do not become constraints: `x <= 1` on a binary
    is already true by definition, and writing it would fill the model with empty
    rows.
    """
    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                     risolvi, valuta)
    from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura
    from esteso import salva_modello

    R = range

    # ---------- 1. MODEL AND INSTANCE ----------
    intestazione("EX 9. Queens: the largest number of non-attacking queens")
    N = 4


    def diagonali(n):
        """The diagonals with at least two squares, in both directions.

        On `i - j = k` the squares are `n - |k|`, on `i + j = k` they are
        `min(k, 2n-2-k) + 1`: the ones with a single square are dropped.
        """
        prima = [k for k in R(-(n - 1), n) if n - abs(k) >= 2]
        seconda = [k for k in R(0, 2 * n - 1) if min(k, 2 * n - 2 - k) + 1 >= 2]
        return prima, seconda


    def modello(n):
        m = nuovo_modello("queens")
        x = m.addVars(n, n, vtype=GRB.BINARY, name="x")
        m.setObjective(x.sum(), GRB.MAXIMIZE)
        m.addConstrs((x.sum(i, "*") <= 1 for i in R(n)), name="row")
        m.addConstrs((x.sum("*", j) <= 1 for j in R(n)), name="column")
        prima, seconda = diagonali(n)
        m.addConstrs((gp.quicksum(x[i, j] for i in R(n) for j in R(n) if i - j == k) <= 1
                      for k in prima), name="diag1")
        m.addConstrs((gp.quicksum(x[i, j] for i in R(n) for j in R(n) if i + j == k) <= 1
                      for k in seconda), name="diag2")
        return m, x


    def duale(n):
        """min sum_i alpha_i + sum_j beta_j + sum_k gamma_k + sum_k delta_k
           s.t. alpha_i + beta_j + gamma_{i-j} + delta_{i+j} >= 1 for every square."""
        d = nuovo_modello("dual_queens")
        alpha = d.addVars(n, name="alpha")
        beta = d.addVars(n, name="beta")
        prima, seconda = diagonali(n)
        gamma = d.addVars(prima, name="gamma")
        delta = d.addVars(seconda, name="delta")
        d.setObjective(alpha.sum() + beta.sum() + gamma.sum() + delta.sum(), GRB.MINIMIZE)
        d.addConstrs((alpha[i] + beta[j]
                      + (gamma[i - j] if i - j in prima else 0)
                      + (delta[i + j] if i + j in seconda else 0) >= 1
                      for i in R(n) for j in R(n)), name="rc")
        return d


    m8, x8 = modello(N)
    salva_modello(m8, "ex09_primale")
    _p, _s = diagonali(N)
    print(f"  A {N}x{N} board: {N * N} binary variables and {2 * N + len(_p) + len(_s)} constraints")
    print(f"  ({N} rows, {N} columns and {len(_p)} + {len(_s)} diagonals with at least "
          "two squares).")

    # ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
    # constructive heuristic row by row: the first free column that is not attacked by the queens already
    # placed. It never backtracks: if a row has no free square, it is skipped.
    def euristica(n):
        pos = []
        passi = []
        for i in R(n):
            scelta = None
            for j in R(n):
                if all(j != jj and abs(i - ii) != abs(j - jj) for ii, jj in pos):
                    scelta = j
                    break
            if scelta is None:
                passi.append(f"row {i + 1}: no free square, the row stays empty")
            else:
                pos.append((i, scelta))
                passi.append(f"row {i + 1}: first free square in column {scelta + 1}")
        return pos, passi


    pos, passi = euristica(N)
    for k, riga in enumerate(passi, 1):
        print(f"  Step {k}. {riga}")
    lb8 = len(pos)
    sol_eur = {f"x[{i},{j}]": 1 for i, j in pos}
    assert ammissibile(m8, sol_eur), sol_eur
    print(f"  Queens placed by the constructive heuristic: {lb8}  ->  lb = {frazione(lb8)}")

    # ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
    d8 = duale(N)
    salva_modello(d8, "ex09_duale")
    mano = {f"alpha[{i}]": 1.0 for i in R(N)}       # beta = gamma = delta = 0
    ub8, viol = valuta(d8, mano)
    assert viol <= 1e-9, viol
    print("  Hand-built dual: alpha_i = 1 on every row, everything else zero. Every square (i, j)")
    print(f"  has alpha_i = 1 >= 1: the solution is feasible and worth {frazione(ub8)}.")
    print("  It is the dual translation of the sentence \"at most one queen sits in each row\".")
    zlp8, zlp8r, _ = due_rilassamenti(m8, d8)

    # ---------- 4. OPTIMUM OF THE MILP ----------
    z8 = risolvi(m8)
    ott = [(i, j) for i in R(N) for j in R(N) if x8[i, j].X > 0.5]
    print("  Optimal solution (one queen per row): "
          + ", ".join(f"row {i + 1} column {j + 1}" for i, j in sorted(ott)))
    riga = registra_bound("EX 9 queens", ub8, lb8, zlp8, zlp8r, z8, senso="max")
    salva_dati(pd.DataFrame([riga]), "ex09_bound")
    salva_dati(pd.DataFrame([{"row": i + 1, "column": j + 1} for i, j in sorted(ott)]),
               "ex09_ottimo")
    assert lb8 <= z8 <= zlp8 <= ub8 + 1e-9
    print(f"  The dual bound {frazione(ub8)} is attained: the solution found is optimal, and we")
    print("  know it without trusting the solver. The constructive heuristic stops earlier: it is the heuristic,")
    print("  not the bound, that leaves the gap.")

    # ---------- 5. TWO VARIANTS ----------
    intestazione("EX 9. Variants")
    varianti = {}
    for n in (5, 6):
        m, x = modello(n)
        z = risolvi(m)
        varianti[f"n = {n}"] = z
        print(f"  {n}x{n} board: z = {frazione(z)} (= n)")
        assert abs(z - n) <= 1e-9
    for n in (2, 3):
        m, x = modello(n)
        z = risolvi(m)
        varianti[f"n = {n}"] = z
        print(f"  {n}x{n} board: z = {frazione(z)} < {n}: the dual bound n is not attainable")
        assert z < n - 0.5
    salva_dati(pd.DataFrame({"board": list(varianti), "z": list(varianti.values())}),
               "ex09_varianti")
    m, x = modello(N)
    m.update()
    for c in [c for c in m.getConstrs() if c.ConstrName.startswith("diag")]:
        m.remove(c)
    m.update()
    z_torri = risolvi(m)
    print(f"  Without the diagonal constraints (rooks instead of queens): z = {frazione(z_torri)},")
    print("  and the model becomes an assignment: the matrix is totally unimodular and the")
    print("  linear relaxation already gives an integer value.")

    # ---------- 6. FIGURE ----------
    fig, ax = plt.subplots(figsize=(4.4, 4.4))
    for i in R(N):
        for j in R(N):
            ax.add_patch(plt.Rectangle((j, N - 1 - i), 1, 1,
                                       color="#EFEFEF" if (i + j) % 2 else "#CFD8DC"))
    for i, j in pos:
        ax.plot(j + 0.5, N - 1 - i + 0.5, marker="s", color=ARANCIO, ms=13)
    for i, j in ott:
        ax.plot(j + 0.5, N - 1 - i + 0.5, marker="*", color=TEAL, ms=17)
    ax.plot([], [], marker="s", ls="", color=ARANCIO, label=f"constructive heuristic ({lb8})")
    ax.plot([], [], marker="*", ls="", color=TEAL, label=f"optimum ({int(z8)})")
    ax.set_xlim(0, N)
    ax.set_ylim(0, N)
    ax.set_xticks([j + 0.5 for j in R(N)])
    ax.set_xticklabels([str(j + 1) for j in R(N)])
    ax.set_yticks([i + 0.5 for i in R(N)])
    ax.set_yticklabels([str(N - i) for i in R(N)])
    ax.set_aspect("equal")
    ax.set_title("EX 9: constructive heuristic against optimum")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2)
    salva_figura(fig, "ex09_scacchiera")
    print("Done.")
    ```

<!-- embedded-script: end -->
