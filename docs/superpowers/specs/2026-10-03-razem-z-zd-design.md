# Moduł „Razem z ZD” – specyfikacja

Data: 2026-10-03 · Status: zaakceptowany wariant A · Budżet: 3–4 h kodu + materiały, 2 commity, push po zgodzie.

## Cel

Osobny moduł HugMe dla osób z zespołem Downa i ich rodzin – pogłębienie obszaru pilotażowego.
Odpowiada na cztery problemy wskazane przez autora: **wizyty i terminy**, **zmęczenie rodziców**,
**formalności i prawa**, **dorosłość i „co po nas”**. Jury widzi go jako jakość pilotażu (nie jako 8. moduł z briefu).

Użytkownicy: **rodzic/opiekun** (główny) i **dorosła osoba z ZD** (widok w tekście łatwym do czytania).
Efekt „wow” na demo: **plan według etapu życia**.

## Decyzje (z rundy pytań)

| Temat | Decyzja |
|---|---|
| Nazwa / miejsce | „Razem z ZD”; zakładka w menu + kafel na stronie startowej i na karcie obszaru `rodziny-zd` |
| Etapy | 6: diagnoza i niemowlę (0–1), maluch (1–3), przedszkole (3–6), szkoła (7–15), młodzież (16–24), dorosłość (25+) |
| Zapamiętanie etapu | ciasteczko (nie localStorage – działa bez JS); brak daty urodzenia i danych dziecka |
| Kontrole zdrowotne | lista „o co zapytać lekarza” wg etapu, z dopiskiem „to nie porada medyczna – PRZYKŁAD” |
| Kalendarz wizyt | **wyłącznie w przeglądarce** (localStorage); bez JS – lista do wydruku; zero danych o zdrowiu na serwerze |
| Teczka dokumentów | nie; tylko lista „co mieć przy sobie” |
| Dzień Specjalistów | przycisk „chcę w moim powiecie” → prośba w skrzynce + licznik wg powiatu w panelu |
| Przyjazne miejsca | lista wg powiatu; rodzice polecają, Hub zatwierdza; bez oceniania lekarzy z nazwiska |
| „Co po nas” | osobna karta |
| Prawa i świadczenia | kreator tak/nie → instytucje i dokumenty; bez kwot i progów |
| Wzory pism | 2–3 wzory, POST → wydruk, bez zapisu; AI opcjonalnie dopisuje uzasadnienie (oznaczone) |
| Rodzic-przewodnik | prośby „szukam” / „chcę być”; pseudonimy; łączy Hub (propozycje par: ten sam powiat i etap) |
| Wytchnienie | formularz prośby (kiedy, ile godzin, powiat) → Hub; bez grafiku |
| Wydarzenia | lista wg powiatu, zapis jednym kliknięciem, przypomnienie w powiadomieniach |
| Forum | nie |
| Wymiana sprzętu | prosta tablica oddam/przyjmę, moderowana, kontakt przez Hub |
| ETR | widok „Moje sprawy” + streszczenie każdego etapu |
| Zgłoszenie osoby z ZD | wybór piktogramu + jedno zdanie → zwykły matchmaking (`/szukaj`) |
| Czytanie na głos | Web Speech API (pl-PL) jako ulepszenie; bez JS przycisk ukryty |
| Piktogramy | SVG spójne z obecnymi ikonami, zawsze z podpisem |
| Dodatki | rodzeństwo, porównanie typów szkół, pytania do stowarzyszenia (PYTANIA_DO_MENTOROW) |
| Rozszerzalność | treści w strukturze „grupa → etapy” (dziś tylko `zd`), kolejne grupy bez zmian w kodzie |
| Panel Hubu | prośby w skrzynce + widok `/admin/razem` |
| Materiały | 1 slajd, ~20 s w filmie, README, KRYTERIA, zrzuty |
| Cięcia przy braku czasu | sprzęt → czytanie na głos → wydarzenia → pisma |

## Architektura

Nowe pliki (wzorem istniejących modułów):

- `app/views/razem.py` – blueprint `razem` (strony rodzica, osoby z ZD, formularze).
- `data/razem.py` – treści: `GROUPS = {"zd": {...}}` z etapami (`slug`, nazwa, wiek, piktogram, „co teraz ważne”,
  „o co zapytać lekarza”, dokumenty/terminy, streszczenie ETR, tagi innowacji), kreator praw (pytania → instytucje),
  wzory pism (pola + szablon), porównanie szkół, rodzeństwo, „co po nas”, teksty „Moje sprawy”.
