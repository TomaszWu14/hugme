"""Program „Jestem potrzebny / potrzebna” – słowniki, odznaki, treści i dane przykładowe (FIKCYJNE).

Osoby z zespołem Downa (w każdym wieku) pomagają innym: psom ze schroniska, osobom w hospicjach i DPS,
młodszym dzieciom. Hub łączy uczestnika z miejscem i potwierdza odbyte misje."""

NAME = "Jestem potrzebny"

# slug → (etykieta, ikona, zainteresowanie które pasuje)
MISSION_KINDS = {
    "psy": ("Psy ze schroniska – spacery", "pies", "psy"),
    "hospicjum": ("Odwiedziny w hospicjum lub DPS", "serce", "starsi"),
    "dzieci": ("Pomoc młodszym dzieciom", "przyjaciele", "dzieci"),
    "inne": ("Inna pomoc (ogród, biblioteka, zwierzęta)", "dom", ""),
}
MISSION_LABELS = {k: v[0] for k, v in MISSION_KINDS.items()}

# slug → (etykieta, ikona) – „co lubię” w formularzu uczestnika
INTERESTS = {
    "psy": ("psy", "pies"), "koty": ("koty", "kot"), "starsi": ("starsze osoby", "serce"),
    "dzieci": ("dzieci", "przyjaciele"), "ogrod": ("ogród", "dom"), "ksiazki": ("książki", "szkola"),
    "sport": ("sport", "sport"), "muzyka": ("muzyka", "glosnik"), "kuchnia": ("gotowanie", "praca"),
}
DAYS = {"pn": "poniedziałek", "wt": "wtorek", "sr": "środa", "cz": "czwartek", "pt": "piątek", "sb": "sobota",
        "nd": "niedziela"}
TIMES = {"rano": "rano", "popoludnie": "po południu"}
AGE_GROUPS = {"dziecko": "dziecko (do 12 lat)", "mlodziez": "młodzież (13–18 lat)", "dorosly": "osoba dorosła"}
COMPANIONS = {"rodzic": "rodzic lub opiekun", "asystent": "asystent osoby z niepełnosprawnością",
              "buddy": "proszę o wolontariusza-buddy z Hubu"}
PROVIDES = {"opiekun": "opiekun ze strony miejsca", "szkolenie": "krótkie szkolenie na początku",
            "kamizelka": "kamizelka lub identyfikator", "ubezpieczenie": "ubezpieczenie NNW"}

# Odznaki: (próg, slug, nazwa, łatwy tekst). Tematyczne – po 3 misjach jednego rodzaju.
BADGES = [
    (1, "pierwsza", "Pierwsza misja", "Pierwsza misja za mną."),
    (5, "dlon", "Pomocna dłoń", "5 misji za mną."),
    (10, "filar", "Filar programu", "10 misji za mną. Jestem ważną osobą."),
]
THEME_BADGES = {"psy": ("przyjaciel-psow", "Przyjaciel psów"), "hospicjum": ("dobry-sasiad", "Dobry sąsiad"),
                "dzieci": ("starszy-kolega", "Starszy kolega"), "inne": ("pomocnik", "Pomocnik")}
SKILLS_FROM = 5  # od ilu misji dzienniczek pokazuje umiejętności
SKILLS = {"psy": ["punktualność", "opieka nad zwierzętami"], "hospicjum": ["cierpliwość", "rozmowa z ludźmi"],
          "dzieci": ["odpowiedzialność", "zabawa w grupie"], "inne": ["współpraca", "dokładność"]}


def badges_for(total, by_kind):
    """Zdobyte odznaki: lista (slug, nazwa, łatwy tekst) z sumy misji i misji wg rodzaju."""
    out = [(s, n, t) for lim, s, n, t in BADGES if total >= lim]
    out += [(THEME_BADGES[k][0], THEME_BADGES[k][1], f"3 razy: {MISSION_LABELS[k].lower()}.")
            for k, n in by_kind.items() if n >= 3 and k in THEME_BADGES]
    return out


def skills_for(total, by_kind):
    if total < SKILLS_FROM:
        return []
    seen = []
    for k, n in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        seen += [s for s in SKILLS.get(k, []) if s not in seen]
    return seen


