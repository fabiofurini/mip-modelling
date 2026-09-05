"""Problem 9.1 -- Lot sizing with a fixed set-up cost.

Inventory balance, activation of production with a big-M and storage. The link is
the fixed cost of section 3.2, with the coefficient read off the data: M_t is the
residual demand, not a large number picked at random.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from euristiche import euristica_lotti
from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, VERDE, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("9.1 Lot sizing: inventory balance, production run with a fixed cost")
d1 = [20, 10, 30, 40, 10]          # demand of the five days
p1 = [2, 3, 2, 3, 2]               # unit production cost
q1 = [50, 50, 50, 50, 50]          # fixed set-up cost of a run
h1 = [1, 1, 1, 1]                  # storage cost at the end of the day (t = 1..n-1)
r0, rn = 0, 0                      # initial and required final inventory
n1 = len(d1)
# the smallest valid big-M: at an optimum one never produces more than the residual demand
M1 = [sum(d1[t:]) + rn for t in R(n1)]
salva_dati(pd.DataFrame({"day": R(1, n1 + 1), "demand": d1, "unit_cost": p1,
                         "setup_cost": q1, "M": M1}), "prod1_dati")


def modello_1(d, p, q, h, r0, rn):
    n = len(d)
    M = [sum(d[t:]) + rn for t in R(n)]
    m = nuovo_modello("lot_sizing")
    x = m.addVars(n, name="x")                       # quantity produced
    s = m.addVars(n - 1, name="s")                   # inventory at the end of day t
    y = m.addVars(n, vtype=GRB.BINARY, name="y")     # production run started
    m.setObjective(gp.quicksum(p[t] * x[t] for t in R(n))
                   + gp.quicksum(q[t] * y[t] for t in R(n))
                   + gp.quicksum(h[t] * s[t] for t in R(n - 1)), GRB.MINIMIZE)
    m.addConstr(x[0] - s[0] == d[0] - r0, name="balance[0]")
    m.addConstrs((x[t] + s[t - 1] - s[t] == d[t] for t in R(1, n - 1)), name="balance")
    m.addConstr(x[n - 1] + s[n - 2] == d[n - 1] + rn, name=f"balance[{n - 1}]")
    m.addConstrs((-x[t] + M[t] * y[t] >= 0 for t in R(n)), name="run")
    return m, x, s, y


def duale_1(d, p, q, h, r0, rn):
    """max sum_t b_t mu_t;  mu_t - pi_t <= p_t;  M_t pi_t <= q_t;  -mu_t + mu_{t+1} <= h_t;
    mu free, pi >= 0."""
    n = len(d)
    M = [sum(d[t:]) + rn for t in R(n)]
    b = [d[0] - r0] + d[1:n - 1] + [d[n - 1] + rn]
    dl = nuovo_modello("dual_lot_sizing")
    mu = dl.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = dl.addVars(n, name="pi")
    dl.setObjective(gp.quicksum(b[t] * mu[t] for t in R(n)), GRB.MAXIMIZE)
    dl.addConstrs((mu[t] - pi[t] <= p[t] for t in R(n)), name="rc_x")
    dl.addConstrs((M[t] * pi[t] <= q[t] for t in R(n)), name="rc_y")
    dl.addConstrs((-mu[t] + mu[t + 1] <= h[t] for t in R(n - 1)), name="rc_s")
    return dl


m1, x1, s1, y1 = modello_1(d1, p1, q1, h1, r0, rn)
print(f"  Total demand {sum(d1)}; big-M per day (residual demand): {M1}")

# ---------- 2. CONSTRUCTIVE HEURISTICS (UPPER BOUND) ----------
# (a) lot-for-lot: every day produce exactly the demand, no inventory
lot_per_lot = sum(p1[t] * d1[t] for t in R(n1)) + sum(q1)
sol_llf = {f"x[{t}]": d1[t] for t in R(n1)} | {f"y[{t}]": 1 for t in R(n1)} \
    | {f"s[{t}]": 0 for t in R(n1 - 1)}
assert ammissibile(m1, sol_llf)
print(f"  (a) lot-for-lot: a run every day, cost "
      f"{sum(p1[t] * d1[t] for t in R(n1))} of production + {sum(q1)} of set-ups = "
      f"{lot_per_lot}")
# (b) least unit cost: cover the number of days that minimises the average cost per unit
e = euristica_lotti(d1, q1[0], h1[0])
e.traccia.stampa()
sol_luc = {f"x[{t}]": e.lanci.get(t, 0) for t in R(n1)} \
    | {f"y[{t}]": 1 if t in e.lanci else 0 for t in R(n1)}
scorta = 0
for t in R(n1 - 1):
    scorta += sol_luc[f"x[{t}]"] - d1[t]
    sol_luc[f"s[{t}]"] = scorta
assert ammissibile(m1, sol_luc)
luc = sum(p1[t] * sol_luc[f"x[{t}]"] for t in R(n1)) + sum(q1[t] for t in e.lanci) \
    + sum(h1[t] * sol_luc[f"s[{t}]"] for t in R(n1 - 1))
print(f"  (b) least unit cost: runs on days {[t + 1 for t in sorted(e.lanci)]}, cost {luc}")
ub1 = min(lot_per_lot, luc)
print(f"  The better of the two: ub = {frazione(ub1)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl1 = duale_1(d1, p1, q1, h1, r0, rn)
# recipe: pi = 0 (the set-ups are given away) and mu_t = cheapest way to have one
# unit available on day t
mu = []
for t in R(n1):
    mu.append(p1[t] if t == 0 else min(mu[t - 1] + h1[t - 1], p1[t]))
mano = {f"mu[{t}]": mu[t] for t in R(n1)}
lb1, viol = valuta(dl1, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: pi = 0 (the set-ups are not charged) and mu_t = the lowest unit")
print("  cost of having one unit available on day t, that is min(mu_{t-1} + h_{t-1}, p_t):")
print("    mu = " + ", ".join(frazione(v) for v in mu))
print(f"  ->  lb = {frazione(lb1)}: the production cost if the set-ups were free.")
zlp1, zlp1r, pi1 = due_rilassamenti(m1, dl1)

# ---------- 4. OPTIMUM OF THE MILP ----------
z1 = risolvi(m1)
lanci_ott = [t + 1 for t in R(n1) if y1[t].X > 0.5]
print(f"  Optimal solution: runs on days {lanci_ott}; quantities "
      + ", ".join(frazione(x1[t].X) for t in R(n1))
      + "; inventories " + ", ".join(frazione(s1[t].X) for t in R(n1 - 1)))
riga = registra_bound("1 lot sizing with setup", ub1, lb1, zlp1, zlp1r, z1)
salva_dati(pd.DataFrame([riga]), "prod1_bound")
assert lb1 <= zlp1 <= z1 <= ub1 + 1e-9

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 1a: daily capacity of 35 litres
m, x, s, y = modello_1(d1, p1, q1, h1, r0, rn)
m.addConstrs((x[t] <= 35 for t in R(n1)), name="capacity")
varianti["1a"] = variante("1a. Daily capacity of 35 litres (x_t <= 35)", m)
# 1b: minimum lot of 25 litres when producing (semicontinuous variable)
m, x, s, y = modello_1(d1, p1, q1, h1, r0, rn)
m.addConstrs((x[t] >= 25 * y[t] for t in R(n1)), name="minimum_lot")
varianti["1b"] = variante("1b. Minimum lot of 25 litres if producing (x_t >= 25 y_t)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "prod1_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(7.0, 3.4))
giorni = list(R(1, n1 + 1))
ax.bar(giorni, [x1[t].X for t in R(n1)], color=TEAL, label="production $x_t$", width=0.55)
ax.plot(giorni, d1, "o--", color=ROSSO, label="demand $d_t$")
ax.plot(giorni[:-1], [s1[t].X for t in R(n1 - 1)], "s-", color=ARANCIO,
        label="inventory at the end of day $s_t$")
for t in lanci_ott:
    ax.annotate("run", (t, x1[t - 1].X), textcoords="offset points", xytext=(0, 6),
                ha="center", fontsize=8, color=BLU)
ax.set_xticks(giorni)
ax.set_xlabel("day")
ax.set_ylabel("litres")
ax.set_title(f"9.1: optimal plan (z = {frazione(z1)})")
ax.legend(fontsize=8, ncols=3, loc="upper left")
salva_figura(fig, "cap09_lotti_ottimo")
print("Done.")
