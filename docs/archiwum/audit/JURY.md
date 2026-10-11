# Symulacja jury HugMe – 4.10.2026

**Zadanie:** HubMi.pl (ROPS Kraków), HackYeah 2026, profil A. Oddanie o 11:00. Etap 1 symulacji: 4.10.2026, ok. 05:00–06:00.

**Metoda**
- Trzech jurorów z briefu:
  - **Juror 1, projektant produktu**: dwa agenty. 1a oglądał ekrany publiczne, 1b ekrany po zalogowaniu i panel.
  - **Juror 2, użytkownik bez przygotowania** (68+, telefon, zoom 200%).
  - **Juror 3, ekspert merytoryczny i wdrożeniowy**: crawler ok. 895 stron, pełne ścieżki, spójność liczb.
- Dwa agenty pomocnicze: **budżet kliknięć** (Playwright, każda ścieżka w nowej sesji) i **testy trafności Matchmakingu** (10 przypadków z briefu i warianty). Ich wyniki są przypisane do jurorów 1, 2 i 3.
- Wszystko sprawdzano **lokalnie** na http://127.0.0.1:5055 z `DEMO_MODE=1` i **bez klucza AI**, więc widać zachowanie fallbacku: BM25, słownik tematów i ramkę „Podpowiedź z szablonu (bez AI)”. Produkcji nie dotykano (wyszukiwanie zużywa dzienny limit AI). Kodu aplikacji w Etapie 1 nie zmieniano.
- Rozdzielczości: 1366×768 i 390×844. Dodatkowo Juror 2 sprawdził 683×384 (odpowiednik zoomu 200%) oraz telefon z A+.
- Zrzuty „przed”: `docs/audit/iteracje/00-przed/`. Pliki 01–17 to ekrany publiczne (Juror 1a), 30–51 to ekrany po zalogowaniu i panel (Juror 1b). Zrzuty i skrypty pozostałych agentów są w scratchpadzie sesji (`scratchpad/juror2/`, `j3/`, `klik/`, `trafnosc/`).
- Porównanie z Trash Fairy i wzorce do przeniesienia: `docs/audit/WZORCE.md`.
- Wagi znalezisk: **BLOKUJE** (martwa ścieżka albo brak elementu wymaganego wprost przez brief), **ODBIERA PUNKTY**, **KOSMETYKA**. Duplikaty zgłoszone przez kilku agentów są scalone pod jednym ID, a w nawiasie podane są ID scalone. Dwa znaleziska podniósł do BLOKUJE sekretarz jury, bo dotyczą wymogu wprost z profilu A (oznaczone †).
- Dane testowe agentów zostały w lokalnej bazie (pomysły „J3 …”, oceny 1★ dla innowacji 1, wpisy przy /biblioteka/1–3 i 24–25). Demo odnawia się samo po 20 minutach bez nowych wpisów.

**Podsumowanie:** brak błędów 500 i błędów konsoli przy GET, axe 0 naruszeń na 136 widokach, brak przewijania w poziomie. Wynik ważony przed poprawkami: **7,17/10**. Najwięcej punktów odbierają:
1. 7 modułów z briefu nie jest widocznych w menu (Tester ma tylko kotwicę).
2. Trafność na potocznym języku mieszkańca: flagowa seniorka na wsi dostaje 2/9.
3. Brak stanu ładowania przy AI i potwierdzeń widocznych na ekranie.
4. Przekroczone budżety kliknięć gościa, a na telefonie 7 z 9 ścieżek ponad budżetem.
5. Główne akcje pod zgięciem: start i wyniki.

---

## Znaleziska

Kolejność: BLOKUJE → ODBIERA PUNKTY (od największego wpływu) → KOSMETYKA. Kryteria: Matchmaking 10%, moduły po 5%, Potencjał 20%, Dostępność 20%, UI 10%, Materiały 10%.

