# Dostępność – WCAG 2.1 AA

Odbiorcy to także seniorzy i osoby z niepełnosprawnościami, dlatego dostępność jest założeniem projektu,
a nie poprawką na końcu.

## Wynik audytu automatycznego

`python scripts/axe_audit.py`: axe-core 4.10 (reguły WCAG 2.0/2.1 A i AA) przez Playwright, na **51 widokach**
(wszystkie ekrany i role) × **desktop 1280 px i telefon 320 px**, plus tryb wysokiego kontrastu i A+.

**128/128 widoków bez naruszeń, bez przewijania w poziomie na 320 px.** Szczegóły: [WCAG_RAPORT.md](WCAG_RAPORT.md).

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
| Ruch | brak animacji; respektujemy `prefers-reduced-motion` | 2.3.3 |
| Filmy | YouTube bez śledzenia, z tytułem iframe i opisem tekstowym | 1.2.1 (częściowo) |
| Czytelna czcionka | Atkinson Hyperlegible (projekt dla osób słabowidzących), 18 px bazowo | – |
| Tekst łatwy do czytania (ETR) | „Strona dla mnie” w module Razem z ZD: krótkie zdania, piktogramy z podpisem, wybór obrazkiem, „Przeczytaj na głos” | 3.1.5 (AAA, cel) |
| Prosty język | piszemy do mieszkańca, krótkie formularze, przykład pod każdym polem | 3.1.5 (AAA, cel) |

## Co dalej

1. **Testy z użytkownikami**: seniorzy, osoby niewidome (NVDA, VoiceOver), rodzice z obszaru pilotażowego.
2. **Ręczny przegląd czytnikiem ekranu** każdego przepływu (automaty wykrywają ok. 40% problemów).
3. **Napisy i audiodeskrypcja** dla filmów w Bibliotece, jako wymóg przy imporcie.
4. **Tekst łatwy do czytania (ETR)** dla ścieżki rodziny i strony startowej.
5. **Deklaracja dostępności** zgodna z ustawą o dostępności cyfrowej (wzór Ministerstwa) przed produkcją.
6. Tryb ciemny zgodny z `prefers-color-scheme`.
