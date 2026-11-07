# How to work with the course

<!-- collana-dalla-home -->
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

## The course at a glance

**6 modelling chapters · 38 fully worked problems · 40 problems to model · 45
Colab notebooks.** The full list, chapter by chapter, is in the
[syllabus](syllabus.md).

## Getting started

Nothing to install: every script of the course has its own
[notebook that opens in Colab](notebooks.md) and runs in the browser.

If you prefer to work locally, the commands and the notes on the Gurobi licence
are on the [downloads page](downloads.md#regenerating-everything).
<!-- /collana-dalla-home -->

The course runs in two parts: first you learn the modelling tools, then you
apply them to complete problems. One thread holds them together — a model is not
just written down: its optimum is enclosed between two numbers,
$\mathit{LB} \le z(\mathit{MILP}) \le \mathit{UB}$, before it is ever handed
to the solver.

## The two-part path

| | Content | Learning objectives |
|---|---|---|
| **Part I** | Modelling | recognise a link between variables (activation, maximum, big-M, if and only if…) and prove that the model really imposes it |
| **Part II** | The problems | apply the links to three families of real problems and to the mixed problems, from the model to Gurobi code |

## The format of every exercise

Every problem of the course follows the same
four-question scheme:

1. **Model.** Write the MILP: variables (with their count), objective,
   constraints with their description, and — if two linked families of
   variables are involved — explain the link: what is the implication, and
   how the constraint (or the optimum) imposes it, in both directions.
2. **Instance.** Write the model for a small numerical instance.
3. **Heuristic.** Design a constructive algorithm that finds a feasible
   solution of the instance, and run it step by step to obtain an upper bound
   (lower bound if the problem is a maximisation).
4. **Dual.** Write the dual of the LP relaxation, for the general model and
   for the instance, and hand-build a feasible dual solution to obtain the
   bound from the other side.

The resulting `lb ≤ z(\mathit{MILP}) ≤ ub` is the thread running through the course: a
model is not just written down: its optimum is enclosed between two numbers
before it is handed to the solver. A solver stopped halfway does provide a certificate, of
course — the incumbent `ObjVal` and the bound `ObjBound` enclose the optimum in
an interval, and `MIPGap` measures its width. The teaching point is a different
one: **being able to build those two numbers by hand** is what makes it possible
to understand where they come from, to judge whether the interval the solver
reports is narrow because the model is good or wide because it is badly
formulated, and to produce a bound even when the solver returns nothing useful.

## The most common mistakes

1. Writing an implication whose thesis is true regardless (vacuous
   contrapositive): before writing it, check that antecedent and consequent
   are both genuine.
2. Proving only one direction of an implication "imposed by the constraint"
   — both "if"s are always needed.
3. Confusing a relation "imposed by the constraint" with one that "follows
   from the optimum": the second requires the six-step exchange argument, not
   just "it's clearly worth it".
4. Concluding "in every optimal solution" when the coefficient is only
   $\ge 0$ (not $> 0$): the correct conclusion is weaker, "there exists an
   optimum in which…".
5. Using a huge big-M "to be safe": it needlessly worsens the LP relaxation.
6. Forgetting that a mutual-exclusion constraint ($A + B \le 1$) does not
   imply that at least one of the two must equal 1.
7. Writing the dual of the relaxation with the wrong direction or sign of a
   dual variable relative to the direction of the primal constraint.
8. Building a feasible dual solution without checking its feasibility on all
   the constraints.

## Reproducibility

No number on these pages is written by hand: they all come out of a script you
can re-run, and an automatic check verifies that text and code say the same
thing. The commands are on the [downloads page](downloads.md#regenerating-everything).
