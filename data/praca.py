"""Zakładka „Praca”: PRAWDZIWE miejsca, w których pracują osoby z zespołem Downa (każde ze źródłem), statystyki
ze źródłem i treści „Poznaj ZD”. Bez danych osobowych pracowników – tylko miejsca i publiczne artykuły."""
from data.mapa import POWIATY_MALOPOLSKA, WOJEWODZTWA

VOIVODESHIPS = {slug: name for slug, name, *_ in WOJEWODZTWA}
POWIAT_SLUGS = {name: slug for slug, name, *_ in POWIATY_MALOPOLSKA}

# slug → (etykieta, krótki opis, klasa koloru)
KINDS = {
    "otwarty": ("Otwarty rynek pracy", "urząd, firma, hotel, sklep – zwykłe miejsce pracy", "wp--otwarty"),
    "spoleczne": ("Przedsiębiorstwo społeczne", "kawiarnia, spółdzielnia socjalna – praca z trenerem", "wp--spoleczne"),
    "zaz": ("ZAZ – zakład aktywności zawodowej", "zatrudnienie chronione dla osób ze znaczną niepełnosprawnością", "wp--zaz"),
    "wtz": ("WTZ – warsztat terapii zajęciowej", "to nie praca, ale przygotowanie do niej", "wp--wtz"),
}
KIND_LABELS = {k: v[0] for k, v in KINDS.items()}

_ZAZ_MP = "https://bip.malopolska.pl/e,pobierz,get.html?id=1757266"  # wykaz ZAZ Małopolskiego Urzędu Wojewódzkiego
# (nazwa, rodzaj, miasto, województwo, powiat (Małopolska) albo None, url źródła, notatka, data sprawdzenia)
WORKPLACES = [
    ("Społeczna Kaffka", "spoleczne", "Kraków", "malopolskie", "Kraków",
     "https://stacja7.pl/z-kraju/w-krakowie-rusza-pierwsza-kawiarnia-zatrudniajaca-osoby-z-zespolem-downa/",
     "Kawiarnia zatrudniająca osoby z zespołem Downa (ul. Na Kozłówce 25); baristów wspierają trenerzy pracy. "
     "Ta sama organizacja prowadzi sklep z rękodziełem „Zręczne Drobiazgi”.", "2026-10-03"),
    ("Urząd Marszałkowski Województwa Małopolskiego", "otwarty", "Kraków", "malopolskie", "Kraków",
     "https://krakow.tvp.pl/89567960/osoby-z-zespolem-downa-pracuja-w-urzedzie-i-kawiarni",
     "Osoby z zespołem Downa porządkują, kopiują i archiwizują dokumenty w urzędzie.", "2026-10-03"),
    ("Urząd Miejski w Gdańsku", "otwarty", "Gdańsk", "pomorskie", None,
     "https://tvn24.pl/pomorze/gdansk-pierwsza-osoba-z-zespolem-downa-zatrudniona-w-urzedzie-miejskim-ra989076-2314936",
     "Pierwsza osoba z zespołem Downa zatrudniona w urzędzie miejskim – prace biurowe na pół etatu.", "2026-10-03"),
    ("Cafe Równik", "spoleczne", "Wrocław", "dolnoslaskie", None,
     "https://gazetawroclawska.pl/jedyna-taka-kawiarnia-niepelnosprawni-kelnerzy-juz-serwuja-kawe-w-cafe-rownik-zdjecia/ar/13282305",
     "Klubokawiarnia (ul. Jedności Narodowej 47): kelnerzy, barmani i pomoc kuchenna to osoby z niepełnosprawnością "
     "intelektualną, w tym z zespołem Downa.", "2026-10-03"),
    ("Kawiarnia Pożyteczna", "spoleczne", "Warszawa", "mazowieckie", None,
     "https://rampa.net.pl/kawiarnia-zatrudniajaca-osoby-z-zespolem-downa/",
     "Kawiarnia prowadzona razem z rodzicami; pracuje w niej siedem osób z niepełnosprawnością intelektualną.", "2026-10-03"),
    ("cieKAWA kawiarnia", "spoleczne", "Gdańsk", "pomorskie", None,
     "https://www.gdansk.pl/wiadomosci/Ruszyla-cieKAWA-kawiarnia-Chodz-na-kawe-ze-spolecznym-przeslaniem,a,151879",
     "Spółdzielnia socjalna – trzon zespołu baristów stanowią osoby z niepełnosprawnością intelektualną.", "2026-10-03"),
    ("Dobra Kawiarnia", "spoleczne", "Poznań", "wielkopolskie", None,
     "https://opoka.org.pl/biblioteka/P/PS/pk201649_niepelnosprawni",
     "Ośmioro pracowników z niepełnosprawnością intelektualną na stałych umowach o pracę.", "2026-10-03"),
    ("Pensjonat i Restauracja „U Pana Cogito” (ZAZ)", "zaz", "Kraków", "malopolskie", "Kraków", _ZAZ_MP,
     "Zakład aktywności zawodowej Stowarzyszenia Rodzin „Zdrowie Psychiczne”.", "2026-10-03"),
    ("ZAZ „Pensjonat na Wzgórzach”", "zaz", "Kraków", "malopolskie", "Kraków", _ZAZ_MP,
     "Zakład aktywności zawodowej Stowarzyszenia „Szansa”.", "2026-10-03"),
    ("ZAZ Bonifraterskiej Fundacji Dobroczynnej", "zaz", "Konary (Świątniki Górne)", "malopolskie", "krakowski", _ZAZ_MP,
     "Zakład aktywności zawodowej w Konarach.", "2026-10-03"),
    ("Zakład Produkcyjny Stowarzyszenia „Piast” (ZAZ)", "zaz", "Wola Rzędzińska", "malopolskie", "tarnowski", _ZAZ_MP,
     "Zakład aktywności zawodowej Stowarzyszenia Kulturalno-Oświatowego „Piast” im. W. Witosa.", "2026-10-03"),
    ("ZAZ Stowarzyszenia Pomocy „Szansa”", "zaz", "Witowice (Charsznica)", "malopolskie", "miechowski", _ZAZ_MP,
     "Zakład aktywności zawodowej w Witowicach.", "2026-10-03"),
    ("ZAZ „Opoka”", "zaz", "Chechło", "malopolskie", "olkuski", _ZAZ_MP,
     "Zakład aktywności zawodowej Spółdzielni Socjalnej „Opoka”.", "2026-10-03"),
    ("ZAZ im. Matki Bożej Fatimskiej", "zaz", "Stróże", "malopolskie", "nowosądecki", _ZAZ_MP,
     "Zakład aktywności zawodowej Fundacji Pomocy Osobom Niepełnosprawnym.", "2026-10-03"),
    ("Powiatowy ZAZ w Nawojowej", "zaz", "Nawojowa", "malopolskie", "nowosądecki", _ZAZ_MP,
     "Zakład aktywności zawodowej prowadzony przez Powiat Nowosądecki.", "2026-10-03"),
    ("ZAZ „Słoneczne Wzgórze”", "zaz", "Tarnów", "malopolskie", "Tarnów", _ZAZ_MP,
     "Centrum Rehabilitacji Społecznej i Zawodowej Gminy Miasta Tarnowa.", "2026-10-03"),
    ("Powiatowy ZAZ w Łysej Górze", "zaz", "Łysa Góra", "malopolskie", "brzeski", _ZAZ_MP,
     "Zakład aktywności zawodowej prowadzony przez Powiat Brzeski.", "2026-10-03"),
]

