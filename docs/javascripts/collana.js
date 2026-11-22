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
  if (typeof document$ !== "undefined") document$.subscribe(collega);
  else document.addEventListener("DOMContentLoaded", collega);
})();
