"""Treści modułu „Razem z ZD” – dla osób z zespołem Downa i ich rodzin.

Struktura „grupa → etapy”: dziś jedna grupa (`zd`), kolejne (np. autyzm) dodaje się wpisem w GROUPS.
To ogólne informacje (PRZYKŁAD), nie porada medyczna ani prawna – do weryfikacji przez lekarzy
i organizacje rodziców."""

GROUPS = {
    "zd": {
        "name": "Rodziny osób z zespołem Downa",
        "area": "rodziny-zd",
        "stages": [
            {"slug": "diagnoza", "name": "Diagnoza i pierwszy rok", "age": "0–1 rok", "icon": "serce",
             "now": ["Nie zostawaj z tym sam – poznaj inne rodziny i organizację rodziców w okolicy.",
                     "Ustal, kto koordynuje opiekę: pediatra, poradnia, wczesne wspomaganie.",
                     "Zapytaj o wczesne wspomaganie rozwoju – im wcześniej, tym lepiej."],
             "ask_doctor": ["Czy i kiedy zbadać serce (echo serca)?", "Kiedy pierwsze badanie słuchu i wzroku?",
                            "Jak często sprawdzać tarczycę?", "Do kogo z karmieniem i napięciem mięśni?"],
             "documents": ["Jedna teczka na skierowania i wyniki badań.",
                           "Opinia o potrzebie wczesnego wspomagania rozwoju (poradnia psychologiczno-pedagogiczna).",
                           "Wniosek o orzeczenie o niepełnosprawności – gdy będziesz gotowy."],
             "etr": "Twoje dziecko jest małe. Dużo się dzieje. Poznaj inne rodziny. Pytaj lekarza o serce, słuch i wzrok.",
             "innovations": ["Klub Rodziców i Rodzeństwa", "Mapa Wsparcia Rodzin"]},
            {"slug": "maluch", "name": "Maluch", "age": "1–3 lata", "icon": "dom",
             "now": ["Rehabilitacja ruchowa i logopeda – ustal stały rytm zajęć.",
                     "Wczesne wspomaganie rozwoju – zajęcia w poradni lub w domu.",
                     "Zadbaj o siebie: kilka godzin wytchnienia w tygodniu to nie luksus."],
             "ask_doctor": ["Kiedy kolejna kontrola słuchu i wzroku?", "Jak często badać tarczycę?",
                            "Czy dziecko dobrze śpi i oddycha w nocy (chrapanie)?"],
             "documents": ["Orzeczenie o niepełnosprawności.", "Plan zajęć wczesnego wspomagania."],
             "etr": "Dziecko dużo się uczy. Ćwiczy z rehabilitantem i logopedą. Rodzic też potrzebuje odpocząć.",
             "innovations": ["Asystent zdrowia rodziny", "Dzień Specjalistów w jednym miejscu",
                             "Godziny dla rodzica – opieka wytchnieniowa"]},
            {"slug": "przedszkole", "name": "Przedszkole", "age": "3–6 lat", "icon": "przyjaciele",
             "now": ["Wybierz przedszkole i porozmawiaj z dyrekcją o wsparciu.",
                     "Orzeczenie o potrzebie kształcenia specjalnego – z poradni psychologiczno-pedagogicznej.",
                     "Pierwsze przyjaźnie: zajęcia z rówieśnikami po przedszkolu."],
             "ask_doctor": ["Kontrola wzroku i słuchu przed szkołą.", "Tarczyca – czy wyniki są w normie?",
                            "Kiedy wizyta u dentysty?"],
             "documents": ["Orzeczenie o potrzebie kształcenia specjalnego.", "Wniosek do gminy o dowóz (jeśli potrzebny)."],
             "etr": "Dziecko idzie do przedszkola. Poznaje kolegów. Rodzic rozmawia z dyrektorem o pomocy.",
             "innovations": ["Klasa w Ruchu – integracja od pierwszego dnia", "Asystent zdrowia rodziny",
                             "Godziny dla rodzica – opieka wytchnieniowa"]},
            {"slug": "szkola", "name": "Szkoła", "age": "7–15 lat", "icon": "szkola",
             "now": ["Typ szkoły: ogólnodostępna, integracyjna albo specjalna – porównaj je spokojnie.",
                     "Asystent ucznia i dostosowanie warunków nauki – masz prawo o nie prosić.",
                     "Zajęcia po lekcjach i przyjaźnie są tak samo ważne jak oceny."],
             "ask_doctor": ["Tarczyca – raz w roku?", "Waga, ruch i dieta.", "Wzrok i kręgosłup."],
             "documents": ["Indywidualny program (IPET) od szkoły.", "Wniosek o asystenta ucznia.", "Wniosek o dowóz."],
             "etr": "Dziecko chodzi do szkoły. Może mieć asystenta. Po lekcjach spotyka przyjaciół.",
             "innovations": ["Klasa w Ruchu – integracja od pierwszego dnia", "Klub Rodziców i Rodzeństwa",
                             "Dzień Specjalistów w jednym miejscu"]},
            {"slug": "mlodziez", "name": "Młodzież i koniec szkoły", "age": "16–24 lata", "icon": "praca",
             "now": ["Plan na „po szkole” zacznij 2–3 lata wcześniej.",
                     "Trening pracy, staże, warsztaty – sprawdź, co jest w powiecie.",
                     "Samodzielność: zakupy, komunikacja, pieniądze – ćwiczcie na co dzień."],
             "ask_doctor": ["Dojrzewanie – o co pytać?", "Tarczyca i waga.", "Nastrój i sen – czy coś się zmieniło?"],
             "documents": ["Nowe orzeczenie po 16. roku życia (orzeczenie o stopniu niepełnosprawności).",
                           "Rejestracja w urzędzie pracy (staże, szkolenia)."],
             "etr": "Szkoła się kończy. Możesz uczyć się pracy. Ćwiczysz samodzielność.",
             "innovations": ["Kawiarnia Treningowa „Po Szkole”", "Klub Rodziców i Rodzeństwa"]},
            {"slug": "doroslosc", "name": "Dorosłość", "age": "25+ lat", "icon": "dom",
             "now": ["Praca albo zajęcia dzienne (np. warsztaty terapii zajęciowej, środowiskowy dom samopomocy).",
                     "Mieszkanie treningowe – nauka samodzielnego życia.",
                     "„Co po nas” – zaplanujcie przyszłość razem, póki jest na to czas."],
             "ask_doctor": ["Tarczyca i serce – kontrole.", "Słuch i wzrok.", "Pamięć i nastrój – czy coś się zmienia?"],
             "documents": ["Decyzje prawne o wsparciu w podejmowaniu decyzji (porozmawiaj z prawnikiem).",
                           "Plan na przyszłość – kto, gdzie, jak."],
             "etr": "Jesteś dorosły. Możesz pracować. Możesz mieszkać bardziej samodzielnie. Planujesz przyszłość.",
             "innovations": ["Kawiarnia Treningowa „Po Szkole”", "Mapa Wsparcia Rodzin"]},
        ],
    },
}

