# Classes with completion bonus and "if and only if" reduction

**Class:** BIP · **Links:** if and only if (two), CNF · **Script:** `python/fam07_scheduling.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb)

!!! abstract "Problem 7.6"
    A company has $n$ jobs executable on a machine with availability $a$. For
    each job $j$, $t_j$ is the time and $r_j$ the revenue. The jobs are
    partitioned into $q \ge 2$ classes. The availability is reduced by $u > 0$
    minutes *if and only if* the machine executes jobs of at least two
    different classes. For each class $c$ an extra revenue $v_c > 0$ is
    obtained *if and only if* all the jobs of the class are executed.
    Maximise the total revenue.

**The problem in words.** Two "if and only if"s: one rewards (completion),
one penalises (mixing). For each it suffices to impose one direction: the
objective imposes the other.

## Model

**Variables.** $n + q + 1$ binary: $x_j$ (job executed), $y_c$ (class
complete), $z$ (jobs of at least two classes).

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} r_j\, x_j + \sum_{c=1}^{q} v_c\, y_c & & \\
\text{subject to} \quad x_j - y_c &\ge 0, & \forall c,\ \forall j \in \mathscr{J}_c, \\
x_j + x_i - z &\le 1, & \forall c < g,\ \forall j \in \mathscr{J}_c,\ \forall i \in \mathscr{J}_g, \\
\sum_{j=1}^{n} t_j\, x_j + u\, z &\le a, & \\
x_j,\ y_c,\ z &\in \{0, 1\}. &
\end{aligned}
$$

- the objective maximises revenues of the jobs plus bonuses of the complete
  classes;
- the **all** constraints: if a class is declared complete, all its jobs are
  executed ($n$ constraints);
- the **mixed** constraints: if two jobs of different classes are executed,
  $z = 1$ ($\sum_{c<g} |\mathscr{J}_c|\,|\mathscr{J}_g|$ constraints);
- the **availability** constraint with the reduction $u z$ ($1$ constraint);
- the domain constraints.

!!! note "Link between the variables: four implications"
    **$y_c$, from the constraint.** $y_c \Rightarrow (x_j \,\mathtt{AND}\, x_i \,\mathtt{AND}\, \dots)$:
    the expression $(x_j \,\mathtt{AND}\, \dots) \,\mathtt{OR}\, \mathtt{NOT}\,y_c$ becomes
    by distributivity the CNF $(x_j \,\mathtt{OR}\, \mathtt{NOT}\,y_c) \,\mathtt{AND}\, \dots$,
    i.e.\ $x_j \ge y_c$. **$y_c$, from the optimum.** If all jobs are
    executed then $y_c = 1$: setting $y_c = 1$ stays feasible and increases
    the objective by $v_c > 0$.

    **$z$, from the constraint.** $x_j \,\mathtt{AND}\, x_i \Rightarrow z$ for
    every mixed pair: De Morgan gives $\mathtt{NOT}\,x_j \,\mathtt{OR}\, \mathtt{NOT}\,x_i \,\mathtt{OR}\, z$,
    i.e.\ $x_j + x_i - z \le 1$. **$z$, from the optimum.** If the executed
    jobs lie in a single class, $z = 0$: setting $z = 0$ stays feasible,
    frees $u$ minutes and does not change the objective (where $z$ does not
    appear) — "there exists an optimum", not "in every optimum".

## The model in gurobipy

```python
pairs = [(j, i) for c in range(q) for g in range(c + 1, q)
         for j in J[c] for i in J[g]]
m = gp.Model("classes_bonus");  m.Params.OutputFlag = 0
x = m.addVars(n, vtype=GRB.BINARY, name="x")
y = m.addVars(q, vtype=GRB.BINARY, name="y")
z = m.addVar(vtype=GRB.BINARY, name="z")
m.setObjective(gp.quicksum(r[j] * x[j] for j in range(n))
               + gp.quicksum(v[c] * y[c] for c in range(q)), GRB.MAXIMIZE)
