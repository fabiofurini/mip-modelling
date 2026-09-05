# 3.2 Fixed cost, capacity and continuous flow

**Technique:** binary with continuous · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

As in [activation](links-01.md), but the quantity used is **continuous**:
$q_j \ge 0$ is how much is produced at plant $j$, and $y_j$ says whether the
plant is open. A closed plant produces nothing; an open one produces at most its
capacity $C_j$.

## The constraints

$$q_j \le C_j\, y_j, \qquad \forall j \qquad (m \text{ constraints}).$$

One constraint per plant, with the **right** coefficient: the capacity, not some
large number picked at random.

## The proof

If $y_j = 0$ the constraint gives $q_j \le 0$ and, together with $q_j \ge 0$,
forces $q_j = 0$: the implication "closed $\Rightarrow$ produces nothing" is
imposed by the constraint, and with it its contrapositive "produces
$\Rightarrow$ open". If $y_j = 1$ the constraint gives $q_j \le C_j$: the
capacity.

The direction "open $\Rightarrow$ produces" is not imposed and follows from
optimality only if $f_j > 0$, as in [technique 3.1](links-01.md).

## The strength of the relaxation

Two plants, fixed costs $f = (10, 14)$, unit costs $c = (3, 2)$, capacities
$C = (6, 7)$, demand $D = 9$. The optimum is $z(\mathrm{MILP}) = 44$ (both open,
$q = (2, 7)$).

| Coefficient of the binary | $z(\mathrm{LP}^+)$ |
|---|---:|
| the capacity $C_j$ | $112/3 \approx 37.33$ |
| a big-M $= 100$ (plus $q_j \le C_j$ separately) | $1059/50 = 21.18$ |

Same integer set, same optimum, relaxations far apart.

!!! tip "The rule"
    The coefficient of an activation binary is the **smallest value the
    continuous variable can be capped at when the activation equals 1**, and it
    must be derived from the data. A big-M chosen "large enough" is always valid
    and almost always terrible.

## In gurobipy, and where it is seen again

```python
m.addConstrs((q[j] <= C[j] * y[j] for j in range(mm)), name="link")
```

Seen again in problem [8.1](location-1.md) and throughout the production family.
