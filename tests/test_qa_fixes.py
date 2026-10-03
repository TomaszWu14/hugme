"""Regresje błędów znalezionych w przeklikaniu aplikacji (QA)."""
import io

import pytest

from conftest import csrf_of, login
from core import db
from data import razem


def test_idea_title_masked_in_admin_notification_and_email(client, app):
    token = login(client, "ngo")
    client.post("/pomysly/nowy", data={"_csrf": token, "title": "Klub PESEL 44051401359 tel. 600 123 456",
                                       "essence": "Sobotnie spotkania młodzieży w świetlicy.", "audience": "seniorzy",
                                       "stage": "pomysł"})
    with app.app_context():
        texts = [r[0] for r in db.query("SELECT body FROM notifications WHERE user_id=5")]
        texts += [r[0] for r in db.query("SELECT subject || body FROM emails WHERE user_id=5")]
    assert not any("44051401359" in t or "600 123 456" in t for t in texts)


@pytest.mark.parametrize("payload", [b'["a","b"]', b"42", b"[null]", b'{"innowacje": 5}', b'{"innowacje": null}'])
def test_import_wrong_json_shape_is_friendly_error(client, payload):
    token = login(client, "admin")
    resp = client.post("/admin/import", data={"_csrf": token, "plik": (io.BytesIO(payload), "x.json")},
                       content_type="multipart/form-data", follow_redirects=True)
    assert resp.status_code == 200 and "Nie udało się odczytać pliku" in resp.get_data(as_text=True)


def test_text_that_grows_after_masking_is_rejected_upfront(client):
    token = csrf_of(client)
    text = ("syn Jo i córka Al " * 90)[:1500]
    resp = client.post("/szukaj", data={"_csrf": token, "opis": text})
    assert resp.status_code == 422 and "za długi" in resp.get_data(as_text=True)


def test_template_justification_not_duplicated(client):
    token = csrf_of(client, "/razem/pisma/asystent")
    data = {"_csrf": token, "akcja": "ai", "rodzic": "Jan", "szkola": "SP 1", "klasa": "2b",
            "uzasadnienie": "potrzebuje pomocy.", "miejscowosc": "Wadowice"}
    first = client.post("/razem/pisma/asystent", data=data).get_data(as_text=True)
    assert ".." not in first.split("Uzasadnienie:")[1][:300]
    data["uzasadnienie"] = f"potrzebuje pomocy. {razem.LETTER_FALLBACK}"
    second = client.post("/razem/pisma/asystent", data=data).get_data(as_text=True)
    assert second.count(razem.LETTER_FALLBACK) == first.count(razem.LETTER_FALLBACK)


def test_guest_request_form_survives_login(client):
    token = csrf_of(client, "/razem/przewodnik")
    client.post("/razem/prosba/przewodnik-szukam", data={"_csrf": token, "powiat": "olkuski", "alias": "Mama Zosi",
                                                          "body": "Szukamy rodziny po diagnozie do rozmowy."})
    token = csrf_of(client, "/konto")
    client.post("/konto", data={"_csrf": token, "user_id": 1, "next": "/razem/przewodnik"})
    html = client.get("/razem/przewodnik").get_data(as_text=True)
    assert 'value="Mama Zosi"' in html and "Szukamy rodziny po diagnozie" in html
    assert 'value="Mama Zosi"' not in client.get("/razem/przewodnik").get_data(as_text=True)  # szkic jednorazowy


def test_event_signup_keeps_powiat_filter(client):
    token = login(client, "mieszkaniec")
    resp = client.post("/razem/wydarzenia/2/zapis", data={"_csrf": token, "powiat": "Kraków"})
    assert "powiat=Krak" in resp.headers["Location"]


def test_api_bad_param_names_the_parameter(client):
    resp = client.get("/api/v1/innowacje?obszar=xxx")
    assert resp.status_code == 400 and "obszar" in resp.get_json()["error"] and "wies" in resp.get_json()["dozwolone"]


def test_new_call_rejects_invalid_date(client, app):
    token = login(client, "admin")
    with app.app_context():
        n = db.one("SELECT COUNT(*) FROM calls")[0]
    client.post("/admin/nabory/nowy", data={"_csrf": token, "title": "Nabór testowy", "area": "wies",
                                            "description": "Opis naboru testowego.", "deadline": "abcdefghij"})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM calls")[0] == n
