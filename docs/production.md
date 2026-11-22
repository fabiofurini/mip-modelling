# Production planning

**Class:** MILP · **Script:** one script and one notebook per problem
(`python/fam09_1_lotsizing.py` … `fam09_3_vehicles.py`).
{ .scheda }

!!! nota "Prerequisites"

    - From this module, [Chapter 6 «Links between variables»](https://fabiofurini.github.io/mip-modelling/links/): fixed cost, minimum lot, integer counts and counting the types.

    - From this module, [Chapter 4 «Constructive heuristics»](https://fabiofurini.github.io/mip-modelling/modelling-4/): the least unit cost heuristic for lot sizing.

    - From the module *Combinatorial Optimization Problems*, the page [«Uncapacitated lot sizing problem (ULS)»](https://fabiofurini.github.io/combinatorial-optimization/combinatorial-optimization-problems/lot-sizing/variants/#box-7-defULS): the single-item lot sizing problem.

!!! chiave "Objectives"

    At the end of this chapter you will be able to:

    - write inventory and workforce balances as equality constraints;

    - link quantities and binaries with a fixed cost and a big-M read off the data;

    - model a minimum lot and a bonus for variety;

    - write the dual of the relaxation with free variables for the balances.

Three problems in which one decides **how much** to produce, not merely
*whether* to do something. The quantity variables are continuous or integer,
and on top of them sit binaries that switch on, limit or reward: the production
setup with its fixed cost (9.1), the workforce with its hirings (9.2), the
minimum lot per type with a bonus for variety (9.3).

The common trait is the **balance**: a quantity that comes in, one that goes
out and one that stays. In 9.1 and 9.2 it is the inventory balance,
$x_t + s_{t-1} - s_t = d_t$; in 9.2 there is in addition the workforce balance,
$y_t - y_{t-1} - z_t = 0$. These are equality constraints, and their duals are
**free** variables: it is the first family of the course in which this happens
systematically.

!!! note "The links between variables that come back here"
    **Fixed cost** (9.1): $x_t \le M_t\, y_t$, with $M_t$ read off the data (the
    residual demand) and not picked at random.
    **Integer counts** (9.2): the workforce $y_t$ and the hirings $z_t$ are
    numbers of people, and the available hours are $r\, y_t$.
    **Minimum lot** (9.3): the semicontinuous variable
    $q_j\, y_j \le x_j \le M_j\, y_j$, which is zero or else at least $q_j$.
    **Counting types** and **if and only if** (9.3): the variety bonus is
    collected only if the count of active types reaches two, and the missing
    direction is imposed by optimality because the bonus is positive.

## Notation of the family

| Symbol | Type | Meaning |
|---|---|---|
| $n$ | $\in \mathbb{Z}_{\ge 1}$ | number of periods, $t \in \{1, 2, \dots, n\}$ |
| $d_t$ | $\in \mathbb{Q}_{\ge 0}$ | demand of period $t$ |
| $p_t$ | $\in \mathbb{Q}_{>0}$ | unit production cost in period $t$ |
| $q_t$ | $\in \mathbb{Q}_{\ge 0}$ | fixed setup cost in period $t$ |
| $h_t$ | $\in \mathbb{Q}_{\ge 0}$ | inventory cost at the end of period $t$ |
| $M_t$ | $\in \mathbb{Q}_{>0}$ | largest useful production: $\sum_{\tau \ge t} d_\tau + r_n$ |
| $m_0$ | $\in \mathbb{Z}_{\ge 0}$ | workers on duty at the start |
| $w,\ u$ | $\in \mathbb{Q}_{>0}$ | wage per period and hiring cost |
| $r,\ g$ | $\in \mathbb{Q}_{>0}$ | hours per worker and hours per unit of product |
| $a_{ij}$ | $\in \mathbb{Q}_{\ge 0}$ | resource $i$ for one unit of type $j$ |
| $b_i$ | $\in \mathbb{Q}_{>0}$ | availability of resource $i$ |
| $\bar q_j$ | $\in \mathbb{Z}_{\ge 1}$ | minimum lot of type $j$, if produced at all |
| $\bar r$ | $\in \mathbb{Q}_{>0}$ | bonus if at least two types are produced |

## The three problems

<div class="grid cards" markdown>

-   **9.1 Lot sizing with a fixed setup cost**

    ---

    Inventory balance and production setup with a big-M read off the data.
    Two heuristics compared: lot-for-lot and least unit cost.

    [:octicons-arrow-right-24: MILP · fixed cost](production-1.md)

-   **9.2 Production and workforce**

    ---

    The same decision written twice, with the hirings or with the workforce:
    the two models are proved equivalent, optimum and relaxation included.

    [:octicons-arrow-right-24: MILP · integer counts](production-2.md)

-   **9.3 Vehicles with a minimum lot and a bonus**

    ---

    Semicontinuous variables, count of the active types and an ``if and only
    if'' bonus. Here the relaxation with the bounds beats the hand-built dual.

    [:octicons-arrow-right-24: MILP · minimum lot](production-3.md)

</div>

## In summary

!!! chiave "In summary"

    - Here one decides how much to produce: continuous or integer quantities, with binaries that switch on, limit or reward.

    - The common feature is the balance $x_t + s_{t-1} - s_t = d_t$; its duals are free variables.

    - The fixed cost uses $x_t \le M_t\, y_t$ with $M_t$ equal to the residual demand, not an arbitrary number.

    - The minimum lot makes a quantity either zero or at least $q_j$; the variety bonus uses the count of active types.
