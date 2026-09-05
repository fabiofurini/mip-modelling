# MIP Modelling

Teaching material designed and developed by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)**, associate
professor at [DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.

**Mixed-integer linear models for Management Engineering** — the course
lecture notes in online form, with Python/Gurobi code, notebooks and
reproducible instances. It is the second course of the series that started
with the [Operations Research Lab](https://fabiofurini.github.io/operations-research-lab/).

A model with binary and integer variables is not just *written*: it is
*proved*. Every constraint linking two families of variables imposes a logical
implication, and the student must be able to prove that it really does — in
both directions, or by explaining why one direction follows from optimality.
Then the model is *squeezed*: a constructive heuristic yields an upper bound
and a dual solution of the linear relaxation yields a lower bound, trapping
the optimal value between the two — the same technique used in practice
whenever a real instance is too large to be solved to proven optimality.
Finally the model is *solved*, with Gurobi from Python.

Every model can be run **right away in the browser**: each chapter has its own
[notebook that opens in Colab](notebooks.md), with nothing to install.

!!! tip "The method of the course"
    For every problem: model → proof of the links → instance → heuristic
    (upper bound) → dual of the LP relaxation (lower bound) → solver →
    **additional modelling questions**, because the base model is read, the
    variant is written.

## The three parts of the course

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
    production planning — plus a chapter of mixed models, for the problems that
    have no family. Solved exercises and additional questions.

    [:octicons-arrow-right-24: The problems](problems.md)

-   :material-school: **The course**

    ---

    Organization, the exam format, the collection of statements to practise
    on, the notebooks.

    [:octicons-arrow-right-24: Organization](organization.md)

</div>

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
