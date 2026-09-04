"""Chapter 7 -- The picture of the bounds on the seven problems.

Not a problem in itself: it collects the bounds already computed by the
seven scripts `fam07_1_...py`--`fam07_7_...py` (each writes its own row to
`data/schedN_bound.csv`) and draws the comparison. Must be run after the
other seven -- opened alone in Colab it finds nothing to read.
"""
import pandas as pd

from stile import BLU, DIR_DATI, GRIGIO, TEAL, plt, salva_dati, salva_figura

R = range

# ---------- 1. READING THE BOUNDS OF THE SEVEN PROBLEMS ----------

righe = [pd.read_csv(DIR_DATI / f"sched{i}_bound.csv") for i in R(1, 8)]
df = pd.concat(righe, ignore_index=True)
salva_dati(df, "sched_bound")
print(df.to_string(index=False))

varianti = [pd.read_csv(DIR_DATI / f"sched{i}_varianti.csv") for i in R(1, 8)]
salva_dati(pd.concat(varianti, ignore_index=True), "sched_varianti")

# ---------- 2. FIGURE: THE BOUND SANDWICH ----------

fig, ax = plt.subplots(figsize=(7.2, 3.6))
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
