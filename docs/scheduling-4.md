# Parallel jobs: the processing time as a maximum

**Class:** MILP · **Links:** maximum variable · **Script:** `python/fam07_4_parallel.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_4_parallel.ipynb)

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
\min ~~ \sum_{m=1}^{k} y_m & &\\
\text{subject to} \quad \sum_{m=1}^{k} x_{jm} &= 1, & \forall j,\\
\sum_{j=1}^{n} x_{jm} &\le p_m, & \forall m,\\
-t_{jm}\, x_{jm} + y_m &\ge 0, & \forall j,\ \forall m,\\
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

## Constructive heuristic: the primal bound

Next-fit on the cardinalities: machine 1 is filled up to $p_1$ jobs, then
machine 2, and so on.

- **Step 1.** Job 1 on machine 1: $y[1] = 6$.
- **Step 2.** Machine 1 is full ($p_1 = 1$): job 2 on machine 2, $y[2] = 10$.
- **Step 3.** Job 3 on machine 2: $y[2] = \max(10, 13) = 13$.

$\bar y = (6, 13, 0)$, value $19$: $z(\mathit{MILP}) \le 19$.

## LP relaxation and dual: the dual bound

With $\mu_j$ free (assignment), $\pi_m \le 0$ (cardinality) and
$\lambda_{jm} \ge 0$ (maximum):

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} \mu_j + \sum_{m=1}^{k} p_m\, \pi_m & &\\
\text{subject to} \quad \mu_j + \pi_m - t_{jm}\, \lambda_{jm} &\le 0, & \forall j,\ \forall m,\\
\sum_{j=1}^{n} \lambda_{jm} &\le 1, & \forall m,\\
\mu_j \gtreqless 0,\quad \pi_m \le 0,\quad \lambda_{jm} &\ge 0. &
\end{aligned}
$$

The second constraint is the reduced cost of $y_m$: the coefficient $1$ in
the primal objective limits the sum of the $\lambda_{jm}$.

**A hand-built dual solution.** $\bar\lambda_{jm} = 1/3$, $\bar\pi_m = 0$,
$\bar\mu_j = \min_m t_{jm}/3$: $1, \tfrac{2}{3}, \tfrac{10}{3}$, value $5$:
$5 \le z(\mathit{MILP}) \le 19$.

**What the solver says.** $z(\mathit{LP}) = 520/49 = 10.61$. Integer optimum
$15$: job 1 on machine 2, jobs 2 and 3 on machine 3, $\tilde y = (0, 5, 10)$.
The uniform split of the $\lambda$ is the first that comes to mind, not the
best.

| $UB$ | $LB$ (hand dual) | $z(\mathit{LP})$ | $z(\mathit{MILP})$ | heuristic gap |
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

??? question "7.4.2 — Fixed cost if the machine works"
    Switching a machine on costs $g_m = 4$ euros, one minute costs $1$ euro.
    Which link is needed and what is the smallest big-M?

## The sandwich on variant 4a

The min-max removes the cost from the $y_m$ and adds $\nu_m \ge 0$ with
$\sum_m \nu_m \le 1$. It pays to price the longest job: the $\nu$ maximising
$\min_m t_{jm}\nu_m$ makes that product constant, and the bound is the harmonic
mean of its times. The recipe is **optimal** for the relaxation.

<!-- tabella-variante: fam07_4a_bound -->

|  | value | what it is |
|---|---:|---|
| $\mathit{UB}$ | $13$ | heuristic solution |
| $\mathit{LB}$ | $\frac{260}{59}$ | dual certificate built by hand |
| $z(\mathit{LP})$ | $\frac{260}{59}$ | relaxation without the bounds |
| $z(\mathit{LP}^+)$ | $\frac{260}{59}$ | relaxation with the bounds |
| $z(\mathit{MILP})$ | $10$ | optimum of the MILP |

<!-- tabella-variante: fine -->

## Code

Full script: [`python/fam07_4_parallel.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_4_parallel.py);
notebook: [`notebooks/fam07_4_parallel.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_4_parallel.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/fam07_4_parallel.py` (203 lines)"

    ```python
    """Problem 7.4 -- Parallel jobs: the processing time as a maximum.

    The maximum-variable pattern in three steps: imposed by the constraint (one
    side), imposed by the optimum (the other side), synthesis that characterises
    y_m as the maximum of the times of the assigned jobs.
    """
    import gurobipy as gp
    import numpy as np
    import pandas as pd
    from gurobipy import GRB

    from euristiche import best_fit, first_fit, matrice, next_fit
    from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                     nuovo_modello, registra_bound, rilassamenti, risolvi,
                     stampa_soluzione, valuta)
    from stile import CICLO, ROSSO, intestazione, plt, salva_dati, salva_figura
    from esteso import salva_modello

    R = range

    # ---------- 1. MODEL AND INSTANCE ----------
    intestazione("4. Parallel jobs: y_m = maximum of the times of the assigned jobs")
    t4 = [[6, 5, 3], [5, 10, 2], [20, 13, 10]]
    p4 = [1, 2, 2]
    salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t4[j][m]}
                             for j in R(3) for m in R(3)]), "fam07_4_lavori")
    salva_dati(pd.DataFrame({"machine": R(1, 4), "p": p4}), "fam07_4_macchine")


    def modello_4(t, p):
        n, k = len(t), len(p)
        m = nuovo_modello("parallelo")
        x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
        y = m.addVars(k, name="y")
        m.setObjective(y.sum(), GRB.MINIMIZE)
        m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
        m.addConstrs((x.sum("*", mm) <= p[mm] for mm in R(k)), name="cardinalita")
        m.addConstrs((-t[j][mm] * x[j, mm] + y[mm] >= 0 for j in R(n) for mm in R(k)), name="massimo")
        return m, x, y


    def duale_4(t, p):
        """max sum mu_j + sum p_m pi_m;  mu_j + pi_m - t_jm lam_jm <= 0;  sum_j lam_jm <= 1."""
        n, k = len(t), len(p)
        d = nuovo_modello("duale_parallelo")
        mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
        pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
        lam = d.addVars(n, k, name="lam")
        d.setObjective(mu.sum() + gp.quicksum(p[mm] * pi[mm] for mm in R(k)), GRB.MAXIMIZE)
        d.addConstrs((mu[j] + pi[mm] - t[j][mm] * lam[j, mm] <= 0 for j in R(n) for mm in R(k)), name="rc_x")
        d.addConstrs((lam.sum("*", mm) <= 1 for mm in R(k)), name="rc_y")
        return d


    def euristica_4(t, p):
        """Next-fit on the number of jobs: a machine is filled up to p_m jobs, then the next one."""
        n, k = len(t), len(p)
        x, y, cm, cnt, passi = {}, [0.0] * k, 0, 0, []
        for j in R(n):
            if cnt == p[cm]:
                if cm == k - 1:
                    return None
                cm, cnt = cm + 1, 0
            x[(j, cm)] = 1
            cnt += 1
            y[cm] = max(y[cm], t[j][cm])
            passi.append(f"Job {j + 1} on machine {cm + 1} (assigned jobs {cnt} <= p = {p[cm]}): "
                         f"y[{cm + 1}] = max(y[{cm + 1}], t[{j + 1}][{cm + 1}] = {t[j][cm]}) = {y[cm]:g}.")
        return x, y, passi


    m4, x4, y4 = modello_4(t4, p4)
    salva_modello(m4, "fam07_4_primale")

    # ---------- 2. THE LP RELAXATION ----------
    zlp4, zlp4r, _ = rilassamenti(m4)

    # ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
    d4 = duale_4(t4, p4)
    salva_modello(d4, "fam07_4_duale")
    mano = {f"lam[{j},{mm}]": 1 / 3 for j in R(3) for mm in R(3)}
    mano.update({f"mu[{j}]": min(t4[j][mm] / 3 for mm in R(3)) for j in R(3)})
    lb4, viol = valuta(d4, mano)
    assert viol <= 1e-9
    print("Hand-built dual solution: lam_jm = 1/3, pi = 0, mu_j = min_m t_jm/3 = "
          + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  lb = {frazione(lb4)}")
    dualita_forte(d4, zlp4)

    # ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
    xe, ye, passi = euristica_4(t4, p4)
    print("Next-fit heuristic on the cardinalities:")
    for i, s in enumerate(passi, 1):
        print(f"  Step {i}. {s}")
    ub4 = sum(ye)
    print(f"  ub = {frazione(ub4)}")

    # ---------- 5. OPTIMAL SOLUTION OF THE MILP ----------
    z4 = risolvi(m4)
    print("Optimal solution of the MILP:")
    stampa_soluzione(m4, solo_non_nulle=True)
    riga = registra_bound("4 parallel", ub4, lb4, zlp4, zlp4r, z4)
    salva_dati(pd.DataFrame([riga]), "fam07_4_bound")

    # ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------


    varianti = {}


    def variante(nome, m):
        z = risolvi(m)
        print(f"  {nome:70s} z = {frazione(z)}")
        return z

    # 4a: minimise the makespan (maximum of the machine times)
    m, x, y = modello_4(t4, p4)
    w = m.addVar(name="w")
    m.addConstrs((w >= y[mm] for mm in R(3)), name="makespan")
    m.setObjective(w, GRB.MINIMIZE)
    varianti["4a"] = variante("4a. Minimise the maximum of the times (min-max: w >= y_m)", m)
    # 4b: fixed cost if a machine works (y_m > 0 => v_m = 1, big-M = max_j t_jm)
    g4 = [4, 4, 4]
    m, x, y = modello_4(t4, p4)
    vv = m.addVars(3, vtype=GRB.BINARY, name="v")
    m.addConstrs((y[mm] <= max(t4[j][mm] for j in R(3)) * vv[mm] for mm in R(3)), name="activate")
    m.setObjective(y.sum() + gp.quicksum(g4[mm] * vv[mm] for mm in R(3)), GRB.MINIMIZE)
    varianti["4b"] = variante("4b. Fixed cost 4 if the machine works (y_m <= M_m v_m)", m)
    salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "fam07_4_varianti")

    # ---------- 7. THE SANDWICH ON THE VARIANT 4a ----------
    intestazione("4a. The sandwich on the variant: minimising the maximum of the times")


    def modello_4a(t, p):
        mm_, xx, yy = modello_4(t, p)
        ww = mm_.addVar(name="w")
        mm_.addConstrs((ww - yy[mz] >= 0 for mz in R(len(p))), name="minmax")
        mm_.setObjective(ww, GRB.MINIMIZE)
        return mm_, xx, yy, ww


    def duale_4a(t, p):
        """Two things change with respect to the dual of 7.4: y_m no longer has a
        cost, and nu_m >= 0 arrives for the constraint w - y_m >= 0. The columns
        become  x_jm: mu_j + pi_m - t_jm lam_jm <= 0;  y_m: sum_j lam_jm - nu_m <= 0;
        w: sum_m nu_m <= 1."""
        nn, kk = len(t), len(p)
        d = nuovo_modello("duale_parallelo_4a")
        mu = d.addVars(nn, lb=-GRB.INFINITY, name="mu")
        pi = d.addVars(kk, lb=-GRB.INFINITY, ub=0.0, name="pi")
        lam = d.addVars(nn, kk, name="lam")
        nu = d.addVars(kk, name="nu")
        d.setObjective(mu.sum() + gp.quicksum(p[mz] * pi[mz] for mz in R(kk)), GRB.MAXIMIZE)
        d.addConstrs((mu[j] + pi[mz] - t[j][mz] * lam[j, mz] <= 0
                      for j in R(nn) for mz in R(kk)), name="rc_x")
        d.addConstrs((lam.sum("*", mz) - nu[mz] <= 0 for mz in R(kk)), name="rc_y")
        d.addConstr(nu.sum() <= 1, name="rc_w")
        return d


    m4a, x4a, y4a, w4a = modello_4a(t4, p4)
    salva_modello(m4a, "fam07_4a_primale")

    # -- feasible heuristic: the same assignment, read with the new objective --
    print("Constructive heuristic: the assignment of the base problem is feasible here too;")
    print("only its evaluation changes, because now the maximum counts and not the sum.")
    assegnazione = sorted(xe)
    carichi = [max([t4[j][mz] for (j, q) in assegnazione if q == mz] + [0]) for mz in R(3)]
    ub4a = max(carichi)
    sol_4a = ({f"x[{j},{mz}]": 1 for (j, mz) in assegnazione}
              | {f"y[{mz}]": carichi[mz] for mz in R(3)} | {"w": ub4a})
    assert ammissibile(m4a, sol_4a), "the heuristic solution of the variant must be feasible"
    print(f"  times per machine {carichi}  ->  ub = {frazione(ub4a)}")

    # -- dual certificate: all the weight on the longest job --
    d4a = duale_4a(t4, p4)
    salva_modello(d4a, "fam07_4a_duale")
    # with a single job priced, lam_jm = nu_m and mu_j <= min_m t_jm nu_m: the nu that
    # maximises that minimum makes t_jm nu_m constant, that is nu_m proportional to 1/t_jm
    lungo = max(R(3), key=lambda j: min(t4[j]))
    somma_inversi = sum(1 / t4[lungo][mz] for mz in R(3))
    nu_b = {mz: (1 / t4[lungo][mz]) / somma_inversi for mz in R(3)}
    mano_4a = {f"nu[{mz}]": nu_b[mz] for mz in R(3)}
    mano_4a.update({f"lam[{lungo},{mz}]": nu_b[mz] for mz in R(3)})
    mano_4a[f"mu[{lungo}]"] = 1 / somma_inversi
    lb4a, viol_4a = valuta(d4a, mano_4a)
    assert viol_4a <= 1e-9, viol_4a
    print(f"Dual solution by hand: only job {lungo + 1} is priced, the longest one on every")
    print("  machine. With lam_jm = nu_m the column of w gives sum_m nu_m <= 1, and")
    print("  the nu maximising min_m t_jm nu_m makes that product constant: nu_m is")
    print("  proportional to 1/t_jm. The bound is the harmonic mean of the times of that job,")
    print(f"  1 / sum_m (1/t_jm) = {frazione(lb4a)}.")
    zlp4a, zlp4ar, _ = due_rilassamenti(m4a, d4a)
    z4a = risolvi(m4a)
    riga_4a = registra_bound("4a min-max of the times", ub4a, lb4a, zlp4a, zlp4ar, z4a)
    salva_dati(pd.DataFrame([riga_4a]), "fam07_4a_bound")
    assert lb4a <= zlp4a <= z4a <= ub4a + 1e-9


    print("Fine.")


    print("Done.")
    ```

<!-- embedded-script: end -->
