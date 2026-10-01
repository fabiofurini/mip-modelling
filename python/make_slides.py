"""The slides of the models and the problems, generated from the same sources as the notes.

Rule zero of the course: a model exists in one place only. The slides are no
exception --- the symbolic models are extracted from the `modello` environment of
the notes, the instance ones from the `.tex` files `esteso.py` generates, the
bounds from the CSVs of the scripts. Only the frame is written here.

It produces `slides/capitoli/*.tex`, included by the main deck:

    modelli_numerici.tex    one slide per EX 1--15
    problemi_famiglie.tex   one slide for each of the 23 problems
    da_modellare.tex        one slide for each of the 40 problems to model

Usage:  python3 make_slides.py
        python3 make_slides.py --check
"""
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
DIR_SLIDE = BASE / "slides" / "capitoli"
DIR_DATI = BASE / "data"
DIR_MODELLI = DIR_DATI / "models"
DISPENSE = sorted(BASE.glob("notes_*/capitoli"))
ESERCIZI = BASE / "exercises" / "capitoli"

NOME_EX = {
    1: "ex01", 2: "ex02", 3: "ex03", 4: "ex04", 5: "ex05", 6: "ex06", 7: "ex07",
    8: "ex08", 9: "ex09", 10: "ex10", 11: "ex11", 12: "ex12", 13: "ex13",
    14: "ex14", 15: "ex15",
}
FAMIGLIE = ([(f"7.{i}", f"fam07_{i}") for i in range(1, 8)]
            + [(f"8.{i}", f"fam08_{i}") for i in range(1, 5)]
            + [(f"9.{i}", f"fam09_{i}") for i in range(1, 4)]
            + [(f"10.{i}", f"fam10_{i}") for i in range(1, 10)])


# ---------------------------------------------------------------- estrazione

def _tutti_i_tex() -> list[Path]:
    fuori = []
    for cartella in DISPENSE:
        fuori += sorted(cartella.rglob("*.tex"))
    if ESERCIZI.exists():
        fuori += sorted(ESERCIZI.glob("*.tex"))
    return fuori


def ambienti(nome: str) -> dict[str, str]:
    """`{titolo: corpo}` di tutti gli ambienti `nome` delle dispense."""
    fuori = {}
    for f in _tutti_i_tex():
        testo = f.read_text(encoding="utf-8")
        for m in re.finditer(r"\\begin\{" + nome + r"\}\[([^\]]*)\](.*?)\\end\{" + nome + r"\}",
                             testo, re.S):
            fuori[m.group(1).strip()] = m.group(2).strip()
    return fuori


def per_beamer(corpo: str) -> str:
    """Il corpo di un ambiente della dispensa, ripulito per una slide."""
    corpo = re.sub(r"\\label\{[^}]*\}", "", corpo)
    corpo = re.sub(r"\\index\{[^}]*\}", "", corpo)
    corpo = re.sub(r"\\(begin|end)\{subequations\}", "", corpo)
    corpo = re.sub(r"\\vskip\s+-?[0-9.]+\s*mm", "", corpo)
    corpo = corpo.replace("\\begin{align}", "\\begin{aligned}").replace("\\end{align}", "\\end{aligned}")
    corpo = corpo.replace("\\begin{align*}", "\\begin{aligned}").replace("\\end{align*}", "\\end{aligned}")
    corpo = corpo.replace("\\nonumber", "")
    corpo = re.sub(r"\\\\\[[0-9.]+ex\]", "\\\\\\\\", corpo)
    corpo = re.sub(r"[ \t]+$", "", corpo, flags=re.M)
    corpo = re.sub(r"\n{2,}", "\n", corpo)
    return corpo.strip()


def bound(nome_csv: str) -> dict | None:
    f = DIR_DATI / f"{nome_csv}_bound.csv"
    if not f.exists():
        return None
    r = pd.read_csv(f).iloc[-1].to_dict()
    return r


