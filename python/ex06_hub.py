"""EX 6 -- Hub-and-spoke: the minimum number of hubs covering eight cities (family 8).

A pure set covering with all costs equal to 1: the number of hubs is minimised.
The dual is the fractional packing of the customers, and the dual constructive heuristic on the
cities finds here a bound that coincides with the optimum.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from euristiche import euristica_copertura
from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 6. Hub-and-spoke: the fewest hubs within 1000 miles of every city")
CITTA = ["Atlanta", "Chicago", "Denver", "Houston", "Los Angeles", "New York",
         "San Francisco", "Seattle"]
copre = [[0, 1, 3, 5], [0, 1, 5], [2, 4], [0, 3], [2, 4, 6], [0, 1, 5], [4, 6, 7], [6, 7]]
n = len(CITTA)
salva_dati(pd.DataFrame([{"city": CITTA[i], "covered_by": ", ".join(CITTA[j] for j in copre[i])}
                         for i in R(n)]), "ex06_copertura")


def modello(copre):
    n = len(copre)
    m = nuovo_modello("hub_spoke")
    y = m.addVars(n, vtype=GRB.BINARY, name="y")
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(y[j] for j in copre[i]) >= 1 for i in R(n)), name="cover")
    return m, y


def duale(copre):
    """max sum_i u_i;  sum_{i : j covers i} u_i <= 1 for every j;  u >= 0."""
    n = len(copre)
    d = nuovo_modello("dual_hub_spoke")
    u = d.addVars(n, name="u")
    d.setObjective(u.sum(), GRB.MAXIMIZE)
    d.addConstrs((gp.quicksum(u[i] for i in R(n) if j in copre[i]) <= 1 for j in R(n)),
                 name="rc")
    return d


m, y = modello(copre)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
e = euristica_copertura([1] * n, copre)
e.traccia.stampa()
ub = e.valore
scelti = [j for j in R(n) if e.y[j]]
assert ammissibile(m, {f"y[{j}]": e.y[j] for j in R(n)})
print("  Heuristic solution: hubs in " + ", ".join(CITTA[j] for j in scelti)
      + f"   ub = {frazione(ub)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
d = duale(copre)
residuo = [1.0] * n
mano = {}
for i in R(n):
    incremento = min(residuo[j] for j in copre[i])
    mano[f"u[{i}]"] = incremento
    for j in copre[i]:
        residuo[j] -= incremento
    print(f"  City {i + 1} ({CITTA[i]}): residuals of the hubs covering it "
          + ", ".join(f"{CITTA[j]} = {frazione(residuo[j] + incremento)}" for j in copre[i])
          + f"; the smallest is {frazione(incremento)}, so u_{i + 1} = {frazione(incremento)}")
lb, viol = valuta(d, mano)
assert viol <= 1e-9, viol
print(f"  Dual by hand (constructive heuristic on the cities): lb = {frazione(lb)}")
zlp, zlpr, pi = due_rilassamenti(m, d)

# ---------- 4. MILP OPTIMUM AND BOUND TABLE ----------
z = risolvi(m)
ott = [j for j in R(n) if y[j].X > 0.5]
print(f"  Optimal solution: {len(ott)} hubs in " + ", ".join(CITTA[j] for j in ott))
for i in R(n):
    assert [CITTA[j] for j in copre[i] if j in ott], CITTA[i]
print("  Every city is covered by at least one chosen hub: checked for all eight.")
riga = registra_bound("EX 6 hub-and-spoke", ub, lb, zlp, zlpr, z)
salva_dati(pd.DataFrame([riga]), "ex06_bound")
assert lb <= zlp <= z <= ub + 1e-9
if abs(lb - z) < 1e-9:
    print("  Here the hand-built dual coincides with the integer optimum: the bound closes")
    print("  the problem without the solver (three pairwise 'distant' cities are enough to")
    print("  prove that two hubs cannot suffice).")

# ---------- 5. FIGURE ----------
fig, ax = plt.subplots(figsize=(7.2, 3.4))
altezza = [len([i for i in R(n) if j in copre[i]]) for j in R(n)]
colori = ["#0E7490" if j in ott else "#F4F6F7" for j in R(n)]
ax.bar(R(n), altezza, color=colori, edgecolor="#7F8C8D", lw=0.8)
for j in R(n):
    ax.annotate(str(altezza[j]), (j, altezza[j]), ha="center", va="bottom", fontsize=9,
                color="#16324A")
ax.set_xticks(R(n))
ax.set_xticklabels([c.replace(" ", "\n") for c in CITTA], fontsize=7.5)
ax.set_ylabel("cities covered if chosen as hub")
ax.set_title(f"EX 6: the {len(ott)} chosen hubs (teal) and how many cities each site covers")
salva_figura(fig, "ex06_ottimo")
print("Done.")
