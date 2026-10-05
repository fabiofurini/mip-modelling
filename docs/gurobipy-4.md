# 3.4 Three classic models

**Class:** implementation · **Script:** `python/cap06_bpp.py`, `python/cap06_cmax.py`, `python/cap06_tsp.py`
{ .scheda }

Bin packing, makespan and travelling salesman: statement, model, construction in
`gurobipy` and model of the instance. They are the three problems on which the
[heuristics chapter](modelling-4.md) builds next-fit, first-fit, best-fit, LPT
and nearest neighbour.

So far the example model has always been the knapsack. The three problems below
come back in the [heuristics chapter](modelling-4.md), where the solutions of
next-fit, first-fit, best-fit, LPT and nearest neighbour are built by hand: here
their models are written, so that those heuristics have an optimum to compare
themselves with.

## Bin packing: how many containers are enough

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_bpp.ipynb)

The script is `python/cap06_bpp.py`.

!!! abstract "Bin packing"
    There are $n$ items, item $j$ weighs $w_j$. The containers are all alike, of
    capacity $C$. Use the smallest number of containers.

### The model

Two families of binary variables are needed: $x_{jb} = 1$ if item $j$ goes into
container $b$, and $y_b = 1$ if container $b$ is used.

$$
\begin{aligned}
\min ~~ \sum_{b=1}^{k} y_b & &\\
\text{subject to} \quad \sum_{b=1}^{k} x_{jb} &= 1, & \forall j \in \{1, 2, \dots, n\},\\
\sum_{j=1}^{n} w_j\, x_{jb} - c\, y_b &\le 0, & \forall b \in \{1, 2, \dots, k\},\\
x_{jb} &\in \{0, 1\}, & \forall j \in \{1, 2, \dots, n\},\ \forall b \in \{1, 2, \dots, k\},\\
y_b &\in \{0, 1\}, & \forall b \in \{1, 2, \dots, k\}.
\end{aligned}
$$

The first family says that every item ends up in exactly one container. The
second is the capacity written as an **activation**: while $y_b = 0$ container
$b$ can receive nothing, and as soon as $y_b = 1$ it takes up to $c$. The
objective counts the containers switched on.

### Building it in gurobipy

```python
def modello_bpp(w, c, k):
    n = len(w)
    m = nuovo_modello("bin_packing")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, vtype=GRB.BINARY, name="y")
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="item")
    m.addConstrs((gp.quicksum(w[j] * x[j, b] for j in R(n)) <= c * y[b]
                  for b in R(k)), name="capacity")
    return m, x, y
```

### The instance

On the instance of four items of weight $w = (5, 4, 3, 3)$ and capacity $c = 7$:

<!-- modello-esteso: cap06_bpp -->

<div class="modello-esteso largo" markdown>

$$
\begin{array}{rrrrrrrrrrrrrrrr c l}
\min &  &  &  &  &  &  &  &  &  &  &  &  & y_1 & +y_2 & +y_3 &  & \\
\text{subject to} & x_{11} & +x_{12} & +x_{13} &  &  &  &  &  &  &  &  &  &  &  &  & = & 1\\
 &  &  &  & x_{21} & +x_{22} & +x_{23} &  &  &  &  &  &  &  &  &  & = & 1\\
 &  &  &  &  &  &  & x_{31} & +x_{32} & +x_{33} &  &  &  &  &  &  & = & 1\\
 &  &  &  &  &  &  &  &  &  & x_{41} & +x_{42} & +x_{43} &  &  &  & = & 1\\
 & 5x_{11} &  &  & +4x_{21} &  &  & +3x_{31} &  &  & +3x_{41} &  &  & -7y_1 &  &  & \le & 0\\
 &  & 5x_{12} &  &  & +4x_{22} &  &  & +3x_{32} &  &  & +3x_{42} &  &  & -7y_2 &  & \le & 0\\
 &  &  & 5x_{13} &  &  & +4x_{23} &  &  & +3x_{33} &  &  & +3x_{43} &  &  & -7y_3 & \le & 0\\
 & x_{11}, & x_{12}, & x_{13}, & x_{21}, & x_{22}, & x_{23}, & x_{31}, & x_{32}, & x_{33}, & x_{41}, & x_{42}, & x_{43} &  &  &  & \in & \{0, 1\}\\
 &  &  &  &  &  &  &  &  &  &  &  &  & y_1, & y_2, & y_3 & \in & \{0, 1\}
