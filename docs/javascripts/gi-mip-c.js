/* Laboratorio di «Modellazione MIP / MIP Modelling»: ricette dei capitoli 5 e 6
 * (Logica e variabili binarie; Legami fra variabili).
 *
 *   big-m         un vincolo acceso e spento da una binaria y con il big-M: il
 *                 rilassamento continuo (proiettato sul piano delle x, oppure nel
 *                 piano (y, x)) al variare di M, l'insieme ammissibile del MILP, il
 *                 suo involucro convesso, il valore minimo valido di M e i due
 *                 valori z(LP+) e z(MILP). Tre esempi: disgiunzione «x1 <= 2 oppure
 *                 x2 <= 2», attivazione x <= M y, disgiunzione con due M diversi.
 *   formulazioni  lo stesso insieme S di punti interi descritto da una formulazione
 *                 debole A e da una forte B (X_B ⊆ X_A), con conv(S); gli ottimi dei
 *                 due rilassamenti per la stessa direzione c (ruotabile con ▶), i
 *                 bound, le aree. Tre esempi: attivazione aggregata / disaggregata
 *                 (proiezione su (y, x1)), dividere per il coefficiente e
 *                 arrotondare, un taglio valido che non basta per arrivare a conv(S).
 *
 * Tutti i conti sono esatti (frazioni di GI_MIP: lp2, verticiEsatti); verificati
 * con uno script Python indipendente (vertici in Fraction) nella prova della fase 2.
 * Il piano non ha per forza la stessa unità sui due assi (nel piano (y, x) la y va
 * da 0 a 1): la vista si adatta alla board con fattore di scala fisso per esempio
 * (inquadra) e la freccia di c è disegnata ortogonale alle rette di livello sullo
 * schermo.
 */
