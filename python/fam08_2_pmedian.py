"""Problem 8.2 -- Location with a maximum number of facilities (p-median).

Disaggregated activation link between x_l (location open) and y_lc (client c
served by l), derived from the CNF of a Boolean implication as in problem
7.5, but here the number of open locations is bounded by k rather than by a
time budget.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, stampa_soluzione, valuta)
from stile import CICLO, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------

intestazione("2. p-median: at most k locations, every client served by the nearest open one")
dist2 = [[5, 6, 10], [3, 12, 9], [10, 9, 4]]   # distance location l -> client c
k2 = 2
m, n = 3, 3
salva_dati(pd.DataFrame([{"location": l + 1, "client": c + 1, "d": dist2[l][c]}
                         for l in R(m) for c in R(n)]), "loc2_distanze")


def modello_2(dist, k):
    m, n = len(dist), len(dist[0])
    mod = nuovo_modello("p_median")
    x = mod.addVars(m, vtype=GRB.BINARY, name="x")
    y = mod.addVars(m, n, vtype=GRB.BINARY, name="y")
    mod.setObjective(gp.quicksum(dist[l][c] * y[l, c] for l in R(m) for c in R(n)), GRB.MINIMIZE)
    mod.addConstrs((y.sum("*", c) == 1 for c in R(n)), name="assign")
    mod.addConstr(x.sum() <= k, name="number_of_locations")
    mod.addConstrs((x[l] - y[l, c] >= 0 for l in R(m) for c in R(n)), name="link")
    return mod, x, y


def duale_2(dist, k):
    """max sum mu_c + k varrho;  varrho + sum_c pi_lc <= 0;  mu_c - pi_lc <= d_lc;
    mu free, varrho <= 0, pi >= 0."""
    m, n = len(dist), len(dist[0])
    dl = nuovo_modello("duale_p_median")
    mu = dl.addVars(n, lb=-GRB.INFINITY, name="mu")
    varrho = dl.addVar(lb=-GRB.INFINITY, ub=0.0, name="varrho")
    pi = dl.addVars(m, n, name="pi")
    dl.setObjective(mu.sum() + k * varrho, GRB.MAXIMIZE)
    dl.addConstrs((varrho + gp.quicksum(pi[l, c] for c in R(n)) <= 0 for l in R(m)), name="rc_x")
    dl.addConstrs((mu[c] - pi[l, c] <= dist[l][c] for l in R(m) for c in R(n)), name="rc_y")
    return dl


m2, x2, y2 = modello_2(dist2, k2)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------

print("Heuristic: the first k locations are opened in natural order, then every client")
print("is served by the nearest open location.")


def euristica_2(dist, k):
    m, n = len(dist), len(dist[0])
    x = [1 if l < k else 0 for l in R(m)]
    y, passi = {}, []
    for c in R(n):
        md, sl = float("inf"), None
        for l in R(k):
            if dist[l][c] < md:
                md, sl = dist[l][c], l
        y[(sl, c)] = 1
        passi.append(f"Client {c + 1}: the nearest open location is {sl + 1} (distance {md}); "
                     f"y[{sl + 1}][{c + 1}] = 1.")
    return x, y, passi


xe, ye, passi = euristica_2(dist2, k2)
print(f"  The first k = {k2} locations are opened: x = {xe}.")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub2 = sum(dist2[l][c] for (l, c) in ye)
print(f"  ub = {ub2}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------

d2 = duale_2(dist2, k2)
mano = {"varrho": 0.0}
mano.update({f"mu[{c}]": min(dist2[l][c] for l in R(m)) for c in R(n)})
lb2, viol = valuta(d2, mano)
assert viol <= 1e-9, viol
print("Hand-built dual solution: pi = 0, varrho = 0, mu_c = min_l d_lc = "
      + ", ".join(frazione(mano[f"mu[{c}]"]) for c in R(n)) + f"  ->  lb = {frazione(lb2)}")
zlp2, zlp2r, _ = due_rilassamenti(m2, d2)

# ---------- 4. OPTIMAL SOLUTION OF THE MILP ----------

z2 = risolvi(m2)
print("Optimal solution of the MILP:")
stampa_soluzione(m2, solo_non_nulle=True)
riga = registra_bound("2 p-median", ub2, lb2, zlp2, zlp2r, z2)
salva_dati(pd.DataFrame([riga]), "loc2_bound")

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------

varianti = {}


def variante(nome, mod):
    z = risolvi(mod)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: exactly k locations must be open (not at most k)
mod, x, y = modello_2(dist2, k2)
mod.addConstr(x.sum() >= k2, name="number_of_locations_exact")   # with "<= k" already in the model, together they impose "= k"
varianti["2a"] = variante("2a. Exactly k open locations (sum x_l = k)", mod)
# 2b: client 1 must be served within distance 4 (additional coverage)
mod, x, y = modello_2(dist2, k2)
mod.addConstrs((y[l, 0] == 0 for l in R(3) if dist2[l][0] > 4), name="max_distance_client1")
varianti["2b"] = variante("2b. Client 1 served within distance 4 (y_l1 = 0 if d_l1 > 4)", mod)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "loc2_varianti")

# ---------- 6. FIGURES ----------

fig, ax = plt.subplots(figsize=(5.5, 5))
xs = {"location": [0, 1.4, 2.8], "client": [0.3, 1.1, 2.4]}
for c in R(3):
    l = next(l for l in R(3) if y2[l, c].X > 0.5)
    ax.plot([xs["location"][l], xs["client"][c]], [1, 0], color=CICLO[c], lw=2, marker="o")
for l in R(3):
    marker = "s" if x2[l].X > 0.5 else "x"
    ax.plot(xs["location"][l], 1, marker=marker, ms=16, color="black" if x2[l].X > 0.5 else "gray")
    ax.annotate(f"location {l + 1}", (xs["location"][l], 1), textcoords="offset points", xytext=(0, 12), ha="center")
for c in R(3):
    ax.plot(xs["client"][c], 0, marker="o", ms=10, color=CICLO[c])
    ax.annotate(f"client {c + 1}", (xs["client"][c], 0), textcoords="offset points", xytext=(0, -18), ha="center")
ax.set_ylim(-0.4, 1.4)
ax.axis("off")
ax.set_title(f"p-median: optimal solution (z = {frazione(z2)}); square = open location")
salva_figura(fig, "cap08_pmediana_ottimo")
print("Fine.")
