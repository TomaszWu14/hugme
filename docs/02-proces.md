# 02. Proces biznesowy

## Aktorzy

Mieszkanka-rodzic, organizacja pozarządowa, gmina, ekspert, koordynatorka Hubu ROPS (administrator), gość.
System: opcjonalny model AI (Claude) – wyłącznie dopisuje tekst, nie podejmuje decyzji.

## PRZED – bez aplikacji

> Poniższy diagram to **hipoteza** zbudowana z opisu problemu, nie z badań – brak danych o procesie sprzed
> aplikacji. Do potwierdzenia albo poprawy w rozmowie z Hubem (pierwszy krok pilotażu).

```mermaid
flowchart TD
    A([Mieszkaniec ma problem]) --> B{Wie, gdzie szukać?}
    B -- nie --> C[Szuka sam: internet, znajomi]
    B -- tak --> D[Kontakt z OPS albo organizacją]
    C --> E[Nie trafia na istniejącą innowację]
    D --> F{Instytucja zna rozwiązanie<br/>z innej gminy?}
    F -- nie --> E
    F -- tak --> G([Dostaje pomoc])
    E --> H([Problem zostaje bez odpowiedzi])
    H -.-> I[Hub nie widzi problemu]
    I -.-> J[Tematy naborów bez danych o potrzebach]
```

Punkty bólu: brak jednego miejsca do opisania problemu, wiedza o innowacjach rozproszona po instytucjach,
brak informacji zwrotnej do Hubu.

## PO – z aplikacją

```mermaid
flowchart TD
    A([Mieszkaniec albo gmina opisuje problem]) --> B[Maskowanie danych osobowych]
    B --> C{"Opis 15–1500 znaków?<br/>(do samego szukania wystarczy 1 słowo z katalogu)"}
    C -- nie --> A
    C -- tak --> D["Analiza: obszar i tematy ze słownika<br/>AI opcjonalnie: streszczenie, dodatkowe słowa"]
    D --> E["Dopasowanie BM25: innowacje, podobne zgłoszenia,<br/>poradniki, eksperci"]
    E --> F{"Najlepszy wynik ≥ 0,35?"}
    F -- tak --> G[Wyniki z etykietą i powodem dopasowania]
    F -- nie --> H[Komunikat: brak sprawdzonego rozwiązania]
    G --> I{Zapisać zgłoszenie?}
    H --> I
    I -- nie --> Z([Koniec: korzysta z wyników sam])
    I -- tak --> J{Zalogowany?}
    J -- nie --> K[Wybór konta – opis czeka w sesji] --> J
    J -- tak --> L["Zgłoszenie + dopasowania + wątek<br/>powiadomienie i e-mail w kolejce do Hubu"]
    L --> M["Hub: status, publikacja, odpowiedź w wątku"]
    M --> N[Autor dostaje powiadomienie i ocenia dopasowania]
    N --> O{"Luka?<br/>wynik < 0,35 / same „niepomocne” / status „luka”"}
    O -- nie --> T([Zgłoszenie połączone albo zamknięte])
    O -- tak --> P[Trendy i luki w panelu Hubu, eksport CSV]
    P --> Q[Hub otwiera nabór – powiadomienie obserwujących obszar]
    Q --> R["Kreator pomysłów: fiszka → kanwa → asystent → wniosek"]
    R --> S([Wniosek złożony – powiadomienie Hubu])
```

### Punkty decyzyjne

| Decyzja | Kto | Reguła | Kod |
|---|---|---|---|
| Czy opis wystarczy? | system | 15–1500 znaków; do szukania 1 słowo znane z katalogu | `app/views/public.py` `validate_search` |
| Czy coś pasuje? | system | najlepszy wynik ≥ 0,35 | `core/domain.py` `GAP_THRESHOLD` |
| Czy zgłoszenie jest publiczne? | Hub | pole „Opublikuj” przy zmianie statusu | `app/views/admin.py` `set_status` |
| Czy to luka? | system + Hub | wynik < 0,35 lub same „niepomocne” lub status „luka” | `app/views/admin.py` `gaps` |
| Czy nabór jest otwarty? | Hub | przełącznik; generator wniosków działa tylko w otwartym naborze przed terminem | `app/views/kreator.py` `application` |

### Wejścia i wyjścia

| Krok | Wejście | Wyjście |
|---|---|---|
| Szukanie | opis, opcjonalnie powiat | lista dopasowań z etykietą i wyjaśnieniem (szkic w sesji) |
| Zapis | szkic, konto | zgłoszenie, do 5 dopasowań w `matches`, wątek, powiadomienie Hubu |
| Decyzja Hubu | zgłoszenie | status, publikacja, powiadomienie autora |
| Ocena autora | dopasowanie | `matches.feedback` = 1 / −1 → miernik trafności |
| Analiza Hubu | wszystkie zgłoszenia | trendy, luki, CSV |

## Procesy w pilotażu „Razem z ZD”

```mermaid
flowchart TD
    subgraph R["Razem z ZD – prośby rodzin"]
        R1([Rodzic wysyła prośbę]) --> R2{Rodzaj}
        R2 -- "miejsce, sprzęt" --> R3{Hub zatwierdza?}
        R3 -- tak --> R4([Widoczne publicznie])
        R3 -- nie --> R5([Odrzucone, autor dostaje powiadomienie])
        R2 -- "szukam / oferuję przewodnika" --> R6["Propozycja pary:<br/>ten sam powiat, ten sam etap wyżej"]
        R6 --> R7([Hub łączy, obie strony dostają powiadomienie])
        R2 -- "wytchnienie, Dzień Specjalistów" --> R8([Hub zamyka po obsłużeniu])
    end
    subgraph P["Jestem potrzebny"]
        P1([Uczestnik / buddy / oferta miejsca]) --> P2{Oferta zatwierdzona?}
        P2 -- tak --> P3["Propozycje par: powiat, zainteresowania,<br/>grupa wiekowa, wolne miejsca"]
        P3 --> P4[Hub łączy – misja]
        P4 --> P5[Hub potwierdza odbyte misje]
        P5 --> P6([Dzienniczek: odznaki, umiejętności, dyplom])
        P4 --> P7[Zamknięcie pary – uczestnik wraca do puli]
    end
```

## Integracje

| Integracja | Kierunek | Format | Gdy nie odpowiada |
|---|---|---|---|
| Claude (Anthropic API) | wyjście: tekst po maskowaniu w ogranicznikach; wejście: tekst lub JSON | HTTPS, SDK `anthropic` | timeout 25 s bez ponowień, dzienny limit wywołań, odpowiedź spoza schematu odrzucona → reguły i szablon; nigdy błąd 500 |
| `POST /api/v1/dopasuj` | wejście: opis → wyjście: dopasowania | JSON | bez AI; walidacja 400 / 422 |
| `GET /api/v1/innowacje` | wyjście: Biblioteka z filtrami | JSON | nieznany filtr → 400 z listą dozwolonych wartości |
| Import Biblioteki | wejście (panel Hubu) | CSV (`,` lub `;`, UTF-8) albo JSON | raport błędów dla każdego wiersza; duplikaty tytułów pomijane |
| Eksport | wyjście | CSV `;` z BOM, ochrona przed formułami | – |
| E-mail | wyjście | wiersz w tabeli `emails` | **nie jest wysyłany** – brak workera SMTP |
| YouTube | osadzenie filmu w karcie innowacji | iframe youtube-nocookie | brak linku → brak filmu |
