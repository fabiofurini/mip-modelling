"""Chapter 2 -- Logic and binary variables: from CNF to linear constraints.

Turns the implications of the chapter's five exercises into conjunctive normal
form and then into linear constraints, and *proves by enumeration* that the
translation is exact: for every binary assignment, the formula is true if and
only if the linear system is satisfied. It ends with a project-selection model
that uses those constraints.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from booleane import (AND, IMP, NOT, OR, V, cnf, equivalenti, scrivi, testo_cnf,
                      valuta, variabili, verifica, vincolo)
from mip import ammissibile, frazione, nuovo_modello, rilassamento, risolvi, stampa_soluzione
from stile import BLU, CICLO, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura

R = range
x = {p: V(f"x{p}") for p in R(1, 11)}

# ---------- 1. THE PROPERTIES OF BOOLEAN ALGEBRA ----------
intestazione("1. De Morgan, distributivity, absorption: checked by enumeration")
a, b, c = V("xa"), V("xb"), V("xc")
PROPRIETA = [
    ("distributivity (C)", AND(a, OR(b, c)), OR(AND(a, b), AND(a, c))),
    ("distributivity (D)", OR(a, AND(b, c)), AND(OR(a, b), OR(a, c))),
    ("De Morgan (A)", NOT(OR(a, b)), AND(NOT(a), NOT(b))),
    ("De Morgan (B)", NOT(AND(a, b)), OR(NOT(a), NOT(b))),
    ("absorption (E)", OR(a, AND(a, b)), a),
    ("absorption (F)", AND(a, OR(a, b)), a),
    ("double negation", NOT(NOT(a)), a),
]
for nome, sinistra, destra in PROPRIETA:
    assert equivalenti(sinistra, destra), nome
    print(f"  {nome:22s} checked on all {2 ** len(variabili(sinistra) | variabili(destra))} assignments")

# ---------- 2. THE VALID SPLITS AND THE INVALID ONE ----------
intestazione("2. Splitting an implication: when it is allowed and when it is not")
scissioni = [
    ("disjunctive antecedent", IMP(OR(a, b), c), AND(IMP(a, c), IMP(b, c)), True),
    ("conjunctive consequent", IMP(a, AND(b, c)), AND(IMP(a, b), IMP(a, c)), True),
    ("conjunctive antecedent", IMP(AND(a, b), c), AND(IMP(a, c), IMP(b, c)), False),
]
for nome, sinistra, destra, attesa in scissioni:
    ok = equivalenti(sinistra, destra)
    assert ok == attesa, nome
    print(f"  {nome:24s} split {'valid' if ok else 'NOT valid'}")
contro = {"xa": 1, "xb": 0, "xc": 0}
assert valuta(IMP(AND(a, b), c), contro) and not valuta(AND(IMP(a, c), IMP(b, c)), contro)
print("  counterexample to the third: xa = 1, xb = 0, xc = 0 makes the original")
print("  implication true (false antecedent) but the conjunction of the splits false.")

# ---------- 3. THE FIVE EXERCISES: CNF AND LINEAR CONSTRAINTS ----------
intestazione("3. Exercises 2.1-2.5: conjunctive normal form and linear constraints")
ESERCIZI = {
    "2.1": [("if 2 is chosen, then 3 is chosen", IMP(x[2], x[3])),
            ("if 2 is chosen, then 4 is not chosen", IMP(x[2], NOT(x[4]))),
            ("if 1 and 6 are chosen, then 7 is chosen", IMP(AND(x[1], x[6]), x[7])),
            ("if 1 or 6 is chosen, then 8 is chosen", IMP(OR(x[1], x[6]), x[8])),
            ("if 2 and 3 are chosen, then 9 is not chosen", IMP(AND(x[2], x[3]), NOT(x[9]))),
            ("if 2 or 3 is chosen, then 10 is not chosen", IMP(OR(x[2], x[3]), NOT(x[10])))],
    "2.2": [("if 3 is not chosen, then 2 is chosen", IMP(NOT(x[3]), x[2])),
            ("if 4 is not chosen, then 2 is not chosen", IMP(NOT(x[4]), NOT(x[2]))),
            ("if 7 is chosen, then 1 and 6 are chosen", IMP(x[7], AND(x[1], x[6]))),
            ("if 8 is chosen, then 1 or 6 is chosen", IMP(x[8], OR(x[1], x[6]))),
            ("if 9 is not chosen, then 2 and 3 are chosen", IMP(NOT(x[9]), AND(x[2], x[3]))),
            ("if 10 is not chosen, then 2 or 3 is chosen", IMP(NOT(x[10]), OR(x[2], x[3])))],
    "2.3": [("if 7 or 3 is chosen, then 1 and 2 are chosen", IMP(OR(x[7], x[3]), AND(x[1], x[2]))),
            ("if 1, 6 and 7 are chosen, then 8 is chosen", IMP(AND(x[1], x[6], x[7]), x[8])),
            ("if 5 and 2 are chosen and 4 is not, then 3 is not chosen",
             IMP(AND(x[5], x[2], NOT(x[4])), NOT(x[3]))),
            ("if 6 and (1 or 4) are chosen, then 2 and (5 or 7) are chosen",
             IMP(AND(OR(x[1], x[4]), x[6]), AND(x[2], OR(x[5], x[7])))),
            ("if (2 or 5) is chosen and 8 is not, then 3 is chosen or 6 is not",
             IMP(AND(OR(x[2], x[5]), NOT(x[8])), OR(x[3], NOT(x[6])))),
            ("if (1 or 4) and (2 or 5) and not 8, then 3 and (not 6 or 7)",
             IMP(AND(OR(x[1], x[4]), OR(x[2], x[5]), NOT(x[8])),
                 AND(x[3], OR(NOT(x[6]), x[7]))))],
    "2.4": [("if 4 is chosen, at least two of 1, 2, 3",
             IMP(x[4], OR(AND(x[1], x[2]), AND(x[1], x[3]), AND(x[2], x[3])))),
            ("if at least two of 6, 7, 8, then 5",
             IMP(OR(AND(x[6], x[7]), AND(x[6], x[8]), AND(x[7], x[8])), x[5])),
            ("if 4 is not chosen, at least two of 1, 2, 3, 9",
             IMP(NOT(x[4]), OR(AND(x[1], x[2]), AND(x[1], x[3]), AND(x[1], x[9]),
                               AND(x[2], x[3]), AND(x[2], x[9]), AND(x[3], x[9])))),
            ("if 8 is chosen, then (1 and 6) or (1 and 7) or (2 and 6)",
             IMP(x[8], OR(AND(x[1], x[6]), AND(x[1], x[7]), AND(x[2], x[6])))),
            ("if at least two of 1, 3, 5, then 9 is not chosen",
             IMP(OR(AND(x[1], x[3]), AND(x[1], x[5]), AND(x[3], x[5])), NOT(x[9]))),
            ("if (1 and 2) or (3 and 4), then 5",
             IMP(OR(AND(x[1], x[2]), AND(x[3], x[4])), x[5]))],
    "2.5": [("if 1 or 2 is chosen, then 3 is chosen", IMP(OR(x[1], x[2]), x[3])),
            ("if 4 is chosen, then 5 and 6 are chosen", IMP(x[4], AND(x[5], x[6]))),
            ("if 1 or 2 is chosen, then 3 and 4 are chosen",
             IMP(OR(x[1], x[2]), AND(x[3], x[4]))),
            ("if 1 and 2 are chosen, then 3 is chosen", IMP(AND(x[1], x[2]), x[3])),
            ("if 5 or 6 is chosen, then 7 is not chosen", IMP(OR(x[5], x[6]), NOT(x[7]))),
            ("if 8 is not chosen or 9 is not chosen, then 10 is chosen",
             IMP(OR(NOT(x[8]), NOT(x[9])), x[10]))],
}
righe = []
for es, voci in ESERCIZI.items():
    print(f"\nExercise {es}")
    for i, (testo, formula) in enumerate(voci, 1):
        clausole = cnf(formula)
        vincoli = [vincolo(c) for c in clausole]
        totali, vere = verifica(formula, vincoli)
        print(f"  {es}.{i}  {testo}")
        print(f"        CNF ({len(clausole)} clauses) -> "
              + " ;  ".join(scrivi(v, mat=False) for v in vincoli))
        print(f"        equivalence checked on {totali} assignments "
              f"({vere} make the formula true)")
        righe.append({"exercise": es, "item": i, "description": testo,
                      "clauses": len(clausole),
                      "constraints": " ; ".join(scrivi(v, mat=False) for v in vincoli),
                      "assignments": totali, "true": vere})
salva_dati(pd.DataFrame(righe), "cap02_implicazioni")

# ---------- 4. CLAUSES OR COUNTING: TWO FORMULATIONS OF THE SAME SET ----------
intestazione("4. 'At least two of 1, 2, 3 if 4 is chosen': clauses versus counting")


def confronta(clausole=True):
    """max x1+x2+x3+3 x4 with the implication x4 => at least two of 1,2,3."""
    m = nuovo_modello("at_least_two")
    v = m.addVars(R(1, 5), vtype=GRB.BINARY, name="x")
    m.setObjective(v[1] + v[2] + v[3] + 3 * v[4], GRB.MAXIMIZE)
    m.addConstr(v[1] + v[2] + v[3] + 2 * v[4] <= 3, name="budget")
    if clausole:                       # three clauses: x_i + x_j >= x4 for every pair
        for i, j in [(1, 2), (1, 3), (2, 3)]:
            m.addConstr(v[i] + v[j] - v[4] >= 0, name=f"pair{i}{j}")
    else:                              # counted form: x1 + x2 + x3 >= 2 x4
        m.addConstr(v[1] + v[2] + v[3] - 2 * v[4] >= 0, name="counting")
    return m, v


for nome, cl in [("three clauses", True), ("one counted constraint", False)]:
    m, v = confronta(cl)
    z = risolvi(m)
    zr, sol, _ = rilassamento(m, rafforzato=True)
    print(f"  {nome:24s} z(MILP) = {frazione(z)}   z(LP+) = {frazione(zr)}   "
          + "  ".join(f"x{p}={frazione(sol[f'x[{p}]'])}" for p in R(1, 5)))
from itertools import product as _p
for valori in _p((0, 1), repeat=4):
    a4 = dict(zip(R(1, 5), valori))
    cl3 = all(a4[i] + a4[j] - a4[4] >= 0 for i, j in [(1, 2), (1, 3), (2, 3)])
    cnt = a4[1] + a4[2] + a4[3] - 2 * a4[4] >= 0
    assert cl3 == cnt, a4
print("  The two formulations have the same 16 binary solutions (checked by")
print("  enumeration) but different relaxations: the counted constraint is stronger.")

# ---------- 5. A SELECTION MODEL WITH THE LOGICAL CONSTRAINTS ----------
intestazione("5. Project selection subject to the implications of exercise 2.1")
r = {1: 9, 2: 7, 3: 4, 4: 8, 5: 3, 6: 6, 7: 2, 8: 5, 9: 7, 10: 6}   # revenues
b = {1: 4, 2: 3, 3: 2, 4: 4, 5: 2, 6: 3, 7: 1, 8: 3, 9: 4, 10: 3}   # costs
budget = 14
salva_dati(pd.DataFrame({"project": list(r), "revenue": list(r.values()),
                         "cost": list(b.values())}), "cap02_progetti")


def modello_selezione(con_logica=True):
    m = nuovo_modello("project_selection")
    xv = m.addVars(R(1, 11), vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(r[p] * xv[p] for p in R(1, 11)), GRB.MAXIMIZE)
    m.addConstr(gp.quicksum(b[p] * xv[p] for p in R(1, 11)) <= budget, name="budget")
    if con_logica:
        for i, (_, formula) in enumerate(ESERCIZI["2.1"], 1):
            for j, cl in enumerate(cnf(formula), 1):
                coef, verso, rhs = vincolo(cl)
                lhs = gp.quicksum(k * xv[int(n[1:])] for n, k in coef.items())
                m.addConstr(lhs <= rhs if verso == "<=" else lhs >= rhs, name=f"logic{i}_{j}")
    return m, xv


m_libero, _ = modello_selezione(con_logica=False)
z_libero = risolvi(m_libero)
m_log, x_log = modello_selezione(con_logica=True)
z_log = risolvi(m_log)
zlp_log, _, _ = rilassamento(m_log, rafforzato=True)
scelti = sorted(p for p in R(1, 11) if x_log[p].X > 0.5)
print(f"Without the logical constraints:  z = {frazione(z_libero)}")
print(f"With the logical constraints:     z = {frazione(z_log)}   projects chosen: {scelti}")
print(f"                                  cost {sum(b[p] for p in scelti)} out of a budget of {budget}")
print(f"LP+ relaxation of the model with the logical constraints: {frazione(zlp_log)}")
for _, formula in ESERCIZI["2.1"]:
    assert valuta(formula, {f"x{p}": int(p in scelti) for p in R(1, 11)})
print("All six implications are satisfied by the optimal solution.")
salva_dati(pd.DataFrame([{"model": "without logical constraints", "z": z_libero, "z_lp": None},
                         {"model": "with logical constraints", "z": z_log, "z_lp": zlp_log}]),
           "cap02_selezione")

# ---------- 6. FIGURE: HOW MANY ASSIGNMENTS SURVIVE EACH IMPLICATION ----------
sopravvivono = []
etichette = []
for i, (testo, formula) in enumerate(ESERCIZI["2.1"], 1):
    totali, vere = verifica(formula, nomi=[f"x{p}" for p in R(1, 11)])
    sopravvivono.append(vere)
    etichette.append(f"2.1.{i}")
tutte = [dict(zip([f"x{p}" for p in R(1, 11)], v)) for v in _p((0, 1), repeat=10)]
cumulate = []
vive = tutte
for testo, formula in ESERCIZI["2.1"]:
    vive = [ass for ass in vive if valuta(formula, ass)]
    cumulate.append(len(vive))
print(f"Assignments of the 10 binaries: {len(tutte)}; after the six implications: {cumulate[-1]}")
fig, ax = plt.subplots(figsize=(7.2, 3.6))
ax.bar(etichette, sopravvivono, color=TEAL, label="single implication")
ax.plot(etichette, cumulate, "o-", color=ROSSO, label="all implications imposed together")
ax.axhline(len(tutte), color=BLU, lw=1, ls="--")
ax.annotate(f"$2^{{10}} = {len(tutte)}$ assignments", (0, len(tutte)),
            textcoords="offset points", xytext=(4, -14), fontsize=9, color=BLU)
ax.set_ylabel("feasible assignments")
ax.set_title("Exercise 2.1: how many of the $2^{10}$ assignments survive")
ax.legend(loc="lower left", fontsize=9)
salva_figura(fig, "cap02_implicazioni")
salva_dati(pd.DataFrame({"implication": etichette, "single": sopravvivono,
                         "cumulative": cumulate}), "cap02_ammissibili")
print("Done.")
