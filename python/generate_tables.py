"""The bound tables of the variants, generated from the CSVs of the scripts.

P0.6 asks, for at least one variant of each exercise of chapters 7 and 8, a
feasible heuristic, a dual certificate and the bound table. The first two live in
the scripts (`salva_modello`, `valuta`, `due_rilassamenti`); the table is
generated here from the CSVs, so the numbers are the verified ones and are never
transcribed by hand.

Use:  python3 generate_tables.py          # writes the tables
      python3 generate_tables.py --check  # checks that they are up to date
"""
import sys
from fractions import Fraction
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent

CONF = dict(dati=BASE / "data", uscita=BASE / "data/tables",
            testa=("", "value", "what it is"),
            voci={"min": [("$\\ub$", "ub", "heuristic solution"),
                          ("$\\lb$", "lb", "dual certificate built by hand")],
                  "max": [("$\\ub$", "ub", "dual certificate built by hand"),
                          ("$\\lb$", "lb", "heuristic solution")]},
            comuni=[
                   ("$\\zlp$", "z_lp", "relaxation without the bounds"),
                   ("$\\zlpp$", "z_lp_rafforzato", "relaxation with the bounds"),
                   ("$\\zmilp$", "z_milp", "optimum of the MILP")])

def numero(x) -> str:
    """Reduced fraction or integer, as in the notes."""
    f = Fraction(float(x)).limit_denominator(10_000)
    return str(f.numerator) if f.denominator == 1 else f"\\frac{{{f.numerator}}}{{{f.denominator}}}"


def voci(riga, conf):
    """The rows of the table, in order, with the notes right for the sense."""
    righe = conf["voci"][str(riga.get("senso", "min"))]
    grezza = riga.get("certificato", "")
    nota = "" if pd.isna(grezza) else str(grezza).strip()
    if nota:   # il bound certificato non viene dal duale: lo dice la tabella
        righe = [(e, c, nota if n0 == "dual certificate built by hand" else n0) for e, c, n0 in righe]
    return righe + conf["comuni"]


def tabella(riga, conf) -> str:
    testa = conf["testa"]
    corpo = "\n".join(f"{etichetta} & ${numero(riga[colonna])}$ & {nota} \\\\"
                      for etichetta, colonna, nota in voci(riga, conf))
    return ("\\begin{center}\\small\n\\begin{tabular}{lrl}\n\\toprule\n"
            f"{testa[0]} & {testa[1]} & {testa[2]} \\\\\n\\midrule\n{corpo}\n"
            "\\bottomrule\n\\end{tabular}\n\\end{center}\n")


# sul sito le macro della dispensa non esistono: si scrive la notazione per esteso
SITO = {"$\\ub$": "$\\mathit{UB}$", "$\\lb$": "$\\mathit{LB}$",
        "$\\zlp$": "$z(\\mathit{LP})$", "$\\zlpp$": "$z(\\mathit{LP}^+)$",
        "$\\zmilp$": "$z(\\mathit{MILP})$"}


def tabella_md(riga, conf) -> str:
    """The same table, in markdown, for the site pages."""
    testa = conf["testa"]
    righe = [f"| {testa[0]} | {testa[1]} | {testa[2]} |", "|---|---:|---|"]
    for etichetta, colonna, nota in voci(riga, conf):
        righe.append(f"| {SITO[etichetta]} | ${numero(riga[colonna])}$ | {nota} |")
    return "\n".join(righe) + "\n"


def main(verifica: bool = False) -> int:
    diversi = []
    conf = CONF
    if True:
        conf["uscita"].mkdir(parents=True, exist_ok=True)
        for csv in sorted(conf["dati"].glob("fam[01][0-9]_*[ab]_bound.csv")):
            riga = pd.read_csv(csv).iloc[0]
            testo = tabella(riga, conf)
            for suffisso, contenuto in ((".tex", testo), (".md", tabella_md(riga, conf))):
                percorso = conf["uscita"] / f"{csv.stem}{suffisso}"
                vecchio = percorso.read_text(encoding="utf-8") if percorso.exists() else ""
                if contenuto == vecchio:
                    continue
                diversi.append(str(percorso.relative_to(BASE)))
                if not verifica:
                    percorso.write_text(contenuto, encoding="utf-8")
    if verifica:
        if diversi:
            print("Variant tables out of date: " + ", ".join(diversi))
            return 1
        print("Variant tables up to date.")
        return 0
    print(f"Tables written or updated: {len(diversi)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(verifica="--check" in sys.argv))
