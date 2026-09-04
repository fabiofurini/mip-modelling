# One machine, job classes with setup

**Class:** BIP · **Links:** disaggregated activation, CNF · **Script:** `python/fam07_5_classessetup.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_5_classessetup.ipynb)

!!! abstract "Problem 7.5"
    A company has $n$ jobs executable on a machine with availability
    $a \in \mathbb{Q}_{>0}$ minutes. For each job $j$, $t_j$ is the time and $r_j$
    the revenue if executed. The jobs are partitioned into $q \ge 2$ classes
    $\mathscr{J}_1, \dots, \mathscr{J}_q$. If the machine executes jobs of a class
    $c$, a setup cost $f_c \ge 0$ is paid and a setup time $s_c \ge 0$ is
    consumed. The machine does not execute jobs in parallel. Maximise the
    profit.

**The problem in words.** *We decide* which jobs to execute and which
classes to activate. *The objective*: revenues minus setup costs. *The
constraint*: times of the jobs plus setup times within the availability. A
knapsack with fixed costs per group: the activation link, this time
**disaggregated** from the start.

## Model

| Symbol | Type | Meaning |
|---|---|---|
| $n$, $a$ | | number of jobs, availability |
| $t_j$, $r_j$ | $\in \mathbb{Q}_{>0}$ | time and revenue of job $j$ |
| $q$, $\mathscr{J}_c$ | | number of classes and jobs of class $c$ (partition) |
| $f_c$, $s_c$ | $\in \mathbb{Q}_{\ge 0}$ | setup cost and time of class $c$ |

**Variables.** $n + q$ binary: $x_j = 1$ if job $j$ is executed; $y_c = 1$ if
at least one job of class $c$ is executed.

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} r_j\, x_j - \sum_{c=1}^{q} f_c\, y_c & & \\
\text{subject to} \quad \sum_{j=1}^{n} t_j\, x_j + \sum_{c=1}^{q} s_c\, y_c &\le a, & \\
x_j - y_c &\le 0, & \forall c,\ \forall j \in \mathscr{J}_c, \\
x_j \in \{0, 1\},\quad y_c &\in \{0, 1\}. &
\end{aligned}
$$

- the objective maximises revenues minus setup costs;
- the **availability** constraint ($1$ linear constraint);
- the **link** constraints: if a job of a class is executed, the class is
  activated ($n$ linear constraints, one per job);
- the domain constraints define the variables.

!!! note "Link between the variables: the CNF becomes a constraint"
    **From the constraint.** "If at least one job of class $c$ is executed,
    the class is activated": $(x_j \,\mathtt{OR}\, x_s \,\mathtt{OR}\, \dots) \Rightarrow y_c$,
    contrapositive $\mathtt{NOT}\,y_c \Rightarrow (\mathtt{NOT}\,x_j \,\mathtt{AND}\, \dots)$.
    The expression $\mathtt{NOT}(x_j \,\mathtt{OR}\, \dots) \,\mathtt{OR}\, y_c$ becomes,
    with De Morgan and distributivity, the CNF
    $(\mathtt{NOT}\,x_j \,\mathtt{OR}\, y_c) \,\mathtt{AND}\, (\mathtt{NOT}\,x_s \,\mathtt{OR}\, y_c) \,\mathtt{AND}\, \dots$,
    i.e.\ $1 - x_j + y_c \ge 1$: **exactly** the link constraints
    $x_j \le y_c$. Check in both directions: $x_j = 1$ forces $y_c = 1$;
    $y_c = 0$ forces all the $x_j$ of the class to $0$.

    **From the optimum.** "If no job of the class is executed, the class is
    not activated": not imposed, follows **without loss of optimality**:
    setting $y_c = 0$ stays feasible, frees $s_c$ minutes and does not
    decrease the objective because $f_c \ge 0$. Since $f_c$ can be zero, the
    correct conclusion is "there exists an optimum in which...", not "in
    every optimum".

## The model in gurobipy

```python
m = gp.Model("classes_setup");  m.Params.OutputFlag = 0
x = m.addVars(n, vtype=GRB.BINARY, name="x")
y = m.addVars(q, vtype=GRB.BINARY, name="y")
m.setObjective(gp.quicksum(r[j] * x[j] for j in range(n))
               - gp.quicksum(f[c] * y[c] for c in range(q)), GRB.MAXIMIZE)
m.addConstr(gp.quicksum(t[j] * x[j] for j in range(n))
            + gp.quicksum(s[c] * y[c] for c in range(q)) <= a, name="availability")
