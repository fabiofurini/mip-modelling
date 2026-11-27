/* Laboratorio di «Modellazione MIP / MIP Modelling»: l'app di copertina.
 *
 *   mip-lotti   problema 9.1 (lotti con costo fisso di setup), istanza del capitolo: 5 giorni,
 *               d = 20, 10, 30, 40, 10; p = 2, 3, 2, 3, 2; q = 50; h = 1; r_0 = r_n = 0;
 *               M_t = domanda residua (110, 90, 80, 50, 10). Ottimo z = 390, z(LP+) = 3890/11 (numeri non interi come frazioni, FR).
 *               Cursori (al massimo due): costo di setup q e costo di giacenza h. Una sola figura: il piano ottimo.
 *
 * Riquadri standard di tutte le app (Fabio, 26/11/2026; RIQ, SOL, CAP qui sotto, usati anche da gi-mip-progetti.js,
 * gi-mip-localizzazione.js, gi-mip-logica.js): a sinistra «Il problema», «Dati» (significati e tabelle, sempre
 * visibile), «Modello» (variabili e modello simbolico, richiudibile: aperto nella home, chiuso nel laboratorio), la
 * figura e la riga del capitolo; a destra i cursori, «Soluzione ottima» (tabelle, poi valore ottimo, rilassamento
 * continuo e gap) e «Prova tu» (richiudibile, gi-comune.js); in fondo al riquadro, a tutta larghezza, il blocco
 * richiudibile «Modello numerico con i dati attuali» in forma matriciale stretta (una colonna per variabile, una riga per vincolo),
 * con il corpo del carattere che si adatta alla larghezza. Gli helper (figure nello stile dei capitoli,
 * arrayLP, SOL, FONDO, DV, ricetta a voci) sono copiati da gi-pl-app.js e gi-ott.js di Modellazione PL.
 *
 * Il calcolo usa il simplesso e l'enumerazione delle 32 assegnazioni delle binarie di gi-mip-d.js
 * (window.GI_MIP_D.milp e .rilassamento), letti al momento del calcolo: l'ordine dei file non conta.
 */
