# Hub location with maximum cost

**Class:** MILP · **Links:** aggregated activation, maximum variable · **Script:** `python/fam08_4_hub.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_4_hub.ipynb)

!!! abstract "Problem 8.4"
    $n \in \mathbb{Z}_{\ge 1}$ terminals, each to be connected to exactly
    one hub; $m \in \mathbb{Z}_{\ge 1}$ hubs, each with capacity $k \in
    \mathbb{Z}_{\ge 1}$ terminals and activation cost $f_j \in
    \mathbb{Q}_{\ge 0}$. $c_{ij} \in \mathbb{Q}_{\ge 0}$ is the cost of
    connecting terminal $i$ to hub $j$. We minimize the sum of activation
    costs and the maximum connection cost of each hub.

**The problem in words.** *We decide* which hubs to activate and which
hub to connect each terminal to. *The objective*: activation plus, for
each hub, the highest connection cost (not the sum). *The constraints*:
every terminal to exactly one hub; an inactive hub serves no one, an
active one serves at most $k$.

## Model

**Decision variables.** $n\,m$ binaries $x_{ij}$, $m$ binaries $y_j$ (hub
activated), $m$ non-negative continuous $z_j$ (maximum cost of hub $j$).

$$
\begin{aligned}
\min ~~ \sum_{j=1}^{m} f_j\, y_j + \sum_{j=1}^{m} z_j & & \\
\text{subject to} \quad \sum_{j=1}^{m} x_{ij} &= 1, & \forall i, \\
-\sum_{i=1}^{n} x_{ij} + k\, y_j &\ge 0, & \forall j, \\
-c_{ij}\, x_{ij} + z_j &\ge 0, & \forall i, j, \\
x_{ij}, y_j &\in \{0, 1\},\ z_j \ge 0. & &
\end{aligned}
$$

- the objective minimizes activation costs plus the maximum cost per hub;
- the first constraint assigns every terminal to one hub ($n$ constraints);
- the second links assignment and activation, in **aggregated** form, and
  imposes capacity ($m$ constraints);
- the third links assignment and the maximum variable ($n\,m$ constraints).

**First link: aggregated activation.** If a terminal is connected to hub
$j$, $j$ must be activated; from the contrapositive, an inactive hub
serves no one. Both imposed directly by the second constraint. The
opposite direction — an activated hub serves at least one terminal —
follows from the objective (since $f_j>0$). As in problem 7.2.

**Second link: maximum variable.** If terminal $i$ is connected to $j$,
$z_j \ge c_{ij}$: imposed directly. At the optimum, $z_j =
\max_{i:x_{ij}=1} c_{ij}$ exactly, because the objective minimizes $z_j$
and no other constraint involves it. As in problem 7.7.

## The model in gurobipy

```python
mod = gp.Model("hub_max")
x = mod.addVars(n, m, vtype=GRB.BINARY, name="x")
y = mod.addVars(m, vtype=GRB.BINARY, name="y")
z = mod.addVars(m, name="z")
mod.setObjective(gp.quicksum(f[j] * y[j] for j in range(m)) + z.sum(), GRB.MINIMIZE)
mod.addConstrs((gp.quicksum(x[i, j] for j in range(m)) == 1 for i in range(n)), name="assignment")
mod.addConstrs((-gp.quicksum(x[i, j] for i in range(n)) + k * y[j] >= 0 for j in range(m)), name="activation")
mod.addConstrs((-c[i][j] * x[i, j] + z[j] >= 0 for i in range(n) for j in range(m)), name="maximum")
```

## The instance

$n=3$ terminals, $m=3$ hubs, $k=2$:

| $c_{ij}$ | $j=1$ | $j=2$ | $j=3$ |
|---|---:|---:|---:|
| $i=1$ | 5 | 10 | 2 |
| $i=2$ | 5 | 4 | 6 |
| $i=3$ | 5 | 4 | 6 |

| | $j=1$ | $j=2$ | $j=3$ |
|---|---:|---:|---:|
| $f_j$ | 5 | 6 | 7 |

## Constructive heuristic: upper bound

A **next-fit** heuristic (bin packing): one hub at a time, up to $k$
terminals — the same generic heuristic as scheduling, reused from
`euristiche.py`. Terminals 1 and 2 on hub 1 (full), terminal 3 on hub 2.
Maximum costs: $z_1=\max(5,5)=5$, $z_2=4$. Value $5+6+5+4=20$:
$z(\mathrm{MILP}) \le \mathrm{ub} = 20$.

## LP relaxation and dual: lower bound

With $\bar\gamma_{ij}=0$ and $\bar\beta_j = f_j/k$ (the largest value
allowed), the constraint on $\alpha_i$ holds for **every** hub $j$, not
only the most convenient one: $\bar\alpha_i = \min_j \bar\beta_j$.

$$
\bar\beta = (5/2,\ 3,\ 7/2),\qquad \bar\alpha_i = 5/2\ \ \forall i,
$$

of value $3\cdot5/2=15/2$. By weak duality, $\mathrm{lb}=15/2 \le
z(\mathrm{LP}) \le z(\mathrm{MILP}) \le \mathrm{ub}=20$.

!!! warning "A common trap"
    The constraint on $\alpha_i$ holds for every hub $j$: setting
    $\bar\gamma_{ij}=0$ only for the "inconvenient" hubs is not enough to
    free $\alpha_i$ from that constraint. $\alpha_i$ stays bounded by the
    minimum over all hubs, not by a single one.

**What the solver says.** $z(\mathrm{LP})=25/2$,
$z(\mathrm{LP}^+)=1015/78\approx13.0$. $z(\mathrm{MILP})=19$, with hubs 1
and 3 activated (not 1 and 2): terminal 1 alone on hub 3 (the cheapest for
it), terminals 2 and 3 on hub 1. Heuristic gap $5.3\%$.

| $\mathrm{ub}$ | $\mathrm{lb}$ (dual) | $z(\mathrm{LP})$ | $z(\mathrm{LP}^+)$ | $z(\mathrm{MILP})$ | gap |
|---:|---:|---:|---:|---:|---:|
| 20 | $15/2$ | $25/2$ | $1015/78$ | 19 | $5.3\%$ |

![Optimal solution](img/cap08_hub_ottimo.png)

## Additional considerations

- $x_{ij} \le y_j$ (disaggregated) is implied by the aggregated
  activation constraint.
- With $M_j=\max_i c_{ij}$, $z_j \le M_j y_j$ is not a valid inequality
  (the model allows $z_j>0$ with $y_j=0$), but it is an
  **optimality-preserving constraint**: minimizing $z_j$, the optimum
  zeroes it anyway when $y_j=0$.

## Additional modelling questions

??? question "8.4.1 — Disaggregated activation link"
    Replace the aggregated constraint with $x_{ij} \le y_j$. Does the
    optimum change?

    ??? success "Solution"
        $x_{ij} \le y_j$ for every $i,j$ ($n\,m$ more constraints). The
        optimum stays $19$: the optimal solution already satisfies it.

??? question "8.4.2 — Forbidden connection"
    Terminal 1 cannot connect to hub 2. How is this modelled? What is the
    new optimum?

    ??? success "Solution"
        $x_{12}=0$. The optimum does not already use it (terminal 1 on
        hub 3): it stays $19$.

## Code

Full script —
[`python/fam08_4_hub.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam08_4_hub.py)
(reproducible with `python3 python/fam08_4_hub.py` from the `python/`
folder, calls `next_fit` from `euristiche.py`). Notebook —
[`notebooks/fam08_4_hub.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam08_4_hub.ipynb)
— opens in Colab from the badge at the top of the page.
