"""Problem 10.1 -- Prizes obtainable in two ways.

Every prize is obtained either with points only, or with fewer points plus a
contribution in euros: two binary variables per prize and a mutual-exclusion
constraint. The link is the one of chapter 2: x_i + y_i <= 1 is a set packing, and
the converses must be refuted explicitly with x_i = y_i = 0.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.1 Prizes: points only, or fewer points plus a contribution in euros")
a1 = [8, 6, 10, 5, 7]        # points if the points-only mode is used
b1 = [4, 3, 6, 2, 4]         # points if the contribution is added
c1 = [10, 8, 15, 5, 9]       # contribution in euros
d1 = [5, 4, 7, 3, 6]         # preference value
p1, ell1 = 20, 16            # points available and minimum preference required
s1 = len(a1)
salva_dati(pd.DataFrame({"prize": R(1, s1 + 1), "a": a1, "b": b1, "c": c1, "d": d1}),
           "premi1_dati")
print(f"  {s1} prizes, {p1} points available, minimum preference required {ell1}")


def modello_1(a, b, c, d, p, ell):
    s = len(a)
    m = nuovo_modello("prizes")
    x = m.addVars(s, vtype=GRB.BINARY, name="x")     # prize with points only
    y = m.addVars(s, vtype=GRB.BINARY, name="y")     # prize with points + contribution
    m.setObjective(gp.quicksum(c[i] * y[i] for i in R(s)), GRB.MINIMIZE)
    m.addConstrs((x[i] + y[i] <= 1 for i in R(s)), name="one_mode")
    m.addConstr(gp.quicksum(a[i] * x[i] + b[i] * y[i] for i in R(s)) <= p, name="points")
    m.addConstr(gp.quicksum(d[i] * (x[i] + y[i]) for i in R(s)) >= ell, name="preference")
    return m, x, y


def duale_1(a, b, c, d, p, ell):
    """max -sum_i sigma_i - p pi + ell rho;  -sigma_i - a_i pi + d_i rho <= 0;
    -sigma_i - b_i pi + d_i rho <= c_i;  sigma, pi >= 0, rho >= 0.
    (sigma are the duals of x_i + y_i <= 1, pi that of the points, rho that of the
    preference; in a minimisation the <= constraints give duals <= 0: here we write
    -sigma with sigma >= 0.)"""
    s = len(a)
    dl = nuovo_modello("dual_prizes")
    sigma = dl.addVars(s, name="sigma")
    pi = dl.addVar(name="pi")
    rho = dl.addVar(name="rho")
    dl.setObjective(-gp.quicksum(sigma[i] for i in R(s)) - p * pi + ell * rho, GRB.MAXIMIZE)
    dl.addConstrs((-sigma[i] - a[i] * pi + d[i] * rho <= 0 for i in R(s)), name="rc_x")
    dl.addConstrs((-sigma[i] - b[i] * pi + d[i] * rho <= c[i] for i in R(s)), name="rc_y")
    return dl


m1, x1, y1 = modello_1(a1, b1, c1, d1, p1, ell1)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# constructive heuristic: the prizes are scanned by decreasing preference; each one is taken with points
# only if they suffice, otherwise with the contribution if the reduced points suffice,
# and we stop as soon as the required preference is reached
punti, pref = p1, 0
scelta = {}
for i in sorted(R(s1), key=lambda i: (-d1[i], i)):
    if pref >= ell1:
        break
    if punti >= a1[i]:
        scelta[i], punti, pref = "points", punti - a1[i], pref + d1[i]
        print(f"  Prize {i + 1} (preference {d1[i]}): the points alone are enough ({a1[i]} <= "
              f"{punti + a1[i]}): it is taken; preference {pref}, points left {punti}")
    elif punti >= b1[i]:
        scelta[i], punti, pref = "contribution", punti - b1[i], pref + d1[i]
        print(f"  Prize {i + 1} (preference {d1[i]}): the points are not enough for mode a "
              f"({a1[i]} > {punti + b1[i]}), mode b is used: {b1[i]} points and {c1[i]} euros; "
              f"preference {pref}, points left {punti}")
    else:
        print(f"  Prize {i + 1} (preference {d1[i]}): the {punti} points left are not enough "
              f"for either mode: it is skipped")
assert pref >= ell1, "the constructive heuristic does not reach the required preference"
ub1 = sum(c1[i] for i, mod in scelta.items() if mod == "contribution")
sol_eur = {f"x[{i}]": 1 for i, mod in scelta.items() if mod == "points"} \
    | {f"y[{i}]": 1 for i, mod in scelta.items() if mod == "contribution"}
assert ammissibile(m1, sol_eur)
print(f"  Heuristic solution: preference {pref} >= {ell1}, total contribution "
      f"ub = {frazione(ub1)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl1 = duale_1(a1, b1, c1, d1, p1, ell1)
# recipe: one chooses the price pi of a point and the price rho of one unit of
# preference; the duals of the mutual exclusion follow from these by setting
# sigma_i = max(0, d_i rho - a_i pi), the smallest value that makes the constraint on
# mode a feasible. What is left to check are the constraints on mode b. The pair
# (pi, rho) is chosen on a grid: the objective is concave and piecewise linear.
def duale_da(pi_v, rho_v):
    sig = [max(0.0, d1[i] * rho_v - a1[i] * pi_v) for i in R(s1)]
    ok = all(-sig[i] - b1[i] * pi_v + d1[i] * rho_v <= c1[i] + 1e-9 for i in R(s1))
    val = -sum(sig) - p1 * pi_v + ell1 * rho_v
    return (val if ok else float("-inf")), sig


griglia = [k / 100 for k in R(0, 301)]
coppie = [(pi_v, rho_v) for pi_v in griglia for rho_v in griglia]
pi_star, rho_star = max(coppie, key=lambda c: duale_da(*c)[0])
_, sigma_star = duale_da(pi_star, rho_star)
mano = {"pi": pi_star, "rho": rho_star} | {f"sigma[{i}]": sigma_star[i] for i in R(s1)}
lb1, viol = valuta(dl1, mano)
assert viol <= 1e-9, (viol, mano)
print("  Hand-built dual: one chooses the price pi of a point and the price rho of one unit")
print("  of preference; the duals of the mutual exclusion follow by setting")
print("  sigma_i = max(0, d_i rho - a_i pi), the smallest value that makes the constraint on")
print("  mode a feasible. What is left to check are the constraints on mode b.")
print(f"    pi = {frazione(pi_star)} euros per point, rho = {frazione(rho_star)} euros per")
print(f"    unit of preference, sigma = " + ", ".join(frazione(v) for v in sigma_star))
print(f"  ->  lb = -sum(sigma) - p pi + l rho = {frazione(lb1)}")
zlp1, zlp1r, _ = due_rilassamenti(m1, dl1)

# ---------- 4. OPTIMUM OF THE MILP ----------
z1 = risolvi(m1)
soli_punti = [i + 1 for i in R(s1) if x1[i].X > 0.5]
con_contributo = [i + 1 for i in R(s1) if y1[i].X > 0.5]
print(f"  Optimal solution: with points only {soli_punti}, with a contribution "
      f"{con_contributo}; total contribution {frazione(z1)}")
print(f"  Points used: "
      f"{sum(a1[i - 1] for i in soli_punti) + sum(b1[i - 1] for i in con_contributo)}"
      f" out of {p1}; preference "
      f"{sum(d1[i - 1] for i in soli_punti + con_contributo)} >= {ell1}")
riga = registra_bound("1 prizes", ub1, lb1, zlp1, zlp1r, z1)
salva_dati(pd.DataFrame([riga]), "premi1_bound")
assert lb1 <= zlp1 <= z1 <= ub1 + 1e-9

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 1a: prizes 3 and 5 are alternatives (at most one of the two, in either mode)
m, x, y = modello_1(a1, b1, c1, d1, p1, ell1)
m.addConstr(x[2] + y[2] + x[4] + y[4] <= 1, name="alternatives")
varianti["1a"] = variante("1a. Prizes 3 and 5 are alternatives (x3+y3+x5+y5 <= 1)", m)
# 1b: at least four prizes are wanted, on top of the preference threshold
m, x, y = modello_1(a1, b1, c1, d1, p1, ell1)
m.addConstr(gp.quicksum(x[i] + y[i] for i in R(s1)) >= 4, name="at_least_four")
varianti["1b"] = variante("1b. At least four prizes are wanted (sum_i (x_i+y_i) >= 4)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "premi1_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
premi = list(R(1, s1 + 1))
larghezza = 0.38
ax.bar([i - larghezza / 2 for i in premi], a1, larghezza, color=TEAL, label="points (mode a)")
ax.bar([i + larghezza / 2 for i in premi], b1, larghezza, color=ARANCIO,
       label="points (mode b, + contribution)")
for i in R(s1):
    if x1[i].X > 0.5:
        ax.annotate("chosen", (i + 1 - larghezza / 2, a1[i]), ha="center", va="bottom",
                    fontsize=8, color=BLU)
    if y1[i].X > 0.5:
        ax.annotate(f"chosen\n{c1[i]} EUR", (i + 1 + larghezza / 2, b1[i]), ha="center",
                    va="bottom", fontsize=8, color=ROSSO)
ax.set_xticks(premi)
ax.set_xticklabels([f"prize {i}\n(pref. {d1[i - 1]})" for i in premi], fontsize=8)
ax.set_ylabel("points required")
ax.set_ylim(0, max(a1) + 3)
ax.set_title(f"10.1: the modes chosen (total contribution {frazione(z1)} EUR)")
ax.legend(fontsize=8)
salva_figura(fig, "cap10_premi_ottimo")
print("Done.")
