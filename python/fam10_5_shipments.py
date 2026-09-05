"""Problem 12.2 -- Shipments in boxes: multi-product flow and counting of containers.

The quantities shipped are a multi-product flow between plants and customers; on
top of them there are the boxes, an integer count tied to the flow by the capacity
(technique 3.4: y >= ceil(sum / w)). The linear relaxation only sees the ratio
between units and capacity, and completely misses the fact that a box cannot be
split between two customers.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range


def scatole(n):
    """"1 box" or "3 boxes"."""
    return f"{int(n)} box" if int(n) == 1 else f"{int(n)} boxes"


# ---------- 1. MODEL AND INSTANCE ----------
intestazione("12.2 Shipments in boxes: minimising the number of boxes")
d2 = [[5, 0],       # units of product p ordered by customer c
      [2, 4]]
a2 = [[8, 6],       # units of product p available at plant s
      [5, 7]]
w2 = 10             # capacity of a box, in units of product
nk, nm, nn = len(d2), len(d2[0]), len(a2[0])   # products, customers, plants
D2 = sum(d2[p][c] for p in R(nk) for c in R(nm))
salva_dati(pd.DataFrame([{"product": p + 1, "customer": c + 1, "demand": d2[p][c]}
                         for p in R(nk) for c in R(nm)]), "spedizioni2_domanda")
salva_dati(pd.DataFrame([{"product": p + 1, "plant": s + 1, "availability": a2[p][s]}
                         for p in R(nk) for s in R(nn)]), "spedizioni2_disponibilita")
print(f"  Units to ship in total: {D2}; capacity of a box: {w2}.")


def modello_2(d, a, w):
    nk, nm, nn = len(d), len(d[0]), len(a[0])
    m = nuovo_modello("shipments")
    x = m.addVars(nk, nn, nm, vtype=GRB.INTEGER, name="x")   # units of p from s to c
    y = m.addVars(nn, nm, vtype=GRB.INTEGER, name="y")       # boxes from s to c
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((x.sum(p, "*", c) == d[p][c] for p in R(nk) for c in R(nm)), name="demand")
    m.addConstrs((x.sum(p, s, "*") <= a[p][s] for p in R(nk) for s in R(nn)),
                 name="availability")
    m.addConstrs((w * y[s, c] - x.sum("*", s, c) >= 0 for s in R(nn) for c in R(nm)),
                 name="capacity")
    return m, x, y


def duale_2(d, a, w):
    """max sum_pc d_pc alpha_pc + sum_ps a_ps beta_ps

    alpha free (demand with =), beta <= 0 (availability with <=), gamma >= 0 (link with
    the boxes). Columns:
      x_psc:  alpha_pc + beta_ps - gamma_sc <= 0
      y_sc:   w gamma_sc <= 1
    """
    nk, nm, nn = len(d), len(d[0]), len(a[0])
    dl = nuovo_modello("dual_shipments")
    alpha = dl.addVars(nk, nm, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(nk, nn, lb=-GRB.INFINITY, ub=0.0, name="beta")
    gamma = dl.addVars(nn, nm, name="gamma")
    dl.setObjective(gp.quicksum(d[p][c] * alpha[p, c] for p in R(nk) for c in R(nm))
                    + gp.quicksum(a[p][s] * beta[p, s] for p in R(nk) for s in R(nn)),
                    GRB.MAXIMIZE)
    dl.addConstrs((alpha[p, c] + beta[p, s] - gamma[s, c] <= 0
                   for p in R(nk) for s in R(nn) for c in R(nm)), name="rcx")
    dl.addConstrs((w * gamma[s, c] <= 1 for s in R(nn) for c in R(nm)), name="rcy")
    return dl


m2, x2, y2 = modello_2(d2, a2, w2)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# customer by customer: we try to serve them from a single plant, the one that has
# everything they need; if no plant is enough, the order is split.
def euristica(d, a, w):
    nk, nm, nn = len(d), len(d[0]), len(a[0])
    res = [[a[p][s] for s in R(nn)] for p in R(nk)]
    x = {(p, s, c): 0 for p in R(nk) for s in R(nn) for c in R(nm)}
    passi = []
    for c in R(nm):
        completi = [s for s in R(nn) if all(res[p][s] >= d[p][c] for p in R(nk))]
        if completi:
            s = completi[0]
            for p in R(nk):
                x[p, s, c] = d[p][c]
                res[p][s] -= d[p][c]
            passi.append(f"customer {c + 1}: plant {s + 1} has the whole order, we ship "
                         f"from there")
        else:
            for p in R(nk):
                manca = d[p][c]
                for s in R(nn):
                    preso = min(manca, res[p][s])
                    x[p, s, c] += preso
                    res[p][s] -= preso
                    manca -= preso
                assert manca == 0, "order cannot be satisfied"
            passi.append(f"customer {c + 1}: no plant is enough on its own, the order is "
                         f"split")
    y = {(s, c): -(-sum(x[p, s, c] for p in R(nk)) // w) for s in R(nn) for c in R(nm)}
    for s in R(nn):
        for c in R(nm):
            if y[s, c]:
                passi.append(f"plant {s + 1} -> customer {c + 1}: "
                             f"{sum(x[p, s, c] for p in R(nk))} units -> {scatole(y[s, c])}")
    return x, y, passi


x_eur, y_eur, passi = euristica(d2, a2, w2)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
ub2 = sum(y_eur.values())
sol_eur = ({f"x[{p},{s},{c}]": x_eur[p, s, c] for p in R(nk) for s in R(nn) for c in R(nm)}
           | {f"y[{s},{c}]": y_eur[s, c] for s in R(nn) for c in R(nm)})
assert ammissibile(m2, sol_eur), sol_eur
print(f"  Boxes used by the heuristic: {ub2}  ->  ub = {frazione(ub2)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl2 = duale_2(d2, a2, w2)
# recipe: beta = 0, gamma_sc = 1/w (the largest value allowed by w gamma <= 1) and
# alpha_pc = 1/w: every unit ordered takes 1/w of a box
mano = ({f"gamma[{s},{c}]": 1 / w2 for s in R(nn) for c in R(nm)}
        | {f"alpha[{p},{c}]": 1 / w2 for p in R(nk) for c in R(nm)})
lb_lp, viol = valuta(dl2, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: beta = 0, gamma_sc = alpha_pc = 1/{w2}. The dual constraints")
print(f"  become 1/{w2} + 0 - 1/{w2} = 0 <= 0 and {w2} * 1/{w2} = 1 <= 1: all verified.")
print(f"  lb = (units ordered) / {w2} = {D2} / {w2} = {frazione(lb_lp)}")
zlp2, zlp2r, _ = due_rilassamenti(m2, dl2)

# ---------- 4. A STRONGER INTEGER BOUND ----------
intestazione("12.2 Counting the boxes customer by customer")
clienti_attivi = [c for c in R(nm) if any(d2[p][c] > 0 for p in R(nk))]
print("  Every customer with at least one unit ordered receives at least one box, and boxes")
print(f"  are not shared between customers. The customers with orders are "
      f"{len(clienti_attivi)}:")
print(f"  lb = {len(clienti_attivi)}, against {frazione(lb_lp)} from the linear relaxation.")
print(f"  More precisely every customer c receives at least ceil(sum_p d_pc / {w2}) boxes:")
per_cliente = [-(-sum(d2[p][c] for p in R(nk)) // w2) for c in R(nm)]
for c in R(nm):
    print(f"    customer {c + 1}: {sum(d2[p][c] for p in R(nk))} units -> at least "
          f"{scatole(per_cliente[c])}")
lb2 = float(sum(per_cliente))
print(f"  Summing up: lb = {frazione(lb2)}.")
salva_dati(pd.DataFrame([{"argument": "dual of the LP relaxation", "bound": lb_lp},
                         {"argument": "boxes per customer", "bound": lb2}]),
           "spedizioni2_argomento")

# ---------- 5. OPTIMUM OF THE MILP ----------
z2 = risolvi(m2)
for s in R(nn):
    for c in R(nm):
        if y2[s, c].X > 0.5:
            carico = ", ".join(f"{int(x2[p, s, c].X)} of product {p + 1}" for p in R(nk)
                               if x2[p, s, c].X > 0.5)
            print(f"  Plant {s + 1} -> customer {c + 1}: {scatole(y2[s, c].X)} with {carico}")
riga = registra_bound("2 shipments", ub2, lb2, zlp2, zlp2r, z2)
salva_dati(pd.DataFrame([riga]), "spedizioni2_bound")
assert lb2 <= z2 <= ub2 + 1e-9

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: smaller boxes
m, x, y = modello_2(d2, a2, 4)
varianti["2a"] = variante("2a. The boxes hold 4 units instead of 10", m)
# 2b: different products cannot travel in the same box
m = nuovo_modello("shipments_separate")
x = m.addVars(nk, nn, nm, vtype=GRB.INTEGER, name="x")
y = m.addVars(nk, nn, nm, vtype=GRB.INTEGER, name="y")
m.setObjective(y.sum(), GRB.MINIMIZE)
m.addConstrs((x.sum(p, "*", c) == d2[p][c] for p in R(nk) for c in R(nm)), name="demand")
m.addConstrs((x.sum(p, s, "*") <= a2[p][s] for p in R(nk) for s in R(nn)), name="availability")
m.addConstrs((w2 * y[p, s, c] - x[p, s, c] >= 0 for p in R(nk) for s in R(nn) for c in R(nm)),
             name="capacity")
varianti["2b"] = variante("2b. Different products cannot travel in the same box", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "spedizioni2_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.4, 3.0))
for s in R(nn):
    for c in R(nm):
        n = int(y2[s, c].X)
        if n:
            ax.plot([0, 1], [nn - 1 - s, nm - 1 - c], color=TEAL, lw=1 + 2 * n)
            ax.annotate(scatole(n), (0.5, (nn - 1 - s + nm - 1 - c) / 2 + 0.06),
                        ha="center", fontsize=8, color=TEAL)
for s in R(nn):
    ax.plot(0, nn - 1 - s, marker="s", color=BLU, ms=14)
    ax.annotate(f"plant {s + 1}", (-0.06, nn - 1 - s), ha="right", va="center", fontsize=9)
for c in R(nm):
    ax.plot(1, nm - 1 - c, marker="o", color=ARANCIO, ms=14)
    ax.annotate(f"customer {c + 1}\n({sum(d2[p][c] for p in R(nk))} units)",
                (1.06, nm - 1 - c), ha="left", va="center", fontsize=9)
ax.set_xlim(-0.45, 1.5)
ax.set_ylim(-0.6, max(nn, nm) - 0.4)
ax.axis("off")
ax.set_title(f"12.2: optimal plan with {frazione(z2)} boxes")
salva_figura(fig, "cap10_spedizioni_ottimo")
print("Done.")
