// Przycisk „Drukuj / zapisz jako PDF” na karcie usługi (CSP 'self' – bez skryptów inline).
// Bez JS przycisk nic by nie robił, więc jest ukryty (hidden na opakowaniu) i pokazujemy go tutaj.
document.querySelectorAll('[data-druk]').forEach((b) => {
  b.closest('[hidden]')?.removeAttribute('hidden');
  b.addEventListener('click', () => window.print());
});
