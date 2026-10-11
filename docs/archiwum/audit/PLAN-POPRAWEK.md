# Plan poprawek HugMe: 4.10.2026, Etap 2 do 08:00

## Status (4.10, 07:50)

**Zrobione**
- **PR #8** (https://github.com/TomaszWu14/hugme/pull/8): Etap 2, pakiety P1–P7. Wszystkie pozycje oznaczone „tak” są w kodzie.
  - Potwierdzone na produkcji: K-04, K-03, K-05, K-06, K-07, K-09, K-02, J1A-01, J1A-02, J1B-01, J1B-08, J2-02, J2-03, J2-07, J3-04, T-3.
- **PR #9** (https://github.com/TomaszWu14/hugme/pull/9): Etap 3, Podpowiedzi (przełącznik, „i” w 3 częściach, „Przewodnik po tej stronie”). axe 0 na produkcji także z otwartą chmurką.
- Wynik ważony symulacji jury: **7,17 → 7,40** (szczegóły w `JURY.md`, „Oceny końcowe”).

**Nie zrobione albo niepełne**
- **BLOKUJE:** T-1 i T-2 nie działają na produkcji, bo baza ma słowa kluczowe innowacji sprzed PR #8 (seniorka daje Przyjaciel na Ławce / Bus na Telefon, wszystko „Słabe”). Naprawa: w terminalu Coolify `python scripts/reset_demo.py --force`, potem curl `POST /api/v1/dopasuj`.
- Z planu „nie”: J3-07, K-08. Po 08:00: J1A-16, J2-10, J3-13, K-11 M, grupowanie panelu, SMTP, WZ-3/5/7/8.
- Niepełne: K-01 (brak „Poproś o kontakt”), K-10 (10 zakładek), J2-08 (pasek demo na telefonie ok. 150 px).
- Nowe z rundy końcowej, nakład S:
  - menu zalogowanych łamie się na 2 rzędy przy 1366 px;
  - arkusz chmurki na telefonie zasłania pole;
  - przewodnik w osobnym rzędzie;
  - Pośrednik z domyślnym „dzieci i młodzież”;
  - prompt asystenta (polszczyzna);
  - `docs/KOSZTY.md` „8 s” zamiast 25 s.
- Lista z plikami: `JURY.md`, „Czego nie zdążono”.

Źródło: `docs/audit/JURY.md` (ID scalone) i `docs/audit/WZORCE.md`. Wynik ważony przed: **7,17/10**.

**Zasady**
- Nie przebudowujemy architektury i nie dodajemy dużych funkcji.
- Usunąć albo schować zbędne jest lepsze niż dodać nowe.
- Każda zmiana działa bez JS i bez klucza AI. CSP zostaje `script-src 'self'`, więc tylko małe pliki w `app/static/js/`.
- Plakietki PRZYKŁAD zostają, bo uczciwość danych jest plusem u Jurora 3.

**Priorytet** = waga kryterium (%) × zysk (1–3 pkt w kryterium) / nakład (S=1, M=2). Waga: Matchmaking 10, moduł 5, Potencjał 20, Dostępność 20, UI 10, Materiały 10. Gdy znalezisko dotyczy kilku kryteriów, liczę to o najwyższej wadze.

## 1. BLOKUJE

| # | ID | Kryterium (waga) | Zysk | Nakład | Priorytet | Pakiet | Do 08:00 |
|---|---|---|---|---|---|---|---|
| 1 | K-04: menu = 7 modułów z briefu, wejście `/tester`, pilotaż na końcu, pasek 7 modułów na starcie | Dostępność / Spełnienie (20) | 3 | S | 60 | P1 + P4 (trasa `/tester`) | **tak** |
| 2 | T-1: słownik i słowa kluczowe dla języka potocznego (seniorka na wsi, depresja) | Matchmaking (10) | 3 | M | 15 | P2 | **tak** |

## 2. ODBIERA PUNKTY

Posortowane według priorytetu.

