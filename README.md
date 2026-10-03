# HugMe — platforma dla HubMi.pl

> **Twój problem nie zostaje sam.**

Prototyp platformy dla **Małopolskiego Hubu Innowacji Społecznych** (Regionalny Ośrodek Polityki Społecznej
w Krakowie), przygotowany na **HackYeah 2026**, zadanie **HubMi.pl**.

## Gra słów

**Hub + Mi**(łopolska) czyta się jak angielskie ***hug me*** – „przytul mnie”. Tak ma działać platforma:
mieszkaniec z problemem nie trafia do urzędu, tylko do kogoś, kto go „obejmuje” i łączy z rozwiązaniem
i ludźmi. Motyw graficzny to **splot**: nici problemów, ludzi i rozwiązań łączą się w węzeł w kształcie serca.

## Problem

W Małopolsce działa wiele dobrych innowacji społecznych, ale ludzie, którzy ich potrzebują, o nich nie wiedzą.
Gmina obok nie wie, że ktoś już rozwiązał jej problem. Hub nie widzi, gdzie brakuje rozwiązań.
HugMe łączy **zgłaszane problemy** z **istniejącymi innowacjami, ludźmi i finansowaniem**, a Hubowi pokazuje
**trendy i luki**, czyli tematy na nowe konkursy.

Obszar pilotażowy w danych przykładowych to **rodziny osób z zespołem Downa**: wizyty u wielu lekarzy,
integracja, praca po szkole, oferty pomocy i odciążenie rodziców. Platforma działa dla każdego wyzwania
regionu, więc w danych są też seniorzy, samotność, wykluczenie cyfrowe, zdrowie psychiczne, wieś i transport
oraz współpraca międzysektorowa.

## Moduły z briefu i gdzie są w aplikacji

| Moduł z briefu | Gdzie w aplikacji | Kod |
|---|---|---|
| **Matchmaking społeczny** (obowiązkowy) | `/` → `/wyniki` → zapis `/zgloszenie/<id>`: dopasowania z trafnością i „dlaczego pasuje”, podobne zgłoszenia, poradniki, eksperci; ocena „pomocne / niepomocne” | `core/match.py`, `core/catalog.py`, `app/views/public.py` |
| **Zasobnik wiedzy** | `/wiedza` (karty wyzwań), `/biblioteka` (filtry, filmy), `/wiedza/material/<id>`, `/wiedza/sciezka-rodziny` | `app/views/wiedza.py` |
| **Trendy potrzeb** (tylko admin) | `/admin/trendy`: obszar miesiąc do miesiąca, mapa powiat × obszar | `app/views/admin.py` |
| **Kreator pomysłów** | `/pomysly/nowy` (fiszka) → `/pomysly/<id>/kanwa` → asystent → `/pomysly/<id>/wniosek/<nabór>` (tylko w trakcie naboru) | `app/views/kreator.py` |
| **Tester innowacji** | `/biblioteka/<id>#tester`: zgłoszenie do testu, ocena 1–5, usprawnienie (powiadomienie Hubu) | `app/views/wiedza.py` |
| **Komunikacja** | wątki przy zgłoszeniu, pomyśle i innowacji, `/powiadomienia`, kolejka e-mail, obserwowanie obszarów, `/ekspert` | `app/views/komunikacja.py`, `core/notify.py` |
| **Panel administratora (ROPS)** | `/admin`: skrzynka, wątki bez odpowiedzi, statusy, edycja i import Biblioteki, nabory, luki, poczta, eksport CSV | `app/views/admin.py` |
| **Pośrednik innowacji** (AI) | `/posrednik` → karta usługi (opis, odbiorcy, zespół, kroki, partnerzy, koszty bez kwot, finansowanie, mierniki, ryzyka) | `app/views/posrednik.py` |
| API dla integracji | `POST /api/v1/dopasuj`, `GET /api/v1/innowacje` | `app/views/api.py` |

