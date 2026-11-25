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

The course presents modelling with integer linear programming: what a MIP model is, relaxations,
duality and bounds, the implementation in Python/Gurobi, constructive heuristics, logic with binary
variables and links between variables, and models of assignment, scheduling, location, covering and
production planning problems.

Prerequisites: [Integer Linear Programming](https://fabiofurini.github.io/integer-linear-programming/).

[Start :material-arrow-right:](modelling.md){ .md-button .md-button--primary }
[:material-pencil: Exercises](to-model.md){ .md-button }
[:material-gesture-tap: Lab](lab/index.md){ .md-button }
[:material-clipboard-check-outline: Quiz](self-assessment.md){ .md-button }
[:material-download: Downloads](downloads.md){ .md-button }

</div>

<!-- collana-app -->
## Try it now

The integer points inside the polyhedron, the optimum of the continuous relaxation and the integer optimum: move the constraints and the objective function with the sliders and see how wide the gap between the two is.

<div class="gi" data-grafico="punti-interi"></div>

[:material-gesture-tap: More apps in the lab](lab/index.md){ .md-button }
<!-- /collana-app -->

## The parts of the course

<div class="grid cards" markdown>

-   :material-vector-polygon: **Modelling**

    ---

    What a MIP is, logic and binary variables, the links between variables
    (activation, minimum lot, big-M, maxima, if and only if…), lower and
    upper bounds, the solver, and fifteen worked numerical models.

    [:octicons-arrow-right-24: The six chapters](modelling.md)

-   :material-timer-sand: **Assignment and scheduling**

    ---

    Jobs on machines with limited availability: fixed costs, selection, parallel
    jobs, setups, "if and only if" prizes, sequencing with a big-M.

    [:octicons-arrow-right-24: The seven problems](scheduling.md)

-   :material-map-marker-radius: **Location and covering**

    ---

    Where to open sites and hubs: aggregated and disaggregated activation, "if
    and only if", maximum variable.

    [:octicons-arrow-right-24: The four problems](location.md)

-   :material-factory: **Production planning**

    ---

    How much to produce, not only whether: inventories, fixed setup cost,
    workforce and hiring, minimum lot.

    [:octicons-arrow-right-24: The three problems](production.md)

-   :material-shape-outline: **Mixed problems**

    ---

    The problems without a family: alternative modes, containers, division and
    balancing, dual bounds from combinatorial arguments.

    [:octicons-arrow-right-24: The nine problems](mixed.md)

-   :material-school: **The course**

    ---

    Organization, the format of the exercises, the notes in PDF, the notebooks.

    [:octicons-arrow-right-24: Organization](organization.md)

</div>

<!-- collana-da-non-perdere -->
## Don't miss

<div class="grid cards" markdown>

-   :material-pencil-box-multiple: **Exercises**

    ---

    Modelling exercises for every chapter, at exam level, on the case studies of the course.

    [:octicons-arrow-right-24: The exercises](to-model.md)

-   :material-clipboard-check-outline: **Self-assessment quiz**

    ---

    A new mock exam at every start: 13 questions, 33 points, with the solution and the link to the notes. Downloads also has the full question bank.

    [:octicons-arrow-right-24: Test yourself](self-assessment.md)

-   :material-gesture-tap: **Interactive lab**

    ---

    Apps running in the browser: move the parameters and watch the ideas of the course at work, one step at a time.

    [:octicons-arrow-right-24: The lab](lab/index.md)

-   :material-download: **Lecture notes in PDF**

    ---

    Lecture notes, exercise books and slides in PDF, with the same numbering as the website.

    [:octicons-arrow-right-24: Downloads](downloads.md)

-   :material-language-python: **Notebooks in Colab**

    ---

    The code of the course running in the browser, with nothing to install.

    [:octicons-arrow-right-24: The notebooks](notebooks.md)

-   :material-format-list-numbered: **Full index**

    ---

    All the chapters with their sections on one page, and how each chapter is organized.

    [:octicons-arrow-right-24: The index](syllabus.md)

</div>
<!-- /collana-da-non-perdere -->

---

<!-- collana -->
## The series

All the courses of the series are built the same way: lecture notes online and in PDF, exercises with solutions, an interactive lab and self-assessment quizzes.

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

-   :material-hexagon-multiple-outline: **[Combinatorial Optimization Problems](https://fabiofurini.github.io/combinatorial-optimization/)**

    knapsack, bin packing, coloring, TSP, scheduling and lot sizing: the problems, their formulations and ad hoc algorithms

-   :material-table-large: **[Dynamic Programming](https://fabiofurini.github.io/dynamic-programming/)**

    principles and DP algorithms for knapsack, lot sizing, coin change and rod cutting

-   :material-map-marker-path: **[Heuristic Algorithms](https://fabiofurini.github.io/heuristic-algorithms/)**

    constructive heuristics, local search, metaheuristics and MIP heuristics for combinatorial optimization problems

-   :material-approximately-equal: **[Approximation Algorithms](https://fabiofurini.github.io/approximation-algorithms/)**

    performance guarantees, approximation schemes and limits of approximation for combinatorial problems

-   :material-chart-line: **[LP Modelling](https://fabiofurini.github.io/lp-modelling/)**

    linear programming models of managerial problems, solved with Python and Gurobi

-   :material-chart-bell-curve-cumulative: **[NLP Modelling](https://fabiofurini.github.io/nlp-modelling/)**

    nonlinear programming models, from portfolios to machine learning, with Python and Gurobi

-   :material-vector-polygon: **MIP Modelling** · *this course*

    integer linear programming models, from the formulation to the solution with solvers

</div>
<!-- /collana -->

---

Teaching material by **[Fabio Furini](https://fabiofurini.github.io/)** —
[DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.
