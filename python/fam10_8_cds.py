"""Problem 10.8 -- Songs on several CDs: minimising the difference between the
longest and the shortest.

Two auxiliary variables: y for the maximum (technique 6.5) and z for the minimum,
with objective y - z. As in 11.2 the linear relaxation is worth zero, and the
useful lower bound comes from a parity argument that settles optimality by itself.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi, valuta)
from stile import ARANCIO, BLU, TEAL, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.8 Songs on CDs: levelling the longest and the shortest CD")
d3 = [5, 6, 7, 3, 4, 10]     # duration of the songs, in minutes
w3 = [1, 1]                  # minimum number of songs per CD
n3, m3 = len(d3), len(w3)
D3 = sum(d3)
salva_dati(pd.DataFrame({"song": R(1, n3 + 1), "duration": d3}), "fam10_8_dati")
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
salva_modello(m3mod, "fam10_8_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp3, zlp3r, _ = rilassamenti(m3mod)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
dl3 = duale_3(d3, w3)
salva_modello(dl3, "fam10_8_duale")
mano = {f"gamma[{j}]": 1 / m3 for j in R(m3)} | {f"delta[{j}]": 1 / m3 for j in R(m3)}
lb_lp, viol = valuta(dl3, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: gamma_j = delta_j = 1/{m3}, alpha = beta = 0 -> value "
      f"{frazione(lb_lp)}.")
dualita_forte(dl3, zlp3)

meta = ({f"x[{i},{j}]": 1 / m3 for i in R(n3) for j in R(m3)}
        | {"y": D3 / m3, "z": D3 / m3})
val_meta, viol_meta = valuta(m3mod, meta)
assert viol_meta <= 1e-9 and abs(val_meta) <= 1e-9
print(f"  And indeed z(LP) = {frazione(zlp3)}: putting 1/{m3} of every song on every CD, all")
print(f"  the CDs last {frazione(D3 / m3)} minutes and the difference is zero. A song, though,")
print("  cannot be split.")
assert abs(zlp3) <= 1e-9

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
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

# ---------- 5. THE PARITY BOUND ----------
intestazione("10.8 A parity argument that settles the problem")
print(f"  The durations are integers and there are {m3} CDs: the two durations add up to")
print(f"  {D3}, which is {'odd' if D3 % 2 else 'even'}. Two integers adding up to an odd")
print("  number cannot be equal, and their difference is itself odd: so it is at least 1.")
lb3 = 1 if D3 % 2 else 0
assert m3 == 2, "the parity argument holds as written for two CDs only"
print(f"  lb = {frazione(lb3)}, and the LPT heuristic reaches {frazione(ub3)}: the two bounds")
print("  coincide and the heuristic solution is already optimal, with no need for the solver.")
salva_dati(pd.DataFrame([{"argument": "parity of the total duration", "bound": lb3},
                         {"argument": "dual of the LP relaxation", "bound": lb_lp}]),
           "fam10_8_argomento")

# ---------- 6. OPTIMUM OF THE MILP ----------
z3 = risolvi(m3mod)
carichi_ott = [sum(d3[i] * x3[i, j].X for i in R(n3)) for j in R(m3)]
for j in R(m3):
    brani = [i + 1 for i in R(n3) if x3[i, j].X > 0.5]
    print(f"  CD {j + 1}: songs {brani}, duration {frazione(carichi_ott[j])} minutes")
riga = registra_bound("3 cds", ub3, lb3, zlp3, zlp3r, z3)
salva_dati(pd.DataFrame([riga]), "fam10_8_bound")
assert lb3 <= z3 <= ub3 + 1e-9 and abs(z3 - lb3) <= 1e-9

# ---------- 7. ADDITIONAL MODELLING QUESTIONS ----------
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
           "fam10_8_varianti")

# ---------- 8. THE SANDWICH ON THE VARIANT 3b ----------
intestazione("10.8b The sandwich on the variant: the collection on three CDs")
M3B = 3
w3b = [1] * M3B

# The number of CDs changes, not the structure: model, dual, heuristic and recipe
# are the same with m = 3.
m3b, x3b, y3b, z3b = modello_3(d3, w3b)
salva_modello(m3b, "fam10_8b_primale")
dl3b = duale_3(d3, w3b)
salva_modello(dl3b, "fam10_8b_duale")

# -- feasible heuristic: LPT on the three CDs --
ordine_3b = sorted(R(n3), key=lambda i: (-d3[i], i))
dove_3b, carichi_3b, ub3b = riempi(d3, M3B, ordine_3b,
                                   "LPT heuristic on the three CDs: tracks in decreasing order.")
sol_3b = ({f"x[{i},{dove_3b[i]}]": 1 for i in R(n3)}
          | {"y": max(carichi_3b), "z": min(carichi_3b)})
assert ammissibile(m3b, sol_3b), "the heuristic solution of the variant must be feasible"
print(f"  ub = {frazione(ub3b)}")

# -- dual certificate: the same recipe, on three CDs --
mano_3b = ({f"gamma[{j}]": 1 / M3B for j in R(M3B)}
           | {f"delta[{j}]": 1 / M3B for j in R(M3B)})
lb3b, viol_3b = valuta(dl3b, mano_3b)
assert viol_3b <= 1e-9, viol_3b
print(f"Dual solution by hand: gamma_j = delta_j = 1/{M3B}, as in the base problem: the two")
print("  columns of y and z ask the gammas and the deltas to sum to one, and spreading them")
print("  evenly is the choice that favours no CD. alpha = beta = 0.")
print(f"  ->  lb = {frazione(lb3b)}")
zlp3b, zlp3br, _ = due_rilassamenti(m3b, dl3b)

# -- combinatorial bound: the parity argument of the base problem, generalised --
resto_3b = D3 % M3B
comb_3b = float(1 if resto_3b else 0)
verso_3b = "is not" if resto_3b else "is"
print(f"  The parity argument generalises: the durations are integers summing to {D3}, and")
print(f"  {D3} {verso_3b} a multiple of {M3B}, so they cannot all be equal and the difference")
print(f"  between the longest and the shortest is at least {frazione(comb_3b)}.")
lb3b_usato = max(lb3b, comb_3b)
z3b_val = risolvi(m3b)
riga_3b = registra_bound("3b collection on three CDs", ub3b, lb3b_usato, zlp3b, zlp3br, z3b_val,
                         certificato="parity of the durations on three CDs")
salva_dati(pd.DataFrame([riga_3b]), "fam10_8b_bound")
assert lb3b_usato <= z3b_val <= ub3b + 1e-9

# ---------- 9. FIGURE ----------
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
ax.set_title(f"10.8: the difference drops from {frazione(diff_nat)} to {frazione(z3)}")
ax.invert_yaxis()
salva_figura(fig, "cap10_cd_ottimo")
print("Done.")
