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
# Part I — the modelling chapters
# ----------------------------------------------------------------------
c1 = pd.read_csv(DATI / "cap01_bound.csv").iloc[0]
assert uguale(c1.z_lp, F("3/2")) and uguale(c1.z_lp_rafforzato, F("3/2")), c1
assert uguale(c1.z_milp, 1), c1
br = pd.read_csv(DATI / "cap01_branch.csv").set_index("node")
assert uguale(br.loc["root"].z_lp, F("3/2")) and uguale(br.loc["x1 <= 0"].z_lp, 1)
assert uguale(br.loc["x1 >= 1"].z_lp, F("3/2")) and uguale(br.loc["x1 >= 1, x2 <= 0"].z_lp, 1)
assert pd.isna(br.loc["x1 >= 1, x2 >= 1"].z_lp)
print("ch. 1: relaxations, optimum and branch-and-bound trace")

imp = pd.read_csv(DATI / "cap02_implicazioni.csv")
assert len(imp) == 30, len(imp)
assert (imp["true"] < imp.assignments).all()      # no implication is a tautology
sel = pd.read_csv(DATI / "cap02_selezione.csv").set_index("model")["z"]
assert uguale(sel["without logical constraints"], 30) and uguale(sel["with logical constraints"], 28)
amm = pd.read_csv(DATI / "cap02_ammissibili.csv")
assert int(amm.cumulative.iloc[-1]) == 234, amm.cumulative.iloc[-1]
print("ch. 2: 30 implications checked by enumeration, selection and counts")

tec = pd.read_csv(DATI / "cap03_tecniche.csv", dtype={"section": str}).set_index("section")
attese3 = {"3.1": 15, "3.2": 44, "3.3": 49, "3.4": 4, "3.5": 4, "3.6": 11, "3.7": 1,
           "3.8": 3, "3.9": 9, "3.10": 15, "3.11": 57, "3.12": 7, "3.13": 6, "3.14": 33}
for k, z in attese3.items():
    assert uguale(tec.loc[k].z_milp, z), (k, tec.loc[k].z_milp, z)
assert uguale(tec.loc["3.1"].z_lp_1, F("38/3")) and uguale(tec.loc["3.1"].z_lp_2, 15)
assert uguale(tec.loc["3.14"].z_lp_1, F("117/4"))
print("ch. 3: the fourteen techniques — optima and relaxations compared")

cop = pd.read_csv(DATI / "cap04_copertura.csv").iloc[0]
assert uguale(cop.ub, 10) and uguale(cop.lb, 7) and uguale(cop.z_lp, F("15/2")) and uguale(cop.z_milp, 10)
zai = pd.read_csv(DATI / "cap04_zaino.csv").iloc[0]
assert uguale(zai.lb, 16) and uguale(zai.ub, 18) and uguale(zai.z_lp, 18)
assert uguale(zai.z_lp_rafforzato, F("71/4")) and uguale(zai.z_milp, 17)
tag = pd.read_csv(DATI / "cap04_tagli.csv").iloc[0]
assert uguale(tag.z_lp_without_cuts, F("71/4")) and uguale(tag.z_lp_with_cuts, F("69/4"))
sol4 = pd.read_csv(DATI / "cap04_solver.csv").set_index("configuration")
assert int(sol4.loc["default settings"].nodes) == 0
assert int(sol4.loc["no presolve, cuts or heuristics"].nodes) > 0
pr = pd.read_csv(DATI / "cap04_prezzi.csv").set_index("capacity")
assert uguale(pr.loc[9].z_milp, 17) and uguale(pr.loc[10].z_milp, 17)   # the jump is zero
print("ch. 4: covering, knapsack, cover cuts, solver nodes and marginal prices")

eur = pd.read_csv(DATI / "cap05_euristiche.csv").set_index("heuristic")
attese5 = {"5.1 next-fit": (14, 11), "5.1 first-fit": (14, 11),
           "5.1 best-fit (minimum cost)": (11, 11), "5.2 LPT (makespan)": (11, 9),
           "5.3 covering constructive heuristic": (10, 10), "5.4 constructive heuristic by ratio p/w": (16, 17),
           "5.5 lot sizing (least unit cost)": (200, 170)}
for k, (v, z) in attese5.items():
    assert uguale(eur.loc[k].heuristic_value, v), (k, eur.loc[k].heuristic_value, v)
    assert uguale(eur.loc[k].z_milp, z), (k, eur.loc[k].z_milp, z)
print("ch. 5: the six heuristics — values and gaps match the texts")

st = pd.read_csv(DATI / "cap06_stati.csv").set_index("case")
assert int(st.loc["optimal"].status) == 2 and int(st.loc["infeasible"].status) == 3
assert int(st.loc["time limit, no solution"].sol_count) == 0
assert uguale(st.loc["first solution"].obj_val, 12) and uguale(st.loc["first solution"].obj_bound, 10)
pro = pd.read_csv(DATI / "cap06_protocollo.csv").iloc[0]
assert uguale(pro.ub, 11) and uguale(pro.lb, 10) and uguale(pro.z_lp, F("53/5")) and uguale(pro.z_milp, 11)
print("ch. 6: solver statuses, tolerances and the full protocol")

