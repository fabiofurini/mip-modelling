"""Bin packing: how many containers are enough (chapter 3).

The first of the three problems the heuristics chapter takes up again: there
next-fit, first-fit and best-fit are built by hand, here the model that says what
the optimum is. The capacity is written as an activation: until the container
opens it can receive nothing.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from esteso import salva_modello
from mip import frazione, nuovo_modello, risolvi
from stile import intestazione, salva_dati

R = range

intestazione("Bin packing: the smallest number of containers")
w_bpp = [5, 4, 3, 3]             # weight of the items
c_bpp = 7                        # capacity of one container
n_bpp = len(w_bpp)


def modello_bpp(w, c, k):
    n = len(w)
    m = nuovo_modello("bin_packing")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, vtype=GRB.BINARY, name="y")
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="item")
    m.addConstrs((gp.quicksum(w[j] * x[j, b] for j in R(n)) <= c * y[b] for b in R(k)),
                 name="capacity")
    return m, x, y


# with one container per item one finds how many are really needed; the model that
# gets printed then uses only those, because the others would stay empty
m_largo, _, _ = modello_bpp(w_bpp, c_bpp, n_bpp)
z_bpp = risolvi(m_largo)
minimo_teorico = -(-sum(w_bpp) // c_bpp)        # rounding up
print(f"  Weights {w_bpp}, capacity {c_bpp}.")
print(f"  The total weight is {sum(w_bpp)}: no solution uses fewer than "
      f"{sum(w_bpp)}/{c_bpp} = {minimo_teorico} containers, and the optimum uses {int(z_bpp)}.")
assert z_bpp == minimo_teorico
m_bpp, x_bpp, y_bpp = modello_bpp(w_bpp, c_bpp, int(z_bpp))
risolvi(m_bpp)
salva_modello(m_bpp, "cap06_bpp")
print("  The relaxation buys fractions of a container and drops to "
      f"{frazione(sum(w_bpp) / c_bpp)}: it does not know a container opens whole.")
salva_dati(pd.DataFrame([{"problem": "bin packing", "z_milp": z_bpp}]), "cap06_bpp")
print("Done.")
