/* Laboratorio di «Modellazione MIP / MIP Modelling»: la localizzazione capacitata (problema 8.1).
 *
 *   mip-localizzazione   3 sedi candidate, 4 clienti: l'istanza del capitolo (sedi 1-2, clienti 1-3) con una sede e
 *                        un cliente in più. t = [[4, 5, 6, 8], [6, 4, 3, 5], [8, 7, 5, 2]] €/litro, u = (50, 50, 50) litri,
 *                        i = (60, 90, i3) €, d = (8, 25, 27, d4) litri. 3 binarie x_l e 12 continue y_lc, 7 vincoli.
 *                        Cursori: il costo di installazione i3 (10..200) e la domanda d4 (5..60).
 *                        Valori iniziali i3 = 70, d4 = 20: sedi 2 e 3 aperte, z(MILP) = 449, z(LP+) = 385.
 *                        Soglie (verificate con Gurobi): i3 >= 110 chiude la sede 3 e apre la 1 (z = 485);
 *                        d4 <= 10 apre le sedi 1 e 2; d4 >= 45 apre tutte e tre le sedi.
 *
 * Stesso formato dell'app «mip-lotti» (gi-mip-lotti.js, da cui vengono SOL, FONDO, DV, numLP, FR e la ricetta
 * a voce, letti al montaggio). La figura: sedi a sinistra, clienti a destra, gli archi con i litri spediti.
 * L'ottimo enumera le 8 assegnazioni delle binarie col simplesso sulle continue, il rilassamento usa lo stesso
 * simplesso (GI_MIP_D di gi-mip-d.js).
 */
