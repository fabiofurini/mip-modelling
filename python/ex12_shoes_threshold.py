"""EX 12 -- Shoes with a minimum production threshold (family 9).

Three resources, three types of shoe and a threshold per type: either at least
q_j pairs are produced, or none. It is the semicontinuous variable of technique
3.3, with the big-M chosen naturally as the largest producible amount of that type
alone.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 12. Shoes: three resources and a minimum production threshold")
NOMI = ["hiking boots", "loafers", "walking shoes"]
RISORSE = ["leather (g)", "machine hours", "nails"]
a11 = [[850, 600, 700],       # leather per pair
       [3, 2, 2.5],           # machine hours per pair
       [20, 15, 20]]          # nails per pair
b11 = [120000, 7000, 40000]
p11 = [150, 120, 130]         # selling price per pair
q11 = [100, 200, 150]         # minimum threshold
ns, nr = len(p11), len(b11)
M11 = [min(int(b11[i] // a11[i][j]) for i in R(nr)) for j in R(ns)]
salva_dati(pd.DataFrame({"type": NOMI, "leather": a11[0], "hours": a11[1], "nails": a11[2],
                         "price": p11, "threshold": q11, "maximum": M11}), "ex12_dati")
print("  Largest producible amount of a single type (the natural big-M):")
for j in R(ns):
    quale = min(R(nr), key=lambda i: b11[i] / a11[i][j])
    print(f"    {NOMI[j]:16s} {M11[j]} pairs, limited by {RISORSE[quale]}")
print("  For the loafers threshold and maximum coincide (200): either exactly 200 are made,")
print("  or none. The variable is in fact a binary multiplied by 200.")


def modello(a, b, p, q, M):
    ns, nr = len(p), len(b)
    m = nuovo_modello("shoes_threshold")
    x = m.addVars(ns, vtype=GRB.INTEGER, name="x")
    y = m.addVars(ns, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(p[j] * x[j] for j in R(ns)), GRB.MAXIMIZE)
    m.addConstrs((gp.quicksum(a[i][j] * x[j] for j in R(ns)) <= b[i] for i in R(nr)),
                 name="resource")
    m.addConstrs((x[j] - q[j] * y[j] >= 0 for j in R(ns)), name="threshold")
    m.addConstrs((x[j] - M[j] * y[j] <= 0 for j in R(ns)), name="activate")
    return m, x, y


def duale(a, b, p, q, M):
    """min sum_i b_i pi_i  with pi >= 0, lam <= 0 (threshold, written >=) and mu >= 0.

    Columns:  x_j: sum_i a_ij pi_i + lam_j + mu_j >= p_j
              y_j: -q_j lam_j - M_j mu_j >= 0
    """
    ns, nr = len(p), len(b)
    d = nuovo_modello("dual_shoes_threshold")
    pi = d.addVars(nr, name="pi")
    lam = d.addVars(ns, lb=-GRB.INFINITY, ub=0.0, name="lam")
    mu = d.addVars(ns, name="mu")
    d.setObjective(gp.quicksum(b[i] * pi[i] for i in R(nr)), GRB.MINIMIZE)
    d.addConstrs((gp.quicksum(a[i][j] * pi[i] for i in R(nr)) + lam[j] + mu[j] >= p[j]
                  for j in R(ns)), name="rcx")
    d.addConstrs((-q[j] * lam[j] - M[j] * mu[j] >= 0 for j in R(ns)), name="rcy")
    return d


m11, x11, y11 = modello(a11, b11, p11, q11, M11)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND) ----------
# constructive heuristic on the price per gram of leather (the tightest resource), respecting the
# threshold: a type enters only if at least q_j pairs can be made
def euristica(a, b, p, q):
    ns, nr = len(p), len(b)
    res = [float(v) for v in b]
    x = [0] * ns
    passi = ["price per gram of leather: "
             + ", ".join(f"{NOMI[j]} {frazione(p[j] / a[0][j])}" for j in R(ns))]
    for j in sorted(R(ns), key=lambda j: (-p[j] / a[0][j], j)):
        if any(a[i][j] * q[j] > res[i] + 1e-9 for i in R(nr)):
            passi.append(f"{NOMI[j]}: the threshold {q[j]} cannot be reached, skipped")
            continue
        n = min(int(res[i] // a[i][j]) for i in R(nr))
        x[j] = n
        for i in R(nr):
            res[i] -= a[i][j] * n
        passi.append(f"{NOMI[j]}: {n} pairs (threshold {q[j]}); resources left "
                     + ", ".join(f"{RISORSE[i]} {frazione(res[i])}" for i in R(nr)))
    return x, passi


x_e, passi = euristica(a11, b11, p11, q11)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
lb11 = sum(p11[j] * x_e[j] for j in R(ns))
sol_eur = ({f"x[{j}]": x_e[j] for j in R(ns)}
           | {f"y[{j}]": 1 if x_e[j] else 0 for j in R(ns)})
assert ammissibile(m11, sol_eur), sol_eur
print("  Heuristic solution: " + ", ".join(f"{x_e[j]} {NOMI[j]}" for j in R(ns) if x_e[j])
      + f"   lb = {frazione(lb11)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d11 = duale(a11, b11, p11, q11, M11)
migliore, mano, scelta = float("inf"), None, None
for i in R(nr):
    prezzo = max(p11[j] / a11[i][j] for j in R(ns))
    prova = {f"pi[{i}]": prezzo}
    val, viol = valuta(d11, prova)
    if viol <= 1e-9 and val < migliore:
        migliore, mano, scelta = val, prova, i
ub11, viol = valuta(d11, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: lam = mu = 0 (the threshold is not priced) and a single resource")
print("  priced, at the highest unit price among the types of shoe:")
for i in R(nr):
    prezzo = max(p11[j] / a11[i][j] for j in R(ns))
    print(f"    {RISORSE[i]:16s} price {frazione(prezzo):>8}  ->  bound "
          f"{frazione(b11[i] * prezzo)}")
print(f"  The better bound comes from: {RISORSE[scelta]}.  ub = {frazione(ub11)}")
zlp11, zlp11r, _ = due_rilassamenti(m11, d11)

# ---------- 4. OPTIMUM OF THE MILP ----------
z11 = risolvi(m11)
print("  Optimal solution: " + ", ".join(f"{int(x11[j].X)} {NOMI[j]}" for j in R(ns)
                                         if x11[j].X > 0.5))
for i in R(nr):
    usato = sum(a11[i][j] * x11[j].X for j in R(ns))
    print(f"    {RISORSE[i]}: {frazione(usato)} out of {b11[i]} "
          f"({'saturated' if abs(usato - b11[i]) < 1e-6 else 'with slack'})")
riga = registra_bound("EX 12 shoes with threshold", ub11, lb11, zlp11, zlp11r, z11,
                      senso="max")
salva_dati(pd.DataFrame([riga]), "ex12_bound")
assert lb11 <= z11 <= zlp11 <= ub11 + 1e-9

# ---------- 5. WHAT THE THRESHOLD COSTS ----------
intestazione("EX 12. The price of the threshold and the price of integrality")
m, x, y = modello(a11, b11, p11, [0] * ns, M11)
z_senza = risolvi(m)
print(f"  ub = lb = z(LP) = z(LP+) = z(MILP) = {frazione(z11)}: on this instance the sandwich")
print("  closes immediately. The reason is that a single resource is tight, the leather, and")
print("  the type that gets the most out of it per gram (the loafers, at 1/5 of a euro per")
print("  gram) uses it up on its own, staying within its own threshold and its own maximum.")
print(f"  Without thresholds the optimum stays {frazione(z_senza)}: here the threshold costs")
print("  nothing.")
varianti = {"without thresholds": z_senza}
m, x, y = modello(a11, b11, p11, [2 * v for v in q11], M11)
z_a = risolvi(m)
varianti["11a. thresholds doubled"] = z_a
print(f"  11a. With the thresholds doubled: z = {frazione(z_a)}. The threshold of the loafers")
print(f"       becomes 400 pairs, but the leather allows at most {M11[1]}: no type reaches")
print("       its own threshold any more and production stops altogether.")
b_alt = [200000, b11[1], b11[2]]
M_alt = [min(int(b_alt[i] // a11[i][j]) for i in R(nr)) for j in R(ns)]
m, x, y = modello(a11, b_alt, p11, q11, M_alt)
z_b = risolvi(m)
varianti["11b. leather at 200000 g"] = z_b
print(f"  11b. With 200000 g of leather: z = {frazione(z_b)}, that is "
      + ", ".join(f"{int(x[j].X)} {NOMI[j]}" for j in R(ns) if x[j].X > 0.5))
print(f"       The maximum producible grows with the resource: the big-Ms must be recomputed "
      f"({M_alt}).")
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "ex12_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
idx = list(R(ns))
ax.bar([j - 0.2 for j in idx], [x_e[j] for j in idx], 0.4, color=ARANCIO, label="heuristic")
ax.bar([j + 0.2 for j in idx], [x11[j].X for j in idx], 0.4, color=TEAL, label="optimum")
for j in idx:
    ax.plot([j - 0.42, j + 0.42], [q11[j], q11[j]], color=GRIGIO, lw=1.5)
    ax.plot([j - 0.42, j + 0.42], [M11[j], M11[j]], color=BLU, lw=1.2, ls=":")
ax.plot([], [], color=GRIGIO, lw=1.5, label="minimum threshold")
ax.plot([], [], color=BLU, lw=1.2, ls=":", label="maximum producible")
ax.set_xticks(idx)
ax.set_xticklabels([n.replace(" ", "\n") for n in NOMI], fontsize=8)
ax.set_ylabel("pairs produced")
ax.set_title(f"EX 12: heuristic {frazione(lb11)} against optimum {frazione(z11)}")
ax.legend(fontsize=8)
salva_figura(fig, "ex12_produzione")
print("Done.")
