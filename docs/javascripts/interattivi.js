/* Grafici interattivi di Modellazione MIP / MIP Modelling (JSXGraph): motore copiato
 * da Programmazione lineare (CORSO_PROGRAMMAZIONE_LINEARE/it/python/sito/javascripts/),
 * da tenere allineato a mano. Helper comuni alle ricette MIP: gi-comune.js (window.GI_MIP).
 *
 * Un solo file per le due lingue: le stringhe dell'interfaccia e il separatore
 * decimale si scelgono da <html lang="…"> (it: virgola, en: punto). Il motore
 * viene dal laboratorio di Analisi Matematica 1 (stesse classi CSS gi-*, stesso
 * aspetto), ma le ricette NON stanno qui: ogni file gi-*.js le registra in
 * window.GI_RICETTE, e il motore le monta quando la pagina è pronta.
 *
 * ============================================================== NELLE PAGINE
 *   <div class="gi" data-grafico="chiave"></div>
 *   (facoltativo: data-funzione="k" sceglie la voce iniziale di `funzioni`)
 * Se la ricetta non esiste, al posto del grafico compare una riga discreta.
 *
 * ============================================================ ORDINE DEI FILE
 * mkdocs.yml carica jsxgraphcore.js, POI questo file, POI i gi-*.js: così le
 * ricette possono usare window.GI (GI.T, GI.num, …) già al caricamento. Il
 * montaggio avviene comunque dopo DOMContentLoaded (e a ogni cambio di pagina
 * della navigazione istantanea di Material, document$), quando tutti gli script
 * sono stati eseguiti. Per non dipendere dall'ordine si può anche registrare una
 * funzione fabbrica: GI_RICETTE["k"] = (GI) => ({ … }), chiamata al montaggio.
 *
 * =========================================================== REGISTRARE UNA RICETTA
 *   window.GI_RICETTE = window.GI_RICETTE || {};
 *   window.GI_RICETTE["nome"] = { … };          // oppure GI.registra("nome", { … })
 *
 * Testi: HTML; le formule vanno fra \\( \\) (nelle stringhe JS le barre si
 * raddoppiano: "\\(x^2\\)", "\\,"); il motore le mette negli span «arithmatex»
 * (l'unica classe che il MathJax della collana elabora) e le fa comporre.
 * Bilingue: GI.T("testo italiano", "English text").
 *
 * CAMPI DELLA RICETTA (tutti facoltativi tranne titolo)
 *   titolo        string            titolo nella testata (HTML, anche con \\( \\))
 *   sottotitolo   string            in piccolo accanto al titolo
 *   parametri     [ { k, nome, min, max, step, val, descr, colore, cifre } ]
 *                   i cursori. k: chiave (in p.k); nome: TeX del nome (default k);
 *                   descr: HTML sotto il cursore; colore: "a".."e" (default in
 *                   ordine a, b, c, d, e) o un colore CSS; cifre: decimali mostrati
 *                   (default quelli di step). Ognuno ha il suo ▶ (animazione).
 *   funzioni      { chiave: { tex, etichetta?, …qualsiasi } }  pulsanti di scelta
 *                   (es. la funzione da studiare); st.chiave() è la voce scelta,
 *                   st.fn() il suo oggetto. etichetta (HTML) sostituisce \\(tex\\).
 *                   (Si accetta anche il nome di Analisi, funzioniCustom.)
 *   iniziale      chiave iniziale di funzioni (altrimenti la prima)
 *   etichettaFunzioni  HTML sopra i pulsanti (default «Funzione»/«Function»)
 *   vista         [xmin, ymax, xmax, ymin]  oppure  (chiave, st) => [...]
 *   stessaScala   true: stessa unità sui due assi (keepAspectRatio)
 *   rapporto      CSS aspect-ratio del riquadro, es. "1 / 1" (default "4 / 3")
 *   assi          false: niente assi (default true)
 *   griglia       true: griglia di sfondo
 *   opzioniBoard  oggetto unito alle opzioni di JXG.JSXGraph.initBoard
 *   g(x, p, f, chiave, st)  funzione di una variabile disegnata in automatico
 *                   (colore b; f = st.fn().f se la voce di funzioni ha un campo f);
 *                   con la sfida, il motore disegna anche g(x, bersaglio, …)
 *   originale     true: disegna anche y = st.fn().f(x) (grigia tratteggiata;
 *                   con fPieno: true piena, colore b, come curva principale)
 *   riferimento   (x) => y: curva di riferimento grigia tratteggiata
 *   monta(board, st)     HOOK: dopo la creazione della board (anche alias
 *                   `disegna`). Qui si creano con JSXGraph punti trascinabili,
 *                   poligoni, curve (anche GI.implicita) ecc.; per seguire i
 *                   cursori usare coordinate-funzione: () => st.p().a.
 *                   La board si ricrea (e monta si richiama) al cambio di tema,
 *                   di voce in `funzioni` e con «Azzera».
 *   aggiorna(board, st)  HOOK: a ogni cambio dei cursori (e di sfida/modo),
 *                   prima di board.update().
 *   formula(p, st, col, chiave)  TeX della riga sopra il grafico (senza
 *                   delimitatori), oppure HTML che contiene già \\( \\). col(k, tex)
 *                   (= st.col) colora un pezzo con il colore del cursore k.
 *   letture(p, st, chiave)       HTML del riquadro grigio a destra (valori
 *                   calcolati, esito di un test…); si riscrive dopo ogni cambio,
 *                   anche quando si trascina un punto (evento «update» della board).
 *                 Il secondo argomento è st con in più i campi della voce scelta
 *                 in funzioni (tex, f, …): così valgono anche le firme di Analisi
 *                 formula(p, fn, col, chiave) e letture(p, fn, chiave). Il quinto
 *                 (formula) o quarto (letture) argomento è st puro. Non scrivere
 *                 proprietà sul secondo argomento: lo stato va in st.dati.
 *                 Un'eccezione in formula/letture finisce in console («GI: …»)
 *                 senza fermare il grafico.
 *   legenda       [[colore, testo, stile]] o (st) => [...]; colore: chiave di
 *                   un parametro, "a".."e", "ammissibile", "ottimo", "locale",
 *                   "orig", "target" o un colore CSS; stile: "", "dashed",
 *                   "dotted", "pieno" (area), "punto".
 *   domanda       HTML del riquadro «Prova tu.» (scheda Esplora)
 *   sfida         { genera(chiave, st) -> {k: valore, …}   il bersaglio (valori
 *                                                   sul passo dei cursori)
 *                   testo?    HTML del compito (default: riproduci il bersaglio)
 *                   aiuti?    {k: HTML}  suggerimento per il primo cursore lontano
 *                   aiuto?(p, bersaglio, st) -> HTML  (al posto di aiuti)
 *                   vicinanza?(p, bersaglio, st) -> numero in [0, 1] (il metro);
 *                             default: confronto fra g(·, p) e g(·, bersaglio)
 *                             se c'è g, altrimenti distanza dei parametri
 *                   vinta?(p, bersaglio, st) -> boolean; default: tutti i
 *                             parametri del bersaglio a meno di mezzo passo,
 *                             o vicinanza > 0,995 }
 *                 Senza g il bersaglio lo disegna la ricetta in monta, con
 *                 visible: () => st.modo() === "sfida" e st.bersaglio().
 *
 * L'OGGETTO st (uno per ogni grafico montato; le ricette sono condivise, quindi
 * lo stato di un grafico va in st.dati, non nella ricetta)
 *   st.p()            {k: valore} dei cursori       st.val(k)
 *   st.imposta(k, v)  sposta un cursore (e aggiorna) st.chiave(), st.fn()
 *   st.colore(x)      colore CSS: chiave di parametro, "a".."e", "ammissibile",
 *                     "ottimo", "locale", "target", "orig", "muted", "line"
 *   st.col(x, tex)    {\\color{…}{tex}} (fra graffe: \\color è un interruttore) con quel colore
 *   st.modo()         "esplora" | "sfida"           st.bersaglio()  (o null)
 *   st.board          la board corrente            st.el  il div .gi
 *   st.dati           oggetto libero per lo stato del grafico (vive quanto il div)
 *   st.aggiorna()     ricalcola tutto (hook aggiorna, board, testi); alias st.ridisegna()
 *   st.testi()        riscrive solo formula, letture e metro della sfida
 *
 * window.GI: EN, T(it, en), num(x, cifre) (TeX, virgola in italiano: «1{,}5»),
 * numTxt(x, cifre) (testo semplice), mj(html), h(tag, attrs, html),
 * typeset(el), derivata(f, x), gradiente(f, x, y), spezzata(board, punti, attr),
 * nuvola(board, max, punti, attr), implicita(board, F, attr) (curva F(x,y) = 0),
 * tabella(righe, intestazioni), registra(nome, ricetta), montaTutti().
 *
 * PROVARE UNA RICETTA (MIP): aggiungere il file gi-*.js in it/docs/javascripts/,
 * lanciare da it/ python3 python/genera_laboratorio.py (copia i file in en/ e li
 * mette in mkdocs.yml, dopo questo file e gi-comune.js), costruire il sito e
 * aprire la pagina del laboratorio; nella console del browser
 * GI_RICETTE elenca le ricette registrate ed eventuali errori di una ricetta
 * compaiono come «GI: …» (il grafico mostra una riga discreta, gli altri
 * funzionano lo stesso).
 */
