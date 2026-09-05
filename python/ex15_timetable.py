"""EX 15 -- Timetable of a music school (family 11).

Four afternoons of three hours each, twelve lesson hours to place: the timetable
is a partition of the twelve slots. The model uses the count of the instruments
per day (technique 3.11), the precedences between consecutive hours (3.9) and the
soft constraints with penalties (3.13).

The starting model contains an instructive mistake: the link between the lesson
and the instrument indicator is written in one direction only, and the variety
constraint becomes empty. We expose it by solving the wrong model, then fix it.

On the data of the exercise, with the corrected model, there is a timetable that
violates no preference: the optimum is zero and the certificate is immediate,
because the costs are all non-negative. The two variants show what happens as soon
as the preferences get tighter: in the first one, counting the available slots
gives a positive lower bound; in the second, the model becomes infeasible.
"""
import gurobipy as gp
import pandas as pd
from gurobipy import GRB

from mip import ammissibile, frazione, nuovo_modello, risolvi, rilassamento, valuta
from stile import ARANCIO, BLU, GRIGIO, TEAL, intestazione, plt, salva_dati, salva_figura

R = range

# ---------- 1. MODEL AND INSTANCE ----------
intestazione("EX 15. Music school timetable: minimising the violated preferences")
GIORNI = ["Monday", "Tuesday", "Wednesday", "Thursday"]
ORE = [1, 2, 3]
STRUM = ["guitar", "violin", "piano", "harp"]
h14 = [6, 3, 2, 1]              # hours to place per instrument
nd, nt, ni = len(GIORNI), len(ORE), len(STRUM)
PIANO, ARPA = 2, 3
print(f"  Hours to place: {sum(h14)}; slots available: {nd} * {nt} = {nd * nt}.")
print("  The two figures coincide: every slot of the timetable holds exactly one lesson.")


def costi(extra_chitarra=()):
    """c[d][t][i] = 1 if the slot violates a preference of the teacher of i."""
    c = [[[0] * ni for _ in R(nt)] for _ in R(nd)]
    for d in R(nd):
        for t in R(nt):
            if t == 0 and d in (0, 1):
                c[d][t][0] = 1                      # guitar: hour 1 of Monday and Tuesday
            if t in extra_chitarra:
                c[d][t][0] = 1                      # extra preferences of the guitar
            if t == 1 and d in (2, 3):
                c[d][t][1] = 1                      # violin: hour 2 of Wednesday and Thursday
            if t == 2:
                c[d][t][2] = 1                      # piano: never at hour 3
            if d == 1:
                c[d][t][3] = 1                      # harp: never on Tuesday
    return c


c14 = costi()
salva_dati(pd.DataFrame([{"day": GIORNI[d], "hour": ORE[t], "instrument": STRUM[i],
                          "cost": c14[d][t][i]}
                         for d in R(nd) for t in R(nt) for i in R(ni)]), "ex15_costi")


def modello(h, c, minimo_strumenti=2, legame_doppio=True):
    """With `legame_doppio=False` one gets the model of the source draft."""
    mod = nuovo_modello("timetable")
    x = mod.addVars(nd, nt, ni, vtype=GRB.BINARY, name="x")
    y = mod.addVars(nd, ni, vtype=GRB.BINARY, name="y")
    mod.setObjective(gp.quicksum(c[d][t][i] * x[d, t, i]
                                 for d in R(nd) for t in R(nt) for i in R(ni)), GRB.MINIMIZE)
    mod.addConstrs((x.sum("*", "*", i) == h[i] for i in R(ni)), name="hours")
    mod.addConstrs((x.sum(d, t, "*") <= 1 for d in R(nd) for t in R(nt)), name="slot")
    mod.addConstrs((y.sum(d, "*") >= minimo_strumenti for d in R(nd)), name="variety")
    mod.addConstrs((x[d, t, i] - y[d, i] <= 0 for d in R(nd) for t in R(nt) for i in R(ni)),
                   name="activate")
    if legame_doppio:
        # without this direction y_di may be 1 even if instrument i does not appear
        mod.addConstrs((y[d, i] - x.sum(d, "*", i) <= 0 for d in R(nd) for i in R(ni)),
                       name="activate_reverse")
    mod.addConstrs((x[d, t, PIANO] + x[d, t + 1, ARPA] <= 1
                    for d in R(nd) for t in R(nt - 1)), name="conflict1")
    mod.addConstrs((x[d, t, ARPA] + x[d, t + 1, PIANO] <= 1
                    for d in R(nd) for t in R(nt - 1)), name="conflict2")
    return mod, x, y


