# Roadmapa

## Etap 0 – po hackathonie (2–4 tygodnie)

- Import prawdziwej Biblioteki Innowacji i Mapy Wyzwań ROPS (mapowanie kolumn w panelu już jest).
- Rozbudowa słownika pojęć z koordynatorami Hubu, na podstawie języka prawdziwych zgłoszeń.
- Testy z użytkownikami: 5 rodzin z obszaru pilotażowego, 5 seniorów, 3 gminy, 3 NGO.
- Decyzja o licencji i przeniesieniu praw (patrz [PYTANIA_DO_MENTOROW](PYTANIA_DO_MENTOROW.md)).

## Etap 1 – pilotaż (3 miesiące)

- Logowanie przez **login.gov.pl** i linkiem e-mail.
- PostgreSQL, kopie zapasowe, monitoring, wysyłka e-maili (SMTP) z kolejki.
- Pilotaż w 2–3 powiatach w obszarze rodzin osób z zespołem Downa, z koordynatorką Hubu.
- Mierniki: czas pierwszej odpowiedzi Hubu (cel ≤ 3 dni robocze), odsetek dopasowań „pomocnych”
  (punkt startowy z danych przykładowych: 60%, cel ≥ 75%), liczba połączeń „problem → innowacja”,
  liczba luk zamienionych na tematy naborów.

## Etap 2 – cały region

- Wszystkie obszary wyzwań, eksperci z sieci partnerów Hubu.
- Integracja z bazą grantową ROPS przez API (`/api/v1`), a nabory i wnioski z generatora trafiają do systemu naborów.
- Lepsze dopasowanie: uczenie wag z ocen „pomocne / niepomocne”, embeddingi jako drugi sygnał obok BM25
  (BM25 zostaje dla wyjaśnialności).
- Rozpoznawanie danych osobowych modelem NER dla języka polskiego jako uzupełnienie wyrażeń regularnych.
- Tekst łatwy do czytania (ETR), napisy do filmów, tryb ciemny.

## Etap 3 – sieć innowacji

- Mapa wdrożeń: która gmina przeniosła którą innowację i z jakim efektem.
- Raporty kwartalne dla zarządu województwa z trendów i luk.
- Otwarcie API dla innych regionalnych hubów innowacji społecznych.
