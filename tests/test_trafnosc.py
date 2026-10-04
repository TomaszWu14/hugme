"""Test trafności matchmakingu: opis problemu → oczekiwana innowacja w top 3.
Metryka: odsetek trafień w top 3 (hit@3). Próg zaliczenia: >= 80%."""
from core.match import Index, Result, detect_area, innovation_text
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

# Zdania z audytu jury (T-1, J3-10): potoczny język mieszkańca, bez słów ze słownika.
SENIORKA = {"Telefon Życzliwości", "Dzienny Dom Seniora w remizie"}
AUDIT_CASES = [
    ("Moja mama ma 82 lata i mieszka sama na wsi, prawie z nikim nie rozmawia", SENIORKA),
    ("Babcia mieszka sama na wsi i jest jej smutno", SENIORKA),
    ("Depresja u nastolatków w małej gminie, brak psychologa",
     {"Przyjaciel na Ławce", "Szkolny Punkt Pierwszego Kontaktu"}),
    ("Mój syn ma 22 lata i zespół Downa, szukamy pierwszej pracy", {"Kawiarnia Treningowa „Po Szkole”"}),
    ("W gminie brakuje transportu do lekarza dla osób z niepełnosprawnością", {"Bus na Telefon"}),
]
CASES += AUDIT_CASES


def top3(query):
    return [DOCS[r.doc_id]["title"] for r in INDEX.search(query, k=3)]


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


def test_every_audit_sentence_hits_top_3():
    misses = [(q, top3(q)) for q, expected in AUDIT_CASES if not expected & set(top3(q))]
    assert not misses


def test_teen_depression_shows_both_youth_innovations():
    assert {"Przyjaciel na Ławce", "Szkolny Punkt Pierwszego Kontaktu"} <= set(top3(AUDIT_CASES[2][0]))


def test_lonely_mother_from_jury_gets_loneliness_not_transport():
    q = ("Moja mama ma 82 lata i mieszka sama na wsi pod Limanową. Od śmierci taty prawie z nikim nie rozmawia, "
         "dzieci są daleko, a sąsiedzi rzadko zaglądają.")
    results = INDEX.search(q, k=3)
    assert "Telefon Życzliwości" in [DOCS[r.doc_id]["title"] for r in results]
    assert all("dojazd i transport" not in r.topics for r in results)


def test_explanation_skips_common_words():
    q = ("W naszej małej gminie coraz więcej nastolatków ma depresję. Psycholog bywa w szkole raz w tygodniu. "
         "Mój syn skończył szkołę i szuka pierwszej pracy.")
    shown = {w for r in INDEX.search(q, k=5) for w in r.words}
    assert not shown & {"gminie", "raz", "tygodniu", "pierwszej", "przed"}


def test_church_roof_has_no_good_match():
    results = INDEX.search("Dach zabytkowego kościoła przecieka", k=5)
    assert all(r.label == "Słabe dopasowanie" for r in results)


def test_same_percent_gives_same_label():
    by_percent = {}
    for s in (0.345, 0.349, 0.35, 0.354, 0.445, 0.449, 0.45, 0.595, 0.599, 0.6):
        r = Result(0, s)
        by_percent.setdefault(r.percent, set()).add(r.label)
    assert all(len(labels) == 1 for labels in by_percent.values()), by_percent
    assert Result(0, 0.349).label == "Może pasować"


def test_score_threshold_agrees_with_label():
    # Szablony i luki porównują score z progiem 0,35 – wynik musi być już zaokrąglony do pokazywanego %.
    for q, _ in CASES:
        for r in INDEX.search(q, k=10):
            assert r.score == r.percent / 100
            assert (r.score >= 0.35) == (r.label != "Słabe dopasowanie")
