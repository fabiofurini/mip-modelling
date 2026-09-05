# 3.3 Minimum lot size and semicontinuous variables

**Technique:** binary with continuous · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

"If you produce, produce at least $\ell$": the quantity $q_j$ is either zero or
lies between a threshold $\ell$ and the capacity $C_j$. It is not an interval:
it is the union of a point and an interval. A variable with this domain is
called **semicontinuous**.

## The constraints

$$\ell\, y_j ~\le~ q_j ~\le~ C_j\, y_j, \qquad \forall j \qquad (2m \text{ constraints}).$$

## The proof

Both directions are imposed by the constraints. If $y_j = 0$:
$0 \le q_j \le 0$, that is $q_j = 0$. If $y_j = 1$: $\ell \le q_j \le C_j$.
Hence

$$q_j \in \{0\} \cup [\ell,\ C_j],$$

exactly the domain wanted. One needs $\ell \le C_j$, otherwise $y_j = 1$ is
infeasible and the variable is forced to zero: a data error the solver reports
as infeasibility only if $y_j$ is forced to 1 by other constraints.

## The strength of the relaxation

On the same instance as [technique 3.2](links-02.md) with $\ell = 5$: the
optimum goes from $44$ to $z(\mathrm{MILP}) = 49$, with $q = (5, 5)$ instead of
$(2, 7)$ — the threshold forces production of 5 at the second plant even though
the first is cheaper to run. But $z(\mathrm{LP}^+)$ stays at $112/3$,
**identical** to the case without the threshold.

!!! warning "Why the minimum lot is invisible in the relaxation"
    In the relaxation $y_j$ is free in $[0,1]$, and the constraint
    $q_j \ge \ell y_j$ is satisfied by lowering $y_j$: $y_j \le q_j/\ell$
    suffices. The threshold constraint **never bites** on the continuous
    problem. All of its effect is discharged onto integrality — which is why
    models with minimum lot sizes are typically harder than those without, at
    equal size.

## In gurobipy, and where it is seen again

```python
m.addConstrs((q[j] >= ell * y[j] for j in range(mm)), name="lot")
m.addConstrs((q[j] <= C[j] * y[j] for j in range(mm)), name="capacity")
```

Gurobi also has the type `GRB.SEMICONT`, which declares the domain directly; in
this course the formulation is written by hand, because that is what one must be
able to prove. Seen again in question 7.2.2 and in exercises 9.1 and 9.3.
