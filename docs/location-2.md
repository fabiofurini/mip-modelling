# p-median: at most $k$ locations

**Class:** BIP · **Links:** disaggregated activation · **Script:** `python/fam08_2_pmedian.py`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_2_pmedian.ipynb)

!!! abstract "Problem 8.2"
    A company must choose at most $k \in \mathbb{Z}_{\ge 1}$ locations,
    among $m \in \mathbb{Z}_{\ge 1}$ candidates, and assign each of the
    $n \in \mathbb{Z}_{\ge 1}$ clients to the most convenient open
    location. For each location $l$ and client $c$, $d_{lc} \in
    \mathbb{Q}_{>0}$ is the distance. We want to minimize the sum of
    client-location distances.

**The problem in words.** *We decide* which locations to open (at most
$k$) and which open location to assign each client to. *The objective*:
minimum sum of distances. *The constraints*: every client to exactly one
open location; at most $k$ open locations. The classic **p-median**
problem.

## Model

**Data.**

| Symbol | Type | Meaning |
|---|---|---|
| $m$ | $\in \mathbb{Z}_{\ge 1}$ | number of locations, $l \in \{1, 2, \dots, m\}$ |
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of clients, $c \in \{1, 2, \dots, n\}$ |
| $d_{lc}$ | $\in \mathbb{Q}_{>0}$ | distance between location $l$ and client $c$ |
| $k$ | $\in \mathbb{Z}_{\ge 1}$ | maximum number of open locations |

**Decision variables.** $m$ binaries $x_l$ (location open) and $m\,n$
binaries $y_{lc}$ (client $c$ served by $l$).

$$
\begin{aligned}
\min ~~ \sum_{l=1}^{m}\sum_{c=1}^{n} d_{lc}\, y_{lc} & & \\
\text{subject to} \quad \sum_{l=1}^{m} y_{lc} &= 1, & \forall c, \\
\sum_{l=1}^{m} x_l &\le k, & \\
x_l - y_{lc} &\ge 0, & \forall l, c, \\
x_l, y_{lc} &\in \{0, 1\}. & &
\end{aligned}
$$

- the objective minimizes the sum of client-location distances;
- the first constraint assigns every client to one location ($n$ constraints);
- the second caps open locations at $k$ (one constraint);
- the third links assignment and opening, in **disaggregated** form
  ($m\,n$ constraints).

**The link.** If $y_{lc}=1$ then $x_l=1$: from the CNF of $y_{lc}
\Rightarrow x_l$, i.e. $\neg y_{lc} \lor x_l$, we get $x_l \ge y_{lc}$,
imposed directly. Unlike problem 8.1, there is no opening cost that would
discourage open-but-unused locations: the opposite direction is neither
imposed nor guaranteed by optimality.

## The model in gurobipy

```python
mod = gp.Model("p_median")
x = mod.addVars(m, vtype=GRB.BINARY, name="x")
y = mod.addVars(m, n, vtype=GRB.BINARY, name="y")
mod.setObjective(gp.quicksum(dist[l][c] * y[l, c] for l in range(m) for c in range(n)), GRB.MINIMIZE)
mod.addConstrs((y.sum("*", c) == 1 for c in range(n)), name="assign")
mod.addConstr(x.sum() <= k, name="number_of_locations")
mod.addConstrs((x[l] - y[l, c] >= 0 for l in range(m) for c in range(n)), name="link")
```

## The instance

$m = 3$ locations, $n = 3$ clients, $k = 2$:

| $d_{lc}$ | $c=1$ | $c=2$ | $c=3$ |
|---|---:|---:|---:|
| $l=1$ | 5 | 6 | 10 |
| $l=2$ | 3 | 12 | 9 |
| $l=3$ | 10 | 9 | 4 |

## Constructive heuristic: the primal bound

The first $k$ locations open; every client goes to the nearest open
location. Opening locations 1 and 2: client 1 → location 2 (dist. 3),
client 2 → location 1 (dist. 6), client 3 → location 2 (dist. 9). Value
$3+6+9=18$: $z(\mathit{MILP}) \le \mathit{UB} = 18$.

## LP relaxation and dual: the dual bound

With $\bar\varrho=0$, $\bar\pi_{lc}=0$ and $\bar\mu_c = \min_l d_{lc}$
(the distance to the nearest location overall):

$$
\bar\mu_1 = 3,\quad \bar\mu_2 = 6,\quad \bar\mu_3 = 4,
$$

of value $13$. By weak duality, $\mathit{LB}=13 \le z(\mathit{LP}) \le
z(\mathit{MILP}) \le \mathit{UB}=18$.