| # | ID | Kryterium (waga) | Zysk | Nakład | Priorytet | Pakiet | Do 08:00 |
|---|---|---|---|---|---|---|---|
| 3 | J2-02: stan „czekam na AI” (`czekaj.js` + `data-czekaj`) | Dostępność (20) | 2 | S | 40 | P1 (JS) + P3/P6/P7 (atrybuty) | **tak** |
| 4 | J1A-02: wyniki nad zgięciem, CTA „Zapisz zgłoszenie” u góry | Dostępność (20) | 2 | S | 40 | P3 | **tak** |
| 5 | J2-01: potwierdzenie w sekcji docelowej (`flash` kategoria `sekcja`) | Dostępność (20) | 2 | S | 40 | P4 + P1 (filtr w `base.html`) | **tak** |
| 6 | J2-08: pasek demo i nagłówek na telefonie i przy zoomie | Dostępność (20) | 1 | S | 20 | P1 | **tak** |
| 7 | J1A-10: `/konto` bez `\|lower`, karta admina pierwsza | Dostępność (20) | 1 | S | 20 | P5 | **tak** |
| 8 | J2-07: żargon z podtytułami | Dostępność (20) | 1 | S | 20 | P7 (+ P6: CUS/OPS) | **tak** |
| 9 | J2-03 (+T-7): bez „trafność %” na wierzchu, ludzkie „dlaczego” | Dostępność (20) | 1 | S | 20 | P4 | **tak** |
| 10 | J3-04: uczciwy tekst o poczcie (panel, `/admin/poczta`) | Potencjał (20) | 1 | S | 20 | P5 (slajd w Etapie 4) | **tak** |
| 11 | K-06: Pośrednik z domyślnymi według roli i `?inspiracja=<id>` | Dostępność (20) | 1 | S | 20 | P6 | **tak** |
| 12 | K-01: gość pyta w 3 kliknięciach, „Zapytaj autorów” na karcie | Dostępność (20) | 2 | M | 20 | P4 | **tak** |
| 13 | K-03: Testuj na karcie, podgląd i role dla gościa, gwiazdki jako przyciski | Dostępność (20) | 2 | M | 20 | P4 | **tak** (gwiazdki opcjonalnie) |
| 14 | T-2: stopwords, „gmina” poza współpracą | Matchmaking (10) | 2 | S | 20 | P2 | **tak** |
| 15 | T-3: komunikat o luce zamiast udawanych dopasowań | Matchmaking (10) | 2 | S | 20 | P3 | **tak** |
| 16 | J1A-01: CTA startu nad zgięciem, bez nadtytułu, ramka demo niżej | UI (10) | 2 | S | 20 | P1 | **tak** |
| 17 | T-4: jedno słowo daje wyniki | Matchmaking (10) | 1 | S | 10 | P3 | **tak** |
| 18 | T-5: skrót do `/razem/praca` przy ZD i pracy | Matchmaking (10) | 1 | S | 10 | P3 | **tak** |
| 19 | J1A-03: neutralna krawędź kart (koniec tęczy) | UI (10) | 1 | S | 10 | P1 | **tak** |
| 20 | J1B-05: odstęp między kartami w `ol.list-plain` | UI (10) | 1 | S | 10 | P1 | **tak** |
| 21 | K-10: kolejność menu panelu, pilotaż na końcu, liczniki | UI (10) | 1 | S | 10 | P5 | **tak** (bez grupowania) |
| 22 | J3-03: jedna ocena na osobę | Tester (5) | 2 | S | 10 | P4 | **tak** |
| 23 | K-02: rząd akcji na innowacji, wątek nad Filmem, „Edytuj” dla admina | Komunikacja (5) | 2 | S | 10 | P4 | **tak** |
| 24 | K-05: „Drukuj / zapisz PDF” na karcie usługi, siatka sekcji | Pośrednik (5) | 2 | S | 10 | P6 | **tak** |
| 25 | K-07: „Trendy i luki” na jednej stronie, kafel trendów | Panel (5) | 2 | S | 10 | P5 | **tak** |
| 26 | J1B-01: kafel „Nowe pomysły”, „czeka na odpowiedź”, caption | Panel (5) | 2 | S | 10 | P5 | **tak** |
| 27 | K-09: dzwonek z licznikiem widoczny na telefonie | Komunikacja (5) | 2 | S | 10 | P1 | **tak** |
| 28 | J3-07: kalibracja procentów i progu luk | Matchmaking (10) | 2 | M | 10 | – | **nie**: zmienia logikę dopasowania i luk w ostatniej chwili. Procent ukrywa J2-03, luki „połączone” załatwia J1B-10. |
| 29 | K-08: dolny pasek nawigacji na telefonie | Dostępność (20) | 1 | M | 10 | – | **nie**: nowy komponent. Najważniejszą część (licznik) daje K-09. |
| 30 | J1B-10: luki „połączone” nie są liczone jako luki | Panel (5) | 1 | S | 5 | P5 | **tak** |
| 31 | J1A-04: ocena testujących w środku karty | Tester (5) | 1 | S | 5 | P4 | **tak** |
| 32 | J1A-05: Film tylko gdy jest, notatka tylko dla admina | Zasobnik (5) | 1 | S | 5 | P4 | **tak** |
| 33 | J1B-08: „Nowa odpowiedź Hubu” na `/moje` | Komunikacja (5) | 1 | S | 5 | P3 | opcjonalnie |
| 34 | J1B-09: kanwa jako siatka kart i `<progress>` (widok, nie edycja) | Kreator (5) | 2 | M | 5 | P7 | **tak** (tylko widok w `pomysl.html`) |
| 35 | J1A-08: podmenu Razem z ZD 5 pozycji + „Więcej” | UI (10) | 1 | M | 5 | P7 | **tak**, jeśli zostanie czas |

