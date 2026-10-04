# Dostępność – WCAG 2.1 AA

Odbiorcy to także seniorzy i osoby z niepełnosprawnościami, dlatego dostępność jest założeniem projektu,
a nie poprawką na końcu.

## Wynik audytu automatycznego

`python scripts/axe_audit.py`: axe-core 4.10 (reguły WCAG 2.0/2.1 A i AA) przez Playwright, na **67 widokach**
(wszystkie ekrany i role) × **desktop 1280 px i telefon 320 px**, plus tryb wysokiego kontrastu i A+; dodatkowo
kontrola układu (przewijanie w bok, tekst poza kartą) na wszystkich widokach na telefonie z A+.

**138/138 widoków bez naruszeń wykrywanych automatycznie, bez przewijania w poziomie na 320 px – także z A+.**
Automaty wykrywają tylko część problemów, dlatego wynik uzupełnia przegląd ręczny (klawiatura, czytnik ekranu) poniżej.
Audyt działa w CI (job `a11y`) i blokuje scalenie zmiany, która wprowadza naruszenie.
Ten sam audyt przechodzi główne ścieżki **samą klawiaturą**: pierwszy Tab to „Przejdź do treści” (fokus trafia do
treści), Tab + Enter prowadzą od pola opisu do wyników i od wyboru konta demo do panelu Hubu, a na każdym zatrzymaniu
fokus musi być widoczny (2.1.1, 2.4.1, 2.4.7). Szczegóły: [WCAG_RAPORT.md](WCAG_RAPORT.md).

Audyt znalazł i pomógł naprawić: tabele przewijane w poziomie niedostępne z klawiatury (dodane `role="region"`
i `tabindex="0"`), tekst dla czytników ekranu rozpychający stronę na telefonie, listę ról za szeroką w trybie A+.

## Co działa

| Wymaganie | Realizacja | Kryterium |
|---|---|---|
| Klawiatura | wszystko to natywne linki, przyciski i formularze; widoczny fokus (3 px + obwódka) | 2.1.1, 2.4.7 |
| Skip link | „Przejdź do treści” jako pierwszy element | 2.4.1 |
| Kontrast ≥ 4,5:1 | paleta zmierzona: tekst #1B2540 na #FBF6EE ≈ 14:1, koral #B8432F ≈ 5:1, AI #1D6B52 na #E1F4EB ≈ 5,9:1 | 1.4.3, 1.4.11 |
| A+ większy tekst | +22% rozmiaru bazowego, zapamiętane w ciasteczku, działa bez JS | 1.4.4 |
| Wysoki kontrast | czerń na bieli, grubsze obramowania | 1.4.3 |
| Etykiety i grupy | każde pole ma `<label>`; grupy radio i checkbox w `fieldset` + `legend` | 1.3.1, 3.3.2 |
| Przykład pod polem | każde pole ma podpowiedź „Np. …” powiązaną przez `aria-describedby` | 3.3.2 |
| Błędy | podsumowanie błędów z linkami do pól (`role="alert"`), `aria-invalid`, opis słowami | 3.3.1, 3.3.3, 4.1.3 |
| Cele dotykowe ≥ 44 px | przyciski, linki menu, radio/checkbox (audyt sprawdza) | 2.5.5 (AAA, spełnione) |
| 320 px, bez przewijania w bok | układ płynny, tabele w przewijanym regionie | 1.4.10 |
| Statusy nie tylko kolorem | status = symbol + słowo (● Nowe, ✔ Połączone, ! Luka); trafność = etykieta + procent; trendy ▲/▼ + „więcej o 1” | 1.4.1 |
| Ilustracja | SVG z `<title>` i `<desc>` opisującym splot | 1.1.1 |
| Nici obszarów a daltonizm | kolor + **wzór kreski** (ciągła, kreski, kropki, paski) – pary mylone w deuteranopii mają różne wzory; nazwa obszaru zawsze obok | 1.4.1 |
| Heatmapa trendów | skala sekwencyjna w granacie z legendą, progi bezwzględne (1 / 2–3 / 4–6 / 7+), liczby w każdej komórce | 1.4.1, 1.4.11 |
| Ikony | SVG w kolorze tekstu (`aria-hidden`), bez emoji; grafiki AI i ilustracji ≥ 3:1 | 1.4.11 |
| Język | `lang="pl"`, angielskie „hug me” oznaczone `lang="en"` | 3.1.1, 3.1.2 |
| Ruch | brak animacji poza krótkim (0,14 s) pojawieniem się chmurki podpowiedzi, wyłączanym przez `prefers-reduced-motion` | 2.3.3 |
| Filmy | YouTube bez śledzenia, z tytułem iframe i opisem tekstowym | 1.2.1 (częściowo) |
| Czytelna czcionka | Atkinson Hyperlegible (projekt dla osób słabowidzących), 18 px bazowo | – |
| Tekst łatwy do czytania (ETR) | „Strona dla mnie” w module Razem z ZD: krótkie zdania, piktogramy z podpisem, wybór obrazkiem, „Przeczytaj na głos” | 3.1.5 (AAA, cel) |
| Prosty język | piszemy do mieszkańca, krótkie formularze, przykład pod każdym polem | 3.1.5 (AAA, cel) |

