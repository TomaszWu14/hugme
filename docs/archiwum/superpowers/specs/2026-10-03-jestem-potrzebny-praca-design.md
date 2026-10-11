# „Jestem potrzebny” + „Praca” – specyfikacja

Data: 2026-10-03 · Status: zaakceptowany (brainstorm 30 pytań) · Budżet: ~8 h, 1 commit (16.), push po zgodzie.

## Cel

Rozszerzenie modułu „Razem z ZD” o dwie zakładki:

1. **Jestem potrzebny / potrzebna** – program, w którym osoby z zespołem Downa (dzieci, młodzież, dorośli)
   pomagają innym: wyprowadzają psy ze schronisk, odwiedzają osoby w hospicjach i DPS, pomagają młodszym
   dzieciom. Osoba z ZD jest tu **dającą**, nie tylko otrzymującą. Hub łączy uczestników z miejscami i potwierdza
   odbyte misje; uczestnik zbiera odznaki w dzienniczku w łatwym tekście.
2. **Praca** – mapa Polski (16 województw) i Małopolski (22 powiaty) z **prawdziwymi** miejscami, w których
   pracują osoby z ZD (ze źródłem), statystyki ze źródłem oraz sekcja **„Poznaj ZD”** (czego oczekują osoby z ZD,
   zainteresowania, mity i fakty, jak rozmawiać) – dla pracodawców, instytucji i rodzin.

Most między nimi: po 5 misjach dzienniczek pokazuje nabyte umiejętności i prowadzi do mapy pracy.

## Decyzje z brainstormu (30 pytań)

| # | Temat | Decyzja |
|---|---|---|
| 1 | Priorytet | wszystkie trzy części; program najgłębiej; uczestnicy w każdym wieku |
| 2 | Nazwa | „Jestem potrzebny / potrzebna” |
| 3 | Kto zgłasza | rodzic/opiekun **lub** sama osoba z ZD (łatwy tekst) |
| 4 | Misje | psy ze schroniska, hospicjum/DPS, pomoc innym dzieciom, + otwarta lista („inne”, Hub zatwierdza) |
| 5 | Oferty | instytucja zgłasza (Hub zatwierdza) **i** rodzic/osoba proponuje miejsce (Hub dzwoni) |
| 6 | Łączenie | Hub łączy – propozycje par, koordynator klika „Połącz” (jak rodzic-przewodnik) |
| 7 | Opieka | zawsze opiekun: rodzic / asystent / buddy z puli Hubu |
| 8 | Uznanie | dzienniczek w łatwym tekście + odznaki + dyplom do wydruku (dyplom = kandydat do cięcia) |
| 9 | Dane o misjach | na serwerze pod pseudonimem; Hub potwierdza „misja odbyła się”; bez diagnozy i danych osobowych |
| 10 | Formularz uczestnika | pseudonim, powiat, grupa wieku, „co lubię” (piktogramy), kiedy mogę, kto towarzyszy, telefon (tylko Hub), zgoda |
| 11 | Oferta miejsca | rodzaj + opis + łatwy tekst + piktogram; kiedy i ile osób; co zapewnia; dla kogo + wymagania |
| 12 | Buddy | osobny formularz „chcę być buddy” (studenci, sąsiedzi, seniorzy) |
| 13 | Zgody | checkbox „jestem opiekunem / mam zgodę opiekuna” + strona „Zasady programu” |
| 14 | Panel Hubu | pary + „Połącz”; zatwierdzanie ofert i propozycji; „Misja odbyła się”; liczby dla ROPS |
| 15 | Most do pracy | dzienniczek po 5 misjach: umiejętności + link do mapy pracy |
| 16 | Dane mapy | **tylko prawdziwe** miejsca z linkiem do źródła; bez danych osobowych pracowników |
| 17 | Mapy | dwie: Polska wg województw + Małopolska wg powiatów; SVG bez JS, klik = link z filtrem |
| 18 | Rodzaje miejsc | otwarty rynek; przedsiębiorstwa społeczne/spółdzielnie; ZAZ; WTZ (oznaczone „droga do pracy”) |
| 19 | Statystyki | liczba osób z ZD w Polsce; wskaźnik zatrudnienia ON (BAEL); liczba ZAZ/WTZ wg województw; liczba miejsc z listy |
| 20 | Dodawanie miejsc | każdy proponuje (formularz), Hub zatwierdza |
| 21 | Poznaj ZD | głosy self-adwokatów (cytaty ze źródłem); zainteresowania liczone na żywo; mity i fakty + jak rozmawiać; wersja ETR (kandydat do cięcia) |
| 22 | Nawigacja | 2 zakładki w menu Razem z ZD: „Jestem potrzebny”, „Praca” (Poznaj ZD = sekcja Pracy); kafle na /razem i na starcie |
| 23 | Scena demo | dorosła osoba z ZD zgłasza się sama (piktogram „psy”) → Hub łączy ze schroniskiem → dzienniczek + odznaka |
| 24 | Seed | ~6 ofert w 4 powiatach, 5 uczestników, 3 buddy, 2 pary, 4 misje odbyte (PRZYKŁAD) |
| 25 | Commity | 1 nowy commit |
| 26 | Cięcia dopuszczalne | dyplom do wydruku; ETR „Poznaj ZD”. **Nie ciąć**: mapy Małopolski, formularza buddy |
| 27 | AI | opis oferty → łatwy tekst (oznaczone, Hub zatwierdza); bez klucza – wskazówki |
| 28 | Materiały | README, docs (ARCHITEKTURA, DANE, KRYTERIA, ROADMAPA, PYTANIA_DO_MENTOROW), slajd + PDF, scena w scenariuszu |
| 29 | Testy | przepływy + spójność danych + axe na nowych widokach |

