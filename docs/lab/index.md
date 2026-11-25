---
hide:
  - navigation
---

# Interactive lab

The apps show relaxations, bounds, heuristics and formulations of the course.
Pick an app: it opens full page. Everything runs in the browser, without Gurobi;
the problems are small, so that every step can be seen.

## Models solved to optimality

<div class="grid cards" markdown>

-   :material-city-variant-outline: **Five projects, two funds**

    ---

    A town chooses which projects to finance with a regional and a European fund. The model is solved to optimality in the browser: the problem, the data, the symbolic and the numerical model, the projects financed by each fund, the continuous relaxation and the gap.

    [Open the app →](projects-funds.md)

-   :material-check-decagram: **Three models solved to optimality**

    ---

    Capacitated facility location, lot sizing with a setup cost and project selection with logical constraints, solved to optimality at every change of the data: the solution drawn, the binaries at 1, the continuous relaxation and the gap.

    [Open the app →](optimal-models.md)

-   :material-factory: **Lot sizing with a fixed setup cost**

    ---

    The lot sizing model with a fixed setup cost (problem 9.1), solved to optimality in the browser: the problem, the data, the symbolic and the numerical model, the optimal plan with its cost, the continuous relaxation and the gap.

    [Open the app →](lot-sizing-setup.md)

</div>

## 2. Relaxations, duality and bounds

<div class="grid cards" markdown>

-   :material-dots-grid: **Integer points and relaxation**

    ---

    The integer points inside the polyhedron, the optimum of the continuous relaxation and the integer optimum: move the constraints and the objective and see how wide the gap between them is.

    [Open the app →](integer-points.md)

</div>

## 4. Constructive heuristics

<div class="grid cards" markdown>

-   :material-bag-personal: **Knapsack: ratio heuristic versus optimum**

    ---

    The constructive ratio heuristic fills the knapsack by value/weight: follow it item by item and compare its value with the optimum and with the bound of the continuous relaxation.

    [Open the app →](knapsack-greedy.md)

-   :material-map-marker-path: **TSP: nearest neighbour versus optimal tour**

    ---

    The nearest-neighbour tour is built step by step, then 2-opt improves it: it is compared with the optimal tour, with the length of both.

    [Open the app →](tsp-heuristics.md)

-   :material-package-variant-closed: **Bin packing and scheduling**

    ---

    Next Fit, First Fit, Best Fit and First Fit Decreasing fill the bins, List scheduling and LPT assign the jobs to the machines: step by step, with the lower bound next to the solution and the optimum at the end.

    [Open the app →](bin-packing-scheduling.md)

</div>

## 5. Logic and binary variables

<div class="grid cards" markdown>

-   :material-alpha-m-box: **Big-M and relaxation**

    ---

    A conditional constraint written with big-M: move \(M\) with the slider and watch the continuous relaxation grow when \(M\) exceeds the minimum, and the MILP set lose pieces when it is too small.

    [Open the app →](big-m.md)

</div>

## 6. Links between variables

<div class="grid cards" markdown>

-   :material-vector-polygon-variant: **Weak and strong formulations**

    ---

    Two formulations with the same integer points, one on top of the other: how close each one gets to the convex hull, and what changes in the bound of the relaxation.

    [Open the app →](formulations.md)

</div>
