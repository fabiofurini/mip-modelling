# 3.5 The maximum auxiliary variable

**Technique:** continuous with binaries · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

A variable $z$ must equal the **maximum** of certain quantities: the duration of
the longest activity, the highest connection cost, the load of the busiest
machine.

## The constraints

$$z ~\ge~ t_j\, x_j, \qquad \forall j \qquad (n \text{ constraints}), \qquad z \ge 0.$$

## The proof, in three steps

1. **Imposed by the constraint.** For every $j$ with $x_j = 1$ we get
   $z \ge t_j$, hence $z \ge \max_{j : x_j = 1} t_j$. This holds in every
   feasible solution.
2. **From optimality.** If $z$ appears in the objective with a strictly positive
   coefficient in a minimisation (or a strictly negative one in a maximisation)
   and in no other constraint, then in every optimum $z$ takes the smallest
   feasible value: given an optimal solution with $z > \max_{j:x_j=1} t_j$,
   lowering $z$ to that maximum leaves all constraints satisfied and strictly
   improves the objective.
3. **Conclusion.** In every optimum, $z = \max_{j : x_j = 1} t_j$ exactly, with
   the convention that the maximum over the empty set is $0$, guaranteed by
   $z \ge 0$.

!!! danger "Step 2 fails if $z$ is used elsewhere"
    If $z$ appears in another constraint that wants it *large* — for instance
    $z \ge$ something else, as in question 7.7.2 — the exchange argument no
    longer works: lowering $z$ may violate that constraint. In that case
    $z \ge \max$ still holds, but $z = \max$ does not.

## The strength of the relaxation

$\min z$ with $z \ge t_j x_j$, $t = (4, 7, 3)$ and $\sum_j x_j \ge 2$: the
integer optimum is $z(\mathit{MILP}) = 4$ (jobs 1 and 3 are chosen, and the
maximum is 4). The relaxation is $168/61 \approx 2.75$: the fractional solution
$x_j = z/t_j$ spreads the choice over all three jobs and lowers the maximum. The
maximum link gives **weak** relaxations: one of the reasons makespan problems
are hard.

## In gurobipy, and where it is seen again

```python
z = m.addVar(name="z")
m.addConstrs((z >= t[j] * x[j] for j in range(n)), name="maximum")
```

Seen again in problems [7.4](scheduling-4.md), [7.7](scheduling-7.md),
[8.4](location-4.md) and 11.4 (books on shelves).
