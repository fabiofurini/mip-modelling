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

## Constructive heuristic: the primal bound

Class by class: the first job pays the setup too, if it fits.

- **Step 1.** Class 1: $s_1 + t_1 = 15 \le 50$; $y[1] = x[1] = 1$, $ra = 35$.
- **Step 2.** $t_2 = 10 \le 35$; $x[2] = 1$, $ra = 25$.
- **Step 3.** Class 2: $s_2 + t_3 = 20 \le 25$; $y[2] = x[3] = 1$, $ra = 5$.
- **Step 4.** $t_4 = 6 > 5$: skipped. **Steps 5–7.** Class 3:
  $s_3 + t_j > 5$: skipped.

Profit $10 + 6 + 8 - 10 - 5 = 9$: $z(\mathit{MILP}) \ge 9$.

## LP relaxation and dual: the dual bound

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
$9 \le z(\mathit{MILP}) \le 100$: a coarse bound, as "knapsack" bounds often
are, ignoring setups and costs.

**What the solver says.** $z(\mathit{LP}) = 425/13 = 32.7$ (with
$\pi = \tfrac{17}{26}$ and some $\lambda_j > 0$); $z(\mathit{LP}^+) = 329/13$.
Integer optimum $21$: classes 2 and 3, jobs $3, 4, 5, 6$, profit $30 - 9$.
The heuristic stays at $9$ (gap $57\%$): the scanning order matters.

| $LB$ | $UB$ (hand dual) | $z(\mathit{LP})$ | $z(\mathit{LP}^+)$ | $z(\mathit{MILP})$ | heuristic gap |
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

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
??? question "7.5.2 — A class subordinate to another"
    Class 3 can be activated only if class 1 is activated too.

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
## Code

Full script: [`python/fam07_5_classessetup.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam07_5_classessetup.py);
notebook: [`notebooks/fam07_5_classessetup.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam07_5_classessetup.ipynb).

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/fam07_5_classessetup.py` (127 lines)"

    ```python
    """Problem 7.5 -- One machine, job classes with setup.

    The disaggregated activation link derived step by step from the CNF of a
    Boolean implication: (OR of jobs) => class activated.
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
    intestazione("5. Job classes with setup cost and time: y_c activates the class")
    r5 = [10, 6, 8, 6, 7, 9, 5]
    t5 = [5, 10, 8, 6, 9, 5, 6]
    J5 = [[0, 1], [2, 3], [4, 5, 6]]       # classes (0-based)
    f5 = [10, 5, 4]
    s5 = [10, 12, 6]
    a5 = 50
    salva_dati(pd.DataFrame({"job": R(1, 8), "r": r5, "t": t5,
                             "class": [c + 1 for j in R(7) for c in R(3) if j in J5[c]]}), "sched5_lavori")
    salva_dati(pd.DataFrame({"class": R(1, 4), "f": f5, "s": s5}), "sched5_classi")


    def modello_5(r, t, J, f, s, a):
        n, q = len(r), len(J)
        m = nuovo_modello("classi_setup")
        x = m.addVars(n, vtype=GRB.BINARY, name="x")
        y = m.addVars(q, vtype=GRB.BINARY, name="y")
        m.setObjective(gp.quicksum(r[j] * x[j] for j in R(n)) - gp.quicksum(f[c] * y[c] for c in R(q)),
                       GRB.MAXIMIZE)
        m.addConstr(gp.quicksum(t[j] * x[j] for j in R(n)) + gp.quicksum(s[c] * y[c] for c in R(q)) <= a,
                    name="disponibilita")
        m.addConstrs((x[j] - y[c] <= 0 for c in R(q) for j in J[c]), name="link")
        return m, x, y


    def duale_5(r, t, J, f, s, a):
        """min a pi;  t_j pi + lam_j >= r_j;  s_c pi - sum_{j in J_c} lam_j >= -f_c;  pi, lam >= 0."""
        n, q = len(r), len(J)
        d = nuovo_modello("duale_classi_setup")
        pi = d.addVar(name="pi")
        lam = d.addVars(n, name="lam")
        d.setObjective(a * pi, GRB.MINIMIZE)
        d.addConstrs((t[j] * pi + lam[j] >= r[j] for j in R(n)), name="rc_x")
        d.addConstrs((s[c] * pi - gp.quicksum(lam[j] for j in J[c]) >= -f[c] for c in R(q)), name="rc_y")
        return d


    def euristica_5(r, t, J, f, s, a):
        """Class by class: the first job also pays the setup, if it fits."""
        n, q = len(r), len(J)
        x, y, ra, passi = [0] * n, [0] * q, a, []
        for c in R(q):
            for j in J[c]:
                if y[c] == 0:
                    if s[c] + t[j] <= ra:
                        y[c], x[j] = 1, 1
                        passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c]} + {t[j]} = "
                                     f"{s[c] + t[j]} <= ra = {ra}; y[{c + 1}] = 1, x[{j + 1}] = 1, ra = {ra - s[c] - t[j]}.")
                        ra -= s[c] + t[j]
                    else:
                        passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c] + t[j]} > ra = {ra}; "
                                     f"job {j + 1} is skipped.")
                else:
                    if t[j] <= ra:
                        x[j] = 1
                        passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} <= ra = {ra}; x[{j + 1}] = 1, ra = {ra - t[j]}.")
                        ra -= t[j]
                    else:
                        passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} > ra = {ra}; job {j + 1} is skipped.")
        return x, y, passi


    m5, x5, y5 = modello_5(r5, t5, J5, f5, s5, a5)

    # ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
    xe, ye, passi = euristica_5(r5, t5, J5, f5, s5, a5)
    print("Class-by-class heuristic:")
    for i, s in enumerate(passi, 1):
        print(f"  Step {i}. {s}")
    lb5 = sum(r5[j] * xe[j] for j in R(7)) - sum(f5[c] * ye[c] for c in R(3))
    print(f"  lb = {lb5}  (x = {xe}, y = {ye})")

    # ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
    d5 = duale_5(r5, t5, J5, f5, s5, a5)
    pi_mano = max(r5[j] / t5[j] for j in R(7))
    ub5, viol = valuta(d5, {"pi": pi_mano})
    assert viol <= 1e-9
    print(f"Hand-built dual solution: lam = 0, pi = max_j r_j/t_j = {frazione(pi_mano)}  ->  ub = {frazione(ub5)}")
    zlp5, zlp5r, _ = due_rilassamenti(m5, d5)

    # ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------
    z5 = risolvi(m5)
    print("Optimal solution of the MILP:")
    stampa_soluzione(m5, solo_non_nulle=True)
    riga = registra_bound("5 classes setup", ub5, lb5, zlp5, zlp5r, z5, senso="max")
    salva_dati(pd.DataFrame([riga]), "sched5_bound")

    # ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------


    varianti = {}


    def variante(nome, m):
        z = risolvi(m)
        print(f"  {nome:70s} z = {frazione(z)}")
        return z

    # 5a: a single active class
    m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
    m.addConstr(y.sum() <= 1, name="one_class")
    varianti["5a"] = variante("5a. At most one class activated (sum y_c <= 1)", m)
    # 5b: class 3 only if class 1
    m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
    m.addConstr(y[2] <= y[0], name="3_only_if_1")
    varianti["5b"] = variante("5b. Class 3 is activated only if class 1 is (y_3 <= y_1)", m)
    salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched5_varianti")

    print("Done.")
    ```

<!-- embedded-script: end -->
