"""Stałe domenowe: obszary wyzwań, powiaty Małopolski, role, etapy, statusy."""

# Obszary wyzwań regionu. Kolor = „nić” obszaru na kartach (kontrast >= 3:1 do kremowego tła).
# Wzór kreski (pattern) odróżnia nici, które przy daltonizmie mają podobny kolor.
AREAS = {
    "rodziny-zd": {
        "pattern": "ciagla",
        "name": "Rodziny osób z zespołem Downa",
        "short": "Rodziny i zespół Downa",
        "color": "#7A3E9D",
        "pilot": True,
        "challenge": "Rodzice dzieci z zespołem Downa koordynują wizyty u wielu specjalistów, "
                     "szukają integracji w szkole i pracy po jej zakończeniu. Często są zmęczeni "
                     "i nie wiedzą, gdzie szukać wsparcia.",
    },
    "seniorzy": {
        "pattern": "kreski",
        "name": "Seniorzy i opieka",
        "short": "Seniorzy",
        "color": "#8F5300",
        "challenge": "Coraz więcej starszych osób mieszka samodzielnie. Potrzebują pomocy na co dzień, "
                     "dostępu do usług i kontaktu z ludźmi.",
    },
    "samotnosc": {
        "pattern": "ciagla",
        "name": "Samotność i więzi sąsiedzkie",
        "short": "Samotność",
        "color": "#2F6AA6",
        "challenge": "Samotność dotyka ludzi w każdym wieku. Brakuje miejsc i okazji, "
                     "żeby poznać sąsiadów i poczuć się potrzebnym.",
    },
    "cyfrowe": {
        "pattern": "kropki",
        "name": "Wykluczenie cyfrowe",
        "short": "Wykluczenie cyfrowe",
        "color": "#1C7570",
        "challenge": "Wiele spraw załatwia się dziś przez internet. Część mieszkańców nie ma sprzętu, "
                     "umiejętności albo pewności siebie, żeby z tego korzystać.",
    },
    "psychiczne": {
        "pattern": "paski",
        "name": "Zdrowie psychiczne",
        "short": "Zdrowie psychiczne",
        "color": "#A8346A",
        "challenge": "Na pomoc psychologa czeka się długo, a o kłopotach trudno mówić. "
                     "Szczególnie dotyczy to młodzieży i opiekunów.",
    },
    "wies": {
        "pattern": "ciagla",
        "name": "Wieś i transport",
        "short": "Wieś i transport",
        "color": "#4A7320",
        "challenge": "W małych miejscowościach autobus jeździ rzadko albo wcale. "
                     "Trudno dojechać do lekarza, urzędu, szkoły czy pracy.",
    },
    "wspolpraca": {
        "pattern": "kreski",
        "name": "Współpraca międzysektorowa",
        "short": "Współpraca",
        "color": "#55596A",
        "challenge": "Gminy, organizacje, firmy i mieszkańcy często działają osobno. "
                     "Dobre pomysły nie przechodzą z jednej gminy do drugiej.",
    },
}

POWIATY = [
    "Kraków", "Nowy Sącz", "Tarnów",
    "bocheński", "brzeski", "chrzanowski", "dąbrowski", "gorlicki", "krakowski",
    "limanowski", "miechowski", "myślenicki", "nowosądecki", "nowotarski", "olkuski",
    "oświęcimski", "proszowicki", "suski", "tarnowski", "tatrzański", "wadowicki", "wielicki",
]

ROLES = {
    "mieszkaniec": "Mieszkanka-rodzic",
    "ngo": "Organizacja pozarządowa",
    "gmina": "Gmina (JST)",
    "ekspert": "Ekspert",
    "admin": "Koordynatorka ROPS",
}

STAGES = ["pomysł", "prototyp", "test", "wdrożenie"]

AUDIENCES = ["dzieci i młodzież", "rodzice i opiekunowie", "dorośli", "seniorzy", "cała społeczność"]

REPORT_STATUSES = {
    "nowe": "Nowe",
    "w-analizie": "W analizie",
    "polaczone": "Połączone z rozwiązaniem",
    "luka": "Luka – brak rozwiązania",
    "zamkniete": "Zamknięte",
}

TEST_KINDS = {"zgloszenie": "Zgłoszenie do testu", "ocena": "Ocena", "usprawnienie": "Propozycja usprawnienia"}

# Progi heatmapy trendów: liczba zgłoszeń → stopień 1–4 (bezwzględne, nie względem maksimum).
HEAT_STEPS = (1, 2, 4, 7)


def heat_level(n):
    return sum(n >= step for step in HEAT_STEPS)


# Próg trafności, poniżej którego zgłoszenie uznajemy za „lukę”.
GAP_THRESHOLD = 0.35
