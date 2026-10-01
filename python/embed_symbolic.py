"""Embeds the symbolic models of the notes into the site pages.

The symbolic model of a problem is written once, in the notes, inside a
`modello` environment. Here it is extracted, turned into what MathJax can read
and put into the page between two markers: what lies between the markers is
regenerated, the rest of the page is left alone.

This way the notes and the site cannot drift apart --- and drifting is how the
site had lost the format: domain rows squeezed together, several constraints per
row, `\\forall` gone.

Only the opening marker is written in the page:

    <!-- model: 7.1 -->        the model of problem 7.1
    <!-- model: 7.1-dual -->   the dual of its LP relaxation

Usage:  python3 embed_symbolic.py           # regenerate the blocks
        python3 embed_symbolic.py --check   # check that they are up to date
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIR_DOCS = BASE / "docs"
NOTES = sorted(BASE.glob("notes_*/capitoli"))

APRE = re.compile(r"<!-- model: ([0-9]+\.[0-9]+[A-Za-z]*(?:-dual)?) -->")
FINE = "<!-- model: end -->"

TITOLO = re.compile(r"\\begin\{modello\}\[([^\]]*)\]")


def _mathjax(corpo: str) -> str:
    """Il corpo di un ambiente `modello` come lo legge MathJax."""
    corpo = re.sub(r"\\label\{[^}]*\}", "", corpo)
    corpo = re.sub(r"\\(begin|end)\{subequations\}", "", corpo)
    corpo = re.sub(r"\\vskip\s+-?[0-9.]+\s*mm", "", corpo)
    corpo = corpo.replace("\\begin{align}", "\\begin{aligned}")
    corpo = corpo.replace("\\end{align}", "\\end{aligned}")
    corpo = corpo.replace("\\nonumber", "")
    corpo = re.sub(r"\\\\\[[0-9.]+ex\]", "\\\\\\\\", corpo)
    corpo = re.sub(r"@\{[^{}]*\}", "", corpo)      # MathJax non conosce @{} in array
    corpo = re.sub(r"[ \t]+$", "", corpo, flags=re.M)
    corpo = re.sub(r"\n{2,}", "\n", corpo)
    return corpo.strip()


def modelli() -> dict[str, str]:
    """`{"7.1": corpo, "7.1-duale": corpo, ...}` da tutte le dispense."""
    fuori = {}
    for cartella in NOTES:
        for f in sorted(cartella.rglob("*.tex")):
            testo = f.read_text(encoding="utf-8")
            for m in re.finditer(r"\\begin\{modello\}\[([^\]]*)\](.*?)\\end\{modello\}",
                                 testo, re.S):
                titolo, corpo = m.group(1), _mathjax(m.group(2))
                n = re.match(r"Model ([0-9]+\.[0-9]+[A-Za-z]*)", titolo)
                if n:
                    fuori[n.group(1)] = corpo
                    continue
                d = re.match(r"Dual of the LP relaxation of model "
                             r"([0-9]+\.[0-9]+[A-Za-z]*)", titolo)
                if d:
                    fuori[d.group(1) + "-dual"] = corpo
    return fuori


def aggiorna(verifica: bool) -> int:
    disponibili = modelli()
    cambiate, mancanti = [], []
    for pagina in sorted(DIR_DOCS.glob("*.md")):
        testo = pagina.read_text(encoding="utf-8")
        if not APRE.search(testo):
            continue
        nuovo = testo
        for m in list(APRE.finditer(testo)):
            nome = m.group(1)
            if nome not in disponibili:
                mancanti.append((pagina.name, nome))
                continue
            inizio = nuovo.index(m.group(0)) + len(m.group(0))
            fine = nuovo.index(FINE, inizio)
            corpo = f"\n\n$$\n{disponibili[nome]}\n$$\n\n"
            nuovo = nuovo[:inizio] + corpo + nuovo[fine:]
        if nuovo != testo:
            cambiate.append(pagina.name)
            if not verifica:
                pagina.write_text(nuovo, encoding="utf-8")
    for pagina, nome in mancanti:
        print(f"  [missing] {pagina}: no model {nome} in the notes")
    if verifica:
        if cambiate or mancanti:
            print("Symbolic models out of date: " + ", ".join(cambiate))
            return 1
        print("Symbolic models: pages in step with the notes.")
        return 0
    print(f"  [models] {len(cambiate)} pages updated, "
          f"{len(disponibili)} models available")
    return 1 if mancanti else 0


if __name__ == "__main__":
    sys.exit(aggiorna("--check" in sys.argv))
