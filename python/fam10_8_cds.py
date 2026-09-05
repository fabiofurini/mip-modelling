"""Problem 11.3 -- Songs on several CDs: minimising the difference between the
longest and the shortest.

Two auxiliary variables: y for the maximum (technique 3.5) and z for the minimum,
with objective y - z. As in 11.2 the linear relaxation is worth zero, and the
useful lower bound comes from a parity argument that settles optimality by itself.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("11.3 Songs on CDs: levelling the longest and the shortest CD")
d3 = [5, 6, 7, 3, 4, 10]     # duration of the songs, in minutes
w3 = [1, 1]                  # minimum number of songs per CD
n3, m3 = len(d3), len(w3)
D3 = sum(d3)
salva_dati(pd.DataFrame({"song": R(1, n3 + 1), "duration": d3}), "cd3_dati")
print(f"  Total duration of the collection: {D3} minutes on {m3} CDs.")


def modello_3(d, w):
    n, m = len(d), len(w)
    mod = nuovo_modello("cds")
    x = mod.addVars(n, m, vtype=GRB.BINARY, name="x")
    y = mod.addVar(name="y")     # duration of the longest CD
    z = mod.addVar(name="z")     # duration of the shortest CD
    mod.setObjective(y - z, GRB.MINIMIZE)
    mod.addConstrs((x.sum(i, "*") == 1 for i in R(n)), name="song")
    mod.addConstrs((x.sum("*", j) >= w[j] for j in R(m)), name="minimum")
    mod.addConstrs((y - gp.quicksum(d[i] * x[i, j] for i in R(n)) >= 0 for j in R(m)),
                   name="maximum")
    mod.addConstrs((gp.quicksum(d[i] * x[i, j] for i in R(n)) - z >= 0 for j in R(m)),
                   name="minimum_duration")
    return mod, x, y, z


def duale_3(d, w):
    """max sum_i alpha_i + sum_j w_j beta_j

    alpha_i free (equality constraint), beta_j >= 0 (>= w_j), gamma_j >= 0 (column of
    y: sum_j gamma_j = 1) and delta_j >= 0 (column of z: sum_j delta_j = 1). Column of
    x_ij: alpha_i + beta_j - d_i gamma_j + d_i delta_j <= 0.
    """
    n, m = len(d), len(w)
    dl = nuovo_modello("dual_cds")
    alpha = dl.addVars(n, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(m, name="beta")
    gamma = dl.addVars(m, name="gamma")
    delta = dl.addVars(m, name="delta")
    dl.setObjective(alpha.sum() + gp.quicksum(w[j] * beta[j] for j in R(m)), GRB.MAXIMIZE)
    dl.addConstr(gamma.sum() == 1, name="rcy")
    dl.addConstr(delta.sum() == 1, name="rcz")
    dl.addConstrs((alpha[i] + beta[j] - d[i] * gamma[j] + d[i] * delta[j] <= 0
                   for i in R(n) for j in R(m)), name="rcx")
    return dl


m3mod, x3, y3, z3v = modello_3(d3, w3)

# ---------- 2. TWO HEURISTICS COMPARED (UPPER BOUND) ----------
def riempi(d, m, ordine, etichetta):
    """The songs are scanned in the given order and each one goes on the shortest CD."""
    carichi = [0] * m
    dove = {}
    passi = []
    for i in ordine:
        j = min(R(m), key=lambda j: (carichi[j], j))
        dove[i] = j
        carichi[j] += d[i]
        passi.append(f"song {i + 1} ({d[i]} min) on CD {j + 1}; durations {carichi}")
    diff = max(carichi) - min(carichi)
    print(f"  {etichetta}")
    for k, riga in enumerate(passi, 1):
        print(f"    Step {k}. {riga}")
    print(f"    final durations {carichi}, difference {diff}")
    return dove, carichi, diff


ordine_lpt = sorted(R(n3), key=lambda i: (-d3[i], i))
dove, carichi, ub3 = riempi(d3, m3, ordine_lpt,
                            "LPT heuristic: songs in decreasing order of duration.")
dove_nat, carichi_nat, diff_nat = riempi(d3, m3, list(R(n3)),
                                         "Naive heuristic: songs in the given order.")
sol_eur = ({f"x[{i},{dove[i]}]": 1 for i in R(n3)}
           | {"y": max(carichi), "z": min(carichi)})
assert ammissibile(m3mod, sol_eur), sol_eur
print(f"  The decreasing order gives {frazione(ub3)}, the natural order {frazione(diff_nat)}:")
print("  the same insertion rule changes a lot depending on the order of the songs.")
print(f"  The better of the two is kept:  ub = {frazione(ub3)}")
assert diff_nat >= ub3

# ---------- 3. THE LP RELAXATION SAYS NOTHING ----------
dl3 = duale_3(d3, w3)
mano = {f"gamma[{j}]": 1 / m3 for j in R(m3)} | {f"delta[{j}]": 1 / m3 for j in R(m3)}
lb_lp, viol = valuta(dl3, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: gamma_j = delta_j = 1/{m3}, alpha = beta = 0 -> value "
      f"{frazione(lb_lp)}.")
zlp3, zlp3r, _ = due_rilassamenti(m3mod, dl3)
meta = ({f"x[{i},{j}]": 1 / m3 for i in R(n3) for j in R(m3)}
        | {"y": D3 / m3, "z": D3 / m3})
val_meta, viol_meta = valuta(m3mod, meta)
assert viol_meta <= 1e-9 and abs(val_meta) <= 1e-9
print(f"  And indeed z(LP) = {frazione(zlp3)}: putting 1/{m3} of every song on every CD, all")
print(f"  the CDs last {frazione(D3 / m3)} minutes and the difference is zero. A song, though,")
print("  cannot be split.")
assert abs(zlp3) <= 1e-9

# ---------- 4. THE PARITY BOUND ----------
intestazione("11.3 A parity argument that settles the problem")
print(f"  The durations are integers and there are {m3} CDs: the two durations add up to")
print(f"  {D3}, which is {'odd' if D3 % 2 else 'even'}. Two integers adding up to an odd")
print("  number cannot be equal, and their difference is itself odd: so it is at least 1.")
lb3 = 1 if D3 % 2 else 0
assert m3 == 2, "the parity argument holds as written for two CDs only"
print(f"  lb = {frazione(lb3)}, and the LPT heuristic reaches {frazione(ub3)}: the two bounds")
print("  coincide and the heuristic solution is already optimal, with no need for the solver.")
salva_dati(pd.DataFrame([{"argument": "parity of the total duration", "bound": lb3},
                         {"argument": "dual of the LP relaxation", "bound": lb_lp}]),
           "cd3_argomento")

# ---------- 5. OPTIMUM OF THE MILP ----------
z3 = risolvi(m3mod)
carichi_ott = [sum(d3[i] * x3[i, j].X for i in R(n3)) for j in R(m3)]
for j in R(m3):
    brani = [i + 1 for i in R(n3) if x3[i, j].X > 0.5]
    print(f"  CD {j + 1}: songs {brani}, duration {frazione(carichi_ott[j])} minutes")
riga = registra_bound("3 cds", ub3, lb3, zlp3, zlp3r, z3)
salva_dati(pd.DataFrame([riga]), "cd3_bound")
assert lb3 <= z3 <= ub3 + 1e-9 and abs(z3 - lb3) <= 1e-9

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 3a: CD 1 is a smaller medium and cannot exceed 15 minutes
m, x, y, z = modello_3(d3, w3)
m.addConstr(gp.quicksum(d3[i] * x[i, 0] for i in R(n3)) <= 15, name="capacity_cd1")
varianti["3a"] = variante("3a. CD 1 cannot exceed 15 minutes", m)
print(f"       CD 2 must then hold at least {D3} - 15 = {D3 - 15} minutes and the difference")
print(f"       cannot go below {D3 - 2 * 15}: the bound is read off the data.")
# 3b: three CDs instead of two
m, x, y, z = modello_3(d3, [1, 1, 1])
varianti["3b"] = variante("3b. The collection is spread over three CDs", m)
print(f"       with three CDs the total duration {D3} is no longer divisible into equal")
print("       parts: the parity argument has to be redone and no longer proves optimality.")
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "cd3_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 2.9))
for k, (nome, car, colore) in enumerate([("naive heuristic", carichi_nat, ARANCIO),
                                         ("LPT heuristic", carichi, TEAL),
                                         ("optimum", carichi_ott, BLU)]):
    for j in R(m3):
        ax.barh(k + (j - 0.5) * 0.34, car[j], 0.3, color=colore)
        ax.annotate(f"CD {j + 1}: {frazione(car[j])}", (0.6, k + (j - 0.5) * 0.34),
                    va="center", fontsize=8, color="white")
    ax.annotate(f"difference {frazione(max(car) - min(car))}", (max(car) + 0.6, k),
                va="center", fontsize=8)
ax.set_yticks(R(3))
ax.set_yticklabels(["naive", "LPT", "optimum"])
ax.set_xlim(0, max(carichi_nat) + 9)
ax.set_xlabel("duration of the CD (minutes)")
ax.set_title(f"11.3: the difference drops from {frazione(diff_nat)} to {frazione(z3)}")
ax.invert_yaxis()
salva_figura(fig, "cap10_cd_ottimo")
print("Done.")
