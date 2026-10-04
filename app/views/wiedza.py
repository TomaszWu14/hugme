"""Zasobnik wiedzy: wyzwania Małopolski, Biblioteka Innowacji (filtry, filmy), materiały, ścieżka rodziny.
Tester innowacji: zgłoszenie do testu, ocena 1–5, propozycja usprawnienia (powiadamia Hub)."""
import re

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from app.auth import login_required
from app.views.komunikacja import thread_view
from core import db, notify
from core.domain import AREAS, AUDIENCES, POWIATY, STAGES, TEST_KINDS
from core.match import Index, innovation_text
from core.privacy import mask

bp = Blueprint("wiedza", __name__)

_YT = re.compile(r"(?:youtube(?:-nocookie)?\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w-]{11})")


def embed_url(url):
    """Tylko YouTube w trybie bez ciasteczek (zgodnie z CSP frame-src)."""
    m = _YT.search(url or "")
    return f"https://www.youtube-nocookie.com/embed/{m.group(1)}" if m else None


FAMILY_PATH = [
    {"key": "diagnoza", "title": "Diagnoza i pierwsze tygodnie",
     "text": "Dużo emocji i dużo informacji naraz. Najważniejsze: nie zostawać z tym samemu. "
             "Warto poznać inne rodziny i dowiedzieć się, kto w okolicy pomaga.",
     "ask": ["Kto w gminie koordynuje wsparcie dla rodzin?", "Gdzie jest najbliższa grupa rodziców?"],
     "innovations": ["Klub Rodziców i Rodzeństwa", "Mapa Wsparcia Rodzin"],
     "materials": ["Gdzie szukać pomocy dla rodziny dziecka z niepełnosprawnością"]},
    {"key": "zdrowie", "title": "Zdrowie i wizyty u specjalistów",
     "text": "Dziecko może potrzebować regularnych wizyt u kilku specjalistów. Pomaga wspólny kalendarz "
             "i ktoś, kto pomoże je poukładać.",
     "ask": ["Czy da się umówić kilka wizyt jednego dnia?", "Kto pomoże pilnować terminów i skierowań?"],
     "innovations": ["Asystent zdrowia rodziny", "Dzień Specjalistów w jednym miejscu"],
     "materials": ["Jak przygotować się do wizyty u specjalisty"]},
    {"key": "szkola", "title": "Przedszkole i szkoła",
     "text": "Integracja zaczyna się od klasy i nauczyciela. Dobrze przygotowana klasa to przyjaźnie "
             "i spokojniejsze poranki.",
     "ask": ["Czy szkoła ma asystenta ucznia?", "Czy klasa może mieć warsztaty przed startem roku?"],
     "innovations": ["Klasa w Ruchu – integracja od pierwszego dnia"],
     "materials": []},
    {"key": "doroslosc", "title": "Dorosłość: praca i samodzielność",
     "text": "Po szkole łatwo o pustkę. Trening pracy, wsparcie trenera i mieszkania treningowe "
             "dają szansę na samodzielne życie.",
     "ask": ["Gdzie jest najbliższy trening pracy?", "Czy w powiecie są mieszkania treningowe?"],
     "innovations": ["Kawiarnia Treningowa „Po Szkole”"],
     "materials": []},
]


@bp.route("/wiedza")
def index():
    counts = {r["area"]: r["n"] for r in db.query("SELECT area, COUNT(*) AS n FROM innovations GROUP BY area")}
    return render_template("wiedza.html", counts=counts,
                           materials=db.query("SELECT * FROM materials ORDER BY area, title"))


@bp.route("/wiedza/obszar/<slug>")
def area(slug):
    if slug not in AREAS:
        abort(404)
    following = bool(g.user and db.one("SELECT 1 FROM follows WHERE user_id = ? AND area = ?", (g.user["id"], slug)))
    return render_template(
        "obszar.html", slug=slug, a=AREAS[slug], following=following,
        innovations=db.query("SELECT * FROM innovations WHERE area = ? ORDER BY title", (slug,)),
        materials=db.query("SELECT * FROM materials WHERE area = ?", (slug,)),
        calls=db.query("SELECT * FROM calls WHERE area = ? AND is_open = 1", (slug,)),
        report_count=db.one("SELECT COUNT(*) FROM reports WHERE area = ?", (slug,))[0],
    )


@bp.route("/wiedza/sciezka-rodziny")
def family_path():
    inn = {r["title"]: r for r in db.query("SELECT id, title, summary FROM innovations")}
    mats = {r["title"]: r for r in db.query("SELECT id, title FROM materials")}
    return render_template("sciezka.html", steps=FAMILY_PATH, inn=inn, mats=mats)


@bp.route("/wiedza/material/<int:mid>")
def material(mid):
    m = db.one("SELECT * FROM materials WHERE id = ?", (mid,))
    if m is None:
        abort(404)
    return render_template("material.html", m=m, is_path=m["title"].startswith("Ścieżka rodziny"))


