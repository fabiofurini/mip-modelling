/* Laboratorio di «Modellazione MIP / MIP Modelling»: tre modelli del corso risolti
 * all'ottimo nel browser, ricalcolati a ogni cambio dei dati.
 *
 *   modelli-ottimi   tre voci, ognuna con la sua formula, il suo disegno e i suoi cursori:
 *     localizzazione   problema 8.1 (localizzazione capacitata): 2 sedi, 3 clienti;
 *                      cursori sui costi di installazione i_l e sulle capacità u_l
 *     lotti            problema 9.1 (lotti con costo fisso di setup): 5 giorni;
 *                      cursori sul costo di setup q, sul costo di magazzino h e sulla
 *                      domanda del giorno 4
 *     progetti         capitolo 5 (selezione di progetti con vincoli logici): 10 progetti,
 *                      budget b e le sei implicazioni dell'esercizio 2.1 accese e spente
 *   Per ogni voce: la soluzione ottima disegnata, z(MILP), le binarie che valgono 1,
 *   il rilassamento continuo z(LP+) (binarie in [0, 1], come m.relax() di Gurobi) e il gap.
 *
 * L'ottimo si trova enumerando tutte le assegnazioni delle binarie (4, 32 e 1024) e
 * risolvendo per ognuna il problema lineare nelle variabili continue con un simplesso
 * a due fasi (regola di Bland); lo stesso simplesso dà il rilassamento. Le istanze di
 * partenza sono quelle del corso (fam08_1_capacitata.py, fam09_1_lotti.py,
 * cap02_logica.py): z = 365, 390, 28 e z(LP+) = 317, 353,64, 29. Il confronto con
 * Gurobi su più combinazioni di dati è nella prova della pagina del laboratorio.
 */
