# Scenariusz filmu (do 3 minut)

**Format:** nagranie ekranu (1920×1080) z lektorem, MP4. **Narzędzie:** np. OBS albo Xbox Game Bar (Win+G).
**Przygotowanie:** świeża baza (usuń `instance/hugme.db`), przeglądarka 125% powiększenia, ukryte zakładki,
bez klucza AI – film pokazuje, że dopasowanie działa bez sztucznej inteligencji.

| Czas | Ekran | Co robisz | Lektor |
|---|---|---|---|
| 0:00–0:15 | Strona startowa | powolne przewinięcie: logo, ilustracja splotu | „HugMe – platforma dla HubMi.pl. Hub plus Mi, Małopolska, czyta się jak *hug me* – przytul mnie. Bo z problemem nikt nie powinien zostać sam.” |
| 0:15–0:35 | Pole „Co jest trudne?” | dopisz: „mój syn Kacper, tel. 600 123 456”, kliknij **Znajdź rozwiązania** | „Mama dziecka z zespołem Downa opisuje własnymi słowami, jak męczące są wizyty u wielu specjalistów. Nie musi znać urzędowych pojęć.” |
| 0:35–1:00 | Wyniki | pokaż komunikat o ukrytych danych, pierwszą kartę, „Dlaczego pasuje” | „Imię i telefon zostały ukryte, zanim cokolwiek trafiło do bazy. Platforma znalazła rozwiązanie z Biblioteki Innowacji – tu przykładowe: Asystenta zdrowia rodziny – i wyjaśnia, dlaczego pasuje. To dopasowanie nie potrzebuje sztucznej inteligencji – każdy wynik da się wyjaśnić. AI może je tylko wzbogacić.” |
| 1:00–1:15 | Zapis zgłoszenia | wybierz konto mieszkanki, **Zapisz**, kliknij **Pomocne** | „Jednym kliknięciem zapisuje zgłoszenie. Jej ocena to dla Hubu pomiar trafności.” |
| 1:15–1:40 | Panel Hubu | przełącz na koordynatorkę: skrzynka → zgłoszenie → status „Połączone”, odpowiedź w wątku | „Koordynatorka Hubu widzi zgłoszenie w skrzynce, łączy rodzinę z autorami rozwiązania i odpisuje. Mama dostaje powiadomienie.” |
| 1:40–1:55 | Razem z ZD | menu „Razem z ZD” → etap „Przedszkole” → plan | „Dla rodzin osób z zespołem Downa jest osobna przestrzeń: plan na każdy etap życia, wizyty zapisane tylko na telefonie i rodzic-przewodnik z tej samej okolicy.” |
| 1:55–2:25 | Jestem potrzebny | „Ja chcę pomagać” → obrazek „psy” → Wyślij; przełącz na admina: `/admin/potrzebny` → „Połącz” Tomka ze schroniskiem → „Misja odbyła się”; wróć na mieszkankę: dzienniczek z odznaką | „Osoby z zespołem Downa nie tylko dostają pomoc – też jej udzielają. W programie „Jestem potrzebny” dorosła osoba z ZD sama wybiera obrazek: psy. Hub łączy ją ze schroniskiem, zawsze z opiekunem, i potwierdza każdą misję. W dzienniczku rośnie liczba odznak, a po pięciu misjach – lista umiejętności do pracy.” |
| 2:25–2:33 | Praca | `/razem/praca` → klik „małopolskie” na mapie | „Mapa pokazuje, gdzie w Polsce naprawdę pracują osoby z zespołem Downa – każde miejsce ze źródłem.” |
| 2:33–2:41 | Pośrednik | przełącz na gminę, gotowa karta usługi | „Gmina, która chce wdrożyć podobną usługę, dostaje od Pośrednika kartę: zespół, kroki, partnerzy, finansowanie.” |
| 2:41–2:49 | Trendy i luki | admin: trendy (mapa powiat × obszar), luki | „Hub widzi, gdzie potrzeby rosną i gdzie brakuje rozwiązań. Luki stają się tematami nowych konkursów.” |
| 2:49–2:54 | Dostępność | kliknij A+ i Wysoki kontrast | „Duży tekst, wysoki kontrast, klawiatura – 136 widoków bez naruszeń wykrywanych automatycznie.” |
| 2:54–3:00 | Strona startowa | plansza: logo, hugme.twapp.pl, repozytorium | „HugMe. Twój problem nie zostaje sam.” |

**W aplikacji, poza filmem (zmiany z 4.10, po nagraniu).** Film trwa 2:59 i nie ma rezerwy czasu, więc tych zmian
w nim nie ma – pokazujemy je na żywo albo w [README](../README.md#scenariusz-demo-5-minut):
- menu z nazwami modułów z briefu (Szukaj pomocy, Zasobnik wiedzy, Biblioteka innowacji, Tester innowacji,
  Kreator pomysłów, Pośrednik innowacji, na końcu „Razem z ZD · pilotaż”), dzwonek powiadomień, na starcie kafle
  „7 modułów HubMi” i „Przewodnik dla jury: 5 kroków”; Trendy i luki na jednym ekranie;
- **tryb Podpowiedzi**: przełącznik „Podpowiedzi: wł./wył.” w pasku, ikonki „i” przy polach, filtrach i wykresach
  (do czego służy, przykład albo jak czytać, skąd to się bierze) oraz „Przewodnik po tej stronie” w 4–5 krokach;
- liczby z dnia oddania: 138 widoków bez naruszeń wykrywanych automatycznie (w filmie: 136), trafność top 3: 16/16.

**Jak powstaje film:** `python scripts/film.py <katalog>` nagrywa przeklikanie (Playwright, rzeczywiste czasy scen
w `sceny.txt`), a `python scripts/film_napisy.py <katalog> [lektor.mp3]` przyspiesza je do 2:59, wtapia napisy PL
i dokłada planszę końcową. Tekst i dokładne czasy lektora: [film/lektor.srt](film/lektor.srt) – to samo źródło dla
głosu z syntezatora i dla napisów; gotowe audio podaje się jako drugi argument.
W oddanej wersji lektor to syntezator mowy (edge-tts, głos `pl-PL-ZofiaNeural`), generowany osobno dla każdej sceny
i dopasowany do jej okna.

**Wskazówki:** mów wolno (ok. 130 słów na minutę, cały tekst ma ok. 300 słów), nie pokazuj paska adresu
z localhost, w drugiej wersji filmu dodaj napisy.
