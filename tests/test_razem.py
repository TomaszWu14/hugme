"""Moduł „Razem z ZD” – dla osób z zespołem Downa i ich rodzin."""
import pytest

from conftest import csrf_of, login
from core import ai, db
from core.privacy import mask
from data import razem
from data.seed_data import RAZEM_REQUESTS

PAGES = ["/razem", "/razem/etap/przedszkole", "/razem/wizyty", "/razem/prawa", "/razem/szkoly", "/razem/rodzenstwo",
         "/razem/co-po-nas", "/razem/przewodnik", "/razem/wytchnienie", "/razem/miejsca", "/razem/sprzet",
         "/razem/wydarzenia", "/razem/pisma", "/razem/pisma/asystent", "/razem/moje-sprawy"]


def count(app, sql, args=()):
    with app.app_context():
        return db.one(sql, args)[0]


# ── Task 1: dane ──────────────────────────────────────────────────────────────
def test_content_has_six_stages_with_required_keys():
    stages = razem.stages()
    assert len(stages) == 6
    for s in stages:
        assert {"slug", "name", "age", "icon", "now", "ask_doctor", "documents", "etr", "innovations"} <= set(s)
        assert len(s["now"]) == 3
    assert razem.stage("nie-ma") is None


def test_rights_wizard_returns_institutions_without_amounts():
    result = razem.rights_result({"orzeczenie": False, "szkola": True})
    names = " ".join(r["institution"] for r in result)
    assert "orzekania o niepełnosprawności" in names and "Poradnia psychologiczno-pedagogiczna" in names
    assert not any("zł" in r["why"] for r in result)


def test_seed_module_data(app):
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='miejsce' AND status='zatwierdzone'") >= 6
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='miejsce' AND status='nowe'") == 1
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind LIKE 'sprzet-%'") == 4
    assert count(app, "SELECT COUNT(*) FROM events") == 4
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='przewodnik-oferuje'") == 3
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='przewodnik-szukam'") == 2
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='dzien-specjalistow'") >= 6


def test_seed_module_texts_have_no_personal_data():
    for row in RAZEM_REQUESTS:
        assert mask(row[6])[1] == [], row[6]


