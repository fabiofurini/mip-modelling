# 3.13 Soft constraints, deviations and penalties

**Technique:** continuous with continuous · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

A constraint one would *prefer* to satisfy, but which may be violated at a
price: the demand of a period, a timetable preference, a service target. Turning
a hard constraint into a soft one is often the difference between an infeasible
model and a useful one.

## The constraint

In place of $a' x = \beta$ one writes

$$a' x + s^- - s^+ = \beta, \qquad s^-,\ s^+ \ge 0
\qquad (1 \text{ constraint}, 2 \text{ continuous variables}),$$

and adds $\pi^- s^- + \pi^+ s^+$ to the objective, with penalties
$\pi^-, \pi^+ > 0$. The variable $s^-$ measures how far **below** the target one
is, $s^+$ how far **above**.

## The proof

The constraint alone is always satisfiable: any $a'x$ can be compensated with
one of the two deviations. The interesting property is that **in every optimum
at least one of the two deviations is zero**: if $s^- = \sigma > 0$ and
$s^+ = \tau > 0$, subtracting $\min(\sigma, \tau)$ from both leaves the
constraint satisfied (the difference $s^- - s^+$ does not change) and reduces
the objective by $(\pi^- + \pi^+)\min(\sigma,\tau) > 0$.

So $s^-$ and $s^+$ really are the positive and negative parts of the deviation,
and $s^- + s^+ = |a'x - \beta|$ in every optimum: the same thing as
[technique 3.7](links-07.md), written with an equality instead of two
inequalities.

!!! warning "With a zero penalty the deviations lose their meaning"
    If $\pi^- = 0$, the exchange argument is no longer strict and an optimal
    solution may have both deviations positive: the reading "$s^-$ is the
    shortfall" is no longer guaranteed. The same rule as everywhere in this
    chapter: the strength of the conclusion depends on the sign of the
    coefficient in the objective.

## The example

Demand $6$ in each of three periods, total availability $15 < 18$, penalties
$\pi^+ = 3$ and $\pi^- = 2$. The hard model would be **infeasible**; the soft
one gives $z(\mathrm{MILP}) = 6$, with $q = (3, 6, 6)$ and a shortfall of $3$
concentrated in the first period. Nothing in the data says it should be
concentrated: any split of the total shortfall $3$ has the same cost, and the
solver returns one of them.

## In gurobipy, and where it is seen again

```python
sm = m.addVars(T, name="s_minus");  sp = m.addVars(T, name="s_plus")
m.addConstrs((q[t] + sm[t] - sp[t] == demand[t] for t in range(T)), name="target")
m.setObjective(cost + gp.quicksum(pen_down * sm[t] + pen_up * sp[t] for t in range(T)),
               GRB.MINIMIZE)
```

Seen again in the music-school timetable (EX 15) and in exercise 9.1.
