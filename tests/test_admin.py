import io

import pytest

from conftest import login
from core import db

ADMIN_PAGES = ["/admin", "/admin/watki", "/admin/trendy", "/admin/biblioteka", "/admin/import",
               "/admin/nabory", "/admin/poczta", "/admin/biblioteka/nowa", "/admin/eksport/zgloszenia.csv"]


@pytest.mark.parametrize("role", ["mieszkaniec", "ngo", "gmina", "ekspert"])
def test_admin_pages_forbidden_for_other_roles(client, role):
    login(client, role)
    for page in ADMIN_PAGES + ["/admin/luki"]:
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
    html = client.get("/admin/trendy").get_data(as_text=True)
    assert "powiat × obszar" in html and "wadowicki" in html and "Ostatnie 30 dni" in html
    assert 'id="luki"' in html and "mieszkań treningowych" in html and "Kandydat na konkurs" in html


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


def _messages_and_notifications(app):
    with app.app_context():
        return (db.one("SELECT COUNT(*) FROM messages")[0], db.one("SELECT COUNT(*) FROM notifications")[0])


def test_hidden_idea_thread_rejects_messages_except_hub(client, app):
    with app.app_context():
        db.execute("UPDATE ideas SET hidden = 1 WHERE id = 1")
    messages, notifications = _messages_and_notifications(app)
    token = login(client, "ngo")
    r = client.post("/watek/pomysl/1", data={"_csrf": token, "tresc": "Pytanie po ukryciu"})
    assert r.status_code == 404
    assert _messages_and_notifications(app) == (messages, notifications)  # ani wiadomości, ani powiadomień
    token = login(client, "admin")                                         # Hub moderuje i może odpisać
    assert client.post("/watek/pomysl/1", data={"_csrf": token, "tresc": "Wątek zamknięty"}).status_code == 302
    assert _messages_and_notifications(app)[0] == messages + 1


def test_gaps_moved_to_trends_and_linked_reports_are_not_gaps(client, app):
    login(client, "admin")
    r = client.get("/admin/luki")
    assert r.status_code == 302 and r.headers["Location"].endswith("/admin/trendy#luki")
    with app.app_context():
        from app.views.admin import gaps
        linked = db.one("SELECT id FROM reports WHERE status = 'polaczone' AND best_score < 0.5 LIMIT 1")
        assert linked and linked["id"] not in {g["id"] for g, _ in gaps()}
        n = len(gaps())
    assert f'<span class="stat__num">{n}</span> luk' in client.get("/admin").get_data(as_text=True)
    html = client.get("/admin/trendy").get_data(as_text=True)
    assert f"Zgłoszenia ({n})" in html                              # kafel i sekcja luk się zgadzają
    assert html.index("Zmiana") < html.index("Razem</th>")          # „Zmiana” zaraz za „Obszar”


def test_inbox_waiting_first_and_new_ideas_tile(client, app):
    with app.app_context():
        db.execute("INSERT INTO ideas (user_id, title, essence, audience, stage, created_at) VALUES (1, ?, ?, ?, ?, ?)",
                   ("Kawiarenka dla rodziców", "Spotkania przy kawie", "rodzice", "pomysł", db.now()))
    login(client, "admin")
    html = client.get("/admin").get_data(as_text=True)
    assert "nowy pomysł bez odpowiedzi" in html or "nowe pomysły bez odpowiedzi" in html
    assert "najpierw czekające na odpowiedź" in html and "Dodaj innowację" in html
    body = html.split("<tbody>")[1]
    rows = body.split("<tr>")[1:]
    flags = ["czeka na odpowiedź" in r for r in rows]
    assert flags == sorted(flags, reverse=True)                     # czekające na górze
    assert "Kawiarenka dla rodziców" in client.get("/admin?typ=pomysl").get_data(as_text=True)
    assert "Wyślij pocztę" not in html
    assert "w demo nic nie jest wysyłane" in client.get("/admin/poczta").get_data(as_text=True)


def test_plural_filter():
    from app import plural
    forms = ("wątek", "wątki", "wątków")
    assert [plural(n, *forms) for n in (0, 1, 2, 4, 5, 12, 14, 22, 25, 112)] == \
        ["wątków", "wątek", "wątki", "wątki", "wątków", "wątków", "wątków", "wątki", "wątków", "wątków"]


def test_unanswered_thread_shows_area_wait_and_reply_button(client, app):
    with app.app_context():
        tid = db.one("SELECT id FROM threads WHERE subject_type = 'pomysl' LIMIT 1")["id"]
        db.execute("INSERT INTO messages (thread_id, user_id, body, created_at) VALUES (?, 1, 'Czy ktoś pomoże?', ?)",
                   (tid, db.now()))
    login(client, "admin")
    html = client.get("/admin/watki").get_data(as_text=True)
    assert "czeka od niecałej godziny" in html and "Odpowiedz" in html and "#watek" in html
    assert 'class="count"' in client.get("/admin/trendy").get_data(as_text=True)  # licznik w menu panelu


def test_waited_text():
    from datetime import datetime
    from app.views.admin import waited
    now = datetime(2026, 10, 4, 12, 0, 0)
    assert waited("2026-10-04 07:00:00", now) == "czeka od 5 h"
    assert waited("2026-10-03 11:00:00", now) == "czeka od 1 dnia"
    assert waited("2026-10-01 12:00:00", now) == "czeka od 3 dni"


