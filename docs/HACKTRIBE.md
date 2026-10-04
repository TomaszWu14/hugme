# Opisy do formularza HackTribe

Gotowe do wklejenia. Zadanie: **HubMi.pl** (ROPS Kraków). Demo: https://hugme.twapp.pl · Kod: https://github.com/TomaszWu14/hugme

**Jak obejrzeć (dla jury):** najprościej wejdź na https://hugme.twapp.pl/demo i wybierz scenariusz – pasek na górze
poprowadzi Cię krok po kroku (ok. 1,5 min każdy), sam przełącza konta, bez haseł:
- **Rodzic osoby z zespołem Downa – „Jestem potrzebny”**: zgłoszenie syna → Hub łączy go ze schroniskiem →
  odpowiedź Hubu i miejsce w dzienniczku → mapa miejsc pracy i zajęcia.
- **Gmina → Hub**: problem seniorów → „Bus na Telefon” („Bardzo pasuje”) → karta usługi z Pośrednika (Drukuj / PDF) →
  Hub odpowiada, trendy i luki → gmina dostaje odpowiedź.

## Problem

W Małopolsce rozwiązania problemów społecznych już istnieją – w Bibliotece Innowacji ROPS, w organizacjach,
w sąsiednich gminach – ale ludzie, którzy ich potrzebują, o nich nie wiedzą. Mama dziecka z zespołem Downa
nie wie, że gdzie indziej ktoś już poukładał wizyty u kilku specjalistów w jeden dzień. Gmina szuka sposobu na
dojazd seniorów do lekarza, choć inna gmina ma go od dawna. A Hub Innowacji Społecznych nie widzi, gdzie potrzeby
rosną i gdzie brakuje rozwiązań, więc trudno mu zaplanować tematy kolejnych konkursów.

## Solution

Zbudowałem **HugMe – platformę dla HubMi.pl** („Hub + Mi(łopolska)” czyta się jak *hug me* – przytul mnie).
Hasło: **„Twój problem nie zostaje sam”**. Mieszkaniec opisuje problem własnymi słowami, bez urzędowych pojęć,
i w kilka sekund widzi, co już działa w regionie, kto może pomóc i skąd wziąć pieniądze – a przy każdym wyniku
wyjaśnienie, *dlaczego* pasuje. Dopasowanie działa **bez sztucznej inteligencji** (BM25, polski stemming, słownik
pojęć), więc każdy wynik da się wyjaśnić; AI (Claude) tylko je wzbogaca, z dziennym limitem kosztu. Zapisane
zgłoszenie trafia do koordynatora Hubu, który odpowiada i łączy ludzi z autorami rozwiązań. Hub widzi trendy
i **luki** – problemy bez dobrego rozwiązania, czyli gotowe tematy nowych konkursów.

## What's done & goal

**Zrobione (działa na https://hugme.twapp.pl):**
- **7 z 7 modułów z briefu**: matchmaking, zasobnik wiedzy, kreator pomysłów z generatorem wniosków, tester innowacji,
  komunikacja, panel ROPS (z użytkownikami i rolami), pośrednik innowacji dla gmin i NGO. Menu ma nazwy modułów
  z briefu (Szukaj pomocy, Zasobnik wiedzy, Biblioteka innowacji, Tester innowacji, Kreator pomysłów, Pośrednik
  innowacji), a na starcie kafle „7 modułów HubMi”.
- **Trafność dopasowania 16 z 16 w top 3, bez AI** (11 przypadków z danych przykładowych i 5 zdań potocznym językiem
  z symulacji jury). Gdy nic dobrze nie pasuje, aplikacja mówi to wprost, a sprawa trafia do Hubu jako luka.
- **Tryb Podpowiedzi**: ikonka „i” przy polach, filtrach i wykresach mówi, do czego coś służy, jak to czytać i skąd
  się bierze (dane, reguły czy AI). „Przewodnik po tej stronie” prowadzi po ekranie w 4–5 krokach. Przełącznik
  w pasku działa bez JavaScriptu.
- **138 widoków bez naruszeń WCAG 2.1 AA wykrywanych automatycznie** (axe-core, komputer i telefon 320 px), duży
  tekst i wysoki kontrast bez JavaScriptu, font Atkinson Hyperlegible.
- Pogłębiony pilotaż dla rodzin osób z zespołem Downa: plan na 6 etapów życia, rodzic-przewodnik, wzory pism,
  „Strona dla mnie” w tekście łatwym do czytania, program „Jestem potrzebny” (osoby z ZD pomagają innym)
  i mapa prawdziwych miejsc pracy ze źródłami.
- Prywatność: dane osobowe są maskowane przed zapisem i przed AI, wizyty zostają tylko w telefonie.
- Jakość: 313 testów automatycznych, audyt dostępności w CI, automatyczne wdrożenie po zielonych testach.

**Cel:** pilotaż w 2–3 powiatach w obszarze rodzin osób z zespołem Downa – import prawdziwej Biblioteki Innowacji
ROPS (działa już z panelu), logowanie przez login.gov.pl, koordynator Hubu odpowiadający w ciągu 3 dni roboczych
i odsetek dopasowań ocenionych jako „pomocne” z 60% do 75%. Koszt technologii: ok. 75 zł miesięcznie z AI,
wariant bez AI ma pełną funkcjonalność.

## Skills

Projekt zrobiłem sam. Python 3.12, Flask i Jinja bez frameworka JavaScript, SQLite (schemat zgodny z PostgreSQL),
wyszukiwanie BM25 z polskim stemmingiem, dostępność WCAG 2.1 AA (axe-core + Playwright), bezpieczeństwo (CSRF, CSP bez
inline, maskowanie danych osobowych, ochrona przed prompt injection), Docker + Coolify na Hetznerze, GitHub Actions
(testy, audyt dostępności, auto-merge, auto-deploy). Kod pisałem z **Claude Code** jako asystentem programisty:
decyzje produktowe (100 pytań w `BRAINSTORM.md`), dane, testy i weryfikacja są moje, a każdy commit ma jawny
dopisek współautorstwa Claude.
