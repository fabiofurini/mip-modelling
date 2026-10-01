"""Shared plotting style and helpers for the laboratory scripts.

Every script imports from here: palette consistent with the lecture notes,
figures saved into the folder of the volume they belong to, data into data/.
"""
import re
import os
import sys
from pathlib import Path

import matplotlib


def _dentro_notebook() -> bool:
    """True inside Jupyter/Colab: there figures are shown, not saved."""
    if "google.colab" in sys.modules:
        return True
    try:
        from IPython import get_ipython
        return type(get_ipython()).__name__ == "ZMQInteractiveShell"
    except Exception:
        return False


NOTEBOOK = _dentro_notebook()

if not NOTEBOOK:
    matplotlib.use("Agg")     # in notebooks the inline backend stays
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
# the three sets of notes are independent: each keeps its own figures
VOLUMI = {1: BASE / "notes_1" / "figure", 2: BASE / "notes_2" / "figure",
          3: BASE / "notes_3" / "figure"}


def dir_figure(nome: str) -> Path:
    """The folder of the volume the figure belongs to, from its name."""
    m = re.match(r"cap(\d\d)", nome)
    if m:
        return VOLUMI[1 if int(m.group(1)) <= 6 else 3]
    if nome.startswith("ex"):
        return VOLUMI[2]
    raise ValueError(f"cannot tell which volume the figure {nome} belongs to")
DIR_DATI = BASE / "data"
DIR_IMG = BASE / "docs" / "img"

# make sure the English output folders exist (they must not overwrite the Italian ones);
# in a notebook there is no repository around the script, so nothing is created
if not NOTEBOOK:
    for _d in (*VOLUMI.values(), DIR_DATI, DIR_IMG):
        os.makedirs(_d, exist_ok=True)

# Institutional palette of the lecture notes
BLU = "#16324A"      # midnight blue (titles)
TEAL = "#0E7490"     # teal (main accent)
ROSSO = "#C0392B"
VERDE = "#1E8449"
ARANCIO = "#CA6F1E"
GRIGIO = "#7F8C8D"
CICLO = [TEAL, ROSSO, VERDE, ARANCIO, BLU, GRIGIO, "#8E44AD", "#B7950B"]

# Il titolo sta a sinistra e staccato dagli assi: cosi' non tocca mai il bordo
# della figura, per quanto sia lungo, e la figura resta leggibile anche piccola.
plt.rcParams.update({
    "figure.figsize": (7.2, 4.2),
    "figure.dpi": 120,
    "font.size": 10,
    "font.family": "DejaVu Sans",
    "axes.prop_cycle": plt.cycler(color=CICLO),
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#B9C2C9",
    "axes.linewidth": 0.8,
    "axes.labelcolor": BLU,
    "axes.labelsize": 9.5,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": "#C9D2D8",
    "grid.alpha": 0.55,
    "grid.linewidth": 0.5,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": BLU,
    "axes.titlelocation": "left",
    "axes.titlepad": 10,
    "xtick.color": "#5B6B77",
    "ytick.color": "#5B6B77",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "text.color": BLU,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "lines.linewidth": 1.9,
    "lines.markersize": 6,
    "patch.linewidth": 0.8,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.08,
})


def _legenda_fuori(fig):
    """Moves the legends out of the plotting area, below the whole figure.

    A legend inside the plot covers the lines and the points: information is
    lost exactly where it is needed. Here the entries of every axes are
    collected into a single legend below the figure, so that it never ends up
    on top of the label of the horizontal axis.
    """
    maniglie, etichette = [], []
    for ax in fig.get_axes():
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()
        m, e = ax.get_legend_handles_labels()
        for mm, ee in zip(m, e):
            if ee and not ee.startswith("_") and ee not in etichette:
                maniglie.append(mm)
                etichette.append(ee)
    if not etichette:
        return
    colonne = len(etichette) if len(etichette) <= 4 else 3
    fig.legend(maniglie, etichette, fontsize=9, frameon=False,
               loc="upper center", bbox_to_anchor=(0.5, -0.08),
               bbox_transform=fig.transFigure,
               ncol=colonne, borderaxespad=0.0)

def salva_figura(fig, nome: str) -> None:
    """Save the figure as PDF (preview) and as PNG for the website (docs/img/).

    In a notebook nothing is saved: the figure is shown below the cell.
    """
    if NOTEBOOK:
        plt.show()
        return
    _legenda_fuori(fig)
    cartella = dir_figure(nome)
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / f"{nome}.pdf"
    fig.savefig(percorso, bbox_inches="tight")
    img = DIR_IMG
    img.mkdir(parents=True, exist_ok=True)
    fig.savefig(img / f"{nome}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [figure] {percorso.relative_to(BASE)} (+ docs/img/{nome}.png)")


def salva_dati(df, nome: str) -> None:
    """Save a DataFrame into data/<name>.csv (in a notebook it only prints its size)."""
    if NOTEBOOK:
        print(f"  [data]   {nome}: {len(df)} rows x {len(df.columns)} columns")
        return
    DIR_DATI.mkdir(parents=True, exist_ok=True)
    percorso = DIR_DATI / f"{nome}.csv"
    df.to_csv(percorso, index=False)
    print(f"  [data]   {percorso.relative_to(BASE)}")


def salva_dat(df, nome: str) -> None:
    """Save a pgfplots-ready CSV into <volume>/figure/dat/<name>.csv.

    Only the printed lecture notes need it: in a notebook it does nothing.
    """
    if NOTEBOOK:
        return
    d = dir_figure(nome) / "dat"
    d.mkdir(parents=True, exist_ok=True)
    percorso = d / f"{nome}.csv"
    df.to_csv(percorso, index=False)
    print(f"  [dat]    {percorso.relative_to(BASE)}")


def salva_tikz(codice: str, nome: str) -> None:
    """Save generated TikZ code into notes/figure/<name>.tex.

    Only the printed lecture notes need it: in a notebook it does nothing.
    """
    if NOTEBOOK:
        return
    cartella = dir_figure(nome)
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / f"{nome}.tex"
    percorso.write_text(codice)
    print(f"  [tikz]   {percorso.relative_to(BASE)}")


def intestazione(titolo: str) -> None:
    print("\n" + "=" * 72)
    print(titolo)
    print("=" * 72)
