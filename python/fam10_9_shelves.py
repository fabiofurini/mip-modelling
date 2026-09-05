"""Problem 11.4 -- Books on shelves: minimising the sum of the heights.

Assignment with a capacity (the width of the shelf) and a maximum variable per
shelf (technique 3.5): the height of a shelf is that of the tallest book on it.
It also shows that the order in which the heuristic looks at the objects can lead
it into a dead end.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import (ammissibile, due_rilassamenti, frazione, nuovo_modello, registra_bound,
                 risolvi, valuta)
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("11.4 Books on shelves: minimising the sum of the heights")
w4 = [3, 5, 4, 6]      # width of the books
h4 = [8, 5, 7, 4]      # height of the books
c4 = 10                # width of every shelf
n4, m4 = len(w4), 2    # books and shelves
salva_dati(pd.DataFrame({"book": R(1, n4 + 1), "width": w4, "height": h4}),
           "scaffali4_dati")
print(f"  Total width of the books: {sum(w4)}; overall capacity: {m4} * {c4} = {m4 * c4}.")


def modello_4(w, h, c, m):
    n = len(w)
    mod = nuovo_modello("shelves")
    x = mod.addVars(n, m, vtype=GRB.BINARY, name="x")
    y = mod.addVars(m, name="y")            # height of the shelf
    mod.setObjective(y.sum(), GRB.MINIMIZE)
    mod.addConstrs((x.sum(b, "*") == 1 for b in R(n)), name="book")
    mod.addConstrs((gp.quicksum(w[b] * x[b, s] for b in R(n)) <= c for s in R(m)),
                   name="width")
    mod.addConstrs((y[s] - h[b] * x[b, s] >= 0 for b in R(n) for s in R(m)), name="height")
    return mod, x, y


def duale_4(w, h, c, m):
    """max sum_b alpha_b + c sum_s beta_s   with  beta_s <= 0  and  gamma >= 0,
       column of x_bs: alpha_b + w_b beta_s - h_b gamma_bs <= 0,
       column of y_s:  sum_b gamma_bs <= 1."""
    n = len(w)
    dl = nuovo_modello("dual_shelves")
    alpha = dl.addVars(n, lb=-GRB.INFINITY, name="alpha")
    beta = dl.addVars(m, lb=-GRB.INFINITY, ub=0.0, name="beta")
    gamma = dl.addVars(n, m, name="gamma")
    dl.setObjective(alpha.sum() + c * beta.sum(), GRB.MAXIMIZE)
    dl.addConstrs((gamma.sum("*", s) <= 1 for s in R(m)), name="rcy")
    dl.addConstrs((alpha[b] + w[b] * beta[s] - h[b] * gamma[b, s] <= 0
                   for b in R(n) for s in R(m)), name="rcx")
    return dl


m4mod, x4, y4 = modello_4(w4, h4, c4, m4)

# ---------- 2. TWO ORDERS FOR THE SAME HEURISTIC ----------
def first_fit(w, h, c, m, ordine, etichetta):
    """Every book on the first shelf where it fits; if it fits nowhere the heuristic
    fails and returns None."""
    n = len(w)
    dove, residuo, passi = {}, [c] * m, []
    for b in ordine:
        posti = [s for s in R(m) if residuo[s] >= w[b]]
        if not posti:
            passi.append(f"book {b + 1} (width {w[b]}): it fits on no shelf "
                         f"(residuals {residuo}) -> the heuristic fails")
            print(f"  {etichetta}")
            for k, riga in enumerate(passi, 1):
                print(f"    Step {k}. {riga}")
            return None, None, passi
        s = posti[0]
        dove[b] = s
        residuo[s] -= w[b]
        passi.append(f"book {b + 1} (width {w[b]}, height {h[b]}) on shelf {s + 1}; "
                     f"residuals {residuo}")
    altezze = [max((h[b] for b in R(n) if dove[b] == s), default=0) for s in R(m)]
    print(f"  {etichetta}")
    for k, riga in enumerate(passi, 1):
        print(f"    Step {k}. {riga}")
    print(f"    shelf heights {altezze}, sum {sum(altezze)}")
    return dove, altezze, passi


ordine_h = sorted(R(n4), key=lambda b: (-h4[b], b))
dove_h, alt_h, _ = first_fit(w4, h4, c4, m4, ordine_h,
                             "Order by decreasing height (books 1, 3, 2, 4):")
assert dove_h is None, "on this instance the height order must get stuck"
print("  The height order ignores the widths and gets stuck. The right criterion for a")
print("  capacity constraint is the width.")
ordine_w = sorted(R(n4), key=lambda b: (-w4[b], b))
dove_w, alt_w, _ = first_fit(w4, h4, c4, m4, ordine_w,
                             "Order by decreasing width (books 4, 2, 3, 1):")
ub4 = sum(alt_w)
sol_eur = {f"x[{b},{dove_w[b]}]": 1 for b in R(n4)} | {f"y[{s}]": alt_w[s] for s in R(m4)}
assert ammissibile(m4mod, sol_eur), sol_eur
print(f"  ub = {frazione(ub4)}")

# ---------- 3. LP RELAXATION AND DUAL (LOWER BOUND) ----------
dl4 = duale_4(w4, h4, c4, m4)
# recipe: beta = 0, and all the gamma "weight" is concentrated on the tallest book
alto = max(R(n4), key=lambda b: h4[b])
mano = ({f"gamma[{alto},{s}]": 1.0 for s in R(m4)}
        | {f"alpha[{alto}]": float(h4[alto])})
lb_lp, viol = valuta(dl4, mano)
assert viol <= 1e-9, viol
print(f"  Hand-built dual: beta = 0, gamma_bs = 1 only for the tallest book (number")
print(f"  {alto + 1}, height {h4[alto]}) and alpha equal to {h4[alto]} on that book, zero on")
print(f"  the others. The dual constraints become {h4[alto]} <= {h4[alto]} and 0 <= 0  ->  "
      f"lb = {frazione(lb_lp)}.")
print("  It is the obvious remark: the shelf holding the tallest book is at least as tall as")
print(f"  that book, so the sum of the heights is at least {h4[alto]}.")
zlp4, zlp4r, _ = due_rilassamenti(m4mod, dl4)

# ---------- 4. A STRONGER COMBINATORIAL BOUND ----------
intestazione("11.4 The combinatorial bound: at least two shelves are used")
usati = -(-sum(w4) // c4)     # integer division rounding up
print(f"  The total width is {sum(w4)} and every shelf holds {c4}: at least")
print(f"  ceil({sum(w4)} / {c4}) = {usati} shelves must be non-empty.")
altre = sorted(h4[b] for b in R(n4) if b != alto)
lb4 = h4[alto] + min(altre)
print(f"  One of them holds the tallest book and measures at least {h4[alto]}; the other one")
print(f"  holds at least one book, so it measures at least {min(altre)}, the smallest")
print("  remaining height.")
print(f"  lb = {h4[alto]} + {min(altre)} = {frazione(lb4)}, better than the dual bound "
      f"{frazione(lb_lp)}.")
salva_dati(pd.DataFrame([{"argument": "dual of the LP relaxation", "bound": lb_lp},
                         {"argument": "shelves used and minimum heights", "bound": lb4}]),
           "scaffali4_argomento")

# ---------- 5. OPTIMUM OF THE MILP ----------
z4 = risolvi(m4mod)
for s in R(m4):
    libri = [b + 1 for b in R(n4) if x4[b, s].X > 0.5]
    largh = sum(w4[b] for b in R(n4) if x4[b, s].X > 0.5)
    print(f"  Shelf {s + 1}: books {libri}, width {largh}/{c4}, height {frazione(y4[s].X)}")
riga = registra_bound("4 shelves", ub4, lb4, zlp4, zlp4r, z4)
salva_dati(pd.DataFrame([riga]), "scaffali4_bound")
assert lb4 <= z4 <= ub4 + 1e-9

# ---------- 6. ADDITIONAL MODELLING QUESTIONS ----------
varianti = {}


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


# 4a: one more shelf
m, x, y = modello_4(w4, h4, c4, 3)
varianti["4a"] = variante("4a. The library buys a third shelf (m = 3)", m)
print("       the optimum does not change: an empty shelf has height zero and costs nothing,")
print("       but splitting the books over three shelves means paying three heights, not two.")
# 4b: wider shelves
m, x, y = modello_4(w4, h4, 12, m4)
varianti["4b"] = variante("4b. The shelves are 12 wide instead of 10", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}),
           "scaffali4_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.4, 3.2))
for s in R(m4):
    sx = 0.0
    for b in R(n4):
        if x4[b, s].X > 0.5:
            ax.bar(sx + w4[b] / 2, h4[b], w4[b] * 0.92, bottom=s * 10, color=TEAL)
            ax.annotate(str(b + 1), (sx + w4[b] / 2, s * 10 + 1), ha="center", fontsize=8,
                        color="white")
            sx += w4[b]
    ax.plot([0, c4], [s * 10 + y4[s].X, s * 10 + y4[s].X], color=ARANCIO, lw=1.6)
    ax.annotate(f"height {frazione(y4[s].X)}", (c4 + 0.2, s * 10 + y4[s].X), fontsize=8,
                va="center", color=ARANCIO)
    ax.plot([c4, c4], [s * 10, s * 10 + 9], color=GRIGIO, ls="--", lw=1.2)
ax.set_xlim(0, c4 + 3.6)
ax.set_yticks([1, 11])
ax.set_yticklabels(["shelf 1", "shelf 2"])
ax.set_xlabel("width")
ax.set_title(f"11.4: sum of the heights {frazione(z4)}")
salva_figura(fig, "cap10_scaffali_ottimo")
print("Done.")
