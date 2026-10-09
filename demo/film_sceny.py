"""Scenariusz filmu HugMe (do 3:00) – jedno źródło dla lektora, napisów, nagrania i docs/SCENARIUSZ_FILMU.md.

Scena: id (nazwa pliku lektora i klucz nagrania), rola (konto demo, na którym nagrywamy; None = gość albo plansza),
podpis (mały napis nad napisami: kto i jaki moduł), ekran (co widać – do docs/SCENARIUSZ_FILMU.md), lektor (tekst czytany = napisy) i opcjonalnie wymowa – ten sam
tekst zapisany tak, żeby syntezator przeczytał go poprawnie („HugMe” → „Hag mi”, „ZD” → „zet de”, liczby słownie).

Długość sceny wyznacza lektor: obraz trwa co najmniej tyle, ile kwestia, plus oddech. Gdy akcja na ekranie
skończy się wcześniej, nagranie czeka (film_nagraj.py), więc żadna kwestia nie jest ucięta ani przyspieszona."""

SCENY = [
    dict(id="00-tytul", rola=None, podpis="",
         ekran="Plansza tytułowa: logo, „HugMe”, „Twój problem nie zostaje sam”.",
         lektor="HugMe – platforma dla Małopolskiego Hubu Innowacji Społecznych.",
         wymowa="Hag mi – platforma dla Małopolskiego Hubu Innowacji Społecznych."),
    dict(id="01-start", rola=None, podpis="Strona startowa",
         ekran="Strona startowa na koncie Anny: hasło i ilustracja, płynne przewinięcie do pola „Co jest trudne? Kogo to dotyczy?”.",
         lektor="Czyta się jak „hug me” – przytul mnie. Bo z problemem nikt nie powinien zostać sam.",
         wymowa="Czyta się jak „hag mi” – przytul mnie. Bo z problemem nikt nie powinien zostać sam."),
    dict(id="02-opis", rola=1, podpis="Anna, mama · Szukaj pomocy",
         ekran="Anna kasuje przykładowy opis, wpisuje własny (z imieniem syna i telefonem), wybiera powiat wadowicki i klika „Znajdź rozwiązania”.",
         lektor="Anna, mama chłopca z zespołem Downa, opisuje problem własnymi słowami – bez urzędowych pojęć. "
                "Wpisuje też imię syna i swój telefon."),
    dict(id="03-wyniki", rola=1, podpis="Anna, mama · Wyniki dopasowania",
         ekran="Wyniki: w opisie „[IMIĘ]” i komunikat o ukrytych danych; karty z Biblioteki Innowacji – „Asystent zdrowia rodziny”, pasek dopasowania i „Dlaczego pasuje”, druga karta.",
         lektor="Zanim cokolwiek trafi do bazy, platforma ukrywa imię i telefon. Potem pokazuje sprawdzone "
                "rozwiązania z Biblioteki Innowacji – na przykład Asystenta zdrowia rodziny, który układa wizyty "
                "u wielu specjalistów. Przy każdym wyniku widać, dlaczego pasuje. Dopasowanie działa bez sztucznej "
                "inteligencji, więc każdy wynik da się wyjaśnić."),
    dict(id="04-zgloszenie", rola=1, podpis="Anna, mama · Zgłoszenie do Hubu",
         ekran="„Zapisz zgłoszenie” → strona zgłoszenia z potwierdzeniem → ocena „Pomocne” przy pierwszym rozwiązaniu.",
         lektor="Anna chce odpowiedzi od człowieka, więc zapisuje zgłoszenie dla Hubu. Ocena „Pomocne” mówi "
                "Hubowi, czy dopasowanie było trafne."),
    dict(id="05-hub", rola=5, podpis="Joanna, koordynatorka Hubu ROPS · Panel Hubu",
         ekran="Konto koordynatorki: Panel Hubu → Skrzynka → zgłoszenie Anny → status „Połączone z rozwiązaniem” → „Zapisz i powiadom autora” → odpowiedź w rozmowie.",
         lektor="Koordynatorka Hubu widzi zgłoszenie w skrzynce. Otwiera je, oznacza jako połączone z rozwiązaniem "
                "i odpisuje Annie. Anna od razu dostaje powiadomienie."),
    dict(id="06-razem", rola=1, podpis="Anna, mama · Razem z ZD",
         ekran="Razem z ZD: „Wasza rodzina nie zostaje sama” → etap „Przedszkole” → plan: „Co teraz ważne” i „Kto pomoże”.",
         lektor="Rodziny osób z zespołem Downa mają też osobny moduł: Razem z ZD. Po wybraniu etapu życia – "
                "na przykład przedszkola – widać, co teraz ważne i kto w Małopolsce pomoże.",
         wymowa="Rodziny osób z zespołem Downa mają też osobny moduł: Razem z zet de. Po wybraniu etapu życia – "
                "na przykład przedszkola – widać, co teraz ważne i kto w Małopolsce pomoże."),
    dict(id="07-potrzebny", rola=1, podpis="Bartek z mamą · „Jestem potrzebny” w łatwym tekście",
         ekran="„Ja chcę pomagać” w łatwym tekście: obrazki psy, sobota, rano, „mama, tata lub opiekun”; pseudonim Bartek, powiat wadowicki, zgoda → „Wyślij”.",
         lektor="Ale osoby z zespołem Downa nie tylko dostają pomoc – same też pomagają. W programie „Jestem "
                "potrzebny” dorosły Bartek wybiera obrazki: lubi psy, ma czas w sobotę rano, a idzie z nim mama."),
    dict(id="08-para", rola=5, podpis="Joanna, koordynatorka Hubu · „Jestem potrzebny”",
         ekran="Jestem potrzebny – panel Hubu: para Bartek ↔ Schronisko dla zwierząt w Wadowicach → „Połącz” → „Misja odbyła się”.",
         lektor="Hub dostaje gotowe propozycje par z tego samego powiatu. Koordynatorka łączy Bartka ze schroniskiem "
                "w Wadowicach, a po spacerze z psami potwierdza misję."),
    dict(id="09-dzienniczek", rola=1, podpis="Bartek z mamą · Dzienniczek",
         ekran="Dzienniczek Bartka: misja w schronisku, odznaka „Pierwsza misja”, zapowiedź umiejętności po 5 misjach.",
         lektor="W dzienniczku Bartka jest już pierwsza odznaka. Po pięciu misjach pojawią się tu umiejętności "
                "przydatne w pracy."),
    dict(id="10-praca", rola=1, podpis="Razem z ZD · Praca",
         ekran="Praca: mapa Polski z miejscami pracy osób z ZD → „małopolskie” → lista miejsc z linkami „Źródło”.",
         lektor="A mapa pokazuje prawdziwe miejsca pracy osób z zespołem Downa – kawiarnie, urzędy, zakłady "
                "aktywności zawodowej – każde ze źródłem."),
    dict(id="11-gmina", rola=3, podpis="Piotr, urzędnik gminy · Biblioteka i Pośrednik innowacji",
         ekran="Konto gminy: karta „Bus na Telefon” → „Dopasuj do mojej gminy” → wypełniony Pośrednik innowacji → „Przygotuj kartę usługi” → karta (zespół, kroki, partnerzy, koszty, finansowanie) → „Drukuj / zapisz jako PDF”.",
         lektor="Z HugMe korzysta też gmina, która szuka sposobu na dowóz seniorów do lekarza. Pośrednik innowacji "
                "bierze sprawdzony Bus na Telefon i przygotowuje kartę usługi: zespół, kroki, partnerów, koszty "
                "i finansowanie – gotową do druku.",
         wymowa="Z Hag mi korzysta też gmina, która szuka sposobu na dowóz seniorów do lekarza. Pośrednik innowacji "
                "bierze sprawdzony Bus na Telefon i przygotowuje kartę usługi: zespół, kroki, partnerów, koszty "
                "i finansowanie – gotową do druku."),
    dict(id="12-trendy", rola=5, podpis="Joanna, koordynatorka Hubu · Trendy i luki",
         ekran="Trendy potrzeb i luki: zmiany wg obszaru, mapa powiat × obszar, luki z plakietką „Kandydat na konkurs”.",
         lektor="Hub widzi, w jakich obszarach i powiatach Małopolski przybywa zgłoszeń. Problemy bez dobrego "
                "rozwiązania stają się lukami – tematami nowych konkursów."),
    dict(id="13-dostepnosc", rola=1, podpis="Dostępność · WCAG 2.1 AA",
         ekran="Strona startowa: „A+ większy tekst”, „Wysoki kontrast”, przejście klawiszem Tab z widocznym fokusem.",
         lektor="HugMe jest dla wszystkich: większy tekst, wysoki kontrast, obsługa klawiaturą. Automatyczny audyt "
                "nie wykrył naruszeń dostępności w 138 widokach.",
         wymowa="Hag mi jest dla wszystkich: większy tekst, wysoki kontrast, obsługa klawiaturą. Automatyczny audyt "
                "nie wykrył naruszeń dostępności w stu trzydziestu ośmiu widokach."),
    dict(id="14-koniec", rola=None, podpis="",
         ekran="Plansza końcowa: hugme.twapp.pl, github.com/TomaszWu14/hugme, kod QR do demo.",
         lektor="HugMe. Twój problem nie zostaje sam.",
         wymowa="Hag mi. Twój problem nie zostaje sam."),
]


def wymowa(s):
    return s.get("wymowa") or s["lektor"]
