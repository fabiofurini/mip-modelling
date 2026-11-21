# 3. From the model to Python/Gurobi

[:material-file-pdf-box: Lecture notes (PDF)](pdf/notes-1-modelling.pdf) · [:material-presentation: Slides (PDF)](pdf/slides-03-gurobi.pdf)

**Class:** implementation · **Script:** `python/cap06_gurobi.py`
{ .scheda }

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_gurobi.ipynb)

!!! nota "Prerequisites"

    - From this module, [Chapter 1 «What is a MIP model»](https://fabiofurini.github.io/mip-modelling/modelling-1/): the classes of variables and the structure of a model.

    - From this module, [Chapter 2 «Relaxations, duality and bounds»](https://fabiofurini.github.io/mip-modelling/modelling-2/): the LP relaxation, its dual and the solver attributes `ObjVal` and `ObjBound`.

!!! chiave "Objectives"

    At the end of this chapter you will be able to:

    - write a model in `gurobipy`, one family of variables and constraints per block;

    - declare the four classes of variables, remembering the default bounds;

    - read the results in the right order: `Status`, `SolCount`, `ObjVal` and `ObjBound`;

    - use tolerances correctly when reading integer values;

    - solve the LP relaxation with `relax()` and read its duals.

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

## In summary

!!! chiave "In summary"

    - A `gurobipy` model is written block by block, one `addConstrs` per family, with the name of the constraint label.

    - The results are read always in the same order; with `SolCount` $=0$ there is no `ObjVal` to read.

    - *Integer* means integer within a tolerance: one tests `x.X > 0.5`, never `x.X == 1`.

    - `relax()` gives the LP relaxation and its duals `Pi`, the numbers that the notes compare with the hand-built dual.

    - Bin packing, makespan and the TSP (MTZ formulation) are the three models that the rest of the course reuses.
