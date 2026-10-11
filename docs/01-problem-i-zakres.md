# 01. Problem i zakres

## Problem

W Małopolsce działa wiele innowacji społecznych – usług, które rozwiązują konkretne problemy mieszkańców
(dowóz seniorów do lekarza, opieka wytchnieniowa dla rodziców, kluby sąsiedzkie). Trzy strony tego samego
procesu nie widzą się nawzajem:

- **mieszkaniec** z problemem nie wie, że w sąsiednim powiecie ktoś już go rozwiązał;
- **gmina albo organizacja** szuka rozwiązania, które istnieje gdzie indziej, i buduje je od zera;
- **Hub Innowacji Społecznych** (Regionalny Ośrodek Polityki Społecznej w Krakowie) nie widzi, gdzie
  rozwiązań brakuje – więc tematy konkursów grantowych powstają bez danych o realnych potrzebach.

Jak ten proces wyglądał przed aplikacją i ile kosztował: `<DO UZUPEŁNIENIA: opis procesu PRZED i liczby z briefu
HubMi.pl albo od ROPS – np. liczba innowacji w Bibliotece, czas odpowiedzi, liczba zgłoszeń>`.

## Cel

Skrócić drogę **problem → istniejące rozwiązanie → ludzie, którzy pomogą**, a z problemów bez rozwiązania
zrobić dla Hubu listę **luk**, czyli kandydatów na tematy kolejnych naborów.

Mierniki, które aplikacja już liczy (panel Hubu):

| Miernik | Skąd | Gdzie w kodzie |
|---|---|---|
| Odsetek dopasowań ocenionych „pomocne” | oceny autorów zgłoszeń | `app/views/admin.py` `helpful_rate` |
| Liczba luk i ich powody | najlepszy wynik < 0,35, same oceny „niepomocne”, status „luka” | `app/views/admin.py` `gaps` |
| Zgłoszenia wg obszaru: ostatnie 30 dni vs poprzednie 30 | daty zgłoszeń | `app/views/admin.py` `trend_data` |
| Czas oczekiwania wątku na odpowiedź Hubu | data ostatniej wiadomości | `app/views/admin.py` `waited` |
| Trafność wyszukiwania (top 3) na zestawie testowym | 16 opisów testowych | `tests/test_trafnosc.py` |

## Interesariusze

| Interesariusz | Rola w aplikacji | Czego potrzebuje |
|---|---|---|
| Mieszkanka / rodzic | `mieszkaniec` | opisać problem po swojemu i dostać konkretne miejsce, osobę, usługę |
| Organizacja pozarządowa | `ngo` | rozwinąć pomysł do wniosku w naborze, wystawić ofertę dla programu „Jestem potrzebny” |
| Gmina (JST) | `gmina` | znaleźć sprawdzoną usługę i dostać kartę wdrożenia |
| Ekspert | `ekspert` | odpowiadać na pytania ze swoich obszarów |
| Koordynatorka Hubu ROPS | `admin` | widzieć zgłoszenia, odpowiadać, moderować, wiedzieć, gdzie są luki |
| Gość | brak konta | przeglądać i szukać bez logowania |

Źródło wymagań: brief zadania HubMi.pl na HackYeah 2026 (7 modułów). `<DO UZUPEŁNIENIA: czy były rozmowy
z ROPS, mentorami albo rodzicami>`.

## W zakresie

| Obszar | Co dokładnie | Szczegóły |
|---|---|---|
| Matchmaking społeczny | opis problemu → dopasowane innowacje z oceną i wyjaśnieniem, podobne zgłoszenia, poradniki, eksperci; zapis zgłoszenia i wątek z Hubem | [03-user-flow](03-user-flow.md) |
| Zasobnik wiedzy i Biblioteka innowacji | karty 7 wyzwań regionu, poradniki, ścieżka rodziny, Biblioteka z filtrami | |
| Tester innowacji | zgłoszenie do testu, ocena 1–5, propozycja usprawnienia | |
| Kreator pomysłów | fiszka → kanwa (10 pól) → asystent → wniosek w otwartym naborze | |
| Pośrednik innowacji | kontekst instytucji → karta usługi (9 sekcji, koszty bez kwot) | |
| Komunikacja | wątki, powiadomienia w aplikacji, kolejka e-mail, obserwowanie obszarów | |
| Panel Hubu | skrzynka, statusy, moderacja, Biblioteka, import CSV/JSON, nabory, trendy i luki, eksport CSV, użytkownicy i role | |
| Pilotaż „Razem z ZD” | moduł dla rodzin osób z zespołem Downa: plan wg etapu życia, prawa, pisma, prośby do Hubu, wydarzenia, program „Jestem potrzebny”, mapa miejsc pracy | |
| API JSON | dopasowanie i lista innowacji dla integracji | [02-proces](02-proces.md#integracje) |

## Poza zakresem – i dlaczego

| Czego nie ma | Dlaczego | Co jest zamiast |
|---|---|---|
| Prawdziwe logowanie | prototyp z hackathonu; docelowe logowanie (login.gov.pl / link e-mail) wymaga integracji z Węzłem Krajowym | konta demo bez haseł, tylko przy `DEMO_MODE` / `DEMO_ACCOUNTS` |
| Wysyłka e-maili | wymaga SMTP i workera | kolejka `emails` widoczna w panelu Hubu |
| Decyzje podejmowane przez AI | wyjaśnialność i bezpieczeństwo (patrz [06-decyzje](06-decyzje.md)) | AI tylko dopisuje tekst; dopasowanie, status i pary liczą reguły |
| Kwoty w kartach usług | model mógłby je wymyślić | tylko rodzaje kosztów; kwoty wycinane także z odpowiedzi AI |
| Obsługa złożonego wniosku przez Hub | nie zdążono w ramach hackathonu `<DO UZUPEŁNIENIA: świadomie czy niedokończone>` | wniosek trafia do skrzynki Hubu i na wydruk |
| Usuwanie danych przez użytkownika, retencja | prototyp na danych fikcyjnych | opis RODO w [DANE.md](DANE.md) |
| PostgreSQL, wiele instancji | jedna instancja wystarcza na demo | SQLite, schemat zgodny z PostgreSQL |

Pełna lista ograniczeń i znanych problemów: [07-ograniczenia](07-ograniczenia.md).
