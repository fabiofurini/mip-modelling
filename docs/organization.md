# Course organization

## The three-part path

| | Content | Learning objectives |
|---|---|---|
| **Part I** | Modelling | recognise a link between variables (activation, maximum, big-M, if and only if…) and prove that the model really imposes it |
| **Part II** | The problems | apply the links to three families of real problems and to the mixed models, from the model to Gurobi code |
| **Part III** | The course | put what was learned to the test with the additional modelling questions |

## The format of every exercise (and of the exam)

Every problem of the course — and every exam question — follows the same
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

The resulting `lb ≤ z(MILP) ≤ ub` is the thread running through the course: a
model is not just written down, it is squeezed from both sides before it is
handed to the solver. A solver stopped halfway does provide a certificate, of
course — the incumbent `ObjVal` and the bound `ObjBound` enclose the optimum in
an interval, and `MIPGap` measures its width. The teaching point is a different
one: **being able to build those two numbers by hand** is what makes it possible
to understand where they come from, to judge whether the interval the solver
reports is narrow because the model is good or wide because it is badly
formulated, and to produce a bound even when the solver returns nothing useful.

## Grading criteria

| Dimension | Weight |
|---|---|
| Correctness of the model (variables, objective, constraints) | 35% |
| Proof of the link between the variables (both directions) | 25% |
| Constructive heuristic and correct execution | 20% |
| Dual of the relaxation and feasible dual solution | 20% |

## Typical discussion questions

- Is the link constraint aggregated or disaggregated? What difference does it
  make to the LP relaxation?
- Is the opposite direction of the implication imposed by the constraint or
  does it follow from the optimum? How is it proved?
- What is the smallest big-M that can be justified from the data?
- Does the heuristic find the optimum? How can one know without the solver?
- Is the hand-built dual optimal for the relaxation, or only feasible?

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

```bash
python3 -m pip install gurobipy matplotlib pandas
python3 python/run_all.py             # regenerates data, results, figures and notebooks
python3 python/check_numbers.py       # checks every number quoted in the notes
```
