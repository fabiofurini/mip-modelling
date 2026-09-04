# Minimum-cost assignment with availability

**Class:** BIP · **Links:** none — a single family of variables · **Script:** `python/fam07_1_assignment.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_1_assignment.ipynb)

!!! abstract "Problem 7.1"
    A company has to process $n \in \mathbb{Z}_{\ge 1}$ jobs on $k \in \mathbb{Z}_{\ge 1}$
    machines. For each job $j \in \{1, 2, \dots, n\}$ and each machine
    $m \in \{1, 2, \dots, k\}$, the value $t_{jm} \in \mathbb{Q}_{>0}$ is the processing time
    in minutes and the value $c_{jm} \in \mathbb{Q}_{>0}$ is the cost in euros of
    processing job $j$ on machine $m$. For each machine
    $m \in \{1, 2, \dots, k\}$, the value $a_m \in \mathbb{Q}_{>0}$ is the available
    processing time in minutes. Each machine processes one job at a time.
    The company wants to assign all jobs to the machines at minimum cost.

**The problem in words.** *We decide* on which machine each job is processed.
*The objective*: minimum total cost. *The constraints*: every job is processed
by exactly one machine; the total time of the jobs assigned to a machine does
not exceed its availability. It is the **generalised assignment** problem: an
assignment with a knapsack constraint per machine.

## Model

**Data (input of the model).**

| Symbol | Type | Meaning |
|---|---|---|
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of jobs, $j \in \{1, 2, \dots, n\}$ |
| $k$ | $\in \mathbb{Z}_{\ge 1}$ | number of machines, $m \in \{1, 2, \dots, k\}$ |
| $t_{jm}$ | $\in \mathbb{Q}_{>0}$ | processing time of job $j$ on machine $m$ |
| $c_{jm}$ | $\in \mathbb{Q}_{>0}$ | cost of processing job $j$ on machine $m$ |
| $a_m$ | $\in \mathbb{Q}_{>0}$ | availability of machine $m$ |

**Decision variables.** We introduce the following $n\,k$ binary variables:

$$
x_{jm} = \begin{cases} 1 & \text{if job } j \text{ is processed by machine } m,\\ 0 & \text{otherwise,}\end{cases}
\qquad \forall j \in \{1, 2, \dots, n\},\ \forall m \in \{1, 2, \dots, k\}.
$$

Using these variables, a BIP model for the problem reads as follows:

$$
\begin{aligned}
\min ~~ \sum_{j=1}^{n} \sum_{m=1}^{k} c_{jm}\, x_{jm} & & \\
\text{subject to} \quad \sum_{m=1}^{k} x_{jm} &= 1, & \forall j \in \{1, 2, \dots, n\}, \\
\sum_{j=1}^{n} t_{jm}\, x_{jm} &\le a_m, & \forall m \in \{1, 2, \dots, k\}, \\
x_{jm} &\in \{0, 1\}, & \forall j \in \{1, 2, \dots, n\},\ \forall m \in \{1, 2, \dots, k\}.
\end{aligned}
$$

Description of the objective function and constraints:

- the linear objective function minimises the total processing cost, the sum
  of the costs of the chosen assignments;
- the **assignment** constraints ensure that each job is assigned to exactly
  one machine, so that all jobs are processed ($n$ linear constraints);
- the **availability** constraints guarantee that the total processing time
  of the jobs assigned to each machine does not exceed its availability ($k$
  linear constraints);
- the domain constraints define the variables of the model.

The model has a single family of variables: there are no links to prove. The
availability constraints are of the "capacity/resource" kind: two quantities
of the same nature (minutes required and minutes available) compared, no
logical implication. The model can be solved to optimality, for example, by the
branch-and-bound algorithm.

## The model in gurobipy

Every family of constraints is one `addConstrs` named after its label.

```python
m = gp.Model("assignment");  m.Params.OutputFlag = 0
x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
m.setObjective(gp.quicksum(c[j][mm] * x[j, mm] for j in range(n)
                           for mm in range(k)), GRB.MINIMIZE)
m.addConstrs((x.sum(j, "*") == 1 for j in range(n)), name="assign")
m.addConstrs((gp.quicksum(t[j][mm] * x[j, mm] for j in range(n)) <= a[mm]
              for mm in range(k)), name="availability")
