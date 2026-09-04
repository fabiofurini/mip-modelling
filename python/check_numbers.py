"""Check of the numbers quoted in the notes and on the website.

Every value written in the texts (ub, lb, z(LP), z(MILP), variant optima) is
an assert here against the CSVs produced by the scripts. Usage: python3 check_numbers.py
(after run_all.py). Stops with an error at the first mismatch.
"""
from fractions import Fraction
from pathlib import Path

import pandas as pd

DATI = Path(__file__).resolve().parent.parent / "data"


def F(s):
    return Fraction(s)


def uguale(a, b):
    return abs(float(a) - float(b)) <= 1e-6


# ----------------------------------------------------------------------
# Chapter 7 — Assignment and scheduling
# ----------------------------------------------------------------------
b = pd.read_csv(DATI / "sched_bound.csv").set_index("problem")
attesi = {   # problem: (heuristic, hand dual, pure z(LP), strengthened z(LP+), z(MILP))
    "1 assignment":  (11, 10, F("53/5"), F("53/5"), 11),
    "2 fixed cost":   (12, F("25/4"), F("25/4"), F("1273/200"), 12),
    "3 selection":     (20, 34, 34, F("680/21"), 25),
    "4 parallel":     (19, 5, F("520/49"), F("520/49"), 15),
    "5 classes setup":  (9, 100, F("425/13"), F("329/13"), 21),
    "6 classes bonus": (32, 150, F("5280/113"), F("5280/113"), 42),
    "7 tardiness":       (12, 2, 2, 2, 11),
}
massimo = {"3 selection", "5 classes setup", "6 classes bonus"}
for nome, (eur, duale, zlp, zlpr, zmilp) in attesi.items():
    r = b.loc[nome]
    ub, lb = (duale, eur) if nome in massimo else (eur, duale)
    assert uguale(r.ub, ub), (nome, "ub", r.ub, ub)
    assert uguale(r.lb, lb), (nome, "lb", r.lb, lb)
    assert uguale(r.z_lp, zlp), (nome, "z_lp", r.z_lp, zlp)
    assert uguale(r.z_lp_rafforzato, zlpr), (nome, "z_lp_rafforzato", r.z_lp_rafforzato, zlpr)
    assert uguale(r.z_milp, zmilp), (nome, "z_milp", r.z_milp, zmilp)
    # the sandwich lb <= z(LP) <= z(MILP) <= ub (min) or reversed (max)
    if nome in massimo:
        assert float(r.lb) <= float(r.z_milp) <= float(r.z_lp) <= float(r.ub) + 1e-9, nome
    else:
        assert float(r.lb) <= float(r.z_lp) <= float(r.z_milp) <= float(r.ub) + 1e-9, nome
print("ch. 7: the seven problems — bounds, relaxations and optima match the texts")

v = pd.read_csv(DATI / "sched_varianti.csv").set_index("variant")["z"]
attese = {"1a": 12, "1b": 18, "2a": 12, "2b": 12, "3a": 20, "3b": 20, "4a": 10, "4b": 23,
          "5a": 17, "5b": 18, "6a": 40, "6b": 42, "7a": 12, "7b": 5}
for k, z in attese.items():
    assert uguale(v[k], z), (k, v[k], z)
print("ch. 7: the fourteen additional questions — optima match the texts")

# ----------------------------------------------------------------------
# Chapter 8 — Location and coverage
# ----------------------------------------------------------------------
b8 = pd.read_csv(DATI / "loc_bound.csv").set_index("problem")
attesi8 = {   # problem: (heuristic, hand dual, pure z(LP), strengthened z(LP+), z(MILP))
    "1 capacitated location": (439, F("1581/5"), F("1581/5"), 317, 365),
    "2 p-median":             (18, 13, 15, 15, 15),
    "3 coverage":             (25, F("225/2"), F("41925/646"), F("125/2"), 45),
    "4 hub":                  (20, F("15/2"), F("25/2"), F("1015/78"), 19),
}
massimo8 = {"3 coverage"}
for nome, (eur, duale, zlp, zlpr, zmilp) in attesi8.items():
    r = b8.loc[nome]
    ub, lb = (duale, eur) if nome in massimo8 else (eur, duale)
    assert uguale(r.ub, ub), (nome, "ub", r.ub, ub)
    assert uguale(r.lb, lb), (nome, "lb", r.lb, lb)
    assert uguale(r.z_lp, zlp), (nome, "z_lp", r.z_lp, zlp)
    assert uguale(r.z_lp_rafforzato, zlpr), (nome, "z_lp_rafforzato", r.z_lp_rafforzato, zlpr)
    assert uguale(r.z_milp, zmilp), (nome, "z_milp", r.z_milp, zmilp)
    if nome in massimo8:
        assert float(r.lb) <= float(r.z_milp) <= float(r.z_lp) <= float(r.ub) + 1e-9, nome
    else:
        assert float(r.lb) <= float(r.z_lp) <= float(r.z_milp) <= float(r.ub) + 1e-9, nome
print("ch. 8: the four problems — bounds, relaxations and optima match the texts")

v8 = pd.read_csv(DATI / "loc_varianti.csv").set_index("variant")["z"]
attese8 = {"1a": 365, "1b": 365, "2a": 15, "2b": 16, "3a": 45, "3b": 45, "4a": 19, "4b": 19}
for k, z in attese8.items():
    assert uguale(v8[k], z), (k, v8[k], z)
print("ch. 8: the eight additional questions — optima match the texts")
print("All checks passed.")
