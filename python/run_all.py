"""Runs all the course scripts in sequence.

Regenerates: data (data/*.csv), data for the pgfplots figures (notes/figure/dat/*.csv),
matplotlib previews (notes/figure/*.pdf), site images (docs/img/*.png),
the chapter notebooks (notebooks/*.ipynb) and the code blocks embedded in the
website pages (docs/*.md).

Usage:  python3 run_all.py
"""
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = [
    # Part I — modelling
    "cap01_models.py",
    "cap02_logic.py",
    "cap03_links.py",
    "cap04_bounds.py",
    "cap05_heuristics.py",
    "cap06_gurobi.py",
    # Part II — the problems
    "fam07_1_assignment.py",
    "fam07_2_fixedcost.py",
    "fam07_3_selection.py",
    "fam07_4_parallel.py",
    "fam07_5_classessetup.py",
    "fam07_6_classesbonus.py",
    "fam07_7_tardiness.py",
    "fam08_1_capacitated.py",
    "fam08_2_pmedian.py",
    "fam08_3_coverage.py",
    "fam08_4_hub.py",
    "fam09_1_lotsizing.py",
    "fam09_2_workforce.py",
    "fam09_3_vehicles.py",
    "fam10_1_prizes.py",
    "fam10_3_diet.py",
    "fam10_2_auction.py",
    "fam10_6_camps.py",
    "fam10_7_antitrust.py",
    "fam10_8_cds.py",
    "fam10_9_shelves.py",
    "fam10_4_lights.py",
    "fam10_5_shipments.py",
    # the fifteen numerical models
    "ex01_van.py",
    "ex02_buslines.py",
    "ex03_relay.py",
    "ex04_shoes.py",
    "ex05_vehicles.py",
    "ex06_hub.py",
    "ex07_aircraft.py",
    "ex08_seminars.py",
    "ex09_queens.py",
    "ex10_tools.py",
    "ex11_balancing.py",
    "ex12_shoes_threshold.py",
    "ex13_funds.py",
    "ex14_shifts.py",
    "ex15_timetable.py",
]

base = Path(__file__).resolve().parent
inizio = time.time()
for s in SCRIPT:
    print(f"\n{'#' * 72}\n# {s}\n{'#' * 72}")
    esito = subprocess.run([sys.executable, str(base / s)], cwd=base)
    if esito.returncode != 0:
        print(f"ERROR in {s}: stopping.")
        sys.exit(1)
for finale, messaggio in [("make_notebooks.py", "notebook generation"),
                          ("embed_code.py", "embedding of the code into the pages")]:
    print(f"\n{'#' * 72}\n# {finale}\n{'#' * 72}")
    esito = subprocess.run([sys.executable, str(base / finale)], cwd=base)
    if esito.returncode != 0:
        print(f"ERROR in the {messaggio}: stopping.")
        sys.exit(1)

print(f"\nAll scripts completed in {time.time() - inizio:.1f} s.")
