# 6.3 Minimum lot size and semicontinuous variables

[:material-file-pdf-box: Lecture notes (PDF)](pdf/notes-1-modelling.pdf) · [:material-presentation: Slides (PDF)](pdf/slides-06-links.pdf)

**Technique:** binary with continuous · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

"If you produce, produce at least $\ell$": the quantity $q_j$ is either zero or
lies between a threshold $\ell$ and the capacity $c_j$. It is not an interval:
it is the union of a point and an interval. A variable with this domain is
called **semicontinuous**; when the quantity is integer on top of that ---
pieces, units, people --- it is called **semi-integer**, and the two constraints
are the same.

## The constraints

$$
\begin{aligned}
\ell\, y_j &~\le~ q_j, & \forall j & \qquad (m \text{ constraints}),\\
q_j &~\le~ c_j\, y_j, & \forall j & \qquad (m \text{ constraints}).
\end{aligned}
$$

## The proof

Both directions are imposed by the constraints. If $y_j = 0$:
$0 \le q_j \le 0$, that is $q_j = 0$. If $y_j = 1$: $\ell \le q_j \le c_j$.
Hence

$$q_j \in \{0\} \cup [\ell,\ c_j],$$

exactly the domain wanted. One needs $\ell \le c_j$, otherwise $y_j = 1$ is
infeasible and the variable is forced to zero: a data error the solver reports
as infeasibility only if $y_j$ is forced to 1 by other constraints.

## The strength of the relaxation

On the same instance as [technique 6.2](links-02.md) with $\ell = 5$: the
optimum goes from $44$ to $z(\mathit{MILP}) = 49$, with $q = (5, 5)$ instead of
$(2, 7)$ — the threshold forces production of 5 at the second plant even though
the first is cheaper to run. But $z(\mathit{LP}^+)$ stays at $112/3$,
**identical** to the case without the threshold.

!!! warning "Why the minimum lot is invisible in the relaxation"
    In the relaxation $y_j$ is free in $[0,1]$, and the constraint
    $q_j \ge \ell y_j$ is satisfied by lowering $y_j$: $y_j \le q_j/\ell$
    suffices. The threshold constraint **never bites** on the continuous
    problem. All of its effect is discharged onto integrality — which is why
    models with minimum lot sizes are typically harder than those without, at
    equal size.

## In gurobipy

```python
m.addConstrs((q[j] >= ell * y[j] for j in range(mm)), name="lot")
m.addConstrs((q[j] <= C[j] * y[j] for j in range(mm)), name="capacity")
```

Gurobi also has the type `GRB.SEMICONT`, which declares the domain directly; in
this course the formulation is written by hand, because that is what one must be
able to prove.