# (liczba, opis, źródło – nazwa, url)
STATS = [
    ("ok. 60 tys.", "osób z zespołem Downa żyje w Polsce; ponad 70% dożywa 50 lat",
     "Światowy Dzień Zespołu Downa – gov.pl", "https://www.gov.pl/web/psse-swidwin/swiatowy-dzien-zespolu-downa"),
    ("1 na 800–1000", "urodzeń to dziecko z zespołem Downa (ok. 600–1000 dzieci rocznie)",
     "Wikipedia: Zespół Downa", "https://pl.wikipedia.org/wiki/Zesp%C3%B3%C5%82_Downa"),
    ("32,5%", "wskaźnik zatrudnienia osób z niepełnosprawnością w wieku produkcyjnym (II kw. 2024) – "
     "o blisko 50 punktów mniej niż u osób sprawnych", "GUS BAEL – Biuro Pełnomocnika Rządu ds. ON",
     "https://niepelnosprawni.gov.pl/baza-wiedzy/niepelnosprawnosc-w-liczbach/rynek-pracy/"),
    ("103 ZAZ · 708 WTZ", "działa w Polsce (2024): ZAZ zatrudniają ok. 5,8 tys. osób, WTZ wspierają ponad 28 tys.",
     "prawo.pl", "https://www.prawo.pl/kadry/wzrost-dofinansowania-dla-zaz-i-wtz-w-tym-roku,523692.html"),
    ("63 WTZ", "ma Małopolska – najwięcej w kraju; w 25 powiatach Polski nie ma żadnego",
     "PFRON – badanie sytuacji WTZ", "https://www.pfron.org.pl/fileadmin/files/r/5062_Raport_koncowy_WTZ.pdf"),
    ("10 ZAZ", "działa w Małopolsce (wykaz Małopolskiego Urzędu Wojewódzkiego)", "BIP Małopolska", _ZAZ_MP),
]