Role demo, przełączane bez haseł w pasku „Tryb demo”: mieszkanka-rodzic, organizacja pozarządowa, gmina,
ekspert, koordynatorka ROPS. Docelowe logowanie przez **login.gov.pl** albo link e-mail opisuje
[docs/ARCHITEKTURA.md](docs/ARCHITEKTURA.md#logowanie).

## Najważniejsze zasady

- **Matchmaking działa bez AI**: BM25, polski stemming, słownik pojęć (np. lekarz/wizyta/kardiolog → „zdrowie”),
  premia za pokrycie słów i wyjaśnialne wyniki. Trafność top 3 na zestawie testowym: **11/11**.
- **AI jest opcjonalne** (Claude Haiku przez `ANTHROPIC_API_KEY`). Wzbogaca analizę opisu, asystenta pomysłu,
  generator wniosków i Pośrednika. Bez klucza albo przy awarii działają reguły i szablony.
  Treści od AI są zawsze oznaczone w interfejsie.
- **Prywatność**: PESEL, telefon, e-mail, adres, kod pocztowy, imię po „syn/córka” i nazwisko po „dr” są maskowane
  **przed** zapisem i przed AI. Wszystkie dane są fikcyjne i oznaczone jako „PRZYKŁAD”.
- **Dostępność (WCAG 2.1 AA)**: audyt axe-core 72/72 widoków bez naruszeń (desktop i 320 px),
  przyciski A+ i wysokiego kontrastu działają bez JS, cele dotykowe mają co najmniej 44 px.
- **Bezpieczeństwo**: CSRF, CSP bez zewnętrznych skryptów i bez stylów inline, ciasteczka HttpOnly/SameSite,
  walidacja i role sprawdzane na serwerze.

## Uruchomienie

```bash
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
flask --app app:create_app run                       # http://127.0.0.1:5000
```

Przy pierwszym starcie baza `instance/hugme.db` tworzy się sama i ładuje dane przykładowe.
Reset danych: usuń plik bazy. AI włączysz zmienną `ANTHROPIC_API_KEY` (przykład w `.env.example`).

**Testy i audyt:**

```bash
pytest                                   # 80 testów: ścieżki, role, CSRF, prywatność, trafność
python -m playwright install chromium
python scripts/axe_audit.py --zrzuty     # raport docs/WCAG_RAPORT.md + docs/zrzuty/
```

**Docker / Coolify (Hetzner VPS):**

```bash
SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") docker compose up -d --build
```

Baza SQLite leży w wolumenie `hugme-data`. Healthcheck: `GET /zdrowie`. W Coolify wystarczy wskazać
repozytorium (build z `Dockerfile`), ustawić `SECRET_KEY` i opcjonalnie `ANTHROPIC_API_KEY`, a potem podpiąć domenę.

## Scenariusz demo (5 minut)

1. **Start, gość.** Pole „Co jest trudne? Kogo to dotyczy?” ma już wpisany przykład o wizytach u wielu specjalistów.
   Dopisz „mój syn Kacper, tel. 600 123 456” i kliknij **Znajdź rozwiązania**.
2. **Wyniki.** Imię i telefon są ukryte, z łagodnym komunikatem. Na górze „Asystent zdrowia rodziny” z oceną
   „Bardzo pasuje” i uzasadnieniem (wspólne słowa i tematy). Obok podobne zgłoszenia, poradniki i eksperci.
3. **Zapisz zgłoszenie.** Wybierz konto mieszkanki: opis zostaje zachowany, powstaje wątek z Hubem,
   a koordynatorka dostaje powiadomienie. Oceń dopasowanie „Pomocne”.
4. **Przełącz na Koordynatorkę ROPS.** Skrzynka pokazuje nowe zgłoszenie. Ustaw status „Połączone z rozwiązaniem”,
   opublikuj i odpisz w wątku. Mieszkanka dostaje powiadomienie.
5. **Gmina, Pośrednik.** Opisz kontekst gminy (seniorzy, 5 sołectw, dojazd do przychodni) i dostaniesz kartę
   usługi wzorowaną na „Busie na telefon”, z kosztami bez kwot.
6. **NGO, Kreator.** Pomysł „Weekendowy klub” → **Zapytaj asystenta** → **Przygotuj wniosek** (trwa nabór) → złóż.
7. **Admin, Trendy i Luki.** Mapa powiat × obszar, porównanie miesiąc do miesiąca, luki jako kandydaci na konkursy,
   eksport CSV.
8. **Dostępność.** Włącz **A+** i **Wysoki kontrast**, przejdź stronę klawiszem Tab od linku „Przejdź do treści”.

## Dokumentacja

[ARCHITEKTURA](docs/ARCHITEKTURA.md) · [DANE](docs/DANE.md) · [WCAG](docs/WCAG.md) ·
[Raport axe](docs/WCAG_RAPORT.md) · [KOSZTY](docs/KOSZTY.md) · [KRYTERIA](docs/KRYTERIA.md) ·
[ROADMAPA](docs/ROADMAPA.md) · [PYTANIA DO MENTORÓW](docs/PYTANIA_DO_MENTOROW.md) ·
[SCENARIUSZ FILMU](docs/SCENARIUSZ_FILMU.md) · [makiety](docs/zrzuty/) · decyzje projektowe: [BRAINSTORM.md](BRAINSTORM.md)

## Stos

Python 3.12, Flask, Jinja, SQLite (schemat zgodny z PostgreSQL), bez frameworków JS, Docker. Jedyne zależności
produkcyjne: `flask`, `gunicorn`, `anthropic`.

---
Wszystkie osoby, organizacje, innowacje i zgłoszenia w prototypie są **fikcyjne**. Licencja zostanie dodana
po decyzji o przeniesieniu praw (patrz [docs/PYTANIA_DO_MENTOROW.md](docs/PYTANIA_DO_MENTOROW.md)).