@pytest.mark.parametrize("user_id, home", [(5, "/admin"), (3, "/posrednik"), (4, "/ekspert"), (1, "/")])
def test_demo_login_lands_by_role(client, user_id, home):
    from conftest import csrf_of
    r = client.post("/konto", data={"_csrf": csrf_of(client, "/konto"), "user_id": user_id})
    assert r.headers["Location"] == home


@pytest.mark.parametrize("target", ["//evil.example", "/\\evil.example", "/\t/evil.example", "https://evil.example",
                                    "javascript:alert(1)", "\\\\evil.example", "/\n/evil.example", ""])
def test_safe_next_blocks_open_redirect(client, target):
    from conftest import csrf_of
    r = client.post("/konto", data={"_csrf": csrf_of(client, "/konto"), "user_id": 5, "next": target})
    assert r.headers["Location"] == "/admin"


def test_safe_next_keeps_fragment_and_query(client):
    from conftest import csrf_of
    from app.auth import safe_next
    assert safe_next("/biblioteka/1#watek") == "/biblioteka/1#watek"
    r = client.post("/konto", data={"_csrf": csrf_of(client, "/konto"), "user_id": 1, "next": "/biblioteka/1?x=1#watek"})
    assert r.headers["Location"] == "/biblioteka/1?x=1#watek"


def test_konto_admin_first_without_lowercase(client):
    html = client.get("/konto").get_data(as_text=True).split("grid--accounts")[1]
    assert html.index("Koordynatorka ROPS") < html.index("Mieszkanka-rodzic")
    assert "Dla jury" in html and "jako koordynatorka rops" not in html and ">Wejdź<" in html
    # Środek zdania: mała pierwsza litera, skróty bez zmian (szuka tego też scripts/axe_audit.py).
    assert "jako koordynatorka ROPS" in html and "jako gmina (JST)" in html


def test_hidden_messages_do_not_affect_waiting_counters(client, app):
    """Issue #19: ukryta (np. spam) wiadomość nie zmienia „czeka na odpowiedź” ani „Hub odpowiedział”."""
    from app.views.admin import HUB_REPLIES_SQL, unanswered
    with app.app_context():
        t = db.one("SELECT id, subject_id FROM threads WHERE subject_type = 'pomysl' LIMIT 1")
        tid, iid = t["id"], t["subject_id"]
        add = "INSERT INTO messages (thread_id, user_id, body, created_at, hidden) VALUES (?, ?, ?, ?, ?)"
        db.execute(add, (tid, 5, "Odpowiedź Hubu", "2099-01-01 10:00:00", 0))
        db.execute(add, (tid, 1, "Spam", "2099-01-01 11:00:00", 1))
        assert tid not in {t["id"] for t in unanswered()}          # ostatnia widoczna to odpowiedź Hubu
        db.execute("DELETE FROM messages WHERE thread_id = ?", (tid,))
        db.execute(add, (tid, 5, "Ukryta odpowiedź", "2099-01-01 10:00:00", 1))
        replied = {(r["subject_type"], r["subject_id"]) for r in db.query(HUB_REPLIES_SQL)}
        assert ("pomysl", iid) not in replied                       # ukryta odpowiedź Hubu się nie liczy


def test_innovation_form_errors_use_polish_plural(client):
    """Issue #26: „Popraw 7 pól” i „co najmniej 10 znaków” zamiast „7 pola” / „10 znaki”."""
    token = login(client, "admin")
    html = client.post("/admin/biblioteka/nowa", data={"_csrf": token, "title": "Tytuł"}).get_data(as_text=True)
    assert "Popraw 7 pól" in html
    assert "co najmniej 10 znaków" in html and "co najmniej 3 znaki" in html


def test_import_twice_skips_duplicates(client, app):
    """Issue #23: ponowny import (i powtórka w pliku) nie tworzy kopii ani drugich powiadomień."""
    token = login(client, "admin")
    row = ("Klub Szachowy Seniora;Seniorzy grają w szachy;Cotygodniowe spotkania szachowe w bibliotece gminnej.;"
           "Seniorzy;olkuski;wdrożenie;seniorzy;Biblioteka X\n")
    csv_text = "tytul;streszczenie;opis;obszar;powiat;etap;odbiorcy;organizacja\n" + row + "  klub szachowy  SENIORA" + row[21:]
    count = "SELECT (SELECT COUNT(*) FROM innovations), (SELECT COUNT(*) FROM notifications)"

    def send():
        return client.post("/admin/import", data={"_csrf": token, "plik": (io.BytesIO(csv_text.encode()), "rops.csv")},
                           content_type="multipart/form-data").get_data(as_text=True)

    html = send()
    assert "Zaimportowano: <strong>1</strong>" in html and "Pominięto: <strong>1</strong>" in html
    with app.app_context():
        before = tuple(db.one(count))
    html = send()
    assert "Zaimportowano: <strong>0</strong>" in html and "Pominięto: <strong>2</strong>" in html and "już jest" in html
    with app.app_context():
        assert tuple(db.one(count)) == before


def test_new_call_rejects_past_deadline(client, app):
    """Issue #16: nabór nie może mieć terminu wcześniejszego niż dziś."""
    token = login(client, "admin")
    form = {"_csrf": token, "title": "Nabór testowy", "area": "rodziny-zd", "description": "Opis naboru testowego."}
    client.post("/admin/nabory/nowy", data={**form, "deadline": "2000-01-01"})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM calls WHERE title = 'Nabór testowy'")[0] == 0
    client.post("/admin/nabory/nowy", data={**form, "deadline": "2999-01-01"})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM calls WHERE title = 'Nabór testowy'")[0] == 1