**Kosmetyka „przy okazji”** (S, w pakietach, które i tak edytują te pliki):
- P1: J1A-12, J1A-14, J1A-18, J2-14, J2-15, J1A-15 (CSS), J1B-11 (CSS kafli).
- P3: T-6 nie trafia do P3, robi go P2 (`core/match.py`).
- P5: J1B-11, J2-13, J1B-16, K-12.
- P7: J1B-12, J1A-13, J1A-15 (tekst).

**Po 08:00 albo nigdy:**
- J1A-16 (pełne tokeny CSS): P1 robi tylko, jeśli zostanie czas.
- J2-10 (daty ISO).
- J3-13 (etykieta etapu „test”: klucz w bazie = etykieta, ryzyko).
- J3-14 (422 zostaje świadomie).
- K-11 w wersji M (formularz w hero).
- Grupowanie menu panelu w 6 grup (K-10 M).
- Wysyłka SMTP (J3-04 M).
- WZ-3 (ikony), WZ-5 (puste stany), WZ-7 (metodologia), WZ-8 w wersji ze stroną API.

**Etap 4:**
- J3-11 i slajd z J3-04: nazwy modułów z briefu w `KRYTERIA.md`, `README.md`, `HACKTRIBE.md` i na slajdach. Pliki mają niezatwierdzone zmiany użytkownika, więc edytować punktowo.
- WZ-11 (PRZED-PO, zrzuty do `docs/audit/iteracje/01-po/`).

### Wzorce z WZORCE.md: gdzie trafiły

| Wzorzec | Gdzie |
|---|---|
| 1. Siatka 7 modułów na starcie | P1 (K-04, pasek „7 modułów HubMi”) |
| 2. Nawigacja = moduły, pilotaż pod jedną pozycją | P1 (K-04) |
| 3. Jedna rodzina ikon | po 08:00 |
| 4. Stan ładowania przy AI | P1 + atrybuty w P3/P6/P7 (J2-02) |
| 5. Puste stany z akcją | częściowo: T-3 (P3), reszta po 08:00 |
| 6. Tokeny | P1, jeśli zostanie czas (J1A-16) |
| 7. Strona „Jak dopasowujemy” | po 08:00 |
| 8. Czytelna dokumentacja API | P1 tylko etykieta linku (J2-15) |
| 9. Przewodnik demo krokami | Etap 3 |
| 10. Hover i wciśnięcie kart i przycisków (`prefers-reduced-motion`) | P1 (J1A-09) |
| 11. PRZED-PO i Lighthouse | Etap 4 |