RULES = [
    ("Zawsze z opiekunem", "Na misję idzie rodzic, asystent albo wolontariusz-buddy dobrany przez Hub. Nikt nie zostaje sam."),
    ("Hub sprawdza miejsce", "Każde schronisko, hospicjum czy świetlica rozmawia z koordynatorką Hubu, zanim przyjmie pierwszą osobę."),
    ("Krótko i regularnie", "Misja to zwykle 1–2 godziny. Lepiej raz w tygodniu niż raz na pół roku."),
    ("Bezpieczeństwo", "Miejsce zapewnia opiekuna, krótkie szkolenie i ubezpieczenie NNW (organizator programu). Zwierzęta – tylko po ocenie behawiorysty schroniska."),
    ("Dane", "Pseudonim, powiat, zainteresowania i dostępność. Telefon widzi tylko Hub. Bez diagnozy, bez daty urodzenia."),
    ("Można przestać", "Każdy może zrezygnować w dowolnym momencie – wystarczy wiadomość do Hubu."),
]
THANKS = {
    "uczestnik": "Dziękujemy! Koordynatorka Hubu zadzwoni, żeby dobrać miejsce i opiekuna.",
    "latwy": "Dziękuję! Ktoś z Hubu zadzwoni.",
    "buddy": "Dziękujemy, że chcesz pomóc! Hub odezwie się, gdy pojawi się para z Twojej okolicy.",
    "instytucja": "Dziękujemy. Hub sprawdzi ofertę i opublikuje ją na liście.",
    "rodzic": "Dziękujemy za propozycję. Hub porozmawia z tym miejscem.",
    "praca": "Dziękujemy. Po sprawdzeniu źródła miejsce pojawi się na mapie.",
}
EASY_HINTS = ["Krótkie zdania.", "Jedna myśl w zdaniu.", "Bez skrótów i trudnych słów.", "Napisz, co dokładnie robi się na misji."]