m.optimize()
```

## The instance

$n = 3$ jobs, $k = 3$ machines:

| $t_{jm}$ | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $j=1$ | 2 | 1 | 3 |
| $j=2$ | 3 | 4 | 2 |
| $j=3$ | 4 | 5 | 3 |

| $c_{jm}$ | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $j=1$ | 5 | 10 | 2 |
| $j=2$ | 5 | 4 | 6 |
| $j=3$ | 5 | 4 | 6 |

| | $m=1$ | $m=2$ | $m=3$ |
|---|---:|---:|---:|
| $a_m$ | 5 | 6 | 7 |

The model for the instance:

$$
\begin{array}{r r@{\;}r@{\;}r@{\;}r@{\;}r@{\;}r@{\;}r@{\;}r@{\;}r c r}
\min & 5x_{11} & +10x_{12} & +2x_{13} & +5x_{21} & +4x_{22} & +6x_{23} & +5x_{31} & +4x_{32} & +6x_{33} & & \\
\text{subject to} & x_{11} & +x_{12} & +x_{13} & & & & & & & = & 1,\\
 & & & & x_{21} & +x_{22} & +x_{23} & & & & = & 1,\\
 & & & & & & & x_{31} & +x_{32} & +x_{33} & = & 1,\\
 & 2x_{11} & & & +3x_{21} & & & +4x_{31} & & & \le & 5,\\
 & & x_{12} & & & +4x_{22} & & & +5x_{32} & & \le & 6,\\
 & & & 3x_{13} & & & +2x_{23} & & & +3x_{33} & \le & 7,\\
 & x_{11}, & x_{12}, & x_{13}, & x_{21}, & x_{22}, & x_{23}, & x_{31}, & x_{32}, & x_{33} & \in & \{0,1\}.
\end{array}
$$

## Constructive heuristic: upper bound

Three heuristics inspired by bin packing. **Next-fit**: one machine is loaded
at a time and the next one is opened when a job no longer fits. **First-fit**:
each job goes on the first machine with enough residual availability.
**Best-fit**: among the machines with enough availability, the one with
minimum cost is chosen.

```text
BestFit(n, k, t, c, a):
  x[j][m] <- 0 for every j, m;   ra[m] <- a[m] for every m      # residual availabilities
  for j = 1..n:
      sm <- 0;  mc <- +inf                                       # selected machine, minimum cost
      for m = 1..k:
          if t[j][m] <= ra[m] and c[j][m] < mc:  sm <- m;  mc <- c[j][m]
      if sm = 0:  return "no solution found"
      x[j][sm] <- 1;  ra[sm] <- ra[sm] - t[j][sm]
  return x
