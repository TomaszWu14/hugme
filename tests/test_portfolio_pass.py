"""Przepustka z portfolio (ciasteczko gosc): ważna = bez bramki, inaczej formularz jak dotąd. Zero prawdziwej sieci."""
import sqlite3
import urllib.error

import pytest

from app import create_app, portfolio_pass


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    portfolio_pass._cache.clear()
    monkeypatch.delenv("PORTFOLIO_PASS", raising=False)
    monkeypatch.delenv("PORTFOLIO_URL", raising=False)


@pytest.fixture
def gated(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "p.db"), "SECRET_KEY": "t", "DEMO_MODE": True,
                       "DEMO_VISITOR_GATE": True})


@pytest.fixture
def calls(monkeypatch):
    seen = []
    status = {"code": 200}

    def fake(base, token):
        seen.append((base, token))
        return status["code"]

    monkeypatch.setattr(portfolio_pass, "_status", fake)
    return seen, status


def rows(app):
    con = sqlite3.connect(app.config["DATABASE"])
    try:
        return con.execute("SELECT first_name, last_name, company FROM demo_visitors").fetchall()
    finally:
        con.close()


def test_valid_pass_skips_gate_without_personal_data_or_push(gated, calls, monkeypatch):
    sent = []
    monkeypatch.setattr("app.gate.notify_visitor", lambda *a: sent.append(a))
    seen, _ = calls
    c = gated.test_client()
    c.set_cookie("gosc", "tok123")
    r = c.get("/biblioteka")
    assert r.status_code == 200 and "visitor_ok=" in r.headers["Set-Cookie"]
    assert rows(gated) == [("Gość z portfolio", "", "")] and sent == []
    assert seen == [("https://portfolio.twapp.pl", "tok123")]
    assert c.get("/biblioteka").status_code == 200 and len(seen) == 1  # kolejne żądania: ciasteczko demo


def test_gate_page_with_valid_pass_redirects_and_has_no_pixel(gated, calls):
    c = gated.test_client()
    c.set_cookie("gosc", "tok")
    r = c.get("/wejscie?next=/biblioteka")
    assert r.status_code == 302 and r.headers["Location"] == "/biblioteka"
    anon = gated.test_client().get("/wejscie").get_data(as_text=True)
    assert "/px/hugme" not in anon and "przedstaw się, proszę" in anon


def test_pixel_stays_on_app_pages(app):
    assert "/px/hugme" in app.test_client().get("/").get_data(as_text=True)


@pytest.mark.parametrize("code", [401, 500, None])
def test_refused_or_failed_check_shows_form(gated, calls, code):
    _, status = calls
    status["code"] = code
    c = gated.test_client()
    c.set_cookie("gosc", "tok")
    r = c.get("/biblioteka")
    assert r.status_code == 302 and r.headers["Location"].startswith("/wejscie")
    assert rows(gated) == []


def test_no_cookie_or_bad_cookie_makes_no_network_call(gated, calls):
    seen, _ = calls
    c = gated.test_client()
    assert c.get("/biblioteka").status_code == 302
    c.set_cookie("gosc", "x" * 201)
    assert c.get("/biblioteka").status_code == 302
    assert seen == []


def test_disabled_or_insecure_url_makes_no_call(gated, calls, monkeypatch):
    seen, _ = calls
    c = gated.test_client()
    c.set_cookie("gosc", "tok")
    monkeypatch.setenv("PORTFOLIO_PASS", "0")
    assert c.get("/biblioteka").status_code == 302
    monkeypatch.delenv("PORTFOLIO_PASS")
    monkeypatch.setenv("PORTFOLIO_URL", "http://portfolio.local")
    assert c.get("/biblioteka").status_code == 302
    assert seen == []


def test_status_sends_only_gosc_cookie_and_maps_errors(monkeypatch):
    captured = {}

    class Resp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class Opener:
        def open(self, req, timeout):
            captured.update(cookie=req.get_header("Cookie"), timeout=timeout, url=req.full_url)
            return Resp()

    monkeypatch.setattr("urllib.request.build_opener", lambda *h: Opener())
    assert portfolio_pass._status("https://p.example", "abc") == 200
    assert captured == {"cookie": "gosc=abc", "timeout": 2, "url": "https://p.example/api/gosc"}

    class Boom:
        def open(self, req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "no", {}, None)

    monkeypatch.setattr("urllib.request.build_opener", lambda *h: Boom())
    assert portfolio_pass._status("https://p.example", "abc") == 401

    class Down:
        def open(self, req, timeout):
            raise TimeoutError("secret-token")

    monkeypatch.setattr("urllib.request.build_opener", lambda *h: Down())
    assert portfolio_pass._status("https://p.example", "abc") is None
