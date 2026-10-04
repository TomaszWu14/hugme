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
- Zrzuty „przed”: `audit/iteracje/00-przed/`. Pliki 01–17 to ekrany publiczne (Juror 1a), 30–51 to ekrany po zalogowaniu i panel (Juror 1b). Zrzuty i skrypty pozostałych agentów są w scratchpadzie sesji (`scratchpad/juror2/`, `j3/`, `klik/`, `trafnosc/`).
- Porównanie z Trash Fairy i wzorce do przeniesienia: `audit/WZORCE.md`.
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

_(Etap 4)_

## Czego nie zdążono i jak o tym mówić

_(Etap 4)_

## 10 najtrudniejszych pytań

_(Etap 4)_

## 5 zdań do prezentacji

_(Etap 4)_

## Oceny końcowe (przed/po)

_(Etap 4)_