**What the solver says.** $z(\mathit{LP}) = z(\mathit{LP}^+) = 15$: the
relaxation is already integral on this instance. $z(\mathit{MILP}) = 15$,
with locations 1 and 3 open (not 1 and 2 as in the heuristic): heuristic
gap $20.0\%$.

| $UB$ | $LB$ (dual) | $z(\mathit{LP})$ | $z(\mathit{LP}^+)$ | $z(\mathit{MILP})$ | gap |
|---:|---:|---:|---:|---:|---:|
| 18 | 13 | 15 | 15 | 15 | $20.0\%$ |

![Optimal solution](img/cap08_pmediana_ottimo.png)

## Additional considerations

- The constraint is "at most $k$", not "exactly $k$": question 8.2.1
  checks that the optimum does not change when equality is imposed.
- $\sum_c y_{lc} \le n\, x_l$ is an aggregated valid inequality, weaker
  than the disaggregated one used in the model.

## Additional modelling questions

??? question "8.2.1 — Exactly $k$ open locations"
    Exactly $k$ locations must be open. How does the model change? What
    is the new optimum?

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
??? question "8.2.2 — Proximity coverage for one client"
    Client 1 must be served within distance $4$. How is this modelled?
    What is the new optimum?

    !!! tip "Solution"
        The solution is in the solutions document, reserved for instructors.
## Code

