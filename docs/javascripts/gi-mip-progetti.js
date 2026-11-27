/* Laboratorio di «Modellazione MIP / MIP Modelling»: l'app di copertina della home.
 *
 *   mip-progetti-fondi   cinque progetti di un comune e due fondi (regionale, europeo): ogni progetto è finanziato
 *                        al più da un fondo, ogni fondo ha il suo budget; massimo beneficio totale. 10 binarie x_ik.
 *                        p = (5, 12, 8, 6, 9) punti, c = (6, 8, 7, 4, c5) M€, b = (b1, 10) M€.
 *                        Cursori: il budget b1 (3..12) e il costo c5 (1..10).
 *                        Valori iniziali b1 = 7, c5 = 3: parco giochi e illuminazione LED sul fondo regionale,
 *                        biblioteca sul fondo europeo; z(MILP) = 27, z(LP+) = 205/7.
 *
 * Stesso formato dell'app «mip-lotti» (gi-mip-lotti.js, da cui vengono SOL, FONDO, DV, numLP, FR e la ricetta
 * a voce, letti al montaggio): il problema a parole con variabili e dati, il modello simbolico, la figura, il
 * blocco «Soluzione ottima», il modello numerico in fondo al riquadro. La figura mostra i due fondi, alti quanto
 * il budget, con i progetti finanziati impilati dentro (altezza = costo) e, in grigio, quelli non finanziati.
 * L'ottimo enumera le 1024 assegnazioni delle binarie, il rilassamento usa il simplesso (GI_MIP_D).
 */
