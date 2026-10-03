"""Test trafności matchmakingu: opis problemu → oczekiwana innowacja w top 3.
Metryka: odsetek trafień w top 3 (hit@3). Próg zaliczenia: >= 80%."""
from core.match import Index, detect_area, innovation_text
from data.seed_data import INNOVATIONS

FIELDS = ("title", "summary", "description", "area", "powiat", "stage", "audience", "org", "keywords")
DOCS = [dict(zip(FIELDS, row)) for row in INNOVATIONS]
INDEX = Index([(i, innovation_text(d)) for i, d in enumerate(DOCS)])

CASES = [
    ("Mamy dziecko z zespołem Downa i jeździmy do kardiologa, logopedy i endokrynologa w różne dni. Nie dajemy rady z terminami.",
     {"Asystent zdrowia rodziny", "Dzień Specjalistów w jednym miejscu"}),
    ("Jestem wykończona opieką, nie mam ani chwili na odpoczynek, nikt nie może zostać z synem.",
     {"Godziny dla rodzica – opieka wytchnieniowa", "Krąg Opiekunów"}),
    ("Córka skończyła szkołę specjalną i nie ma pracy, siedzi w domu.",
     {"Kawiarnia Treningowa „Po Szkole”"}),
    ("Dziecko idzie do zwykłej szkoły, boimy się, że klasa go nie przyjmie.",
     {"Klasa w Ruchu – integracja od pierwszego dnia"}),
    ("Nie wiemy, gdzie szukać ulg, turnusów i terapii dla dziecka z niepełnosprawnością.",
     {"Mapa Wsparcia Rodzin"}),
    ("Babcia mieszka sama na wsi i nie ma jak dojechać do lekarza, autobus nie jeździ.",
     {"Bus na Telefon", "Asystent Seniora na telefon", "Sąsiedzkie Dojazdy"}),
    ("Starsi sąsiedzi są samotni, nikt do nich nie dzwoni ani nie odwiedza.",
     {"Telefon Życzliwości", "Sąsiedzka Koperta Życia"}),
    ("Seniorzy nie umieją korzystać ze smartfona i e-recepty.",
     {"Cyfrowy Przewodnik w bibliotece", "Tablet z Bibliotecznej Półki"}),
    ("Nastolatki w szkole mają depresję i lęki, psycholog jest dostępny za pół roku.",
     {"Szkolny Punkt Pierwszego Kontaktu"}),
    ("Starsi mieszkańcy pięciu sołectw nie mają jak dojechać do przychodni.",
     {"Bus na Telefon", "Sąsiedzkie Dojazdy"}),
    ("Chcemy, żeby gmina, fundacje i firmy zaczęły razem współpracować przy usługach społecznych.",
     {"Gminne Laboratorium Innowacji", "Inkubator Partnerstw dla NGO"}),
]


def test_hit_at_3_at_least_80_percent():
    hits, misses = 0, []
    for query, expected in CASES:
        top = [DOCS[r.doc_id]["title"] for r in INDEX.search(query, k=3)]
        if expected & set(top):
            hits += 1
        else:
            misses.append((query[:50], top))
    rate = hits / len(CASES)
    print(f"\nTrafność hit@3: {hits}/{len(CASES)} = {rate:.0%}")
    assert rate >= 0.8, misses


def test_explanation_lists_shared_words_and_topics():
    r = INDEX.search(CASES[0][0], k=1)[0]
    assert r.words and r.topics
    assert any("zdrowie" in t for t in r.topics)


def test_good_match_scores_above_gap_threshold():
    assert INDEX.search(CASES[0][0], k=1)[0].score >= 0.45


def test_unrelated_text_is_a_gap():
    results = INDEX.search("Hałas z lotniska nad osiedlem w nocy", k=1)
    assert not results or results[0].score < 0.35


def test_detect_area():
    assert detect_area(CASES[0][0]) == "rodziny-zd"
    assert detect_area(CASES[5][0]) in {"wies", "seniorzy"}