## Model danych (`core/db.py`)

Wszystkie tabele mają `id`, `created_at`. Bez diagnoz, bez daty urodzenia; telefon tylko w panelu.

- **`volunteers`**: `user_id`, `role` (`uczestnik`|`buddy`), `alias`, `powiat`, `age_group`
  (`dziecko`|`mlodziez`|`dorosly`; buddy: `''`), `interests` (CSV slugów: psy, koty, starsi, dzieci, ogrod, ksiazki,
  sport, muzyka, kuchnia), `days` (CSV: pn, wt, sr, cz, pt, sb, nd, rano, popoludnie), `companion`
  (`rodzic`|`asystent`|`buddy`|`''`), `phone`, `consent` (0/1), `source` (`rodzic`|`latwy-tekst`|`buddy`),
  `status` (`nowe`|`polaczone`|`zamkniete`).
- **`offers`**: `user_id`, `source` (`instytucja`|`rodzic`), `institution`, `mission_kind`
  (`psy`|`hospicjum`|`dzieci`|`inne`), `title`, `body`, `body_easy`, `easy_by_ai` (0/1), `powiat`, `days` (CSV),
  `slots` (int), `for_whom` (CSV grup wieku), `provides` (CSV: opiekun, szkolenie, kamizelka, ubezpieczenie),
  `requirements`, `status` (`nowe`|`zatwierdzone`|`odrzucone`|`zamkniete`).
- **`missions`**: `volunteer_id`, `offer_id`, `buddy_id` (NULL), `done` (int, misje potwierdzone), `status`
  (`polaczone`|`zamkniete`).
- **`workplaces`**: `name`, `kind` (`otwarty`|`spoleczne`|`zaz`|`wtz`), `city`, `voivodeship` (slug z 16),
  `powiat` (tylko Małopolska, NULL poza), `url` (źródło, wymagane), `note`, `checked_at` (data),
  `status` (`zatwierdzone`|`nowe`|`odrzucone`), `user_id` (NULL dla seedu).

## Reguły

**Propozycja pary** (panel): ten sam `powiat`; `mission_kind` ∈ zainteresowania uczestnika wg mapy
psy→psy, hospicjum→starsi, dzieci→dzieci, inne→dowolne; `age_group` ∈ `for_whom`; liczba par oferty < `slots`;
uczestnik `status = nowe`. Sortowanie: liczba wspólnych dni malejąco. Buddy sugerowany, gdy `companion = buddy`:
ten sam powiat + wspólny dzień, `status = nowe`.

**Połącz**: wiersz `missions(status=polaczone)`, uczestnik i buddy → `polaczone`; powiadomienia dla uczestnika,
instytucji (autor oferty) i buddy. **Misja odbyła się**: `done += 1`. **Zamknij**: `missions.status = zamkniete`,
uczestnik wraca do `nowe`.

**Odznaki** (z `SUM(done)` uczestnika): 1 „Pierwsza misja”, 5 „Pomocna dłoń”, 10 „Filar programu”;
tematyczne po 3 misjach jednego rodzaju: „Przyjaciel psów”, „Dobry sąsiad” (hospicjum), „Starszy kolega” (dzieci).
**Umiejętności** od 5 misji łącznie: psy → punktualność, opieka nad zwierzętami; hospicjum → cierpliwość, rozmowa;
dzieci → odpowiedzialność, zabawa w grupie; inne → współpraca.

**Prywatność**: pola tekstowe przez `core/privacy.mask` jak zgłoszenia; telefon tylko w panelu; pseudonimy.

## Ekrany

Menu „Razem z ZD”: + „Jestem potrzebny”, + „Praca”. Kafle na `/razem` i na stronie startowej (sekcja Razem z ZD).

