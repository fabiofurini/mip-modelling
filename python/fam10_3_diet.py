"""Problem 10.3 -- Diet with a count of the foods and a minimum lot.

A classic diet (continuous quantities, two-sided nutritional constraints) with
three integer techniques on top: activation (3.2), minimum lot (3.3) and counting
of the types (3.11). Without the minimum lot the count "at least t different
foods" would be empty: indicators would switch on with zero quantity.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, rilassamento, risolvi,
                 valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.3 Diet: minimum cost with at least t different foods and a minimum lot")
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
                         "min": c2, "max": d2}), "fam10_3_dati")


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
salva_modello(m2, "fam10_3_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp2, zlp2r, _ = rilassamenti(m2)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
dl2 = duale_2(w2, g2, a2, b2, c2, d2, t2)
salva_modello(dl2, "fam10_3_duale")
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
dualita_forte(dl2, zlp2)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
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

# ---------- 5. WITHOUT THE MINIMUM LOT THE COUNT IS EMPTY ----------
intestazione("10.3 Why the count needs the minimum lot")
m, x, y = modello_2(w2, g2, a2, b2, [0] * s2, d2, t2)   # c_i = 0: no minimum lot
z_senza = risolvi(m)
accesi = [CIBI[i] for i in R(s2) if y[i].X > 0.5]
vuoti = [CIBI[i] for i in R(s2) if y[i].X > 0.5 and x[i].X < 1e-9]
print(f"  With c_i = 0 the optimum drops to {frazione(z_senza)} and the 'active' foods are "
      f"{accesi},")
print(f"  but of these the following have zero quantity: {vuoti}. The variety constraint is")
print("  satisfied by empty indicators: without a minimum lot the count says nothing.")
assert vuoti, "with c = 0 empty indicators must appear"

# ---------- 6. OPTIMUM OF THE MILP ----------
z2 = risolvi(m2)
print("  Optimal solution: " + ", ".join(f"{CIBI[i]} {x2[i].X:.4g} kg" for i in R(s2)
                                         if x2[i].X > 1e-9)
      + f"   ({int(sum(y2[i].X for i in R(s2)))} different foods, {t2} required)")
for j in R(r2):
    print(f"    {NUTRIENTI[j]}: {sum(g2[i][j] * x2[i].X for i in R(s2)):.4g} g "
          f"(between {a2[j]} and {b2[j]})")
riga = registra_bound("2 diet", ub2, lb2, zlp2, zlp2r, z2)
salva_dati(pd.DataFrame([riga]), "fam10_3_bound")
assert lb2 <= zlp2 <= z2 <= ub2 + 1e-9

# ---------- 7. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: the minimum lot rises to 2 kg for every chosen food
m, x, y = modello_2(w2, g2, a2, b2, [2] * s2, d2, t2)
varianti["3a"] = variante("3a. The minimum lot rises to 2 kg per food (c_i = 2)", m)
# 2b: at least four different foods are wanted
m, x, y = modello_2(w2, g2, a2, b2, c2, d2, 4)
varianti["3b"] = variante("3b. At least four different foods are wanted (t = 4)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "fam10_3_varianti")

# ---------- 8. THE SANDWICH ON THE VARIANT 2b ----------
intestazione("10.3b The sandwich on the variant: at least four different foods")
T2B = 4

# The variant changes a datum, not the structure: model, dual and heuristic are
# the same with t = 4. What changes is the value of the certificate --- and above
# all the heuristic, which must switch on one more food at its minimum lot.
m2b, x2b, y2b = modello_2(w2, g2, a2, b2, c2, d2, T2B)
salva_modello(m2b, "fam10_3b_primale")
dl2b = duale_2(w2, g2, a2, b2, c2, d2, T2B)
salva_modello(dl2b, "fam10_3b_duale")

# -- feasible heuristic: the same rule, with one more food --
x_2b, passi_2b = euristica(w2, g2, a2, b2, c2, d2, T2B)
assert x_2b is not None, "the heuristic must stay feasible with four foods"
for i, s in enumerate(passi_2b, 1):
    print(f"  Step {i}. {s}")
ub2b = sum(w2[i] * x_2b[i] for i in R(s2))
sol_2b = ({f"x[{i}]": x_2b[i] for i in R(s2)}
          | {f"y[{i}]": (1 if x_2b[i] > 1e-9 else 0) for i in R(s2)})
assert ammissibile(m2b, sol_2b), "the heuristic solution of the variant must be feasible"
print(f"  ub = {frazione(ub2b)}")

# -- dual certificate: the same recipe, on t = 4 --
mano_2b, migliore_2b, scelto_2b = {}, -1.0, None
for j in R(r2):
    prova = {f"alpha[{jj}]": (min(w2[i] / g2[i][jj] for i in R(s2) if g2[i][jj] > 0)
                              if jj == j else 0.0) for jj in R(r2)}
    val, viol = valuta(dl2b, prova)
    if viol <= 1e-9 and val > migliore_2b:
        migliore_2b, scelto_2b, mano_2b = val, j, prova
lb2b, viol_2b = valuta(dl2b, mano_2b)
assert viol_2b <= 1e-9, viol_2b
print("Dual solution by hand: the same recipe as the base problem --- beta = mu = tau = 0 and")
print(f"  a single positive alpha, on {NUTRIENTI[scelto_2b]}. Variety is not priced: tau")
print("  enters the objective with its right-hand side t, but the column of the y_i imposes")
print("  tau <= c_i lam_i - d_i mu_i, and with lam = mu = 0 it stays tau = 0. Asking for one")
print("  more food does not move the relaxation, it moves the integer optimum.")
print(f"  ->  lb = {frazione(lb2b)}")
zlp2b, zlp2br, _ = due_rilassamenti(m2b, dl2b)
z2b = risolvi(m2b)
riga_2b = registra_bound("3b at least four foods", ub2b, lb2b, zlp2b, zlp2br, z2b)
salva_dati(pd.DataFrame([riga_2b]), "fam10_3b_bound")
assert lb2b <= zlp2b <= z2b <= ub2b + 1e-9

# ---------- 9. FIGURE ----------
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
ax.set_title(f"10.3: heuristic diet ({frazione(ub2)} EUR) and optimal one ({frazione(z2)} EUR)")
ax.legend(fontsize=8)
salva_figura(fig, "cap10_dieta_ottimo")
print("Done.")
