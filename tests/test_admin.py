import io

import pytest

from conftest import login
from core import db

ADMIN_PAGES = ["/admin", "/admin/watki", "/admin/luki", "/admin/trendy", "/admin/biblioteka", "/admin/import",
               "/admin/nabory", "/admin/poczta", "/admin/biblioteka/nowa", "/admin/eksport/zgloszenia.csv"]


@pytest.mark.parametrize("role", ["mieszkaniec", "ngo", "gmina", "ekspert"])
def test_admin_pages_forbidden_for_other_roles(client, role):
    login(client, role)
    for page in ADMIN_PAGES:
        assert client.get(page).status_code == 403, page


def test_admin_pages_redirect_guest_to_login(client):
    resp = client.get("/admin/trendy")
    assert resp.status_code == 302 and "/konto" in resp.headers["Location"]


def test_admin_post_forbidden_for_non_admin(client):
    token = login(client, "ngo")
    assert client.post("/admin/zgloszenie/1/status", data={"_csrf": token, "status": "zamkniete"}).status_code == 403
    assert client.post("/admin/nabory/1/przelacz", data={"_csrf": token}).status_code == 403


def test_admin_pages_render(client):
    login(client, "admin")
    for page in ADMIN_PAGES:
        assert client.get(page).status_code == 200, page


def test_dashboard_inbox_and_metrics(client):
    login(client, "admin")
    html = client.get("/admin").get_data(as_text=True)
    assert "Skrzynka" in html and "wątków bez odpowiedzi" in html and "pomocne" in html
    assert "Pomysł" in html


def test_status_change_notifies_author(client, app):
    token = login(client, "admin")
    with app.app_context():
        r = db.one("SELECT id, user_id FROM reports WHERE status = 'nowe' LIMIT 1")
    client.post(f"/admin/zgloszenie/{r['id']}/status", data={"_csrf": token, "status": "w-analizie", "approved": "1"})
    with app.app_context():
        assert tuple(db.one("SELECT status, approved FROM reports WHERE id=?", (r["id"],))) == ("w-analizie", 1)
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=? AND body LIKE 'Status Twojego%'",
                      (r["user_id"],))[0] == 1
    assert client.post(f"/admin/zgloszenie/{r['id']}/status", data={"_csrf": token, "status": "zle"}).status_code == 400


def test_quick_library_edit_is_live_in_matching(client, app):
    token = login(client, "admin")
    form = {"_csrf": token, "title": "Wypożyczalnia rowerów trójkołowych", "summary": "Rowery dla seniorów z gminy.",
            "description": "Gmina wypożycza rowery trójkołowe seniorom, żeby mogli dojechać na targ.",
            "area": "seniorzy", "powiat": "wielicki", "stage": "test", "audience": "seniorzy", "org": "Gmina Test",
            "video_url": "https://youtu.be/dQw4w9WgXcQ", "keywords": "rower trójkołowy"}
    assert client.post("/admin/biblioteka/nowa", data=form).status_code == 302
    assert "Wypożyczalnia rowerów" in client.get("/biblioteka", query_string={"q": "rower trójkołowy"}).get_data(as_text=True)
    with app.app_context():
        # Piotr (id 3) obserwuje obszar „seniorzy”
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=3 AND body LIKE 'Nowa innowacja%'")[0] == 1


def test_library_edit_validation(client):
    token = login(client, "admin")
    resp = client.post("/admin/biblioteka/1", data={"_csrf": token, "title": "x", "video_url": "https://evil.example"})
    assert resp.status_code == 422 and "YouTube" in resp.get_data(as_text=True)


def test_import_csv_with_validation(client, app):
    token = login(client, "admin")
    csv_text = ("tytul;streszczenie;opis;obszar;powiat;etap;odbiorcy;organizacja\n"
                "Klub Szachowy Seniora;Seniorzy grają w szachy;Cotygodniowe spotkania szachowe w bibliotece gminnej.;"
                "Seniorzy;olkuski;wdrożenie;seniorzy;Biblioteka X\n"
                "Zły wiersz;;;nieznany;;;;\n")
    resp = client.post("/admin/import", data={"_csrf": token, "plik": (io.BytesIO(csv_text.encode()), "rops.csv")},
                       content_type="multipart/form-data")
    html = resp.get_data(as_text=True)
    assert "Zaimportowano: <strong>1</strong>" in html and "Pominięto" in html
    with app.app_context():
        assert db.one("SELECT is_example FROM innovations WHERE title='Klub Szachowy Seniora'")[0] == 0


