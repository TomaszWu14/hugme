"""Program „Jestem potrzebny”: zgłoszenia, oferty, pary, misje, odznaki, mapa pracy."""
import pytest

from conftest import csrf_of, login
from core import db
from data import potrzebny as P

PAGES = ["/razem/jestem-potrzebny", "/razem/jestem-potrzebny?powiat=Kraków", "/razem/jestem-potrzebny/zglos",
         "/razem/jestem-potrzebny/latwy", "/razem/jestem-potrzebny/oferta", "/razem/jestem-potrzebny/oferta?jako=rodzic",
         "/razem/jestem-potrzebny/buddy", "/razem/jestem-potrzebny/zasady", "/razem/praca", "/razem/praca?woj=malopolskie",
         "/razem/praca?powiat=Kraków"]


def count(app, sql, args=()):
    with app.app_context():
        return db.one(sql, args)[0]


@pytest.mark.parametrize("path", PAGES)
def test_public_pages_render(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert "Jestem potrzebny" in r.get_data(as_text=True)


def test_seed_has_full_picture(app):
    assert count(app, "SELECT COUNT(*) FROM offers WHERE status = 'zatwierdzone'") == 6
    assert count(app, "SELECT COUNT(*) FROM volunteers WHERE role = 'uczestnik'") == 5
    assert count(app, "SELECT COUNT(*) FROM volunteers WHERE role = 'buddy'") == 3
    assert count(app, "SELECT COUNT(*) FROM missions WHERE status = 'polaczone'") == 2
    assert count(app, "SELECT COALESCE(SUM(done), 0) FROM missions") == 4


# ── Zgłoszenia ────────────────────────────────────────────────────────────────
def signup_data(token, **over):
    data = {"_csrf": token, "alias": "Zosia", "powiat": "wadowicki", "age_group": "mlodziez", "interests": ["psy", "sport"],
            "days": ["sb", "rano"], "companion": "rodzic", "phone": "600 100 200", "consent": "1"}
    data.update(over)
    return data


def test_guest_is_sent_to_account_picker(client):
    r = client.post("/razem/jestem-potrzebny/zglos", data=signup_data(csrf_of(client)))
    assert r.status_code == 302 and "/konto" in r.headers["Location"]


def test_parent_signup_validates_and_saves(client, app):
    token = login(client, "mieszkaniec")
    r = client.post("/razem/jestem-potrzebny/zglos", data=signup_data(token, interests=[], consent=""))
    assert r.status_code == 422
    html = r.get_data(as_text=True)
    assert "Popraw 2 pola" in html and "Wybierz, co lubisz" in html and "Potrzebujemy zgody" in html
    r = client.post("/razem/jestem-potrzebny/zglos", data=signup_data(token, alias="Zosia 600123456"), follow_redirects=True)
    assert r.status_code == 200 and P.THANKS["uczestnik"] in r.get_data(as_text=True)
    with app.app_context():
        v = db.one("SELECT * FROM volunteers WHERE alias LIKE 'Zosia%'")
    assert v["interests"] == "psy,sport" and v["days"] == "sb,rano" and v["source"] == "rodzic" and v["consent"] == 1
    assert "600123456" not in v["alias"]  # telefon wpisany w pseudonim jest maskowany
    assert v["phone"] == "600 100 200"  # telefon w swoim polu zostaje – widzi go tylko Hub
    assert count(app, "SELECT COUNT(*) FROM notifications WHERE body LIKE 'Jestem potrzebny: nowy uczestnik%'") >= 1


def test_easy_text_signup_is_adult_self_report(client, app):
    token = login(client, "mieszkaniec")
    data = {"_csrf": token, "alias": "Ja", "powiat": "Kraków", "interests": ["starsi"], "days": ["popoludnie"],
            "companion": "buddy", "consent": "1"}
    r = client.post("/razem/jestem-potrzebny/latwy", data=data)
    assert r.status_code == 302 and r.headers["Location"].endswith("/dzienniczek")
    with app.app_context():
        v = db.one("SELECT * FROM volunteers WHERE alias = 'Ja'")
    assert v["age_group"] == "dorosly" and v["source"] == "latwy-tekst" and v["companion"] == "buddy"


def test_buddy_signup(client, app):
    token = login(client, "ekspert")
    data = {"_csrf": token, "alias": "Student Jan", "powiat": "Kraków", "days": ["sb"], "phone": "", "consent": "1"}
    assert client.post("/razem/jestem-potrzebny/buddy", data=data).status_code == 302
    assert count(app, "SELECT COUNT(*) FROM volunteers WHERE role = 'buddy' AND alias = 'Student Jan'") == 1


# ── Oferty ────────────────────────────────────────────────────────────────────
def offer_data(token, **over):
    data = {"_csrf": token, "institution": "Schronisko Testowe", "mission_kind": "psy", "title": "Spacer z psem w niedzielę",
            "body": "Spokojne psy, opiekun zawsze obok, godzina spaceru po parku.", "body_easy": "", "powiat": "Kraków",
            "days": ["nd", "rano"], "slots": "3", "for_whom": ["dorosly"], "provides": ["opiekun", "ubezpieczenie"],
            "requirements": "", "action": "wyslij"}
    data.update(over)
    return data


def test_offer_needs_hub_approval_before_listing(client, app):
    token = login(client, "ngo")
    r = client.post("/razem/jestem-potrzebny/oferta", data=offer_data(token, for_whom=[]))
    assert r.status_code == 422 and "kogo zapraszacie" in r.get_data(as_text=True)
    assert client.post("/razem/jestem-potrzebny/oferta", data=offer_data(token)).status_code == 302
    assert "Schronisko Testowe" not in client.get("/razem/jestem-potrzebny").get_data(as_text=True)
    with app.app_context():
        oid = db.one("SELECT id FROM offers WHERE institution = 'Schronisko Testowe'")["id"]
    token = login(client, "admin")
    client.post(f"/admin/potrzebny/oferta/{oid}/status", data={"_csrf": token, "status": "zatwierdzone"})
    assert "Schronisko Testowe" in client.get("/razem/jestem-potrzebny?powiat=Kraków").get_data(as_text=True)


def test_ai_simplify_without_key_keeps_form_and_explains(client):
    token = login(client, "ngo")
    r = client.post("/razem/jestem-potrzebny/oferta", data=offer_data(token, action="uprosc"))
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "AI jest niedostępne" in html and "Schronisko Testowe" in html


def test_parent_place_proposal_is_simpler(client, app):
    token = login(client, "mieszkaniec")
    data = {"_csrf": token, "institution": "Biblioteka w Suchej", "mission_kind": "inne", "title": "Układanie książek raz w tygodniu",
            "body": "Syn lubi porządek i książki; biblioteka jest blisko.", "powiat": "suski", "action": "wyslij"}
    assert client.post("/razem/jestem-potrzebny/oferta?jako=rodzic", data=data).status_code == 302
    with app.app_context():
        o = db.one("SELECT * FROM offers WHERE institution = 'Biblioteka w Suchej'")
    assert o["source"] == "rodzic" and o["status"] == "nowe"


# ── Panel: pary, misje, odznaki ───────────────────────────────────────────────
def test_panel_is_admin_only(client):
    assert client.get("/admin/potrzebny").status_code == 302
    login(client, "mieszkaniec")
    assert client.get("/admin/potrzebny").status_code == 403
    login(client, "admin")
    assert client.get("/admin/potrzebny").status_code == 200


def test_pair_rules_powiat_interest_age_and_buddy(app, client):
    from app.views.admin_potrzebny import pair_proposals
    login(client, "admin")
    with app.app_context():
        pairs = pair_proposals()
        names = {(v["alias"], o["institution"].split(" (")[0]) for v, o, _, _ in pairs}
        # Tomek (wadowicki, psy, młodzież) → schronisko w Wadowicach; Ola (krakowski, dzieci, dorosła) → świetlica w Krzeszowicach
        assert ("Tomek", "Schronisko dla zwierząt w Wadowicach") in names
        assert ("Ola", "Świetlica „Tęcza” w Krzeszowicach") in names
        # Marysia (myślenicki, dzieci/muzyka/sport, młodzież) nie pasuje do DPS (hospicjum → „starsi”), pasuje do biblioteki („inne”)
        assert ("Marysia", "Dom Pomocy Społecznej w Myślenicach") not in names
        assert ("Marysia", "Biblioteka Publiczna w Myślenicach") in names
        ola = next(p for p in pairs if p[0]["alias"] == "Ola")
        assert ola[3] is not None and ola[3]["role"] == "buddy" and ola[3]["powiat"] == "krakowski"
        assert pairs[0][2] >= pairs[-1][2]  # sortowanie: wspólne dni malejąco


def test_connect_confirm_mission_badges_and_close(client, app):
    token = login(client, "admin")
    with app.app_context():
        v = db.one("SELECT * FROM volunteers WHERE alias = 'Ola'")
        o = db.one("SELECT * FROM offers WHERE institution LIKE 'Świetlica%'")
        b = db.one("SELECT * FROM volunteers WHERE alias LIKE 'Pan Józef%'")
    r = client.post("/admin/potrzebny/polacz", data={"_csrf": token, "volunteer_id": v["id"], "offer_id": o["id"], "buddy_id": b["id"]},
                    follow_redirects=True)
    assert "Połączono: Ola" in r.get_data(as_text=True)
    with app.app_context():
        m = db.one("SELECT * FROM missions WHERE volunteer_id = ?", (v["id"],))
        assert m["buddy_id"] == b["id"] and m["status"] == "polaczone"
        assert db.one("SELECT status FROM volunteers WHERE id = ?", (v["id"],))["status"] == "polaczone"
        assert db.one("SELECT status FROM volunteers WHERE id = ?", (b["id"],))["status"] == "polaczone"
        assert db.one("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND body LIKE 'Hub połączył Cię z miejscem%'",
                      (v["user_id"],))[0] == 1
    # Misja odbyła się → odznaka „Pierwsza misja”; po 3 → odznaka tematyczna; po 5 → umiejętności
    for _ in range(5):
        client.post(f"/admin/potrzebny/misja/{m['id']}/odbyta", data={"_csrf": token})
    login(client, "mieszkaniec")  # Ola należy do konta mieszkanki (uid 0)
    html = client.get("/razem/jestem-potrzebny/dzienniczek").get_data(as_text=True)
    assert "Pierwsza misja" in html and "Pomocna dłoń" in html and "Starszy kolega" in html
    assert "odpowiedzialność" in html and "/razem/praca" in html
    assert client.get(f"/razem/jestem-potrzebny/dzienniczek/dyplom/{v['id']}").status_code == 200
    token = login(client, "admin")
    client.post(f"/admin/potrzebny/misja/{m['id']}/zamknij", data={"_csrf": token})
    with app.app_context():
        assert db.one("SELECT status FROM missions WHERE id = ?", (m["id"],))["status"] == "zamkniete"
        assert db.one("SELECT status FROM volunteers WHERE id = ?", (v["id"],))["status"] == "nowe"


def test_badges_and_skills_thresholds():
    assert [b[1] for b in P.badges_for(0, {})] == []
    assert [b[1] for b in P.badges_for(1, {"psy": 1})] == ["Pierwsza misja"]
    assert "Przyjaciel psów" in [b[1] for b in P.badges_for(3, {"psy": 3})]
    assert P.skills_for(4, {"psy": 4}) == []
    assert P.skills_for(5, {"psy": 3, "hospicjum": 2}) == ["punktualność", "opieka nad zwierzętami", "cierpliwość", "rozmowa z ludźmi"]


def test_inbox_lists_program_items(client):
    login(client, "admin")
    html = client.get("/admin?typ=potrzebny").get_data(as_text=True)
    assert "Uczestnik – Marysia" in html and "propozycja rodzica" in html or "Oferta – Schronisko w Krakowie" in html


# ── Mapa pracy ────────────────────────────────────────────────────────────────
def test_workplace_proposal_needs_source_and_approval(client, app):
    token = login(client, "ngo")
    data = {"_csrf": token, "name": "Kawiarnia Próbna", "kind": "spoleczne", "city": "Nowy Sącz", "voivodeship": "malopolskie",
            "powiat": "Nowy Sącz", "url": "brak", "note": "obsługa gości"}
    r = client.post("/razem/praca/zglos", data=data, follow_redirects=True)
    assert "Podaj link do źródła" in r.get_data(as_text=True)
    data["url"] = "https://przyklad.invalid/artykul"
    client.post("/razem/praca/zglos", data=data)
    assert "Kawiarnia Próbna" not in client.get("/razem/praca").get_data(as_text=True)
    with app.app_context():
        wid = db.one("SELECT id FROM workplaces WHERE name = 'Kawiarnia Próbna'")["id"]
    before = client.get("/razem/praca?powiat=Nowy Sącz").get_data(as_text=True)
    token = login(client, "admin")
    client.post(f"/admin/potrzebny/miejsce/{wid}/status", data={"_csrf": token, "status": "zatwierdzone"})
    after = client.get("/razem/praca?powiat=Nowy Sącz").get_data(as_text=True)
    assert "Kawiarnia Próbna" in after and "Kawiarnia Próbna" not in before


def test_map_counts_match_list(client, app):
    html = client.get("/razem/praca").get_data(as_text=True)
    with app.app_context():
        total = db.one("SELECT COUNT(*) FROM workplaces WHERE status = 'zatwierdzone'")[0]
        mp = db.one("SELECT COUNT(*) FROM workplaces WHERE status = 'zatwierdzone' AND voivodeship = 'malopolskie'")[0]
    assert f"Polska – {total} miejsc na mapie" in html
    assert f'aria-label="małopolskie: {mp} miejsc"' in html
    assert html.count("<path class=\"map__r") == 16 + 22


# ── Role: kto może wysłać który formularz ─────────────────────────────────────
@pytest.mark.parametrize("role,path,data_fn,ok", [
    ("gmina", "/razem/jestem-potrzebny/zglos", signup_data, False),
    ("ngo", "/razem/jestem-potrzebny/latwy", signup_data, False),
    ("admin", "/razem/jestem-potrzebny/buddy", lambda t: {"_csrf": t, "alias": "Hub", "powiat": "Kraków", "days": ["sb"], "consent": "1"}, False),
    ("mieszkaniec", "/razem/jestem-potrzebny/oferta", offer_data, False),
    ("gmina", "/razem/jestem-potrzebny/oferta", offer_data, True),
    ("mieszkaniec", "/razem/jestem-potrzebny/zglos", signup_data, True),
])
def test_only_matching_role_can_submit(client, role, path, data_fn, ok):
    token = login(client, role)
    r = client.post(path, data=data_fn(token))
    assert (r.status_code == 302) if ok else (r.status_code == 403)


def test_wrong_role_sees_hint_instead_of_submit(client):
    login(client, "gmina")
    html = client.get("/razem/jestem-potrzebny/zglos").get_data(as_text=True)
    assert "zmień konto" in html and "Wyślij zgłoszenie" not in html
    login(client, "mieszkaniec")
    html = client.get("/razem/jestem-potrzebny/oferta").get_data(as_text=True)
    assert "konto organizacji albo gminy" in html and "Wyślij ofertę do Hubu" not in html


def test_double_connect_creates_one_mission(client, app):
    token = login(client, "admin")
    with app.app_context():
        v = db.one("SELECT id FROM volunteers WHERE alias = 'Tomek'")
        o = db.one("SELECT id FROM offers WHERE institution LIKE 'Schronisko dla zwierząt w Wadowicach%'")
    data = {"_csrf": token, "volunteer_id": v["id"], "offer_id": o["id"]}
    assert client.post("/admin/potrzebny/polacz", data=data).status_code == 302
    assert client.post("/admin/potrzebny/polacz", data=data).status_code == 400
    assert count(app, "SELECT COUNT(*) FROM missions WHERE volunteer_id = ?", (v["id"],)) == 1


def test_pair_rejected_when_offer_has_no_free_slots(client, app):
    """Issue #17: oferta z 2 miejscami – trzecie połączenie jest odrzucane."""
    token = login(client, "admin")
    with app.app_context():
        oid = db.one("SELECT id FROM offers WHERE status = 'zatwierdzone' LIMIT 1")["id"]
        db.execute("DELETE FROM missions WHERE offer_id = ?", (oid,))
        db.execute("UPDATE offers SET slots = 2 WHERE id = ?", (oid,))
        vids = [r["id"] for r in db.query("SELECT id FROM volunteers WHERE role = 'uczestnik' AND status = 'nowe'")]
    assert len(vids) >= 3
    codes = [client.post("/admin/potrzebny/polacz", data={"_csrf": token, "volunteer_id": vid, "offer_id": oid}).status_code
             for vid in vids[:3]]
    assert codes == [302, 302, 400]
    r = client.post("/admin/potrzebny/polacz", data={"_csrf": token, "volunteer_id": vids[2], "offer_id": oid})
    assert "nie ma już wolnych miejsc" in r.get_data(as_text=True)
    assert count(app, "SELECT COUNT(*) FROM missions WHERE offer_id = ?", (oid,)) == 2
    assert count(app, "SELECT status FROM volunteers WHERE id = ?", (vids[2],)) == "nowe"
