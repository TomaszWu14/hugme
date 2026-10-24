"""Aktywność gościa demo: ekrany, sekcje, czas wizyty, push „zaangażowany gość”; nigdy nie psuje odpowiedzi."""
import json
import sqlite3

import pytest
from itsdangerous import URLSafeTimedSerializer

from app import create_app, visitor_activity, visitor_notify
from tests.conftest import csrf_of
from tests.test_gate import submit
from tests.test_visitor_notify import URL, SyncThread


@pytest.fixture
def gated(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "a.db"), "SECRET_KEY": "t", "DEMO_MODE": True,
                       "DEMO_VISITOR_GATE": True})


@pytest.fixture
def gc(gated):
    return gated.test_client()


@pytest.fixture
def pushes(monkeypatch):
    calls = []
    monkeypatch.setattr(visitor_notify.threading, "Thread", SyncThread)
    monkeypatch.setattr(visitor_notify, "_send", lambda *args: calls.append(args))
    return calls


def activity(app):
    con = sqlite3.connect(app.config["DATABASE"])
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT page_views, last_seen_at, sections FROM demo_visitors ORDER BY id")]
    finally:
        con.close()


def test_three_pages_counted_with_sections(gated, gc):
    assert submit(gc).status_code == 302
    for path in ("/biblioteka", "/biblioteka?q=x", "/"):
        assert gc.get(path).status_code == 200
    [row] = activity(gated)
    assert row["page_views"] == 3 and row["last_seen_at"]
    assert json.loads(row["sections"]) == {"biblioteka": 2, "start": 1}


def test_static_health_api_404_post_and_gate_not_counted(gated, gc):
    submit(gc)
    gc.get("/zdrowie")
    gc.get("/static/css/style.css")
    gc.get("/api/v1/health")
    assert gc.get("/nie-ma-takiej-strony").status_code == 404
    gc.get("/wejscie")
    gc.post("/konto", data={"_csrf": "zly"})
    assert activity(gated)[0]["page_views"] == 0


def test_visitor_without_flag_or_with_forged_flag_not_counted(gated, gc):
    submit(gc)
    other = gated.test_client()
    assert other.get("/biblioteka").status_code == 302  # bez flagi – do bramki
    forged = URLSafeTimedSerializer("inny-klucz", salt="demo-visitor").dumps({"v": 1})
    other.set_cookie("visitor_ok", forged)
    assert other.get("/biblioteka").status_code == 302
    assert activity(gated)[0]["page_views"] == 0


def test_old_flag_without_id_admits_but_not_counted(gated, gc):
    submit(gc)
    old = gated.test_client()
    with gated.app_context():
        old.set_cookie("visitor_ok", URLSafeTimedSerializer("t", salt="demo-visitor").dumps(1))
    assert old.get("/biblioteka").status_code == 200
    assert activity(gated)[0]["page_views"] == 0


def test_engaged_threshold_sends_exactly_one_push(monkeypatch, gated, gc, pushes):
    monkeypatch.setenv("NTFY_URL", URL)
    monkeypatch.setenv("NTFY_ENGAGED_VIEWS", "3")
    submit(gc)
    for _ in range(6):
        gc.get("/biblioteka")
    assert len(pushes) == 2  # wejście + jeden „zaangażowany”
    _url, body, _token, title, tags, priority = pushes[1]
    assert body == "Anna Kowalska (Acme Sp. z o.o.) obejrzał już 3 ekranów w hugme"
    assert (title, tags, priority) == ("Gosc oglada demo: hugme", "eyes", "default")


def test_engaged_push_urgent_for_watched_company(monkeypatch, gc, pushes):
    monkeypatch.setenv("NTFY_URL", URL)
    monkeypatch.setenv("NTFY_ENGAGED_VIEWS", "1")
    monkeypatch.setenv("NTFY_WATCH_COMPANIES", "acme")
    submit(gc)
    gc.get("/biblioteka")
    assert pushes[1][3:] == ("Gosc oglada demo: hugme", "eyes", "urgent")


@pytest.mark.parametrize("value", ["0", "nie-liczba"])
def test_engaged_disabled_or_invalid(monkeypatch, gc, pushes, value):
    monkeypatch.setenv("NTFY_URL", URL)
    monkeypatch.setenv("NTFY_ENGAGED_VIEWS", value)
    submit(gc)
    for _ in range(11):
        gc.get("/biblioteka")
    assert len(pushes) == (1 if value == "0" else 2)  # nieprawidłowa wartość = domyślne 10


