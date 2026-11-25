/* Laboratorio di «Modellazione MIP / MIP Modelling»: il risolutore comune delle app «risolte all'ottimo».
 *
 * Un simplesso a due fasi (regola di Bland) per i problemi lineari nelle variabili continue, l'ottimo di un MILP
 * per enumerazione delle assegnazioni delle binarie (per ognuna, il simplesso sulle continue) e il rilassamento
 * continuo con le binarie in [0, 1] (z(LP+), come m.relax() di Gurobi). Lo usano, al momento del calcolo, le app
 * mip-lotti (gi-mip-lotti.js), mip-localizzazione (gi-mip-localizzazione.js), mip-progetti-logica
 * (gi-mip-logica.js) e mip-progetti-fondi (gi-mip-progetti.js): window.GI_MIP_D = { simplesso, milp, rilassamento }.
 */
(function () {
  "use strict";

  const EPS = 1e-9;

  // ------------------------------------------------------------ simplesso a due fasi
  /** P = {senso: "min"|"max", c, A, rel ("<=", ">=", "="), b, ub (Infinity = nessun limite)}, x >= 0.
   *  Restituisce {stato: "ottimo"|"inammissibile"|"illimitato", x, z}. */
  function simplesso(P) {
    const n = P.c.length, s = P.senso === "max" ? -1 : 1;
    const righe = P.A.map((a, i) => ({ a: a.slice(), rel: P.rel[i], b: P.b[i] }));
    if (P.ub) P.ub.forEach((u, j) => {
      if (isFinite(u)) { const a = new Array(n).fill(0); a[j] = 1; righe.push({ a, rel: "<=", b: u }); }
    });
    for (const r of righe) if (r.b < 0) {
      r.a = r.a.map((v) => -v); r.b = -r.b;
      r.rel = r.rel === "<=" ? ">=" : r.rel === ">=" ? "<=" : "=";
    }
    const m = righe.length;
    const nSl = righe.filter((r) => r.rel !== "=").length, nAr = righe.filter((r) => r.rel !== "<=").length;
    const N = n + nSl + nAr, Tb = [], base = [];
    let js = n, ja = n + nSl;
    for (const r of righe) {
      const row = new Array(N + 1).fill(0);
      r.a.forEach((v, j) => (row[j] = v));
      row[N] = r.b;
      if (r.rel === "<=") { row[js] = 1; base.push(js++); }
      else if (r.rel === ">=") { row[js++] = -1; row[ja] = 1; base.push(ja++); }
      else { row[ja] = 1; base.push(ja++); }
      Tb.push(row);
    }
    const pivot = (obj, r, j) => {
      const pr = Tb[r], pv = pr[j];
      for (let k = 0; k <= N; k++) pr[k] /= pv;
      for (let i = 0; i < m; i++) if (i !== r && Math.abs(Tb[i][j]) > 0) {
        const f = Tb[i][j];
        if (f !== 0) for (let k = 0; k <= N; k++) Tb[i][k] -= f * pr[k];
      }
      const f = obj[j];
      if (f !== 0) for (let k = 0; k <= N; k++) obj[k] -= f * pr[k];
      base[r] = j;
    };
    const esegui = (obj, ammessa) => {
      for (let it = 0; it < 5000; it++) {
        let j = -1;
        for (let k = 0; k < N; k++) if (ammessa(k) && obj[k] < -EPS) { j = k; break; }
        if (j < 0) return "ottimo";
        let r = -1, best = Infinity;
        for (let i = 0; i < m; i++) if (Tb[i][j] > EPS) {
          const q = Tb[i][N] / Tb[i][j];
          if (q < best - EPS || (Math.abs(q - best) <= EPS && base[i] < base[r])) { best = q; r = i; }
        }
        if (r < 0) return "illimitato";
        pivot(obj, r, j);
      }
      return "ottimo";
    };
    // fase 1: somma delle artificiali
    if (nAr) {
      const w = new Array(N + 1).fill(0);
      for (let k = n + nSl; k < N; k++) w[k] = 1;
      for (let i = 0; i < m; i++) if (base[i] >= n + nSl) for (let k = 0; k <= N; k++) w[k] -= Tb[i][k];
      esegui(w, () => true);
      if (-w[N] > 1e-7) return { stato: "inammissibile" };
      for (let i = 0; i < m; i++) if (base[i] >= n + nSl) {
        let j = -1;
        for (let k = 0; k < n + nSl; k++) if (Math.abs(Tb[i][k]) > 1e-7) { j = k; break; }
        if (j >= 0) pivot(w, i, j);
      }
    }
    // fase 2
    const obj = new Array(N + 1).fill(0);
    P.c.forEach((v, j) => (obj[j] = s * v));
    for (let i = 0; i < m; i++) { const f = obj[base[i]]; if (f !== 0) for (let k = 0; k <= N; k++) obj[k] -= f * Tb[i][k]; }
    const esito = esegui(obj, (k) => k < n + nSl);
    if (esito === "illimitato") return { stato: "illimitato" };
    const x = new Array(n).fill(0);
    for (let i = 0; i < m; i++) if (base[i] < n) x[base[i]] = Tb[i][N];
    return { stato: "ottimo", x, z: P.c.reduce((t, v, j) => t + v * x[j], 0) };
  }

  /** ottimo del MILP per enumerazione delle binarie `bin` (indici di variabili); il resto è continuo.
   *  piu = true: a parità di valore vince l'assegnazione con più binarie a 1 (altrimenti con meno).
   *  Restituisce anche quante assegnazioni delle binarie sono ottime (nOtt). */
  function milp(P, bin, piu) {
    const n = P.c.length, cont = n - bin.length, s = P.senso === "max" ? -1 : 1;
    let best = null, nOtt = 0;
    // a parità di valore: meno binarie a 1 (niente setup o sedi inutili) o, con piu, di più
    const pc = (x) => { let c = 0; while (x) { c += x & 1; x >>= 1; } return c; };
    const maschere = [...Array(1 << bin.length).keys()].sort((a, b) => (piu ? pc(b) - pc(a) : pc(a) - pc(b)) || a - b);
    for (const mask of maschere) {
      const v = bin.map((_, k) => (mask >> k) & 1);
      let r;
      if (!cont) {
        const x = new Array(n).fill(0);
        bin.forEach((j, k) => (x[j] = v[k]));
        const ok = P.A.every((a, i) => {
          const lhs = a.reduce((t, c, j) => t + c * x[j], 0);
          return P.rel[i] === "<=" ? lhs <= P.b[i] + EPS : P.rel[i] === ">=" ? lhs >= P.b[i] - EPS : Math.abs(lhs - P.b[i]) <= EPS;
        });
        r = ok ? { stato: "ottimo", x, z: P.c.reduce((t, c, j) => t + c * x[j], 0) } : null;
      } else {
        const A = P.A.slice(), rel = P.rel.slice(), b = P.b.slice();
        bin.forEach((j, k) => { const a = new Array(n).fill(0); a[j] = 1; A.push(a); rel.push("="); b.push(v[k]); });
        r = simplesso({ senso: P.senso, c: P.c, A, rel, b, ub: P.ub });
        if (r.stato !== "ottimo") r = null;
        else bin.forEach((j, k) => (r.x[j] = v[k]));
      }
      if (!r) continue;
      if (!best || s * r.z < s * best.z - 1e-7) { best = r; nOtt = 1; }
      else if (Math.abs(r.z - best.z) <= 1e-7) nOtt++;
    }
    return best ? Object.assign(best, { nOtt }) : { stato: "inammissibile" };
  }

  /** rilassamento continuo con le binarie in [0, 1] (z(LP+), come m.relax()) */
  function rilassamento(P, bin) {
    const ub = (P.ub || new Array(P.c.length).fill(Infinity)).slice();
    for (const j of bin) ub[j] = Math.min(ub[j], 1);
    return simplesso(Object.assign({}, P, { ub }));
  }

  window.GI_MIP_D = { simplesso, milp, rilassamento };
})();
