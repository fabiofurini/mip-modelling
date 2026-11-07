---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# MIP Modelling

<!-- collana-riga -->
<p class="collana-riga" markdown>A course of the <b>Operations Research and Mathematics</b> series · [all the courses](#the-series)</p>
<!-- /collana-riga -->

Teaching material designed and developed by **[Fabio Furini](https://fabiofurini.github.io/)**, associate
professor at [DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.

**Mixed-integer linear models for making optimal decisions.**

[Start :material-arrow-right:](modelling.md){ .md-button .md-button--primary }
[:material-pencil: Exercises](problems.md){ .md-button }
[:material-gesture-tap: Lab](lab/index.md){ .md-button }
[:material-clipboard-check-outline: Quiz](self-assessment.md){ .md-button }
[:material-download: Downloads](downloads.md){ .md-button }

</div>

<!-- collana-app -->
## Try it now

Heuristics for the travelling salesman: compare the tours found with the bound and look at the gap.

<div class="gi" data-grafico="tsp"></div>

[:material-gesture-tap: More apps in the lab](lab/index.md){ .md-button }
<!-- /collana-app -->

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

    Forty-five notebooks that run in the browser with nothing to install: the
    same code as the pages, cell by cell.

    [:octicons-arrow-right-24: The notebooks](notebooks.md)

-   :material-flask-outline:{ .lg .middle } **I want to see the ideas in motion**

    ---

    Six interactive apps that run in the browser: integer points and relaxation,
    heuristics, big-M and formulations.

    [:octicons-arrow-right-24: The lab](lab/index.md)

-   :material-clipboard-check-outline:{ .lg .middle } **Self-assessment**

    ---

    *Mock exam*

    A new mock exam at every start: 13 questions, 33 points, with the solutions and links to the notes.

    [:octicons-arrow-right-24: Test yourself](self-assessment.md)

</div>

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
- **Forty-five [notebooks](notebooks.md)** that run in Colab with nothing to
  install: the same code as the pages, cell by cell.
- **No result transcribed by hand**: every number comes from a script you can
  re-run, and an automatic check verifies that text and code say the same thing.

!!! tip "The format of every exercise"
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

    Organization, the format of the exercises, the notes in PDF, the notebooks.

    [:octicons-arrow-right-24: Organization](organization.md)

</div>

## The course at a glance

**6 modelling chapters · 38 fully worked problems · 40 problems to model · 45
Colab notebooks.** The full list, chapter by chapter, is in the
[syllabus](syllabus.md).

## Getting started

Nothing to install: every script of the course has its own
[notebook that opens in Colab](notebooks.md) and runs in the browser.

If you prefer to work locally, the commands and the notes on the Gurobi licence
are on the [downloads page](downloads.md#regenerating-everything).

---

<!-- collana -->
## The series

Ten courses built the same way: lecture notes online and in PDF, exercises with solutions, an interactive lab and self-assessment quizzes.

<div class="grid cards" markdown>

-   :material-function-variant: **[Mathematical Analysis 1](https://fabiofurini.github.io/mathematical-analysis-1/)**

    real numbers, functions, limits, derivatives and series, with interactive graphs

-   :material-matrix: **[Linear Algebra](https://fabiofurini.github.io/linear-algebra/)**

    vectors, matrices, determinants, linear systems and eigenvalues, with the computation lab

-   :material-code-braces: **[Algorithms](https://fabiofurini.github.io/algorithms/)**

    number representation, pseudo-code, sorting and searching, analysis and recursive algorithms

-   :material-vector-triangle: **[Linear Programming](https://fabiofurini.github.io/linear-programming/)**

    polyhedra, the simplex algorithm, duality and the dual simplex, with the interactive lab

-   :material-dots-grid: **[Integer Linear Programming](https://fabiofurini.github.io/integer-linear-programming/)**

    LP relaxation, valid inequalities, cutting planes, branch-and-bound and branch-and-cut

-   :material-vector-curve: **[Convex Optimization](https://fabiofurini.github.io/convex-optimization/)**

    convex sets and functions, convex optimization problems, with interactive graphs

-   :material-graph-outline: **[Network Optimization](https://fabiofurini.github.io/network-optimization/)**

    graphs, spanning trees, shortest paths, network flows, the network simplex and project management

-   :material-hexagon-multiple-outline: **[Combinatorial Optimization](https://fabiofurini.github.io/combinatorial-optimization/)**

    knapsack, bin packing, coloring, TSP, scheduling and lot sizing, solved in every way

-   :material-vector-polygon: **MIP Modelling** · *this course*

    integer linear programming models, from the formulation to the solution with solvers

-   :material-chart-timeline-variant: **[Operations Research Lab](https://fabiofurini.github.io/operations-research-lab/)**

    modelling and solving optimization problems with Python and solvers

</div>
<!-- /collana -->

Teaching material by **[Fabio Furini](https://fabiofurini.github.io/)** —
[DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.