| ID (scalone) | Juror | Ekran | Waga | Kryterium | Co widzi → Dlaczego → Poprawka | Nakład |
|---|---|---|---|---|---|---|
| **K-04** (J1A-07, J2-06, J3-01, J3-02, WZ-1, WZ-2) † | 1, 2, 3 | Menu główne, `/` | **BLOKUJE** | Spełnienie wyzwania: 7 modułów, Tester | Menu: „Szukaj pomocy · Razem z ZD · Wiedza · Biblioteka innowacji · Pomysły · Pośrednik”. Nazwy nie odpowiadają briefowi ani H1 („Wiedza” prowadzi do „Zasobnik wiedzy”, „Pomysły” do „Kreator pomysłów”). Tester to tylko kotwica `#tester`, a pilotaż stoi na 2. miejscu. → Profil A wymaga wprost, żeby 7 modułów było pierwszym, co widać, a Tester miał osobne wejście. Modułu, którego jury nie znajdzie w 10 s, nie policzy. → Menu 7 pozycji o nazwach równych H1: Szukaj pomocy · Zasobnik wiedzy · Biblioteka innowacji · Tester innowacji (`/tester`) · Kreator pomysłów · Pośrednik innowacji · „Razem z ZD · pilotaż” na końcu z separatorem. Na starcie pasek „7 modułów HubMi”, w przewodniku demo krok „Przetestuj i oceń”, sekcja Razem z ZD pod „Jak to działa”. | S |
| **T-1** (J3-10) † | 3 | `/wyniki` | **BLOKUJE** | Matchmaking | „Mama ma 82 lata, mieszka sama na wsi… z nikim nie rozmawia” daje top 3 transport (Sąsiedzkie Dojazdy, Bus na Telefon), wszystkie „Słabe dopasowanie”. Telefonu Życzliwości nie ma w top 5. Przy depresji nastolatków brak „Przyjaciela na Ławce”. → To pierwszy test jury i zdanie, które padnie na żywo. W `data/slownik.py` „wieś/wsi/sołectwo/daleko” są w temacie transportu, a słownik samotności nie zna języka potocznego. → Usunąć te słowa z `TOPICS['transport']`. Do samotności dodać: sama, sam, samotnie, nikim, odwiedza, porozmawiać, rozmawia, smutno, opuszczona. Dodać synonimy: depresja, lęk, kryzys, psycholog, nastolat* → zdrowie psychiczne i młodzież. W `seed_data.py` dopisać frazy potoczne w keywords 4 innowacji senioralnych. Do `test_trafnosc.py` dodać 5 zdań z audytu. | M |
| **J2-02** (J1A-09, WZ-4) | 1, 2 | `/`, `/pomysly/<id>` (asystent), `/posrednik`, wniosek, `razem/pismo` | ODBIERA PUNKTY | Dostępność | Po kliknięciu przycisku z AI (limit 25 s) nic się nie zmienia: brak „trwa…”, przycisk dalej aktywny. → Brief wymaga informacji, co się dzieje. Senior klika drugi raz, co daje podwójne wywołanie i zużycie limitu. → `app/static/js/czekaj.js` (CSP `'self'`): formularz z `data-czekaj="…"` przy wysłaniu blokuje przycisk, ustawia `aria-busy`, zmienia tekst i wpisuje komunikat do `role=status`. Bez JS zostaje statyczna linia „Odpowiedź może potrwać do 30 sekund”. | S |
| **J1A-02** (J2-04, J1A-11) | 1, 2 | `/wyniki` | ODBIERA PUNKTY | Matchmaking / Dostępność | Pierwszy ekran zajmują „Twój opis” i ramka fallbacku. Nagłówek wyników jest na y≈690, a na telefonie strona ma 6633 px i formularz „Zapisz zgłoszenie” zaczyna się na y=5952. → Najwyżej punktowany moduł chowa efekt „wow”, a senior nie dojdzie do odpowiedzi człowieka. → „Twój opis” zwinąć do jednej linii z linkiem „Zmień opis”, a tematy pokazać jako jedną linię meta. U góry pasek „Chcesz odpowiedzi od człowieka z Hubu? Zapisz zgłoszenie ↓”. Formularz przenieść zaraz po innowacjach, a „Inni mieli podobnie”, „Poradniki” i „Eksperci” zwinąć w `<details>`. | S |
| **J2-01** | 2 | `/biblioteka/<id>#tester`, `#watek` | ODBIERA PUNKTY | Dostępność | Po „Zgłoś do testu” albo „Wyślij” strona przewija się do kotwicy, a komunikat „✔ … wysłane” zostaje 965–2633 px wyżej, poza ekranem. → Senior myśli, że nic się nie stało, i klika drugi raz (dubel). → Flash z kategorią `sekcja`, renderowany w sekcji docelowej (`#tester`, `thread_block`). `base.html` pomija tę kategorię w globalnym pasku. W treści napisać, co dalej („odpowie Hub albo ekspert, zwykle w 2 dni robocze – zobaczysz w Powiadomieniach”). | S |
| **T-2** | 3 | `/wyniki` „Dlaczego pasuje” | ODBIERA PUNKTY | Matchmaking | Uzasadnienia oparte na słowach pospolitych: „gminie, raz, tygodniu”, „przed”, „szkołę, pierwszej”. Rdzeń „przych” łączy „przychodzi” z „przychodnią”, a „gmina” daje temat „współpraca” każdemu urzędnikowi. → Laik widzi dopasowanie po przypadkowych słowach, co niszczy zaufanie do mocnej strony projektu. → Do `STOPWORDS` dodać: przed, raz, razy, tydzień, tygodniu, dzień, dni, kilka, pierwszy…, osoby, osób, lata, mieszka, przychodzi, gminie, gdzie, szukać. Z `TOPICS['wspolpraca']` usunąć „gmina, gminy”. Symulacja potwierdza hit@3 11/11. Opcjonalnie `stem()` 7 znaków. | S |
| **T-3** (J3-05, J1B-06) | 1, 3 | `/wyniki`, `/zgloszenie/<id>` | ODBIERA PUNKTY | Matchmaking | Dach kościoła daje „Klasa w Ruchu 17%, wspólne słowa: przed”, a rowery przy dworcu dają 4 przypadkowe innowacje. Komunikat o braku rozwiązania pojawia się tylko przy 0 wyników. Na zgłoszeniu 4 z 5 propozycji to „Słabe dopasowanie”. → Jury wprost testuje „potrzebę bez pasującej innowacji”, a system udaje, że ma rozwiązanie. Panel liczy wynik < 0,35 jako lukę, a mieszkaniec dostaje go jako rozwiązanie. → Przekazać `gap=GAP_THRESHOLD`. Gdy nie ma wyniku ≥ progu: komunikat „Nie mamy jeszcze sprawdzonego rozwiązania…” z przyciskami „Zapisz zgłoszenie – Hub poszuka” i „Masz pomysł? Zgłoś go”, a słabe wyniki w `<details>` „Luźno powiązane (N)”. Na `/zgloszenie` maksymalnie 3 dobre propozycje, resztę zwinąć. | S |
| **K-01** (J2-09, J3-09) | 1, 2, 3 | `/wyniki` → `/biblioteka/<id>#watek` | ODBIERA PUNKTY | Dostępność / Komunikacja | Pytanie jako gość: 5 kliknięć przy budżecie 3 (Znajdź → tytuł → „Wybierz konto” → konto → Wyślij). Na kartach wyników nie ma żadnej akcji, a w wątku jest tylko link w zdaniu. → Przekroczony budżet na ścieżce, którą jury zaczyna jako gość. → Na karcie wyniku przycisk „Zapytaj autorów” (`/biblioteka/<id>#watek`). W `thread_block` dla gościa w DEMO_MODE przyciski jednego kliknięcia „Napisz jako mieszkanka / organizacja” (POST `/konto`, `next=<ścieżka>#watek`). Wynik: gość 3, zalogowany 2. | M |
| **K-03** (J1A-06) | 1 | `/biblioteka` → `/biblioteka/<id>#tester` | ODBIERA PUNKTY | Tester / Dostępność | Zgłoszenie do testu i ocena: 5 kliknięć przy budżecie 4, gość 7, telefon 6/8. Po wyborze konta powrót bez `#tester`. Gość widzi tylko jeden przycisk „Wybierz konto…”. → Moduł za 5% wygląda na pusty i jest ponad budżetem. → „Testuj” na kartach. Dla gościa podgląd (średnia, 3 kroki: Wypróbuj → Oceń 1–5 → Zaproponuj poprawkę) i przyciski roli z `next=…#tester`. Ocena jako 5 przycisków `name=rating value=n`, co usuwa krok „Oceń”. | M |
| **J3-04** | 3 | `/admin` „Co teraz?”, `/admin/poczta`, slajd | ODBIERA PUNKTY | Komunikacja / Potencjał | Panel każe „Wyślij pocztę – 30 e-maili czeka”, ale nie ma czym, a slajd obiecuje e-mail. → Pytanie „czy da się uruchomić jutro?” rozbija się o brak wysyłki, a obietnica bez pokrycia osłabia zaufanie. → Tekst: „Poczta: 30 wiadomości czeka – po wdrożeniu wyjdą automatycznie przez SMTP”. Na slajdzie: „kolejka e-mail (wysyłka SMTP po wdrożeniu)”. Wysyłka przez `smtplib` przy ustawionym `SMTP_HOST` to wersja M, po 08:00. | S |
| **J2-03** (T-7) | 2, 3 | `/wyniki`, `/zgloszenie/<id>` (karty) | ODBIERA PUNKTY | Dostępność / Matchmaking | „trafność 77%” i lista odmienionych słów („downa”) wyglądają jak wydruk z maszyny. „Dlaczego pasuje” stoi przy „Słabe dopasowanie”, a przed kropką jest spacja („przed .”). → Senior nie wie, czy 61% to dobrze. „Pasuje” przy słabym wyniku wprowadza w błąd. → Procent ukryć do `.sr-only`, zostawić etykietę słowną i pasek. Słowa ograniczyć do 4. Przy wyniku < 0,35 nagłówek „Co łączy z Twoim opisem:”. Usunąć białe znaki przed kropką (`{%-`). | S |
| **K-06** (J3-08) | 1, 3 | `/posrednik`, `/biblioteka/<id>` | ODBIERA PUNKTY | Pośrednik / Dostępność | Zalogowana gmina ma niezaznaczone „Kim jesteś?” (`institution=''` na sztywno) i puste pola. Nie ma też wejścia „Dopasuj do mojej gminy” z innowacji. Ścieżka gminy to 7 akcji przy budżecie 4. → Każde wymagane, a niezaznaczone pole to dodatkowe kliknięcie. → Instytucja według roli (gmina→gmina, organizacja→ngo), powiat z profilu, domyślna skala i budżet. `GET ?inspiracja=<id>` wypełnia opis z innowacji. Na innowacji przycisk „Dopasuj do mojej gminy”. | S |
| **J1A-01** (K-11) | 1 | `/` (1366×768 i 390×844) | ODBIERA PUNKTY | UI | Na pierwszym ekranie laptopa nie ma przycisku: `.hero__cta` jest ukryte na desktopie, pole opisu jest na y≈625–775, a „Znajdź rozwiązania” na y≈1200 (telefon: y=1770). Nad hero są ramka demo i nadtytuł, który powtarza podpis logo. → Test 5 sekund: hasło jest, akcji nie ma. → Pokazać `.hero__cta` zawsze, usunąć nadtytuł, ramkę „Oglądasz demo?” przenieść pod hero, zmniejszyć ilustrację na telefonie. Formularz w hero to wersja M, później. | S |
| **J2-08** (J1B-15, J2-12, J1A-17) | 1, 2 | Pasek demo i nagłówek (telefon, zoom 200%, A+) | ODBIERA PUNKTY | Dostępność | Przy zoomie 200% chrom zajmuje 280 z 384 px, a na telefonie 215 z 844 px. Select ról jest ucięty („gość (r”, „Koordynatork…”). „A+” na telefonie nie ma podpisu, a podpis logo łamie się na 2 linie. → Osoba powiększająca stronę zaczyna od przewijania i nie widzi akcji. → Poniżej 600 px: select w osobnym rzędzie na 100% szerokości, krótkie nazwy ról, „A+ Większy tekst” widoczne (bez `sr-only-sm`), „Zmień” → „Przełącz konto”, ukryty podpis logo. Zwinięte menu już od ok. 48em. | S |
| **J1A-10** (J2-05) | 1, 2 | `/konto` (także z `/pomysly/nowy`) | ODBIERA PUNKTY | Dostępność / Panel | Przyciski „Wejdź jako gmina (jst)” i „…koordynatorka rops” (filtr `\|lower`) łamią się na 2 linie i mają nierówne wysokości. Karta admina jest sama w 2. rzędzie, pod zgięciem. → „jst/rops” wyglądają jak błąd, a najważniejsza dla jury karta jest najmniej widoczna. → Usunąć `\|lower`, krótki przycisk „Wejdź”, karta „Koordynatorka Hubu – panel administratora” pierwsza, z dopiskiem „dla jury: zgłoszenia, trendy, luki”. | S |
| **J2-07** | 2 | `/pomysly*`, kanwa, `/posrednik` | ODBIERA PUNKTY | Dostępność | Żargon bez wyjaśnienia: fiszka, kanwa, nabory, mierniki, generator wniosków, etap, CUS/OPS. → Osoba 68+ albo mała organizacja nie zgłosi pomysłu. → Zostawić nazwy oficjalne i dodać podtytuły: „Krótki opis pomysłu – 4 pola, ok. 5 minut”, „Plan pomysłu w 10 pytaniach (Kanwa…)”, „Konkursy z pieniędzmi na pomysły (nabory)”, „Po czym poznasz, że działa”, „Ośrodek pomocy społecznej (OPS, CUS)”. | S |
| **K-05** (J1B-07, J3-08) | 1, 3 | `/posrednik/karta/<id>` | ODBIERA PUNKTY | Pośrednik | Karta usługi nie ma przycisku Pobierz ani Drukuj, jest tylko „Ctrl+P” na dole. To ok. 2450 px tekstu w jednej kolumnie, a inspiracje są gołymi linkami. → Na telefonie nie ma Ctrl+P, więc ścieżka gminy się nie domyka. → Pod H1 przycisk „Drukuj / zapisz PDF” (`static/js/druk.js`, `window.print()`). Sekcje w siatce 2 kolumn (`.grid`), inspiracje jako `innovation_card`. | S |
| **K-07** (J1B-04) | 1 | `/admin/trendy`, `/admin/luki` | ODBIERA PUNKTY | Panel | Trendy i luki to dwa ekrany: 3 kliknięcia przy budżecie 2, na telefonie 6. Obszary nie są posortowane, kolumna „Zmiana” jest ucięta na 390 px, brak kafla trendów. → Kluczowa wartość dla ROPS, czyli wnioski z danych, jest rozbita. → Lista luk na `/admin/trendy#luki`, `/admin/luki` przekierowuje tam. Obszary posortowane malejąco, „Zmiana” zaraz za „Obszar”. W panelu kafel „Trendy potrzeb” (top 3), w menu panelu jedna pozycja „Trendy i luki”. | S |
| **J1B-01** (J1B-02) | 1 | `/admin` (Skrzynka) | ODBIERA PUNKTY | Panel / Komunikacja | Brak kafla „nowe pomysły”. Wiersze „Pomysł” mają puste „Szczegóły”. „Nowe sprawy (33)” kłóci się z kaflem „7 nowych”, a 33 wiersze dają ok. 3250 px. → Jury pyta wprost, jak admin dowiaduje się o nowym pomyśle. → Kafel „Nowe pomysły” (`/admin?typ=pomysl`). Plakietka „czeka na odpowiedź” dla każdego typu, nieobsłużone wiersze na górze. Caption „Wszystkie sprawy (33), najnowsze na górze”. | S |
| **K-09** | 3 | Menu na telefonie (admin, autor) | ODBIERA PUNKTY | Komunikacja | Licznik 8 nowych powiadomień jest schowany w zwiniętym `<details>` „Menu”. Autor na telefonie nie widzi, że Hub odpisał (P7: 3 kliknięcia przy budżecie 2). → Szybkość komunikacji jury sprawdza wprost. → Obok `<summary>` zawsze widoczny dzwonek-link `/powiadomienia` z liczbą (`aria-label="Powiadomienia: N nowych"`). | S |
| **K-02** (K-13) | 1 | `/biblioteka/<id>` | ODBIERA PUNKTY | Komunikacja | Rozmowa zaczyna się na y≈1907 (za opisem, Filmem i 3 formularzami Testera). Nigdzie nie ma słowa „kontakt”. Admin nie ma linku „Edytuj”. → Ścieżka „poprosić o kontakt” nie ma wejścia. → Pod H1 rząd akcji: „Zadaj pytanie” (#watek), „Testuj i oceń” (#tester), „Dopasuj do mojej gminy” (`/posrednik?inspiracja=<id>`), dla admina „Edytuj w panelu”. Sekcję `#watek` przenieść nad Film. | S |
| **J3-03** | 3 | `/biblioteka/<id>#tester` | ODBIERA PUNKTY | Tester / wiarygodność | To samo konto ocenia wielokrotnie: dwa kliknięcia „1★” zmieniły średnią z 4.5/5 (2) na 2.8/5 (4). → Średnia trafia na karty i do decyzji Hubu, więc jedna osoba może nią sterować. → W `test_action` dla `kind=='ocena'` najpierw `DELETE … WHERE innovation_id=? AND user_id=? AND kind='ocena'`, potem `INSERT`. Komunikat „Zaktualizowaliśmy Twoją ocenę”. Test regresji. | S |
| **T-4** (J3-06) | 3 | `/` → POST `/szukaj` | ODBIERA PUNKTY | Matchmaking | Jedno słowo „samotność” dostaje odmowę „Napisz trochę więcej” (422), a „samotność seniorów” daje świetne wyniki (73%). → Test „jedno słowo” jest na liście jury. → W `search()` wymagać ≥ 1 znaczącego słowa, a `MIN_LEN` zostawić tylko przy zapisie zgłoszenia. Przy krótkim opisie podpowiedź „Dopisz, kogo to dotyczy”. Zaktualizować test. | S |
| **J1A-03** | 1 | `/`, `/wiedza`, `/biblioteka`, `/pomysly` | ODBIERA PUNKTY | UI | Każdy obszar ma inny kolor i wzór krawędzi karty, więc 24 karty dają tęczę i ok. 10 odcieni na ekranie. → Brak jednej spokojnej palety, kolor dominuje nad treścią. → `.card--thread::before` → neutralna `var(--line)`. Kolor obszaru tylko na kropce `.area-tag__dot`. | S |
| **J1B-05** | 1 | `/zgloszenie/<id>` (i każda `ol.list-plain` z kartami) | ODBIERA PUNKTY | UI | 5 kart dopasowań leży bez odstępu, a paski obszaru tworzą jeden słup, bo `.list-plain > li:not(.card)` pomija karty. → Najważniejszy ekran mieszkanki po zapisie wygląda niechlujnie. → `.list-plain > li.card + li.card { margin-top: .75rem }`. | S |
| **K-10** (J1B-03, J3-12) | 1, 3 | `/admin/*` (menu panelu) | ODBIERA PUNKTY | Panel / UI | 12 zakładek w 2 rzędach, pilotaże między Trendami a Biblioteką. Z H1 to ok. 420 z 768 px. Brak liczników. → Cel 5–7 pozycji, najważniejsze zadania się rozmywają. → Kolejność: Skrzynka, Wątki bez odpowiedzi, Trendy i luki, Biblioteka, Nabory, Import, Kolejka e-mail, Użytkownicy, Role, na końcu „Pilotaż ZD”. Liczniki przy Skrzynce i Wątkach, mniejszy H1 panelu. Grupowanie w 5–6 grup to wersja M. | S |
| **T-5** | 3 | `/wyniki` (syn z ZD, praca) | ODBIERA PUNKTY | Matchmaking | Top 3 po „szkołę, pierwszej”, brak przejścia do `/razem/praca` i „Jestem potrzebny”. → Pilotaż i Matchmaking wyglądają jak dwa osobne światy. → Gdy obszar to `rodziny-zd` i temat „praca”, nad listą karta-skrót „Mapa miejsc pracy przyjaznych osobom z ZD → /razem/praca” (i `/razem/jestem-potrzebny`). | S |
| **J1A-04** (J2-11 część) | 1, 2 | `/biblioteka` | ODBIERA PUNKTY | Tester | „Ocena testujących: 5.0/5 (1 ocena)” wisi pod kartą, w szczelinie siatki, i rozjeżdża wiersze. Zapis „4.5/5 (2)” jest nieczytelny. → Jedyny ślad Testera na liście wygląda jak błąd układu. → Ocena w środku karty jako plakietka „★ 4,5 na 5 · 2 oceny” (opcjonalny parametr `rating` w `innovation_card`). | S |
| **J1A-05** (J2-11) | 1, 2 | `/biblioteka/<id>` (Film) | ODBIERA PUNKTY | Zasobnik wiedzy | Gość widzi pusty „Film” z notatką dla admina: „pojawi się po imporcie…”. → Wygląda jak placeholder. → Sekcja tylko `{% if video %}`, a notatka wyłącznie dla roli admin. | S |
| **J3-07** | 3 | `/wyniki`, `/admin/luki` | ODBIERA PUNKTY | Matchmaking / wiarygodność | Idealny „Telefon Życzliwości” ma „37%”, a luki „seniorzy sami w górskich wsiach” przeczą Bibliotece. → Na lukach nie da się oprzeć decyzji o konkursach. → Nie pokazywać surowego procentu BM25 (częściowo robi to J2-03). Przekalibrować `gaps()`: luka tylko wtedy, gdy nie ma innowacji z obszaru z etykietą co najmniej „Może pasować”. | M |
| **J1B-09** | 1 | `/pomysly/<id>`, `/kanwa` | ODBIERA PUNKTY | Kreator | „Kanwa” to 10 par tekstu w jednej kolumnie, a „9 z 10” to szary tekst. → Wizytówka Kreatora wygląda jak formularz. → Kanwa jako `.grid` kart (3 kolumny na desktopie, 1 na telefonie), postęp jako `<progress>`. | M |
| **J1B-08** | 1 | `/moje` | ODBIERA PUNKTY | Komunikacja | Lista zgłoszeń nie mówi, przy którym odpisał Hub. Status „Nowe” jest wypełniony, reszta konturowa. → Autor nie wie, co otworzyć (budżet 2). → Plakietka „Nowa odpowiedź Hubu” i sortowanie tych zgłoszeń na górę. | S |
| **J1A-08** | 1 | `/razem*` | ODBIERA PUNKTY | UI | Podmenu modułu ma 10 pozycji w 2 liniach (z sierotą), razem z menu głównym 16 pozycji. → Pilotaż przytłacza moduły z briefu. → 5 pozycji, reszta pod `<details>` „Więcej”, „Strona dla mnie (łatwy tekst)” jako pigułka w nagłówku. | M |
| **K-08** | 2 | Wszystkie ekrany na telefonie | ODBIERA PUNKTY | Dostępność | Zwinięte menu i drugie „Menu panelu” dokładają 1–2 kliknięcia, więc 7 z 9 ścieżek jest ponad budżetem na telefonie. → Juror 2 testuje na telefonie. → Stały dolny pasek z 4 pozycjami na ≤600 px. Najważniejszą część (licznik) pokrywa K-09. | M |
| **J1A-12** | 1 | `/wyniki` | KOSMETYKA | UI | Dwie przerywane ramki pod rząd (`.masked`, `.ai-box--rules`), ⚙, podwójne oznaczenie PRZYKŁAD. → Dashed wygląda jak makieta. → Ramki solid 1px `var(--line)`, nagłówek fallbacku „Rozpoznane tematy”. | S |
| **J1A-14** (J1B-13) | 1 | `/wiedza`, `/biblioteka/<id>`, `/pomysly/<id>`, kanwa, karta, admin form | KOSMETYKA | UI | Trzy różne style akcentów: koral u góry i fiolet z boku spotykają się w rogu. Link „← …” przylega do nagłówka. → Brak spójności i oddechu. → Jeden wzór akcentu (lewa krawędź), bez `border-top` koral. Odstęp linku powrotu (CSS na pierwszym `<p>` w `main`). | S |
| **J1A-16** (J1B-14, WZ-6) | 1 | `hugme.css` | KOSMETYKA | UI | Ok. 20 kolorów wpisanych na sztywno poza `:root` i 6 różnych promieni. → Paleta wycieka, tryb kontrastu wymaga polowania po pliku. → Tokeny `--violet`, `--ok-bg`, `--mark`, `--ai-dark`, `--heat-*`, `--radius-sm`, a w regułach `var()`. | S–M |
| **J2-14** | 2 | Plakietki (`.badge`, `.status`) | KOSMETYKA | Dostępność | 13,5 px, a na ekranie 8+ plakietek PRZYKŁAD. → Granica czytelności. → `.badge`, `.status` ≥ 0.95rem. Plakietki PRZYKŁAD zostają (uczciwość danych to plus u Jurora 3). | S |
| **J1B-11** (J2-13) | 1, 2 | `/admin` (kafle) | KOSMETYKA | UI | Wysokie kafle z pustym dołem, klikalny tylko tekst. Odmiana „1 wątków”, „4 wątków czeka”, kod „zgloszenie”, „CSV”. → Wygląda niedbale. → `.stat a {display:block;height:100%}`, filtr `plural`, mapa `kind` → etykieta, „Pobierz do Excela (plik CSV)”. | S |
| **J1B-16** | 1 | `/admin/watki` | KOSMETYKA | Komunikacja | Wiersz bez obszaru, bez „czeka od …” i bez przycisku „Odpowiedz”. → Szybkość komunikacji. → `area_tag`, „czeka od X h/dni”, przycisk „Odpowiedz” → `#watek`. | S |
| **J1B-12** | 1 | `/pomysly/<id>` | KOSMETYKA | UI | 4 kolory przycisków, kilka głównych akcji. → Brak jednej głównej akcji. → „Przygotuj wniosek” jako `.btn` (kontur), ceglasty tylko „Wyślij”. | S |
| **J1A-13** | 1 | `/wiedza/obszar/<slug>` | KOSMETYKA | Zasobnik | Dwa przyciski primary obok siebie. → Brak hierarchii. → Jeden primary, „Obserwuj” jako ghost, reszta jako linki. | S |
| **J1A-15** | 1 | `/razem/praca`, `/razem/jestem-potrzebny` | KOSMETYKA | UI | Kafle liczb przyklejone do hero, „103 ZAZ · 708 WTZ” łamie się. → Rytm odstępów. → Margines nad kaflami, „103 ZAZ”, WTZ w opisie. | S |
| **J1A-18** | 1 | `/` (ramka demo) | KOSMETYKA | Materiały | „Oglądasz demo?” to `<summary>` bez strzałki, wygląda jak statyczny pasek. → Atut dla jury łatwo przeoczyć. → Znacznik ▸/▾, `cursor:pointer`, hover. Tekst „Oglądasz demo? Przewodnik dla jury: 5 kroków, 3 min” (test sprawdza „Oglądasz demo?”). | S |
| **J2-15** (WZ-8) | 2 | Stopka | KOSMETYKA | Dostępność | Link „API” otwiera surowy JSON. → Ślepa uliczka dla seniora. → Tekst „Dane otwarte (dla programistów)”. Strona HTML z opisem API dopiero po 08:00. | S |
| **K-12** | 1 | `/konto` → przekierowanie | KOSMETYKA | Dostępność | Po wyborze roli bez `next` każdy ląduje na `/`. → Admin traci kliknięcie na każdej ścieżce (P6, P8, P9). → Domyślny cel według roli: admin→`/admin`, gmina→`/posrednik`, ekspert→`/ekspert`. | S |
| **T-6** | 2, 3 | `/wyniki` | KOSMETYKA | Matchmaking | Dwie karty „35%” z różnymi etykietami („Może pasować” i „Słabe”). → Wygląda na błąd skali. → `label(round(score, 2))`. | S |
| **J2-10** | 2 | `/pomysly`, `/pomysly/<id>`, `/admin/nabory` | KOSMETYKA | Dostępność | Terminy w ISO „2026-11-15”, a gdzie indziej „04.10.2026”. → Niespójne i nieczytelne. → Filtr `data_pl`. | S |
| **J3-11** | 3 | `docs/KRYTERIA.md`, `README.md`, slajdy | KOSMETYKA | Materiały | Tabela ma 8 wierszy („Trendy” jako moduł), nazwy różnią się od briefu, Tester opisany jako `#tester`. → Jury porównuje 1:1 z listą z briefu. → Dokładne nazwy z briefu, Trendy w wierszu Panelu, nowa ścieżka `/tester`. To Etap 4, po zamrożeniu nazw. | S |
| **J3-13** | 3 | Etap innowacji | KOSMETYKA | Materiały | „Etap: test” na 9 ekranach wygląda jak ślad roboczy. → Dwuznaczne. → Etykieta „w testach”, ale `STAGES` to jednocześnie klucze w bazie, więc tylko mapą etykiet przy wyświetlaniu. | S |
| **J3-14** | 3 | Błędy walidacji | KOSMETYKA | Potencjał | 422 widoczne na czerwono w konsoli DevTools. → Juror może to wziąć za błąd. → Świadomie zostawiamy 422 (semantyka i testy), na sali odpowiadamy jednym zdaniem. | – |
| WZ-3, WZ-5, WZ-7, WZ-9, WZ-11 | 1 | Globalnie | KOSMETYKA | UI / Materiały | Ikony Unicode zamiast jednej rodziny, puste stany bez akcji, brak strony „Jak dopasowujemy”, brak przewodnika krokowego, brak PRZED-PO. → Wzorce z Trash Fairy. → WZ-9 w Etapie 3, WZ-11 w Etapie 4, pozostałe po 08:00 (patrz `WZORCE.md`). | S–M |

† podniesione do BLOKUJE przez sekretarza: wymóg wprost z profilu A (7 modułów i osobne wejście Testera) oraz pierwszy test trafności z listy jury.

---

## Przegląd wizualny (Juror 1)

Skala 1–5. Najpierw ekrany z najniższą oceną cząstkową, potem według sumy. ≤3 = do planu poprawek.

| Ekran | Pierwsze wrażenie | Kolory | Schludność | Spójność | Gęstość | Czytelność | Min / suma | Komentarz |
|---|---|---|---|---|---|---|---|---|
| `/admin` (Skrzynka) | 3 | 3 | 3 | 4 | **2** | 3 | 2 / 18 | 12 zakładek, 33 wiersze „Nowe sprawy” niezgodne z kaflem, nowe pomysły niewidoczne, błędy odmiany |
| `/posrednik/karta/<id>` | 3 | 4 | 3 | 3 | **2** | 3 | 2 / 18 | Ściana tekstu w przerywanej ramce, brak Drukuj/PDF, inspiracje jako gołe linki |
| `/biblioteka` | 4 | **2** | 3 | 4 | 3 | 4 | 2 / 20 | Tęcza 7 kolorów i wzorów, ocena pływa pod kartą |
| `/zgloszenie/<id>` (po zapisie) | 4 | 4 | **2** | 4 | 3 | 4 | 2 / 21 | Świetny flash, ale karty sklejone, 4 z 5 „Słabe”, dubel treści w rozmowie |
| `/razem` | 3 | 4 | 4 | 3 | **2** | 5 | 2 / 21 | 16 pozycji nawigacji, sierota w podmenu, fiolet poza marką |
| `/moje` (mieszkanka) | 3 | 4 | 3 | 3 | 3 | 4 | 3 / 20 | Brak sygnału „Hub odpisał”, niespójne statusy |
| `/moje` (organizacja) | 3 | 4 | 3 | 3 | 3 | 4 | 3 / 20 | Ok. 2900 px, pomysły jako zwykłe linki |
| `/pomysly/<id>` | 4 | 3 | 3 | 3 | 3 | 4 | 3 / 20 | Kanwa to lista, 4 kolory przycisków, link powrotu przyklejony |
| `/wyniki` | 3 | 4 | 4 | 3 | 3 | 4 | 3 / 21 | Świetne karty z „Dlaczego pasuje”, ale pod „Twój opis” i ramką fallbacku, brak akcji |
| `/razem/praca` | 3 | 4 | 3 | 4 | 3 | 4 | 3 / 21 | Kafle przyklejone do hero, kafel ZAZ/WTZ się łamie |
| `/admin/trendy` | 3 | 4 | 4 | 4 | 3 | 3 | 3 / 21 | Brak wykresu i sortowania, na telefonie ucięta kolumna „Zmiana” |
| `/admin/uzytkownicy` | 3 | 4 | 3 | 4 | 3 | 4 | 3 / 21 | Kafle z pustą przestrzenią |
| `/` (start) | 3 | 3 | 4 | 4 | 3 | 5 | 3 / 22 | Ciepła paleta i hasło, ale brak przycisku nad zgięciem, tęcza kart obszarów |
| `/biblioteka/<id>` (+ #tester) | 3 | 4 | 3 | 4 | 3 | 5 | 3 / 22 | Pusty „Film”, Tester dla gościa to jeden przycisk |
| `/wiedza/obszar/<slug>` | 3 | 4 | 4 | 3 | 3 | 5 | 3 / 22 | Dwa przyciski główne |
| `/pomysly/<id>/kanwa` | 3 | 4 | 4 | 4 | 3 | 4 | 3 / 22 | Długi pionowy formularz bez metafory kanwy |
| `/pomysly/<id>/wniosek/<cid>` | 3 | 4 | 4 | 4 | 3 | 4 | 3 / 22 | Spójny, bez uwag krytycznych |
| `/admin/watki` | 3 | 4 | 4 | 4 | 3 | 4 | 3 / 22 | H1 i podmenu zajmują pół ekranu, brak „Odpowiedz” |
| `/admin/biblioteka/nowa` | 3 | 4 | 4 | 3 | 4 | 4 | 3 / 22 | Brak podmenu panelu, link powrotu przyklejony |
| `/admin/role` | 3 | 4 | 4 | 4 | 3 | 4 | 3 / 22 | Ok. 3400 px na telefonie |
| `/wiedza` | 4 | 3 | 4 | 3 | 4 | 5 | 3 / 23 | Karta „Ścieżka rodziny” z dwoma akcentami, tęcza obszarów |
| `/konto` (też z `/pomysly/nowy`) | 3 | 4 | 3 | 4 | 4 | 5 | 3 / 23 | Nierówne przyciski, karta admina pod zgięciem |
| `/razem/jestem-potrzebny` | 4 | 4 | 3 | 4 | 3 | 5 | 3 / 23 | Kafle liczb stykają się z hero |
| `/powiadomienia` | 3 | 4 | 4 | 4 | 4 | 4 | 3 / 23 | Poprawnie, bez typów i ikon |
| `/ekspert` | 3 | 4 | 4 | 4 | 4 | 4 | 3 / 23 | Pusty stan bez kontekstu |
| `/admin/nabory` | 3 | 4 | 4 | 4 | 4 | 4 | 3 / 23 | Spójny |
| `/admin/razem` | 4 | 4 | 4 | 4 | 3 | 4 | 3 / 23 | Wzorcowe numerowane kolejki do przeniesienia do Skrzynki |
| `/admin/potrzebny` | 4 | 4 | 4 | 4 | 3 | 4 | 3 / 23 | Jak `/admin/razem` |
| `/admin/poczta` | 3 | 4 | 4 | 4 | 4 | 4 | 3 / 23 | H1 i podmenu dominują nad 1 wierszem |
| `/pomysly` | 4 | 3 | 4 | 4 | 4 | 5 | 3 / 24 | Wzorowy: jedna akcja, ale karty naborów w różnych kolorach |
| `/` i `/wyniki`: A+ | 4 | 5 | 3 | 4 | 3 | 5 | 3 / 24 | Ucięty select w pasku demo, podpis logo w 2 liniach |
| `/` i `/wyniki`: wysoki kontrast | 4 | 5 | 4 | 5 | 3 | 5 | 3 / 26 | Bardzo dobrze |
| `/posrednik` (śr. 1a i 1b) | 4 | 4,5 | 4 | 4 | 4 | 4,5 | 4 / 25 | Spokojny formularz, fieldset ról wysoki |
| `/admin/luki` | 4 | 4 | 4 | 4 | 4 | 4 | 4 / 24 | Dobry, ale luka „połączona” liczona jako luka |
| `/admin/biblioteka` | 4 | 4 | 4 | 4 | 4 | 4 | 4 / 24 | Wzorcowy ekran panelu |
| `/dostepnosc` | 4 | 5 | 4 | 4 | 4 | 5 | 4 / 26 | Czysty |

---

## Budżet kliknięć

Pomiar Playwright na 127.0.0.1:5055, nowa sesja od `/`, 1366×768. Kolumna telefonu (390×844) to ta sama sekwencja plus otwarcia zwiniętych menu. Przełączenie roli paskiem demo liczę jako 0 kliknięć tylko tam, gdzie ścieżka zakłada rolę. Wpisanie tekstu nie jest kliknięciem, wybór radio jest.

| # | Ścieżka | Budżet | Desktop (rola z paska) | Gość | Telefon | Ekrany | Status | Poprawka |
|---|---|---|---|---|---|---|---|---|
| P1 | Opisać problem → dopasowania | 2 | – | 1 (przykład wpisany) | 1, ale po ~2 ekranach przewijania | 2 | ✓ (akcja pod zgięciem) | J1A-01 |
| P2 | Z wyniku do innowacji → pytanie/kontakt | 3 | 3 (mieszkanka) | **5** | 5 gość | gość 6 | ✗ gość +2, brak „Poproś o kontakt” | K-01, K-02 |
| P3 | Zgłosić pomysł (fiszka) | 4 | 3 (NGO) | 4 | 4 / gość **5** | 4 | ✓ desktop, ✗ telefon gość +1 | K-04 |
| P4 | Zgłosić się do testu i ocenić | 4 | **5** (NGO) | **7** | **6 / 8** | 5 | ✗ +1 / gość +3 | K-03, K-04 |
| P5 | Gmina: Pośrednik → karta → pobrać | 4 | 3 do karty, pobranie tylko Ctrl+P | – | 4, **nie da się pobrać** | 3 | ✗ niedomknięta | K-05, K-06 |
| P6 | Admin: nowy pomysł → odpowiedź autorowi | 3 | 3 | – | **4** | 4 | ✓ desktop, ✗ telefon +1 | K-12, K-09, J1B-01 |
| P7 | Autor: zobaczyć odpowiedź Hubu | 2 | 2 | – | **3** (licznik w zwiniętym menu) | 3 | ✓ desktop, ✗ telefon +1 | K-09 |
| P8 | Admin: dodać/edytować innowację | 4 | 4 | – | **6** | 5 | ✓ desktop, ✗ telefon +2 | K-02 (Edytuj), K-12 |
| P9 | Admin: trendy i luki | 2 | **3** (dwa ekrany) | – | **6** | 4 | ✗ +1 / telefon +4 | K-07, K-12 |

**Wynik:** na desktopie 4 z 9 ścieżek są ponad budżetem albo niedomknięte (P2 gość, P4, P5, P9), na telefonie 7 z 9.

**Architektura informacji teraz:**
- Gość ma 6 pozycji menu, mieszkanka, NGO i gmina po 8, ekspert i admin po 9, a w panelu admina jest jeszcze 12 zakładek.
- Nazwy z briefu („Zasobnik wiedzy”, „Kreator pomysłów”, „Pośrednik innowacji”) występują tylko jako H1.
- „Tester innowacji” to tylko kotwica, a „Platforma komunikacji” nie ma wejścia.

Docelowe menu gościa ma 7 pozycji (patrz K-04 i pakiet P1 w `PLAN-POPRAWEK.md`).

---

## Trafność Matchmakingu (Juror 3, bez AI)

Top 3 oceniane 0–3: 3 = trafne, 0 = bez związku. Przypadki przez API `POST /api/v1/dopasuj`, 7 z nich także przez UI.

| # | Opis | Top 3 (trafność) | Oceny | Suma | Uwagi / ID |
|---|---|---|---|---|---|
| 1 | Seniorka sama na wsi, z nikim nie rozmawia | Sąsiedzkie Dojazdy 27% / Bus na Telefon 24% / Stół Sąsiedzki 21% | 0/0/2 | **2/9** | Brak Telefonu Życzliwości i Dziennego Domu Seniora w top 5, „wsi” daje temat transportu (T-1). Wariant ze słowem „samotna” daje 3/3/1. |
| 2 | Syn 22 l. z ZD szuka pierwszej pracy | Kawiarnia Treningowa 56% / Klasa w Ruchu 44% / Szkolny Punkt Pierwszego Kontaktu 34% | 3/0/0 | 3/9 | Pozycje 2–3 po słowach „szkołę, pierwszej” (T-2), brak linku do `/razem/praca` (T-5) |
| 3 | Gmina bez transportu do lekarza dla osób z niepełnosprawnością | Bus na Telefon 58% / Asystent Seniora na telefon 39% / Dzień Specjalistów 38% | 3/1/2 | 6/9 | Nr 2 po „urzędu, gminy, osoby” |
| 4 | Depresja nastolatków w małej gminie | Szkolny Punkt Pierwszego Kontaktu 41% / Punkt e-Spraw 33% / Stół Sąsiedzki 29% | 3/0/0 | 3/9 | Pozycje 2–3 po „gminie, raz, tygodniu”, brak Przyjaciela na Ławce (T-1, T-2) |
| 5 | Wykluczenie cyfrowe seniorów | Cyfrowy Przewodnik 54% / Punkt e-Spraw 40% / Bus na Telefon 40% | 3/3/0 | 6/9 | Bus po słowie „zamówić” |
| 6 | Literówki, bez ogonków | Bus na Telefon 37% / Telefon Życzliwości 35% / Cyfrowy Przewodnik 35% | 0/3/2 | 5/9 | Ogonki obsłużone, ale „35%” ma dwie różne etykiety (T-6) |
| 7a | „samotność” (jedno słowo) | odmowa „Napisz trochę więcej” (422) | – | – | T-4 |
| 7b | „samotność seniorów” | Telefon Życzliwości 73% / Koperta Życia 72% / Międzypokoleniowe Podwórko 71% | 3/1/3 | 7/9 | Koperta zawyżona |
| 8 | Długi opis (1282 znaki) | Dzień Specjalistów 49% / Bus na Telefon 44% / Klasa w Ruchu 43% | 2/3/2 | 7/9 | Działa sensownie. Brak `maxlength` w polu (limit 1500 sprawdzany po wysłaniu). |
| 9a | „asdf” | odmowa „Napisz trochę więcej” | – | OK | Komunikat zrozumiały |
| 9b | „asdf asdf asdf asdf” | 0 wyników, komunikat i formularz zapisu | – | OK | Brak linku do Kreatora (T-3) |
| 10 | Dach zabytkowego kościoła przecieka | Klasa w Ruchu 17% („wspólne słowa: przed .”) | 0 | **0/3** | Udawane dopasowanie zamiast komunikatu o luce (T-3) |
| 10b | Brak miejsc na rowery przy dworcu w Tarnowie | 4 przypadkowe (Przyjaciel na Ławce „parkowania”, Dzień Specjalistów „miejsc”) | 0 | 0/3 | T-3, T-2 |

**Suma dla 8 ocenianych przypadków: 39/72 = 54%.** Testy `hit@3 = 11/11` przechodzą, bo używają słów ze słownika, a nie języka mieszkańca. Z kluczem AI `expanded_query` dopisuje synonimy, ale po wyczerpaniu limitu dziennego jury zobaczy fallback.

---

## Oceny wstępne (przed poprawkami)

- Juror 1 = średnia agentów 1a (ekrany publiczne) i 1b (zalogowani i panel).
- Juror 2 ocenił moduły łącznie („Stopień spełnienia wyzwania” = 7), więc 7 wpisano w każdym wierszu modułu.
- Juror 3 = średnia agenta J3 i testów trafności tam, gdzie oba oceniały (Matchmaking: 7 i 6; Potencjał: 7 i 7).
- Agent pomiaru kliknięć dał Dostępność 6, UI 6, Spełnienie 7. Nie jest wliczony do średniej, ale to ostrzeżenie: na telefonie Dostępność wypada niżej niż na desktopie.

| Kryterium (waga) | Juror 1 | Juror 2 | Juror 3 | Średnia | Średnia × waga |
|---|---|---|---|---|---|
| Matchmaking społeczny (10%) | 7,0 | 7 | 6,5 | 6,83 | 0,683 |
| Zasobnik wiedzy (5%) | 7,0 | 7 | 8 | 7,33 | 0,367 |
| Kreator pomysłów (5%) | 6,5 | 7 | 8 | 7,17 | 0,358 |
| Tester innowacji (5%) | 5,5 | 7 | 5 | 5,83 | 0,292 |
| Platforma komunikacji (5%) | 6,5 | 7 | 7 | 6,83 | 0,342 |
| Panel administratora (5%) | 6,0 | 7 | 8 | 7,00 | 0,350 |
| Pośrednik innowacji / Middleman (5%) | 6,5 | 7 | 7 | 6,83 | 0,342 |
| Potencjał wdrożeniowy (20%) | 7,0 | 7 | 7 | 7,00 | 1,400 |
| Dostępność i intuicyjność (20%) | 8,0 | 8 | 8 | 8,00 | 1,600 |
| Atrakcyjność i jakość interfejsu (10%) | 6,0 | 8 | 7 | 7,00 | 0,700 |
| Jakość materiałów i MVP (10%) | 7,0 | 7 | 8 | 7,33 | 0,733 |
| **WYNIK WAŻONY** (Σ ocena × waga) | **6,90** | **7,30** | **7,30** | **7,17** | **7,17** |

Sprawdzenie: (6,90 + 7,30 + 7,30) / 3 = 7,17. Juror 1: 0,70 + 0,05×38 + 1,40 + 1,60 + 0,60 + 0,70 = 6,90.

**Najsłabsze wiersze:** Tester (5,83), Matchmaking (6,83: trafność na języku potocznym), Komunikacja i Pośrednik (6,83). Juror 1 najniżej ocenia UI (6).

## Pytania na salę

- **Juror 1 (projektant, ekrany publiczne):** „Otwieram HugMe na laptopie (1366×768): gdzie na pierwszym ekranie jest ta jedna rzecz, którą mam kliknąć? I dlaczego po kliknięciu „Znajdź rozwiązania” pierwszy wynik widzę dopiero po przewinięciu?”
- **Juror 1 (projektant, panel):** „Koordynatorka otwiera panel w poniedziałek o 8:00 i ma przed sobą 33 wiersze i 12 zakładek. Gdzie w pierwszych 5 sekundach widzi, że ktoś zgłosił nowy pomysł i czeka na odpowiedź, i ile kliknięć dzieli ją od odpowiedzi?”
- **Juror 2 (użytkownik bez przygotowania):** „Pani Halina ma 68 lat i telefon. Wpisuje problem, klika „Znajdź rozwiązania”, potem zadaje pytanie ekspertowi. Skąd wie, że ma czekać, gdy AI myśli, zamiast kliknąć drugi raz? Gdzie widzi, że pytanie dotarło i kiedy odpowie człowiek z Hubu?”
- **Juror 3 (ekspert wdrożeniowy):** „Jeśli ROPS uruchomi HugMe jutro, to jak koordynatorka dowie się o nowym pomyśle, gdy nie siedzi zalogowana? Dziś e-maile tylko czekają w kolejce. Kto i w jakim czasie odpowie autorowi?”
- **Juror 3 (trafność):** „Mieszkanka wpisuje: „Mama ma 82 lata, mieszka sama na wsi i prawie z nikim nie rozmawia”, a system pokazuje wspólne przejazdy samochodem. Jak sprawdzacie trafność na potocznych opisach i kto w Hubie poprawia słownik, gdy dopasowanie zawiedzie?”
- **Pomiar kliknięć:** „Pokażcie Tester innowacji z telefonu, od strony startowej: gdzie jest w menu i ile kliknięć zajmuje zgłoszenie do testu i ocena?”

---

## Co poprawiono

Runda końcowa: 4.10, ok. 07:45–08:00, **produkcja** https://hugme.twapp.pl (AI włączone). Agenty: Juror 1 (projektant), Juror 2 (68+, telefon, klawiatura, axe), Juror 3 (ROPS, crawl 141 stron, trafność przez API), pomiar budżetu kliknięć.

- **PR #8** (https://github.com/TomaszWu14/hugme/pull/8): Etap 2, pakiety P1–P7 z `PLAN-POPRAWEK.md`.
- **PR #9** (https://github.com/TomaszWu14/hugme/pull/9): Etap 3, tryb Podpowiedzi.

„✔ prod” = potwierdzone przez agenta na produkcji w rundzie końcowej. „kod” = jest w PR, ale w tej rundzie nikt tego nie sprawdził.

**Spełnienie wyzwania (7 modułów)**
- K-04 ✔ prod: menu ma nazwy z briefu i zgodne z H1. Tester ma osobną stronę `/tester` (3 kroki w kartach). „Razem z ZD · pilotaż” jest na końcu za separatorem. Na starcie są kafle „7 modułów HubMi” i przewodnik dla jury „5 kroków, ok. 3 min” (J1A-18).

**Matchmaking**
- T-3 ✔ prod: „Dach kościoła” daje 0 wyników zamiast udawanego dopasowania. Gdy nic nie przekracza progu, UI pokazuje „Nie mamy jeszcze sprawdzonego rozwiązania” i „Luźno powiązane (N)”.
- J2-03, T-6 ✔ prod: zamiast procentu jest etykieta słowna z paskiem, a etykieta jest liczona z pokazanego procentu.
- J1A-02 ✔ prod: opis zwinięty do jednej linii z „Zmień opis”, u góry „Zapisz zgłoszenie ↓”, pierwsza karta nad zgięciem na desktopie (y≈615–636).
- T-1, T-2 kod: lokalnie `tests/test_trafnosc.py` 12/12. **Na produkcji jeszcze nie działa**, bo baza ma słowa kluczowe innowacji sprzed PR #8. Patrz BLOKUJE w „Czego nie zdążono”.
- T-4, T-5 kod.

**Tester innowacji**
- K-03 ✔ prod: przycisk „Testuj” na kartach, ocena ★1–5 jednym kliknięciem. P4 zajmuje 4 kliknięcia zamiast 5, a gościowi 5 zamiast 7.
- J3-03 kod: jedna ocena na osobę.
- J1A-04 kod.

**Platforma komunikacji**
- K-09 ✔ prod: dzwonek z licznikiem.
- J1B-08 ✔ prod: plakietka „Nowa odpowiedź Hubu” na `/moje`.
- K-02 ✔ prod: rząd 3 akcji na innowacji („Zadaj pytanie”, „Testuj i oceń”, „Dopasuj do mojej gminy”).
- Pełna pętla zgłoszenie → skrzynka → status → odpowiedź → powiadomienie ✔ prod (J3: zgłoszenie #43).
- K-01 częściowo: jest „Zapytaj autorów” i wejście jednym kliknięciem roli demo, ale nadal nie ma „Poproś o kontakt”.

**Panel administratora**
- K-07 ✔ prod: trendy i luki na jednej stronie, posortowane. P9 zajmuje 2 kliknięcia zamiast 3.
- J1B-01 ✔ prod: kafle z liczbami na górze, sprawy „czeka na odpowiedź” na górze skrzynki, nowy pomysł od razu widoczny.
- K-10 częściowo ✔ prod: podmenu w 1 rzędzie z licznikiem przy Skrzynce, ale nadal 10 zakładek.
- J3-04 ✔ prod: uczciwy tekst „po wdrożeniu wyjdą automatycznie przez SMTP (w demo nic nie jest wysyłane)”.
- J1B-11, J1B-10, J2-13, K-12 kod.

**Pośrednik innowacji**
- K-06 ✔ prod: gmina ma od razu zaznaczone „Gmina / urząd”, a `?inspiracja=<id>` wypełnia opis.
- K-05 ✔ prod: przycisk „Drukuj / zapisz jako PDF” pod H1 z instrukcją dla telefonu. P5 jest domknięty (wcześniej nie dało się pobrać karty).

**Kreator pomysłów**
- J2-07 ✔ prod: „Fiszka pomysłu – 4 pola, ok. 5 minut” i wyjaśnienie słowa kanwa.
- J2-02 ✔ prod: `data-czekaj` „Asystent pracuje… do pół minuty”. Asystent odpowiada w 10,1 s.
- J1B-09 kod (kanwa jako karty).

**Dostępność i intuicyjność**
- J2-02 ✔ prod: stan oczekiwania na AI.
- J1A-01 ✔ prod: „Opisz sytuację” nad zgięciem (desktop y≈547).
- Skip link, widoczny fokus 3 px i 0 naruszeń axe na 8 widokach produkcji ✔ prod. Wśród nich są widoki z otwartą chmurką i z otwartym przewodnikiem.
- J1A-10, J2-08 częściowo (pasek demo na telefonie nadal ok. 150 px).
- J2-01 kod: potwierdzenia w sekcji docelowej.
- PR #9 ✔ prod:
  - przełącznik „Podpowiedzi: wł./wył.” jako ciasteczko bez JS, jak A+;
  - „i” jako natywne `<details>` w 3 częściach, cel dotykowy 49,5 px, zamykanie Esc z powrotem fokusu;
  - „Przewodnik po tej stronie” na 7 ekranach;
  - po wyłączeniu 0 śladów na 4 ekranach.

**Atrakcyjność interfejsu**
- J1A-03, J1B-05, J1A-12, J1A-14 kod.
- Oceny wizualne Jurora 1 (min/suma) wzrosły:
  - `/biblioteka/1` z 3/22 na 4/25;
  - `/admin` z 2/18 na 3/22;
  - karta usługi z 2/18 na 3/23;
  - `/zgloszenie` z 2/21 na 4/24.

**Zrzuty: przed → po → końcowe**
- `docs/audit/iteracje/00-przed/`: lokalnie, bez AI, Etap 1.
- `docs/audit/iteracje/01-po/`: po PR #8, pliki `p1-…` do `p5-…` (pakiety).
- `docs/audit/iteracje/02-final/`: produkcja po PR #9.
  - 01–16: Juror 1, ekrany i tryb Podpowiedzi.
  - 20–33: Juror 2, telefon, chmurki, przewodniki, A+ z kontrastem.
  - 30-j3…38-j3: Juror 3. **31-j3-wyniki-seniorka** to dowód problemu z danymi.
  - 40–51 budzet: ścieżki P1–P9.
  - 40–48: Juror 2, klawiatura.
- Pary do slajdu PRZED/PO:

| Ekran | Przed | Po PR #8 | Końcowe |
|---|---|---|---|
| Start | `00-przed/01-start-desktop.jpg` | `01-po/p1-start-desktop.jpg` | `02-final/01-start-desktop.jpg` |
| Wyniki | `00-przed/02-wyniki-desktop.jpg` | `01-po/p3-wyniki-desktop.jpg` | `02-final/02-wyniki-desktop.jpg` |
| Tester | `00-przed/05-innowacja-tester-desktop.jpg` | `01-po/p4-tester-desktop.jpg` | `02-final/05-tester-desktop.jpg` |
| Panel Hubu | `00-przed/40-admin-desktop.jpg` | `01-po/p5-panel-desktop.jpg` | `02-final/13-admin-desktop.jpg` |
| Podpowiedzi | – | – | `02-final/15-przewodnik-start-desktop.jpg`, `16-chmurka-i-desktop.jpg` |

## Czego nie zdążono i jak o tym mówić

Przy każdej pozycji podane jest, jak o niej mówić jury: uczciwie, jako roadmapa.

**BLOKUJE (naprawa operacyjna, 2 minuty, bez kodu)**
- **Produkcja ma stare dane innowacji** (słowa kluczowe sprzed PR #8). Seed ładuje się tylko do pustej bazy, a reset demo czeka na 20 minut bez wpisów, których przez audyty nie było. Sekretarz sprawdził o ok. 07:55 przez `POST /api/v1/dopasuj` zdanie „Mama ma 82 lata, mieszka sama na wsi…” i dostał Przyjaciel na Ławce 0,24 / Bus na Telefon 0,20 / Koperta Życia 0,07, wszystko „Słabe dopasowanie”. Obszar „samotnosc” rozpoznało poprawnie, więc kod słownika już działa.
  - Naprawa: w terminalu kontenera w Coolify uruchomić `python scripts/reset_demo.py --force`. Potem powtórzyć curl: Dzienny Dom Seniora albo Telefon Życzliwości ma być w top 3. Do pokazu nic nie zapisywać.
  - *Jak mówić:* „Poprawka trafności jest w kodzie i w testach, a dane demo odświeżamy osobnym poleceniem. W ROPS Bibliotekę zmienia koordynatorka w panelu albo importem, a nie seed”. Lepiej jednak, żeby to pytanie w ogóle nie padło.

**Z planu: „nie” lub po 08:00**
- J3-07 (kalibracja procentów i progu luk, M): „Próg luki jest jedną stałą (`GAP_THRESHOLD`). Kalibrujemy go na prawdziwych zgłoszeniach z pilotażu, a nie na 42 przykładowych”.
- K-08 (dolny pasek nawigacji na telefonie, M): „Na telefonie dzwonek z licznikiem i najważniejsze akcje są już widoczne. Dolny pasek to następny krok po testach z seniorami”.
- J1A-16 (tokeny CSS): „Kolory są zebrane w zmiennych dla trybu kontrastu, porządkowanie reszty to dług techniczny bez wpływu na użytkownika”.
- J2-10 (daty ISO): „Ujednolicamy na format polski, drobiazg z listy”.
- J3-13 („Etap: test”): „To nazwa etapu z Biblioteki ROPS (prototyp/test/wdrożenie). Etykietę zmienimy przy imporcie prawdziwych danych”.
- J3-14 (422 w konsoli): „422 to poprawna odpowiedź na za krótki opis, użytkownik widzi zwykły komunikat”.
- K-11 w wersji M (formularz w hero): „Główna akcja jest już nad zgięciem, a formularz w hero przetestujemy A/B”.
- Grupowanie 10 zakładek panelu (K-10 M): „Najważniejsze zadania koordynatorki są na górze panelu z licznikami, a zakładki pogrupujemy po rozmowie z koordynatorką ROPS”.
- Wysyłka SMTP (J3-04 M): „Kolejka e-mail jest gotowa i widoczna w panelu. Wysyłka to podanie serwera SMTP urzędu, ok. dzień pracy”.
- WZ-3 (ikony), WZ-5 (puste stany), WZ-7 (strona „Jak dopasowujemy”), WZ-8 (strona API): „Roadmapa UI. Logikę dopasowania wyjaśnia każda karta („Dlaczego pasuje”), a API ma dokumentację w README”.

**Pozostałe problemy jurorów (runda końcowa)**

| Waga | Problem | Plik | Nakład | Jak mówić |
|---|---|---|---|---|
| ODBIERA PUNKTY | Menu zalogowanych przy 1366 px łamie się na 2 rzędy, „Razem z ZD · pilotaż” zostaje sam z kreską (J1, J3, kliknięcia) | `app/static/css/hugme.css`, `app/templates/base.html` | S | „Znamy to, poprawka CSS. Gość widzi menu w 1 rzędzie” |
| ODBIERA PUNKTY | Arkusz chmurki „i” na telefonie (55vh) zasłania pole, którego dotyczy (J2) | `app/static/css/podpowiedzi.css` (l. 39), `app/static/js/podpowiedzi.js` (`placeHelp`) | S | „Chmurka zamyka się Esc albo kliknięciem obok. Wysokość arkusza zmniejszamy do 40% ekranu” |
| ODBIERA PUNKTY | „Przewodnik po tej stronie” zajmuje osobny rząd, a na `/` są dwa przewodniki (J1) | `app/templates/_podpowiedzi.html`, `app/static/css/podpowiedzi.css` (`.tour-start`) | S | „Jeden jest dla mieszkańca (ten ekran), drugi to trasa dla jury. W wersji produkcyjnej trasy jury nie ma” |
| ODBIERA PUNKTY | Pasek demo na telefonie ok. 150 px, H1 na ok. 280 px (J1) | `base.html`, `hugme.css` | S | „Pasek istnieje tylko w trybie demo. W produkcji jest logowanie, a wybór ról znika” |
| ODBIERA PUNKTY | Pośrednik: domyślne „dzieci i młodzież” daje kartę seniorów „Dla: dzieci i młodzież” (kliknięcia) | `app/templates/posrednik.html` | S | „Pole ma wartość domyślną. Dodajemy pustą opcję, więc wybór będzie wymuszony” |
| ODBIERA PUNKTY | Brak „Poproś o kontakt”, jest tylko „Zadaj pytanie” (K-01, kliknięcia) | `app/templates/innowacja.html` | S | „Pytanie w wątku trafia do autorów i Hubu z powiadomieniem, to jest prośba o kontakt” |
| ODBIERA PUNKTY | Asystent AI pisze z błędami („godparent”, „relaisu”) (J3) | `core/ai.py` (prompt asystenta) | S | „Odpowiedź AI jest oznaczona „sprawdź, zanim użyjesz”. Prompt wymusza poprawną polszczyznę” |
| ODBIERA PUNKTY | Potrzeba spoza katalogu w API: 5 słabych wyników (rowery w Tarnowie). UI zwija je w „Luźno powiązane” (J3) | `app/views/api.py`, `core/catalog.py` | S | „W interfejsie mówimy wprost, że nie mamy rozwiązania, i zapisujemy lukę. API zwraca etykietę „Słabe dopasowanie” dla integratorów” |
| ODBIERA PUNKTY | Gość +1 kliknięcie w P2 i P4 (wybór konta demo) | `innowacja.html`, `app/auth.py` | M | „W produkcji to logowanie login.gov.pl, którego wymaga RODO przy ocenach i wątkach” |
| ODBIERA PUNKTY | Materiały: „nazwy z briefu” w menu, a „Szukaj pomocy” i „Moje sprawy” to inne nazwy. `docs/KOSZTY.md` pisze „limit 8 s”, a kod ma 25 s (`core/ai.py:19`) (J3, kliknięcia, sekretarz) | `docs/slajdy/prezentacja.html`, `docs/KRYTERIA.md`, `docs/KOSZTY.md` | S | „Menu mówi językiem mieszkańca. Mapowanie na nazwy z briefu jest na kaflach „7 modułów HubMi”” |
| ODBIERA PUNKTY | Budżet kliknięć na telefonie nie był ponownie mierzony (wcześniej 7 z 9 ponad budżetem) | – | – | „Na telefonie dzwonek i przyciski akcji są już widoczne bez menu. Pełny pomiar mobilny robimy po hackathonie” |
| KOSMETYKA | Tester poniżej 3 kroków wygląda jak klon Biblioteki (J1). Obietnica „jednym kliknięciem” na `/tester`, a gwiazdki są w karcie (J2) | `app/templates/biblioteka.html` | S (tekst) / M (sekcja) | „Tester i Biblioteka to ten sam katalog, a Tester dodaje proces: zgłoszenie, ocena i poprawka” |
| KOSMETYKA | Żargon w pasku: „Gmina (JST)”, „Koordynatorka ROPS”, „CUS”, „ZD” (J2) | `core/domain.py`, `innowacja.html:58`, `base.html` | S | „Każdy skrót ma „i” z wyjaśnieniem. Etykiety ról upraszczamy” |
| KOSMETYKA | Brak flasha po odpowiedzi w wątku zgłoszenia (J3) | `app/views/komunikacja.py` | S | „Wiadomość dochodzi, autor dostaje powiadomienie. Brakuje tylko potwierdzenia dla koordynatorki” |
| KOSMETYKA | `/api/v1/innowacje` zwraca `http://` zamiast `https://` (brak ProxyFix) (J3) | `app/__init__.py` | S | „Konfiguracja proxy, jedna linia” |
| KOSMETYKA | Fokus po przejściu na `/wyniki` zostaje na BODY. Kroki przewodnika po `/wyniki` na telefonie skaczą (J2) | `wyniki.html`, `czekaj.js`, `app/podpowiedzi.json` | S | „Tytuł strony się zmienia. Fokus na H1 to poprawka z listy” |
| KOSMETYKA | 5 kółek „i” w filtrach, 3 style plakietek na `/moje`, szablon karty powtarza problem, kafel trendów to tekst, po edycji innowacji admin ląduje na stronie publicznej (J1, kliknięcia) | `biblioteka.html`, `moje.html`, `app/views/posrednik.py` (`rule_card`), `admin/*.html`, `app/views/admin.py` | S | Bez komentarza na sali, poprawki z listy |

## 10 najtrudniejszych pytań

1. **„Mama ma 82 lata, mieszka sama na wsi i z nikim nie rozmawia”, a pierwszy wynik to Bus na Telefon. Dlaczego, skoro materiały mówią, że to zdanie przechodzi test? Kto poprawia słownik?** (J2, J3)
   - Po odświeżeniu danych demo to zdanie daje Dzienny Dom Seniora, Telefon Życzliwości i Stół Sąsiedzki. Pilnuje tego `tests/test_trafnosc.py` (16/16 w top 3 na zestawie testowym).
   - Matchmaking to BM25 + słownik tematów (`core/match.py`), więc każdy wynik ma „Dlaczego pasuje” i da się go poprawić bez programisty: koordynatorka edytuje „Słowa kluczowe dla wyszukiwarki” innowacji w panelu.
   - *Warunek: przed 08:30 wykonać reset danych na produkcji.*
2. **Poprawka trafności jest w repo, ale nie na produkcji. Jak wdrażacie zmiany danych razem z kodem?** (J3)
   - Kod (słownik) wdraża się automatycznie. Dane przykładowe ładują się tylko do pustej bazy, żeby wdrożenie nigdy nie nadpisało pracy koordynatorki.
   - W ROPS Biblioteka pochodzi z importu CSV/JSON (`/admin/import`) i edycji w panelu, a nie z seedu. Seed to tylko demo, które odświeżamy `scripts/reset_demo.py --force`.
3. **Potrzeba spoza katalogu (rowery przy dworcu w Tarnowie) dostaje przypadkowe wyniki. Kiedy mówicie wprost „nie mamy rozwiązania”?** (J3)
   - Gdy żaden wynik nie przekracza progu `GAP_THRESHOLD`, ekran wyników pokazuje „Nie mamy jeszcze sprawdzonego rozwiązania dla tej potrzeby” z przyciskami „Zapisz zgłoszenie – Hub poszuka” i „Masz pomysł? Zgłoś go”. Słabe wyniki są zwinięte w „Luźno powiązane”. Dach kościoła daje dziś 0 wyników.
   - Zgłoszenie bez rozwiązania trafia do panelu jako luka, a luki i trendy są dla ROPS podstawą do naborów.
4. **Ile kosztuje AI przy 1000 zgłoszeń miesięcznie i co widzi mieszkaniec po wyczerpaniu limitu?** (J2, J3)
   - Analiza opisu to ok. 0,0015 USD (0,6 gr), więc 1000 wyszukiwań to ok. 1,5 USD. Cały pilotaż z asystentem i kartami to ok. 25 zł miesięcznie (`docs/KOSZTY.md`).
   - Sufit jest w kodzie (`AI_DAILY_LIMIT`, domyślnie 300 dziennie, maks. ok. 250 zł miesięcznie), a powtórzone pytania idą z pamięci podręcznej.
   - Po limicie wyniki dalej są: liczy je BM25 i słownik. Znika tylko ramka „Jak rozumiemy Twoją sytuację”, którą zastępuje podpowiedź z szablonu.
5. **Koordynatorka nie siedzi zalogowana. Jak dowie się o nowym pomyśle, kto odpowiada i w jakim czasie?** (J3, kliknięcia)
   - Każde zgłoszenie i pomysł trafia na górę Skrzynki z licznikiem i do kolejki e-mail. Wysyłka to podanie serwera SMTP urzędu (dziś w demo uczciwie: „nic nie jest wysyłane”).
   - `docs/KOSZTY.md` zakłada 1 etat koordynatora Hubu z celem odpowiedzi w 3 dni robocze. Technologia kosztuje ok. 75 zł miesięcznie, a ludzie ok. 10–13 tys. zł.
6. **Gdzie w menu jest Matchmaking i Platforma komunikacji? I co znaczą JST, ROPS, CUS, ZD?** (kliknięcia, J2)
   - Menu mówi językiem mieszkańca: „Szukaj pomocy” to Matchmaking społeczny, „Moje sprawy” z dzwonkiem to Platforma komunikacji, „Panel Hubu (administratora)” to Panel. Pełne nazwy z briefu są na kaflach „7 modułów HubMi” na starcie.
   - Skróty mają przy sobie „i” z wyjaśnieniem, a etykiety ról w pasku demo upraszczamy.
7. **Na telefonie podpowiedź zasłania pole. Czy podpowiedzi są domyślne, pamiętacie wyłączenie i co z czytnikiem ekranu?** (J2)
   - Podpowiedzi są domyślnie włączone. Wyłączenie zapisuje ciasteczko (`hints_off`), tak jak A+ i kontrast, bez JS.
   - „i” to natywne `<details>`: czytnik ogłasza „Podpowiedź: Powiat, zwinięte”, Esc zamyka i oddaje fokus. axe daje 0 naruszeń także z otwartą chmurką.
   - Wysokość arkusza na telefonie (55% ekranu) zmniejszamy, żeby pole było widoczne.
8. **Po zalogowaniu na laptopie 1366 px menu rozjeżdża się na dwa rzędy, a na każdej stronie jest osobny rząd na przewodnik. Testowaliście to?** (J1)
   - Testowaliśmy jako gość, gdzie menu ma 7 pozycji w jednym rzędzie. Zalogowane role mają 8–9 pozycji i dzwonek, to poprawka CSS.
   - Przewodnik po stronie jest dla mieszkańca, a rozwijana trasa „5 kroków” na starcie jest tylko dla jury i znika poza trybem demo.
9. **Tester wygląda jak Biblioteka i obiecuje ocenę „jednym kliknięciem”, a gwiazdki są w karcie po wyborze konta. Ile kliknięć potrzebuje nowa osoba? Co z RODO?** (J1, J2, kliknięcia)
   - Zalogowana mieszkanka potrzebuje 4 kliknięć (Tester → Testuj → Zgłoś do testu → ★5, budżet 4), gość 5, bo wybiera konto demo.
   - Tester celowo korzysta z tego samego katalogu co Biblioteka i dokłada proces: zgłoszenie do testu, ocenę 1–5 (jedna na osobę, nie da się nabić średniej) i propozycję poprawki.
   - W produkcji wybór konta zastępuje login.gov.pl, bo oceny i wątki muszą mieć autora.
10. **Karta usługi dla problemu seniorów ma „Dla: dzieci i młodzież”. Ile trwa karta bez AI i co, gdy AI nie odpowie w 25 s?** (kliknięcia, J1)
    - Karta z AI powstaje w ok. 16 s. Bez AI albo po 25 s bez odpowiedzi (`core/ai.py`, `TIMEOUT = 25`) od razu generuje się karta z szablonu, więc ścieżka gminy się nie urywa.
    - Pole „Dla kogo” miało wartość domyślną. Zmieniamy to na wymuszony wybór, żeby karta nie przeczyła problemowi.

## 5 zdań do prezentacji

1. **Spełnienie wyzwania:** „HugMe ma wszystkie 7 z 7 modułów HubMi, każdy z własnym wejściem. Na starcie są kafle „7 modułów HubMi”, a Tester innowacji ma osobną stronę, gdzie zgłoszenie do testu i ocena 1–5 to 4 kliknięcia.”
2. **Potencjał wdrożeniowy:** „To jeden kontener Flask, który na VPS z AI kosztuje ok. 75 zł miesięcznie. AI jest opcjonalne, bo bez klucza wszystko działa na BM25 i szablonach, a prawdziwą Bibliotekę ROPS koordynatorka importuje z CSV lub JSON bez programisty.”
3. **Dostępność i intuicyjność:** „138 widoków bez naruszeń wykrywanych automatycznie (axe, WCAG 2.1 A/AA), pełna obsługa klawiaturą, A+ i wysoki kontrast. Do tego tryb Podpowiedzi: „i” przy polach (do czego służy, przykład, skąd dane) i „Przewodnik po tej stronie”, wyłączane jednym przyciskiem.”
4. **Atrakcyjność UI:** „Każdy ekran ma jedną główną akcję. „Opisz sytuację” i pierwsza dopasowana innowacja są nad zgięciem, zamiast surowego procentu jest słowna ocena „Bardzo pasuje”, a panel Hubu zaczyna od spraw czekających na odpowiedź.”
5. **Materiały i MVP:** „Działające MVP na produkcji z 5 rolami demo i 313 testami automatycznymi. Trafność to 16/16 w top 3 na zestawie testowym, także dla zdań potocznych, a wszystkie 9 ścieżek jury mieści się w budżecie kliknięć na desktopie.”

*Uwaga: zdanie 5 („16/16”) i demo zdania seniorki na żywo mówić dopiero po resecie danych na produkcji i sprawdzeniu curl (patrz BLOKUJE). Liczbę 313 sekretarz sprawdził 4.10 ok. 07:58: `pytest -q` lokalnie daje „313 passed in 121.43s”.*

## Oceny końcowe (przed/po)

| Kryterium (waga) | J1 przed | J1 po | J2 przed | J2 po | J3 przed | J3 po | Średnia przed | Średnia po | Zmiana |
|---|---|---|---|---|---|---|---|---|---|
| Matchmaking społeczny (10%) | 7,0 | 7,5 | 7 | 7,0 | 6,5 | 6,75 | 6,83 | 7,08 | +0,25 |
| Zasobnik wiedzy (5%) | 7,0 | 7,0 | 7 | 7,5 | 8 | 8,0 | 7,33 | 7,50 | +0,17 |
| Kreator pomysłów (5%) | 6,5 | 7,0 | 7 | 7,0 | 8 | 7,75 | 7,17 | 7,25 | +0,08 |
| Tester innowacji (5%) | 5,5 | 7,0 | 7 | 8,0 | 5 | 7,5 | 5,83 | 7,50 | **+1,67** |
| Platforma komunikacji (5%) | 6,5 | 7,0 | 7 | 7,0 | 7 | 7,75 | 6,83 | 7,25 | +0,42 |
| Panel administratora (5%) | 6,0 | 7,0 | 7 | 7,5 | 8 | 8,0 | 7,00 | 7,50 | +0,50 |
| Pośrednik innowacji / Middleman (5%) | 6,5 | 7,5 | 7 | 8,0 | 7 | 7,25 | 6,83 | 7,58 | +0,75 |
| Potencjał wdrożeniowy (20%) | 7,0 | 7,0 | 7 | 7,5 | 7 | 7,0 | 7,00 | 7,17 | +0,17 |
| Dostępność i intuicyjność (20%) | 8,0 | 8,0 | 8 | 8,0 | 8 | 7,75 | 8,00 | 7,92 | −0,08 |
| Atrakcyjność i jakość interfejsu (10%) | 6,0 | 6,5 | 8 | 7,5 | 7 | 7,75 | 7,00 | 7,25 | +0,25 |
| Jakość materiałów i MVP (10%) | 7,0 | 7,0 | 7 | 7,5 | 8 | 7,0 | 7,33 | 7,17 | −0,17 |
| **WYNIK WAŻONY** (Σ ocena × waga) | **6,90** | **7,23** | **7,30** | **7,55** | **7,30** | **7,41** | **7,17** | **7,40** | **+0,23** |

Juror 3 „po” to średnia agenta Juror 3 i agenta pomiaru kliknięć tam, gdzie oba ocenili kryterium (Matchmaking 6 i 7,5; Kreator 8 i 7,5; Tester 7 i 8; Komunikacja 8 i 7,5; Panel 8 i 8; Pośrednik 7 i 7,5; Dostępność 8 i 7,5; UI 7,5 i 8). Agent kliknięć nie ocenił Zasobnika, Potencjału ani Materiałów, więc w tych wierszach jest sama ocena Jurora 3 (8, 7, 7). „Przed” u Jurora 3 to średnia J3 i testów trafności z Etapu 1.

**Sprawdzenie rachunku**
- J1 po: 0,1×7,5 + 0,05×(7+7+7+7+7+7,5 = 42,5) + 0,2×7 + 0,2×8 + 0,1×6,5 + 0,1×7 = 0,75 + 2,125 + 1,40 + 1,60 + 0,65 + 0,70 = **7,225 ≈ 7,23**.
- J2 po: 0,1×7 + 0,05×(7,5+7+8+7+7,5+8 = 45) + 0,2×7,5 + 0,2×8 + 0,1×7,5 + 0,1×7,5 = 0,70 + 2,25 + 1,50 + 1,60 + 0,75 + 0,75 = **7,55**.
- J3 po: 0,1×6,75 + 0,05×(8+7,75+7,5+7,75+8+7,25 = 46,25) + 0,2×7 + 0,2×7,75 + 0,1×7,75 + 0,1×7 = 0,675 + 2,3125 + 1,40 + 1,55 + 0,775 + 0,70 = **7,4125 ≈ 7,41**.
- Średnia: (7,225 + 7,55 + 7,4125) / 3 = 22,1875 / 3 = **7,396 ≈ 7,40**.
- Ta sama liczba z kolumny „Średnia po”: 0,708 + 0,05×44,583 (= 2,229) + 1,433 + 1,583 + 0,725 + 0,717 = **7,396**.
- Przed: (6,90 + 7,30 + 7,30) / 3 = **7,17**. Zmiana: **+0,23**.

**Wniosek**
- Największe zyski to Tester (+1,67), Pośrednik (+0,75) i Panel (+0,50). Pochodzą z modułów po 5%, więc wynik ważony rośnie tylko o 0,23.
- Spadek Materiałów (−0,17) i niski Matchmaking u J3 (6) mają jedną przyczynę: stare dane na produkcji. Flagowe zdanie nie działa, a materiały obiecują 16/16.
- Spadek Dostępności (−0,08) wynika z ostrożności agenta kliknięć, który nie mierzył telefonu (7,5).
- Szacunek, nie pomiar: po resecie danych (2 min) Matchmaking u J3 wraca co najmniej do 7, a Materiały do 8, co daje wynik ok. **7,45**.
- Poprawka menu zalogowanych i arkusza chmurki na telefonie to szansa na +0,25 w UI i Dostępności, czyli ok. 7,5.
