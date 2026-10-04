// Tryb „Podpowiedzi” – ulepszenia w JS (bez JS chmurki „i” działają natywnie jako <details>).
// 1) Chmurki: jedna otwarta naraz, Esc zamyka i wraca fokusem do „i”, klik obok zamyka, panel nie wychodzi za ekran.
// 2) „Przewodnik po tej stronie”: kroki z <script type="application/json" id="przewodnik-dane">.
// Bez localStorage i bez atrybutu style – tylko CSSOM (zgodnie z CSP).
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function phone() { return window.matchMedia("(max-width: 37.5em)").matches; }
  function scrollToY(y) { window.scrollTo({ top: Math.max(0, y), behavior: reduce ? "auto" : "smooth" }); }

  /* ---------- Chmurki ---------- */
  function openHelps() { return document.querySelectorAll("details.help[open]"); }
  function closeHelp(d, refocus) {
    d.open = false;
    if (refocus) d.querySelector("summary").focus();
  }

  function placeHelp(d) {
    var panel = d.querySelector(".help__panel");
    panel.style.left = "";
    document.body.style.paddingBottom = "";
    if (phone()) {
      // Arkusz na dole: odsłoń „i” nad arkuszem i daj stronie miejsce na przewinięcie.
      var h = panel.offsetHeight;
      document.body.style.paddingBottom = h + "px";
      var s = d.querySelector("summary").getBoundingClientRect();
      var limit = window.innerHeight - h - 16;
      if (s.bottom > limit) scrollToY(window.scrollY + s.bottom - limit);
      return;
    }
    var r = panel.getBoundingClientRect();
    var over = r.right - (document.documentElement.clientWidth - 8);
    if (over > 0) panel.style.left = -Math.min(over, r.left - 8) + "px";
  }

  function initHelps() {
    document.addEventListener("toggle", function (e) {
      var d = e.target;
      if (!d.matches || !d.matches("details.help")) return;
      if (d.open) {
        openHelps().forEach(function (o) { if (o !== d) o.open = false; });
        var btn = d.querySelector(".help__close");
        if (btn) btn.hidden = false;
        placeHelp(d);
      } else if (!openHelps().length && !tour) {
        document.body.style.paddingBottom = "";
      }
    }, true);

    document.addEventListener("click", function (e) {
      var close = e.target.closest && e.target.closest(".help__close");
      if (close) { closeHelp(close.closest("details.help"), true); return; }
      openHelps().forEach(function (d) { if (!d.contains(e.target)) d.open = false; });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape" || tourActive()) return;
      var open = openHelps();
      if (!open.length) return;
      open.forEach(function (d) { closeHelp(d, d.contains(document.activeElement) || open.length === 1); });
    });
  }

  /* ---------- Przewodnik ---------- */
  var tour = null; // { steps, i, dlg, back, next, start, target }
  function tourActive() { return tour !== null; }

  function visible(el) { return el.getClientRects().length > 0; }
  function findTarget(key) {
    var all = document.querySelectorAll('[data-help="' + key + '"]');
    for (var i = 0; i < all.length; i++) if (visible(all[i])) return all[i];
    return null;
  }
  function availableSteps(raw) {
    return raw.map(function (s) { return { s: s, el: findTarget(s.klucz) }; })
      .filter(function (x) { return x.el; }); // krok bez elementu (np. inna rola) – pomijamy
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function buildDialog() {
    var dlg = el("div", "tour");
    dlg.setAttribute("role", "dialog");
    dlg.setAttribute("aria-modal", "false");
    dlg.setAttribute("aria-labelledby", "tour-title");
    dlg.setAttribute("aria-describedby", "tour-text");
    dlg.tabIndex = -1;
    var live = el("div");
    live.setAttribute("aria-live", "polite");
    var count = el("p", "tour__count"); count.id = "tour-count";
    var title = el("h2", "tour__title"); title.id = "tour-title";
    var text = el("p", "tour__text"); text.id = "tour-text";
    live.append(count, title, text);
    var actions = el("div", "tour__actions");
    var back = el("button", "btn btn--small btn--ghost", "Wstecz"); back.type = "button";
    var next = el("button", "btn btn--small btn--primary", "Dalej"); next.type = "button";
    var end = el("button", "btn btn--small btn--ghost tour__end", "Zakończ"); end.type = "button";
    actions.append(back, next, end);
    dlg.append(live, actions);
    back.addEventListener("click", function () { show(tour.i - 1); });
    next.addEventListener("click", function () {
      if (tour.i < tour.steps.length - 1) show(tour.i + 1); else endTour();
    });
    end.addEventListener("click", endTour);
    document.body.appendChild(dlg);
    return { dlg: dlg, count: count, title: title, text: text, back: back, next: next };
  }

  function place(noScroll) {
    var t = tour, r = t.target.getBoundingClientRect();
    var top = r.top + window.scrollY, left = r.left + window.scrollX;
    if (phone()) {
      t.ui.dlg.style.top = "";
      t.ui.dlg.style.left = "";
      document.body.style.paddingBottom = t.ui.dlg.offsetHeight + "px";
      if (!noScroll) scrollToY(top - 16);
      return;
    }
    document.body.style.paddingBottom = "";
    var w = t.ui.dlg.offsetWidth, vw = document.documentElement.clientWidth;
    // Pod elementem; przy wysokim elemencie – w połowie ekranu, żeby okienko było widać razem z jego początkiem.
    t.ui.dlg.style.top = (top + Math.min(r.height + 16, window.innerHeight * 0.45)) + "px";
    t.ui.dlg.style.left = Math.max(16, Math.min(left, window.scrollX + vw - w - 16)) + "px";
    if (!noScroll) scrollToY(top - 96);
  }

  function show(i) {
    var t = tour;
    if (t.target) t.target.classList.remove("tour-target");
    t.i = i;
    var step = t.steps[i];
    t.target = step.el;
    t.target.classList.add("tour-target");
    t.ui.count.textContent = "Krok " + (i + 1) + " z " + t.steps.length;
    t.ui.title.textContent = step.s.tytul;
    t.ui.text.textContent = step.s.tekst;
    t.ui.back.disabled = i === 0;
    t.ui.next.textContent = i === t.steps.length - 1 ? "Gotowe" : "Dalej";
    place();
    if (!t.ui.dlg.contains(document.activeElement) || document.activeElement.disabled) {
      t.ui.dlg.focus({ preventScroll: true });
    }
  }

  function startTour(raw, startBtn) {
    var steps = availableSteps(raw);
    if (!steps.length) return;
    openHelps().forEach(function (d) { d.open = false; });
    tour = { steps: steps, i: 0, target: null, start: startBtn, ui: buildDialog() };
    show(0);
    tour.ui.dlg.focus({ preventScroll: true });
  }

  function endTour() {
    if (!tour) return;
    var t = tour;
    tour = null;
    if (t.target) t.target.classList.remove("tour-target");
    t.ui.dlg.remove();
    document.body.style.paddingBottom = "";
    t.start.focus();
  }

  function initTour() {
    var data = document.getElementById("przewodnik-dane");
    var btn = document.getElementById("przewodnik-start");
    if (!data || !btn) return;
    var raw;
    try { raw = JSON.parse(data.textContent); } catch (e) { return; }
    if (!Array.isArray(raw) || !availableSteps(raw).length) return;
    btn.hidden = false;
    btn.addEventListener("click", function () { startTour(raw, btn); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && tour) { e.preventDefault(); endTour(); }
    });
    window.addEventListener("resize", function () { if (tour) place(true); }); // bez przewijania: pasek adresu na telefonie też wywołuje resize
  }

  function init() { initHelps(); initTour(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
