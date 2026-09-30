"""Embeds in the site pages the instance models written out in full.

Gli stessi file che la dispensa include con `\\input{../data/models/NOME}` qui
finiscono dentro un blocco `$$...$$` delimitato da due marcatori HTML: il
contenuto fra i marcatori e' rigenerato, il resto della pagina non si tocca.
Cosi' dispensa e sito mostrano lo stesso modello, e i numeri restano quelli che
il solver risolve davvero.

Nella pagina si scrive soltanto il marcatore di apertura:

    <!-- modello-esteso: ex08_primale -->

Use:  python3 embed_models.py          # regenerate the blocks
      python3 embed_models.py --check   # check that they are up to date
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DIR_MODELLI = BASE / "data" / "models"
DIR_DOCS = BASE / "docs"

APRE = re.compile(r"<!-- modello-esteso: ([a-z0-9_]+) -->")
FINE = "<!-- modello-esteso: fine -->"


def blocco(nome: str) -> str:
    corpo = (DIR_MODELLI / f"{nome}.tex").read_text(encoding="utf-8").rstrip("\n")
    larghe = corpo.count("&") // max(corpo.count(chr(92) * 2) + 1, 1)
    classe = "modello-esteso largo" if larghe > 8 else "modello-esteso"
    return "\n".join([f"<!-- modello-esteso: {nome} -->", "",
                      f'<div class="{classe}" markdown>', "", "$$", corpo, "$$", "",
                      "</div>", "", FINE])


def aggiorna(testo: str) -> str:
    """Sostituisce ogni blocco marcato con il modello generato."""
    fuori, resto = [], testo
    while True:
        m = APRE.search(resto)
        if not m:
            fuori.append(resto)
            break
        fuori.append(resto[:m.start()])
        nome = m.group(1)
        if not (DIR_MODELLI / f"{nome}.tex").exists():
            raise SystemExit(f"model not generated: data/models/{nome}.tex "
                             f"(the chapter script produces it)")
        coda = resto[m.end():]
        fine = coda.find(FINE)
        resto = coda[fine + len(FINE):] if fine >= 0 else coda
        fuori.append(blocco(nome))
    return "".join(fuori)


def main(verifica: bool = False) -> int:
    diversi = []
    for pagina in sorted(DIR_DOCS.glob("*.md")):
        testo = pagina.read_text(encoding="utf-8")
        if not APRE.search(testo):
            continue
        nuovo = aggiorna(testo)
        if nuovo == testo:
            continue
        diversi.append(pagina.name)
        if not verifica:
            pagina.write_text(nuovo, encoding="utf-8")
    if verifica:
        if diversi:
            print("Models not up to date in: " + ", ".join(diversi))
            return 1
        print("Page models aligned with the data.")
        return 0
    print(f"Pages updated: {len(diversi)}" + (": " + ", ".join(diversi) if diversi else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(verifica="--check" in sys.argv))
