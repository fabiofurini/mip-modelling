"""EX 5 -- Vehicle production with a minimum lot (family 9).

Two resources (steel and labour hours) and five vehicle types, each with a minimum
quantity if it is produced. It is the same structure as problem 9.3 without the
variety bonus: minimum lot (3.3) plus activation (3.1), that is semicontinuous
variables.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 5. Vehicles: two resources and a minimum quantity per type")
NOMI = ["compact car", "midsize car", "large car", "midsize minivan", "large minivan"]
a4 = [[2, 3, 5, 6, 8],            # steel per unit
      [30, 25, 40, 45, 55]]       # labour hours per unit
b4 = [1000, 2000]                 # resources available
RISORSE = ["steel (tons)", "labour hours"]
p4 = [200, 250, 300, 550, 700]    # profit per unit
q4 = [10, 10, 10, 5, 5]           # minimum quantity if the type is produced
ns, nr = len(p4), len(b4)
M4 = [min(b4[i] // a4[i][j] for i in R(nr)) for j in R(ns)]
salva_dati(pd.DataFrame({"type": NOMI, "steel": a4[0], "hours": a4[1], "profit": p4,
                         "minimum": q4, "maximum": M4}), "ex05_dati")
print("  Largest quantity of a single type that can be produced (the natural big-M):")
for j in R(ns):
    print(f"    {NOMI[j]:20s} min({b4[0]}/{a4[0][j]}, {b4[1]}/{a4[1][j]}) = {M4[j]}")


def modello(a, b, p, q, M):
    ns, nr = len(p), len(b)
    m = nuovo_modello("vehicles_num4")
    x = m.addVars(ns, vtype=GRB.INTEGER, name="x")
    y = m.addVars(ns, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(p[j] * x[j] for j in R(ns)), GRB.MAXIMIZE)
    m.addConstrs((gp.quicksum(a[i][j] * x[j] for j in R(ns)) <= b[i] for i in R(nr)),
                 name="resource")
    m.addConstrs((x[j] - q[j] * y[j] >= 0 for j in R(ns)), name="minimum_lot")
    m.addConstrs((x[j] - M[j] * y[j] <= 0 for j in R(ns)), name="activate")
    return m, x, y


def duale(a, b, p, q, M):
    """min sum_i b_i pi_i  with pi >= 0, lam <= 0 (minimum lot, written >=) and mu >= 0.

    Columns:  x_j: sum_i a_ij pi_i + lam_j + mu_j >= p_j
              y_j: -q_j lam_j - M_j mu_j >= 0
    """
    ns, nr = len(p), len(b)
    d = nuovo_modello("dual_vehicles_num4")
    pi = d.addVars(nr, name="pi")
    lam = d.addVars(ns, lb=-GRB.INFINITY, ub=0.0, name="lam")
    mu = d.addVars(ns, name="mu")
    d.setObjective(gp.quicksum(b[i] * pi[i] for i in R(nr)), GRB.MINIMIZE)
    d.addConstrs((gp.quicksum(a[i][j] * pi[i] for i in R(nr)) + lam[j] + mu[j] >= p[j]
                  for j in R(ns)), name="rcx")
    d.addConstrs((-q[j] * lam[j] - M[j] * mu[j] >= 0 for j in R(ns)), name="rcy")
    return d


m4, x4, y4 = modello(a4, b4, p4, q4, M4)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
# constructive heuristic on the profit per labour hour (the tightest resource): a type is switched on
# only if its minimum quantity can be reached, then it is pushed to the maximum
def euristica(a, b, p, q):
    ns, nr = len(p), len(b)
    res = list(map(float, b))
    x = [0] * ns
    passi = [f"profit per labour hour: "
             + ", ".join(f"{NOMI[j]} {frazione(p[j] / a[1][j])}" for j in R(ns))]
    for j in sorted(R(ns), key=lambda j: (-p[j] / a[1][j], j)):
        if any(a[i][j] * q[j] > res[i] + 1e-9 for i in R(nr)):
            passi.append(f"{NOMI[j]}: the minimum quantity {q[j]} cannot be reached, skipped")
            continue
        n = min(int(res[i] // a[i][j]) for i in R(nr))
        x[j] = n
        for i in R(nr):
            res[i] -= a[i][j] * n
        passi.append(f"{NOMI[j]}: {n} units are produced (minimum {q[j]}); resources left "
                     + ", ".join(f"{RISORSE[i]} {frazione(res[i])}" for i in R(nr)))
    return x, passi


x_e, passi = euristica(a4, b4, p4, q4)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
lb4 = sum(p4[j] * x_e[j] for j in R(ns))
sol_eur = ({f"x[{j}]": x_e[j] for j in R(ns)}
           | {f"y[{j}]": 1 if x_e[j] else 0 for j in R(ns)})
assert ammissibile(m4, sol_eur), sol_eur
print(f"  Heuristic solution: " + ", ".join(f"{x_e[j]} {NOMI[j]}" for j in R(ns) if x_e[j])
      + f"   lb = {frazione(lb4)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d4 = duale(a4, b4, p4, q4, M4)
# recipe: lam = mu = 0 (the minimum lot is not priced) and a single resource priced at
# the highest unit price among the vehicles
migliore, mano, scelta = float("inf"), None, None
for i in R(nr):
    prezzo = max(p4[j] / a4[i][j] for j in R(ns))
    prova = {f"pi[{i}]": prezzo}
    val, viol = valuta(d4, prova)
    if viol <= 1e-9 and val < migliore:
        migliore, mano, scelta = val, prova, i
ub4, viol = valuta(d4, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: lam = mu = 0 and a single resource priced, at the highest unit")
print("  price among the vehicles (so that every constraint a_ij pi_i >= p_j holds):")
for i in R(nr):
    prezzo = max(p4[j] / a4[i][j] for j in R(ns))
    print(f"    {RISORSE[i]:16s} price {frazione(prezzo):>8}  ->  bound "
          f"{frazione(b4[i] * prezzo)}")
print(f"  The better bound comes from: {RISORSE[scelta]}.  ub = {frazione(ub4)}")
zlp4, zlp4r, _ = due_rilassamenti(m4, d4)

# ---------- 4. OPTIMUM OF THE MILP ----------
z4 = risolvi(m4)
print("  Optimal solution: " + ", ".join(f"{int(x4[j].X)} {NOMI[j]}" for j in R(ns)
                                         if x4[j].X > 0.5))
for i in R(nr):
    usato = sum(a4[i][j] * x4[j].X for j in R(ns))
    print(f"    {RISORSE[i]}: {frazione(usato)} out of {b4[i]}")
riga = registra_bound("EX 5 vehicles", ub4, lb4, zlp4, zlp4r, z4, senso="max")
salva_dati(pd.DataFrame([riga]), "ex05_bound")
assert lb4 <= z4 <= zlp4 <= ub4 + 1e-9

# ---------- 5. THE MINIMUM LOT IS A CONSTRAINT, NOT A HELP ----------
intestazione("EX 5. What the minimum lot costs")
m, x, y = modello(a4, b4, p4, [0] * ns, M4)
z_senza = risolvi(m)
print(f"  Without minimum quantities the optimum rises to {frazione(z_senza)} (against "
      f"{frazione(z4)}):")
print(f"  the minimum lot costs {frazione(z_senza - z4)} of profit because it prevents")
print("  producing few units of the most profitable types.")
varianti = {"without minimum quantities": z_senza}
# 4a: minimum quantities doubled
m, x, y = modello(a4, b4, p4, [2 * v for v in q4], M4)
z_a = risolvi(m)
varianti["4a. minimum quantities doubled"] = z_a
print(f"  4a. With the minimum quantities doubled: z = {frazione(z_a)}")
# 4b: labour hours doubled
b_b = [b4[0], 2 * b4[1]]
m, x, y = modello(a4, b_b, p4, q4,
                  [min(b_b[i] // a4[i][j] for i in R(nr)) for j in R(ns)])
z_b = risolvi(m)
varianti["4b. labour hours doubled"] = z_b
uso_b = [sum(a4[i][j] * x[j].X for j in R(ns)) for i in R(nr)]
print(f"  4b. With the labour hours doubled: z = {frazione(z_b)}; resources used "
      + ", ".join(f"{RISORSE[i]} {frazione(uso_b[i])} out of {b_b[i]}" for i in R(nr)))
print("      The hours stay the tight resource and the profit almost exactly doubles.")
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "ex05_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
idx = list(R(ns))
ax.bar([j - 0.2 for j in idx], [x_e[j] for j in idx], 0.4, color=ARANCIO, label="heuristic")
ax.bar([j + 0.2 for j in idx], [x4[j].X for j in idx], 0.4, color=TEAL, label="optimum")
for j in idx:
    ax.plot([j - 0.42, j + 0.42], [q4[j], q4[j]], color=GRIGIO, lw=1.5)
ax.plot([], [], color=GRIGIO, lw=1.5, label="minimum quantity")
ax.set_xticks(idx)
ax.set_xticklabels([n.replace(" ", "\n") for n in NOMI], fontsize=8)
ax.set_ylabel("units produced")
ax.set_title(f"EX 5: heuristic {frazione(lb4)} against optimum {frazione(z4)}")
ax.legend(fontsize=8)
salva_figura(fig, "ex05_produzione")
print("Done.")