m.addConstrs((x[j] - y[c] >= 0 for c in range(q) for j in J[c]), name="all")
m.addConstrs((x[j] + x[i] - z <= 1 for (j, i) in pairs), name="mixed")
m.addConstr(gp.quicksum(t[j] * x[j] for j in range(n)) + u * z <= a, name="availability")
m.optimize()
```

## The instance

$n = 6$, $q = 3$: $\mathscr{J}_1 = \{1, 2\}$, $\mathscr{J}_2 = \{3, 4\}$,
$\mathscr{J}_3 = \{5, 6\}$, $a = 50$, $u = 10$.

| | $j=1$ | $j=2$ | $j=3$ | $j=4$ | $j=5$ | $j=6$ |
|---|---:|---:|---:|---:|---:|---:|
| $r_j$ | 10 | 5 | 20 | 12 | 10 | 22 |
| $t_j$ | 5 | 15 | 25 | 15 | 10 | 38 |

| | $c=1$ | $c=2$ | $c=3$ |
|---|---:|---:|---:|
| $v_c$ | 5 | 4 | 10 |

## Constructive heuristic: lower bound

Class by class; from the second class on, the first executed job also pays
$u$.

- **Steps 1–2.** Class 1: $x[1] = x[2] = 1$, $ra = 30$; class complete,
  $y[1] = 1$.
- **Step 3.** Class 2: $t_3 + u = 35 > 30$, skipped. **Step 4.**
  $t_4 + u = 25 \le 30$: $x[4] = 1$, $z = 1$, $ra = 5$.
- **Steps 5–6.** Class 3: $t_5, t_6 > 5$, skipped.

Revenue $10 + 5 + 12 + 5 = 32$: $z(\mathrm{MILP}) \ge 32$.

## LP relaxation and dual: upper bound

With $\pi_j \le 0$ (all), $\lambda_{ji} \ge 0$ (mixed), $\mu \ge 0$
(availability):

$$
\begin{aligned}
\min ~~ \sum_{\text{mixed pairs}} \lambda_{ji} + a\, \mu & & \\
\text{subject to} \quad \pi_j + \sum_{i \notin \mathscr{J}_c} \lambda_{ji} + t_j\, \mu &\ge r_j, & \forall c,\ \forall j \in \mathscr{J}_c, \\
-\sum_{j \in \mathscr{J}_c} \pi_j &\ge v_c, & \forall c, \\
-\sum_{\text{mixed pairs}} \lambda_{ji} + u\, \mu &\ge 0. &
\end{aligned}
$$

**A hand-built dual solution.** The bonus of every class loaded on one job:
$\bar\pi_1 = -5$, $\bar\pi_3 = -4$, $\bar\pi_5 = -10$; $\bar\lambda = 0$;
$\bar\mu = \max_j (r_j - \bar\pi_j)/t_j = \max\{3, \tfrac{1}{3}, \tfrac{24}{25}, \tfrac{4}{5}, 2, \tfrac{11}{19}\} = 3$;
value $150$: $32 \le z(\mathrm{MILP}) \le 150$.

**What the solver says.** $z(\mathrm{LP}) = 5280/113 = 46.7$. Integer optimum
$42$: class 3 alone, complete, jobs 5 and 6 ($48 \le 50$, $z = 0$), revenue
$10 + 22 + 10$. Heuristic gap $24\%$.

| $\mathrm{lb}$ | $\mathrm{ub}$ (hand dual) | $z(\mathrm{LP})$ | $z(\mathrm{MILP})$ | heuristic gap |
|---:|---:|---:|---:|---:|
| 32 | 150 | $5280/113$ | 42 | $23.8\%$ |

## Additional considerations

- The optimality direction for $y_c$ is imposed with
  $\sum_{j \in \mathscr{J}_c} x_j - y_c \le |\mathscr{J}_c| - 1$
  ($q$ optimality-preserving, not valid, constraints).
- The optimality direction for $z$: $z \le \sum_{j \notin \mathscr{J}_c} x_j$
  for every $c$.
- An aggregated form with class variables $w_c \ge x_j$ and
  $\sum_c w_c - 1 \le (q-1) z$ replaces the pairs: same integer set,
  different relaxation.

## Additional modelling questions

??? question "7.6.1 — At least one job per class"
    Execute at least one job of every class. What happens to $z$?

    ??? success "Solution"
        Covering per class $\sum_{j \in \mathscr{J}_c} x_j \ge 1$. With every
        class touched, the "mixed" constraints force $z = 1$: the reduction
        is certain and $z$ can be eliminated ($a - u$). Optimum $40$.

??? question "7.6.2 — Penalty for a class started and not finished"
    Starting a class without completing it costs $w = 3$.

    ??? success "Solution"
        A variable $s_c$ "class started" with $s_c \ge x_j$ for
        $j \in \mathscr{J}_c$; objective $- w \sum_c (s_c - y_c)$. The
        direction $s_c = 0$ on an empty class follows from the objective
        ($-w < 0$ in a maximisation); $y_c \le s_c$ holds in every feasible
        solution from $y_c \le x_j \le s_c$. The optimum stays $42$.

## Code

Full script: [`python/fam07_scheduling.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_scheduling.py);
notebook: [`notebooks/fam07_scheduling.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb).
