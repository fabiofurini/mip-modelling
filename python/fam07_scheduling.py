"""Chapter 7 — Assignment and scheduling (seven MILP models).

For every problem: instance data, model in gurobipy, constructive heuristic
(upper bound), LP relaxation and dual with a hand-built dual solution
(lower bound), MILP optimum, table of bounds; then the additional modelling
questions (variants), solved.

Contents:
  1. Minimum-cost assignment with availability (GAP)
  2. Machines with a fixed usage cost
  3. Job selection with revenues and fixed-cost machines
  4. Parallel jobs: processing time of the machines (maximum variables)
  5. One machine, job classes with setup
  6. One machine, classes with completion bonus and "if and only if" reduction
  7. One machine, total tardiness: sequencing with big-M
  8. Additional modelling questions
  9. Figures
"""
import gurobipy as gp
import numpy as np
import pandas as pd
from gurobipy import GRB

from euristiche import best_fit, first_fit, matrice, next_fit
from mip import (ammissibile, frazione, nuovo_modello, rilassamento, risolvi,
                 stampa_soluzione, tabella_bound, valuta)
from stile import (ARANCIO, BLU, CICLO, GRIGIO, ROSSO, TEAL, VERDE, intestazione, plt,
                   salva_dati, salva_figura)

R = range
bound = []          # one row per problem: ub, lb, z(LP), z(MILP)


def registra(nome, ub, lb, zlp, zlp_r, zmilp, senso="min"):
    bound.append({"problem": nome, "ub": ub, "lb": lb, "z_lp": zlp, "z_lp_rafforzato": zlp_r,
                  "z_milp": zmilp})
    print(tabella_bound(ub, lb, zlp, zmilp, senso, zlp_r))


def due_rilassamenti(m, d):
    """Pure z(LP) (= optimum of the hand-written dual) and the solver's strengthened z(LP+)."""
    zlp, _, pi = rilassamento(m, rafforzato=False)
    zlp_r, _, _ = rilassamento(m, rafforzato=True)
    zd = risolvi(d)
    assert abs(zlp - zd) <= 1e-6, (zlp, zd)
    print(f"Dual optimum = z(LP) (strong duality): {frazione(zd)};  strengthened relaxation "
          f"with x <= 1: z(LP+) = {frazione(zlp_r)}")
    return zlp, zlp_r, pi


# ======================================================================
# 1. MINIMUM-COST ASSIGNMENT WITH AVAILABILITY (GAP)
# ======================================================================
intestazione("1. Minimum-cost assignment: n jobs, k machines, availability a_m")
t1 = [[2, 1, 3], [3, 4, 2], [4, 5, 3]]
c1 = [[5, 10, 2], [5, 4, 6], [5, 4, 6]]
a1 = [5, 6, 7]
n, k = 3, 3
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t1[j][m], "c": c1[j][m]}
                         for j in R(n) for m in R(k)]), "sched1_lavori")
salva_dati(pd.DataFrame({"machine": R(1, k + 1), "a": a1}), "sched1_macchine")


def modello_1(t, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("assegnamento")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    m.setObjective(gp.quicksum(c[j][mm] * x[j, mm] for j in R(n) for mm in R(k)), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
    m.addConstrs((gp.quicksum(t[j][mm] * x[j, mm] for j in R(n)) <= a[mm] for mm in R(k)),
                 name="disponibilita")
    return m, x


def duale_1(t, c, a):
    """Dual of the LP relaxation: max sum mu_j + sum a_m pi_m, mu_j + t_jm pi_m <= c_jm, pi <= 0."""
    n, k = len(t), len(a)
    d = nuovo_modello("duale_assegnamento")
    mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
    d.setObjective(mu.sum() + gp.quicksum(a[mm] * pi[mm] for mm in R(k)), GRB.MAXIMIZE)
    d.addConstrs((mu[j] + t[j][mm] * pi[mm] <= c[j][mm] for j in R(n) for mm in R(k)), name="rc")
    return d


def valore_1(e, c):
    return sum(c[j][mm] for (j, mm) in e.x)


m1, x1 = modello_1(t1, c1, a1)
print("Constructive heuristics:")
e_next = next_fit(t1, a1)
e_first = first_fit(t1, a1)
e_best = best_fit(t1, a1, lambda j, mm, ra: c1[j][mm], "cost")
for nome, e in [("next-fit", e_next), ("first-fit", e_first), ("best-fit (minimum cost)", e_best)]:
    print(f"  {nome:26s} ub = {valore_1(e, c1)}   assignment "
          + ", ".join(f"x[{j + 1}][{mm + 1}]" for (j, mm) in sorted(e.x)))
print("Step-by-step run of the best-fit:")
e_best.traccia.stampa()
ub1 = valore_1(e_best, c1)
sol_eur = {f"x[{j},{mm}]": 1 for (j, mm) in e_best.x}
assert ammissibile(m1, sol_eur)

d1 = duale_1(t1, c1, a1)
# hand-built dual solution: pi = 0, mu_j = min_m c_jm
mano = {f"mu[{j}]": min(c1[j]) for j in R(n)}
lb1, viol = valuta(d1, mano)
assert viol <= 1e-9, viol
print(f"Hand-built dual solution: pi = 0, mu_j = min_m c_jm = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(n)) + f"  ->  lb = {frazione(lb1)}")
zlp1, zlp1r, pi_lp = due_rilassamenti(m1, d1)
print("Duals of the relaxation read from Gurobi:", {kk: round(v, 4) for kk, v in pi_lp.items()})
z1 = risolvi(m1)
print("Optimal solution of the MILP:")
stampa_soluzione(m1, solo_non_nulle=True)
registra("1 assignment", ub1, lb1, zlp1, zlp1r, z1)
ott1 = {(j, mm) for j in R(n) for mm in R(k) if x1[j, mm].X > 0.5}

# ======================================================================
# 2. MACHINES WITH A FIXED USAGE COST
# ======================================================================
intestazione("2. Fixed cost per used machine: activation variables y_m")
t2 = [[6, 5, 3], [5, 10, 2], [20, 13, 10]]
c2 = [8, 7, 5]
a2 = [25, 20, 12]
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t2[j][m]}
                         for j in R(3) for m in R(3)]), "sched2_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "c": c2, "a": a2}), "sched2_macchine")