DEFAULT_GROUP = "zd"
DISCLAIMER = "To ogólne informacje (PRZYKŁAD), nie porada medyczna. O zdrowiu dziecka zawsze rozmawiaj z lekarzem."


def stages(group=DEFAULT_GROUP):
    return GROUPS[group]["stages"]


def stage(slug, group=DEFAULT_GROUP):
    return next((s for s in stages(group) if s["slug"] == slug), None)


REQUEST_KINDS = {
    "przewodnik-szukam": "Szukam rodzica-przewodnika",
    "przewodnik-oferuje": "Chcę być rodzicem-przewodnikiem",
    "wytchnienie": "Prośba o opiekę wytchnieniową",
    "dzien-specjalistow": "Chcę Dzień Specjalistów w powiecie",
    "miejsce": "Polecenie przyjaznego miejsca",
    "sprzet-oddam": "Oddam sprzęt",
    "sprzet-przyjme": "Przyjmę sprzęt",
}
PUBLIC_KINDS = {"miejsce", "sprzet-oddam", "sprzet-przyjme"}  # widoczne publicznie po zatwierdzeniu przez Hub
PLACE_CATEGORIES = ["przychodnia", "dentysta", "fryzjer", "basen i sport", "kawiarnia", "inne"]

RIGHTS_QUESTIONS = [
    ("orzeczenie", "Czy dziecko (osoba z ZD) ma orzeczenie o niepełnosprawności?"),
    ("szkola", "Czy chodzi do przedszkola albo szkoły?"),
    ("praca", "Czy opiekun ograniczył pracę, żeby się opiekować?"),
    ("dorosly", "Czy osoba z ZD ma 16 lat lub więcej?"),
    ("sprzet", "Czy potrzebny jest sprzęt albo turnus rehabilitacyjny?"),
]

_HUB = {"institution": "Hub Innowacji Społecznych ROPS (HugMe)",
        "why": "Nie wiesz, od czego zacząć? Opisz problem – połączymy Cię z ludźmi.", "documents": []}


