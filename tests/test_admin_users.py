"""Panel Hubu: użytkownicy, role, blokada, macierz uprawnień, dziennik."""
from conftest import csrf_of, login
from core import db


def test_users_pages_admin_only(client):
    assert client.get("/admin/uzytkownicy").status_code == 302
    login(client, "ngo")
    assert client.get("/admin/uzytkownicy").status_code == 403 and client.get("/admin/role").status_code == 403
    login(client, "admin")
    html = client.get("/admin/uzytkownicy").get_data(as_text=True)
    assert "Koordynatorka ROPS" in html and "Anna – mama" in html
    assert client.get("/admin/uzytkownicy?rola=ekspert&q=Ewa").status_code == 200
    html = client.get("/admin/role").get_data(as_text=True)
    assert "Macierz uprawnień" in html and "Jestem potrzebny: oferta miejsca" in html


def test_change_role_and_log(client, app):
    token = login(client, "admin")
    r = client.post("/admin/uzytkownicy/2", data={"_csrf": token, "name": "Marta – Fundacja", "role": "gmina", "org": "Fundacja",
                                                  "areas": ["seniorzy"], "bio": "tel. 600 123 456"})
    assert r.status_code == 302
    with app.app_context():
        u = db.one("SELECT * FROM users WHERE id = 2")
        log = db.one("SELECT action FROM admin_log WHERE user_id = 2 ORDER BY id DESC")
    assert u["role"] == "gmina" and u["areas"] == "seniorzy" and "600 123 456" not in u["bio"]
    assert "rola Organizacja pozarządowa → Gmina (JST)" in log["action"]
    assert "Gmina (JST)" in client.get("/admin/uzytkownicy/2").get_data(as_text=True)


def test_cannot_demote_last_admin_or_block_self(client, app):
    token = login(client, "admin")
    r = client.post("/admin/uzytkownicy/5", data={"_csrf": token, "name": "Joanna", "role": "ngo"})
    assert r.status_code == 422 and "ostatnie aktywne konto Hubu" in r.get_data(as_text=True)
    client.post("/admin/uzytkownicy/5/blokada", data={"_csrf": token})
    with app.app_context():
        assert db.one("SELECT is_active FROM users WHERE id = 5")["is_active"] == 1


def test_blocked_account_cannot_be_used(client, app):
    token = login(client, "admin")
    client.post("/admin/uzytkownicy/3/blokada", data={"_csrf": token})
    with app.app_context():
        assert db.one("SELECT is_active FROM users WHERE id = 3")["is_active"] == 0
    html = client.get("/konto").get_data(as_text=True)
    assert "Piotr – Urząd Gminy" not in html  # zniknął z listy kont demo
    r = client.post("/konto", data={"_csrf": csrf_of(client, "/konto"), "user_id": 3}, follow_redirects=True)
    assert "zablokowane" in r.get_data(as_text=True)
    assert "Koordynatorka ROPS – Joanna" in client.get("/").get_data(as_text=True)  # sesja została przy adminie
    token = login(client, "admin")
    client.post("/admin/uzytkownicy/3/blokada", data={"_csrf": token})
    assert "Piotr – Urząd Gminy" in client.get("/konto").get_data(as_text=True)


def test_new_account_appears_in_demo_bar(client, app):
    token = login(client, "admin")
    r = client.post("/admin/uzytkownicy/nowy", data={"_csrf": token, "name": "Kasia – OPS Myślenice", "role": "gmina",
                                                     "org": "OPS Myślenice", "areas": ["rodziny-zd", "seniorzy"]})
    assert r.status_code == 302
    assert "Kasia – OPS Myślenice" in client.get("/konto").get_data(as_text=True)
    r = client.post("/admin/uzytkownicy/nowy", data={"_csrf": token, "name": "ab", "role": "x"})
    assert r.status_code == 422 and "Popraw 2 pola" in r.get_data(as_text=True)
