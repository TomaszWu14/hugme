import json

from conftest import csrf_of, login
from core import ai, db

CTX = {"institution": "gmina", "audience": "seniorzy", "scale": "srednia", "budget": "maly", "powiat": "dąbrowski",
       "problem": "Starsi mieszkańcy pięciu sołectw nie mają jak dojechać do przychodni."}


def test_broker_rule_card_without_ai(client, app):
    token = login(client, "gmina")
    resp = client.post("/posrednik", data={"_csrf": token, **CTX})
    assert resp.status_code == 302
    html = client.get(resp.headers["Location"]).get_data(as_text=True)
    for label in ("Opis usługi", "Odbiorcy", "Zespół", "Kroki wdrożenia", "Partnerzy", "Koszty", "Skąd finansowanie",
                  "Mierniki", "Ryzyka"):
        assert label in html
    assert "Podpowiedź z szablonu (bez AI)" in html and "Bus na Telefon" in html
    assert "zł" not in html


def test_broker_validation_and_guest(client):
    token = csrf_of(client, "/posrednik")
    assert "/konto" in client.post("/posrednik", data={"_csrf": token, **CTX}).headers["Location"]
    token = login(client, "ngo")
    resp = client.post("/posrednik", data={"_csrf": token, **CTX, "scale": "ogromna", "problem": "x"})
    assert resp.status_code == 422 and "error-summary" in resp.get_data(as_text=True)


def test_broker_card_private(client):
    token = login(client, "gmina")
    url = client.post("/posrednik", data={"_csrf": token, **CTX}).headers["Location"]
    login(client, "ngo")
    assert client.get(url).status_code == 403


def test_broker_ai_card_is_labelled_and_strips_amounts(client, monkeypatch):
    fake = {k: ["Krok A", "Krok B"] for k in ("kroki", "partnerzy", "finansowanie", "mierniki", "ryzyka")}
    fake.update(opis="Bus na żądanie dla sołectw", odbiorcy="Seniorzy", zespol="Koordynator",
                koszty=["Paliwo – ok. 12 000 zł rocznie", "Kierowca"])
    monkeypatch.setattr(ai, "ask_json", lambda *a, **k: fake)
    token = login(client, "gmina")
    html = client.get(client.post("/posrednik", data={"_csrf": token, **CTX}).headers["Location"]).get_data(as_text=True)
    assert "Wygenerowane przez AI" in html
    assert "12 000 zł" not in html and "[kwota do wyceny]" in html


def test_matchmaking_ai_enrichment_is_labelled(client, monkeypatch):
    monkeypatch.setattr(ai, "ask_json", lambda *a, **k: {"podsumowanie": "Rodzinom potrzebna koordynacja wizyt.",
                                                          "slowa": ["koordynacja", "kalendarz"], "obszar": "rodziny-zd"})
    token = csrf_of(client)
    client.post("/szukaj", data={"_csrf": token, "opis": "Rodzice dzieci z zespołem Downa jeżdżą do wielu lekarzy."})
    html = client.get("/wyniki").get_data(as_text=True)
    assert "Wygenerowane przez AI" in html and "Rodzinom potrzebna koordynacja wizyt." in html


def test_ai_disabled_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("AI_DISABLED", raising=False)
    assert ai.enabled() is False and ai.ask("cokolwiek") is None


def test_api_match(client):
    resp = client.post("/api/v1/dopasuj", json={"opis": "Seniorzy nie umieją korzystać ze smartfona, tel. 600 123 456", "limit": 3})
    data = resp.get_json()
    assert resp.status_code == 200 and len(data["wyniki"]) == 3
    assert data["wyniki"][0]["tytul"] in ("Cyfrowy Przewodnik w bibliotece", "Tablet z Bibliotecznej Półki")
    assert "TELEFON" in data["ukryte_dane"] and "600 123 456" not in data["opis_zamaskowany"]
    assert {"trafnosc", "etykieta", "dlaczego", "url"} <= set(data["wyniki"][0])


def test_api_match_validation(client):
    assert client.post("/api/v1/dopasuj", data="nie json").status_code == 400
    assert client.post("/api/v1/dopasuj", json={"opis": "krótko"}).status_code == 422
    assert client.post("/api/v1/dopasuj", json={"opis": "x" * 20, "limit": 99}).status_code == 422


def test_api_innovations_and_filters(client):
    data = client.get("/api/v1/innowacje").get_json()
    assert data["liczba"] == 24 and data["innowacje"][0]["przyklad"] is True
    assert client.get("/api/v1/innowacje?obszar=wies").get_json()["liczba"] == 2
    resp = client.get("/api/v1/innowacje?obszar=zle")
    assert resp.status_code == 400 and resp.is_json


def test_static_pages(client):
    assert "WCAG 2.1" in client.get("/dostepnosc").get_data(as_text=True)
    assert "PESEL" in client.get("/prywatnosc").get_data(as_text=True)
