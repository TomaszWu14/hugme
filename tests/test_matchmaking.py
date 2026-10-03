from conftest import csrf_of, login
from core import db

PROBLEM = ("Rodzice dzieci z zespołem Downa jeżdżą do kardiologa, logopedy i endokrynologa w różne dni. "
           "Mój syn Kacper, tel. 600 123 456.")


def search(client, text=PROBLEM, powiat="wadowicki"):
    token = csrf_of(client)
    return client.post("/szukaj", data={"_csrf": token, "opis": text, "powiat": powiat})


def test_guest_search_shows_explained_matches_and_masks(client):
    resp = search(client)
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/wyniki")
    html = client.get("/wyniki").get_data(as_text=True)
    assert "Asystent zdrowia rodziny" in html or "Dzień Specjalistów" in html
    assert "Dlaczego pasuje" in html and "trafność" in html
    assert "Kacper" not in html and "600 123 456" not in html
    assert "ukryliśmy" in html.lower()
    assert "Inni mieli podobnie" in html and "Eksperci" in html and "Poradniki" in html


def test_too_short_description_gives_friendly_error(client):
    resp = search(client, text="lekarz")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 422 and "Napisz trochę więcej" in html and 'aria-invalid="true"' in html


def test_guest_save_redirects_to_login_and_keeps_draft(client):
    search(client)
    token = csrf_of(client, "/wyniki")
    resp = client.post("/zgloszenie", data={"_csrf": token, "opis": PROBLEM})
    assert "/konto" in resp.headers["Location"]
    token = csrf_of(client, "/konto")
    client.post("/konto", data={"_csrf": token, "user_id": 1, "next": "/wyniki"})
    assert "Zapisz zgłoszenie" in client.get("/wyniki").get_data(as_text=True)


def test_save_report_masks_creates_thread_and_notifies_admin(client, app):
    token = login(client, "mieszkaniec")
    search(client)
    resp = client.post("/zgloszenie", data={"_csrf": token, "opis": PROBLEM, "area": "rodziny-zd", "powiat": "wadowicki"})
    assert resp.status_code == 302
    with app.app_context():
        r = db.one("SELECT * FROM reports ORDER BY id DESC LIMIT 1")
        assert "Kacper" not in r["body"] and "[IMIĘ]" in r["body"] and r["is_example"] == 0
        assert db.one("SELECT COUNT(*) FROM matches WHERE report_id = ?", (r["id"],))[0] > 0
        assert db.one("SELECT COUNT(*) FROM threads WHERE subject_type='zgloszenie' AND subject_id=?", (r["id"],))[0] == 1
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id = 5 AND body LIKE 'Nowe zgłoszenie%'")[0] >= 3
        assert db.one("SELECT COUNT(*) FROM emails WHERE user_id = 5")[0] >= 1


def test_author_rates_match_and_others_cannot(client, app):
    token = login(client, "mieszkaniec")
    with app.app_context():
        m = db.one("SELECT m.* FROM matches m JOIN reports r ON r.id = m.report_id WHERE r.user_id = 1 LIMIT 1")
    client.post(f"/zgloszenie/{m['report_id']}/ocena", data={"_csrf": token, "innovation_id": m["innovation_id"], "ocena": "pomocne"})
    with app.app_context():
        assert db.one("SELECT feedback FROM matches WHERE report_id=? AND innovation_id=?",
                      (m["report_id"], m["innovation_id"]))[0] == 1
    token = login(client, "ngo")
    resp = client.post(f"/zgloszenie/{m['report_id']}/ocena", data={"_csrf": token, "innovation_id": m["innovation_id"], "ocena": "niepomocne"})
    assert resp.status_code == 403


def test_unapproved_report_hidden_from_other_users(client, app):
    with app.app_context():
        r = db.one("SELECT id FROM reports WHERE approved = 0 AND user_id = 1")
    assert client.get(f"/zgloszenie/{r['id']}").status_code == 403
    login(client, "admin")
    assert client.get(f"/zgloszenie/{r['id']}").status_code == 200


def test_thread_reply_by_hub_notifies_author(client, app):
    with app.app_context():
        r = db.one("SELECT id FROM reports WHERE user_id = 1 ORDER BY id LIMIT 1")
    token = login(client, "admin")
    client.post(f"/watek/zgloszenie/{r['id']}", data={"_csrf": token, "tresc": "Dzień dobry, łączymy Was z CUS."})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id = 1 AND body LIKE 'Nowa wiadomość%'")[0] == 1


def test_stranger_cannot_post_in_report_thread(client, app):
    with app.app_context():
        r = db.one("SELECT id FROM reports WHERE user_id = 1 ORDER BY id LIMIT 1")
    token = login(client, "gmina")
    assert client.post(f"/watek/zgloszenie/{r['id']}", data={"_csrf": token, "tresc": "test"}).status_code == 403


def test_notifications_page_and_mark_read(client, app):
    token = login(client, "mieszkaniec")
    assert "Hub odpowiedział" in client.get("/powiadomienia").get_data(as_text=True)
    client.post("/powiadomienia/przeczytane", data={"_csrf": token})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=1 AND is_read=0")[0] == 0


def test_expert_inbox_role_guard(client):
    login(client, "mieszkaniec")
    assert client.get("/ekspert").status_code == 403
    login(client, "ekspert")
    assert "Czekają na odpowiedź" in client.get("/ekspert").get_data(as_text=True)


def test_my_page_and_follow(client, app):
    token = login(client, "gmina")
    client.post("/obserwuj/cyfrowe", data={"_csrf": token, "next": "/moje"})
    with app.app_context():
        assert db.one("SELECT 1 FROM follows WHERE user_id=3 AND area='cyfrowe'")
    assert "Moje zgłoszenia" in client.get("/moje").get_data(as_text=True)