@bp.route("/biblioteka")
@bp.route("/tester", endpoint="tester", defaults={"tester": True})
def library(tester=False):
    """Biblioteka; pod /tester ta sama lista jako wejście do Testera (bez filtra etapu: prototyp i test)."""
    f = {k: request.args.get(k, "") for k in ("obszar", "powiat", "etap", "grupa", "q")}
    sql, args = "SELECT * FROM innovations WHERE 1=1", []
    for key, col, allowed in [("obszar", "area", AREAS), ("powiat", "powiat", POWIATY),
                              ("etap", "stage", STAGES), ("grupa", "audience", AUDIENCES)]:
        if f[key] in allowed:
            sql += f" AND {col} = ?"
            args.append(f[key])
    rows = db.query(sql + " ORDER BY created_at DESC", args)
    if f["q"].strip():
        by_id = {r["id"]: r for r in rows}
        hits = Index([(r["id"], innovation_text(r)) for r in rows]).search(f["q"][:200], k=len(rows) or 1)
        rows = [by_id[h.doc_id] for h in hits]
    if tester and not f["etap"]:
        trial = [r for r in rows if r["stage"] in ("prototyp", "test")]
        rows = trial if len(trial) >= 4 else rows
    ratings = {r["innovation_id"]: r for r in db.query(
        "SELECT innovation_id, ROUND(AVG(rating), 1) AS avg, COUNT(rating) AS n FROM tests "
        "WHERE rating IS NOT NULL GROUP BY innovation_id")}
    return render_template("biblioteka.html", rows=rows, f=f, ratings=ratings, tester=tester,
                           powiaty=POWIATY, stages=STAGES, audiences=AUDIENCES)


@bp.route("/biblioteka/<int:iid>")
def innovation(iid):
    i = db.one("SELECT * FROM innovations WHERE id = ?", (iid,))
    if i is None:
        abort(404)
    rating = db.one("SELECT ROUND(AVG(rating), 1) AS avg, COUNT(rating) AS n FROM tests "
                    "WHERE innovation_id = ? AND rating IS NOT NULL", (iid,))
    tests = db.query("SELECT t.*, u.name FROM tests t JOIN users u ON u.id = t.user_id "
                     "WHERE t.innovation_id = ? ORDER BY t.created_at DESC", (iid,))
    # Potwierdzenie (flash „sekcja”) pokazujemy w jednej sekcji: Testera albo rozmowy.
    return render_template("innowacja.html", i=i, video=embed_url(i["video_url"]), rating=rating,
                           tests=tests, thread=thread_view("innowacja", iid), kinds=TEST_KINDS,
                           tester_ok=session.pop("tester_ok", False))


@bp.post("/biblioteka/<int:iid>/test")
@login_required
def test_action(iid):
    i = db.one("SELECT id, title FROM innovations WHERE id = ?", (iid,))
    if i is None:
        abort(404)
    kind = request.form.get("kind")
    if kind not in TEST_KINDS:
        abort(400)
    rating = request.form.get("rating", type=int)
    body, _ = mask(request.form.get("tresc", "").strip()[:1500])
    link = url_for("wiedza.innovation", iid=iid) + "#tester"
    if kind == "ocena" and rating not in range(1, 6):
        flash("Wybierz ocenę od 1 do 5.", "error")
        return redirect(link)
    if kind in ("zgloszenie", "usprawnienie") and len(body) < 10:
        flash("Napisz kilka słów (co najmniej 10 znaków) – np. gdzie i kiedy chcesz testować albo co poprawić.", "error")
        return redirect(link)
    if kind == "ocena":  # jedna ocena na osobę – nowa zastępuje poprzednią
        db.execute("DELETE FROM tests WHERE innovation_id = ? AND user_id = ? AND kind = 'ocena'", (iid, g.user["id"]))
    db.execute("INSERT INTO tests (innovation_id, user_id, kind, rating, body, created_at) VALUES (?,?,?,?,?,?)",
               (iid, g.user["id"], kind, rating if kind == "ocena" else None, body, db.now()))
    what = {"zgloszenie": "zgłoszenie do testu", "ocena": f"ocena {rating}/5", "usprawnienie": "propozycja usprawnienia"}[kind]
    notify.notify_admins(f"Tester: {what} – „{i['title']}”", link, exclude=g.user["id"])
    flash({"zgloszenie": "Zgłoszenie do testu wysłane. Hub skontaktuje Cię z autorami innowacji "
                         "– zobaczysz to w Powiadomieniach.",
           "ocena": "Zapisaliśmy Twoją ocenę (jedna ocena na osobę – nowa zastępuje poprzednią).",
           "usprawnienie": "Dziękujemy! Przekazaliśmy propozycję autorom i Hubowi."}[kind], "sekcja")
    session["tester_ok"] = True
    return redirect(link)
