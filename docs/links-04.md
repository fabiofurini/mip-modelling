# 3.4 Integer counts and rounding up

**Technique:** integer with binaries · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

"How many containers are needed?" The variable is not binary but **integer**:
$w \in \mathbb{Z}_{\ge 0}$ counts indivisible objects (boxes, trucks, shifts,
workers) and each carries a capacity $K$.

## The constraints

$$\sum_{i} a_i\, x_i ~\le~ K\, w, \qquad w \in \mathbb{Z}_{\ge 0}
\qquad (1 \text{ constraint}, 1 \text{ integer variable}).$$

## The proof

Setting $A = \sum_i a_i x_i$, the constraint imposes $w \ge A/K$ and integrality
imposes $w \ge \lceil A/K \rceil$. Together with an objective that minimises $w$
(or pays for $w$), in every optimum $w$ equals exactly that ceiling: if it were
larger, lowering it by 1 would stay feasible and reduce the cost. With a zero
cost on $w$ the conclusion weakens to "there exists an optimum".

!!! warning "The ceiling is not written with $\lceil\cdot\rceil$"
    $\lceil t \rceil$ is not a linear function: it cannot be written inside a
    constraint. The pair "inequality $\le K w$ + declaration that $w$ is
    integer" realises it *implicitly*, and that is how it must be read when
    explaining the model.

## The strength of the relaxation

$17$ unit items, capacity $K = 5$: the relaxation gives $w \ge 17/5 = 3.4$ and
the integer optimum is $z(\mathit{MILP}) = 4$. The gap $4 - 17/5 = 3/5$ comes
entirely from integrality: no linear cut on the $x$ alone closes it, an
inequality using $w$ integer is needed.

## In gurobipy, and where it is seen again

```python
w = m.addVar(vtype=GRB.INTEGER, name="w")
m.addConstr(gp.quicksum(a[i] * x[i] for i in range(n)) <= K * w, name="capacity")
```

Seen again in exercises 12.1 (boxes of lights), 12.2 (shipments) and 9.2
(workforce).