\end{array}
$$

</div>

<!-- modello-esteso: fine -->

The total weight is $15$, so no solution can use fewer than
$\lceil 15/7 \rceil = 3$ containers; the optimum uses exactly $3$, and the count
is therefore tight.

!!! warning "The relaxation of bin packing is very weak"
    Relaxing $y_b$ to $y_b \ge 0$ the model buys fractions of a container, and the
    LP optimum drops to $\sum_j w_j / c = 15/7 \approx 2.14$: the relaxation does not
    know that a container opens whole. This is why on this problem the dual bound
    is of little use and the heuristics matter more.

## Makespan: the load of the busiest machine

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_cmax.ipynb)

The script is `python/cap06_cmax.py`.

!!! abstract "Makespan on identical machines"
    There are $n$ jobs, of duration $d_j$, and $k$ identical machines. Every job
    goes on a single machine and is not interrupted. Minimise the load of the
    busiest machine.

### The model

With $x_{jm} = 1$ if job $j$ goes on machine $m$, and $z \ge 0$ the load of
the busiest machine:

$$
\begin{aligned}
\min ~~ z & &\\
\text{subject to} \quad \sum_{m=1}^{k} x_{jm} &= 1, & \forall j \in \{1, 2, \dots, n\},\\
\sum_{j=1}^{n} d_j\, x_{jm} - z &\le 0, & \forall m \in \{1, 2, \dots, k\},\\
x_{jm} &\in \{0, 1\}, & \forall j \in \{1, 2, \dots, n\},\ \forall m \in \{1, 2, \dots, k\},\\
z &\ge 0. &
\end{aligned}
$$

The objective is the single variable $z$: no datum appears in it. It is the $k$ load
rows that give it meaning, saying that no machine works longer than $z$;
the minimisation then presses it down onto the load of the busiest machine. It is
the [min-max](links-06.md) technique.

### Building it in gurobipy

```python
def modello_cmax(d, k):
    n = len(d)
    m = nuovo_modello("makespan")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    z = m.addVar(name="z")
    m.setObjective(z, GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="job")
    m.addConstrs((gp.quicksum(d[j] * x[j, mm] for j in R(n)) <= z
                  for mm in R(k)), name="load")
    return m, x, z
```

### The instance

On the instance of four jobs of duration $d = (3, 4, 5, 6)$ on $k = 2$ machines
— the very one the heuristics chapter runs LPT on:

<!-- modello-esteso: cap06_cmax -->

<div class="modello-esteso largo" markdown>

$$
\begin{array}{rrrrrrrrrr c l}
\min &  &  &  &  &  &  &  &  & z &  & \\
\text{subject to} & x_{11} & +x_{12} &  &  &  &  &  &  &  & = & 1\\
 &  &  & x_{21} & +x_{22} &  &  &  &  &  & = & 1\\
 &  &  &  &  & x_{31} & +x_{32} &  &  &  & = & 1\\
 &  &  &  &  &  &  & x_{41} & +x_{42} &  & = & 1\\
 & 3x_{11} &  & +4x_{21} &  & +5x_{31} &  & +6x_{41} &  & -z & \le & 0\\
 &  & 3x_{12} &  & +4x_{22} &  & +5x_{32} &  & +6x_{42} & -z & \le & 0\\
 & x_{11}, & x_{12}, & x_{21}, & x_{22}, & x_{31}, & x_{32}, & x_{41}, & x_{42} &  & \in & \{0, 1\}\\
 &  &  &  &  &  &  &  &  & z & \ge & 0
\end{array}
$$

</div>

<!-- modello-esteso: fine -->

The total load is $18$ and the machines are two: no solution can go below
$18/2 = 9$, and the optimum is exactly $9$ — the jobs split into $6+3$ and
$5+4$. Here the count settles the problem on its own.

## Travelling salesman: the MTZ formulation

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_tsp.ipynb)

The script is `python/cap06_tsp.py`.

!!! abstract "Travelling salesman"
    There are $n$ cities and a distance $d_{ij}$ between every pair. Find the
    shortest tour that visits every city exactly once and returns to the starting
    point.

### The model