def modello_2(t, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("costo_fisso")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(c[mm] * y[mm] for mm in R(k)), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
    m.addConstrs((-gp.quicksum(t[j][mm] * x[j, mm] for j in R(n)) + a[mm] * y[mm] >= 0
                  for mm in R(k)), name="link")
    return m, x, y


def duale_2(t, c, a):
    """max sum mu_j;  mu_j - t_jm pi_m <= 0;  a_m pi_m <= c_m;  pi >= 0, mu libere."""
    n, k = len(t), len(a)
    d = nuovo_modello("duale_costo_fisso")
    mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(k, name="pi")
    d.setObjective(mu.sum(), GRB.MAXIMIZE)
    d.addConstrs((mu[j] - t[j][mm] * pi[mm] <= 0 for j in R(n) for mm in R(k)), name="rc_x")
    d.addConstrs((a[mm] * pi[mm] <= c[mm] for mm in R(k)), name="rc_y")
    return d


def valore_2(e, c):
    return sum(c[mm] * y for mm, y in enumerate(e.y))


m2, x2, y2 = modello_2(t2, c2, a2)
print("Constructive heuristics:")
eur2 = [("next-fit", next_fit(t2, a2)),
        ("first-fit", first_fit(t2, a2)),
        ("best-fit (minimum time)", best_fit(t2, a2, lambda j, mm, ra: t2[j][mm], "time")),
        ("first-fit on opened machines", first_fit(t2, a2, solo_aperte=True)),
        ("best-fit on opened (tightest fit)", best_fit(t2, a2, lambda j, mm, ra: ra[mm] - t2[j][mm],
                                                      "slack", solo_aperte=True))]
for nome, e in eur2:
    print(f"  {nome:34s} ub = {valore_2(e, c2):3d}   machines used "
          + str([mm + 1 for mm, y in enumerate(e.y) if y]))
print("Step-by-step run of the minimum-time best-fit:")
eur2[2][1].traccia.stampa()
ub2 = min(valore_2(e, c2) for _, e in eur2)
d2 = duale_2(t2, c2, a2)
mano = {f"pi[{mm}]": c2[mm] / a2[mm] for mm in R(3)}
mano.update({f"mu[{j}]": min(t2[j][mm] * c2[mm] / a2[mm] for mm in R(3)) for j in R(3)})
lb2, viol = valuta(d2, mano)
assert viol <= 1e-9
print("Hand-built dual solution: pi_m = c_m/a_m = " + ", ".join(frazione(c2[mm] / a2[mm]) for mm in R(3))
      + ";  mu_j = min_m t_jm pi_m = " + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3))
      + f"  ->  lb = {frazione(lb2)}")
zlp2, zlp2r, _ = due_rilassamenti(m2, d2)
z2 = risolvi(m2)
print("Optimal solution of the MILP:")
stampa_soluzione(m2, solo_non_nulle=True)
registra("2 fixed cost", ub2, lb2, zlp2, zlp2r, z2)

# the same instance with the disaggregated link constraints x_jm <= y_m: stronger relaxation
m2d, x2d, y2d = modello_2(t2, c2, a2)
m2d.addConstrs((x2d[j, mm] <= y2d[mm] for j in R(3) for mm in R(3)), name="disaggregated")
zlp2d, _, _ = rilassamento(m2d, rafforzato=True)
print(f"Strengthened relaxation with the disaggregated links x_jm <= y_m: z(LP+) = {frazione(zlp2d)} "
      f"(with the aggregated link only: {frazione(zlp2r)}) — the disaggregated formulation is stronger")

# ======================================================================
# 3. JOB SELECTION WITH REVENUES AND FIXED-COST MACHINES
# ======================================================================
intestazione("3. Job selection: maximum profit = revenues - fixed costs")
t3 = [25, 40, 75]
r3 = [10, 15, 30]
c3 = [20, 30, 15]
a3 = [105, 110, 100]
salva_dati(pd.DataFrame({"job": R(1, 4), "t": t3, "r": r3}), "sched3_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "c": c3, "a": a3}), "sched3_macchine")


def modello_3(t, r, c, a):
    n, k = len(t), len(a)
    m = nuovo_modello("selezione")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(r[j] * x[j, mm] for j in R(n) for mm in R(k))
                   - gp.quicksum(c[mm] * y[mm] for mm in R(k)), GRB.MAXIMIZE)
    m.addConstrs((x.sum(j, "*") <= 1 for j in R(n)), name="al_piu_una")
    m.addConstrs((gp.quicksum(t[j] * x[j, mm] for j in R(n)) - a[mm] * y[mm] <= 0 for mm in R(k)),
                 name="link")
    return m, x, y


