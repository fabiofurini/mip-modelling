/* Laboratorio di «Modellazione MIP / MIP Modelling»: la selezione di progetti con vincoli logici (capitolo 5).
 *
 *   mip-progetti-logica   l'istanza del capitolo: 10 progetti, r = (9, 7, 4, 8, 3, 6, 2, 5, 7, 6), c = (4, 3, 2, 4, 2, 3, 1,
 *                         3, 4, 3), budget b, le sei implicazioni dell'esercizio 2.1 come otto clausole. 10 binarie, 9 vincoli.
 *                         Cursori: il budget b (4..30) e il ricavo r2 (1..15).
 *                         Valori iniziali b = 14, r2 = 7: z(MILP) = 28 (4 soluzioni ottime), z(LP+) = 29.
 *                         Soglie (verificate con Gurobi): r2 <= 6 toglie il progetto 2 dall'ottimo e z(LP+) = z(MILP) = 28;
 *                         r2 >= 8 dà l'unico ottimo 1, 2, 3, 5, 8; b = 24 finanzia otto progetti, z = z(LP+) = 46.
 *
 * Stesso formato dell'app «mip-lotti» (gi-mip-lotti.js, da cui vengono SOL, FONDO, DV, numLP, FR e la ricetta
 * a voce, letti al montaggio). La figura: i dieci progetti come schede, il valore nel rilassamento sotto ognuna,
 * il budget in fondo riempito dai costi dei progetti scelti. L'ottimo enumera le 1024 assegnazioni delle binarie,
 * il rilassamento usa il simplesso (GI_MIP_D di gi-mip-d.js).
 */
