# 3.7 The absolute value

**Technique:** continuous with continuous (and a binary, when needed) · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

One wants $|u - v|$: a gap, an error, an imbalance. The case in the objective
and the case in a constraint behave **radically differently**.

## The constraints

- **In the objective, minimising**: a variable $d \ge 0$ and two constraints,

    $$d \ge u - v, \qquad d \ge v - u \qquad (2 \text{ constraints}),$$

    with $d$ in the objective to be minimised. No binary.

- **As a $\le$ constraint**: $|u - v| \le k$ is simply $u - v \le k$ and
  $v - u \le k$ ($2$ constraints, no binary).

- **As a $\ge$ constraint**: $|u - v| \ge k$ **cannot** be written without
  binaries. It is the disjunction "$u - v \ge k$ *or* $v - u \ge k$", and needs
  a binary $b$ and a big-M:

    $$u - v \ge k - M(1 - b), \qquad v - u \ge k - M b \qquad (2 \text{ constraints}, 1 \text{ binary}).$$

## The proof

In the first case the two constraints impose $d \ge |u - v|$ (one of the two
right-hand sides *is* $|u-v|$); the objective, which minimises $d$ and in which
$d$ appears nowhere else, drives it to equality by the exchange argument of
[technique 3.5](links-05.md). In the third case, $b = 1$ switches off the second
constraint (provided $M \ge k + \max(v-u)$) and leaves the first, and vice
versa: it is a disjunction, not a conjunction, and without the binary both would
be imposed — that is, $0 \ge 2k$, infeasible for $k > 0$.

!!! danger "The $\ge$ case is not symmetric to the $\le$ case"
    $|u-v| \le k$ is the intersection of two half-planes: a **convex** set,
    written with two linear constraints. $|u-v| \ge k$ is the complement of a
    strip: it is **not** convex, and no system of linear constraints without
    integer variables can describe it. The binary is not a trick: it is
    necessary.

## The strength of the relaxation

On the five-weight instance, $\min |L_1 - L_2|$ has optimum
$z(\mathrm{MILP}) = 1$ and relaxation $z(\mathrm{LP}^+) = 0$: the continuous
problem splits $21$ into two equal halves and zeroes the gap. The relaxation of
an absolute-value objective is typically $0$, that is, useless.

## In gurobipy, and where it is seen again

```python
d = m.addVar(name="d")
m.addConstr(d >= u - v, name="abs_plus")
m.addConstr(d >= v - u, name="abs_minus")
```

Seen again in exercises 11.3 (CDs) and 11.2 (antitrust), and in
[technique 3.13](links-13.md) in an equivalent form with two deviations.
