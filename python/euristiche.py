"""Constructive heuristics of the course: line-by-line transcription of the pseudocodes.

The three families inspired by bin packing — next-fit, first-fit, best-fit — for
"jobs on machines with availability" problems: every function returns an `Esito`
with the solution, the machines used and the step-by-step trace of the run (the
same text that appears in the lecture notes).

Conventions: 0-based indices in the code, 1-based in the messages; `t[j][m]` is
the time of job j on machine m (for machine-independent times pass the matrix
with constant rows), `a[m]` the availability of machine m.
(Function names are shared with the Italian version, so the two scripts stay parallel.)
"""
from dataclasses import dataclass, field

INF = float("inf")


class Traccia(list):
    """List of the steps of the heuristic, one per job."""

    def passo(self, testo: str) -> None:
        self.append(testo)

    def stampa(self) -> None:
        for i, r in enumerate(self, 1):
            print(f"  Step {i}. {r}")


@dataclass
class Esito:
    x: dict                      # {(j, m): 1} job j assigned to machine m
    y: list                      # y[m] = 1 if machine m is used
    traccia: Traccia = field(default_factory=Traccia)
    ok: bool = True              # False = "no feasible solution found"
    saltati: list = field(default_factory=list)   # jobs not executed (when allowed)

    def assegnazione(self, j: int):
        """Machine (0-based) job j is assigned to, or None."""
        for (jj, m), v in self.x.items():
            if jj == j and v == 1:
                return m
        return None


def _ra_testo(ra) -> str:
    return ", ".join(f"ra[{m + 1}] = {r:g}" for m, r in enumerate(ra))


def next_fit(t, a, salta: bool = False) -> Esito:
    """Next-fit: one machine is loaded at a time.

    Job j goes on the current machine if it fits; otherwise the next machine is
    opened (if the job fits there) or the algorithm fails — or, with `salta=True`,
    the job is skipped (selection problems).
    """
    n, k = len(t), len(a)
    e = Esito(x={}, y=[0] * k)
    cm, ra = 0, a[0]
    for j in range(n):
        if t[j][cm] > ra:
            if cm < k - 1 and t[j][cm + 1] <= a[cm + 1]:
                e.traccia.passo(
                    f"Job {j + 1}: t[{j + 1}][{cm + 1}] = {t[j][cm]:g} > ra = {ra:g}, machine "
                    f"{cm + 1} is not enough; move to machine {cm + 2} (ra = {a[cm + 1]:g}), "
                    f"where t[{j + 1}][{cm + 2}] = {t[j][cm + 1]:g} fits: x[{j + 1}][{cm + 2}] = 1, "
                    f"ra = {a[cm + 1]:g} - {t[j][cm + 1]:g} = {a[cm + 1] - t[j][cm + 1]:g}.")
                cm, ra = cm + 1, a[cm + 1]
            elif salta:
                e.traccia.passo(
                    f"Job {j + 1}: t[{j + 1}][{cm + 1}] = {t[j][cm]:g} > ra = {ra:g} and there is "
                    f"no further machine to move to: the job is skipped.")
                e.saltati.append(j)
                continue
            else:
                e.traccia.passo(
                    f"Job {j + 1}: t[{j + 1}][{cm + 1}] = {t[j][cm]:g} > ra = {ra:g} and there is "
                    f"no further machine to move to: no feasible solution found.")
                e.ok = False
                return e
        else:
            e.traccia.passo(
                f"Job {j + 1}: current machine {cm + 1}, ra = {ra:g}; t[{j + 1}][{cm + 1}] = "
                f"{t[j][cm]:g} <= {ra:g}, hence x[{j + 1}][{cm + 1}] = 1 and ra = {ra:g} - {t[j][cm]:g} "
                f"= {ra - t[j][cm]:g}.")
        e.x[(j, cm)] = 1
        e.y[cm] = 1
        ra -= t[j][cm]
    return e


