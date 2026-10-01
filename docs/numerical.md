# Fifteen numerical models

**Class:** BIP · ILP · MILP · **Scripts:** one per model,
`python/ex01_van.py` … `python/ex15_timetable.py`

The fifteen numerical models of the course, from EX 1 to EX 15. Explicit data,
few variables, one technique per model: they are the easiest ones, and they come
before the three families of problems and the mixed problems.

Every numerical model always has the same five parts:

1. the statement, with the data of the instance;
2. the **variables**, with their domain and their count;
3. the **model of the instance**, primal and dual;
4. a feasible solution built by hand, which gives the primal bound;
5. a dual solution built by hand, which gives the dual bound, and the comparison
   with the solver's optimum.

Every model has its own page, its own script and its own notebook.

| Model | What it brings into play | Notebook |
|---|---|---|
| [EX 1 — The eight-seat van](ex-01.md) | selection with a capacity and an implication between groups | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex01_van.ipynb) |
| [EX 2 — Bus lines](ex-02.md) | assignment with a capacity in number of lines | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex02_buslines.ipynb) |
| [EX 3 — Relay](ex-03.md) | assignment with more resources than tasks; totally unimodular matrix | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex03_relay.ipynb) |
| [EX 4 — Shoes: production, inventory and hirings](ex-04.md) | inventory balance and workforce over three months | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex04_shoes.ipynb) |
| [EX 5 — Vehicles with a minimum quantity](ex-05.md) | minimum lot: a minimum quantity if the type is produced | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex05_vehicles.ipynb) |
| [EX 6 — Hub-and-spoke](ex-06.md) | covering: the minimum number of hubs | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex06_hub.ipynb) |
| [EX 7 — Custom aircraft with a fixed set-up cost](ex-07.md) | fixed set-up cost and a free quantity up to the order | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex07_aircraft.ipynb) |
| [EX 8 — Seminars](ex-08.md) | exact cardinality, non-adjacency, dual with a free variable | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex08_seminars.ipynb) |
| [EX 9 — The eight queens](ex-09.md) | packing on a chessboard: rows, columns and diagonals | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex09_queens.ipynb) |
| [EX 10 — Tools of a CNC machine](ex-10.md) | selection with a tool set: disaggregated activation | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex10_tools.ipynb) |
| [EX 11 — Balancing between two workers](ex-11.md) | min-max against difference: same solutions, different values | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex11_balancing.ipynb) |
| [EX 12 — Shoes with a minimum production threshold](ex-12.md) | minimum lot with three shared resources | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex12_shoes_threshold.ipynb) |
| [EX 13 — Mutual funds bought in lots](ex-13.md) | integer counts in lots, with a proportion constraint | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex13_funds.ipynb) |
| [EX 14 — Emergency department shifts](ex-14.md) | covering the daily requirements with weekly shifts | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex14_shifts.ipynb) |
| [EX 15 — The music school timetable](ex-15.md) | conflicts, non-adjacency and preferences to avoid | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex15_timetable.ipynb) |