m.addConstrs((x[j] - y[c] <= 0 for c in range(q) for j in J[c]), name="link")
m.optimize()
```

## The instance

$n = 7$, $q = 3$: $\mathscr{J}_1 = \{1, 2\}$, $\mathscr{J}_2 = \{3, 4\}$,
$\mathscr{J}_3 = \{5, 6, 7\}$, $a = 50$.

| | $j=1$ | $j=2$ | $j=3$ | $j=4$ | $j=5$ | $j=6$ | $j=7$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| $r_j$ | 10 | 6 | 8 | 6 | 7 | 9 | 5 |
| $t_j$ | 5 | 10 | 8 | 6 | 9 | 5 | 6 |

| | $c=1$ | $c=2$ | $c=3$ |
|---|---:|---:|---:|
| $f_c$ | 10 | 5 | 4 |
| $s_c$ | 10 | 12 | 6 |

## Constructive heuristic: lower bound

Class by class: the first job pays the setup too, if it fits.

- **Step 1.** Class 1: $s_1 + t_1 = 15 \le 50$; $y[1] = x[1] = 1$, $ra = 35$.
- **Step 2.** $t_2 = 10 \le 35$; $x[2] = 1$, $ra = 25$.
- **Step 3.** Class 2: $s_2 + t_3 = 20 \le 25$; $y[2] = x[3] = 1$, $ra = 5$.
- **Step 4.** $t_4 = 6 > 5$: skipped. **Steps 5–7.** Class 3:
  $s_3 + t_j > 5$: skipped.

Profit $10 + 6 + 8 - 10 - 5 = 9$: $z(\mathrm{MILP}) \ge 9$.

## LP relaxation and dual: upper bound

With $\pi \ge 0$ (availability) and $\lambda_j \ge 0$ (link):

$$
\begin{aligned}
\min ~~ a\, \pi & & \\
\text{subject to} \quad t_j\, \pi + \lambda_j &\ge r_j, & \forall j, \\
s_c\, \pi - \sum_{j \in \mathscr{J}_c} \lambda_j &\ge -f_c, & \forall c, \\
\pi \ge 0,\quad \lambda_j &\ge 0. &
\end{aligned}
$$

**A hand-built dual solution.** $\bar\lambda = 0$ and
$\bar\pi = \max_j r_j/t_j = \tfrac{10}{5} = 2$: value $100$. Hence
$9 \le z(\mathrm{MILP}) \le 100$: a coarse bound, as "knapsack" bounds often
are, ignoring setups and costs.

**What the solver says.** $z(\mathrm{LP}) = 425/13 = 32.7$ (with
$\pi = \tfrac{17}{26}$ and some $\lambda_j > 0$); $z(\mathrm{LP}^+) = 329/13$.
Integer optimum $21$: classes 2 and 3, jobs $3, 4, 5, 6$, profit $30 - 9$.
The heuristic stays at $9$ (gap $57\%$): the scanning order matters.

| $\mathrm{lb}$ | $\mathrm{ub}$ (hand dual) | $z(\mathrm{LP})$ | $z(\mathrm{LP}^+)$ | $z(\mathrm{MILP})$ | heuristic gap |
|---:|---:|---:|---:|---:|---:|
| 9 | 100 | $425/13$ | $329/13$ | 21 | $57.1\%$ |

## Additional considerations

- $y_c \le 1$ strengthens the relaxation; $x_j \le 1$ is implied.
- $\sum_{j \in \mathscr{J}_c} x_j \ge y_c$ ($q$ constraints) is not valid but
  preserves the optimum.
- The aggregated form $\sum_{j \in \mathscr{J}_c} x_j \le |\mathscr{J}_c|\, y_c$
  has the same integer set and a weaker relaxation.

## Additional modelling questions

??? question "7.5.1 — A single class"
    At most one class can be activated.

    ??? success "Solution"
        Set packing on the activations: $\sum_c y_c \le 1$. Optimum $17$:
        class 3 alone, all its jobs ($26 \le 50$), $21 - 4$.

??? question "7.5.2 — A class subordinate to another"
    Class 3 can be activated only if class 1 is activated too.

    ??? success "Solution"
        $y_3 \Rightarrow y_1$, i.e.\ $y_3 \le y_1$. Optimum from $21$ to $18$.

## Code

Full script: [`python/fam07_5_classessetup.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_5_classessetup.py);
notebook: [`notebooks/fam07_5_classessetup.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_5_classessetup.ipynb).
