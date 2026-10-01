"""Problem 10.2 -- Combinatorial auction (set packing).

An auctioneer has n items and receives r bids: bid j asks for the subset B_j and
pays p_j, and it is all or nothing. This is pure set packing: one constraint per
item, one variable per bid. Since it is a maximisation, the heuristic gives the
lower bound and the hand-built dual the upper one: the roles swap with respect to
10.1 and 10.2.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, dualita_forte, due_rilassamenti, frazione,
                 nuovo_modello, registra_bound, rilassamenti, risolvi, stampa_lp,
                 valuta)
from stile import ARANCIO, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura
from esteso import salva_modello

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("10.2 Combinatorial auction: choosing the bids of maximum profit")
n3 = 4                                                     # items for sale
B3 = [[0], [1], [2, 3], [0, 2], [1, 3], [0, 2, 3]]         # items asked by each bid
p3 = [6, 3, 12, 12, 10, 16]                                # profit of the bid
r3 = len(p3)
salva_dati(pd.DataFrame({"bid": [j + 1 for j in R(r3)],
                         "items": ["{" + ",".join(str(i + 1) for i in B3[j]) + "}"
                                   for j in R(r3)],
                         "profit": p3}), "fam10_2_dati")


def modello_3(n, B, p, extra=None):
    r = len(p)
    m = nuovo_modello("auction")
    x = m.addVars(r, vtype=GRB.BINARY, name="x")           # 1 if the bid is accepted
    m.setObjective(gp.quicksum(p[j] * x[j] for j in R(r)), GRB.MAXIMIZE)
    m.addConstrs((gp.quicksum(x[j] for j in R(r) if i in B[j]) <= 1 for i in R(n)),
                 name="item")
    return m, x


def duale_3(n, B, p):
    """min sum_i lam_i  s.t.  sum_{i in B_j} lam_i >= p_j for every bid j, lam >= 0.

    The dual has one variable per item: lam_i is the price the auctioneer puts on
    item i, and every bid must cost at least what it pays.
    """
    r = len(p)
    dl = nuovo_modello("dual_auction")
    lam = dl.addVars(n, name="lam")
    dl.setObjective(gp.quicksum(lam[i] for i in R(n)), GRB.MINIMIZE)
    dl.addConstrs((gp.quicksum(lam[i] for i in B[j]) >= p[j] for j in R(r)), name="bid")
    return dl, lam


m3, x3 = modello_3(n3, B3, p3)
salva_modello(m3, "fam10_2_primale")
print("  The model of the instance:")
stampa_lp(m3)

# ---------- 2. THE LP RELAXATION ----------
zlp3, zlp3r, _ = rilassamenti(m3)

# ---------- 3. THE DUAL OF THE RELAXATION (LOWER BOUND) ----------
dl3, lam3 = duale_3(n3, B3, p3)
salva_modello(dl3, "fam10_2_duale")
# Hand recipe: spread every bid over its items and take the maximum,
# lam_i = max_{j : i in B_j} p_j / |B_j|. It is always feasible because for every
# bid j we have sum_{i in B_j} lam_i >= |B_j| * p_j / |B_j| = p_j.
mano = {f"lam[{i}]": max(p3[j] / len(B3[j]) for j in R(r3) if i in B3[j]) for i in R(n3)}
ub3, viol = valuta(dl3, mano)
assert viol <= 1e-9, viol
print("  Hand-built dual: lam_i = max_{j : i in B_j} p_j / |B_j| (the profit of every bid")
print("  spread over its items; the sum over B_j is then at least p_j):")
for i in R(n3):
    quote = ", ".join(f"{p3[j]}/{len(B3[j])}" for j in R(r3) if i in B3[j])
    print(f"    item {i + 1}: max({quote}) = {frazione(mano[f'lam[{i}]'])}")
print(f"  ub = sum of the prices = {frazione(ub3)}")
# for comparison: the recipe of the source notes, lam_i = max p_j over the bids
grezza = {f"lam[{i}]": max(p3[j] for j in R(r3) if i in B3[j]) for i in R(n3)}
ub_grezzo, viol_g = valuta(dl3, grezza)
assert viol_g <= 1e-9
print(f"  (with the cruder recipe lam_i = max_j p_j one would only get "
      f"{frazione(ub_grezzo)})")
dualita_forte(dl3, zlp3)

# ---------- 4. CONSTRUCTIVE HEURISTIC (UPPER BOUND) ----------
# constructive heuristic on the profit per item: the most profitable bids are accepted among those
# whose items are still free. Cost O(r log r + r n).
def euristica(n, B, p):
    r = len(p)
    x = [0] * r
    libero = [True] * n
    passi = []
    for j in sorted(R(r), key=lambda j: (-p[j] / len(B[j]), j)):
        oggetti = "{" + ",".join(str(i + 1) for i in B[j]) + "}"
        occupati = [i + 1 for i in B[j] if not libero[i]]
        if occupati:
            passi.append(f"bid {j + 1} {oggetti}, {p[j] / len(B[j]):.4g} per item: "
                         f"rejected, items {occupati} are already sold")
            continue
        x[j] = 1
        for i in B[j]:
            libero[i] = False
        passi.append(f"bid {j + 1} {oggetti}, {p[j] / len(B[j]):.4g} per item: "
                     f"accepted (profit {p[j]})")
    return x, passi


x_eur, passi = euristica(n3, B3, p3)
for k, riga in enumerate(passi, 1):
    print(f"  Step {k}. {riga}")
lb3 = sum(p3[j] * x_eur[j] for j in R(r3))
sol_eur = {f"x[{j}]": x_eur[j] for j in R(r3)}
assert ammissibile(m3, sol_eur), sol_eur
accettate = [j + 1 for j in R(r3) if x_eur[j]]
print(f"  Heuristic solution: bids {accettate}   lb = {frazione(lb3)}")

# ---------- 5. OPTIMUM OF THE MILP ----------
z3 = risolvi(m3)
ottime = [j + 1 for j in R(r3) if x3[j].X > 0.5]
venduti = sorted({i + 1 for j in R(r3) if x3[j].X > 0.5 for i in B3[j]})
print(f"  Optimal solution: bids {ottime}, items sold {venduti}, profit {frazione(z3)}")
invenduti = [i + 1 for i in R(n3) if i + 1 not in venduti]
print(f"  Unsold items: {invenduti if invenduti else 'none'}. The auctioneer sells everything,")
print("  but not because a constraint forces it: the constraints are <=, not =. With other")
print("  bids the optimal solution could leave items on the shelf.")
riga = registra_bound("3 auction", ub3, lb3, zlp3, zlp3r, z3, senso="max")
salva_dati(pd.DataFrame([riga]), "fam10_2_bound")
assert lb3 <= z3 <= zlp3r <= zlp3 <= ub3 + 1e-9

# ---------- 6. THE TWO RELAXATIONS AND INTEGRALITY ----------
intestazione("10.2 The two relaxations and the integrality of the relaxation")
print(f"  z(LP) = {frazione(zlp3)} and z(LP+) = {frazione(zlp3r)} coincide: the constraints")
print("  sum_{j : i in B_j} x_j <= 1 already imply x_j <= 1 for every bid with a non-empty")
print("  B_j. The valid inequalities x_j <= 1 are therefore redundant and do not strengthen.")
assert abs(zlp3 - zlp3r) <= 1e-9
print(f"  On this instance we also have z(LP) = z(MILP) = {frazione(z3)}: the relaxation")
print("  lands on an integer vertex. That is a lucky feature of the instance, not a property")
print("  of set packing. The minimal counterexample is the triangle: three items and three")
print("  bids asking for two of them each, all with profit 1.")
m_tri, _ = modello_3(3, [[0, 1], [1, 2], [0, 2]], [1, 1, 1])
dl_tri, _ = duale_3(3, [[0, 1], [1, 2], [0, 2]], [1, 1, 1])
z_tri = risolvi(m_tri)
zlp_tri, zlp_tri_r, _ = due_rilassamenti(m_tri, dl_tri)
print(f"  Triangle: z(LP) = {frazione(zlp_tri)} (x = 1/2 on all three) against "
      f"z(MILP) = {frazione(z_tri)}.")
assert zlp_tri > z_tri + 1e-9
salva_dati(pd.DataFrame([{"instance": "auction 10.2", "z_lp": zlp3, "z_milp": z3},
                         {"instance": "triangle", "z_lp": zlp_tri, "z_milp": z_tri}]),
           "fam10_2_triangolo")

# ---------- 7. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 3a: bids 4 and 5 come from the same bidder, who can win at most one
m, x = modello_3(n3, B3, p3)
m.addConstr(x[3] + x[4] <= 1, name="same_bidder")
varianti["2a"] = variante("2a. Bids 4 and 5 are from the same bidder (x4+x5 <= 1)", m)
# 3b: the auctioneer delivers at most two items in this round
m, x = modello_3(n3, B3, p3)
m.addConstr(gp.quicksum(len(B3[j]) * x[j] for j in R(r3)) <= 2, name="deliveries")
varianti["2b"] = variante("2b. At most two items are delivered (sum_j |B_j| x_j <= 2)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "fam10_2_varianti")

# ---------- 8. THE SANDWICH ON THE VARIANT 3b ----------
intestazione("10.2b The sandwich on the variant: at most two items delivered")
MAX_OGG = 2


def modello_3b(n, B, p, massimo=MAX_OGG):
    mm, xx = modello_3(n, B, p)
    mm.addConstr(gp.quicksum(len(B[j]) * xx[j] for j in R(len(p))) <= massimo, name="consegne")
    return mm, xx


def duale_3b(n, B, p, massimo=MAX_OGG):
    """To the dual of 10.2 one adds mu >= 0 for the constraint sum_j |B_j| x_j <= 2.
    The right-hand side is 2, so mu enters the objective, and in the column of
    every bid it appears multiplied by how many items that bid asks for."""
    rr = len(p)
    dl = nuovo_modello("duale_asta_3b")
    lam = dl.addVars(n, name="lam")
    mu = dl.addVar(name="mu")
    dl.setObjective(lam.sum() + massimo * mu, GRB.MINIMIZE)
    dl.addConstrs((gp.quicksum(lam[i] for i in B[j]) + len(B[j]) * mu >= p[j] for j in R(rr)),
                  name="rc_x")
    return dl


m3b, x3b = modello_3b(n3, B3, p3)
salva_modello(m3b, "fam10_2b_primale")

# -- feasible heuristic: the best bid that does not exceed the two items is taken --
print("Constructive heuristic: the bids in decreasing order of profit; a bid is accepted if")
print("its items are free and the total delivered stays within two.")
presi, consegnati, valore_3b = set(), 0, 0
for j in sorted(R(r3), key=lambda j: -p3[j]):
    if consegnati + len(B3[j]) > MAX_OGG:
        continue
    if any(i in presi for i in B3[j]):
        continue
    presi |= set(B3[j])
    consegnati += len(B3[j])
    valore_3b += p3[j]
    print(f"  bid {j + 1} (items {sorted(i + 1 for i in B3[j])}, profit {p3[j]}): "
          f"accepted, delivered {consegnati}")
lb3b = valore_3b
accettate_3b = [j for j in R(r3) if set(B3[j]) <= presi and len(B3[j]) <= MAX_OGG]
sol_3b = {f"x[{j}]": 0 for j in R(r3)}
presi2, cons2 = set(), 0
for j in sorted(R(r3), key=lambda j: -p3[j]):
    if cons2 + len(B3[j]) <= MAX_OGG and not (set(B3[j]) & presi2):
        sol_3b[f"x[{j}]"] = 1
        presi2 |= set(B3[j]); cons2 += len(B3[j])
assert ammissibile(m3b, sol_3b), "the heuristic solution of the variant must be feasible"
print(f"  lb = {frazione(lb3b)}")

# -- dual certificate: mu is paid twice and discounts every bid --
dl3b = duale_3b(n3, B3, p3)
salva_modello(dl3b, "fam10_2b_duale")


def valore_duale_3b(mu_val):
    lam_v = {i: max([0.0] + [(p3[j] - len(B3[j]) * mu_val) / len(B3[j])
                             for j in R(r3) if i in B3[j]]) for i in R(n3)}
    return sum(lam_v.values()) + MAX_OGG * mu_val, lam_v


candidati_3b = sorted({0.0} | {p3[j] / len(B3[j]) for j in R(r3)})
scelto_3b = min(candidati_3b, key=lambda v: valore_duale_3b(v)[0])
ub3b, lam_3b = valore_duale_3b(scelto_3b)
mano_3b = {f"lam[{i}]": lam_3b[i] for i in R(n3)} | {"mu": scelto_3b}
ub3b_val, viol_3b = valuta(dl3b, mano_3b)
assert viol_3b <= 1e-9, (viol_3b, mano_3b)
print("Dual solution by hand: with mu fixed, every bid is spread over its items net of mu,")
print("  and lam_i is the largest among the bids asking for item i. mu is tried among the")
print("  per-item profits of the bids and the lowest value is kept:")
print(f"  mu = {frazione(scelto_3b)}, lam = {[frazione(lam_3b[i]) for i in R(n3)]}")
print(f"  ->  ub = {frazione(ub3b_val)}")
zlp3b, zlp3br, _ = due_rilassamenti(m3b, dl3b)
z3b = risolvi(m3b)
riga_3b = registra_bound("2b at most two items", ub3b_val, lb3b, zlp3b, zlp3br, z3b, senso="max")
salva_dati(pd.DataFrame([riga_3b]), "fam10_2b_bound")
assert lb3b <= z3b <= zlp3b + 1e-9 <= ub3b_val + 1e-9

# ---------- 9. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.8, 3.2))
idx = list(R(r3))
colori = [TEAL if x3[j].X > 0.5 else GRIGIO for j in idx]
ax.bar(idx, p3, 0.55, color=colori)
for j in idx:
    if x_eur[j]:
        ax.plot(j, p3[j] + 0.6, marker="v", color=ARANCIO, ms=8)
ax.plot([], [], marker="v", ls="", color=ARANCIO, label="chosen by the heuristic")
ax.bar([], [], color=TEAL, label="accepted at the optimum")
ax.bar([], [], color=GRIGIO, label="rejected at the optimum")
ax.set_xticks(idx)
ax.set_xticklabels(["{" + ",".join(str(i + 1) for i in B3[j]) + "}" for j in idx])
ax.set_xlabel("items asked by the bid")
ax.set_ylabel("profit")
ax.set_title(f"10.2: heuristic {frazione(lb3)} <= optimum {frazione(z3)} <= dual "
             f"{frazione(ub3)}")
ax.legend(fontsize=8, loc="upper left")
salva_figura(fig, "cap10_asta_offerte")
print("Done.")
