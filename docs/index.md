# MIP Modelling

Teaching material designed and developed by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)**, associate
professor at [DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.

**Mixed-integer linear models for making optimal decisions.**

<div class="grid cards" markdown>

-   :material-book-open-page-variant:{ .lg .middle } **I am studying the theory**

    ---

    What a MIP model is, logic and binary variables, the fourteen links,
    relaxations and bounds, heuristics, Gurobi.

    [:octicons-arrow-right-24: The six chapters](modelling.md)

-   :material-pencil-ruler:{ .lg .middle } **I want to do exercises**

    ---

    Thirty-eight problems worked out in full and forty to model, with statement,
    model, instance, heuristic, dual and optimum.

    [:octicons-arrow-right-24: The problems](problems.md)

-   :material-language-python:{ .lg .middle } **I want to use Gurobi**

    ---

    Forty-four notebooks that run in the browser with nothing to install: the
    same code as the pages, cell by cell.

    [:octicons-arrow-right-24: The notebooks](notebooks.md)

</div>

[:octicons-download-24: Download the course material](downloads.md){ .md-button .md-button--primary }

## What you learn to do

- **Read a problem and write its model.** What the decisions are, which
  variables are needed and with which domain, and how each sentence of the
  statement becomes a constraint.
- **Show that the model does what it should.** A constraint linking two
  variables imposes an implication: you prove that it really does, in both
  directions.
- **Find a good solution by hand**, with a heuristic built in a few steps and
  justified.
- **Build the dual of the relaxation** and read off how much, at most, there
  still is to gain.
- **Say what the solution in your hands is worth.** On a large instance the
  solver stops short of the optimum: what is left is a solution and two numbers
  enclosing it. If they are close, that solution is good enough — and you can
  prove it.
- **Write and solve the model with Gurobi**, and understand what the solver
  answers.

## How the course gets there

- **The method, in six chapters**: logic and binary variables, the fourteen
  links between variables with their proofs, relaxations and bounds,
  constructive heuristics, Gurobi.
- **Thirty-eight problems worked out in full**: fifteen numerical models, one
  per technique, with the data written out; and twenty-three problems of the
  three families — assignment and scheduling, location and covering, production
  planning — plus the mixed problems. Each with statement, model, instance,
  heuristic, dual, optimum and comparison.
- **Two or three additional questions on every problem**: a datum changes or a
  constraint is added, and model and bounds are redone. For each exercise one
  variant is worked out in full, as a model answer.
- **Forty problems to model**, presented as they would arise in practice and with no model
  already written: twenty with explicit numerical data and twenty in symbolic
  form.
- **Forty-four [notebooks](notebooks.md)** that run in Colab with nothing to
  install: the same code as the pages, cell by cell.
- **No result transcribed by hand**: every number comes from a script you can
  re-run, and an automatic check verifies that text and code say the same thing.

!!! tip "The format of every exercise (and of the exam)"
    Model → links between the variables → instance → heuristic (upper bound) →
    dual of the LP relaxation (lower bound) → solver → additional modelling
    questions.

## The two parts of the course

<div class="grid cards" markdown>

-   :material-vector-polygon: **Modelling**

    ---

    What a MIP is, logic and binary variables, the links between variables
    (activation, minimum lot, big-M, maxima, if and only if…), lower and
    upper bounds, the solver.

    [:octicons-arrow-right-24: The six chapters](modelling.md)

-   :material-puzzle: **The problems**

    ---

    Three families — assignment and scheduling, location and coverage,
    production planning — plus a chapter of mixed problems, for the problems that
    have no family. Solved exercises and additional questions.

    [:octicons-arrow-right-24: The problems](problems.md)

-   :material-school: **The course**

    ---

    Organization, the exam format, the notes in PDF, the notebooks.

    [:octicons-arrow-right-24: Organization](organization.md)

</div>

## The course at a glance

**6 modelling chapters · 38 fully worked problems · 40 problems to model · 44
Colab notebooks.** The full list, chapter by chapter, is in the
[syllabus](syllabus.md).

## Getting started

Nothing to install: every script of the course has its own
[notebook that opens in Colab](notebooks.md) and runs in the browser.

If you prefer to work locally, the commands and the notes on the Gurobi licence
are on the [downloads page](downloads.md#regenerating-everything).

---

By the same author: **[Operations Research Lab](https://fabiofurini.github.io/operations-research-lab/)** —
the lab module, with the same tools and the same style.

Teaching material by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)** —
[DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.