```

Run on the instance (output of the script):

- **Step 1.** Job 1: $ra = (5, 6, 7)$; every machine is enough; costs
  $5, 10, 2$: the minimum is machine 3, hence $x[1][3] = 1$ and $ra[3] = 7 - 3 = 4$.
- **Step 2.** Job 2: $ra = (5, 6, 4)$; costs $5, 4, 6$: the minimum is
  machine 2, hence $x[2][2] = 1$ and $ra[2] = 6 - 4 = 2$.
- **Step 3.** Job 3: $ra = (5, 2, 4)$; machine 2 is not enough ($5 > 2$);
  among the others, costs $5$ and $6$: the minimum is machine 1, hence
  $x[3][1] = 1$ and $ra[1] = 5 - 4 = 1$.

Solution $\bar x_{13} = \bar x_{22} = \bar x_{31} = 1$, value $2 + 4 + 5 = 11$:
$\mathrm{ub} = 11$, i.e.\ $z(\mathrm{MILP}) \le 11$. Next-fit and first-fit both
find $x_{11} = x_{21} = x_{32} = 1$, of value $14$.

## LP relaxation and dual: lower bound

The LP relaxation replaces $x_{jm} \in \{0,1\}$ with $x_{jm} \ge 0$ (the
constraint $x_{jm} \le 1$ is implied by the assignment constraints). With a
free dual variable $\mu_j$ for each assignment constraint and a non-positive
$\pi_m$ for each availability constraint ($\le$ in a minimisation), the dual is:

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} \mu_j + \sum_{m=1}^{k} a_m\, \pi_m & & \\
\text{subject to} \quad \mu_j + t_{jm}\, \pi_m &\le c_{jm}, & \forall j \in \{1, 2, \dots, n\},\ \forall m \in \{1, 2, \dots, k\}, \\
\mu_j &\gtreqless 0, & \forall j \in \{1, 2, \dots, n\}, \\
\pi_m &\le 0, & \forall m \in \{1, 2, \dots, k\}.
\end{aligned}
$$

**A hand-built dual solution.** With $\bar\pi_m = 0$, the constraints become
$\mu_j \le c_{jm}$ for every $m$: the largest feasible value is

$$
\bar\mu_1 = \min\{5, 10, 2\} = 2,\qquad \bar\mu_2 = \min\{5, 4, 6\} = 4,\qquad \bar\mu_3 = \min\{5, 4, 6\} = 4,
$$

with value $10$. By weak duality

$$
10 ~\le~ z(\mathrm{LP}) ~\le~ z(\mathrm{MILP}) ~\le~ 11.
$$

The recipe has a meaning: "every job costs at least its minimum cost" is a
lower bound anyone would write down; the dual formalises it and says how to
improve it, with $\pi_m < 0$ where the availability is tight.

**What the solver says.** $z(\mathrm{LP}) = 53/5 = 10.6$ (equal to the optimum
of the dual: strong duality), with duals $\tilde\mu = (2,\ 4.8,\ 5)$ and
$\tilde\pi = (0,\ -0.2,\ 0)$: machine 2 is the tight resource. The integer
optimum is $z(\mathrm{MILP}) = 11$ with $\tilde x_{13} = \tilde x_{22} = \tilde x_{31} = 1$:
the best-fit heuristic had found the optimum, but only the solver certifies it
— the dual bound stopped at $10$ (and since the costs are integer,
$\lceil 53/5 \rceil = 11$ closes the gap).

| $\mathrm{ub}$ (best-fit) | $\mathrm{lb}$ (hand dual) | $z(\mathrm{LP})$ | $z(\mathrm{MILP})$ | heuristic gap |
|---:|---:|---:|---:|---:|
| 11 | 10 | $53/5$ | 11 | $0.0\%$ |

![Optimal solution of the instance](img/cap07_gap_ottimo.png)

## Additional considerations

- $x_{jm} \le 1$ ($n\,k$ inequalities) are valid but implied by the
  assignment constraints: they do not strengthen the relaxation (indeed
  $z(\mathrm{LP}) = z(\mathrm{LP}^+)$).
- If a job $j$ does not fit on a machine $m$ ($t_{jm} > a_m$), $x_{jm}$ can be
  fixed to zero before solving: the model is smaller and the relaxation does
  not get worse.

## Additional modelling questions

??? question "7.1.1 — Jobs 1 and 3 on the same machine"
    Jobs 1 and 3 use the same tool and must be processed by the same machine.
    How does the model change? What is the new optimum for the instance?

    ??? success "Solution"
        For every machine $m$, $x_{1m} = 1$ if and only if $x_{3m} = 1$:

        $$x_{1m} = x_{3m}, \qquad \forall m \in \{1, 2, \dots, k\}$$

        ($k$ linear constraints). Both directions are imposed by the
        constraint; the assignment constraints guarantee that the common
        machine is unique. New optimum $12$: the pair sits on machine 3
        ($3 + 3 \le 7$, cost $2 + 6$) and job 2 on machine 2 ($4$).

??? question "7.1.2 — Fixed cost per used machine"
    Every machine that processes at least one job costs an extra $g_m = 3$
    euros to switch on. Model the fixed cost and find the new optimum. Which
    link comes into play?

    ??? success "Solution"
        The family of **activations** $y_m \in \{0,1\}$ is needed, the
        objective becomes $\sum_j \sum_m c_{jm} x_{jm} + \sum_m g_m y_m$ and
        the link "if a job is assigned to $m$ then $m$ is used" is imposed by

        $$x_{jm} \le y_m, \qquad \forall j,\ \forall m$$

        ($n\,k$ constraints). The opposite direction — a machine with no jobs
        is not switched on — follows from the objective in every optimum
        because $g_m > 0$. It is the activation link, studied in full in
        [problem 7.2](scheduling-2.md). New optimum $18$, with two machines
        only: jobs 1 and 3 on machine 3 and job 2 on machine 2, plus
        $2 \cdot 3$ for switching on; the three-machine solution would cost
        $11 + 9 = 20$.

## Code

The complete script of the family — data, seven models, heuristics, duals,
solutions and figures — is
[`python/fam07_1_assignment.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_1_assignment.py)
(reproducible with `python3 python/fam07_1_assignment.py` from the `python/`
folder). The same code is also available as a notebook —
[`notebooks/fam07_1_assignment.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_1_assignment.ipynb)
— which opens in Colab from the badge at the top of the page.
