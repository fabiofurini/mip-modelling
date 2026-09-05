# Job selection with revenues and fixed-cost machines

**Class:** BIP · **Links:** activation (aggregated), maximisation problem · **Script:** `python/fam07_3_selection.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_3_selection.ipynb)

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

## Constructive heuristic: the primal bound

In a maximisation problem a feasible solution gives a *lower* bound. A job
that does not fit anywhere is **skipped**. The best-fit chooses the
**fullest** machine among those that are enough:

- **Step 1.** Job 1 ($t_1 = 25$): $ra = (105, 110, 100)$; the fullest is
  machine 3: $x[1][3] = 1$, $ra[3] = 75$.
- **Step 2.** Job 2 ($t_2 = 40$): the fullest is still machine 3:
  $x[2][3] = 1$, $ra[3] = 35$.
- **Step 3.** Job 3 ($t_3 = 75$): machine 3 is not enough; between 1 and 2
  the fullest is machine 1: $x[3][1] = 1$, $ra[1] = 30$.

Profit $10 + 15 + 30 - 20 - 15 = 20$: $z(\mathit{MILP}) \ge 20$. Next-fit and
first-fit fill machine 1 first and reach $5$.

## LP relaxation and dual: the dual bound

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

$$20 ~\le~ z(\mathit{MILP}) ~\le~ 34.$$

**What the solver says.** $z(\mathit{LP}) = 34$: the hand-built solution is
optimal for the dual; the relaxation with the bounds drops to $680/21 = 32.38$.
Integer optimum $25$: jobs 1 and 3 on machine 3 ($25 + 75 = 100$, exactly the
availability), profit $40 - 15$; job 2 does not pay because it would require a
second machine ($c_1 = 20 > r_2 = 15$). Heuristic gap: $20\%$.

| $LB$ (best-fit) | $UB$ (hand dual) | $z(\mathit{LP})$ | $z(\mathit{LP}^+)$ | $z(\mathit{MILP})$ | heuristic gap |
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

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
??? question "7.3.2 — A job conditional on another"
    Job 3 can be executed only if job 2 is executed too. Write the constraint
    and find the new optimum.

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
## Code

Full script: [`python/fam07_3_selection.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_3_selection.py);
notebook: [`notebooks/fam07_3_selection.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_3_selection.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/fam07_3_selection.py` (110 lines)"

    ```python
    """Problem 7.3 -- Job selection with revenues and fixed-cost machines.

    The same activation link as problem 7.2, read in a maximisation problem: the
    heuristic gives a lower bound, the dual an upper bound -- the roles swap
    with respect to minimisation problems.
    """
    import gurobipy as gp
    import numpy as np
    import pandas as pd
    from gurobipy import GRB

    from euristiche import best_fit, first_fit, matrice, next_fit
    from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello,
                     registra_bound, risolvi, stampa_soluzione, valuta)
    from stile import CICLO, ROSSO, intestazione, plt, salva_dati, salva_figura

    R = range

    # ---------- 1. MODEL AND INSTANCE ----------
    intestazione("3. Job selection: maximum profit = revenues - fixed costs")
    t3 = [25, 40, 75]
    r3 = [10, 15, 30]
    c3 = [20, 30, 15]
    a3 = [105, 110, 100]
    salva_dati(pd.DataFrame({"job": R(1, 4), "t": t3, "r": r3}), "sched3_lavori")
    salva_dati(pd.DataFrame({"machine": R(1, 4), "c": c3, "a": a3}), "sched3_macchine")


    def modello_3(t, r, c, a):
        n, k = len(t), len(a)
        m = nuovo_modello("selezione")
        x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
        y = m.addVars(k, vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(r[j] * x[j, mm] for j in R(n) for mm in R(k))
                       - gp.quicksum(c[mm] * y[mm] for mm in R(k)), GRB.MAXIMIZE)
        m.addConstrs((x.sum(j, "*") <= 1 for j in R(n)), name="al_piu_una")
        m.addConstrs((gp.quicksum(t[j] * x[j, mm] for j in R(n)) - a[mm] * y[mm] <= 0 for mm in R(k)),
                     name="link")
        return m, x, y


    def duale_3(t, r, c, a):
        """min sum mu_j;  mu_j + t_j pi_m >= r_j;  -a_m pi_m >= -c_m;  mu, pi >= 0."""
        n, k = len(t), len(a)
        d = nuovo_modello("duale_selezione")
        mu = d.addVars(n, name="mu")
        pi = d.addVars(k, name="pi")
        d.setObjective(mu.sum(), GRB.MINIMIZE)
        d.addConstrs((mu[j] + t[j] * pi[mm] >= r[j] for j in R(n) for mm in R(k)), name="rc_x")
        d.addConstrs((-a[mm] * pi[mm] >= -c[mm] for mm in R(k)), name="rc_y")
        return d


    def valore_3(e, r, c):
        return sum(r[j] for (j, mm) in e.x) - sum(c[mm] * y for mm, y in enumerate(e.y))


    m3, x3, y3 = modello_3(t3, r3, c3, a3)

    # ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
    T3 = matrice(t3, 3)
    eur3 = [("next-fit (skips if it does not fit)", next_fit(T3, a3, salta=True)),
            ("first-fit", first_fit(T3, a3, salta=True)),
            ("best-fit (fullest machine)", best_fit(T3, a3, lambda j, mm, ra: ra[mm], "ra", salta=True))]
    print("Constructive heuristics (here they give a LOWER bound: maximisation problem):")
    for nome, e in eur3:
        print(f"  {nome:32s} lb = {valore_3(e, r3, c3):3d}")
    print("Step-by-step run of the best-fit:")
    eur3[2][1].traccia.stampa()
    lb3 = max(valore_3(e, r3, c3) for _, e in eur3)

    # ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
    d3 = duale_3(t3, r3, c3, a3)
    mano = {f"pi[{mm}]": c3[mm] / a3[mm] for mm in R(3)}
    mano.update({f"mu[{j}]": max([0] + [r3[j] - t3[j] * c3[mm] / a3[mm] for mm in R(3)]) for j in R(3)})
    ub3, viol = valuta(d3, mano)
    assert viol <= 1e-9
    print("Hand-built dual solution: pi_m = c_m/a_m; mu_j = max{0, r_j - t_j pi_m} = "
          + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  ub = {frazione(ub3)}")
    zlp3, zlp3r, _ = due_rilassamenti(m3, d3)

    # ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
    z3 = risolvi(m3)
    print("Optimal solution of the MILP:")
    stampa_soluzione(m3, solo_non_nulle=True)
    riga = registra_bound("3 selection", ub3, lb3, zlp3, zlp3r, z3, senso="max")
    salva_dati(pd.DataFrame([riga]), "sched3_bound")

    # ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


    varianti = {}


    def variante(nome, m):
        z = risolvi(m)
        print(f"  {nome:70s} z = {frazione(z)}")
        return z

    # 3a: all jobs must be executed (the assignment constraint is back)
    m, x, y = modello_3(t3, r3, c3, a3)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(3)), name="all")
    varianti["3a"] = variante("3a. All jobs executed (sum_m x_jm = 1)", m)
    # 3b: job 3 only if job 2
    m, x, y = modello_3(t3, r3, c3, a3)
    m.addConstr(x.sum(2, "*") <= x.sum(1, "*"), name="3_only_if_2")
    varianti["3b"] = variante("3b. Job 3 is executed only if job 2 is executed", m)
    salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched3_varianti")

    print("Done.")
    ```

<!-- embedded-script: end -->