m14, x14, y14 = modello(h14, c14)


def stampa_orario(valore):
    for d in R(nd):
        riga = []
        for t in R(nt):
            chi = [STRUM[i] for i in R(ni) if valore(d, t, i) > 0.5]
            pen = [i for i in R(ni) if valore(d, t, i) > 0.5 and c14[d][t][i]]
            riga.append((chi[0] if chi else "-") + ("*" if pen else ""))
        print(f"    {GIORNI[d]:11s} " + " | ".join(f"{s:10s}" for s in riga))


# ---------- 2. A ONE-WAY VARIETY CONSTRAINT IS EMPTY ----------
intestazione("EX 15. Why the variety constraint needs both directions")
m_err, x_err, y_err = modello(h14, c14, legame_doppio=False)
z_err = risolvi(m_err)
print("  With the link x_dti <= y_di alone the solver returns this timetable:")
stampa_orario(lambda d, t, i: x_err[d, t, i].X)
strumenti_giorno = [sum(1 for i in R(ni) if any(x_err[d, t, i].X > 0.5 for t in R(nt)))
                    for d in R(nd)]
print("  Instruments actually present: "
      + ", ".join(f"{GIORNI[d]} {strumenti_giorno[d]}" for d in R(nd)))
poveri = [GIORNI[d] for d in R(nd) if strumenti_giorno[d] < 2]
print(f"  There are days with a single instrument ({', '.join(poveri)}), and yet the")
print("  constraint sum_i y_di >= 2 is satisfied: it is enough to set y_di = 1 without")
print("  teaching. The link x_dti <= y_di says \"if there is a lesson then the indicator is")
print("  on\", not the converse. One also needs y_di <= sum_t x_dti, that is technique 3.10")
print("  (if and only if).")
assert poveri, "the model without the second direction must allow single-instrument days"
salva_dati(pd.DataFrame({"day": GIORNI, "instruments_wrong_model": strumenti_giorno}),
           "ex15_varieta")

# ---------- 3. A FEASIBLE SOLUTION BUILT BY HAND ----------
# Rule: the guitar fills hours 2 and 3 of the first three days, avoiding hour 1 of
# Monday and Tuesday; the piano goes at hour 1 (never at hour 3); the harp on
# Thursday (never on Tuesday); the violin takes the remaining slots, avoiding hour 2
# of Wednesday and Thursday.
piano_orario = {
    (0, 0): PIANO, (0, 1): 0, (0, 2): 0,
    (1, 0): 1, (1, 1): 0, (1, 2): 0,
    (2, 0): PIANO, (2, 1): 0, (2, 2): 0,
    (3, 0): 1, (3, 1): ARPA, (3, 2): 1,
}
sol_eur = {f"x[{d},{t},{i}]": 1 for (d, t), i in piano_orario.items()}
for (d, t), i in piano_orario.items():
    sol_eur[f"y[{d},{i}]"] = 1
assert ammissibile(m14, sol_eur), sol_eur
ub14 = sum(c14[d][t][i] for (d, t), i in piano_orario.items())
print("  Timetable built by hand (the asterisk marks a violated preference):")
stampa_orario(lambda d, t, i: 1 if piano_orario.get((d, t)) == i else 0)
for i in R(ni):
    assert sum(1 for v in piano_orario.values() if v == i) == h14[i]
print(f"  Preferences violated: {ub14}  ->  ub = {frazione(ub14)}")

# ---------- 4. THE LOWER BOUND ----------
print("  All the costs c_dti are 0 or 1, so the objective is a sum of non-negative terms:")
print("  z >= 0 with no dual needed. The hand-built timetable is worth 0, so it is optimal.")
print("  The dual of the relaxation cannot do better:")
zlp14, _, _ = rilassamento(m14, rafforzato=False)
zlp14r, _, _ = rilassamento(m14, rafforzato=True)
lb14 = 0.0
print(f"    z(LP) = {frazione(zlp14)}   z(LP+) = {frazione(zlp14r)}")
assert abs(zlp14) <= 1e-9

