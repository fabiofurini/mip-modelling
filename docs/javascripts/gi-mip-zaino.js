/* Laboratorio di «Modellazione MIP / MIP Modelling»: l'app di copertina della home.
 *
 *   mip-zaino-multiplo   lo zaino multiplo su un'istanza piccola: n = 5 oggetti, m = 2 zaini, 10 binarie x_ik.
 *                        p = (5, 12, 8, 6, 9), w = (6, 8, 7, 4, w5), b = (b1, 10).
 *                        Cursori: la capacità b1 (3..12) e il peso w5 (1..10).
 *                        Valori iniziali b1 = 7, w5 = 3: oggetti 4 e 5 nello zaino 1, oggetto 2 nello zaino 2,
 *                        z(MILP) = 27, z(LP+) = 205/7.
 *
 * Stesso formato dell'app «mip-lotti» (gi-mip-lotti.js, da cui vengono SOL, FONDO, DV, numLP, FR e la ricetta
 * a voce, letti al montaggio): il problema a parole con variabili e dati, il modello simbolico, il blocco
 * «Soluzione ottima», il modello numerico in fondo al riquadro. Niente grafico: la board resta nascosta.
 * L'ottimo enumera le 1024 assegnazioni delle binarie, il rilassamento usa il simplesso (GI_MIP_D).
 */
