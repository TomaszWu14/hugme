// Razem z ZD – ulepszenia w JS (strona działa też bez nich).
// 1) Lista wizyt TYLKO w localStorage tego urządzenia – nic nie trafia na serwer.
// 2) „Przeczytaj na głos” – synteza mowy przeglądarki (pl-PL).
(function () {
  "use strict";

  var KEY = "hugme-razem-wizyty";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function save(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list)); return true; } catch (e) { return false; }
  }
  function fmt(iso) {
    var p = iso.split("-");
    return p.length === 3 ? p[2] + "." + p[1] + "." + p[0] : iso;
  }

  function initVisits() {
    var app = document.getElementById("wizyty-app");
    if (!app) return;
    var form = document.getElementById("wizyta-form");
    var list = document.getElementById("wizyty-lista");
    var empty = document.getElementById("wizyty-puste");
    var status = document.getElementById("wizyty-status");
    var err = document.getElementById("w-blad");
    var spec = document.getElementById("w-spec");
    var when = document.getElementById("w-data");
    var where = document.getElementById("w-gdzie");
    var heading = document.getElementById("lista-h");
    heading.setAttribute("tabindex", "-1");
    app.hidden = false;

    function render() {
      var items = load().sort(function (a, b) { return a.date < b.date ? -1 : 1; });
      list.textContent = "";
      empty.hidden = items.length > 0;
      items.forEach(function (v, i) {
        var li = document.createElement("li");
        li.className = "visit";
        var text = document.createElement("span");
        text.textContent = fmt(v.date) + " – " + v.spec + (v.where ? " (" + v.where + ")" : "");
        var del = document.createElement("button");
        del.type = "button";
        del.className = "btn btn--small";
        del.textContent = "Usuń";
        del.setAttribute("aria-label", "Usuń wizytę: " + v.spec + " " + fmt(v.date));
        del.addEventListener("click", function () {
          var all = load();
          var idx = all.findIndex(function (x) { return x.id === v.id; });
          if (idx !== -1) { all.splice(idx, 1); save(all); }  // -1: usunięta już w innej karcie
          render();
          status.textContent = "Usunięto wizytę.";
          heading.focus();  // lista jest przebudowana – fokus wraca do nagłówka listy, nie na górę strony
        });
        li.appendChild(text);
        li.appendChild(del);
        list.appendChild(li);
      });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var ok = spec.value.trim() && when.value;
      err.hidden = !!ok;
      spec.setAttribute("aria-invalid", spec.value.trim() ? "false" : "true");
      when.setAttribute("aria-invalid", when.value ? "false" : "true");
      if (!ok) { (spec.value.trim() ? when : spec).focus(); return; }
      var all = load();
      all.push({ id: Date.now(), spec: spec.value.trim().slice(0, 80), date: when.value, where: where.value.trim().slice(0, 80) });
      if (!save(all)) { status.textContent = "Nie udało się zapisać – przeglądarka blokuje pamięć strony."; return; }
      form.reset();
      render();
      status.textContent = "Dodano wizytę.";
      spec.focus();
    });
    render();
  }

  function initReadAloud() {
    var btn = document.getElementById("czytaj");
    if (!btn || !("speechSynthesis" in window)) return;
    var target = document.getElementById(btn.getAttribute("aria-controls"));
    btn.hidden = false;
    btn.addEventListener("click", function () {
      if (window.speechSynthesis.speaking) { window.speechSynthesis.cancel(); return; }
      var u = new SpeechSynthesisUtterance(target.innerText);
      u.lang = "pl-PL";
      u.rate = 0.9;
      window.speechSynthesis.speak(u);
    });
  }

  initVisits();
  initReadAloud();
})();
