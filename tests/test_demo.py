"""Publiczne demo (DEMO_MODE): konta z paska „Tryb demo” nie do zepsucia, odnawianie bazy po ciszy."""
import re
import sys
from datetime import timedelta
from pathlib import Path

from app import create_app
from conftest import login
from core import db

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reset_demo  # noqa: E402


def test_demo_accounts_locked_only_in_demo_mode(tmp_path):
    for demo, expected in ((True, 1), (False, 0)):
        app = create_app({"TESTING": True, "DATABASE": str(tmp_path / f"{demo}.db"), "SECRET_KEY": "t", "DEMO_MODE": demo,
                          "DEMO_ACCOUNTS": True})
        client = app.test_client()
        token = login(client, "admin")
        client.post("/admin/uzytkownicy/1/blokada", data={"_csrf": token})
        r = client.post("/admin/uzytkownicy/2", data={"_csrf": token, "name": "Marta – Fundacja", "role": "gmina"})
        client.post("/admin/uzytkownicy/6/blokada", data={"_csrf": token})  # konto spoza paska demo – zawsze można
        with app.app_context():
            assert db.one("SELECT is_active FROM users WHERE id = 1")[0] == expected
            assert (db.one("SELECT role FROM users WHERE id = 2")[0] == "ngo") == demo
            assert db.one("SELECT is_active FROM users WHERE id = 6")[0] == 0
        assert (r.status_code == 422) == demo


def test_reset_waits_for_quiet_and_keeps_ai_counter(app):
    with app.app_context():
        con = db.get_db()
        con.execute("INSERT INTO reports (body, created_at) VALUES ('mój wpis sprzed chwili', ?)", (db.now(),))
        con.execute("INSERT INTO ai_usage (day, calls) VALUES ('2026-10-03', 42)")
        con.commit()
        assert reset_demo.reset(con) is False                    # świeży wpis – oglądający jeszcze klika
        later = reset_demo.last_write(con) + timedelta(minutes=21)
        assert reset_demo.reset(con, now=later) is True
        assert not con.execute("SELECT 1 FROM reports WHERE body = 'mój wpis sprzed chwili'").fetchone()
        assert con.execute("SELECT name FROM users WHERE id = 1").fetchone()[0].startswith("Anna")
        assert con.execute("SELECT calls FROM ai_usage").fetchone()[0] == 42


def test_home_demo_buttons_and_reset_note_only_in_demo_mode(tmp_path):
    on = create_app({"TESTING": True, "DATABASE": str(tmp_path / "on.db"), "SECRET_KEY": "t", "DEMO_MODE": True}).test_client()
    off = create_app({"TESTING": True, "DATABASE": str(tmp_path / "off.db"), "SECRET_KEY": "t"}).test_client()
    html = on.get("/").get_data(as_text=True)
    assert 'action="/demo/rodzic/1"' in html and 'action="/demo/gmina/1"' in html
    assert "nie mają haseł" in html and "odnawia się samo" in html and "odnawia się" in on.get("/konto").get_data(as_text=True)
    html = off.get("/").get_data(as_text=True)
    assert 'action="/demo/gmina/1"' in html and "nie mają haseł" in html and "odnawia się" not in html
    assert "Oglądasz demo?" not in html  # dawna ramka zastąpiona przyciskami scenariuszy


def test_account_switcher_only_with_demo_accounts(tmp_path, monkeypatch):
    """Issue #15: bez DEMO_MODE=1 (ani DEMO_ACCOUNTS=1) nikt nie wybierze konta – także admina."""
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.delenv("DEMO_ACCOUNTS", raising=False)
    off = create_app({"TESTING": True, "DATABASE": str(tmp_path / "off.db"), "SECRET_KEY": "t"})
    client = off.test_client()
    html = client.get("/").get_data(as_text=True)
    token = re.search(r'name="_csrf" value="([^"]+)"', html).group(1)
    assert 'id="role-switch"' not in html
    assert client.get("/konto").status_code == 404
    assert client.post("/konto", data={"_csrf": token, "user_id": 5}).status_code == 404
    assert client.post("/demo/gmina/1", data={"_csrf": token}).status_code == 404
    with client.session_transaction() as s:
        assert "uid" not in s
    assert client.get("/admin").status_code != 200

    monkeypatch.setenv("DEMO_MODE", "1")
    on = create_app({"TESTING": True, "DATABASE": str(tmp_path / "on.db"), "SECRET_KEY": "t"}).test_client()
    login(on, "admin")
    assert on.get("/admin").status_code == 200