# ── Task 2: strony rodzica ────────────────────────────────────────────────────
@pytest.mark.parametrize("path", PAGES)
def test_module_pages_render_for_guest(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, path
    assert "Razem z ZD" in resp.get_data(as_text=True)


def test_stage_choice_is_remembered_in_cookie(client):
    token = csrf_of(client, "/razem")
    resp = client.post("/razem/etap", data={"_csrf": token, "etap": "szkola"})
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/razem/etap/szkola")
    assert "razem_etap=szkola" in resp.headers["Set-Cookie"]
    assert "Twój etap: Szkoła" in client.get("/razem").get_data(as_text=True)


def test_unknown_stage_404_and_bad_choice_400(client):
    assert client.get("/razem/etap/xyz").status_code == 404
    token = csrf_of(client, "/razem")
    assert client.post("/razem/etap", data={"_csrf": token, "etap": "xyz"}).status_code == 400


def test_stage_plan_content(client):
    html = client.get("/razem/etap/przedszkole").get_data(as_text=True)
    assert "O co zapytać lekarza" in html and "nie porada medyczna" in html
    assert "Klasa w Ruchu" in html  # innowacja z Biblioteki
    assert "Łatwy tekst" in html


def test_rights_wizard_page(client):
    html = client.get("/razem/prawa?orzeczenie=nie&szkola=tak").get_data(as_text=True)
    assert "Poradnia psychologiczno-pedagogiczna" in html
    assert "orzekania o niepełnosprawności" in html


def test_visits_page_is_browser_only(client):
    html = client.get("/razem/wizyty").get_data(as_text=True)
    assert "razem.js" in html and "<noscript>" in html and "tylko na tym urządzeniu" in html


# ── Task 3: prośby ────────────────────────────────────────────────────────────
def test_request_requires_login(client):
    token = csrf_of(client, "/razem/wytchnienie")
    resp = client.post("/razem/prosba/wytchnienie", data={"_csrf": token, "powiat": "wadowicki"})
    assert "/konto" in resp.headers["Location"]


def test_request_validation(client):
    token = login(client, "mieszkaniec")
    resp = client.post("/razem/prosba/wytchnienie", data={"_csrf": token, "alias": "Mama", "body": "Potrzebuję przerwy w sobotę."})
    assert resp.status_code == 422 and "error-summary" in resp.get_data(as_text=True)
    assert client.post("/razem/prosba/hack", data={"_csrf": token}).status_code == 404


def test_request_is_masked_saved_and_notifies_hub(client, app):
    token = login(client, "mieszkaniec")
    resp = client.post("/razem/prosba/przewodnik-szukam", data={
        "_csrf": token, "powiat": "olkuski", "stage": "diagnoza", "alias": "Mama z Olkusza",
        "body": "Świeża diagnoza, mój tel. 600 123 456, szukamy rodziny do rozmowy."})
    assert resp.status_code == 302
    with app.app_context():
        r = db.one("SELECT * FROM family_requests WHERE alias='Mama z Olkusza'")
        assert "600 123 456" not in r["body"] and r["status"] == "nowe"
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=5 AND body LIKE 'Razem z ZD:%'")[0] == 1


def test_specialist_day_one_click(client, app):
    token = login(client, "mieszkaniec")
    before = count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='dzien-specjalistow'")
    client.post("/razem/prosba/dzien-specjalistow", data={"_csrf": token, "powiat": "suski", "alias": "Rodzic"})
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE kind='dzien-specjalistow'") == before + 1


def test_public_lists_show_only_approved(client):
    html = client.get("/razem/miejsca").get_data(as_text=True)
    assert "Przychodnia „Pod Lipami”" in html and "Plac zabaw „Dla wszystkich”" not in html
    assert "Oddam pionizator" in client.get("/razem/sprzet").get_data(as_text=True)


# ── Task 4: wydarzenia i pisma ────────────────────────────────────────────────
def test_event_signup_toggle(client, app):
    token = login(client, "mieszkaniec")
    client.post("/razem/wydarzenia/1/zapis", data={"_csrf": token})
    assert count(app, "SELECT COUNT(*) FROM event_signups WHERE event_id=1 AND user_id=1") == 1
    assert count(app, "SELECT COUNT(*) FROM notifications WHERE user_id=1 AND body LIKE 'Zapisano%'") == 1
    client.post("/razem/wydarzenia/1/zapis", data={"_csrf": token})
    assert count(app, "SELECT COUNT(*) FROM event_signups WHERE event_id=1 AND user_id=1") == 0


def test_letter_post_prints_without_storing(client, app):
    tables = ["reports", "family_requests", "messages", "notifications", "emails"]
    before = [count(app, f"SELECT COUNT(*) FROM {t}") for t in tables]
    token = csrf_of(client, "/razem/pisma/asystent")
    html = client.post("/razem/pisma/asystent", data={
        "_csrf": token, "rodzic": "Jan Testowy", "szkola": "SP 1", "klasa": "2b",
        "uzasadnienie": "potrzebuje pomocy na przerwach", "miejscowosc": "Wadowice"}).get_data(as_text=True)
    assert "WNIOSEK O ZAPEWNIENIE ASYSTENTA UCZNIA" in html and "Jan Testowy" in html
    assert [count(app, f"SELECT COUNT(*) FROM {t}") for t in tables] == before
    assert 'value="Jan"' not in client.get("/razem/pisma/asystent?rodzic=Jan").get_data(as_text=True)
    assert client.get("/razem/pisma/nie-ma").status_code == 404


def test_letter_ai_justification_is_labelled(client, monkeypatch):
    monkeypatch.setattr(ai, "ask", lambda *a, **k: "Dziecko potrzebuje stałego wsparcia, aby bezpiecznie uczestniczyć w zajęciach.")
    token = csrf_of(client, "/razem/pisma/asystent")
    html = client.post("/razem/pisma/asystent", data={
        "_csrf": token, "akcja": "ai", "rodzic": "Jan Testowy", "szkola": "SP 1", "klasa": "2b",
        "uzasadnienie": "przerwy", "miejscowosc": "Wadowice"}).get_data(as_text=True)
    assert "Wygenerowane przez AI" in html and "bezpiecznie uczestniczyć" in html


# ── Task 5: „Moje sprawy” ─────────────────────────────────────────────────────
def test_my_matters_easy_to_read(client):
    html = client.get("/razem/moje-sprawy").get_data(as_text=True)
    for sentence in razem.MY_INTRO:
        assert sentence in html and len(sentence.split()) <= 8
    assert 'action="/szukaj"' in html and 'name="temat"' in html
    assert 'id="czytaj"' in html and "hidden" in html.split('id="czytaj"')[1][:40]


def test_my_matters_goes_to_matchmaking(client):
    token = csrf_of(client, "/razem/moje-sprawy")
    resp = client.post("/szukaj", data={"_csrf": token, "temat": "praca", "opis": "Chcę pracować w kawiarni."})
    assert resp.status_code == 302
    assert "Kawiarnia Treningowa" in client.get("/wyniki").get_data(as_text=True)


def test_module_js_served(client):
    js = client.get("/static/js/razem.js").get_data(as_text=True)
    assert "localStorage" in js and "speechSynthesis" in js


# ── Task 6: panel Hubu ────────────────────────────────────────────────────────
@pytest.mark.parametrize("role", ["mieszkaniec", "ngo", "gmina", "ekspert"])
def test_admin_module_view_forbidden(client, role):
    login(client, role)
    assert client.get("/admin/razem").status_code == 403


def test_admin_module_view_and_inbox(client):
    login(client, "admin")
    html = client.get("/admin/razem").get_data(as_text=True)
    assert "Propozycje par" in html and "Mama Ani" in html and "Marta" in html
    assert "Dzień Specjalistów" in html
    assert "Razem z ZD" in client.get("/admin?typ=razem").get_data(as_text=True)


def test_moderation_approves_and_notifies(client, app):
    token = login(client, "admin")
    with app.app_context():
        rid = db.one("SELECT id, user_id FROM family_requests WHERE kind='miejsce' AND status='nowe'")
    client.post(f"/admin/razem/{rid['id']}/status", data={"_csrf": token, "status": "zatwierdzone"})
    assert "Plac zabaw „Dla wszystkich”" in client.get("/razem/miejsca").get_data(as_text=True)
    assert count(app, "SELECT COUNT(*) FROM notifications WHERE user_id=? AND body LIKE 'Hub zatwierdził%'", (rid["user_id"],)) == 1
    assert client.post(f"/admin/razem/{rid['id']}/status", data={"_csrf": token, "status": "zle"}).status_code == 400


def test_pairing_guides(client, app):
    token = login(client, "admin")
    with app.app_context():
        s = db.one("SELECT * FROM family_requests WHERE kind='przewodnik-szukam' AND powiat='wadowicki'")
        o = db.one("SELECT * FROM family_requests WHERE kind='przewodnik-oferuje' AND powiat='wadowicki'")
    client.post("/admin/razem/polacz", data={"_csrf": token, "szukam_id": s["id"], "oferuje_id": o["id"]})
    with app.app_context():
        s2 = db.one("SELECT * FROM family_requests WHERE id=?", (s["id"],))
        o2 = db.one("SELECT * FROM family_requests WHERE id=?", (o["id"],))
        assert (s2["status"], s2["matched_with"]) == ("polaczone", o["id"])
        assert (o2["status"], o2["matched_with"]) == ("polaczone", s["id"])
    for uid in (s["user_id"], o["user_id"]):
        assert count(app, "SELECT COUNT(*) FROM notifications WHERE user_id=? AND body LIKE 'Hub połączył%'", (uid,)) == 1
    resp = client.post("/admin/razem/polacz", data={"_csrf": token, "szukam_id": o["id"], "oferuje_id": s["id"]})
    assert resp.status_code == 400


def test_signup_is_idempotent_at_db_level(app):
    """Równoczesny drugi zapis (wyścig) nie może skończyć się błędem."""
    with app.app_context():
        for _ in range(2):
            db.execute("INSERT INTO event_signups (event_id, user_id, created_at) VALUES (1, 2, '2026-10-03') "
                       "ON CONFLICT (event_id, user_id) DO NOTHING")
        assert db.one("SELECT COUNT(*) FROM event_signups WHERE event_id=1 AND user_id=2")[0] == 1


def test_guide_request_cannot_be_approved_only_closed(client, app):
    token = login(client, "admin")
    with app.app_context():
        rid = db.one("SELECT id FROM family_requests WHERE kind='przewodnik-szukam' LIMIT 1")["id"]
    assert client.post(f"/admin/razem/{rid}/status", data={"_csrf": token, "status": "zatwierdzone"}).status_code == 400
    assert client.post(f"/admin/razem/{rid}/status", data={"_csrf": token, "status": "zamkniete"}).status_code == 302


# ── Poprawki z przeglądu dwuosiowego ──────────────────────────────────────────
@pytest.mark.parametrize("role", ["mieszkaniec", "ngo", "gmina", "ekspert", "admin"])
def test_module_pages_render_for_roles(client, role):
    login(client, role)
    for path in PAGES:
        assert client.get(path).status_code == 200, (role, path)


@pytest.mark.parametrize("back", ["//evil.example", "https://evil.example", "/admin"])
def test_request_back_param_cannot_redirect_outside_module(client, back):
    token = login(client, "mieszkaniec")
    resp = client.post("/razem/prosba/dzien-specjalistow", data={"_csrf": token, "powiat": "suski", "alias": "Rodzic", "wroc": back})
    assert resp.headers["Location"] == "/razem"


def test_easy_read_error_stays_in_module(client):
    token = csrf_of(client, "/razem/moje-sprawy")
    resp = client.post("/szukaj", data={"_csrf": token, "zrodlo": "etr", "opis": "Chcę pracować."})  # bez obrazka
    assert resp.headers["Location"].endswith("/razem/moje-sprawy")
    assert razem.ETR_ERROR in client.get("/razem/moje-sprawy").get_data(as_text=True)


def test_letter_template_fallback_without_ai(client):
    token = csrf_of(client, "/razem/pisma/asystent")
    html = client.post("/razem/pisma/asystent", data={
        "_csrf": token, "akcja": "ai", "rodzic": "Jan Testowy", "szkola": "SP 1", "klasa": "2b",
        "uzasadnienie": "przerwy", "miejscowosc": "Wadowice"}).get_data(as_text=True)
    assert "Podpowiedź z szablonu" in html and razem.LETTER_FALLBACK in html


def test_specialist_day_votes_in_inbox_with_pseudonym(client):
    html = client.get("/razem/etap/przedszkole")
    login(client, "admin")
    inbox = client.get("/admin?typ=razem").get_data(as_text=True)
    assert "Chcę Dzień Specjalistów" in inbox
    login(client, "mieszkaniec")
    assert 'name="alias" value="Rodzic"' in client.get("/razem/etap/przedszkole").get_data(as_text=True)


def test_events_filter_by_powiat(client):
    html = client.get("/razem/wydarzenia?powiat=Kraków").get_data(as_text=True)
    assert "Klub rodzeństwa" in html and "Piknik rodzin" not in html


def test_respite_requires_when_and_how_long(client):
    token = login(client, "mieszkaniec")
    resp = client.post("/razem/prosba/wytchnienie", data={"_csrf": token, "powiat": "wadowicki", "alias": "Mama",
                                                         "body": "Potrzebuję przerwy w sobotę."})
    assert resp.status_code == 422 and "Wpisz nazwę" in resp.get_data(as_text=True)


def test_admin_can_close_family_request(client, app):
    token = login(client, "admin")
    with app.app_context():
        rid = db.one("SELECT id FROM family_requests WHERE kind='wytchnienie' LIMIT 1")["id"]
    assert "Zamknij – sprawa załatwiona" in client.get("/admin/razem").get_data(as_text=True)
    client.post(f"/admin/razem/{rid}/status", data={"_csrf": token, "status": "zamkniete"})
    assert count(app, "SELECT COUNT(*) FROM family_requests WHERE id=? AND status='zamkniete'", (rid,)) == 1


def test_family_requests_only_from_resident_account(client):
    token = login(client, "gmina")
    r = client.post("/razem/prosba/wytchnienie", data={"_csrf": token, "alias": "Urząd", "powiat": "Kraków", "title": "sobota",
                                                       "body": "Prośba testowa z konta gminy – nie powinna przejść."})
    assert r.status_code == 403
    html = client.get("/razem/wytchnienie").get_data(as_text=True)
    assert "zmień konto" in html and 'name="body"' not in html.split("zmień konto")[0][-200:] or "Wyślij prośbę" not in html