With $x_{ij} = 1$ if the tour goes from $i$ to $j$, the two families "one
leaves once" and "one enters once" are not enough: they also admit solutions made
of separate **subtours**. The Miller–Tucker–Zemlin formulation adds a variable
$u_i$ for every city other than the first, recording its position along the
tour.

$$
\begin{aligned}
\min ~~ \sum_{i=1}^{n} \sum_{j \ne i} d_{ij}\, x_{ij} & &\\
\text{subject to} \quad \sum_{j \ne i} x_{ij} &= 1, & \forall i \in \{1, 2, \dots, n\},\\
\sum_{i \ne j} x_{ij} &= 1, & \forall j \in \{1, 2, \dots, n\},\\
u_i - u_j + n\, x_{ij} &\le n - 1, & \forall i, j \in \{2, 3, \dots, n\},\ i \ne j,\\
x_{ij} &\in \{0, 1\}, & \forall i, j \in \{1, 2, \dots, n\},\ i \ne j,\\
u_i &\in [1,\, n-1], & \forall i \in \{2, 3, \dots, n\}.
\end{aligned}
$$

The third group is the heart of the formulation. If $x_{ij} = 0$ the row becomes
$u_i - u_j \le n - 1$, always true because the $u$ lie between $1$ and $n-1$: it
forbids nothing. If instead $x_{ij} = 1$ it becomes $u_j \ge u_i + 1$, that is
"if I go from $i$ to $j$, the position of $j$ is the next one". A subtour missing
city $1$ would need a chain of ever-growing positions closing on itself, which is
impossible; city $1$ has no $u$ of its own precisely because it is where the tour
closes.

### Building it in gurobipy

```python
def modello_tsp(D):
    n = len(D)
    m = nuovo_modello("tsp")
    x = m.addVars(((i, j) for i in R(n) for j in R(n) if i != j),
                  vtype=GRB.BINARY, name="x")
    u = m.addVars(R(1, n), lb=1, ub=n - 1, name="u")
    m.setObjective(gp.quicksum(D[i][j] * x[i, j] for i, j in x), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(x[i, j] for j in R(n) if j != i) == 1
                  for i in R(n)), name="out")
    m.addConstrs((gp.quicksum(x[i, j] for i in R(n) if i != j) == 1
                  for j in R(n)), name="in")
    m.addConstrs((u[i] - u[j] + n * x[i, j] <= n - 1
                  for i in R(1, n) for j in R(1, n) if i != j), name="mtz")
    return m, x, u
```

### The instance

On the four-city instance of the [heuristics chapter](modelling-4.md) the
optimal tour is $1 \to 2 \to 4 \to 3 \to 1$ and measures $22$. The model of the
instance has fifteen columns — twelve arcs and three positions — and fourteen
rows:

<!-- modello-esteso: cap06_tsp -->

<div class="modello-esteso largo" markdown>

$$
\begin{array}{rrrrrrrrrrrrrrrr c l}
\min & 4x_{12} & +5x_{13} & +9x_{14} & +4x_{21} & +9x_{23} & +9x_{24} & +5x_{31} & +9x_{32} & +4x_{34} & +9x_{41} & +9x_{42} & +4x_{43} &  &  &  &  & \\
\text{subject to} & x_{12} & +x_{13} & +x_{14} &  &  &  &  &  &  &  &  &  &  &  &  & = & 1\\
 &  &  &  & x_{21} & +x_{23} & +x_{24} &  &  &  &  &  &  &  &  &  & = & 1\\
 &  &  &  &  &  &  & x_{31} & +x_{32} & +x_{34} &  &  &  &  &  &  & = & 1\\
 &  &  &  &  &  &  &  &  &  & x_{41} & +x_{42} & +x_{43} &  &  &  & = & 1\\
 &  &  &  & x_{21} &  &  & +x_{31} &  &  & +x_{41} &  &  &  &  &  & = & 1\\
 & x_{12} &  &  &  &  &  &  & +x_{32} &  &  & +x_{42} &  &  &  &  & = & 1\\
 &  & x_{13} &  &  & +x_{23} &  &  &  &  &  &  & +x_{43} &  &  &  & = & 1\\
 &  &  & x_{14} &  &  & +x_{24} &  &  & +x_{34} &  &  &  &  &  &  & = & 1\\
 &  &  &  &  & 4x_{23} &  &  &  &  &  &  &  & +u_2 & -u_3 &  & \le & 3\\
 &  &  &  &  &  & 4x_{24} &  &  &  &  &  &  & +u_2 &  & -u_4 & \le & 3\\
 &  &  &  &  &  &  &  & 4x_{32} &  &  &  &  & -u_2 & +u_3 &  & \le & 3\\
 &  &  &  &  &  &  &  &  & 4x_{34} &  &  &  &  & +u_3 & -u_4 & \le & 3\\
 &  &  &  &  &  &  &  &  &  &  & 4x_{42} &  & -u_2 &  & +u_4 & \le & 3\\
 &  &  &  &  &  &  &  &  &  &  &  & 4x_{43} &  & -u_3 & +u_4 & \le & 3\\
 & x_{12}, & x_{13}, & x_{14}, & x_{21}, & x_{23}, & x_{24}, & x_{31}, & x_{32}, & x_{34}, & x_{41}, & x_{42}, & x_{43} &  &  &  & \in & \{0, 1\}\\
 &  &  &  &  &  &  &  &  &  &  &  &  & u_2, & u_3, & u_4 & \ge & 1