# „Poznaj ZD” – czego oczekują osoby z zespołem Downa (źródła: przegląd badań i polskie historie)
EXPECTATIONS = [
    ("Samodzielność i decydowanie o sobie", "Dorosłe osoby z ZD mówią o chęci mieszkania na swoim, wyboru miejsca "
     "i sposobu życia – planowanie wyprowadzki z domu rodzinnego daje poczucie sprawczości.",
     "Przegląd badań jakości życia dorosłych z ZD (PLOS One)",
     "https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0280014"),
    ("Praca, która ma sens", "Praca daje poczucie bezpieczeństwa, rytm dnia i własne pieniądze. Osoby z ZD pracują "
     "w urzędach, kawiarniach, hotelach i firmach – gdy mają trenera pracy i jasne zadania.",
     "ZespolDowna.info: Co daje praca osobom z ZD?",
     "https://www.zespoldowna.info/co-daje-praca-osobom-z-zespolem-downa-poczucie-bezpieczenstwa.html"),
    ("Przyjaciele, związki, bycie potrzebnym", "Relacje, aktywny czas wolny i udział w życiu społeczności są dla osób "
     "z ZD równie ważne jak dla każdego – stąd nasz program „Jestem potrzebny”.",
     "Przegląd: udział w życiu społeczności dorosłych z ZD",
     "https://www.tandfonline.com/doi/full/10.1080/09638288.2025.2476731"),
    ("Zwykła praca w zwykłym miejscu", "Pierwsza osoba z ZD w Urzędzie Miejskim w Gdańsku pracuje na pół etatu przy "
     "dokumentach; w Urzędzie Marszałkowskim w Krakowie – dwie osoby. To działa.",
     "TVN24 (Gdańsk) i TVP Kraków",
     "https://tvn24.pl/pomorze/gdansk-pierwsza-osoba-z-zespolem-downa-zatrudniona-w-urzedzie-miejskim-ra989076-2314936"),
]

# (mit, fakt, źródło – nazwa, url)
MYTHS = [
    ("Zespół Downa to choroba.", "To cecha genetyczna (dodatkowy chromosom 21), nie choroba – nie można się nią zarazić "
     "ani jej wyleczyć; można dobrze wspierać rozwój.", "Fundacja Pełna Życia", "https://pelna-zycia.pl/o-zespole-downa-slow-kilka/"),
    ("Dzieci z ZD rodzą tylko starsze matki.", "Najwięcej dzieci z zespołem Downa rodzą kobiety przed 30. rokiem życia, "
     "bo w tym wieku rodzi się najwięcej dzieci.", "uwazniej.pl: mity o zespole Downa", "https://uwazniej.pl/mity-o-zespole-downa/"),
    ("Wszystkie osoby z ZD wyglądają tak samo.", "Osoba z ZD jest bardziej podobna do swojej rodziny niż do innych osób "
     "z trisomią 21.", "uwazniej.pl: mity o zespole Downa", "https://uwazniej.pl/mity-o-zespole-downa/"),
    ("Osoby z ZD są zawsze szczęśliwe.", "Mają pełną gamę emocji – złoszczą się, smucą i nudzą jak każdy. "
     "„Wiecznie uśmiechnięte dziecko” to stereotyp.", "Fundacja Pełna Życia", "https://pelna-zycia.pl/o-zespole-downa-slow-kilka/"),
    ("Osoby z ZD nie mogą się uczyć ani pracować.", "Uczą się wolniej, ale uczą się – i pracują na różnych stanowiskach, "
     "gdy zadania są dopasowane, a start wspiera trener pracy.", "Fundacja Pełna Życia", "https://pelna-zycia.pl/o-zespole-downa-slow-kilka/"),
    ("Osoby z ZD nie dożywają dorosłości.", "Ponad 70% osób z ZD w Polsce dożywa ponad 50 lat – dorosłość, praca "
     "i „co po nas” to realne tematy.", "gov.pl – Światowy Dzień Zespołu Downa",
     "https://www.gov.pl/web/psse-swidwin/swiatowy-dzien-zespolu-downa"),
]

# Poradnik HugMe dla pracodawców i instytucji (zasady ogólne, bez źródła zewnętrznego)
HOW_TO_TALK = [
    "Mów wprost do osoby, nie do opiekuna. Patrz na nią, nie na rodzica.",
    "Krótkie zdania, jedna myśl naraz. Daj czas na odpowiedź – nie kończ za nią.",
    "Pokaż, nie tylko mów: zrób zadanie razem pierwszy raz, potem obserwuj.",
    "Jedno zadanie naraz, stały rytm dnia, jasny koniec („gdy skończysz, powiedz mi”).",
    "Chwal konkretnie: „dobrze ułożyłeś książki” zamiast „super”.",
    "Na początku pomaga trener pracy albo buddy; po kilku tygodniach zwykle nie jest już potrzebny.",
]
INTERESTS_NOTE = ("Organizacje rodziców prowadzą dla osób z ZD zajęcia na basenie, sportowe, muzyczne i plastyczne – "
                  "to najczęstsze zainteresowania także w naszym programie.",
                  "Stowarzyszenie „Bardziej Kochani”", "https://bardziejkochani.pl/o-nas/")
