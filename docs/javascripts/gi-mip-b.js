/* Laboratorio di «Modellazione MIP / MIP Modelling»: ricette del capitolo 4 (Euristiche costruttive).
 *
 *   zaino     problema dello zaino 0-1: l'euristica costruttiva per rapporto p_j/w_j
 *             (greedy) passo per passo, l'ottimo esatto (programmazione dinamica) e il
 *             rilassamento continuo (un oggetto frazionario), con LB <= z(MILP) <= z(LP)
 *   tsp       città trascinabili: nearest neighbour passo per passo da una partenza
 *             scelta, facoltativo miglioramento 2-opt, giro ottimo (Held-Karp), gap
 *   bpp-lpt   bin packing (Next Fit, First Fit, Best Fit, First Fit Decreasing) con i
 *             contenitori a colonne e il bound ⌈Σ w_j / C⌉; P||Cmax (list scheduling,
 *             LPT) con il diagramma di Gantt e il bound max(max_j t_j, Σ_j t_j / k)
 *
 * Notazione e regole come nella pagina del capitolo 4 e in python/euristiche.py:
 * zaino p, w, C (pareggi sull'indice più piccolo); bin packing w, C, «primo
 * contenitore aperto in cui ci sta»; makespan t_j, k macchine, carichi L_m;
 * TSP d_ij; gap dell'euristica = |valore − ottimo| / ottimo.
 *
 * Formato delle ricette: commento in testa a interattivi.js; helper comuni in
 * gi-comune.js (window.GI_MIP). Il cursore del passo si chiama «passo» / «step»
 * (non k, che nel makespan è il numero di macchine): la sua chiave è
 * "text{passo}" / "text{step}", cioè il nome TeX senza «\», come vuole inputDi.
 * Le funzioni di calcolo (senza disegno) sono anche in window.GI_MIP_B, per le prove.
 */