## Tryb Podpowiedzi

Ikonka „i” przy polach, filtrach, wykresach i wskaźnikach oraz „Przewodnik po tej stronie” (4–5 kroków na 7 ekranach).
Kod: `app/templates/_podpowiedzi.html`, `app/static/css/podpowiedzi.css`, `app/static/js/podpowiedzi.js`.

| Wymaganie | Realizacja | Kryterium |
|---|---|---|
| Działa bez JS | chmurka to natywne `<details>`/`<summary>`: otwiera się Enterem lub Spacją, czytnik ogłasza „rozwinięte/zwinięte”; przełącznik „Podpowiedzi: wł./wył.” to formularz POST z ciasteczkiem, jak A+ i kontrast | 2.1.1, 4.1.2 |
| Nazwa dla czytnika | „i” jest ukryte przed czytnikiem (`aria-hidden`), a `<summary>` ma tekst „Podpowiedź:” + nazwa pola (np. „Podpowiedź: Powiat”); przełącznik ma `aria-pressed` | 1.1.1, 2.4.6, 4.1.2 |
| Struktura | trzy części jako lista definicji (`<dl>`): Do czego służy · Przykład albo Jak czytać · Skąd to się bierze | 1.3.1 |
| Klawiatura i Esc | Esc zamyka chmurkę i wraca fokusem do „i”; naraz otwarta jest jedna; klik obok zamyka; z JS jest też przycisk „Zamknij” | 2.1.2, 2.4.3 |
| Przewodnik | okno `role="dialog"` z tytułem i opisem, treść kroku w `aria-live`, fokus przechodzi do okna; Wstecz / Dalej / Zakończ, Esc kończy i oddaje fokus przyciskowi „Przewodnik po tej stronie”; kroki bez elementu na ekranie (inna rola) są pomijane; bez JS przycisk się nie pokazuje | 2.1.1, 2.4.3, 4.1.3 |
| Telefon | poniżej 600 px chmurka i przewodnik wysuwają się jako arkusz przy dolnej krawędzi (do 40% wysokości, z przewijaniem), a strona przewija się tak, żeby opisywane pole było widać nad arkuszem; panel nie wychodzi poza ekran | 1.4.10 |
| Cele dotykowe | obszar kliknięcia „i” 44 × 44 px, widoczne kółko ok. 22 px | 2.5.5 |
| Kontrast | tekst granatowy na białym (≈ 14:1), obramowanie 2 px; „i” w kolorze tekstu pomocniczego (7,6:1); w trybie wysokiego kontrastu czerń na bieli, grubsze ramki, bez cieni; podświetlenie kroku – obwódka 4–5 px | 1.4.3, 1.4.11 |
| Ruch | animacja chmurki tylko przy `prefers-reduced-motion: no-preference`; przy ograniczonym ruchu przewijanie bez płynnego efektu | 2.3.3 |
| Wybór | podpowiedzi można wyłączyć jednym przyciskiem w pasku; przy druku są ukryte | – |
| Bezpieczeństwo (CSP) | bez stylów inline i bez skryptów w treści: kroki przewodnika to dane JSON, położenie ustawia CSSOM | – |

## Co dalej

1. **Testy z użytkownikami**: seniorzy, osoby niewidome (NVDA, VoiceOver), rodzice z obszaru pilotażowego.
2. **Ręczny przegląd czytnikiem ekranu** każdego przepływu (automaty wykrywają ok. 40% problemów).
3. **Napisy i audiodeskrypcja** dla filmów w Bibliotece, jako wymóg przy imporcie.
4. **Tekst łatwy do czytania (ETR)** dla ścieżki rodziny i strony startowej.
5. **Deklaracja dostępności** zgodna z ustawą o dostępności cyfrowej (wzór Ministerstwa) przed produkcją.
6. Tryb ciemny zgodny z `prefers-color-scheme`.
