// La collana: nella barra in alto il nome del corso porta alla home del corso,
// «Fabio Furini» alla pagina personale (Fabio, 22/11/2026). Generato da COLLANA/collana.py: non modificare a mano.
(function () {
  function collega() {
    var span = document.querySelector(".md-header__title .md-header__topic:first-child .md-ellipsis");
    if (!span || span.querySelector("a")) return;
    var testo = span.textContent.trim();
    var k = testo.lastIndexOf(" · ");
    var logo = document.querySelector(".md-header__button.md-logo");
    var home = logo ? logo.getAttribute("href") : null;   // su telefono il logo è nascosto ma resta nella pagina
    if (!home) {
      try { home = JSON.parse(document.getElementById("__config").textContent).base + "/"; } catch (e) { home = "."; }
    }
    home = new URL(home, window.location.href).href;   // assoluto: resta giusto anche con il caricamento istantaneo
    var it = (document.documentElement.lang || "").slice(0, 2) === "it";
    var corso = k >= 0 ? testo.slice(0, k) : testo;
    var a = document.createElement("a");
    a.href = home;
    a.className = "collana-titolo";
    a.textContent = corso;
    a.title = it ? "Prima pagina del corso" : "Course home page";
    // dopo lo scorrimento la barra mostra il titolo della pagina: anche quello porta alla home del corso
    var barra = document.querySelector(".md-header__title");
    if (barra && !barra.dataset.collana) {
      barra.dataset.collana = "1";
      barra.addEventListener("click", function (ev) {
        if (!ev.target.closest("a")) window.location.href = a.href;
      });
    }
    span.textContent = "";
    span.appendChild(a);
    if (k >= 0) {
      var b = document.createElement("a");
      b.href = it ? "https://fabiofurini.github.io/it/" : "https://fabiofurini.github.io/";
      b.className = "collana-titolo";
      b.textContent = testo.slice(k + 3);
      b.title = it ? "Pagina personale di Fabio Furini" : "Fabio Furini's home page";
      span.appendChild(document.createTextNode(" · "));
      span.appendChild(b);
    }
  }
  // riquadri dei capitoli (e delle schede): si apre il link principale toccando il riquadro intero,
  // non solo la piccola scritta «Leggi il capitolo» (Fabio, 22/11/2026: da telefono è difficile centrarla)
  function riquadri() {
    var carte = document.querySelectorAll(".md-typeset .grid.cards > ul > li, .md-typeset .grid > .card");
    for (var i = 0; i < carte.length; i++) {
      var c = carte[i];
      if (c.dataset.collana) continue;
      if (c.querySelector(".gi, .la-tool, canvas, iframe, .jxgbox")) continue;   // un'app dentro il riquadro: niente
      // il link principale: l'unico con l'icona (la freccia di «Leggi il capitolo»), o l'unico link del riquadro;
      // con più link a icona (per esempio più PDF) il riquadro resta com'è
      var conIcona = [], tutti = c.querySelectorAll("a[href]");
      for (var j = 0; j < tutti.length; j++) if (tutti[j].querySelector(".twemoji")) conIcona.push(tutti[j]);
      var link = conIcona.length === 1 ? conIcona[0] : (conIcona.length === 0 && tutti.length === 1 ? tutti[0] : null);
      if (!link) continue;
      c.dataset.collana = "1";
      c.classList.add("collana-carta");
      (function (l) {
        c.addEventListener("click", function (ev) {
          if (ev.target.closest("a, button, input, select, textarea, summary, label")) return;
          if (window.getSelection && String(window.getSelection())) return;   // chi seleziona del testo non viene portato via
          l.click();
        });
      })(link);
    }
  }
  function tutto() { collega(); riquadri(); }
  if (typeof document$ !== "undefined") document$.subscribe(tutto);
  else document.addEventListener("DOMContentLoaded", tutto);
})();
