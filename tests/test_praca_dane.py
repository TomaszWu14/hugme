"""Spójność danych mapy pracy: każde miejsce ma źródło i poprawny region; kontury pokrywają wszystkie regiony."""
import re

from core.domain import POWIATY
from data import mapa, praca as W


def test_every_workplace_has_https_source_and_valid_region():
    for name, kind, city, woj, powiat, url, note, checked in W.WORKPLACES:
        assert url.startswith("https://"), name
        assert kind in W.KINDS, name
        assert woj in W.VOIVODESHIPS, name
        assert powiat is None or (powiat in POWIATY and woj == "malopolskie"), name
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", checked), name
        assert note and len(name) >= 3


def test_stats_and_content_have_sources():
    for row in W.STATS + W.EXPECTATIONS + W.MYTHS:
        assert row[-1].startswith("https://"), row[0]
    assert W.INTERESTS_NOTE[2].startswith("https://")
    assert len(W.MYTHS) >= 5 and len(W.HOW_TO_TALK) >= 5


def test_map_paths_cover_all_regions():
    assert len(mapa.WOJEWODZTWA) == 16 and len({w[0] for w in mapa.WOJEWODZTWA}) == 16
    assert [p[1] for p in mapa.POWIATY_MALOPOLSKA] == POWIATY
    for slug, name, path, cx, cy in mapa.WOJEWODZTWA + mapa.POWIATY_MALOPOLSKA:
        assert path.startswith("M") and path.endswith("Z") and len(path) > 40, name
        assert 0 <= cx <= 600 and 0 <= cy <= 560, name
