"""EX 8 -- Seminars: exactly two sessions, never two consecutive hours (family 7).

A set packing on two dimensions (slot and seminar) with an exact cardinality
constraint and non-adjacency constraints between consecutive slots. The dual has
a free variable for the equality, and its simplest recipe --- "two sessions are
worth at most twice the best score" --- is in fact optimal for the relaxation.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 8. Seminars: exactly two sessions, never two consecutive hours")
p = [[8, 6, 5, 3], [7, 9, 4, 6], [5, 7, 8, 9]]
ns, nk, q = 3, 4, 2
SLOT = ["9--10", "10--11", "11--12", "12--13"]
salva_dati(pd.DataFrame([{"seminar": s + 1, "slot": k + 1, "time": SLOT[k], "p": p[s][k]}
                         for s in R(ns) for k in R(nk)]), "ex08_preferenze")


def modello(p, q):
    ns, nk = len(p), len(p[0])
    m = nuovo_modello("seminars")
    x = m.addVars(ns, nk, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(p[s][k] * x[s, k] for s in R(ns) for k in R(nk)), GRB.MAXIMIZE)
    m.addConstrs((x.sum("*", k) <= 1 for k in R(nk)), name="slot")
    m.addConstrs((x.sum(s, "*") <= 1 for s in R(ns)), name="seminar")
    m.addConstr(gp.quicksum(x[s, k] for s in R(ns) for k in R(nk)) == q, name="how_many")
    m.addConstrs((gp.quicksum(x[s, k] + x[s, k + 1] for s in R(ns)) <= 1 for k in R(nk - 1)),
                 name="consecutive")
    return m, x


def duale(p, q):
    """min sum_k alpha_k + sum_s beta_s + q gamma + sum_k delta_k
       s.t.  alpha_k + beta_s + gamma + sum_{k' : k in {k', k'+1}} delta_k' >= p_sk
       alpha, beta, delta >= 0;  gamma free."""
    ns, nk = len(p), len(p[0])
    d = nuovo_modello("dual_seminars")
    alpha = d.addVars(nk, name="alpha")
    beta = d.addVars(ns, name="beta")
    gamma = d.addVar(lb=-GRB.INFINITY, name="gamma")
    delta = d.addVars(nk - 1, name="delta")
    d.setObjective(alpha.sum() + beta.sum() + q * gamma + delta.sum(), GRB.MINIMIZE)
    for s in R(ns):
        for k in R(nk):
            vicini = [kk for kk in R(nk - 1) if k in (kk, kk + 1)]
            d.addConstr(alpha[k] + beta[s] + gamma + gp.quicksum(delta[kk] for kk in vicini)
                        >= p[s][k], name=f"rc{s}{k}")
    return d


m, x = modello(p, q)

# ---------- 2. CONSTRUCTIVE HEURISTIC (LOWER BOUND: IT IS A MAXIMISATION) ----------
def ammesse(scelte):
    for s in R(ns):
        for k in R(nk):
            if any(ss == s or kk == k or abs(kk - k) <= 1 for ss, kk in scelte):
                continue
            yield p[s][k], s, k


scelte = []
for passo in R(q):
    candidate = sorted(ammesse(scelte), reverse=True)
    if not candidate:
        break
    val, s, k = candidate[0]
    scelte.append((s, k))
    print(f"  Step {passo + 1}: the feasible session with the highest score is seminar "
          f"{s + 1} in slot {k + 1} ({SLOT[k]}), score {val}")
lb = sum(p[s][k] for s, k in scelte)
sol_eur = {f"x[{s},{k}]": 1 for s, k in scelte}
assert ammissibile(m, sol_eur), "the constructive heuristic must produce a feasible solution"
print("  Heuristic solution: " + ", ".join(f"seminar {s + 1} in slot {k + 1}" for s, k in scelte)
      + f"   lb = {frazione(lb)}")

# ---------- 3. LP RELAXATION AND DUAL (UPPER BOUND) ----------
d = duale(p, q)
pmax = max(p[s][k] for s in R(ns) for k in R(nk))
mano = {"gamma": pmax}
ub, viol = valuta(d, mano)
assert viol <= 1e-9, viol
print(f"  Dual by hand: alpha = beta = delta = 0 and gamma = max_sk p_sk = {pmax}")
print(f"  ->  ub = q gamma = {q} * {pmax} = {frazione(ub)}")
print("  Meaning: 'two sessions are attended, and none is worth more than the best one'.")
mano2 = {f"alpha[{k}]": max(p[s][k] for s in R(ns)) for k in R(nk)}
ub2, viol2 = valuta(d, mano2)
assert viol2 <= 1e-9
print(f"  Alternative recipe (gamma = 0, alpha_k = max_s p_sk): ub = {frazione(ub2)}, weaker")
zlp, zlpr, pi = due_rilassamenti(m, d)

# ---------- 4. MILP OPTIMUM AND BOUND TABLE ----------
z = risolvi(m)
ott = [(s, k) for s in R(ns) for k in R(nk) if x[s, k].X > 0.5]
print("  Optimal solution: " + ", ".join(f"seminar {s + 1} in slot {k + 1} ({SLOT[k]}, "
                                         f"score {p[s][k]})" for s, k in sorted(ott, key=lambda t: t[1])))
riga = registra_bound("EX 8 seminars", ub, lb, zlp, zlpr, z, senso="max")
salva_dati(pd.DataFrame([riga]), "ex08_bound")
assert lb <= z <= zlp + 1e-9 <= ub + 1e-9
if abs(ub - zlp) < 1e-9:
    print("  The hand-built dual coincides with z(LP): the recipe is optimal for the")
    print("  relaxation, and what gap remains belongs entirely to integrality.")

# ---------- 5. FIGURE ----------
fig, ax = plt.subplots(figsize=(7.0, 3.0))
colori = ["#0E7490", "#C0392B", "#CA6F1E"]
for s in R(ns):
    for k in R(nk):
        scelto = (s, k) in ott
        ax.add_patch(plt.Rectangle((k - 0.45, s - 0.35), 0.9, 0.7,
                                   facecolor=colori[s] if scelto else "#F4F6F7",
                                   edgecolor="#7F8C8D", lw=0.8))
        ax.annotate(str(p[s][k]), (k, s), ha="center", va="center", fontsize=10,
                    color="white" if scelto else "#16324A",
                    fontweight="bold" if scelto else "normal")
ax.set_xlim(-0.6, nk - 0.4)
ax.set_ylim(-0.6, ns - 0.4)
ax.set_xticks(R(nk))
ax.set_xticklabels([f"slot {k + 1}\n{SLOT[k]}" for k in R(nk)], fontsize=8)
ax.set_yticks(R(ns))
ax.set_yticklabels([f"seminar {s + 1}" for s in R(ns)])
ax.set_title(f"EX 8: the two chosen sessions (z = {frazione(z)})")
ax.invert_yaxis()
ax.grid(False)
salva_figura(fig, "ex08_ottimo")
print("Done.")