def duale_3(t, r, c, a):
    """min sum mu_j;  mu_j + t_j pi_m >= r_j;  -a_m pi_m >= -c_m;  mu, pi >= 0."""
    n, k = len(t), len(a)
    d = nuovo_modello("duale_selezione")
    mu = d.addVars(n, name="mu")
    pi = d.addVars(k, name="pi")
    d.setObjective(mu.sum(), GRB.MINIMIZE)
    d.addConstrs((mu[j] + t[j] * pi[mm] >= r[j] for j in R(n) for mm in R(k)), name="rc_x")
    d.addConstrs((-a[mm] * pi[mm] >= -c[mm] for mm in R(k)), name="rc_y")
    return d


def valore_3(e, r, c):
    return sum(r[j] for (j, mm) in e.x) - sum(c[mm] * y for mm, y in enumerate(e.y))


m3, x3, y3 = modello_3(t3, r3, c3, a3)
T3 = matrice(t3, 3)
eur3 = [("next-fit (skips if it does not fit)", next_fit(T3, a3, salta=True)),
        ("first-fit", first_fit(T3, a3, salta=True)),
        ("best-fit (fullest machine)", best_fit(T3, a3, lambda j, mm, ra: ra[mm], "ra", salta=True))]
print("Constructive heuristics (here they give a LOWER bound: maximisation problem):")
for nome, e in eur3:
    print(f"  {nome:32s} lb = {valore_3(e, r3, c3):3d}")
print("Step-by-step run of the best-fit:")
eur3[2][1].traccia.stampa()
lb3 = max(valore_3(e, r3, c3) for _, e in eur3)
d3 = duale_3(t3, r3, c3, a3)
mano = {f"pi[{mm}]": c3[mm] / a3[mm] for mm in R(3)}
mano.update({f"mu[{j}]": max([0] + [r3[j] - t3[j] * c3[mm] / a3[mm] for mm in R(3)]) for j in R(3)})
ub3, viol = valuta(d3, mano)
assert viol <= 1e-9
print("Hand-built dual solution: pi_m = c_m/a_m; mu_j = max{0, r_j - t_j pi_m} = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  ub = {frazione(ub3)}")
zlp3, zlp3r, _ = due_rilassamenti(m3, d3)
z3 = risolvi(m3)
print("Optimal solution of the MILP:")
stampa_soluzione(m3, solo_non_nulle=True)
registra("3 selection", ub3, lb3, zlp3, zlp3r, z3, senso="max")

# ======================================================================
# 4. PARALLEL JOBS: PROCESSING TIME = MAXIMUM
# ======================================================================
intestazione("4. Parallel jobs: y_m = maximum of the times of the assigned jobs")
t4 = [[6, 5, 3], [5, 10, 2], [20, 13, 10]]
p4 = [1, 2, 2]
salva_dati(pd.DataFrame([{"job": j + 1, "machine": m + 1, "t": t4[j][m]}
                         for j in R(3) for m in R(3)]), "sched4_lavori")
salva_dati(pd.DataFrame({"machine": R(1, 4), "p": p4}), "sched4_macchine")


def modello_4(t, p):
    n, k = len(t), len(p)
    m = nuovo_modello("parallelo")
    x = m.addVars(n, k, vtype=GRB.BINARY, name="x")
    y = m.addVars(k, name="y")
    m.setObjective(y.sum(), GRB.MINIMIZE)
    m.addConstrs((x.sum(j, "*") == 1 for j in R(n)), name="assegna")
    m.addConstrs((x.sum("*", mm) <= p[mm] for mm in R(k)), name="cardinalita")
    m.addConstrs((-t[j][mm] * x[j, mm] + y[mm] >= 0 for j in R(n) for mm in R(k)), name="massimo")
    return m, x, y


def duale_4(t, p):
    """max sum mu_j + sum p_m pi_m;  mu_j + pi_m - t_jm lam_jm <= 0;  sum_j lam_jm <= 1."""
    n, k = len(t), len(p)
    d = nuovo_modello("duale_parallelo")
    mu = d.addVars(n, lb=-GRB.INFINITY, name="mu")
    pi = d.addVars(k, lb=-GRB.INFINITY, ub=0.0, name="pi")
    lam = d.addVars(n, k, name="lam")
    d.setObjective(mu.sum() + gp.quicksum(p[mm] * pi[mm] for mm in R(k)), GRB.MAXIMIZE)
    d.addConstrs((mu[j] + pi[mm] - t[j][mm] * lam[j, mm] <= 0 for j in R(n) for mm in R(k)), name="rc_x")
    d.addConstrs((lam.sum("*", mm) <= 1 for mm in R(k)), name="rc_y")
    return d


