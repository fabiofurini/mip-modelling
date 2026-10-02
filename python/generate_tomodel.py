"""The site page with the forty problems to model.

It is generated from the sources of volume V, so the statements stay one thing:
if the notes change, the page changes.

Use:  python3 python/generate_tomodel.py          # writes docs/to-model.md
      python3 python/generate_tomodel.py --check  # checks that it is up to date
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIR_CAPITOLI = BASE / "exercises" / "capitoli"
USCITA = BASE / "docs" / "to-model.md"

CAPITOLI = [("cap20_numerical", "Twenty numerical problems",
             "Data written out, as in the fifteen numerical models: one reads the "
             "statement, recognises the decisions, writes the MILP and solves it."),
            ("cap21_symbolic", "Twenty symbolic problems",
             "Data declared with their type and unit, as in the problems of the "
             "families. Every problem brings two or three links between variables into "
             "play, and the model has to be written in general, with the quantifiers.")]

TESTA = """# Problems to model

**Forty problems** presented as they would arise in practice — a text, some data, a question —
with no model already written: twenty with explicit numerical data and twenty in
symbolic form. They can also be downloaded
[as a PDF](pdf/exercises.pdf).

The solutions are reserved for instructors. The method for answering is the one
of every problem of the course: decisions and variables, one constraint per
sentence of the statement, the links between the variables, a feasible solution
and a dual one for the two bounds, then the solver.
"""


def _tabella(testo: str) -> str:
    """`\\begin{tabular}` -> markdown table."""
    righe = [r.strip() for r in testo.strip().split("\\\\") if r.strip()]
    fuori = []
    for k, r in enumerate(righe):
        celle = [c.strip() for c in r.split("&")]
        fuori.append("| " + " | ".join(celle) + " |")
        if k == 0:
            fuori.append("|" + "|".join(["---"] * len(celle)) + "|")
    return "\n".join(fuori)


def markdown(corpo: str) -> str:
    """The body of a `problema` box in markdown, with the mathematics intact."""
    # i trattini lunghi prima della tabella: dopo, mangerebbero la riga `|---|`
    corpo = corpo.replace("---", "—").replace("``", "\u201c").replace("''", "\u201d")
    corpo = re.sub(r"\\begin\{center\}\\small\s*\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}\s*\\end\{center\}",
                   lambda m: "\n\n" + _tabella(m.group(1).replace("\\toprule", "")
                                               .replace("\\midrule", "").replace("\\bottomrule", "")) + "\n",
                   corpo, flags=re.S)
    corpo = corpo.replace("\\Z", "\\mathbb{Z}").replace("\\Q", "\\mathbb{Q}")
    corpo = re.sub(r"\\textsc\{([^}]*)\}", lambda m: m.group(1).upper(), corpo)
    corpo = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", corpo)
    corpo = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", corpo)
    corpo = re.sub(r"\\index\{[^}]*\}", "", corpo)
    # la tilde di LaTeX e' uno spazio insecabile: fuori dalla matematica, uno spazio
    corpo = "".join(p if k % 2 else p.replace("~", " ")
                    for k, p in enumerate(re.split(r"(\$[^$]*\$)", corpo)))
    return re.sub(r"\n{3,}", "\n\n", corpo).strip()


# La difficoltà è quella di *ricavare il modello dall'enunciato*: scelta delle
# variabili, numero di famiglie, legami da riconoscere, struttura temporale o
# disgiuntiva. Non misura la dimensione dell'istanza ne' il tempo del solver.
DIFFICOLTA = {
    "N1": 1, "N2": 2, "N3": 1, "N4": 1, "N5": 1, "N6": 3, "N7": 2, "N8": 4,
    "N9": 3, "N10": 3, "N11": 3, "N12": 3, "N13": 4, "N14": 1, "N15": 4,
    "N16": 2, "N17": 3, "N18": 3, "N19": 5, "N20": 3,
    "S1": 3, "S2": 4, "S3": 4, "S4": 4, "S5": 4, "S6": 4, "S7": 5, "S8": 4,
    "S9": 5, "S10": 4, "S11": 5, "S12": 3, "S13": 5, "S14": 5, "S15": 4,
    "S16": 4, "S17": 5, "S18": 4, "S19": 4, "S20": 5,
}


def stelle(etichetta: str) -> str:
    """Le cinque stelle della difficolta', dal codice N3 o S12 dell'enunciato."""
    codice = etichetta.split(None, 1)[0].strip()
    n = DIFFICOLTA.get(codice)
    return "" if n is None else "★" * n + "☆" * (5 - n)


def rientra(testo: str) -> str:
    """Il corpo dentro un box: quattro spazi davanti a ogni riga non vuota."""
    return "\n".join("    " + r if r.strip() else "" for r in testo.split("\n"))


def pagina() -> str:
    pezzi = [TESTA]
    for nome, titolo, intro in CAPITOLI:
        testo = (DIR_CAPITOLI / f"{nome}.tex").read_text(encoding="utf-8")
        pezzi.append(f"\n## {titolo}\n\n{intro}\n")
        for m in re.finditer(r"\\section\*\{(.+?)\}\s*\n\\begin\{problema\}\[(.+?)\]\n(.*?)\n\\end\{problema\}",
                             testo, re.S):
            etichetta, _, corpo = m.group(1), m.group(2), m.group(3)
            d = stelle(etichetta)
            riga = f"    **%s:** {d}\n\n" % "Difficulty" if d else ""
            pezzi.append(f'!!! abstract "{markdown(etichetta)}"\n\n'
                         + riga + rientra(markdown(corpo)) + "\n")
    return "\n".join(pezzi).rstrip() + "\n"


def main(verifica: bool = False) -> int:
    if not DIR_CAPITOLI.is_dir():
        print("sources of the notes absent: page of the problems to model skipped")
        return 0
    nuovo = pagina()
    vecchio = USCITA.read_text(encoding="utf-8") if USCITA.exists() else ""
    if verifica:
        if nuovo != vecchio:
            print("docs/to-model.md is not up to date: re-run generate_tomodel.py")
            return 1
        print("Page of the problems to model up to date.")
        return 0
    USCITA.write_text(nuovo, encoding="utf-8")
    quanti = nuovo.count("!!! abstract")
    print(f"  [page] docs/{USCITA.name} ({quanti} problems)")
    return 0


if __name__ == "__main__":
    sys.exit(main(verifica="--check" in sys.argv))