## 3. Pakiety Etapu 2 (równolegle, rozłączne pliki)

| Pakiet | Pliki (wyłączny właściciel) | ID | Czas |
|---|---|---|---|
| P1 Wygląd i nawigacja | `app/static/css/hugme.css`, `app/templates/base.html`, `_macros.html`, `home.html`, `app/static/js/czekaj.js` (nowy), `tests/test_app.py`, `tests/test_demo.py` | K-04, K-09, J1A-01, J3-02, J2-02 (JS), J2-01 (filtr), J2-08, J1A-03, J1B-05, J1A-09, J1A-12, J1A-14, J1A-18, J2-14, J2-15, J1A-15 (CSS), J1B-11 (CSS) | 60 |
| P2 Trafność dopasowania | `data/slownik.py`, `data/seed_data.py`, `core/match.py`, `tests/test_trafnosc.py` | T-1, T-2, T-6 | 50 |
| P3 Ekran wyników | `app/views/public.py`, `wyniki.html`, `zgloszenie.html`, `moje.html`, `tests/test_matchmaking.py` | J1A-02, T-3, T-4, T-5, J1B-06, J2-02 (atrybut), J1B-08 (opcja) | 50 |
| P4 Innowacja: Tester i rozmowa | `app/views/wiedza.py`, `app/views/komunikacja.py`, `innowacja.html`, `_cards.html`, `biblioteka.html`, `tests/test_wiedza.py` | K-04 (trasa `/tester`), J3-03, K-03, K-01, K-02, J2-01, J1A-04, J1A-05, J2-03, T-7 | 60 |
| P5 Panel admina i konto | `app/views/admin.py`, `app/auth.py`, `app/__init__.py`, `konto.html`, `admin/panel.html`, `admin/_nav.html`, `admin/trendy.html`, `admin/luki.html`, `admin/watki.html`, `admin/poczta.html`, `admin/razem.html`, `tests/test_admin.py` | K-07, J1B-01, J1B-02, J1B-10, K-10, J1B-11, J2-13, J3-04, J1B-16, K-12, J1A-10, J2-05 | 60 |
| P6 Pośrednik | `app/views/posrednik.py`, `posrednik.html`, `karta.html`, `app/static/js/druk.js` (nowy), `tests/test_posrednik_api.py` | K-05, K-06, J1B-07, J2-07 (CUS/OPS), J2-02 (atrybut) | 45 |
| P7 Kreator i prosty język | `pomysl.html`, `pomysl_nowy.html`, `kanwa.html`, `pomysly.html`, `wniosek.html`, `obszar.html`, `razem/_razem.html`, `razem/praca.html`, `razem/pismo.html`, `tests/test_kreator.py`, `tests/test_razem.py` | J2-07, J1B-12, J1B-09, J1A-13, J1A-08, J1A-15 (tekst), J2-02 (atrybuty) | 50 |