(function () {
  "use strict";
  const GI = window.GI, M = window.GI_MIP;
  const T = GI.T;
  const D = () => window.GI_MIP_D;
  window.GI_RICETTE = window.GI_RICETTE || {};
  const n = (x, c = 2) => GI.num(x, c), nt = (x, c = 2) => GI.numTxt(x, c);
  const tx = (s) => `\\(${s}\\)`;

  // ================================================================ numeri non interi come frazioni
  /* Fabio, 25/11/2026: niente numeri con la virgola, frazioni. Un valore in virgola mobile del simplesso diventa la
   * frazione p/q delle frazioni continue, con q <= maxDen e |p/q - x| < tol; se non ce n'è una, resta il decimale. */
  const razionale = (x, maxDen = 1000, tol = 1e-9) => {
    if (!isFinite(x)) return null;
    const s = x < 0 ? -1 : 1, a0 = Math.abs(x);
    let h1 = 1, h2 = 0, k1 = 0, k2 = 1, v = a0;
    for (let i = 0; i < 40; i++) {
      const a = Math.floor(v), h = a * h1 + h2, k = a * k1 + k2;
      if (k > maxDen) break;
      if (Math.abs(h / k - a0) < tol) return [s * h, k];
      h2 = h1; h1 = h; k2 = k1; k1 = k;
      if (v - a < 1e-15) break;
      v = 1 / (v - a);
    }
    return null;
  };
  const mcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a || 1; };
  const FR = {
    /** per il TeX: intero, \frac{p}{q}, oppure il decimale con c cifre */
    tex(x, c = 2) {
      const r = razionale(x);
      if (!r) return n(x, c);
      if (r[1] === 1) return n(r[0], 0);
      return `${r[0] < 0 ? "-" : ""}\\frac{${Math.abs(r[0])}}{${r[1]}}`;
    },
    /** per il testo semplice (grafici, celle): «3/11» */
    txt(x, c = 2) {
      const r = razionale(x);
      if (!r) return nt(x, c);
      if (r[1] === 1) return nt(r[0], 0);
      return `${r[0] < 0 ? "−" : ""}${Math.abs(r[0])}/${r[1]}`;
    },
    /** importo in euro, come TeX in linea */
    euro: (x) => `\\(${FR.tex(x)}\\) €`,
    /** importo in euro, testo semplice */
    euroTxt: (x) => `${FR.txt(x)} €`,
    /** gap (a - b)/a come frazione esatta (da a e b razionali) e percentuale intera: «\frac{40}{429} \approx 9\,\%» */
    gap(a, b) {
      const ra = razionale(a), rb = razionale(b), pct = `${Math.round(100 * (a - b) / a)}\\,\\%`;
      if (!ra || !rb) return `\\approx ${pct}`;
      // (pa/qa - pb/qb) / (pa/qa) = (pa qb - pb qa) / (pa qb)
      let p = ra[0] * rb[1] - rb[0] * ra[1], q = ra[0] * rb[1];
      if (p === 0) return "0";
      const g = mcd(p, q); p /= g; q /= g;
      if (q < 0) { p = -p; q = -q; }
      return q === 1 ? `${p}` : q <= 10000 ? `\\frac{${p}}{${q}} \\approx ${pct}` : `\\approx ${pct}`;
    },
  };

  // ================================================================ lo stile delle figure dei capitoli
  const FIG = () => (M.scuro()
    ? { blu: "#D6E4F0", teal: "#22A6C7", rosso: "#E5675A", verde: "#3DBB6E", arancio: "#E8923F", grigio: "#A3AFB0", navy: "#9CC3E6", fascia: "#4DABF7" }
    : { blu: "#16324A", teal: "#0E7490", rosso: "#C0392B", verde: "#1E8449", arancio: "#CA6F1E", grigio: "#7F8C8D", navy: "#16324A", fascia: "#1971C2" });
  /** tacche «belle» per l'intervallo [a, b] (gi-ott.js) */
  function tacche(a, b, quante = 5) {
    const grezzo = (b - a) / quante, e = Math.pow(10, Math.floor(Math.log10(grezzo)));
    const f = grezzo / e, passo = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * e;
    const out = [];
    for (let v = Math.ceil(a / passo - 1e-9) * passo; v <= b + 1e-9 * passo; v += passo) out.push(Math.abs(v) < passo * 1e-9 ? 0 : v);
    return { valori: out, passo };
  }
  /** un riquadro con assi, tacche e griglia orizzontale (gi-ott.js, GI_OTT.pannello) */
  function pannello(crea, P, C, opz = {}) {
    const X = (x) => P.X0 + ((x - P.xa) / (P.xb - P.xa)) * (P.X1 - P.X0);
    const Y = (y) => P.Y0 + ((y - P.ya) / (P.yb - P.ya)) * (P.Y1 - P.Y0);
    if (crea) {
      const fs = opz.fontSize || 11, cifre = (p) => Math.max(0, -Math.floor(Math.log10(p) + 1e-9));
      const tX = tacche(P.xa, P.xb, opz.nTx || 6), tY = tacche(P.ya, P.yb, opz.nTy || 4);
      const dx = (P.X1 - P.X0) * 0.012, dy = (P.Y1 - P.Y0) * 0.03;
      for (const v of tY.valori) {
        if (opz.ymax !== undefined && v > opz.ymax + 1e-9) continue;
        M.linea(crea, P.X0, Y(v), P.X1, Y(v), { strokeColor: C.line, strokeWidth: 1 });
        M.scritta(crea, P.X0 - dx, Y(v), (opz.fy || ((u) => GI.numTxt(u, cifre(tY.passo))))(v), { anchorX: "right", fontSize: fs, strokeColor: C.muted });
      }
      for (const v of tX.valori) {
        const s = (opz.fx || ((u) => GI.numTxt(u, cifre(tX.passo))))(v);
        if (!s) continue;
        M.linea(crea, X(v), P.Y0, X(v), P.Y0 - 4, { strokeColor: C.muted, strokeWidth: 1 });
        M.scritta(crea, X(v), P.Y0 - 7, s, { anchorY: "top", fontSize: fs, strokeColor: C.muted });
      }
      M.linea(crea, P.X0, P.Y0, P.X1, P.Y0, { strokeColor: C.muted, strokeWidth: 1.2 });
      M.linea(crea, P.X0, P.Y0, P.X0, P.Y1, { strokeColor: C.muted, strokeWidth: 1.2 });
    }
    return Object.assign({}, P, { X, Y });
  }
  /** un pannello nello stile delle figure: titolo in grassetto sopra, nomi degli assi fuori */
  function figura(crea, P, C, opz = {}) {
    const Q = pannello(crea, P, C, opz);
    const F = FIG();
    if (P.titolo) M.scritta(crea, (P.X0 + P.X1) / 2, P.Y1 + 7, P.titolo, { anchorY: "bottom", fontSize: 13.5, strokeColor: F.blu, cssStyle: "font-weight:700" });
    if (P.nx) M.scritta(crea, (P.X0 + P.X1) / 2, P.Y0 - 28, P.nx, { anchorY: "top", fontSize: 12, strokeColor: C.testo });
    if (P.ny) M.scritta(crea, P.X0 - 44, (P.Y0 + P.Y1) / 2, P.ny, { fontSize: 12, strokeColor: C.testo, rotate: 90 });
    return Q;
  }
  /** legenda in riga, in alto dentro il pannello (va a capo se serve).
   *  tipo: "barra", "fascia" (sfondo chiaro), "linea", "lineaPunti", "tratteggioPunti" */
  function legendaRiga(crea, P, voci, C) {
    const fs = 11.5, lung = 20, passo = 17;
    let x = P.X0 + 10, y = P.Y1 - 12;
    voci.forEach(([col, testo, tipo]) => {
      const largo = lung + 7 + testo.length * fs * 0.55 + 18;
      if (x + largo > P.X1 - 4 && x > P.X0 + 10) { x = P.X0 + 10; y -= passo; }
      if (tipo === "barra") M.rett(crea, x + 2, y - 5, x + lung - 2, y + 5, { fillColor: col, fillOpacity: 1, strokeColor: col, strokeWidth: 0.5 });
      else if (tipo === "fascia") M.rett(crea, x, y - 7, x + lung, y + 7, { fillColor: col, fillOpacity: 0.13, strokeColor: col, strokeOpacity: 0.35, strokeWidth: 1 });
      else {
        M.linea(crea, x, y, x + lung, y, { strokeColor: col, strokeWidth: 2.2, dash: tipo.startsWith("tratteggio") ? 2 : 0 });
        if (tipo.endsWith("Punti")) M.pallino(crea, x + lung / 2, y, { size: 3.5, fillColor: col, strokeColor: col });
      }
      M.scritta(crea, x + lung + 7, y, testo, { anchorX: "left", fontSize: fs, strokeColor: C.testo });
      x += largo;
    });
  }
  /** spezzata con i pallini (matplotlib "-o") */
  const lineaPunti = (crea, P, xs, ys, col, opz = {}) => {
    crea("curve", [xs.map(P.X), ys.map(P.Y)], { strokeColor: col, strokeWidth: opz.spessore || 2.2, dash: opz.dash || 0, fixed: true, highlight: false });
    xs.forEach((x, k) => M.pallino(crea, P.X(x), P.Y(ys[k]), Object.assign({ size: opz.r || 3.5, fillColor: col, strokeColor: col }, opz.punto || {})));
  };
  const MF = { sx: 66, dx: 14, basso: 54, alto: 30 };

  // ================================================================ il capitolo che spiega il modello
  const CAPITOLO = { lotti: ["produzione-1/", "production-1/", "Lotti con costo fisso di setup", "Lot sizing with a fixed setup cost"] };
  const radice = () => {
    try { if (window.__md_scope) return new URL(window.__md_scope); } catch (e) { /* sotto */ }
    const cfg = document.getElementById("__config");
    try { return new URL(JSON.parse(cfg.textContent).base + "/", location.href); } catch (e) { return new URL("./", location.href); }
  };
  const rigaCapitolo = (chiave) => {
    const c = CAPITOLO[chiave];
    if (!c) return "";
    const url = new URL(GI.EN ? c[1] : c[0], radice()).href;
    if (new URL(url).pathname.replace(/\/$/, "") === location.pathname.replace(/(index\.html)?\/?$/, "")) return "";
    return `<p class="plm-cap">${T("Il modello è spiegato nel capitolo", "The model is explained in the chapter")} <a href="${url}">${GI.EN ? c[3] : c[2]}</a>.</p>`;
  };

  // ================================================================ il modello sopra il grafico (gi-pl-app.js)
  const NUM = { aperto: false };
  document.addEventListener("toggle", (e) => {
    const d = e.target;
    if (d && d.classList && d.classList.contains("plm-num")) { NUM.aperto = d.open; window.dispatchEvent(new Event("resize")); }
  }, true);
  if (window.ResizeObserver) {
    let attesa = 0;
    const ro = new ResizeObserver(() => { clearTimeout(attesa); attesa = setTimeout(() => window.dispatchEvent(new Event("resize")), 120); });
    // il modello numerico non scorre di lato: il corpo del carattere si adatta alla larghezza del riquadro
    // (misurando le celle vere, mjx-table), fra 0,75em e 1,45em
    const BASE = 1.45, MINIMO = 0.75;
    const adatta = (cont) => {
      const box = cont.closest(".plm-array");
      if (!box || !box.clientWidth) return;
      const ora = parseFloat(box.dataset.fs || BASE), largo = (cont.querySelector("mjx-table") || cont).getBoundingClientRect().width / ora;
      if (!largo) return;
      const fs = Math.max(MINIMO, Math.min(BASE, Math.floor(((box.clientWidth - 12) / largo) * 100) / 100));
      if (Math.abs(fs - ora) > 0.004) { box.dataset.fs = fs; box.style.fontSize = fs + "em"; }
    };
    const roArray = new ResizeObserver((voci) => voci.forEach((v) => adatta(v.target)));
    const osserva = () => {
      document.querySelectorAll(".gi-app-intera .gi-formula:not([data-plm])").forEach((f) => { f.dataset.plm = "1"; ro.observe(f); });
      document.querySelectorAll(".plm-array mjx-container:not([data-plm])").forEach((m) => { m.dataset.plm = "1"; roArray.observe(m); });
    };
    new MutationObserver(osserva).observe(document.documentElement, { childList: true, subtree: true });
    window.addEventListener("resize", () => document.querySelectorAll(".plm-array mjx-container").forEach(adatta));
  }
  const SA = () => T("\\text{soggetto a}", "\\text{subject to}");
  const PER = (i, a, b) => `\\forall ${i} \\in \\{${a}, \\dots, ${b}\\}`;
  const REL = { "<=": "\\le", "=": "=", ">=": "\\ge", "><": "\\gtreqless" };
  /** il modello numerico in un solo array (GI_PL_NUM.arrayLP di gi-pl-app.js, senza i pezzi a capo):
   *  una colonna per variabile, segni in colonne proprie, celle vuote per le variabili assenti, relazione e
   *  termine noto a destra, in fondo le righe del dominio.
   *  P = { senso, vars, c, righe: [{ a, rel, rhs, cifre }], dominio: [{ cols, rel, rhs }], cifre, cifreObj } */
  const arrayLP = (P) => {
    const N = P.vars.length, tutte = [...Array(N).keys()];
    const nz = (a) => a && Math.abs(a) > 1e-12;
    const rhsTex = (r, c) => (typeof r === "number" ? n(r, c ?? 2) : r ?? "");
    const righe = [{ lab: P.senso === "max" ? "\\max" : "\\min", c: P.c, cifre: P.cifreObj ?? P.cifre ?? 3 }];
    P.righe.forEach((r, i) => righe.push({ lab: i ? "" : SA(), c: r.a, rel: r.rel, rhs: rhsTex(r.rhs, r.cifre ?? P.cifre), cifre: r.cifre ?? P.cifre ?? 3 }));
    (P.dominio || [{ cols: tutte, rel: ">=", rhs: "0" }]).forEach((d) => righe.push({ dominio: d.cols, rel: d.rel, rhs: d.rhs }));
    const br = (s) => (s === "" ? "" : /^\\text/.test(s) ? s : `{${s}}`);
    const out = [];
    righe.forEach((r, ir) => {
      const usa = (j) => (r.dominio ? r.dominio.includes(j) : nz(r.c[j]));
      const ultimoDom = r.dominio ? Math.max(...r.dominio) : -1;
      let visto = false;
      const celle = [r.lab || ""];
      for (let j = 0; j < N; j++) {
        let s = "", t = "";
        if (usa(j)) {
          if (r.dominio) t = P.vars[j] + (j === ultimoDom ? "" : ",");
          else {
            const a = r.c[j];
            t = (Math.abs(Math.abs(a) - 1) < 1e-12 ? "" : n(Math.abs(a), r.cifre) + "\\,") + P.vars[j];
            s = a < 0 ? "-" : visto ? "+" : "";
            visto = true;
          }
        }
        if (j === 0) celle.push(s === "-" ? "-" + t : t);   // la prima colonna non ha la colonna del segno
        else celle.push(s, t);
      }
      celle.push(r.rel ? REL[r.rel] || r.rel : "", r.rhs ?? "");
      while (celle.length && celle[celle.length - 1] === "") celle.pop();
      out.push(celle.map(br).join(" & ") + (ir === righe.length - 1 ? "\n" : " \\\\[1ex]\n"));
    });
    return `\\begin{array}{rr${"cr".repeat(N - 1)}cr} ${out.join("")}\\end{array}`;
  };
  const numLP = (P, titolo) => `<p class="plm-tit">${titolo}</p><div class="plm-riga plm-array">\\(\\displaystyle ${arrayLP(P)}\\)</div>`;
  /** il blocco completo: problema, rimando al capitolo, modello simbolico, modello numerico richiudibile */
  const modello = (testo, simbolico, num, cap) =>
    `<div class="plm"><p class="plm-testo">${testo}</p>${rigaCapitolo(cap)}` +
    `<div class="plm-sim">\\(\\displaystyle \\begin{aligned} ${simbolico} \\end{aligned}\\)</div>` +
    `<details class="plm-num"${NUM.aperto ? " open" : ""}><summary>${T("Modello numerico con i dati attuali", "Numerical model with the current data")}</summary>` +
    `<div class="plm-num-corpo">${num}</div></details></div>`;

  // ================================================================ «Soluzione ottima» sotto il grafico (GI_PL_SOL)
  const SOL = {
    /** il riquadro va nella colonna di destra, sotto i cursori e «Azzera», sopra il «Prova tu» (Fabio, 26/11/2026) */
    mostra(st, html) {
      const dx = st.el.querySelector(".gi-corpo > div:last-child"), lett = dx && dx.querySelector(":scope > .gi-letture");
      if (!dx) return;
      let b = st.el.querySelector(".plm-sol");
      if (!b) b = GI.h("div", { class: "plm-sol plm-box" });
      if (b.parentElement !== dx) { if (lett) lett.before(b); else dx.append(b); }
      const testo = html ? `<p class="plm-box-tit">${T("Soluzione ottima", "Optimal solution")}</p>${html}` : "";
      if (b.dataset.html === testo) return;
      b.dataset.html = testo;
      b.hidden = !html;
      b.innerHTML = GI.mj(testo);
      if (html) GI.typeset(b);
    },
    z: (x, c = 2) => (Math.abs(x) < 0.5 * Math.pow(10, -c) ? "—" : FR.txt(x, c)),
    tab: (titolo, intest, righe) => `<div class="plm-sol-t">${titolo ? `<p>${titolo}</p>` : ""}${M.tab(intest, righe)}</div>`,
    blocco: (valore, tabelle = [], nota = "") =>   // prima i valori delle variabili, sotto il valore ottimo (Fabio, 26/11/2026)
      (tabelle.length ? `<div class="plm-sol-tabs">${tabelle.join("")}</div>` : "") + (nota ? `<p class="plm-sol-nota">${nota}</p>` : "") +
      `<div class="plm-sol-val">${valore}</div>`,
    /** il valore ottimo e, sotto, in breve, il rilassamento continuo e il gap
     *  nome: «Costo ottimo»…; z, zLP: testi già formattati; gap: testo TeX del gap (o null) */
    valore: (nome, z, zLP, gap) =>
      `<p class="plm-sol-z">${T("Valore ottimo", "Optimal value")} \\(z(\\text{MILP})\\) = <b>${z}</b></p>` +
      `<p class="plm-sol-lp">${T("Rilassamento continuo", "Continuous relaxation")} \\(z(\\text{LP}^+)\\) = ${zLP === null ? "—" : zLP} · <span class="plm-nowrap">gap ${gap === null ? "—" : `\\(${gap}\\)`}</span></p>`,
  };

  // ================================================================ il modello numerico in fondo al riquadro (GI_PL_FONDO)

  // ================================================================ riquadri standard (Fabio, 26/11/2026)
  /* Ogni app di modellazione ha gli stessi riquadri: «Il problema», «Variabili», «Dati» (significati e tabelle),
   * «Modello» (simbolico); poi «Soluzione ottima» e «Prova tu». Le app scrivono ancora il testo con le voci
   * <b>Il problema.</b> … <br><b>Variabili:</b> … <br><b>Dati:</b> …: qui lo si divide nei riquadri. */
  const RIQ = {
    voce(seg) {
      const m = seg.match(/^\s*<b>\s*([^<]*?)\s*[.:]\s*<\/b>\s*/);
      if (!m) return null;
      const t = m[1].toLowerCase(), resto = seg.slice(m[0].length);
      if (/^(il problema|the problem)$/.test(t)) return ["problema", resto];
      if (/^(variabili|variables)$/.test(t)) return ["variabili", resto];
      if (/^(dati|data)$/.test(t)) return ["dati", resto];
      return null;
    },
    box(cls, tit, corpo) { return `<div class="plm-box ${cls}"><p class="plm-box-tit">${tit}</p>${corpo}</div>`; },
    /** blocco richiudibile con lo stesso aspetto dei riquadri (Fabio, 26/11/2026): il titolo resta sempre visibile */
    scatola(cls, tit, corpo, aperto) {
      return `<details class="plm-box ${cls}"${aperto ? " open" : ""}><summary class="plm-box-tit">${tit}</summary><div class="plm-box-corpo">${corpo}</div></details>`;
    },
    /** il «Modello» è aperto all'avvio nella home (data-vetrina), chiuso nelle pagine del laboratorio; poi resta come lo lascia chi legge */
    modelloAperto(st) {
      const d = st && st.el ? st.el.dataset.plmMod : undefined;
      return d !== undefined ? d === "1" : !!(st && st.el && st.el.dataset.vetrina);
    },
    applica(html, st) {
      if (typeof html !== "string" || html.indexOf('class="plm-testo"') < 0 || html.indexOf("plm-box") >= 0) return html;
      const tpl = document.createElement("div");
      tpl.innerHTML = html;
      const plm = tpl.querySelector(".plm");
      if (!plm) return html;
      // la riga «Il modello è spiegato nel capitolo …» va in fondo al riquadro, dopo la figura
      const cap = plm.querySelector(":scope > .plm-cap");
      if (cap) { if (st) CAP.mostra(st, cap.outerHTML); cap.remove(); } else if (st) CAP.mostra(st, "");
      const sez = { problema: [], variabili: [], dati: [] };
      let cur = "problema", tabelle = null;
      for (const n of Array.from(plm.children)) {
        if (n.matches("p.plm-testo")) {
          for (const seg of n.innerHTML.split(/<br\s*\/?>/i)) {
            if (!seg.trim()) continue;
            const v = RIQ.voce(seg);
            if (v) { cur = v[0]; if (v[1].trim()) sez[cur].push(v[1]); } else sez[cur].push(seg);
          }
          n.remove();
        } else if (n.matches("div.plm-dati")) {   // più blocchi di tabelle: un solo riquadro «Dati»
          if (!tabelle) tabelle = n;
          else { n.querySelectorAll(":scope > .plm-dati-tit").forEach((t) => t.remove()); tabelle.append(...n.childNodes); }
          n.remove();
        }
      }
      let out = "";
      if (sez.problema.length) out += RIQ.box("plm-box-problema", T("Il problema", "The problem"), `<p>${sez.problema.join("<br>")}</p>`);
      if (sez.dati.length || tabelle) {
        const sig = sez.dati.length ? `<p class="plm-dati-sig">${sez.dati.join("<br>")}</p>` : "";
        if (tabelle) {
          const tit = tabelle.querySelector(":scope > .plm-dati-tit");
          if (tit) tit.insertAdjacentHTML("afterend", sig); else tabelle.insertAdjacentHTML("afterbegin", `<p class="plm-dati-tit">${T("Dati", "Data")}</p>` + sig);
          tabelle.classList.add("plm-box");
          out += tabelle.outerHTML;
        } else out += `<div class="plm-dati plm-box"><p class="plm-dati-tit">${T("Dati", "Data")}</p>${sig}</div>`;
      }
      plm.insertAdjacentHTML("afterbegin", out);
      // «Modello»: variabili e modello simbolico in un blocco richiudibile
      const sim = plm.querySelector(":scope > .plm-sim");
      const vv = sez.variabili.length ? `<p class="plm-mod-var"><b>${T("Variabili", "Variables")}:</b> ${sez.variabili.join("<br>")}</p>` : "";
      if (sim) sim.outerHTML = RIQ.scatola("plm-box-mod", T("Modello", "Model"), vv + sim.outerHTML, RIQ.modelloAperto(st));
      return tpl.innerHTML;
    },
  };
  // il blocco «Modello» resta aperto o chiuso come lo lascia chi legge, anche quando i cursori ridisegnano il riquadro
  document.addEventListener("toggle", (e) => {
    const d = e.target;
    if (!d || !d.classList || !d.classList.contains("plm-box-mod")) return;
    const g = d.closest(".gi");
    if (g) g.dataset.plmMod = d.open ? "1" : "0";
    window.dispatchEvent(new Event("resize"));
  }, true);

  // ================================================================ la riga del capitolo in fondo al riquadro, dopo la figura
  const CAP = {
    mostra(st, html) {
      const leg = st.el.querySelector(".gi-legenda");
      if (!leg) return;
      let b = st.el.querySelector(".plm-cap-fondo");
      if (!b) { b = GI.h("div", { class: "plm-cap-fondo" }); leg.after(b); }
      if (b.dataset.html === html) return;
      b.dataset.html = html;
      b.hidden = !html;
      b.innerHTML = html;
    },
  };

  const FONDO = {
    sposta(st, html) {
      if (typeof html !== "string" || !st || !st.el) return html;
      html = RIQ.applica(html, st);
      const i = html.indexOf('<details class="plm-num"');
      if (i < 0) return html;
      const j = html.indexOf("</details>", i) + "</details>".length;
      FONDO.mostra(st, html.slice(i, j));
      return html.slice(0, i) + html.slice(j);
    },
    mostra(st, html) {
      let b = st.el.querySelector(":scope > .plm-fondo");
      if (!b) { b = GI.h("div", { class: "plm-fondo" }); st.el.append(b); }
      if (b.dataset.html === html) return;
      const prima = b.querySelector("details.plm-num"), aperto = prima ? prima.open : null;
      b.dataset.html = html;
      b.innerHTML = GI.mj(html);
      const d = b.querySelector("details.plm-num");
      if (d && aperto !== null) d.open = aperto;
      GI.typeset(b);
    },
  };

  // ================================================================ valori dei dati (GI_PL_DV)
  const DV = {
    f: (x, c = 2) => GI.num(x, c),
    L: (a, c = 2) => a.map((x) => DV.f(x, c)).join(GI.EN ? ",\\ " : ";\\ "),
    tab: (titolo, intest, righe) => `<div class="plm-sol-t"><p>${titolo}</p>${M.tab(intest, righe)}</div>`,
    tabelle: (...t) => `</p><div class="plm-dati"><p class="plm-dati-tit">${T("Dati", "Data")}</p>${t.join("")}</div><p class="plm-testo">`,
  };

  // ================================================================ il modello 9.1 sui dati dei cursori
  const LOT = { d: [20, 10, 30, 40, 10], p: [2, 3, 2, 3, 2], r0: 0, rn: 0 };
  /** colonne x_1..x_n, s_1..s_{n-1}, y_1..y_n, come il modello esteso del capitolo */
  function modelloLotti(q, h, d5) {
    const d = LOT.d.slice(); d[4] = d5;
    const nG = d.length, X = (t) => t, S = (t) => nG + t, Y = (t) => 2 * nG - 1 + t, nv = 3 * nG - 1;
    const Mt = d.map((_, t) => d.slice(t).reduce((a, v) => a + v, 0) + LOT.rn - (t === 0 ? LOT.r0 : 0));
    const c = new Array(nv).fill(0);
    for (let t = 0; t < nG; t++) { c[X(t)] = LOT.p[t]; c[Y(t)] = q; }
    for (let t = 0; t < nG - 1; t++) c[S(t)] = h;
    const A = [], rel = [], b = [];
    for (let t = 0; t < nG; t++) {
      const a = new Array(nv).fill(0); a[X(t)] = 1;
      if (t > 0) a[S(t - 1)] = 1;
      if (t < nG - 1) a[S(t)] = -1;
      A.push(a); rel.push("="); b.push(d[t] - (t === 0 ? LOT.r0 : 0) + (t === nG - 1 ? LOT.rn : 0));
    }
    for (let t = 0; t < nG; t++) {
      const a = new Array(nv).fill(0); a[X(t)] = -1; a[Y(t)] = Mt[t];
      A.push(a); rel.push(">="); b.push(0);
    }
    return { P: { senso: "min", c, A, rel, b }, bin: d.map((_, t) => Y(t)), d, Mt, X, S, Y, nG, q, h };
  }
  /** ottimo (enumerazione delle 32 assegnazioni delle binarie + simplesso) e rilassamento continuo */
  function calcola(v) {
    const Mo = modelloLotti(v[0], v[1], v[2] ?? LOT.d[4]);   // due cursori (q, h): d_5 resta quella dell'istanza
    const o = D().milp(Mo.P, Mo.bin), r = D().rilassamento(Mo.P, Mo.bin);
    const R = { Mo, stato: o.stato, nOtt: o.nOtt, zLP: r.stato === "ottimo" ? r.z : null };
    if (o.stato !== "ottimo") return R;
    const t0 = (x) => (Math.abs(x) < 1e-7 ? 0 : x);
    const nG = Mo.nG, rng = [...Array(nG).keys()];
    R.z = o.z;
    R.x = rng.map((t) => t0(o.x[Mo.X(t)]));
    R.s = rng.slice(0, nG - 1).map((t) => t0(o.x[Mo.S(t)]));
    R.y = rng.map((t) => (o.x[Mo.Y(t)] > 0.5 ? 1 : 0));
    R.yLP = r.stato === "ottimo" ? rng.map((t) => t0(r.x[Mo.Y(t)])) : null;
    R.prod = rng.reduce((a, t) => a + LOT.p[t] * R.x[t], 0);
    R.costoSetup = R.y.reduce((a, y) => a + y, 0) * Mo.q;
    R.mag = R.s.reduce((a, s) => a + Mo.h * s, 0);
    R.gap = R.zLP !== null && Math.abs(R.z) > 1e-9 ? (R.z - R.zLP) / R.z : null;
    return R;
  }

  // ================================================================ la voce
  const vLotti = {
    etichetta: T("Lotti con costo fisso di setup", "Lot sizing with a fixed setup cost"),
    cursori: [
      { nome: T("\\text{setup}\\ q_t", "\\text{setup}\\ q_t"), min: 10, max: 250, step: 10, val: 50,
        fmt: (x) => T(`${nt(x, 0)} € per setup`, `${nt(x, 0)} € per setup`),
        descr: T("costo fisso di setup, uguale in tutti i giorni", "fixed setup cost, the same on every day") },
      { nome: T("\\text{giacenza}\\ h_t", "\\text{holding}\\ h_t"), min: 1, max: 5, step: 1, val: 1,
        fmt: (x) => T(`${nt(x, 0)} € per unità e giorno`, `${nt(x, 0)} € per unit and day`),
        descr: T("costo di tenere un'unità in magazzino a fine giorno, uguale nei giorni 1–4", "cost of keeping one unit in stock at the end of a day, the same on days 1–4") },
    ],
    calcola,
    formula(R, v, st) {
      const Mo = R.Mo, nG = Mo.nG;
      const sim = `\\min ~~ \\sum_{t=1}^{n} p_t\\, x_t + \\sum_{t=1}^{n} ${st.col("a", "q_t")}\\, y_t + \\sum_{t=1}^{n-1} ${st.col("b", "h_t")}\\, s_t & & \\\\
        ${SA()} \\quad x_1 - s_1 &= d_1 - r_0, & \\\\
        x_t + s_{t-1} - s_t &= d_t, & \\forall t \\in \\{2, 3, \\dots, n-1\\}, \\\\
        x_n + s_{n-1} &= d_n + r_n, & \\\\
        -x_t + M_t\\, y_t &\\ge 0, & \\forall t \\in \\{1, 2, \\dots, n\\}, \\\\
        x_t &\\ge 0, & \\forall t \\in \\{1, 2, \\dots, n\\}, \\\\
        s_t &\\ge 0, & \\forall t \\in \\{1, 2, \\dots, n-1\\}, \\\\
        y_t &\\in \\{0, 1\\}, & \\forall t \\in \\{1, 2, \\dots, n\\}.`;
      // forma matriciale stretta, come il modello esteso del capitolo: x_1..x_5, s_1..s_4, y_1..y_5
      const vars = [];
      for (let t = 0; t < nG; t++) vars[Mo.X(t)] = `x_{${t + 1}}`;
      for (let t = 0; t < nG - 1; t++) vars[Mo.S(t)] = `s_{${t + 1}}`;
      for (let t = 0; t < nG; t++) vars[Mo.Y(t)] = `y_{${t + 1}}`;
      const col = (f, k) => [...Array(k).keys()].map(f);
      const nv = vars.length, nc = Mo.P.A.length;
      const num = numLP({ senso: "min", vars, c: Mo.P.c, cifre: 2,
        righe: Mo.P.A.map((a, k) => ({ a, rel: Mo.P.rel[k], rhs: Mo.P.b[k] })),
        dominio: [{ cols: col(Mo.X, nG), rel: ">=", rhs: "0" }, { cols: col(Mo.S, nG - 1), rel: ">=", rhs: "0" },
          { cols: col(Mo.Y, nG), rel: "\\in", rhs: "\\{0, 1\\}" }] },
        T(`Il modello MILP dell'istanza: ${nv} variabili, ${nc} vincoli.`, `The MILP model of the instance: ${nv} variables, ${nc} constraints.`));
      const giorni = ["\\(t\\)", ...Mo.d.map((_, t) => String(t + 1))];
      const riga = (nome, a) => [nome, ...a.map((x) => (x === null ? "—" : FR.txt(x)))];
      const TABS = DV.tabelle(DV.tab(T("Dimensioni", "Sizes"), ["\\(n\\)"], [[String(nG)]]),
        DV.tab(T("Scorte (unità)", "Stock (units)"), ["\\(r_0\\)", "\\(r_n\\)"], [[String(LOT.r0), String(LOT.rn)]]),
        DV.tab(T("Dati per giorno", "Data by day"), giorni, [
        riga(T("\\(d_t\\) (unità)", "\\(d_t\\) (units)"), Mo.d),
        riga("\\(p_t\\) (€)", LOT.p),
        riga("\\(q_t\\) (€)", Mo.d.map(() => Mo.q)),
        riga("\\(h_t\\) (€)", Mo.d.map((_, t) => (t < nG - 1 ? Mo.h : null))),
        riga(T("\\(M_t\\) (unità)", "\\(M_t\\) (units)"), Mo.Mt),
      ]));
      const testo = T(`<b>Il problema.</b> Decidiamo quanto produrre in ogni giorno di un orizzonte di più giorni, e di conseguenza quanto resta in magazzino. ` +
        "L'obiettivo è minimizzare il costo totale di produzione, di setup e di magazzino. I vincoli: la domanda di ogni giorno è servita per intero, e non si produce in un giorno senza pagarne il costo fisso di setup." +
        "<br><b>Variabili:</b> \\(x_t \\ge 0\\): unità prodotte nel giorno \\(t\\), con \\(t \\in \\{1, \\dots, n\\}\\); \\(s_t \\ge 0\\): unità a scorta alla fine del giorno \\(t\\), con \\(t \\in \\{1, \\dots, n-1\\}\\); \\(y_t \\in \\{0,1\\}\\): vale 1 se nel giorno \\(t\\) si attiva la produzione, con \\(t \\in \\{1, \\dots, n\\}\\)." +
        `<br><b>Dati:</b> \\(n\\): numero di giorni; \\(d_t\\): domanda del giorno \\(t\\) (unità); \\(p_t\\): costo di produzione di un'unità nel giorno \\(t\\) (€); \\(q_t\\): costo fisso di setup del giorno \\(t\\) (€); \\(h_t\\): costo di tenere un'unità in magazzino alla fine del giorno \\(t\\), con \\(t \\in \\{1, \\dots, n-1\\}\\) (€); \\(M_t = d_t + \\dots + d_n + r_n\\): big-M del giorno \\(t\\), la domanda che resta da coprire (unità); \\(r_0\\), \\(r_n\\): scorte iniziale e finale (unità); con \\(t \\in \\{1, \\dots, n\\}\\).` + TABS,
      `<b>The problem.</b> We decide how much to produce on each day of a horizon of several days, and consequently how much is left in stock. ` +
        "The objective is to minimize the total cost of production, setups and stock. The constraints: the demand of every day is served in full, and nothing is produced on a day without paying its fixed setup cost." +
        "<br><b>Variables:</b> \\(x_t \\ge 0\\): units produced on day \\(t\\), with \\(t \\in \\{1, \\dots, n\\}\\); \\(s_t \\ge 0\\): units in stock at the end of day \\(t\\), with \\(t \\in \\{1, \\dots, n-1\\}\\); \\(y_t \\in \\{0,1\\}\\): equals 1 if production is set up on day \\(t\\), with \\(t \\in \\{1, \\dots, n\\}\\)." +
        `<br><b>Data:</b> \\(n\\): number of days; \\(d_t\\): demand of day \\(t\\) (units); \\(p_t\\): production cost of one unit on day \\(t\\) (€); \\(q_t\\): fixed setup cost of day \\(t\\) (€); \\(h_t\\): cost of keeping one unit in stock at the end of day \\(t\\), with \\(t \\in \\{1, \\dots, n-1\\}\\) (€); \\(M_t = d_t + \\dots + d_n + r_n\\): big-M of day \\(t\\), the demand still to be covered (units); \\(r_0\\), \\(r_n\\): initial and final stock (units); with \\(t \\in \\{1, \\dots, n\\}\\).` + TABS);
      return FONDO.sposta(st, modello(testo, sim, num, "lotti"));
    },
    disegna(crea, R, v, C, S) {
      if (R.stato !== "ottimo") return M.scritta(crea, S.W / 2, S.H / 2, T("Nessun piano ammissibile", "No feasible plan"), { fontSize: 15, strokeColor: C.rosso });
      const F = FIG(), Mo = R.Mo, nG = Mo.nG, giorni = Mo.d.map((_, t) => t + 1);
      const fx = (u) => (Number.isInteger(u) && u >= 1 && u <= nG ? String(u) : "");
      const hTop = S.H - MF.basso - MF.alto;   // una sola figura, la più significativa (Fabio, 26/11/2026)
      // 1. produzione, domanda, scorte e giorni con setup
      // scala fissa: produzione e scorte non superano la domanda totale M_1, così la figura non cambia scala con la soluzione
      const vmax = Math.max(Mo.Mt[0], ...Mo.d, 10);
      const A = figura(crea, { X0: MF.sx, X1: S.W - MF.dx, Y0: S.H - MF.alto - hTop, Y1: S.H - MF.alto, xa: 0.4, xb: nG + 0.6, ya: 0, yb: vmax * 1.32,
        titolo: T(`Piano ottimo: produzione, domanda e scorte (z(MILP) = ${FR.euroTxt(R.z)})`, `Optimal plan: production, demand and stock (z(MILP) = ${FR.euroTxt(R.z)})`),
        ny: T("unità", "units"), nx: T("giorno", "day") }, C, { nTy: 5, fx, ymax: vmax });
      giorni.forEach((g, t) => {
        if (!R.y[t]) return;
        M.rett(crea, A.X(g - 0.46), A.Y(0), A.X(g + 0.46), A.Y(vmax * 1.18), { fillColor: F.fascia, fillOpacity: M.scuro() ? 0.16 : 0.09, strokeColor: "none" });
        M.scritta(crea, A.X(g), A.Y(vmax * 1.18) - 9, T("setup", "setup"), { fontSize: 11.5, strokeColor: F.fascia, cssStyle: "font-weight:700" });
      });
      giorni.forEach((g, t) => {
        const q = R.x[t];
        if (q <= 1e-9) return;
        M.rett(crea, A.X(g - 0.26), A.Y(0), A.X(g + 0.26), A.Y(q), { fillColor: F.teal, fillOpacity: 1, strokeColor: F.teal, strokeWidth: 0.5 });
        // il valore in una riga fissa sopra le barre, sotto la scritta «setup»: non si sposta quando cambia la soluzione
        M.scritta(crea, A.X(g), A.Y(vmax * 1.07), FR.txt(q, 1), { fontSize: 12, strokeColor: F.teal, cssStyle: "font-weight:700" });
      });
      lineaPunti(crea, A, giorni, Mo.d, F.rosso, { dash: 2, spessore: 1.8 });
      lineaPunti(crea, A, giorni.slice(0, nG - 1), R.s, F.arancio, { r: 4, punto: { face: "[]" } });
      legendaRiga(crea, A, [[F.teal, T("produzione x̃(MILP)", "production x̃(MILP)"), "barra"], [F.rosso, T("domanda dₜ", "demand dₜ"), "tratteggioPunti"],
        [F.arancio, T("scorta s̃(MILP) a fine giorno", "stock s̃(MILP) at the end of the day"), "lineaPunti"], [F.fascia, T("giorno con setup (ỹ(MILP) = 1)", "setup day (ỹ(MILP) = 1)"), "fascia"]], C);
    },
    legenda: () => [],
    letture: () => "",
    soluzione(R) {
      if (R.stato !== "ottimo") return "";
      const Mo = R.Mo;
      const intest = ["", ...Mo.d.map((_, t) => `\\(t = ${t + 1}\\)`)];
      const righe = [
        ["\\(\\tilde x(\\text{MILP})\\)", ...R.x.map((x) => SOL.z(x))],
        ["\\(\\tilde s(\\text{MILP})\\)", ...R.s.map((x) => SOL.z(x)), ""],
        ["\\(\\tilde y(\\text{MILP})\\)", ...R.y.map(String)],
      ];
      const nota = T("«—»: valore nullo.", "«—»: zero value.") +
        (R.nOtt > 1 ? " " + T(`Ci sono ${R.nOtt} piani ottimi con lo stesso costo: si mostra quello con meno setup.`, `There are ${R.nOtt} optimal plans with the same cost: the one with fewer setups is shown.`) : "");
      return SOL.blocco(
        SOL.valore(T("Costo ottimo", "Optimal cost"), FR.euro(R.z), R.zLP === null ? null : FR.euro(R.zLP), R.gap === null ? null : FR.gap(R.z, R.zLP)),
        [SOL.tab("", intest, righe)], nota);
    },
    domanda: T("Porta \\(q_t\\) a 160 €: basta un solo setup, nel giorno 1. Riporta \\(q_t\\) a 50 € e \\(h_t\\) a 3 €: si aggiunge un setup nel giorno 4.",
      "Set \\(q_t\\) to 160 €: a single setup, on day 1, is enough. Set \\(q_t\\) back to 50 € and \\(h_t\\) to 3 €: a setup is added on day 4."),
  };

  // ================================================================ ricetta a voci (GI_OTT.ricettaVoci di gi-ott.js, una voce sola)
  function ricettaVoce(opz, vc) {
    const parametri = vc.cursori.map((c, i) => ({ k: "s" + i, nome: "s_" + i, min: 0, max: 100, step: 1, val: 50, colore: "abcde"[i] }));
    const valori = (st) => { const p = st.p(); return vc.cursori.map((c, i) => p["s" + i]); };
    function configura(st) {
      const D0 = st.dati, tema = M.scuro();
      // al cambio di tema la board si ricrea ma i cursori restano dove sono; con «Azzera» tornano ai valori iniziali
      const nuovo = !(D0.tema !== undefined && D0.tema !== tema);
      D0.tema = tema;
      const bEl = st.el.querySelector(".gi-board");
      if (bEl && !st.el.classList.contains("gi-app-intera")) bEl.style.aspectRatio = window.innerWidth < 600 ? "4 / 5" : "";
      st.el.querySelectorAll(".gi-ctrl").forEach((ctrl, i) => {
        const c = vc.cursori[i];
        if (!c) { ctrl.hidden = true; return; }
        const inp = ctrl.querySelector("input");
        inp.min = c.min; inp.max = c.max; inp.step = c.step;
        if (nuovo) inp.value = c.val;
        const nome = ctrl.querySelector(".gi-nome");
        if (nome.dataset.tex !== c.nome) { nome.dataset.tex = c.nome; nome.innerHTML = GI.mj(`\\(${c.nome}\\)`); GI.typeset(nome); }
        const val = ctrl.querySelector(".gi-val");
        if (val) val.style.display = "none";
        let mio = ctrl.querySelector(".gi-val-voce");
        if (!mio) { mio = GI.h("span", { class: "gi-val gi-val-voce" }); ctrl.querySelector(".gi-riga > span:last-child").append(mio); }
        let sm = ctrl.querySelector("small");
        if (!sm) { sm = GI.h("small"); ctrl.append(sm); }
        if (sm.dataset.testo !== (c.descr || "")) { sm.dataset.testo = c.descr || ""; sm.innerHTML = GI.mj(c.descr || ""); GI.typeset(sm); }
      });
      if (!D0.ro && window.ResizeObserver) {
        const el = st.el.querySelector(".gi-board");
        D0.ro = new ResizeObserver(() => {
          clearTimeout(D0.roT);
          D0.roT = setTimeout(() => { if (document.body.contains(st.el)) st.aggiorna(); else D0.ro.disconnect(); }, 120);
        });
        D0.ro.observe(el);
      }
    }
    function risultato(st) {
      const v = valori(st), firma = v.join(",");
      if (st.dati.R && st.dati.Rf === firma) return st.dati.R;
      st.dati.Rf = firma;
      st.dati.R = vc.calcola(v, st);
      return st.dati.R;
    }
    function misura(board) {
      const cont = board.containerObj;
      if (cont && cont.clientWidth > 0 && cont.clientHeight > 0 &&
        (Math.abs(cont.clientWidth - board.canvasWidth) > 1 || Math.abs(cont.clientHeight - board.canvasHeight) > 1)) {
        board.resizeContainer(cont.clientWidth, cont.clientHeight, true, true);
      }
      const Wp = board.canvasWidth || 600, Hp = board.canvasHeight || 400;
      const bb = board.getBoundingBox();
      if (Math.abs(bb[0]) > 1e-9 || Math.abs(bb[1] - Hp) > 1e-6 || Math.abs(bb[2] - Wp) > 1e-6 || Math.abs(bb[3]) > 1e-9) board.setBoundingBox([0, Hp, Wp, 0], false);
      return { W: Wp, H: Hp };
    }
    return {
      titolo: opz.titolo,
      parametri,
      vista: [0, 300, 400, 0],
      assi: false,
      opzioniBoard: M.OPZ,
      monta(board, st) { st.dati.R = null; configura(st); },
      aggiorna(board, st) {
        const v = valori(st), Rr = risultato(st), C = M.COL(st), S = misura(board);
        st.el.querySelectorAll(".gi-ctrl").forEach((ctrl, i) => {
          const c = vc.cursori[i], mio = ctrl.querySelector(".gi-val-voce");
          if (c && mio) mio.textContent = c.fmt ? c.fmt(v[i]) : GI.numTxt(v[i], 2);
        });
        M.ridisegna(board, st, [v.join(","), M.scuro(), S.W, S.H].join("|"), (crea) => vc.disegna(crea, Rr, v, C, S, st, board));
      },
      formula(p, st) { return vc.formula(risultato(st), valori(st), st); },
      letture(p, st) {
        const R = risultato(st), C = M.COL(st);
        let h = "";
        try { h = vc.soluzione(R) || ""; } catch (e) { console.error("GI: soluzione", e); }
        SOL.mostra(st, h);
        return vc.letture(R, valori(st), st, C);
      },
      legenda: () => [],
      domanda: vc.domanda,
    };
  }

  window.GI_RICETTE["mip-lotti"] = () => ricettaVoce({ titolo: T("Lotti con costo fisso di setup", "Lot sizing with a fixed setup cost") }, vLotti);
  // per le prove automatiche: solo il calcolo; gli helper di formato li usa anche gi-mip-progetti.js (app della home)
  window.GI_MIP_LOTTI = { modelloLotti, calcola, FR, SOL, FONDO, DV, numLP, ricettaVoce };
})();