(function () {
  "use strict";
  const GI = window.GI, T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const L = () => window.GI_MIP_LOTTI, D = () => window.GI_MIP_D;
  const tx = (s) => `\\(${s}\\)`;
  const SA = () => T("\\text{soggetto a}", "\\text{subject to}");

  const DATI = { p: [5, 12, 8, 6, 9], c: [6, 8, 7, 4, 3], b: [7, 10] };
  const NOMI = () => T(["pista ciclabile", "biblioteca", "fotovoltaico", "parco giochi", "illuminazione LED"],
    ["cycle lane", "library", "solar plant", "playground", "LED lighting"]);
  const FONDI = () => T(["regionale", "europeo"], ["regional", "European"]);
  const N = 5, K = 2;
  const ix = (i, k) => i * K + k;   // colonne x_11, x_12, x_21, ..., x_52

  // home (data-vetrina): il riquadro «Dati» va nella colonna dei cursori, sopra i cursori, come nell'app di Modellazione PNL
  // (la «Soluzione ottima» va sotto i cursori in tutte le app: SOL.mostra di gi-mip-lotti.js)
  function datiDestra(st) {
    const ctrl = st.el.querySelector(".gi-ctrl");
    if (!ctrl) return;
    const dx = ctrl.parentElement, dati = st.el.querySelector(".plm .plm-dati");   // il riquadro appena ridisegnato
    if (dati) { dx.querySelectorAll(":scope > .plm-dati").forEach((e) => e.remove()); dx.insertBefore(dati, ctrl); }
  }

  function calcola(v) {
    const costo = DATI.c.slice(), b = DATI.b.slice();
    b[0] = v[0]; costo[4] = v[1];
    const c = new Array(N * K).fill(0), A = [], rel = [], rhs = [];
    for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) c[ix(i, k)] = DATI.p[i];
    for (let k = 0; k < K; k++) { const a = new Array(N * K).fill(0); for (let i = 0; i < N; i++) a[ix(i, k)] = costo[i]; A.push(a); rel.push("<="); rhs.push(b[k]); }
    for (let i = 0; i < N; i++) { const a = new Array(N * K).fill(0); for (let k = 0; k < K; k++) a[ix(i, k)] = 1; A.push(a); rel.push("<="); rhs.push(1); }
    const P = { senso: "max", c, A, rel, b: rhs }, bin = [...Array(N * K).keys()];
    const o = D().milp(P, bin), r = D().rilassamento(P, bin);
    const out = { P, costo, b, stato: o.stato, zLP: r.stato === "ottimo" ? r.z : null };
    if (o.stato !== "ottimo") return out;
    out.z = o.z;
    out.fondo = [...Array(N).keys()].map((i) => { const k = [0, 1].find((q) => o.x[ix(i, q)] > 0.5); return k === undefined ? 0 : k + 1; });
    return out;
  }

  const vProgetti = {
    etichetta: T("Progetti e fondi", "Projects and funds"),
    cursori: [
      { nome: "\\text{budget}\\ b_1", min: 3, max: 12, step: 1, val: 7,
        fmt: (x) => `${x} M€`, descr: T("budget del fondo regionale", "budget of the regional fund") },
      { nome: T("\\text{costo}\\ c_5", "\\text{cost}\\ c_5"), min: 1, max: 10, step: 1, val: 3,
        fmt: (x) => `${x} M€`, descr: T("costo dell'illuminazione LED", "cost of the LED lighting") },
    ],
    calcola,
    formula(R, v, st) {
      const H = L();
      const sim = `\\max ~~ \\sum_{i=1}^{n} \\sum_{k=1}^{m} p_i\\, x_{ik} & & \\\\
        ${SA()} \\quad \\sum_{i=1}^{n} ${st.col("b", "c_i")}\\, x_{ik} &\\le ${st.col("a", "b_k")}, & \\forall k \\in \\{1, \\dots, m\\}, \\\\
        \\sum_{k=1}^{m} x_{ik} &\\le 1, & \\forall i \\in \\{1, \\dots, n\\}, \\\\
        x_{ik} &\\in \\{0, 1\\}, & \\forall i \\in \\{1, \\dots, n\\},~\\forall k \\in \\{1, \\dots, m\\}.`;
      const vars = [];
      for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) vars[ix(i, k)] = `x_{${i + 1}${k + 1}}`;
      const num = H.numLP({ senso: "max", vars, c: R.P.c, cifre: 0, righe: R.P.A.map((a, q) => ({ a, rel: R.P.rel[q], rhs: R.P.b[q] })),
        dominio: [{ cols: [...vars.keys()], rel: "\\in", rhs: "\\{0, 1\\}" }] },
        T(`Il modello MILP dell'istanza: ${vars.length} variabili binarie, ${R.P.b.length} vincoli.`, `The MILP model of the instance: ${vars.length} binary variables, ${R.P.b.length} constraints.`));
      // tabelle per riga (un progetto, un fondo per colonna): il riquadro resta basso e l'app della home sta in una schermata.
      // I nomi dei progetti (nella figura) qui non ci stanno: con una riga per progetto l'app esce dalla schermata 1440×900.
      const TAB = H.DV.tabelle(H.DV.tab(T("Dimensioni", "Sizes"), ["\\(n\\)", "\\(m\\)"], [[String(N), String(K)]]),
        H.DV.tab(T("Progetti", "Projects"), ["\\(i\\)", ...NOMI().map((_, i) => String(i + 1))],
          [["\\(p_i\\)", ...DATI.p.map(String)], ["\\(c_i\\)", ...R.costo.map(String)]]),
        H.DV.tab(T("Fondi", "Funds"), ["\\(k\\)", "1", "2"], [["\\(b_k\\)", ...R.b.map(String)]]));
      const testo = T(
        "<b>Il problema.</b> Un comune ha alcuni progetti e alcuni fondi di finanziamento, ciascuno con il suo budget. " +
        "Ogni progetto ha un costo e un beneficio stimato, e può essere finanziato da un solo fondo. Quali progetti finanziare, e con quale fondo, per massimizzare il beneficio totale senza superare i budget?" +
        "<br><b>Variabili:</b> \\(x_{ik} \\in \\{0,1\\}\\): vale 1 se il progetto \\(i\\) è finanziato dal fondo \\(k\\), con \\(i \\in \\{1, \\dots, n\\}\\) e \\(k \\in \\{1, \\dots, m\\}\\)." +
        "<br><b>Dati:</b> \\(n\\), \\(m\\): numero di progetti e di fondi; \\(p_i\\), \\(c_i\\): beneficio (punti) e costo (M€) del progetto \\(i\\); \\(b_k\\): budget del fondo \\(k\\) (M€); con \\(i \\in \\{1, \\dots, n\\}\\) e \\(k \\in \\{1, \\dots, m\\}\\)." + TAB,
        "<b>The problem.</b> A town has some projects and some funding sources, each with its own budget. " +
        "Each project has a cost and an estimated benefit, and can be financed by one fund only. Which projects should be financed, and by which fund, to maximize the total benefit without exceeding the budgets?" +
        "<br><b>Variables:</b> \\(x_{ik} \\in \\{0,1\\}\\): equals 1 if project \\(i\\) is financed by fund \\(k\\), with \\(i \\in \\{1, \\dots, n\\}\\) and \\(k \\in \\{1, \\dots, m\\}\\)." +
        "<br><b>Data:</b> \\(n\\), \\(m\\): number of projects and of funds; \\(p_i\\), \\(c_i\\): benefit (points) and cost (M€) of project \\(i\\); \\(b_k\\): budget of fund \\(k\\) (M€); with \\(i \\in \\{1, \\dots, n\\}\\) and \\(k \\in \\{1, \\dots, m\\}\\)." + TAB);
      const V = !!st.el.dataset.vetrina;
      if (V) setTimeout(() => datiDestra(st), 0);
      const html = `<div class="plm"><p class="plm-testo">${testo}</p>` +
        `<div class="plm-sim">\\(\\displaystyle \\begin{aligned} ${sim} \\end{aligned}\\)</div>` +
        `<details class="plm-num"><summary>${T("Modello numerico con i dati attuali", "Numerical model with the current data")}</summary>` +
        `<div class="plm-num-corpo">${num}</div></details></div>`;
      return H.FONDO.sposta(st, html);
    },
    // la figura: i due fondi alti quanto il budget, con i progetti finanziati impilati (altezza = costo),
    // e a destra, in grigio, i progetti non finanziati
    disegna(crea, R, v, C, S) {
      const M = window.GI_MIP, W = S.W, H = S.H, nomi = NOMI(), fondi = FONDI();
      M.scritta(crea, W / 2, H - 16, T("Soluzione ottima x̃(MILP): i progetti finanziati da ogni fondo (altezza = costo)", "Optimal solution x̃(MILP): the projects financed by each fund (height = cost)"),
        { fontSize: 13.5, strokeColor: C.testo, cssStyle: "font-weight:700" });
      if (R.stato !== "ottimo") return;
      const COL = [C.a, C.b, C.c, C.d, C.e], y0 = 62, alto = H - 44;
      const fuori = [...Array(N).keys()].filter((i) => !R.fondo[i]), costoFuori = fuori.reduce((t, i) => t + R.costo[i], 0);
      const u = (alto - y0) / Math.max(12, ...R.b, costoFuori);   // pixel per M€
      const larg = Math.min(170, W * 0.22), xk = [W * 0.2, W * 0.48], xf = W * 0.79;
      const blocco = (x, y, i, grigio) => {
        const h = R.costo[i] * u, col = grigio ? C.grigio : COL[i];
        M.rett(crea, x - larg / 2 + 4, y, x + larg / 2 - 4, y + h - 2, { fillColor: col, fillOpacity: grigio ? 0.35 : 0.85, strokeColor: col, strokeWidth: 1 });
        const stile = { fontSize: 12, strokeColor: grigio ? C.testo : "#ffffff", cssStyle: "font-weight:700" }, ym = y + (h - 2) / 2;
        if (h > 38) {
          M.scritta(crea, x, ym + 8, nomi[i], stile);
          M.scritta(crea, x, ym - 8, T(`${DATI.p[i]} punti · ${R.costo[i]} M€`, `${DATI.p[i]} points · ${R.costo[i]} M€`), Object.assign({}, stile, { cssStyle: "" }));
        } else M.scritta(crea, x, ym, nomi[i], stile);
        return y + h;
      };
      [0, 1].forEach((k) => {
        const x = xk[k];
        let y = y0, speso = 0;
        for (let i = 0; i < N; i++) if (R.fondo[i] === k + 1) { y = blocco(x, y, i, false); speso += R.costo[i]; }
        M.rett(crea, x - larg / 2, y0, x + larg / 2, y0 + R.b[k] * u, { strokeColor: C.testo, strokeWidth: 2.5 });
        M.scritta(crea, x, y0 - 14, T(`fondo ${fondi[k]}`, `${fondi[k]} fund`), { fontSize: 13, strokeColor: C.testo, cssStyle: "font-weight:700" });
        M.scritta(crea, x, y0 - 32, T(`speso ${speso} su ${R.b[k]} M€`, `spent ${speso} of ${R.b[k]} M€`), { fontSize: 12, strokeColor: C.muted });
      });
      let y = y0;
      for (const i of fuori) y = blocco(xf, y, i, true);
      M.scritta(crea, xf, y0 - 14, T("non finanziati", "not financed"), { fontSize: 13, strokeColor: C.muted, cssStyle: "font-weight:700" });
    },
    letture: () => "",
    soluzione(R) {
      if (R.stato !== "ottimo") return "";
      const H = L(), FR = H.FR;
      const pt = (z) => `${FR.euro(z).replace(" €", "")} ${T("punti", "points")}`;
      return H.SOL.blocco(
        H.SOL.valore(T("Beneficio ottimo", "Optimal benefit"), pt(R.z), R.zLP === null ? null : pt(R.zLP), R.zLP === null ? null : FR.gap(R.zLP, R.z)),
        [H.SOL.tab("", ["\\(i\\)", ...R.fondo.map((_, i) => String(i + 1))],
          [[T("\\(k\\) con \\(\\tilde x_{ik}(\\text{MILP}) = 1\\)", "\\(k\\) with \\(\\tilde x_{ik}(\\text{MILP}) = 1\\)"), ...R.fondo.map((k) => (k ? String(k) : T("no", "no")))]])]);
    },
    domanda: T("Porta \\(b_1\\) a 12: il gap va a zero. Porta \\(c_5\\) a 7: si finanziano solo i progetti 2 e 5, biblioteca e illuminazione LED.",
      "Set \\(b_1\\) to 12: the gap drops to zero. Set \\(c_5\\) to 7: only projects 2 and 5, library and LED lighting, are financed."),
  };

  window.GI_RICETTE["mip-progetti-fondi"] = () => L().ricettaVoce({ titolo: T("Progetti e fondi", "Projects and funds") }, vProgetti);
  // per le prove automatiche: solo il calcolo
  window.GI_MIP_PROGETTI = { calcola, DATI };
})();
