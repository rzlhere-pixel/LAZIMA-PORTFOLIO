/* Fills every <figure data-slot> from window.LAZIMA_ASSETS.
 * Loads the local private file when present; otherwise leaves the labelled
 * placeholder (rendered by CSS from data-label) in place. */
(function () {
  "use strict";
  var assets = window.LAZIMA_ASSETS || {};

  function fill(fig) {
    var id = fig.getAttribute("data-slot");
    var a = assets[id];
    if (!a) {
      fig.classList.add("is-missing");
      return;
    }
    if (a.ratio && !fig.hasAttribute("data-free")) fig.style.setProperty("--ratio", a.ratio);

    var note = document.createElement("span");
    note.className = "source-note";
    note.textContent = a.status;
    fig.appendChild(note);

    if (!a.file) {
      fig.classList.add("is-placeholder");
      return;
    }
    var img = new Image();
    img.decoding = "async";
    img.alt = a.alt;
    img.onload = function () {
      fig.classList.remove("is-placeholder");
      fig.classList.add("has-image");
      fig.insertBefore(img, fig.firstChild);
    };
    img.onerror = function () {
      fig.classList.add("is-placeholder");
    };
    fig.classList.add("is-placeholder");
    img.src = a.file;
  }

  document.querySelectorAll("figure[data-slot]").forEach(fill);

  /* Source-notes toggle (review mode) */
  var btn = document.getElementById("toggle-notes");
  if (btn) {
    btn.addEventListener("click", function () {
      var on = document.body.classList.toggle("show-notes");
      btn.setAttribute("aria-pressed", String(on));
    });
  }
  var printBtn = document.getElementById("print");
  if (printBtn) printBtn.addEventListener("click", function () { window.print(); });
})();
