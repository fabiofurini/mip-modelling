# 3.3 Tolerances and relaxations

**Class:** implementation · **Script:** `python/cap06_gurobi.py`
{ .scheda }

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_gurobi.ipynb)

"Integer" means "integer within a tolerance", and `relax()` builds the
relaxation of the model one has just written.

## Tolerances

| Parameter | Default | Meaning |
|---|---:|---|
| `IntFeasTol` | $10^{-5}$ | how far an integer variable may be from an integer |
| `FeasibilityTol` | $10^{-6}$ | violation allowed on a linear constraint |
| `OptimalityTol` | $10^{-6}$ | tolerance on the reduced costs |
| `MIPGap` | $10^{-4}$ | relative gap below which the solver stops |

!!! warning "«Integer» means «integer within a tolerance»"
    A binary may come back as $0.9999999997$. In the text one writes $1$: values
    are rounded *when they are reported*, and comparisons always use a tolerance
    — in this course $10^{-6}$, the constant `TOL` of `python/mip.py`. Writing
    `if x.X == 1` is a mistake; one writes `if x.X > 0.5`.

    The default `MIPGap` $= 10^{-4}$ also means the solver may stop *before* the
    exact optimum while declaring `OPTIMAL`: on instances with large values it
    is worth lowering it.

## The relaxation with `relax()`

```python
m.update()            # relax() copies the model: pending changes must be applied first
r = m.relax()         # binaries become 0 <= x <= 1, integers x >= lb
r.Params.OutputFlag = 0
r.optimize()
zlp = r.ObjVal
duals = {c.ConstrName: c.Pi for c in r.getConstrs()}
```

On that instance, $z(\mathit{LP}^+) = z(\mathit{LP}) = 53/5$ — the
two relaxations coincide because the assignment constraints already imply
$x_{jm} \le 1$ — and the nonzero duals are $\tilde\mu = (2,\ 4.8,\ 5)$ and
$\tilde\pi_2 = -0.2$: machine 2 is the only tight resource.