(function () {
  "use strict";
  const GI = window.GI, M = window.GI_MIP;
  const T = GI.T;
  const { Q, Qv, Qtex, Qsub, Qmul, Qadd, coppiaQ, lin, lp2, poligono, involucro, verticiEsatti, puntiInteri } = M;
  window.GI_RICETTE = window.GI_RICETTE || {};

  // ------------------------------------------------------------ helper locali
  /** 16 direzioni intere della funzione obiettivo, in ordine di angolo */
  const DIR = [[1, 0], [2, 1], [1, 1], [1, 2], [0, 1], [-1, 2], [-1, 1], [-2, 1],
    [-1, 0], [-2, -1], [-1, -1], [-1, -2], [0, -1], [1, -2], [1, -1], [2, -1]];
  const dirDi = (st) => DIR[((Math.round(st.p().d) % 16) + 16) % 16];

  /** vista del riquadro box = [x0, x1, y0, y1] adattata alla board, con unità
   *  orizzontale = r volte quella verticale; restituisce le unità in pixel */
  function inquadra(board, box, r) {
    const cont = board.containerObj;
    if (cont && cont.clientWidth > 0 && cont.clientHeight > 0 &&
      (Math.abs(cont.clientWidth - board.canvasWidth) > 1 || Math.abs(cont.clientHeight - board.canvasHeight) > 1)) {
      board.resizeContainer(cont.clientWidth, cont.clientHeight, true, true);
    }
    const W = board.canvasWidth || 600, H = board.canvasHeight || 400;
    const [x0, x1, y0, y1] = box;
    const uy = Math.min(W / (r * (x1 - x0)), H / (y1 - y0)), ux = r * uy;
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const bb = [cx - W / ux / 2, cy + H / uy / 2, cx + W / ux / 2, cy - H / uy / 2];
    const old = board.getBoundingBox();
    if (old.some((v, i) => Math.abs(v - bb[i]) > 1e-9 * (1 + Math.abs(v)))) board.setBoundingBox(bb, false);
    return { ux, uy, W, H };
  }
  /** la vista di partenza (prima che la board abbia le sue misure) */
  const vistaIniziale = (box) => [box[0], box[3], box[1], box[2]];

  /** la board si ridimensiona dopo il montaggio (app a tutta pagina): si rifà la vista */
  function seguiMisure(st) {
    const D = st.dati, el = st.el.querySelector(".gi-board");
    if (!el || D.ro || !window.ResizeObserver) return;
    D.ro = new ResizeObserver(() => {
      clearTimeout(D.roT);
      D.roT = setTimeout(() => { if (document.body.contains(st.el)) st.aggiorna(); else D.ro.disconnect(); }, 120);
    });
    D.ro.observe(el);
  }

  /** valori iniziali dell'esempio, applicati al primo montaggio, al cambio di
   *  esempio e con «Azzera» (non al cambio di tema) */
  function applicaIniziali(st, E, rangeM) {
    const D = st.dati, tema = M.scuro();
    const cambioTema = D.tema !== undefined && D.tema !== tema && D.chiave === st.chiave();
    D.tema = tema;
    if (cambioTema) return;
    D.chiave = st.chiave();
    if (rangeM) {
      const iM = M.inputDi(st, "M");
      if (iM) { iM.min = rangeM[0]; iM.max = rangeM[1]; iM.value = E.Mdef; }
    }
    const iD = M.inputDi(st, "d");
    if (iD) iD.value = E.ddef;
  }

  /** freccia di c dal punto P, ortogonale alle rette di livello sullo schermo */
  function frecciaC(crea, P, c, U, colore) {
    let sx = c[0] / U.ux, sy = c[1] / U.uy;
    const n = Math.hypot(sx, sy) || 1, L = Math.max(42, Math.min(80, 0.11 * Math.min(U.W, U.H)));
    sx = (sx / n) * L; sy = (sy / n) * L;
    return crea("arrow", [[P[0], P[1]], [P[0] + sx / U.ux, P[1] + sy / U.uy]],
      { strokeColor: colore, strokeWidth: 3, fixed: true, highlight: false, lastArrow: { type: 2, size: 6 } });
  }
  /** retta di livello c'x = z tratteggiata */
  const livello = (crea, c, z, colore) =>
    crea("line", [-z, c[0], c[1]], { strokeColor: colore, strokeWidth: 1.6, dash: 2, fixed: true, highlight: false, withLabel: false });
  /** nomi degli assi, piccoli, in fondo agli assi */
  function nomiAssi(crea, board, nomi, C) {
    const [x0, y1, x1, y0] = board.getBoundingBox();
    const dx = (x1 - x0) * 0.012, dy = (y1 - y0) * 0.03;
    M.scritta(crea, x1 - dx, dy, nomi[0], { anchorX: "right", anchorY: "bottom", fontSize: 15, strokeColor: C.muted });
    M.scritta(crea, dx, y1 - dy * 0.6, nomi[1], { anchorX: "left", anchorY: "top", fontSize: 15, strokeColor: C.muted });
  }
  /** valore di c'x in frazione */
  const valQ = (c, x) => Qadd(Qmul(Q(c[0]), x[0]), Qmul(Q(c[1]), x[1]));
  /** area esatta di un poligono convesso dai vertici esatti */
  function areaQ(vs) {
    if (vs.length < 3) return Q(0);
    const cx = vs.reduce((s, v) => s + Qv(v[0]), 0) / vs.length, cy = vs.reduce((s, v) => s + Qv(v[1]), 0) / vs.length;
    const P = vs.slice().sort((u, w) => Math.atan2(Qv(u[1]) - cy, Qv(u[0]) - cx) - Math.atan2(Qv(w[1]) - cy, Qv(w[0]) - cx));
    let s = Q(0);
    for (let i = 0; i < P.length; i++) {
      const a = P[i], b = P[(i + 1) % P.length];
      s = Qadd(s, Qsub(Qmul(a[0], b[1]), Qmul(a[1], b[0])));
    }
    return Q(Math.abs(s.n), 2 * s.d);
  }
  const num = (q) => Qtex(q) + (q.d === 1 ? "" : "\\approx " + GI.num(Qv(q), 2));
  const tx = (s) => `\\(${s}\\)`;
  const areaTex = (q) => (q.d === 1 ? String(q.n) : (q.d <= 6 ? Qtex(q) + "\\approx " : "\\approx ") + GI.num(Qv(q), 2));

  // ================================================================
  // 1. Big-M (cap. 5; tecnica 6.8 del cap. 6)
  // ================================================================
  // tipo "disg": y = 1 accende x1 <= b1, y = 0 accende x2 <= b2, con 0 <= x <= U:
  //   x1 <= b1 + M(1 - y),  x2 <= b2 + M y.
  //   Proiezione del rilassamento sul piano (x1, x2) (Fourier-Motzkin su y in [0, 1]):
  //   x1 <= b1 + M,  x2 <= b2 + M,  x1 + x2 <= b1 + b2 + M.
  // tipo "att": piano (y, x), 0 <= x <= U, x <= M y (se y = 0 allora x = 0).
  const BIGM = {
    disg: {
      etichetta: T("\\(x_1 \\le 2\\) oppure \\(x_2 \\le 2\\)", "\\(x_1 \\le 2\\) or \\(x_2 \\le 2\\)"),
      tipo: "disg", b: [2, 2], U: [5, 5], Mrange: [0, 10], Mdef: 5, ddef: 2,
    },
    att: {
      etichetta: "\\(x \\le M y\\)",
      tipo: "att", U: 4, Mrange: [0, 20], Mdef: 10, ddef: 7,
    },
    due: {
      etichetta: T("\\(x_1 \\le 1\\) oppure \\(x_2 \\le 3\\)", "\\(x_1 \\le 1\\) or \\(x_2 \\le 3\\)"),
      tipo: "disg", b: [1, 3], U: [5, 4], Mrange: [0, 10], Mdef: 6, ddef: 3,
    },
  };
  const Mmin = (E) => (E.tipo === "att" ? E.U : Math.max(E.U[0] - E.b[0], E.U[1] - E.b[1]));
  function relaxBM(E, m) {
    if (E.tipo === "att") return [{ a: [1, 0], b: 1 }, { a: [0, 1], b: E.U }, { a: [-m, 1], b: 0 }, ...M.nonneg()];
    const [b1, b2] = E.b, [U1, U2] = E.U;
    return [{ a: [1, 0], b: U1 }, { a: [0, 1], b: U2 }, { a: [1, 0], b: b1 + m }, { a: [0, 1], b: b2 + m },
      { a: [1, 1], b: b1 + b2 + m }, ...M.nonneg()];
  }
  /** i due rami y = 0 e y = 1 del modello con questo M (vincoli nel piano del disegno) */
  function ramiBM(E, m) {
    if (E.tipo === "att") {
      const base = [{ a: [0, 1], b: E.U }, ...M.nonneg()];
      return [
        { y: 0, V: [...base, { a: [1, 0], b: 0 }, { a: [0, 1], b: 0 }] },
        { y: 1, V: [...base, { a: [1, 0], b: 1 }, { a: [-1, 0], b: -1 }, { a: [0, 1], b: m }] },
      ];
    }
    const [b1, b2] = E.b, [U1, U2] = E.U, box = [{ a: [1, 0], b: U1 }, { a: [0, 1], b: U2 }, ...M.nonneg()];
    return [
      { y: 0, V: [...box, { a: [1, 0], b: b1 + m }, { a: [0, 1], b: b2 }] },
      { y: 1, V: [...box, { a: [1, 0], b: b1 }, { a: [0, 1], b: b2 + m }] },
    ];
  }
  /** ottimo del MILP con questo M: il migliore dei due rami */
  function milpBM(E, m, c) {
    let best = null;
    for (const R of ramiBM(E, m)) {
      const r = lp2(R.V, c, "max");
      if (r.stato === "ottimo" && (!best || Qv(r.z) > Qv(best.z) + 1e-12)) best = Object.assign({ y: R.y }, r);
    }
    return best;
  }
  /** l'insieme ammissibile del MILP (y binaria) come forme da disegnare */
  function formeBM(E, m) {
    if (E.tipo === "att") {
      const h = Math.max(0, Math.min(E.U, m));
      return [{ punto: [0, 0] }, h > 0 ? { P: [[1, 0], [1, h]] } : { punto: [1, 0] }];
    }
    const [b1, b2] = E.b, [U1, U2] = E.U;
    const a1 = Math.min(b1, U1), h1 = Math.min(U2, b2 + m), w0 = Math.min(U1, b1 + m), h0 = Math.min(b2, U2);
    return [{ P: [[0, 0], [w0, 0], [w0, h0], [a1, h0], [a1, h1], [0, h1]] }];
  }
  const boxBM = (E) => (E.tipo === "att" ? [-0.3, 1.35, -0.5, E.U + 0.6] : [-0.6, E.U[0] + 0.8, -0.5, E.U[1] + 0.7]);
  const rBM = (E) => (E.tipo === "att" ? 3.2 : 1);
  const nomiBM = (E) => (E.tipo === "att" ? ["y", "x"] : ["x₁", "x₂"]);
  const varsBM = (E) => (E.tipo === "att" ? ["y", "x"] : ["x_1", "x_2"]);
  /** i vincoli condizionati in TeX, con M come simbolo o come numero */
  function vincoliBM(E, Mt) {
    if (E.tipo === "att") return `x \\le ${Mt}\\,y`;
    const [b1, b2] = E.b;
    return `x_1 \\le ${b1} + ${Mt}(1-y),\\ \\ x_2 \\le ${b2} + ${Mt}\\,y`;
  }
  const domTex = (E) => (E.tipo === "att" ? `0 \\le x \\le ${E.U},\\ y \\in \\{0,1\\}`
    : `0 \\le x_1 \\le ${E.U[0]},\\ 0 \\le x_2 \\le ${E.U[1]},\\ y \\in \\{0,1\\}`);

  function analisiBM(st) {
    const E = BIGM[st.chiave()], m = Math.round(st.p().M), c = dirDi(st), mm = Mmin(E);
    const D = st.dati, firma = [st.chiave(), m, c.join(",")].join("|");
    if (D.anBM && D.anBM.firma === firma) return D.anBM;
    const lp = lp2(relaxBM(E, m), c, "max");
    const ip = milpBM(E, m, c), vero = milpBM(E, mm, c), lpMin = lp2(relaxBM(E, mm), c, "max");
    D.anBM = { firma, E, m, c, mm, lp, ip, vero, lpMin };
    return D.anBM;
  }
  /** il valore (o l'intervallo) di y nel punto ottimo del rilassamento */
  function yTilde(A) {
    const { E, m, lp } = A;
    if (lp.stato !== "ottimo") return "";
    if (E.tipo === "att") return `\\tilde y = ${Qtex(lp.x[0])}`;
    if (m === 0) return `\\tilde y \\in [0, 1]`;
    const lo0 = Qmul(Qsub(lp.x[1], Q(E.b[1])), Q(1, m)), hi0 = Qsub(Q(1), Qmul(Qsub(lp.x[0], Q(E.b[0])), Q(1, m)));
    const lo = Qv(lo0) > 0 ? lo0 : Q(0), hi = Qv(hi0) < 1 ? hi0 : Q(1);
    return Qv(hi) - Qv(lo) < 1e-12 ? `\\tilde y = ${Qtex(lo)}` : `\\tilde y \\in \\big[${Qtex(lo)}${GI.EN ? ",\\ " : ";\\ "}${Qtex(hi)}\\big]`;
  }

  window.GI_RICETTE["big-m"] = {
    titolo: T("Big-M e rilassamento", "Big-M and relaxation"),
    funzioni: BIGM,
    etichettaFunzioni: T("Vincolo condizionato", "Conditional constraint"),
    parametri: [
      { k: "M", nome: "M", min: 0, max: 10, step: 1, val: 5, colore: "a", cifre: 0,
        descr: T("▶ fa crescere \\(M\\) di 1 ogni 0,9 s", "▶ increases \\(M\\) by 1 every 0.9 s") },
      { k: "d", nome: "d", min: 0, max: 15, step: 1, val: 2, colore: "b", cifre: 0,
        descr: T("direzione di \\(\\boldsymbol c\\) (16 in tutto): ▶ la fa ruotare", "direction of \\(\\boldsymbol c\\) (16 in all): ▶ rotates it") },
    ],
    vista: (k) => vistaIniziale(boxBM(BIGM[k])),
    stessaScala: false,
    legenda: (st) => {
      const C = M.COL(st);
      return [
        [C.rosso, T("rilassamento continuo (\\(0 \\le y \\le 1\\))", "continuous relaxation (\\(0 \\le y \\le 1\\))"), "pieno"],
        [C.verde, T("ammissibili del MILP (\\(y \\in \\{0,1\\}\\))", "MILP feasible set (\\(y \\in \\{0,1\\}\\))"), "pieno"],
        [C.viola, T("involucro convesso", "convex hull"), "dashed"],
        [C.grigio, T("tagliato da un \\(M\\) troppo piccolo", "cut off by a too small \\(M\\)"), "dashed"],
        [C.rosso, T("ottimo del rilassamento", "relaxation optimum"), "punto"],
        [C.blu, T("ottimo del MILP", "MILP optimum"), "punto"],
        [st.colore("b"), "\\(\\boldsymbol c\\)", ""],
      ];
    },
    monta(board, st) {
      const E = BIGM[st.chiave()];
      applicaIniziali(st, E, E.Mrange);
      st.dati.anBM = null;
      seguiMisure(st);
    },
    aggiorna(board, st) {
      const A = analisiBM(st), E = A.E, C = M.COL(st);
      const U = inquadra(board, boxBM(E), rBM(E));
      M.ridisegna(board, st, [A.firma, M.scuro(), U.W, U.H].join("|"), (crea) => {
        // rilassamento
        const P = poligono(relaxBM(E, A.m));
        M.area(crea, P, { strokeColor: C.rosso, fillColor: C.rosso, fillOpacity: 0.16, strokeWidth: 2 });
        // insieme vero (con M valido) tratteggiato grigio se M non è valido
        if (A.m < A.mm) for (const f of formeBM(E, A.mm)) {
          if (f.P && f.P.length === 2) M.linea(crea, f.P[0][0], f.P[0][1], f.P[1][0], f.P[1][1], { strokeColor: C.grigio, strokeWidth: 6, dash: 2 });
          else if (f.P) M.area(crea, f.P, { strokeColor: C.grigio, fillColor: C.grigio, fillOpacity: 0.12, strokeWidth: 2, dash: 2 });
        }
        // ammissibili del MILP con questo M
        for (const f of formeBM(E, A.m)) {
          if (f.punto) M.pallino(crea, f.punto[0], f.punto[1], { size: 4, fillColor: C.verde, strokeColor: C.verde });
          else if (f.P.length === 2) M.linea(crea, f.P[0][0], f.P[0][1], f.P[1][0], f.P[1][1], { strokeColor: C.verde, strokeWidth: 6 });
          else M.area(crea, f.P, { strokeColor: C.verde, fillColor: C.verde, fillOpacity: 0.32, strokeWidth: 2.5 });
        }
        // involucro convesso dell'insieme vero
        const pts = [];
        for (const f of formeBM(E, A.mm)) { if (f.punto) pts.push(f.punto); else pts.push(...f.P); }
        M.area(crea, involucro(pts), { strokeColor: C.viola, fillColor: "none", fillOpacity: 0, strokeWidth: 2.2, dash: 2 });
        // rette di livello e ottimi
        if (A.lp.stato === "ottimo") livello(crea, A.c, Qv(A.lp.z), C.rosso);
        if (A.ip) livello(crea, A.c, Qv(A.ip.z), C.blu);
        frecciaC(crea, [0, 0], A.c, U, st.colore("b"));
        if (A.lp.stato === "ottimo") M.pallino(crea, Qv(A.lp.x[0]), Qv(A.lp.x[1]), { size: 6, fillColor: C.rosso, strokeColor: C.rosso });
        if (A.ip) M.pallino(crea, Qv(A.ip.x[0]), Qv(A.ip.x[1]), { size: 5, fillColor: C.blu, strokeColor: "#ffffff", strokeWidth: 1.5 });
        nomiAssi(crea, board, nomiBM(E), C);
      });
    },
    formula(p, st) {
      const A = analisiBM(st), E = A.E;
      return `\\max\\ ${lin(A.c, varsBM(E))}\\quad ${vincoliBM(E, st.col("a", String(A.m)))},\\ \\ ${domTex(E)}`;
    },
    letture(p, st) {
      const A = analisiBM(st), E = A.E, C = M.COL(st);
      const stato = A.m < A.mm
        ? M.tinta(C.rosso, T(`\\(M = ${A.m}\\) non è valido`, `\\(M = ${A.m}\\) is not valid`)) +
          T(": taglia soluzioni ammissibili (in grigio).", ": it cuts off feasible solutions (in grey).")
        : A.m === A.mm
          ? M.tinta(C.verde, T(`\\(M = ${A.m}\\) è il minimo valido`, `\\(M = ${A.m}\\) is the minimum valid value`)) +
            T(": il rilassamento più stretto.", ": the tightest relaxation.")
          : M.tinta(C.a, T(`\\(M = ${A.m}\\) è valido ma migliorabile`, `\\(M = ${A.m}\\) is valid but can be improved`)) +
            T(": stessi punti, rilassamento più largo.", ": same points, larger relaxation.");
      let spieg = "";
      // il valore minimo di M, calcolato dai dati
      if (E.tipo === "att") {
        spieg += T(`Con \\(y = 1\\), \\(x \\le M\\) non deve tagliare \\(x = ${E.U}\\): basta \\(M = ${E.U}\\).`,
          `With \\(y = 1\\), \\(x \\le M\\) must not cut \\(x = ${E.U}\\): \\(M = ${E.U}\\) is enough.`);
      } else {
        const [b1, b2] = E.b, [U1, U2] = E.U, m1 = U1 - b1, m2 = U2 - b2;
        spieg += T(`Spento, un vincolo non taglia il riquadro se \\(M \\ge \\max\\{${U1} - ${b1},\\ ${U2} - ${b2}\\} = ${A.mm}\\).`,
          `When off, a constraint does not cut the box if \\(M \\ge \\max\\{${U1} - ${b1},\\ ${U2} - ${b2}\\} = ${A.mm}\\).`);
        spieg += " " + T(`Rilassamento proiettato: \\(x_1 + x_2 \\le ${b1 + b2 + A.m}\\).`, `Projected relaxation: \\(x_1 + x_2 \\le ${b1 + b2 + A.m}\\).`);
        if (m1 !== m2) spieg += " " + T(
          `Con \\(M_1 = ${m1}\\) e \\(M_2 = ${m2}\\), uno per vincolo, sarebbe l'involucro.`,
          `With \\(M_1 = ${m1}\\) and \\(M_2 = ${m2}\\), one per constraint, it would be the hull.`);
      }
      const righe = [];
      if (A.lp.stato === "ottimo") righe.push([M.tinta(C.rosso, tx("\\zlpp")), tx(num(A.lp.z)), tx(coppiaQ(A.lp.x))]);
      if (A.ip) righe.push([M.tinta(C.blu, tx("\\zmilp")), tx(Qtex(A.ip.z)), tx(coppiaQ(A.ip.x))]);
      if (A.m < A.mm && A.vero) righe.push([T("ottimo vero", "true optimum"), tx(Qtex(A.vero.z)), tx(coppiaQ(A.vero.x))]);
      if (A.lpMin.stato === "ottimo" && A.m !== A.mm) righe.push([T(`\\(\\zlpp\\), \\(M = ${A.mm}\\)`, `\\(\\zlpp\\), \\(M = ${A.mm}\\)`), tx(num(A.lpMin.z)), ""]);
      let r = M.tab(["", T("valore", "value"), T("punto", "point")], righe);
      if (A.lp.stato === "ottimo" && A.ip) {
        const gap = Qsub(A.lp.z, A.ip.z);
        r += `<div style="margin-top:.3em">${tx(yTilde(A))}; ${T("divario", "gap")} \\(${num(gap)}\\)</div>`;
      }
      return r + `<div style="margin-top:.3em">${stato}</div><div style="margin-top:.3em">${spieg}</div>`;
    },
    domanda: T("Premi ▶ accanto a \\(M\\) partendo da \\(0\\): finché \\(M\\) è sotto il minimo, quali soluzioni spariscono e che cosa succede a \\(\\zmilp\\)? Al valore minimo, il rilassamento coincide con l'involucro convesso? Poi \\(\\zlpp\\) cresce: fino a quando? Nel terzo esempio, perché un solo \\(M\\) non basta per arrivare all'involucro?",
      "Press ▶ next to \\(M\\) starting from \\(0\\): while \\(M\\) is below the minimum, which solutions disappear and what happens to \\(\\zmilp\\)? At the minimum value, does the relaxation coincide with the convex hull? Then \\(\\zlpp\\) grows: up to when? In the third example, why is a single \\(M\\) not enough to reach the hull?"),
  };

  // ================================================================
  // 2. Formulazioni deboli e forti (cap. 6)
  // ================================================================
  // Ogni esempio: A (debole) e B (forte) con lo stesso insieme S di punti interi
  // (controllato a ogni montaggio per enumerazione), X_B ⊆ X_A.
  const FORM = {
    att: {
      etichetta: T("aggregata / disaggregata", "aggregated / disaggregated"),
      vars: ["y", "x_1"], nomi: ["y", "x₁"], box: [-0.3, 1.35, -0.3, 1.3], r: 1, ddef: 5,
      A: [{ a: [-3, 1], b: 0 }, { a: [1, 0], b: 1 }, { a: [0, 1], b: 1 }, ...M.nonneg()],
      B: [{ a: [-1, 1], b: 0 }, { a: [1, 0], b: 1 }, ...M.nonneg()],
      texA: ["x_1 \\le 3y", "y \\le 1,\\ x_1 \\le 1", "y,\\ x_1 \\ge 0"],
      texB: ["x_1 \\le y", "y \\le 1", "y,\\ x_1 \\ge 0"],
      nota: T("Attivazione con \\(n = 3\\) utenti vista sul piano \\((y, x_1)\\): A da \\(x_1 + x_2 + x_3 \\le 3y\\) (aggregata), B da \\(x_i \\le y\\) (disaggregata).",
        "Activation with \\(n = 3\\) users seen on the plane \\((y, x_1)\\): A from \\(x_1 + x_2 + x_3 \\le 3y\\) (aggregated), B from \\(x_i \\le y\\) (disaggregated)."),
    },
    mcd: {
      etichetta: T("dividere e arrotondare", "divide and round"),
      vars: ["x_1", "x_2"], nomi: ["x₁", "x₂"], box: [-0.6, 4.1, -0.6, 3.9], r: 1, ddef: 2,
      A: [{ a: [2, 4], b: 13 }, { a: [6, 3], b: 20 }, ...M.nonneg()],
      B: [{ a: [1, 2], b: 6 }, { a: [2, 1], b: 6 }, ...M.nonneg()],
      texA: ["2x_1 + 4x_2 \\le 13", "6x_1 + 3x_2 \\le 20", "x_1,\\ x_2 \\ge 0"],
      texB: ["x_1 + 2x_2 \\le 6", "2x_1 + x_2 \\le 6", "x_1,\\ x_2 \\ge 0"],
      nota: T("B divide ogni vincolo di A per il MCD dei coefficienti (2 e 3) e arrotonda per difetto il termine noto: sui punti interi non cambia nulla.",
        "B divides each constraint of A by the GCD of its coefficients (2 and 3) and rounds the right-hand side down: nothing changes on integer points."),
    },
    cg: {
      etichetta: T("un taglio valido", "a valid cut"),
      vars: ["x_1", "x_2"], nomi: ["x₁", "x₂"], box: [-0.6, 6.2, -0.6, 4.0], r: 1, ddef: 2,
      A: [{ a: [4, 2], b: 23 }, { a: [-2, 5], b: 9 }, ...M.nonneg()],
      B: [{ a: [4, 2], b: 23 }, { a: [-2, 5], b: 9 }, { a: [0, 1], b: 3 }, ...M.nonneg()],
      texA: ["4x_1 + 2x_2 \\le 23", "-2x_1 + 5x_2 \\le 9", "x_1,\\ x_2 \\ge 0"],
      texB: ["4x_1 + 2x_2 \\le 23", "-2x_1 + 5x_2 \\le 9", "x_2 \\le 3", "x_1,\\ x_2 \\ge 0"],
      texBbreve: "X_A \\cap \\{x_2 \\le 3\\}",
      nota: T("Il taglio di B: \\(\\tfrac16\\) del primo vincolo più \\(\\tfrac13\\) del secondo dà \\(2x_2 \\le \\tfrac{41}{6}\\), cioè \\(x_2 \\le 3\\) sui punti interi.",
        "The cut of B: \\(\\tfrac16\\) of the first constraint plus \\(\\tfrac13\\) of the second gives \\(2x_2 \\le \\tfrac{41}{6}\\), that is \\(x_2 \\le 3\\) on integer points."),
    },
  };
  const BOXI = [-1, 12, -1, 12];
  function analisiF(st) {
    const k = st.chiave(), E = FORM[k], c = dirDi(st), D = st.dati, firma = k + "|" + c.join(",");
    if (D.anF && D.anF.firma === firma) return D.anF;
    if (!E._S) {
      E._S = puntiInteri(E.A, ...BOXI);
      const SB = puntiInteri(E.B, ...BOXI);
      E._ok = SB.length === E._S.length && SB.every((p, i) => p[0] === E._S[i][0] && p[1] === E._S[i][1]);
      if (!E._ok) console.error("GI: «formulazioni»: A e B hanno insiemi interi diversi", k);
      E._H = involucro(E._S);
      E._vA = verticiEsatti(E.A); E._vB = verticiEsatti(E.B);
      E._aA = areaQ(E._vA); E._aB = areaQ(E._vB); E._aH = areaQ(E._H.map((p) => [Q(p[0]), Q(p[1])]));
      E._frazB = E._vB.filter((v) => v[0].d !== 1 || v[1].d !== 1);
    }
    const a = lp2(E.A, c, "max"), b = lp2(E.B, c, "max");
    let ip = null;
    for (const p of E._S) { const z = c[0] * p[0] + c[1] * p[1]; if (!ip || z > ip.z) ip = { x: p, z }; }
    D.anF = { firma, E, c, a, b, ip: { x: [Q(ip.x[0]), Q(ip.x[1])], z: Q(ip.z) } };
    return D.anF;
  }

  window.GI_RICETTE["formulazioni"] = {
    titolo: T("Formulazioni deboli e forti", "Weak and strong formulations"),
    funzioni: FORM,
    etichettaFunzioni: T("Esempio", "Example"),
    parametri: [
      { k: "d", nome: "d", min: 0, max: 15, step: 1, val: 5, colore: "b", cifre: 0,
        descr: T("direzione di \\(\\boldsymbol c\\) (16 in tutto): ▶ la fa ruotare", "direction of \\(\\boldsymbol c\\) (16 in all): ▶ rotates it") },
    ],
    vista: (k) => vistaIniziale(FORM[k].box),
    stessaScala: false,
    legenda: (st) => {
      const C = M.COL(st);
      return [
        [C.rosso, T("\\(X_A\\): formulazione debole", "\\(X_A\\): weak formulation"), "pieno"],
        [C.viola, T("\\(X_B\\): formulazione forte", "\\(X_B\\): strong formulation"), "pieno"],
        [C.verde, T("\\(\\mathrm{conv}(S)\\), involucro dei punti interi", "\\(\\mathrm{conv}(S)\\), hull of the integer points"), "dashed"],
        [C.verde, T("punti interi \\(S\\)", "integer points \\(S\\)"), "punto"],
        [C.rosso, T("ottimo su \\(X_A\\)", "optimum over \\(X_A\\)"), "punto"],
        [C.viola, T("ottimo su \\(X_B\\)", "optimum over \\(X_B\\)"), "punto"],
        [C.blu, T("ottimo intero", "integer optimum"), "punto"],
        [st.colore("b"), "\\(\\boldsymbol c\\)", ""],
      ];
    },
    monta(board, st) {
      applicaIniziali(st, FORM[st.chiave()], null);
      st.dati.anF = null;
      seguiMisure(st);
    },
    aggiorna(board, st) {
      const A = analisiF(st), E = A.E, C = M.COL(st);
      const U = inquadra(board, E.box, E.r);
      M.ridisegna(board, st, [A.firma, M.scuro(), U.W, U.H].join("|"), (crea) => {
        M.area(crea, poligono(E.A), { strokeColor: C.rosso, fillColor: C.rosso, fillOpacity: 0.14, strokeWidth: 2 });
        M.area(crea, poligono(E.B), { strokeColor: C.viola, fillColor: C.viola, fillOpacity: 0.2, strokeWidth: 2.5 });
        M.area(crea, E._H, { strokeColor: C.verde, fillColor: "none", fillOpacity: 0, strokeWidth: 2.4, dash: 2 });
        for (const p of E._S) M.pallino(crea, p[0], p[1], { size: 3, fillColor: C.verde, strokeColor: C.verde });
        livello(crea, A.c, Qv(A.a.z), C.rosso);
        livello(crea, A.c, Qv(A.b.z), C.viola);
        livello(crea, A.c, Qv(A.ip.z), C.blu);
        frecciaC(crea, [0, 0], A.c, U, st.colore("b"));
        M.pallino(crea, Qv(A.a.x[0]), Qv(A.a.x[1]), { size: 6, fillColor: C.rosso, strokeColor: C.rosso });
        M.pallino(crea, Qv(A.b.x[0]), Qv(A.b.x[1]), { size: 5.5, fillColor: C.viola, strokeColor: C.viola });
        M.pallino(crea, Qv(A.ip.x[0]), Qv(A.ip.x[1]), { size: 5, fillColor: C.blu, strokeColor: "#ffffff", strokeWidth: 1.5 });
        nomiAssi(crea, board, E.nomi, C);
      });
    },
    formula(p, st) {
      const A = analisiF(st), E = A.E, C = M.COL(st);
      const sis = (righe) => righe.filter((t) => !/\\ge 0$/.test(t)).join(",\\ ");
      return `\\max\\ ${st.col("b", lin(A.c, E.vars))}\\qquad {\\color{${C.rosso}}{X_A\\!: ${sis(E.texA)}}}\\qquad ` +
        `{\\color{${C.viola}}{X_B${E.texBbreve ? " = " + E.texBbreve : "\\!: " + sis(E.texB)}}}`;
    },
    letture(p, st) {
      const A = analisiF(st), E = A.E, C = M.COL(st);
      let r = M.tab(["", T("bound", "bound"), T("ottimo", "optimum"), T("area", "area")], [
        [M.tinta(C.rosso, tx("X_A")), tx(Qtex(A.a.z)), tx(coppiaQ(A.a.x)), tx(areaTex(E._aA))],
        [M.tinta(C.viola, tx("X_B")), tx(Qtex(A.b.z)), tx(coppiaQ(A.b.x)), tx(areaTex(E._aB))],
        [M.tinta(C.verde, tx("\\mathrm{conv}(S)")), M.tinta(C.blu, tx(Qtex(A.ip.z))), tx(coppiaQ(A.ip.x)), tx(areaTex(E._aH))],
      ]);
      const gA = Qsub(A.a.z, A.ip.z), gB = Qsub(A.b.z, A.ip.z);
      r += `<div style="margin-top:.35em">` + T(
        `Divari da \\(\\zmilp\\): A \\(${num(gA)}\\), B \\(${num(gB)}\\).`,
        `Gaps from \\(\\zmilp\\): A \\(${num(gA)}\\), B \\(${num(gB)}\\).`) + "</div>";
      r += `<div style="margin-top:.35em">` + (E._frazB.length
        ? T(`\\(X_B \\subseteq X_A\\), ma \\(X_B \\ne \\mathrm{conv}(S)\\): ${E._frazB.length > 1 ? "vertici frazionari" : "vertice frazionario"} ${E._frazB.map((v) => tx(coppiaQ(v))).join(", ")}.`,
          `\\(X_B \\subseteq X_A\\), but \\(X_B \\ne \\mathrm{conv}(S)\\): fractional ${E._frazB.length > 1 ? "vertices" : "vertex"} ${E._frazB.map((v) => tx(coppiaQ(v))).join(", ")}.`)
        : T("\\(X_B \\subseteq X_A\\) e \\(X_B = \\mathrm{conv}(S)\\): i vertici di B sono interi, il bound è \\(\\zmilp\\) per ogni \\(\\boldsymbol c\\).",
          "\\(X_B \\subseteq X_A\\) and \\(X_B = \\mathrm{conv}(S)\\): the vertices of B are integer, the bound is \\(\\zmilp\\) for every \\(\\boldsymbol c\\).")) + "</div>";
      return r + `<div style="margin-top:.35em">${E.nota}</div>`;
    },
    domanda: T("Premi ▶ e fai ruotare \\(\\boldsymbol c\\): per quali direzioni il bound di A coincide con \\(\\zmilp\\)? Nel terzo esempio trova una direzione in cui anche B lascia un divario: quale vertice di \\(X_B\\) è responsabile, e quale disuguaglianza lo taglierebbe?",
      "Press ▶ and rotate \\(\\boldsymbol c\\): for which directions does the bound of A coincide with \\(\\zmilp\\)? In the third example find a direction in which B also leaves a gap: which vertex of \\(X_B\\) is responsible, and which inequality would cut it off?"),
  };
})();