def euristica_4(t, p):
    """Next-fit on the number of jobs: a machine is filled up to p_m jobs, then the next one."""
    n, k = len(t), len(p)
    x, y, cm, cnt, passi = {}, [0.0] * k, 0, 0, []
    for j in R(n):
        if cnt == p[cm]:
            if cm == k - 1:
                return None
            cm, cnt = cm + 1, 0
        x[(j, cm)] = 1
        cnt += 1
        y[cm] = max(y[cm], t[j][cm])
        passi.append(f"Job {j + 1} on machine {cm + 1} (assigned jobs {cnt} <= p = {p[cm]}): "
                     f"y[{cm + 1}] = max(y[{cm + 1}], t[{j + 1}][{cm + 1}] = {t[j][cm]}) = {y[cm]:g}.")
    return x, y, passi


m4, x4, y4 = modello_4(t4, p4)
xe, ye, passi = euristica_4(t4, p4)
print("Next-fit heuristic on the cardinalities:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub4 = sum(ye)
print(f"  ub = {frazione(ub4)}")
d4 = duale_4(t4, p4)
mano = {f"lam[{j},{mm}]": 1 / 3 for j in R(3) for mm in R(3)}
mano.update({f"mu[{j}]": min(t4[j][mm] / 3 for mm in R(3)) for j in R(3)})
lb4, viol = valuta(d4, mano)
assert viol <= 1e-9
print("Hand-built dual solution: lam_jm = 1/3, pi = 0, mu_j = min_m t_jm/3 = "
      + ", ".join(frazione(mano[f"mu[{j}]"]) for j in R(3)) + f"  ->  lb = {frazione(lb4)}")
zlp4, zlp4r, _ = due_rilassamenti(m4, d4)
z4 = risolvi(m4)
print("Optimal solution of the MILP:")
stampa_soluzione(m4, solo_non_nulle=True)
registra("4 parallel", ub4, lb4, zlp4, zlp4r, z4)

# ======================================================================
# 5. ONE MACHINE, JOB CLASSES WITH SETUP
# ======================================================================
intestazione("5. Job classes with setup cost and time: y_c activates the class")
r5 = [10, 6, 8, 6, 7, 9, 5]
t5 = [5, 10, 8, 6, 9, 5, 6]
J5 = [[0, 1], [2, 3], [4, 5, 6]]       # classes (0-based)
f5 = [10, 5, 4]
s5 = [10, 12, 6]
a5 = 50
salva_dati(pd.DataFrame({"job": R(1, 8), "r": r5, "t": t5,
                         "class": [c + 1 for j in R(7) for c in R(3) if j in J5[c]]}), "sched5_lavori")
salva_dati(pd.DataFrame({"class": R(1, 4), "f": f5, "s": s5}), "sched5_classi")


def modello_5(r, t, J, f, s, a):
    n, q = len(r), len(J)
    m = nuovo_modello("classi_setup")
    x = m.addVars(n, vtype=GRB.BINARY, name="x")
    y = m.addVars(q, vtype=GRB.BINARY, name="y")
    m.setObjective(gp.quicksum(r[j] * x[j] for j in R(n)) - gp.quicksum(f[c] * y[c] for c in R(q)),
                   GRB.MAXIMIZE)
    m.addConstr(gp.quicksum(t[j] * x[j] for j in R(n)) + gp.quicksum(s[c] * y[c] for c in R(q)) <= a,
                name="disponibilita")
    m.addConstrs((x[j] - y[c] <= 0 for c in R(q) for j in J[c]), name="link")
    return m, x, y


def duale_5(r, t, J, f, s, a):
    """min a pi;  t_j pi + lam_j >= r_j;  s_c pi - sum_{j in J_c} lam_j >= -f_c;  pi, lam >= 0."""
    n, q = len(r), len(J)
    d = nuovo_modello("duale_classi_setup")
    pi = d.addVar(name="pi")
    lam = d.addVars(n, name="lam")
    d.setObjective(a * pi, GRB.MINIMIZE)
    d.addConstrs((t[j] * pi + lam[j] >= r[j] for j in R(n)), name="rc_x")
    d.addConstrs((s[c] * pi - gp.quicksum(lam[j] for j in J[c]) >= -f[c] for c in R(q)), name="rc_y")
    return d


def euristica_5(r, t, J, f, s, a):
    """Class by class: the first job also pays the setup, if it fits."""
    n, q = len(r), len(J)
    x, y, ra, passi = [0] * n, [0] * q, a, []
    for c in R(q):
        for j in J[c]:
            if y[c] == 0:
                if s[c] + t[j] <= ra:
                    y[c], x[j] = 1, 1
                    passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c]} + {t[j]} = "
                                 f"{s[c] + t[j]} <= ra = {ra}; y[{c + 1}] = 1, x[{j + 1}] = 1, ra = {ra - s[c] - t[j]}.")
                    ra -= s[c] + t[j]
                else:
                    passi.append(f"Class {c + 1} not active: s[{c + 1}] + t[{j + 1}] = {s[c] + t[j]} > ra = {ra}; "
                                 f"job {j + 1} is skipped.")
            else:
                if t[j] <= ra:
                    x[j] = 1
                    passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} <= ra = {ra}; x[{j + 1}] = 1, ra = {ra - t[j]}.")
                    ra -= t[j]
                else:
                    passi.append(f"Class {c + 1} active: t[{j + 1}] = {t[j]} > ra = {ra}; job {j + 1} is skipped.")
    return x, y, passi