def numero(x) -> str:
    from fractions import Fraction
    if pd.isna(x):
        return "---"
    fr = Fraction(float(x)).limit_denominator(10_000)
    return str(fr.numerator) if fr.denominator == 1 else f"\\tfrac{{{fr.numerator}}}{{{fr.denominator}}}"


def riga_bound(r: dict) -> str:
    """I cinque numeri su una riga sola: sulla slide la tabella ruba spazio al modello."""
    massimo = str(r.get("senso", "min")) == "max"
    eur, duale = ("\\lb", "\\ub") if massimo else ("\\ub", "\\lb")
    v_eur = numero(r["lb"] if massimo else r["ub"])
    v_duale = numero(r["ub"] if massimo else r["lb"])
    pezzi = [f"${eur} = {v_eur}$", f"${duale} = {v_duale}$",
             f"$\\zlp = {numero(r['z_lp'])}$"]
    if not pd.isna(r.get("z_lp_rafforzato")):
        pezzi.append(f"$\\zlpp = {numero(r['z_lp_rafforzato'])}$")
    pezzi.append(f"$\\zmilp = {numero(r['z_milp'])}$")
    return ("\\begin{center}\\scriptsize\n" + " \\;$\\cdot$\\; ".join(pezzi)
            + "\n\\end{center}")


def tabella_bound(r: dict) -> str:
    massimo = str(r.get("senso", "min")) == "max"
    eur, duale = ("$\\lb$", "$\\ub$") if massimo else ("$\\ub$", "$\\lb$")
    v_eur = numero(r["lb"] if massimo else r["ub"])
    v_duale = numero(r["ub"] if massimo else r["lb"])
    righe = [f"{eur} (euristica) & ${v_eur}$ \\\\",
             f"{duale} (duale a mano) & ${v_duale}$ \\\\",
             f"$\\zlp$ & ${numero(r['z_lp'])}$ \\\\"]
    if not pd.isna(r.get("z_lp_rafforzato")):
        righe.append(f"$\\zlpp$ & ${numero(r['z_lp_rafforzato'])}$ \\\\")
    righe.append(f"$\\zmilp$ & ${numero(r['z_milp'])}$ \\\\")
    return ("\\begin{center}\\footnotesize\n\\begin{tabular}{lr}\n\\toprule\n"
            + "\n".join(righe) + "\n\\bottomrule\n\\end{tabular}\n\\end{center}")



LEGENDA = r"""\begin{itemize}\footnotesize
  \item $\lb$ and $\ub$ are the two sides of the sandwich built \emph{by hand}:
        the heuristic solution on one side, the dual certificate on the other.
  \item $\zlp$ is the relaxation without the bounds, $\zlpp$ the one with them,
        $\zmilp$ the integer optimum.
  \item In a minimisation the heuristic gives $\ub$ and the dual $\lb$; in a
        maximisation the two roles swap.
\end{itemize}"""

APERTURA_EX = r"""\begin{frame}{Fifteen numerical models}
Explicit data, few variables, one technique per model. Every slide shows the
model of the instance written out --- one column per variable, as the script
generates it --- and the five numbers of the sandwich.
\vfill
""" + LEGENDA + r"""
\end{frame}
"""

APERTURA_FAM = r"""\begin{frame}{Twenty-three problems with a symbolic model}
For each problem: the statement as it arrives, the symbolic model and the five
numbers of the sandwich. The models are those of the notes, generated from the
same source.
\vfill
""" + LEGENDA + r"""
\end{frame}
"""

APERTURA_MOD = r"""\begin{frame}{Forty problems to model}
Here there are only the statements: twenty with explicit numerical data and
twenty in symbolic form. The model is to be written, not read --- these are the
problems to practise on, and the solutions are reserved for instructors.
\end{frame}
"""

# ---------------------------------------------------------------- le slide

