"""Travelling salesman with the MTZ formulation (chapter 3).

The third of the three problems the heuristics chapter takes up again: there the
tour is built with nearest neighbour, here the optimum is found.

The u variables order the cities along the tour: the constraint
u_i - u_j + n x_ij <= n - 1 is true when x_ij = 0 and forces u_j >= u_i + 1 when
x_ij = 1. Subtours that miss city 1 are thereby excluded, because they would need
a chain of ever-growing u that closes on itself.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from esteso import salva_modello
from mip import frazione, nuovo_modello, risolvi
from stile import intestazione, salva_dati

R = range

intestazione("Travelling salesman: the shortest tour")
D_tsp = [[0, 4, 5, 9],
         [4, 0, 9, 9],
         [5, 9, 0, 4],
         [9, 9, 4, 0]]
n_tsp = len(D_tsp)


def modello_tsp(D):
    n = len(D)
    m = nuovo_modello("tsp")
    x = m.addVars(((i, j) for i in R(n) for j in R(n) if i != j), vtype=GRB.BINARY, name="x")
    u = m.addVars(R(1, n), lb=1, ub=n - 1, name="u")
    m.setObjective(gp.quicksum(D[i][j] * x[i, j] for i, j in x), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(x[i, j] for j in R(n) if j != i) == 1 for i in R(n)), name="out")
    m.addConstrs((gp.quicksum(x[i, j] for i in R(n) if i != j) == 1 for j in R(n)), name="in")
    m.addConstrs((u[i] - u[j] + n * x[i, j] <= n - 1
                  for i in R(1, n) for j in R(1, n) if i != j), name="mtz")
    return m, x, u


m_tsp, x_tsp, u_tsp = modello_tsp(D_tsp)
salva_modello(m_tsp, "cap06_tsp")
z_tsp = risolvi(m_tsp)
seguente = {i: j for (i, j) in x_tsp if x_tsp[i, j].X > 0.5}
giro, citta = [0], 0
while seguente[citta] != 0:
    citta = seguente[citta]
    giro.append(citta)
print(f"  {n_tsp} cities, symmetric and metric distances.")
print("  Optimal tour: " + " -> ".join(str(c + 1) for c in giro + [0])
      + f", length {frazione(z_tsp)}.")
salva_dati(pd.DataFrame([{"problem": "TSP", "z_milp": z_tsp}]), "cap06_tsp")
print("Done.")