m5, x5, y5 = modello_5(r5, t5, J5, f5, s5, a5)
xe, ye, passi = euristica_5(r5, t5, J5, f5, s5, a5)
print("Class-by-class heuristic:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
lb5 = sum(r5[j] * xe[j] for j in R(7)) - sum(f5[c] * ye[c] for c in R(3))
print(f"  lb = {lb5}  (x = {xe}, y = {ye})")
d5 = duale_5(r5, t5, J5, f5, s5, a5)
pi_mano = max(r5[j] / t5[j] for j in R(7))
ub5, viol = valuta(d5, {"pi": pi_mano})
assert viol <= 1e-9
print(f"Hand-built dual solution: lam = 0, pi = max_j r_j/t_j = {frazione(pi_mano)}  ->  ub = {frazione(ub5)}")
zlp5, zlp5r, _ = due_rilassamenti(m5, d5)
z5 = risolvi(m5)
print("Optimal solution of the MILP:")
stampa_soluzione(m5, solo_non_nulle=True)
registra("5 classes setup", ub5, lb5, zlp5, zlp5r, z5, senso="max")

# ======================================================================
# 6. CLASSES WITH COMPLETION BONUS AND "IF AND ONLY IF" REDUCTION
# ======================================================================
intestazione("6. Bonus if the whole class is executed; reduction u if and only if >= 2 classes")
r6 = [10, 5, 20, 12, 10, 22]
t6 = [5, 15, 25, 15, 10, 38]
J6 = [[0, 1], [2, 3], [4, 5]]
v6 = [5, 4, 10]
a6, u6 = 50, 10
salva_dati(pd.DataFrame({"job": R(1, 7), "r": r6, "t": t6,
                         "class": [c + 1 for j in R(6) for c in R(3) if j in J6[c]]}), "sched6_lavori")
salva_dati(pd.DataFrame({"class": R(1, 4), "v": v6}), "sched6_classi")


def coppie(J):
    return [(j, i, c, g) for c in R(len(J)) for g in R(c + 1, len(J)) for j in J[c] for i in J[g]]


def modello_6(r, t, J, v, a, u):
    n, q = len(r), len(J)
    m = nuovo_modello("classi_premio")
    x = m.addVars(n, vtype=GRB.BINARY, name="x")
    y = m.addVars(q, vtype=GRB.BINARY, name="y")
    z = m.addVar(vtype=GRB.BINARY, name="z")
    m.setObjective(gp.quicksum(r[j] * x[j] for j in R(n)) + gp.quicksum(v[c] * y[c] for c in R(q)),
                   GRB.MAXIMIZE)
    m.addConstrs((x[j] - y[c] >= 0 for c in R(q) for j in J[c]), name="all")
    m.addConstrs((x[j] + x[i] - z <= 1 for (j, i, c, g) in coppie(J)), name="miste")
    m.addConstr(gp.quicksum(t[j] * x[j] for j in R(n)) + u * z <= a, name="disponibilita")
    return m, x, y, z


def duale_6(r, t, J, v, a, u):
    """min sum lam_ji + a mu;  pi_j + sum lam + t_j mu >= r_j;  -sum_{J_c} pi_j >= v_c;
    -sum lam + u mu >= 0;  pi <= 0, lam >= 0, mu >= 0."""
    n, q = len(r), len(J)
    cp = coppie(J)
    d = nuovo_modello("duale_classi_premio")
    pi = d.addVars(n, lb=-GRB.INFINITY, ub=0.0, name="pi")
    lam = d.addVars([(j, i) for (j, i, _, _) in cp], name="lam")
    mu = d.addVar(name="mu")
    d.setObjective(lam.sum() + a * mu, GRB.MINIMIZE)
    for j in R(n):
        d.addConstr(pi[j] + gp.quicksum(lam[jj, ii] for (jj, ii, _, _) in cp if jj == j or ii == j)
                    + t[j] * mu >= r[j], name=f"rc_x[{j}]")
    d.addConstrs((-gp.quicksum(pi[j] for j in J[c]) >= v[c] for c in R(q)), name="rc_y")
    d.addConstr(-lam.sum() + u * mu >= 0, name="rc_z")
    return d


def euristica_6(r, t, J, v, a, u):
    """Class by class: from the second class on, the first job also pays the reduction u."""
    n, q = len(r), len(J)
    x, y, z, ra, passi = [0] * n, [0] * q, 0, a, []
    for c in R(q):
        cnt = 0
        for j in J[c]:
            if c == 0 or z == 1:
                if t[j] <= ra:
                    x[j], ra, cnt = 1, ra - t[j], cnt + 1
                    passi.append(f"Class {c + 1}: t[{j + 1}] = {t[j]} <= ra; x[{j + 1}] = 1, ra = {ra}.")
                else:
                    passi.append(f"Class {c + 1}: t[{j + 1}] = {t[j]} > ra = {ra}; job {j + 1} is skipped.")
            else:
                if t[j] + u <= ra:
                    x[j], z, ra, cnt = 1, 1, ra - t[j] - u, cnt + 1
                    passi.append(f"Class {c + 1}, reduction not applied yet: t[{j + 1}] + u = {t[j] + u} <= ra; "
                                 f"x[{j + 1}] = 1, z = 1, ra = {ra}.")
                else:
                    passi.append(f"Class {c + 1}, reduction not applied yet: t[{j + 1}] + u = {t[j] + u} > ra = {ra}; "
                                 f"job {j + 1} is skipped.")
        if cnt == len(J[c]):
            y[c] = 1
            passi.append(f"All the jobs of class {c + 1} are executed: y[{c + 1}] = 1 (bonus v = {v[c]}).")
    return x, y, z, passi


m6, x6, y6, z6 = modello_6(r6, t6, J6, v6, a6, u6)
xe, ye, ze, passi = euristica_6(r6, t6, J6, v6, a6, u6)
print("Class-by-class heuristic:")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
lb6 = sum(r6[j] * xe[j] for j in R(6)) + sum(v6[c] * ye[c] for c in R(3))
print(f"  lb = {lb6}  (x = {xe}, y = {ye}, z = {ze})")
d6 = duale_6(r6, t6, J6, v6, a6, u6)
pi_mano = {f"pi[{J6[c][0]}]": -v6[c] for c in R(3)}      # the first job of every class carries the bonus
mu_mano = max((r6[j] - pi_mano.get(f"pi[{j}]", 0)) / t6[j] for j in R(6))
mano = dict(pi_mano, mu=mu_mano)
ub6, viol = valuta(d6, mano)
assert viol <= 1e-9
print(f"Hand-built dual solution: pi_1 = -5, pi_3 = -4, pi_5 = -10, lam = 0, "
      f"mu = max_j (r_j - pi_j)/t_j = {frazione(mu_mano)}  ->  ub = {frazione(ub6)}")
zlp6, zlp6r, _ = due_rilassamenti(m6, d6)
z6v = risolvi(m6)
print("Optimal solution of the MILP:")
stampa_soluzione(m6, solo_non_nulle=True)
registra("6 classes bonus", ub6, lb6, zlp6, zlp6r, z6v, senso="max")

# ======================================================================
# 7. TOTAL TARDINESS ON ONE MACHINE: SEQUENCING WITH BIG-M
# ======================================================================
intestazione("7. Total tardiness: precedences s_ji, completions kappa_j, tardiness tau_j, big-M")
t7 = [5, 4, 6]
d7 = [3, 4, 10]
salva_dati(pd.DataFrame({"job": R(1, 4), "t": t7, "d": d7}), "sched7_lavori")


def modello_7(t, d):
    n = len(t)
    M = sum(t)
    m = nuovo_modello("ritardo")
    s = m.addVars([(j, i) for j in R(n) for i in R(n) if j != i], vtype=GRB.BINARY, name="s")
    kappa = m.addVars(n, name="kappa")
    tau = m.addVars(n, name="tau")
    m.setObjective(tau.sum(), GRB.MINIMIZE)
    m.addConstrs((s[j, i] + s[i, j] == 1 for j in R(n) for i in R(j + 1, n)), name="ordine")
    m.addConstrs((-M * s[j, i] - kappa[j] + kappa[i] >= t[i] - M for j in R(n) for i in R(n) if j != i),
                 name="precedenza")
    m.addConstrs((-kappa[j] + tau[j] >= -d[j] for j in R(n)), name="ritardo")
    m.addConstrs((kappa[j] >= t[j] for j in R(n)), name="inizio")
    return m, s, kappa, tau, M


def duale_7(t, d):
    """Dual with alpha (free), beta, gamma, delta >= 0 — see the lecture notes."""
    n = len(t)
    M = sum(t)
    D = nuovo_modello("duale_ritardo")
    alpha = D.addVars([(j, i) for j in R(n) for i in R(j + 1, n)], lb=-GRB.INFINITY, name="alpha")
    beta = D.addVars([(j, i) for j in R(n) for i in R(n) if j != i], name="beta")
    gamma = D.addVars(n, name="gamma")
    delta = D.addVars(n, name="delta")
    D.setObjective(alpha.sum() + gp.quicksum((t[i] - M) * beta[j, i] for (j, i) in beta)
                   - gp.quicksum(d[j] * gamma[j] for j in R(n)) + gp.quicksum(t[j] * delta[j] for j in R(n)),
                   GRB.MAXIMIZE)
    D.addConstrs((alpha[j, i] - M * beta[j, i] <= 0 for (j, i) in alpha), name="rc_s_ji")
    D.addConstrs((alpha[j, i] - M * beta[i, j] <= 0 for (j, i) in alpha), name="rc_s_ij")
    D.addConstrs((-gp.quicksum(beta[j, i] for i in R(n) if i != j) + gp.quicksum(beta[i, j] for i in R(n) if i != j)
                  - gamma[j] + delta[j] <= 0 for j in R(n)), name="rc_kappa")
    D.addConstrs((gamma[j] <= 1 for j in R(n)), name="rc_tau")
    return D


def euristica_7(t, d, ordine=None):
    """Sequence in the given order (natural if absent): completions and tardiness."""
    n = len(t)
    ordine = list(R(n)) if ordine is None else ordine
    kappa, tau, fine, passi = [0] * n, [0] * n, 0, []
    for j in ordine:
        fine += t[j]
        kappa[j] = fine
        tau[j] = max(0, fine - d[j])
        passi.append(f"Job {j + 1}: kappa = {fine}, tau = max(0, {fine} - {d[j]}) = {tau[j]}.")
    return kappa, tau, passi


m7, s7, k7, tau7, M7 = modello_7(t7, d7)
print(f"Big-M = sum of the times = {M7}")
kappa_e, tau_e, passi = euristica_7(t7, d7)
print("Heuristic: natural order 1 -> 2 -> 3")
for i, s in enumerate(passi, 1):
    print(f"  Step {i}. {s}")
ub7 = sum(tau_e)
print(f"  ub = {ub7}")
D7 = duale_7(t7, d7)
lb7, viol = valuta(D7, {"gamma[0]": 1, "delta[0]": 1})
assert viol <= 1e-9
print(f"Hand-built dual solution: gamma_1 = 1, delta_1 = 1, all the rest 0  ->  lb = {frazione(lb7)}")
zlp7, zlp7r, _ = due_rilassamenti(m7, D7)
z7 = risolvi(m7)
print("Optimal solution of the MILP:")
stampa_soluzione(m7, solo_non_nulle=True)
registra("7 tardiness", ub7, lb7, zlp7, zlp7r, z7)
ordine_ott = sorted(R(3), key=lambda j: k7[j].X)
print("Optimal sequence:", " -> ".join(str(j + 1) for j in ordine_ott))

salva_dati(pd.DataFrame(bound), "sched_bound")

# ======================================================================
# 8. ADDITIONAL MODELLING QUESTIONS (solved variants)
# ======================================================================
intestazione("8. Additional modelling questions")


def variante(nome, m):
    z = risolvi(m)
    print(f"  {nome:70s} z = {frazione(z)}")
    return z


varianti = {}
# 1a: jobs 1 and 3 must be on the same machine
m, x = modello_1(t1, c1, a1)
m.addConstrs((x[0, mm] == x[2, mm] for mm in R(3)), name="together")
varianti["1a"] = variante("1a. Jobs 1 and 3 on the same machine (x_1m = x_3m)", m)
# 1b: fixed cost g_m per used machine (activation)
g1 = [3, 3, 3]
m, x = modello_1(t1, c1, a1)
y = m.addVars(3, vtype=GRB.BINARY, name="y")
m.addConstrs((x[j, mm] <= y[mm] for j in R(3) for mm in R(3)), name="activate")
m.update()
m.setObjective(m.getObjective() + gp.quicksum(g1[mm] * y[mm] for mm in R(3)), GRB.MINIMIZE)
varianti["1b"] = variante("1b. Fixed cost g_m = 3 per used machine (x_jm <= y_m)", m)
# 2a: a used machine must work at least 8 minutes (link in the opposite direction)
m, x, y = modello_2(t2, c2, a2)
m.addConstrs((gp.quicksum(t2[j][mm] * x[j, mm] for j in R(3)) >= 8 * y[mm] for mm in R(3)), name="min_usage")
varianti["2a"] = variante("2a. A used machine works at least 8 minutes (sum_j t_jm x_jm >= 8 y_m)", m)
# 2b: if machine 1 is used then machine 3 is used too (link between activations)
m, x, y = modello_2(t2, c2, a2)
m.addConstr(y[0] <= y[2], name="1_implies_3")
varianti["2b"] = variante("2b. If machine 1 is used so is machine 3 (y_1 <= y_3)", m)
# 3a: all jobs must be executed (the assignment constraint is back)
m, x, y = modello_3(t3, r3, c3, a3)
m.addConstrs((x.sum(j, "*") == 1 for j in R(3)), name="all")
varianti["3a"] = variante("3a. All jobs executed (sum_m x_jm = 1)", m)
# 3b: job 3 only if job 2
m, x, y = modello_3(t3, r3, c3, a3)
m.addConstr(x.sum(2, "*") <= x.sum(1, "*"), name="3_only_if_2")
varianti["3b"] = variante("3b. Job 3 is executed only if job 2 is executed", m)
# 4a: minimise the makespan (maximum of the machine times)
m, x, y = modello_4(t4, p4)
w = m.addVar(name="w")
m.addConstrs((w >= y[mm] for mm in R(3)), name="makespan")
m.setObjective(w, GRB.MINIMIZE)
varianti["4a"] = variante("4a. Minimise the maximum of the times (min-max: w >= y_m)", m)
# 4b: fixed cost if a machine works (y_m > 0 => v_m = 1, big-M = max_j t_jm)
g4 = [4, 4, 4]
m, x, y = modello_4(t4, p4)
vv = m.addVars(3, vtype=GRB.BINARY, name="v")
m.addConstrs((y[mm] <= max(t4[j][mm] for j in R(3)) * vv[mm] for mm in R(3)), name="activate")
m.setObjective(y.sum() + gp.quicksum(g4[mm] * vv[mm] for mm in R(3)), GRB.MINIMIZE)
varianti["4b"] = variante("4b. Fixed cost 4 if the machine works (y_m <= M_m v_m)", m)
# 5a: a single active class
m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
m.addConstr(y.sum() <= 1, name="one_class")
varianti["5a"] = variante("5a. At most one class activated (sum y_c <= 1)", m)
# 5b: class 3 only if class 1
m, x, y = modello_5(r5, t5, J5, f5, s5, a5)
m.addConstr(y[2] <= y[0], name="3_only_if_1")
varianti["5b"] = variante("5b. Class 3 is activated only if class 1 is (y_3 <= y_1)", m)
# 6a: at least one job per class
m, x, y, z = modello_6(r6, t6, J6, v6, a6, u6)
m.addConstrs((gp.quicksum(x[j] for j in J6[c]) >= 1 for c in R(3)), name="at_least_one")
varianti["6a"] = variante("6a. At least one job per class (hence z = 1)", m)
# 6b: penalty w per class started and not completed
w6 = 3
m, x, y, z = modello_6(r6, t6, J6, v6, a6, u6)
st = m.addVars(3, vtype=GRB.BINARY, name="s")
m.addConstrs((st[c] >= x[j] for c in R(3) for j in J6[c]), name="started")
m.update()
m.setObjective(m.getObjective() - w6 * gp.quicksum(st[c] - y[c] for c in R(3)), GRB.MAXIMIZE)
varianti["6b"] = variante("6b. Penalty 3 per class started and not completed (s_c >= x_j)", m)
# 7a: release dates
rho7 = [0, 2, 0]
m, s, kappa, tau, M = modello_7(t7, d7)
m.addConstrs((kappa[j] >= rho7[j] + t7[j] for j in R(3)), name="release")
varianti["7a"] = variante("7a. Job 2 available from time 2 (kappa_j >= rho_j + t_j)", m)
# 7b: minimise the maximum tardiness
m, s, kappa, tau, M = modello_7(t7, d7)
T = m.addVar(name="T")
m.addConstrs((T >= tau[j] for j in R(3)), name="max_tardiness")
m.setObjective(T, GRB.MINIMIZE)
varianti["7b"] = variante("7b. Minimise the maximum tardiness (min-max: T >= tau_j)", m)
salva_dati(pd.DataFrame({"variant": list(varianti), "z": list(varianti.values())}), "sched_varianti")

# ======================================================================
# 9. FIGURES
# ======================================================================
intestazione("9. Figures")


def barre_macchine(assegn, t, a, titolo, nome):
    """Every machine: bar of the times of the assigned jobs and availability."""
    k = len(a)
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    for mm in R(k):
        inizio = 0
        for (j, m2) in sorted(assegn):
            if m2 == mm:
                ax.barh(mm, t[j][mm], left=inizio, color=CICLO[j % len(CICLO)], edgecolor="white")
                ax.text(inizio + t[j][mm] / 2, mm, f"{j + 1}", ha="center", va="center", color="white",
                        fontsize=9, fontweight="bold")
                inizio += t[j][mm]
        ax.plot([a[mm], a[mm]], [mm - 0.4, mm + 0.4], color=ROSSO, lw=2)
    ax.set_yticks(R(k))
    ax.set_yticklabels([f"machine {mm + 1}" for mm in R(k)])
    ax.set_xlabel("time (minutes); in red the availability $a_m$")
    ax.set_title(titolo)
    ax.invert_yaxis()
    salva_figura(fig, nome)


barre_macchine(e_best.x, t1, a1, "Assignment: best-fit solution (ub = 11)", "cap07_gap_euristica")
barre_macchine(ott1, t1, a1, f"Assignment: optimal solution (z = {frazione(z1)})", "cap07_gap_ottimo")
ott2 = {(j, mm) for j in R(3) for mm in R(3) if x2[j, mm].X > 0.5}
barre_macchine(ott2, t2, a2, f"Fixed cost: optimal solution (z = {frazione(z2)})", "cap07_costo_fisso_ottimo")

# tardiness: Gantt of the natural and of the optimal sequence
fig, ax = plt.subplots(figsize=(7.2, 3.0))
for riga, (etichetta, ordine) in enumerate([("natural order (ub = 12)", list(R(3))),
                                             (f"optimal sequence (z = {frazione(z7)})", ordine_ott)]):
    fine = 0
    for j in ordine:
        ax.barh(riga, t7[j], left=fine, color=CICLO[j], edgecolor="white")
        ax.text(fine + t7[j] / 2, riga, f"job {j + 1}", ha="center", va="center", color="white", fontsize=9)
        fine += t7[j]
        ax.plot([d7[j], d7[j]], [riga - 0.45, riga + 0.45], color=CICLO[j], lw=1.5, ls="--")
ax.set_yticks([0, 1])
ax.set_yticklabels(["natural order", "optimal sequence"])
ax.set_xlabel("time; dashed the due dates $d_j$ (same colour as the job)")
ax.set_title("Total tardiness on one machine")
ax.invert_yaxis()
salva_figura(fig, "cap07_ritardo_gantt")

# bounds: for every problem, lb - z - ub
fig, ax = plt.subplots(figsize=(7.2, 3.6))
df = pd.DataFrame(bound)
for i, riga in df.iterrows():
    ax.plot([riga.lb, riga.ub], [i, i], color=GRIGIO, lw=3, solid_capstyle="round")
    ax.plot(riga.z_lp, i, marker="|", color=TEAL, ms=14, mew=2)
    ax.plot(riga.z_milp, i, marker="o", color=BLU, ms=7)
ax.set_yticks(R(len(df)))
ax.set_yticklabels(df.problem)
ax.invert_yaxis()
ax.set_xlabel("value; grey segment = [lb, ub], teal bar = z(LP), dot = z(MILP)")
ax.set_title("The bound sandwich on the seven problems")
salva_figura(fig, "cap07_bound")
print("Done.")
