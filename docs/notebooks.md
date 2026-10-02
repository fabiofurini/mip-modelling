# The notebooks of the course

Every chapter with models has its own **notebook**: one click on the badge opens
it in Google Colab, it installs the solver by itself and runs in the browser —
nothing to install on your machine. It is the very same code as the scripts in
`python/`, cell by cell, with the figures appearing below the cells instead of
being written to a file.

!!! tip "The pip licence is enough"
    The licence bundled with `gurobipy` is limited to 2000 variables and 2000
    constraints: the instances of the course are small and all fit with plenty of
    room. For larger instances activate the free academic licence at
    [portal.gurobi.com](https://portal.gurobi.com).

| Chapter | Class | Notebook |
|---|---|---|
| [3. From the model to Python/Gurobi](modelling-3.md) | implementation | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap06_gurobi.ipynb) |
| [4. Constructive heuristics](modelling-4.md) | algorithms | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap05_heuristics.ipynb) |
| [5. Logic and binary variables](modelling-5.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap02_logic.ipynb) |
| [6. Links between variables](links.md) | modelling techniques | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/cap03_links.ipynb) |
| [EX 1 — The eight-seat van](ex-01.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex01_van.ipynb) |
| [EX 2 — Bus lines](ex-02.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex02_buslines.ipynb) |
| [EX 3 — Relay](ex-03.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex03_relay.ipynb) |
| [EX 4 — Hub-and-spoke](ex-04.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex04_hub.ipynb) |
| [EX 5 — Funds bought in lots](ex-05.md) | ILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex05_funds.ipynb) |
| [EX 6 — Vehicles with a minimum quantity](ex-06.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex06_vehicles.ipynb) |
| [EX 7 — Custom aircraft with a fixed cost](ex-07.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex07_aircraft.ipynb) |
| [EX 8 — Seminars](ex-08.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex08_seminars.ipynb) |
| [EX 9 — Queens on the chessboard](ex-09.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex09_queens.ipynb) |
| [EX 10 — Tools of a CNC machine](ex-10.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex10_tools.ipynb) |
| [EX 11 — Shoes with a minimum production threshold](ex-11.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex11_shoes_threshold.ipynb) |
| [EX 12 — Balancing between two workers](ex-12.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex12_balancing.ipynb) |
| [EX 13 — The emergency room shifts](ex-13.md) | ILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex13_shifts.ipynb) |
| [EX 14 — Shoes: production, inventory and hiring](ex-14.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex14_shoes.ipynb) |
| [EX 15 — The music school timetable](ex-15.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/ex15_timetable.ipynb) |
| [Minimum-cost assignment with availability](scheduling-1.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_1_assignment.ipynb) |
| [Machines with a fixed usage cost](scheduling-2.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_2_fixedcost.ipynb) |
| [Job selection with revenues and fixed-cost machines](scheduling-3.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_3_selection.ipynb) |
| [Parallel jobs: the processing time as a maximum](scheduling-4.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_4_parallel.ipynb) |
| [One machine, job classes with setup](scheduling-5.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_5_classessetup.ipynb) |
| [Classes with completion bonus and "if and only if" reduction](scheduling-6.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_6_classesbonus.ipynb) |
| [Total tardiness on one machine: sequencing with big-M](scheduling-7.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam07_7_tardiness.ipynb) |
| [Capacitated facility location](location-1.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_1_capacitated.ipynb) |
| [p-median: at most $k$ locations](location-2.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_2_pmedian.ipynb) |
| [Signal coverage with interference](location-3.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_3_coverage.ipynb) |
| [Hub location with maximum cost](location-4.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam08_4_hub.ipynb) |
| [Lot sizing with a fixed setup cost](production-1.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam09_1_lotsizing.ipynb) |
| [Production and workforce: two equivalent formulations](production-2.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam09_2_workforce.ipynb) |
| [Vehicles: minimum lot and a bonus for variety](production-3.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam09_3_vehicles.ipynb) |
| [Prizes obtainable in two ways](mixed-1.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_1_prizes.ipynb) |
| [Combinatorial auction](mixed-2.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_2_auction.ipynb) |
| [Diet with a count of the foods and a minimum lot](mixed-3.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_3_diet.ipynb) |
| [Christmas trees and boxes of lights](mixed-4.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_4_lights.ipynb) |
| [Shipments in boxes](mixed-5.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_5_shipments.ipynb) |
| [Children across summer camps](mixed-6.md) | ILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_6_camps.ipynb) |
| [Branches across two companies](mixed-7.md) | BIP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_7_antitrust.ipynb) |
| [Songs across CDs](mixed-8.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_8_cds.ipynb) |
| [Books across shelves](mixed-9.md) | MILP | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiofurini/mip-modelling/blob/main/notebooks/fam10_9_shelves.ipynb) |

## How they are made

The notebooks are not written by hand: they are generated from the scripts with

```bash
python3 python/make_notebooks.py
```

The chapter script remains the single source of the code — the notebook takes its
docstring, sections and comments from it — and whoever prefers the command line
keeps running, from the `python/` folder:

```bash
python3 fam07_1_assignment.py
```
