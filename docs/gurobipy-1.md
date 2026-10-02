# 3.1 Writing a model in gurobipy

**Class:** implementation · **Script:** `python/cap06_gurobi.py`
{ .scheda }

The eight instructions that are enough to write a model, the four classes of
variables and the rule of the course: one family of constraints per block, with
the names of the mathematical model.

## The eight instructions that are enough

A model is written in gurobipy with eight instructions, always the same ones, and
from here on the line of code that writes it appears next to every model. It pays
to see them once on a small, complete model: the **binary knapsack**, where out
of $n$ items of value $p_j$ and weight $w_j$ one chooses a subset of weight at
most $c$ worth as much as possible.

$$
\begin{aligned}
\max ~~ \sum_{j=1}^{n} p_j\, x_j & &\\
\text{subject to} \quad \sum_{j=1}^{n} w_j\, x_j &\le c, &\\
x_j &\in \{0, 1\}, & \forall j \in \{1, 2, \dots, n\}.
\end{aligned}
$$

```python
import gurobipy as gp                       # the module, always abbreviated gp
from gurobipy import GRB                    # the constants: GRB.BINARY, GRB.MAXIMIZE...

p = [10, 7, 6, 4]                           # values
w = [5, 4, 3, 3]                            # weights
c = 9                                       # capacity
n = len(p)

m = gp.Model("knapsack")                                     # an empty model
x = m.addVars(n, vtype=GRB.BINARY, name="x")                 # n binary variables
m.setObjective(gp.quicksum(p[j] * x[j] for j in range(n)), GRB.MAXIMIZE)
m.addConstr(gp.quicksum(w[j] * x[j] for j in range(n)) <= c, name="capacity")
m.optimize()
```

Eight instructions, one per line of the model:

- `Model` creates the model; everything else hangs off it.
- `addVars` adds a whole indexed family: `addVars(n)` gives
  $x_0, \dots, x_{n-1}$, `addVars(n, k)` the matrix $x_{ij}$, indexed as `x[j]`
  and `x[i, j]`. For a single variable there is `addVar`. Python indices start at
  zero, written models start at one: that is the only difference to keep in mind.
- `vtype` declares the domain: `GRB.BINARY`, `GRB.INTEGER`, and without `vtype`
  the variable is continuous and non-negative. The domain is a constraint:
  declaring it wrongly is declaring a different model.
- `quicksum` builds a sum $\sum_j c_j x_j$ without intermediate expressions.
- `setObjective` takes the expression and the direction, `GRB.MINIMIZE` or
  `GRB.MAXIMIZE`.
- `addConstr` adds *one* constraint, `addConstrs` a whole family, and wants a
  generator in round brackets: one line of code per family, just as it is one
  line in the written model.
- `optimize` solves.

With the same eight instructions one writes the other classical problems that
come back in these pages. **Bin packing** — $n$ items of size $w_j$ into bins of
capacity $c$, using as few as possible — wants two families of binaries,
$x_{ji}$ and $y_i$, and two families of constraints:

```python
x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
y = m.addVars(k, vtype=GRB.BINARY, name="y")
m.setObjective(y.sum(), GRB.MINIMIZE)
m.addConstrs((x.sum(j, "*") == 1 for j in range(n)), name="assign")
m.addConstrs((gp.quicksum(w[j] * x[j, i] for j in range(n)) <= c * y[i]
              for i in range(k)), name="capacity")
```

**Scheduling on identical machines** ($P||z$) changes only the objective
and one constraint: a continuous $T$ for the makespan, $\min T$, and
$\sum_j t_j x_{ji} \le T$ for every machine. The **travelling salesman** has one
binary per arc, $x_{ij}$, and two families of equalities — every city is left
once and entered once — plus the constraints forbidding subtours.

## The four classes of variables

| What | `vtype` | Domain | Typical use |
|---|---|---|---|
| yes/no decision | `GRB.BINARY` | $\{0,1\}$ | selection, activation, assignment |
| count | `GRB.INTEGER` | $\mathbb{Z}$ between `lb` and `ub` | boxes, shifts, workers |
| measurable quantity | (default) | $[\mathit{LB}, \mathit{UB}] \subseteq \mathbb{R}$ | time, money, flow |
| free variable | (default) with `lb=-GRB.INFINITY` | $\mathbb{R}$ | duals of equalities |

!!! warning "The two defaults people forget"
    `GRB.BINARY` already implies `lb = 0` and `ub = 1`: there is no need to
    repeat them. A continuous variable has `lb = 0` by default: a variable that
    must be allowed to go negative — typically the dual of an equality, or a
    signed deviation — must be declared with `lb=-GRB.INFINITY`, otherwise the
    model is silently wrong.

## The model, one family per block

```python
def model(t, c, a):
    """Problem 7.1: one addConstrs per family, with the label as its name."""
    m = gp.Model("assignment");  m.Params.OutputFlag = 0
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")           # data -> variables
    m.setObjective(gp.quicksum(c[j][h] * x[j, h] for j in range(n)
                               for h in range(k)), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in range(n)), name="assign")
    m.addConstrs((gp.quicksum(t[j][h] * x[j, h] for j in range(n)) <= a[h]
                  for h in range(k)), name="availability")
    return m, x
```

The three writing rules of the course: **one `addConstrs` per family**, in the
order of the mathematical model, with the `name` equal to the label; **variables
are declared all at once** with `addVars` and the indices of the model
(`x.sum(j, "*")` is the writing of the dummy index); **data come in as
arguments**, not as globals, so the same function serves the base instance and
all the variants.

The model has $9$ variables, $6$ constraints and $18$ nonzero coefficients. To
check that it is what was written on paper, `m.write("model.lp")`:

```text
Minimize
  5 x[0,0] + 10 x[0,1] + 2 x[0,2] + 5 x[1,0] + 4 x[1,1] + 6 x[1,2]
   + 5 x[2,0] + 4 x[2,1] + 6 x[2,2]
Subject To
 assign[0]: x[0,0] + x[0,1] + x[0,2] = 1
 ...
```

It is the quickest way to spot a wrong coefficient: the instance table and this
output must agree line by line.
