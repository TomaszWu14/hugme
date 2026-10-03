# Dane: przykładowe, import i prywatność

## Dane przykładowe

Brief zakazuje prawdziwych danych osobowych i wrażliwych, dlatego **wszystko jest fikcyjne**
i oznaczone w interfejsie plakietką **PRZYKŁAD**:

| Zbiór | Liczba | Uwagi |
|---|---|---|
| Innowacje | 24 | 7 obszarów, 7 z obszaru pilotażowego; organizacje z dopiskiem „(PRZYKŁAD)” |
| Zgłoszenia | 42 | 18 powiatów, ostatnie 120 dni, skupiska do trendów (np. obszar pilotażowy: +10 m/m), opisy **grup**, nie osób (test pilnuje, że maskowanie nic w nich nie znajduje) |
| Materiały | 8 | poradniki, listy kontrolne, instrukcje |
| Nabory | 3 | 2 otwarte, 1 zamknięty |
| Użytkownicy | 11 | 5 kont demo i 6 ekspertów do dopasowań |
| Pomysły | 2 | z kanwą i wątkiem pytań do ekspertów |
| Razem z ZD | 24 prośby + 4 wydarzenia | 7 miejsc, 4 ogłoszenia sprzętu, 5 przewodników/rodzin, wytchnienie, 6 głosów na Dzień Specjalistów – pseudonimy, opisy bez danych dziecka |

Źródło: `data/seed_data.py`. Ładowanie: automatycznie do pustej bazy (`data/seed.py`).

## Import prawdziwej Biblioteki Innowacji ROPS

Panel → **Import** (`/admin/import`) przyjmuje CSV (separator `,` albo `;`) lub JSON, w kodowaniu UTF-8.

Rozpoznawane kolumny (polskie albo angielskie nazwy): `tytul/title`, `streszczenie/summary`, `opis/description`,
`obszar/area` (kod albo nazwa obszaru), `powiat`, `etap/stage`, `odbiorcy/audience`, `organizacja/org`,
`film/video_url` (YouTube), `slowa_kluczowe/keywords`.

Każdy wiersz przechodzi tę samą walidację co ręczna edycja. Błędne wiersze są pomijane i wypisane z powodem.
Zaimportowane innowacje nie mają plakietki „PRZYKŁAD”. Materiały ROPS dostaniemy na stoisku, a mapowanie kolumn
zajmuje jeden słownik (`IMPORT_COLUMNS` w `app/views/admin.py`).

## Ochrona prywatności

**Zasada:** problem jest ważny, dane osobowe nie są potrzebne.

1. **Maskowanie przed zapisem i przed AI** (`core/privacy.py`), dla każdego tekstu od użytkownika: zgłoszenia,
   wiadomości, pomysłu, kanwy, wniosku, karty Pośrednika i zapytania API.

   | Co | Jak rozpoznajemy | Zamiana |
   |---|---|---|
   | PESEL | 11 cyfr + suma kontrolna | `[PESEL]` (inne 11 cyfr → `[NUMER]`) |
   | Telefon | 9 cyfr, opcjonalnie +48, spacje/myślniki | `[TELEFON]` |
   | E-mail | wzorzec adresu | `[E-MAIL]` |
   | Adres | ul./al./os./pl. + nazwa + numer | `[ADRES]` |
   | Kod pocztowy | `NN-NNN` | `[KOD]` |
   | Imię | po słowach syn, córka, mąż, wnuk, „mam na imię”… | `[IMIĘ]` |
   | Nazwisko lekarza | po dr / lek. / prof. | `[NAZWISKO]` |

2. **Oryginał nie jest nigdzie zapisywany**, także w logach.
3. **Łagodny komunikat**: „Nie musisz podawać diagnozy ani danych osobowych”, a po maskowaniu informacja,
   co ukryliśmy.
4. **Widoczność**: zgłoszenie widzą autor, Hub i eksperci. Publicznie (jako „podobne zgłoszenie”) pojawia się
   dopiero po zatwierdzeniu przez Hub. Pomysły są publiczne z założenia, co mówi komunikat przy fiszce.
5. **Trendy** są zagregowane (obszar, powiat, miesiąc), bez treści i autorów, i widoczne tylko dla admina.
6. **API** zwraca tekst po maskowaniu i listę rodzajów ukrytych danych.

## RODO (docelowo)

- **Administrator**: Regionalny Ośrodek Polityki Społecznej w Krakowie.
- **Podstawa**: art. 6 ust. 1 lit. e RODO (zadanie publiczne); dane szczególnych kategorii nie są zbierane, bo
  maskowanie i komunikaty zniechęcają do ich podawania.
- **Retencja**: zgłoszenia i wątki 24 miesiące od zamknięcia sprawy, potem anonimizacja (zostają agregaty do trendów).
  Kolejka e-mail: 90 dni.
- **Podmiot przetwarzający AI**: Anthropic (umowa powierzenia; wariant bez AI dostępny jednym przełącznikiem –
  brak klucza).
- **Prawa osób**: dostęp, sprostowanie i usunięcie przez koordynatora Hubu; docelowo przycisk „usuń moje dane”.
- **DPIA** przed produkcją: ryzyko wpisania danych o zdrowiu, łagodzone maskowaniem i moderacją.

## Moduł „Razem z ZD” – zasady danych

- **Wizyty u specjalistów** zapisują się tylko w przeglądarce (localStorage) – na serwer nie trafia nic o zdrowiu.
- **Etap życia** (np. „przedszkole”) w ciasteczku zamiast daty urodzenia; brak danych dziecka.
- **Pisma** wypełniane formularzem POST i drukowane – niczego nie zapisujemy; do AI trafia tylko zamaskowane uzasadnienie.
- **Prośby** (przewodnik, wytchnienie, miejsca, sprzęt) pod pseudonimem, maskowane; publiczne dopiero po zatwierdzeniu przez Hub;
  kontakt między rodzinami wyłącznie przez koordynatora.

## Ograniczenia maskowania

Wyrażenia regularne nie złapią wszystkiego, np. imienia bez słowa-kluczy („Kasia ma 8 lat”) albo nazwy rzadkiej
choroby. Dlatego zgłoszenia są publikowane dopiero po moderacji, a w roadmapie jest model NER dla języka polskiego.
