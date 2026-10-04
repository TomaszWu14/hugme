"""Demo prowadzące jury (app/scenariusze.py, app/views/demo.py): każdy krok obu scenariuszy prowadzi
na żywy ekran z paskiem kroku i na właściwe konto; martwa ścieżka albo zły tytuł = czerwony test."""
import pytest
from markupsafe import escape

from app.scenariusze import BARTEK, BUS, GMINA_OPIS, SCENARIUSZE
from app.views.komunikacja import short
from core import db
from conftest import csrf_of, login
from test_podpowiedzi import sentences

STEPS = [(sid, n) for sid, s in SCENARIUSZE.items() for n in range(1, len(s["kroki"]) + 1)]


def go(client, sid, n):
    return client.post(f"/demo/{sid}/{n}", data={"_csrf": csrf_of(client, "/demo")})


@pytest.mark.parametrize("sid,n", STEPS)
def test_each_step_opens_live_page_with_bar_on_right_account(client, sid, n):
    kroki = SCENARIUSZE[sid]["kroki"]
    st = kroki[n - 1]
    r = go(client, sid, n)
    assert r.status_code == 302 and r.headers["Location"] == st["path"]
    page = client.get(st["path"])
    html = page.get_data(as_text=True)
    assert page.status_code == 200, st["path"]
    assert f"Krok {n} z {len(kroki)}" in html and str(escape(st["tytul"])) in html
    assert 'aria-label="Scenariusz demo"' in html and 'id="przewodnik-dane"' not in html  # jeden przewodnik naraz
    with client.session_transaction() as s:
        assert s.get("uid") == st["uid"] and s["scen"] == [sid, n]


@pytest.mark.parametrize("sid,n", STEPS)
def test_step_texts_are_short(sid, n):
    st = SCENARIUSZE[sid]["kroki"][n - 1]
    assert sentences(st["tekst"]) <= 2, st["tekst"]


def test_bar_buttons_back_next_and_end(client):
    go(client, "gmina", 1)
    html = client.get("/").get_data(as_text=True)
    assert 'action="/demo/gmina/0"' not in html and 'action="/demo/gmina/2"' in html
    assert ": " + str(escape(SCENARIUSZE["gmina"]["kroki"][1]["tytul"])) + "</span>" in html and 'action="/demo/koniec"' in html
    last = len(SCENARIUSZE["gmina"]["kroki"])
    go(client, "gmina", last)
    html = client.get(SCENARIUSZE["gmina"]["kroki"][-1]["path"]).get_data(as_text=True)
    assert f'action="/demo/gmina/{last - 1}"' in html and "Zakończ scenariusz" in html and "Dalej:" not in html


def test_bad_step_404_and_csrf_400(client):
    token = csrf_of(client, "/demo")
    for path in ("/demo/nie-ma/1", "/demo/rodzic/0", f"/demo/rodzic/{len(SCENARIUSZE['rodzic']['kroki']) + 1}"):
        assert client.post(path, data={"_csrf": token}).status_code == 404, path
    assert client.post("/demo/rodzic/1").status_code == 400
    assert client.post("/demo/koniec").status_code == 400


def test_end_clears_scenario_and_brings_back_tour(client):
    go(client, "gmina", 1)
    r = client.post("/demo/koniec", data={"_csrf": csrf_of(client, "/demo")})
    assert r.status_code == 302 and r.headers["Location"] == "/demo"
    with client.session_transaction() as s:
        assert "scen" not in s
    html = client.get("/").get_data(as_text=True)
    assert 'aria-label="Scenariusz demo"' not in html and 'id="przewodnik-dane"' in html


def test_scenario_survives_manual_account_switch_and_does_not_skip_on_wrong_account(client):
    go(client, "rodzic", 3)
    login(client, "ngo")
    client.get("/admin/potrzebny")  # ekran kroku 4, ale konto nie to – krok się nie zmienia
    with client.session_transaction() as s:
        assert s["scen"] == ["rodzic", 3] and s["uid"] == 2


def test_demo_page_lists_both_scenarios(client):
    html = client.get("/demo").get_data(as_text=True)
    for sid, s in SCENARIUSZE.items():
        assert f'action="/demo/{sid}/1"' in html and str(escape(s["tytul"])) in html
    assert html.count("Rozpocznij") == len(SCENARIUSZE)


def test_home_is_four_blocks_with_two_scenario_buttons(client):
    html = client.get("/").get_data(as_text=True)
    assert 'action="/demo/rodzic/1"' in html and 'action="/demo/gmina/1"' in html
    assert "Wyzwania Małopolski" not in html and "Wyzwania Małopolski" in client.get("/wiedza").get_data(as_text=True)


