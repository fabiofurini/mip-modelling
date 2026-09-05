# 3.8 Big-M: conditional constraints and disjunctions

**Technique:** binary with a constraint · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

"If $y = 1$ then the constraint $a' x \le b$ holds; if $y = 0$ the constraint is
not there." A constraint that switches on and off.

## The constraint

$$a' x ~\le~ b + M\,(1 - y) \qquad (1 \text{ constraint}).$$

## The proof, and how $M$ is chosen

With $y = 1$ the constraint is $a' x \le b$: switched on. With $y = 0$ it
becomes $a' x \le b + M$: switched off **provided** $M$ is large enough to cut
nothing off, that is

$$M ~\ge~ \max\{a' x : x \text{ feasible for the other constraints}\} - b.$$

Three things must be told apart:

- a **valid** $M$: it satisfies the inequality above, so the model has the right
  integer set;
- an **improvable** $M$: valid but larger than necessary; the integer set is the
  same, the relaxation is weaker;
- the **smallest proved $M$**: the smallest value for which validity has been
  *proved*, typically by computing that maximum from the variable bounds alone.
  It is not necessarily the absolute minimum, and it is honest to say so.

!!! danger "An invalid $M$ is not «a little different»"
    With $a = (3,4,5)$, $b = 6$ and $x$ binary, the maximum of $a'x$ is $12$, so
    $M = 12 - 6 = 6$ is valid. On $\max\ x_1 + x_2 + x_3 + y$ the optimum is
    $z(\mathit{MILP}) = 3$ (with $y = 0$ and all the $x$ at 1). With $M = 5$ the
    constraint with $y = 0$ remains $3x_1 + 4x_2 + 5x_3 \le 11$, which excludes
    $x = (1,1,1)$: the optimum drops to $2$. The model no longer answers the
    question asked.

## The strength of the relaxation

| $M$ | $z(\mathit{LP}^+)$ | |
|---|---:|---|
| $6$ (the smallest proved) | $3$ | coincides with $z(\mathit{MILP})$ |
| $20$ | $37/10 = 3.7$ | |
| $1000$ | $1997/500 \approx 3.994$ | almost the largest possible, $4$ |

The degradation is monotone and fast. The operational rule: **compute $M$ from
the data, always, and write it in the text right after the model**.

## In gurobipy, and where it is seen again

```python
M = sum(max(a[j], 0) for j in range(n)) - b       # computed from the data, not guessed
m.addConstr(gp.quicksum(a[j] * x[j] for j in range(n)) <= b + M * (1 - y), name="cond")
```

Seen again in problem [7.7](scheduling-7.md) and in
[technique 3.9](links-09.md).