# ---------- 5. OPTIMUM OF THE MILP ----------
z14 = risolvi(m14)
print("  Optimal timetable found by the solver:")
stampa_orario(lambda d, t, i: x14[d, t, i].X)
print(f"  ub = {frazione(ub14)}   lb = {frazione(lb14)}   z(LP) = {frazione(zlp14)}   "
      f"z(LP+) = {frazione(zlp14r)}   z(MILP) = {frazione(z14)}")
salva_dati(pd.DataFrame([{"problem": "EX 15 timetable", "ub": ub14, "lb": lb14,
                          "z_lp": zlp14, "z_lp_rafforzato": zlp14r, "z_milp": z14}]),
           "ex15_bound")
salva_dati(pd.DataFrame([{"day": GIORNI[d], "hour": ORE[t], "instrument": STRUM[i]}
                         for d in R(nd) for t in R(nt) for i in R(ni)
                         if x14[d, t, i].X > 0.5]), "ex15_ottimo")
assert abs(z14) <= 1e-9

# ---------- 6. VARIANTS ----------
intestazione("EX 15. What happens if the preferences get tighter")
# 14a: the guitar teacher would rather not teach at hours 1 and 2 of any day
c_a = costi(extra_chitarra=(0, 1))
libere = sum(1 for d in R(nd) for t in R(nt) if c_a[d][t][0] == 0)
print("  14a. The guitar teacher would rather not teach at hours 1 and 2 of any day.")
print(f"       Only {libere} slots stay penalty-free for the guitar, but the hours to place")
print(f"       are {h14[0]}: at least {h14[0] - libere} lessons will violate the preference.")
print("       It is a lower bound read off the data alone.")
m, x, y = modello(h14, c_a)
z_a = risolvi(m)
print(f"       z = {frazione(z_a)}, which matches the bound: the count is exact.")
assert z_a >= h14[0] - libere - 1e-9
# 14b: every day must have at least three different instruments
print("  14b. Every day must have at least three different instruments.")
print("       With three hours a day and three different instruments the guitar can take at")
print(f"       most one slot a day, that is {nd} in total, but the guitar hours are {h14[0]}.")
print("       The model is infeasible, and one proves it by counting.")
m, x, y = modello(h14, c14, minimo_strumenti=3)
m.optimize()
stato = {GRB.INFEASIBLE: "INFEASIBLE", GRB.OPTIMAL: "OPTIMAL"}.get(m.Status, str(m.Status))
print(f"       Gurobi returns the status {stato}, as expected.")
assert m.Status == GRB.INFEASIBLE
salva_dati(pd.DataFrame([{"variant": "14a. guitar free only at hour 3", "z": z_a},
                         {"variant": "14b. three instruments a day", "z": float("nan")}]),
           "ex15_varianti")

# ---------- 7. FIGURE ----------
fig, ax = plt.subplots(figsize=(6.6, 3.0))
colori = {0: TEAL, 1: BLU, 2: ARANCIO, 3: GRIGIO}
for d in R(nd):
    for t in R(nt):
        for i in R(ni):
            if x14[d, t, i].X > 0.5:
                ax.add_patch(plt.Rectangle((t, nd - 1 - d), 1, 1, color=colori[i]))
                ax.annotate(STRUM[i], (t + 0.5, nd - 1 - d + 0.5), ha="center", va="center",
                            fontsize=8, color="white")
for i in R(ni):
    ax.plot([], [], color=colori[i], lw=6, label=f"{STRUM[i]} ({h14[i]} h)")
ax.set_xlim(0, nt)
ax.set_ylim(0, nd)
ax.set_xticks([t + 0.5 for t in R(nt)])
ax.set_xticklabels([f"hour {o}" for o in ORE])
ax.set_yticks([nd - 1 - d + 0.5 for d in R(nd)])
ax.set_yticklabels(GIORNI)
ax.set_title(f"EX 15: optimal timetable, {frazione(z14)} preferences violated")
ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4)
salva_figura(fig, "ex15_orario")
print("Done.")
