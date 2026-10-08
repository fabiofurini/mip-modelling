# 3.2 Reading the results

[:material-file-pdf-box: Lecture notes (PDF)](pdf/notes-1-modelling.pdf) · [:material-presentation: Slides (PDF)](pdf/slides-03-gurobi.pdf)

**Class:** implementation · **Script:** `python/cap06_gurobi.py`
{ .scheda }

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_gurobi.ipynb)

`Status`, `SolCount`, `ObjVal`, `ObjBound`, `MIPGap`, `NodeCount`: what they
mean and which ones may be read, including the case where the solver has not
finished.

## Reading the results

The reading order never changes: `Status`, then `SolCount`, then `ObjVal` and
`ObjBound`, then `MIPGap`, `NodeCount`, `Runtime`.

| `Status` | value | `SolCount` | What can be said |
|---|---:|---:|---|
| `OPTIMAL` | 2 | $\ge 1$ | $z(\mathit{MILP}) = $ `ObjVal`, proved |
| `INFEASIBLE` | 3 | 0 | the model has no feasible solution |
| `UNBOUNDED` | 5 | 0 | a constraint, or a bound on a variable, is missing |
| `TIME_LIMIT` | 9 | 0 | nothing: neither a solution nor, in general, a useful bound |
| `TIME_LIMIT` | 9 | $\ge 1$ | `ObjBound` $\le z(\mathit{MILP}) \le$ `ObjVal` |
| `SOLUTION_LIMIT` | 10 | $\ge 1$ | as above |

!!! example "The four cases on the assignment instance"
    - **Normal solve.** `Status = 2`, `SolCount = 2`, `ObjVal = ObjBound = 11`,
      `MIPGap = 0`, `NodeCount = 0`.
    - **Infeasible.** With availability $(1,1,1)$: `Status = 3`, `SolCount = 0`.
    - **Stopped immediately.** With `TimeLimit = 0`: `Status = 9`,
      `SolCount = 0`, `ObjBound` $= -\infty$. There is nothing to report.
    - **Stopped at the first solution.** With `SolutionLimit = 1`:
      `Status = 10`, `SolCount = 1`, `ObjVal = 12`, `ObjBound = 10`,
      `MIPGap = 0.1667`. This is the case where an **interval** is reported: the
      optimum lies between $10$ and $12$. Saying "the optimum is $12$" would be
      false.

!!! danger "What is *not* reported"
    One does not write "the optimum is `ObjVal`" if `Status` is not `OPTIMAL`.
    One does not write a gap if `SolCount` is $0$. One does not compare the
    `Runtime` of two models solved with different settings. And one does not
    read `ObjBound` at the end of the solve thinking it is the root relaxation:
    for that, `relax()` is needed.
