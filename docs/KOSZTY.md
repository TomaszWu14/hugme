# Koszty utrzymania i potrzebne zasoby

Wymóg formalny regulaminu. Kwoty to **szacunki na październik 2026**; ceny usług chmurowych i stawki
wynagrodzeń należy zweryfikować przed wdrożeniem.

## 1. Hosting

| Pozycja | Wariant pilotażowy | Wariant regionalny |
|---|---|---|
| Serwer | Hetzner VPS 2 vCPU / 4 GB (np. CX22) | 4 vCPU / 8 GB + osobny PostgreSQL |
| Koszt miesięcznie | ok. **5–10 €** | ok. **25–50 €** |
| Kopie zapasowe | snapshoty dostawcy + zrzut bazy co noc: ok. 1–3 € | ok. 5–10 € |
| Domena + certyfikat | domena ok. 50–100 zł rocznie, certyfikat Let's Encrypt bez opłat | to samo |
| Panel wdrożeń | Coolify (open source) na tym samym serwerze, bez opłat | to samo |

Aplikacja to jeden kontener. Jedyne zależności produkcyjne to `flask`, `gunicorn` i `anthropic`,
bez osobnego frontendu i bez płatnych usług SaaS.

## 2. AI (opcjonalne): Claude Haiku 4.5

Cennik: **1 USD za milion tokenów wejścia, 5 USD za milion tokenów wyjścia**.

| Funkcja | Tokeny (wejście / wyjście) | Koszt jednego użycia |
|---|---|---|
| Analiza opisu w matchmakingu | ok. 700 / 150 | ok. **0,0015 USD** (0,6 gr) |
| Asystent pomysłu | ok. 900 / 700 | ok. **0,0044 USD** (1,8 gr) |
| Podpowiedź do wniosku | ok. 600 / 500 | ok. **0,0031 USD** (1,3 gr) |
| Karta usługi (Pośrednik) | ok. 800 / 1200 | ok. **0,0068 USD** (2,8 gr) |

**Miesięcznie** (założenie pilotażu: 2000 wyszukiwań, 300 rozmów z asystentem, 150 podpowiedzi do wniosków,
100 kart Pośrednika): ok. 3,0 + 1,3 + 0,5 + 0,7 = **ok. 5,5 USD (ok. 25 zł)**.
Skala całego regionu (×10): ok. **55 USD (ok. 230 zł)** miesięcznie.
Cache odpowiedzi w aplikacji i limit 8 s na zapytanie ograniczają koszt awarii i powtórzeń.

## 3. Ludzie: koszt, który naprawdę się liczy

Technologia jest tania. Wartość platformy zależy od tego, czy **ktoś odpowiada ludziom**.

| Rola | Wymiar | Zadania |
|---|---|---|
| Koordynator/ka Hubu (ROPS) | **1 etat** | odpowiedzi na zgłoszenia (cel: 3 dni robocze), łączenie z innowacjami, statusy, nabory |
| Moderacja treści | **0,25–0,5 etatu** (może być w ramach etatu koordynatora w pilotażu) | zatwierdzanie zgłoszeń przed publikacją, kontrola danych osobowych, wątki |
| Eksperci dziedzinowi | umowy zlecenia / wolontariat, ok. 5–10 godzin miesięcznie na obszar | odpowiedzi w wątkach, konsultacje pomysłów |
| Utrzymanie techniczne | ok. **4–8 godzin miesięcznie** (usługa zewnętrzna albo dział IT) | aktualizacje, kopie, monitoring |
| Aktualizacja Biblioteki | w ramach etatu koordynatora | import i edycja innowacji (panel, bez programisty) |

Szacunek kosztu etatu koordynatora z kosztami pracodawcy w jednostce samorządowej: ok. **9–11 tys. zł miesięcznie**
(do weryfikacji wg siatki płac ROPS).

## 4. Podsumowanie miesięczne (pilotaż)

| Wariant | Technologia | Ludzie | Razem |
|---|---|---|---|
| **Z AI** | hosting ok. 50 zł + AI ok. 25 zł = **ok. 75 zł** | 1–1,5 etatu + eksperci | **ok. 10–13 tys. zł** |
| **Bez AI** | hosting ok. 50 zł | jak wyżej | **ok. 10–13 tys. zł** (AI to < 1% kosztu) |

**Wariant bez AI** działa w pełni: matchmaking BM25, asystent regułowy, generator z fiszki i kanwy,
Pośrednik z szablonu. Wyłączenie AI to usunięcie jednej zmiennej środowiskowej i nie wymaga zmian w kodzie.

## 5. Koszty jednorazowe (wdrożenie produkcyjne)

- integracja z login.gov.pl (Węzeł Krajowy): ok. 10–20 dni pracy programisty;
- migracja na PostgreSQL i import Biblioteki ROPS: ok. 3–5 dni;
- audyt dostępności z udziałem użytkowników i deklaracja dostępności: ok. 5–10 dni;
- DPIA i umowa powierzenia z dostawcą AI: po stronie inspektora ochrony danych ROPS.
