// Stan oczekiwania (np. na AI): formularz z data-czekaj="…" po wysłaniu blokuje przycisk,
// pokazuje ten tekst i ogłasza go czytnikowi ekranu. Drugie wysłanie jest blokowane. Bez JS formularz działa zwykle.
document.addEventListener('submit', function (e) {
  var form = e.target, tekst = form.getAttribute && form.getAttribute('data-czekaj');
  if (!tekst || e.defaultPrevented) return;
  if (form.hasAttribute('data-wysylam')) { e.preventDefault(); return; }
  form.setAttribute('data-wysylam', '');
  var btn = e.submitter || form.querySelector('[type=submit]');
  // disabled dopiero po zebraniu danych formularza – inaczej zginęłoby name/value przycisku
  setTimeout(function () {
    if (btn) { btn.dataset.tekst = btn.textContent; btn.textContent = tekst; btn.disabled = true; btn.setAttribute('aria-busy', 'true'); }
  }, 0);
  var st = form.nextElementSibling;
  if (!st || !st.matches('.czekaj-status')) {
    st = document.createElement('p');
    st.className = 'czekaj-status';
    st.setAttribute('role', 'status');
    st.setAttribute('aria-live', 'polite');
    form.after(st);
  }
  setTimeout(function () { st.textContent = tekst; }, 50);  // pusty region najpierw – wtedy czytnik go ogłosi
});
// Powrót „Wstecz” z pamięci przeglądarki: odblokuj formularze
window.addEventListener('pageshow', function (e) {
  if (!e.persisted) return;
  document.querySelectorAll('form[data-wysylam]').forEach(function (form) {
    form.removeAttribute('data-wysylam');
    form.querySelectorAll('[aria-busy=true]').forEach(function (b) { b.textContent = b.dataset.tekst; b.disabled = false; b.removeAttribute('aria-busy'); });
    var st = form.nextElementSibling;
    if (st && st.matches('.czekaj-status')) st.textContent = '';
  });
});