def rights_result(answers):
    """answers: {klucz: True/False}. Zwraca instytucje: gdzie zapytać i jakie dokumenty (bez kwot i progów)."""
    out = []
    if answers.get("orzeczenie") is False:
        out.append({"institution": "Powiatowy zespół do spraw orzekania o niepełnosprawności",
                    "why": "Orzeczenie otwiera dostęp do wielu form wsparcia.",
                    "documents": ["wniosek (formularz w zespole)", "zaświadczenie od lekarza", "dokumentacja medyczna"]})
    out.append({"institution": "Ośrodek pomocy społecznej (OPS) lub centrum usług społecznych (CUS) w gminie",
                "why": "Świadczenia rodzinne, usługi opiekuńcze, opieka wytchnieniowa, asystent rodziny.",
                "documents": ["dowód osobisty", "orzeczenie (jeśli jest)"]})
    if answers.get("szkola"):
        out.append({"institution": "Poradnia psychologiczno-pedagogiczna",
                    "why": "Orzeczenie o potrzebie kształcenia specjalnego i opinie dla przedszkola/szkoły.",
                    "documents": ["wniosek rodzica", "dokumentacja z przedszkola/szkoły"]})
        out.append({"institution": "Gmina – wydział edukacji",
                    "why": "Bezpłatny dowóz do przedszkola lub szkoły.", "documents": ["wniosek", "orzeczenie z poradni"]})
    if answers.get("praca"):
        out.append({"institution": "Ośrodek pomocy społecznej – dział świadczeń dla opiekunów",
                    "why": "Zapytaj o świadczenia dla opiekunów osób z niepełnosprawnością i zasady łączenia z pracą.",
                    "documents": ["orzeczenie", "zaświadczenia o dochodach (jeśli wymagane)"]})
    if answers.get("dorosly"):
        out.append({"institution": "Powiatowe centrum pomocy rodzinie (PCPR)",
                    "why": "Warsztaty terapii zajęciowej, dofinansowania z PFRON, mieszkania wspomagane.",
                    "documents": ["orzeczenie o stopniu niepełnosprawności"]})
        out.append({"institution": "Powiatowy urząd pracy",
                    "why": "Staże, szkolenia, trener pracy.", "documents": ["dowód osobisty", "orzeczenie"]})
    if answers.get("sprzet"):
        out.append({"institution": "Powiatowe centrum pomocy rodzinie – dofinansowania PFRON",
                    "why": "Sprzęt rehabilitacyjny, turnusy, likwidacja barier.",
                    "documents": ["wniosek", "zaświadczenie lekarskie", "orzeczenie"]})
    out.append(_HUB)
    return out


LETTERS = {
    "asystent": {
        "title": "Wniosek o asystenta ucznia",
        "fields": [("rodzic", "Imię i nazwisko rodzica", "Anna Przykładowa"),
                   ("szkola", "Nazwa szkoły", "Szkoła Podstawowa nr 1 w Przykładowie"),
                   ("klasa", "Klasa", "2b"),
                   ("uzasadnienie", "Dlaczego dziecko potrzebuje wsparcia?", "potrzebuje pomocy przy przechodzeniu między zajęciami"),
                   ("miejscowosc", "Miejscowość", "Wadowice")],
        "template": ("{miejscowosc}, dnia {data}\n\n{rodzic}\n\nDyrektor\n{szkola}\n\n"
                     "WNIOSEK O ZAPEWNIENIE ASYSTENTA UCZNIA\n\n"
                     "Zwracam się z prośbą o zapewnienie asystenta mojemu dziecku, uczniowi klasy {klasa}, "
                     "posiadającemu orzeczenie o potrzebie kształcenia specjalnego.\n\n"
                     "Uzasadnienie: {uzasadnienie}\n\nZ poważaniem\n{rodzic}"),
    },
    "dostosowanie": {
        "title": "Prośba o dostosowanie warunków nauki",
        "fields": [("rodzic", "Imię i nazwisko rodzica", "Anna Przykładowa"),
                   ("szkola", "Nazwa szkoły", "Szkoła Podstawowa nr 1 w Przykładowie"),
                   ("klasa", "Klasa", "2b"),
                   ("uzasadnienie", "Jakie dostosowania są potrzebne?", "więcej czasu na sprawdzianach, polecenia na piśmie"),
                   ("miejscowosc", "Miejscowość", "Wadowice")],
        "template": ("{miejscowosc}, dnia {data}\n\n{rodzic}\n\nDyrektor\n{szkola}\n\n"
                     "PROŚBA O DOSTOSOWANIE WARUNKÓW NAUKI\n\n"
                     "Proszę o dostosowanie warunków nauki dla mojego dziecka, ucznia klasy {klasa}, "
                     "zgodnie z orzeczeniem o potrzebie kształcenia specjalnego.\n\n"
                     "Potrzebne dostosowania: {uzasadnienie}\n\nZ poważaniem\n{rodzic}"),
    },
    "wytchnienie": {
        "title": "Wniosek o opiekę wytchnieniową",
        "fields": [("rodzic", "Imię i nazwisko opiekuna", "Anna Przykładowa"),
                   ("gmina", "Ośrodek pomocy społecznej w gminie", "OPS w Przykładowie"),
                   ("godziny", "Ile godzin w tygodniu?", "6"),
                   ("uzasadnienie", "Dlaczego potrzebujesz wytchnienia?", "opiekuję się dzieckiem sama, bez przerw"),
                   ("miejscowosc", "Miejscowość", "Wadowice")],
        "template": ("{miejscowosc}, dnia {data}\n\n{rodzic}\n\n{gmina}\n\n"
                     "WNIOSEK O USŁUGĘ OPIEKI WYTCHNIENIOWEJ\n\n"
                     "Zwracam się z prośbą o przyznanie usługi opieki wytchnieniowej w wymiarze {godziny} godzin "
                     "tygodniowo dla opiekuna osoby z niepełnosprawnością.\n\n"
                     "Uzasadnienie: {uzasadnienie}\n\nZ poważaniem\n{rodzic}"),
    },
}

