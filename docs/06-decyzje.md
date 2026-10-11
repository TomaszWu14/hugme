# 06. Dziennik decyzji

Decyzje podjęte przed kodowaniem w ustrukturyzowanej sesji 100 pytań i przed oddaniem projektu (50 pytań).
Źródło każdej decyzji: [archiwum/BRAINSTORM.md](archiwum/BRAINSTORM.md) – numer pytania w nawiasie.
„Rozważane opcje” to warianty zapisane w tym dokumencie, nie dopisane po fakcie.

---

## D-01. Dopasowanie liczą reguły (BM25), AI tylko poszerza zapytanie

- **Kontekst:** matchmaking to moduł obowiązkowy. Mieszkaniec pisze potocznie („mama ma 82 lata, mieszka sama na wsi”),
  a Biblioteka używa języka projektów. Wynik musi być zrozumiały dla koordynatorki Hubu, a AI nie zawsze jest
  dostępne (koszt, klucz, awarie).
- **Rozważane opcje:** (1) AI układa ranking; (2) AI tylko streszcza opis; (3) AI dopisuje słowa kluczowe do zapytania,
  ranking liczy BM25 (pyt. 85). Dla polskiego: biblioteka stemmingu (pystempel) albo własny prosty stemming
  + słownik pojęć (pyt. 28). Embeddingi jako drugi sygnał – zapisane na później w [ROADMAPA](ROADMAPA.md).
- **Decyzja:** opcja 3 – BM25 z prostym stemmingiem i słownikiem pojęć; wynik = 0,5 · BM25 znormalizowane
  + 0,5 · pokrycie słów; AI tylko poszerza zapytanie i dopisuje streszczenie.
- **Dlaczego:** wynik da się wyjaśnić (wspólne słowa i tematy przy każdej karcie), działa bez klucza i bez kosztów,
  jest deterministyczny – można go testować (`tests/test_trafnosc.py`, 16/16 w top 3).
- **Skutki:** trafność zależy od słownika pojęć (`data/slownik.py`), który trzeba rozwijać na prawdziwych
  zgłoszeniach; stemming jest heurystyką (oznaczony w kodzie jako miejsce do wymiany na Morfeusz/pystempel).

## D-02. Dane osobowe maskowane przed zapisem i przed AI; oryginał nie istnieje

- **Kontekst:** opisy dotyczą rodzin, dzieci i niepełnosprawności – ludzie wpisują imiona, telefony, adresy.
- **Rozważane opcje:** zapisać oryginał i maskować tylko przy wyświetlaniu; maskować przed zapisem (pyt. 77);
  maskować także nazwy placówek (pyt. 75 – odrzucone, bo są potrzebne do dopasowania).
- **Decyzja:** jedna funkcja `core/privacy.py` `mask` wywoływana przed każdym zapisem tekstu i w `core/ai.py`
  dla każdego zapytania do modelu; użytkownik widzi, co ukryto (pyt. 76).
- **Dlaczego:** dane, których nie ma, nie wyciekną; jedno miejsce maskowania nie zależy od tego, czy widok
  o nim pamięta.
- **Skutki:** maskowanie regułami ma luki (np. imię bez słowa „syn/córka”); NER dla polskiego zapisany w roadmapie.
  Telefon w programie „Jestem potrzebny” jest celowo jawny (kontakt koordynatorki). Dane o zdrowiu po maskowaniu
  nadal są danymi o zdrowiu – o AI w pilotażu decyduje ROPS po DPIA (decyzja przed oddaniem nr 3).

## D-03. „Luka” jako jawna kategoria, próg 0,35

- **Kontekst:** brief wymaga trendów potrzeb dla Hubu; zgłoszenie bez rozwiązania nie może zniknąć.
- **Rozważane opcje:** pokazać zawsze top 5 bez względu na wynik; próg słabego dopasowania (pyt. 27).
- **Decyzja:** luka = najlepszy wynik < 0,35 **lub** same oceny „niepomocne” **lub** status nadany przez Hub;
  przy wyniku < 0,35 użytkownik dostaje wprost komunikat „nie mamy jeszcze sprawdzonego rozwiązania”.
- **Dlaczego:** uczciwość wobec mieszkańca i dane dla Hubu: luki to kandydaci na tematy naborów.
- **Skutki:** próg jest stałą w `core/domain.py`, dobraną na danych przykładowych – do ponownego sprawdzenia
  na prawdziwych zgłoszeniach.

## D-04. Ocena „pomocne / niepomocne” mierzy, nie uczy

- **Kontekst:** potrzebny jest sprawdzian trafności w działaniu, nie tylko na zestawie testowym.
- **Rozważane opcje:** oceny zmieniają ranking (uczenie); oceny są tylko miernikiem w panelu (pyt. 31).
- **Decyzja:** tylko miernik (odsetek „pomocnych”) i sygnał luki.
- **Dlaczego:** przy kilkudziesięciu zgłoszeniach uczenie byłoby szumem i utrudniłoby wyjaśnienie wyniku.
- **Skutki:** uczenie wag z ocen zapisane w roadmapie (etap 2).

## D-05. Zgłoszenie publiczne dopiero po decyzji Hubu

