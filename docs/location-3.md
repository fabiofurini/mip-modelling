# Signal coverage with interference

**Class:** BIP · **Links:** if and only if (threshold + interference) · **Script:** `python/fam08_3_coverage.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_3_coverage.ipynb)

!!! abstract "Problem 8.3"
    An operator chooses at most $k \in \mathbb{Z}_{\ge 1}$ locations,
    among $m \in \mathbb{Z}_{\ge 1}$ candidates, to serve $n \in
    \mathbb{Z}_{\ge 1}$ clients. $s_{lc} \in \mathbb{Q}_{\ge 0}$ is the
    signal received by client $c$ if $l$ is installed. A client is
    **covered** if and only if the total signal is at least $t \in
    \mathbb{Q}_{>0}$ *and* at most one location generates for it a signal
    $\ge b \in \mathbb{Q}_{>0}$. $p_c \in \mathbb{Q}_{>0}$ is the profit if
    covered. We want to maximize the total profit.

**The problem in words.** *We decide* which locations to install (at most
$k$). *The objective*: maximum total profit. *The constraints*: a client
is covered if and only if it receives enough signal and not too much
interference; at most $k$ installed locations.

## Model

**Data.** $m$, $n$, $s_{lc} \in \mathbb{Q}_{\ge 0}$, $p_c \in
\mathbb{Q}_{>0}$, threshold $t$, interference limit $b$, budget $k$. For
every client $c$: $\mathscr{L}_c = \{l : s_{lc} \ge b\}$.

**Decision variables.** $m$ binaries $x_l$ (location installed), $n$
binaries $y_c$ (client covered).

$$
\begin{aligned}
\max ~~ \sum_{c=1}^{n} p_c\, y_c & & \\
\text{subject to} \quad -\sum_{l=1}^{m} s_{lc}\, x_l + t\, y_c &\le 0, & \forall c, \\
\sum_{l \in \mathscr{L}_c} x_l + (m-1)\, y_c &\le m, & \forall c, \\
\sum_{l=1}^{m} x_l &\le k, & \\
x_l, y_c &\in \{0, 1\}. & &
\end{aligned}
$$

- the objective maximizes total profit;
- the first constraint links coverage and received signal ($n$ constraints);
- the second links coverage and interference ($n$ constraints);
- the third caps installed locations at $k$ (one constraint).

**The link: an if and only if.** One direction — $y_c=1 \Rightarrow$
signal $\ge t$ **and** at most one strong location — is imposed directly
by the two constraints. The other direction — if both conditions hold,
the client is covered — is not imposed by the constraints (which also
allow $y_c=0$), but follows from optimality: since $p_c>0$ and $y_c$
appears only in these two constraints, raising it to $1$ remains feasible
and raises the objective. The same pattern as problem 7.6.

## The model in gurobipy

```python
mod = gp.Model("coverage_interference")
x = mod.addVars(m, vtype=GRB.BINARY, name="x")
y = mod.addVars(n, vtype=GRB.BINARY, name="y")
mod.setObjective(gp.quicksum(p[c] * y[c] for c in range(n)), GRB.MAXIMIZE)
mod.addConstrs((-gp.quicksum(s[l][c] * x[l] for l in range(m)) + t * y[c] <= 0
                for c in range(n)), name="threshold")
mod.addConstrs((gp.quicksum(x[l] for l in L[c]) + (m - 1) * y[c] <= m
                for c in range(n)), name="interference")
mod.addConstr(x.sum() <= k, name="budget")
```

## The instance

$m=3$, $n=5$, $t=5$, $b=4$, $k=2$:

| $s_{lc}$ | $c=1$ | $c=2$ | $c=3$ | $c=4$ | $c=5$ |
|---|---:|---:|---:|---:|---:|
| $l=1$ | 6 | 0 | 5 | 3 | 1 |
| $l=2$ | 4 | 5 | 2 | 0 | 0 |
| $l=3$ | 0 | 7 | 5 | 4 | 2 |

| | $c=1$ | $c=2$ | $c=3$ | $c=4$ | $c=5$ |
|---|---:|---:|---:|---:|---:|
| $p_c$ | 10 | 20 | 5 | 15 | 25 |

With $b=4$: $\mathscr{L}_1=\{1,2\}$, $\mathscr{L}_2=\{3\}$,
$\mathscr{L}_3=\{1,3\}$, $\mathscr{L}_4=\{3\}$, $\mathscr{L}_5=\emptyset$.

## Constructive heuristic: lower bound

The first $k$ locations open. Client 1: signal $10\ge5$ but 2 strong
locations ($>1$): **not covered**. Client 2: signal $5\ge5$, 0 strong
locations: **covered**. Client 3: signal $7\ge5$, 1 strong location:
**covered**. Clients 4 and 5: insufficient signal: **not covered**. Value
$20+5=25$: $z(\mathrm{MILP}) \ge \mathrm{lb} = 25$.

## LP relaxation and dual: upper bound

With $\bar\pi_c=0$, $\bar\mu=0$ and $\bar\lambda_c = p_c/(m-1) = p_c/2$:

$$
\bar\lambda_1=5,\ \bar\lambda_2=10,\ \bar\lambda_3=5/2,\ \bar\lambda_4=15/2,\ \bar\lambda_5=25/2,
$$

of value $m\sum_c\bar\lambda_c = 3\cdot75/2=225/2$. By weak duality (a
maximisation problem: the heuristic gives the lower bound, the dual the
upper bound), $\mathrm{lb}=25 \le z(\mathrm{MILP}) \le z(\mathrm{LP}) \le
\mathrm{ub}=225/2$.

**What the solver says.** $z(\mathrm{LP}) = 41925/646 \approx 64.9$,
$z(\mathrm{LP}^+) = 125/2 = 62.5$. $z(\mathrm{MILP}) = 45$, with locations
1 and 3 installed and clients 1, 2, 4 covered (not 3 or 5): different from
what the heuristic found. Heuristic gap $44.4\%$.

| $\mathrm{lb}$ | $\mathrm{ub}$ (dual) | $z(\mathrm{LP})$ | $z(\mathrm{LP}^+)$ | $z(\mathrm{MILP})$ | gap |
|---:|---:|---:|---:|---:|---:|
| 25 | $225/2$ | $41925/646$ | $125/2$ | 45 | $44.4\%$ |

![Optimal solution](img/cap08_copertura_ottimo.png)

## Additional considerations

- Client 5 can never be covered: maximum signal $1+0+2=3<5$ even opening
  all locations.
- For clients with $|\mathscr{L}_c|\le1$ (2, 4, 5) the interference
  constraint is redundant.

## Additional modelling questions

??? question "8.3.1 — Guaranteed minimum coverage"
    At least 3 clients must be covered. How does the model change? What
    is the new optimum?

    ??? success "Solution"
        $\sum_c y_c \ge 3$. The optimum already covers 3 clients: it
        stays $45$.

??? question "8.3.2 — Conditional installation"
    Location 1 can only be installed if location 3 is also installed. How
    is this modelled? What is the new optimum?

    ??? success "Solution"
        $x_1 \le x_3$. The optimum already installs both: it stays $45$.

## Code

Full script —
[`python/fam08_3_coverage.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam08_3_coverage.py)
(reproducible with `python3 python/fam08_3_coverage.py` from the
`python/` folder). Notebook —
[`notebooks/fam08_3_coverage.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam08_3_coverage.ipynb)
— opens in Colab from the badge at the top of the page.
