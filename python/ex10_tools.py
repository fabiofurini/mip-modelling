"""EX 10 -- CNC tools: operation selection with a limited magazine (family 8).

Disaggregated activation the other way round: an operation runs only if *all* of
its tools are loaded, and the magazine holds at most four. It is a maximisation,
so the heuristic gives the lower bound and the dual the upper one.

The archive draft proposed alpha = 2000 with all multipliers at 900: that dual
solution is *not feasible*, because some tools serve more than two operations.
The recipe used here is different and it is checked.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 10. CNC tools: which operations to run with at most four tools")
pr = [2000, 1500, 1800, 1700, 800]
T = [[0, 2, 3, 4], [0, 1, 5], [0, 1, 2, 4], [1, 3, 4], [4, 5]]
no, nu, K = 5, 6, 4
salva_dati(pd.DataFrame([{"operation": i + 1,
                          "tools": ", ".join(str(j + 1) for j in T[i]),
                          "profit": pr[i]} for i in R(no)]), "ex10_operazioni")


def modello(pr, T, K):
    no, nu = len(pr), max(max(t) for t in T) + 1
    m = nuovo_modello("cnc_tools")
    x = m.addVars(no, vtype=GRB.BINARY, name="x")
    y = m.addVars(nu, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(pr[i] * x[i] for i in R(no)), GRB.MAXIMIZE)
    m.addConstr(y.sum() <= K, name="magazine")
    for i in R(no):
        for j in T[i]:
            m.addConstr(x[i] - y[j] <= 0, name=f"link[{i},{j}]")
    return m, x, y


def duale(pr, T, K):
    """min K alpha;  sum_{j in T_i} beta_ij >= p_i;  sum_{i : j in T_i} beta_ij <= alpha;
    alpha, beta >= 0."""
    no, nu = len(pr), max(max(t) for t in T) + 1
    d = nuovo_modello("dual_cnc_tools")
    alpha = d.addVar(name="alpha")
    beta = d.addVars([(i, j) for i in R(no) for j in T[i]], name="beta")
    d.setObjective(K * alpha, GRB.MINIMIZE)
    d.addConstrs((gp.quicksum(beta[i, j] for j in T[i]) >= pr[i] for i in R(no)), name="rc_x")
    d.addConstrs((gp.quicksum(beta[i, j] for i in R(no) if j in T[i]) <= alpha for j in R(nu)),
                 name="rc_y")
    return d


m, x, y = modello(pr, T, K)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND: IT IS A MAXIMISATION) ----------
carichi, eseguite = set(), []
for i in sorted(R(no), key=lambda i: -pr[i]):
    nuovi = set(T[i]) - carichi
    if len(carichi) + len(nuovi) <= K:
        carichi |= nuovi
        eseguite.append(i)
        print(f"  Operation {i + 1} (profit {pr[i]}, tools "
              + ", ".join(str(j + 1) for j in T[i])
              + f"): {len(nuovi)} new ones are needed, the magazine reaches {len(carichi)} <= {K}: it runs")
    else:
        print(f"  Operation {i + 1} (profit {pr[i]}): {len(nuovi)} new tools would be needed, "
              f"the magazine would reach {len(carichi) + len(nuovi)} > {K}: discarded")
lb = sum(pr[i] for i in eseguite)
sol_eur = {f"x[{i}]": 1 for i in eseguite} | {f"y[{j}]": 1 for j in carichi}
assert ammissibile(m, sol_eur)
print("  Heuristic solution: operations " + ", ".join(str(i + 1) for i in sorted(eseguite))
      + " with tools " + ", ".join(str(j + 1) for j in sorted(carichi))
      + f"   lb = {frazione(lb)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d = duale(pr, T, K)
mano = {f"beta[{i},{j}]": pr[i] / len(T[i]) for i in R(no) for j in T[i]}
carico = {j: sum(mano[f"beta[{i},{j}]"] for i in R(no) if j in T[i]) for j in R(nu)}
mano["alpha"] = max(carico.values())
ub, viol = valuta(d, mano)
assert viol <= 1e-9, viol
print("  Dual by hand: beta_ij = p_i / |T_i| (the profit spread over the tools it needs)")
for i in R(no):
    print(f"    operation {i + 1}: {pr[i]} / {len(T[i])} = "
          f"{frazione(pr[i] / len(T[i]))} on each of its tools")
print("  Load of each tool: " + ", ".join(f"{j + 1}: {frazione(carico[j])}" for j in R(nu)))
utensile_critico = max(carico, key=carico.get)
print(f"  The largest is tool {utensile_critico + 1}, so alpha = "
      f"{frazione(mano['alpha'])} and ub = {K} alpha = {frazione(ub)}")
bozza = {f"beta[{i},{j}]": 900 for i in R(no) for j in T[i]} | {"alpha": 2000}
_, viol_bozza = valuta(d, bozza)
assert viol_bozza > 1e-6
peggiore = max(R(nu), key=lambda j: sum(900 for i in R(no) if j in T[i]))
print("  Check of the draft's recipe (alpha = 2000, all beta = 900): NOT feasible,")
print(f"  largest violation {frazione(viol_bozza)}. Tool {peggiore + 1} serves "
      f"{sum(1 for i in R(no) if peggiore in T[i])} operations, so it receives "
      f"{sum(900 for i in R(no) if peggiore in T[i])} > 2000.")
zlp, zlpr, pi = due_rilassamenti(m, d)

# ---------- 4. MILP OPTIMUM AND BOUND TABLE ----------
z = risolvi(m)
op_ott = [i for i in R(no) if x[i].X > 0.5]
ut_ott = [j for j in R(nu) if y[j].X > 0.5]
print("  Optimal solution: operations " + ", ".join(str(i + 1) for i in op_ott)
      + " with tools " + ", ".join(str(j + 1) for j in ut_ott)
      + f"   z(MILP) = {frazione(z)}")
riga = registra_bound("EX 10 CNC tools", ub, lb, zlp, zlpr, z, senso="max")
salva_dati(pd.DataFrame([riga]), "ex10_bound")
assert lb <= z <= zlp + 1e-9 <= ub + 1e-9
print(f"  The sandwich: {frazione(lb)} <= z(MILP) = {frazione(z)} <= z(LP) = {frazione(zlp)} "
      f"<= ub = {frazione(ub)}")
print("  Here the relaxation is very weak: in the continuous problem one can load 'a bit'")
print("  of every tool and run fractions of all the operations.")

# ---------- 5. FIGURE ----------
fig, ax = plt.subplots(figsize=(7.0, 3.2))
for i in R(no):
    for j in R(nu):
        serve = j in T[i]
        colore = ("#0E7490" if i in op_ott else "#F4F6F7") if serve else "white"
        ax.add_patch(plt.Rectangle((j - 0.45, i - 0.4), 0.9, 0.8, facecolor=colore,
                                   edgecolor="#7F8C8D" if serve else "#E5E8E8", lw=0.8))
for j in ut_ott:
    ax.annotate("loaded", (j, no - 0.35), ha="center", va="bottom", fontsize=7.5,
                color="#C0392B")
ax.set_xlim(-0.6, nu - 0.4)
ax.set_ylim(-0.6, no + 0.1)
ax.set_xticks(R(nu))
ax.set_xticklabels([f"tool {j + 1}" for j in R(nu)], fontsize=8)
ax.set_yticks(R(no))
ax.set_yticklabels([f"op. {i + 1} ({pr[i]})" for i in R(no)], fontsize=8)
ax.set_title(f"EX 10: the operations run (teal) and the {K} tools loaded (z = {frazione(z)})")
ax.invert_yaxis()
ax.grid(False)
salva_figura(fig, "ex10_ottimo")
print("Done.")