def first_fit(t, a, salta: bool = False, solo_aperte: bool = False) -> Esito:
    """First-fit: the job goes on the first machine with enough residual availability.

    With `solo_aperte=True` the already-opened machines are scanned first (in index
    order) and, if none is enough, the next one is opened.
    """
    n, k = len(t), len(a)
    e = Esito(x={}, y=[0] * k)
    ra = list(a)
    aperte = 0
    for j in range(n):
        sm = None
        limite = aperte if solo_aperte else k
        for m in range(limite):
            if t[j][m] <= ra[m]:
                sm = m
                break
        if sm is None and solo_aperte and aperte < k and t[j][aperte] <= a[aperte]:
            sm = aperte
            aperte += 1
            apre = f" (machine {sm + 1} is opened)"
        else:
            apre = ""
        if sm is None:
            if salta:
                e.traccia.passo(f"Job {j + 1}: no machine has enough availability "
                                f"({_ra_testo(ra)}); the job is skipped.")
                e.saltati.append(j)
                continue
            e.traccia.passo(f"Job {j + 1}: no machine has enough availability "
                            f"({_ra_testo(ra)}): no feasible solution found.")
            e.ok = False
            return e
        scartate = [f"t[{j + 1}][{m + 1}] = {t[j][m]:g} > ra[{m + 1}] = {ra[m]:g}"
                    for m in range(sm) if t[j][m] > ra[m]]
        motivo = ("; ".join(scartate) + "; " if scartate else "")
        e.traccia.passo(
            f"Job {j + 1}: residual availabilities {_ra_testo(ra)}. {motivo}machine {sm + 1} "
            f"is the first with enough availability (t[{j + 1}][{sm + 1}] = {t[j][sm]:g} <= "
            f"{ra[sm]:g}){apre}: x[{j + 1}][{sm + 1}] = 1, ra[{sm + 1}] = {ra[sm]:g} - {t[j][sm]:g} "
            f"= {ra[sm] - t[j][sm]:g}.")
        e.x[(j, sm)] = 1
        e.y[sm] = 1
        ra[sm] -= t[j][sm]
        if not solo_aperte:
            aperte = max(aperte, sm + 1)
    return e


def best_fit(t, a, criterio, nome_criterio: str, salta: bool = False,
             solo_aperte: bool = False) -> Esito:
    """Best-fit: among the machines with enough availability, pick the one that
    minimises `criterio(j, m, ra)`.

    Criteria used in the course: the cost c[j][m] (minimum cost), the time t[j][m]
    (minimum time), the residual availability ra[m] (fullest machine) and the
    availability after the assignment ra[m] - t[j][m] (tightest fit).
    """
    n, k = len(t), len(a)
    e = Esito(x={}, y=[0] * k)
    ra = list(a)
    aperte = 0
    for j in range(n):
        limite = aperte if solo_aperte else k
        candidate = [(criterio(j, m, ra), m) for m in range(limite) if t[j][m] <= ra[m]]
        apre = ""
        if candidate:
            val, sm = min(candidate)
            dettagli = "; ".join(f"machine {m + 1}: {nome_criterio} = {v:g}" for v, m in
                                 sorted(candidate, key=lambda c: c[1]))
            motivo = f"feasible machines — {dettagli}; the minimum is machine {sm + 1}"
        elif solo_aperte and aperte < k and t[j][aperte] <= a[aperte]:
            sm = aperte
            aperte += 1
            motivo = f"no opened machine is enough, machine {sm + 1} is opened"
        else:
            if salta:
                e.traccia.passo(f"Job {j + 1}: no machine has enough availability "
                                f"({_ra_testo(ra)}); the job is skipped.")
                e.saltati.append(j)
                continue
            e.traccia.passo(f"Job {j + 1}: no machine has enough availability "
                            f"({_ra_testo(ra)}): no feasible solution found.")
            e.ok = False
            return e
        e.traccia.passo(
            f"Job {j + 1}: residual availabilities {_ra_testo(ra)}; {motivo}: "
            f"x[{j + 1}][{sm + 1}] = 1, ra[{sm + 1}] = {ra[sm]:g} - {t[j][sm]:g} = {ra[sm] - t[j][sm]:g}.")
        e.x[(j, sm)] = 1
        e.y[sm] = 1
        ra[sm] -= t[j][sm]
        if not solo_aperte:
            aperte = max(aperte, sm + 1)
    return e


def matrice(vettore, k: int):
    """Machine-independent times: the vector t_j becomes an n x k matrix."""
    return [[v] * k for v in vettore]
