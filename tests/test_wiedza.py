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
        # Gmina oceniła już w seedzie – nowa ocena zastępuje starą (J3-03), więc przybywają 2 wiersze
        assert db.one("SELECT COUNT(*) FROM tests WHERE user_id = 3 AND innovation_id = 1")[0] == before + 2
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


def test_one_rating_per_person_newest_wins(client, app):
    """J3-03: druga ocena tej samej osoby zastępuje pierwszą, a potwierdzenie stoi w sekcji Testera."""
    token = login(client, "gmina")
    client.post("/biblioteka/3/test", data={"_csrf": token, "kind": "ocena", "rating": 5})
    resp = client.post("/biblioteka/3/test", data={"_csrf": token, "kind": "ocena", "rating": 2}, follow_redirects=True)
    tester = resp.get_data(as_text=True).split('id="tester"')[1]
    assert "Zapisaliśmy Twoją ocenę" in tester
    with app.app_context():
        r = db.one("SELECT COUNT(*) AS n, AVG(rating) AS avg FROM tests "
                   "WHERE innovation_id = 3 AND user_id = 3 AND kind = 'ocena'")
        assert (r["n"], r["avg"]) == (1, 2)


def test_tester_entry_page(client):
    """K-04: Tester ma własne wejście z H1, krokami i kartami z akcjami."""
    html = client.get("/tester").get_data(as_text=True)
    assert "<h1>Tester innowacji</h1>" in html and "Zaproponuj poprawkę" in html
    assert "#tester" in html and "Zapytaj autorów" in html
    assert "Etap: wdrożenie" not in html  # tylko prototypy i testy


def test_guest_gets_one_click_demo_buttons(app):
    """K-01/K-03: gość w demo wchodzi na konto jednym kliknięciem i wraca do sekcji."""
    app.config["DEMO_MODE"] = True
    html = app.test_client().get("/biblioteka/1").get_data(as_text=True)
    assert 'value="/biblioteka/1#watek"' in html and 'value="/biblioteka/1#tester"' in html
    assert "Dopasuj do mojej gminy" in html and "4,5 na 5 (2 oceny)" in html