(function () {
  "use strict";
  const GI = window.GI, T = GI.T;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const L = () => window.GI_MIP_LOTTI, D = () => window.GI_MIP_D;
  const tx = (s) => `\\(${s}\\)`;
  const SA = () => T("\\text{soggetto a}", "\\text{subject to}");
  const FIG = () => (window.GI_MIP.scuro()
    ? { blu: "#D6E4F0", teal: "#22A6C7", rosso: "#E5675A", verde: "#3DBB6E", grigio: "#A3AFB0" }
    : { blu: "#16324A", teal: "#0E7490", rosso: "#C0392B", verde: "#1E8449", grigio: "#7F8C8D" });

  const DATI = { t: [[4, 5, 6, 8], [6, 4, 3, 5], [8, 7, 5, 2]], u: [50, 50, 50], i: [60, 90, 70], d: [8, 25, 27, 20] };
  const NS = 3, NC = 4;
  const X = (l) => l, Y = (l, c) => NS + l * NC + c;   // colonne x_1..x_3, y_11..y_14, ..., y_31..y_34
  const NV = NS + NS * NC;

  // ================================================================ il capitolo che spiega il modello
  const radice = () => {
    try { if (window.__md_scope) return new URL(window.__md_scope); } catch (e) { /* sotto */ }
    const cfg = document.getElementById("__config");
    try { return new URL(JSON.parse(cfg.textContent).base + "/", location.href); } catch (e) { return new URL("./", location.href); }
  };
  const rigaCapitolo = () => {
    const url = new URL(GI.EN ? "location-1/" : "localizzazione-1/", radice()).href;
    return `<p class="plm-cap">${T("Il modello è spiegato nel capitolo", "The model is explained in the chapter")} <a href="${url}">${T("Localizzazione capacitata", "Capacitated facility location")}</a>.</p>`;
  };

  function calcola(v) {
    const inst = DATI.i.slice(), d = DATI.d.slice();
    inst[2] = v[0]; d[3] = v[1];
    const c = new Array(NV).fill(0), A = [], rel = [], rhs = [];
    for (let l = 0; l < NS; l++) { c[X(l)] = inst[l]; for (let k = 0; k < NC; k++) c[Y(l, k)] = DATI.t[l][k]; }
    for (let l = 0; l < NS; l++) {
      const a = new Array(NV).fill(0); a[X(l)] = DATI.u[l];
      for (let k = 0; k < NC; k++) a[Y(l, k)] = -1;
      A.push(a); rel.push(">="); rhs.push(0);
    }
    for (let k = 0; k < NC; k++) {
      const a = new Array(NV).fill(0);
      for (let l = 0; l < NS; l++) a[Y(l, k)] = 1;
      A.push(a); rel.push("="); rhs.push(d[k]);
    }
    const P = { senso: "min", c, A, rel, b: rhs }, bin = [0, 1, 2];
    const o = D().milp(P, bin), r = D().rilassamento(P, bin);
    const out = { P, inst, d, stato: o.stato, zLP: r.stato === "ottimo" ? r.z : null };
    if (o.stato !== "ottimo") return out;
    const t0 = (x) => (Math.abs(x) < 1e-7 ? 0 : x);
    out.z = o.z;
    out.x = [0, 1, 2].map((l) => (o.x[X(l)] > 0.5 ? 1 : 0));
    out.y = [0, 1, 2].map((l) => [0, 1, 2, 3].map((k) => t0(o.x[Y(l, k)])));
    out.xLP = r.stato === "ottimo" ? [0, 1, 2].map((l) => t0(r.x[X(l)])) : null;
    out.inst = inst;
    out.costoInst = out.x.reduce((s, x, l) => s + x * inst[l], 0);
    return out;
  }

  const vLoc = {
    etichetta: T("Localizzazione capacitata", "Capacitated facility location"),
    cursori: [
      { nome: T("\\text{installazione}\\ i_3", "\\text{opening}\\ i_3"), min: 10, max: 200, step: 10, val: 70,
        fmt: (x) => `${x} €`, descr: T("costo di installazione della sede 3", "opening cost of site 3") },
      { nome: T("\\text{domanda}\\ d_4", "\\text{demand}\\ d_4"), min: 5, max: 60, step: 5, val: 20,
        fmt: (x) => T(`${x} litri`, `${x} litres`), descr: T("domanda del cliente 4", "demand of customer 4") },
    ],
    calcola,
    formula(R, v, st) {
      const H = L();
      const sim = `\\min ~~ \\sum_{l=1}^{m} ${st.col("a", "i_l")}\\, x_l + \\sum_{l=1}^{m}\\sum_{c=1}^{n} t_{lc}\\, y_{lc} & & \\\\
        ${SA()} \\quad u_l\\, x_l - \\sum_{c=1}^{n} y_{lc} &\\ge 0, & \\forall l \\in \\{1, 2, \\dots, m\\}, \\\\
        \\sum_{l=1}^{m} y_{lc} &= ${st.col("b", "d_c")}, & \\forall c \\in \\{1, 2, \\dots, n\\}, \\\\
        x_l &\\in \\{0, 1\\}, & \\forall l \\in \\{1, 2, \\dots, m\\}, \\\\
        y_{lc} &\\ge 0, & \\forall l \\in \\{1, 2, \\dots, m\\},\\ \\forall c \\in \\{1, 2, \\dots, n\\}.`;
      const vars = [];
      for (let l = 0; l < NS; l++) vars[X(l)] = `x_{${l + 1}}`;
      for (let l = 0; l < NS; l++) for (let k = 0; k < NC; k++) vars[Y(l, k)] = `y_{${l + 1}${k + 1}}`;
      const ys = [];
      for (let l = 0; l < NS; l++) for (let k = 0; k < NC; k++) ys.push(Y(l, k));
      const num = H.numLP({ senso: "min", vars, c: R.P.c, cifre: 0, righe: R.P.A.map((a, q) => ({ a, rel: R.P.rel[q], rhs: R.P.b[q] })),
        dominio: [{ cols: [0, 1, 2], rel: "\\in", rhs: "\\{0, 1\\}" }, { cols: ys, rel: ">=", rhs: "0" }] },
        T(`Il modello MILP dell'istanza: ${NV} variabili (${NS} binarie, ${NS * NC} continue), ${R.P.b.length} vincoli.`,
          `The MILP model of the instance: ${NV} variables (${NS} binary, ${NS * NC} continuous), ${R.P.b.length} constraints.`));
      const TAB = H.DV.tabelle(H.DV.tab(T("Dimensioni", "Sizes"), ["\\(m\\)", "\\(n\\)"], [[String(NS), String(NC)]]),
        H.DV.tab(T("Sedi", "Sites"), [T("sede \\(l\\)", "site \\(l\\)"), "\\(i_l\\) (€)", T("\\(u_l\\) (litri)", "\\(u_l\\) (litres)"),
          ...[1, 2, 3, 4].map((k) => `\\(t_{l${k}}\\) (€)`)],
          [0, 1, 2].map((l) => [String(l + 1), String(R.inst[l]), String(DATI.u[l]), ...DATI.t[l].map(String)])),
        H.DV.tab(T("Clienti", "Customers"), [T("cliente \\(c\\)", "customer \\(c\\)"), "1", "2", "3", "4"],
          [[T("\\(d_c\\) (litri)", "\\(d_c\\) (litres)"), ...R.d.map(String)]]));
      const testo = T(
        "<b>Il problema.</b> Un'azienda deve servire alcuni clienti e ha individuato alcune sedi candidate. Decidiamo quali sedi installare e quanti litri spedire da ogni sede a ogni cliente. " +
        "L'obiettivo è minimizzare il costo totale, di installazione e di trasporto. I vincoli: la domanda di ogni cliente è soddisfatta esattamente, da una sede non installata non parte nulla e una sede installata non supera la sua capacità." +
        "<br><b>Variabili:</b> \\(x_l \\in \\{0,1\\}\\): vale 1 se si installa la sede \\(l\\), con \\(l \\in \\{1, \\dots, m\\}\\); \\(y_{lc} \\ge 0\\): litri spediti dalla sede \\(l\\) al cliente \\(c\\), con \\(l \\in \\{1, \\dots, m\\}\\) e \\(c \\in \\{1, \\dots, n\\}\\)." +
        "<br><b>Dati:</b> \\(m\\): numero di sedi; \\(n\\): numero di clienti; \\(i_l\\): costo di installazione della sede \\(l\\) (€); \\(u_l\\): capacità della sede \\(l\\) (litri); " +
        "\\(t_{lc}\\): costo di trasporto di un litro dalla sede \\(l\\) al cliente \\(c\\) (€); \\(d_c\\): domanda del cliente \\(c\\) (litri); con \\(l \\in \\{1, \\dots, m\\}\\) e \\(c \\in \\{1, \\dots, n\\}\\)." + TAB,
        "<b>The problem.</b> A company has to serve some customers and has identified some candidate sites. We decide which sites to open and how many litres to ship from each site to each customer. " +
        "The objective is to minimize the total cost, of opening and of transport. The constraints: the demand of every customer is met exactly, nothing leaves a site that is not open, and an open site does not exceed its capacity." +
        "<br><b>Variables:</b> \\(x_l \\in \\{0,1\\}\\): equals 1 if site \\(l\\) is opened, with \\(l \\in \\{1, \\dots, m\\}\\); \\(y_{lc} \\ge 0\\): litres shipped from site \\(l\\) to customer \\(c\\), with \\(l \\in \\{1, \\dots, m\\}\\) and \\(c \\in \\{1, \\dots, n\\}\\)." +
        "<br><b>Data:</b> \\(m\\): number of sites; \\(n\\): number of customers; \\(i_l\\): opening cost of site \\(l\\) (€); \\(u_l\\): capacity of site \\(l\\) (litres); " +
        "\\(t_{lc}\\): cost of transporting one litre from site \\(l\\) to customer \\(c\\) (€); \\(d_c\\): demand of customer \\(c\\) (litres); with \\(l \\in \\{1, \\dots, m\\}\\) and \\(c \\in \\{1, \\dots, n\\}\\)." + TAB);
      const html = `<div class="plm"><p class="plm-testo">${testo}</p>${rigaCapitolo()}` +
        `<div class="plm-sim">\\(\\displaystyle \\begin{aligned} ${sim} \\end{aligned}\\)</div>` +
        `<details class="plm-num"><summary>${T("Modello numerico con i dati attuali", "Numerical model with the current data")}</summary>` +
        `<div class="plm-num-corpo">${num}</div></details></div>`;
      return H.FONDO.sposta(st, html);
    },
    // la figura: sedi a sinistra (quadrati, piene se aperte), clienti a destra (cerchi), archi spessi quanto i litri spediti
    disegna(crea, R, v, C, S) {
      const M = window.GI_MIP, F = FIG(), FR = L().FR, W = S.W, H = S.H;
      const titolo = R.stato === "ottimo"
        ? T(`Soluzione ottima: sedi aperte x̃(MILP) e litri spediti ỹ(MILP) (z(MILP) = ${FR.euroTxt(R.z)})`, `Optimal solution: open sites x̃(MILP) and litres shipped ỹ(MILP) (z(MILP) = ${FR.euroTxt(R.z)})`)
        : T("Nessuna soluzione ammissibile", "No feasible solution");
      M.scritta(crea, W / 2, H - 16, titolo, { fontSize: 13.5, strokeColor: F.blu, cssStyle: "font-weight:700" });
      if (R.stato !== "ottimo") return;
      const xs = W * 0.3, xc = W * 0.72, lato = Math.max(30, Math.min(44, H / 15)), rag = Math.max(15, Math.min(21, H / 26));
      // nodi distanziati su tutta l'altezza (niente spazio vuoto sotto il titolo): in alto c'è posto per il valore x̃(LP⁺)
      const alto = H - 44 - lato / 2 - 16, basso = 64 + lato / 2 + 10;
      const ys = [0, 1, 2].map((l) => alto - (alto - basso) * l / (NS - 1)), yc = [0, 1, 2, 3].map((k) => alto - (alto - basso) * k / (NC - 1));
      const qMax = Math.max(...R.d);
      // archi: prima quelli vuoti, poi quelli usati (sopra)
      const archi = [];
      for (let l = 0; l < NS; l++) for (let k = 0; k < NC; k++) archi.push([l, k, R.y[l][k]]);
      archi.sort((a, b) => (a[2] > 1e-9) - (b[2] > 1e-9));
      for (const [l, k, q] of archi) {
        const x0 = xs + lato / 2 + 2, y0 = ys[l], dx = xc - x0, dy = yc[k] - y0, Lg = Math.hypot(dx, dy), ux = dx / Lg, uy = dy / Lg;
        const p1 = [xc - ux * (rag + 4), yc[k] - uy * (rag + 4)], pieno = q > 1e-9;
        crea("arrow", [[x0, y0], p1], { strokeColor: pieno ? F.teal : C.grigio, strokeOpacity: pieno ? 1 : 0.55, strokeWidth: pieno ? 2 + 7 * q / qMax : 1.1,
          dash: pieno ? 0 : 2, fixed: true, highlight: false, withLabel: false, lastArrow: { type: 2, size: pieno ? 3 : 6 } });
        if (pieno) M.scritta(crea, x0 + (p1[0] - x0) * 0.62 - uy * 13, y0 + (p1[1] - y0) * 0.62 + ux * 13, FR.txt(q), { fontSize: 13, strokeColor: F.teal,
          display: "html", cssStyle: "font-weight:700;background:var(--md-default-bg-color);padding:0 .25em;border-radius:3px" });
      }
      // sedi: aperte piene, chiuse tratteggiate; accanto i litri usati sulla capacità e il valore nel rilassamento
      ys.forEach((y, l) => {
        const aperta = R.x[l] === 1, usati = R.y[l].reduce((s, q) => s + q, 0);
        M.rett(crea, xs - lato / 2, y - lato / 2, xs + lato / 2, y + lato / 2, aperta
          ? { fillColor: F.teal, fillOpacity: 1, strokeColor: F.teal, strokeWidth: 2 }
          : { fillColor: "none", strokeColor: C.grigio, strokeWidth: 1.8, dash: 2 });
        M.scritta(crea, xs, y, String(l + 1), { fontSize: 15, strokeColor: aperta ? "#ffffff" : C.muted, cssStyle: "font-weight:700" });
        const xt = xs - lato / 2 - 12;
        M.scritta(crea, xt, y + 17, T(`sede ${l + 1}: ${aperta ? "aperta" : "chiusa"}`, `site ${l + 1}: ${aperta ? "open" : "closed"}`), { anchorX: "right", fontSize: 12.5, strokeColor: aperta ? C.testo : C.muted, cssStyle: "font-weight:700" });
        M.scritta(crea, xt, y, T(`i = ${R.inst[l]} €, u = ${DATI.u[l]} litri`, `i = ${R.inst[l]} €, u = ${DATI.u[l]} litres`), { anchorX: "right", fontSize: 12, strokeColor: C.muted });
        M.scritta(crea, xt, y - 16, aperta ? T(`spedisce ${FR.txt(usati)} su ${DATI.u[l]}`, `ships ${FR.txt(usati)} of ${DATI.u[l]}`) : "", { anchorX: "right", fontSize: 12, strokeColor: C.testo });
        if (R.xLP) M.scritta(crea, xs, y + lato / 2 + 11, `x̃${"₁₂₃"[l]}(LP⁺) = ${FR.txt(R.xLP[l])}`, { fontSize: 12, strokeColor: F.rosso, cssStyle: "font-weight:700" });
      });
      // clienti con la domanda
      yc.forEach((y, k) => {
        M.pallino(crea, xc, y, { size: rag, fillColor: F.verde, strokeColor: F.verde });
        M.scritta(crea, xc, y, String(k + 1), { fontSize: 14, strokeColor: "#ffffff", cssStyle: "font-weight:700" });
        M.scritta(crea, xc + rag + 10, y + 8, T(`cliente ${k + 1}`, `customer ${k + 1}`), { anchorX: "left", fontSize: 12.5, strokeColor: C.testo, cssStyle: "font-weight:700" });
        M.scritta(crea, xc + rag + 10, y - 9, T(`d = ${R.d[k]} litri`, `d = ${R.d[k]} litres`), { anchorX: "left", fontSize: 12, strokeColor: C.muted });
      });
      M.scritta(crea, W / 2, 34, T("arco pieno: litri spediti nell'ottimo; tratteggio: nessuna spedizione", "solid arc: litres shipped in the optimum; dashed: no shipment"), { fontSize: 11.5, strokeColor: C.muted });
      M.scritta(crea, W / 2, 16, T("in rosso: il valore x̃(LP⁺) della sede nel rilassamento continuo", "in red: the value x̃(LP⁺) of the site in the continuous relaxation"), { fontSize: 11.5, strokeColor: F.rosso });
    },
    letture: () => "",
    soluzione(R) {
      if (R.stato !== "ottimo") return "";
      const H = L(), FR = H.FR;
      return H.SOL.blocco(
        H.SOL.valore(T("Costo ottimo", "Optimal cost"), FR.euro(R.z), R.zLP === null ? null : FR.euro(R.zLP), R.zLP === null ? null : FR.gap(R.z, R.zLP)),
        [H.SOL.tab(T("Sedi aperte \\(\\tilde x(\\text{MILP})\\) e litri spediti \\(\\tilde y(\\text{MILP})\\)", "Open sites \\(\\tilde x(\\text{MILP})\\) and litres shipped \\(\\tilde y(\\text{MILP})\\)"),
          [T("sede \\(l\\)", "site \\(l\\)"), "\\(\\tilde x_l\\)", ...[1, 2, 3, 4].map((k) => `\\(c = ${k}\\)`)],
          [0, 1, 2].map((l) => [String(l + 1), String(R.x[l]), ...R.y[l].map((q) => H.SOL.z(q))]))],
        T("«—»: nessuna spedizione.", "«—»: no shipment."));
    },
    domanda: T("Con \\(i_3 = 110\\) € la sede 3 chiude e si apre la 1. Con \\(d_4 = 45\\) litri si aprono tutte e tre.",
      "With \\(i_3 = 110\\) € site 3 closes and site 1 opens. With \\(d_4 = 45\\) litres all three open."),
  };

  window.GI_RICETTE["mip-localizzazione"] = () => L().ricettaVoce({ titolo: T("Localizzazione capacitata", "Capacitated facility location") }, vLoc);
  // per le prove automatiche: solo il calcolo
  window.GI_MIP_LOCALIZZAZIONE = { calcola, DATI };
})();
