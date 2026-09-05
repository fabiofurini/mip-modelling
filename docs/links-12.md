# 3.12 Alldiff and binary expansion

**Technique:** binaries with each other; integer with binaries · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

Two different but related needs: giving $n$ objects $n$ **all distinct** values
(*alldiff*), and representing a bounded integer variable with binary variables
(*binary expansion*).

## The constraints

**Alldiff**, with $p_{iv} = 1$ if object $i$ gets value $v$:

$$
\sum_{v} p_{iv} = 1 \quad \forall i \qquad (n \text{ constraints}), \qquad
\sum_{i} p_{iv} = 1 \quad \forall v \qquad (n \text{ constraints}).
$$

**Binary expansion** of $v \in \{0, 1, \dots, 2^K - 1\}$:

$$v = \sum_{k=0}^{K-1} 2^k\, b_k, \qquad b_k \in \{0,1\}
\qquad (1 \text{ constraint}, K \text{ binaries}).$$

## The proof

Alldiff is a **double set partitioning**: the first group gives "every object
one value", the second "every value to one object". Together they impose a
bijection, that is, all distinct values. Binary expansion is the base-2
representation, unique for every integer in that range: the correspondence
between $v$ and $(b_0, \dots, b_{K-1})$ is one-to-one.

!!! note "Alldiff has an exact relaxation, expansion does not help"
    The matrix of the double partitioning is the one of the assignment problem:
    it is **totally unimodular**, so every vertex of the relaxation is integer
    and $z(\mathrm{LP}^+) = z(\mathrm{MILP})$. On the $3 \times 3$ instance of
    the script both are $7$: integrality is free.

    Binary expansion, by contrast, adds no strength: $\sum_k 2^k b_k$ with
    $b_k \in [0,1]$ covers all of $[0, 2^K - 1]$ continuously, exactly like
    $v \ge 0$, $v \le 2^K - 1$. It serves to *reformulate*, not to tighten — for
    instance when another part of the model needs binary indicators rather than
    an integer variable.

## The example

$v \in \{0,\dots,7\}$ with $v \ge 5$, $\min v$: the model gives
$v = 5 = 1 + 4$, that is $(b_0, b_1, b_2) = (1, 0, 1)$.

## In gurobipy, and where it is seen again

```python
m.addConstrs((p.sum(i, "*") == 1 for i in range(n)), name="one_value")
m.addConstrs((p.sum("*", v) == 1 for v in range(n)), name="alldiff")
m.addConstr(v == gp.quicksum(2 ** k * b[k] for k in range(K)), name="expansion")
```

Alldiff is seen again in the numerical model of the queens (EX 9) and in the
music-school timetable (EX 15).
