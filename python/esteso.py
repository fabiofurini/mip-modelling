"""The instance model written out in full, generated from the Gurobi model.

Course rule: the `modello` box is always symbolic ($n$, $m$, $k$, $c_j$), the
`istanza` box is always written **out in full**, one column per variable, as in
the original sources. Writing it by hand means letting it drift away from the
numbers, so it is generated from the model the solver actually solves.

Conventions (the same as the original sources):

* one column per variable, terms lined up;
* no punctuation after the right-hand side;
* in the row of the variables the comma sits next to the variable;
* one family of variables per domain row;
* a coefficient of $1$ is left out, fractions as `\\frac{a}{b}`.

(Function names are shared with the Italian version, so the two scripts stay
parallel.)

Use inside a script:

    from esteso import salva_modello
    salva_modello(m, "ex08_primale")     # -> data/models/ex08_primale.tex
"""
import re
from fractions import Fraction
from pathlib import Path

import gurobipy as gp
from stile import NOTEBOOK
from gurobipy import GRB

BASE = Path(__file__).resolve().parent.parent
DIR_MODELLI = BASE / "data" / "models"

GRECHE = ("alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
          "iota", "kappa", "lambda", "mu", "nu", "xi", "rho", "sigma", "tau",
          "phi", "chi", "psi", "omega", "pi",
          # le varianti: senza, il nome esce in tondo invece che in greco
          "varepsilon", "vartheta", "varpi", "varrho", "varsigma", "varphi")

# i nomi che gurobipy non puo' portare per intero: `lambda` e' una parola
# riservata di Python, `epsilon` si scrive `\varepsilon` nella dispensa
ALIAS = {"lam": "lambda", "eps": "varepsilon"}

VERSO = {"<": "\\le", ">": "\\ge", "=": "="}


# ---------------------------------------------------------------- nomi

def _indice(pezzo: str) -> str:
    """Indice in base 1 come nella dispensa: `0` -> `1`, `ab` -> `ab`."""
    pezzo = pezzo.strip()
    try:
        return str(int(pezzo) + 1)
    except ValueError:
        return pezzo


def nome_latex(nome: str) -> str:
    """`x[0,1]` -> `x_{12}`, `alpha[2]` -> `\\alpha_3`, `gamma` -> `\\gamma`."""
    radice, _, coda = nome.partition("[")
    radice = radice.strip()
    if not coda:
        m = re.fullmatch(r"([A-Za-z]+?)(\d+)", radice)
        if m and m.group(1) in GRECHE:
            return f"\\{m.group(1)}_{m.group(2)}"
    radice = ALIAS.get(radice, radice)
    testa = f"\\{radice}" if radice in GRECHE else radice
    if not coda:
        return testa
    indici = "".join(_indice(p) for p in coda.rstrip("]").split(","))
    return f"{testa}_{{{indici}}}" if len(indici) > 1 else f"{testa}_{indici}"


def famiglia(nome: str) -> str:
    """La radice del nome: tutte le `x[...]` stanno sulla stessa riga di dominio."""
    return nome.partition("[")[0].strip()


# ---------------------------------------------------------------- numeri

def numero(x: float) -> str:
    """Intero, frazione ridotta o decimale con la virgola, come nella dispensa."""
    f = Fraction(x).limit_denominator(10_000)
    if f.denominator == 1:
        return str(f.numerator)
    if abs(float(f) - x) > 1e-9:
        return f"{x:g}".replace(".", "{,}")
    return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"


def _termine(coef: float, var: str, primo: bool) -> str:
    """Un addendo con il suo segno; il coefficiente 1 non si scrive."""
    if abs(coef) < 1e-12:
        return ""
    segno = "-" if coef < 0 else ("" if primo else "+")
    modulo = abs(coef)
    testo = "" if abs(modulo - 1) < 1e-12 else numero(modulo)
    return f"{segno}{testo}{var}"


# ---------------------------------------------------------------- domini

def _dominio(v) -> tuple[str, str]:
    """(verso, insieme) della riga di dominio di una variabile."""
    if v.VType == GRB.BINARY:
        return "\\in", "\\{0, 1\\}"
    if v.VType == GRB.INTEGER:
        return "\\in", "\\Z_{\\ge 0}" if v.LB == 0 else "\\Z"
    if v.LB <= -GRB.INFINITY / 2:
        # without looking at the upper bound too, a non-positive variable
        # (lb = -inf, ub = 0) would be printed as a free one
        if v.UB <= 0:
            return "\\le", numero(v.UB) if v.UB else "0"
        return "\\gtreqless", "0"
    if v.LB == 0:
        return "\\ge", "0"
    return "\\ge", numero(v.LB)


# ---------------------------------------------------------------- il corpo

