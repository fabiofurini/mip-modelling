# Modelling

You do not learn models by heart here: you learn the **techniques for building
them**. Thirty memorised formulations are no help in front of a new text; a
dozen links between variables, knowing why they work, are.

!!! success "By the end of this part you can"
    - Translate a logical condition into linear constraints, and prove that they
      really impose it.
    - Link a binary variable to a continuous or integer one: activation, fixed
      cost, minimum lot, a big-M read from the data.
    - Derive a bound from the linear relaxation and write its dual by hand.
    - Build a feasible solution by hand, and say which bound it gives.
    - Take the model into Python/Gurobi and read what the solver answers.

Six chapters, in this order: what a MIP model is, the logic of binary variables,
the fourteen links between variables, bounds from the relaxation side (the dual)
and from the feasible-solutions side (constructive heuristics), and the solver.

Every chapter has a **script** producing all the numbers quoted and a
**notebook** that opens in Colab. No value appears on these pages unless it
comes out of a reproducible run.

<div class="grid cards" markdown>

-   :material-shape-outline: **1. What is a MIP model**

    ---

    Data, variables, objective, constraints. Why rounding fails. The two LP
    relaxations and which side the bounds are on. Three gaps not to be confused.
    Branch-and-bound in one page.

    [:octicons-arrow-right-24: The chapter](modelling-1.md)

-   :material-gate-and: **2. Logic and binary variables**

    ---

    AND, OR, NOT; clauses and conjunctive normal form; the three rules turning a
    CNF into linear constraints; implications, contrapositives and splits; five
    solved exercises, all checked by enumeration.

    [:octicons-arrow-right-24: The chapter](modelling-2.md)

-   :material-link-variant: **3. Links between variables**

    ---

    Fourteen techniques for linking different families of variables: activation,
    fixed cost, minimum lot, counts, maximum, min-max, absolute value, big-M,
    precedences, "if and only if", types, alldiff, penalties, piecewise
    functions. Plus the map.

    [:octicons-arrow-right-24: The fourteen techniques](links.md)

-   :material-arrow-collapse-vertical: **4. Relaxations, duality and bounds**

    ---

    The primal/dual conversion table, three recipes for building a dual solution
    by hand, valid inequalities and cover cuts, and why the LP duals are not the
    marginal prices of the MILP.

    [:octicons-arrow-right-24: The chapter](modelling-4.md)

-   :material-run-fast: **5. Constructive heuristics**

    ---

    Next-fit, first-fit, best-fit, LPT, covering constructive heuristic, knapsack constructive heuristic and lot
    sizing: pseudocode, trace, feasibility check and bound. A failure of the
    constructive heuristic does not prove infeasibility.

    [:octicons-arrow-right-24: The chapter](modelling-5.md)

-   :material-language-python: **6. From the model to Python/Gurobi**

    ---

    The four classes of variables, one `addConstrs` per family, and how to read
    `Status`, `SolCount`, `ObjVal`, `ObjBound`, `MIPGap`, `NodeCount` and the
    tolerances. The course protocol, from start to finish.

    [:octicons-arrow-right-24: The chapter](modelling-6.md)

</div>
