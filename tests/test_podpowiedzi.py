"""Tryb „Podpowiedzi”: kompletność tekstów (app/podpowiedzi.json), makra i przełącznik w ciasteczku."""
import re
from pathlib import Path

import pytest

from app import auth, podpowiedzi
from conftest import csrf_of

ROOT = Path(__file__).resolve().parent.parent
DATA = podpowiedzi.data()
INTEGRATED = "podpowiedzi" in auth.PREF_COOKIES
NOT_YET = pytest.mark.skipif(not INTEGRATED, reason="czeka na integrację: PREF_COOKIES['podpowiedzi'] i init(app)")

# help('k'), help_i('k'), field(..., help='k') oraz data-help="k" – klucze wpisane na stałe w szablonach
KEY_IN_TEMPLATE = re.compile(r"""(?:\bhelp\w*\(\s*|\bhelp\s*=\s*|data-help=)["']([a-z0-9_]+\.[a-z0-9_.]+)["']""")
ABBREV = re.compile(r"\b(?:np|ok|tzw|itp|itd|tj|m\.in|ul|godz|min|r)\.", re.I)
SENTENCE_END = re.compile(r"[.!?…][”\"»)]*(?=\s|$)")


def sentences(text):
    text = ABBREV.sub("", text).strip()
    return len(SENTENCE_END.findall(text)) + (0 if SENTENCE_END.search(text[-3:]) else 1)


def template_keys():
    keys = set()
    for path in (ROOT / "app" / "templates").rglob("*.html"):
        keys |= {(k, path.name) for k in KEY_IN_TEMPLATE.findall(path.read_text(encoding="utf-8"))}
    return keys


@pytest.mark.parametrize("key", sorted(DATA["pola"]))
def test_each_hint_has_three_short_parts(key):
    h = DATA["pola"][key]
    assert h.get("nazwa"), key
    second = h.get("przyklad") or h.get("jak_czytac")
    for part in (h.get("po_co"), second, h.get("zrodlo")):
        assert part, f"{key}: brak części (po_co / przyklad|jak_czytac / zrodlo)"
        assert sentences(part) <= 2, f"{key}: więcej niż 2 zdania: {part}"


def test_keys_used_in_templates_exist():
    missing = sorted(f"{k} ({f})" for k, f in template_keys() if k not in DATA["pola"])
    assert not missing, f"Brak w app/podpowiedzi.json: {missing}"


def test_tour_steps_point_to_existing_keys_and_endpoints(app):
    for endpoint, steps in DATA["przewodnik"].items():
        assert endpoint in app.view_functions, f"Nie ma widoku {endpoint}"
        assert 3 <= len(steps) <= 7, endpoint
        for s in steps:
            assert s["klucz"] in DATA["pola"], f"{endpoint}: {s['klucz']}"
            assert s["tytul"] and s["tekst"]


def render(app, source, path="/", cookies=None):
    podpowiedzi.init(app)  # do czasu integracji w create_app; podwójne wywołanie jest nieszkodliwe
    headers = {"Cookie": "; ".join(f"{k}={v}" for k, v in (cookies or {}).items())} if cookies else {}
    with app.test_request_context(path, headers=headers):
        return app.jinja_env.from_string('{% from "_podpowiedzi.html" import help, toggle, tour %}' + source).render()


def test_help_macro_renders_details_and_respects_cookie(app):
    html = render(app, "{{ help('home.opis') }}")
    assert '<details class="help" data-help-for="home.opis">' in html
    assert "Podpowiedź: Opis sytuacji" in html and "Skąd to się bierze" in html
    assert render(app, "{{ help('home.opis') }}", cookies={"hints_off": "1"}).strip() == ""
    assert render(app, "{{ help('') }}").strip() == ""


def test_help_macro_unknown_key_fails_in_tests(app):
    with pytest.raises(KeyError):
        render(app, "{{ help('nie.ma.takiego') }}")


def test_toggle_and_tour_macros(app):
    html = render(app, "{{ toggle() }}{{ tour() }}")
    assert 'name="pref" value="podpowiedzi"' in html and 'aria-pressed="true"' in html and "Podpowiedzi: wł." in html
    assert 'id="przewodnik-start" hidden' in html and 'type="application/json" id="przewodnik-dane"' in html
    off = render(app, "{{ toggle() }}{{ tour() }}", cookies={"hints_off": "1"})
    assert "Podpowiedzi: wył." in off and "przewodnik-dane" not in off
    assert "przewodnik-dane" not in render(app, "{{ tour() }}", path="/prywatnosc")  # widok bez kroków


@NOT_YET
def test_toggle_cookie_on_off(client):
    assert "Podpowiedzi: wł." in client.get("/").get_data(as_text=True)  # domyślnie włączone
    token = csrf_of(client)
    client.post("/ustawienia", data={"_csrf": token, "pref": "podpowiedzi", "next": "/"})
    assert client.get_cookie("hints_off").value == "1"
    assert "Podpowiedzi: wył." in client.get("/").get_data(as_text=True)
    client.post("/ustawienia", data={"_csrf": token, "pref": "podpowiedzi", "next": "/"})
    assert client.get_cookie("hints_off") is None
    assert "Podpowiedzi: wł." in client.get("/").get_data(as_text=True)


@NOT_YET
def test_home_shows_hints_only_when_on(client):
    assert 'class="help"' in client.get("/").get_data(as_text=True)
    client.set_cookie("hints_off", "1")
    assert 'class="help"' not in client.get("/").get_data(as_text=True)
