// The same shorthands as the notes preamble: without them the browser
// prints \Z instead of Z. The bodies must stay identical to those in
// notes_1/preambolo.tex, otherwise site and PDF drift apart.
window.MathJax = {
  tex: { inlineMath: [["\\(", "\\)"], ["$", "$"]],
         displayMath: [["\\[", "\\]"], ["$$", "$$"]],
         processEscapes: true,
         macros: {
           R: "\\mathbb{R}",
           Q: "\\mathbb{Q}",
           Z: "\\mathbb{Z}",
           E: "\\mathbb{E}",
           Prob: "\\mathbb{P}",
           var: "\\mathrm{VaR}",
           cvar: "\\mathrm{CVaR}",
           AND: "\\mathrel{\\texttt{ AND }}",
           OR: "\\mathrel{\\texttt{ OR }}",
           NOT: "\\mathop{\\texttt{NOT}}\\,",
           true: "\\texttt{TRUE}",
           false: "\\texttt{FALSE}",
           zmilp: "z(\\mathit{MILP})",
           zlp: "z(\\mathit{LP})",
           zlpp: "z(\\mathit{LP}^+)",
           zlppp: "z(\\mathit{LP}^{++})",
           zdual: "z(\\mathit{D}(\\mathit{LP}))",
           ub: "\\mathit{UB}",
           lb: "\\mathit{LB}"
         } },
  options: { ignoreHtmlClass: ".*|", processHtmlClass: "arithmatex" }
};
