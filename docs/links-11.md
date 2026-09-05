# 3.11 Counting the different types

**Technique:** binaries with continuous and a count · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

"At least two different types must be produced", "at most three foods in the
diet", "no more than four configurations". One counts **how many** elements are
active, not how much of them is produced.

## The constraints

With $q_j \ge 0$ the quantity and $y_j$ the indicator:

$$
\begin{aligned}
q_j &\le c_j\, y_j, & \forall j &\qquad (n \text{ constraints}),\\
q_j &\ge \ell\, y_j, & \forall j &\qquad (n \text{ constraints}),\\
\sum_{j=1}^{n} y_j &\ge p & &\qquad (1 \text{ constraint}).
\end{aligned}
$$

## The proof, and why both thresholds are needed

The first group gives "$y_j = 0 \Rightarrow q_j = 0$"; the second gives the
missing direction "$y_j = 1 \Rightarrow q_j \ge \ell$".

!!! danger "Without the threshold $\ell$ the count is empty"
    Without $q_j \ge \ell y_j$, a solution with $y_j = 1$ and $q_j = 0$ is
    feasible: the counting constraint is satisfied by **switching on empty
    indicators**, and the condition "at least $p$ different types" says nothing
    any more. Counting types works only if every switched-on type actually
    produces something, and the threshold $\ell$ is what guarantees it. The two
    techniques — [activation](links-02.md) and [minimum lot](links-03.md) — go
    together.

## The strength of the relaxation

Three types, unit revenues $(4, 3, 5)$, resource $12$, capacity $10$ each,
threshold $\ell = 3$, at least two types: $z(\mathit{MILP}) = 57$, with
$q = (3, 0, 9)$. The relaxation is also $57$: here the counting introduces no
gap at all.

## In gurobipy, and where it is seen again

```python
m.addConstrs((q[j] <= C[j] * y[j] for j in range(n)), name="activate")
m.addConstrs((q[j] >= ell * y[j] for j in range(n)), name="lot")
m.addConstr(y.sum() >= p, name="at_least_p_types")
```

Seen again in exercises 9.3 (vehicles), 10.2 (diet) and 12.1 (trees).
