# 3.10 "If and only if"

**Technique:** binary with binaries · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

A binary $y$ must equal 1 **exactly when** a condition holds — for instance "all
the jobs of the class are done". One implication is not enough: two are needed.

## The constraints

With $x_1, \dots, x_p$ binary and the condition "all equal 1":

$$
\begin{aligned}
y &\le x_j, & \forall j &\qquad (p \text{ constraints}),\\
y &\ge \sum_{j=1}^{p} x_j - (p - 1) & &\qquad (1 \text{ constraint}).
\end{aligned}
$$

## The proof, in both directions

- The first group gives $y = 1 \Rightarrow x_j = 1$ for every $j$;
  equivalently, if even one of the $x_j$ is zero then $y = 0$.
- The second gives the converse: if all $x_j = 1$, the right-hand side equals
  $p - (p-1) = 1$, so $y \ge 1$ and hence $y = 1$. If at least one is zero, the
  right-hand side is $\le 0$ and the constraint says nothing.

Together they impose $y = 1 \iff \sum_j x_j = p$ in **every** feasible solution.

## When one direction is enough

If $y$ appears in the objective of a maximisation with a bonus $v > 0$ and in no
other constraint, the second constraint may be omitted: in every optimum, if all
$x_j = 1$ and $y = 0$, raising $y$ to 1 stays feasible and increases the
objective by $v > 0$. This is an optimality argument, and it holds **only at the
optimum**.

!!! danger "With $v = 0$ the argument fails, and $y$ stops meaning anything"
    Three-job instance, revenues $(2,2,2)$, capacity 3:

    | bonus $v$ | constraints | $z(\mathrm{MILP})$ | $y$, $x$ at the optimum | does $y$ say "class complete"? |
    |---:|---|---:|---|---|
    | $9$ | only $y \le x_j$ | $15$ | $y=1$, $x=(1,1,1)$ | yes |
    | $9$ | both | $15$ | $y=1$, $x=(1,1,1)$ | yes |
    | $0$ | only $y \le x_j$ | $6$ | $y=0$, $x=(1,1,1)$ | **no** |
    | $0$ | both | $6$ | $y=1$, $x=(1,1,1)$ | yes |

    With $v = 0$ the optimal value is the same in the two models, but in the
    third case $y$ is no longer a faithful indicator. If $y$ only serves to
    collect a bonus, the missing direction is useless; if $y$ appears in *other*
    constraints — and this happens as soon as a condition on the number of
    complete classes is added — it must be written.

## The strength of the relaxation

$z(\mathrm{LP}^+) = 15 = z(\mathrm{MILP})$ on this instance: with both
directions imposed the relaxation is exact. The second constraint is weak in the
relaxation (with $x_j = 1/2$ its right-hand side is negative), but here that
does not matter.

## In gurobipy, and where it is seen again

```python
m.addConstrs((y <= x[j] for j in range(p)), name="iff_up")
m.addConstr(y >= gp.quicksum(x[j] for j in range(p)) - (p - 1), name="iff_down")
```

Seen again in problem [7.6](scheduling-6.md) and in exercise 9.3.
