import json

from conftest import login
from core import db


def test_ideas_list_is_public_and_shows_calls(client):
    html = client.get("/pomysly").get_data(as_text=True)
    assert "Weekendowy klub" in html and "Otwarty do" in html and "Zamknięty" in html


def test_new_idea_validation_errors(client):
    token = login(client, "ngo")
    resp = client.post("/pomysly/nowy", data={"_csrf": token, "title": "", "essence": "krótko"})
    html = resp.get_data(as_text=True)
    assert resp.status_code == 422 and "error-summary" in html and 'aria-invalid="true"' in html


def test_full_creator_flow(client, app):
    token = login(client, "ngo")
    resp = client.post("/pomysly/nowy", data={
        "_csrf": token, "title": "Kawiarenka sąsiedzka", "audience": "seniorzy", "stage": "pomysł",
        "essence": "Seniorzy prowadzą kawiarenkę w świetlicy, mój tel. 600 123 456.", "area": "samotnosc"})
    assert resp.status_code == 302
    iid = int(resp.headers["Location"].rsplit("/", 1)[1])
    with app.app_context():
        idea = db.one("SELECT * FROM ideas WHERE id = ?", (iid,))
        assert "600 123 456" not in idea["essence"]
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=5 AND body LIKE 'Nowy pomysł%'")[0] == 1
    client.post(f"/pomysly/{iid}/kanwa", data={"_csrf": token, "problem": "Seniorzy są samotni", "partnerzy": "OPS"})
    with app.app_context():
        assert json.loads(db.one("SELECT canvas FROM ideas WHERE id=?", (iid,))[0]) == {"problem": "Seniorzy są samotni", "partnerzy": "OPS"}
    html = client.post(f"/pomysly/{iid}/asystent", data={"_csrf": token}).get_data(as_text=True)
    assert "Mocne strony" in html and "Podpowiedź z szablonu (bez AI)" in html and "Szkic prototypu" in html

    # Generator: szkic → złożenie (nabór 1 otwarty)
    page = client.get(f"/pomysly/{iid}/wniosek/1").get_data(as_text=True)
    assert "Kawiarenka sąsiedzka" in page  # wypełnione z fiszki
    fields = {"tytul": "Kawiarenka", "problem": "p", "grupa": "g", "dzialania": "d", "rezultaty": "r", "budzet": "b", "partnerzy": ""}
    resp = client.post(f"/pomysly/{iid}/wniosek/1", data={"_csrf": token, "akcja": "zloz", **fields})
    assert resp.status_code == 422  # brak partnerów
    client.post(f"/pomysly/{iid}/wniosek/1", data={"_csrf": token, "akcja": "szkic", **fields})
    resp = client.post(f"/pomysly/{iid}/wniosek/1", data={"_csrf": token, "akcja": "zloz", **fields, "partnerzy": "OPS"})
    assert "/wnioski/" in resp.headers["Location"]
    with app.app_context():
        assert db.one("SELECT status FROM applications WHERE idea_id=?", (iid,))[0] == "zlozony"
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id=5 AND body LIKE 'Złożono wniosek%'")[0] == 1
    assert "ZŁOŻONY" in client.get(resp.headers["Location"]).get_data(as_text=True)


def test_generator_inactive_for_closed_call(client):
    token = login(client, "ngo")
    resp = client.get("/pomysly/1/wniosek/3")  # nabór 3 zamknięty
    assert resp.status_code == 302 and "/pomysly/1" in resp.headers["Location"]


def test_only_owner_edits_canvas_and_applies(client):
    token = login(client, "gmina")
    assert client.post("/pomysly/1/kanwa", data={"_csrf": token, "problem": "x"}).status_code == 403
    assert client.get("/pomysly/1/wniosek/1").status_code == 403


def test_application_print_restricted(client, app):
    token = login(client, "ngo")
    fields = {k: "x" for k in ("tytul", "problem", "grupa", "dzialania", "rezultaty", "budzet", "partnerzy")}
    resp = client.post("/pomysly/1/wniosek/1", data={"_csrf": token, "akcja": "zloz", **fields})
    url = resp.headers["Location"]
    login(client, "mieszkaniec")
    assert client.get(url).status_code == 403
    login(client, "admin")
    assert client.get(url).status_code == 200


def test_idea_page_plain_language_canvas_grid_and_single_primary(client):
    login(client, "ngo")
    html = client.get("/pomysly/1").get_data(as_text=True)
    assert "Plan pomysłu w 10 pytaniach" in html and "Kanwa Innowacji Społecznych" in html
    assert '<progress id="kanwa-postep"' in html and "Co znaczą etapy?" in html
    assert "Pomoc w napisaniu wniosku" in html and "(nabór)" in html
    # J1B-12: przy kilku naborach „Przygotuj wniosek” jest konturem, nie ceglastym primary
    assert 'class="btn btn--primary" href="/pomysly/1/wniosek/' not in html
