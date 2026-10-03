"""Ładuje dane przykładowe (FIKCYJNE) do pustej bazy. Uruchamiane automatycznie przy pierwszym starcie."""
import json
import random
from datetime import datetime, timedelta, timezone

from core.match import Index, innovation_text
from data import seed_data as D


def ago(days, hours=10):
    t = datetime.now(timezone.utc) - timedelta(days=days)
    return t.replace(hour=hours % 24, minute=(days * 7) % 60, second=0).strftime("%Y-%m-%d %H:%M:%S")


def run(con):
    rnd = random.Random(7)
    uid = {}
    for i, (name, role, org, areas, bio, demo) in enumerate(D.USERS):
        email = f"user{i + 1}@przyklad.invalid"
        cur = con.execute(
            "INSERT INTO users (name, role, org, areas, email, bio, is_demo) VALUES (?,?,?,?,?,?,?)",
            (name, role, org, areas, email, bio, demo))
        uid[i] = cur.lastrowid

    for n, (title, summary, desc, area, powiat, stage, aud, org, kw) in enumerate(D.INNOVATIONS):
        con.execute(
            "INSERT INTO innovations (title, summary, description, area, powiat, stage, audience, org, keywords, "
            "created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (title, summary, desc, area, powiat, stage, aud, org, kw, ago(400 - n * 12)))
    innovations = con.execute("SELECT * FROM innovations").fetchall()
    index = Index([(r["id"], innovation_text(r)) for r in innovations])

    authors = [uid[0], uid[1], uid[2]]
    report_ids = []
    for n, (body, area, powiat, days, status, approved) in enumerate(D.REPORTS):
        author = uid[0] if n < 2 else authors[n % 3]
        cur = con.execute(
            "INSERT INTO reports (user_id, body, area, powiat, status, approved, created_at) VALUES (?,?,?,?,?,?,?)",
            (author, body, area, powiat, status, approved, ago(days, 9 + n)))
        rid = cur.lastrowid
        report_ids.append(rid)
        results = index.search(body, k=5)
        for r in results:
            # Część autorów oceniła dopasowania – dane do metryki trafności w panelu.
            fb = None
            if n % 2 == 0 and rnd.random() < 0.7:
                fb = 1 if r.score >= 0.45 else -1
            con.execute("INSERT INTO matches (report_id, innovation_id, score, feedback) VALUES (?,?,?,?)",
                        (rid, r.doc_id, r.score, fb))
        best = results[0].score if results else 0
        con.execute("UPDATE reports SET best_score = ? WHERE id = ?", (best, rid))

    for n, (title, area, kind, summary, body) in enumerate(D.MATERIALS):
        con.execute("INSERT INTO materials (title, area, kind, summary, body, created_at) VALUES (?,?,?,?,?,?)",
                    (title, area, kind, summary, body, ago(200 - n * 10)))

    for n, (title, area, desc, is_open, deadline) in enumerate(D.CALLS):
        con.execute("INSERT INTO calls (title, area, description, is_open, deadline, created_at) VALUES (?,?,?,?,?,?)",
                    (title, area, desc, is_open, deadline, ago(30 + n * 40)))

    idea_ids = []
    for n, (ui, title, essence, aud, stage, area, canvas) in enumerate(D.IDEAS):
        cur = con.execute(
            "INSERT INTO ideas (user_id, title, essence, audience, stage, area, canvas, is_example, created_at) "
            "VALUES (?,?,?,?,?,?,?,1,?)",
            (uid[ui], title, essence, aud, stage, area, json.dumps(canvas, ensure_ascii=False), ago(8 - n * 3)))
        idea_ids.append(cur.lastrowid)

    subjects = {"pomysl": idea_ids, "zgloszenie": report_ids}
    for stype, key, title, msgs in D.THREADS:
        cur = con.execute("INSERT INTO threads (subject_type, subject_id, title, created_at) VALUES (?,?,?,?)",
                          (stype, subjects[stype][key], title, ago(msgs[0][1])))
        for ui, days, body in msgs:
            con.execute("INSERT INTO messages (thread_id, user_id, body, created_at) VALUES (?,?,?,?)",
                        (cur.lastrowid, uid[ui], body, ago(days, 12)))

    for ui, area in [(0, "rodziny-zd"), (1, "rodziny-zd"), (1, "samotnosc"), (2, "wies"), (2, "seniorzy"),
                     (3, "rodziny-zd")]:
        con.execute("INSERT INTO follows (user_id, area) VALUES (?,?)", (uid[ui], area))

    inno = {r["title"]: r["id"] for r in innovations}
    tests = [
        (inno["Asystent zdrowia rodziny"], 1, "ocena", 5, "Sprawdziliśmy u nas – rodzice oszczędzają mnóstwo czasu."),
        (inno["Asystent zdrowia rodziny"], 2, "ocena", 4, "Dobre, ale potrzebny etat w CUS."),
        (inno["Bus na Telefon"], 2, "zgloszenie", None, "Chcemy przetestować w 5 sołectwach od stycznia."),
        (inno["Kawiarnia Treningowa „Po Szkole”"], 0, "usprawnienie", None,
         "Warto dodać dojazd dla uczestników z okolicznych wsi."),
        (inno["Telefon Życzliwości"], 1, "ocena", 5, ""),
    ]
    for n, (iid, ui, kind, rating, body) in enumerate(tests):
        con.execute("INSERT INTO tests (innovation_id, user_id, kind, rating, body, created_at) VALUES (?,?,?,?,?,?)",
                    (iid, uid[ui], kind, rating, body, ago(20 - n * 3)))

    for ui, body, link, days in [
        (0, "Hub odpowiedział na Twoje zgłoszenie „informacja o terapiach i turnusach”.", f"/zgloszenie/{report_ids[1]}", 8),
        (0, "Nowa innowacja w obszarze, który obserwujesz: „Mapa Wsparcia Rodzin”.", f"/biblioteka/{inno['Mapa Wsparcia Rodzin']}", 30),
        (4, "Nowe zgłoszenie z powiatu wadowickiego czeka na odpowiedź.", f"/zgloszenie/{report_ids[0]}", 3),
        (4, "Nowe zgłoszenie z powiatu dąbrowskiego czeka na odpowiedź.", f"/zgloszenie/{report_ids[7]}", 5),
    ]:
        con.execute("INSERT INTO notifications (user_id, body, link, created_at) VALUES (?,?,?,?)",
                    (uid[ui], body, link, ago(days)))
    con.commit()
