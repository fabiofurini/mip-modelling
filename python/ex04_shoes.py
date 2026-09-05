"""EX 4 -- Shoe production and workforce over three months (family 9).

Inventory balance, working hours proportional to production and workforce dynamics
with hirings only. It is the numerical version of problem 9.2, with the same
structure: one balance constraint per period and one conservation constraint for
the workforce.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 4. Shoes: production, inventory and hirings over three months")
d3 = [3000, 5000, 7000]      # monthly demand in pairs
s0 = 500                     # initial inventory
y0 = 100                     # workers on duty at the start
w3 = 1500                    # monthly wage of a worker
ore3 = 160                   # hours worked a month by one worker
ore_paio = 4                 # labour hours per pair
mat3 = 15                    # raw materials per pair
ass3 = 100                   # cost of hiring a worker
mag3 = 3                     # storage cost per pair at the end of the month
T = len(d3)
salva_dati(pd.DataFrame({"month": R(1, T + 1), "demand": d3}), "ex04_domanda")
netta = [d3[0] - s0] + d3[1:]
print(f"  Net demand of the first month: {d3[0]} - {s0} = {netta[0]} pairs; total to produce "
      f"{sum(netta)} pairs.")


def modello(d, s0, y0, mag=None):
    mag = mag3 if mag is None else mag
    T = len(d)
    m = nuovo_modello("shoes")
    x = m.addVars(T, name="x")                       # pairs produced
    s = m.addVars(T - 1, name="s")                   # inventory at the end of the month
    y = m.addVars(T, vtype=GRB.INTEGER, name="y")    # workers on duty
    z = m.addVars(T, vtype=GRB.INTEGER, name="z")    # workers hired
    m.setObjective(mat3 * x.sum() + mag * s.sum() + w3 * y.sum() + ass3 * z.sum(),
                   GRB.MINIMIZE)
    m.addConstr(x[0] - s[0] == d[0] - s0, name="balance[0]")
    for t in R(1, T - 1):
        m.addConstr(x[t] + s[t - 1] - s[t] == d[t], name=f"balance[{t}]")
    m.addConstr(x[T - 1] + s[T - 2] == d[T - 1], name=f"balance[{T - 1}]")
    m.addConstrs((ore3 * y[t] - ore_paio * x[t] >= 0 for t in R(T)), name="hours")
    m.addConstr(y[0] - z[0] == y0, name="workforce[0]")
    m.addConstrs((y[t] - y[t - 1] - z[t] == 0 for t in R(1, T)), name="workforce")
    return m, x, s, y, z


def duale(d, s0, y0):
    """max sum_t b_t alpha_t + y0 gamma_1  with alpha, gamma free and beta >= 0.

    Columns:  x_t: alpha_t - ore_paio beta_t <= mat
              s_t: -alpha_t + alpha_{t+1} <= mag
              y_t: hours beta_t + gamma_t - gamma_{t+1} <= w   (gamma_{T+1} = 0)
              z_t: -gamma_t <= hire
    """
    T = len(d)
    dl = nuovo_modello("dual_shoes")
    alpha = dl.addVars(T, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(T, name="beta")
    gamma = dl.addVars(T, lb=-GRB.INFINITY, name="gamma")
    b = [d[0] - s0] + list(d[1:])
    dl.setObjective(gp.quicksum(b[t] * alpha[t] for t in R(T)) + y0 * gamma[0], GRB.MAXIMIZE)
    dl.addConstrs((alpha[t] - ore_paio * beta[t] <= mat3 for t in R(T)), name="rcx")
    dl.addConstrs((-alpha[t] + alpha[t + 1] <= mag3 for t in R(T - 1)), name="rcs")
    for t in R(T):
        succ = gamma[t + 1] if t + 1 < T else 0
        dl.addConstr(ore3 * beta[t] + gamma[t] - succ <= w3, name=f"rcy[{t}]")
    dl.addConstrs((-gamma[t] <= ass3 for t in R(T)), name="rcz")
    return dl


m3, x3, s3, y3, z3 = modello(d3, s0, y0)

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# "just in time" production: every month exactly the net demand is produced, with no
# inventory, hiring as many workers as needed
def euristica(d, s0, y0):
    T = len(d)
    b = [d[0] - s0] + list(d[1:])
    x = [float(v) for v in b]
    s = [0.0] * (T - 1)
    y, z, passi = [], [], []
    organico = y0
    for t in R(T):
        serve = -(-int(ore_paio * x[t]) // ore3)     # ceil
        nuovi = max(0, serve - organico)
        organico = max(organico, serve)
        y.append(organico)
        z.append(nuovi)
        passi.append(f"month {t + 1}: {int(x[t])} pairs are produced, "
                     f"{int(ore_paio * x[t])} hours are needed, that is {serve} workers; "
                     f"{nuovi} are hired and the workforce rises to {organico}")
    return x, s, y, z, passi


x_e, s_e, y_e, z_e, passi = euristica(d3, s0, y0)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
ub3 = (mat3 * sum(x_e) + mag3 * sum(s_e) + w3 * sum(y_e) + ass3 * sum(z_e))
sol_eur = ({f"x[{t}]": x_e[t] for t in R(T)} | {f"s[{t}]": s_e[t] for t in R(T - 1)}
           | {f"y[{t}]": y_e[t] for t in R(T)} | {f"z[{t}]": z_e[t] for t in R(T)})
assert ammissibile(m3, sol_eur), sol_eur
print(f"  Cost of the heuristic solution: ub = {frazione(ub3)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl3 = duale(d3, s0, y0)
# recipe: an hour of work is worth beta = w / hours (what it really costs), so a pair
# is worth at most alpha = mat + ore_paio * beta; gamma = 0
beta_v = w3 / ore3
alpha_v = mat3 + ore_paio * beta_v
mano = {f"beta[{t}]": beta_v for t in R(T)} | {f"alpha[{t}]": alpha_v for t in R(T)}
lb3, viol = valuta(dl3, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: gamma = 0, beta_t = {w3}/{ore3} = {frazione(beta_v)} euros an hour")
print(f"  (the true cost of an hour of work) and alpha_t = {mat3} + {ore_paio} * "
      f"{frazione(beta_v)} = {frazione(alpha_v)} euros a pair.")
print(f"  lb = {frazione(alpha_v)} * {sum(netta)} = {frazione(lb3)}")
zlp3, zlp3r, _ = due_rilassamenti(m3, dl3)

# ---------- 4. OPTIMUM OF THE MILP ----------
z3v = risolvi(m3)
print("  Optimal solution:")
for t in R(T):
    scorta = s3[t].X if t < T - 1 else 0.0
    print(f"    month {t + 1}: {frazione(x3[t].X)} pairs, {int(y3[t].X)} workers "
          f"({int(z3[t].X)} hired), inventory at the end of the month {frazione(scorta)}")
riga = registra_bound("EX 4 shoes", ub3, lb3, zlp3, zlp3r, z3v)
salva_dati(pd.DataFrame([riga]), "ex04_bound")
assert lb3 <= zlp3 <= z3v <= ub3 + 1e-9

# ---------- 5. WHY PRODUCING EARLY PAYS OFF ----------
intestazione("EX 4. Storage against hiring")
print(f"  Keeping a pair in stock for one month costs {mag3} euros; hiring a worker costs")
print(f"  {ass3} euros once plus {w3} euros a month. The optimum produces early exactly to")
print("  avoid hiring at the last moment.")
prove = []
for nome, mag in [("storage at 3 euros", 3), ("storage at 20 euros", 20),
                  ("storage at 60 euros", 60)]:
    m, x, s, y, z = modello(d3, s0, y0, mag=mag)
    val = risolvi(m)
    scorte = [s[t].X for t in R(T - 1)]
    print(f"  {nome:24s} z = {frazione(val):>10}   inventories "
          + ", ".join(frazione(v) for v in scorte))
    prove.append({"variant": nome, "z": val,
                  "inventories": " ".join(str(int(v)) for v in scorte)})
salva_dati(pd.DataFrame(prove), "ex04_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.6, 3.0))
idx = list(R(T))
ax.bar([t - 0.2 for t in idx], [x_e[t] for t in idx], 0.4, color=ARANCIO, label="heuristic")
ax.bar([t + 0.2 for t in idx], [x3[t].X for t in idx], 0.4, color=TEAL, label="optimum")
ax.plot(idx, d3, marker="o", color=BLU, lw=1.6, label="demand")
ax2 = ax.twinx()
ax2.plot(idx, [y3[t].X for t in idx], marker="s", color=GRIGIO, ls="--", lw=1.4,
         label="workers (optimum)")
ax2.set_ylabel("workers")
ax.set_xticks(idx)
ax.set_xticklabels([f"month {t + 1}" for t in idx])
ax.set_ylabel("pairs")
ax.set_title(f"EX 4: optimal plan (cost {frazione(z3v)})")
ax.legend(fontsize=8, loc="upper left")
ax2.legend(fontsize=8, loc="lower right")
salva_figura(fig, "ex04_piano")
print("Done.")
