"""Chapter 8 -- The overview of bounds on the four problems.

Not a problem on its own: it collects the bounds already computed by the
four scripts `fam08_1_...py`--`fam08_4_...py` (each writes its own row to
`data/*_bound.csv`) and draws the comparison. Must be run after the other
four -- on its own in Colab it finds nothing to read.
"""
import pandas as pd

from stile import BLU, DIR_DATI, GRIGIO, TEAL, plt, salva_dati, salva_figura

R = range

# ---------- 1. READING THE BOUNDS OF THE FOUR PROBLEMS ----------

PREFIXES = ["loc1", "loc2", "loc3", "hub4"]

righe = [pd.read_csv(DIR_DATI / f"{p}_bound.csv") for p in PREFIXES]
df = pd.concat(righe, ignore_index=True)
salva_dati(df, "loc_bound")
print(df.to_string(index=False))

varianti = [pd.read_csv(DIR_DATI / f"{p}_varianti.csv") for p in PREFIXES]
salva_dati(pd.concat(varianti, ignore_index=True), "loc_varianti")

# ---------- 2. FIGURE: THE BOUND SANDWICH ----------

fig, ax = plt.subplots(figsize=(7.2, 3.2))
for i, riga in df.iterrows():
    ax.plot([riga.lb, riga.ub], [i, i], color=GRIGIO, lw=3, solid_capstyle="round")
    ax.plot(riga.z_lp, i, marker="|", color=TEAL, ms=14, mew=2)
    ax.plot(riga.z_milp, i, marker="o", color=BLU, ms=7)
ax.set_yticks(R(len(df)))
ax.set_yticklabels(df.problem)
ax.invert_yaxis()
ax.set_xlabel("value; grey segment = [lb, ub], teal bar = z(LP), dot = z(MILP)")
ax.set_title("The bound sandwich on the four location problems")
salva_figura(fig, "cap08_bound")
print("Fine.")