# ----------------------------------------------------------------------
# Chapter 7 — Assignment and scheduling
# ----------------------------------------------------------------------
b = pd.concat([pd.read_csv(DATI / f"sched{k}_bound.csv") for k in range(1, 8)],
          ignore_index=True).set_index("problem")
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

v = pd.concat([pd.read_csv(DATI / f"sched{k}_varianti.csv") for k in range(1, 8)],
          ignore_index=True).set_index("variant")["z"]
attese = {"1a": 12, "1b": 18, "2a": 12, "2b": 12, "3a": 20, "3b": 20, "4a": 10, "4b": 23,
          "5a": 17, "5b": 18, "6a": 40, "6b": 42, "7a": 12, "7b": 5}
for k, z in attese.items():
    assert uguale(v[k], z), (k, v[k], z)
print("ch. 7: the fourteen additional questions — optima match the texts")

# ----------------------------------------------------------------------
# Chapter 8 — Location and coverage
# ----------------------------------------------------------------------
b8 = pd.concat([pd.read_csv(DATI / f"loc{k}_bound.csv") for k in (1, 2, 3)]
          + [pd.read_csv(DATI / "hub4_bound.csv")], ignore_index=True).set_index("problem")
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

v8 = pd.concat([pd.read_csv(DATI / f"loc{k}_varianti.csv") for k in (1, 2, 3)]
          + [pd.read_csv(DATI / "hub4_varianti.csv")], ignore_index=True).set_index("variant")["z"]
attese8 = {"1a": 365, "1b": 365, "2a": 15, "2b": 16, "3a": 45, "3b": 45,
           "4a": 19, "4a_without_capacity": 10, "4a_with_capacity": 19, "4b": 19}
for k, z in attese8.items():
    assert uguale(v8[k], z), (k, v8[k], z)
print("ch. 8: the eight additional questions — optima match the texts")
# ----------------------------------------------------------------------
# Numerical models of families 7 and 8
# ----------------------------------------------------------------------
attesi_num = {   # NUM: (ub, lb, z(LP), z(LP+), z(MILP), senso)
    "02": (13, 7, 9, 9, 9, "min"),
    "03": (99, 93, 95, 95, 95, "min"),
    "06": (3, 3, 3, 3, 3, "min"),
    "08": (18, 18, 18, 18, 18, "max"),
    "10": (F("23000/3"), 2000, 5200, 5200, 2500, "max"),
    "11": (9, 9, 9, 9, 9, "min"),
}
for k, (ub, lb, zlp, zlpr, zmilp, senso) in attesi_num.items():
    r = pd.read_csv(DATI / f"ex{k}_bound.csv").iloc[0]
    assert uguale(r.ub, ub), (k, "ub", r.ub, ub)
    assert uguale(r.lb, lb), (k, "lb", r.lb, lb)
    assert uguale(r.z_lp, zlp), (k, "z_lp", r.z_lp, zlp)
    assert uguale(r.z_lp_rafforzato, zlpr), (k, "z_lp_rafforzato", r.z_lp_rafforzato, zlpr)
    assert uguale(r.z_milp, zmilp), (k, "z_milp", r.z_milp, zmilp)
    if senso == "max":
        assert float(r.lb) <= float(r.z_milp) <= float(r.z_lp) + 1e-6 <= float(r.ub) + 1e-6, k
    else:
        assert float(r.lb) <= float(r.z_lp) <= float(r.z_milp) <= float(r.ub) + 1e-9, k