(function () {
  "use strict";
  const GI = window.GI, M = window.GI_MIP;
  const T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};

  const EPS = 1e-9;
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

  // ------------------------------------------------------------ simplesso a due fasi
  /** P = {senso: "min"|"max", c, A, rel ("<=", ">=", "="), b, ub (Infinity = nessun limite)}, x >= 0.
   *  Restituisce {stato: "ottimo"|"inammissibile"|"illimitato", x, z}. */
  function simplesso(P) {
    const n = P.c.length, s = P.senso === "max" ? -1 : 1;
    const righe = P.A.map((a, i) => ({ a: a.slice(), rel: P.rel[i], b: P.b[i] }));
    if (P.ub) P.ub.forEach((u, j) => {
      if (isFinite(u)) { const a = new Array(n).fill(0); a[j] = 1; righe.push({ a, rel: "<=", b: u }); }
    });
    for (const r of righe) if (r.b < 0) {
      r.a = r.a.map((v) => -v); r.b = -r.b;
      r.rel = r.rel === "<=" ? ">=" : r.rel === ">=" ? "<=" : "=";
    }
    const m = righe.length;
    const nSl = righe.filter((r) => r.rel !== "=").length, nAr = righe.filter((r) => r.rel !== "<=").length;
    const N = n + nSl + nAr, Tb = [], base = [];
    let js = n, ja = n + nSl;
    for (const r of righe) {
      const row = new Array(N + 1).fill(0);
      r.a.forEach((v, j) => (row[j] = v));
      row[N] = r.b;
      if (r.rel === "<=") { row[js] = 1; base.push(js++); }
      else if (r.rel === ">=") { row[js++] = -1; row[ja] = 1; base.push(ja++); }
      else { row[ja] = 1; base.push(ja++); }
      Tb.push(row);
    }
    const pivot = (obj, r, j) => {
      const pr = Tb[r], pv = pr[j];
      for (let k = 0; k <= N; k++) pr[k] /= pv;
      for (let i = 0; i < m; i++) if (i !== r && Math.abs(Tb[i][j]) > 0) {
        const f = Tb[i][j];
        if (f !== 0) for (let k = 0; k <= N; k++) Tb[i][k] -= f * pr[k];
      }
      const f = obj[j];
      if (f !== 0) for (let k = 0; k <= N; k++) obj[k] -= f * pr[k];
      base[r] = j;
    };
    const esegui = (obj, ammessa) => {
      for (let it = 0; it < 5000; it++) {
        let j = -1;
        for (let k = 0; k < N; k++) if (ammessa(k) && obj[k] < -EPS) { j = k; break; }
        if (j < 0) return "ottimo";
        let r = -1, best = Infinity;
        for (let i = 0; i < m; i++) if (Tb[i][j] > EPS) {
          const q = Tb[i][N] / Tb[i][j];
          if (q < best - EPS || (Math.abs(q - best) <= EPS && base[i] < base[r])) { best = q; r = i; }
        }
        if (r < 0) return "illimitato";
        pivot(obj, r, j);
      }
      return "ottimo";
    };
    // fase 1: somma delle artificiali
    if (nAr) {
      const w = new Array(N + 1).fill(0);
      for (let k = n + nSl; k < N; k++) w[k] = 1;
      for (let i = 0; i < m; i++) if (base[i] >= n + nSl) for (let k = 0; k <= N; k++) w[k] -= Tb[i][k];
      esegui(w, () => true);
      if (-w[N] > 1e-7) return { stato: "inammissibile" };
      for (let i = 0; i < m; i++) if (base[i] >= n + nSl) {
        let j = -1;
        for (let k = 0; k < n + nSl; k++) if (Math.abs(Tb[i][k]) > 1e-7) { j = k; break; }
        if (j >= 0) pivot(w, i, j);
      }
    }
    // fase 2
    const obj = new Array(N + 1).fill(0);
    P.c.forEach((v, j) => (obj[j] = s * v));
    for (let i = 0; i < m; i++) { const f = obj[base[i]]; if (f !== 0) for (let k = 0; k <= N; k++) obj[k] -= f * Tb[i][k]; }
    const esito = esegui(obj, (k) => k < n + nSl);
    if (esito === "illimitato") return { stato: "illimitato" };
    const x = new Array(n).fill(0);
    for (let i = 0; i < m; i++) if (base[i] < n) x[base[i]] = Tb[i][N];
    return { stato: "ottimo", x, z: P.c.reduce((t, v, j) => t + v * x[j], 0) };
  }

  /** ottimo del MILP per enumerazione delle binarie `bin` (indici di variabili); il resto è continuo.
   *  piu = true: a parità di valore vince l'assegnazione con più binarie a 1 (altrimenti con meno).
   *  Restituisce anche quante assegnazioni delle binarie sono ottime (nOtt). */
  function milp(P, bin, piu) {
    const n = P.c.length, cont = n - bin.length, s = P.senso === "max" ? -1 : 1;
    let best = null, nOtt = 0;
    // a parità di valore: meno binarie a 1 (niente setup o sedi inutili) o, con piu, di più
    const pc = (x) => { let c = 0; while (x) { c += x & 1; x >>= 1; } return c; };
    const maschere = [...Array(1 << bin.length).keys()].sort((a, b) => (piu ? pc(b) - pc(a) : pc(a) - pc(b)) || a - b);
    for (const mask of maschere) {
      const v = bin.map((_, k) => (mask >> k) & 1);
      let r;
      if (!cont) {
        const x = new Array(n).fill(0);
        bin.forEach((j, k) => (x[j] = v[k]));
        const ok = P.A.every((a, i) => {
          const lhs = a.reduce((t, c, j) => t + c * x[j], 0);
          return P.rel[i] === "<=" ? lhs <= P.b[i] + EPS : P.rel[i] === ">=" ? lhs >= P.b[i] - EPS : Math.abs(lhs - P.b[i]) <= EPS;
        });
        r = ok ? { stato: "ottimo", x, z: P.c.reduce((t, c, j) => t + c * x[j], 0) } : null;
      } else {
        const A = P.A.slice(), rel = P.rel.slice(), b = P.b.slice();
        bin.forEach((j, k) => { const a = new Array(n).fill(0); a[j] = 1; A.push(a); rel.push("="); b.push(v[k]); });
        r = simplesso({ senso: P.senso, c: P.c, A, rel, b, ub: P.ub });
        if (r.stato !== "ottimo") r = null;
        else bin.forEach((j, k) => (r.x[j] = v[k]));
      }
      if (!r) continue;
      if (!best || s * r.z < s * best.z - 1e-7) { best = r; nOtt = 1; }
      else if (Math.abs(r.z - best.z) <= 1e-7) nOtt++;
    }
    return best ? Object.assign(best, { nOtt }) : { stato: "inammissibile" };
  }

  /** rilassamento continuo con le binarie in [0, 1] (z(LP+), come m.relax()) */
  function rilassamento(P, bin) {
    const ub = (P.ub || new Array(P.c.length).fill(Infinity)).slice();
    for (const j of bin) ub[j] = Math.min(ub[j], 1);
    return simplesso(Object.assign({}, P, { ub }));
  }

  // ------------------------------------------------------------ numeri
  const tondo = (v) => (Math.abs(v - Math.round(v)) < 1e-7 ? Math.round(v) : v);
  /** numero con al più due decimali (virgola in italiano) */
  const nm = (v) => { v = tondo(v); return Number.isInteger(v) ? String(v) : GI.num(v, 2); };
  /** lo stesso in testo semplice (etichette del disegno, non TeX) */
  const dec = (v, c) => { const t = String(+v.toFixed(c)); return GI.EN ? t : t.replace(".", ","); };
  const nmT = (v) => { v = tondo(v); return Number.isInteger(v) ? String(v) : dec(v, 2); };
  /** frazione con denominatore piccolo, altrimenti decimale (testo semplice) */
  function fraz(v) {
    v = tondo(v);
    if (Number.isInteger(v)) return String(v);
    for (let d = 2; d <= 12; d++) if (Math.abs(v * d - Math.round(v * d)) < 1e-7) return `${Math.round(v * d)}/${d}`;
    return dec(v, 2);
  }
  const pct = (x) => GI.num(100 * x, 1) + "\\,\\%";
  const tx = (s) => `\\(${s}\\)`;
  const pedici = (v, I) => I.map((j) => `${v}_{${j}}`).join(",\\ ");

  // ------------------------------------------------------------ le tre istanze del corso
  const LOC = { t: [[4, 5, 6], [6, 4, 3]], d: [8, 25, 27] };                       // problema 8.1
  const LOT = { d: [20, 10, 30, 40, 10], p: [2, 3, 2, 3, 2] };                     // problema 9.1
  const PRO = { r: [9, 7, 4, 8, 3, 6, 2, 5, 7, 6], c: [4, 3, 2, 4, 2, 3, 1, 3, 4, 3] };  // capitolo 5
  // le sei implicazioni dell'esercizio 2.1 e le loro clausole (come in cap02_progetti): [coefficienti per progetto, rel, b]
  const IMPL = [
    { tex: "x_2 \\Rightarrow x_3", cl: [[{ 2: -1, 3: 1 }, ">=", 0]] },
    { tex: "x_2 \\Rightarrow \\lnot x_4", cl: [[{ 2: 1, 4: 1 }, "<=", 1]] },
    { tex: "x_1 \\land x_6 \\Rightarrow x_7", cl: [[{ 1: 1, 6: 1, 7: -1 }, "<=", 1]] },
    { tex: "x_1 \\lor x_6 \\Rightarrow x_8", cl: [[{ 1: -1, 8: 1 }, ">=", 0], [{ 6: -1, 8: 1 }, ">=", 0]] },
    { tex: "x_2 \\land x_3 \\Rightarrow \\lnot x_9", cl: [[{ 2: 1, 3: 1, 9: 1 }, "<=", 2]] },
    { tex: "x_2 \\lor x_3 \\Rightarrow \\lnot x_{10}", cl: [[{ 2: 1, 10: 1 }, "<=", 1], [{ 3: 1, 10: 1 }, "<=", 1]] },
  ];

  /** i tre modelli: dati dai cursori -> {P, bin} */
  function modelloLoc(p) {
    const i = [p.i1, p.i2], u = [p.u1, p.u2], m = 2, n = 3, nv = m + m * n;
    const Y = (l, c) => m + l * n + c;
    const c = new Array(nv).fill(0);
    i.forEach((v, l) => (c[l] = v));
    for (let l = 0; l < m; l++) for (let k = 0; k < n; k++) c[Y(l, k)] = LOC.t[l][k];
    const A = [], rel = [], b = [];
    for (let l = 0; l < m; l++) {
      const a = new Array(nv).fill(0); a[l] = u[l];
      for (let k = 0; k < n; k++) a[Y(l, k)] = -1;
      A.push(a); rel.push(">="); b.push(0);
    }
    for (let k = 0; k < n; k++) {
      const a = new Array(nv).fill(0);
      for (let l = 0; l < m; l++) a[Y(l, k)] = 1;
      A.push(a); rel.push("="); b.push(LOC.d[k]);
    }
    return { P: { senso: "min", c, A, rel, b }, bin: [0, 1], i, u, Y };
  }
  function domandaLot(p) { const d = LOT.d.slice(); d[3] = p.d4; return d; }
  function modelloLot(p) {
    const d = domandaLot(p), n = d.length, X = (t) => t, S = (t) => n + t, Yv = (t) => 2 * n - 1 + t, nv = 3 * n - 1;
    const Mt = d.map((_, t) => d.slice(t).reduce((a, v) => a + v, 0));
    const c = new Array(nv).fill(0);
    for (let t = 0; t < n; t++) { c[X(t)] = LOT.p[t]; c[Yv(t)] = p.q; }
    for (let t = 0; t < n - 1; t++) c[S(t)] = p.h;
    const A = [], rel = [], b = [];
    for (let t = 0; t < n; t++) {
      const a = new Array(nv).fill(0); a[X(t)] = 1;
      if (t > 0) a[S(t - 1)] = 1;
      if (t < n - 1) a[S(t)] = -1;
      A.push(a); rel.push("="); b.push(d[t]);
    }
    for (let t = 0; t < n; t++) {
      const a = new Array(nv).fill(0); a[X(t)] = -1; a[Yv(t)] = Mt[t];
      A.push(a); rel.push(">="); b.push(0);
    }
    return { P: { senso: "min", c, A, rel, b }, bin: d.map((_, t) => Yv(t)), d, Mt, X, S, Yv };
  }
  function modelloPro(p, attive) {
    const n = 10, A = [PRO.c.slice()], rel = ["<="], b = [p.b];
    IMPL.forEach((im, k) => {
      if (!attive[k]) return;
      for (const [co, r, rhs] of im.cl) {
        const a = new Array(n).fill(0);
        for (const [j, v] of Object.entries(co)) a[+j - 1] = v;
        A.push(a); rel.push(r); b.push(rhs);
      }
    });
    return { P: { senso: "max", c: PRO.r.slice(), A, rel, b }, bin: [...Array(n).keys()], piu: true };
  }

  const VOCI = {
    localizzazione: {
      etichetta: T("Localizzazione", "Facility location"),
      cursori: ["i_1", "i_2", "u_1", "u_2"],
      modello: (p) => modelloLoc(p),
    },
    lotti: {
      etichetta: T("Lotti con setup", "Lot sizing"),
      cursori: ["q", "h", "d_4"],
      modello: (p) => modelloLot(p),
    },
    progetti: {
      etichetta: T("Progetti e logica", "Projects and logic"),
      cursori: ["b"],
      modello: (p, st) => modelloPro(p, attiveDi(st)),
    },
  };
  const attiveDi = (st) => st.dati.attive || (st.dati.attive = IMPL.map(() => true));

  /** il calcolo, ripetuto solo se cambiano voce, cursori o implicazioni */
  function analisi(st) {
    const k = st.chiave(), p = st.p(), D = st.dati;
    const firma = k + "|" + VOCI[k].cursori.map((n) => p[chiaveDi[n]]).join(",") + "|" + attiveDi(st).join("");
    if (D.an && D.an.firma === firma) return D.an;
    const Mo = VOCI[k].modello(p, st);
    const ott = milp(Mo.P, Mo.bin, Mo.piu), lp = rilassamento(Mo.P, Mo.bin);
    const A = { firma, k, p, Mo, ott, lp };
    if (k === "progetti") {
      // senza vincoli logici, per confronto
      A.libero = milp(modelloPro(p, IMPL.map(() => false)).P, Mo.bin, true);
    }
    D.an = A;
    return A;
  }
  /** gap fra z(MILP) e z(LP+), relativo a z(MILP) */
  const gapDi = (A) => (A.ott.stato === "ottimo" && A.lp.stato === "ottimo" && Math.abs(A.ott.z) > EPS
    ? Math.abs(A.ott.z - A.lp.z) / Math.abs(A.ott.z) : null);

  // ------------------------------------------------------------ cursori
  const PAR = [
    { k: "i1", nome: "i_1", min: 0, max: 150, step: 5, val: 60, colore: "a", cifre: 0 },
    { k: "i2", nome: "i_2", min: 0, max: 150, step: 5, val: 90, colore: "a", cifre: 0 },
    { k: "u1", nome: "u_1", min: 0, max: 80, step: 5, val: 50, colore: "c", cifre: 0 },
    { k: "u2", nome: "u_2", min: 0, max: 80, step: 5, val: 50, colore: "c", cifre: 0 },
    { k: "q", nome: "q", min: 0, max: 150, step: 5, val: 50, colore: "a", cifre: 0, descr: T("costo fisso di setup, uguale ogni giorno", "fixed setup cost, the same every day") },
    { k: "h", nome: "h", min: 0, max: 4, step: 0.5, val: 1, colore: "b", cifre: 1, descr: T("costo di magazzino per unità e giorno", "holding cost per unit and day") },
    { k: "d4", nome: "d_4", min: 0, max: 80, step: 5, val: 40, colore: "c", cifre: 0, descr: T("domanda del giorno 4", "demand on day 4") },
    { k: "b", nome: "b", min: 0, max: 30, step: 1, val: 14, colore: "a", cifre: 0, descr: T("budget per i progetti", "budget for the projects") },
  ];
  const chiaveDi = Object.fromEntries(PAR.map((q) => [q.nome, q.k]));

  /** mostra solo i cursori della voce scelta, la domanda «Prova tu» della voce e,
   *  per i progetti, i pulsanti delle implicazioni */
  function preparaPannello(st) {
    const k = st.chiave(), V = VOCI[k];
    for (const q of PAR) {
      const c = M.ctrlDi(st, q.nome);
      if (c) c.style.display = V.cursori.includes(q.nome) ? "" : "none";
    }
    const dom = st.el.querySelector(".gi-domanda");
    if (dom) {
      const forte = dom.querySelector("strong");
      dom.innerHTML = (forte ? forte.outerHTML + " " : "") + GI.mj(DOMANDE[k]);
      GI.typeset(dom);
    }
    // l'«Azzera» del motore riporta anche le implicazioni tutte accese
    const pan = M.pannello(st);
    const az = [...pan.querySelectorAll("button.gi-btn")].find((b) => b.textContent === T("Azzera", "Reset"));
    if (az && !az.dataset.impl) {
      az.dataset.impl = "1";
      az.addEventListener("click", () => { st.dati.attive = IMPL.map(() => true); st.dati.an = null; aggiornaChips(st); st.aggiorna(); });
    }
    let box = st.dati.boxImpl;
    if (!box || !st.el.contains(box)) {
      box = GI.h("div", { class: "gi-implicazioni", style: "margin:.2em 0 .4em" });
      box.append(GI.h("div", { style: "margin-bottom:.2em" },
        `<strong>${T("Implicazioni (esercizio 2.1)", "Implications (exercise 2.1)")}</strong> <small style="color:var(--gi-muted)">${T("clic per spegnerle o riaccenderle", "click to switch them off or on")}</small>`));
      const chips = GI.h("div", { class: "gi-chips", style: "margin:.2em 0 .2em" });
      IMPL.forEach((im, j) => {
        const b = GI.h("button", { class: "gi-chip", "aria-pressed": "true", style: "padding:.15em .6em" }, `(${j + 1}) \\(${im.tex}\\)`);
        b.onclick = () => { const a = attiveDi(st); a[j] = !a[j]; aggiornaChips(st); st.aggiorna(); };
        chips.append(b);
      });
      box.append(chips);
      const ctrl = M.ctrlDi(st, "b");
      ctrl.after(box);
      st.dati.boxImpl = box;
      GI.typeset(box);
    }
    box.style.display = k === "progetti" ? "" : "none";
    aggiornaChips(st);
  }
  function aggiornaChips(st) {
    const box = st.dati.boxImpl;
    if (!box) return;
    const a = attiveDi(st);
    box.querySelectorAll(".gi-chip").forEach((b, j) => b.setAttribute("aria-pressed", String(a[j])));
  }

  const DOMANDE = {
    localizzazione: T("Con \\(u_1 = u_2 = 50\\) la domanda totale (60 litri) obbliga ad aprire tutte e due le sedi. Porta \\(u_1\\) a 60 o più: per quali valori di \\(i_1\\) e \\(i_2\\) conviene chiudere una sede? Perché il rilassamento apre le sedi solo «in parte», e il gap cresce con i costi di installazione?",
      "With \\(u_1 = u_2 = 50\\) the total demand (60 litres) forces both sites to open. Move \\(u_1\\) to 60 or more: for which values of \\(i_1\\) and \\(i_2\\) is it better to close one site? Why does the relaxation open the sites only «in part», and why does the gap grow with the opening costs?"),
    lotti: T("Porta \\(q\\) a 0: quanti setup fa l'ottimo, e perché il gap sparisce? Poi alza \\(q\\): da quale valore conviene produrre tutto il primo giorno? Con \\(h\\) alto, che cosa succede alle scorte? Nel rilassamento \\(\\tilde y_t = x_t / M_t\\): perché paga solo una frazione del setup?",
      "Move \\(q\\) to 0: how many setups does the optimum make, and why does the gap vanish? Then raise \\(q\\): from which value is it better to produce everything on day 1? With a high \\(h\\), what happens to the stock? In the relaxation \\(\\tilde y_t = x_t / M_t\\): why does it pay only a fraction of the setup?"),
    progetti: T("Spegni tutte le implicazioni: l'ottimo sale a 30. Quali implicazioni, riaccese una alla volta, lo fanno scendere, e perché le altre non contano? Muovi \\(b\\): per quali budget il rilassamento dà già l'ottimo intero?",
      "Switch off all the implications: the optimum rises to 30. Which implications, switched on one at a time, make it go down, and why do the others not matter? Move \\(b\\): for which budgets does the relaxation already give the integer optimum?"),
  };

  // ------------------------------------------------------------ disegno (coordinate in pixel, y verso l'alto)
  const dim = (board) => {
    const el = board.containerObj, cw = el ? el.clientWidth : 0, ch = el ? el.clientHeight : 0;
    if (cw > 0 && ch > 0 && (Math.abs(cw - board.canvasWidth) > 1 || Math.abs(ch - board.canvasHeight) > 1)) board.resizeContainer(cw, ch, true, true);
    return [Math.round(board.canvasWidth || 600), Math.round(board.canvasHeight || 400)];
  };
  function osservaDimensioni(board, st) {
    if (st.dati.ro) st.dati.ro.disconnect();
    if (!window.ResizeObserver || !board.containerObj) return;
    st.dati.ro = new ResizeObserver(() => {
      if (!document.body.contains(st.el) || st.board !== board) return;
      const [w, h] = [board.containerObj.clientWidth, board.containerObj.clientHeight];
      if (w > 0 && h > 0 && st.dati.roDim !== w + "x" + h) { st.dati.roDim = w + "x" + h; st.aggiorna(); }
    });
    st.dati.ro.observe(board.containerObj);
  }
  const sfondo = (C) => (M.scuro() ? "#101b29" : "#ffffff");

  /** in testa al disegno: z(MILP), z(LP+) e gap (o «inammissibile») */
  function riga(crea, A, W, H, C, fs) {
    const y = H - fs * 1.15, o = A.ott;
    if (o.stato !== "ottimo") {
      M.scritta(crea, 12, y, T("inammissibile: u₁ + u₂ < 60, la domanda non si soddisfa", "infeasible: u₁ + u₂ < 60, the demand cannot be met"),
        { anchorX: "left", fontSize: fs * 1.05, strokeColor: C.rosso, cssStyle: "font-weight:700" });
      return;
    }
    const g = gapDi(A), pezzi = [
      [`z(MILP) = ${nmT(o.z)}`, C.blu], [`z(LP⁺) = ${nmT(A.lp.z)}`, C.rosso],
      [`gap ${g === null ? "—" : dec(100 * g, 1) + " %"}`, C.testo],
    ];
    let x = 12;
    for (const [t, c] of pezzi) {
      M.scritta(crea, x, y, t, { anchorX: "left", fontSize: fs * 1.08, strokeColor: c, cssStyle: "font-weight:700" });
      x += t.length * fs * 0.62 + fs * 1.4;
    }
  }

  /** 8.1: sedi a sinistra, clienti a destra, flussi dell'ottimo come archi spessi */
  function disegnaLoc(crea, A, W, H, C) {
    const fs = clamp(Math.min(W, H) / 27, 10, 16), Mo = A.Mo, o = A.ott, lp = A.lp;
    riga(crea, A, W, H, C, fs);
    const xs = W * (W < 500 ? 0.27 : 0.25), xc = W * (W < 500 ? 0.76 : 0.72);
    const ys = [H * 0.64, H * 0.3], yc = [H * 0.76, H * 0.47, H * 0.2];
    const lato = clamp(Math.min(W, H) * 0.13, 34, 62), rag = clamp(Math.min(W, H) * 0.05, 14, 26);
    const ok = o.stato === "ottimo";
    const fmax = Math.max(...LOC.d);
    // archi
    for (let l = 0; l < 2; l++) for (let c = 0; c < 3; c++) {
      const f = ok ? tondo(o.x[Mo.Y(l, c)]) : 0;
      const x0 = xs + lato / 2, y0 = ys[l], x1 = xc - rag, y1 = yc[c];
      if (f > EPS) M.linea(crea, x0, y0, x1, y1, { strokeColor: C.blu, strokeWidth: 2 + 9 * f / fmax, strokeOpacity: 0.75 });
      else M.linea(crea, x0, y0, x1, y1, { strokeColor: C.grigio, strokeWidth: 1.2, dash: 2, strokeOpacity: 0.8 });
      const tt = 0.22, tx0 = x0 + tt * (x1 - x0), ty0 = y0 + tt * (y1 - y0);
      M.scritta(crea, tx0, ty0 + fs * 0.75, `t=${LOC.t[l][c]}`, { fontSize: fs * 0.82, strokeColor: C.muted });
      if (f > EPS) {
        const tm = 0.62, mx = x0 + tm * (x1 - x0), my = y0 + tm * (y1 - y0);
        M.scritta(crea, mx, my + fs * 0.85, nmT(f), { fontSize: fs, strokeColor: C.blu, cssStyle: "font-weight:700" });
      }
    }
    // sedi
    for (let l = 0; l < 2; l++) {
      const aperta = ok && o.x[l] > 0.5, y = ys[l];
      M.rett(crea, xs - lato / 2, y - lato / 2, xs + lato / 2, y + lato / 2, aperta
        ? { strokeColor: C.blu, fillColor: C.blu, fillOpacity: 0.28, strokeWidth: 2.5 }
        : { strokeColor: C.grigio, fillColor: sfondo(C), fillOpacity: 1, strokeWidth: 2, dash: 2 });
      M.scritta(crea, xs, y, String(l + 1), { fontSize: fs * 1.35, strokeColor: aperta ? C.blu : C.muted, cssStyle: "font-weight:700" });
      M.scritta(crea, xs, y + lato / 2 + fs * 0.9, (aperta ? T("aperta", "open") : T("chiusa", "closed")) + `: x${["₁", "₂"][l]} = ${aperta ? 1 : 0}`,
        { fontSize: fs, strokeColor: aperta ? C.blu : C.muted, cssStyle: "font-weight:600" });
      M.scritta(crea, xs, y - lato / 2 - fs * 0.85, `i=${Mo.i[l]} · u=${Mo.u[l]}`, { fontSize: fs * 0.9, strokeColor: C.testo });
      // capacità usata: barra verticale a sinistra
      const usati = ok ? [0, 1, 2].reduce((s, c) => s + o.x[Mo.Y(l, c)], 0) : 0;
      const bx = xs - lato / 2 - 14, h0 = y - lato / 2, h1 = y + lato / 2;
      M.rett(crea, bx - 5, h0, bx + 5, h1, { strokeColor: C.muted, strokeWidth: 1 });
      if (Mo.u[l] > 0 && usati > EPS) M.rett(crea, bx - 5, h0, bx + 5, h0 + (h1 - h0) * Math.min(1, usati / Mo.u[l]), { strokeColor: "none", fillColor: C.blu, fillOpacity: 0.6 });
      M.scritta(crea, bx - 8, y, `${nmT(usati)}/${Mo.u[l]}`, { anchorX: "right", fontSize: fs * 0.85, strokeColor: C.muted });
      if (lp.stato === "ottimo") M.scritta(crea, xs, y - lato / 2 - fs * 2.05, `x̃${["₁", "₂"][l]} = ${fraz(lp.x[l])}`, { fontSize: fs * 0.95, strokeColor: C.rosso, cssStyle: "font-weight:600" });
    }
    // clienti
    for (let c = 0; c < 3; c++) {
      crea("circle", [[xc, yc[c]], rag], { fixed: true, highlight: false, strokeColor: C.verde, strokeWidth: 2, fillColor: C.verde, fillOpacity: 0.18 });
      M.scritta(crea, xc, yc[c], String(c + 1), { fontSize: fs * 1.2, strokeColor: C.verde, cssStyle: "font-weight:700" });
      M.scritta(crea, xc + rag + 6, yc[c], `d=${LOC.d[c]}`, { anchorX: "left", fontSize: fs, strokeColor: C.testo });
    }
    M.scritta(crea, xs, fs * 0.9, T("sedi", "sites"), { fontSize: fs, strokeColor: C.muted, cssStyle: "font-style:italic" });
    M.scritta(crea, xc, fs * 0.9, T("clienti", "customers"), { fontSize: fs, strokeColor: C.muted, cssStyle: "font-style:italic" });
  }

  /** 9.1: per ogni giorno domanda e produzione, i setup sotto l'asse, le scorte fra un giorno e l'altro */
  function disegnaLot(crea, A, W, H, C) {
    const Mo = A.Mo, o = A.ott, lp = A.lp, d = Mo.d, n = d.length;
    const fs = clamp(Math.min(W, H) / 28, 10, 16);
    riga(crea, A, W, H, C, fs);
    const sx = W < 500 ? 34 : 70, dx = 10, top = fs * 3.4, bot = fs * 5.2;
    const prod = d.map((_, t) => tondo(o.x[Mo.X(t)]));
    const sc = d.slice(0, n - 1).map((_, t) => tondo(o.x[Mo.S(t)]));
    const vmax = Math.max(10, ...prod, ...d, ...sc) * 1.12;
    const g = (W - sx - dx) / n, y0 = bot, ky = (H - top - bot) / vmax;
    const X0 = (t) => sx + t * g;
    // griglia
    const passo = vmax > 100 ? 25 : vmax > 50 ? 20 : 10;
    for (let v = 0; v <= vmax; v += passo) {
      M.linea(crea, sx - 4, y0 + v * ky, W - dx, y0 + v * ky, { strokeColor: C.line, strokeWidth: 1 });
      M.scritta(crea, sx - 8, y0 + v * ky, String(v), { anchorX: "right", fontSize: fs * 0.8, strokeColor: C.muted });
    }
    M.linea(crea, sx - 4, y0, W - dx, y0, { strokeColor: C.muted, strokeWidth: 1.5 });
    const bw = g * 0.3;
    for (let t = 0; t < n; t++) {
      const xm = X0(t) + g / 2;
      // domanda
      M.rett(crea, xm - bw - 2, y0, xm - 2, y0 + d[t] * ky, { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0.25, strokeWidth: 1.5 });
      M.scritta(crea, xm - bw / 2 - 2, y0 + d[t] * ky + fs * 0.7, String(d[t]), { fontSize: fs * 0.85, strokeColor: C.muted });
      // produzione
      if (prod[t] > EPS) {
        M.rett(crea, xm + 2, y0, xm + bw + 2, y0 + prod[t] * ky, { strokeColor: C.blu, fillColor: C.blu, fillOpacity: 0.5, strokeWidth: 2 });
        M.scritta(crea, xm + bw / 2 + 2, y0 + prod[t] * ky + fs * 0.7, nmT(prod[t]), { fontSize: fs * 0.9, strokeColor: C.blu, cssStyle: "font-weight:700" });
      }
      // righe sotto l'asse: giorno, setup, rilassamento
      M.scritta(crea, xm, y0 - fs * 1.0, W < 500 ? `t=${t + 1}` : T(`giorno ${t + 1}`, `day ${t + 1}`), { fontSize: fs * 0.9, strokeColor: C.testo });
      const attivo = o.x[Mo.Yv(t)] > 0.5;
      M.scritta(crea, xm, y0 - fs * 2.4, `y=${setup ? 1 : 0}`, { fontSize: fs, strokeColor: setup ? C.blu : C.muted, cssStyle: setup ? "font-weight:700" : "" });
      if (attivo) M.rett(crea, xm - fs * 1.7, y0 - fs * 3.05, xm + fs * 1.7, y0 - fs * 1.75, { strokeColor: C.blu, strokeWidth: 1.5 });
      if (lp.stato === "ottimo") M.scritta(crea, xm, y0 - fs * 3.9, `ỹ=${fraz(lp.x[Mo.Yv(t)])}`, { fontSize: fs * 0.88, strokeColor: C.rosso });
    }
    // scorte: frecce arancioni dal giorno t al giorno t + 1
    for (let t = 0; t < n - 1; t++) if (sc[t] > EPS) {
      const xa = X0(t) + g / 2 + bw + 4, xb = X0(t + 1) + g / 2 - bw - 4, yy = y0 + Math.max(sc[t] * ky, fs * 0.6);
      crea("arrow", [[xa, yy], [xb, yy]], { strokeColor: C.target, strokeWidth: 2.5, fixed: true, highlight: false, lastArrow: { type: 2, size: 5 } });
      M.scritta(crea, (xa + xb) / 2, yy + fs * 0.75, (W < 500 ? "" : "s=") + nmT(sc[t]), { fontSize: fs * 0.85, strokeColor: C.target, cssStyle: "font-weight:700" });
    }
    if (W >= 420) {
      M.scritta(crea, sx - 8, y0 - fs * 2.4, T("setup", "setup"), { anchorX: "right", fontSize: fs * 0.82, strokeColor: C.muted });
      M.scritta(crea, sx - 8, y0 - fs * 3.9, "LP", { anchorX: "right", fontSize: fs * 0.82, strokeColor: C.rosso });
    }
  }

  /** capitolo 5: i dieci progetti come schede, il rilassamento sotto ognuna, il budget in fondo */
  function disegnaPro(crea, A, W, H, C, st) {
    const o = A.ott, lp = A.lp, b = A.p.b, n = 10;
    const fs = clamp(Math.min(W, H) / 28, 10, 16);
    riga(crea, A, W, H, C, fs);
    const mg = W < 500 ? 4 : 12, col = 5, rig = 2, cima = H - fs * 2.3;
    const gw = (W - 2 * mg) / col, alt = H * 0.58, gh = alt / rig;
    const presi = o.stato === "ottimo" ? o.x.map((v) => v > 0.5) : new Array(n).fill(false);
    for (let j = 0; j < n; j++) {
      const r = Math.floor(j / col), c = j % col;
      const x0 = mg + c * gw + 3, x1 = x0 + gw - 6, y1 = cima - r * gh - 3, y0 = y1 - gh + 6;
      M.rett(crea, x0, y0, x1, y1, presi[j]
        ? { strokeColor: C.blu, fillColor: C.blu, fillOpacity: 0.25, strokeWidth: 2.5 }
        : { strokeColor: C.grigio, strokeWidth: 1.5 });
      const xm = (x0 + x1) / 2, hh = y1 - y0;
      M.scritta(crea, xm, y1 - hh * 0.2, (W < 500 ? "" : T("progetto ", "project ")) + (j + 1), { fontSize: fs * (W < 500 ? 1.15 : 1), strokeColor: presi[j] ? C.blu : C.testo, cssStyle: "font-weight:700" });
      M.scritta(crea, xm, y1 - hh * 0.43, `r=${PRO.r[j]}  c=${PRO.c[j]}`, { fontSize: fs * (W < 500 ? 0.78 : 0.92), strokeColor: C.testo });
      // rilassamento: barra rossa con x̃_p
      if (lp.stato === "ottimo") {
        const v = clamp(tondo(lp.x[j]), 0, 1), bx0 = x0 + 5, bx1 = x1 - 5, by = y0 + hh * 0.22;
        M.rett(crea, bx0, by - 4, bx1, by + 4, { strokeColor: C.rosso, strokeWidth: 1, strokeOpacity: 0.6 });
        if (v > EPS) M.rett(crea, bx0, by - 4, bx0 + (bx1 - bx0) * v, by + 4, { strokeColor: "none", fillColor: C.rosso, fillOpacity: 0.6 });
        M.scritta(crea, xm, by + fs * 0.95, (W < 500 ? "" : "x̃=") + fraz(v), { fontSize: fs * 0.85, strokeColor: C.rosso });
      }
    }
    // budget: barra lunga b, riempita dai costi dei progetti scelti
    const u = (W - 2 * mg - (W < 500 ? 10 : 90)) / 30, by = H * 0.15, x0 = mg + (W < 500 ? 4 : 80);
    M.scritta(crea, x0 - 8, by, W < 500 ? "" : T("budget", "budget"), { anchorX: "right", fontSize: fs, strokeColor: C.muted, cssStyle: "font-weight:600" });
    let x = x0, costo = 0;
    for (let j = 0; j < n; j++) if (presi[j]) {
      M.rett(crea, x, by - 13, x + PRO.c[j] * u, by + 13, { strokeColor: C.blu, fillColor: C.blu, fillOpacity: 0.4, strokeWidth: 1.5 });
      if (PRO.c[j] * u > fs) M.scritta(crea, x + PRO.c[j] * u / 2, by, String(j + 1), { fontSize: fs * 0.9, strokeColor: C.testo });
      x += PRO.c[j] * u; costo += PRO.c[j];
    }
    M.rett(crea, x0, by - 17, x0 + b * u, by + 17, { strokeColor: C.testo, strokeWidth: 2 });
    for (let v = 0; v <= 30; v += 5) M.scritta(crea, x0 + v * u, by - 17 - fs * 0.8, String(v), { fontSize: fs * 0.75, strokeColor: C.muted });
    M.scritta(crea, x0, by + 17 + fs * 0.9, T(`costo ${costo} su b = ${b}`, `cost ${costo} out of b = ${b}`), { anchorX: "left", fontSize: fs * 0.95, strokeColor: C.testo });
  }

  // ------------------------------------------------------------ letture
  function letture(A, C) {
    const o = A.ott, lp = A.lp, k = A.k, Mo = A.Mo;
    if (o.stato !== "ottimo") {
      return M.tinta(C.rosso, T("Il modello è inammissibile", "The model is infeasible")) +
        T(": la capacità totale \\(u_1 + u_2\\) è minore della domanda totale \\(60\\).", ": the total capacity \\(u_1 + u_2\\) is smaller than the total demand \\(60\\).");
    }
    const g = gapDi(A);
    const righe = [
      [M.tinta(C.blu, tx("\\zmilp")), tx(nm(o.z))],
      [M.tinta(C.rosso, tx("\\zlpp")), tx(nm(lp.z))],
      [T("gap", "gap"), g === null ? "—" : tx(pct(g))],
    ];
    let r = M.tab([T(k === "progetti" ? "massimo" : "minimo", k === "progetti" ? "maximum" : "minimum"), T("valore", "value")], righe);
    let uno, extra = "";
    if (k === "localizzazione") {
      uno = Mo.bin.filter((j) => o.x[j] > 0.5).map((j) => j + 1);
      const fisso = uno.reduce((s, l) => s + Mo.i[l - 1], 0);
      extra = T(`Costo di installazione \\(${fisso}\\), trasporto \\(${nm(o.z - fisso)}\\).`,
        `Opening cost \\(${fisso}\\), transport \\(${nm(o.z - fisso)}\\).`);
      uno = pedici("x", uno);
    } else if (k === "lotti") {
      const gi = Mo.d.map((_, t) => t).filter((t) => o.x[Mo.Yv(t)] > 0.5);
      const costoSetup = gi.length * A.p.q, mag = Mo.d.slice(0, -1).reduce((s, _, t) => s + A.p.h * o.x[Mo.S(t)], 0);
      extra = T(`Setup \\(${gi.length} \\cdot ${A.p.q} = ${nm(costoSetup)}\\), produzione \\(${nm(o.z - costoSetup - mag)}\\), magazzino \\(${nm(mag)}\\). Big-M: \\(M_t = d_t + \\dots + d_5\\) = ${Mo.Mt.join(", ")}.`,
        `Setups \\(${gi.length} \\cdot ${A.p.q} = ${nm(costoSetup)}\\), production \\(${nm(o.z - costoSetup - mag)}\\), holding \\(${nm(mag)}\\). Big-M: \\(M_t = d_t + \\dots + d_5\\) = ${Mo.Mt.join(", ")}.`);
      uno = pedici("y", gi.map((t) => t + 1));
    } else {
      const pr = o.x.map((v, j) => (v > 0.5 ? j + 1 : 0)).filter(Boolean);
      const lib = A.libero, att = A.Mo.P.A.length - 1;
      const libP = lib.x.map((v, j) => (v > 0.5 ? j + 1 : 0)).filter(Boolean);
      extra = T(`Senza vincoli logici: \\(z = ${nm(lib.z)}\\) (progetti ${libP.join(", ") || "—"}). Clausole nel modello: ${att}.`,
        `Without logical constraints: \\(z = ${nm(lib.z)}\\) (projects ${libP.join(", ") || "—"}). Clauses in the model: ${att}.`);
      if (o.nOtt > 1) extra += " " + T(`Ci sono ${o.nOtt} soluzioni ottime: se ne mostra una.`, `There are ${o.nOtt} optimal solutions: one is shown.`);
      uno = pedici("x", pr);
    }
    r += `<div style="margin-top:.35em">${T("Binarie a 1", "Binaries at 1")}: ${uno ? tx(uno) : "—"}</div>`;
    return r + `<div style="margin-top:.3em">${extra}</div>`;
  }

  // ------------------------------------------------------------ formule (due righe al massimo)
  function formula(st) {
    const k = st.chiave(), C = M.COL(st);
    const a = (tex) => st.col("a", tex), b = (tex) => st.col("b", tex), c = (tex) => st.col("c", tex);
    if (k === "localizzazione")
      return `\\begin{gathered}\\min\\ \\textstyle\\sum_{l} ${a("i_l")}\\,x_l + \\sum_{l,c} t_{lc}\\,y_{lc}\\\\ ` +
        `\\textstyle\\sum_{c} y_{lc} \\le ${c("u_l")}\\,x_l,\\ \\ \\sum_{l} y_{lc} = d_c,\\ \\ x_l \\in \\{0,1\\},\\ y_{lc} \\ge 0\\end{gathered}`;
    if (k === "lotti")
      return `\\begin{gathered}\\min\\ \\textstyle\\sum_{t} (p_t\\,x_t + ${a("q")}\\,y_t) + ${b("h")}\\sum_{t<5} s_t\\\\ ` +
        `s_{t-1} + x_t - s_t = ${c("d_t")},\\ \\ x_t \\le M_t\\,y_t,\\ \\ y_t \\in \\{0,1\\},\\ x_t, s_t \\ge 0\\end{gathered}`;
    return `\\begin{gathered}\\max\\ \\textstyle\\sum_{p} r_p\\,x_p\\\\ ` +
      `\\textstyle\\sum_{p} c_p\\,x_p \\le ${a("b")},\\ \\ \\text{${st.el.clientWidth < 600 ? T("clausole accese", "active clauses") : T("clausole delle implicazioni accese", "clauses of the active implications")}},\\ \\ x_p \\in \\{0,1\\}\\end{gathered}`;
  }

  /** la formula (due righe) entra nella larghezza: se serve si riduce il corpo del carattere */
  function adattaFormula(st) {
    const f = st.el.querySelector(".gi-formula");
    if (!f || st.dati.moFormula) return;
    // in home (griglia a una colonna «1fr») la formula larga allargherebbe la colonna oltre lo schermo
    for (const c of st.el.querySelector(".gi-corpo").children) c.style.minWidth = "0";
    const adatta = () => {
      f.style.fontSize = "";
      const base = parseFloat(getComputedStyle(f).fontSize) || 16;
      let fsz = base;
      for (let k = 0; k < 4 && f.scrollWidth > f.clientWidth + 1 && fsz > base * 0.55; k++) {
        fsz = Math.max(base * 0.55, fsz * (f.clientWidth - 4) / f.scrollWidth);
        f.style.fontSize = fsz + "px";
      }
    };
    st.dati.moFormula = new MutationObserver(() => requestAnimationFrame(adatta));
    st.dati.moFormula.observe(f, { childList: true, subtree: true });
    window.addEventListener("resize", () => requestAnimationFrame(adatta));
  }

  window.GI_RICETTE["modelli-ottimi"] = {
    titolo: T("Tre modelli MIP risolti all'ottimo", "Three MIP models solved to optimality"),
    funzioni: VOCI,
    etichettaFunzioni: T("Modello", "Model"),
    parametri: PAR,
    assi: false,
    opzioniBoard: M.OPZ,
    vista: [0, 300, 400, 0],
    legenda: (st) => {
      const C = M.COL(st), k = st.chiave();
      if (k === "localizzazione") return [
        [C.blu, T("sede aperta (\\(x_l = 1\\)) e flussi \\(y_{lc}\\) dell'ottimo", "open site (\\(x_l = 1\\)) and optimal flows \\(y_{lc}\\)"), "pieno"],
        [C.grigio, T("sede chiusa, arco non usato", "closed site, unused arc"), "dashed"],
        [C.verde, T("clienti con la domanda \\(d_c\\)", "customers with demand \\(d_c\\)"), "pieno"],
        [C.rosso, T("\\(\\tilde x_l\\): rilassamento continuo", "\\(\\tilde x_l\\): continuous relaxation"), ""],
      ];
      if (k === "lotti") return [
        [C.grigio, T("domanda \\(d_t\\)", "demand \\(d_t\\)"), "pieno"],
        [C.blu, T("produzione \\(x_t\\) e setup \\(y_t = 1\\) dell'ottimo", "optimal production \\(x_t\\) and setups \\(y_t = 1\\)"), "pieno"],
        [C.target, T("scorta \\(s_t\\) a fine giorno", "end-of-day stock \\(s_t\\)"), ""],
        [C.rosso, T("\\(\\tilde y_t\\): rilassamento continuo", "\\(\\tilde y_t\\): continuous relaxation"), ""],
      ];
      return [
        [C.blu, T("progetti dell'ottimo (\\(x_p = 1\\))", "projects in the optimum (\\(x_p = 1\\))"), "pieno"],
        [C.rosso, T("\\(\\tilde x_p\\): rilassamento continuo", "\\(\\tilde x_p\\): continuous relaxation"), "pieno"],
        [C.testo, T("budget \\(b\\)", "budget \\(b\\)"), "pieno"],
      ];
    },
    monta(board, st) {
      st.dati.an = null;
      preparaPannello(st);
      adattaFormula(st);
      osservaDimensioni(board, st);
    },
    aggiorna(board, st) {
      const A = analisi(st), C = M.COL(st);
      const [W, H] = dim(board);
      M.ridisegna(board, st, [A.firma, M.scuro(), W, H].join("|"), (crea) => {
        board.setBoundingBox([0, H, W, 0], false);
        if (A.k === "localizzazione") disegnaLoc(crea, A, W, H, C);
        else if (A.k === "lotti") disegnaLot(crea, A, W, H, C);
        else disegnaPro(crea, A, W, H, C, st);
      });
    },
    formula: (p, st) => formula(st),
    letture: (p, st) => letture(analisi(st), M.COL(st)),
    domanda: DOMANDE.localizzazione,
  };

  // per le prove automatiche (confronto con Gurobi): solo le funzioni di calcolo
  window.GI_MIP_D = { simplesso, milp, rilassamento, modelloLoc, modelloLot, modelloPro };
})();