def test_gmina_flow_prefills_problem_and_finds_bus(client):
    go(client, "gmina", 1)
    html = client.get("/").get_data(as_text=True)
    assert str(escape(GMINA_OPIS)) in html
    client.post("/szukaj", data={"_csrf": csrf_of(client, "/"), "opis": GMINA_OPIS})
    html = client.get("/wyniki").get_data(as_text=True)
    assert "Krok 2 z " in html  # akcja z kroku 1 prowadzi na ekran kroku 2 – pasek przechodzi sam
    first = html[html.index('class="card card--thread'):]
    assert first.index("Bus na Telefon") < first.index("</article>") and "Bardzo pasuje" in first[:first.index("</article>")]
    assert "Bus na Telefon" in client.get(f"/biblioteka/{BUS}").get_data(as_text=True)
    assert "Chcemy wdrożyć u nas: Bus na Telefon" in client.get(f"/posrednik?inspiracja={BUS}").get_data(as_text=True)


def test_rodzic_flow_signup_becomes_pair_for_shelter(client):
    go(client, "rodzic", 2)
    token = csrf_of(client, "/razem/jestem-potrzebny/zglos")
    r = client.post("/razem/jestem-potrzebny/zglos", data={
        "_csrf": token, "alias": "Bartek", "powiat": "wadowicki", "age_group": "dorosly", "interests": "psy",
        "days": ["sb", "rano"], "companion": "rodzic", "consent": "1"})
    assert r.status_code == 302
    html = client.get("/razem/jestem-potrzebny/dzienniczek").get_data(as_text=True)
    assert "Bartek" in html and "Krok 3 z " in html
    go(client, "rodzic", 4)
    html = client.get("/admin/potrzebny").get_data(as_text=True)
    pairs = html[html.index('id="pary-h"'):html.index('id="sprawdz-h"')]
    assert "<strong>Bartek</strong>" in pairs and "Schronisko dla zwierząt w Wadowicach" in pairs


def test_admin_nav_five_items_rest_under_more(client):
    login(client, "admin")
    html = client.get("/admin").get_data(as_text=True)
    nav = html[html.index('class="no-print admin-nav"'):html.index("</nav>", html.index('class="no-print admin-nav"'))]
    desktop = nav[nav.index('class="nav nav-d'):nav.index("</ul>", nav.index('class="nav nav-d'))]
    assert desktop.count("<li>") == 5 and "Skrzynka" in desktop and "Kolejka e-mail" not in desktop
    assert '<details class="admin-nav__more">' in nav and "Więcej" in nav and "Kolejka e-mail" in nav
    html = client.get("/admin/nabory").get_data(as_text=True)
    assert '<details class="admin-nav__more" open>' in html  # bieżąca strona jest w „Więcej” – lista otwarta


def test_action_step_has_small_next_and_cel_only_on_its_screen(client):
    go(client, "rodzic", 2)  # krok z akcją (formularz): „Dalej” nie kusi do pominięcia
    html = client.get("/razem/jestem-potrzebny/zglos").get_data(as_text=True)
    assert 'class="btn btn--small"><span>Dalej<span' in html and 'data-cel="form.card"' in html
    html = client.get("/razem").get_data(as_text=True)  # inny ekran – nic nie obwodzimy
    assert 'data-cel=""' in html
    go(client, "rodzic", 1)
    assert 'class="btn btn--primary"><span>Dalej<span' in client.get("/razem/jestem-potrzebny").get_data(as_text=True)


def test_skipped_signup_still_shows_bartek_for_hub(client, app):
    go(client, "rodzic", 4)  # jury kliknęło „Dalej” bez wysłania formularza z kroku 2
    go(client, "rodzic", 3)  # drugi raz nie tworzy drugiego Bartka
    with app.app_context():
        rows = db.query("SELECT user_id FROM volunteers WHERE alias = ?", (BARTEK["alias"],))
        assert [r["user_id"] for r in rows] == [SCENARIUSZE["rodzic"]["kroki"][1]["uid"]]  # jeden, na koncie mamy
    go(client, "rodzic", 4)
    html = client.get("/admin/potrzebny").get_data(as_text=True)
    assert 'data-alias="Bartek"' in html


def test_gmina_step2_ignores_older_search(client):
    client.post("/szukaj", data={"_csrf": csrf_of(client, "/"), "opis": "Rodzice dzieci z autyzmem nie mają gdzie szukać wsparcia."})
    go(client, "gmina", 1)
    go(client, "gmina", 2)
    html = client.get("/wyniki").get_data(as_text=True)
    first = html[html.index('class="card card--thread'):]
    assert first.index("Bus na Telefon") < first.index("</article>")


def test_short_cuts_on_word_without_hanging_dash():
    assert short(GMINA_OPIS) == "Seniorzy z pięciu sołectw nie mają jak dojechać do lekarza…"
    assert short("krótko") == "krótko"
