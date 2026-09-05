# Classes with completion bonus and "if and only if" reduction

**Class:** BIP · **Links:** if and only if (two), CNF · **Script:** `python/fam07_6_classesbonus.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_6_classesbonus.ipynb)

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

## Constructive heuristic: the primal bound

Class by class; from the second class on, the first executed job also pays
$u$.

- **Steps 1–2.** Class 1: $x[1] = x[2] = 1$, $ra = 30$; class complete,
  $y[1] = 1$.
- **Step 3.** Class 2: $t_3 + u = 35 > 30$, skipped. **Step 4.**
  $t_4 + u = 25 \le 30$: $x[4] = 1$, $z = 1$, $ra = 5$.
- **Steps 5–6.** Class 3: $t_5, t_6 > 5$, skipped.

Revenue $10 + 5 + 12 + 5 = 32$: $z(\mathit{MILP}) \ge 32$.

## LP relaxation and dual: the dual bound

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
value $150$: $32 \le z(\mathit{MILP}) \le 150$.

**What the solver says.** $z(\mathit{LP}) = 5280/113 = 46.7$. Integer optimum
$42$: class 3 alone, complete, jobs 5 and 6 ($48 \le 50$, $z = 0$), revenue
$10 + 22 + 10$. Heuristic gap $24\%$.

| $LB$ | $UB$ (hand dual) | $z(\mathit{LP})$ | $z(\mathit{MILP})$ | heuristic gap |
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

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
??? question "7.6.2 — Penalty for a class started and not finished"
    Starting a class without completing it costs $w = 3$.

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
## Code

Full script: [`python/fam07_6_classesbonus.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_6_classesbonus.py);
notebook: [`notebooks/fam07_6_classesbonus.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_6_classesbonus.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/fam07_6_classesbonus.py` (146 lines)"

    ```python
    """Problem 7.6 -- Classes with completion bonus and if-and-only-if reduction.

    Two "if and only if"s: each with one direction imposed by the constraint (via
    CNF) and the other by the optimum -- the general scheme to model an iff.
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
    intestazione("6. Bonus if the whole class is executed; reduction u if and only if >= 2 classes")
    r6 = [10, 5, 20, 12, 10, 22]
    t6 = [5, 15, 25, 15, 10, 38]
    J6 = [[0, 1], [2, 3], [4, 5]]
    v6 = [5, 4, 10]
    a6, u6 = 50, 10
    salva_dati(pd.DataFrame({"job": R(1, 7), "r": r6, "t": t6,
                             "class": [c + 1 for j in R(6) for c in R(3) if j in J6[c]]}), "sched6_lavori")
    salva_dati(pd.DataFrame({"class": R(1, 4), "v": v6}), "sched6_classi")


    def coppie(J):
        return [(j, i, c, g) for c in R(len(J)) for g in R(c + 1, len(J)) for j in J[c] for i in J[g]]


    def modello_6(r, t, J, v, a, u):
        n, q = len(r), len(J)
        m = nuovo_modello("classi_premio")
        x = m.addVars(n, vtype=GRB.BINARY, name="x")
        y = m.addVars(q, vtype=GRB.BINARY, name="y")
        z = m.addVar(vtype=GRB.BINARY, name="z")
        m.setObjective(gp.quicksum(r[j] * x[j] for j in R(n)) + gp.quicksum(v[c] * y[c] for c in R(q)),
                       GRB.MAXIMIZE)
        m.addConstrs((x[j] - y[c] >= 0 for c in R(q) for j in J[c]), name="all")
        m.addConstrs((x[j] + x[i] - z <= 1 for (j, i, c, g) in coppie(J)), name="miste")
        m.addConstr(gp.quicksum(t[j] * x[j] for j in R(n)) + u * z <= a, name="disponibilita")
        return m, x, y, z


    def duale_6(r, t, J, v, a, u):
        """min sum lam_ji + a mu;  pi_j + sum lam + t_j mu >= r_j;  -sum_{J_c} pi_j >= v_c;
        -sum lam + u mu >= 0;  pi <= 0, lam >= 0, mu >= 0."""
        n, q = len(r), len(J)
        cp = coppie(J)
        d = nuovo_modello("duale_classi_premio")
        pi = d.addVars(n, lb=-GRB.INFINITY, ub=0.0, name="pi")
        lam = d.addVars([(j, i) for (j, i, _, _) in cp], name="lam")
        mu = d.addVar(name="mu")
        d.setObjective(lam.sum() + a * mu, GRB.MINIMIZE)
        for j in R(n):
            d.addConstr(pi[j] + gp.quicksum(lam[jj, ii] for (jj, ii, _, _) in cp if jj == j or ii == j)
                        + t[j] * mu >= r[j], name=f"rc_x[{j}]")
        d.addConstrs((-gp.quicksum(pi[j] for j in J[c]) >= v[c] for c in R(q)), name="rc_y")
        d.addConstr(-lam.sum() + u * mu >= 0, name="rc_z")
        return d


    def euristica_6(r, t, J, v, a, u):
        """Class by class: from the second class on, the first job also pays the reduction u."""
        n, q = len(r), len(J)
        x, y, z, ra, passi = [0] * n, [0] * q, 0, a, []
        for c in R(q):
            cnt = 0
            for j in J[c]:
                if c == 0 or z == 1:
                    if t[j] <= ra:
                        x[j], ra, cnt = 1, ra - t[j], cnt + 1
                        passi.append(f"Class {c + 1}: t[{j + 1}] = {t[j]} <= ra; x[{j + 1}] = 1, ra = {ra}.")
                    else:
                        passi.append(f"Class {c + 1}: t[{j + 1}] = {t[j]} > ra = {ra}; job {j + 1} is skipped.")
                else:
                    if t[j] + u <= ra:
                        x[j], z, ra, cnt = 1, 1, ra - t[j] - u, cnt + 1
                        passi.append(f"Class {c + 1}, reduction not applied yet: t[{j + 1}] + u = {t[j] + u} <= ra; "
                                     f"x[{j + 1}] = 1, z = 1, ra = {ra}.")
                    else:
                        passi.append(f"Class {c + 1}, reduction not applied yet: t[{j + 1}] + u = {t[j] + u} > ra = {ra}; "
                                     f"job {j + 1} is skipped.")
            if cnt == len(J[c]):
                y[c] = 1
                passi.append(f"All the jobs of class {c + 1} are executed: y[{c + 1}] = 1 (bonus v = {v[c]}).")
        return x, y, z, passi


    m6, x6, y6, z6 = modello_6(r6, t6, J6, v6, a6, u6)

    # ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
    xe, ye, ze, passi = euristica_6(r6, t6, J6, v6, a6, u6)
    print("Class-by-class heuristic:")
    for i, s in enumerate(passi, 1):
        print(f"  Step {i}. {s}")
    lb6 = sum(r6[j] * xe[j] for j in R(6)) + sum(v6[c] * ye[c] for c in R(3))
    print(f"  lb = {lb6}  (x = {xe}, y = {ye}, z = {ze})")

    # ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
    d6 = duale_6(r6, t6, J6, v6, a6, u6)
    pi_mano = {f"pi[{J6[c][0]}]": -v6[c] for c in R(3)}      # the first job of every class carries the bonus
    mu_mano = max((r6[j] - pi_mano.get(f"pi[{j}]", 0)) / t6[j] for j in R(6))
    mano = dict(pi_mano, mu=mu_mano)
    ub6, viol = valuta(d6, mano)
    assert viol <= 1e-9
    print(f"Hand-built dual solution: pi_1 = -5, pi_3 = -4, pi_5 = -10, lam = 0, "
          f"mu = max_j (r_j - pi_j)/t_j = {frazione(mu_mano)}  ->  ub = {frazione(ub6)}")
    zlp6, zlp6r, _ = due_rilassamenti(m6, d6)

    # ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
    z6v = risolvi(m6)
    print("Optimal solution of the MILP:")
    stampa_soluzione(m6, solo_non_nulle=True)
    riga = registra_bound("6 classes bonus", ub6, lb6, zlp6, zlp6r, z6v, senso="max")
    salva_dati(pd.DataFrame([riga]), "sched6_bound")

    # ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


    varianti = {}


    def variante(nome, m):
        z = risolvi(m)
        print(f"  {nome:70s} z = {frazione(z)}")
        return z

    # 6a: at least one job per class
    m, x, y, z = modello_6(r6, t6, J6, v6, a6, u6)
    m.addConstrs((gp.quicksum(x[j] for j in J6[c]) >= 1 for c in R(3)), name="at_least_one")
    varianti["6a"] = variante("6a. At least one job per class (hence z = 1)", m)
    # 6b: penalty w per class started and not completed
    w6 = 3
    m, x, y, z = modello_6(r6, t6, J6, v6, a6, u6)
    st = m.addVars(3, vtype=GRB.BINARY, name="s")
    m.addConstrs((st[c] >= x[j] for c in R(3) for j in J6[c]), name="started")
    m.update()
    m.setObjective(m.getObjective() - w6 * gp.quicksum(st[c] - y[c] for c in R(3)), GRB.MAXIMIZE)
    varianti["6b"] = variante("6b. Penalty 3 per class started and not completed (s_c >= x_j)", m)
    salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched6_varianti")

    print("Done.")
    ```

<!-- embedded-script: end -->
