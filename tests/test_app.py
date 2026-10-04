import re
from conftest import csrf_of, login


def test_home_has_problem_field_and_example(client):
    html = client.get("/").get_data(as_text=True)
    assert "Co jest trudne? Kogo to dotyczy?" in html
    assert "zespołem Downa" in html
    assert 'href="#tresc"' in html  # skip link


def test_security_headers(client):
    resp = client.get("/")
    csp = resp.headers["Content-Security-Policy"]
    assert "script-src 'self'" in csp and "frame-ancestors 'none'" in csp
    assert resp.headers["X-Content-Type-Options"] == "nosniff"


def test_post_without_csrf_rejected(client):
    assert client.post("/konto", data={"user_id": 1}).status_code == 400


def test_demo_login_switches_role(client):
    token = csrf_of(client, "/konto")
    resp = client.post("/konto", data={"_csrf": token, "user_id": 5, "next": "/"})
    assert resp.status_code == 302
    assert "Panel Hubu" in client.get("/").get_data(as_text=True)


def test_open_redirect_blocked(client):
    token = csrf_of(client, "/konto")
    resp = client.post("/konto", data={"_csrf": token, "user_id": 1, "next": "//evil.example"})
    assert resp.headers["Location"] == "/"


def test_session_cookie_flags(client):
    token = csrf_of(client, "/konto")
    resp = client.post("/konto", data={"_csrf": token, "user_id": 1})
    cookie = resp.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_a11y_prefs_toggle_cookie(client):
    token = csrf_of(client)
    client.post("/ustawienia", data={"_csrf": token, "pref": "duzy-tekst", "next": "/"})
    assert 'class="a11y-size' in client.get("/").get_data(as_text=True)


def test_a11y_prefs_announce_state(client):
    # czytnik ekranu musi usłyszeć „wciśnięty” po włączeniu A+ / kontrastu (WCAG 4.1.2)
    pressed = lambda: re.findall(r'aria-pressed="(\w+)"', client.get("/").get_data(as_text=True))[:2]  # 3. przycisk to „Podpowiedzi”
    assert pressed() == ["false", "false"]
    for pref in ("duzy-tekst", "kontrast"):
        client.post("/ustawienia", data={"_csrf": csrf_of(client), "pref": pref, "next": "/"})
    assert pressed() == ["true", "true"]
    client.post("/ustawienia", data={"_csrf": csrf_of(client), "pref": "kontrast", "next": "/"})
    assert pressed() == ["true", "false"]


def test_area_css_from_domain(client):
    css = client.get("/obszary.css").get_data(as_text=True)
    assert ".thread--rodziny-zd{--thread:#7A3E9D;" in css
    # drugi kanał obok koloru: pary mylone przy daltonizmie mają różne wzory
    assert "repeating-linear-gradient" in css.split(".thread--seniorzy")[1].split("}")[0]
    assert "repeating-linear-gradient" not in css.split(".thread--wies")[1].split("}")[0]


def test_friendly_404(client):
    resp = client.get("/nie-ma-takiej")
    assert resp.status_code == 404 and "Nie ma takiej strony" in resp.get_data(as_text=True)


def test_logout(client):
    token = login(client, "mieszkaniec")
    client.post("/konto/wyloguj", data={"_csrf": token})
    assert "Wyloguj" not in client.get("/").get_data(as_text=True)


def test_health_endpoint(client):
    assert client.get("/zdrowie").get_json() == {"status": "ok"}


def test_heat_levels_are_absolute_not_relative():
    from core.domain import heat_level
    assert [heat_level(n) for n in (0, 1, 2, 3, 4, 6, 7, 30)] == [0, 1, 2, 2, 3, 3, 4, 4]


def test_no_emoji_used_as_icons_in_templates():
    import pathlib
    for f in pathlib.Path("app/templates").rglob("*.html"):
        text = f.read_text(encoding="utf-8")
        assert not any(ch in text for ch in "🛡👍👎"), f


def test_menu_shows_brief_modules_in_order_and_bell(client):
    # K-04: moduły z briefu jako pierwsze w menu, pilotaż na końcu; K-09: dzwonek poza zwiniętym menu
    html = client.get("/").get_data(as_text=True)
    nav = html[html.index('class="nav nav-d'):]
    names = ["Szukaj pomocy", "Zasobnik wiedzy", "Biblioteka innowacji", "Tester innowacji",
             "Kreator pomysłów", "Pośrednik innowacji", "Razem z ZD · pilotaż"]
    assert [nav.index(n) for n in names] == sorted(nav.index(n) for n in names)
    assert 'href="/powiadomienia"' not in html  # gość nie ma powiadomień
    login(client, "admin")
    html = client.get("/").get_data(as_text=True)
    bell = re.search(r'<a class="bell" href="/powiadomienia" aria-label="Powiadomienia(, nowe: \d+)?"', html)
    assert bell and bell.start() > html.index("</nav>")
    assert ">Panel Hubu<" in html


def test_home_wait_state_and_seven_modules(client):
    html = client.get("/").get_data(as_text=True)
    assert 'data-czekaj="Szukam rozwiązań' in html and "js/czekaj.js" in html
    assert "7 modułów HubMi" in html and html.count('class="mod"') == 7
    # Start w 4 blokach: hero → demo w 1,5 minuty → formularz → moduły; reszta jest w /wiedza i /razem
    order = [html.index(x) for x in ('id="hero-title"', 'id="demo-title"', 'id="ask-title"', 'id="mod-title"')]
    assert order == sorted(order)
    assert "Jak to działa" not in html and "Wyzwania Małopolski" not in html and 'id="razem-title"' not in html


def test_flash_sekcja_not_shown_on_top(app):
    # J2-01: komunikaty kategorii „sekcja” pokazuje sekcja docelowa, nie góra strony
    from flask import flash, render_template
    with app.test_request_context("/dostepnosc"):
        app.preprocess_request()
        flash("Wysłane do testu", "sekcja")
        flash("Zapisano", "success")
        html = render_template("dostepnosc.html")
    assert "Zapisano" in html and "Wysłane do testu" not in html
