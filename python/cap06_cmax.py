"""Makespan on identical machines (chapter 3).

The second of the three problems the heuristics chapter takes up again: there the
natural order is compared with LPT on the very same four jobs. The objective is a
single variable, z, and it is the load constraints that give it meaning: this is
the min-max technique.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from esteso import salva_modello
from mip import frazione, nuovo_modello, risolvi
from stile import intestazione, salva_dati

R = range

intestazione("Makespan: the load of the busiest machine")
d_cmax = [3, 4, 5, 6]            # job durations
k_cmax = 2                       # identical machines


def modello_cmax(d, k):
    n = len(d)
    m = nuovo_modello("makespan")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    z = m.addVar(name="z")
    m.setObjective(z, GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="job")
    m.addConstrs((gp.quicksum(d[j] * x[j, mm] for j in R(n)) <= z for mm in R(k)),
                 name="load")
    return m, x, z


m_cmax, x_cmax, z_var = modello_cmax(d_cmax, k_cmax)
z_cmax = risolvi(m_cmax)
salva_modello(m_cmax, "cap06_cmax")
print(f"  Durations {d_cmax} on {k_cmax} identical machines.")
print(f"  The total load is {sum(d_cmax)}: divided by {k_cmax} it gives "
      f"{frazione(sum(d_cmax) / k_cmax)}, and the optimum is {frazione(z_cmax)}.")
for mm in R(k_cmax):
    lavori = [j + 1 for j in R(len(d_cmax)) if x_cmax[j, mm].X > 0.5]
    print(f"    machine {mm + 1}: jobs {lavori}, load "
          f"{sum(d_cmax[j - 1] for j in lavori)}")
assert z_cmax == sum(d_cmax) / k_cmax
salva_dati(pd.DataFrame([{"problem": "makespan", "z_milp": z_cmax}]), "cap06_cmax")
print("Done.")
