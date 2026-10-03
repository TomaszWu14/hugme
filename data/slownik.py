"""Słownik pojęć: słowa mieszkańców → tematy. Dzięki temu „lekarz”, „wizyta” i „kardiolog”
trafiają do tego samego tematu „zdrowie”, nawet gdy innowacja używa innych słów.
Rozszerzaj bez programowania: dopisz słowo w formie podstawowej do listy."""

TOPICS = {
    "zdrowie": ("zdrowie i wizyty u lekarzy", [
        "lekarz", "lekarka", "lekarze", "wizyta", "wizyty", "specjalista", "specjalistów", "przychodnia",
        "kardiolog", "logopeda", "endokrynolog", "neurolog", "pediatra", "okulista", "laryngolog",
        "stomatolog", "dentysta", "rehabilitacja", "rehabilitant", "fizjoterapia", "badanie", "badania",
        "szpital", "termin", "terminy", "rejestracja", "leczenie", "zdrowie", "recepta", "poradnia",
    ]),
    "niepelnosprawnosc": ("niepełnosprawność i zespół Downa", [
        "zespół", "down", "downa", "niepełnosprawność", "niepełnosprawny", "niepełnosprawnością",
        "orzeczenie", "intelektualna", "intelektualną", "trisomia", "autyzm", "specjalne", "potrzeby",
    ]),
    "szkola": ("szkoła i edukacja", [
        "szkoła", "szkole", "klasa", "nauczyciel", "nauczycielka", "przedszkole", "uczeń", "uczniowie",
        "edukacja", "lekcje", "integracyjna", "wychowawca", "świetlica",
    ]),
    "praca": ("praca i dorosłość", [
        "praca", "pracy", "zatrudnienie", "pracodawca", "zawód", "staż", "dorosłość", "dorosły", "dorośli",
        "kawiarnia", "trening", "zawodowy", "samodzielność", "samodzielny", "mieszkanie",
    ]),
    "odciazenie": ("odciążenie rodziców i opiekunów", [
        "zmęczenie", "zmęczeni", "zmęczony", "wypalenie", "odpoczynek", "odpocząć", "wytchnienie",
        "wytchnieniowa", "odciążenie", "opiekun", "opiekunowie", "opiekunka", "przerwa", "rodzic", "rodzice",
        "rodziców", "sił", "wyczerpani",
    ]),
    "integracja": ("integracja i rówieśnicy", [
        "integracja", "rówieśnicy", "przyjaciele", "przyjaźń", "koledzy", "akceptacja", "wykluczenie",
        "wspólne", "razem", "klub", "spotkania",
    ]),
    "oferty": ("informacja o ofertach pomocy", [
        "oferta", "oferty", "ulga", "ulgi", "świadczenie", "świadczenia", "informacja", "informacji",
        "gdzie", "baza", "mapa", "turnus", "turnusy", "dofinansowanie", "pomoc",
    ]),
    "seniorzy": ("seniorzy i starość", [
        "senior", "seniorka", "seniorzy", "seniorów", "starszy", "starsza", "starsze", "starszych",
        "emeryt", "emerytka", "babcia", "dziadek", "starość", "wiek",
    ]),
    "samotnosc": ("samotność i więzi", [
        "samotność", "samotny", "samotna", "samotni", "izolacja", "rozmowa", "towarzystwo", "sąsiad",
        "sąsiedzi", "sąsiedzki", "kontakt", "więzi",
    ]),
    "cyfrowe": ("technologia i internet", [
        "internet", "internecie", "komputer", "smartfon", "telefon", "tablet", "aplikacja", "online",
        "recepta", "profil", "zaufany", "cyfrowy", "cyfrowe", "mobywatel", "bankowość", "formularz",
    ]),
    "psychiczne": ("zdrowie psychiczne i emocje", [
        "psycholog", "psychiatra", "psychoterapia", "depresja", "lęk", "kryzys", "stres", "emocje",
        "nastolatek", "nastolatki", "młodzież", "samookaleczenia", "smutek", "załamanie",
    ]),
    "transport": ("dojazd i transport", [
        "autobus", "dojazd", "dojechać", "dojeżdżać", "bus", "transport", "samochód", "kurs", "kursy",
        "przystanek", "komunikacja", "wieś", "wsi", "sołectwo", "daleko", "dowóz",
    ]),
    "wspolpraca": ("współpraca instytucji", [
        "współpraca", "partnerstwo", "partner", "partnerzy", "organizacja", "organizacje", "ngo",
        "fundacja", "stowarzyszenie", "gmina", "gminy", "firma", "firmy", "biznes", "samorząd", "sektor",
    ]),
    "finansowanie": ("finansowanie i granty", [
        "grant", "dotacja", "konkurs", "nabór", "finansowanie", "budżet", "pieniądze", "środki", "fundusz",
    ]),
}

# Temat → obszar wyzwania (do automatycznego wykrywania obszaru zgłoszenia).
TOPIC_AREA = {
    "niepelnosprawnosc": "rodziny-zd", "seniorzy": "seniorzy", "samotnosc": "samotnosc",
    "cyfrowe": "cyfrowe", "psychiczne": "psychiczne", "transport": "wies", "wspolpraca": "wspolpraca",
}

STOPWORDS = set("""
a aby ach albo ale ani aż bardzo bez bo być był była było były będzie będą by byśmy chce chcemy
co czy czyli dla do dość gdy go i ich ile im inne inny iż ja jak jaki jakie jakiś jako je jego jej jest
jeszcze jestem jesteśmy już kiedy kto która które który których ku lub ma mają mam mamy mi mnie mogą może
można mój moja moje mu my na nad nam nas nasz nasza nasze naszej naszych naszym nawet nic nie niż no o od on ona
one oni ono oraz po pod przez przy sa się sobie są ta tak tam te tego tej ten też to tu tylko tym u w we wiele
więc wszystko z za ze że żeby bardziej często coraz każdy każda inaczej czasem trzeba chodzi jedna jeden
""".split())
