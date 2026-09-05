# 3.9 Precedences and sequencing

**Technique:** binaries with continuous, big-M · **Script:** `python/cap03_links.py` · [All the techniques](links.md)

## The link in words

On a machine that runs one job at a time, for every pair of jobs one precedes
the other. It is a **disjunction per pair**, not a precedence fixed by the data.

## The constraints

With $\kappa_j \ge 0$ the completion time of job $j$, $t_j$ its duration and
$s_{ij} \in \{0,1\}$ equal to 1 if $j$ precedes $i$:

$$
\begin{aligned}
s_{ij} + s_{ji} &= 1, & \forall i < j &\qquad \big(\tbinom{n}{2} \text{ constraints}\big),\\
\kappa_i &\ge \kappa_j + t_i - M\,(1 - s_{ij}), & \forall i \ne j &\qquad (n(n-1) \text{ constraints}),\\
\kappa_j &\ge t_j, & \forall j &\qquad (n \text{ constraints}).
\end{aligned}
$$

## The proof, and the smallest $M$

The first constraint imposes that exactly one of the two orders is chosen. If
$s_{ij} = 1$, the second becomes $\kappa_i \ge \kappa_j + t_i$: job $i$ finishes
at least $t_i$ after $j$ finishes, so they do not overlap. If $s_{ij} = 0$ it
becomes $\kappa_i \ge \kappa_j + t_i - M$, which must always hold. Since
$\kappa_i \ge t_i$ and $\kappa_j \le \sum_h t_h$ in every sensible solution, it
suffices to take

$$M = \sum_{h=1}^{n} t_h,$$

because then $\kappa_j + t_i - M \le \sum_h t_h + t_i - \sum_h t_h = t_i \le \kappa_i$.

!!! warning "The horizon must be declared"
    Without an upper bound on the $\kappa_j$, **no finite $M$ is valid**. The
    horizon $\sum_h t_h$ is part of the model, not an implementation detail.

## The strength of the relaxation

Three jobs of duration $(3, 2, 4)$ on one machine, makespan objective:
$z(\mathrm{MILP}) = 9 = \sum_h t_h$ (obviously: a single machine), with
completion times $(3, 5, 9)$. The relaxation is $4$: with $s_{ij} = 1/2$ all the
precedence constraints are half switched off and the jobs may overlap. It is the
weakest relaxation in the whole chapter, and it explains why big-M sequencing
models scale badly.

## In gurobipy, and where it is seen again

```python
M = sum(t)                                    # the horizon, declared
for i in range(n):
    for j in range(i):
        m.addConstr(s[i, j] + s[j, i] == 1, name=f"disj{i}{j}")
        m.addConstr(kappa[i] >= kappa[j] + t[i] - M * (1 - s[i, j]), name=f"prec{i}{j}")
        m.addConstr(kappa[j] >= kappa[i] + t[j] - M * (1 - s[j, i]), name=f"prec{j}{i}")
```

Seen again in problem [7.7](scheduling-7.md), where release dates allow $M$ to
be reduced.