- **Kontekst:** podobne zgłoszenia innych osób pomagają, ale to treści o prywatnych problemach.
- **Rozważane opcje:** publikacja od razu; publikacja po zatwierdzeniu (pyt. 34–35).
- **Decyzja:** niezatwierdzone zgłoszenie widzi autor, Hub i eksperci; w „podobnych” pokazujemy tylko zatwierdzone.
  Treści pilotażu (miejsca, sprzęt, oferty, miejsca pracy) – tak samo. Moderacja po publikacji (ukryj / przywróć)
  dla pomysłów i wiadomości (decyzja przed oddaniem nr 5).
- **Skutki:** Hub jest wąskim gardłem; aplikacja liczy, ile wątków czeka i od kiedy.

## D-06. Karta usługi bez kwot – wymuszone w kodzie, nie w prompcie

- **Kontekst:** gmina dostaje z Pośrednika kartę wdrożenia; model językowy chętnie podaje kwoty, których nie zna.
- **Rozważane opcje:** prosić model o brak kwot; podawać tylko kategorie kosztów (pyt. 71); realne nazwy źródeł
  finansowania z dopiskiem „sprawdź aktualne nabory” (pyt. 73).
- **Decyzja:** tylko rodzaje kosztów; dodatkowo każda kwota w odpowiedzi AI jest wycinana wyrażeniem regularnym
  (`app/views/posrednik.py` `no_amounts`) i zastępowana „[kwota do wyceny]”.
- **Dlaczego:** zmyślona kwota w dokumencie dla urzędu to ryzyko decyzji na złych danych; reguła w kodzie działa
  także wtedy, gdy model zignoruje polecenie.
- **Skutki:** karta jest mniej konkretna – wycenę robi instytucja.

## D-07. Strony renderowane na serwerze, pełne działanie bez JavaScriptu

- **Kontekst:** użytkownicy to także seniorzy, osoby z niepełnosprawnością intelektualną, starsze telefony,
  czytniki ekranu; wymóg WCAG 2.1 AA.
- **Rozważane opcje:** wyniki na żywo przy pisaniu albo po kliknięciu (pyt. 32); powiadomienia przez odpytywanie JS
  albo przy odświeżeniu (pyt. 56); pełne działanie bez JS (pyt. 88).
- **Decyzja:** Flask + Jinja, bez frameworka JS; JS tylko jako ulepszenie (podpowiedzi, lista wizyt);
  A+ i wysoki kontrast zapamiętywane w ciasteczku.
- **Dlaczego:** mniej elementów do utrzymania (3 zależności produkcyjne), przewidywalna dostępność.
- **Skutki:** każda akcja przeładowuje stronę; brak powiadomień na żywo.

## D-08. SQLite w wolumenie, schemat zgodny z PostgreSQL

- **Kontekst:** prototyp na jednym serwerze, demo dla jury, wdrożenie przez Coolify.
- **Rozważane opcje:** PostgreSQL od początku; SQLite w wolumenie Dockera (pyt. 95).
- **Decyzja:** SQLite, typy kolumn zgodne z PostgreSQL, opisana ścieżka migracji ([ARCHITEKTURA](ARCHITEKTURA.md#wdrożenie)).
- **Skutki:** jeden worker gunicorna; przy większym ruchu konieczna migracja (3 miejsca z funkcjami dat SQLite).

## D-09. Konta demo bez haseł zamiast logowania

- **Kontekst:** jury i oglądający muszą zobaczyć 5 ról w kilka minut; prawdziwe logowanie (login.gov.pl) to
  integracja z Węzłem Krajowym.
- **Rozważane opcje:** przełącznik ról zawsze widoczny (pyt. 17); jedna rola na osobę (pyt. 24).
- **Decyzja:** konta demo bez haseł, ale tylko przy `DEMO_MODE=1` albo `DEMO_ACCOUNTS=1` – bez flagi przełącznik
  zwraca 404; na publicznym demo konta z paska nie do zablokowania, baza odnawia się po 20 min ciszy.
- **Skutki:** prototyp nie nadaje się do prawdziwych danych; role i dekoratory są niezależne od sposobu logowania,
  więc docelowe logowanie nie zmienia kodu ról.

## D-10. Pilotaż w obszarze rodzin osób z zespołem Downa

- **Kontekst:** platforma obsługuje 7 obszarów wyzwań regionu; jeden obszar pogłębiono modułem „Razem z ZD”,
  programem „Jestem potrzebny” i mapą miejsc pracy.
- **Decyzja:** własny wybór autora, nie wymóg briefu. W kodzie obszar ma flagę `pilot: True` (`core/domain.py`).
- **Efekt:** w tym jednym obszarze widać pełną ścieżkę (zgłoszenie → Hub → para, misja, miejsce pracy),
  a nie tylko wyszukiwarkę.
- **Skutki:** najwięcej danych przykładowych i reguł w tym obszarze; pozostałe obszary mają tylko matchmaking
  i Bibliotekę.

## D-11. Licencja MIT

- **Kontekst:** w trakcie hackathonu nie było jasne, czy regulamin HackYeah przenosi prawa majątkowe na organizatora;
  do wyjaśnienia repozytorium nie miało licencji.
- **Rozważane opcje:** licencja otwarta od razu; brak pliku do odpowiedzi mentorów (pyt. 100); docelowo EUPL 1.2
  (licencja zalecana dla administracji).
- **Decyzja:** prawa do kodu zostały przy autorze → licencja MIT (najprostsza dla repozytorium portfolio).
- **Skutki:** każdy może użyć i zmienić kod; przy wdrożeniu w administracji można rozważyć ponowne
  wydanie na EUPL 1.2.
