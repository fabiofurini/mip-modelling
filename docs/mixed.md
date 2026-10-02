# Mixed problems

**Class:** BIP / MILP · **Script:** one script and one notebook per problem
(`python/fam10_1_prizes.py` … `fam10_9_shelves.py`).
{ .scheda }

The three preceding families have a recognisable structure: one assigns, one
locates, one plans. The nine problems in this chapter do not have one, and none
should be forced on them: each puts together different pieces, and the
modelling work consists precisely in recognising which.

- **Selection with alternative modes** (10.1 and 10.2): a subset is chosen, but
  each object has more than one way of being chosen, and the ways exclude one
  another.
- **Quantities with a minimum lot** (10.3): next to the binaries there are
  continuous quantities, and a quantity may be zero or else between a threshold
  and a cap.
- **Covering with containers** (10.4 and 10.5): a requirement must be covered
  by buying packs of fixed composition, and the excess is either paid for or
  wasted.
- **Splitting and balancing** (10.6–10.9): a set must be divided among several
  containers and the quality is measured by how much the containers resemble
  one another.

Four of these problems share a trait that did not appear in the three families:
the **LP relaxation is weak**, and in two cases it is exactly zero. The
reason is always the same: a fractional solution can split every object in half
and put one half in each container, levelling everything.

!!! note "Where to look for a combinatorial bound when the relaxation is not enough"
    **Parity:** a count that cannot but be even.
    **Number of containers:** how many are needed at the very least, read off
    the capacities.
    **Dominance of one class:** a class of objects that by itself imposes the
    value.
    These are *combinatorial* arguments: they come from integrality, and the
    dual of the relaxation cannot see them.

## The nine problems

<div class="grid cards" markdown>

-   **10.1 Prizes with two payment modes**

    ---

    Set packing on four variables instead of two: the quantity $x_i + y_i$ is
    the indicator ``prize $i$ taken''.

    [:octicons-arrow-right-24: BIP · set packing](mixed-1.md)

-   **10.2 Combinatorial auction**

    ---

    A set packing on the bids: two bids sharing a lot cannot both be accepted.

    [:octicons-arrow-right-24: BIP · set packing](mixed-2.md)

-   **10.3 Diet with a minimum lot**

    ---

    Continuous quantities with a minimum lot: a food is bought at zero or else
    between its threshold and its cap.

    [:octicons-arrow-right-24: MILP · minimum lot](mixed-3.md)

-   **10.4 Boxes of lights for the trees**

    ---

    Configurations of fixed composition and a variety constraint: how many
    boxes of each type to buy.

    [:octicons-arrow-right-24: MILP · containers](mixed-4.md)

-   **10.5 Shipments in boxes**

    ---

    Covering a demand with containers of different size, one per product type.

    [:octicons-arrow-right-24: MILP · capacity](mixed-5.md)

-   **10.6 Children among summer camps**

    ---

    Integer counts and composition constraints. The LP relaxation does not
    see parity: the useful bound is combinatorial.

    [:octicons-arrow-right-24: ILP · integer counts](mixed-6.md)

-   **10.7 Branches between two companies**

    ---

    Min-max on the worst imbalance. The relaxation is zero: every branch is
    split in half.

    [:octicons-arrow-right-24: BIP · min-max](mixed-7.md)

-   **10.8 Tracks among CDs**

    ---

    Absolute value and levelling of the durations. Here too the relaxation is
    zero.

    [:octicons-arrow-right-24: MILP · max and min](mixed-8.md)

-   **10.9 Books among shelves**

    ---

    Maximum variable: the height of a shelf is that of its tallest book,
    imposed with $y_s \ge h_b\, x_{bs}$.

    [:octicons-arrow-right-24: MILP · maximum variable](mixed-9.md)

</div>

## Numerical models of the family

Four short models with explicit data: a selection with an implication, a
minimum lot, a packing and integer counts in lots.

| Model | What it brings into play | $z(\mathit{MILP})$ |
|---|---|---:|
| [EX 1 — The eight-seat van](ex-01-van.md) | selection with a capacity and an implication between groups | 120 |
| [EX 5 — Mutual funds bought in lots](ex-05-funds.md) | integer counts in lots, with a proportion constraint | 16 |
| [EX 6 — Vehicles with a minimum quantity](ex-06-vehicles.md) | minimum lot: a minimum quantity if the type is produced | 25 250 |
| [EX 9 — Queens on the chessboard](ex-09-queens.md) | packing on a chessboard: rows, columns and diagonals | 4 |
