"""Checks that the models on the site pages follow the format of the course.

The rules are those of Fabio's own sources, and they hold in every form --- the
notes, the site, the instructors' booklet:

1. the relation symbol sits on the alignment point (`lhs &\\le rhs`), not before
   it: that way `=`, `\\le`, `\\ge` and `\\in` line up in a column;
2. one domain row per family of variables, each with its own `\\forall`;
3. never more than one constraint per row;
4. every shorthand of the preamble the pages use (`\\Z`, `\\ub`, ...) is defined
   for MathJax too, otherwise the browser prints the command instead of the
   symbol.

It exits non-zero on the first row out of format, so CI stops.

    python3 python/check_models.py
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "docs"
PREAMBLE = BASE / "notes_1" / "preambolo.tex"
MATHJAX = DOCS / "javascripts" / "mathjax.js"
MODELLI = BASE / "data" / "models"

# The shorthands defined by the notes preamble. The list lives here, and is not
# read from the `.tex`, because the notes are private and absent in CI; when the
# preamble is at hand the two lists are checked against each other as well.
MACRO_DEL_CORSO = frozenset({
    "AND", "E", "NOT", "OR", "Prob", "Q", "R", "Z", "cvar", "false", "figdat",
    "lb", "true", "ub", "var", "zdual", "zlp", "zlpp", "zlppp", "zmilp",
})

# un dominio: `\in \{0, 1\}`, `\ge 0`, `\le 0`, `\gtreqless 0`, `\in \Z_{\ge 0}`
DOMINIO = re.compile(r"\\in\s*\\\{0|\\ge\s*0|\\le\s*0|\\gtreqless\s*0|\\in\s*\\(Z|Q|R)")
RELAZIONE = re.compile(r"\\le|\\ge|\\in|\\gtreqless|(?<![<>!=])=(?!=)")
APRE = re.compile(r"(\\le|\\ge|\\in|\\gtreqless|=)")


def _nudo(s: str) -> str:
    """Drop the arguments in braces: the `=` of `\\sum_{j=1}^{n}` and the `\\in` of
    `\\sum_{j \\in J}` are not the relation symbol of the row."""
    while True:
        senza = re.sub(r"\{[^{}]*\}", "", s)
        if senza == s:
            return s
        s = senza


def righe(blocco: str):
    corpo = re.sub(r"\\(begin|end)\{(aligned|array)\}(\{[^}]*\})?", "", blocco)
    for riga in re.split(r"\\\\(?:\[[^\]]*\])?", corpo):
        riga = riga.strip()
        if riga:
            yield riga


def problemi(riga: str) -> list[str]:
    fuori = []
    colonne = riga.split("&")
    sinistra = colonne[0].replace("\\text{subject to}", "").replace("\\quad", " ", 1).strip()
    dopo = colonne[1].lstrip().lstrip("~") if len(colonne) > 1 else ""

    if dopo and not APRE.match(dopo) and not dopo.startswith("\\forall"):
        if RELAZIONE.search(_nudo(dopo)):
            fuori.append("relation not on the alignment point")
    if RELAZIONE.search(_nudo(sinistra)):
        fuori.append("more than one relation before the alignment point")
    nucleo = (sinistra + " & " + dopo) if dopo else sinistra
    # `\Z_{\ge 0}` e' un dominio solo, non `\in` piu' `\ge 0`
    nucleo = re.sub(r"\\(Z|Q|R)_\{\\ge 0\}", r"\\\1", nucleo)
    if len(DOMINIO.findall(nucleo)) > 1:
        fuori.append("several families of variables on one domain row")
    return fuori


def undefined_macros() -> list[str]:
    """The course shorthands the pages use and MathJax does not know.

    Without the definition the browser prints `\\Z` in place of Z, and the model
    looks wrong even when it is not.
    """
    if PREAMBLE.exists():   # locally: the list above must stay in step with it
        in_tex = set(re.findall(r"\\newcommand\{\\([A-Za-z]+)\}",
                                PREAMBLE.read_text(encoding="utf-8")))
        if in_tex != set(MACRO_DEL_CORSO):
            return [f"MACRO_DEL_CORSO does not match {PREAMBLE.name}: "
                    f"only in the tex {sorted(in_tex - MACRO_DEL_CORSO)}, "
                    f"only here {sorted(MACRO_DEL_CORSO - in_tex)}"]
    for_mathjax = set(re.findall(r"^\s*([A-Za-z]+):\s*\"",
                                 MATHJAX.read_text(encoding="utf-8"), re.M))
    missing: dict[str, list[str]] = {}
    for page in sorted(DOCS.glob("*.md")):
        for name in set(re.findall(r"\\([A-Za-z]+)", page.read_text(encoding="utf-8"))):
            if name in MACRO_DEL_CORSO and name not in for_mathjax:
                missing.setdefault(name, []).append(page.name)
    return [f"\\{n} used on {len(p)} pages ({', '.join(sorted(p)[:3])}...) "
            f"but not defined in {MATHJAX.name}" for n, p in sorted(missing.items())]


def missing_models() -> list[str]:
    """Every numerical page shows the primal and, when it exists, the dual.

    The generated model may be there without anyone embedding it: the page then
    talks about a dual the reader never sees.
    """
    fuori = []
    for page in sorted(DOCS.glob("ex-*.md")):
        n = page.stem.removeprefix("ex-")
        text = page.read_text(encoding="utf-8")
        for side in ("primale", "duale"):
            nome = f"ex{n}_{side}"
            if (BASE / "data" / "models" / f"{nome}.tex").exists() \
                    and f"modello-esteso: {nome}" not in text:
                fuori.append(f"{page.name}: model {nome} exists but the page does not show it")
    return fuori


def greek_without_backslash() -> list[str]:
    """A Greek name written without its backslash comes out in roman type.

    It happened with "pi1" and with "varrho": the generator did not recognise
    them and the model showed Latin letters. The generated models are checked
    here, because that is where the mistake is born.
    """
    greche = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
              "iota", "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau",
              "phi", "chi", "psi", "omega", "pi", "varepsilon", "vartheta",
              "varpi", "varrho", "varsigma", "varphi")
    fuori = []
    for p in sorted(MODELLI.glob("*.tex")):
        testo = p.read_text(encoding="utf-8")
        for g in greche:
            if re.search(rf"(?<![\\A-Za-z]){g}(?![A-Za-z])", testo):
                fuori.append(f"{p.name}: \"{g}\" without its backslash, comes out in roman")
                break
    return fuori


def main() -> int:
    trovati = 0
    for trouble in undefined_macros():
        print(trouble)
        trovati += 1
    for trouble in greek_without_backslash():
        print(trouble)
        trovati += 1
    for trouble in missing_models():
        print(trouble)
        trovati += 1
    for pagina in sorted(DOCS.glob("*.md")):
        testo = pagina.read_text(encoding="utf-8")
        for n, blocco in enumerate(re.findall(r"\$\$\n(.*?)\n\$\$", testo, re.S), 1):
            if "begin{aligned}" not in blocco and "begin{array}" not in blocco:
                continue
            if "\\text{min-max:}" in blocco:   # a comparison of formulations, not a model
                continue
            for riga in righe(blocco):
                for p in problemi(riga):
                    print(f"{pagina.name} (model {n}): {p}\n    {riga[:110]}")
                    trovati += 1
    if trovati:
        print(f"\n{trovati} points to fix.")
        return 1
    print("Model format: every page in order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
