# Architektura

## Zasada: najprościej, jak się da utrzymać

HugMe to jedna aplikacja Flask renderowana po stronie serwera (Jinja). Nie ma frameworka JS ani osobnego
frontendu. Strona działa bez JavaScriptu, więc działa też na starszych telefonach i z czytnikami ekranu.
Utrzymanie sprowadza się do jednego kontenera i jednego pliku bazy (docelowo PostgreSQL).

```
przeglądarka ──HTTP──► gunicorn ─► Flask (app/)
                                     │  widoki: public, wiedza, kreator, komunikacja, admin, posrednik, api
                                     ▼
                                   core/
                                     ├─ privacy.py  maskowanie danych osobowych (przed DB i AI)
                                     ├─ match.py    BM25 + stemming + słownik pojęć + wyjaśnienia
                                     ├─ catalog.py  wyszukiwanie: innowacje, zgłoszenia, materiały, eksperci
                                     ├─ ai.py       opcjonalny Claude (Haiku), timeout 8 s, brak ponowień
                                     ├─ notify.py   powiadomienia + kolejka e-mail + obserwujący
                                     ├─ db.py       SQLite, schemat zgodny z PostgreSQL
                                     └─ domain.py   obszary, powiaty, role, statusy
                                   data/
                                     ├─ seed.py, seed_data.py  dane przykładowe (fikcyjne)
                                     └─ slownik.py  słownik pojęć – edytowalny bez programowania
```

## Przepływ matchmakingu

1. Mieszkaniec wpisuje opis. `privacy.mask()` ukrywa dane osobowe, a oryginał nie jest nigdzie zapisywany.
2. `catalog.analyze()` wykrywa obszar i tematy ze słownika. Gdy jest klucz AI, Claude dodaje streszczenie
   i słowa kluczowe, które **rozszerzają zapytanie**. Ranking zawsze liczy BM25.
3. `match.Index` liczy wynik: `0,5 · BM25/(BM25+8) + 0,5 · pokrycie słów`. Tematy (np. „zdrowie”) wzmacniają
   BM25, ale nie liczą się do pokrycia, więc same wspólne tematy nie dają „dobrego” dopasowania.
4. Wynik zawiera etykietę słowną („Bardzo pasuje”, „Pasuje”, „Może pasować”), procent oraz wspólne słowa i tematy.
5. Zapisane zgłoszenie dostaje wątek z Hubem, a admin powiadomienie i e-mail w kolejce. Autor ocenia
   dopasowania „pomocne / niepomocne”, co daje metrykę trafności w panelu.
6. **Luka** to najlepszy wynik < 0,35 albo same oceny „niepomocne”, albo status nadany przez Hub. Luki to
   kandydaci na nowe konkursy.

Indeks jest budowany przy każdym zapytaniu z aktualnej bazy. Dzięki temu edycja Biblioteki w panelu działa
**od razu, bez przebudowy**. Przy 24 innowacjach to ułamki milisekund; przy kilku tysiącach warto dodać cache
unieważniany przy edycji (miejsce oznaczone w kodzie).

## AI: tylko wzbogacenie

| Funkcja | Bez AI (zawsze działa) | Z AI (oznaczone miętową ramką) |
|---|---|---|
| Analiza opisu | tematy ze słownika, obszar | streszczenie i dodatkowe słowa do wyszukiwania |
| Asystent pomysłu | mocne strony z kanwy, pytania o puste pola, podobne innowacje | mocne strony, pytania, nieoczywiste kierunki, szkic prototypu |
| Generator wniosków | wypełnienie z fiszki i kanwy | podpowiedź opisów działań i rezultatów |
| Pośrednik | szablon karty i najlepiej dopasowana innowacja | pełna karta; kwoty z odpowiedzi są usuwane |

Model ustawia `ANTHROPIC_MODEL` (domyślnie `claude-haiku-4-5`). Timeout wynosi 8 s, bez ponowień, a odpowiedzi
są cache'owane w pamięci procesu. Do AI trafia wyłącznie tekst po maskowaniu.

## Bezpieczeństwo

- **CSRF**: token w sesji i ukryte pole w każdym formularzu POST. API JSON jest bezstanowe (nie czyta sesji), więc jest wyłączone z CSRF.
- **CSP**: `script-src 'self'`, `style-src 'self'` (bez inline – kolory obszarów serwuje `/obszary.css`),
  `frame-src https://www.youtube-nocookie.com`, `frame-ancestors 'none'`.
- **Ciasteczka**: HttpOnly, SameSite=Lax, Secure za HTTPS (`COOKIE_SECURE=1`). Sesja jest czyszczona przy zmianie konta.
- **Role** sprawdzane na serwerze: dekoratory `login_required` / `role_required`, a cały blueprint `/admin` ma strażnika.
- **Walidacja** po stronie serwera (białe listy wartości, limity długości), ochrona przed open redirect,
  eksport CSV odporny na wstrzykiwanie formuł.

## Logowanie

Prototyp ma konta demo bez haseł. Docelowo:

1. **login.gov.pl (Węzeł Krajowy)** dla mieszkańców i urzędników: profil zaufany, e-dowód, bankowość.
   Integracja SAML 2.0 przez Węzeł Krajowy; z tożsamości zapisujemy tylko identyfikator pseudonimowy, bez PESEL.
2. **Jednorazowy link e-mail** dla osób bez profilu zaufanego: token ważny 15 minut, jednorazowy, haszowany w bazie.
3. Role przyznaje koordynator Hubu (NGO, gmina, ekspert). Mieszkaniec dostaje rolę domyślną.

Kod ról się nie zmienia, bo `g.user` i dekoratory są niezależne od sposobu logowania.

## Wdrożenie

Docker (Python 3.12, gunicorn, użytkownik bez uprawnień, healthcheck `/zdrowie`) na Coolify / Hetzner VPS.
Baza leży w wolumenie. Migracja na PostgreSQL: typy w schemacie są zgodne, trzeba zamienić
`INTEGER PRIMARY KEY` na `GENERATED ALWAYS AS IDENTITY`, placeholdery `?` na `%s` i funkcję `datetime('now', …)`
na `now() - interval …` (3 miejsca w panelu).

## Integracje

- `POST /api/v1/dopasuj`: `{"opis": "...", "limit": 5}` → wyniki z trafnością i wyjaśnieniem (bez AI, deterministycznie).
- `GET /api/v1/innowacje?obszar=&powiat=&etap=`: Biblioteka dla bazy grantowej ROPS.
- Import Biblioteki ROPS z CSV/JSON w panelu (`/admin/import`), z walidacją każdego wiersza.
- Kolejka e-mail (`emails`): worker co minutę wysyła wiersze z `sent_at IS NULL` przez SMTP.
