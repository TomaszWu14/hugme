# 07. Ograniczenia, znane problemy, co dalej

## Czego aplikacja nie ma

| Brak | Skutek | Co jest zamiast |
|---|---|---|
| Prawdziwe logowanie | nie nadaje się do prawdziwych danych | konta demo bez haseł tylko przy `DEMO_MODE` / `DEMO_ACCOUNTS` ([06-decyzje](06-decyzje.md#d-09-konta-demo-bez-haseł-zamiast-logowania)) |
| Wysyłka e-maili | powiadomienia e-mail nie wychodzą | kolejka `emails` w panelu Hubu |
| Obsługa złożonego wniosku przez Hub | wniosek zawsze „czeka” w skrzynce, mimo komunikatu „Hub potwierdzi przyjęcie” | wydruk wniosku |
| Usuwanie danych przez użytkownika, retencja | brak realizacji prawa do usunięcia | opis RODO w [DANE.md](DANE.md) |
| Limit zapytań do API | publiczne `POST /api/v1/dopasuj` bez ograniczeń | – |
| PostgreSQL, wiele instancji | jeden worker | SQLite, schemat zgodny z PostgreSQL |
| Testy z użytkownikami | dostępność sprawdzona automatycznie (axe-core) i ręcznie, bez osób z niepełnosprawnościami | – |

Dane: wszystkie osoby, organizacje, innowacje i zgłoszenia są fikcyjne (plakietka PRZYKŁAD); prawdziwe są tylko
miejsca pracy i statystyki w zakładce „Praca”, każde ze źródłem.

## Znane problemy (obserwacje z analizy kodu)

Lista do decyzji, nie zadania do naprawy w tym repozytorium.

| # | Obserwacja | Gdzie | Pytanie analityka |
|---|---|---|---|
| 1 | Złożony wniosek nie ma dalszej obsługi | `app/views/kreator.py` `application`, `app/views/admin.py` `inbox` | Kto i jak potwierdza przyjęcie wniosku? |
| 2 | Status zgłoszenia bez reguł przejść; w bazie bez CHECK | `app/views/admin.py` `set_status`, `core/db.py` | Czy „zamknięte” może wrócić do „nowe”? Kto zamyka? |
| 3 | „Hub odpowiada w ciągu 3 dni roboczych” to tylko tekst | `app/views/public.py`, `app/views/komunikacja.py` | Jak mierzyć i eskalować przekroczenie? |
| 4 | Nabór po terminie dalej jest „otwarty” na liście | `app/views/kreator.py` `detail` | Zamykać automatycznie po terminie? |
| 5 | Ocena dopasowania spoza zgłoszenia pokazuje „Dziękujemy”, nic nie zapisując | `app/views/public.py` `rate_match` | – |
| 6 | Jedna ocena / jeden głos pilnowane w kodzie, bez UNIQUE w bazie | `app/views/wiedza.py`, `app/views/razem.py` | Co przy dwóch równoczesnych kliknięciach? |
| 7 | Ekspert widzi wszystkie niezatwierdzone zgłoszenia, nie tylko ze swoich obszarów | `app/views/public.py` `can_see_report` | Czy to zamierzone? |
| 8 | Telefon w programie „Jestem potrzebny” zapisywany jawnie (zgoda jest wymagana, ale bez zakresu i terminu) | `app/views/potrzebny.py` `save_volunteer` | Kto widzi telefon i jak długo go przechowujemy? |
| 9 | Obszar zgłoszenia przychodzi z formularza, nie z analizy na serwerze | `app/views/public.py` `create_report` | Czy trendy mogą zależeć od pola, które da się zmienić? |
| 10 | Para przewodników tylko w tym samym powiecie | `app/views/admin.py` `guide_pairs` | Co z sąsiednim powiatem? |
| 11 | Liczba miejsc w ofercie po cichu ograniczana do 1–20 | `app/views/potrzebny.py` `save_offer` | Komunikat czy twardy błąd? |
| 12 | Wydarzenia bez limitu miejsc | `app/views/razem.py` `toggle_signup` | – |
| 13 | Kolejka e-mail rośnie bez końca | `core/notify.py` | – |
| 14 | Bez `SECRET_KEY` restart aplikacji wylogowuje wszystkich | `app/__init__.py` `create_app` | – |
| 15 | Wartości wielokrotne jako CSV w polach tekstowych | `core/db.py` | – |
| 16 | Trafność zmierzona na 16 zdaniach testowych | `tests/test_trafnosc.py` | Jak wypadnie na prawdziwych zgłoszeniach? |

## Co dalej

Pełna roadmapa: [ROADMAPA.md](ROADMAPA.md). Najbliższe kroki, które wynikają z ograniczeń powyżej:

1. Logowanie (login.gov.pl, link e-mail), wysyłka poczty, PostgreSQL.
2. Obsługa wniosku po złożeniu i cykl życia statusu zgłoszenia (problemy 1–2).
3. Pomiar czasu odpowiedzi Hubu (cel z roadmapy: ≤ 3 dni robocze).
4. Rozbudowa słownika pojęć i ponowny pomiar trafności na prawdziwych zgłoszeniach.
5. Testy z użytkownikami: rodziny z obszaru pilotażu, seniorzy, gminy, organizacje.
