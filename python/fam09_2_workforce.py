"""Problem 9.2 -- Production and workforce: two equivalent formulations.

The same decision written twice: with the *hirings* z_t (formulation A) or with
the *workforce* y_t (formulation B). We prove that they have the same set of
feasible plans and the same optimum, and we compare the relaxations. This is the
theme of chapter 4: two formulations may be compared only after proving that they
describe the same integer set.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 rilassamento, risolvi, valuta)
from stile import ARANCIO, BLU, ROSSO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("9.2 Production and workforce: hirings (A) or workforce (B)")
d2 = [60, 100, 140]        # demand of the three months (pairs)
p2 = [15, 15, 15]          # production cost per pair
h2 = [3, 3]                # storage cost at the end of the month
w2, r2, g2, u2, m2, r0 = 1500, 160, 4, 100, 2, 0
n2 = len(d2)
salva_dati(pd.DataFrame({"month": R(1, n2 + 1), "demand": d2, "cost_pair": p2}), "prod2_dati")
print(f"  {m2} workers at the start, {r2} h a month each, {g2} h per pair: the initial")
print(f"  capacity is {m2 * r2 // g2} pairs a month. Wage {w2}, hiring {u2}.")


def modello_A(d, p, h, w, r, g, u, m0, r0):
    """Formulation A: z_t = how many workers are hired at the start of month t."""
    n = len(d)
    mm = nuovo_modello("workforce_A")
    x = mm.addVars(n, vtype=GRB.INTEGER, name="x")
    s = mm.addVars(n - 1, vtype=GRB.INTEGER, name="s")
    z = mm.addVars(n, vtype=GRB.INTEGER, name="z")
    mm.setObjective(gp.quicksum(p[t] * x[t] for t in R(n))
                    + gp.quicksum(h[t] * s[t] for t in R(n - 1))
                    + gp.quicksum((u + w * (n - t)) * z[t] for t in R(n)), GRB.MINIMIZE)
    mm.addConstr(x[0] - s[0] == d[0] - r0, name="balance[0]")
    mm.addConstrs((x[t] + s[t - 1] - s[t] == d[t] for t in R(1, n - 1)), name="balance")
    mm.addConstr(x[n - 1] + s[n - 2] == d[n - 1], name=f"balance[{n - 1}]")
    mm.addConstrs((-g * x[t] + gp.quicksum(r * z[j] for j in R(t + 1)) >= -r * m0
                   for t in R(n)), name="hours")
    return mm, x, s, z


def modello_B(d, p, h, w, r, g, u, m0, r0):
    """Formulation B: y_t = how many workers are employed in month t (workforce)."""
    n = len(d)
    mm = nuovo_modello("workforce_B")
    x = mm.addVars(n, vtype=GRB.INTEGER, name="x")
    s = mm.addVars(n - 1, vtype=GRB.INTEGER, name="s")
    y = mm.addVars(n, vtype=GRB.INTEGER, name="y")
    # the workforce pays the wage every month; the hirings are the increments y_t - y_{t-1}
    mm.setObjective(gp.quicksum(p[t] * x[t] for t in R(n))
                    + gp.quicksum(h[t] * s[t] for t in R(n - 1))
                    + gp.quicksum(w * y[t] for t in R(n))
                    + u * (y[n - 1] - m0), GRB.MINIMIZE)   # total hirings = y_n - m0
    mm.addConstr(x[0] - s[0] == d[0] - r0, name="balance[0]")
    mm.addConstrs((x[t] + s[t - 1] - s[t] == d[t] for t in R(1, n - 1)), name="balance")
    mm.addConstr(x[n - 1] + s[n - 2] == d[n - 1], name=f"balance[{n - 1}]")
    mm.addConstrs((-g * x[t] + r * y[t] >= 0 for t in R(n)), name="hours")
    mm.addConstr(y[0] >= m0, name="initial_workforce")
    mm.addConstrs((-y[t - 1] + y[t] >= 0 for t in R(1, n)), name="no_layoffs")
    return mm, x, s, y


def duale_A(d, p, h, w, r, g, u, m0, r0):
    """max sum_t b_t mu_t - r m0 sum_t nu_t;  mu_t - g nu_t <= p_t;
    -mu_t + mu_{t+1} <= h_t;  r sum_{t >= j} nu_t <= u + w (n - j);  mu free, nu >= 0."""
    n = len(d)
    b = [d[0] - r0] + d[1:n - 1] + [d[n - 1]]
    dl = nuovo_modello("dual_workforce")
    mu = dl.addVars(n, lb=-GRB.INFINITY, name="mu")
    nu = dl.addVars(n, name="nu")
    dl.setObjective(gp.quicksum(b[t] * mu[t] for t in R(n))
                    - r * m0 * gp.quicksum(nu[t] for t in R(n)), GRB.MAXIMIZE)
    dl.addConstrs((mu[t] - g * nu[t] <= p[t] for t in R(n)), name="rc_x")
    dl.addConstrs((-mu[t] + mu[t + 1] <= h[t] for t in R(n - 1)), name="rc_s")
    dl.addConstrs((r * gp.quicksum(nu[t] for t in R(j, n)) <= u + w * (n - j) for j in R(n)),
                  name="rc_z")
    return dl


mA, xA, sA, zA = modello_A(d2, p2, h2, w2, r2, g2, u2, m2, r0)
mB, xB, sB, yB = modello_B(d2, p2, h2, w2, r2, g2, u2, m2, r0)
costante_A = m2 * w2 * n2          # the wage of the initial workers, outside model A
zA_val = risolvi(mA) + costante_A
zB_val = risolvi(mB)
print(f"  Formulation A (hirings):   z = {frazione(zA_val)} "
      f"(of which {costante_A} of wages of the initial workers, a constant term)")
print(f"  Formulation B (workforce): z = {frazione(zB_val)}")
assert abs(zA_val - zB_val) < 1e-6, (zA_val, zB_val)
print("  The two optima coincide: the two formulations describe the same problem.")
print("  Plan A: production " + ", ".join(frazione(xA[t].X) for t in R(n2))
      + "; hirings " + ", ".join(frazione(zA[t].X) for t in R(n2)))
print("  Plan B: production " + ", ".join(frazione(xB[t].X) for t in R(n2))
      + "; workforce " + ", ".join(frazione(yB[t].X) for t in R(n2)))

# ---------- 2. THE EQUIVALENCE, VERIFIED ----------
intestazione("9.2 The equivalence between the two formulations, verified")
print("  The correspondence is y_t = m0 + sum_{j <= t} z_j, that is z_t = y_t - y_{t-1}")
print("  (with y_0 = m0). On the optimal plans:")
yA = [m2 + sum(round(zA[j].X) for j in R(t + 1)) for t in R(n2)]
print("    from A: implied workforce = " + ", ".join(str(v) for v in yA))
print("    from B: workforce         = " + ", ".join(str(round(yB[t].X)) for t in R(n2)))
zB_implicite = [round(yB[0].X) - m2] + [round(yB[t].X) - round(yB[t - 1].X) for t in R(1, n2)]
print("    from B: implied hirings   = " + ", ".join(str(v) for v in zB_implicite))
assert sum(v * (u2 + w2 * (n2 - t)) for t, v in enumerate(zB_implicite)) + costante_A \
    == sum(round(zA[t].X) * (u2 + w2 * (n2 - t)) for t in R(n2)) + costante_A
print("  The staff cost is the same: A charges every hiring once for all the months that")
print("  remain, B charges the workforce month by month. Same total, counted two ways.")

# ---------- 3. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
intestazione("9.2 Heuristic, dual and bounds")
# constructive heuristic: produce the demand of the month, and hire only when the hours are not enough
organico, assunzioni, prod = m2, [0] * n2, []
for t in R(n2):
    prod.append(d2[t])
    servono = -(-g2 * d2[t] // r2)               # ceil
    if organico < servono:
        assunzioni[t] = servono - organico
        organico = servono
    print(f"  Month {t + 1}: {d2[t]} pairs are produced, "
          f"ceil({g2} * {d2[t]} / {r2}) = {servono} workers are needed; workforce "
          f"{organico - assunzioni[t]} -> {assunzioni[t]} are hired")
ub2 = sum(p2[t] * prod[t] for t in R(n2)) \
    + sum(assunzioni[t] * (u2 + w2 * (n2 - t)) for t in R(n2)) + costante_A
sol_eur = {f"x[{t}]": prod[t] for t in R(n2)} | {f"z[{t}]": assunzioni[t] for t in R(n2)} \
    | {f"s[{t}]": 0 for t in R(n2 - 1)}
assert ammissibile(mA, sol_eur)
print(f"  Cost of the heuristic: ub = {frazione(ub2)}")

# ---------- 4. DUAL AND LOWER BOUND ----------
dl2 = duale_A(d2, p2, h2, w2, r2, g2, u2, m2, r0)
# recipe: nu = 0 (the hours are not charged) and mu_t = cheapest way to have a pair
# available in month t
mu = []
for t in R(n2):
    mu.append(p2[t] if t == 0 else min(mu[t - 1] + h2[t - 1], p2[t]))
mano = {f"mu[{t}]": mu[t] for t in R(n2)}
lb2_var, viol = valuta(dl2, mano)
assert viol <= 1e-9, viol
lb2 = lb2_var + costante_A
print("  Hand-built dual: nu = 0 (working hours are not charged) and")
print("  mu_t = min(mu_{t-1} + h, p_t)")
print(f"    mu = " + ", ".join(frazione(v) for v in mu)
      + f"  ->  lb = {frazione(lb2_var)} + {costante_A} = {frazione(lb2)}")
zlp2, zlp2r, _ = due_rilassamenti(mA, dl2)
zlp2, zlp2r = zlp2 + costante_A, zlp2r + costante_A
riga = registra_bound("2 workforce", ub2, lb2, zlp2, zlp2r, zA_val)
salva_dati(pd.DataFrame([riga]), "prod2_bound")
assert lb2 <= zlp2 <= zA_val <= ub2 + 1e-9

# ---------- 5. COMPARING THE RELAXATIONS OF THE TWO FORMULATIONS ----------
zlpA, _, _ = rilassamento(mA, rafforzato=True)
zlpB, _, _ = rilassamento(mB, rafforzato=True)
print(f"  Relaxations: A -> {frazione(zlpA + costante_A)}   B -> {frazione(zlpB)}   "
      f"z(MILP) = {frazione(zA_val)}")
salva_dati(pd.DataFrame([{"formulation": "A (hirings)", "z_lp": zlpA + costante_A,
                          "z_milp": zA_val},
                         {"formulation": "B (workforce)", "z_lp": zlpB, "z_milp": zB_val}]),
           "prod2_formulazioni")

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m, costante=0.0):
    z = risolvi(m) + costante
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 2a: hiring costs much more (3000 instead of 100)
m, x, s, y = modello_B(d2, p2, h2, w2, r2, g2, 3000, m2, r0)
varianti["2a"] = variante("2a. A hiring costs 3000 euros instead of 100", m)
print("     workforce: " + ", ".join(str(round(y[t].X)) for t in R(n2))
      + ";  production: " + ", ".join(str(round(x[t].X)) for t in R(n2)))
# 2b: overtime, up to 40 extra hours per worker a month, at 25 euros an hour
m, x, s, y = modello_B(d2, p2, h2, w2, r2, g2, u2, m2, r0)
o = m.addVars(n2, name="o")
m.update()
for t in R(n2):
    m.chgCoeff(m.getConstrByName(f"hours[{t}]"), o[t], 1.0)   # the available hours grow
m.addConstrs((o[t] <= 40 * y[t] for t in R(n2)), name="max_overtime")
m.setObjective(m.getObjective() + gp.quicksum(25 * o[t] for t in R(n2)), GRB.MINIMIZE)
varianti["2b"] = variante("2b. Overtime: up to 40 h per worker, 25 euros an hour", m)
print("     overtime used: " + ", ".join(frazione(o[t].X) for t in R(n2))
      + "  (none: producing early and storing costs less)")
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "prod2_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(7.0, 3.2))
mesi = list(R(1, n2 + 1))
ax.bar(mesi, [xB[t].X for t in R(n2)], color=TEAL, width=0.55, label="production $x_t$")
ax.plot(mesi, d2, "o--", color=ROSSO, label="demand $d_t$")
ax2 = ax.twinx()
ax2.step(mesi, [yB[t].X for t in R(n2)], where="mid", color=BLU, lw=2, label="workforce $y_t$")
ax2.set_ylabel("workers", color=BLU)
ax2.set_ylim(0, max(yB[t].X for t in R(n2)) + 1.5)
ax2.grid(False)
ax.set_xticks(mesi)
ax.set_xlabel("month")
ax.set_ylabel("pairs")
ax.set_title(f"9.2: optimal plan (z = {frazione(zB_val)})")
ax.legend(fontsize=8, loc="upper left")
ax2.legend(fontsize=8, loc="lower right")
salva_figura(fig, "cap09_manodopera_ottimo")
print("Done.")
