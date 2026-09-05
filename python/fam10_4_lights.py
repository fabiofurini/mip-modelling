"""Problem 12.1 -- Christmas trees: configurations and boxes of lights.

Two integer decisions tied by an availability constraint: how many lights are
needed (from the chosen configurations) and how many are bought (from the boxes).
On top of that, the variety constraint "at least f different configurations",
which needs an indicator per configuration and the link with the count
(technique 3.11).
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("12.1 Christmas trees: configurations, lights and boxes")
q1 = 20                          # trees to decorate
i1 = [7, 6, 8]                   # installation cost of a configuration
u1 = [[4, 2], [2, 3], [2, 2]]    # lights of colour l required by configuration c
p1 = [100, 200]                  # cost of a box
v1 = [[10, 2], [15, 4]]          # lights of colour l contained in a box of type b
f1 = 2                           # different configurations required
nc, nl, nb = len(i1), len(u1[0]), len(p1)
salva_dati(pd.DataFrame({"configuration": R(1, nc + 1), "cost": i1,
                         "colour_1": [u[0] for u in u1], "colour_2": [u[1] for u in u1]}),
           "luci1_configurazioni")
salva_dati(pd.DataFrame({"box": R(1, nb + 1), "cost": p1,
                         "colour_1": [v[0] for v in v1], "colour_2": [v[1] for v in v1]}),
           "luci1_scatole")


def modello_1(q, i, u, p, v, f):
    nc, nl, nb = len(i), len(u[0]), len(p)
    m = nuovo_modello("lights")
    x = m.addVars(nc, vtype=GRB.INTEGER, name="x")        # trees with configuration c
    y = m.addVars(nb, vtype=GRB.INTEGER, name="y")        # boxes bought of type b
    z = m.addVars(nc, vtype=GRB.BINARY, name="z")         # configuration c used
    m.setObjective(gp.quicksum(i[c] * x[c] for c in R(nc))
                   + gp.quicksum(p[b] * y[b] for b in R(nb)), GRB.MINIMIZE)
    m.addConstr(x.sum() == q, name="trees")
    m.addConstrs((gp.quicksum(v[b][l] * y[b] for b in R(nb))
                  - gp.quicksum(u[c][l] * x[c] for c in R(nc)) >= 0 for l in R(nl)),
                 name="lights")
    m.addConstr(z.sum() >= f, name="variety")
    m.addConstrs((x[c] - z[c] >= 0 for c in R(nc)), name="used")
    return m, x, y, z


def duale_1(q, i, u, p, v, f):
    """max q alpha + f gamma

    alpha free (equality on the trees), beta_l >= 0 (availability of the lights),
    gamma >= 0 (variety), delta_c >= 0 (link x_c >= z_c). Columns:
      x_c:  alpha - sum_l u_cl beta_l + delta_c <= i_c
      y_b:  sum_l v_bl beta_l <= p_b
      z_c:  gamma - delta_c <= 0
    """
    nc, nl, nb = len(i), len(u[0]), len(p)
    dl = nuovo_modello("dual_lights")
    alpha = dl.addVar(lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(nl, name="beta")
    gamma = dl.addVar(name="gamma")
    delta = dl.addVars(nc, name="delta")
    dl.setObjective(q * alpha + f * gamma, GRB.MAXIMIZE)
    dl.addConstrs((alpha - gp.quicksum(u[c][l] * beta[l] for l in R(nl)) + delta[c] <= i[c]
                   for c in R(nc)), name="rcx")
    dl.addConstrs((gp.quicksum(v[b][l] * beta[l] for l in R(nl)) <= p[b] for b in R(nb)),
                  name="rcy")
    dl.addConstrs((gamma - delta[c] <= 0 for c in R(nc)), name="rcz")
    return dl


m1, x1, y1, z1 = modello_1(q1, i1, u1, p1, v1, f1)
print("  Price of one light, colour by colour, in each type of box:")
for b in R(nb):
    print(f"    box {b + 1}: " + ", ".join(
        f"colour {l + 1} at {frazione(p1[b] / v1[b][l])}" for l in R(nl) if v1[b][l] > 0))

# ---------- 2. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# Two phases. First the configurations: q - f + 1 trees with the cheapest one to
# install and one tree for each of the other f - 1, so that variety is met at the
# lowest installation cost. Then the boxes: while some light is missing, buy the box
# with the lowest price per missing light.
def euristica(q, i, u, p, v, f):
    nc, nl, nb = len(i), len(u[0]), len(p)
    ordine = sorted(R(nc), key=lambda c: (i[c], c))
    x = [0] * nc
    for c in ordine[1:f]:
        x[c] = 1
    x[ordine[0]] = q - (f - 1)
    altre = ", ".join(str(c + 1) for c in ordine[1:f])
    passi = [f"configurations: {x[ordine[0]]} trees with number {ordine[0] + 1} "
             f"(installation {i[ordine[0]]} each) and one tree with configuration "
             f"{altre}, the second cheapest to install"]
    serve = [sum(u[c][l] * x[c] for c in R(nc)) for l in R(nl)]
    passi.append("lights needed: " + ", ".join(f"colour {l + 1} -> {serve[l]}"
                                               for l in R(nl)))
    y = [0] * nb
    while True:
        manca = [max(0, serve[l] - sum(v[b][l] * y[b] for b in R(nb))) for l in R(nl)]
        if max(manca) == 0:
            break
        # price per still-missing light: only the useful lights are counted
        b = min(R(nb), key=lambda b: (p[b] / max(1e-9, sum(min(v[b][l], manca[l])
                                                           for l in R(nl))), b))
        y[b] += 1
        passi.append(f"{manca} are missing: a box {b + 1} is bought (cost {p[b]}); "
                     f"boxes {y}")
    return x, y, passi


x_eur, y_eur, passi = euristica(q1, i1, u1, p1, v1, f1)
for k, riga in enumerate(passi[:4], 1):
    print(f"  Step {k}. {riga}")
print(f"  ... ({len(passi) - 4} further purchases of the same kind)")
print(f"  Step {len(passi)}. {passi[-1]}")
ub1 = sum(i1[c] * x_eur[c] for c in R(nc)) + sum(p1[b] * y_eur[b] for b in R(nb))
sol_eur = ({f"x[{c}]": x_eur[c] for c in R(nc)} | {f"y[{b}]": y_eur[b] for b in R(nb)}
           | {f"z[{c}]": 1 if x_eur[c] > 0 else 0 for c in R(nc)})
assert ammissibile(m1, sol_eur), sol_eur
print(f"  Heuristic solution: trees {x_eur}, boxes {y_eur}   ub = {frazione(ub1)}")
print("  The heuristic picks the configuration that is cheapest to install, number 2, which")
print("  is however the greediest for the expensive colour: the boxes pay the bill. It is the")
print("  typical mistake of a constructive heuristic that looks at a single cost item.")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl1 = duale_1(q1, i1, u1, p1, v1, f1)
# recipe: gamma = delta = 0; a single colour is priced, at the highest price per light
# that no box can beat; then every tree costs at least alpha = min_c (i_c + its lights)
migliore, mano, scelto = float("-inf"), None, None
for l in R(nl):
    prezzo = min(p1[b] / v1[b][l] for b in R(nb) if v1[b][l] > 0)
    prova = {f"beta[{l}]": prezzo}
    prova["alpha"] = min(i1[c] + u1[c][l] * prezzo for c in R(nc))
    val, viol = valuta(dl1, prova)
    if viol <= 1e-9 and val > migliore:
        migliore, mano, scelto = val, prova, l
lb1, viol = valuta(dl1, mano)
assert viol <= 1e-9, viol
prezzo = mano[f"beta[{scelto}]"]
print(f"  Hand-built dual: gamma = delta = 0 and a single colour priced. On colour "
      f"{scelto + 1}")
print(f"  both types of box give the same price per light, {frazione(prezzo)}: it is the")
print("  largest value of beta compatible with sum_l v_bl beta_l <= p_b.")
print("  Then every tree costs at least alpha = min_c (i_c + u_c" + str(scelto + 1)
      + " * beta) = " + ", ".join(f"{i1[c]} + {u1[c][scelto]} * {frazione(prezzo)} = "
                                  f"{frazione(i1[c] + u1[c][scelto] * prezzo)}"
                                  for c in R(nc)))
print(f"  alpha = {frazione(mano['alpha'])}  ->  lb = {q1} * alpha = {frazione(lb1)}")
zlp1, zlp1r, _ = due_rilassamenti(m1, dl1)

# ---------- 4. OPTIMUM OF THE MILP ----------
z1v = risolvi(m1)
print("  Optimal solution: "
      + ", ".join(f"{int(x1[c].X)} trees with configuration {c + 1}" for c in R(nc)
                  if x1[c].X > 0.5)
      + "; boxes "
      + ", ".join(f"{int(y1[b].X)} of type {b + 1}" for b in R(nb) if y1[b].X > 0.5))
for l in R(nl):
    serve = sum(u1[c][l] * x1[c].X for c in R(nc))
    compra = sum(v1[b][l] * y1[b].X for b in R(nb))
    print(f"    colour {l + 1}: {int(serve)} lights needed, {int(compra)} bought")
riga = registra_bound("1 lights", ub1, lb1, zlp1, zlp1r, z1v)
salva_dati(pd.DataFrame([riga]), "luci1_bound")
assert lb1 <= zlp1 <= z1v <= ub1 + 1e-9

# ---------- 5. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 1a: all three configurations are wanted
m, x, y, z = modello_1(q1, i1, u1, p1, v1, 3)
varianti["1a"] = variante("1a. All three configurations must appear (f = 3)", m)
# 1b: every configuration used must decorate at least three trees (minimum lot)
m, x, y, z = modello_1(q1, i1, u1, p1, v1, f1)
m.addConstrs((x[c] - 3 * z[c] >= 0 for c in R(nc)), name="minimum_lot")
varianti["1b"] = variante("1b. Every configuration used decorates at least three trees", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "luci1_varianti")

# ---------- 6. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.0))
etichette = ["heuristic", "optimum"]
inst = [sum(i1[c] * x_eur[c] for c in R(nc)),
        sum(i1[c] * x1[c].X for c in R(nc))]
scat = [sum(p1[b] * y_eur[b] for b in R(nb)),
        sum(p1[b] * y1[b].X for b in R(nb))]
ax.barh(R(2), inst, 0.5, color=TEAL, label="installation")
ax.barh(R(2), scat, 0.5, left=inst, color=ARANCIO, label="boxes of lights")
for k in R(2):
    ax.annotate(f"{frazione(inst[k] + scat[k])}", (inst[k] + scat[k] + 40, k), va="center",
                fontsize=9)
ax.axvline(lb1, color=BLU, ls="--", lw=1.4)
ax.annotate(f"dual bound {frazione(lb1)}", (lb1, 1.55), ha="center", fontsize=8, color=BLU)
ax.set_yticks(R(2))
ax.set_yticklabels(etichette)
ax.set_xlim(0, max(inst[k] + scat[k] for k in R(2)) * 1.18)
ax.set_xlabel("cost (euros)")
ax.set_title("12.1: where the cost goes")
ax.legend(fontsize=8, loc="lower right")
ax.invert_yaxis()
salva_figura(fig, "cap10_luci_ottimo")
print("Done.")