| URL | Treść |
|---|---|
| `/razem/jestem-potrzebny` | co to jest (3 zdania, piktogramy misji); 3 wejścia: „Chcę pomagać” (rodzic), „Ja chcę pomagać” (ETR), „Nasze miejsce potrzebuje pomocy” (instytucja); lista zatwierdzonych ofert wg powiatu (`?powiat=`); link do zasad; skrót do dzienniczka dla zalogowanego |
| `…/zglos` | formularz uczestnika (pkt 10) |
| `…/latwy` | ETR: wybierz obrazek (zainteresowania) → kiedy → kto ze mną → 1 zdanie → Wyślij; `source=latwy-tekst` |
| `…/oferta` | formularz instytucji (pkt 11); `?jako=rodzic` → „Proponuję miejsce” (`source=rodzic`) |
| `…/buddy` | formularz buddy: pseudonim, powiat, kiedy mogę, telefon, zgoda |
| `…/zasady` | zasady programu |
| `…/dzienniczek` | zalogowany: pary, misje w łatwym tekście, odznaki SVG, umiejętności + link do pracy; `…/dzienniczek/dyplom` (wydruk) |
| `/razem/praca` | 4 liczby ze źródłem; mapa Polski (`?woj=`); mapa Małopolski (`?powiat=`); tabele tekstowe pod mapami; lista miejsc (karty: rodzaj, miasto, źródło, data); sekcja „Poznaj ZD”; formularz „Zgłoś miejsce pracy” |
| `/admin/potrzebny` | 1) pary + buddy + „Połącz”; 2) do sprawdzenia: oferty, propozycje miejsc, miejsca pracy; 3) pary połączone: „Misja odbyła się”, „Zamknij”; 4) liczby |

Wpisy trafiają też do skrzynki `/admin` (typ „Jestem potrzebny”). Formularze wymagają konta demo (jak prośby).

## Mapy

`scripts/mapa_svg.py` (jednorazowo): pobiera GeoJSON województw i powiatów z otwartego repozytorium
(dane OSM/GUGiK), rzutuje, upraszcza i zapisuje ścieżki do `data/mapa.py` (`WOJEWODZTWA`, `POWIATY_MALOPOLSKA`:
slug → nazwa, ścieżka, środek etykiety). Atrybucja w stopce `/razem/praca`. Zapas: mapa kafelkowa.
Mapa jest `<svg role="img">` z `<a href="?woj=…">` na regionach, liczbą i kolorem wg skali granatowej (jak heatmapa
trendów); pod mapą tabela region × liczba (alternatywa tekstowa).

## Dane realne (`data/praca.py`)

Każde miejsce: `name, kind, city, voivodeship, powiat, url, note, checked_at`. Źródła: artykuły prasowe i strony
organizacji (kawiarnie, hotele, firmy), wykaz ZAZ (PFRON/województwa), wybrane WTZ Małopolski.
Statystyki: liczba osób z ZD w Polsce (~60 tys.), częstość urodzeń (1:800–1000), wskaźnik zatrudnienia ON w wieku
produkcyjnym (32,5 %, BAEL II kw. 2024), liczba ZAZ/WTZ wg województw – każda z `url`.
Test spójności: `url` niepusty i `https`, region z listy, suma na mapie = długość listy.

## AI (opcjonalne)

`core/ai.easy_text(text)` → wersja w łatwym tekście (krótkie zdania, bez skrótów). W formularzu oferty przycisk
„Uprość tekst (AI)”; wynik trafia do `body_easy` z `easy_by_ai=1`, Hub widzi oznaczenie i może poprawić.
Bez klucza: wskazówki „jak pisać prosto” pod polem.

## Testy

`tests/test_potrzebny.py`: zgłoszenie rodzica i ETR (walidacja, maskowanie, zgoda), oferta → zatwierdzenie →
widoczna na liście, propozycje par (reguły), Połącz (statusy, powiadomienia), Misja odbyła się → odznaka,
Zamknij, buddy, propozycja miejsca pracy → zatwierdzenie → licznik na mapie, uprawnienia (admin only), CSRF.
`tests/test_praca_dane.py`: spójność danych. `scripts/axe_audit.py`: nowe widoki w `PAGES`.

## Materiały

README (tabela modułów, sekcja programu), docs/ARCHITEKTURA (tabele, przepływ), DANE (źródła), KRYTERIA,
ROADMAPA, PYTANIA_DO_MENTOROW (ubezpieczenie NNW, zgody, współpraca ze schroniskami i hospicjami);
slajd „Razem z ZD” + program + mapa (10 slajdów), PDF; scena 30 s w SCENARIUSZ_FILMU.

## Plan czasu (start 17:40) i cięcia

Schema + dane + formularze + strona programu (2 h) → panel i pary (1 h) → dzienniczek i odznaki (45 min) →
mapa + research (1,5 h) → Poznaj ZD + statystyki (45 min) → testy + axe (45 min) → materiały + PDF (45 min) →
commit 16. Po 1:00 w nocy: najpierw dyplom, potem ETR „Poznaj ZD”.
