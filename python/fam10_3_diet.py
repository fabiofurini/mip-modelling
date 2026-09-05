"""Problem 10.2 -- Diet with a count of the foods and a minimum lot.

A classic diet (continuous quantities, two-sided nutritional constraints) with
three integer techniques on top: activation (3.2), minimum lot (3.3) and counting
of the types (3.11). Without the minimum lot the count "at least t different
foods" would be empty: indicators would switch on with zero quantity.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 rilassamento, risolvi, valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.2 Diet: minimum cost with at least t different foods and a minimum lot")
CIBI = ["milk", "rice", "bread", "potatoes"]
NUTRIENTI = ["iron", "calcium"]
w2 = [2, 3, 1, 4]                      # cost per kilo
g2 = [[10, 5], [20, 10], [5, 15], [25, 5]]   # grams of nutrient j per kilo of food i
a2 = [60, 40]                          # monthly minimum of each nutrient
b2 = [200, 150]                        # monthly maximum
c2 = [1, 1, 1, 1]                      # minimum quantity if the food is chosen
d2 = [8, 8, 8, 8]                      # maximum quantity
t2 = 3                                 # at least three different foods
s2, r2 = len(w2), len(a2)
salva_dati(pd.DataFrame({"food": CIBI, "cost": w2,
                         "iron": [g[0] for g in g2], "calcium": [g[1] for g in g2],
                         "min": c2, "max": d2}), "dieta2_dati")


def modello_2(w, g, a, b, c, d, t):
    s, r = len(w), len(a)
    m = nuovo_modello("diet")
    x = m.addVars(s, name="x")                        # kilos of each food
    y = m.addVars(s, vtype=GRB.BINARY, name="y")      # food present in the diet
    m.setObjective(gp.quicksum(w[i] * x[i] for i in R(s)), GRB.MINIMIZE)
    m.addConstrs((gp.quicksum(g[i][j] * x[i] for i in R(s)) >= a[j] for j in R(r)),
                 name="minimum")
    m.addConstrs((gp.quicksum(g[i][j] * x[i] for i in R(s)) <= b[j] for j in R(r)),
                 name="maximum")
    m.addConstrs((x[i] - c[i] * y[i] >= 0 for i in R(s)), name="minimum_lot")
    m.addConstrs((x[i] - d[i] * y[i] <= 0 for i in R(s)), name="activate")
    m.addConstr(gp.quicksum(y[i] for i in R(s)) >= t, name="variety")
    return m, x, y


def duale_2(w, g, a, b, c, d, t):
    """max sum_j a_j alpha_j - sum_j b_j beta_j + t tau
       s.t.  sum_j g_ij (alpha_j - beta_j) + lam_i - mu_i <= w_i        (column x_i)
             -c_i lam_i + d_i mu_i + tau <= 0                            (column y_i)
             alpha, beta, lam, mu, tau >= 0."""
    s, r = len(w), len(a)
    dl = nuovo_modello("dual_diet")
    alpha = dl.addVars(r, name="alpha")
    beta = dl.addVars(r, name="beta")
    lam = dl.addVars(s, name="lam")
    mu = dl.addVars(s, name="mu")
    tau = dl.addVar(name="tau")
    dl.setObjective(gp.quicksum(a[j] * alpha[j] for j in R(r))
                    - gp.quicksum(b[j] * beta[j] for j in R(r)) + t * tau, GRB.MAXIMIZE)
    dl.addConstrs((gp.quicksum(g[i][j] * (alpha[j] - beta[j]) for j in R(r))
                   + lam[i] - mu[i] <= w[i] for i in R(s)), name="rc_x")
    dl.addConstrs((-c[i] * lam[i] + d[i] * mu[i] + tau <= 0 for i in R(s)), name="rc_y")
    return dl


m2, x2, y2 = modello_2(w2, g2, a2, b2, c2, d2, t2)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# constructive heuristic: start from the minimum lot of the t cheapest foods, then cover the residual
# requirement with the food that has the lowest cost per gram
def euristica(w, g, a, b, c, d, t):
    s, r = len(w), len(a)
    x = [0.0] * s
    scelti = sorted(R(s), key=lambda i: (w[i], i))[:t]
    for i in scelti:
        x[i] = c[i]
    passi = [f"the {t} cheapest foods are switched on at their minimum lot: "
             + ", ".join(f"{CIBI[i]} ({c[i]} kg)" for i in scelti)]
    for j in R(r):
        while sum(g[i][j] * x[i] for i in R(s)) < a[j] - 1e-9:
            # the food, already switched on, with the lowest cost per gram of nutrient j
            cand = [i for i in scelti if g[i][j] > 0 and x[i] < d[i] - 1e-9]
            if not cand:
                return None, passi + [f"no active food can cover the {NUTRIENTI[j]}"]
            i = min(cand, key=lambda i: w[i] / g[i][j])
            manca = a[j] - sum(g[k][j] * x[k] for k in R(s))
            aggiunta = min(manca / g[i][j], d[i] - x[i])
            x[i] += aggiunta
            passi.append(f"{NUTRIENTI[j]}: {manca:.4g} g are missing; {aggiunta:.4g} kg of "
                         f"{CIBI[i]} are added (cost per gram {w[i] / g[i][j]:.4g})")
    return x, passi


x_eur, passi = euristica(w2, g2, a2, b2, c2, d2, t2)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
ub2 = sum(w2[i] * x_eur[i] for i in R(s2))
sol_eur = {f"x[{i}]": x_eur[i] for i in R(s2)} | {f"y[{i}]": 1 if x_eur[i] > 1e-9 else 0
                                                 for i in R(s2)}
assert ammissibile(m2, sol_eur), sol_eur
print("  Heuristic solution: " + ", ".join(f"{CIBI[i]} {x_eur[i]:.4g} kg" for i in R(s2)
                                           if x_eur[i] > 1e-9)
      + f"   ub = {frazione(ub2)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl2 = duale_2(w2, g2, a2, b2, c2, d2, t2)
# recipe: beta = mu = tau = 0 (maxima, caps and variety are not priced);
# a single nutrient is priced, at the lowest cost per gram among the foods
mano, migliore, scelto = {}, -1.0, None
for j in R(r2):
    prova = {f"alpha[{jj}]": (min(w2[i] / g2[i][jj] for i in R(s2) if g2[i][jj] > 0)
                              if jj == j else 0.0) for jj in R(r2)}
    val, viol = valuta(dl2, prova)
    if viol <= 1e-9 and val > migliore:
        migliore, scelto, mano = val, j, prova
lb2, viol = valuta(dl2, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: beta = mu = tau = 0 (maxima, caps and variety are not priced) and")
print("  a single positive alpha_j, equal to the lowest cost per gram among the foods:")
for j in R(r2):
    prezzo = min(w2[i] / g2[i][j] for i in R(s2) if g2[i][j] > 0)
    print(f"    {NUTRIENTI[j]}: price {frazione(prezzo)} EUR/g  ->  a_j * price = "
          f"{frazione(a2[j] * prezzo)}")
print(f"  The best one is {NUTRIENTI[scelto]}:  lb = {frazione(lb2)}")
zlp2, zlp2r, _ = due_rilassamenti(m2, dl2)

# ---------- 4. OPTIMUM OF THE MILP ----------
z2 = risolvi(m2)
print("  Optimal solution: " + ", ".join(f"{CIBI[i]} {x2[i].X:.4g} kg" for i in R(s2)
                                         if x2[i].X > 1e-9)
      + f"   ({int(sum(y2[i].X for i in R(s2)))} different foods, {t2} required)")
for j in R(r2):
    print(f"    {NUTRIENTI[j]}: {sum(g2[i][j] * x2[i].X for i in R(s2)):.4g} g "
          f"(between {a2[j]} and {b2[j]})")
riga = registra_bound("2 diet", ub2, lb2, zlp2, zlp2r, z2)
salva_dati(pd.DataFrame([riga]), "dieta2_bound")
assert lb2 <= zlp2 <= z2 <= ub2 + 1e-9

# ---------- 5. WITHOUT THE MINIMUM LOT THE COUNT IS EMPTY ----------
intestazione("10.2 Why the count needs the minimum lot")
m, x, y = modello_2(w2, g2, a2, b2, [0] * s2, d2, t2)   # c_i = 0: no minimum lot
z_senza = risolvi(m)
accesi = [CIBI[i] for i in R(s2) if y[i].X > 0.5]
vuoti = [CIBI[i] for i in R(s2) if y[i].X > 0.5 and x[i].X < 1e-9]
print(f"  With c_i = 0 the optimum drops to {frazione(z_senza)} and the 'active' foods are "
      f"{accesi},")
print(f"  but of these the following have zero quantity: {vuoti}. The variety constraint is")
print("  satisfied by empty indicators: without a minimum lot the count says nothing.")
assert vuoti, "with c = 0 empty indicators must appear"

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: the minimum lot rises to 2 kg for every chosen food
m, x, y = modello_2(w2, g2, a2, b2, [2] * s2, d2, t2)
varianti["2a"] = variante("2a. The minimum lot rises to 2 kg per food (c_i = 2)", m)
# 2b: at least four different foods are wanted
m, x, y = modello_2(w2, g2, a2, b2, c2, d2, 4)
varianti["2b"] = variante("2b. At least four different foods are wanted (t = 4)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "dieta2_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
idx = list(R(s2))
ax.bar([i - 0.2 for i in idx], [x_eur[i] for i in idx], 0.4, color=ARANCIO, label="heuristic")
ax.bar([i + 0.2 for i in idx], [x2[i].X for i in idx], 0.4, color=TEAL, label="optimum")
for i in idx:
    ax.plot([i - 0.42, i + 0.42], [c2[i], c2[i]], color=ROSSO, lw=1.5)
ax.plot([], [], color=ROSSO, lw=1.5, label="minimum lot $c_i$")
ax.set_xticks(idx)
ax.set_xticklabels(CIBI)
ax.set_ylabel("kilos a month")
ax.set_title(f"10.2: heuristic diet ({frazione(ub2)} EUR) and optimal one ({frazione(z2)} EUR)")
ax.legend(fontsize=8)
salva_figura(fig, "cap10_dieta_ottimo")
print("Done.")
