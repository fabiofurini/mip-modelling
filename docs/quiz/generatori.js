// Autovalutazione — domande generate del modulo «Modellazione MIP» (mip-modelling).
// Formato: QUIZ_SPEC.md. Ogni generatore riceve rng() in [0,1) e la lingua ("it" | "en") e restituisce
// { testo, opzioni[4], corretta, spiegazione, _v }. Il campo _v (dati dell'istanza) serve solo al gemello
// di verifica in Python (quiz/verifica/): il motore lo ignora.
// Nessuna dipendenza esterna, niente Math.random: solo rng. I dati si estraggono prima del testo, quindi
// lo stesso seme dà la stessa istanza nelle due lingue.
window.QUIZ_GEN = window.QUIZ_GEN || {};
(function () {
  "use strict";
  var MOD = "mip-modelling";
  var IT = "https://fabiofurini.github.io/modellazione-mip/";
  var EN = "https://fabiofurini.github.io/mip-modelling/";
  function L(it, en) { return { it: IT + it, en: EN + en }; }

  // ---------------------------------------------------------------- aiuti
  function ri(rng, a, b) { return a + Math.floor(rng() * (b - a + 1)); }
  function pick(rng, arr) { return arr[Math.floor(rng() * arr.length)]; }
  function sample(rng, arr, k) {
    var a = arr.slice(), out = [];
    while (out.length < k && a.length) out.push(a.splice(Math.floor(rng() * a.length), 1)[0]);
    return out;
  }
  function sum(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i]; return s; }
  function maxA(a) { return Math.max.apply(null, a); }
  function minA(a) { return Math.min.apply(null, a); }
  function distinct(arr) {
    var seen = {};
    for (var i = 0; i < arr.length; i++) { if (seen[arr[i]]) return false; seen[arr[i]] = true; }
    return true;
  }
  function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { var t = a % b; a = b; b = t; } return a; }
  function fr(n, d) { if (d < 0) { n = -n; d = -d; } var g = gcd(n, d) || 1; return { n: n / g, d: d / g }; }
  function frAdd(a, b) { return fr(a.n * b.d + b.n * a.d, a.d * b.d); }
  function frMul(a, b) { return fr(a.n * b.n, a.d * b.d); }
  function frKey(a) { return a.n + "/" + a.d; }
  /** frazione in TeX: intero se il denominatore è 1 */
  function frTex(a) {
    if (a.d === 1) return String(a.n);
    return (a.n < 0 ? "-" : "") + "\\tfrac{" + Math.abs(a.n) + "}{" + a.d + "}";
  }
  function tupla(a) { return "(" + a.join(", ") + ")"; }
  function T(l, it, en) { return l === "it" ? it : en; }
  /** vincolo lineare in TeX: termini [[coef, nome]], relazione, termine noto */
  function lin(terms, rel, rhs) {
    var s = "";
    terms.forEach(function (t, i) {
      var c = t[0], v = t[1], a = Math.abs(c);
      var coef = a === 1 ? "" : String(a);
      if (i === 0) s += (c < 0 ? "-" : "") + coef + v;
      else s += (c < 0 ? " - " : " + ") + coef + v;
    });
    return s + " " + rel + " " + rhs;
  }
  function xv(i) { return "x_{" + i + "}"; }
  function math(s) { return "$" + s + "$"; }
  function ins(l, list) {           // «$a$ e $b$» / «$a$ and $b$»
    return list.map(math).join(l === "it" ? " e " : " and ");
  }
  var REL = { le: "\\le", ge: "\\ge", eq: "=" };

  var G = [];

  // ================================================================ 6.8 big-M minimo
  G.push({
    id: "mip-g-bigm-minimo", livello: "facile", capitolo: "6-legami",
    link: L("legami-08/", "links-08/"),
    genera: function (rng, l) {
      var n, a, u, b, S, M, bin, opz;
      for (var tent = 0; tent < 200; tent++) {
        n = ri(rng, 3, 4); bin = rng() < 0.5;
        a = []; u = [];
        for (var j = 0; j < n; j++) { a.push(ri(rng, 2, 9)); u.push(bin ? 1 : ri(rng, 1, 3)); }
        S = 0; for (j = 0; j < n; j++) S += a[j] * u[j];
        b = ri(rng, 2, S - 3);
        M = S - b;
        var termMax = 0, termMin = 1e9;
        for (j = 0; j < n; j++) { termMax = Math.max(termMax, a[j] * u[j]); termMin = Math.min(termMin, a[j] * u[j]); }
        var d1 = S, d2 = S - b - termMin, d3 = termMax - b > 0 ? termMax - b : S + b;
        if (!bin && sum(a) - b > 0) d3 = sum(a) - b;
        opz = [M, d1, d2, d3];
        if (distinct(opz) && d2 > 0) break;
      }
      var terms = a.map(function (c, j) { return [c, xv(j + 1)]; });
      var vinc = lin(terms, "\\le", b);
      var vars = a.map(function (c, j) { return xv(j + 1); }).join(", ");
      var dom = bin ? T(l, "sono binarie", "are binary")
        : T(l, "sono intere con $0 \\le x_j \\le u_j$ e $u = " + tupla(u) + "$",
               "are integer with $0 \\le x_j \\le u_j$ and $u = " + tupla(u) + "$");
      var testo = T(l,
        "Le variabili $" + vars + "$ " + dom + ". Il vincolo $" + vinc + "$ deve valere solo quando la binaria $y$ vale $1$, e lo si scrive $" +
        lin(terms, "\\le", b + " + M(1 - y)") + "$. Qual è il più piccolo valore di $M$ di cui si dimostra la validità usando i soli bound delle variabili?",
        "The variables $" + vars + "$ " + dom + ". The constraint $" + vinc + "$ must hold only when the binary $y$ equals $1$, and it is written $" +
        lin(terms, "\\le", b + " + M(1 - y)") + "$. What is the smallest value of $M$ whose validity is proved from the variable bounds alone?");
      var spieg = T(l,
        "Con $y = 0$ il vincolo è spento solo se $M \\ge \\max a'x - b$. Il massimo di $a'x$ sui bound vale $" + S + "$, quindi $M = " + S + " - " + b + " = " + M +
        "$. Dimenticare di sottrarre $b$ dà un $M$ valido ma migliorabile; un valore più piccolo taglia soluzioni.",
        "With $y = 0$ the constraint is switched off only if $M \\ge \\max a'x - b$. The maximum of $a'x$ over the bounds is $" + S + "$, so $M = " + S + " - " + b + " = " + M +
        "$. Forgetting to subtract $b$ gives a valid but improvable $M$; a smaller value cuts off solutions.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg,
               _v: { a: a, u: u, b: b } };
    }
  });

  // ================================================================ 5 implicazioni -> vincoli
  var TIPI_IMPL = ["and_imp", "or_imp", "imp_and", "imp_or", "imp_not", "not_imp", "and_imp_not"];
  G.push({
    id: "mip-g-implicazione", livello: "facile", capitolo: "5-logica",
    link: L("modellazione-5/#implicazioni-logiche", "modelling-5/#logical-implications"),
    genera: function (rng, l) {
      var tipo = pick(rng, TIPI_IMPL);
      var idx = sample(rng, [1, 2, 3, 4, 5, 6, 7, 8, 9], 3).sort(function (p, q) { return p - q; });
      idx = sample(rng, idx, 3);                       // ordine casuale dei ruoli A, B, C
      var A = xv(idx[0]), B = xv(idx[1]), C = xv(idx[2]);
      var expr, giusta, sbagliate;
      // ogni opzione è un elenco di vincoli [termini, rel, rhs]
      if (tipo === "and_imp") {
        expr = A + " \\land " + B + " \\Rightarrow " + C;
        giusta = [[[[1, A], [1, B], [-1, C]], "le", 1]];
        sbagliate = [
          [[[[1, C], [-1, A]], "ge", 0], [[[1, C], [-1, B]], "ge", 0]],
          [[[[1, A], [1, B], [-1, C]], "le", 0]],
          [[[[1, A], [1, B], [1, C]], "le", 2]]];
      } else if (tipo === "or_imp") {
        expr = A + " \\lor " + B + " \\Rightarrow " + C;
        giusta = [[[[1, C], [-1, A]], "ge", 0], [[[1, C], [-1, B]], "ge", 0]];
        sbagliate = [
          [[[[1, A], [1, B], [-1, C]], "le", 1]],
          [[[[1, C], [-1, A], [-1, B]], "ge", 0]],
          [[[[1, A], [-1, C]], "ge", 0], [[[1, B], [-1, C]], "ge", 0]]];
      } else if (tipo === "imp_and") {
        expr = A + " \\Rightarrow " + B + " \\land " + C;
        giusta = [[[[1, B], [-1, A]], "ge", 0], [[[1, C], [-1, A]], "ge", 0]];
        sbagliate = [
          [[[[1, B], [1, C], [-1, A]], "ge", 0]],
          [[[[1, A], [-1, B]], "ge", 0], [[[1, A], [-1, C]], "ge", 0]],
          [[[[1, B], [1, C], [-1, A]], "ge", 1]]];
      } else if (tipo === "imp_or") {
        expr = A + " \\Rightarrow " + B + " \\lor " + C;
        giusta = [[[[1, B], [1, C], [-1, A]], "ge", 0]];
        sbagliate = [
          [[[[1, B], [-1, A]], "ge", 0], [[[1, C], [-1, A]], "ge", 0]],
          [[[[1, A], [-1, B], [-1, C]], "ge", 0]],
          [[[[1, B], [1, C], [-1, A]], "ge", 1]]];
      } else if (tipo === "imp_not") {
        expr = A + " \\Rightarrow \\lnot " + B;
        giusta = [[[[1, A], [1, B]], "le", 1]];
        sbagliate = [
          [[[[1, B], [-1, A]], "ge", 0]],
          [[[[1, A], [1, B]], "ge", 1]],
          [[[[1, A], [-1, B]], "ge", 0]]];
      } else if (tipo === "not_imp") {
        expr = "\\lnot " + A + " \\Rightarrow " + B;
        giusta = [[[[1, A], [1, B]], "ge", 1]];
        sbagliate = [
          [[[[1, A], [1, B]], "le", 1]],
          [[[[1, B], [-1, A]], "ge", 0]],
          [[[[1, A], [-1, B]], "ge", 0]]];
      } else {
        expr = A + " \\land " + B + " \\Rightarrow \\lnot " + C;
        giusta = [[[[1, A], [1, B], [1, C]], "le", 2]];
        sbagliate = [
          [[[[1, A], [1, B], [-1, C]], "le", 1]],
          [[[[1, A], [1, C]], "le", 1], [[[1, B], [1, C]], "le", 1]],
          [[[[1, A], [1, B], [1, C]], "le", 1]]];
      }
      function rend(opt) {
        return ins(l, opt.map(function (c) { return lin(c[0], REL[c[1]], c[2]); }));
      }
      var opz = [rend(giusta)].concat(sbagliate.map(rend));
      var testo = T(l,
        "Le variabili $" + [A, B, C].join(", ") + "$ sono binarie. Quale insieme di vincoli lineari traduce **esattamente** l'implicazione $" + expr + "$, cioè ammette tutte e sole le assegnazioni che la rendono vera?",
        "The variables $" + [A, B, C].join(", ") + "$ are binary. Which set of linear constraints translates **exactly** the implication $" + expr + "$, i.e. admits all and only the assignments that make it true?");
      var spieg = T(l,
        "Si porta l'implicazione in CNF ($p \\Rightarrow q$ è $\\lnot p \\lor q$), poi ogni clausola diventa un vincolo $\\ge 1$ con $1 - x$ per i letterali negativi: si ottiene " + rend(giusta) +
        ". Una disgiunzione nell'antecedente o una congiunzione nel conseguente costano due vincoli; scindere un antecedente congiunzione non è lecito.",
        "Bring the implication to CNF ($p \\Rightarrow q$ is $\\lnot p \\lor q$), then every clause becomes a constraint $\\ge 1$ with $1 - x$ for the negative literals: this gives " + rend(giusta) +
        ". A disjunction in the antecedent or a conjunction in the consequent costs two constraints; splitting a conjunctive antecedent is not allowed.");
      return { testo: testo, opzioni: opz, corretta: 0, spiegazione: spieg,
               _v: { tipo: tipo, idx: idx } };
    }
  });

  // ================================================================ conteggio di variabili e vincoli
  // Ogni modello: nome, famiglie di vincoli, variabili, dimensioni (lettere del corso), formule e distrattori.
  // Le dimensioni sono a = primo indice, b = secondo indice (vedi «dim»).
  var MODELLI = {
    "7.2": { it: "Problema 7.2 (macchine con costo fisso)", en: "Problem 7.2 (machines with a fixed cost)",
      fam: "$\\sum_{m} x_{jm} = 1\\ \\forall j$, $\\ \\sum_{j} t_{jm} x_{jm} \\le a_m y_m\\ \\forall m$",
      vars: "$x_{jm}$ e $y_m$ binarie", varsEn: "$x_{jm}$ and $y_m$ binary",
      dim: ["n", "k", "lavori", "macchine", "jobs", "machines"],
      V: function (a, b) { return a * b + b; }, C: function (a, b) { return a + b; },
      dV: function (a, b) { return [a * b, a + b, a * b + a]; }, dC: function (a, b) { return [a * b + b, a, a + b + 1]; } },
    "7.4": { it: "Problema 7.4 (lavori in parallelo)", en: "Problem 7.4 (parallel jobs)",
      fam: "$\\sum_{m} x_{jm} = 1\\ \\forall j$, $\\ \\sum_{j} x_{jm} \\le p_m\\ \\forall m$, $\\ y_m \\ge t_{jm} x_{jm}\\ \\forall j, m$",
      vars: "$x_{jm}$ binarie e $y_m \\ge 0$", varsEn: "$x_{jm}$ binary and $y_m \\ge 0$",
      dim: ["n", "k", "lavori", "macchine", "jobs", "machines"],
      V: function (a, b) { return a * b + b; }, C: function (a, b) { return a + b + a * b; },
      dV: function (a, b) { return [a * b, a * b + a, a + b]; }, dC: function (a, b) { return [a + b, a * b + a, a + 2 * b]; } },
    "7.5": { it: "Problema 7.5 (classi con setup)", en: "Problem 7.5 (classes with setup)",
      fam: "$\\sum_{j} t_j x_j + \\sum_{c} s_c y_c \\le a$, $\\ x_j \\le y_c\\ \\forall c,\\ \\forall j \\in \\mathscr{J}_c$",
      vars: "$x_j$ e $y_c$ binarie", varsEn: "$x_j$ and $y_c$ binary",
      dim: ["n", "q", "lavori", "classi", "jobs", "classes"],
      V: function (a, b) { return a + b; }, C: function (a, b) { return 1 + a; },
      dV: function (a, b) { return [a * b + b, a, a * b]; }, dC: function (a, b) { return [1 + b, 1 + a * b, a]; } },
    "7.7": { it: "Problema 7.7 (ritardo totale su una macchina)", en: "Problem 7.7 (total tardiness on one machine)",
      fam: "$s_{ji} + s_{ij} = 1\\ \\forall j < i$, $\\ \\kappa_i \\ge \\kappa_j + t_i - M(1 - s_{ji})\\ \\forall j \\ne i$, $\\ \\tau_j \\ge \\kappa_j - d_j\\ \\forall j$, $\\ \\kappa_j \\ge t_j\\ \\forall j$",
      vars: "$s_{ji}$ binarie ($j \\ne i$), $\\kappa_j \\ge 0$ e $\\tau_j \\ge 0$", varsEn: "$s_{ji}$ binary ($j \\ne i$), $\\kappa_j \\ge 0$ and $\\tau_j \\ge 0$",
      dim: ["n", null, "lavori", null, "jobs", null],
      V: function (a) { return a * (a - 1) + 2 * a; }, C: function (a) { return a * (a - 1) / 2 + a * (a - 1) + 2 * a; },
      dV: function (a) { return [a * (a - 1) / 2 + 2 * a, a * a + 2 * a, a * (a - 1) + a]; },
      dC: function (a) { return [2 * a * (a - 1) + 2 * a, a * (a - 1) + 2 * a, a * (a - 1) / 2 + a * (a - 1) + a]; } },
    "8.2": { it: "Problema 8.2 (p-mediana)", en: "Problem 8.2 (p-median)",
      fam: "$\\sum_{l} y_{lc} = 1\\ \\forall c$, $\\ \\sum_{l} x_l \\le k$, $\\ x_l \\ge y_{lc}\\ \\forall l, c$",
      vars: "$x_l$ e $y_{lc}$ binarie", varsEn: "$x_l$ and $y_{lc}$ binary",
      dim: ["m", "n", "sedi candidate", "clienti", "candidate sites", "customers"],
      V: function (a, b) { return a + a * b; }, C: function (a, b) { return b + 1 + a * b; },
      dV: function (a, b) { return [a * b, b + a * b, a + b]; }, dC: function (a, b) { return [b + 1 + a, b + a * b, a + 1 + a * b]; } },
    "8.1": { it: "Problema 8.1 (localizzazione capacitata)", en: "Problem 8.1 (capacitated facility location)",
      fam: "$u_l x_l - \\sum_{c} y_{lc} \\ge 0\\ \\forall l$, $\\ \\sum_{l} y_{lc} = d_c\\ \\forall c$",
      vars: "$x_l$ binarie e $y_{lc} \\ge 0$", varsEn: "$x_l$ binary and $y_{lc} \\ge 0$",
      dim: ["m", "n", "sedi candidate", "clienti", "candidate sites", "customers"],
      V: function (a, b) { return a + a * b; }, C: function (a, b) { return a + b; },
      dV: function (a, b) { return [a * b, a + b, b + a * b]; }, dC: function (a, b) { return [a * b + b, a * b + a, a + b + a * b]; } },
    "8.4": { it: "Problema 8.4 (hub con costo massimo)", en: "Problem 8.4 (hubs with maximum cost)",
      fam: "$\\sum_{j} x_{ij} = 1\\ \\forall i$, $\\ \\sum_{i} x_{ij} \\le k\\, y_j\\ \\forall j$, $\\ z_j \\ge c_{ij} x_{ij}\\ \\forall i, j$",
      vars: "$x_{ij}$ e $y_j$ binarie, $z_j \\ge 0$", varsEn: "$x_{ij}$ and $y_j$ binary, $z_j \\ge 0$",
      dim: ["n", "m", "terminali", "hub", "terminals", "hubs"],
      V: function (a, b) { return a * b + 2 * b; }, C: function (a, b) { return a + b + a * b; },
      dV: function (a, b) { return [a * b + b, a * b + a + b, a * b]; }, dC: function (a, b) { return [a + b, a + a * b, a + 2 * b + a * b]; } }
  };
  function generaConteggio(chiavi) {
    return function (rng, l) {
      var key, a, b, cosa, giusto, dis;
      for (var tent = 0; tent < 200; tent++) {
        key = pick(rng, chiavi);
        a = ri(rng, 3, 7); b = ri(rng, 2, 4);
        if (key === "7.7") a = ri(rng, 3, 6);
        cosa = rng() < 0.5 ? "V" : "C";
        var Md = MODELLI[key];
        giusto = Md[cosa](a, b);
        dis = (cosa === "V" ? Md.dV : Md.dC)(a, b);
        if (distinct([giusto].concat(dis))) break;
      }
      var Mo = MODELLI[key], dm = Mo.dim;
      var dims = "$" + dm[0] + " = " + a + "$ " + T(l, dm[2], dm[4]);
      if (dm[1]) dims += T(l, " e ", " and ") + "$" + dm[1] + " = " + b + "$ " + T(l, dm[3], dm[5]);
      var domanda = cosa === "V" ? T(l, "quante variabili ha il modello?", "how many variables does the model have?")
        : T(l, "quanti vincoli lineari ha il modello, esclusi i vincoli di dominio?", "how many linear constraints does the model have, domain constraints excluded?");
      var testo = T(l,
        Mo.it + ". Le famiglie di vincoli sono " + Mo.fam + "; le variabili sono " + Mo.vars + ". Con " + dims + ", " + domanda,
        Mo.en + ". The constraint families are " + Mo.fam + "; the variables are " + Mo.varsEn + ". With " + dims + ", " + domanda);
      var spieg = T(l,
        "Si conta famiglia per famiglia, seguendo i quantificatori: il totale è $" + giusto + "$. Gli errori tipici sono contare le coppie ordinate al posto di quelle non ordinate e dimenticare una famiglia (o una variabile ausiliaria).",
        "Count family by family, following the quantifiers: the total is $" + giusto + "$. The typical mistakes are counting ordered pairs instead of unordered ones and forgetting a family (or an auxiliary variable).");
      return { testo: testo, opzioni: [giusto].concat(dis).map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg,
               _v: { modello: key, a: a, b: b, cosa: cosa } };
    };
  }
  G.push({
    id: "mip-g-conteggio-scheduling", livello: "facile", capitolo: "7-scheduling",
    link: L("scheduling/", "scheduling/"),
    genera: generaConteggio(["7.2", "7.4", "7.5", "7.7"])
  });
  G.push({
    id: "mip-g-conteggio-localizzazione", livello: "facile", capitolo: "8-localizzazione",
    link: L("localizzazione/", "location/"),
    genera: generaConteggio(["8.1", "8.2", "8.4"])
  });

  // ================================================================ 6.2 costo fisso: valore dell'obiettivo
  G.push({
    id: "mip-g-costo-fisso-valore", livello: "facile", capitolo: "6-legami",
    link: L("legami-02/", "links-02/"),
    genera: function (rng, l) {
      var m = 3, f, c, C, q, z, opz;
      for (var tent = 0; tent < 200; tent++) {
        f = []; c = []; C = []; q = [];
        for (var j = 0; j < m; j++) { f.push(ri(rng, 5, 20)); c.push(ri(rng, 1, 6)); C.push(ri(rng, 5, 10)); }
        var zero = ri(rng, 0, m - 1);
        for (j = 0; j < m; j++) q.push(j === zero ? 0 : ri(rng, 1, C[j]));
        var var_ = 0, fixUsed = 0, fixAll = sum(f), perUnit = 0;
        for (j = 0; j < m; j++) { var_ += c[j] * q[j]; if (q[j] > 0) fixUsed += f[j]; perUnit += f[j] * q[j]; }
        z = var_ + fixUsed;
        opz = [z, var_, var_ + fixAll, var_ + perUnit];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "Tre impianti con costi fissi $f = " + tupla(f) + "$, costi unitari $c = " + tupla(c) + "$ e capacità $C = " + tupla(C) +
        "$. Il modello minimizza $\\sum_j (c_j q_j + f_j y_j)$ con $q_j \\le C_j y_j$ e $y_j \\in \\{0,1\\}$. Fissate le quantità $q = " + tupla(q) +
        "$, qual è il valore dell'obiettivo con la scelta migliore delle $y_j$ compatibile con i vincoli?",
        "Three plants with fixed costs $f = " + tupla(f) + "$, unit costs $c = " + tupla(c) + "$ and capacities $C = " + tupla(C) +
        "$. The model minimises $\\sum_j (c_j q_j + f_j y_j)$ subject to $q_j \\le C_j y_j$ and $y_j \\in \\{0,1\\}$. With the quantities fixed at $q = " + tupla(q) +
        "$, what is the objective value under the best choice of the $y_j$ compatible with the constraints?");
      var spieg = T(l,
        "Un impianto che produce deve essere aperto ($q_j > 0 \\Rightarrow y_j = 1$, imposto dal vincolo); uno che non produce si chiude, perché $f_j > 0$. Si paga quindi il costo variabile più i soli costi fissi degli impianti con $q_j > 0$: $" + z +
        "$. Il costo fisso non si moltiplica per la quantità.",
        "A plant that produces must be open ($q_j > 0 \\Rightarrow y_j = 1$, imposed by the constraint); one that does not produce is closed, since $f_j > 0$. So one pays the variable cost plus only the fixed costs of the plants with $q_j > 0$: $" + z +
        "$. The fixed cost is not multiplied by the quantity.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg,
               _v: { f: f, c: c, C: C, q: q } };
    }
  });

  // ================================================================ 6.4 conteggio intero (tetto)
  G.push({
    id: "mip-g-conteggio-intero", livello: "facile", capitolo: "6-legami",
    link: L("legami-04/", "links-04/"),
    genera: function (rng, l) {
      var a, cap, S, w, opz;
      for (var tent = 0; tent < 200; tent++) {
        var n = ri(rng, 4, 6); a = [];
        for (var i = 0; i < n; i++) a.push(ri(rng, 2, 9));
        cap = ri(rng, 6, 15); S = sum(a);
        if (S % cap === 0 || S < 2 * cap) continue;
        w = Math.ceil(S / cap);
        opz = [String(w), String(Math.floor(S / cap)), frTex(fr(S, cap)), String(w + 1)];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "Pezzi di ingombro $a = " + tupla(a) + "$ vanno tutti spediti in scatole di capienza $c = " + cap +
        "$. Il modello minimizza $w$ con $\\sum_i a_i \\le c\\, w$ e $w \\in \\mathbb{Z}_{\\ge 0}$. Quanto vale $w$ all'ottimo?",
        "Items of size $a = " + tupla(a) + "$ must all be shipped in boxes of capacity $c = " + cap +
        "$. The model minimises $w$ subject to $\\sum_i a_i \\le c\\, w$ and $w \\in \\mathbb{Z}_{\\ge 0}$. What is the value of $w$ at the optimum?");
      var spieg = T(l,
        "Il vincolo dà $w \\ge " + S + "/" + cap + "$ e l'interezza lo porta a $\\lceil " + S + "/" + cap + " \\rceil = " + w +
        "$: il tetto non si scrive, lo realizza la dichiarazione $w$ intera. Il valore frazionario è quello del rilassamento.",
        "The constraint gives $w \\ge " + S + "/" + cap + "$ and integrality raises it to $\\lceil " + S + "/" + cap + " \\rceil = " + w +
        "$: the ceiling is not written, the declaration of $w$ as integer realises it. The fractional value is that of the relaxation.");
      return { testo: testo, opzioni: opz.map(math), corretta: 0, spiegazione: spieg, _v: { a: a, c: cap } };
    }
  });

  // ================================================================ 6.7 valore assoluto >= k: big-M
  G.push({
    id: "mip-g-assoluto-bigm", livello: "facile", capitolo: "6-legami",
    link: L("legami-07/#i-vincoli", "links-07/#the-constraints"),
    genera: function (rng, l) {
      var U, k, M, opz;
      for (var tent = 0; tent < 200; tent++) {
        U = ri(rng, 5, 30); k = ri(rng, 2, U - 2);
        M = U + k;
        var pool = [U, k, 2 * U, U - k, U + 2 * k, 2 * U + k];
        var d = [];
        for (var i = 0; i < pool.length && d.length < 3; i++) {
          var v = pick(rng, pool);
          if (v > 0 && v !== M && d.indexOf(v) < 0) d.push(v);
        }
        if (d.length === 3) { opz = [M].concat(d); if (distinct(opz)) break; }
      }
      var testo = T(l,
        "Le variabili continue $u, v$ stanno in $[0, " + U + "]$ e si vuole $|u - v| \\ge " + k + "$. Con una binaria $b$ si scrive $u - v \\ge " + k +
        " - M(1 - b)$ e $v - u \\ge " + k + " - M\\, b$. Qual è il più piccolo $M$ valido, ricavato dai bound?",
        "The continuous variables $u, v$ lie in $[0, " + U + "]$ and we want $|u - v| \\ge " + k + "$. With a binary $b$ one writes $u - v \\ge " + k +
        " - M(1 - b)$ and $v - u \\ge " + k + " - M\\, b$. What is the smallest valid $M$, derived from the bounds?");
      var spieg = T(l,
        "Quando un vincolo è spento deve valere per ogni $u, v$: per il primo serve $" + k + " - M \\le \\min (u - v) = -" + U + "$, cioè $M \\ge " + k + " + " + U + " = " + M +
        "$. Il caso $\\ge$ del valore assoluto non è convesso: è una disgiunzione, e la binaria è necessaria.",
        "When a constraint is switched off it must hold for every $u, v$: the first needs $" + k + " - M \\le \\min (u - v) = -" + U + "$, that is $M \\ge " + k + " + " + U + " = " + M +
        "$. The $\\ge$ case of the absolute value is not convex: it is a disjunction, and the binary is necessary.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { U: U, k: k } };
    }
  });

  // ================================================================ 6.9 precedenze: M
  G.push({
    id: "mip-g-precedenze-M", livello: "facile", capitolo: "6-legami",
    link: L("legami-09/", "links-09/"),
    genera: function (rng, l) {
      var t, M, opz;
      for (var tent = 0; tent < 200; tent++) {
        var n = ri(rng, 3, 5); t = [];
        for (var i = 0; i < n; i++) t.push(ri(rng, 2, 9));
        M = sum(t);
        opz = [M, maxA(t), M - minA(t), M - maxA(t)];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "Su una macchina si sequenziano lavori di durata $t = " + tupla(t) + "$ con $s_{ij} + s_{ji} = 1$ e $\\kappa_i \\ge \\kappa_j + t_i - M(1 - s_{ij})$, $\\kappa_j \\ge t_j$, cercando l'ottimo fra le sequenze senza tempi morti. Qual è il più piccolo $M$ che il corso dimostra valido?",
        "Jobs of duration $t = " + tupla(t) + "$ are sequenced on one machine with $s_{ij} + s_{ji} = 1$ and $\\kappa_i \\ge \\kappa_j + t_i - M(1 - s_{ij})$, $\\kappa_j \\ge t_j$, looking for the optimum among sequences without idle time. What is the smallest $M$ the course proves valid?");
      var spieg = T(l,
        "Senza tempi morti $\\kappa_j \\le \\sum_h t_h$, e con $M = \\sum_h t_h = " + M + "$ si ha $\\kappa_j + t_i - M \\le t_i \\le \\kappa_i$: il vincolo spento non taglia nulla. Un valore più piccolo fallisce quando $j$ è l'ultimo lavoro e $i$ il primo. L'orizzonte va dichiarato.",
        "Without idle time $\\kappa_j \\le \\sum_h t_h$, and with $M = \\sum_h t_h = " + M + "$ one has $\\kappa_j + t_i - M \\le t_i \\le \\kappa_i$: the switched-off constraint cuts nothing. A smaller value fails when $j$ is the last job and $i$ the first. The horizon must be declared.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { t: t } };
    }
  });

  // ================================================================ 6.14 funzione a tratti
  G.push({
    id: "mip-g-tratti", livello: "facile", capitolo: "6-legami",
    link: L("legami-14/", "links-14/"),
    genera: function (rng, l) {
      var qn, gv, s, qb, val, env, wrong, opz, seg;
      for (var tent = 0; tent < 300; tent++) {
        var l1 = ri(rng, 2, 5), l2 = ri(rng, 2, 5), l3 = ri(rng, 2, 6);
        var s1 = ri(rng, 4, 6), s2 = ri(rng, 2, s1 - 1), s3 = ri(rng, 1, s2 - 1);
        qn = [0, l1, l1 + l2, l1 + l2 + l3]; s = [s1, s2, s3];
        gv = [0, s1 * l1, s1 * l1 + s2 * l2, s1 * l1 + s2 * l2 + s3 * l3];
        seg = ri(rng, 2, 3);                 // tratto 2 o 3
        qb = ri(rng, qn[seg - 1] + 1, qn[seg] - 1);
        if (qb <= qn[seg - 1] || qb >= qn[seg]) continue;
        val = gv[seg - 1] + s[seg - 1] * (qb - qn[seg - 1]);
        env = fr(gv[3] * qb, qn[3]);          // corda da (0,0) a (q3,g3): inviluppo convesso inferiore
        wrong = gv[seg - 2] + s[seg - 2] * (qb - qn[seg - 2]);   // pendenza del tratto precedente
        opz = [frTex(fr(val, 1)), frTex(env), String(wrong), String(gv[seg])];
        if (distinct(opz) && !(env.d === 1 && env.n === val)) break;
      }
      var testo = T(l,
        "Il costo $g(q)$ è continuo e lineare a tratti, con nodi $(" + qn.join(", ") + ")$ e valori $(" + gv.join(", ") +
        ")$ (sconti di quantità: non è convesso). Nel modello con combinazione convessa $\\lambda_k$, binarie di tratto $w_t$ e vincoli di adiacenza, si fissa $q = " + qb + "$. Quanto vale $g(q)$?",
        "The cost $g(q)$ is continuous and piecewise linear, with breakpoints $(" + qn.join(", ") + ")$ and values $(" + gv.join(", ") +
        ")$ (quantity discounts: it is not convex). In the model with convex combination $\\lambda_k$, segment binaries $w_t$ and adjacency constraints, $q = " + qb + "$ is fixed. What is $g(q)$?");
      var spieg = T(l,
        "Con l'adiacenza sono positive solo le $\\lambda$ dei due nodi del tratto che contiene $q$, e $(q, g)$ sta sul grafico: $g(" + qb + ") = " + val +
        "$. Senza adiacenza il modello mescolerebbe i nodi estremi e scenderebbe all'inviluppo convesso inferiore, $" + frTex(env) + "$.",
        "With adjacency only the $\\lambda$ of the two breakpoints of the segment containing $q$ are positive, and $(q, g)$ lies on the graph: $g(" + qb + ") = " + val +
        "$. Without adjacency the model would mix the extreme breakpoints and drop to the lower convex envelope, $" + frTex(env) + "$.");
      return { testo: testo, opzioni: opz.map(math), corretta: 0, spiegazione: spieg, _v: { nodi: qn, valori: gv, q: qb } };
    }
  });

  // ================================================================ 4 LPT
  function lpt(t, k, ordine) {
    var Ld = []; for (var m = 0; m < k; m++) Ld.push(0);
    ordine.forEach(function (j) {
      var best = 0; for (var m2 = 1; m2 < k; m2++) if (Ld[m2] < Ld[best]) best = m2;
      Ld[best] += t[j];
    });
    return Ld;
  }
  G.push({
    id: "mip-g-lpt", livello: "facile", capitolo: "4-euristiche",
    link: L("modellazione-4/#pc_max-la-regola-del-meno-carico", "modelling-4/#pc_max-the-least-loaded-rule"),
    genera: function (rng, l) {
      var t, k, opz;
      for (var tent = 0; tent < 300; tent++) {
        var n = ri(rng, 6, 7); k = ri(rng, 2, 3); t = [];
        for (var i = 0; i < n; i++) t.push(ri(rng, 2, 9));
        var idx = t.map(function (_, j) { return j; });
        var ord = idx.slice().sort(function (p, q) { return t[q] - t[p] || p - q; });
        var Lp = lpt(t, k, ord), Ls = lpt(t, k, idx);
        var lb = Math.max(maxA(t), Math.ceil(sum(t) / k));
        opz = [maxA(Lp), maxA(Ls), lb, minA(Lp)];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "I lavori di durata $t = " + tupla(t) + "$ vanno su $k = " + k + "$ macchine identiche, minimizzando il makespan. Che valore restituisce LPT (lavori per durata decrescente, ciascuno sulla macchina meno carica, pareggi sull'indice più piccolo)?",
        "Jobs of duration $t = " + tupla(t) + "$ go on $k = " + k + "$ identical machines, minimising the makespan. What value does LPT return (jobs by decreasing duration, each on the least loaded machine, ties broken by the smallest index)?");
      var spieg = T(l,
        "LPT ordina i lavori per durata decrescente e mette ciascuno sulla macchina meno carica; il makespan è il carico massimo finale, $" + opz[0] +
        "$. È un upper bound, perché il problema è di minimo; $\\max(\\max_j t_j, \\lceil \\sum_j t_j / k \\rceil)$ è invece un lower bound.",
        "LPT sorts the jobs by decreasing duration and puts each on the least loaded machine; the makespan is the largest final load, $" + opz[0] +
        "$. It is an upper bound, since the problem is a minimisation; $\\max(\\max_j t_j, \\lceil \\sum_j t_j / k \\rceil)$ is instead a lower bound.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { t: t, k: k } };
    }
  });

  // ================================================================ 4 bin packing
  function binpack(w, C, regola) {
    var res = [];
    var cur = -1;
    w.forEach(function (x) {
      var b = -1;
      if (regola === "nf") { if (cur >= 0 && res[cur] >= x) b = cur; }
      else if (regola === "ff") { for (var i = 0; i < res.length; i++) if (res[i] >= x) { b = i; break; } }
      else { var bestR = 1e9; for (var i2 = 0; i2 < res.length; i2++) if (res[i2] >= x && res[i2] - x < bestR) { bestR = res[i2] - x; b = i2; } }
      if (b < 0) { res.push(C); b = res.length - 1; cur = b; }
      res[b] -= x;
    });
    return res.length;
  }
  var NOMI_BPP = { nf: "next-fit", ff: "first-fit", bf: "best-fit" };
  G.push({
    id: "mip-g-bin-packing", livello: "facile", capitolo: "4-euristiche",
    link: L("modellazione-4/#bin-packing-le-regole-di-inserimento", "modelling-4/#bin-packing-the-insertion-rules"),
    genera: function (rng, l) {
      var w, C, regola, giusto, opz;
      for (var tent = 0; tent < 400; tent++) {
        var n = ri(rng, 6, 8); C = ri(rng, 7, 10); w = [];
        for (var i = 0; i < n; i++) w.push(ri(rng, 2, C - 3));
        regola = pick(rng, ["nf", "ff", "bf"]);
        giusto = binpack(w, C, regola);
        var lb = Math.ceil(sum(w) / C);
        var cand = [binpack(w, C, "nf"), binpack(w, C, "ff"), binpack(w, C, "bf"), lb, giusto + 1, giusto - 1];
        var d = [];
        cand.forEach(function (v) { if (v > 0 && v !== giusto && d.indexOf(v) < 0 && d.length < 3) d.push(v); });
        if (d.length === 3) { opz = [giusto].concat(d); break; }
      }
      var testo = T(l,
        "Oggetti di peso $w = " + tupla(w) + "$, nell'ordine dato, vanno in contenitori di capacità $C = " + C + "$. Quanti contenitori usa il **" + NOMI_BPP[regola] +
        "** (best-fit: fra i contenitori in cui l'oggetto entra, quello con il residuo più piccolo; pareggi sull'indice più piccolo)?",
        "Items of weight $w = " + tupla(w) + "$, in the given order, go into bins of capacity $C = " + C + "$. How many bins does **" + NOMI_BPP[regola] +
        "** use (best-fit: among the bins where the item fits, the one with the smallest residual; ties broken by the smallest index)?");
      var spieg = T(l,
        "Eseguendo la regola oggetto per oggetto si aprono $" + giusto + "$ contenitori. Next-fit guarda solo il contenitore corrente, first-fit il primo in cui l'oggetto entra, best-fit quello che resta più pieno; $\\lceil \\sum_j w_j / C \\rceil$ è il lower bound elementare.",
        "Running the rule item by item opens $" + giusto + "$ bins. Next-fit looks only at the current bin, first-fit at the first bin where the item fits, best-fit at the one left fullest; $\\lceil \\sum_j w_j / C \\rceil$ is the elementary lower bound.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { w: w, C: C, regola: regola } };
    }
  });

  // ================================================================ 2 duale: azzerare e saturare
  G.push({
    id: "mip-g-duale-azzera", livello: "facile", capitolo: "2-bound-duali",
    link: L("modellazione-2/#tre-ricette-per-costruire-a-mano-una-soluzione-duale", "modelling-2/#three-recipes-for-building-a-dual-solution-by-hand"),
    genera: function (rng, l) {
      var n, k = 3, c, LB, opz;
      for (var tent = 0; tent < 300; tent++) {
        n = ri(rng, 3, 4); c = [];
        for (var j = 0; j < n; j++) { var row = []; for (var m = 0; m < k; m++) row.push(ri(rng, 1, 12)); c.push(row); }
        LB = 0; var mx = 0, colmin = 0;
        for (j = 0; j < n; j++) { LB += minA(c[j]); mx += maxA(c[j]); }
        var tot = []; for (m = 0; m < k; m++) { var s = 0, cm = 1e9; for (j = 0; j < n; j++) { s += c[j][m]; cm = Math.min(cm, c[j][m]); } tot.push(s); colmin += cm; }
        opz = [LB, mx, minA(tot), colmin];
        if (distinct(opz)) break;
      }
      var righe = c.map(function (r) { return "(" + r.join(", ") + ")"; }).join(", ");
      var testo = T(l,
        "Nel problema 7.1 (assegnamento a costo minimo con disponibilità) ci sono $n = " + n + "$ lavori e $k = 3$ macchine; le righe dei costi $c_{jm}$, una per lavoro, sono " + righe +
        ". Nel duale del rilassamento si applica la ricetta «azzerare e saturare»: $\\bar\\pi = 0$ sulle disponibilità e ogni $\\bar\\mu_j$ al valore più grande ammissibile. Quanto vale il bound che si ottiene?",
        "In problem 7.1 (minimum-cost assignment with availability) there are $n = " + n + "$ jobs and $k = 3$ machines; the rows of the costs $c_{jm}$, one per job, are " + righe +
        ". In the dual of the relaxation one applies the recipe \"zero out and saturate\": $\\bar\\pi = 0$ on the availabilities and each $\\bar\\mu_j$ at the largest feasible value. What bound is obtained?");
      var spieg = T(l,
        "Con $\\bar\\pi = 0$ i vincoli duali diventano $\\mu_j \\le c_{jm}$ per ogni $m$, quindi $\\bar\\mu_j = \\min_m c_{jm}$ e il bound è $\\sum_j \\min_m c_{jm} = " + LB +
        "$: «ogni lavoro costa almeno il suo costo minimo». In un minimo è un lower bound, valido per dualità debole.",
        "With $\\bar\\pi = 0$ the dual constraints become $\\mu_j \\le c_{jm}$ for every $m$, so $\\bar\\mu_j = \\min_m c_{jm}$ and the bound is $\\sum_j \\min_m c_{jm} = " + LB +
        "$: \"every job costs at least its minimum cost\". In a minimisation it is a lower bound, valid by weak duality.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { c: c } };
    }
  });

  // ================================================================ 6.10 se e solo se (prodotto di binarie)
  G.push({
    id: "mip-g-se-e-solo-se", livello: "facile", capitolo: "6-legami",
    link: L("legami-10/", "links-10/"),
    genera: function (rng, l) {
      var p = ri(rng, 2, 4);
      var xs = []; for (var j = 1; j <= p; j++) xs.push([1, xv(j)]);
      var somma = xs.map(function (t, i) { return (i ? " + " : "") + t[1]; }).join("");
      var giusta = "y \\ge " + somma + " - " + (p - 1);
      var d1 = "y \\ge " + somma + " - " + p;
      var d2 = p + "y \\ge " + somma;
      var d3 = "y \\le " + somma + " - " + (p - 1);
      var testo = T(l,
        "Le variabili $" + xs.map(function (t) { return t[1]; }).join(", ") + ", y$ sono binarie e si vuole $y = 1$ **se e solo se** $" + xs.map(function (t) { return t[1]; }).join(" = ") +
        " = 1$ (cioè $y$ è il prodotto delle $x$). I vincoli $y \\le x_j$, $j \\in \\{1, \\dots, " + p + "\\}$, sono già nel modello. Quale vincolo va aggiunto per avere il legame nei due versi in ogni soluzione ammissibile?",
        "The variables $" + xs.map(function (t) { return t[1]; }).join(", ") + ", y$ are binary and we want $y = 1$ **if and only if** $" + xs.map(function (t) { return t[1]; }).join(" = ") +
        " = 1$ (i.e. $y$ is the product of the $x$). The constraints $y \\le x_j$, $j \\in \\{1, \\dots, " + p + "\\}$, are already in the model. Which constraint must be added to have the link in both directions in every feasible solution?");
      var spieg = T(l,
        "Se tutte le $x_j$ valgono $1$ il membro destro di $" + giusta + "$ vale $1$ e forza $y = 1$; se almeno una è nulla vale al più $0$ e non dice nulla. Con $-" + p +
        "$ al posto di $-" + (p - 1) + "$ il vincolo non morde mai.",
        "If all $x_j$ equal $1$ the right-hand side of $" + giusta + "$ is $1$ and forces $y = 1$; if at least one is zero it is at most $0$ and says nothing. With $-" + p +
        "$ instead of $-" + (p - 1) + "$ the constraint never bites.");
      return { testo: testo, opzioni: [giusta, d1, d2, d3].map(math), corretta: 0, spiegazione: spieg, _v: { p: p } };
    }
  });

  // ================================================================ (media) 2/4 zaino: il sandwich
  G.push({
    id: "mip-g-zaino-sandwich", livello: "media", capitolo: "2-bound-duali",
    link: L("modellazione-2/#un-problema-di-massimo-i-ruoli-si-scambiano", "modelling-2/#a-maximisation-problem-the-roles-swap"),
    genera: function (rng, l) {
      var p, w, C, Gv, Gs, ub, ubmin, opz, ord, ok;
      for (var tent = 0; tent < 400; tent++) {
        var n = ri(rng, 4, 5); p = []; w = [];
        for (var j = 0; j < n; j++) { w.push(ri(rng, 2, 7)); p.push(ri(rng, 3, 15)); }
        var rat = p.map(function (pj, jj) { return fr(pj, w[jj]); });
        ok = true;
        for (var a1 = 0; a1 < n; a1++) for (var a2 = a1 + 1; a2 < n; a2++) if (frKey(rat[a1]) === frKey(rat[a2])) ok = false;
        if (!ok) continue;
        C = ri(rng, Math.ceil(sum(w) / 3), Math.floor(sum(w) * 2 / 3));
        ord = p.map(function (_, jj) { return jj; }).sort(function (x, y) { return p[y] * w[x] - p[x] * w[y]; });
        var res = C; Gv = 0;
        ord.forEach(function (jj) { if (w[jj] <= res) { res -= w[jj]; Gv += p[jj]; } });
        res = C; Gs = 0; var stop = false;
        ord.forEach(function (jj) { if (stop) return; if (w[jj] <= res) { res -= w[jj]; Gs += p[jj]; } else stop = true; });
        var best = rat[ord[0]], worst = rat[ord[n - 1]];
        ub = frMul(fr(C, 1), best); ubmin = frMul(fr(C, 1), worst);
        if (Gv === Gs) continue;
        opz = [
          "$\\lb = " + Gv + "$, $\\ub = " + frTex(ub) + "$",
          "$\\lb = " + Gs + "$, $\\ub = " + frTex(ub) + "$",
          "$\\lb = " + Gv + "$, $\\ub = " + sum(p) + "$",
          "$\\lb = " + frTex(ub) + "$, $\\ub = " + Gv + "$"];
        if (distinct(opz) && sum(p) > ub.n / ub.d) break;
      }
      var testo = T(l,
        "Zaino binario: valori $p = " + tupla(p) + "$, pesi $w = " + tupla(w) + "$, capacità $C = " + C +
        "$, da massimizzare. L'euristica costruttiva scandisce gli oggetti per $p_j/w_j$ decrescente e prende ogni oggetto che ci sta ancora; la soluzione duale a mano è $\\bar v = \\max_j p_j / w_j$ sull'unico vincolo. Quali bound si ottengono?",
        "Binary knapsack: values $p = " + tupla(p) + "$, weights $w = " + tupla(w) + "$, capacity $C = " + C +
        "$, to be maximised. The constructive heuristic scans the items by decreasing $p_j/w_j$ and takes every item that still fits; the hand-made dual solution is $\\bar v = \\max_j p_j / w_j$ on the only constraint. Which bounds are obtained?");
      var spieg = T(l,
        "In un massimo l'euristica dà un lower bound: $\\lb = " + Gv + "$ (non ci si ferma al primo oggetto che non entra). Il duale dà un upper bound: $\\ub = C \\cdot \\max_j p_j/w_j = " + frTex(ub) +
        "$, ammissibile perché $w_j \\bar v \\ge p_j$ per ogni $j$. In un minimo i nomi si scambierebbero.",
        "In a maximisation the heuristic gives a lower bound: $\\lb = " + Gv + "$ (one does not stop at the first item that does not fit). The dual gives an upper bound: $\\ub = C \\cdot \\max_j p_j/w_j = " + frTex(ub) +
        "$, feasible because $w_j \\bar v \\ge p_j$ for every $j$. In a minimisation the names would swap.");
      return { testo: testo, opzioni: opz, corretta: 0, spiegazione: spieg, _v: { p: p, w: w, C: C } };
    }
  });

  // ================================================================ (media) 6.8 disgiunzione: due M
  G.push({
    id: "mip-g-disgiunzione", livello: "media", capitolo: "6-legami",
    link: L("legami-08/", "links-08/"),
    genera: function (rng, l) {
      var U, a, cc, b1, b2, M1, M2, S1, S2, opz;
      for (var tent = 0; tent < 300; tent++) {
        U = [ri(rng, 2, 6), ri(rng, 2, 6)];
        a = [ri(rng, 1, 6), ri(rng, 1, 6)]; cc = [ri(rng, 1, 6), ri(rng, 1, 6)];
        S1 = a[0] * U[0] + a[1] * U[1]; S2 = cc[0] * U[0] + cc[1] * U[1];
        b1 = ri(rng, 2, S1 - 2); b2 = ri(rng, 2, S2 - 2);
        M1 = S1 - b1; M2 = S2 - b2;
        var mm = Math.max(M1, M2);
        opz = ["(" + M1 + ", " + M2 + ")", "(" + M2 + ", " + M1 + ")", "(" + S1 + ", " + S2 + ")", "(" + mm + ", " + mm + ")"];
        if (M1 !== M2 && distinct(opz)) break;
      }
      var v1 = lin([[a[0], "x_1"], [a[1], "x_2"]], "\\le", b1), v2 = lin([[cc[0], "x_1"], [cc[1], "x_2"]], "\\le", b2);
      var testo = T(l,
        "Le variabili sono intere con $0 \\le x_1 \\le " + U[0] + "$ e $0 \\le x_2 \\le " + U[1] + "$, e deve valere **almeno uno** dei vincoli $" + v1 + "$ oppure $" + v2 +
        "$. Con una binaria $y$ si scrive $" + lin([[a[0], "x_1"], [a[1], "x_2"]], "\\le", b1 + " + M_1(1 - y)") + "$ e $" + lin([[cc[0], "x_1"], [cc[1], "x_2"]], "\\le", b2 + " + M_2\\, y") +
        "$. Quali sono i più piccoli valori $(M_1, M_2)$ validi, ricavati dai bound?",
        "The variables are integer with $0 \\le x_1 \\le " + U[0] + "$ and $0 \\le x_2 \\le " + U[1] + "$, and **at least one** of the constraints $" + v1 + "$ or $" + v2 +
        "$ must hold. With a binary $y$ one writes $" + lin([[a[0], "x_1"], [a[1], "x_2"]], "\\le", b1 + " + M_1(1 - y)") + "$ and $" + lin([[cc[0], "x_1"], [cc[1], "x_2"]], "\\le", b2 + " + M_2\\, y") +
        "$. What are the smallest valid values $(M_1, M_2)$, derived from the bounds?");
      var spieg = T(l,
        "Ogni vincolo, quando è spento, deve essere soddisfatto da ogni punto dei bound: $M_1 = " + S1 + " - " + b1 + " = " + M1 + "$ e $M_2 = " + S2 + " - " + b2 + " = " + M2 +
        "$. Ogni vincolo ha il suo $M$; usare il più grande per entrambi è valido ma indebolisce il rilassamento.",
        "Each constraint, when switched off, must be satisfied by every point of the bounds: $M_1 = " + S1 + " - " + b1 + " = " + M1 + "$ and $M_2 = " + S2 + " - " + b2 + " = " + M2 +
        "$. Each constraint has its own $M$; using the larger one for both is valid but weakens the relaxation.");
      return { testo: testo, opzioni: opz.map(math), corretta: 0, spiegazione: spieg, _v: { U: U, a: a, c: cc, b1: b1, b2: b2 } };
    }
  });

  // ================================================================ (media) 4 TSP vicino più vicino
  function nnTour(D, s) {
    var n = D.length, vis = [s], cur = s, len = 0;
    while (vis.length < n) {
      var best = -1;
      for (var j = 0; j < n; j++) if (vis.indexOf(j) < 0 && (best < 0 || D[cur][j] < D[cur][best])) best = j;
      len += D[cur][best]; vis.push(best); cur = best;
    }
    return { len: len + D[cur][s], open: len, giro: vis };
  }
  function tspOpt(D) {
    var n = D.length, best = 1e9;
    function rec(path, used, len) {
      if (path.length === n) { best = Math.min(best, len + D[path[n - 1]][path[0]]); return; }
      for (var j = 1; j < n; j++) if (!used[j]) { used[j] = true; path.push(j); rec(path, used, len + D[path[path.length - 2]][j]); path.pop(); used[j] = false; }
    }
    var u = []; u[0] = true; rec([0], u, 0);
    return best;
  }
  G.push({
    id: "mip-g-tsp-vicino", livello: "media", capitolo: "4-euristiche",
    link: L("modellazione-4/#tsp-il-vicino-piu-vicino", "modelling-4/#tsp-the-nearest-neighbour"),
    genera: function (rng, l) {
      var D, s, r, opz;
      for (var tent = 0; tent < 400; tent++) {
        var n = 5; D = [];
        for (var i = 0; i < n; i++) { D.push([]); for (var j = 0; j < n; j++) D[i].push(0); }
        for (i = 0; i < n; i++) for (j = i + 1; j < n; j++) { D[i][j] = D[j][i] = ri(rng, 1, 9); }
        s = ri(rng, 0, n - 1);
        r = nnTour(D, s);
        var altro = nnTour(D, s === 0 ? 1 : 0).len;
        var opt = tspOpt(D);
        var cand = [r.open, altro, opt, r.len + 1];
        var d = [];
        cand.forEach(function (v) { if (v !== r.len && d.indexOf(v) < 0 && d.length < 3) d.push(v); });
        if (d.length === 3) { opz = [r.len].concat(d); break; }
      }
      var righe = D.map(function (row, i) { return (i + 1) + ": (" + row.map(function (v, j) { return i === j ? "-" : v; }).join(", ") + ")"; }).join("; ");
      var testo = T(l,
        "Cinque città con distanze simmetriche, riga per riga: " + righe + ". Partendo dalla città " + (s + 1) +
        ", il vicino più vicino va ogni volta alla città non visitata più vicina (pareggi sull'indice più piccolo) e alla fine torna alla partenza. Quanto è lungo il giro?",
        "Five cities with symmetric distances, row by row: " + righe + ". Starting from city " + (s + 1) +
        ", nearest neighbour always moves to the closest unvisited city (ties broken by the smallest index) and finally returns to the start. How long is the tour?");
      var spieg = T(l,
        "Il giro è $" + r.giro.map(function (v) { return v + 1; }).join(" \\to ") + " \\to " + (s + 1) + "$, lungo $" + r.len +
        "$, compreso l'arco di ritorno (spesso il più caro). È una soluzione ammissibile, quindi un upper bound: non dice nulla sulla distanza dall'ottimo.",
        "The tour is $" + r.giro.map(function (v) { return v + 1; }).join(" \\to ") + " \\to " + (s + 1) + "$, of length $" + r.len +
        "$, including the return arc (often the most expensive one). It is a feasible solution, hence an upper bound: it says nothing about the distance from the optimum.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { D: D, s: s } };
    }
  });

  // ================================================================ (media) 2/4 copertura: euristica e duale
  var COPPIE = [[0, 1], [1, 2], [0, 2], [0, 3], [1, 3], [2, 3]];
  function coverGreedy(c, byRatio) {
    var scop = [0, 1, 2, 3, 4, 5], scelti = [], cost = 0;
    while (scop.length) {
      var best = -1, bv = 0;
      for (var j = 0; j < 4; j++) {
        if (scelti.indexOf(j) >= 0) continue;
        var nuove = scop.filter(function (i) { return COPPIE[i].indexOf(j) >= 0; }).length;
        if (!nuove) continue;
        var v = byRatio ? c[j] / nuove : c[j];
        if (best < 0 || v < bv - 1e-12) { best = j; bv = v; }
      }
      scelti.push(best); cost += c[best];
      scop = scop.filter(function (i) { return COPPIE[i].indexOf(best) < 0; });
    }
    return cost;
  }
  function coverDual(c, aggiorna) {
    var res = c.slice(), tot = 0;
    COPPIE.forEach(function (pr) {
      var v = Math.min(res[pr[0]], res[pr[1]]);
      tot += v;
      if (aggiorna) { res[pr[0]] -= v; res[pr[1]] -= v; }
    });
    return tot;
  }
  G.push({
    id: "mip-g-copertura-bound", livello: "media", capitolo: "4-euristiche",
    link: L("modellazione-4/#set-covering-la-regola-del-completamento-piu-economico", "modelling-4/#set-covering-the-cheapest-completion-rule"),
    genera: function (rng, l) {
      var c, ub, lb, ubAbs, lbNo, opz;
      for (var tent = 0; tent < 400; tent++) {
        c = [ri(rng, 2, 9), ri(rng, 2, 9), ri(rng, 2, 9), ri(rng, 2, 9)];
        ub = coverGreedy(c, true); ubAbs = coverGreedy(c, false);
        lb = coverDual(c, true); lbNo = coverDual(c, false);
        var lbMax = 0; COPPIE.forEach(function (pr) { lbMax += Math.max(c[pr[0]], c[pr[1]]); });
        var cand = [[lb, ub], [ub, lbNo], [ubAbs, lb], [ub, lbMax]];
        var vis = [ub + "|" + lb], d = [];
        cand.forEach(function (pq) { var key = pq[0] + "|" + pq[1]; if (vis.indexOf(key) < 0 && d.length < 3) { vis.push(key); d.push(pq); } });
        if (d.length === 3 && lb < ub) { opz = [[ub, lb]].concat(d); break; }
      }
      var testo = T(l,
        "Quattro squadre di costo $c = " + tupla(c) + "$ devono coprire sei zone, ciascuna al confine fra due distretti: nell'ordine $\\{1,2\\}, \\{2,3\\}, \\{1,3\\}, \\{1,4\\}, \\{2,4\\}, \\{3,4\\}$ (problema di minimo). " +
        "L'euristica costruttiva sceglie ogni volta la squadra di costo minimo per zona nuova coperta; la soluzione duale a mano scorre le zone nell'ordine dato, alza $\\pi_i$ fino a saturare il primo vincolo duale e aggiorna i residui. Quali sono $(\\ub, \\lb)$?",
        "Four teams of cost $c = " + tupla(c) + "$ must cover six zones, each on the border between two districts: in order $\\{1,2\\}, \\{2,3\\}, \\{1,3\\}, \\{1,4\\}, \\{2,4\\}, \\{3,4\\}$ (minimisation). " +
        "The constructive heuristic always picks the team of minimum cost per newly covered zone; the hand-made dual solution scans the zones in the given order, raises $\\pi_i$ until the first dual constraint is saturated and updates the residuals. What are $(\\ub, \\lb)$?");
      var spieg = T(l,
        "L'euristica dà una copertura ammissibile di costo $\\ub = " + ub + "$; la ricetta duale dà $\\lb = " + lb +
        "$, ammissibile perché ogni residuo resta non negativo. Senza aggiornare i residui la soluzione duale non è ammissibile e il suo valore non è un bound.",
        "The heuristic gives a feasible cover of cost $\\ub = " + ub + "$; the dual recipe gives $\\lb = " + lb +
        "$, feasible because every residual stays non-negative. Without updating the residuals the dual solution is infeasible and its value is not a bound.");
      return { testo: testo, opzioni: opz.map(function (pq) { return "$(" + pq[0] + ", " + pq[1] + ")$"; }), corretta: 0, spiegazione: spieg, _v: { c: c } };
    }
  });

  // ================================================================ (media) 6.6 tre obiettivi di equità
  G.push({
    id: "mip-g-equita", livello: "media", capitolo: "6-legami",
    link: L("legami-06/", "links-06/"),
    genera: function (rng, l) {
      var p, S, H, Lo, opz;
      for (var tent = 0; tent < 300; tent++) {
        p = []; for (var i = 0; i < 5; i++) p.push(ri(rng, 2, 9));
        S = sum(p); if (S % 2 === 0) continue;
        H = 1e9;
        for (var mask = 0; mask < 32; mask++) { var a = 0; for (i = 0; i < 5; i++) if (mask >> i & 1) a += p[i]; H = Math.min(H, Math.max(a, S - a)); }
        Lo = S - H;
        var half = frTex(fr(S, 2));
        opz = ["(" + H + ", " + Lo + ", " + (H - Lo) + ")", "(" + half + ", " + half + ", 0)", "(" + Lo + ", " + H + ", " + (H - Lo) + ")", "(" + H + ", " + H + ", 0)"];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "Cinque lavori di durata $p = " + tupla(p) + "$ vanno divisi fra due operai, ogni lavoro intero a uno solo. Si confrontano tre modelli: min-max ($\\min z$, $z \\ge \\ell_k$), max-min ($\\max u$, $u \\le \\ell_k$) e differenza ($\\min z - u$). Quali sono i tre valori ottimi, nell'ordine?",
        "Five jobs of duration $p = " + tupla(p) + "$ are split between two workers, each job wholly to one of them. Three models are compared: min-max ($\\min z$, $z \\ge \\ell_k$), max-min ($\\max u$, $u \\le \\ell_k$) and range ($\\min z - u$). What are the three optimal values, in order?");
      var spieg = T(l,
        "Il totale è $" + S + "$, dispari: la ripartizione migliore è $(" + H + ", " + Lo + ")$, e con due operai i tre modelli la scelgono tutti. I valori sono però diversi, $" + H + "$, $" + Lo + "$ e $" + (H - Lo) +
        "$: descrivono la stessa soluzione e non si confrontano. $" + frTex(fr(S, 2)) + "$ è il rilassamento.",
        "The total is $" + S + "$, odd: the best split is $(" + H + ", " + Lo + ")$, and with two workers all three models choose it. Their values differ, though, $" + H + "$, $" + Lo + "$ and $" + (H - Lo) +
        "$: they describe the same solution and are not comparable. $" + frTex(fr(S, 2)) + "$ is the relaxation.");
      return { testo: testo, opzioni: opz.map(math), corretta: 0, spiegazione: spieg, _v: { p: p } };
    }
  });

  // ================================================================ (complessa) 6.2 costo fisso: ottimo e rilassamento
  function fcSolve(f, c, C, D, aperti) {
    var idx = aperti.slice().sort(function (a, b) { return c[a] - c[b] || a - b; });
    var rest = D, cost = 0;
    aperti.forEach(function (j) { cost += f[j]; });
    idx.forEach(function (j) { var q = Math.min(C[j], rest); cost += c[j] * q; rest -= q; });
    return rest > 0 ? null : cost;
  }
  G.push({
    id: "mip-g-costo-fisso-ottimo", livello: "complessa", capitolo: "6-legami",
    link: L("legami-02/#la-forza-del-rilassamento", "links-02/#the-strength-of-the-relaxation"),
    genera: function (rng, l) {
      var f, c, C, D, opt, lp, opz;
      for (var tent = 0; tent < 400; tent++) {
        f = []; c = []; C = [];
        for (var j = 0; j < 3; j++) { f.push(ri(rng, 6, 20)); c.push(ri(rng, 1, 5)); C.push(ri(rng, 4, 9)); }
        D = ri(rng, Math.max(C[0], C[1], C[2]) + 1, sum(C) - 1);
        opt = 1e9; var optVar = 1e9;
        for (var mask = 1; mask < 8; mask++) {
          var ap = []; for (j = 0; j < 3; j++) if (mask >> j & 1) ap.push(j);
          var v = fcSolve(f, c, C, D, ap);
          if (v !== null && v < opt) opt = v;
        }
        // rilassamento con coefficiente C_j: costo unitario effettivo c_j + f_j / C_j
        var eff = [0, 1, 2].sort(function (a, b) { return (c[a] + f[a] / C[a]) - (c[b] + f[b] / C[b]) || a - b; });
        lp = fr(0, 1); var rest = D;
        eff.forEach(function (jj) { var q = Math.min(C[jj], rest); rest -= q; lp = frAdd(lp, frMul(fr(c[jj] * C[jj] + f[jj], C[jj]), fr(q, 1))); });
        var tutti = fcSolve(f, c, C, D, [0, 1, 2]);
        var soloVar = fcSolve([0, 0, 0], c, C, D, [0, 1, 2]);
        var d = [];
        [frTex(lp), String(tutti), String(soloVar), String(opt + 1)].forEach(function (s) { if (s !== String(opt) && d.indexOf(s) < 0 && d.length < 3) d.push(s); });
        if (d.length === 3 && !(lp.d === 1 && lp.n === opt)) { opz = [String(opt)].concat(d); break; }
      }
      var testo = T(l,
        "Tre impianti: costi fissi $f = " + tupla(f) + "$, costi unitari $c = " + tupla(c) + "$, capacità $C = " + tupla(C) + "$; la domanda $D = " + D +
        "$ va soddisfatta. Il modello è $\\min \\sum_j (f_j y_j + c_j q_j)$ con $\\sum_j q_j = D$, $q_j \\le C_j y_j$, $q_j \\ge 0$, $y_j \\in \\{0,1\\}$. Quanto vale $\\zmilp$?",
        "Three plants: fixed costs $f = " + tupla(f) + "$, unit costs $c = " + tupla(c) + "$, capacities $C = " + tupla(C) + "$; the demand $D = " + D +
        "$ must be met. The model is $\\min \\sum_j (f_j y_j + c_j q_j)$ subject to $\\sum_j q_j = D$, $q_j \\le C_j y_j$, $q_j \\ge 0$, $y_j \\in \\{0,1\\}$. What is $\\zmilp$?");
      var spieg = T(l,
        "Per ogni insieme di impianti aperti con capacità sufficiente si riempiono prima i più economici per unità e si sommano i costi fissi: il migliore vale $" + opt +
        "$. Il valore frazionario $" + frTex(lp) + "$ è $\\zlpp$, dove ogni impianto costa $c_j + f_j/C_j$ per unità.",
        "For every set of open plants with enough capacity, fill the cheapest per unit first and add the fixed costs: the best is $" + opt +
        "$. The fractional value $" + frTex(lp) + "$ is $\\zlpp$, where every plant costs $c_j + f_j/C_j$ per unit.");
      return { testo: testo, opzioni: opz.map(math), corretta: 0, spiegazione: spieg, _v: { f: f, c: c, C: C, D: D } };
    }
  });

  // ================================================================ (complessa) 5 progetti con vincoli logici
  G.push({
    id: "mip-g-progetti-logici", livello: "complessa", capitolo: "5-logica",
    link: L("modellazione-5/#i-vincoli-logici-dentro-un-modello-di-ottimizzazione", "modelling-5/#logical-constraints-inside-an-optimisation-model"),
    genera: function (rng, l) {
      var n = 6, r, c, b, imp, opt, optNo, optSplit, opz;
      function ok(x, imps, split) {
        for (var q = 0; q < imps.length; q++) {
          var I = imps[q], A = x[I.a], B = x[I.b], Cc = x[I.c];
          if (I.t === "and") { if (split) { if (A && !Cc) return false; if (B && !Cc) return false; } else if (A && B && !Cc) return false; }
          if (I.t === "or") { if ((A || B) && !Cc) return false; }
          if (I.t === "not") { if (A && B) return false; }
        }
        return true;
      }
      function best(imps, split) {
        var bv = -1;
        for (var mask = 0; mask < 64; mask++) {
          var x = [], cost = 0, val = 0;
          for (var j = 0; j < n; j++) { x.push(mask >> j & 1); cost += x[j] * c[j]; val += x[j] * r[j]; }
          if (cost <= b && ok(x, imps, split) && val > bv) bv = val;
        }
        return bv;
      }
      for (var tent = 0; tent < 500; tent++) {
        r = []; c = [];
        for (var j = 0; j < n; j++) { r.push(ri(rng, 3, 12)); c.push(ri(rng, 1, 6)); }
        b = ri(rng, Math.floor(sum(c) / 2), sum(c) - 3);
        var tr = sample(rng, [0, 1, 2, 3, 4, 5], 3), tr2 = sample(rng, [0, 1, 2, 3, 4, 5], 2);
        imp = [{ t: "and", a: tr[0], b: tr[1], c: tr[2] }, { t: pick(rng, ["or", "not"]), a: tr2[0], b: tr2[1], c: tr[2] }];
        if (imp[1].t === "or" && (imp[1].a === tr[2] || imp[1].b === tr[2])) continue;
        opt = best(imp, false); optNo = best([], false); optSplit = best(imp, true);
        var d = [];
        [optSplit, optNo, opt - 1].forEach(function (v) { if (v !== opt && v >= 0 && d.indexOf(v) < 0) d.push(v); });
        if (d.length === 3 && optNo !== opt && optSplit !== opt) { opz = [opt].concat(d); break; }
      }
      function fmt(I) {
        var A = xv(I.a + 1), B = xv(I.b + 1), Cc = xv(I.c + 1);
        if (I.t === "and") return A + " \\land " + B + " \\Rightarrow " + Cc;
        if (I.t === "or") return A + " \\lor " + B + " \\Rightarrow " + Cc;
        return A + " \\Rightarrow \\lnot " + B;
      }
      var testo = T(l,
        "Sei progetti con ricavi $r = " + tupla(r) + "$ e costi $c = " + tupla(c) + "$, budget $b = " + b +
        "$; $x_p = 1$ se il progetto $p$ si finanzia e si massimizza il ricavo. Valgono le implicazioni $" + fmt(imp[0]) + "$ e $" + fmt(imp[1]) +
        "$, tradotte esattamente in vincoli lineari. Quanto vale $\\zmilp$?",
        "Six projects with revenues $r = " + tupla(r) + "$ and costs $c = " + tupla(c) + "$, budget $b = " + b +
        "$; $x_p = 1$ if project $p$ is funded and revenue is maximised. The implications $" + fmt(imp[0]) + "$ and $" + fmt(imp[1]) +
        "$ hold, translated exactly into linear constraints. What is $\\zmilp$?");
      var spieg = T(l,
        "Si enumerano i sottoinsiemi entro il budget che rispettano le due implicazioni (la prima diventa un vincolo solo, $x_a + x_b - x_c \\le 1$): l'ottimo vale $" + opt +
        "$. Senza vincoli logici varrebbe $" + optNo + "$; scindendo l'antecedente congiunzione si taglierebbero soluzioni ammesse.",
        "Enumerate the subsets within budget that respect the two implications (the first becomes a single constraint, $x_a + x_b - x_c \\le 1$): the optimum is $" + opt +
        "$. Without logical constraints it would be $" + optNo + "$; splitting the conjunctive antecedent would cut off allowed solutions.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { r: r, c: c, b: b, imp: imp } };
    }
  });

  // ================================================================ (complessa) 7.7 ritardo totale
  function perms(a) {
    if (a.length <= 1) return [a.slice()];
    var out = [];
    a.forEach(function (x, i) { var rest = a.slice(0, i).concat(a.slice(i + 1)); perms(rest).forEach(function (p) { out.push([x].concat(p)); }); });
    return out;
  }
  function tard(seq, t, d) {
    var tt = 0, mx = 0, k = 0;
    seq.forEach(function (j) { k += t[j]; var r = Math.max(0, k - d[j]); tt += r; mx = Math.max(mx, r); });
    return { tot: tt, max: mx };
  }
  G.push({
    id: "mip-g-ritardo-totale", livello: "complessa", capitolo: "7-scheduling",
    link: L("scheduling-7/", "scheduling-7/"),
    genera: function (rng, l) {
      var t, d, opt, opz;
      for (var tent = 0; tent < 500; tent++) {
        t = []; d = [];
        for (var j = 0; j < 4; j++) { t.push(ri(rng, 2, 7)); }
        var T0 = sum(t);
        for (j = 0; j < 4; j++) d.push(ri(rng, 2, T0 - 2));
        var all = perms([0, 1, 2, 3]);
        opt = 1e9; var optMax = 0;
        all.forEach(function (s) { var v = tard(s, t, d); if (v.tot < opt) { opt = v.tot; optMax = v.max; } });
        var edd = [0, 1, 2, 3].sort(function (a, b) { return d[a] - d[b] || a - b; });
        var spt = [0, 1, 2, 3].sort(function (a, b) { return t[a] - t[b] || a - b; });
        var vE = tard(edd, t, d).tot, vS = tard(spt, t, d).tot;
        var vN = tard([0, 1, 2, 3], t, d).tot;
        var dd = [];
        [vE, vS, vN, optMax].forEach(function (v) { if (v !== opt && dd.indexOf(v) < 0 && dd.length < 3) dd.push(v); });
        if (dd.length === 3 && opt > 0) { opz = [opt].concat(dd); break; }
      }
      var testo = T(l,
        "Una macchina, quattro lavori con durate $t = " + tupla(t) + "$ e scadenze $d = " + tupla(d) +
        "$. Il modello 7.7 minimizza $\\sum_j \\tau_j$ con $\\tau_j \\ge \\kappa_j - d_j$, $\\tau_j \\ge 0$ e i vincoli di precedenza con big-M. Quanto vale $\\zmilp$?",
        "One machine, four jobs with durations $t = " + tupla(t) + "$ and due dates $d = " + tupla(d) +
        "$. Model 7.7 minimises $\\sum_j \\tau_j$ subject to $\\tau_j \\ge \\kappa_j - d_j$, $\\tau_j \\ge 0$ and the big-M precedence constraints. What is $\\zmilp$?");
      var spieg = T(l,
        "All'ottimo $\\tau_j = \\max\\{0, \\kappa_j - d_j\\}$ e conviene una sequenza senza tempi morti: basta confrontare le $24$ sequenze. Il ritardo totale minimo è $" + opt +
        "$; l'ordine per scadenza o per durata è solo un'euristica e può dare di più.",
        "At the optimum $\\tau_j = \\max\\{0, \\kappa_j - d_j\\}$ and a sequence without idle time is best: it suffices to compare the $24$ sequences. The minimum total tardiness is $" + opt +
        "$; ordering by due date or by duration is only a heuristic and may give more.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { t: t, d: d } };
    }
  });

  // ================================================================ 9.1 lotti: il big-M dai dati
  G.push({
    id: "mip-g-lotti-bigM", livello: "facile", capitolo: "9-produzione",
    link: L("produzione-1/#modello", "production-1/#model"),
    genera: function (rng, l) {
      var d, r0, rn, t, M, opz, n;
      for (var tent = 0; tent < 300; tent++) {
        n = ri(rng, 4, 5); d = [];
        for (var i = 0; i < n; i++) d.push(5 * ri(rng, 1, 8));
        r0 = 5 * ri(rng, 1, 3); rn = 5 * ri(rng, 1, 3);
        if (r0 >= d[0]) continue;
        t = ri(rng, 1, n);
        var coda = 0; for (i = t - 1; i < n; i++) coda += d[i];
        M = t === 1 ? coda + rn - r0 : coda + rn;
        var cand = t === 1 ? [coda + rn, coda - r0, sum(d) + rn + r0, d[0] + rn]
                           : [coda + rn - r0, coda, sum(d) + rn, d[t - 1] + rn];
        var dd = [];
        cand.forEach(function (v) { if (v > 0 && v !== M && dd.indexOf(v) < 0 && dd.length < 3) dd.push(v); });
        if (dd.length === 3) { opz = [M].concat(dd); break; }
      }
      var testo = T(l,
        "Lot sizing con costo fisso di lancio (problema 9.1) su $n = " + n + "$ periodi: domande $d = " + tupla(d) + "$, scorta iniziale $r_0 = " + r0 +
        "$, scorta finale richiesta $r_n = " + rn + "$. Il lancio si modella con $x_t \\le M_t\\, y_t$. Qual è il valore di $M_{" + t + "}$ letto dai dati, il più piccolo che non taglia soluzioni ottime?",
        "Lot sizing with a fixed setup cost (problem 9.1) over $n = " + n + "$ periods: demands $d = " + tupla(d) + "$, initial stock $r_0 = " + r0 +
        "$, required final stock $r_n = " + rn + "$. The setup is modelled with $x_t \\le M_t\\, y_t$. What is the value of $M_{" + t + "}$ read from the data, the smallest that cuts off no optimal solution?");
      var spieg = T(l,
        "In un ottimo non si produce mai più della domanda che resta da coprire: $M_t = \\sum_{\\tau \\ge t} d_\\tau + r_n$; solo nel primo periodo si toglie la scorta iniziale, che è un dato. Qui $M_{" + t + "} = " + M +
        "$. Un valore più grande è valido ma indebolisce il rilassamento.",
        "At an optimum one never produces more than the demand still to be covered: $M_t = \\sum_{\\tau \\ge t} d_\\tau + r_n$; only in the first period is the initial stock, which is a datum, subtracted. Here $M_{" + t + "} = " + M +
        "$. A larger value is valid but weakens the relaxation.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { d: d, r0: r0, rn: rn, t: t } };
    }
  });

  // ================================================================ 10.9 scaffali: valore dell'obiettivo
  G.push({
    id: "mip-g-scaffali-valore", livello: "facile", capitolo: "10-misti",
    link: L("misti-9/#modello", "mixed-9/#model"),
    genera: function (rng, l) {
      var h, w, cap, ass, z, opz, n, m;
      for (var tent = 0; tent < 300; tent++) {
        n = ri(rng, 5, 6); m = ri(rng, 2, 3); h = []; w = []; ass = [];
        for (var b = 0; b < n; b++) { h.push(ri(rng, 15, 35)); w.push(ri(rng, 2, 6)); ass.push(ri(rng, 1, m)); }
        var larg = []; for (var s = 0; s < m; s++) larg.push(0);
        for (b = 0; b < n; b++) larg[ass[b] - 1] += w[b];
        if (minA(larg) === 0) continue;
        cap = maxA(larg) + ri(rng, 0, 3);
        var hmax = [], hmin = [], hsum = 0;
        for (s = 0; s < m; s++) { hmax.push(0); hmin.push(1e9); }
        for (b = 0; b < n; b++) { var k = ass[b] - 1; hmax[k] = Math.max(hmax[k], h[b]); hmin[k] = Math.min(hmin[k], h[b]); hsum += h[b]; }
        z = sum(hmax);
        opz = [z, hsum, m * maxA(h), sum(hmin)];
        if (distinct(opz)) break;
      }
      var testo = T(l,
        "Problema 10.9: libri di altezza $h = " + tupla(h) + "$ e larghezza $w = " + tupla(w) + "$, $m = " + m + "$ scaffali di larghezza $c = " + cap +
        "$; il modello minimizza $\\sum_s y_s$ con $y_s \\ge h_b\\, x_{bs}$. Gli scaffali assegnati ai libri, nell'ordine, sono $" + tupla(ass) +
        "$ (assegnamento ammissibile). Qual è il valore dell'obiettivo con le $y_s$ migliori per questo assegnamento?",
        "Problem 10.9: books of height $h = " + tupla(h) + "$ and width $w = " + tupla(w) + "$, $m = " + m + "$ shelves of width $c = " + cap +
        "$; the model minimises $\\sum_s y_s$ subject to $y_s \\ge h_b\\, x_{bs}$. The shelves assigned to the books, in order, are $" + tupla(ass) +
        "$ (a feasible assignment). What is the objective value with the best $y_s$ for this assignment?");
      var spieg = T(l,
        "I vincoli danno $y_s \\ge \\max_{b : x_{bs} = 1} h_b$ e il minimo porta ogni $y_s$ a quel massimo: l'altezza di uno scaffale è quella del libro più alto che contiene. La somma vale $" + z + "$.",
        "The constraints give $y_s \\ge \\max_{b : x_{bs} = 1} h_b$ and minimisation brings each $y_s$ down to that maximum: the height of a shelf is that of its tallest book. The sum is $" + z + "$.");
      return { testo: testo, opzioni: opz.map(function (v) { return math(String(v)); }), corretta: 0, spiegazione: spieg, _v: { h: h, w: w, c: cap, ass: ass } };
    }
  });

  // ================================================================ 1 gap dell'euristica
  function pct(a, l) {                 // frazione -> percentuale con un decimale
    var v = Math.round(1000 * a.n / a.d) / 10;
    var s = v.toFixed(1);
    if (l === "it") s = s.replace(".", "{,}");
    return s + "\\%";
  }
  G.push({
    id: "mip-g-gap-euristica", livello: "facile", capitolo: "1-modelli-mip",
    link: L("modellazione-1/#tre-gap-da-non-confondere", "modelling-1/#three-gaps-not-to-be-confused"),
    genera: function (rng, l) {
      var z, h, lb, vals, opzIt;
      for (var tent = 0; tent < 300; tent++) {
        z = ri(rng, 20, 90); h = z + ri(rng, 2, 25); lb = z - ri(rng, 2, 15);
        if (lb <= 0) continue;
        vals = [fr(h - z, z), fr(h - z, h), fr(h - lb, h), fr(z - lb, z)];
        opzIt = vals.map(function (v) { return pct(v, "it"); });
        // niente casi a metà fra due decimali (l'arrotondamento sarebbe ambiguo)
        var mezzo = vals.some(function (v) { return (2000 * v.n) % (2 * v.d) === v.d; });
        if (!mezzo && distinct(opzIt)) break;
      }
      var testo = T(l,
        "In un problema di minimo l'euristica costruttiva trova una soluzione di valore $" + h + "$, una soluzione duale costruita a mano vale $" + lb +
        "$ e il solver certifica $\\zmilp = " + z + "$. Qual è il gap dell'euristica?",
        "In a minimisation problem the constructive heuristic finds a solution of value $" + h + "$, a hand-made dual solution is worth $" + lb +
        "$ and the solver certifies $\\zmilp = " + z + "$. What is the gap of the heuristic?");
      var spieg = T(l,
        "Il gap dell'euristica si misura rispetto all'ottimo noto: $|\\ub - \\zmilp| / |\\zmilp| = " + (h - z) + "/" + z + " \\approx " + pct(vals[0], "it") +
        "$. Il rapporto $(\\ub - \\lb)/|\\ub|$ è invece il divario certificato fra i due bound, che serve quando l'ottimo non è noto.",
        "The gap of the heuristic is measured against the known optimum: $|\\ub - \\zmilp| / |\\zmilp| = " + (h - z) + "/" + z + " \\approx " + pct(vals[0], "en") +
        "$. The ratio $(\\ub - \\lb)/|\\ub|$ is instead the certified gap between the two bounds, used when the optimum is unknown.");
      return { testo: testo, opzioni: vals.map(function (v) { return math(pct(v, l)); }), corretta: 0, spiegazione: spieg, _v: { z: z, h: h, lb: lb } };
    }
  });

  G.forEach(function (g) { (QUIZ_GEN[MOD] = QUIZ_GEN[MOD] || []).push(g); });
})();