Full script —
[`python/fam08_2_pmedian.py`](https://github.com/fabiofurini/mip-modelling/blob/main/python/fam08_2_pmedian.py)
(reproducible with `python3 python/fam08_2_pmedian.py` from the `python/`
folder). Notebook —
[`notebooks/fam08_2_pmedian.ipynb`](https://github.com/fabiofurini/mip-modelling/blob/main/notebooks/fam08_2_pmedian.ipynb)
— opens in Colab from the badge at the top of the page.

<!-- embedded-script: begin (regenerated by python/embed_code.py) -->

??? example "Show the complete script — `python/fam08_2_pmedian.py` (142 lines)"

    ```python
    """Problem 8.2 -- Location with a maximum number of facilities (p-median).

    Disaggregated activation link between x_l (location open) and y_lc (client c
    served by l), derived from the CNF of a Boolean implication as in problem
    7.5, but here the number of open locations is bounded by k rather than by a
    time budget.
    """
    import gurobipy as gp
    import pandas as pd
    from gurobipy import GRB

    from mip import (due_rilassamenti, frazione, nuovo_modello, registra_bound,
                     risolvi, stampa_soluzione, valuta)
    from stile import CICLO, intestazione, plt, salva_dati, salva_figura

    R = range

    # ---------- 1. MODEL AND INSTANCE ----------

    intestazione("2. p-median: at most k locations, every client served by the nearest open one")
    dist2 = [[5, 6, 10], [3, 12, 9], [10, 9, 4]]   # distance location l -> client c
    k2 = 2
    m, n = 3, 3
    salva_dati(pd.DataFrame([{"location": l + 1, "client": c + 1, "d": dist2[l][c]}
                             for l in R(m) for c in R(n)]), "loc2_distanze")


    def modello_2(dist, k):
        m, n = len(dist), len(dist[0])
        mod = nuovo_modello("p_median")
        x = mod.addVars(m, vtype=GRB.BINARY, name="x")
        y = mod.addVars(m, n, vtype=GRB.BINARY, name="y")
        mod.setObjective(gp.quicksum(dist[l][c] * y[l, c] for l in R(m) for c in R(n)), GRB.MINIMIZE)
        mod.addConstrs((y.sum("*", c) == 1 for c in R(n)), name="assign")
        mod.addConstr(x.sum() <= k, name="number_of_locations")
        mod.addConstrs((x[l] - y[l, c] >= 0 for l in R(m) for c in R(n)), name="link")
        return mod, x, y


    def duale_2(dist, k):
        """max sum mu_c + k varrho;  varrho + sum_c pi_lc <= 0;  mu_c - pi_lc <= d_lc;
        mu free, varrho <= 0, pi >= 0."""
        m, n = len(dist), len(dist[0])
        dl = nuovo_modello("duale_p_median")
        mu = dl.addVars(n, lb=-GRB.INFINITY, name="mu")
        varrho = dl.addVar(lb=-GRB.INFINITY, ub=0.0, name="varrho")
        pi = dl.addVars(m, n, name="pi")
        dl.setObjective(mu.sum() + k * varrho, GRB.MAXIMIZE)
        dl.addConstrs((varrho + gp.quicksum(pi[l, c] for c in R(n)) <= 0 for l in R(m)), name="rc_x")
        dl.addConstrs((mu[c] - pi[l, c] <= dist[l][c] for l in R(m) for c in R(n)), name="rc_y")
        return dl


    m2, x2, y2 = modello_2(dist2, k2)

    # ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------

    print("Heuristic: the first k locations are opened in natural order, then every client")
    print("is served by the nearest open location.")


    def euristica_2(dist, k):
        m, n = len(dist), len(dist[0])
        x = [1 if l < k else 0 for l in R(m)]
        y, passi = {}, []
        for c in R(n):
            md, sl = float("inf"), None
            for l in R(k):
                if dist[l][c] < md:
                    md, sl = dist[l][c], l
            y[(sl, c)] = 1
            passi.append(f"Client {c + 1}: the nearest open location is {sl + 1} (distance {md}); "
                         f"y[{sl + 1}][{c + 1}] = 1.")
        return x, y, passi


    xe, ye, passi = euristica_2(dist2, k2)
    print(f"  The first k = {k2} locations are opened: x = {xe}.")
    for i, s in enumerate(passi, 1):
        print(f"  Step {i}. {s}")
    ub2 = sum(dist2[l][c] for (l, c) in ye)
    print(f"  ub = {ub2}")

    # ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------

    d2 = duale_2(dist2, k2)
    mano = {"varrho": 0.0}
    mano.update({f"mu[{c}]": min(dist2[l][c] for l in R(m)) for c in R(n)})
    lb2, viol = valuta(d2, mano)
    assert viol <= 1e-9, viol
    print("Hand-built dual solution: pi = 0, varrho = 0, mu_c = min_l d_lc = "
          + ", ".join(frazione(mano[f"mu[{c}]"]) for c in R(n)) + f"  ->  lb = {frazione(lb2)}")
    zlp2, zlp2r, _ = due_rilassamenti(m2, d2)

    # ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------

    z2 = risolvi(m2)
    print("Optimal solution of the MILP:")
    stampa_soluzione(m2, solo_non_nulle=True)
    riga = registra_bound("2 p-median", ub2, lb2, zlp2, zlp2r, z2)
    salva_dati(pd.DataFrame([riga]), "loc2_bound")

    # ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------

    varianti = {}


    def variante(nome, mod):
        z = risolvi(mod)
        print(f"  {nome:70s} z = {frazione(z)}")
        return z


    # 2a: exactly k locations must be open (not at most k)
    mod, x, y = modello_2(dist2, k2)
    mod.addConstr(x.sum() >= k2, name="number_of_locations_exact")   # with "<= k" already in the model, together they impose "= k"
    varianti["2a"] = variante("2a. Exactly k open locations (sum x_l = k)", mod)
    # 2b: client 1 must be served within distance 4 (additional coverage)
    mod, x, y = modello_2(dist2, k2)
    mod.addConstrs((y[l, 0] == 0 for l in R(3) if dist2[l][0] > 4), name="max_distance_client1")
    varianti["2b"] = variante("2b. Client 1 served within distance 4 (y_l1 = 0 if d_l1 > 4)", mod)
    salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "loc2_varianti")

    # ---------- 6. FIGURES ----------

    fig, ax = plt.subplots(figsize=(5.5, 5))
    xs = {"location": [0, 1.4, 2.8], "client": [0.3, 1.1, 2.4]}
    for c in R(3):
        l = next(l for l in R(3) if y2[l, c].X > 0.5)
        ax.plot([xs["location"][l], xs["client"][c]], [1, 0], color=CICLO[c], lw=2, marker="o")
    for l in R(3):
        marker = "s" if x2[l].X > 0.5 else "x"
        ax.plot(xs["location"][l], 1, marker=marker, ms=16, color="black" if x2[l].X > 0.5 else "gray")
        ax.annotate(f"location {l + 1}", (xs["location"][l], 1), textcoords="offset points", xytext=(0, 12), ha="center")
    for c in R(3):
        ax.plot(xs["client"][c], 0, marker="o", ms=10, color=CICLO[c])
        ax.annotate(f"client {c + 1}", (xs["client"][c], 0), textcoords="offset points", xytext=(0, -18), ha="center")
    ax.set_ylim(-0.4, 1.4)
    ax.axis("off")
    ax.set_title(f"p-median: optimal solution (z = {frazione(z2)}); square = open location")
    salva_figura(fig, "cap08_pmediana_ottimo")
    print("Fine.")
    ```

<!-- embedded-script: end -->