def slide_numerici(problemi: dict) -> str:
    pezzi = ["\\section{The fifteen numerical models}\n", APERTURA_EX]
    for n in range(1, 16):
        titolo = next((t for t in problemi if t.startswith(f"EX {n} ---")), None)
        modello = DIR_MODELLI / f"{NOME_EX[n]}_primale.tex"
        r = bound(NOME_EX[n])
        if titolo is None or not modello.exists() or r is None:
            print(f"  [skipped] EX {n}")
            continue
        nome = titolo.split("---", 1)[1].strip()
        pezzi.append(f"""\\begin{{frame}}{{EX {n} --- {nome}}}
\\begin{{center}}
\\adjustbox{{max width=\\textwidth, max totalheight=0.66\\textheight}}{{$\\displaystyle
\\input{{../data/models/{NOME_EX[n]}_primale}}
$}}
\\end{{center}}
\\vfill
{riga_bound(r)}
\\end{{frame}}
""")
    return "\n".join(pezzi)


def slide_famiglie(modelli: dict, problemi: dict) -> str:
    pezzi = ["\\section{The twenty-three problems}\n", APERTURA_FAM]
    for numero_p, csv in FAMIGLIE:
        chiave_m = next((t for t in modelli
                         if t.startswith(f"Model {numero_p} ---")
                         or t.startswith(f"Model {numero_p}A ---")), None)
        chiave_p = next((t for t in problemi if t.startswith(f"Problem {numero_p} ---")), None)
        r = bound(csv)
        if chiave_m is None or r is None:
            print(f"  [skipped] problem {numero_p}")
            continue
        nome = chiave_m.split("---", 1)[1].strip()
        enunciato = per_beamer(problemi[chiave_p]) if chiave_p else ""
        if enunciato:
            pezzi.append(f"""\\begin{{frame}}[allowframebreaks]{{Problem {numero_p} --- {nome}}}
\\begin{{block}}{{The statement}}
\\footnotesize {enunciato}
\\end{{block}}
\\end{{frame}}
""")
        pezzi.append(f"""\\begin{{frame}}{{Model {numero_p} --- {nome}}}
\\begin{{center}}
\\adjustbox{{max width=\\textwidth, max totalheight=0.66\\textheight}}{{$\\displaystyle
{per_beamer(modelli[chiave_m])}
$}}
\\end{{center}}
\\vfill
{riga_bound(r)}
\\end{{frame}}
""")
    return "\n".join(pezzi)


def slide_da_modellare(problemi: dict) -> str:
    pezzi = ["\\section{The forty problems to model}\n", APERTURA_MOD]
    for prefisso, titolo_sezione in (("N", "Twenty numerical problems"),
                                     ("S", "Twenty symbolic problems")):
        pezzi.append(f"\\subsection{{{titolo_sezione}}}\n")
        for i in range(1, 21):
            chiave = next((t for t in problemi if t.startswith(f"{prefisso}{i} ---")), None)
            if chiave is None:
                continue
            nome = chiave.split("---", 1)[1].strip()
            pezzi.append(f"""\\begin{{frame}}[allowframebreaks]{{{prefisso}{i} --- {nome}}}
\\footnotesize
{per_beamer(problemi[chiave])}
\\end{{frame}}
""")
    return "\n".join(pezzi)


def main() -> int:
    verifica = "--check" in sys.argv
    modelli = ambienti("modello")
    problemi = ambienti("problema")
    DIR_SLIDE.mkdir(parents=True, exist_ok=True)
    attesi = {
        "modelli_numerici.tex": slide_numerici(problemi),
        "problemi_famiglie.tex": slide_famiglie(modelli, problemi),
        "da_modellare.tex": slide_da_modellare(problemi),
    }
    cambiati = []
    for nome, testo in attesi.items():
        f = DIR_SLIDE / nome
        if not f.exists() or f.read_text(encoding="utf-8") != testo:
            cambiati.append(nome)
            if not verifica:
                f.write_text(testo, encoding="utf-8")
        n = testo.count("\\begin{frame}")
        print(f"  [slide] {nome}: {n} slide")
    if verifica and cambiati:
        print("Slides out of date: " + ", ".join(cambiati))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