SCHOOLS = [
    {"type": "Ogólnodostępna", "what": "Zwykła szkoła w okolicy; dziecko z orzeczeniem ma prawo do dostosowań i wsparcia.",
     "good": "Blisko domu, rówieśnicy z sąsiedztwa.", "ask": "Czy szkoła zapewni asystenta i zajęcia rewalidacyjne?"},
    {"type": "Integracyjna", "what": "Mniejsze klasy, dwóch nauczycieli (w tym nauczyciel wspomagający).",
     "good": "Wsparcie na lekcjach, doświadczenie w integracji.", "ask": "Ilu uczniów z orzeczeniem jest w klasie?"},
    {"type": "Specjalna", "what": "Klasy dla uczniów z niepełnosprawnościami, specjaliści na miejscu.",
     "good": "Dużo terapii i indywidualne tempo.", "ask": "Jak szkoła dba o kontakt z rówieśnikami spoza szkoły?"},
]

SIBLINGS = [
    "Rodzeństwo też ma swoje emocje: dumę, troskę, czasem złość albo zazdrość. Wszystkie są w porządku.",
    "Znajdź czas tylko dla brata albo siostry – nawet godzina w tygodniu robi różnicę.",
    "Grupy rodzeństwa (np. w Klubie Rodziców i Rodzeństwa) pozwalają spotkać dzieci z podobnym doświadczeniem.",
    "Mów prawdę prostymi słowami, dopasowanymi do wieku dziecka.",
]

FUTURE = [
    ("Gdzie zamieszka?", "Mieszkania treningowe i wspomagane uczą samodzielności. Zapytaj PCPR i organizacje rodziców."),
    ("Kto pomoże w decyzjach?", "Porozmawiaj z prawnikiem o formach wsparcia w podejmowaniu decyzji – zanim będzie to pilne."),
    ("Z czego będzie żyć?", "Świadczenia, praca, zabezpieczenie rodziny – zaplanujcie to razem z doradcą."),
    ("Kto będzie blisko?", "Sieć ludzi: rodzeństwo, przyjaciele, wspólnota, organizacja. Im więcej osób, tym bezpieczniej."),
    ("Czego chce osoba z ZD?", "Najważniejsze: zapytajcie ją samą. To jej przyszłość."),
]

# „Moje sprawy” – tekst łatwy do czytania (ETR): krótkie zdania, jedno zdanie = jedna myśl.
MY_TOPICS = [
    ("praca", "Praca", "Chcę pracować. Chcę się uczyć pracy."),
    ("przyjaciele", "Przyjaciele", "Chcę mieć przyjaciół. Chcę spotykać ludzi."),
    ("lekarz", "Lekarz", "Chcę iść do lekarza. Potrzebuję pomocy."),
    ("dom", "Dom", "Chcę mieszkać samodzielnie. Chcę się tego uczyć."),
    ("szkola", "Szkoła", "Mam kłopot w szkole. Potrzebuję pomocy."),
    ("pieniadze", "Pieniądze", "Chcę umieć liczyć pieniądze. Chcę robić zakupy."),
]
MY_INTRO = [
    "To jest strona dla Ciebie.",
    "Możesz tu powiedzieć, co jest trudne.",
    "Wybierz obrazek.",
    "Napisz jedno zdanie.",
    "Ktoś z Hubu Ci odpowie.",
]
