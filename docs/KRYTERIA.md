# Pokrycie kryteriów oceny

## Stopień spełnienia wyzwania (40%)

Matchmaking (obowiązkowy) liczy się 10%, a każdy kolejny moduł +5%. **Dostarczone: wszystkie 7 modułów.**

| Moduł | Stan | Dowód |
|---|---|---|
| Matchmaking społeczny | ✔ pełny | opis własnymi słowami → innowacje z trafnością i „dlaczego pasuje”, podobne zgłoszenia, materiały, eksperci; zapis → wątek + powiadomienie admina; „pomocne / niepomocne”; trafność top 3 = 11/11 (`tests/test_trafnosc.py`) |
| Zasobnik wiedzy | ✔ | karty 7 wyzwań, Biblioteka z 4 filtrami + wyszukiwarką, filmy (YouTube bez śledzenia), materiały, ścieżka rodziny 4 etapy |
| Trendy potrzeb | ✔ | tylko admin: obszar m/m, mapa powiat × obszar, metryka trafności |
| Kreator pomysłów | ✔ | fiszka 4 pola, Kanwa (10 pól), asystent AI/regułowy (mocne strony, pytania, kierunki, prototyp), generator wniosków tylko w naborze, szkic, złożenie, wydruk |
| Tester innowacji | ✔ | zgłoszenie do testu, ocena 1–5, usprawnienie, każde z powiadomieniem Hubu |
| Komunikacja | ✔ | wątki przy zgłoszeniu, pomyśle i innowacji (pytania do ekspertów), powiadomienia, kolejka e-mail, obserwowanie obszarów → automatyczne powiadomienia o innowacjach i naborach, skrzynka eksperta |
| Panel administratora | ✔ | skrzynka, wątki bez odpowiedzi, statusy z powiadomieniem, szybka edycja Biblioteki (działa od razu), import CSV/JSON, nabory, luki, eksport CSV |
| Pośrednik innowacji | ✔ | kontekst instytucji → karta usługi (9 sekcji), koszty bez kwot (wymuszone także dla AI) |

**Pogłębienie pilotażu – moduł „Razem z ZD”** (`/razem`): plan rodziny wg 6 etapów życia, wizyty bez danych na serwerze,
kreator praw, wzory pism, rodzic-przewodnik łączony przez Hub, opieka wytchnieniowa, Dzień Specjalistów jako sygnał
dla Hubu, przyjazne miejsca, wymiana sprzętu, wydarzenia, „Strona dla mnie” w tekście łatwym do czytania (ETR, piktogramy,
czytanie na głos). Odpowiada na cztery główne problemy rodzin: wizyty, zmęczenie, formalności, dorosłość i „co po nas”.

**Program „Jestem potrzebny”** (`/razem/jestem-potrzebny`): osoba z ZD jako dająca, nie tylko otrzymująca – misje w schronisku,
hospicjum/DPS i świetlicy, zawsze z opiekunem (rodzic, asystent albo buddy z puli Hubu); Hub dobiera pary regułami
(powiat, zainteresowania, wiek, wolne miejsca) i potwierdza misje; dzienniczek w łatwym tekście, odznaki, dyplom,
umiejętności jako most do pracy. **Praca** (`/razem/praca`): mapa Polski i Małopolski z prawdziwymi miejscami ze źródłem,
statystyki GUS/PFRON, „Poznaj ZD” dla pracodawców i instytucji.

## Potencjał wdrożeniowy (20%)

- **Prostota utrzymania**: jeden kontener, 3 zależności, brak frameworka JS, SQLite → PostgreSQL bez zmian modelu.
- **Koszt**: ok. 75 zł miesięcznie technologii z AI, a bez AI pełna funkcjonalność ([KOSZTY](KOSZTY.md)).
- **Skalowalność i elastyczność**: dowolne obszary i powiaty (konfiguracja w `core/domain.py`), słownik pojęć
  edytowalny bez programowania, import Biblioteki ROPS, API JSON dla bazy grantowej.
- **Gotowość**: Docker + Coolify, healthcheck, 181 testów automatycznych, audyt dostępności jako skrypt.
- **Ścieżka do produkcji**: login.gov.pl, RODO, DPIA opisane w [ARCHITEKTURA](ARCHITEKTURA.md) i [DANE](DANE.md).

## Dostępność i intuicyjność (20%)

- WCAG 2.1 AA: **128/128 widoków bez naruszeń axe** (desktop i 320 px, tryb kontrastu i A+) – [WCAG](WCAG.md).
- Dla seniorów: 18 px bazowo, Atkinson Hyperlegible, A+, wysoki kontrast, cele ≥ 44 px, działanie bez JS.
- Prosty język: pole „Co jest trudne? Kogo to dotyczy?” od razu na stronie startowej, z przykładem;
  krótkie formularze z przykładem pod każdym polem; komunikaty błędów słowami.

## Atrakcyjność i pomysłowość UI (10%)

- Gra słów HugMe i motyw **splotu**: logo z dwóch nici splecionych w serce, ilustracja trzech nici
  (problemy, ludzie, rozwiązania), kolor „nici” każdego obszaru na kartach.
- Ciepła paleta (krem, granat, koral) i mięta jako jednoznaczny kolor AI.
- Nieszablonowo: wyjaśnialne dopasowania z wyróżnionymi wspólnymi słowami, „luki” jako źródło tematów konkursów.
- Makiety: [docs/zrzuty](zrzuty/) (desktop i telefon).

## Jakość materiałów i MVP (10%)

- Działający MVP z danymi przykładowymi i scenariuszem demo ([README](../README.md#scenariusz-demo-5-minut)).
- Prezentacja PDF (do 10 slajdów), film do 3 minut ([SCENARIUSZ_FILMU](SCENARIUSZ_FILMU.md)).
- Dokumentacja: architektura, dane i prywatność, WCAG + raport, koszty, roadmapa, pytania do mentorów.
