"""Generate the Jupyter/Colab notebooks of the chapters from the scripts.

One notebook per chapter in `notebooks/labNN_name.ipynb`, derived from the
matching script in `python/`: the course code stays in one place — the scripts
are the source, the notebooks are regenerated. The sections of a script (the
`# ---- n. TITLE ----` blocks) become separate code cells, each preceded by its
title in a text cell.

It also generates the website page that lists them (`docs/notebooks.md`).

Usage:  python3 make_notebooks.py           # regenerate notebooks and website page
        python3 make_notebooks.py --check   # verify they are up to date
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIR_SCRIPT = BASE / "python"
DIR_NOTEBOOK = BASE / "notebooks"
DIR_DOCS = BASE / "docs"

REPO = "fabiofurini/mip-modelling"
SITO = "https://fabiofurini.github.io/mip-modelling"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/python"
MODULI = ("stile", "mip", "euristiche", "esteso", "booleane")   # the shared modules every notebook downloads if missing
BADGE = "https://colab.research.google.com/assets/colab-badge.svg"

RIGA = re.compile(r"^# [-=]{10,}$")
BANNER = re.compile(r"^# [-=]{3,}\s+(.+?)\s+[-=]{3,}$")
VOCE = re.compile(r"^\s+(\d+)\. ")

PREPARAZIONE = f"""## Setup

