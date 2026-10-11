/* Helper comuni alle ricette del laboratorio di «Modellazione MIP / MIP Modelling».
 *
 * Si carica DOPO interattivi.js (che definisce window.GI) e PRIMA delle ricette
 * gi-mip-*.js, che li trovano in window.GI_MIP. Raccoglie gli strumenti delle
 * ricette di Programmazione lineare (frazioni esatte, poliedri in R^2) e di
 * Algoritmi (passo per passo con ◀ ▶ Esegui, disegno che si rifà solo quando
 * cambia lo stato), più qualcosa di proprio del corso (punti interi, LP in due
 * variabili risolto in modo esatto, coppie di coordinate con il separatore giusto).
 *
 * Elenco completo e esempi d'uso: commento di ogni funzione qui sotto.
 */
(function () {
  "use strict";
  const GI = window.GI;
  const T = GI.T;

  // ------------------------------------------------------------ colori
  const scuro = () => (document.body && document.body.getAttribute("data-md-color-scheme")) === "slate";
  /** i colori del grafico (dal CSS --gi-…), già risolti in valori CSS:
   *  a..e cursori; rosso = regione ammissibile (rilassamento), blu = ottimo,
   *  viola = locale/secondario, grigio = riferimenti, verde = intero/ok, testo, muted, line, target */
  const COL = (st) => {
    const pr = (k, chiaro, buio) => {
      const v = st.colore(k);
      return /^(#|rgb|hsl)/.test(v) ? v : scuro() ? buio : chiaro;
    };
    return {
      a: pr("a", "#D9480F", "#FF8A4C"), b: pr("b", "#0E7490", "#3BC9DB"), c: pr("c", "#2B8A3E", "#63E6A0"),
      d: pr("d", "#C2255C", "#F783AC"), e: pr("e", "#B08900", "#FFD43B"),
      rosso: pr("ammissibile", "#E03131", "#FF6B6B"), blu: pr("ottimo", "#1971C2", "#4DABF7"),
      viola: pr("locale", "#9C36B5", "#DA77F2"), grigio: pr("orig", "#9aa5b1", "#6b7b8f"),
      target: pr("target", "#F08C00", "#FFA94D"), muted: pr("muted", "#5b6675", "#9fb0c3"),
      line: pr("line", "#e3e8ef", "#2a3b52"),
      verde: scuro() ? "#69DB7C" : "#2F9E44", testo: scuro() ? "#E9ECEF" : "#212529",
    };
  };
  /** testo in grassetto colorato / evidenziato (HTML) */
  const tinta = (c, html) => `<strong style="color:${c}">${html}</strong>`;
  const fondo = (c, html) => `<span style="background:color-mix(in srgb, ${c} 28%, transparent);border-radius:3px;padding:0 .2em">${html}</span>`;
  /** opzioni di board senza pan né zoom (grafici «a schema»: alberi, barre, scatole) */
  const OPZ = { pan: { enabled: false }, zoom: { enabled: false, wheel: false } };

  // ------------------------------------------------------------ cursori dall'esterno
  /** il campo <input> di un cursore (il motore mette aria-label = nome del cursore, senza «\») */
  const inputDi = (st, nome) => st.el.querySelector(`.gi-ctrl input[aria-label="${nome}"]`);
  const ctrlDi = (st, nome) => { const i = inputDi(st, nome); return i ? i.closest(".gi-ctrl") : null; };
  /** cambia l'intervallo [min, max] di un cursore e ci riporta dentro il valore */
  const intervallo = (st, nome, min, max) => {
    const i = inputDi(st, nome);
    if (!i) return;
    if (+i.min !== min) i.min = min;
    if (+i.max !== max) i.max = max;
    const v = Math.round(+i.value);
    if (v < min) i.value = min;
    else if (v > max) i.value = max;
  };
  const intero = (st, k) => Math.round(st.p()[k]);
  /** il cursore k (passo) va da 0 a K: restituisce il passo corrente, già nell'intervallo */
  const passoK = (st, K, nome = "k") => { intervallo(st, nome, 0, K); return Math.max(0, Math.min(K, intero(st, nome))); };
  /** la colonna di destra (controlli) del grafico */
  const pannello = (st) => st.el.querySelector(".gi-corpo").children[1];

  // ------------------------------------------------------------ passo per passo
  /** ferma «Esegui» */
  function ferma(st) {
    if (st.dati.timer) clearInterval(st.dati.timer);
    st.dati.timer = null;
    if (st.dati.play) st.dati.play.textContent = T("Esegui ⏵", "Run ⏵");
  }
  /** Pulsanti dei grafici passo per passo, messi sotto l'ultimo cursore:
   *  ◀ / ▶ (un passo sul cursore `opz.k`, default "k"), «Esegui» (avanza da solo
   *  fino alla fine; velocità lenta predefinita, media, veloce) e altri pulsanti
   *  `altri` = [[testo, titolo, funzione], …] (es. «Nuova istanza»).
   *  Va chiamato in monta(board, st): si crea una volta sola per grafico.
   *  opz.ritmo: millisecondi per passo alla velocità media (default 900;
   *  lenta = ritmo·2, veloce = ritmo·0,45). */
  function comandi(st, altri = [], opz = {}) {
    if (st.dati.comandi && st.el.contains(st.dati.comandi)) return;
    const nome = opz.k || "k";
    const ctrls = st.el.querySelectorAll(".gi-ctrl");
    const ultimo = ctrls[ctrls.length - 1];
    const box = GI.h("div", { class: "gi-comandi", style: "display:flex;flex-wrap:wrap;gap:.35em;margin:.3em 0 .4em" });
    const bt = (testo, titolo, fz, primario) => {
      const b = GI.h("button", { class: "gi-btn" + (primario ? " primario" : ""), title: titolo, "aria-label": titolo, style: "margin:0" }, testo);
      b.onclick = fz;
      box.append(b);
      return b;
    };
    const vai = (d) => {
      const i = inputDi(st, nome);
      if (!i) return false;
      const nuovo = Math.max(+i.min, Math.min(+i.max, Math.round(+i.value) + d));
      if (nuovo === Math.round(+i.value)) return false;
      st.imposta(nome, nuovo);
      return true;
    };
    if (inputDi(st, nome)) {
      bt("◀", T("un passo indietro", "one step back"), () => { ferma(st); vai(-1); });
      bt("▶", T("un passo avanti", "one step forward"), () => { ferma(st); vai(1); });
      const VEL = [[T("lenta", "slow"), 2], [T("media", "medium"), 1], [T("veloce", "fast"), 0.45]];
      const parti = () => {
        st.dati.timer = setInterval(() => {
          if (!document.body.contains(st.el) || !vai(1)) ferma(st);
        }, (opz.ritmo || 900) * VEL[st.dati.vel || 0][1]);
      };
      st.dati.play = bt(T("Esegui ⏵", "Run ⏵"), T("esegui fino alla fine", "run to the end"), () => {
        if (st.dati.timer) { ferma(st); return; }
        const i = inputDi(st, nome);
        if (i && +i.value >= +i.max) st.imposta(nome, +i.min);
        st.dati.play.textContent = T("Pausa ⏸", "Pause ⏸");
        parti();
      }, true);
      const sel = GI.h("select", { class: "gi-btn", title: T("velocità di «Esegui»", "speed of «Run»"), "aria-label": T("velocità", "speed"), style: "margin:0" },
        VEL.map(([n], j) => `<option value="${j}">${T("Velocità: ", "Speed: ") + n}</option>`).join(""));
      sel.value = st.dati.vel || 0;
      sel.onchange = () => { st.dati.vel = +sel.value; if (st.dati.timer) { clearInterval(st.dati.timer); parti(); } };
      box.append(sel);
    }
    for (const [testo, titolo, fz] of altri) bt(testo, titolo, () => { ferma(st); fz(); });
    if (ultimo) ultimo.after(box);
    else pannello(st).prepend(box);
    st.dati.comandi = box;
  }

  // ------------------------------------------------------------ disegno «a firma»
  /** Ridisegna gli oggetti del grafico solo se la firma dello stato è cambiata:
   *  costruisci(crea) crea gli oggetti con crea(tipo, parenti, attributi) (come
   *  board.create); alla firma successiva diversa vengono tolti e ricreati.
   *  Uso tipico in aggiorna(board, st): ridisegna(board, st, [k, scuro()].join("|"), (crea) => { … }). */
  function ridisegna(board, st, firma, costruisci) {
    const D = st.dati;
    if (D._board === board && D._firma === firma) return;
    if (D._board !== board) D._ogg = [];
    D._board = board; D._firma = firma;
    board.suspendUpdate();
    for (const o of D._ogg || []) { try { board.removeObject(o); } catch (e) { /* già tolto */ } }
    const ogg = [];
    const crea = (tipo, par, attr) => { const o = board.create(tipo, par, attr); ogg.push(o); return o; };
    try { costruisci(crea); } finally { D._ogg = ogg; board.unsuspendUpdate(); }
  }
  /** rettangolo, segmento, testo e poligono pieno come oggetti singoli (senza punti da togliere) */
  const rett = (crea, x0, y0, x1, y1, attr) =>
    crea("curve", [[x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0]],
      Object.assign({ fixed: true, highlight: false, strokeWidth: 1, fillColor: "none", fillOpacity: 0 }, attr));
  const linea = (crea, x0, y0, x1, y1, attr) =>
    crea("curve", [[x0, x1], [y0, y1]], Object.assign({ fixed: true, highlight: false, strokeWidth: 1 }, attr));
  const scritta = (crea, x, y, s, attr) =>
    crea("text", [x, y, String(s)], Object.assign({
      fixed: true, highlight: false, display: "internal", anchorX: "middle", anchorY: "middle", fontSize: 12,
    }, attr));
  const area = (crea, P, attr) => P.length < 2 ? null :
    crea("curve", [[...P.map((p) => p[0]), P[0][0]], [...P.map((p) => p[1]), P[0][1]]],
      Object.assign({ fixed: true, highlight: false, strokeWidth: 2, fillOpacity: 0.18 }, attr));
  const pallino = (crea, x, y, attr) =>
    crea("point", [x, y], Object.assign({ name: "", fixed: true, size: 3, highlight: false, showInfobox: false, withLabel: false }, attr));
  /** stessa unità sui due assi: allarga [x0, x1] x [y0, y1] fino alle proporzioni della board */
  const adatta = (board, x0, y1, x1, y0) => {
    const W = board.canvasWidth || 400, H = board.canvasHeight || 300;
    const u = Math.min(W / (x1 - x0), H / (y1 - y0)), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    board.setBoundingBox([cx - W / u / 2, cy + H / u / 2, cx + W / u / 2, cy - H / u / 2], false);
  };
  /** tabella HTML per le letture; corrente = indice della riga evidenziata (colore c) */
  const tab = (intest, righe, corrente, c) =>
    `<table class="gi-tabella"><tr>${intest.map((t) => `<th>${t}</th>`).join("")}</tr>` +
    righe.map((r, i) => `<tr${i === corrente ? ` style="background:color-mix(in srgb, ${c || "#D9480F"} 18%, transparent);font-weight:700"` : ""}>` +
      r.map((x) => `<td>${x}</td>`).join("") + `</tr>`).join("") + `</table>`;

  // ------------------------------------------------------------ casualità
  const casuale = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
  const mescola = (A) => { for (let i = A.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [A[i], A[j]] = [A[j], A[i]]; } return A; };
  /** generatore pseudo-casuale riproducibile: const r = seme(42); r() in [0, 1) */
  const seme = (s) => () => { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; };

  // ------------------------------------------------------------ frazioni esatte
  const gcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a || 1; };
  /** frazione ridotta {n, d} con d > 0 */
  const Q = (n, d = 1) => { if (d < 0) { n = -n; d = -d; } const g = gcd(n, d); return { n: n / g, d: d / g }; };
  const Qs = (s) => { const [n, d] = String(s).split("/"); return Q(parseInt(n, 10), d ? parseInt(d, 10) : 1); };
  const Qv = (q) => q.n / q.d;
  const Qeq = (a, b) => a.n === b.n && a.d === b.d;
  const Qadd = (a, b) => Q(a.n * b.d + b.n * a.d, a.d * b.d);
  const Qsub = (a, b) => Q(a.n * b.d - b.n * a.d, a.d * b.d);
  const Qmul = (a, b) => Q(a.n * b.n, a.d * b.d);
  const Qfloor = (q) => Math.floor(q.n / q.d);
  const Qceil = (q) => Math.ceil(q.n / q.d);
  const Qintero = (q) => q.d === 1;
  /** TeX della frazione: 3, -\tfrac{7}{2} */
  const Qtex = (q) => (q.d === 1 ? String(q.n) : `${q.n < 0 ? "-" : ""}\\tfrac{${Math.abs(q.n)}}{${q.d}}`);
  /** coppia di coordinate in TeX: (a; b) in italiano (virgola decimale), (a, b) in inglese */
  const SEP = () => (GI.EN ? ",\\ " : ";\\ ");
  const coppia = (a, b) => `\\big(${a}${SEP()}${b}\\big)`;
  const coppiaQ = (p) => coppia(Qtex(p[0]), Qtex(p[1]));
  /** a_1 x_1 + a_2 x_2 in TeX; coefficienti numeri o frazioni {n, d} */
  const lin = (cs, vars = ["x_1", "x_2"]) => {
    let s = "";
    cs.forEach((c, i) => {
      const q = typeof c === "number" ? Q(c) : c;
      if (q.n === 0) return;
      const neg = q.n < 0, abs = Q(Math.abs(q.n), q.d);
      const coef = abs.n === 1 && abs.d === 1 ? "" : Qtex(abs);
      s += (s ? (neg ? " - " : " + ") : neg ? "-" : "") + coef + vars[i];
    });
    return s || "0";
  };

  // ------------------------------------------------------------ poliedri in R^2
  // Un vincolo è {a: [a1, a2], b} e significa a1 x1 + a2 x2 <= b, con a1, a2, b INTERI
  // (per >= si cambia segno). nonneg() aggiunge x1 >= 0, x2 >= 0.
  const nonneg = () => [{ a: [-1, 0], b: 0, segno: true }, { a: [0, -1], b: 0, segno: true }];
  /** vertici esatti (frazioni): intersezioni di due rette che soddisfano tutti i vincoli */
  const verticiEsatti = (V) => {
    const out = [];
    for (let i = 0; i < V.length; i++) for (let j = i + 1; j < V.length; j++) {
      const [p, q] = [V[i], V[j]];
      let d = p.a[0] * q.a[1] - p.a[1] * q.a[0];
      if (d === 0) continue;
      let n1 = p.b * q.a[1] - p.a[1] * q.b, n2 = p.a[0] * q.b - p.b * q.a[0];
      if (d < 0) { n1 = -n1; n2 = -n2; d = -d; }
      if (!V.every((v) => v.a[0] * n1 + v.a[1] * n2 <= v.b * d)) continue;
      const P = [Q(n1, d), Q(n2, d)];
      if (!out.some((o) => Qeq(o[0], P[0]) && Qeq(o[1], P[1]))) out.push(P);
    }
    return out;
  };
  /** taglia il poligono P (lista di [x, y]) con il semipiano a·x <= b (Sutherland-Hodgman) */
  const taglia = (P, a, b) => {
    const out = [], f = (p) => a[0] * p[0] + a[1] * p[1] - b, tol = 1e-9 * (1 + Math.abs(b));
    for (let k = 0; k < P.length; k++) {
      const p = P[k], q = P[(k + 1) % P.length], fp = f(p), fq = f(q);
      if (fp <= tol) out.push(p);
      if ((fp < -tol && fq > tol) || (fp > tol && fq < -tol)) {
        const t = fp / (fp - fq);
        out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
      }
    }
    return out;
  };
  /** la regione {x : V} come poligono (in virgola mobile), dentro il quadrato [-L, L]^2:
   *  [] se vuota. Per disegnarla: area(crea, poligono(V), {strokeColor: C.rosso, fillColor: C.rosso}) */
  const poligono = (V, L = 1e3) => {
    let P = [[-L, -L], [L, -L], [L, L], [-L, L]];
    for (const v of V) { if (!P.length) break; P = taglia(P, v.a, v.b); }
    return P;
  };
  /** i punti interi (x1, x2) del riquadro [x0, x1] x [y0, y1] che soddisfano tutti i vincoli */
  const puntiInteri = (V, x0, x1, y0, y1) => {
    const out = [];
    for (let i = Math.ceil(x0); i <= Math.floor(x1); i++)
      for (let j = Math.ceil(y0); j <= Math.floor(y1); j++)
        if (V.every((v) => v.a[0] * i + v.a[1] * j <= v.b)) out.push([i, j]);
    return out;
  };
  /** Risolve in modo esatto max (o min) c1 x1 + c2 x2 su {x : V}, con c interi.
   *  Restituisce {stato: "ottimo" | "inammissibile" | "illimitato", x: [Q, Q], z: Q}.
   *  Illimitato se il poligono tocca il bordo del riquadro grande nella direzione di c. */
  const lp2 = (V, c, senso = "max") => {
    const s = senso === "max" ? 1 : -1;
    const P = poligono(V, 1e6);
    if (!P.length) return { stato: "inammissibile" };
    const zf = Math.max(...P.map((p) => s * (c[0] * p[0] + c[1] * p[1])));
    const vert = verticiEsatti(V);
    if (!vert.length) return { stato: "illimitato" };
    let best = null, bz = null;
    for (const p of vert) {
      const z = Qadd(Qmul(Q(c[0]), p[0]), Qmul(Q(c[1]), p[1]));
      if (!best || s * Qv(z) > s * Qv(bz) + 1e-12) { best = p; bz = z; }
    }
    if (zf > s * Qv(bz) + 1e-6 * (1 + Math.abs(Qv(bz)))) return { stato: "illimitato" };
    return { stato: "ottimo", x: best, z: bz };
  };
  /** ottimo intero per enumerazione nel riquadro (istanze piccole): {stato, x: [i, j], z} */
  const ip2 = (V, c, senso = "max", box = [0, 30, 0, 30]) => {
    const s = senso === "max" ? 1 : -1;
    let best = null;
    for (const p of puntiInteri(V, ...box)) {
      const z = c[0] * p[0] + c[1] * p[1];
      if (!best || s * z > s * best.z) best = { x: p, z };
    }
    return best ? Object.assign({ stato: "ottimo" }, best) : { stato: "inammissibile" };
  };
  /** involucro convesso (catena monotona) di una lista di punti [x, y] */
  const involucro = (pts) => {
    const P = pts.map((p) => p.slice()).sort((u, w) => u[0] - w[0] || u[1] - w[1]);
    if (P.length < 3) return P;
    const cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], hi = [];
    for (const p of P) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], p) <= 0) lo.pop(); lo.push(p); }
    for (const p of P.slice().reverse()) { while (hi.length >= 2 && cr(hi[hi.length - 2], hi[hi.length - 1], p) <= 0) hi.pop(); hi.push(p); }
    return lo.slice(0, -1).concat(hi.slice(0, -1));
  };
  /** TeX di un vincolo {a, b}: "2x_1 + 3x_2 \le 12" (rel per scegliere \ge con i segni cambiati) */
  const vincoloTex = (v, vars) => `${lin(v.a, vars)} \\le ${v.b}`;

  window.GI_MIP = {
    T, scuro, COL, tinta, fondo, OPZ,
    inputDi, ctrlDi, intervallo, intero, passoK, pannello,
    comandi, ferma,
    ridisegna, rett, linea, scritta, area, pallino, adatta, tab,
    casuale, mescola, seme,
    gcd, Q, Qs, Qv, Qeq, Qadd, Qsub, Qmul, Qfloor, Qceil, Qintero, Qtex, SEP, coppia, coppiaQ, lin,
    nonneg, verticiEsatti, taglia, poligono, puntiInteri, lp2, ip2, involucro, vincoloTex,
  };
})();