# EX 11: i due obiettivi descrivono la stessa soluzione con numeri diversi
ob = pd.read_csv(DATI / "ex11_obiettivi.csv").set_index("objective")["z"]
assert uguale(ob["min-max"], 9) and uguale(ob["minimum range"], 0)
assert uguale(ob["min-max"], 18 / 2 + ob["minimum range"] / 2)
print("numerical models EX 2, 5, 7, 9, 10, 15 — bounds and optima match the texts")
# ----------------------------------------------------------------------
# Chapters 9-12: the twelve problems of the four new families
# ----------------------------------------------------------------------
# (file, ub, lb, z(LP), z(LP+), z(MILP), sense)
attesi_fam = [
    ("prod1", 420, 270, F("3890/11"), F("3890/11"), 390, "min"),
    ("prod2", 18200, 13500, 15960, 15960, 16660, "min"),
    ("veic3", 11250, 9200, F("20625/2"), 9750, 9700, "max"),
    ("premi1", 8, 3, 3, 3, 5, "min"),
    ("dieta2", F("39/4"), 9, F("46/5"), F("48/5"), F("48/5"), "min"),
    ("asta3", 23, 21, 22, 22, 22, "max"),
    ("campi1", 23, 15, 23, 23, 23, "max"),
    ("antitrust2", 6, 2, 0, 0, 4, "min-cert"),
    ("cd3", 1, 1, 0, 0, 1, "min-cert"),
    ("scaffali4", 15, 12, 8, 8, 15, "min-cert"),
    ("luci1", 3121, 2140, 2140, 2141, 2141, "min"),
    ("spedizioni2", 2, 2, F("11/10"), F("11/10"), 2, "min-cert"),
]
for nome, ub, lb, zlp, zlpr, zmilp, senso in attesi_fam:
    r = pd.read_csv(DATI / f"{nome}_bound.csv").iloc[0]
    assert uguale(r.ub, ub), (nome, "ub", r.ub, ub)
    assert uguale(r.lb, lb), (nome, "lb", r.lb, lb)
    assert uguale(r.z_lp, zlp), (nome, "z_lp", r.z_lp, zlp)
    assert uguale(r.z_lp_rafforzato, zlpr), (nome, "z_lp+", r.z_lp_rafforzato, zlpr)
    assert uguale(r.z_milp, zmilp), (nome, "z_milp", r.z_milp, zmilp)
    if senso == "max":
        assert float(r.lb) <= float(r.z_milp) <= float(r.z_lp) + 1e-6 <= float(r.ub) + 1e-6, nome
    elif senso == "min":
        assert float(r.lb) <= float(r.z_lp) <= float(r.z_milp) <= float(r.ub) + 1e-9, nome
    else:   # lb is a combinatorial bound, not the dual value: it may exceed z(LP)
        assert float(r.lb) <= float(r.z_milp) <= float(r.ub) + 1e-9, nome
        assert float(r.z_lp) <= float(r.z_milp) + 1e-9, nome
print("ch. 9-10: the twelve problems — bounds, relaxations and optima match the texts")

attese_var = {
    "prod1": {"1a": 470, "1b": 390},
    "prod2": {"2a": 19560, "2b": 16660},
    "veic3": {"3a": 9200, "3b": 9200},
    "premi1": {"1a": 10, "1b": 13},
    "dieta2": {"2a": 12, "2b": F("31/3")},
    "asta3": {"3a": 21, "3b": 12},
    "campi1": {"1a": 24, "1b": 15},
    "antitrust2": {"2a": 6, "2b": 8},
    "cd3": {"3a": 5, "3b": 2},
    "scaffali4": {"4a": 15, "4b": 12},
    "luci1": {"1a": 2239, "1b": 2143},
    "spedizioni2": {"2a": 3, "2b": 3},
}
for nome, attese in attese_var.items():
    v = pd.read_csv(DATI / f"{nome}_varianti.csv").set_index("variant")["z"]
    for k, z in attese.items():
        assert uguale(v[k], z), (nome, k, v[k], z)
print("ch. 9-10: the twenty-four additional questions — optima match the texts")

# ----------------------------------------------------------------------
# The nine new numerical models
# ----------------------------------------------------------------------
attesi_num2 = {
    "01": (160, 110, 160, 140, 120, "max"),
    "04": (825000, 761250, 773500, 773500, 774180, "min"),
    "05": (F("280000/11"), 25200, F("280000/11"), F("229000/9"), 25250, "max"),
    "07": (5, 4, 5, 5, 5, "max"),
    "09": (8, 5, 8, 8, 8, "max"),
    "12": (24000, 24000, 24000, 24000, 24000, "max"),
    "13": (F("50/3"), 16, F("50/3"), F("50/3"), 16, "max"),
    "14": (8410, 6300, F("115970/17"), F("115970/17"), 7060, "min"),
    "15": (0, 0, 0, 0, 0, "min"),
}
for k, (ub, lb, zlp, zlpr, zmilp, senso) in attesi_num2.items():
    r = pd.read_csv(DATI / f"ex{k}_bound.csv").iloc[0]
    assert uguale(r.ub, ub), (k, "ub", r.ub, ub)
    assert uguale(r.lb, lb), (k, "lb", r.lb, lb)
    assert uguale(r.z_lp, zlp), (k, "z_lp", r.z_lp, zlp)
    assert uguale(r.z_lp_rafforzato, zlpr), (k, "z_lp+", r.z_lp_rafforzato, zlpr)
    assert uguale(r.z_milp, zmilp), (k, "z_milp", r.z_milp, zmilp)
    if senso == "max":
        assert float(r.lb) <= float(r.z_milp) + 1e-6, k
        assert float(r.z_milp) <= float(r.z_lp) + 1e-6, k
        assert float(r.z_lp) <= float(r.ub) + 1e-6, k
    else:
        assert float(r.lb) <= float(r.z_lp) + 1e-6, k
        assert float(r.z_lp) <= float(r.z_milp) + 1e-6, k
        assert float(r.z_milp) <= float(r.ub) + 1e-6, k
# EX 15: without the second direction of the link the variety constraint is empty
vv = pd.read_csv(DATI / "ex15_varieta.csv")
assert (vv.instruments_wrong_model < 2).any(), vv
print("numerical models EX 1, 3, 4, 6, 8, 11, 12, 13, 14 — bounds and optima match")
print("All checks passed.")
