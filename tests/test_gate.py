"""Bramka odwiedzających demo: obowiązkowe przedstawienie się, rejestr 90 dni, lista dla admina."""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app import create_app
from tests.conftest import csrf_of

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reset_demo

GOOD = {"first_name": "Anna", "last_name": "Kowalska", "company": "Acme Sp. z o.o.", "consent": "1"}


@pytest.fixture
def gated(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "g.db"), "SECRET_KEY": "t", "DEMO_MODE": True, "DEMO_VISITOR_GATE": True})
    return app


@pytest.fixture
def gc(gated):
    return gated.test_client()


def visitors(app):
    con = sqlite3.connect(app.config["DATABASE"])
    try:
        return con.execute("SELECT first_name, last_name, company FROM demo_visitors ORDER BY id").fetchall()
    finally:
        con.close()


def submit(client, **over):
    token = csrf_of(client, "/wejscie")
    data = {**GOOD, **over, "_csrf": token, "next": "/biblioteka"}
    return client.post("/wejscie", data={k: v for k, v in data.items() if v is not None})


def test_exempt_paths_open_and_pages_redirect(gc):
    assert gc.get("/zdrowie").status_code == 200
    assert gc.get("/api/v1/health").status_code != 302
    r = gc.get("/biblioteka?x=1")
    assert r.status_code == 302 and r.headers["Location"].startswith("/wejscie?next=")
    assert "przedstaw się, proszę" in gc.get("/wejscie").get_data(as_text=True)


def test_gate_hides_owner_email_from_scrapers(gc):
    html = gc.get("/wejscie").get_data(as_text=True)
    assert "tomasz.wierzbowski@op.pl" not in html
    assert "tomasz.wierzbowski [at] op.pl" in html


@pytest.mark.parametrize("over", [{"first_name": None}, {"last_name": " a "}, {"company": ""}, {"consent": None},
                                  {"first_name": "A\x00nna"}, {"company": "x" * 101}, {"first_name": "jan@x.pl"}])
def test_missing_or_bad_data_is_refused(gated, gc, over):
    assert submit(gc, **over).status_code == 422
    assert visitors(gated) == []
    assert gc.get("/biblioteka").status_code == 302


def test_honeypot_is_refused(gated, gc):
    assert submit(gc, website="http://spam").status_code == 400
    assert visitors(gated) == []


def test_valid_registration_stores_and_admits(gated, gc):
    r = submit(gc, first_name="  Anna  ")
    assert r.status_code == 302 and r.headers["Location"] == "/biblioteka"
    assert visitors(gated) == [("Anna", "Kowalska", "Acme Sp. z o.o.")]
    cookie = r.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie and "Max-Age=2592000" in cookie
    assert gc.get("/biblioteka").status_code == 200


def test_tampered_cookie_does_not_admit(gc):
    gc.set_cookie("visitor_ok", "podrobione")
    assert gc.get("/biblioteka").status_code == 302


def test_demo_reset_keeps_visitors(gated, gc):
    submit(gc)
    con = reset_demo.db.connect(gated.config["DATABASE"])
    try:
        assert reset_demo.reset(con, force=True) is True
    finally:
        con.close()
    assert len(visitors(gated)) == 1


def test_retention_deletes_old_records_on_write(gated, gc):
    old = (datetime.now(timezone.utc) - timedelta(days=91)).strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(gated.config["DATABASE"])
    con.execute("INSERT INTO demo_visitors (created_at, first_name, last_name, company) VALUES (?, 'Stary', 'Wpis', 'Firma')", (old,))
    con.commit()
    con.close()
    submit(gc)
    assert visitors(gated) == [("Anna", "Kowalska", "Acme Sp. z o.o.")]


def test_list_only_for_admin_newest_first(gated, gc):
    submit(gc, first_name="Pierwsza")
    submit(gc, first_name="Druga")
    assert gc.get("/admin/odwiedzajacy").status_code == 302  # gość -> wybór konta
    token = csrf_of(gc, "/konto")
    gc.post("/konto", data={"_csrf": token, "user_id": 1})  # mieszkaniec
    gc.get("/")  # pierwsze żądanie po zmianie konta przekierowuje zamiast 403 (#20)
    assert gc.get("/admin/odwiedzajacy").status_code == 403
    gc.post("/konto", data={"_csrf": csrf_of(gc, "/"), "user_id": 5})  # admin
    html = gc.get("/admin/odwiedzajacy").get_data(as_text=True)
    assert html.index("Druga") < html.index("Pierwsza")


def test_clause_mentions_activity_record(gc):
    html = gc.get("/wejscie").get_data(as_text=True)
    assert ("powiadomień push ntfy. Zapisuję też, ile i jakie ekrany wersji demonstracyjnej obejrzałeś (bez adresu IP), "
            "żeby wiedzieć, co zainteresowało gości. Poza tym nikomu danych nie przekazuję.") in html
    assert ("via the ntfy push notification service. I also record how many and which screens of the demo you viewed "
            "(without your IP address) to see what visitors find interesting. Apart from that I do not share") in html
    assert "push ntfy; poza tym" not in html
