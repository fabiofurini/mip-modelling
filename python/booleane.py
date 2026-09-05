"""Boolean expressions: evaluation, conjunctive normal form, linear constraints.

Chapter 2 turns boolean expressions into linear constraints with three rules:
every clause becomes an inequality >= 1, every OR becomes a +, every negative
literal NOT x becomes 1 - x. This module performs the transformation and
*checks* it by enumeration: the set of assignments making the expression true
must coincide with the set of binary solutions of the linear system.

An expression is a tree:
    ("var", name) | ("not", e) | ("and", e1, ...) | ("or", e1, ...) | ("imp", e1, e2)
Clauses are sets of literals (name, sign) with sign True = positive.
(Function names are shared with the Italian version, so the two stay parallel.)
"""
from itertools import product

# ---------- readable constructors ----------
def V(nome):
    return ("var", nome)


def NOT(e):
    return ("not", e)


def AND(*e):
    return ("and", *e)


def OR(*e):
    return ("or", *e)


def IMP(a, b):
    return ("imp", a, b)


def variabili(e) -> set:
    if e[0] == "var":
        return {e[1]}
    return set().union(*(variabili(f) for f in e[1:]))


def valuta(e, ass: dict) -> bool:
    """Truth value of the expression under the assignment {name: 0/1}."""
    if e[0] == "var":
        return bool(ass[e[1]])
    if e[0] == "not":
        return not valuta(e[1], ass)
    if e[0] == "and":
        return all(valuta(f, ass) for f in e[1:])
    if e[0] == "or":
        return any(valuta(f, ass) for f in e[1:])
    if e[0] == "imp":
        return (not valuta(e[1], ass)) or valuta(e[2], ass)
    raise ValueError(e)


# ---------- transformation into CNF ----------
def _senza_implicazioni(e):
    """A => B  becomes  (NOT A) OR B."""
    if e[0] == "var":
        return e
    if e[0] == "imp":
        return ("or", ("not", _senza_implicazioni(e[1])), _senza_implicazioni(e[2]))
    return (e[0], *(_senza_implicazioni(f) for f in e[1:]))


def _negazioni_dentro(e):
    """Pushes the NOTs onto the literals with De Morgan and double negation."""
    if e[0] == "var":
        return e
    if e[0] == "not":
        f = e[1]
        if f[0] == "var":
            return e
        if f[0] == "not":                                   # NOT NOT x  <=>  x
            return _negazioni_dentro(f[1])
        if f[0] == "and":                                   # De Morgan
            return ("or", *(_negazioni_dentro(("not", g)) for g in f[1:]))
        if f[0] == "or":                                    # De Morgan
            return ("and", *(_negazioni_dentro(("not", g)) for g in f[1:]))
    return (e[0], *(_negazioni_dentro(f) for f in e[1:]))


def _clausole(e) -> list:
    """CNF as a list of clauses; every clause is a frozenset of literals."""
    if e[0] == "var":
        return [frozenset({(e[1], True)})]
    if e[0] == "not":
        return [frozenset({(e[1][1], False)})]
    if e[0] == "and":
        fuori = []
        for f in e[1:]:
            fuori += _clausole(f)
        return fuori
    if e[0] == "or":                                        # distributivita' OR su AND
        fuori = [frozenset()]
        for f in e[1:]:
            fuori = [a | b for a in fuori for b in _clausole(f)]
        return fuori
    raise ValueError(e)


def _semplifica(clausole: list) -> list:
    """Drops tautological clauses (x OR NOT x) and subsumed ones (absorption)."""
    vive = [c for c in clausole if not any((n, not s) in c for (n, s) in c)]
    ridotte = []
    for c in sorted(set(vive), key=lambda c: (len(c), sorted(c))):
        if not any(d <= c for d in ridotte):
            ridotte.append(c)
    return ridotte


def cnf(e) -> list:
    """Conjunctive normal form of the expression, simplified."""
    return _semplifica(_clausole(_negazioni_dentro(_senza_implicazioni(e))))


# ---------- clauses -> linear constraints ----------
def vincolo(clausola) -> tuple:
    """Clause -> (coefficients, sense, right-hand side) in the preferred form.

    Rule: sum_{positive} x - sum_{negative} x >= 1 - (number of negatives).
    With two or more negative literals the equivalent <= form is reported
    (multiplying by -1), as in the course originals.
    """
    pos = sorted(n for (n, s) in clausola if s)
    neg = sorted(n for (n, s) in clausola if not s)
    coef = {n: 1 for n in pos} | {n: -1 for n in neg}
    rhs = 1 - len(neg)
    if len(neg) >= 2:
        return ({n: -c for n, c in coef.items()}, "<=", -rhs)
    return (coef, ">=", rhs)


def _ordina(nome):
    """Natural ordering: x2 before x10."""
    cifre = "".join(ch for ch in nome if ch.isdigit())
    return (int(cifre) if cifre else 0, nome)


def scrivi(vinc, mat: bool = True) -> str:
    """The constraint as a string; with mat=True in LaTeX syntax ($x_{10}$ etc.)."""
    coef, verso, rhs = vinc
    pezzi = []
    for n in sorted(coef, key=_ordina):
        c = coef[n]
        nome = f"x_{{{n[1:]}}}" if mat and n.startswith("x") else n
        segno = "+" if c > 0 else "-"
        if not pezzi:
            pezzi.append(("" if c > 0 else "-") + nome)
        else:
            pezzi.append(f"{segno} {nome}")
    simbolo = {"<=": r"\le" if mat else "<=", ">=": r"\ge" if mat else ">="}[verso]
    return f"{' '.join(pezzi)} {simbolo} {rhs}"


def soddisfa(vinc, ass: dict) -> bool:
    coef, verso, rhs = vinc
    lhs = sum(c * ass[n] for n, c in coef.items())
    return lhs <= rhs + 1e-9 if verso == "<=" else lhs >= rhs - 1e-9


def verifica(e, vincoli=None, nomi=None) -> tuple:
    """Enumerates all assignments: truth of the expression == feasibility.

    Returns (number of assignments, number of true assignments). Raises
    AssertionError if even one assignment tells the two sets apart: it is the
    proof, by cases, that the constraints are equivalent to the formula.
    """
    nomi = sorted(nomi or variabili(e), key=_ordina)
    vincoli = [vincolo(c) for c in cnf(e)] if vincoli is None else vincoli
    vere = 0
    for valori in product((0, 1), repeat=len(nomi)):
        ass = dict(zip(nomi, valori))
        vero = valuta(e, ass)
        ammissibile = all(soddisfa(v, ass) for v in vincoli)
        assert vero == ammissibile, (ass, vero, ammissibile)
        vere += vero
    return 2 ** len(nomi), vere


def equivalenti(e1, e2) -> bool:
    """True if two expressions have the same truth set."""
    nomi = sorted(variabili(e1) | variabili(e2), key=_ordina)
    return all(valuta(e1, dict(zip(nomi, v))) == valuta(e2, dict(zip(nomi, v)))
               for v in product((0, 1), repeat=len(nomi)))


def testo_cnf(e) -> str:
    """The CNF as a LaTeX string with the operators used in the course."""
    def lett(n, s):
        nome = f"x_{{{n[1:]}}}" if n.startswith("x") else n
        return nome if s else rf"\NOT {nome}"
    parti = []
    for c in cnf(e):
        letterali = sorted(c, key=lambda l: (_ordina(l[0]), not l[1]))
        parti.append("(" + r"\OR ".join(lett(n, s) for (n, s) in letterali) + ")"
                     if len(c) > 1 else lett(*next(iter(c))))
    return r"\AND ".join(parti)
