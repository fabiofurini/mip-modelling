# Capacitated facility location

**Class:** MILP · **Links:** aggregated activation (also the capacity constraint) · **Script:** `python/fam08_1_capacitated.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_1_capacitated.ipynb)

!!! abstract "Problem 8.1"
    A company must serve $n \in \mathbb{Z}_{\ge 1}$ clients and has
    identified $m \in \mathbb{Z}_{\ge 1}$ candidate locations. For each
    client $c$, $d_c \in \mathbb{Q}_{>0}$ is the demand in liters. For each
    location $l$ and client $c$, $t_{lc} \in \mathbb{Q}_{>0}$ is the
    transport cost per liter. For each location $l$, $u_l \in
    \mathbb{Q}_{>0}$ is the capacity and $i_l \in \mathbb{Q}_{>0}$ the
    installation cost. We want to decide where to install and how to serve
    clients, at minimum cost.

**The problem in words.** *We decide* where to install facilities and how
much to ship from each location to each client. *The objective*: minimum
total cost (installation plus transport). *The constraints*: an
uninstalled location ships nothing, and an installed one does not exceed
its capacity; demand must be satisfied exactly. The **capacitated facility
location** problem.

## Model

**Data.**

| Symbol | Type | Meaning |
|---|---|---|
| $m$ | $\in \mathbb{Z}_{\ge 1}$ | number of locations, $l \in \{1, 2, \dots, m\}$ |
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of clients, $c \in \{1, 2, \dots, n\}$ |
| $t_{lc}$ | $\in \mathbb{Q}_{>0}$ | transport cost from location $l$ to client $c$ |
| $u_l$ | $\in \mathbb{Q}_{>0}$ | capacity of location $l$ |
| $i_l$ | $\in \mathbb{Q}_{>0}$ | installation cost of location $l$ |
| $d_c$ | $\in \mathbb{Q}_{>0}$ | demand of client $c$ |

**Decision variables.** $m$ binaries $x_l$ (location $l$ installed) and
$m\,n$ non-negative continuous $y_{lc}$ (liters shipped from $l$ to $c$):

$$
x_l = \begin{cases} 1 & \text{if location } l \text{ is installed,}\\ 0 & \text{otherwise,}\end{cases}
\qquad y_{lc} = \text{liters shipped from } l \text{ to } c.
$$

MILP model:

$$
\begin{aligned}
\min ~~ \sum_{l=1}^{m} i_l\, x_l + \sum_{l=1}^{m}\sum_{c=1}^{n} t_{lc}\, y_{lc} & & \\
\text{subject to} \quad u_l\, x_l - \sum_{c=1}^{n} y_{lc} &\ge 0, & \forall l \in \{1, 2, \dots, m\}, \\
\sum_{l=1}^{m} y_{lc} &= d_c, & \forall c \in \{1, 2, \dots, n\}, \\
x_l &\in \{0, 1\}, & \forall l \in \{1, 2, \dots, m\}, \\
y_{lc} &\ge 0, & \forall l, c.
\end{aligned}
$$

- the objective minimizes total cost (installation plus transport);
- the first constraint links transport and installation **and** imposes
  capacity ($m$ linear constraints);
- the second satisfies every client's demand ($n$ linear constraints);
- the remaining constraints define the variables.

**The link.** If a positive quantity ships from location $l$, the location
must be installed; from the contrapositive, a closed location ships
nothing. Both directions are imposed directly by the first constraint. The
opposite direction — an installed location ships something — is not
imposed but follows from the objective: since $i_l > 0$, an optimum never
leaves an open location unused. A single family of constraints thus acts
as both the activation link and the capacity constraint.

## The model in gurobipy

```python
mod = gp.Model("capacitated_location")
x = mod.addVars(m, vtype=GRB.BINARY, name="x")
y = mod.addVars(m, n, name="y")
mod.setObjective(gp.quicksum(i[l] * x[l] for l in range(m))
                 + gp.quicksum(t[l][c] * y[l, c] for l in range(m) for c in range(n)), GRB.MINIMIZE)
