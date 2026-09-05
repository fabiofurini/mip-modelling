"""Problem 9.3 -- Vehicles: minimum lot and a bonus for variety.

Three techniques together: the semicontinuous variable of the minimum lot (3.3),
the count of the active types (3.11) and a bonus paid "if and only if" at least
two types are produced (3.10). The bonus is collected only if the count reaches
two: the missing direction follows from optimality, because the bonus is positive.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("9.3 Vehicles: minimum lot per type and a bonus for at least two types")
a3 = [[2, 3, 5],        # steel (tons) per unit of the three types
      [30, 25, 40]]     # labour hours per unit
b3 = [100, 1200]        # steel and hours available
p3 = [200, 250, 300]    # profit per unit
q3 = [10, 10, 10]       # minimum quantity if the type is produced
r3 = 500                # bonus if at least two types are produced
n3, m3 = 3, 2
# the smallest valid big-M per type: how many units the resources allow at most
M3 = [min(b3[i] // a3[i][j] for i in R(m3)) for j in R(n3)]
salva_dati(pd.DataFrame({"type": R(1, n3 + 1), "steel": a3[0], "hours": a3[1],
                         "profit": p3, "minimum": q3, "M": M3}), "veic3_dati")
print(f"  Resources: {b3[0]} t of steel, {b3[1]} hours. Big-M per type (from the data "
      f"alone): {M3}")


def modello_3(a, b, p, q, r):
    n, m = len(p), len(b)
    M = [min(b[i] // a[i][j] for i in R(m)) for j in R(n)]
    mm = nuovo_modello("vehicles")
    x = mm.addVars(n, vtype=GRB.INTEGER, name="x")     # units produced
    y = mm.addVars(n, vtype=GRB.BINARY, name="y")      # type activated
    z = mm.addVar(vtype=GRB.BINARY, name="z")          # bonus for variety
    mm.setObjective(gp.quicksum(p[j] * x[j] for j in R(n)) + r * z, GRB.MAXIMIZE)
    mm.addConstrs((gp.quicksum(a[i][j] * x[j] for j in R(n)) <= b[i] for i in R(m)),
                  name="resource")
    mm.addConstrs((x[j] - q[j] * y[j] >= 0 for j in R(n)), name="minimum_lot")
    mm.addConstrs((x[j] - M[j] * y[j] <= 0 for j in R(n)), name="activate")
    mm.addConstr(-gp.quicksum(y[j] for j in R(n)) + 2 * z <= 0, name="bonus")
    return mm, x, y, z


def duale_3(a, b, p, q, r):
    """min sum_i b_i pi_i;  sum_i a_ij pi_i - alpha_j + beta_j >= p_j;
    q_j alpha_j - M_j beta_j + gamma >= 0;  -2 gamma >= r;  pi, alpha, beta >= 0, gamma <= 0.
    (written with the signs of the conversion table for a maximisation primal)"""
    n, m = len(p), len(b)
    M = [min(b[i] // a[i][j] for i in R(m)) for j in R(n)]
    dl = nuovo_modello("dual_vehicles")
    pi = dl.addVars(m, name="pi")                                   # resources (<= in a max)
    alpha = dl.addVars(n, lb=-GRB.INFINITY, ub=0.0, name="alpha")   # minimum lot (>= in a max)
    beta = dl.addVars(n, name="beta")                               # activation (<=)
    gamma = dl.addVar(name="gamma")                                 # bonus (<=)
    dl.setObjective(gp.quicksum(b[i] * pi[i] for i in R(m)), GRB.MINIMIZE)
    dl.addConstrs((gp.quicksum(a[i][j] * pi[i] for i in R(m)) + alpha[j] + beta[j] >= p[j]
                   for j in R(n)), name="rc_x")
    dl.addConstrs((-q[j] * alpha[j] - M[j] * beta[j] - gamma >= 0 for j in R(n)), name="rc_y")
    dl.addConstr(2 * gamma >= r, name="rc_z")
    return dl


m3m, x3, y3, z3 = modello_3(a3, b3, p3, q3, r3)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND: IT IS A MAXIMISATION) ----------
# constructive heuristic: two types are activated (to collect the bonus) starting from the highest
# profit per unit of the scarcest resource, then one fills up with the best type
def euristica(a, b, p, q, r):
    n, m = len(p), len(b)
    # profit / consumption ratio of the tightest resource
    ordine = sorted(R(n), key=lambda j: -p[j] / max(a[i][j] / b[i] for i in R(m)))
    x = [0] * n
    res = list(b)
    attivi = []
    for j in ordine:                       # first the minimum lot of the two best types
        if len(attivi) < 2 and all(res[i] >= a[i][j] * q[j] for i in R(m)):
            x[j] = q[j]
            for i in R(m):
                res[i] -= a[i][j] * q[j]
            attivi.append(j)
    for j in ordine:                       # then fill up with the most profitable type
        if x[j] == 0:
            continue
        extra = min(res[i] // a[i][j] for i in R(m))
        x[j] += extra
        for i in R(m):
            res[i] -= a[i][j] * extra
    return x, attivi, res


x_eur, attivi, res = euristica(a3, b3, p3, q3, r3)
lb3 = sum(p3[j] * x_eur[j] for j in R(n3)) + (r3 if len(attivi) >= 2 else 0)
sol_eur = {f"x[{j}]": x_eur[j] for j in R(n3)} \
    | {f"y[{j}]": 1 if x_eur[j] > 0 else 0 for j in R(n3)} | {"z": 1 if len(attivi) >= 2 else 0}
assert ammissibile(m3m, sol_eur)
print(f"  Heuristic: types {[j + 1 for j in attivi]} are activated at their minimum lot, then")
print(f"  one fills up with the most profitable one; production {x_eur}, resources left {res}")
print(f"  lb = {sum(p3[j] * x_eur[j] for j in R(n3))} + {r3} of bonus = {frazione(lb3)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
dl3 = duale_3(a3, b3, p3, q3, r3)
# recipe: gamma = r/2 (the smallest value allowed by 2 gamma >= r), beta = 0, and
# lambda_j = gamma / q_j (every activated type "carries" its share of the bonus); then
# a single resource is priced so that it covers all types, and the better bound is kept
gamma = r3 / 2
lam = [gamma / q3[j] for j in R(n3)]
bound = {}
for i in R(m3):
    prezzo = max((p3[j] + lam[j]) / a3[i][j] for j in R(n3))
    bound[i] = b3[i] * prezzo
critica = min(bound, key=bound.get)
prezzo = max((p3[j] + lam[j]) / a3[critica][j] for j in R(n3))
mano = {"gamma": gamma} | {f"pi[{i}]": 0.0 for i in R(m3)} \
    | {f"alpha[{j}]": -lam[j] for j in R(n3)} | {f"beta[{j}]": 0.0 for j in R(n3)}
mano[f"pi[{critica}]"] = prezzo
ub3, viol = valuta(dl3, mano)
assert viol <= 1e-9, (viol, mano)
print(f"  Hand-built dual: gamma = r/2 = {frazione(gamma)} (the smallest value satisfying")
print(f"  2 gamma >= r), beta = 0 and lambda_j = gamma / q_j = "
      + ", ".join(frazione(v) for v in lam))
print("  so every activated type carries its share of the bonus. Then a single resource is")
print("  priced at max_j (p_j + lambda_j) / a_ij, and the tighter bound is kept:")
for i in R(m3):
    print(f"    resource {i + 1}: price "
          f"{frazione(max((p3[j] + lam[j]) / a3[i][j] for j in R(n3)))}"
          f"  ->  b_i * price = {frazione(bound[i])}")
print(f"  The smallest is resource {critica + 1}:  ub = {frazione(ub3)}")
zlp3, zlp3r, _ = due_rilassamenti(m3m, dl3)

# ---------- 4. OPTIMUM OF THE MILP ----------
z3v = risolvi(m3m)
print("  Optimal solution: production " + ", ".join(str(round(x3[j].X)) for j in R(n3))
      + f"; active types {[j + 1 for j in R(n3) if y3[j].X > 0.5]}; bonus collected: "
      + ("yes" if z3.X > 0.5 else "no"))
print("  Resources used: " + ", ".join(
    f"{frazione(sum(a3[i][j] * round(x3[j].X) for j in R(n3)))} out of {b3[i]}" for i in R(m3)))
riga = registra_bound("3 vehicles", ub3, lb3, zlp3, zlp3r, z3v, senso="max")
salva_dati(pd.DataFrame([riga]), "veic3_bound")
assert lb3 <= z3v <= zlp3 + 1e-6 <= ub3 + 1e-6

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 3a: the bonus requires at least three different types
m, x, y, z = modello_3(a3, b3, p3, q3, r3)
m.update()
m.remove([c for c in m.getConstrs() if c.ConstrName == "bonus"])
m.addConstr(-gp.quicksum(y[j] for j in R(n3)) + 3 * z <= 0, name="bonus3")
varianti["3a"] = variante("3a. The bonus is paid only with at least three types", m)
# 3b: the bonus is zero -- what happens to the "if and only if" link?
m, x, y, z = modello_3(a3, b3, p3, q3, 0)
zz = risolvi(m)
print(f"  {'3b. The bonus is 0: z is no longer a faithful indicator':70s} z = {frazione(zz)}")
print(f"      active types {[j + 1 for j in R(n3) if y[j].X > 0.5]}, but z = {round(z.X)}: with")
print("      a zero bonus the optimum has no reason to raise z, and the constraint alone")
print("      does not force it. Making it a faithful indicator needs the other direction too.")
varianti["3b"] = zz
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "veic3_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
tipi = list(R(1, n3 + 1))
colori = [TEAL if y3[j].X > 0.5 else "#F4F6F7" for j in R(n3)]
ax.bar(tipi, [x3[j].X for j in R(n3)], color=colori, edgecolor="#7F8C8D", width=0.55)
for j in R(n3):
    ax.plot([j + 0.72, j + 1.28], [q3[j], q3[j]], color=ROSSO, lw=2)
ax.plot([], [], color=ROSSO, lw=2, label="minimum lot $q_j$")
for j in R(n3):
    ax.annotate(str(round(x3[j].X)), (j + 1, x3[j].X), ha="center", va="bottom", fontsize=9)
ax.set_xticks(tipi)
ax.set_xticklabels([f"type {j}" for j in tipi])
ax.set_ylabel("units produced")
ax.set_title(f"9.3: optimal plan (z = {frazione(z3v)}, bonus collected)")
ax.legend(fontsize=8)
salva_figura(fig, "cap09_veicoli_ottimo")
print("Done.")
