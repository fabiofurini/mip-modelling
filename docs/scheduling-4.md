# Parallel jobs: the processing time as a maximum

**Class:** MILP · **Links:** maximum variable · **Script:** `python/fam07_scheduling.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb)

!!! abstract "Problem 7.4"
    A company needs to execute $n$ jobs with $k$ machines. For each job $j$
    and machine $m$, $t_{jm} \in \mathbb{Q}_{>0}$ is the processing time. Each
    machine $m$ can execute at most $p_m \in \mathbb{Z}_{\ge 1}$ jobs, in
    parallel: all the jobs assigned to the same machine start together.
    Minimise the sum of the processing times of the machines, where the time
    of a machine is the time of the longest job among those assigned.

**The problem in words.** *We decide* on which machine each job goes.
*The objective*: the sum of the processing times of the machines, each equal
to the **maximum** of the times of the assigned jobs. *The constraints*: every
job on one machine; at most $p_m$ jobs on machine $m$. A maximum is not
linear, but it is linearised with a continuous variable and $n$ "$\ge$"
constraints per machine.

## Model

| Symbol | Type | Meaning |
|---|---|---|
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of jobs |
| $k$ | $\in \mathbb{Z}_{\ge 1}$ | number of machines |
| $t_{jm}$ | $\in \mathbb{Q}_{>0}$ | time of job $j$ on machine $m$ |
| $p_m$ | $\in \mathbb{Z}_{\ge 1}$ | maximum number of jobs on machine $m$ |

**Variables.** $n\,k$ binary $x_{jm}$ (job $j$ on machine $m$) and $k$
continuous non-negative $y_m$ = processing time of machine $m$.

$$
\begin{aligned}
\min ~~ \sum_{m=1}^{k} y_m & & \\
\text{subject to} \quad \sum_{m=1}^{k} x_{jm} &= 1, & \forall j, \\
\sum_{j=1}^{n} x_{jm} &\le p_m, & \forall m, \\
-t_{jm}\, x_{jm} + y_m &\ge 0, & \forall j,\ \forall m, \\
x_{jm} \in \{0, 1\},\quad y_m &\ge 0. &
\end{aligned}
$$

- the objective minimises the sum of the processing times;
- the **assignment** ($n$) and **cardinality** ($k$) constraints;
- the **maximum** constraints link assignments and times: if job $j$ is on
  machine $m$, the time of the machine is at least $t_{jm}$ ($n\,k$ linear
  constraints);
- the domain constraints define the variables.

!!! note "Link between the variables: the maximum variable in three steps"
    1. **From the constraint.** $x_{jm} = 1 \Rightarrow y_m \ge t_{jm}$ and, by
       contraposition, $y_m < t_{jm} \Rightarrow x_{jm} = 0$: the constraint
       gives $y_m \ge t_{jm} x_{jm}$; if $x_{jm} = 1$, $y_m \ge t_{jm}$; if
       $y_m < t_{jm}$, $x_{jm}$ cannot equal $1$. Holding for every $j$:
       $y_m \ge \max_j t_{jm} x_{jm}$.
    2. **From the optimum.** $\sum_j x_{jm} = 0 \Rightarrow y_m = 0$: not
       imposed by the constraints (they reduce to $y_m \ge 0$), follows from
       the objective because $y_m$ has coefficient $1 > 0$: lowering it to
       $0$ stays feasible and reduces the objective.
    3. **Synthesis.** In every optimum $y_m = \max_j t_{jm} x_{jm}$: if $y_m$
       exceeded the maximum, setting it equal to the maximum would keep all
       constraints and reduce the objective.

## The model in gurobipy

```python
m = gp.Model("parallel");  m.Params.OutputFlag = 0
x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
y = m.addVars(k, name="y")                                   # continuous, >= 0
m.setObjective(y.sum(), GRB.MINIMIZE)
m.addConstrs((x.sum(j, "*") == 1 for j in range(n)), name="assign")
m.addConstrs((x.sum("*", mm) <= p[mm] for mm in range(k)), name="cardinality")
m.addConstrs((-t[j][mm] * x[j, mm] + y[mm] >= 0
              for j in range(n) for mm in range(k)), name="maximum")