(function () {
  "use strict";

  // ------------------------------------------------------------------ lingua
  const EN = /^en\b/i.test(document.documentElement.lang || "");
  const T = (it, en) => (EN ? en : it);
  const S = {
    esplora: T("Esplora", "Explore"),
    sfida: T("Sfida", "Challenge"),
    azzera: T("Azzera", "Reset"),
    prova: T("Prova tu.", "Try it."),
    nuova: T("Nuova sfida", "New challenge"),
    aiuto: T("Suggerimento", "Hint"),
    vinte: T("Sfide vinte: ", "Challenges won: "),
    centrato: T("Centrato! 🎯", "Bull's-eye! 🎯"),
    quasi: T("Ci sei quasi…", "Almost there…"),
    funzione: T("Funzione", "Function"),
    anima: T("Anima", "Animate"),
    grafico: T("Grafico interattivo: ", "Interactive graph: "),
    compito: T("Riproduci il <strong style=\"color:var(--gi-target)\">bersaglio</strong> muovendo i cursori.",
      "Reproduce the <strong style=\"color:var(--gi-target)\">target</strong> by moving the sliders."),
    assente: T("Grafico interattivo in preparazione.", "Interactive graph in preparation."),
    errore: T("Questo grafico interattivo non si è potuto disegnare.", "This interactive graph could not be drawn."),
    funzioneLegenda: T("la funzione", "the function"),
    bersaglio: T("bersaglio", "target"),
  };

  // ------------------------------------------------------------------ utilità
  const COLORI = ["a", "b", "c", "d", "e"];
  const css = (el, v) => getComputedStyle(el).getPropertyValue(v).trim();
  /** numero per il TeX: arrotondato a `cifre` decimali, zeri finali tolti, virgola in italiano */
  const num = (x, cifre = 1) => {
    if (!isFinite(x)) return isNaN(x) ? "?" : x > 0 ? "+\\infty" : "-\\infty";
    const p = Math.pow(10, cifre);
    let s = (Math.round(x * p) / p).toFixed(cifre);
    if (cifre > 0) s = s.replace(/\.?0+$/, "");
    if (s === "-0") s = "0";
    return EN ? s : s.replace(".", "{,}");
  };
  /** lo stesso numero come testo semplice (fuori dalle formule) */
  const numTxt = (x, c = 3) => {
    if (!isFinite(x)) return isNaN(x) ? "?" : x > 0 ? "+∞" : "−∞";
    return num(x, c).replace("{,}", ",");
  };
  // ogni formula \(...\) va in uno span «arithmatex»: è l'unica classe che
  // il MathJax della collana elabora
  const mj = (html) => String(html).replace(/\\\((.+?)\\\)/gs, (m) => `<span class="arithmatex">${m}</span>`);
  const h = (tag, attrs = {}, html = "") => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    e.innerHTML = mj(html);
    return e;
  };
  // MathJax può non essere ancora pronto quando il grafico si disegna: si aspetta
  const typeset = (el, tentativi = 0) => {
    // in coda con tutte le altre composizioni (mathjax.js): mai due insieme
    if (window.componiFormule) window.componiFormule([el]);
    else if (tentativi < 100) setTimeout(() => typeset(el, tentativi + 1), 150);
  };
  const derivata = (f, x, hh = 1e-5) => (f(x + hh) - f(x - hh)) / (2 * hh);
  const gradiente = (f, x, y, hh = 1e-5) => [(f(x + hh, y) - f(x - hh, y)) / (2 * hh), (f(x, y + hh) - f(x, y - hh)) / (2 * hh)];
  const decimali = (step) => (String(step).split(".")[1] || "").length;

  // ---------------------------------------------------------- strumenti di disegno
  /** spezzata che si ricalcola a ogni aggiornamento: punti() -> [[x, y], ...] */
  const spezzata = (board, punti, attr) => {
    const c = board.create("curve", [[0], [0]], Object.assign({ highlight: false }, attr));
    c.updateDataArray = function () {
      const P = punti();
      this.dataX = P.map((q) => q[0]);
      this.dataY = P.map((q) => q[1]);
    };
    return c;
  };
  /** insieme di punti (fino a max) che si ricalcola: punti() -> [[x, y], ...] */
  const nuvola = (board, max, punti, attr) => {
    let cache = [];
    const P = [];
    for (let i = 0; i < max; i++) {
      P.push(board.create("point", [() => { if (i === 0) cache = punti(); return cache[i] ? cache[i][0] : NaN; }, () => (cache[i] ? cache[i][1] : NaN)],
        Object.assign({ name: "", fixed: true, size: 2.5, highlight: false, showInfobox: false, visible: () => !!cache[i] }, attr)));
    }
    return P;
  };
  /** curva implicita F(x, y) = 0 (F può dipendere dai cursori: si ricalcola) */
  const implicita = (board, F, attr) =>
    board.create("implicitcurve", [F], Object.assign({ strokeWidth: 2.5, highlight: false, resolution_outer: 30, resolution_inner: 30 }, attr));
  const tabella = (righe, intest) =>
    `<table class="gi-tabella">` +
    `<tr>${intest.map((t) => `<th>${t}</th>`).join("")}</tr>` +
    righe.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("") + `</table>`;

  // ------------------------------------------------------------------ registro
  window.GI_RICETTE = window.GI_RICETTE || {};
  const registra = (nome, ricetta) => { window.GI_RICETTE[nome] = ricetta; };
  const ricetta = (nome) => {
    let R = window.GI_RICETTE[nome];
    if (typeof R === "function") R = window.GI_RICETTE[nome] = R(window.GI);
    return R && typeof R === "object" ? R : null;
  };

  // ------------------------------------------------------------------ motore
  function monta(el) {
    if (el.dataset.montato) return;
    const nome = el.dataset.grafico;
    let R;
    try { R = ricetta(nome); } catch (e) { console.error("GI: ricetta «" + nome + "»", e); }
    if (!R) {
      // ricetta non (ancora) registrata: una riga discreta, nessun errore
      el.classList.add("gi-assente");
      el.textContent = S.assente;
      return;
    }
    el.dataset.montato = "1";
    el.classList.remove("gi-assente");
    el.innerHTML = "";
    try { costruisci(el, R); } catch (e) {
      console.error("GI: grafico «" + nome + "»", e);
      el.innerHTML = "";
      el.classList.add("gi-assente");
      el.textContent = S.errore;
    }
  }

  function costruisci(el, R) {
    const funzioni = R.funzioniCustom || (R.funzioni && !Array.isArray(R.funzioni) ? R.funzioni : null);
    const parametri = R.parametri || [];
    let chiave = (funzioni && el.dataset.funzione in funzioni ? el.dataset.funzione : null) || R.iniziale || (funzioni ? Object.keys(funzioni)[0] : null);
    let modo = "esplora", bersaglio = null, vinte = 0, giaVinta = false, board = null, anim = null, osservatore = null;
    let ultimaFormula = null, ultimeLetture = null, testiInCoda = false;

    // --- intestazione
    const testa = h("div", { class: "gi-testa" }, `<span class="gi-titolo">${R.titolo || ""}<small>${R.sottotitolo || ""}</small></span>`);

    // app a tutta pagina: il titolo e la descrizione della pagina vanno nella testata della scatola
    if (el.classList.contains("gi-app-intera")) {
      const h1 = el.parentElement && el.parentElement.querySelector(":scope > h1");
      if (h1) {
        const p = h1.nextElementSibling && h1.nextElementSibling.tagName === "P" ? h1.nextElementSibling : null;
        const t1 = h1.cloneNode(true);
        t1.querySelectorAll(".headerlink").forEach((a) => a.remove());
        testa.querySelector(".gi-titolo").innerHTML = t1.innerHTML + (p ? `<small>${p.innerHTML}</small>` : "");
        h1.classList.add("gi-nascosto");
        if (p) p.classList.add("gi-nascosto");
        typeset(testa);
      }
    }
    const tabs = h("div", { class: "gi-tabs" });
    const tEsplora = h("button", { class: "gi-tab", "aria-selected": "true" }, S.esplora);
    const tSfida = h("button", { class: "gi-tab", "aria-selected": "false" }, S.sfida);
    if (R.sfida) { tabs.append(tEsplora, tSfida); testa.append(tabs); }
    el.append(testa);

    const corpo = h("div", { class: "gi-corpo" });
    const sx = h("div"), dx = h("div");
    corpo.append(sx, dx);
    el.append(corpo);

    const formula = h("div", { class: "gi-formula" });
    const bid = "gi-" + Math.random().toString(36).slice(2);
    const titoloPiano = String(R.titolo || "").replace(/<[^>]*>|\\[()]/g, "");
    const boardEl = h("div", { class: "gi-board jxgbox", id: bid, "aria-label": S.grafico + titoloPiano });
    if (R.rapporto) boardEl.style.aspectRatio = R.rapporto;
    const legenda = h("div", { class: "gi-legenda" });
    sx.append(formula, boardEl, legenda);

    // app a tutta pagina: la board occupa lo spazio che resta nello schermo, così si vede tutta senza scorrere
    if (el.classList.contains("gi-app-intera") && !R.rapporto) {
      const altezza = () => {
        if (!document.body.contains(el)) return;
        const top = boardEl.getBoundingClientRect().top + window.scrollY;
        const hh = Math.round(window.innerHeight - top - legenda.offsetHeight - 30);
        boardEl.style.height = Math.max(window.innerWidth < 860 ? 300 : 360, hh) + "px";
        boardEl.style.minHeight = "0";
      };
      requestAnimationFrame(altezza);
      setTimeout(altezza, 700);
      window.addEventListener("resize", altezza);
    }

    // --- scelta della funzione
    if (funzioni) {
      dx.append(h("div", {}, `<strong>${R.etichettaFunzioni || S.funzione}</strong>`));
      const chips = h("div", { class: "gi-chips" });
      for (const [k, v] of Object.entries(funzioni)) {
        const b = h("button", { class: "gi-chip", "aria-pressed": String(k === chiave) }, v.etichetta || `\\(${v.tex}\\)`);
        b.onclick = () => {
          chiave = k;
          chips.querySelectorAll(".gi-chip").forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
          if (modo === "sfida") nuovaSfida(true);
          else aggiorna(true);
        };
        chips.append(b);
      }
      dx.append(chips);
    }

    // --- cursori
    const input = {}, valEl = {}, coloreDi = {};
    parametri.forEach((p, i) => {
      const k = p.k;
      coloreDi[k] = p.colore || COLORI[i % COLORI.length];
      const cv = cssVar(coloreDi[k]);
      const ctrl = h("div", { class: "gi-ctrl", style: `--c: ${cv}` });
      const riga = h("div", { class: "gi-riga" });
      riga.append(h("span", { class: "gi-nome", style: `color: ${cv}` }, `\\(${p.nome || k}\\)`));
      const destra = h("span");
      const play = h("button", { class: "gi-play", title: S.anima, "aria-label": S.anima }, "▶");
      valEl[k] = h("span", { class: "gi-val" });
      destra.append(play, valEl[k]);
      riga.append(destra);
      input[k] = h("input", { type: "range", min: p.min, max: p.max, step: p.step, value: p.val, "aria-label": String(p.nome || k).replace(/\\/g, "") });
      input[k].addEventListener("input", () => aggiorna());
      ctrl.append(riga, input[k]);
      if (p.descr) ctrl.append(h("small", {}, p.descr));
      play.onclick = () => anima(k, play);
      dx.append(ctrl);
    });

    const bottoni = h("div");
    const azzera = h("button", { class: "gi-btn" }, S.azzera);
    azzera.onclick = () => { ferma(); parametri.forEach((p) => (input[p.k].value = p.val)); aggiorna(true); };
    bottoni.append(azzera);
    dx.append(bottoni);

    const letture = h("div", { class: "gi-letture", hidden: "" });
    dx.append(letture);

    const pEsplora = h("div", { class: "gi-domanda" }, `<strong>${S.prova}</strong> ${R.domanda || ""}`);
    if (R.domanda) dx.append(pEsplora);

    // --- sfida
    const pSfida = h("div", { hidden: "" });
    let metro, vinto, punti, aiuto;
    if (R.sfida) {
      pSfida.append(h("p", { style: "margin:.6em 0 .2em" }, R.sfida.testo || S.compito));
      metro = h("div", { class: "gi-metro" }, "<div></div>");
      const riga = h("div", { style: "display:flex;justify-content:space-between;align-items:center" });
      vinto = h("span", { class: "gi-vinto" });
      punti = h("span", { class: "gi-punti" }, S.vinte + "0");
      riga.append(vinto, punti);
      const nuova = h("button", { class: "gi-btn primario" }, S.nuova);
      const bAiuto = h("button", { class: "gi-btn" }, S.aiuto);
      aiuto = h("div", { class: "gi-domanda", hidden: "" });
      nuova.onclick = () => nuovaSfida();
      bAiuto.onclick = () => {
        let testo = "";
        if (R.sfida.aiuto) testo = R.sfida.aiuto(p(), bersaglio, st);
        else if (R.sfida.aiuti) {
          const lontano = parametri.map((q) => q.k).find((k) => k in bersaglio && !vicino(k)) || parametri[0].k;
          testo = R.sfida.aiuti[lontano] || "";
        }
        aiuto.innerHTML = mj(testo);
        aiuto.hidden = !testo;
        typeset(aiuto);
      };
      pSfida.append(metro, riga, nuova, bAiuto, aiuto);
      dx.append(pSfida);
      tEsplora.onclick = () => setModo("esplora");
      tSfida.onclick = () => setModo("sfida");
    }

    // --- stato
    function cssVar(c) { return /^(#|rgb|hsl|var\()/.test(c) ? c : `var(--gi-${c})`; }
    function cssColore(c) { return /^(#|rgb|hsl)/.test(c) ? c : css(el, "--gi-" + c) || c; }
    const val = (k) => parseFloat(input[k].value);
    const p = () => Object.fromEntries(parametri.map((q) => [q.k, val(q.k)]));
    const passo = (k) => parseFloat(input[k].step) || 0;
    const vicino = (k) => Math.abs(val(k) - bersaglio[k]) <= passo(k) / 2 + 1e-9;
    const colore = (x) => cssColore(x in coloreDi ? coloreDi[x] : x);
    const st = {
      p, val, colore,
      col: (x, tex) => `{\\color{${colore(x)}}{${tex}}}`,
      chiave: () => chiave,
      fn: () => (funzioni ? funzioni[chiave] : null),
      modo: () => modo,
      bersaglio: () => bersaglio,
      imposta: (k, v) => { input[k].value = v; aggiorna(); },
      el, dati: {}, board: null,
      aggiorna: () => aggiorna(),
      ridisegna: () => aggiorna(),
      testi: () => pianificaTesti(),
    };
    const FN0 = { f: (x) => x, tex: "x", wrap: (a) => a };
    const voce = () => (funzioni && funzioni[chiave]) || FN0;
    // secondo argomento di formula/letture: st più i campi della voce scelta
    const stFn = () => Object.assign({}, voce(), st);
    const g = (x, q) => { try { return R.g(x, q, voce().f, chiave, st); } catch (e) { return NaN; } };
    const segnalati = new Set();
    const prova = (nomeHook, fz) => {
      try { return fz(); } catch (e) {
        if (!segnalati.has(nomeHook)) { segnalati.add(nomeHook); console.error("GI: «" + el.dataset.grafico + "»." + nomeHook, e); }
        return "";
      }
    };
    const vista = () => (typeof R.vista === "function" ? R.vista(chiave, st) : R.vista) || [-5, 5, 5, -5];

    function creaBoard() {
      if (board) JXG.JSXGraph.freeBoard(board);
      const muted = css(el, "--gi-muted"), line = css(el, "--gi-line");
      const assi = { strokeColor: muted, ticks: { strokeColor: line, majorHeight: -1, label: { strokeColor: muted } } };
      board = JXG.JSXGraph.initBoard(bid, Object.assign({
        boundingbox: vista(), axis: R.assi !== false, grid: !!R.griglia, keepAspectRatio: !!R.stessaScala,
        showCopyright: false, showNavigation: false,
        pan: { enabled: true, needShift: false, needTwoFingers: true }, zoom: { wheel: true, needShift: true },
        defaultAxes: { x: assi, y: assi },
      }, R.opzioniBoard || {}));
      st.board = board;
      if (R.originale) board.create("functiongraph", [(x) => voce().f(x)], R.fPieno
        ? { strokeColor: colore("b"), strokeWidth: 3, highlight: false }
        : { strokeColor: colore("orig"), strokeWidth: 2.2, dash: 2, highlight: false });
      if (R.riferimento) board.create("functiongraph", [R.riferimento], { strokeColor: colore("orig"), strokeWidth: 2, dash: 2, highlight: false });
      if (R.sfida && R.g) board.create("functiongraph", [(x) => (bersaglio ? g(x, bersaglio) : NaN)], { strokeColor: colore("target"), strokeWidth: 4, dash: 1, highlight: false, visible: () => modo === "sfida" });
      if (R.g) board.create("functiongraph", [(x) => g(x, p())], { strokeColor: colore("b"), strokeWidth: 3.5, highlight: false });
      const hook = R.monta || R.disegna;
      if (hook) hook.call(R, board, st);
      // qualunque cambio della board (anche un punto trascinato) riscrive i testi
      board.on("update", pianificaTesti);
    }

    function scriviLegenda() {
      const voci = typeof R.legenda === "function" ? R.legenda(st) : R.legenda || [
        ...(R.g ? [["b", S.funzioneLegenda, ""]] : []),
        ...(R.sfida && R.g ? [["target", S.bersaglio, "dotted"]] : []),
      ];
      legenda.innerHTML = mj(voci
        .filter((v) => v[0] !== "target" || modo === "sfida")
        .map(([k, t, s]) => {
          const c = cssVar(k in coloreDi ? coloreDi[k] : k);
          const segno = s === "pieno" ? `<i class="gi-pieno" style="border-color:${c};background:color-mix(in srgb, ${c} 25%, transparent)"></i>`
            : s === "punto" ? `<i class="gi-punto" style="background:${c}"></i>`
              : `<i style="border-color:${c};border-top-style:${s || "solid"}"></i>`;
          const testo = /\\\(/.test(t) || !(/[\\_^=]/.test(t) || /^[a-z]'*$/.test(t)) ? t : `\\(${t}\\)`;
          return `<span>${segno}${testo}</span>`;
        })
        .join(""));
      typeset(legenda);
    }

    function vicinanza() {
      if (R.sfida.vicinanza) return +prova("sfida.vicinanza", () => R.sfida.vicinanza(p(), bersaglio, st)) || 0;
      if (R.g) {
        let s = 0, n = 0;
        const [x0, , x1] = vista();
        for (let x = x0; x <= x1; x += (x1 - x0) / 160) {
          const y1 = g(x, p()), y2 = g(x, bersaglio);
          const ok1 = isFinite(y1), ok2 = isFinite(y2);
          if (!ok1 && !ok2) continue;
          n++;
          s += ok1 !== ok2 ? 4 : Math.min(Math.abs(y1 - y2), 4);
        }
        return n ? Math.max(0, 1 - s / n / 2) : 0;
      }
      const ks = parametri.filter((q) => q.k in bersaglio);
      if (!ks.length) return 0;
      const d = ks.reduce((s, q) => s + Math.min(1, (4 * Math.abs(val(q.k) - bersaglio[q.k])) / ((q.max - q.min) || 1)), 0) / ks.length;
      return 1 - d;
    }

    function pianificaTesti() {
      if (testiInCoda) return;
      testiInCoda = true;
      requestAnimationFrame(() => { testiInCoda = false; if (document.body.contains(el)) scriviTesti(); });
    }

    function scriviTesti() {
      parametri.forEach((q) => (valEl[q.k].textContent = numTxt(val(q.k), q.cifre ?? decimali(q.step))));
      if (R.formula) {
        let f = prova("formula", () => R.formula(p(), stFn(), st.col, chiave, st));
        f = f == null ? "" : String(f);
        if (f && !/\\\(/.test(f)) f = `\\(${f}\\)`;
        if (f !== ultimaFormula) { ultimaFormula = f; formula.innerHTML = mj(f); typeset(formula); }
      }
      if (R.letture) {
        const l = String(prova("letture", () => R.letture(p(), stFn(), chiave, st)) ?? "");
        if (l !== ultimeLetture) { ultimeLetture = l; letture.hidden = !l; letture.innerHTML = mj(l); typeset(letture); }
      }
      if (R.sfida && modo === "sfida" && bersaglio) {
        const q = Math.max(0, Math.min(1, vicinanza()));
        metro.firstChild.style.width = (q * 100).toFixed(0) + "%";
        const esatto = R.sfida.vinta ? !!prova("sfida.vinta", () => R.sfida.vinta(p(), bersaglio, st))
          : parametri.filter((pp) => pp.k in bersaglio).every((pp) => vicino(pp.k)) || q > 0.995;
        if (esatto && !giaVinta) { giaVinta = true; vinte++; punti.textContent = S.vinte + vinte; vinto.textContent = S.centrato; }
        else if (!esatto) vinto.textContent = q > 0.9 ? S.quasi : "";
      }
    }

    function aggiorna(ricrea) {
      if (ricrea || !board) { creaBoard(); scriviLegenda(); }
      if (R.aggiorna) prova("aggiorna", () => R.aggiorna.call(R, board, st));
      board.update();
      pianificaTesti();
    }

    function nuovaSfida(ricrea) {
      bersaglio = R.sfida.genera(chiave, st);
      giaVinta = false; vinto.textContent = ""; aiuto.hidden = true;
      parametri.forEach((q) => (input[q.k].value = q.val));
      aggiorna(ricrea);
    }

    function setModo(m) {
      modo = m;
      tEsplora.setAttribute("aria-selected", String(m === "esplora"));
      tSfida.setAttribute("aria-selected", String(m === "sfida"));
      pEsplora.hidden = m !== "esplora";
      pSfida.hidden = m !== "sfida";
      scriviLegenda();
      if (m === "sfida" && !bersaglio) nuovaSfida(); else aggiorna();
    }

    function ferma() {
      if (!anim) return;
      cancelAnimationFrame(anim.id); anim.btn.classList.remove("on"); anim.btn.textContent = "▶";
      anim = null;
    }

    function anima(k, btn) {
      if (anim) { const stesso = anim.k === k; ferma(); if (stesso) return; }
      const inp = input[k], lo = +inp.min, hi = +inp.max, ps = +inp.step || (hi - lo) / 100, t0 = performance.now();
      const nPassi = Math.round((hi - lo) / ps), discreto = Number.isInteger(ps) && ps > 0 && nPassi <= 400;
      let i0 = Math.round((+inp.value - lo) / ps);
      if (i0 >= nPassi) i0 = 0;
      btn.classList.add("on"); btn.textContent = "⏸";
      const step = (t) => {
        if (!document.body.contains(el)) return;
        // parametri a passi interi (passo dell'algoritmo, n, ...): un passo ogni 0,9 s, poi si ferma
        if (discreto) {
          const i = Math.min(nPassi, i0 + Math.floor((t - t0) / 900));
          if (+inp.value !== lo + i * ps) { inp.value = String(lo + i * ps); aggiorna(); }
          if (i >= nPassi) { setTimeout(ferma, 900); return; }
          anim.id = requestAnimationFrame(step);
          return;
        }
        const v = lo + (hi - lo) * (0.5 - 0.5 * Math.cos((t - t0) / 6000));
        inp.value = (lo + Math.round((v - lo) / ps) * ps).toFixed(6);
        aggiorna();
        if (anim) anim.id = requestAnimationFrame(step);
      };
      anim = { k, btn, id: requestAnimationFrame(step) };
    }

    // cambio di tema chiaro/scuro: si ridisegna con i colori giusti; il grafico
    // tolto dalla pagina (navigazione istantanea) smette di ascoltare
    osservatore = new MutationObserver(() => {
      if (!document.body.contains(el)) { osservatore.disconnect(); ferma(); return; }
      ultimaFormula = ultimeLetture = null;
      aggiorna(true);
    });
    osservatore.observe(document.body, { attributes: true, attributeFilter: ["data-md-color-scheme"] });

    aggiorna(true);
    typeset(el);
  }

  function montaTutti() {
    if (!window.JXG) return;
    document.querySelectorAll(".gi[data-grafico]").forEach(monta);
  }
  // si monta dopo che tutti gli script della pagina (anche i gi-*.js caricati
  // dopo questo file) sono stati eseguiti
  function avvia() {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", montaTutti, { once: true });
    else montaTutti();
  }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(avvia);
  else avvia();

  window.GI = Object.assign(window.GI || {}, {
    EN, T, num, numTxt, mj, h, typeset, derivata, gradiente, spezzata, nuvola, implicita, tabella,
    COLORI, registra, montaTutti,
  });
})();
