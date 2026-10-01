"""Problem 8.4 -- Hub location with maximum connection cost.

Two links: activation (aggregated, as in scheduling 7.2) and a maximum
variable z_j = max_i {c_ij : x_ij = 1} (same pattern as the processing time 7.4).
The
next-fit heuristic is the generic one from euristiche.py: hubs are the
"machines" (capacity k) and terminals the "jobs" (unit time, independent of
the machine).
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from euristiche import matrice, next_fit
from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, rilassamento, risolvi,
                 stampa_soluzione, valuta)
from stile import intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------

intestazione("4. Hub location: activation and maximum connection cost")
c4 = [[5, 10, 2], [5, 4, 6], [5, 4, 6]]   # connection cost terminal i -> hub j
f4 = [5, 6, 7]                             # activation cost of hub j
k4 = 2                                     # capacity of each hub
n, m = 3, 3
salva_dati(pd.DataFrame([{"terminal": i + 1, "hub": j + 1, "c": c4[i][j]}
                         for i in R(n) for j in R(m)]), "fam08_4_costi")
salva_dati(pd.DataFrame({"hub": R(1, m + 1), "f": f4}), "fam08_4_attivazione")


def modello_4(c, f, k):
    n, m = len(c), len(f)
    mod = nuovo_modello("hub_max")
    x = mod.addVars(n, m, vtype=GRB.BINARY, name="x")
    y = mod.addVars(m, vtype=GRB.BINARY, name="y")
    z = mod.addVars(m, name="z")
    mod.setObjective(gp.quicksum(f[j] * y[j] for j in R(m)) + z.sum(), GRB.MINIMIZE)
    mod.addConstrs((gp.quicksum(x[i, j] for j in R(m)) == 1 for i in R(n)), name="assignment")
    mod.addConstrs((-gp.quicksum(x[i, j] for i in R(n)) + k * y[j] >= 0 for j in R(m)), name="activation")
    mod.addConstrs((-c[i][j] * x[i, j] + z[j] >= 0 for i in R(n) for j in R(m)), name="maximum")
    return mod, x, y, z


def duale_4(c, f, k):
    """max sum_i alpha_i;  alpha_i - beta_j - c_ij gamma_ij <= 0;  k beta_j <= f_j;
    sum_i gamma_ij <= 1;  alpha free, beta,gamma >= 0."""
    n, m = len(c), len(f)
    dl = nuovo_modello("duale_hub")
    alpha = dl.addVars(n, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(m, name="beta")
    gamma = dl.addVars(n, m, name="gamma")
    dl.setObjective(alpha.sum(), GRB.MAXIMIZE)
    dl.addConstrs((alpha[i] - beta[j] - c[i][j] * gamma[i, j] <= 0 for i in R(n) for j in R(m)), name="rc_x")
    dl.addConstrs((k * beta[j] <= f[j] for j in R(m)), name="rc_y")
    dl.addConstrs((gp.quicksum(gamma[i, j] for i in R(n)) <= 1 for j in R(m)), name="rc_z")
    return dl


m4, x4, y4, z4 = modello_4(c4, f4, k4)
salva_modello(m4, "fam08_4_primale")

# ---------- 2. THE LP RELAXATION ----------
zlp4, zlp4r, _ = rilassamenti(m4)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------

d4 = duale_4(c4, f4, k4)
salva_modello(d4, "fam08_4_duale")
beta_mano = [f4[j] / k4 for j in R(m)]     # the largest value allowed by k*beta_j <= f_j
alpha_mano = min(beta_mano)                # must hold for EVERY hub j, not only the most convenient one
mano = {f"gamma[{i},{j}]": 0.0 for i in R(n) for j in R(m)}
mano.update({f"beta[{j}]": beta_mano[j] for j in R(m)})
mano.update({f"alpha[{i}]": alpha_mano for i in R(n)})
lb4, viol = valuta(d4, mano)
assert viol <= 1e-9, viol
print(f"Hand-built dual solution: gamma = 0, beta_j = f_j/k = {[frazione(b) for b in beta_mano]}, "
      f"alpha_i = min_j beta_j = {frazione(alpha_mano)}  ->  lb = {frazione(lb4)}")
dualita_forte(d4, zlp4)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------

print("Next-fit heuristic: hubs are filled one at a time up to k terminals,")
print("then the algorithm moves to the next one (the same generic heuristic as scheduling).")
t4 = matrice([1] * n, m)   # unit time for every terminal, independent of the hub
a4 = [k4] * m               # residual capacity of each hub
esito4 = next_fit(t4, a4)
esito4.traccia.stampa()
assert esito4.ok
ye = esito4.y
ze = [0.0] * m
for j in R(m):
    if ye[j]:
        ze[j] = max(c4[i][j] for i in R(n) if esito4.x.get((i, j)) == 1)
ub4 = sum(f4[j] * ye[j] for j in R(m)) + sum(ze)
print(f"  y = {ye}, z = {ze}  ->  ub = {frazione(ub4)}")

# ---------- 5. OPTIMAL SOLUTION OF THE MILP ----------

z4v = risolvi(m4)
print("Optimal solution of the MILP:")
stampa_soluzione(m4, solo_non_nulle=True)
riga = registra_bound("4 hub", ub4, lb4, zlp4, zlp4r, z4v, senso="min")
salva_dati(pd.DataFrame([riga]), "fam08_4_bound")

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------

varianti = {}


def variante(nome, mod):
    z = risolvi(mod)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 4a: the disaggregated links x_ij <= y_j are ADDED to the aggregated constraint
mod, x, y, z = modello_4(c4, f4, k4)
mod.addConstrs((x[i, j] <= y[j] for i in R(n) for j in R(m)), name="disaggregated_activation")
varianti["4a"] = variante("4a. Disaggregated links ADDED to the aggregated one (x_ij <= y_j)", mod)
zlp_4a, _, _ = rilassamento(mod, rafforzato=True)
zlp_base, _, _ = rilassamento(modello_4(c4, f4, k4)[0], rafforzato=True)
print(f"      relaxation: z(LP+) goes from {frazione(zlp_base)} to {frazione(zlp_4a)}: the")
print("      disaggregated links are valid inequalities implied by the aggregated one on")
print("      integer points, but not by the relaxation, and they tighten it.")

# 4a-bis: the trap. REPLACING the aggregated constraint by the disaggregated links
# alone also loses the capacity k: the model is no longer the one of the problem.
# The capacity must be kept explicitly, or one speaks of addition, not replacement.
mod, x, y, z = modello_4(c4, f4, k4)
mod.update()
mod.remove([cc for cc in mod.getConstrs() if cc.ConstrName.startswith("activation")])
mod.update()
mod.addConstrs((x[i, j] <= y[j] for i in R(n) for j in R(m)), name="disaggregated_only")
varianti["4a_without_capacity"] = variante(
    "4a'. REPLACING the aggregated one by the disaggregated links (capacity lost)", mod)
mod, x, y, z = modello_4(c4, f4, k4)
mod.update()
mod.remove([cc for cc in mod.getConstrs() if cc.ConstrName.startswith("activation")])
mod.update()
mod.addConstrs((x[i, j] <= y[j] for i in R(n) for j in R(m)), name="disaggregated_only")
mod.addConstrs((gp.quicksum(x[i, j] for i in R(n)) <= k4 for j in R(m)), name="capacity")
varianti["4a_with_capacity"] = variante(
    "4a\'\'. Correct replacement: disaggregated links + separate capacity", mod)
assert varianti["4a_without_capacity"] < varianti["4a"], "without the capacity the optimum drops"
assert varianti["4a_with_capacity"] == varianti["4a"], "with the capacity the optimum is unchanged"
# 4b: terminal 1 cannot be connected to hub 2
mod, x, y, z = modello_4(c4, f4, k4)
mod.addConstr(x[0, 1] == 0, name="terminal1_not_hub2")
varianti["4b"] = variante("4b. Terminal 1 cannot connect to hub 2 (x_12 = 0)", mod)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "fam08_4_varianti")

# ---------- 7. THE SANDWICH ON THE VARIANT 4b ----------
intestazione("4b. The sandwich on the variant: terminal 1 cannot use hub 2")

VIETATA = (0, 1)      # (terminale, hub) proibito


def modello_4b(c, f, k, vietata=VIETATA):
    mod_, xx, yy, zz = modello_4(c, f, k)
    mod_.addConstr(xx[vietata] == 0, name="connessione_vietata")
    return mod_, xx, yy, zz


def duale_4b(c, f, k, vietata=VIETATA):
    """Forbidding a connection means removing a column from the primal, hence
    removing the corresponding constraint from the dual: alpha_1 no longer has
    to stand the comparison with hub 2, and can rise."""
    nn, mm = len(c), len(f)
    dl = nuovo_modello("duale_hub_4b")
    alpha = dl.addVars(nn, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(mm, name="beta")
    gamma = dl.addVars(nn, mm, name="gamma")
    dl.setObjective(alpha.sum(), GRB.MAXIMIZE)
    dl.addConstrs((alpha[i] - beta[j] - c[i][j] * gamma[i, j] <= 0
                   for i in R(nn) for j in R(mm) if (i, j) != vietata), name="rc_x")
    dl.addConstrs((k * beta[j] <= f[j] for j in R(mm)), name="rc_y")
    dl.addConstrs((gp.quicksum(gamma[i, j] for i in R(nn)) <= 1 for j in R(mm)), name="rc_z")
    return dl


m4b, x4b, y4b, z4b = modello_4b(c4, f4, k4)
salva_modello(m4b, "fam08_4b_primale")

# -- feasible heuristic: the base one, moving the forbidden terminal --
print("Constructive heuristic: start from the solution of the base problem and, if the")
print("forbidden terminal sits on the forbidden hub, move it to the cheapest hub with room.")
ass_4b = {i: j for (i, j), v in esito4.x.items() if v == 1}
ti, hj = VIETATA
if ass_4b.get(ti) == hj:
    carichi = {j: sum(1 for q, jj in ass_4b.items() if jj == j and q != ti) for j in R(m)}
    nuovo_hub = min((j for j in R(m) if j != hj and carichi[j] < k4), key=lambda j: c4[ti][j])
    print(f"  terminal {ti + 1} was on hub {hj + 1}: it moves to hub {nuovo_hub + 1}")
    ass_4b[ti] = nuovo_hub
else:
    print(f"  terminal {ti + 1} was not on hub {hj + 1}: nothing to repair")
y_4b = [1 if any(j == q for q in ass_4b.values()) else 0 for j in R(m)]
z_4b = [max([c4[i][j] for i, q in ass_4b.items() if q == j] + [0.0]) for j in R(m)]
ub4b = sum(f4[j] * y_4b[j] for j in R(m)) + sum(z_4b)
sol_4b = ({f"x[{i},{j}]": (1 if ass_4b[i] == j else 0) for i in R(n) for j in R(m)}
          | {f"y[{j}]": y_4b[j] for j in R(m)} | {f"z[{j}]": z_4b[j] for j in R(m)})
assert ammissibile(m4b, sol_4b), "the heuristic solution of the variant must be feasible"
print(f"  ub = {frazione(ub4b)}")

# -- dual certificate: without that column, alpha_1 rises --
d4b = duale_4b(c4, f4, k4)
salva_modello(d4b, "fam08_4b_duale")
beta_4b = {j: f4[j] / k4 for j in R(m)}
# the forbidden terminal can spend one gamma on every hub left to it: each hub
# has a budget of 1 and no other terminal uses it in the recipe
mano_4b = {f"beta[{j}]": beta_4b[j] for j in R(m)}
mano_4b.update({f"gamma[{i},{j}]": 0.0 for i in R(n) for j in R(m)})
mano_4b.update({f"gamma[{ti},{j}]": 1.0 for j in R(m) if j != hj})
alpha_vietato = min(beta_4b[j] + c4[ti][j] for j in R(m) if j != hj)
alpha_altri = min(beta_4b.values())
mano_4b.update({f"alpha[{i}]": (alpha_vietato if i == ti else alpha_altri) for i in R(n)})
lb4b, viol_4b = valuta(d4b, mano_4b)
assert viol_4b <= 1e-9, viol_4b
print("Dual solution by hand: beta_j = f_j/k as in the base problem. For the free")
print("  terminals alpha_i = min_j beta_j. The forbidden terminal, instead, no longer has to")
print("  stand the comparison with the forbidden hub: it is given one gamma on each of the")
print("  hubs left to it (each hub has budget 1 and nobody else uses it), and then")
print(f"  alpha_{ti + 1} = min_(j != {hj + 1}) (beta_j + c_{ti + 1}j) = {frazione(alpha_vietato)}")
print(f"  instead of {frazione(alpha_altri)}.")
print(f"  ->  lb = {frazione(lb4b)}  (the recipe of the base problem would give "
      f"{frazione(n * alpha_altri)})")
zlp4b, zlp4br, _ = due_rilassamenti(m4b, d4b)
z4b_val = risolvi(m4b)
riga_4b = registra_bound("4b forbidden connection", ub4b, lb4b, zlp4b, zlp4br, z4b_val)
salva_dati(pd.DataFrame([riga_4b]), "fam08_4b_bound")
assert lb4b <= zlp4b <= z4b_val <= ub4b + 1e-9

# ---------- 8. FIGURES ----------

fig, ax = plt.subplots(figsize=(6.4, 3.2))
colori = ["#16324A", "#0E7490", "#CA6F1E"]
for j in R(m):
    if y4[j].X > 0.5:
        assegnati = [i + 1 for i in R(n) if x4[i, j].X > 0.5]
        ax.barh(j, z4[j].X, color=colori[j % 3], label=f"hub {j + 1}: terminals {assegnati}")
ax.set_yticks(R(m))
ax.set_yticklabels([f"hub {j + 1}" for j in R(m)])
ax.set_xlabel("maximum connection cost $z_j$")
ax.set_title(f"Optimal solution (z = {frazione(z4v)})")
ax.legend(fontsize=7, loc="lower right")
salva_figura(fig, "cap08_hub_ottimo")
print("Fine.")