# ── Dane przykładowe (FIKCYJNE, PRZYKŁAD) ─────────────────────────────────────
# (indeks użytkownika, source, institution, mission_kind, title, body, body_easy, powiat, days, slots, for_whom,
#  provides, requirements, status, dni temu)
OFFERS = [
    (1, "instytucja", "Schronisko dla zwierząt w Wadowicach (PRZYKŁAD)", "psy", "Spacery z psami w sobotnie przedpołudnia",
     "Nasze psy czekają na spacer. Potrzebujemy osób, które raz w tygodniu wyprowadzą spokojnego psa po parku z opiekunem schroniska.",
     "Idziesz na spacer z psem. Pies jest spokojny. Jest z Tobą opiekun. Spacer trwa 1 godzinę.",
     "wadowicki", "sb,nd,rano", 4, "mlodziez,dorosly", "opiekun,szkolenie,kamizelka,ubezpieczenie", "Spokój przy psach.", "zatwierdzone", 30),
    (1, "instytucja", "Hospicjum św. Łazarza – wolontariat (PRZYKŁAD)", "hospicjum", "Czytanie i rozmowa z pacjentami",
     "Pacjenci lubią, gdy ktoś poczyta gazetę albo po prostu posiedzi. Wolontariusz hospicjum jest cały czas obok.",
     "Siadasz obok starszej osoby. Czytasz albo rozmawiasz. Jest z Tobą wolontariusz.",
     "Kraków", "wt,cz,popoludnie", 2, "dorosly", "opiekun,szkolenie,ubezpieczenie", "Od 18 lat, spokojne osoby.", "zatwierdzone", 25),
    (2, "instytucja", "Dom Pomocy Społecznej w Myślenicach (PRZYKŁAD)", "hospicjum", "Wspólne śpiewanie i gry planszowe",
     "Raz w tygodniu mieszkańcy DPS grają w planszówki i śpiewają. Chętnie przyjmiemy pomocników do rozdawania kart i prowadzenia gier.",
     "Grasz w gry z seniorami. Śpiewacie razem. Pani z DPS pomaga.",
     "myślenicki", "sr,popoludnie", 3, "mlodziez,dorosly", "opiekun,kamizelka,ubezpieczenie", "", "zatwierdzone", 20),
    (1, "instytucja", "Świetlica „Tęcza” w Krzeszowicach (PRZYKŁAD)", "dzieci", "Starszy kolega na zajęciach plastycznych",
     "Dzieci 5–8 lat malują i kleją. Potrzebujemy starszego kolegi, który pomoże rozdać farby i pochwali prace.",
     "Pomagasz małym dzieciom malować. Rozdajesz farby. Chwalisz obrazki.",
     "krakowski", "pt,popoludnie", 2, "mlodziez,dorosly", "opiekun,szkolenie,ubezpieczenie", "", "zatwierdzone", 18),
    (2, "instytucja", "Przedszkole integracyjne nr 3 w Wadowicach (PRZYKŁAD)", "dzieci", "Pomoc przy podwieczorku i czytaniu bajek",
     "Przedszkolaki uwielbiają, gdy ktoś starszy czyta im bajkę. Pomoc przy podwieczorku raz w tygodniu.",
     "Czytasz bajkę dzieciom. Pomagasz przy podwieczorku. Pani jest obok.",
     "wadowicki", "pn,sr,rano", 2, "dorosly", "opiekun,ubezpieczenie", "", "zatwierdzone", 14),
    (1, "instytucja", "Biblioteka Publiczna w Myślenicach (PRZYKŁAD)", "inne", "Układanie książek i naklejanie kodów",
     "Spokojna praca w czytelni: układanie zwróconych książek na półkach i naklejanie kodów na nowe egzemplarze.",
     "Układasz książki na półkach. Naklejasz kody. Jest cicho i spokojnie.",
     "myślenicki", "wt,cz,rano", 2, "mlodziez,dorosly", "opiekun,szkolenie", "", "zatwierdzone", 12),
    (0, "rodzic", "Schronisko w Krakowie – propozycja rodzica (PRZYKŁAD)", "psy", "Syn uwielbia psy – czy schronisko przyjmie pomoc?",
     "Mój syn (16 lat) chętnie wyprowadzałby psy. Proszę Hub o kontakt ze schroniskiem.", "",
     "Kraków", "sb", 1, "mlodziez", "", "", "nowe", 3),
]
# (indeks użytkownika, role, alias, powiat, age_group, interests, days, companion, source, status, dni temu)
VOLUNTEERS = [
    (0, "uczestnik", "Ania", "wadowicki", "dorosly", "psy,koty,muzyka", "sb,nd,rano", "rodzic", "latwy-tekst", "polaczone", 28),
    (0, "uczestnik", "Kuba", "Kraków", "dorosly", "starsi,ksiazki", "wt,cz,popoludnie", "buddy", "rodzic", "polaczone", 22),
    (6, "uczestnik", "Marysia", "myślenicki", "mlodziez", "dzieci,muzyka,sport", "sr,pt,popoludnie", "rodzic", "rodzic", "nowe", 9),
    (6, "uczestnik", "Tomek", "wadowicki", "mlodziez", "psy,sport", "sb,rano", "asystent", "rodzic", "nowe", 6),
    (0, "uczestnik", "Ola", "krakowski", "dorosly", "dzieci,ksiazki,kuchnia", "pt,popoludnie", "buddy", "latwy-tekst", "nowe", 4),
    (3, "buddy", "Kasia – studentka", "Kraków", "", "", "wt,cz,sb,popoludnie", "", "buddy", "polaczone", 26),
    (3, "buddy", "Pan Józef – emeryt", "krakowski", "", "", "pn,wt,sr,cz,pt,popoludnie", "", "buddy", "nowe", 15),
    (3, "buddy", "Michał – harcerz", "wadowicki", "", "", "sb,nd,rano", "", "buddy", "nowe", 10),
]
# (indeks uczestnika w VOLUNTEERS, indeks oferty w OFFERS, indeks buddy w VOLUNTEERS albo None, done, dni temu)
MISSIONS = [(0, 0, None, 3, 21), (1, 1, 5, 1, 15)]
