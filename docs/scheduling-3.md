# Job selection with revenues and fixed-cost machines

**Class:** BIP · **Links:** activation (aggregated), maximisation problem · **Script:** `python/fam07_scheduling.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb)

!!! abstract "Problem 7.3"
    A company can execute $n \in \mathbb{Z}_{\ge 1}$ jobs and has $k \in \mathbb{Z}_{\ge 1}$
    machines. For each job $j$, $t_j \in \mathbb{Q}_{>0}$ is the processing time
    (the same on every machine) and $r_j \in \mathbb{Q}_{>0}$ the revenue if the
    job is executed. For each machine $m$, $a_m \in \mathbb{Q}_{>0}$ is the
    availability and $c_m \in \mathbb{Q}_{>0}$ the cost if the machine is used.
    Each machine processes one job at a time. The company wants to choose
    which jobs to execute, and on which machines, to maximise the profit:
    revenues of the executed jobs minus costs of the machines used.

**The problem in words.** *We decide* which jobs to execute, on which
machines, and which machines to switch on. *The objective*: maximum profit.
*The constraints*: every job on at most one machine; no job on a machine
switched off; availability respected. It is [problem 7.2](scheduling-2.md)
where the jobs are no longer compulsory and have a revenue: a
**maximisation** problem, and the roles of the bounds swap.

## Model

**Data (input of the model).**

| Symbol | Type | Meaning |
|---|---|---|
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of jobs, $j \in \{1, 2, \dots, n\}$ |
| $k$ | $\in \mathbb{Z}_{\ge 1}$ | number of machines, $m \in \{1, 2, \dots, k\}$ |
| $t_j$ | $\in \mathbb{Q}_{>0}$ | processing time of job $j$ |
| $r_j$ | $\in \mathbb{Q}_{>0}$ | revenue if job $j$ is executed |
| $a_m$ | $\in \mathbb{Q}_{>0}$ | availability of machine $m$ |
| $c_m$ | $\in \mathbb{Q}_{>0}$ | fixed cost if machine $m$ is used |

**Decision variables.** $n\,k + k$ binary variables: $x_{jm} = 1$ if job $j$
is executed by machine $m$; $y_m = 1$ if machine $m$ is used.

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} \sum_{m=1}^{k} r_j\, x_{jm} - \sum_{m=1}^{k} c_m\, y_m & & \\
\text{subject to} \quad \sum_{m=1}^{k} x_{jm} &\le 1, & \forall j \in \{1, 2, \dots, n\}, \\
\sum_{j=1}^{n} t_j\, x_{jm} - a_m\, y_m &\le 0, & \forall m \in \{1, 2, \dots, k\}, \\
x_{jm} &\in \{0, 1\}, & \forall j,\ \forall m, \\
y_m &\in \{0, 1\}, & \forall m \in \{1, 2, \dots, k\}.
\end{aligned}
$$

- the objective maximises the profit, revenues of the executed jobs minus
  costs of the machines used;
- the **at most one** constraints ensure that each job is assigned to at
  most one machine ($n$ linear constraints);
- the **link** constraints connect assignments and usage and impose the
  capacity ($k$ linear constraints);
- the domain constraints define the variables.

!!! note "Link between the variables"
    The same as in problem 7.2, with $t_j$ in place of $t_{jm}$. The
    "optimality" direction changes sign: since $c_m > 0$, if $y_m = 1$ with no
    jobs, setting $y_m = 0$ stays feasible and **increases** the profit by
    $c_m$ — in a maximisation problem the direction of the improvement is
    reversed, the structure of the argument is not.

## The model in gurobipy

```python
m = gp.Model("selection");  m.Params.OutputFlag = 0
x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
y = m.addVars(k, vtype=GRB.BINARY, name="y")
m.setObjective(gp.quicksum(r[j] * x[j, mm] for j in range(n) for mm in range(k))
               - gp.quicksum(c[mm] * y[mm] for mm in range(k)), GRB.MAXIMIZE)
m.addConstrs((x.sum(j, "*") <= 1 for j in range(n)), name="at_most_one")
m.addConstrs((gp.quicksum(t[j] * x[j, mm] for j in range(n)) - a[mm] * y[mm] <= 0
              for mm in range(k)), name="link")
