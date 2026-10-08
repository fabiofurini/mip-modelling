# 3. From the model to Python/Gurobi

[:material-file-pdf-box: Lecture notes (PDF)](pdf/notes-1-modelling.pdf) · [:material-presentation: Slides (PDF)](pdf/slides-03-gurobi.pdf)

**Class:** implementation · **Script:** `python/cap06_gurobi.py`
{ .scheda }

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_gurobi.ipynb)

The course uses **one solver only**, Gurobi from Python. The chapter shows how a
model is **written** — one family of constraints per block, with the names of the
mathematical model — how the results are **read**, including the case where the
solver has not finished, and three **complete models** that the
[heuristics chapter](modelling-4.md) takes up again.

Every number on these pages comes from a single script,
`python/cap06_gurobi.py`, and the chapter is organised into five sections.

<div class="grid cards" markdown>

-   :material-pencil-ruler: **3.1 Writing a model in gurobipy**

    ---

    The basic gurobipy instructions, the four classes of variables and the
    rule of the course: one family of constraints per block.

    [:octicons-arrow-right-24: The section](gurobipy-1.md)

-   :material-magnify: **3.2 Reading the results**

    ---

    `Status`, `SolCount`, `ObjVal`, `ObjBound`, `MIPGap`, `NodeCount`, and the three
    cases where `ObjVal` cannot be read.

    [:octicons-arrow-right-24: The section](gurobipy-2.md)

-   :material-tune: **3.3 Tolerances and relaxations**

    ---

    "Integer" within `IntFeasTol`, and `relax()` to obtain the relaxation of the
    model just written.

    [:octicons-arrow-right-24: The section](gurobipy-3.md)

-   :material-cube-outline: **3.4 Three classic models**

    ---

    Bin packing, makespan and travelling salesman, from the statement to the
    instance: the three problems the heuristics take up again.

    [:octicons-arrow-right-24: The section](gurobipy-4.md)

-   :material-play-circle: **3.5 The protocol, and how to run it**

    ---

    The sequence every problem repeats, from the data to the table of bounds, and
    how the script is run.

    [:octicons-arrow-right-24: The section](gurobipy-5.md)

</div>
