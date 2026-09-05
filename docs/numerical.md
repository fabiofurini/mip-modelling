# Fifteen numerical models

**Class:** BIP · ILP · MILP · **Scripts:** one per model,
`python/ex01_van.py` … `python/ex15_timetable.py`

The fifteen numerical models of the course, from EX 1 to EX 15. They are the
easiest examples: explicit data, few variables, one step for each technique.
They come before the families of problems for exactly this reason — read them to
get your bearings, then take on the general problems.

The format is reduced but always keeps the same five pieces:

1. the statement, with the data of the instance;
2. the **symbolic model**, with its variables and its constraints;
3. the **model of the instance**, primal and dual;
4. a feasible solution built by hand, which gives the primal bound;
5. a dual solution built by hand, which gives the dual bound, and the comparison
   with the solver's optimum.

Every model has its own script and notebook. Six models also have an online
page, linked below; for the others the full text is in the PDF notes, and the
code runs in Colab.

| Model | What it brings into play | $z(\mathit{MILP})$ | Notebook |
|---|---|---:|---|
| EX 1 — The eight-seat van | selection with a capacity and an implication between groups | 120 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex01_van.ipynb) |
| [EX 2 — Bus lines](ex-02.md) | assignment with a capacity in number of lines | 9 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex02_buslines.ipynb) |
| [EX 3 — Relay](ex-03.md) | assignment with more resources than tasks; totally unimodular matrix | 95 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex03_relay.ipynb) |
| EX 4 — Shoes: production, inventory and hirings | inventory balance and workforce over three months | 774 180 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex04_shoes.ipynb) |
| EX 5 — Vehicles with a minimum quantity | minimum lot: a minimum quantity if the type is produced | 25 250 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex05_vehicles.ipynb) |
| [EX 6 — Hub-and-spoke](ex-06.md) | covering: the minimum number of hubs | 3 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex06_hub.ipynb) |
| EX 7 — Custom aircraft with a fixed set-up cost | fixed set-up cost and a free quantity up to the order | 5 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex07_aircraft.ipynb) |
| [EX 8 — Seminars](ex-08.md) | exact cardinality, non-adjacency, dual with a free variable | 18 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex08_seminars.ipynb) |
| EX 9 — The eight queens | packing on a chessboard: rows, columns and diagonals | 8 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex09_queens.ipynb) |
| [EX 10 — Tools of a CNC machine](ex-10.md) | selection with a tool set: disaggregated activation | 2 500 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex10_tools.ipynb) |
| [EX 11 — Balancing between two workers](ex-11.md) | min-max against difference: same solutions, different values | 9 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex11_balancing.ipynb) |
| EX 12 — Shoes with a minimum production threshold | minimum lot with three shared resources | 24 000 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex12_shoes_threshold.ipynb) |
| EX 13 — Mutual funds bought in lots | integer counts in lots, with a proportion constraint | 16 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex13_funds.ipynb) |
| EX 14 — Emergency department shifts | covering the daily requirements with weekly shifts | 7 060 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex14_shifts.ipynb) |
| EX 15 — The music school timetable | conflicts, non-adjacency and preferences to avoid | 0 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex15_timetable.ipynb) |