(function () {
  "use strict";
  const GI = window.GI, T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const L = () => window.GI_MIP_LOTTI, D = () => window.GI_MIP_D;
  const tx = (s) => `\\(${s}\\)`;
  const SA = () => T("\\text{soggetto a}", "\\text{subject to}");
  const FIG = () => (window.GI_MIP.scuro()
    ? { blu: "#D6E4F0", teal: "#22A6C7", rosso: "#E5675A", grigio: "#A3AFB0" }
    : { blu: "#16324A", teal: "#0E7490", rosso: "#C0392B", grigio: "#7F8C8D" });

  const DATI = { r: [9, 7, 4, 8, 3, 6, 2, 5, 7, 6], c: [4, 3, 2, 4, 2, 3, 1, 3, 4, 3], b: 14 };
  const N = 10;
  // le sei implicazioni dell'esercizio 2.1 e le loro clausole: [coefficienti per progetto, relazione, termine noto]
  const IMPL = [
    { tex: "x_2 \\Rightarrow x_3", cl: [[{ 2: -1, 3: 1 }, ">=", 0]] },
    { tex: "x_2 \\Rightarrow \\lnot x_4", cl: [[{ 2: 1, 4: 1 }, "<=", 1]] },
    { tex: "x_1 \\land x_6 \\Rightarrow x_7", cl: [[{ 1: 1, 6: 1, 7: -1 }, "<=", 1]] },
    { tex: "x_1 \\lor x_6 \\Rightarrow x_8", cl: [[{ 1: -1, 8: 1 }, ">=", 0], [{ 6: -1, 8: 1 }, ">=", 0]] },
    { tex: "x_2 \\land x_3 \\Rightarrow \\lnot x_9", cl: [[{ 2: 1, 3: 1, 9: 1 }, "<=", 2]] },
    { tex: "x_2 \\lor x_3 \\Rightarrow \\lnot x_{10}", cl: [[{ 2: 1, 10: 1 }, "<=", 1], [{ 3: 1, 10: 1 }, "<=", 1]] },
  ];
  const REL = { "<=": "\\le", ">=": "\\ge" };
  /** una clausola in TeX, variabili a sinistra: «-x_2 + x_3 \ge 0» */
  const clausolaTex = ([co, rel, rhs]) => Object.entries(co).map(([j, v], k) =>
    `${v < 0 ? "-" : k ? "+" : ""}${Math.abs(v) === 1 ? "" : Math.abs(v)}x_{${j}}`).join(" ") + ` &${REL[rel]} ${rhs}`;

  // ================================================================ il capitolo che spiega il modello
  const radice = () => {
    try { if (window.__md_scope) return new URL(window.__md_scope); } catch (e) { /* sotto */ }
    const cfg = document.getElementById("__config");
    try { return new URL(JSON.parse(cfg.textContent).base + "/", location.href); } catch (e) { return new URL("./", location.href); }
  };
  const rigaCapitolo = () => {
    const url = new URL(GI.EN ? "modelling-5/" : "modellazione-5/", radice()).href;
    return `<p class="plm-cap">${T("Il modello è spiegato nel capitolo", "The model is explained in the chapter")} <a href="${url}">${T("5. Logica e variabili binarie", "5. Logic and binary variables")}</a>.</p>`;
  };

  function calcola(v) {
    const b = v[0], r = DATI.r.slice();
    r[1] = v[1];
    const A = [DATI.c.slice()], rel = ["<="], rhs = [b];
    IMPL.forEach((im) => im.cl.forEach(([co, rr, q]) => {
      const a = new Array(N).fill(0);
      for (const [j, x] of Object.entries(co)) a[+j - 1] = x;
      A.push(a); rel.push(rr); rhs.push(q);
    }));
    const P = { senso: "max", c: r, A, rel, b: rhs }, bin = [...Array(N).keys()];
    const o = D().milp(P, bin, true), lp = D().rilassamento(P, bin);
    const out = { P, r, b, stato: o.stato, nOtt: o.nOtt, zLP: lp.stato === "ottimo" ? lp.z : null };
    if (o.stato !== "ottimo") return out;
    out.z = o.z;
    out.x = o.x.map((x) => (x > 0.5 ? 1 : 0));
    out.xLP = lp.stato === "ottimo" ? lp.x.map((x) => (Math.abs(x) < 1e-7 ? 0 : x)) : null;
    out.costo = out.x.reduce((s, x, p) => s + x * DATI.c[p], 0);
    return out;
  }

  const vLogica = {
    etichetta: T("Progetti con vincoli logici", "Projects with logical constraints"),
    cursori: [
      { nome: "\\text{budget}\\ b", min: 4, max: 30, step: 1, val: 14,
        fmt: (x) => String(x), descr: T("budget per i progetti", "budget for the projects") },
      { nome: T("\\text{ricavo}\\ r_2", "\\text{revenue}\\ r_2"), min: 1, max: 15, step: 1, val: 7,
        fmt: (x) => String(x), descr: T("ricavo del progetto 2", "revenue of project 2") },
    ],
    calcola,
    formula(R, v, st) {
      const H = L();
      const righe = [];
      IMPL.forEach((im, k) => im.cl.forEach((cl) => righe.push(`${clausolaTex(cl)}, & \\text{(${k + 1})}\\ ${im.tex}, \\\\`)));
      const sim = `\\max ~~ \\sum_{p=1}^{n} ${st.col("b", "r_p")}\\, x_p & & \\\\
        ${SA()} \\quad \\sum_{p=1}^{n} c_p\\, x_p &\\le ${st.col("a", "b")}, & \\\\
        ${righe.join("\n")}
        x_p &\\in \\{0, 1\\}, & \\forall p \\in \\{1, 2, \\dots, n\\}.`;
      const vars = [...Array(N).keys()].map((p) => `x_{${p + 1}}`);
      const num = H.numLP({ senso: "max", vars, c: R.P.c, cifre: 0, righe: R.P.A.map((a, q) => ({ a, rel: R.P.rel[q], rhs: R.P.b[q] })),
        dominio: [{ cols: [...vars.keys()], rel: "\\in", rhs: "\\{0, 1\\}" }] },
        T(`Il modello MILP dell'istanza: ${N} variabili binarie, ${R.P.b.length} vincoli.`, `The MILP model of the instance: ${N} binary variables, ${R.P.b.length} constraints.`));
      const TAB = H.DV.tabelle(H.DV.tab(T("Progetti", "Projects"), [T("progetto \\(p\\)", "project \\(p\\)"), ...vars.map((_, p) => String(p + 1))],
        [["\\(r_p\\)", ...R.r.map(String)], ["\\(c_p\\)", ...DATI.c.map(String)]]),
        H.DV.tab(T("Dimensioni", "Sizes"), ["\\(n\\)"], [[String(N)]]), H.DV.tab(T("Budget", "Budget"), ["\\(b\\)"], [[String(R.b)]]));
      const imp = IMPL.map((im, k) => `(${k + 1}) \\(${im.tex}\\)`).join("; ");
      const testo = T(
        "<b>Il problema.</b> Un'azienda valuta alcuni progetti, ciascuno con un ricavo e un costo, e dispone di un budget. Alcune scelte sono legate da implicazioni logiche, del tipo «se si sceglie un progetto allora se ne sceglie (o non se ne sceglie) un altro». " +
        "Decidiamo quali progetti finanziare. L'obiettivo è massimizzare il ricavo totale. I vincoli: il costo totale non supera il budget e tutte le implicazioni sono rispettate." +
        "<br><b>Variabili:</b> \\(x_p \\in \\{0,1\\}\\): vale 1 se si finanzia il progetto \\(p\\), con \\(p \\in \\{1, \\dots, n\\}\\)." +
        `<br><b>Dati:</b> \\(n\\): numero di progetti; \\(r_p\\): ricavo del progetto \\(p\\); \\(c_p\\): costo del progetto \\(p\\); \\(b\\): budget; con \\(p \\in \\{1, \\dots, n\\}\\). Le sei implicazioni dell'esercizio 2.1: ${imp}. Ogni implicazione diventa una o due disuguaglianze lineari.` + TAB,
        "<b>The problem.</b> A company evaluates some projects, each with a revenue and a cost, and has a budget. Some choices are linked by logical implications, of the kind «if a project is chosen then another one is (or is not) chosen». " +
        "We decide which projects to finance. The objective is to maximize the total revenue. The constraints: the total cost does not exceed the budget and all the implications hold." +
        "<br><b>Variables:</b> \\(x_p \\in \\{0,1\\}\\): equals 1 if project \\(p\\) is financed, with \\(p \\in \\{1, \\dots, n\\}\\)." +
        `<br><b>Data:</b> \\(n\\): number of projects; \\(r_p\\): revenue of project \\(p\\); \\(c_p\\): cost of project \\(p\\); \\(b\\): budget; with \\(p \\in \\{1, \\dots, n\\}\\). The six implications of exercise 2.1: ${imp}. Each implication becomes one or two linear inequalities.` + TAB);
      const html = `<div class="plm"><p class="plm-testo">${testo}</p>${rigaCapitolo()}` +
        `<div class="plm-sim">\\(\\displaystyle \\begin{aligned} ${sim} \\end{aligned}\\)</div>` +
        `<details class="plm-num"><summary>${T("Modello numerico con i dati attuali", "Numerical model with the current data")}</summary>` +
        `<div class="plm-num-corpo">${num}</div></details></div>`;
      return H.FONDO.sposta(st, html);
    },
    // la figura: i dieci progetti come schede (piene se finanziati), sotto ognuna il valore nel rilassamento continuo;
    // in fondo il budget, riempito dai costi dei progetti scelti
    disegna(crea, R, v, C, S) {
      const M = window.GI_MIP, F = FIG(), FR = L().FR, W = S.W, H = S.H;
      const titolo = R.stato === "ottimo"
        ? T(`Soluzione ottima x̃ₚ(MILP): i progetti finanziati (z(MILP) = ${FR.txt(R.z)})`, `Optimal solution x̃ₚ(MILP): the financed projects (z(MILP) = ${FR.txt(R.z)})`)
        : T("Nessuna soluzione ammissibile", "No feasible solution");
      M.scritta(crea, W / 2, H - 16, titolo, { fontSize: 13.5, strokeColor: F.blu, cssStyle: "font-weight:700" });
      if (R.stato !== "ottimo") return;
      const mg = 16, col = 5, cima = H - 46, zonaBudget = 120, gh = (cima - zonaBudget) / 2, gw = (W - 2 * mg) / col;
      for (let p = 0; p < N; p++) {
        const rr = Math.floor(p / col), cc = p % col, preso = R.x[p] === 1;
        const x0 = mg + cc * gw + 6, x1 = x0 + gw - 12, y1 = cima - rr * gh - 6, y0 = y1 - gh + 12, xm = (x0 + x1) / 2, hh = y1 - y0;
        M.rett(crea, x0, y0, x1, y1, preso
          ? { fillColor: F.teal, fillOpacity: 1, strokeColor: F.teal, strokeWidth: 2 }
          : { fillColor: "none", strokeColor: C.grigio, strokeWidth: 1.5, dash: 2 });
        const colT = preso ? "#ffffff" : C.testo;
        M.scritta(crea, xm, y1 - hh * 0.2, T(`progetto ${p + 1}`, `project ${p + 1}`), { fontSize: 14, strokeColor: colT, cssStyle: "font-weight:700" });
        M.scritta(crea, xm, y1 - hh * 0.42, `r = ${R.r[p]} · c = ${DATI.c[p]}`, { fontSize: 12.5, strokeColor: preso ? "#ffffff" : C.muted });
        if (R.xLP) {
          const val = Math.max(0, Math.min(1, R.xLP[p])), bx0 = x0 + 12, bx1 = x1 - 12, by = y0 + hh * 0.2;
          M.rett(crea, bx0, by - 5, bx1, by + 5, { fillColor: "#ffffff", fillOpacity: preso ? 0.9 : 0, strokeColor: F.rosso, strokeWidth: 1 });
          if (val > 1e-9) M.rett(crea, bx0, by - 5, bx0 + (bx1 - bx0) * val, by + 5, { fillColor: F.rosso, fillOpacity: 1, strokeColor: F.rosso, strokeWidth: 0.5 });
          M.scritta(crea, xm, by + 15, `x̃(LP⁺) = ${FR.txt(val)}`, { fontSize: 12, strokeColor: preso ? "#ffffff" : F.rosso, cssStyle: "font-weight:700" });
        }
      }
      // budget: barra lunga b, riempita dai costi dei progetti scelti
      const x0 = mg + 70, u = (W - x0 - mg - 10) / 30, by = 62;
      M.scritta(crea, x0 - 10, by, "budget", { anchorX: "right", fontSize: 12.5, strokeColor: C.testo, cssStyle: "font-weight:700" });
      let x = x0;
      for (let p = 0; p < N; p++) if (R.x[p]) {
        M.rett(crea, x + 1, by - 13, x + DATI.c[p] * u - 1, by + 13, { fillColor: F.teal, fillOpacity: 1, strokeColor: F.teal, strokeWidth: 0.5 });
        M.scritta(crea, x + DATI.c[p] * u / 2, by, String(p + 1), { fontSize: 12, strokeColor: "#ffffff", cssStyle: "font-weight:700" });
        x += DATI.c[p] * u;
      }
      M.rett(crea, x0, by - 17, x0 + R.b * u, by + 17, { fillColor: "none", strokeColor: C.testo, strokeWidth: 2 });
      for (let k = 0; k <= 30; k += 5) M.scritta(crea, x0 + k * u, by - 28, String(k), { fontSize: 11, strokeColor: C.muted });
      M.scritta(crea, x0, by + 30, T(`costo dei progetti scelti: ${R.costo} su b = ${R.b}`, `cost of the chosen projects: ${R.costo} out of b = ${R.b}`), { anchorX: "left", fontSize: 12.5, strokeColor: C.testo });
      M.scritta(crea, W - mg, by + 30, T("in rosso: il valore x̃ₚ(LP⁺) nel rilassamento continuo", "in red: the value x̃ₚ(LP⁺) in the continuous relaxation"), { anchorX: "right", fontSize: 11.5, strokeColor: F.rosso });
    },
    letture: () => "",
    soluzione(R) {
      if (R.stato !== "ottimo") return "";
      const H = L(), FR = H.FR;
      return H.SOL.blocco(
        H.SOL.valore(T("Ricavo ottimo", "Optimal revenue"), tx(FR.tex(R.z)), R.zLP === null ? null : tx(FR.tex(R.zLP)), R.zLP === null ? null : FR.gap(R.zLP, R.z)),
        [0, 5].map((k) => H.SOL.tab("", ["\\(p\\)", ...[1, 2, 3, 4, 5].map((q) => String(k + q))],   // due righe da 5: la colonna è stretta
          [["\\(\\tilde x(\\text{MILP})\\)", ...R.x.slice(k, k + 5).map(String)]])),
        R.nOtt > 1 ? T(`Ci sono ${R.nOtt} soluzioni ottime con lo stesso ricavo: se ne mostra una.`, `There are ${R.nOtt} optimal solutions with the same revenue: one is shown.`) : "");
    },
    domanda: T("Con \\(r_2 = 6\\) il progetto 2 esce e il gap va a zero. Con \\(b = 24\\) si finanziano otto progetti.",
      "With \\(r_2 = 6\\) project 2 leaves and the gap drops to zero. With \\(b = 24\\) eight projects are financed."),
  };

  window.GI_RICETTE["mip-progetti-logica"] = () => L().ricettaVoce({ titolo: T("Progetti con vincoli logici", "Projects with logical constraints") }, vLogica);
  // per le prove automatiche: solo il calcolo
  window.GI_MIP_LOGICA = { calcola, DATI, IMPL };
})();
