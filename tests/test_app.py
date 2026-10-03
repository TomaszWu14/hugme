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


def test_area_css_from_domain(client):
    css = client.get("/obszary.css").get_data(as_text=True)
    assert ".thread--rodziny-zd{--thread:#7A3E9D}" in css


def test_friendly_404(client):
    resp = client.get("/nie-ma-takiej")
    assert resp.status_code == 404 and "Nie ma takiej strony" in resp.get_data(as_text=True)


def test_logout(client):
    token = login(client, "mieszkaniec")
    client.post("/konto/wyloguj", data={"_csrf": token})
    assert "Wyloguj" not in client.get("/").get_data(as_text=True)