The cell below installs `gurobipy` and downloads the four shared modules of the
course: `stile.py` (palette), `mip.py` (relaxation, dual, bounds),
`euristiche.py` (next-fit, first-fit, best-fit) and `esteso.py` (the model of the
instance written out in full). The licence bundled with the pip package is limited
to **2000 variables and 2000 constraints**: the instances of the course are small
and all fit with plenty of room. For larger instances activate the free academic
licence at [portal.gurobi.com](https://portal.gurobi.com).
"""

CODICE_PREPARAZIONE = f'''# Environment: the solver and the shared modules of the course.
# Locally it uses the repository's python/stile.py; on Colab it installs and downloads what is missing.
import importlib.util
import subprocess
import sys
import urllib.request
from pathlib import Path

if importlib.util.find_spec("gurobipy") is None:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "gurobipy", "matplotlib", "pandas", "scipy"], check=True)

for modulo in {MODULI}:                     # plotting style and course utilities
    locale = next((p for p in (Path(f"../python/{{modulo}}.py"), Path(f"python/{{modulo}}.py"))
                   if p.exists()), None)
    if locale is not None:
        sys.path.insert(0, str(locale.parent.resolve()))       # notebook opened in the repository
    else:                                 # on Colab always re-download: sessions last,
        urllib.request.urlretrieve(f"{RAW}/{{modulo}}.py", f"{{modulo}}.py")   # modules change
'''

CHIUSURA = f"""---

Notebook generated from `python/{{nome}}.py` with `python3 python/make_notebooks.py`:
edits go into the script, not here.

Teaching material by [Fabio Furini]({{sito}}) — DIAG, Sapienza University of Rome.
Text, figures and data [CC BY 4.0](https://github.com/{REPO}/blob/main/LICENSE),
code [MIT](https://github.com/{REPO}/blob/main/LICENSE-CODE).
"""


INDICE = """# The notebooks of the course

Every chapter with models has its own **notebook**: one click on the badge opens
it in Google Colab, it installs the solver by itself and runs in the browser —
nothing to install on your machine. It is the very same code as the scripts in
`python/`, cell by cell, with the figures appearing below the cells instead of
being written to a file.

!!! tip "The pip licence is enough"
    The licence bundled with `gurobipy` is limited to 2000 variables and 2000
    constraints: the instances of the course are small and all fit with plenty of
    room. For larger instances activate the free academic licence at
    [portal.gurobi.com](https://portal.gurobi.com).

| Chapter | Class | Notebook |
|---|---|---|
{righe}

## How they are made

The notebooks are not written by hand: they are generated from the scripts with

```bash
python3 python/make_notebooks.py
```

The chapter script remains the single source of the code — the notebook takes its
docstring, sections and comments from it — and whoever prefers the command line
keeps running, from the `python/` folder:

```bash
python3 fam07_1_assignment.py
```
"""


def pagina_del_capitolo(nome: str) -> str | None:
    """Finds the site page presenting this script (the "Script:" field).

    Several pages may quote the same script (a chapter's choice page and its
    subpages): the one with the shortest slug is chosen, that is, the main page.
    """
    candidate = []
    for pagina in sorted(DIR_DOCS.glob("*.md")):
        quante = pagina.read_text().count(f"python/{nome}.py")
        if quante:
            candidate.append((-quante, len(pagina.stem), pagina.stem))
    return min(candidate)[2] if candidate else None


def titolo_e_classe(slug: str) -> tuple[str, str]:
    """Title (H1) and model class declared in the header of the page."""
    righe = (DIR_DOCS / f"{slug}.md").read_text().splitlines()
    titolo = next(r[2:].strip() for r in righe if r.startswith("# "))
    classe = ""
    for r in righe:
        if "Class" in r and "·" in r:
            testo = r.split("·")[0].replace("*", "").strip()
            classe = testo.removeprefix("Class:").strip()
            break
    return titolo, classe


def pagina_indice() -> str:
    """The website page listing the notebooks, one badge per chapter."""
    righe = []
    # chapters go in the reading order of the notes, not in the order of the file
    # names; chapters 1 and 2 come before the course introduces Python, and their
    # notebook is not offered here
    ORDINE = {"cap06_gurobi": 1, "cap05_heuristics": 2, "cap02_logic": 3, "cap03_links": 4}
    SENZA_NOTEBOOK = {"cap01_models", "cap04_bounds"}

    def chiave(p):
        if p.stem.startswith("cap"):
            return (0, ORDINE.get(p.stem, 99), p.stem)
        return (1, 0, p.stem)

    for percorso in sorted((p for p in list(DIR_SCRIPT.glob("cap*.py")) + list(DIR_SCRIPT.glob("fam*.py"))
              + list(DIR_SCRIPT.glob("ex*.py"))
              if not p.stem.endswith("_summary") and p.stem not in SENZA_NOTEBOOK), key=chiave):
        nome = percorso.stem
        slug = pagina_del_capitolo(nome)
        if not slug:
            continue
        titolo, classe = titolo_e_classe(slug)
        colab = (f"https://colab.research.google.com/github/{REPO}"
                 f"/blob/main/notebooks/{nome}.ipynb")
        righe.append(f"| [{titolo}]({slug}.md) | {classe} | "
                     f"[![Open in Colab]({BADGE})]({colab}) |")
    return INDICE.format(righe="\n".join(righe))


def testa_e_corpo(sorgente: str) -> tuple[str, str, str]:
    """Split the module docstring (title, body) from the rest of the code."""
    fine = sorgente.index('"""', 3)
    doc = sorgente[3:fine].strip()
    titolo, _, corpo = doc.partition("\n")
    return titolo.rstrip("."), corpo.strip(), sorgente[fine + 3:].lstrip("\n")


def sezioni(codice: str) -> list[tuple[str | None, str]]:
    """Split the code at the `# ---- title ----` banners: [(title, code), ...]."""
    righe = codice.splitlines()
    blocchi: list[tuple[str | None, list[str]]] = [(None, [])]
    i = 0
    while i < len(righe):
        m = BANNER.match(righe[i])
        if m:                       # `# ---------- 1. MODEL AND INSTANCE ----------`
            blocchi.append((m.group(1).strip(), []))
            i += 1
            continue
        if RIGA.match(righe[i]):
            j = i + 1
            titolo = []
            while j < len(righe) and righe[j].startswith("#") and not RIGA.match(righe[j]):
                titolo.append(righe[j].lstrip("#").strip())
                j += 1
            if titolo and j < len(righe) and RIGA.match(righe[j]):
                blocchi.append((" ".join(titolo), []))
                i = j + 1
                continue
        blocchi[-1][1].append(righe[i])
        i += 1
    return [(t, "\n".join(c).strip()) for t, c in blocchi if "\n".join(c).strip()]


ACRONIMI = {"LP", "MILP", "MIP", "BIP", "ILP", "CNF", "LPT", "EDD", "SPT", "CD", "EX"}


def titolo_sezione(t: str) -> str:
    """`3. RILASSAMENTO LP E DUALE (LOWER BOUND)` -> `3. Rilassamento LP e duale (lower bound)`."""
    numero, punto, resto = t.partition(". ")
    if not punto:
        numero, resto = "", t
    parole = []
    for i, p in enumerate(resto.split()):
        nudo = p.strip("()[],.:;")
        if nudo in ACRONIMI:
            parole.append(p)
        elif i == 0:
            parole.append(p.capitalize())
        else:
            parole.append(p.lower())
    testo = " ".join(parole)
    return f"{numero}. {testo}" if numero else testo


def cella_testo(testo: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": righe_json(testo)}


def cella_codice(codice: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": righe_json(codice)}


def righe_json(testo: str) -> list[str]:
    """Text as a list of lines keeping the trailing newline, but not on the last one."""
    righe = testo.rstrip("\n").split("\n")
    return [r + "\n" for r in righe[:-1]] + righe[-1:]


def notebook(percorso: Path) -> dict:
    nome = percorso.stem
    titolo, corpo, codice = testa_e_corpo(percorso.read_text())
    slug = pagina_del_capitolo(nome)
    colab = f"https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{nome}.ipynb"

    intro = [f"# {titolo}", "", f"[![Open in Colab]({BADGE})]({colab})", ""]
    intro.append("\n".join(VOCE.sub(r"\1. ", r) for r in corpo.splitlines()))
    if slug:
        intro += ["", f"The full chapter — model, data, results and sensitivity "
                      f"analysis — is [on the website]({SITO}/{slug}/)."]

    celle = [cella_testo("\n".join(intro)),
             cella_testo(PREPARAZIONE),
             cella_codice(CODICE_PREPARAZIONE.strip())]
    for t, c in sezioni(codice):
        if t:
            celle.append(cella_testo(f"## {titolo_sezione(t)}"))
        celle.append(cella_codice(c))
    celle.append(cella_testo(CHIUSURA.format(
        nome=nome, sito="https://fabiofurini.github.io/")))

    return {"cells": celle,
            "metadata": {"colab": {"provenance": []},
                         "kernelspec": {"display_name": "Python 3",
                                        "language": "python", "name": "python3"},
                         "language_info": {"name": "python"}},
            "nbformat": 4, "nbformat_minor": 5}


def main() -> int:
    verifica = "--check" in sys.argv
    DIR_NOTEBOOK.mkdir(exist_ok=True)
    disallineati = []
    indice = DIR_DOCS / "notebooks.md"
    if verifica:
        if not indice.exists() or indice.read_text() != pagina_indice():
            disallineati.append(indice.name)
    else:
        indice.write_text(pagina_indice())
        print(f"  [page]     docs/{indice.name}")
    for percorso in sorted(p for p in list(DIR_SCRIPT.glob("cap*.py")) + list(DIR_SCRIPT.glob("fam*.py"))
              + list(DIR_SCRIPT.glob("ex*.py"))
              if not p.stem.endswith("_summary")):
        atteso = json.dumps(notebook(percorso), ensure_ascii=False, indent=1) + "\n"
        uscita = DIR_NOTEBOOK / f"{percorso.stem}.ipynb"
        if verifica:
            if not uscita.exists() or uscita.read_text() != atteso:
                disallineati.append(uscita.name)
        else:
            uscita.write_text(atteso)
            print(f"  [notebook] notebooks/{uscita.name}")
    if verifica:
        if disallineati:
            print("Notebooks out of date: " + ", ".join(disallineati))
            print("Regenerate them with: python3 python/make_notebooks.py")
            return 1
        print("Every notebook is in sync with its script.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