\end{array}
$$

</div>

<!-- modello-esteso: fine -->

!!! warning "MTZ is convenient, not the strongest"
    The MTZ constraints are $O(n^2)$ and take three lines of `gurobipy`, but their
    linear relaxation is weak: the continuous $u$ absorb almost everything and the
    LP stays far from the integer optimum. Formulations that remove subtours with
    connectivity cuts give much better bounds, at the price of an exponential
    number of constraints to be generated as they are needed. For the sizes of
    this course MTZ is enough.

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/cap06_bpp.py` (51 lines)"

    ```python
    """Bin packing: how many containers are enough (chapter 3).

    The first of the three problems the heuristics chapter takes up again: there
    next-fit, first-fit and best-fit are built by hand, here the model that says what
    the optimum is. The capacity is written as an activation: until the container
    opens it can receive nothing.
    """
    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from esteso import salva_modello
    from mip import frazione, nuovo_modello, risolvi
    from stile import intestazione, salva_dati

    R = range

    intestazione("Bin packing: the smallest number of containers")
    w_bpp = [5, 4, 3, 3]             # weight of the items
    c_bpp = 7                        # capacity of one container
    n_bpp = len(w_bpp)


    def modello_bpp(w, c, k):
        n = len(w)
        m = nuovo_modello("bin_packing")
        x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
        y = m.addVars(k, vtype=GRB.BINARY, name="y")
        m.setObjective(y.sum(), GRB.MINIMIZE)
        m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="item")
        m.addConstrs((gp.quicksum(w[j] * x[j, b] for j in R(n)) <= c * y[b] for b in R(k)),
                     name="capacity")
        return m, x, y


    # with one container per item one finds how many are really needed; the model that
    # gets printed then uses only those, because the others would stay empty
    m_largo, _, _ = modello_bpp(w_bpp, c_bpp, n_bpp)
    z_bpp = risolvi(m_largo)
    minimo_teorico = -(-sum(w_bpp) // c_bpp)        # rounding up
    print(f"  Weights {w_bpp}, capacity {c_bpp}.")
    print(f"  The total weight is {sum(w_bpp)}: no solution uses fewer than "
          f"{sum(w_bpp)}/{c_bpp} = {minimo_teorico} containers, and the optimum uses {int(z_bpp)}.")
    assert z_bpp == minimo_teorico
    m_bpp, x_bpp, y_bpp = modello_bpp(w_bpp, c_bpp, int(z_bpp))
    risolvi(m_bpp)
    salva_modello(m_bpp, "cap06_bpp")
    print("  The relaxation buys fractions of a container and drops to "
          f"{frazione(sum(w_bpp) / c_bpp)}: it does not know a container opens whole.")
    salva_dati(pd.DataFrame([{"problem": "bin packing", "z_milp": z_bpp}]), "cap06_bpp")
    print("Done.")
    ```

??? example "Show the complete script — `python/cap06_cmax.py` (47 lines)"

    ```python
    """Makespan on identical machines (chapter 3).

    The second of the three problems the heuristics chapter takes up again: there the
    natural order is compared with LPT on the very same four jobs. The objective is a
    single variable, z, and it is the load constraints that give it meaning: this is
    the min-max technique.
    """
    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from esteso import salva_modello
    from mip import frazione, nuovo_modello, risolvi
    from stile import intestazione, salva_dati

    R = range

    intestazione("Makespan: the load of the busiest machine")
    d_cmax = [3, 4, 5, 6]            # job durations
    k_cmax = 2                       # identical machines


    def modello_cmax(d, k):
        n = len(d)
        m = nuovo_modello("makespan")
        x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
        z = m.addVar(name="z")
        m.setObjective(z, GRB.MINIMIZE)
        m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="job")
        m.addConstrs((gp.quicksum(d[j] * x[j, mm] for j in R(n)) <= z for mm in R(k)),
                     name="load")
        return m, x, z


    m_cmax, x_cmax, z_var = modello_cmax(d_cmax, k_cmax)
    z_cmax = risolvi(m_cmax)
    salva_modello(m_cmax, "cap06_cmax")
    print(f"  Durations {d_cmax} on {k_cmax} identical machines.")
    print(f"  The total load is {sum(d_cmax)}: divided by {k_cmax} it gives "
          f"{frazione(sum(d_cmax) / k_cmax)}, and the optimum is {frazione(z_cmax)}.")
    for mm in R(k_cmax):
        lavori = [j + 1 for j in R(len(d_cmax)) if x_cmax[j, mm].X > 0.5]
        print(f"    machine {mm + 1}: jobs {lavori}, load "
              f"{sum(d_cmax[j - 1] for j in lavori)}")
    assert z_cmax == sum(d_cmax) / k_cmax
    salva_dati(pd.DataFrame([{"problem": "makespan", "z_milp": z_cmax}]), "cap06_cmax")
    print("Done.")
    ```

??? example "Show the complete script — `python/cap06_tsp.py` (54 lines)"

    ```python
    """Travelling salesman with the MTZ formulation (chapter 3).

    The third of the three problems the heuristics chapter takes up again: there the
    tour is built with nearest neighbour, here the optimum is found.

    The u variables order the cities along the tour: the constraint
    u_i - u_j + n x_ij <= n - 1 is true when x_ij = 0 and forces u_j >= u_i + 1 when
    x_ij = 1. Subtours that miss city 1 are thereby excluded, because they would need
    a chain of ever-growing u that closes on itself.
    """
    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from esteso import salva_modello
    from mip import frazione, nuovo_modello, risolvi
    from stile import intestazione, salva_dati

    R = range

    intestazione("Travelling salesman: the shortest tour")
    D_tsp = [[0, 4, 5, 9],
             [4, 0, 9, 9],
             [5, 9, 0, 4],
             [9, 9, 4, 0]]
    n_tsp = len(D_tsp)


    def modello_tsp(D):
        n = len(D)
        m = nuovo_modello("tsp")
        x = m.addVars(((i, j) for i in R(n) for j in R(n) if i != j), vtype=GRB.BINARY, name="x")
        u = m.addVars(R(1, n), lb=1, ub=n - 1, name="u")
        m.setObjective(gp.quicksum(D[i][j] * x[i, j] for i, j in x), GRB.MINIMIZE)
        m.addConstrs((gp.quicksum(x[i, j] for j in R(n) if j != i) == 1 for i in R(n)), name="out")
        m.addConstrs((gp.quicksum(x[i, j] for i in R(n) if i != j) == 1 for j in R(n)), name="in")
        m.addConstrs((u[i] - u[j] + n * x[i, j] <= n - 1
                      for i in R(1, n) for j in R(1, n) if i != j), name="mtz")
        return m, x, u


    m_tsp, x_tsp, u_tsp = modello_tsp(D_tsp)
    salva_modello(m_tsp, "cap06_tsp")
    z_tsp = risolvi(m_tsp)
    seguente = {i: j for (i, j) in x_tsp if x_tsp[i, j].X > 0.5}
    giro, citta = [0], 0
    while seguente[citta] != 0:
        citta = seguente[citta]
        giro.append(citta)
    print(f"  {n_tsp} cities, symmetric and metric distances.")
    print("  Optimal tour: " + " -> ".join(str(c + 1) for c in giro + [0])
          + f", length {frazione(z_tsp)}.")
    salva_dati(pd.DataFrame([{"problem": "TSP", "z_milp": z_tsp}]), "cap06_tsp")
    print("Done.")
    ```

<!-- embedded-script: end -->