m.optimize()
```

## The instance

| $t_{jm}$ | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $j=1$ | 6 | 5 | 3 |
| $j=2$ | 5 | 10 | 2 |
| $j=3$ | 20 | 13 | 10 |

| | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $p_m$ | 1 | 2 | 2 |

## Constructive heuristic: upper bound

Next-fit on the cardinalities: machine 1 is filled up to $p_1$ jobs, then
machine 2, and so on.

- **Step 1.** Job 1 on machine 1: $y[1] = 6$.
- **Step 2.** Machine 1 is full ($p_1 = 1$): job 2 on machine 2, $y[2] = 10$.
- **Step 3.** Job 3 on machine 2: $y[2] = \max(10, 13) = 13$.

$\bar y = (6, 13, 0)$, value $19$: $z(\mathrm{MILP}) \le 19$.

## LP relaxation and dual: lower bound

With $\mu_j$ free (assignment), $\pi_m \le 0$ (cardinality) and
$\lambda_{jm} \ge 0$ (maximum):

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} \mu_j + \sum_{m=1}^{k} p_m\, \pi_m & & \\
\text{subject to} \quad \mu_j + \pi_m - t_{jm}\, \lambda_{jm} &\le 0, & \forall j,\ \forall m, \\
\sum_{j=1}^{n} \lambda_{jm} &\le 1, & \forall m, \\
\mu_j \gtreqless 0,\quad \pi_m \le 0,\quad \lambda_{jm} &\ge 0. &
\end{aligned}
$$

The second constraint is the reduced cost of $y_m$: the coefficient $1$ in
the primal objective limits the sum of the $\lambda_{jm}$.

**A hand-built dual solution.** $\bar\lambda_{jm} = 1/3$, $\bar\pi_m = 0$,
$\bar\mu_j = \min_m t_{jm}/3$: $1, \tfrac{2}{3}, \tfrac{10}{3}$, value $5$:
$5 \le z(\mathrm{MILP}) \le 19$.

**What the solver says.** $z(\mathrm{LP}) = 520/49 = 10.61$. Integer optimum
$15$: job 1 on machine 2, jobs 2 and 3 on machine 3, $\tilde y = (0, 5, 10)$.
The uniform split of the $\lambda$ is the first that comes to mind, not the
best.

| $\mathrm{ub}$ | $\mathrm{lb}$ (hand dual) | $z(\mathrm{LP})$ | $z(\mathrm{MILP})$ | heuristic gap |
|---:|---:|---:|---:|---:|
| 19 | 5 | $520/49$ | 15 | $26.7\%$ |

## Additional considerations

- With $\bar t_m = \max_j t_{jm}$, the constraints $\bar t_m \sum_j x_{jm} - y_m \ge 0$
  force $y_m = 0$ on an empty machine: **not** valid (the model allows
  $y_m > 0$ on an empty machine) but **optimality-preserving**. The distinction
  between "valid" and "optimality-preserving" is the same as between the two
  steps of the link.

## Additional modelling questions

??? question "7.4.1 — Minimising the time of the slowest machine"
    Minimise the maximum of the processing times (makespan), not the sum.

    ??? success "Solution"
        A variable $w \ge 0$ with $w \ge y_m$ for every $m$ and objective
        $\min\ w$: the min-max pattern. The $y_m$ leave the objective, so
        "$y_m$ = maximum in every optimum" falls; it remains true that there
        exists an optimum where it is. Optimal makespan $10$: job 3 requires
        at least $10$ minutes anywhere.

??? question "7.4.2 — Fixed cost if the machine works"
    Switching a machine on costs $g_m = 4$ euros, one minute costs $1$ euro.
    Which link is needed and what is the smallest big-M?

    ??? success "Solution"
        An activation $v_m \in \{0,1\}$ and the link
        $y_m > 0 \Rightarrow v_m = 1$ imposed by $y_m \le M_m v_m$; the
        smallest valid $M_m$ is $\bar t_m = \max_j t_{jm}$. The opposite
        direction follows from the objective because $g_m > 0$. Optimum
        $23 = 15 + 2 \cdot 4$.

## Code

Full script: [`python/fam07_scheduling.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_scheduling.py);
notebook: [`notebooks/fam07_scheduling.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb).
