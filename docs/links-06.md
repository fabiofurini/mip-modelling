# 3.6 Min-max, max-min and the range

**Technique:** continuous with continuous · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

Three fairness objectives, often confused: **min-max** (minimise the largest
load), **max-min** (maximise the smallest load) and **range** (minimise the gap
between the largest and the smallest).

## The constraints

With $L_k$ the load of resource $k$, $k = 1, \dots, K$:

$$
\begin{aligned}
\text{min-max:}&\quad \min T \quad\text{with}\quad T \ge L_k,\ \forall k &&(K \text{ constraints}),\\
\text{max-min:}&\quad \max U \quad\text{with}\quad U \le L_k,\ \forall k &&(K \text{ constraints}),\\
\text{range:}&\quad \min\,(T - U) \quad\text{with both} &&(2K \text{ constraints}).
\end{aligned}
$$

## The proof

Each is the [maximum auxiliary variable](links-05.md) (or minimum) with the
exchange argument in the right direction: in a $\min T$ the variable $T$ falls
to the maximum of the loads; in a $\max U$ it rises to the minimum. In the range
both pressures are present and the two conclusions hold together.

!!! danger "The three objectives are not comparable"
    On the five-weight instance $p = (3, 5, 2, 4, 7)$ to be split between two
    workers (total $21$), the three versions choose the **same** split
    $(11, 10)$ — the best possible, because the total is odd — but their optimal
    values are $11$, $10$ and $1$. They are three different numbers describing
    the same solution. Comparing "$z = 11$" of a min-max with "$z = 1$" of a
    range means nothing. And the optimal solutions need not coincide either:
    with more than two resources, min-max and max-min in general choose
    different splits.

## The strength of the relaxation

The min-max on that instance gives $z(\mathrm{LP}^+) = 21/2 = 10.5$ against
$z(\mathrm{MILP}) = 11$: the relaxation splits the weights exactly in half,
which integrality does not allow.

## In gurobipy, and where it is seen again

```python
T = m.addVar(name="T")
m.addConstrs((T >= load[k] for k in range(K)), name="max")
m.setObjective(T, GRB.MINIMIZE)
```

Seen again in question 7.4.1 (makespan), in exercise 11.2 (antitrust split) and
in 11.3 (tracks on CDs).
