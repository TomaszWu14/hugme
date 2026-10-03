from conftest import login
from core import db


def test_knowledge_hub_pages(client):
    html = client.get("/wiedza").get_data(as_text=True)
    assert "Wyzwania Małopolski" in html and "Ścieżka rodziny" in html and "Materiały edukacyjne" in html
    assert client.get("/wiedza/obszar/rodziny-zd").status_code == 200
    assert client.get("/wiedza/obszar/nie-ma").status_code == 404
    path = client.get("/wiedza/sciezka-rodziny").get_data(as_text=True)
    for step in ("Diagnoza", "Zdrowie", "szkoła", "Dorosłość"):
        assert step.lower() in path.lower()
    assert client.get("/wiedza/material/1").status_code == 200


def test_library_filters(client):
    html = client.get("/biblioteka?obszar=wies").get_data(as_text=True)
    assert "Bus na Telefon" in html and "Asystent zdrowia rodziny" not in html
    assert "Znaleziono: 2" in html
    html = client.get("/biblioteka?q=smartfon").get_data(as_text=True)
    assert "Cyfrowy Przewodnik" in html
    # Nieznane wartości filtrów są ignorowane (walidacja po stronie serwera)
    assert "Znaleziono: 24" in client.get("/biblioteka?obszar=';DROP").get_data(as_text=True)


def test_innovation_detail_with_tester_and_video_policy(client, app):
    from app.views.wiedza import embed_url
    assert embed_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"
    assert embed_url("https://evil.example/video") is None
    html = client.get("/biblioteka/1").get_data(as_text=True)
    assert "Tester innowacji" in html and "PRZYKŁAD" in html


def test_tester_actions_notify_hub(client, app):
    token = login(client, "gmina")
    with app.app_context():
        before = db.one("SELECT COUNT(*) FROM tests WHERE user_id = 3 AND innovation_id = 1")[0]
    client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "ocena", "rating": 4})
    client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "zgloszenie", "tresc": "Chcemy testować od stycznia w 3 sołectwach."})
    client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "usprawnienie", "tresc": "Dodać dowóz z okolicznych wsi."})
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM tests WHERE user_id = 3 AND innovation_id = 1")[0] == before + 3
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id = 5 AND body LIKE 'Tester:%'")[0] == 3


def test_tester_validation(client, app):
    token = login(client, "ngo")
    client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "ocena", "rating": 9})
    client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "zgloszenie", "tresc": "x"})
    assert client.post("/biblioteka/1/test", data={"_csrf": token, "kind": "hack"}).status_code == 400
    with app.app_context():
        assert db.one("SELECT COUNT(*) FROM tests WHERE user_id = 2 AND innovation_id = 1")[0] == 1  # tylko z seeda


def test_question_on_innovation_notifies_experts(client, app):
    token = login(client, "mieszkaniec")
    client.post("/watek/innowacja/1", data={"_csrf": token, "tresc": "Czy to działa też w małej gminie?"})
    with app.app_context():
        # Innowacja 1 = obszar rodziny-zd → ekspertka Ewa (id 4) i inni eksperci obszaru
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id = 4 AND body LIKE 'Pytanie do ekspertów%'")[0] == 1