**Kontrakty między pakietami.** Każdy jest bezpieczny, gdy druga strona nie zdąży.
1. **`/tester`**: P4 dodaje trasę (H1 „Tester innowacji”), P1 dodaje ją do menu.
2. **Flash `sekcja`**: P4 flashuje sukcesy Testera i wątku z kategorią `sekcja` i renderuje je w sekcji (`#tester`, `thread_block`). P1 w `base.html` pomija `sekcja` w globalnym pasku. Kategoria `error` zostaje globalna.
3. **`data-czekaj="Tekst…"`** na `<form>`: P1 tworzy `czekaj.js` i dołącza go w `base.html` (`defer`). Pozostali dodają tylko atrybut i statyczną linię „Odpowiedź może potrwać do 30 sekund” pod przyciskiem.
4. **`/posrednik?inspiracja=<id>`**: P6 obsługuje parametr, P4 linkuje z innowacji. Bez P6 parametr jest po prostu ignorowany.
5. **`innovation_card(i, res=none, heading='h3', ...)`**: P4 dodaje tylko parametry opcjonalne z domyślnymi wartościami. Pozostali wołają makro jak dotąd.
6. **CSS**: tylko P1 edytuje `hugme.css`. Pozostali używają istniejących klas (`btn`, `btn--primary`, `btn--ghost`, `btn--small`, `card`, `grid`, `meta`, `notice`, `badge`, `actions`, `inline-form`, `lead`, `sr-only`, `<details>`) i nie dodają atrybutów `style`.
7. **Etykieta panelu** w menu musi dalej zawierać „Panel Hubu”, bo sprawdza to `tests/test_app.py:27`. Np. „Panel Hubu (administratora)”.
8. **Testy**: każdy pakiet uruchamia swoje pliki testów, a na końcu cały zestaw `.venv/Scripts/python.exe -m pytest -q`. Błąd w cudzym pliku zgłasza, nie poprawia go.

## 4. Etap 3: „Podpowiedzi” (po Etapie 2, do 08:20)

Projekt ma już **przełączniki A+ i „Wysoki kontrast” jako preferencję serwerową bez JS**:
- `app/auth.py`: `PREF_COOKIES = {"duzy-tekst": "a11y_size", "kontrast": "a11y_contrast"}`, trasa `toggle_pref` (POST + `next`), context processor `prefs()` ustawia `pref_size` i `pref_contrast`.
- `base.html` dokłada klasy `a11y-size` i `a11y-contrast` do `<html>`, a przyciski w pasku mają `aria-pressed`.

**Przełącznik „Podpowiedzi: wł./wył.” ma użyć tego samego mechanizmu**, a nie `localStorage`:
- Nowy klucz w `PREF_COOKIES`, np. `"podpowiedzi": "a11y_hints_off"`. Ciasteczko zapisuje stan „wyłączone”, więc przy pierwszej wizycie podpowiedzi są **włączone**.
- `prefs()` zwraca `pref_hints`, `<html>` dostaje klasę `hints-off`.
- Przycisk w pasku obok A+ („? Podpowiedzi”) z `aria-pressed`.
- Działa bez JS i jest spójne z dwoma istniejącymi przełącznikami (brief: „Jeśli projekt ma już podobny mechanizm – ujednolić”).

**Ikonki „i”:**
- Makro `help(key)` w `_macros.html` renderuje `<details class="help">` z `<summary aria-label="Podpowiedź: …">i</summary>`. Otwiera się kliknięciem lub Enterem, bez JS.
- Treść w trzech częściach: do czego służy / przykład albo jak czytać / skąd dane (przykładowe? AI czy reguły?).
- Teksty w jednym pliku `data/podpowiedzi.py` albo `app/podpowiedzi.json`, klucze `ekran.element`, w szablonach `data-help`.
- `html.hints-off .help {display:none}`.
- Mały `app/static/js/help.js`: Esc i klik obok zamykają otwarte `<details class="help">`.
- Na ≤600 px treść jako panel na dole (CSS `position:fixed; bottom:0`).
- Skrypt `scripts/check_help.py` sprawdza, że każdy `data-help` ma treść, a każdy klucz jest użyty.

**„Przewodnik po tej stronie”** (WZ-9): kroki prowadzone przez serwer (`?przewodnik=N`, pasek „Krok N z 5”, Dalej / Wstecz / Zakończ, podświetlenie przez `:target` albo klasę) albo mały `tour.js`. Bez biblioteki z CDN, bo CSP `'self'`. Kroki = ścieżki z budżetu kliknięć.

Pliki Etapu 3 (`base.html`, `_macros.html`, `hugme.css`, `auth.py`) pokrywają się z P1 i P5, więc **Etap 3 rusza dopiero po zamknięciu Etapu 2**, jednym agentem.