def test_error_while_counting_does_not_break_response(monkeypatch, gated, gc):
    submit(gc)

    def boom(*args, **kwargs):
        raise sqlite3.OperationalError("baza zablokowana")

    monkeypatch.setattr(visitor_activity.db, "now", boom)
    r = gc.get("/biblioteka")
    assert r.status_code == 200 and "Biblioteka" in r.get_data(as_text=True)
    assert activity(gated)[0]["page_views"] == 0


def test_sections_limited_to_20_keys(gated, gc):
    submit(gc)
    con = sqlite3.connect(gated.config["DATABASE"])
    con.execute("UPDATE demo_visitors SET sections = ?", (json.dumps({f"s{i}": 1 for i in range(20)}),))
    con.commit()
    con.close()
    gc.get("/biblioteka")  # nowa sekcja ponad limit – ignorowana, ekran policzony
    gc.get("/biblioteka")
    [row] = activity(gated)
    sections = json.loads(row["sections"])
    assert row["page_views"] == 2 and len(sections) == 20 and "biblioteka" not in sections


def test_existing_section_still_counted_at_limit(gated, gc):
    submit(gc)
    con = sqlite3.connect(gated.config["DATABASE"])
    con.execute("UPDATE demo_visitors SET sections = ?",
                (json.dumps({**{f"s{i}": 1 for i in range(19)}, "biblioteka": 4}),))
    con.commit()
    con.close()
    gc.get("/biblioteka")
    assert json.loads(activity(gated)[0]["sections"])["biblioteka"] == 5


@pytest.mark.parametrize("path, section", [("/", "start"), ("/palety/123", "palety"), ("/Biblioteka/x", "biblioteka"),
                                           ("/a%20b.c", "a20bc"), ("/" + "x" * 50, "x" * 40), ("/ąę", None)])
def test_section_of(path, section):
    assert visitor_activity.section_of(path) == section


def test_list_shows_activity_columns(gated, gc):
    submit(gc)
    gc.get("/biblioteka")
    gc.get("/biblioteka")
    gc.get("/")
    con = sqlite3.connect(gated.config["DATABASE"])
    con.execute("UPDATE demo_visitors SET created_at = datetime(last_seen_at, '-12 minutes')")
    con.execute("INSERT INTO demo_visitors (created_at, first_name, last_name, company) VALUES "
                "('2026-10-01 10:00:00', 'Bez', 'Ruchu', 'Firma')")
    con.commit()
    con.close()
    gc.post("/konto", data={"_csrf": csrf_of(gc, "/"), "user_id": 5})  # admin
    html = gc.get("/admin/odwiedzajacy").get_data(as_text=True)
    for header in ("Ekrany", "Czas", "Najczęściej"):
        assert f'<th scope="col">{header}</th>' in html
    # + „/” przy pobraniu tokenu CSRF; strony po przełączeniu na admina liczą się już po wyrenderowaniu listy
    assert "<td>4</td><td>ok. 12 min</td><td>biblioteka (2), start (2)</td>" in html
    assert "<td>0</td><td>—</td><td>—</td>" in html


def test_summary_top_three():
    row = {"page_views": 9, "created_at": "2026-10-01 10:00:00", "last_seen_at": "2026-10-01 10:30:20",
           "sections": json.dumps({"a": 1, "b": 5, "c": 2, "d": 1})}
    assert visitor_activity.summary(row) == {"views": 9, "duration": "ok. 30 min", "top": "b (5), c (2), a (1)"}


def test_migration_adds_columns_to_existing_table(tmp_path):
    path = tmp_path / "stara.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE demo_visitors (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP NOT NULL, "
                "first_name TEXT NOT NULL, last_name TEXT NOT NULL, company TEXT NOT NULL)")
    con.execute("INSERT INTO demo_visitors (created_at, first_name, last_name, company) VALUES ('2026-10-01 10:00:00', 'A', 'B', 'C')")
    con.commit()
    con.close()
    create_app({"TESTING": True, "DATABASE": str(path), "SECRET_KEY": "t"})
    con = sqlite3.connect(path)
    assert con.execute("SELECT page_views, last_seen_at, sections FROM demo_visitors").fetchone() == (0, None, "{}")
    con.close()