(function () {
  "use strict";
  const GI = window.GI, T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const L = () => window.GI_MIP_LOTTI, D = () => window.GI_MIP_D;
  const tx = (s) => `\\(${s}\\)`;
  const SA = () => T("\\text{soggetto a}", "\\text{subject to}");

  const DATI = { p: [5, 12, 8, 6, 9], w: [6, 8, 7, 4, 3], b: [7, 10] };
  const N = 5, K = 2;
  const ix = (i, k) => i * K + k;   // colonne x_11, x_12, x_21, ..., x_52

  function calcola(v) {
    const w = DATI.w.slice(), b = DATI.b.slice();
    b[0] = v[0]; w[4] = v[1];
    const c = new Array(N * K).fill(0), A = [], rel = [], rhs = [];
    for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) c[ix(i, k)] = DATI.p[i];
    for (let k = 0; k < K; k++) { const a = new Array(N * K).fill(0); for (let i = 0; i < N; i++) a[ix(i, k)] = w[i]; A.push(a); rel.push("<="); rhs.push(b[k]); }
    for (let i = 0; i < N; i++) { const a = new Array(N * K).fill(0); for (let k = 0; k < K; k++) a[ix(i, k)] = 1; A.push(a); rel.push("<="); rhs.push(1); }
    const P = { senso: "max", c, A, rel, b: rhs }, bin = [...Array(N * K).keys()];
    const o = D().milp(P, bin), r = D().rilassamento(P, bin);
    const out = { P, w, b, stato: o.stato, zLP: r.stato === "ottimo" ? r.z : null };
    if (o.stato !== "ottimo") return out;
    out.z = o.z;
    out.zaino = [...Array(N).keys()].map((i) => { const k = [0, 1].find((q) => o.x[ix(i, q)] > 0.5); return k === undefined ? 0 : k + 1; });
    return out;
  }

  const vZaino = {
    etichetta: T("Zaino multiplo", "Multiple knapsack"),
    cursori: [
      { nome: T("\\text{capacità}\\ b_1", "\\text{capacity}\\ b_1"), min: 3, max: 12, step: 1, val: 7,
        fmt: (x) => `${x} kg`, descr: T("capacità dello zaino 1", "capacity of knapsack 1") },
      { nome: T("\\text{peso}\\ w_5", "\\text{weight}\\ w_5"), min: 1, max: 10, step: 1, val: 3,
        fmt: (x) => `${x} kg`, descr: T("peso dell'oggetto 5", "weight of item 5") },
    ],
    calcola,
    formula(R, v, st) {
      const H = L();
      const sim = `\\max ~~ \\sum_{i=1}^{n} \\sum_{k=1}^{m} p_i\\, x_{ik} & & \\\\
        ${SA()} \\quad \\sum_{i=1}^{n} ${st.col("b", "w_i")}\\, x_{ik} &\\le ${st.col("a", "b_k")}, & \\forall k \\in \\{1, \\dots, m\\}, \\\\
        \\sum_{k=1}^{m} x_{ik} &\\le 1, & \\forall i \\in \\{1, \\dots, n\\}, \\\\
        x_{ik} &\\in \\{0, 1\\}, & \\forall i \\in \\{1, \\dots, n\\},~\\forall k \\in \\{1, \\dots, m\\}.`;
      const vars = [];
      for (let i = 0; i < N; i++) for (let k = 0; k < K; k++) vars[ix(i, k)] = `x_{${i + 1}${k + 1}}`;
      const num = H.numLP({ senso: "max", vars, c: R.P.c, cifre: 0, righe: R.P.A.map((a, q) => ({ a, rel: R.P.rel[q], rhs: R.P.b[q] })),
        dominio: [{ cols: [...vars.keys()], rel: "\\in", rhs: "\\{0, 1\\}" }] },
        T(`Il modello MILP dell'istanza: ${vars.length} variabili binarie, ${R.P.b.length} vincoli.`, `The MILP model of the instance: ${vars.length} binary variables, ${R.P.b.length} constraints.`));
      const TAB = H.DV.tabelle(H.DV.tab(T("Oggetti", "Items"), [tx("i"), ...DATI.p.map((_, i) => String(i + 1))],
        [[T("\\(p_i\\) (€)", "\\(p_i\\) (€)"), ...DATI.p.map(String)], ["\\(w_i\\) (kg)", ...R.w.map(String)]]));
      const testo = T(
        "<b>Il problema.</b> Cinque oggetti, due zaini. Decidiamo quali oggetti mettere in ogni zaino, ognuno al più in uno zaino, " +
        "per massimizzare il valore caricato senza superare la capacità degli zaini." +
        "<br><b>Variabili:</b> \\(x_{ik} \\in \\{0,1\\}\\): vale 1 se l'oggetto \\(i\\) va nello zaino \\(k\\)." +
        `<br><b>Dati:</b> \\(n = ${N}\\) oggetti, \\(m = ${K}\\) zaini; \\(p_i\\): valore dell'oggetto \\(i\\); \\(w_i\\): peso dell'oggetto \\(i\\); \\(b_k\\): capacità dello zaino \\(k\\), \\(b_1 = ${R.b[0]}\\) kg e \\(b_2 = ${R.b[1]}\\) kg.` + TAB,
        "<b>The problem.</b> Five items, two knapsacks. We decide which items to put in each knapsack, each item in at most one knapsack, " +
        "to maximize the value loaded without exceeding the capacity of the knapsacks." +
        "<br><b>Variables:</b> \\(x_{ik} \\in \\{0,1\\}\\): equals 1 if item \\(i\\) goes into knapsack \\(k\\)." +
        `<br><b>Data:</b> \\(n = ${N}\\) items, \\(m = ${K}\\) knapsacks; \\(p_i\\): value of item \\(i\\); \\(w_i\\): weight of item \\(i\\); \\(b_k\\): capacity of knapsack \\(k\\), \\(b_1 = ${R.b[0]}\\) kg and \\(b_2 = ${R.b[1]}\\) kg.` + TAB);
      const html = `<div class="plm"><p class="plm-testo">${testo}</p>` +
        `<div class="plm-sim">\\(\\displaystyle \\begin{aligned} ${sim} \\end{aligned}\\)</div>` +
        `<details class="plm-num" open><summary>${T("Modello numerico con i dati attuali", "Numerical model with the current data")}</summary>` +
        `<div class="plm-num-corpo">${num}</div></details></div>`;
      return H.FONDO.sposta(st, html);
    },
    // niente grafico: la board resta nascosta
    disegna(crea, R, v, C, S, st, board) { if (board && board.containerObj) board.containerObj.style.display = "none"; },
    letture: () => "",
    soluzione(R) {
      if (R.stato !== "ottimo") return "";
      const H = L(), FR = H.FR, g = R.zLP === null ? "—" : tx(FR.gap(R.zLP, R.z));
      return H.SOL.blocco(
        `${T("Valore ottimo", "Optimal value")} \\(z(\\mathrm{MILP})\\): <b>${FR.euro(R.z)}</b><br>` +
        `${T("Rilassamento continuo", "Continuous relaxation")} \\(z(\\mathrm{LP}^+)\\): <b>${R.zLP === null ? "—" : FR.euro(R.zLP)}</b> · ` +
        `gap \\((z(\\mathrm{LP}^+) - z(\\mathrm{MILP}))/z(\\mathrm{LP}^+)\\) = <b>${g}</b>`,
        [H.SOL.tab(T("Zaino di ogni oggetto", "Knapsack of each item"), [tx("i"), ...R.zaino.map((_, i) => String(i + 1))],
          [[T("zaino", "knapsack"), ...R.zaino.map((k) => (k ? String(k) : "—"))]])],
        T("«—»: l'oggetto resta fuori.", "«—»: the item stays out."));
    },
    domanda: T("Porta \\(b_1\\) a 12: il gap va a zero. Porta \\(w_5\\) a 7: entrano solo gli oggetti 2 e 5.",
      "Set \\(b_1\\) to 12: the gap drops to zero. Set \\(w_5\\) to 7: only items 2 and 5 are loaded."),
  };

  window.GI_RICETTE["mip-zaino-multiplo"] = () => L().ricettaVoce({ titolo: T("Zaino multiplo", "Multiple knapsack") }, vZaino);
  // per le prove automatiche: solo il calcolo
  window.GI_MIP_ZAINO = { calcola, DATI };
})();