- `app/templates/razem/*.html` – szablony modułu; `app/templates/admin/razem.html`.
- `app/static/js/razem.js` – kalendarz wizyt (localStorage) i „Przeczytaj na głos”. Ładowany tylko na stronach modułu
  (`script-src 'self'` – zgodne z CSP).
- Piktogramy: rozszerzenie makra `icon()` w `_macros.html`.

Zmiany w istniejących plikach: `core/db.py` (2 tabele), `data/seed.py` + `seed_data.py` (dane przykładowe),
`app/__init__.py` (rejestracja), `base.html` (menu), `home.html` i `obszar.html` (kafel), `admin.py` (skrzynka +
widok `/admin/razem`), `hugme.css` (style modułu).

## Dane

```sql
family_requests (id, user_id, kind, powiat, stage, alias, title, body, status, matched_with, created_at)
  kind   ∈ przewodnik-szukam | przewodnik-oferuje | wytchnienie | dzien-specjalistow | miejsce | sprzet-oddam | sprzet-przyjme
  status ∈ nowe | zatwierdzone | odrzucone | polaczone | zamkniete
events (id, title, powiat, date, place, body, created_at)
event_signups (event_id, user_id, created_at, PRIMARY KEY(event_id, user_id))
```

Miejsca i ogłoszenia sprzętu są publiczne tylko ze statusem `zatwierdzone`. Każdy tekst przechodzi przez
`privacy.mask()`. Pseudonim (`alias`) zamiast nazwy konta w publicznych listach.

Dane przykładowe: 6 miejsc (zatwierdzone), 1 polecenie oczekujące, 4 ogłoszenia sprzętu, 4 wydarzenia,
3 przewodników „oferuję” i 2 rodziny „szukam” (w tym para do połączenia w powiecie wadowickim), 1 prośba o wytchnienie,
6 prośb o Dzień Specjalistów w kilku powiatach. Wszystko fikcyjne, oznaczone „PRZYKŁAD”.

## Przepływy

1. **Plan:** `/razem` → wybór etapu (POST → ciasteczko `razem_etap`) → `/razem/etap/<slug>`.
2. **Prośba** (przewodnik/wytchnienie/dzień/miejsce/sprzęt): wymaga konta (jak reszta HugMe, przekierowanie
   na `/konto`) → walidacja (białe listy powiatu i etapu, długości) → maskowanie → `family_requests` →
   `notify_admins` → komunikat sukcesu.
3. **Łączenie przewodnika:** `/admin/razem` pokazuje pary (szukam ↔ oferuję, ten sam powiat; ten sam etap = wyżej)
   → „Połącz” ustawia `polaczone` + `matched_with` po obu stronach → powiadomienia do obu rodzin.
4. **Moderacja:** zatwierdź/odrzuć miejsce lub ogłoszenie → autor dostaje powiadomienie.
5. **Wydarzenia:** zapis/wypis (POST) → powiadomienie „zapisano”.
6. **Pisma:** formularz (POST) → wydruk z danymi z formularza; nic nie zapisujemy. „Dopisz uzasadnienie (AI)” –
   `ai.ask()` z fallbackiem na zdanie szablonowe; oznaczenie AI.
7. **Prawa:** formularz GET z odpowiedziami tak/nie (tylko wartości z białej listy, bez danych osobowych) → lista instytucji.
8. **Moje sprawy:** piktogram + zdanie → POST do istniejącego `/szukaj` (opis = „[kategoria]: zdanie”).

## Obsługa błędów

Błędy walidacji: podsumowanie błędów + `aria-invalid`, kod 422 (jak w Kreatorze). Nieznany etap/rodzaj → 404/400.
AI niedostępne → szablon. Brak JS → kalendarz jako lista do wydruku, brak przycisku czytania.

## Testy

- każda strona modułu renderuje się (gość i role), etap w ciasteczku zmienia plan;
- prośby: walidacja, maskowanie, powiadomienie Hubu, wymagane konto;
- publiczne listy pokazują tylko `zatwierdzone`; moderacja tylko dla admina;
- łączenie przewodnika ustawia status po obu stronach i powiadamia obie rodziny; rola admina sprawdzana na serwerze;
- pisma: POST, brak zapisu w bazie, dane nie w URL; kreator praw zwraca instytucje;
- wydarzenia: zapis i wypis;
- audyt axe (`scripts/axe_audit.py`) rozszerzony o nowe widoki – desktop i 320 px bez naruszeń.

## Poza zakresem

Forum, grafik opieki wytchnieniowej, teczka dokumentów, kalkulator świadczeń, prawdziwe nazwy placówek,
synchronizacja kalendarza między urządzeniami.
