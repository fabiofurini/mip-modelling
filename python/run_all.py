"""Runs all the course scripts in sequence.

Regenerates: data (data/*.csv), data for the pgfplots figures (notes/figure/dat/*.csv),
matplotlib previews (notes/figure/*.pdf), site images (docs/img/*.png)
and the chapter notebooks (notebooks/*.ipynb).

Usage:  python3 run_all.py
"""
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = [
    # Part I — modelling
    # Part II — the problems
    "fam07_1_assignment.py",
    "fam07_2_fixedcost.py",
    "fam07_3_selection.py",
    "fam07_4_parallel.py",
    "fam07_5_classessetup.py",
    "fam07_6_classesbonus.py",
    "fam07_7_tardiness.py",
    "fam07_8_summary.py",
]

base = Path(__file__).resolve().parent
inizio = time.time()
for s in SCRIPT:
    print(f"\n{'#' * 72}\n# {s}\n{'#' * 72}")
    esito = subprocess.run([sys.executable, str(base / s)], cwd=base)
    if esito.returncode != 0:
        print(f"ERROR in {s}: stopping.")
        sys.exit(1)
print(f"\n{'#' * 72}\n# make_notebooks.py\n{'#' * 72}")
esito = subprocess.run([sys.executable, str(base / "make_notebooks.py")], cwd=base)
if esito.returncode != 0:
    print("ERROR while generating the notebooks: stopping.")
    sys.exit(1)

print(f"\nAll scripts completed in {time.time() - inizio:.1f} s.")