def test_import_json(client, app):
    token = login(client, "admin")
    data = ('[{"title": "Mobilna biblioteka", "summary": "Bibliobus odwiedza wsie.", '
            '"description": "Raz w tygodniu bibliobus przyjeżdża do sołectw.", "area": "wies", "powiat": "suski", '
            '"stage": "test", "audience": "seniorzy", "org": "GBP"}]').encode()
    client.post("/admin/import", data={"_csrf": token, "plik": (io.BytesIO(data), "rops.json")},
                content_type="multipart/form-data")
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM innovations WHERE title='Mobilna biblioteka'")[0] == 1


def test_toggle_call_notifies_followers(client, app):
    token = login(client, "admin")
    client.post("/admin/nabory/1/przelacz", data={"_csrf": token})  # zamknij
    with app.app_context():
        assert db.one("SELECT is_open FROM calls WHERE id=1")[0] == 0
        assert db.one("SELECT COUNT(*) FROM notifications WHERE body LIKE 'Ruszył nabór%'")[0] == 0
    client.post("/admin/nabory/1/przelacz", data={"_csrf": token})  # otwórz ponownie
    with app.app_context():
        # Marta (id 2) obserwuje rodziny-zd
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=2 AND body LIKE 'Ruszył nabór%'")[0] == 1


def test_gaps_list_and_trends(client):
    login(client, "admin")
    html = client.get("/admin/luki").get_data(as_text=True)
    assert "mieszkań treningowych" in html and "Kandydat na konkurs" in html
    html = client.get("/admin/trendy").get_data(as_text=True)
    assert "powiat × obszar" in html and "wadowicki" in html and "Ostatnie 30 dni" in html


def test_csv_export_and_formula_injection_guard(client):
    text = '=HYPERLINK("x") rodzice dzieci z zespołem Downa i lekarze'
    token = login(client, "mieszkaniec")
    client.post("/szukaj", data={"_csrf": token, "opis": text})
    client.post("/zgloszenie", data={"_csrf": token, "opis": text})
    login(client, "admin")
    resp = client.get("/admin/eksport/zgloszenia.csv")
    body = resp.get_data(as_text=True)
    assert resp.mimetype == "text/csv" and body.startswith("﻿id;data")
    assert "'=HYPERLINK" in body
    for kind in ("luki", "oceny"):
        assert client.get(f"/admin/eksport/{kind}.csv").status_code == 200
    assert client.get("/admin/eksport/hasla.csv").status_code == 404



def test_admin_hides_and_restores_idea_and_message(client, app):
    with app.app_context():
        title = db.one("SELECT title FROM ideas WHERE id = 1")[0]
        msg = db.one("SELECT m.id, m.body FROM messages m JOIN threads t ON t.id = m.thread_id "
                     "WHERE t.subject_type = 'pomysl' AND t.subject_id = 1")
    token = login(client, "ngo")
    assert client.post("/admin/ukryj/pomysl/1", data={"_csrf": token}).status_code == 403
    token = login(client, "admin")
    r = client.post("/admin/ukryj/pomysl/1", data={"_csrf": token, "next": "https://zly.example"})
    assert r.headers["Location"] == "/admin"                                  # bez open redirect
    client.post(f"/admin/ukryj/wiadomosc/{msg['id']}", data={"_csrf": token})
    assert "widzi go tylko Hub" in client.get("/pomysly/1").get_data(as_text=True)  # Hub widzi i może przywrócić
    with app.app_context():
        assert "ukryto pomysł #1" in db.one("SELECT action FROM admin_log WHERE action LIKE '%pomysł%'")[0]
    login(client, "mieszkaniec")
    assert title not in client.get("/pomysly").get_data(as_text=True)
    assert client.get("/pomysly/1").status_code == 404
    token = login(client, "admin")
    client.post("/admin/ukryj/pomysl/1", data={"_csrf": token})
    login(client, "mieszkaniec")
    page = client.get("/pomysly/1").get_data(as_text=True)
    assert title in page and msg["body"][:30] not in page and "Ukryj" not in page
