# Jak współtworzyć HugMe

## Uruchomienie lokalnie

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
flask --app app:create_app run                       # http://127.0.0.1:5000
pytest                                               # wszystkie testy
```

Baza `instance/hugme.db` tworzy się przy pierwszym starcie i ładuje dane przykładowe.
AI jest opcjonalne (`ANTHROPIC_API_KEY`, przykład w `.env.example`) — bez klucza aplikacja
używa szablonów.

## Zgłaszanie błędów i pomysłów

Załóż issue z szablonu **Zgłoszenie błędu** albo **Propozycja zmiany**. Podaj rolę konta,
adres strony i kroki do odtworzenia. Nie wklejaj danych osobowych — aplikacja dotyczy
spraw wrażliwych.

## Gałęzie i commity

- Gałąź od `main`, nazwa z numerem issue: `fix/14-ukryty-pomysl`, `feat/23-duplikaty-importu`,
  `docs/28-zmienne-srodowiskowe`.
- Commity w konwencji [Conventional Commits](https://www.conventionalcommits.org/),
  po angielsku: `fix:`, `feat:`, `docs:`, `test:`, `refactor:`, `chore:`.
  Przykład: `fix: reject messages on hidden ideas`.
- Każdy bugfix ma test regresji.

## Pull request

- Opis według szablonu: **Co się zmienia**, **Dlaczego**, **Jak sprawdzić**, `Closes #<numer>`.
- CI (`pytest`) musi być zielone.
- Zmiany w interfejsie: sprawdź obsługę z klawiatury i widok 320 px — projekt trzyma
  WCAG 2.1 AA (`python scripts/axe_audit.py`).
- Jedna sprawa = jeden PR.