(function () {
  "use strict";
  const GI = window.GI, M = window.GI_MIP;
  const T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};

  // ------------------------------------------------------------ utilità comuni
  const PASSO = T("text{passo}", "text{step}");
  const parPasso = (descr) => ({ k: PASSO, nome: "\\" + PASSO, min: 0, max: 20, step: 1, val: 0, colore: "a", cifre: 0, descr });
  const DESCR_PASSO = T("◀ ▶ un passo alla volta, «Esegui» per vederli tutti",
    "◀ ▶ one step at a time, «Run» to watch all of them");
  const vaiAZero = (st) => { const i = M.inputDi(st, PASSO); if (i) i.value = 0; };
  const pct = (x) => GI.num(100 * x, 1) + "\\,\\%";
  const qTxt = (q) => (q.d === 1 ? String(q.n) : `${q.n}/${q.d}`);
  const lista = (A) => A.join(", ");
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  let contatore = 0;
  const nuovoId = () => "i" + (++contatore);
  /** la board ricalcola il disegno quando cambia dimensione (la firma contiene le dimensioni) */
  function osservaDimensioni(board, st) {
    if (st.dati.ro) st.dati.ro.disconnect();
    if (!window.ResizeObserver || !board.containerObj) return;
    // subito, non dopo un ritardo: il disegno si rifà nello stesso fotogramma del cambio di dimensione
    st.dati.ro = new ResizeObserver(() => {
      if (!document.body.contains(st.el) || st.board !== board) return;
      const [w, h] = [board.containerObj.clientWidth, board.containerObj.clientHeight];
      if (w > 0 && h > 0 && st.dati.roDim !== w + "x" + h) { st.dati.roDim = w + "x" + h; st.aggiorna(); }
    });
    st.dati.ro.observe(board.containerObj);
  }

  /** al cambio di voce (algoritmo) il passo torna a 0 e «Esegui» si ferma */
  function nuovaVoce(st) {
    if (st.dati.voce !== st.chiave()) {
      if (st.dati.voce !== undefined) { vaiAZero(st); M.ferma(st); }
      st.dati.voce = st.chiave();
    }
  }
  /** dimensioni del disegno in pixel; se il contenitore è cambiato (la pagina dell'app gli dà
   *  l'altezza dopo il primo disegno) la board si adegua prima di disegnare */
  const dim = (board) => {
    const el = board.containerObj, cw = el ? el.clientWidth : 0, ch = el ? el.clientHeight : 0;
    if (cw > 0 && ch > 0 && (Math.abs(cw - board.canvasWidth) > 1 || Math.abs(ch - board.canvasHeight) > 1)) board.resizeContainer(cw, ch, true, true);
    return [Math.round(board.canvasWidth || 600), Math.round(board.canvasHeight || 400)];
  };
  /** stato iniziale da un link: #passo=3 (o #step=3) e #voce=chiave (una voce di «funzioni») */
  function daIndirizzo(st) {
    if (st.dati.indirizzo) return;
    st.dati.indirizzo = true;
    const h = decodeURIComponent(location.hash || "");
    const v = /voce=([\w-]+)/.exec(h), k = /(?:passo|step)=(\d+)/.exec(h);
    if (!v && !k) return;
    setTimeout(() => {
      if (v && v[1] !== st.chiave()) {
        const R = window.GI_RICETTE[st.el.dataset.grafico], i = Object.keys(R.funzioni || {}).indexOf(v[1]);
        const b = st.el.querySelectorAll(".gi-chip")[i];
        if (b) b.click();
      }
      if (k) setTimeout(() => st.imposta(PASSO, +k[1]), 50);
    }, 30);
  }

  // =================================================================
  // 1. ZAINO 0-1
  // =================================================================
  const ZAINO_ES = {
    corso: { p: [10, 7, 6, 4], w: [5, 4, 3, 3], C: 9 },
    otto: { p: [3, 14, 13, 4, 5, 8, 11, 6], w: [7, 9, 9, 6, 3, 3, 7, 2], C: 23 },
  };
  const copiaZaino = (I) => ({ p: I.p.slice(), w: I.w.slice(), C: I.C, id: nuovoId() });
  function zainoCasuale() {
    const n = M.casuale(6, 10), w = [], p = [];
    for (let j = 0; j < n; j++) { w.push(M.casuale(2, 9)); p.push(M.casuale(3, 20)); }
    const C = Math.max(Math.max(...w), Math.floor(w.reduce((a, b) => a + b, 0) / 2));
    return { p, w, C, id: nuovoId() };
  }
  /** ordine per p_j/w_j decrescente, pareggi sull'indice più piccolo (confronto esatto) */
  const ordineRapporto = (p, w) => p.map((_, j) => j).sort((i, j) => (p[j] * w[i] - p[i] * w[j]) || (i - j));
  function zainoOttimo(p, w, C) {
    const n = p.length, V = [];
    for (let j = 0; j <= n; j++) V.push(new Array(C + 1).fill(0));
    for (let j = 1; j <= n; j++) for (let c = 0; c <= C; c++) {
      V[j][c] = V[j - 1][c];
      if (w[j - 1] <= c && V[j - 1][c - w[j - 1]] + p[j - 1] > V[j][c]) V[j][c] = V[j - 1][c - w[j - 1]] + p[j - 1];
    }
    const S = [];
    let c = C;
    for (let j = n; j >= 1; j--) if (V[j][c] !== V[j - 1][c]) { S.push(j - 1); c -= w[j - 1]; }
    return { val: V[n][C], S: S.reverse() };
  }
  function zainoCalcola(I) {
    const { p, w, C } = I, n = p.length, ord = ordineRapporto(p, w);
    const tr = [{ cur: null, presi: [], scart: [], res: C, val: 0 }];
    let res = C, val = 0;
    const presi = [], scart = [];
    for (const j of ord) {
      const prima = res, ok = w[j] <= res;
      if (ok) { res -= w[j]; val += p[j]; presi.push(j); } else scart.push(j);
      tr.push({ cur: j, ok, prima, presi: presi.slice(), scart: scart.slice(), res, val });
    }
    tr.push({ cur: null, fine: true, presi: presi.slice(), scart: scart.slice(), res, val });
    // rilassamento continuo: stesso ordine, l'oggetto che non entra entra per la frazione che ci sta
    let r = C, z = M.Q(0), fraz = null;
    const pieni = [];
    for (const j of ord) {
      if (w[j] <= r) { r -= w[j]; z = M.Qadd(z, M.Q(p[j])); pieni.push(j); }
      else { if (r > 0) { fraz = { j, q: M.Q(r, w[j]) }; z = M.Qadd(z, M.Q(p[j] * r, w[j])); } break; }
    }
    const opt = zainoOttimo(p, w, C);
    return { n, ord, tr, opt, lp: { z, pieni, fraz }, LB: val, pesoPresi: C - res };
  }

  window.GI_RICETTE["zaino"] = {
    titolo: T("Zaino: greedy contro ottimo", "Knapsack: greedy versus optimum"),
    parametri: [parPasso(DESCR_PASSO)],
    assi: false,
    opzioniBoard: M.OPZ,
    vista: [-3, 1, 12, -12],
    legenda: (st) => {
      const C = M.COL(st);
      return [
        [C.a, T("presi dall'euristica", "taken by the heuristic"), "pieno"],
        [C.blu, T("ottimo (programmazione dinamica)", "optimum (dynamic programming)"), "pieno"],
        [C.rosso, T("rilassamento continuo", "continuous relaxation"), "pieno"],
        [C.grigio, T("da esaminare / scartati", "to examine / discarded"), "pieno"],
      ];
    },
    monta(board, st) {
      const D = st.dati;
      if (!D.ist) D.ist = copiaZaino(ZAINO_ES.corso);
      const usa = (I) => { D.ist = I; D.calc = null; vaiAZero(st); st.aggiorna(); };
      M.comandi(st, [
        [T("Esempio", "Example"), T("l'esempio del capitolo: p = (10, 7, 6, 4), w = (5, 4, 3, 3), C = 9", "the chapter example: p = (10, 7, 6, 4), w = (5, 4, 3, 3), C = 9"), () => usa(copiaZaino(ZAINO_ES.corso))],
        [T("8 oggetti", "8 items"), T("un'istanza con otto oggetti", "an instance with eight items"), () => usa(copiaZaino(ZAINO_ES.otto))],
        [T("Casuale", "Random"), T("da 6 a 10 oggetti casuali", "6 to 10 random items"), () => usa(zainoCasuale())],
      ], { k: PASSO });
      osservaDimensioni(board, st);
      daIndirizzo(st);
    },
    aggiorna(board, st) {
      const D = st.dati, I = D.ist;
      if (!D.calc) D.calc = zainoCalcola(I);
      const R = D.calc, K = R.tr.length - 1, k = M.passoK(st, K, PASSO), E = R.tr[k], C = M.COL(st);
      const [W, H] = dim(board), stretto = W < 620, n = R.n;
      M.ridisegna(board, st, [I.id, k, M.scuro(), W, H].join("|"), (crea) => {
        const sx = stretto ? 62 : 128, dx = stretto ? 106 : 210;          // margini in pixel: etichette e valori
        const u = Math.max(3, (W - sx - dx - 12) / I.C);                  // pixel per unità di peso
        const righe = 4 + n, x0 = -(sx + 6) / u;
        board.setBoundingBox([x0, 0.75, x0 + W / u, 0.75 - (righe + 0.35)], false);
        const rh = H / (righe + 0.35), fs = clamp(rh * 0.42, 10, 16), hb = 0.31;
        const etichetta = (y, s, col, bold) => M.scritta(crea, -8 / u, y, s, { anchorX: "right", fontSize: fs, strokeColor: col || C.testo, cssStyle: bold ? "font-weight:600" : "" });
        const valore = (y, s, col) => M.scritta(crea, I.C + 10 / u, y, s, { anchorX: "left", fontSize: fs, strokeColor: col || C.testo });
        const pezzo = (x, w, y, col, op, testo, attr) => {
          M.rett(crea, x, y - hb, x + w, y + hb, Object.assign({ strokeColor: col, fillColor: col, fillOpacity: op, strokeWidth: 1.5 }, attr || {}));
          if (testo && w * u > fs * 0.55 * testo.length + 8) M.scritta(crea, x + w / 2, y, testo, { fontSize: fs * 0.92, strokeColor: C.testo });
        };
        const capienza = (y) => M.rett(crea, 0, y - hb - 0.05, I.C, y + hb + 0.05, { strokeColor: C.muted, strokeWidth: 1.5 });
        // tre zaini: euristica, ottimo, rilassamento
        capienza(0);
        let x = 0;
        for (const j of E.presi) { pezzo(x, I.w[j], 0, C.a, j === E.cur ? 0.8 : 0.5, String(j + 1)); x += I.w[j]; }
        etichetta(0, T("euristica", "heuristic"), C.a, true);
        valore(0, E.fine ? `LB = ${E.val}` : stretto ? String(E.val) : T(`valore ${E.val}`, `value ${E.val}`), C.a);
        capienza(-1);
        x = 0;
        for (const j of R.ord.filter((j) => R.opt.S.includes(j))) { pezzo(x, I.w[j], -1, C.blu, 0.45, String(j + 1)); x += I.w[j]; }
        etichetta(-1, T("ottimo", "optimum"), C.blu, true);
        valore(-1, `z(MILP) = ${R.opt.val}`, C.blu);
        capienza(-2);
        x = 0;
        for (const j of R.lp.pieni) { pezzo(x, I.w[j], -2, C.rosso, 0.4, String(j + 1)); x += I.w[j]; }
        if (R.lp.fraz) pezzo(x, I.C - x, -2, C.rosso, 0.14, `${R.lp.fraz.j + 1}·${qTxt(R.lp.fraz.q)}`, { dash: 2 });
        etichetta(-2, stretto ? T("rilass.", "relax.") : T("rilassamento", "relaxation"), C.rosso, true);
        valore(-2, `z(LP) = ${qTxt(R.lp.z)}`, C.rosso);
        M.scritta(crea, 0, -3, T("oggetti in ordine di p/w decrescente", "items by decreasing p/w"),
          { anchorX: "left", fontSize: fs * 0.92, strokeColor: C.muted, cssStyle: "font-style:italic" });
        // gli oggetti, uno per riga, nell'ordine in cui l'euristica li guarda
        R.ord.forEach((j, i) => {
          const y = -4 - i, presi = E.presi.includes(j), scart = E.scart.includes(j), cur = j === E.cur;
          if (cur) M.rett(crea, x0, y - 0.48, x0 + W / u, y + 0.48, { strokeColor: "none", fillColor: C.a, fillOpacity: 0.1 });
          if (presi) pezzo(0, I.w[j], y, C.a, cur ? 0.8 : 0.5);
          else if (scart) pezzo(0, I.w[j], y, C.grigio, 0.12, null, { dash: 2, strokeWidth: cur ? 2.5 : 1.5, strokeColor: cur ? C.a : C.grigio });
          else pezzo(0, I.w[j], y, C.grigio, 0.35);
          if (I.w[j] * u > fs * 2.2 + 8) M.scritta(crea, I.w[j] / 2, y, `w=${I.w[j]}`, { fontSize: fs * 0.85, strokeColor: C.testo });
          etichetta(y, (stretto ? "" : T("oggetto ", "item ")) + (j + 1), cur ? C.a : C.muted, cur);
          valore(y, stretto ? `p=${I.p[j]}` : `p = ${I.p[j]}  ·  p/w = ${qTxt(M.Q(I.p[j], I.w[j]))}`, cur ? C.a : C.muted);
        });
      });
    },
    formula(p, st) {
      const D = st.dati, R = D.calc;
      if (!R) return "";
      const K = R.tr.length - 1, k = M.passoK(st, K, PASSO), E = R.tr[k];
      if (E.fine) return `\\lb = ${E.val} \\;\\le\\; \\zmilp = ${R.opt.val} \\;\\le\\; \\zlp = ${M.Qtex(R.lp.z)}`;
      return T(`\\text{valore} = ${E.val},\\quad \\text{capacità residua} = ${E.res}`,
        `\\text{value} = ${E.val},\\quad \\text{residual capacity} = ${E.res}`);
    },
    letture(p, st) {
      const D = st.dati, R = D.calc, I = D.ist;
      if (!R) return "";
      const K = R.tr.length - 1, k = M.passoK(st, K, PASSO), E = R.tr[k], C = M.COL(st);
      let nota;
      if (k === 0) {
        nota = T(`Ordine per \\(p_j/w_j\\) decrescente: ${lista(R.ord.map((j) => j + 1))} (pareggi sull'indice più piccolo). Capacità \\(C = ${I.C}\\).`,
          `Order by decreasing \\(p_j/w_j\\): ${lista(R.ord.map((j) => j + 1))} (ties on the smallest index). Capacity \\(C = ${I.C}\\).`);
      } else if (!E.fine) {
        const j = E.cur, J = j + 1, rap = `\\(p_{${J}}/w_{${J}} = ${M.Qtex(M.Q(I.p[j], I.w[j]))}\\)`;
        nota = E.ok
          ? T(`Oggetto ${J}: ${rap}, \\(w_{${J}} = ${I.w[j]} \\le ${E.prima}\\) (capacità residua): ${M.tinta(C.a, "si prende")}, residuo \\(${E.prima} - ${I.w[j]} = ${E.res}\\).`,
            `Item ${J}: ${rap}, \\(w_{${J}} = ${I.w[j]} \\le ${E.prima}\\) (residual capacity): ${M.tinta(C.a, "taken")}, residual \\(${E.prima} - ${I.w[j]} = ${E.res}\\).`)
          : T(`Oggetto ${J}: ${rap}, \\(w_{${J}} = ${I.w[j]} > ${E.prima}\\): ${M.tinta(C.muted, "si scarta")}.`,
            `Item ${J}: ${rap}, \\(w_{${J}} = ${I.w[j]} > ${E.prima}\\): ${M.tinta(C.muted, "discarded")}.`);
      } else {
        nota = T(`Fine: presi gli oggetti ${lista(E.presi.map((j) => j + 1).sort((a, b) => a - b))}, peso ${R.pesoPresi}, valore ${E.val}. Il problema è di massimo: il valore dell'euristica è un ${M.tinta(C.a, "lower bound")}.`,
          `End: items ${lista(E.presi.map((j) => j + 1).sort((a, b) => a - b))} taken, weight ${R.pesoPresi}, value ${E.val}. The problem is a maximum: the heuristic value is a ${M.tinta(C.a, "lower bound")}.`);
        if (R.lp.fraz) {
          const f = R.lp.fraz, base = R.lp.pieni.reduce((s, j) => s + I.p[j], 0);
          nota += T(` Nel rilassamento continuo l'oggetto ${f.j + 1} entra per \\(${M.Qtex(f.q)}\\): \\(\\zlp = ${base} + ${I.p[f.j]} \\cdot ${M.Qtex(f.q)} = ${M.Qtex(R.lp.z)}\\).`,
            ` In the continuous relaxation item ${f.j + 1} enters with \\(${M.Qtex(f.q)}\\): \\(\\zlp = ${base} + ${I.p[f.j]} \\cdot ${M.Qtex(f.q)} = ${M.Qtex(R.lp.z)}\\).`);
        }
      }
      const gap = (R.opt.val - R.LB) / R.opt.val;
      const righe = [
        [E.fine ? T("\\(\\lb\\) (euristica)", "\\(\\lb\\) (heuristic)") : T("euristica, finora", "heuristic, so far"), `\\(${E.val}\\)`],
        [T("\\(\\zmilp\\) (ottimo)", "\\(\\zmilp\\) (optimum)"), `\\(${R.opt.val}\\)`],
        [T("\\(\\zlp\\) (rilassamento)", "\\(\\zlp\\) (relaxation)"), `\\(${M.Qtex(R.lp.z)}\\)`],
        [T("gap dell'euristica", "heuristic gap"), E.fine ? `\\(${pct(gap)}\\)` : "—"],
      ];
      return nota + M.tab([T("bound", "bound"), T("valore", "value")], righe, E.fine ? 0 : -1, C.a);
    },
    domanda: T("Nell'esempio del corso, quale oggetto lascia un residuo che non serve più a niente? Prima dell'ultimo passo prevedi \\(\\zlp\\) (l'oggetto frazionario è il primo che non entra) e controlla che \\(\\lb \\le \\zmilp \\le \\zlp\\). Con «Nuova istanza» cerca un caso in cui il gap supera il 20 %.",
      "In the course example, which item leaves a residual capacity that is no longer useful? Before the last step predict \\(\\zlp\\) (the fractional item is the first one that does not fit) and check that \\(\\lb \\le \\zmilp \\le \\zlp\\). With «New instance» look for a case where the gap exceeds 20 %."),
  };

  // =================================================================
  // 2. TSP: NEAREST NEIGHBOUR (+ 2-OPT) CONTRO IL GIRO OTTIMO
  // =================================================================
  const TSP_ES = [[4, 10], [0, 1], [10, 9], [9, 5], [3, 0], [5, 5], [0, 9]];
  const LATO = 10;
  const dist = (P, i, j) => Math.hypot(P[i][0] - P[j][0], P[i][1] - P[j][1]);
  const lunghezza = (P, t) => t.reduce((s, c, i) => s + dist(P, c, t[(i + 1) % t.length]), 0);
  function puntoLibero(P) {
    for (let tent = 0; tent < 400; tent++) {
      const q = [M.casuale(0, LATO), M.casuale(0, LATO)];
      const minimo = tent < 300 ? 2.5 : 1.2;
      if (P.every((r) => Math.hypot(q[0] - r[0], q[1] - r[1]) >= minimo)) return q;
    }
    return [M.casuale(0, LATO), M.casuale(0, LATO)];
  }
  function tspCasuale(n) { const P = []; while (P.length < n) P.push(puntoLibero(P)); return P; }
  function vicinoPiuVicino(P, s) {
    const n = P.length, path = [s], passi = [{ fase: "inizio", path: [s], len: 0 }];
    let len = 0;
    while (path.length < n) {
      const c = path[path.length - 1];
      const cand = [];
      for (let j = 0; j < n; j++) if (!path.includes(j)) cand.push(j);
      let a = cand[0];
      for (const j of cand) if (dist(P, c, j) < dist(P, c, a) - 1e-12) a = j;
      len += dist(P, c, a);
      path.push(a);
      passi.push({ fase: "nn", path: path.slice(), da: c, a, cand, len });
    }
    const ult = path[n - 1];
    len += dist(P, ult, s);
    passi.push({ fase: "ritorno", path: path.slice(), chiuso: true, da: ult, a: s, len });
    return { tour: path, len, passi };
  }
  function dueOpt(P, tour0, passi) {
    const n = P.length;
    let t = tour0.slice(), len = lunghezza(P, t);
    for (let giri = 0; giri < 40; giri++) {
      let best = null;
      for (let i = 0; i < n - 1; i++) for (let j = i + 2; j < n; j++) {
        if (i === 0 && j === n - 1) continue;
        const a = t[i], b = t[i + 1], c = t[j], d = t[(j + 1) % n];
        const delta = dist(P, a, c) + dist(P, b, d) - dist(P, a, b) - dist(P, c, d);
        if (delta < -1e-9 && (!best || delta < best.delta - 1e-12)) best = { i, j, a, b, c, d, delta };
      }
      if (!best) break;
      t = t.slice(0, best.i + 1).concat(t.slice(best.i + 1, best.j + 1).reverse(), t.slice(best.j + 1));
      len = lunghezza(P, t);
      passi.push({ fase: "2opt", tour: t.slice(), chiuso: true, rimossi: [[best.a, best.b], [best.c, best.d]], aggiunti: [[best.a, best.c], [best.b, best.d]], delta: best.delta, len });
    }
    passi.push({ fase: "fine2opt", tour: t.slice(), chiuso: true, len });
    return { tour: t, len };
  }
  /** Held-Karp: giro ottimo (n <= 10), partendo dalla città 0 */
  function heldKarp(P) {
    const n = P.length, N = 1 << n, INF = Infinity;
    const dp = Array.from({ length: N }, () => new Float64Array(n).fill(INF));
    const pr = Array.from({ length: N }, () => new Int8Array(n).fill(-1));
    dp[1][0] = 0;
    for (let S = 1; S < N; S += 2) for (let j = 0; j < n; j++) {
      if (!(S & (1 << j)) || dp[S][j] === INF) continue;
      for (let q = 1; q < n; q++) {
        if (S & (1 << q)) continue;
        const T2 = S | (1 << q), v = dp[S][j] + dist(P, j, q);
        if (v < dp[T2][q] - 1e-12) { dp[T2][q] = v; pr[T2][q] = j; }
      }
    }
    let best = INF, last = 0;
    for (let j = 1; j < n; j++) { const v = dp[N - 1][j] + dist(P, j, 0); if (v < best - 1e-12) { best = v; last = j; } }
    const tour = [];
    let S = N - 1, j = last;
    while (j >= 0 && j !== 0) { tour.push(j); const pj = pr[S][j]; S ^= 1 << j; j = pj; }
    tour.push(0);
    return { tour: tour.reverse(), len: n > 1 ? best : 0 };
  }
  function tspCalcola(P, s, con2opt) {
    const nn = vicinoPiuVicino(P, s), passi = nn.passi.slice();
    const opt2 = con2opt ? dueOpt(P, nn.tour, passi) : null;
    const ott = heldKarp(P);
    const tutte = P.map((_, q) => vicinoPiuVicino(P, q).len);
    return { nn, opt2, ott, passi, tutte };
  }

  /** le città trascinabili della board corrente: una per punto di D.P */
  function cittaSullaBoard(board, st) {
    const D = st.dati, C = M.COL(st);
    if (D.ptsBoard === board && D.pts.length === D.P.length) {
      D.pts.forEach((pt, i) => { if (pt.X() !== D.P[i][0] || pt.Y() !== D.P[i][1]) pt.moveTo(D.P[i]); });
      return;
    }
    if (D.ptsBoard === board) for (const o of D.pts) { try { board.removeObject(o); } catch (e) { /* già tolto */ } }
    D.ptsBoard = board;
    D.pts = D.P.map((q, i) => {
      const pt = board.create("point", q.slice(), {
        name: String(i + 1), size: 7, snapToGrid: true, snapSizeX: 1, snapSizeY: 1, showInfobox: false,
        fillColor: C.grigio, strokeColor: C.muted, strokeWidth: 2, highlightFillColor: C.a, highlightStrokeColor: C.a,
        label: { offset: [10, 10], fontSize: 15, cssStyle: "font-weight:700" },
      });
      pt.on("drag", () => {
        const X = clamp(Math.round(pt.X()), 0, LATO), Y = clamp(Math.round(pt.Y()), 0, LATO);
        if (X !== pt.X() || Y !== pt.Y()) pt.moveTo([X, Y]);
        if (D.P[i][0] !== X || D.P[i][1] !== Y) { D.P[i] = [X, Y]; st.aggiorna(); }
      });
      return pt;
    });
  }

  const TSP_FUNZ = {
    nn: { etichetta: "<span title=\"nearest neighbour\">NN</span>" },
    nn2: { etichetta: "<span title=\"nearest neighbour + 2-opt\">NN + 2-opt</span>" },
  };

  window.GI_RICETTE["tsp"] = {
    titolo: T("TSP: nearest neighbour contro giro ottimo", "TSP: nearest neighbour versus optimal tour"),
    funzioni: TSP_FUNZ,
    etichettaFunzioni: T("Euristica: nearest neighbour (NN), da sola o seguita dal 2-opt", "Heuristic: nearest neighbour (NN), alone or followed by 2-opt"),
    parametri: [
      { k: "s", min: 1, max: 7, step: 1, val: 1, colore: "c", cifre: 0, descr: T("città di partenza", "starting city") },
      parPasso(DESCR_PASSO),
    ],
    assi: false,
    stessaScala: true,
    opzioniBoard: M.OPZ,
    vista: [-1, LATO + 1, LATO + 1, -1],
    legenda: (st) => {
      const C = M.COL(st), due = st.chiave() === "nn2";
      return [
        [C.a, T("giro dell'euristica", "heuristic tour"), ""],
        [C.grigio, due ? T("distanze esaminate, archi tolti", "distances examined, edges removed") : T("distanze esaminate", "distances examined"), "dashed"],
        ...(due ? [[C.viola, T("archi della mossa 2-opt", "edges of the 2-opt move"), ""]] : []),
        [C.blu, T("giro ottimo", "optimal tour"), "pieno"],
      ];
    },
    monta(board, st) {
      const D = st.dati;
      nuovaVoce(st);
      if (!D.P) D.P = TSP_ES.map((q) => q.slice());
      D.ptsBoard = null;
      D.calc = null;
      D.dim = null;
      M.comandi(st, [
        [T("Esempio", "Example"), T("sette città di esempio", "seven example cities"), () => {
          D.P = TSP_ES.map((q) => q.slice()); D.calc = null; vaiAZero(st);
          const s = M.inputDi(st, "s"); if (s) s.value = 1;
          st.aggiorna();
        }],
        [T("Casuale", "Random"), T("le stesse città in posizioni casuali", "the same cities at random positions"), () => {
          D.P = tspCasuale(D.P.length); D.calc = null; vaiAZero(st); st.aggiorna();
        }],
        [T("+ città", "+ city"), T("aggiungi una città (al più 9)", "add a city (at most 9)"), () => {
          if (D.P.length < 9) { D.P.push(puntoLibero(D.P)); D.calc = null; vaiAZero(st); st.aggiorna(); }
        }],
        [T("− città", "− city"), T("togli l'ultima città (almeno 5)", "remove the last city (at least 5)"), () => {
          if (D.P.length > 5) { D.P = D.P.slice(0, -1); D.calc = null; vaiAZero(st); st.aggiorna(); }
        }],
      ], { k: PASSO });
      osservaDimensioni(board, st);
      daIndirizzo(st);
    },
    aggiorna(board, st) {
      const D = st.dati, C = M.COL(st);
      const n = D.P.length;
      M.intervallo(st, "s", 1, n);
      const s = M.intero(st, "s") - 1, due = st.chiave() === "nn2";
      const firmaDati = [D.P.map((q) => q.join(",")).join(";"), s, due].join("|");
      if (!D.calc || D.calcFirma !== firmaDati) { D.calc = tspCalcola(D.P, s, due); D.calcFirma = firmaDati; }
      cittaSullaBoard(board, st);
      const [W, H] = dim(board);
      if (D.dim !== W + "x" + H) { D.dim = W + "x" + H; M.adatta(board, -0.8, LATO + 0.9, LATO + 0.8, -0.8); }
      const R = D.calc, K = R.passi.length - 1, k = M.passoK(st, K, PASSO), E = R.passi[k], P = D.P;
      // colori delle città: partenza, già visitate, da visitare
      const visitate = new Set(E.path || E.tour || []);
      D.pts.forEach((pt, i) => {
        const att = i === s ? { fillColor: C.a, strokeColor: C.a, face: "[]", size: 8 }
          : visitate.has(i) ? { fillColor: C.a, strokeColor: C.a, face: "o", size: 6 }
            : { fillColor: M.scuro() ? "#1b2636" : "#ffffff", strokeColor: C.muted, face: "o", size: 6 };
        pt.setAttribute(att);
      });
      M.ridisegna(board, st, [firmaDati, k, M.scuro(), W, H].join("|"), (crea) => {
        const seg = (i, j, attr) => M.linea(crea, P[i][0], P[i][1], P[j][0], P[j][1], attr);
        // il giro ottimo, sotto, come un evidenziatore
        const o = R.ott.tour;
        o.forEach((c, i) => seg(c, o[(i + 1) % o.length], { strokeColor: C.blu, strokeWidth: 11, strokeOpacity: M.scuro() ? 0.38 : 0.22, lineCap: "round" }));
        if (E.fase === "inizio" || E.fase === "nn" || E.fase === "ritorno") {
          if (E.fase === "nn") for (const j of E.cand) if (j !== E.a) seg(E.da, j, { strokeColor: C.grigio, strokeWidth: 1.6, dash: 2 });
          const t = E.path;
          for (let i = 0; i + 1 < t.length; i++) seg(t[i], t[i + 1], { strokeColor: C.a, strokeWidth: 3.5 });
          if (E.chiuso) seg(t[t.length - 1], t[0], { strokeColor: C.a, strokeWidth: 3.5 });
          if (E.fase !== "inizio") seg(E.da, E.a, { strokeColor: C.a, strokeWidth: 6.5 });
        } else {
          const t = E.tour;
          t.forEach((c, i) => seg(c, t[(i + 1) % t.length], { strokeColor: C.a, strokeWidth: 3.5 }));
          if (E.fase === "2opt") {
            for (const [a, b] of E.rimossi) seg(a, b, { strokeColor: C.grigio, strokeWidth: 2.5, dash: 2 });
            for (const [a, b] of E.aggiunti) seg(a, b, { strokeColor: C.viola, strokeWidth: 6 });
          }
        }
      });
    },
    formula(p, st) {
      const D = st.dati, R = D.calc;
      if (!R) return "";
      const K = R.passi.length - 1, k = M.passoK(st, K, PASSO), E = R.passi[k], nf = (x) => GI.num(x, 2);
      if (E.fase === "inizio") return T(`\\text{partenza: città } ${E.path[0] + 1}`, `\\text{start: city } ${E.path[0] + 1}`);
      const stretto = st.board && st.board.canvasWidth < 620;
      if (E.fase === "nn" && stretto) return `d_{${E.da + 1}${E.a + 1}} = ${nf(dist(D.P, E.da, E.a))} = \\min_j d_{${E.da + 1}j}`;
      if (E.fase === "nn") {
        return T(`\\min_{j\\ \\text{non visitata}} d_{${E.da + 1}j} = d_{${E.da + 1}${E.a + 1}} = ${nf(dist(D.P, E.da, E.a))} \\qquad \\text{lunghezza parziale} = ${nf(E.len)}`,
          `\\min_{j\\ \\text{unvisited}} d_{${E.da + 1}j} = d_{${E.da + 1}${E.a + 1}} = ${nf(dist(D.P, E.da, E.a))} \\qquad \\text{partial length} = ${nf(E.len)}`);
      }
      const gap = (E.len - R.ott.len) / R.ott.len;
      return `\\ub = ${nf(E.len)} \\;\\ge\\; \\zmilp = ${nf(R.ott.len)}` + (stretto ? "" : ` \\qquad \\text{gap} = ${pct(gap)}`);
    },
    letture(p, st) {
      const D = st.dati, R = D.calc;
      if (!R) return "";
      const K = R.passi.length - 1, k = M.passoK(st, K, PASSO), E = R.passi[k], C = M.COL(st), nf = (x) => GI.num(x, 2);
      const s = R.nn.tour[0] + 1, giro = (t) => t.concat([t[0]]).map((c) => c + 1).join(" → ");
      let nota;
      if (E.fase === "inizio") nota = T(`Si parte dalla città ${s}: a ogni passo si va alla più vicina fra quelle non ancora visitate.`, `Start from city ${s}: at each step go to the nearest city not yet visited.`);
      else if (E.fase === "nn") {
        const elenco = E.cand.map((j) => { const t = `${j + 1}: \\(${nf(dist(D.P, E.da, j))}\\)`; return j === E.a ? M.tinta(C.a, t) : t; }).join("; ");
        nota = T(`Dalla città ${E.da + 1}, distanze dalle non visitate: ${elenco}. La minima porta alla città ${E.a + 1}.`,
          `From city ${E.da + 1}, distances to the unvisited ones: ${elenco}. The smallest leads to city ${E.a + 1}.`);
      } else if (E.fase === "ritorno") {
        nota = T(`Visitate tutte le città: si torna da ${E.da + 1} alla partenza ${s} (\\(${nf(dist(D.P, E.da, E.a))}\\)). Giro ${giro(E.path)}, lungo \\(${nf(E.len)}\\): un ${M.tinta(C.a, "upper bound")}.`,
          `All cities visited: go back from ${E.da + 1} to the start ${s} (\\(${nf(dist(D.P, E.da, E.a))}\\)). Tour ${giro(E.path)}, length \\(${nf(E.len)}\\): an ${M.tinta(C.a, "upper bound")}.`);
      } else if (E.fase === "2opt") {
        const ar = ([a, b]) => `(${a + 1}, ${b + 1})`;
        nota = T(`Mossa 2-opt: si tolgono gli archi ${E.rimossi.map(ar).join(" e ")}, si mettono ${M.tinta(C.viola, E.aggiunti.map(ar).join(" e "))}; il giro si accorcia di \\(${nf(-E.delta)}\\).`,
          `2-opt move: remove edges ${E.rimossi.map(ar).join(" and ")}, add ${M.tinta(C.viola, E.aggiunti.map(ar).join(" and "))}; the tour gets shorter by \\(${nf(-E.delta)}\\).`);
      } else {
        nota = T(`Nessuna mossa 2-opt accorcia il giro ${giro(E.tour)}: è un ottimo locale, lungo \\(${nf(E.len)}\\).`,
          `No 2-opt move shortens the tour ${giro(E.tour)}: it is a local optimum, of length \\(${nf(E.len)}\\).`);
      }
      const nnFatto = k >= R.nn.passi.length - 1, fine = k === K;
      const righe = [[T(`nearest neighbour da ${s}`, `nearest neighbour from ${s}`), nnFatto ? `\\(${nf(R.nn.len)}\\)` : "—", nnFatto ? `\\(${pct((R.nn.len - R.ott.len) / R.ott.len)}\\)` : "—"]];
      if (R.opt2) righe.push([T("dopo 2-opt", "after 2-opt"), fine ? `\\(${nf(R.opt2.len)}\\)` : "—", fine ? `\\(${pct((R.opt2.len - R.ott.len) / R.ott.len)}\\)` : "—"]);
      righe.push([T("giro ottimo \\(\\zmilp\\)", "optimal tour \\(\\zmilp\\)"), `\\(${nf(R.ott.len)}\\)`, "\\(0\\)"]);
      const mi = Math.min(...R.tutte), ma = Math.max(...R.tutte), da = R.tutte.indexOf(mi) + 1;
      const multi = T(`Da tutte le ${R.tutte.length} partenze il nearest neighbour va da \\(${nf(mi)}\\) (città ${da}) a \\(${nf(ma)}\\).`,
        `Over all ${R.tutte.length} starting cities nearest neighbour ranges from \\(${nf(mi)}\\) (city ${da}) to \\(${nf(ma)}\\).`);
      return nota + M.tab(["", T("lunghezza", "length"), "gap"], righe, -1, C.a) + `<div style="margin-top:.3em">${multi}</div>`;
    },
    domanda: T("Cambia la città di partenza \\(s\\): quali partenze trovano il giro ottimo? Poi trascina una città in modo che il nearest neighbour da \\(s = 1\\) sbagli di più del 30 %: di solito è l'ultimo arco, il ritorno, a costare caro. Il 2-opt chiude sempre il gap?",
      "Change the starting city \\(s\\): which starts find the optimal tour? Then drag a city so that nearest neighbour from \\(s = 1\\) is more than 30 % off: usually it is the last edge, the way back, that costs a lot. Does 2-opt always close the gap?"),
  };

  // =================================================================
  // 3. BIN PACKING E P||Cmax
  // =================================================================
  const BPP_ES = [{ w: [4, 4, 5, 3, 2, 3], C: 7 }, { w: [3, 3, 2, 2, 2, 2], C: 7 }];
  const CMAX_ES = [{ t: [5, 5, 4, 4, 3, 3, 3], k: 3 }, { t: [3, 4, 5, 6], k: 2 }];
  const BPP_FUNZ = {
    nf: { etichetta: "Next Fit", tipo: "bpp" },
    ff: { etichetta: "First Fit", tipo: "bpp" },
    bf: { etichetta: "Best Fit", tipo: "bpp" },
    ffd: { etichetta: "<span title=\"First Fit Decreasing\">FFD</span>", nome: "First Fit Decreasing", tipo: "bpp" },
    ls: { etichetta: T("List scheduling", "List scheduling"), tipo: "cmax" },
    lpt: { etichetta: "LPT", tipo: "cmax" },
  };
  const decrescente = (v) => v.map((_, j) => j).sort((i, j) => (v[j] - v[i]) || (i - j));
  const somma = (v) => v.reduce((a, b) => a + b, 0);

  function bppTraccia(w, C, regola) {
    const n = w.length, ord = regola === "ffd" ? decrescente(w) : w.map((_, j) => j);
    const bins = [], tr = [{ bins: [], cur: null, ord, fatti: 0 }];
    ord.forEach((j, i) => {
      const res = bins.map((b) => C - somma(b.map((q) => w[q])));
      let b = -1, scartati = [], cand = [];
      if (regola === "nf") {
        const u = bins.length - 1;
        if (u >= 0 && w[j] <= res[u]) b = u; else if (u >= 0) scartati = [u];
      } else if (regola === "bf") {
        cand = res.map((r, q) => q).filter((q) => w[j] <= res[q]);
        for (const q of cand) if (b < 0 || res[q] - w[j] < res[b] - w[j]) b = q;
      } else {
        for (let q = 0; q < bins.length; q++) { if (w[j] <= res[q]) { b = q; break; } scartati.push(q); }
      }
      const nuovo = b < 0;
      if (nuovo) { bins.push([]); b = bins.length - 1; }
      bins[b].push(j);
      tr.push({ bins: bins.map((x) => x.slice()), cur: j, b, nuovo, scartati, cand, res, ord, fatti: i + 1 });
    });
    tr[tr.length - 1].fine = true;
    return tr;
  }
  /** minimo numero di contenitori, per enumerazione (n <= 12) */
  function bppOttimo(w, C) {
    const ord = decrescente(w), n = w.length, LB = Math.ceil(somma(w) / C), res = [];
    let best = n;
    const dfs = (i) => {
      if (best === LB || res.length >= best) return;
      if (i === n) { best = res.length; return; }
      const x = w[ord[i]], visti = new Set();
      for (let b = 0; b < res.length; b++) {
        if (res[b] >= x && !visti.has(res[b])) { visti.add(res[b]); res[b] -= x; dfs(i + 1); res[b] += x; }
      }
      if (res.length + 1 < best) { res.push(C - x); dfs(i + 1); res.pop(); }
    };
    dfs(0);
    return best;
  }
  function cmaxTraccia(t, k, regola) {
    const ord = regola === "lpt" ? decrescente(t) : t.map((_, j) => j);
    const L = new Array(k).fill(0), ass = Array.from({ length: k }, () => []);
    const tr = [{ L: L.slice(), ass: ass.map((a) => a.slice()), cur: null, ord, fatti: 0 }];
    ord.forEach((j, i) => {
      let m = 0;
      for (let q = 1; q < k; q++) if (L[q] < L[m]) m = q;
      const prima = L.slice();
      ass[m].push([j, L[m]]);
      L[m] += t[j];
      tr.push({ L: L.slice(), prima, ass: ass.map((a) => a.slice()), cur: j, m, ord, fatti: i + 1 });
    });
    tr[tr.length - 1].fine = true;
    return tr;
  }
  /** makespan minimo, per enumerazione con tagli (n <= 12, k <= 4) */
  function cmaxOttimo(t, k) {
    const ord = decrescente(t), n = t.length, L = new Array(k).fill(0);
    const lpt = cmaxTraccia(t, k, "lpt");
    let best = Math.max(...lpt[lpt.length - 1].L);
    const LB = Math.max(Math.max(...t), Math.ceil(somma(t) / k));
    const dfs = (i, mx) => {
      if (mx >= best || best === LB) return;
      if (i === n) { best = mx; return; }
      const x = t[ord[i]], visti = new Set();
      for (let m = 0; m < k; m++) {
        if (visti.has(L[m]) || L[m] + x >= best) continue;
        visti.add(L[m]);
        L[m] += x; dfs(i + 1, Math.max(mx, L[m])); L[m] -= x;
      }
    };
    dfs(0, 0);
    return best;
  }
  function bppCasuale() {
    const n = M.casuale(6, 10), C = M.casuale(8, 12), w = [];
    for (let j = 0; j < n; j++) w.push(M.casuale(2, Math.min(8, C - 1)));
    return { w, C, id: nuovoId() };
  }
  function cmaxCasuale() {
    const n = M.casuale(6, 9), k = M.casuale(2, 3), t = [];
    for (let j = 0; j < n; j++) t.push(M.casuale(2, 9));
    return { t, k, id: nuovoId() };
  }
  function bppStato(st) {
    const D = st.dati, regola = st.chiave(), tipo = BPP_FUNZ[regola].tipo;
    if (!D.bpp) D.bpp = Object.assign({ id: nuovoId() }, BPP_ES[0], { w: BPP_ES[0].w.slice() });
    if (!D.cmax) D.cmax = Object.assign({ id: nuovoId() }, CMAX_ES[0], { t: CMAX_ES[0].t.slice() });
    const I = tipo === "bpp" ? D.bpp : D.cmax, firma = regola + "|" + I.id;
    if (D.bFirma !== firma) {
      D.bFirma = firma;
      if (tipo === "bpp") {
        D.btr = bppTraccia(I.w, I.C, regola);
        D.bott = bppOttimo(I.w, I.C);
        D.bLB = Math.ceil(somma(I.w) / I.C);
        // posti per i contenitori: il massimo fra le quattro regole, così il disegno non salta cambiando regola
        D.bSlot = Math.max(...["nf", "ff", "bf", "ffd"].map((r) => { const q = bppTraccia(I.w, I.C, r); return q[q.length - 1].bins.length; }));
      } else {
        D.btr = cmaxTraccia(I.t, I.k, regola);
        D.bott = cmaxOttimo(I.t, I.k);
        D.bLBq = M.Q(somma(I.t), I.k);
        D.bLB = Math.max(Math.max(...I.t), M.Qv(D.bLBq));
      }
    }
    const K = D.btr.length - 1, k = M.passoK(st, K, PASSO);
    return { D, I, regola, tipo, tr: D.btr, K, k, E: D.btr[k], ott: D.bott, LB: D.bLB };
  }

  function disegnaBpp(board, st, S, crea, C) {
    const { I, tr, E, LB } = S, n = I.w.length, w = I.w, Cap = I.C;
    const slot = Math.max(S.D.bSlot, LB), x1 = slot + 1 + n;
    const [W, H] = dim(board);
    board.setBoundingBox([-0.35, Cap * 1.1 + 0.9, x1 + 0.1, -Cap * 0.2 - 0.6], false);
    const ux = W / (x1 + 0.45), uy = H / (Cap * 1.3 + 1.5);
    const fs = clamp(Math.min(ux * 0.42, uy * 0.75), 9, 15), bw = 0.39;
    const ytesto = -Math.max(0.35, 12 / uy);
    // contenitori aperti
    E.bins.forEach((bin, b) => {
      const xc = b + 0.5, scart = E.scartati && E.scartati.includes(b) && E.cur != null;
      M.rett(crea, xc - bw - 0.04, 0, xc + bw + 0.04, Cap, { strokeColor: scart ? C.viola : C.muted, strokeWidth: scart ? 2.5 : 1.5, dash: scart ? 2 : 0 });
      let y = 0;
      for (const j of bin) {
        const cur = j === E.cur;
        M.rett(crea, xc - bw, y, xc + bw, y + w[j], { strokeColor: cur ? C.a : C.b, fillColor: cur ? C.a : C.b, fillOpacity: cur ? 0.75 : 0.42, strokeWidth: 1.5 });
        if (w[j] * uy > fs) M.scritta(crea, xc, y + w[j] / 2, String(w[j]), { fontSize: fs, strokeColor: C.testo });
        y += w[j];
      }
      M.scritta(crea, xc, ytesto, String(b + 1), { fontSize: fs * 0.95, strokeColor: C.muted, cssStyle: "font-weight:600" });
    });
    // il bound: le prime LB colonne
    const yb = ytesto - Math.max(0.35, fs * 1.25 / uy);
    M.linea(crea, 0.1, yb, LB - 0.1, yb, { strokeColor: C.verde, strokeWidth: 3 });
    M.scritta(crea, LB - 0.05, yb, `  LB = ⌈${somma(w)}/${Cap}⌉ = ${LB}`, { anchorX: "left", fontSize: fs, strokeColor: C.verde, cssStyle: "font-weight:600" });
    // la coda: oggetti ancora da sistemare, nell'ordine in cui verranno guardati
    const x0 = slot + 1;
    M.linea(crea, slot + 0.5, -0.1, slot + 0.5, Cap * 1.05, { strokeColor: C.line, strokeWidth: 1.5, dash: 2 });
    M.scritta(crea, x0 + 0.1, Cap * 1.1 + 0.4, T("da sistemare", "to be packed"), { anchorX: "left", fontSize: fs * 0.95, strokeColor: C.muted, cssStyle: "font-style:italic" });
    M.scritta(crea, 0.1, Cap * 1.1 + 0.4, T(`contenitori (capacità C = ${Cap})`, `bins (capacity C = ${Cap})`), { anchorX: "left", fontSize: fs * 0.95, strokeColor: C.muted, cssStyle: "font-style:italic" });
    E.ord.slice(E.fatti).forEach((j, i) => {
      const xc = x0 + i + 0.5;
      M.rett(crea, xc - bw, 0, xc + bw, w[j], { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0.35, strokeWidth: 1.5 });
      if (w[j] * uy > fs) M.scritta(crea, xc, w[j] / 2, String(w[j]), { fontSize: fs, strokeColor: C.testo });
      M.scritta(crea, xc, ytesto, String(j + 1), { fontSize: fs * 0.85, strokeColor: C.muted });
    });
  }

  function disegnaCmax(board, st, S, crea, C) {
    const { I, tr, E, LB, ott } = S, t = I.t, k = I.k;
    const [W, H] = dim(board), stretto = W < 620;
    // stessa scala per le due regole, così passando da una all'altra il disegno non salta
    const fin = Math.max(...["ls", "lpt"].map((r) => { const q = cmaxTraccia(t, k, r); return Math.max(...q[q.length - 1].L); }));
    const Xmax = Math.max(fin, LB) * 1.12 + 1.2;
    const sx = stretto ? 34 : 92, ux = (W - sx - 10) / Xmax;
    const x0 = -sx / ux, y1 = k + 1.3, y0 = -0.8;
    board.setBoundingBox([x0, y1, Xmax, y0], false);
    const uy = H / (y1 - y0), fs = clamp(uy * 0.3, 10, 16), hb = 0.33;
    const Lmax = Math.max(...E.L);
    for (let m = 0; m < k; m++) {
      const y = k - m - 0.5;
      M.scritta(crea, -8 / ux, y, (stretto ? "M" : T("macchina ", "machine ")) + (m + 1), { anchorX: "right", fontSize: fs, strokeColor: m === E.m && E.cur != null ? C.a : C.muted, cssStyle: "font-weight:600" });
      M.linea(crea, 0, y - hb - 0.08, Xmax, y - hb - 0.08, { strokeColor: C.line, strokeWidth: 1 });
      for (const [j, s0] of E.ass[m]) {
        const cur = j === E.cur;
        M.rett(crea, s0, y - hb, s0 + t[j], y + hb, { strokeColor: cur ? C.a : C.b, fillColor: cur ? C.a : C.b, fillOpacity: cur ? 0.75 : 0.42, strokeWidth: 1.5 });
        if (t[j] * ux > 2.6 * fs) M.scritta(crea, s0 + t[j] / 2, y, `${j + 1}: ${t[j]}`, { fontSize: fs, strokeColor: C.testo });
        else if (t[j] * ux > fs) M.scritta(crea, s0 + t[j] / 2, y, String(t[j]), { fontSize: fs, strokeColor: C.testo });
      }
      M.scritta(crea, E.L[m] + 6 / ux, y, `L${m + 1} = ${E.L[m]}`, { anchorX: "left", fontSize: fs * 0.9, strokeColor: E.L[m] === Lmax && Lmax > 0 ? C.d : C.muted });
    }
    // asse dei tempi
    const passo = Xmax > 40 ? 10 : Xmax > 20 ? 5 : Xmax > 10 ? 2 : 1;
    M.linea(crea, 0, 0, Xmax, 0, { strokeColor: C.muted, strokeWidth: 1.2 });
    for (let x = 0; x <= Xmax - 0.5; x += passo) {
      M.linea(crea, x, 0, x, -0.1, { strokeColor: C.muted });
      M.scritta(crea, x, -0.38, String(x), { fontSize: fs * 0.82, strokeColor: C.muted });
    }
    // righe verticali: bound, makespan corrente, ottimo (alla fine)
    const verticali = [[LB, C.verde, "LB"]];
    if (Lmax > 0) verticali.push([Lmax, C.d, E.fine ? "UB" : "Cmax"]);
    if (E.fine) verticali.push([ott, C.blu, "z(MILP)"]);
    const gruppi = new Map();
    for (const [x, c, nm] of verticali) { const key = x.toFixed(6); if (!gruppi.has(key)) gruppi.set(key, { x, c, nomi: [] }); gruppi.get(key).nomi.push(nm); }
    [...gruppi.values()].sort((a, b) => a.x - b.x).forEach((g, i) => {
      M.linea(crea, g.x, 0, g.x, k + 0.15, { strokeColor: g.c, strokeWidth: 2.2, dash: 2 });
      const v = Number.isInteger(g.x) ? String(g.x) : GI.numTxt(g.x, 2);
      M.scritta(crea, g.x, k + 0.38 + (i % 2) * 0.45, `${g.nomi.join(" = ")} = ${v}`, { fontSize: fs * 0.9, strokeColor: g.c, cssStyle: "font-weight:600" });
    });
  }

  window.GI_RICETTE["bpp-lpt"] = {
    titolo: T("Bin packing e scheduling", "Bin packing and scheduling"),
    funzioni: BPP_FUNZ,
    etichettaFunzioni: T("Regola: bin packing (le prime quattro) · makespan", "Rule: bin packing (first four) · makespan"),
    parametri: [parPasso(DESCR_PASSO)],
    assi: false,
    opzioniBoard: M.OPZ,
    vista: [-1, 10, 20, -2],
    legenda: (st) => {
      const C = M.COL(st);
      if (BPP_FUNZ[st.chiave()].tipo === "bpp") return [
        [C.b, T("oggetti sistemati", "packed items"), "pieno"],
        [C.a, T("oggetto corrente", "current item"), "pieno"],
        [C.grigio, T("da sistemare", "to be packed"), "pieno"],
        [C.viola, T("contenitore esaminato, non basta", "bin examined, too full"), "dashed"],
        [C.verde, T("bound \\(\\lb = \\lceil \\sum_j w_j / C \\rceil\\)", "bound \\(\\lb = \\lceil \\sum_j w_j / C \\rceil\\)"), ""],
      ];
      return [
        [C.b, T("lavori assegnati", "assigned jobs"), "pieno"],
        [C.a, T("lavoro corrente", "current job"), "pieno"],
        [C.verde, T("\\(\\lb = \\max(\\max_j t_j,\\ \\sum_j t_j / k)\\)", "\\(\\lb = \\max(\\max_j t_j,\\ \\sum_j t_j / k)\\)"), "dashed"],
        [C.d, T("makespan corrente", "current makespan"), "dashed"],
        [C.blu, T("ottimo \\(\\zmilp\\)", "optimum \\(\\zmilp\\)"), "dashed"],
      ];
    },
    monta(board, st) {
      const D = st.dati;
      nuovaVoce(st);
      const tipo = () => BPP_FUNZ[st.chiave()].tipo;
      const es = (q) => () => {
        if (tipo() === "bpp") D.bpp = { w: BPP_ES[q].w.slice(), C: BPP_ES[q].C, id: nuovoId() };
        else D.cmax = { t: CMAX_ES[q].t.slice(), k: CMAX_ES[q].k, id: nuovoId() };
        vaiAZero(st); st.aggiorna();
      };
      M.comandi(st, [
        [T("Esempio 1", "Example 1"), T("bin packing: w = (4, 4, 5, 3, 2, 3), C = 7; makespan: t = (5, 5, 4, 4, 3, 3, 3), k = 3", "bin packing: w = (4, 4, 5, 3, 2, 3), C = 7; makespan: t = (5, 5, 4, 4, 3, 3, 3), k = 3"), es(0)],
        [T("Esempio 2", "Example 2"), T("bin packing: w = (3, 3, 2, 2, 2, 2), C = 7; makespan: t = (3, 4, 5, 6), k = 2", "bin packing: w = (3, 3, 2, 2, 2, 2), C = 7; makespan: t = (3, 4, 5, 6), k = 2"), es(1)],
        [T("Casuale", "Random"), T("dati casuali", "random data"), () => {
          if (tipo() === "bpp") D.bpp = bppCasuale(); else D.cmax = cmaxCasuale();
          vaiAZero(st); st.aggiorna();
        }],
      ], { k: PASSO });
      osservaDimensioni(board, st);
      daIndirizzo(st);
    },
    aggiorna(board, st) {
      const S = bppStato(st), C = M.COL(st), [W, H] = dim(board);
      M.ridisegna(board, st, [S.regola, S.I.id, S.k, M.scuro(), W, H].join("|"), (crea) => {
        if (S.tipo === "bpp") disegnaBpp(board, st, S, crea, C); else disegnaCmax(board, st, S, crea, C);
      });
    },
    formula(p, st) {
      const S = bppStato(st), { I, E, K, k, LB, ott } = S, stretto = st.board && st.board.canvasWidth < 620;
      if (S.tipo === "bpp") {
        const usati = E.bins.length, lb = `\\lb = \\left\\lceil \\tfrac{${somma(I.w)}}{${I.C}} \\right\\rceil = ${LB}`;
        if (E.fine) return `${lb} \\;\\le\\; \\zmilp = ${ott} \\;\\le\\; \\ub = ${usati}`;
        if (stretto) return T(`\\text{aperti} = ${usati} \\qquad ${lb}`, `\\text{open} = ${usati} \\qquad ${lb}`);
        return T(`\\text{passo } ${k}/${K}:\\quad \\text{contenitori aperti} = ${usati} \\qquad ${lb}`, `\\text{step } ${k}/${K}:\\quad \\text{open bins} = ${usati} \\qquad ${lb}`);
      }
      const lbq = S.D.bLBq, lb = `\\lb = \\max\\big(${Math.max(...I.t)},\\ ${M.Qtex(lbq)}\\big) = ${M.Qtex(Math.max(...I.t) >= M.Qv(lbq) ? M.Q(Math.max(...I.t)) : lbq)}`;
      const cm = Math.max(...E.L);
      if (E.fine) return `${lb} \\;\\le\\; \\zmilp = ${ott} \\;\\le\\; \\ub = ${cm}`;
      if (stretto) return `\\max_m L_m = ${cm} \\qquad \\lb = ${M.Qtex(Math.max(...I.t) >= M.Qv(lbq) ? M.Q(Math.max(...I.t)) : lbq)}`;
      return T(`\\text{passo } ${k}/${K}:\\quad \\max_m L_m = ${cm} \\qquad ${lb}`, `\\text{step } ${k}/${K}:\\quad \\max_m L_m = ${cm} \\qquad ${lb}`);
    },
    letture(p, st) {
      const S = bppStato(st), { I, E, k, LB, ott, regola } = S, C = M.COL(st), nome = BPP_FUNZ[regola].nome || BPP_FUNZ[regola].etichetta;
      let nota = "", righe;
      if (S.tipo === "bpp") {
        const w = I.w;
        if (k === 0) {
          nota = regola === "ffd"
            ? T(`${nome}: gli oggetti si guardano per peso decrescente: ${lista(E.ord.map((j) => j + 1))} (pareggi sull'indice più piccolo).`, `${nome}: items are examined by decreasing weight: ${lista(E.ord.map((j) => j + 1))} (ties on the smallest index).`)
            : T(`${nome}: gli oggetti si guardano nell'ordine dato, \\(w = (${lista(w)})\\), capacità \\(C = ${I.C}\\).`, `${nome}: items are examined in the given order, \\(w = (${lista(w)})\\), capacity \\(C = ${I.C}\\).`);
        } else {
          const j = E.cur, J = j + 1, b = E.b + 1, r = E.res, ogg = T(`Oggetto ${J} (\\(w_{${J}} = ${w[j]}\\)): `, `Item ${J} (\\(w_{${J}} = ${w[j]}\\)): `);
          const resTxt = r.length ? T(`capacità residue dei contenitori aperti \\((${lista(r)})\\)`, `residual capacities of the open bins \\((${lista(r)})\\)`) : T("nessun contenitore aperto", "no open bin");
          let perche;
          if (regola === "nf") perche = E.nuovo ? (r.length ? T(`il contenitore corrente ${r.length} ha residuo ${r[r.length - 1]} < ${w[j]}: si chiude e si apre il contenitore ${b}`, `the current bin ${r.length} has residual ${r[r.length - 1]} < ${w[j]}: it is closed and bin ${b} is opened`) : T(`si apre il contenitore ${b}`, `bin ${b} is opened`))
            : T(`ci sta nel contenitore corrente ${b}`, `it fits in the current bin ${b}`);
          else if (regola === "bf") perche = E.nuovo ? T(`non ci sta in nessun contenitore aperto: si apre il contenitore ${b}`, `it fits in no open bin: bin ${b} is opened`)
            : T(`ci sta in ${lista(E.cand.map((q) => `${q + 1} (resterebbe ${r[q] - w[j]})`))}: il più pieno dopo l'inserimento è il contenitore ${b}`, `it fits in ${lista(E.cand.map((q) => `${q + 1} (${r[q] - w[j]} would be left)`))}: the fullest after insertion is bin ${b}`);
          else perche = E.nuovo ? T(`non ci sta in nessun contenitore aperto: si apre il contenitore ${b}`, `it fits in no open bin: bin ${b} is opened`)
            : T(`il primo contenitore in cui ci sta è il contenitore ${b}`, `the first bin where it fits is bin ${b}`);
          nota = `${ogg}${resTxt}; ${perche}.`;
          if (E.fine) nota += T(` Fine: ${M.tinta(C.a, E.bins.length + " contenitori")}, un upper bound (problema di minimo).`, ` End: ${M.tinta(C.a, E.bins.length + " bins")}, an upper bound (minimisation problem).`);
        }
        righe = [
          [T("\\(\\lb = \\lceil \\sum_j w_j / C \\rceil\\)", "\\(\\lb = \\lceil \\sum_j w_j / C \\rceil\\)"), `\\(${LB}\\)`],
          [T("\\(\\zmilp\\) (ottimo)", "\\(\\zmilp\\) (optimum)"), `\\(${ott}\\)`],
          [E.fine ? T(`\\(\\ub\\) (${nome})`, `\\(\\ub\\) (${nome})`) : T("contenitori aperti", "open bins"), `\\(${E.bins.length}\\)`],
          [T("gap dell'euristica", "heuristic gap"), E.fine ? `\\(${pct((E.bins.length - ott) / ott)}\\)` : "—"],
        ];
      } else {
        const t = I.t, Ltex = (L) => `(${lista(L)})`;
        if (k === 0) {
          nota = regola === "lpt"
            ? T(`LPT: i lavori si guardano per durata decrescente: ${lista(E.ord.map((j) => j + 1))} (pareggi sull'indice più piccolo); ognuno va sulla macchina meno carica.`, `LPT: jobs are examined by decreasing duration: ${lista(E.ord.map((j) => j + 1))} (ties on the smallest index); each goes to the least loaded machine.`)
            : T(`List scheduling: i lavori nell'ordine dato, \\(t = (${lista(t)})\\), su \\(k = ${I.k}\\) macchine; ognuno va sulla macchina meno carica.`, `List scheduling: jobs in the given order, \\(t = (${lista(t)})\\), on \\(k = ${I.k}\\) machines; each goes to the least loaded machine.`);
        } else {
          const j = E.cur, J = j + 1, m = E.m + 1;
          nota = T(`Lavoro ${J} (\\(t_{${J}} = ${t[j]}\\)): carichi \\(L = ${Ltex(E.prima)}\\); il minimo è la macchina ${m}, che passa a \\(${E.prima[E.m]} + ${t[j]} = ${E.L[E.m]}\\).`,
            `Job ${J} (\\(t_{${J}} = ${t[j]}\\)): loads \\(L = ${Ltex(E.prima)}\\); the minimum is machine ${m}, which goes to \\(${E.prima[E.m]} + ${t[j]} = ${E.L[E.m]}\\).`);
          if (E.fine) nota += T(` Fine: makespan ${M.tinta(C.a, String(Math.max(...E.L)))}, un upper bound.`, ` End: makespan ${M.tinta(C.a, String(Math.max(...E.L)))}, an upper bound.`);
        }
        const coda = E.ord.slice(E.fatti).map((j) => `${j + 1} (${t[j]})`);
        if (coda.length) nota += `<br>${T("Da assegnare, nell'ordine", "Still to assign, in order")}: ${lista(coda)}.`;
        const cm = Math.max(...E.L), lbtex = Number.isInteger(LB) ? String(LB) : M.Qtex(S.D.bLBq);
        righe = [
          [T("\\(\\lb = \\max(\\max_j t_j,\\ \\sum_j t_j/k)\\)", "\\(\\lb = \\max(\\max_j t_j,\\ \\sum_j t_j/k)\\)"), `\\(${lbtex}\\)`],
          [T("\\(\\zmilp\\) (ottimo)", "\\(\\zmilp\\) (optimum)"), `\\(${ott}\\)`],
          [E.fine ? `\\(\\ub\\) (${nome})` : T("makespan corrente", "current makespan"), `\\(${cm}\\)`],
          [T("gap dell'euristica", "heuristic gap"), E.fine ? `\\(${pct((cm - ott) / ott)}\\)` : "—"],
        ];
      }
      return nota + M.tab([T("bound", "bound"), T("valore", "value")], righe, -1, C.a);
    },
    domanda: T("Sull'esempio 1 confronta Next Fit, First Fit e Best Fit: su quale oggetto si separano? Poi First Fit Decreasing sull'esempio 2: arriva al bound \\(\\lb\\)? Nel makespan, confronta List scheduling e LPT sull'esempio 2 e spiega perché conviene mettere per ultimi i lavori corti.",
      "On example 1 compare Next Fit, First Fit and Best Fit: on which item do they part ways? Then First Fit Decreasing on example 2: does it reach the bound \\(\\lb\\)? For the makespan, compare List scheduling and LPT on example 2 and explain why the short jobs should come last."),
  };

  // funzioni di calcolo, per le prove (nessun effetto sul disegno)
  window.GI_MIP_B = { zainoCalcola, zainoOttimo, ordineRapporto, vicinoPiuVicino, heldKarp, tspCalcola, bppTraccia, bppOttimo, cmaxTraccia, cmaxOttimo };
})();
