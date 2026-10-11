/* Laboratorio di «Modellazione MIP / MIP Modelling»: ricette del capitolo 2
 * (Rilassamenti, dualità e bound).
 *
 *   punti-interi   il poliedro di un problema intero in due variabili, i suoi punti
 *                  interi, l'ottimo del rilassamento continuo (vertice esatto) e
 *                  l'ottimo intero; la retta di livello z; il bound z(LP) >= z(MILP)
 *                  e cosa succede arrotondando l'ottimo continuo
 *   branch-bound   il branch-and-bound passo passo sugli stessi problemi: a sinistra
 *                  il poliedro del nodo corrente, a destra (sotto, su telefono)
 *                  l'albero che cresce; visita in profondità o per miglior bound
 *
 * Notazione delle dispense: \tilde x ottimo del rilassamento continuo, x^* ottimo
 * intero, \bar x incumbent (la migliore soluzione intera trovata), in un massimo
 * \lb = valore dell'incumbent e \ub = miglior bound dei nodi aperti.
 * Tutti i rilassamenti si risolvono in modo esatto (frazioni) enumerando i vertici:
 * tutti i problemi sono di massimo, con x >= 0 e regione limitata.
 * Helper comuni in gi-comune.js (window.GI_MIP); formato delle ricette nel commento
 * in testa a interattivi.js.
 */