def _righe_estese(m: gp.Model, etichetta_vincoli: str = "subject to") -> list[list[str]]:
    """Le celle del modello esteso: una riga per vincolo, una colonna per variabile."""
    m.update()
    variabili = m.getVars()
    nomi = [nome_latex(v.VarName) for v in variabili]
    n = len(variabili)
    posizione = {v.VarName: k for k, v in enumerate(variabili)}

    def riga(etichetta: str, coef: dict[str, float], verso: str, rhs) -> list[str]:
        celle = [etichetta] + [""] * n + [verso, "" if rhs is None else rhs]
        primo = True
        for nome, c in coef.items():
            t = _termine(c, nomi[posizione[nome]], primo)
            if t:
                celle[1 + posizione[nome]] = t
                primo = False
        return celle

    righe = []

    obiettivo = m.getObjective()
    coef_obj = {obiettivo.getVar(i).VarName: obiettivo.getCoeff(i)
                for i in range(obiettivo.size())}
    verso_obj = "\\min" if m.ModelSense == GRB.MINIMIZE else "\\max"
    righe.append(riga(verso_obj, coef_obj, "", None))

    for k, c in enumerate(m.getConstrs()):
        espressione = m.getRow(c)
        coef = {espressione.getVar(i).VarName: espressione.getCoeff(i)
                for i in range(espressione.size())}
        etichetta = f"\\text{{{etichetta_vincoli}}}" if k == 0 else ""
        righe.append(riga(etichetta, coef, VERSO[c.Sense], numero(c.RHS)))

    # domini: una riga per famiglia di variabili, virgola attaccata alla variabile
    gruppi: dict[tuple, list[int]] = {}
    for k, v in enumerate(variabili):
        gruppi.setdefault((famiglia(v.VarName), _dominio(v)), []).append(k)
    for (_, (verso, insieme)), indici in gruppi.items():
        celle = [""] + [""] * n + [verso, insieme]
        for posto, k in enumerate(indici):
            celle[1 + k] = nomi[k] + ("," if posto < len(indici) - 1 else "")
        righe.append(celle)
    return righe


def array_esteso(m: gp.Model, etichetta_vincoli: str = "subject to") -> str:
    """Il `\\begin{array}...\\end{array}` del modello, una colonna per variabile."""
    righe = _righe_estese(m, etichetta_vincoli)
    n = len(m.getVars())
    # oltre nove colonne lo spazio fra le colonne si azzera: il modello
    # deve stare nella larghezza della pagina senza uscire dal margine
    glue = "@{}" if n > 9 else "@{\\,}"
    spec = "r" + (glue + "r") * n + " c l"
    corpo = "\\\\\n".join(" & ".join(r) for r in righe)
    return f"\\begin{{array}}{{{spec}}}\n{corpo}\n\\end{{array}}"


# ---------------------------------------------------------------- testo

def _senza_latex(t: str) -> str:
    """`x_{11}` -> `x11`, `\\le` -> `<=`, `\\frac{a}{b}` -> `a/b`: the model in plain text."""
    t = re.sub(r"\\text\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", t)
    t = t.replace("\\le", "<=").replace("\\ge", ">=").replace("\\gtreqless", "free")
    t = t.replace("\\min", "min").replace("\\max", "max")
    t = t.replace("\\in", "in").replace("\\{", "{").replace("\\}", "}")
    t = t.replace("\\Z", "Z").replace("\\Q", "Q").replace("\\R", "R")
    t = re.sub(r"_\{([^}]*)\}", r"\1", t).replace("_", "")
    t = t.replace("\\,", "").replace("{,}", ",").replace("\\", "")
    return t.strip()


def testo_esteso(m: gp.Model, etichetta_vincoli: str = "subject to") -> str:
    """The model of the instance as aligned text: one column per variable.

    In a notebook the font is monospaced, so the columns line up as in the box
    of the notes --- and it does not depend on MathJax.
    """
    righe = [[_senza_latex(c) for c in r] for r in _righe_estese(m, etichetta_vincoli)]
    larghezze = [max(len(r[k]) for r in righe) for k in range(len(righe[0]))]
    fuori = []
    for r in righe:
        celle = [r[0].ljust(larghezze[0])]
        celle += [r[k].rjust(larghezze[k]) for k in range(1, len(r) - 2)]
        celle += [r[-2].rjust(larghezze[-2]), r[-1]]
        fuori.append(" ".join(celle).rstrip())
    return "\n".join(fuori)


def salva_modello(m: gp.Model, nome: str, etichetta_vincoli: str = "subject to") -> None:
    """Writes `data/models/<name>.tex`; inside a notebook it shows the model."""
    if NOTEBOOK:              # in a notebook the model is printed in plain text, not LaTeX
        print(testo_esteso(m, etichetta_vincoli))
        return
    corpo = array_esteso(m, etichetta_vincoli)
    DIR_MODELLI.mkdir(parents=True, exist_ok=True)
    percorso = DIR_MODELLI / f"{nome}.tex"
    percorso.write_text(corpo + "\n", encoding="utf-8")
    print(f"  [modello] {percorso.relative_to(BASE)} "
          f"({len(m.getVars())} variables, {len(m.getConstrs())} constraints)")
