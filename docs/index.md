# MIP Modelling

Teaching material designed and developed by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)**, associate
professor at [DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.

**Mixed-integer linear models for Management Engineering.**

[:octicons-download-24: The notes in PDF](downloads.md){ .md-button .md-button--primary }
[:octicons-play-24: The notebooks in Colab](notebooks.md){ .md-button }

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
- **Forty problems to model**, given as they really arrive and with no model
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

## Full contents

**[Modelling](modelling.md)**

1. [What is a MIP model](modelling-1.md) — data, variables, objective,
   constraints; relaxations, bounds and gaps
2. [Logic and binary variables](modelling-2.md) — CNF, the three translation
   rules, five exercises
3. [Links between variables](links.md) — the fourteen techniques, one per
   subpage, with the [map](links.md)
4. [Relaxations, duality and bounds](modelling-4.md) — the conversion table,
   three recipes for a hand-built dual solution
5. [Constructive heuristics](modelling-5.md) — the six rules, and when they
   fail
6. [From the model to Python/Gurobi](modelling-6.md) — the four classes of
   variables, the tolerances, the course protocol

**[The problems](problems.md)**

*[Fifteen numerical models](numerical.md)* — from EX 1 to EX 15, with the online page for

EX 2 [Bus lines](ex-02.md) ·
EX 3 [Relay](ex-03.md) ·
EX 6 [Hub-and-spoke](ex-06.md) ·
EX 8 [Seminars](ex-08.md) ·
EX 10 [CNC tools](ex-10.md) ·
EX 11 [Balancing](ex-11.md)

*[Assignment and scheduling](scheduling.md)*

7.1 [Minimum-cost assignment](scheduling-1.md) ·
7.2 [Machines with fixed cost](scheduling-2.md) ·
7.3 [Job selection](scheduling-3.md) ·
7.4 [Parallel jobs](scheduling-4.md) ·
7.5 [Classes with setup](scheduling-5.md) ·
7.6 [Classes with bonus](scheduling-6.md) ·
7.7 [Total tardiness](scheduling-7.md)

*[Location and coverage](location.md)*

8.1 [Capacitated location](location-1.md) ·
8.2 [p-median](location-2.md) ·
8.3 [Coverage with interference](location-3.md) ·
8.4 [Hub with maximum cost](location-4.md)

*[Production planning](production.md)*

9.1 [Lot sizing with fixed cost](production-1.md) ·
9.2 [Production and workforce](production-2.md) ·
9.3 [Vehicles with a minimum lot](production-3.md)

*[Mixed problems](mixed.md)*

10.1 [Prizes in two ways](mixed-1.md) ·
10.2 [Combinatorial auction](mixed-2.md) ·
10.3 [Diet with a minimum lot](mixed-3.md) ·
10.4 [Trees and boxes of lights](mixed-4.md) ·
10.5 [Shipments in boxes](mixed-5.md) ·
10.6 [Children across summer camps](mixed-6.md) ·
10.7 [Branches across two companies](mixed-7.md) ·
10.8 [Songs across CDs](mixed-8.md) ·
10.9 [Books across shelves](mixed-9.md)

**The course**

- [Organisation of the course](organization.md) — the path, the exam, the
  mistakes to avoid
- [Notebooks in Colab](notebooks.md) — one per problem, they open in the browser

## Installation and licence

```bash
python3 -m pip install gurobipy
```

The pip package ships with a **demo licence** (up to 2000 variables and 2000 constraints):
enough for every instance in this course. At start-up the line
`Restricted license - for non-production use only` appears: this is normal.

**Full academic licence (free of charge):**
1. register at <https://portal.gurobi.com> with your institutional email (`@uniroma1.it`);
2. request a *Named-User Academic License*;
3. run the command `grbgetkey XXXXXXXX-...` shown by the portal (you need the university network or a VPN);
4. the licence is saved in `~/gurobi.lic` and from that moment there are no size limits.

---

## Quick start

```bash
python3 -m pip install gurobipy matplotlib pandas
python3 python/run_all.py             # regenerates data, results, figures and notebooks
```

Or **with nothing to install**: every chapter has a
[notebook that opens in Colab](notebooks.md) and runs in the browser.

In the [repository](https://github.com/fabiofurini/mip-modelling)
you will find all the **Python scripts** and the **instances** in CSV format.

---

Teaching material by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)** —
[DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.