m.optimize()
```

## The instance

| | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $a_m$ | 105 | 110 | 100 |
| $c_m$ | 20 | 30 | 15 |

| | $j=1$ | $j=2$ | $j=3$ |
|---|---:|---:|---:|
| $t_j$ | 25 | 40 | 75 |
| $r_j$ | 10 | 15 | 30 |

## Constructive heuristic: lower bound

In a maximisation problem a feasible solution gives a *lower* bound. A job
that does not fit anywhere is **skipped**. The best-fit chooses the
**fullest** machine among those that are enough:

- **Step 1.** Job 1 ($t_1 = 25$): $ra = (105, 110, 100)$; the fullest is
  machine 3: $x[1][3] = 1$, $ra[3] = 75$.
- **Step 2.** Job 2 ($t_2 = 40$): the fullest is still machine 3:
  $x[2][3] = 1$, $ra[3] = 35$.
- **Step 3.** Job 3 ($t_3 = 75$): machine 3 is not enough; between 1 and 2
  the fullest is machine 1: $x[3][1] = 1$, $ra[1] = 30$.

Profit $10 + 15 + 30 - 20 - 15 = 20$: $z(\mathrm{MILP}) \ge 20$. Next-fit and
first-fit fill machine 1 first and reach $5$.

## LP relaxation and dual: upper bound

With $\mu_j \ge 0$ (at most one) and $\pi_m \ge 0$ (link):

$$
\begin{aligned}
\min ~~ \sum_{j=1}^{n} \mu_j & & \\
\text{subject to} \quad \mu_j + t_j\, \pi_m &\ge r_j, & \forall j,\ \forall m, \\
-a_m\, \pi_m &\ge -c_m, & \forall m, \\
\mu_j \ge 0,\quad \pi_m &\ge 0. &
\end{aligned}
$$

**A hand-built dual solution.** $\bar\pi_m = c_m/a_m$: $\tfrac{4}{21}, \tfrac{3}{11}, \tfrac{3}{20}$;
then $\bar\mu_j = \max\{0, \max_m (r_j - t_j \bar\pi_m)\}$:
$\bar\mu_1 = \tfrac{25}{4}$, $\bar\mu_2 = 9$, $\bar\mu_3 = \tfrac{75}{4}$;
value $34$:

$$20 ~\le~ z(\mathrm{MILP}) ~\le~ 34.$$

**What the solver says.** $z(\mathrm{LP}) = 34$: the hand-built solution is
optimal for the dual; the strengthened relaxation drops to $680/21 = 32.38$.
Integer optimum $25$: jobs 1 and 3 on machine 3 ($25 + 75 = 100$, exactly the
availability), profit $40 - 15$; job 2 does not pay because it would require a
second machine ($c_1 = 20 > r_2 = 15$). Heuristic gap: $20\%$.

| $\mathrm{lb}$ (best-fit) | $\mathrm{ub}$ (hand dual) | $z(\mathrm{LP})$ | $z(\mathrm{LP}^+)$ | $z(\mathrm{MILP})$ | heuristic gap |
|---:|---:|---:|---:|---:|---:|
| 20 | 34 | 34 | $680/21$ | 25 | $20.0\%$ |

## Additional considerations

- $y_m \le 1$ strengthens the relaxation ($34 \to 32.38$); $x_{jm} \le 1$ is
  implied.
- The disaggregated links $x_{jm} \le y_m$ are valid and strengthen the
  relaxation.
- If $r_j < \min_m c_m$ and job $j$ is the only one on a machine, executing it
  never pays (job 2 in the instance).

## Additional modelling questions

??? question "7.3.1 — All jobs compulsory"
    All jobs must be executed. How does the model change and how much does
    the obligation cost?

    ??? success "Solution"
        The "at most one" constraints become equalities $\sum_m x_{jm} = 1$:
        the model becomes that of problem 7.2 with the constant $\sum_j r_j$
        in the objective. The optimum drops from $25$ to $20$ (two machines
        are needed: job 3 on machine 3, jobs 1 and 2 on machine 1). The
        obligation costs $5$ euros.

??? question "7.3.2 — A job conditional on another"
    Job 3 can be executed only if job 2 is executed too. Write the constraint
    and find the new optimum.

    ??? success "Solution"
        "3 $\Rightarrow$ 2" with the propositions $\sum_m x_{3m} = 1$ and
        $\sum_m x_{2m} = 1$:

        $$\sum_{m=1}^{k} x_{3m} \le \sum_{m=1}^{k} x_{2m}.$$

        If job 3 is executed the constraint forces job 2; if job 2 is not
        executed it forces job 3 out; it does not impose the converse. New
        optimum $20$.

## Code

Full script: [`python/fam07_scheduling.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_scheduling.py);
notebook: [`notebooks/fam07_scheduling.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_scheduling.ipynb).