mod.addConstrs((u[l] * x[l] - gp.quicksum(y[l, c] for c in range(n)) >= 0
                for l in range(m)), name="capacity")
mod.addConstrs((gp.quicksum(y[l, c] for l in range(m)) == d[c] for c in range(n)), name="demand")
```

## The instance

$m = 2$ locations, $n = 3$ clients:

| $t_{lc}$ | $c=1$ | $c=2$ | $c=3$ |
|---|---:|---:|---:|
| $l=1$ | 4 | 5 | 6 |
| $l=2$ | 6 | 4 | 3 |

| | $l=1$ | $l=2$ |
|---|---:|---:|
| $u_l$ | 50 | 50 |
| $i_l$ | 60 | 90 |

| | $c=1$ | $c=2$ | $c=3$ |
|---|---:|---:|---:|
| $d_c$ | 8 | 25 | 27 |

## Constructive heuristic: upper bound

Locations are scanned in order; for each, clients are shipped the minimum
of residual capacity and residual demand.

Execution: location 1 ships $8$ to client 1, $25$ to client 2, $17$ to
client 3 (capacity exhausted); location 2 ships the remaining $10$ to
client 3. Value: $60+90 + (4{\cdot}8+5{\cdot}25+6{\cdot}17+3{\cdot}10) =
150+289 = 439$. Hence $z(\mathrm{MILP}) \le \mathrm{ub} = 439$.

## LP relaxation and dual: lower bound

With $\bar\mu_l = i_l/u_l$ (spreading the fixed cost over capacity) and
$\bar\pi_c = \min_l(t_{lc}+\bar\mu_l)$:

$$
\bar\mu_1 = 6/5,\quad \bar\mu_2 = 9/5,\qquad
\bar\pi_1 = 26/5,\quad \bar\pi_2 = 29/5,\quad \bar\pi_3 = 24/5,
$$

of value $8{\cdot}26/5 + 25{\cdot}29/5 + 27{\cdot}24/5 = 1581/5$. By weak
duality, $\mathrm{lb} = 1581/5 \le z(\mathrm{LP}) \le z(\mathrm{MILP}) \le
\mathrm{ub} = 439$.

**What the solver says.** $z(\mathrm{LP}) = 1581/5$ exactly: the hand-built
dual solution is already optimal. Strengthening with $x_l \le 1$,
$z(\mathrm{LP}^+) = 317$. $z(\mathrm{MILP}) = 365$, with both locations
open: location 1 serves client 1 and part of client 2, location 2 the rest
of client 2 and all of client 3. Heuristic gap $20.3\%$.

| $\mathrm{ub}$ | $\mathrm{lb}$ (dual) | $z(\mathrm{LP})$ | $z(\mathrm{LP}^+)$ | $z(\mathrm{MILP})$ | gap |
|---:|---:|---:|---:|---:|---:|
| 439 | $1581/5$ | $1581/5$ | 317 | 365 | $20.3\%$ |

![Optimal solution](img/cap08_capacitata_ottimo.png)

## Additional considerations

- If $u_l < d_c$ no single location can satisfy client $c$'s demand alone:
  not the case here, but worth checking.
- $y_{lc} \le d_c\, x_l$ is valid but implied jointly by the two
  constraints.

## Additional modelling questions

??? question "8.1.1 — Minimum lot for every open location"
    Every open location must ship at least $5$ liters. How does the model
    change? What is the new optimum?

    ??? success "Solution"
        $\sum_c y_{lc} \ge 5\, x_l$ for every $l$ ($m$ constraints). On
        the instance it is never binding: the optimum stays $365$.

??? question "8.1.2 — Conditional opening"
    Location 2 can only be installed if location 1 is also installed. How
    is this modelled? What is the new optimum?

    ??? success "Solution"
        $x_2 \le x_1$ (one constraint). The optimum already opens both
        locations: it stays $365$.

## Code

Full script —
[`python/fam08_1_capacitated.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam08_1_capacitated.py)
(reproducible with `python3 python/fam08_1_capacitated.py` from the
`python/` folder). Notebook —
[`notebooks/fam08_1_capacitated.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam08_1_capacitated.ipynb)
— opens in Colab from the badge at the top of the page.