(function () {
  "use strict";
  const GI = window.GI, M = window.GI_MIP;
  const T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const { Q, Qv, Qtex, Qadd, Qmul, coppiaQ, coppia, lin, tinta } = M;

  // ================================================================ problemi
  // max c'x, A x <= b, x >= 0 intero. I primi due vincoli si muovono con i cursori
  // b_1, b_2 nell'app dei punti interi. Numeri verificati con python (bb.py):
  //   e1: z(LP) = 23/5 in (9/5; 14/5), z(MILP) = 4
  //   e2: z(LP) = 165/4 in (9/4; 15/4), z(MILP) = 40 in (0; 5)
  //   e3: z(LP) = 59/7 in (20/7; 3), z(MILP) = 7 in (2; 1)
  //   e4: z(LP) = 63/2 in (9/4; 9/2), z(MILP) = 30 in (3; 3)
  const ESEMPI = {
    e1: { c: [1, 1], V: [{ a: [2, 3], b: 12 }, { a: [4, 1], b: 10 }] },
    e2: { c: [5, 8], V: [{ a: [1, 1], b: 6 }, { a: [5, 9], b: 45 }] },
    e3: { c: [4, -1], V: [{ a: [7, -2], b: 14 }, { a: [0, 1], b: 3 }, { a: [2, -2], b: 3 }] },
    e4: { c: [6, 4], V: [{ a: [2, 1], b: 9 }, { a: [4, 4], b: 27 }] },
  };
  const VOCI = () => Object.fromEntries(Object.keys(ESEMPI).map((k, i) => [k, { etichetta: T("Es. ", "Ex. ") + (i + 1) }]));
  // intervallo dei cursori b_i: dal 60 % al 130 % circa del valore di partenza
  const rangeB = (b) => [Math.max(1, Math.round(b * 0.6)), Math.round(b * 1.3)];

  // ================================================================ aritmetica esatta
  const cmpQ = (a, b) => Math.sign(a.n * b.d - b.n * a.d);
  const valore = (c, x) => Qadd(Qmul(Q(c[0]), x[0]), Qmul(Q(c[1]), x[1]));
  /** max c'x su {x : V} in modo esatto, enumerando i vertici; a parità di valore
   *  il vertice con x_1 minore (poi x_2 minore). null se la regione è vuota. */
  const risolvi = (V, c) => {
    let best = null, bz = null;
    for (const p of M.verticiEsatti(V)) {
      const z = valore(c, p);
      const s = best ? cmpQ(z, bz) : 1;
      if (s > 0 || (s === 0 && (cmpQ(p[0], best[0]) < 0 || (cmpQ(p[0], best[0]) === 0 && cmpQ(p[1], best[1]) < 0)))) { best = p; bz = z; }
    }
    return best ? { x: best, z: bz } : null;
  };
  /** frazione come testo semplice (per le scritte sul grafico): 63/2, −3 */
  const qt = (q) => (q.n < 0 ? "−" : "") + (q.d === 1 ? Math.abs(q.n) : Math.abs(q.n) + "/" + q.d);
  const SUB = ["₁", "₂"];
  const vincoliTex = (V) => V.map((v) => `${lin(v.a)} \\le ${v.b}`);
  // il problema in una riga (o in due, se la finestra è stretta)
  const problemaTex = (ob, vincoli) => {
    const con = `\\text{${T("con", "s.t.")}}`, dom = "\\boldsymbol x \\in \\Z^2_+";
    return window.innerWidth < 700
      ? `\\begin{array}{l}\\max\\ ${ob},\\ \\ ${dom} \\\\ ${vincoli.join(",\\ ")}\\end{array}`
      : `\\max\\ ${ob}\\quad ${con}\\quad ${vincoli.join(",\\ ")},\\ ${dom}`;
  };

  // segmento della retta a'x = b dentro il riquadro [x0, x1] x [y0, y1] (o null)
  const segmento = (a, b, x0, x1, y0, y1) => {
    const P = [];
    if (a[1] !== 0) for (const x of [x0, x1]) { const y = (b - a[0] * x) / a[1]; if (y >= y0 - 1e-9 && y <= y1 + 1e-9) P.push([x, y]); }
    if (a[0] !== 0) for (const y of [y0, y1]) { const x = (b - a[1] * y) / a[0]; if (x >= x0 - 1e-9 && x <= x1 + 1e-9) P.push([x, y]); }
    if (P.length < 2) return null;
    let lo = P[0], hi = P[0];
    const u = (p) => -a[1] * p[0] + a[0] * p[1];
    for (const p of P) { if (u(p) < u(lo)) lo = p; if (u(p) > u(hi)) hi = p; }
    return [lo, hi];
  };
  // il tratto della retta c'x = z dentro il poligono P (o null)
  const trattoRetta = (P, c, z) => {
    const pts = [], f = (p) => c[0] * p[0] + c[1] * p[1] - z, tol = 1e-9 * (1 + Math.abs(z));
    for (let k = 0; k < P.length; k++) {
      const p = P[k], q = P[(k + 1) % P.length], fp = f(p), fq = f(q);
      if (Math.abs(fp) <= tol) pts.push(p);
      if ((fp < -tol && fq > tol) || (fp > tol && fq < -tol)) {
        const t = fp / (fp - fq);
        pts.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
      }
    }
    if (!pts.length) return null;
    const u = (p) => -c[1] * p[0] + c[0] * p[1];
    let lo = pts[0], hi = pts[0];
    for (const p of pts) { if (u(p) < u(lo)) lo = p; if (u(p) > u(hi)) hi = p; }
    return [lo, hi];
  };
  // sposta il riquadro delle letture subito dopo l'elemento dopo (le letture restano in vista
  // senza scorrere la colonna dei controlli)
  const lettureDopo = (st, dopo) => {
    const l = st.el.querySelector(".gi-letture");
    if (l && dopo && dopo.nextElementSibling !== l) dopo.after(l);
  };
  // La board segue le dimensioni del suo contenitore (il motore le cambia per riempire la
  // finestra): il ridimensionamento automatico di JSXGraph è spento (opzioni ADATTA) e qui la
  // tela si rimisura e la ricetta ridisegna. Il contenitore resta lo stesso quando la board si
  // ricrea, quindi l'osservatore è uno solo; il callback arriva al più una volta per fotogramma.
  const ADATTA = Object.assign({}, M.OPZ, { resize: { enabled: false } });
  const seguiDimensioni = (board, st) => {
    const el = board.containerObj;
    if (window.ResizeObserver && el && !el._mipRO) {
      el._mipRO = new ResizeObserver(() => { if (document.body.contains(el)) st.aggiorna(); });
      el._mipRO.observe(el);
    }
  };
  /** rimisura la tela sul contenitore e restituisce [larghezza, altezza] in pixel */
  const misura = (board) => {
    const el = board.containerObj, W = el.clientWidth || board.canvasWidth, H = el.clientHeight || board.canvasHeight;
    if (Math.abs(board.canvasWidth - W) > 1 || Math.abs(board.canvasHeight - H) > 1) board.resizeContainer(W, H, true, true);
    return [W, H];
  };
  // il pulsante «Azzera» del motore: dopo il suo clic, i cursori tornano ai valori dell'esempio
  const dopoAzzera = (st, fz) => {
    const az = [...st.el.querySelectorAll("button.gi-btn")].find((b) => b.textContent.trim() === T("Azzera", "Reset"));
    if (az && !az._mipA) { az._mipA = true; az.addEventListener("click", fz); }
  };

  // ================================================================
  // 1. Punti interi e rilassamento continuo
  // ================================================================
  // il problema corrente (esempio + cursori)
  const problemaPI = (st) => {
    const E = ESEMPI[st.chiave()], p = st.p();
    const V = E.V.map((v, i) => (i < 2 ? { a: v.a, b: Math.round(i ? p.b2 : p.b1) } : v));
    return { c: [Math.round(p.c1), Math.round(p.c2)], V, V0: V.concat(M.nonneg()) };
  };
  // riquadro che contiene il poliedro anche con i b_i al massimo
  const cacheBox = {};
  const boxDi = (k) => {
    if (cacheBox[k]) return cacheBox[k];
    const E = ESEMPI[k];
    const V = E.V.map((v, i) => (i < 2 ? { a: v.a, b: rangeB(v.b)[1] } : v)).concat(M.nonneg());
    const P = M.poligono(V, 1e3);
    const X = Math.max(4, ...P.map((q) => q[0])), Y = Math.max(4, ...P.map((q) => q[1]));
    return (cacheBox[k] = { X: Math.ceil(X), Y: Math.ceil(Y) });
  };
  // tutti i calcoli dell'app (memorizzati per firma)
  const analisiPI = (st) => {
    const P = problemaPI(st), firma = st.chiave() + "|" + P.c + "|" + P.V.map((v) => v.b);
    if (st.dati.an && st.dati.an.firma === firma) return st.dati.an;
    const B = boxDi(st.chiave());
    const lp = risolvi(P.V0, P.c);
    const interi = M.puntiInteri(P.V0, 0, B.X + 1, 0, B.Y + 1);
    let ip = null;
    for (const q of interi) { const z = P.c[0] * q[0] + P.c[1] * q[1]; if (!ip || z > ip.z) ip = { x: q, z }; }
    const tondo = lp ? lp.x.map((q) => Math.round(Qv(q))) : null;
    const violati = tondo ? P.V0.map((v, i) => [v, i]).filter(([v]) => v.a[0] * tondo[0] + v.a[1] * tondo[1] > v.b) : [];
    const poli = M.poligono(P.V0, 1e3);
    const vals = poli.map((q) => P.c[0] * q[0] + P.c[1] * q[1]);
    return (st.dati.an = { firma, P, B, lp, interi, ip, tondo, violati, poli, zmin: Math.min(0, ...vals) });
  };
  // il cursore z: l'intervallo segue il problema (da min c'x sul poliedro a z(LP) + 2)
  const preparaZ = (st, A) => {
    const i = M.inputDi(st, "z");
    if (!i || !A.lp) return;
    const lo = Math.floor(A.zmin), hi = Math.ceil(Qv(A.lp.z)) + 2;
    if (+i.min !== lo) i.min = lo;
    if (+i.max !== hi) i.max = hi;
    if (+i.value > hi) i.value = hi;
    if (+i.value < lo) i.value = lo;
  };
  const valoriEsempio = (st) => {
    const E = ESEMPI[st.chiave()], k = st.chiave();
    const imposta = (nome, v, lo, hi) => {
      const i = M.inputDi(st, nome);
      if (!i) return;
      if (lo !== undefined) { i.min = lo; i.max = hi; }
      i.value = v;
    };
    imposta("c_1", E.c[0]); imposta("c_2", E.c[1]);
    imposta("b_1", E.V[0].b, ...rangeB(E.V[0].b));
    imposta("b_2", E.V[1].b, ...rangeB(E.V[1].b));
    st.dati.es = k;
    st.dati.an = null;
    const A = analisiPI(st);
    preparaZ(st, A);
    const iz = M.inputDi(st, "z");
    if (iz && A.ip) iz.value = A.ip.z;
  };

  window.GI_RICETTE["punti-interi"] = {
    titolo: T("Punti interi e rilassamento", "Integer points and relaxation"),
    funzioni: VOCI(),
    etichettaFunzioni: T("Problema", "Problem"),
    parametri: [
      { k: "z", nome: "z", min: 0, max: 10, step: 0.25, val: 4, colore: "a", cifre: 2,
        descr: T("livello della retta \\(\\boldsymbol c'\\boldsymbol x = z\\) (▶ la fa scorrere)", "level of the line \\(\\boldsymbol c'\\boldsymbol x = z\\) (▶ slides it)") },
      { k: "c1", nome: "c_1", min: -4, max: 9, step: 1, val: 1, colore: "b", cifre: 0,
        descr: T("coefficiente di \\(x_1\\) nell'obiettivo", "coefficient of \\(x_1\\) in the objective") },
      { k: "c2", nome: "c_2", min: -4, max: 9, step: 1, val: 1, colore: "b", cifre: 0,
        descr: T("coefficiente di \\(x_2\\) nell'obiettivo", "coefficient of \\(x_2\\) in the objective") },
      { k: "b1", nome: "b_1", min: 1, max: 20, step: 1, val: 12, colore: "e", cifre: 0,
        descr: T("termine noto del vincolo 1: sposta la retta", "right-hand side of constraint 1: moves the line") },
      { k: "b2", nome: "b_2", min: 1, max: 20, step: 1, val: 10, colore: "e", cifre: 0,
        descr: T("termine noto del vincolo 2", "right-hand side of constraint 2") },
    ],
    // stessa unità sui due assi: la vista si adatta alla board in aggiorna (M.adatta)
    vista: (k) => { const B = boxDi(k); return [-0.7, B.Y + 0.7, B.X + 0.7, -0.7]; },
    opzioniBoard: ADATTA,
    legenda: (st) => {
      const C = M.COL(st);
      return [
        [C.rosso, T("rilassamento continuo", "continuous relaxation"), "pieno"],
        [C.verde, T("punti interi ammissibili", "feasible integer points"), "punto"],
        [C.verde, T("involucro dei punti interi", "hull of the integer points"), "dashed"],
        [C.blu, T("\\(\\tilde{\\boldsymbol x}\\) ottimo continuo", "\\(\\tilde{\\boldsymbol x}\\) continuous optimum"), "punto"],
        [C.viola, T("\\(\\tilde{\\boldsymbol x}\\) arrotondato", "\\(\\tilde{\\boldsymbol x}\\) rounded"), "punto"],
        [st.colore("a"), T("retta \\(\\boldsymbol c'\\boldsymbol x = z\\)", "line \\(\\boldsymbol c'\\boldsymbol x = z\\)"), ""],
      ];
    },
    monta(board, st) {
      if (st.dati.es !== st.chiave()) valoriEsempio(st);
      dopoAzzera(st, () => { st.dati.es = null; valoriEsempio(st); st.aggiorna(); });
      lettureDopo(st, M.ctrlDi(st, "z"));
      seguiDimensioni(board, st);
      const C = M.COL(st), A = () => analisiPI(st);
      // la retta di livello e il suo tratto dentro il poliedro (seguono il cursore z)
      board.create("line", [() => -st.p().z, () => A().P.c[0], () => A().P.c[1]], {
        strokeColor: st.colore("a"), strokeWidth: 2, fixed: true, highlight: false, withLabel: false,
        visible: () => A().P.c[0] !== 0 || A().P.c[1] !== 0,
      });
      GI.spezzata(board, () => trattoRetta(A().poli, A().P.c, st.p().z) || [], {
        strokeColor: st.colore("a"), strokeWidth: 6, strokeOpacity: 0.8, fixed: true,
      });
      // i punti interi ammissibili che stanno sulla retta
      GI.nuvola(board, 40, () => {
        const a = A(), z = st.p().z;
        return a.interi.filter((q) => Math.abs(a.P.c[0] * q[0] + a.P.c[1] * q[1] - z) < 1e-9);
      }, { size: 8, fillColor: "none", fillOpacity: 0, strokeColor: st.colore("a"), strokeWidth: 2.5 });
      void C;
    },
    aggiorna(board, st) {
      const A = analisiPI(st), C = M.COL(st), B0 = boxDi(st.chiave());
      preparaZ(st, A);
      misura(board);
      M.adatta(board, -0.7, B0.Y + 0.7, B0.X + 0.7, -0.7);
      M.ridisegna(board, st, [A.firma, M.scuro()].join("|"), (crea) => {
        const { P, B } = A, c = P.c;
        // le rette dei vincoli (1 e 2 dei colori dei loro cursori, gli altri grigi)
        P.V.forEach((v, i) => {
          const s = segmento(v.a, v.b, -0.9, B.X + 0.9, -0.9, B.Y + 0.9);
          if (s) crea("curve", [[s[0][0], s[1][0]], [s[0][1], s[1][1]]], {
            strokeColor: i < 2 ? st.colore("e") : C.grigio, strokeWidth: i < 2 ? 1.8 : 1.3,
            dash: 2, fixed: true, highlight: false,
          });
        });
        if (A.poli.length) M.area(crea, A.poli, { strokeColor: C.rosso, fillColor: C.rosso, fillOpacity: 0.16 });
        // l'involucro convesso dei punti interi ammissibili
        const H = M.involucro(A.interi);
        if (H.length >= 3) M.area(crea, H, { strokeColor: C.verde, strokeWidth: 2, dash: 2, fillColor: C.verde, fillOpacity: 0.1 });
        else if (H.length === 2) M.linea(crea, H[0][0], H[0][1], H[1][0], H[1][1], { strokeColor: C.verde, strokeWidth: 2, dash: 2 });
        // il reticolo: punti interi fuori in grigio, dentro in verde
        for (let i = 0; i <= B.X; i++) for (let j = 0; j <= B.Y; j++) {
          const dentro = P.V0.every((v) => v.a[0] * i + v.a[1] * j <= v.b);
          if (!dentro) M.pallino(crea, i, j, { size: 1.5, fillColor: C.grigio, strokeColor: C.grigio });
        }
        for (const q of A.interi) M.pallino(crea, q[0], q[1], { size: 3.5, fillColor: C.verde, strokeColor: C.verde });
        // la direzione di c, nell'origine
        const nc = Math.hypot(c[0], c[1]);
        if (nc) crea("arrow", [[0, 0], [(c[0] / nc) * 1.2, (c[1] / nc) * 1.2]], {
          strokeColor: C.blu, strokeWidth: 3, fixed: true, highlight: false, withLabel: false, lastArrow: { type: 2, size: 5 },
        });
        // l'arrotondamento di x~, l'ottimo intero e l'ottimo continuo
        if (A.tondo && !(A.lp.x[0].d === 1 && A.lp.x[1].d === 1)) {
          M.linea(crea, Qv(A.lp.x[0]), Qv(A.lp.x[1]), A.tondo[0], A.tondo[1], { strokeColor: C.viola, strokeWidth: 1.5, dash: 2 });
          M.pallino(crea, A.tondo[0], A.tondo[1], { face: "x", size: 6, strokeWidth: 3, strokeColor: C.viola, fillColor: C.viola });
        }
        if (A.ip) M.pallino(crea, A.ip.x[0], A.ip.x[1], { size: 7, fillColor: C.verde, strokeColor: C.testo, strokeWidth: 2 });
        if (A.lp) M.pallino(crea, Qv(A.lp.x[0]), Qv(A.lp.x[1]), { size: 6, fillColor: C.blu, strokeColor: C.blu });
      });
    },
    formula(p, st) {
      const A = analisiPI(st), c = A.P.c;
      const t = (v, k, x, primo) => `${v < 0 ? "-" : primo ? "" : "+"}${st.col(k, Math.abs(v))}\\,${x}`;
      const righe = A.P.V.map((v, i) => {
        const s = `${lin(v.a)} \\le ${i < 2 ? st.col(i ? "b2" : "b1", v.b) : v.b}`;
        return s;
      });
      return problemaTex(`${t(c[0], "c1", "x_1", true)} ${t(c[1], "c2", "x_2", false)}`, righe);
    },
    letture(p, st) {
      const A = analisiPI(st), C = M.COL(st), c = A.P.c;
      if (!A.lp) return T("Il poliedro è vuoto.", "The polyhedron is empty.");
      if (!c[0] && !c[1]) return T("Con \\(\\boldsymbol c = \\boldsymbol 0\\) tutti i punti hanno valore \\(0\\): scegli un \\(c_1\\) o un \\(c_2\\) diverso da zero.",
        "With \\(\\boldsymbol c = \\boldsymbol 0\\) every point has value \\(0\\): pick a nonzero \\(c_1\\) or \\(c_2\\).");
      const zl = A.lp.z, righe = [];
      righe.push(T(`${tinta(C.blu, "Rilassamento continuo")}: \\(\\tilde{\\boldsymbol x} = ${coppiaQ(A.lp.x)}\\), \\(\\zlp = ${Qtex(zl)}\\)`,
        `${tinta(C.blu, "Continuous relaxation")}: \\(\\tilde{\\boldsymbol x} = ${coppiaQ(A.lp.x)}\\), \\(\\zlp = ${Qtex(zl)}\\)`));
      if (!A.ip) { righe.push(T("Nessun punto intero ammissibile: il problema intero è inammissibile.", "No feasible integer point: the integer problem is infeasible.")); return righe.join("<br>"); }
      const n = A.interi.length, nott = A.interi.filter((q) => c[0] * q[0] + c[1] * q[1] === A.ip.z).length;
      righe.push(T(`${tinta(C.verde, "Ottimo intero")}: \\(\\boldsymbol x^* = ${coppia(A.ip.x[0], A.ip.x[1])}\\), \\(\\zmilp = ${A.ip.z}\\) (${n} ${n === 1 ? "punto intero ammissibile" : "punti interi ammissibili"}${nott > 1 ? `, ${nott} ottimi` : ""})`,
        `${tinta(C.verde, "Integer optimum")}: \\(\\boldsymbol x^* = ${coppia(A.ip.x[0], A.ip.x[1])}\\), \\(\\zmilp = ${A.ip.z}\\) (${n} feasible integer ${n === 1 ? "point" : "points"}${nott > 1 ? `, ${nott} optimal` : ""})`));
      const gap = M.Qsub(zl, Q(A.ip.z));
      righe.push(gap.n === 0
        ? T(`<strong>Bound</strong>: \\(\\zmilp = \\zlp = ${A.ip.z}\\): il rilassamento chiude il problema, divario \\(0\\).`,
          `<strong>Bound</strong>: \\(\\zmilp = \\zlp = ${A.ip.z}\\): the relaxation closes the problem, gap \\(0\\).`)
        : T(`<strong>Bound</strong>: \\(\\zmilp = ${A.ip.z} \\le \\zlp = ${Qtex(zl)}\\); divario \\(\\zlp - \\zmilp = ${Qtex(gap)}\\).`,
          `<strong>Bound</strong>: \\(\\zmilp = ${A.ip.z} \\le \\zlp = ${Qtex(zl)}\\); gap \\(\\zlp - \\zmilp = ${Qtex(gap)}\\).`));
      // arrotondare
      const intero = A.lp.x[0].d === 1 && A.lp.x[1].d === 1;
      if (intero) {
        righe.push(T("\\(\\tilde{\\boldsymbol x}\\) è già intero: è anche l'ottimo intero.", "\\(\\tilde{\\boldsymbol x}\\) is already integer: it is also the integer optimum."));
      } else {
        const r = A.tondo, rt = `\\(${coppia(r[0], r[1])}\\)`, zr = c[0] * r[0] + c[1] * r[1];
        let s;
        if (A.violati.length) {
          const [v] = A.violati[0], lhs = v.a[0] * r[0] + v.a[1] * r[1];
          s = T(`${rt} ${tinta(C.viola, "non è ammissibile")}: \\(${lin(v.a)} = ${lhs} > ${v.b}\\).`, `${rt} ${tinta(C.viola, "is infeasible")}: \\(${lin(v.a)} = ${lhs} > ${v.b}\\).`);
        } else if (zr < A.ip.z) {
          s = T(`${rt} è ammissibile ma ${tinta(C.viola, "non è ottimo")}: vale \\(${zr} < ${A.ip.z}\\).`, `${rt} is feasible but ${tinta(C.viola, "not optimal")}: its value is \\(${zr} < ${A.ip.z}\\).`);
        } else {
          s = T(`${rt} è ammissibile e ottimo: qui arrotondare funziona.`, `${rt} is feasible and optimal: here rounding works.`);
        }
        righe.push(T(`<strong>Arrotondare</strong> \\(\\tilde{\\boldsymbol x}\\) dà `, `<strong>Rounding</strong> \\(\\tilde{\\boldsymbol x}\\) gives `) + s);
      }
      // la retta di livello
      const z = p.z, zs = GI.num(z, 2), zc = st.colore("a");
      const sopra = A.interi.filter((q) => c[0] * q[0] + c[1] * q[1] >= z - 1e-9).length;
      let r;
      if (z > Qv(zl) + 1e-9) r = T(`la retta non incontra più il poliedro: \\(z > \\zlp\\).`, `the line no longer meets the polyhedron: \\(z > \\zlp\\).`);
      else if (z > A.ip.z + 1e-9) r = T(`la retta taglia ancora il poliedro, ma nessun punto intero ha \\(\\boldsymbol c'\\boldsymbol x \\ge ${zs}\\): siamo nel divario, \\(\\zmilp < z \\le \\zlp\\).`,
        `the line still cuts the polyhedron, but no integer point has \\(\\boldsymbol c'\\boldsymbol x \\ge ${zs}\\): we are in the gap, \\(\\zmilp < z \\le \\zlp\\).`);
      else r = T(`${sopra} ${sopra === 1 ? "punto intero ammissibile ha" : "punti interi ammissibili hanno"} \\(\\boldsymbol c'\\boldsymbol x \\ge ${zs}\\).`,
        `${sopra} feasible integer ${sopra === 1 ? "point has" : "points have"} \\(\\boldsymbol c'\\boldsymbol x \\ge ${zs}\\).`);
      righe.push(`${tinta(zc, T("Retta", "Line"))} \\(z = ${zs}\\): ` + r);
      return righe.join("<br>");
    },
    domanda: T("Nell'esempio 1 premi ▶ su \\(z\\): fra quali valori la retta taglia il poliedro senza toccare punti interi? Nell'esempio 2 arrotonda \\(\\tilde{\\boldsymbol x}\\): il punto è ammissibile? E arrotondando per difetto, quanto perdi rispetto a \\(\\zmilp\\)? Riesci a portare il divario a zero muovendo \\(b_1\\) e \\(b_2\\)?",
      "In example 1 press ▶ on \\(z\\): for which values does the line cut the polyhedron without touching integer points? In example 2 round \\(\\tilde{\\boldsymbol x}\\): is the point feasible? And rounding down, how much do you lose with respect to \\(\\zmilp\\)? Can you bring the gap to zero by moving \\(b_1\\) and \\(b_2\\)?"),
  };

  // ================================================================
  // 2. Branch-and-bound passo passo
  // ================================================================
  // La traccia: un'istantanea per passo. Un nodo si risolve in un passo (il suo
  // rilassamento) e si decide nel passo dopo (potatura o ramificazione); un nodo
  // inammissibile si risolve e si pota nello stesso passo.
  // Regole: si ramifica sulla prima variabile frazionaria; visita «dfs» (in
  // profondità, prima il ramo <=) o «best» (nodo aperto con il bound del padre
  // più alto, a parità quello creato prima); potatura per bound se z <= LB.
  const tracciaBB = (E, visita) => {
    const V0 = E.V.concat(M.nonneg());
    const nodi = [{ id: 0, padre: null, extra: [], ramo: null, bound: null, stato: "aperto", x: null, z: null, prof: 0 }];
    const aperti = [0];
    let LB = null, inc = null;
    const passi = [];
    const foto = (o) => passi.push(Object.assign({ nodi: nodi.map((n) => Object.assign({}, n)), aperti: aperti.slice(), LB, inc, corrente: null }, o));
    foto({ tipo: "inizio" });
    while (aperti.length) {
      let pos = aperti.length - 1;
      if (visita === "best") {
        pos = 0;
        for (let i = 1; i < aperti.length; i++) {
          const s = cmpQ(nodi[aperti[i]].bound, nodi[aperti[pos]].bound);
          if (s > 0 || (s === 0 && aperti[i] < aperti[pos])) pos = i;
        }
      }
      const id = aperti.splice(pos, 1)[0], n = nodi[id];
      const r = risolvi(V0.concat(n.extra), E.c);
      if (!r) { n.stato = "inamm"; foto({ tipo: "inamm", corrente: id }); continue; }
      n.x = r.x; n.z = r.z; n.stato = "corrente";
      foto({ tipo: "risolto", corrente: id });
      if (LB !== null && cmpQ(r.z, LB) <= 0) { n.stato = "bound"; foto({ tipo: "bound", corrente: id }); continue; }
      const fr = [0, 1].filter((j) => r.x[j].d !== 1);
      if (!fr.length) { LB = r.z; inc = r.x; n.stato = "intero"; foto({ tipo: "intero", corrente: id }); continue; }
      const j = fr[0], fl = M.Qfloor(r.x[j]);
      const aL = [0, 0], aR = [0, 0];
      aL[j] = 1; aR[j] = -1;
      const s = { id: nodi.length, padre: id, extra: n.extra.concat([{ a: aL, b: fl }]), ramo: { j, rel: "le", v: fl }, bound: r.z, stato: "aperto", x: null, z: null, prof: n.prof + 1 };
      const d = { id: nodi.length + 1, padre: id, extra: n.extra.concat([{ a: aR, b: -(fl + 1) }]), ramo: { j, rel: "ge", v: fl + 1 }, bound: r.z, stato: "aperto", x: null, z: null, prof: n.prof + 1 };
      nodi.push(s, d);
      n.figli = [s.id, d.id]; n.stato = "ramificato";
      if (visita === "best") aperti.push(s.id, d.id); else aperti.push(d.id, s.id);
      foto({ tipo: "ramo", corrente: id, j, fl });
    }
    foto({ tipo: "fine" });
    // posizioni dell'albero finale: foglie in fila (prima il ramo <=), padre al centro dei figli
    let foglia = 0;
    const pos = {};
    const visitaAlbero = (id) => {
      const n = nodi[id];
      if (n.figli) { n.figli.forEach(visitaAlbero); pos[id] = (pos[n.figli[0]] + pos[n.figli[1]]) / 2; } else pos[id] = foglia++;
    };
    visitaAlbero(0);
    const prof = Math.max(...nodi.map((n) => n.prof));
    return { passi, nodi, pos, foglie: foglia, prof, LB, inc, V0 };
  };
  const tracciaDi = (st) => {
    const D = st.dati, chiave = st.chiave() + "|" + (D.visita || "dfs");
    if (!D.tr || D.trChiave !== chiave) { D.tr = tracciaBB(ESEMPI[st.chiave()], D.visita || "dfs"); D.trChiave = chiave; }
    return D.tr;
  };
  // il bound superiore globale al passo: il migliore fra i bound dei nodi aperti
  // (e del nodo appena risolto e non ancora deciso), mai sotto LB
  const ubDi = (E) => {
    let ub = null;
    const su = (q) => { if (q && (!ub || cmpQ(q, ub) > 0)) ub = q; };
    for (const id of E.aperti) su(E.nodi[id].bound);
    if (E.tipo === "risolto") su(E.nodi[E.corrente].z);
    if (E.LB && (!ub || cmpQ(E.LB, ub) > 0)) ub = E.LB;
    return ub;
  };
  const ramoTex = (r) => `x_${r.j + 1} ${r.rel === "le" ? "\\le" : "\\ge"} ${r.v}`;
  const ramoTxt = (r) => `x${SUB[r.j]} ${r.rel === "le" ? "≤" : "≥"} ${r.v}`;
  // i vincoli di ramo del nodo id (dalla radice)
  const ramiDi = (nodi, id) => {
    const out = [];
    for (let n = nodi[id]; n && n.ramo; n = nodi[n.padre]) out.unshift(n.ramo);
    return out;
  };
  const scegliVisita = (st) => {
    const pan = M.pannello(st);
    let box = pan.querySelector(".mip-visita");
    if (box) box.remove();
    box = GI.h("div", { class: "mip-visita" }, `<strong>${T("Visita dei nodi", "Node selection")}</strong>`);
    const chips = GI.h("div", { class: "gi-chips" });
    for (const [k, testo, titolo] of [
      ["dfs", T("in profondità", "depth-first"), T("prima il ramo ≤, poi si risale", "the ≤ branch first, then backtrack")],
      ["best", T("miglior bound", "best bound"), T("il nodo aperto con il bound più alto", "the open node with the highest bound")],
    ]) {
      const b = GI.h("button", { class: "gi-chip", "aria-pressed": String((st.dati.visita || "dfs") === k), title: titolo }, testo);
      b.onclick = () => {
        M.ferma(st);
        st.dati.visita = k;
        chips.querySelectorAll(".gi-chip").forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
        st.imposta("k", 0);
      };
      chips.append(b);
    }
    box.append(chips);
    const prima = pan.querySelector(".gi-ctrl");
    if (prima) prima.before(box); else pan.append(box);
  };

  // per le verifiche (python/bb.py della prova confronta questi numeri)
  window.GI_MIP_A = { ESEMPI, risolvi, tracciaBB };

  window.GI_RICETTE["branch-bound"] = {
    titolo: T("Branch-and-bound passo passo", "Branch-and-bound step by step"),
    funzioni: VOCI(),
    etichettaFunzioni: T("Problema", "Problem"),
    parametri: [{ k: "k", nome: "k", min: 0, max: 24, step: 1, val: 0, colore: "a", cifre: 0,
      descr: T("passo: ◀ ▶ un passo alla volta, «Esegui» per vederli tutti", "step: ◀ ▶ one step at a time, «Run» to watch all of them") }],
    assi: false,
    // la board lavora in pixel e si ridisegna quando cambia dimensione (seguiDimensioni)
    opzioniBoard: ADATTA,
    vista: [0, 1, 1, 0],
    legenda: (st) => {
      const C = M.COL(st);
      return [
        [C.rosso, T("rilassamento del nodo", "relaxation of the node"), "pieno"],
        [C.viola, T("vincoli di ramo", "branching constraints"), "dashed"],
        [C.blu, T("\\(\\tilde{\\boldsymbol x}\\) del nodo / nodo ramificato", "node's \\(\\tilde{\\boldsymbol x}\\) / branched node"), "punto"],
        [C.verde, T("incumbent \\(\\bar{\\boldsymbol x}\\) / nodo intero", "incumbent \\(\\bar{\\boldsymbol x}\\) / integer node"), "punto"],
        [C.grigio, T("nodo potato", "pruned node"), "pieno"],
        [st.colore("a"), T("nodo corrente", "current node"), ""],
      ];
    },
    monta(board, st) {
      scegliVisita(st);
      M.comandi(st, []);
      lettureDopo(st, st.dati.comandi);
      seguiDimensioni(board, st);
    },
    aggiorna(board, st) {
      const tr = tracciaDi(st), k = M.passoK(st, tr.passi.length - 1), E = tr.passi[k], C = M.COL(st);
      const el = board.containerObj;
      // su telefono poliedro e albero stanno uno sopra l'altro: serve una board più alta
      // di quella che il motore dà (300 px); il ResizeObserver richiama poi aggiorna
      if (window.innerWidth < 860 && el.clientHeight < 560) { el.style.height = Math.round(Math.min(680, Math.max(560, window.innerHeight * 0.75))) + "px"; }
      const [W, H] = misura(board);
      board.setBoundingBox([0, H, W, 0], false);
      M.ridisegna(board, st, [st.dati.trChiave, k, W, H, M.scuro()].join("|"), (crea) => {
        // ---- le due zone: poliedro e albero (affiancati, o uno sopra l'altro se la board è stretta)
        const largo = W >= 1.15 * H, pad = 12;
        const zp = largo ? [0, 0, W * 0.47, H] : [0, H * 0.5, W, H];
        const za = largo ? [W * 0.47, 0, W, H] : [0, 0, W, H * 0.5];
        // ---- il poliedro, in scala
        const P0 = M.poligono(tr.V0, 1e3);
        const X = Math.ceil(Math.max(3, ...P0.map((q) => q[0]))), Y = Math.ceil(Math.max(3, ...P0.map((q) => q[1])));
        const x0 = -0.7, x1 = X + 0.7, y0 = -0.7, y1 = Y + 0.7;
        const s = Math.min((zp[2] - zp[0] - 2 * pad) / (x1 - x0), (zp[3] - zp[1] - 2 * pad) / (y1 - y0));
        const ox = (zp[0] + zp[2]) / 2 - (s * (x0 + x1)) / 2, oy = (zp[1] + zp[3]) / 2 - (s * (y0 + y1)) / 2;
        const px = (x, y) => [ox + s * x, oy + s * y];
        const curva = (pts, attr) => crea("curve", [pts.map((q) => px(...q)[0]), pts.map((q) => px(...q)[1])],
          Object.assign({ fixed: true, highlight: false, strokeWidth: 1 }, attr));
        const regione = (V, attr) => { const R = M.poligono(V, 1e3); if (R.length) curva(R.concat([R[0]]), attr); return R; };
        const retta = (a, b, attr) => { const sg = segmento(a, b, x0, x1, y0, y1); if (sg) curva(sg, attr); };
        // griglia, assi, numeri
        const fs = Math.max(10, Math.min(13, s * 0.4));
        const ogni = s < 22 ? 2 : 1;
        for (let i = 1; i <= X; i++) curva([[i, y0], [i, y1]], { strokeColor: C.line, strokeWidth: 1 });
        for (let j = 1; j <= Y; j++) curva([[x0, j], [x1, j]], { strokeColor: C.line, strokeWidth: 1 });
        crea("arrow", [px(x0, 0), px(x1, 0)], { strokeColor: C.muted, strokeWidth: 1.2, fixed: true, highlight: false, lastArrow: { type: 2, size: 4 } });
        crea("arrow", [px(0, y0), px(0, y1)], { strokeColor: C.muted, strokeWidth: 1.2, fixed: true, highlight: false, lastArrow: { type: 2, size: 4 } });
        for (let i = ogni; i <= X; i += ogni) M.scritta(crea, ...px(i, -0.32), i, { fontSize: fs, strokeColor: C.muted });
        for (let j = ogni; j <= Y; j += ogni) M.scritta(crea, ...px(-0.32, j), j, { fontSize: fs, strokeColor: C.muted });
        M.scritta(crea, ...px(x1 - 0.15, 0.35), "x₁", { fontSize: fs + 1, strokeColor: C.muted, anchorX: "right" });
        M.scritta(crea, ...px(0.3, y1 - 0.2), "x₂", { fontSize: fs + 1, strokeColor: C.muted, anchorX: "left" });
        // il poliedro di partenza (grigio) e le rette dei vincoli
        for (const v of tr.V0) if (v.a[0] > 0 || v.a[1] > 0 || v.b !== 0) retta(v.a, v.b, { strokeColor: C.grigio, strokeWidth: 1.2, dash: 2 });
        regione(tr.V0, { strokeColor: C.grigio, strokeWidth: 1.5, fillColor: C.grigio, fillOpacity: E.tipo === "fine" ? 0 : 0.1 });
        // il nodo corrente: la sua regione (al passo di ramificazione, quelle dei due figli)
        const nc = E.corrente !== null ? E.nodi[E.corrente] : null;
        const RS = { strokeColor: C.rosso, strokeWidth: 2, fillColor: C.rosso, fillOpacity: 0.22 };
        if (E.tipo === "fine") regione(tr.V0, Object.assign({}, RS, { fillOpacity: 0.12 }));
        else if (E.tipo === "inizio") regione(tr.V0, Object.assign({}, RS, { fillOpacity: 0.12, dash: 2 }));
        else if (E.tipo === "ramo") {
          regione(tr.V0.concat(nc.extra), { strokeColor: C.rosso, strokeWidth: 1.5, dash: 2, fillColor: "none", fillOpacity: 0 });
          for (const f of nc.figli) regione(tr.V0.concat(E.nodi[f].extra), RS);
          const sp = E.nodi[nc.figli[0]].extra.slice(-1)[0], dp = E.nodi[nc.figli[1]].extra.slice(-1)[0];
          retta(sp.a, sp.b, { strokeColor: C.viola, strokeWidth: 2, dash: 2 });
          retta(dp.a, dp.b, { strokeColor: C.viola, strokeWidth: 2, dash: 2 });
        } else if (nc) regione(tr.V0.concat(nc.extra), RS);
        if (nc) for (const v of nc.extra) retta(v.a, v.b, { strokeColor: C.viola, strokeWidth: 2, dash: 2 });
        // i punti interi ammissibili
        for (const q of M.puntiInteri(tr.V0, 0, X, 0, Y)) crea("circle", [px(...q), Math.max(2.5, s * 0.07)], {
          fixed: true, highlight: false, strokeColor: C.verde, fillColor: C.verde, fillOpacity: 1, strokeWidth: 1 });
        // incumbent e ottimo del rilassamento del nodo
        if (E.inc) crea("circle", [px(Qv(E.inc[0]), Qv(E.inc[1])), Math.max(7, s * 0.2)], {
          fixed: true, highlight: false, strokeColor: C.verde, strokeWidth: 3, fillColor: C.verde, fillOpacity: E.tipo === "fine" ? 0.5 : 0.15 });
        if (nc && nc.x && E.tipo !== "fine") crea("circle", [px(Qv(nc.x[0]), Qv(nc.x[1])), Math.max(4, s * 0.12)], {
          fixed: true, highlight: false, strokeColor: C.blu, fillColor: C.blu, fillOpacity: 1, strokeWidth: 1 });

        // ---- l'albero
        const L = tr.foglie, Dp = Math.max(1, tr.prof);
        const tw = za[2] - za[0] - 2 * pad, th = za[3] - za[1] - 2 * pad - 14;
        const dx = tw / L, dy = th / (Dp + 0.45);
        const r = Math.max(10, Math.min(19, dx * 0.32, dy * 0.3));
        const fsT = Math.max(11, Math.min(15, r * 0.95)), stretto = dx < 95;
        const pos = (id) => [za[0] + pad + (tr.pos[id] + 0.5) * dx, za[3] - pad - r - 4 - E.nodi[id].prof * dy];
        const visibili = E.nodi.map((n) => n.id);
        // i rami, con il vincolo aggiunto
        for (const id of visibili) {
          const n = E.nodi[id];
          if (n.padre === null) continue;
          const [xa, ya] = pos(n.padre), [xb, yb] = pos(id);
          M.linea(crea, xa, ya - r, xb, yb + r, { strokeColor: C.muted, strokeWidth: 1.5 });
          const sx = n.ramo.rel === "le" ? -1 : 1;
          M.scritta(crea, (xa + xb) / 2 + sx * 5, (ya + yb) / 2 + 3, ramoTxt(n.ramo), {
            fontSize: fsT - 1, strokeColor: C.viola, anchorX: sx < 0 ? "right" : "left" });
        }
        // i nodi
        const stile = {
          aperto: { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0, dash: 2 },
          corrente: { strokeColor: st.colore("a"), fillColor: st.colore("a"), fillOpacity: 0.2 },
          ramificato: { strokeColor: C.blu, fillColor: C.blu, fillOpacity: 0.22 },
          intero: { strokeColor: C.verde, fillColor: C.verde, fillOpacity: 0.55 },
          bound: { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0.45 },
          inamm: { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0.45 },
        };
        for (const id of visibili) {
          const n = E.nodi[id], [x, y] = pos(id);
          if (id === E.corrente) crea("circle", [[x, y], r + 4], { fixed: true, highlight: false, strokeColor: st.colore("a"), strokeWidth: 3, fillOpacity: 0 });
          crea("circle", [[x, y], r], Object.assign({ fixed: true, highlight: false, strokeWidth: 2 }, stile[n.stato]));
          M.scritta(crea, x, y, id, { fontSize: fsT, strokeColor: C.testo, cssStyle: "font-weight:700" });
          // a destra del nodo: z (o ∅) e, sotto, il motivo della potatura
          const z = n.stato === "inamm" ? "∅" : n.z ? (stretto ? "" : "z = ") + qt(n.z) : "";
          const perche = { inamm: T("inamm.", "infeas."), bound: "≤ LB", intero: T("intero", "integer") }[n.stato] || "";
          const colT = n.stato === "intero" ? C.verde : C.muted;
          if (z) M.scritta(crea, x + r + 7, perche ? y + fsT * 0.55 : y, z, { fontSize: fsT - 1, strokeColor: colT, anchorX: "left" });
          if (perche) M.scritta(crea, x + r + 7, y - fsT * 0.6, perche, { fontSize: fsT - 2, strokeColor: colT, anchorX: "left" });
        }
      });
    },
    formula(p, st) {
      const E = ESEMPI[st.chiave()];
      return problemaTex(lin(E.c), vincoliTex(E.V));
    },
    letture(p, st) {
      const tr = tracciaDi(st), k = M.passoK(st, tr.passi.length - 1), E = tr.passi[k], C = M.COL(st);
      const n = E.corrente !== null ? E.nodi[E.corrente] : null;
      const righe = [`<strong>${T("Passo", "Step")} ${k}/${tr.passi.length - 1}</strong>` + (n ? T(` · nodo ${n.id}`, ` · node ${n.id}`) : "")];
      if (n) {
        const rami = ramiDi(E.nodi, n.id);
        righe.push(rami.length ? T("Vincoli di ramo: ", "Branching constraints: ") + `\\(${rami.map(ramoTex).join(",\\ ")}\\)` : T("Il nodo radice: il rilassamento continuo del problema.", "The root node: the continuous relaxation of the problem."));
      }
      const xt = n && n.x ? `\\(\\tilde{\\boldsymbol x} = ${coppiaQ(n.x)}\\), \\(z = ${Qtex(n.z)}\\)` : "";
      const lbTex = () => (E.LB ? Qtex(E.LB) : "-\\infty");
      switch (E.tipo) {
        case "inizio":
          righe.push(T("Si parte dal nodo \\(0\\), il problema intero di partenza: è l'unico nodo aperto e non c'è ancora una soluzione intera.",
            "We start from node \\(0\\), the original integer problem: it is the only open node and there is no integer solution yet."));
          break;
        case "inamm":
          righe.push(T(`Il rilassamento è ${tinta(C.rosso, "vuoto")}: i vincoli di ramo tagliano via tutto il poliedro. Nodo ${tinta(C.muted, "potato per inammissibilità")}.`,
            `The relaxation is ${tinta(C.rosso, "empty")}: the branching constraints cut away the whole polyhedron. Node ${tinta(C.muted, "pruned by infeasibility")}.`));
          break;
        case "risolto":
          righe.push(T(`Rilassamento del nodo: ${tinta(C.blu, "ottimo")} ${xt}.`, `Relaxation of the node: ${tinta(C.blu, "optimum")} ${xt}.`));
          break;
        case "bound":
          righe.push(T(`${xt}: \\(z = ${Qtex(n.z)} \\le \\lb = ${lbTex()}\\), nessuna soluzione del nodo batte l'incumbent. Nodo ${tinta(C.muted, "potato per bound")}.`,
            `${xt}: \\(z = ${Qtex(n.z)} \\le \\lb = ${lbTex()}\\), no solution of the node beats the incumbent. Node ${tinta(C.muted, "pruned by bound")}.`));
          break;
        case "intero":
          righe.push(T(`${xt}: \\(\\tilde{\\boldsymbol x}\\) è ${tinta(C.verde, "intero")}, quindi ammissibile, e migliora l'incumbent: \\(\\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\). Nodo potato per interezza.`,
            `${xt}: \\(\\tilde{\\boldsymbol x}\\) is ${tinta(C.verde, "integer")}, hence feasible, and it improves the incumbent: \\(\\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\). Node pruned by integrality.`));
          break;
        case "ramo": {
          const v = n.x[E.j], j = E.j + 1, fl = E.fl;
          righe.push(T(`${xt}. \\(\\tilde x_${j} = ${Qtex(v)}\\) è frazionaria: ${tinta(C.blu, "si ramifica")} con \\(x_${j} \\le \\lfloor ${Qtex(v)} \\rfloor = ${fl}\\) (nodo ${n.figli[0]}) e \\(x_${j} \\ge \\lceil ${Qtex(v)} \\rceil = ${fl + 1}\\) (nodo ${n.figli[1]}). La striscia \\(${fl} < x_${j} < ${fl + 1}\\) non contiene punti interi.`,
            `${xt}. \\(\\tilde x_${j} = ${Qtex(v)}\\) is fractional: ${tinta(C.blu, "we branch")} with \\(x_${j} \\le \\lfloor ${Qtex(v)} \\rfloor = ${fl}\\) (node ${n.figli[0]}) and \\(x_${j} \\ge \\lceil ${Qtex(v)} \\rceil = ${fl + 1}\\) (node ${n.figli[1]}). The strip \\(${fl} < x_${j} < ${fl + 1}\\) contains no integer point.`));
          break;
        }
        case "fine":
          righe.push(T(`Nessun nodo aperto: l'incumbent è ottimo, \\(\\boldsymbol x^* = \\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\), \\(\\zmilp = ${Qtex(E.LB)}\\). Nodi: ${E.nodi.length}; alla radice \\(\\zlp = ${Qtex(E.nodi[0].z)}\\).`,
            `No open node left: the incumbent is optimal, \\(\\boldsymbol x^* = \\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\), \\(\\zmilp = ${Qtex(E.LB)}\\). Nodes: ${E.nodi.length}; at the root \\(\\zlp = ${Qtex(E.nodi[0].z)}\\).`));
          break;
      }
      const ub = ubDi(E);
      righe.push(`\\(\\lb = ${lbTex()} \\le \\zmilp \\le \\ub = ${ub ? Qtex(ub) : "+\\infty"}\\)` +
        (E.inc && E.tipo !== "fine" ? T(` · incumbent \\(\\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\)`, ` · incumbent \\(\\bar{\\boldsymbol x} = ${coppiaQ(E.inc)}\\)`) : ""));
      righe.push(T("Nodi aperti: ", "Open nodes: ") + (E.aperti.length ? E.aperti.slice().sort((a, b) => a - b).join(", ") : "—"));
      righe.push(`<small>${T("Si ramifica sulla prima variabile frazionaria; si pota per bound quando \\(z \\le \\lb\\).", "We branch on the first fractional variable; a node is pruned by bound when \\(z \\le \\lb\\).")}</small>`);
      return righe.join("<br>");
    },
    domanda: T("Nell'esempio 4 esegui la visita in profondità e poi quella per miglior bound: quanti nodi servono in ciascun caso? Quando si trova l'ottimo, e da quel momento quanti nodi si potano per bound? Segui \\(\\lb\\) e \\(\\ub\\): quando si incontrano?",
      "In example 4 run the depth-first search and then the best-bound search: how many nodes does each need? When is the optimum found, and from then on how many nodes are pruned by bound? Follow \\(\\lb\\) and \\(\\ub\\): when do they meet?"),
  };
})();
