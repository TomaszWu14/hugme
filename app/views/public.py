"""Strona startowa i matchmaking: opis problemu → dopasowania → zapis zgłoszenia → ocena trafności."""
from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, session, url_for

from app.auth import login_required
from app.views.komunikacja import ensure_thread, thread_view
from core import catalog, db, notify
from core.domain import AREAS, POWIATY
from core.privacy import describe, mask
from data.razem import MY_TOPICS

bp = Blueprint("public", __name__)

EXAMPLE_PROBLEM = (
    "Nasze dzieci z zespołem Downa potrzebują wizyt u wielu specjalistów – kardiologa, logopedy, "
    "endokrynologa. Każda wizyta to inny termin i inna przychodnia, a rodzice są tym zmęczeni."
)
MIN_LEN, MAX_LEN = 15, 1500
MY_TOPIC_LABELS = {slug: label for slug, label, _ in MY_TOPICS}


def validate_problem(text):
    if not text:
        return "Napisz kilka słów o tym, co jest trudne."
    if len(text) < MIN_LEN:
        return "Napisz trochę więcej – np. kogo to dotyczy i co sprawia trudność. Wystarczą 1–2 zdania."
    if len(text) > MAX_LEN:
        return f"Opis jest za długi. Skróć go do {MAX_LEN} znaków – najważniejsze wystarczy."
    return None


@bp.route("/")
def home():
    return render_template("home.html", example=EXAMPLE_PROBLEM, powiaty=POWIATY)


@bp.post("/szukaj")
def search():
    text = request.form.get("opis", "").strip()
    powiat = request.form.get("powiat", "")
    topic = MY_TOPIC_LABELS.get(request.form.get("temat", ""))  # „Moje sprawy” – temat wybrany obrazkiem
    if topic and text:
        text = f"{topic}: {text}"
    error = validate_problem(text)
    if error:
        return render_template("home.html", example=text, error=error, powiaty=POWIATY), 422
    masked, found = mask(text)
    session["draft"] = {"opis": masked, "found": found, "powiat": powiat if powiat in POWIATY else ""}
    return redirect(url_for("public.results"))


@bp.route("/wyniki")
def results():
    draft = session.get("draft")
    if not draft:
        return redirect(url_for("public.home"))
    text = draft["opis"]
    analysis = catalog.analyze(text)
    query = catalog.expanded_query(text, analysis)
    return render_template(
        "wyniki.html", draft=draft, analysis=analysis, masked_info=describe(draft["found"]),
        innovations=catalog.match_innovations(query),
        reports=catalog.similar_reports(query),
        materials=catalog.match_materials(query),
        experts=catalog.match_experts(query),
        powiaty=POWIATY,
    )


@bp.post("/zgloszenie")
def create_report():
    if g.user is None:
        flash("Wybierz konto, a potem kliknij „Zapisz zgłoszenie” jeszcze raz. Twój opis czeka.", "info")
        return redirect(url_for("auth.demo", next=url_for("public.results")))
    text = request.form.get("opis", "").strip()
    error = validate_problem(text)
    if error:
        flash(error, "error")
        return redirect(url_for("public.results"))
    body, _ = mask(text)  # zawsze maskujemy po stronie serwera, niezależnie od tego, co przyszło
    area = request.form.get("area") if request.form.get("area") in AREAS else None
    powiat = request.form.get("powiat") if request.form.get("powiat") in POWIATY else None
    rid = db.execute(
        "INSERT INTO reports (user_id, body, area, powiat, is_example, created_at) VALUES (?,?,?,?,0,?)",
        (g.user["id"], body, area, powiat, db.now()))
    matches = catalog.match_innovations(body)
    con = db.get_db()
    for inn, res in matches:
        con.execute("INSERT INTO matches (report_id, innovation_id, score) VALUES (?,?,?)", (rid, inn["id"], res.score))
    con.execute("UPDATE reports SET best_score = ? WHERE id = ?", (matches[0][1].score if matches else 0, rid))
    con.commit()
    ensure_thread("zgloszenie", rid, "Zgłoszenie: " + body[:70] + ("…" if len(body) > 70 else ""),
                  first_message=(g.user["id"], body))
    where = f" ({powiat})" if powiat else ""
    notify.notify_admins(f"Nowe zgłoszenie{where} czeka na odpowiedź.", url_for("public.report", rid=rid))
    session.pop("draft", None)
    flash("Zgłoszenie zapisane. Hub zwykle odpowiada w ciągu 3 dni roboczych – dostaniesz powiadomienie.", "success")
    return redirect(url_for("public.report", rid=rid))


def can_see_report(r):
    if g.user and (g.user["id"] == r["user_id"] or g.user["role"] in ("admin", "ekspert")):
        return True
    return bool(r["approved"])


@bp.route("/zgloszenie/<int:rid>")
def report(rid):
    r = db.one("SELECT * FROM reports WHERE id = ?", (rid,))
    if r is None:
        abort(404)
    if not can_see_report(r):
        abort(403)
    rows = db.query(
        "SELECT i.*, m.score, m.feedback FROM matches m JOIN innovations i ON i.id = m.innovation_id "
        "WHERE m.report_id = ? ORDER BY m.score DESC", (rid,))
    is_author = g.user is not None and g.user["id"] == r["user_id"]
    thread = None
    if g.user and (is_author or g.user["role"] in ("admin", "ekspert")):
        thread = thread_view("zgloszenie", rid)
    return render_template("zgloszenie.html", r=r, matches=rows, is_author=is_author, thread=thread)


@bp.post("/zgloszenie/<int:rid>/ocena")
@login_required
def rate_match(rid):
    r = db.one("SELECT user_id FROM reports WHERE id = ?", (rid,))
    if r is None:
        abort(404)
    if r["user_id"] != g.user["id"]:
        abort(403)
    value = {"pomocne": 1, "niepomocne": -1}.get(request.form.get("ocena"))
    iid = request.form.get("innovation_id", type=int)
    if value is None or iid is None:
        abort(400)
    db.execute("UPDATE matches SET feedback = ? WHERE report_id = ? AND innovation_id = ?", (value, rid, iid))
    flash("Dziękujemy! Twoja ocena pomaga nam lepiej dopasowywać rozwiązania.", "success")
    return redirect(url_for("public.report", rid=rid) + f"#dop-{iid}")


@bp.route("/moje")
@login_required
def mine():
    uid = g.user["id"]
    return render_template(
        "moje.html",
        reports=db.query("SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC", (uid,)),
        ideas=db.query("SELECT * FROM ideas WHERE user_id = ? ORDER BY created_at DESC", (uid,)),
        tests=db.query("SELECT t.*, i.title FROM tests t JOIN innovations i ON i.id = t.innovation_id "
                       "WHERE t.user_id = ? ORDER BY t.created_at DESC", (uid,)),
        follows=[r["area"] for r in db.query("SELECT area FROM follows WHERE user_id = ?", (uid,))],
    )


@bp.route("/obszary.css")
def area_css():
    """Kolory „nici” obszarów z jednego źródła (core.domain.AREAS); CSP nie pozwala na style inline."""
    css = "".join(
        f".thread--{slug}{{--thread:{a['color']};--thread-v:{thread_pattern(a, 'to bottom')};"
        f"--thread-h:{thread_pattern(a, 'to right')}}}" for slug, a in AREAS.items())
    return Response(css, mimetype="text/css", headers={"Cache-Control": "public, max-age=3600"})


def thread_pattern(area, direction):
    """Wzór „nici” – drugi kanał obok koloru (daltonizm): ciągła, kreski, kropki, paski."""
    c = area["color"]
    return {
        "ciagla": c,
        "kreski": f"repeating-linear-gradient({direction},{c} 0 12px,transparent 12px 18px)",
        "kropki": f"repeating-linear-gradient({direction},{c} 0 5px,transparent 5px 10px)",
        "paski": f"repeating-linear-gradient(45deg,{c} 0 4px,transparent 4px 7px)",
    }[area["pattern"]]


@bp.route("/dostepnosc")
def accessibility():
    return render_template("dostepnosc.html")


@bp.route("/prywatnosc")
def privacy():
    return render_template("prywatnosc.html")


@bp.route("/zdrowie")
def health():
    """Sprawdzenie dla Coolify/Dockera: aplikacja odpowiada i baza działa."""
    db.one("SELECT 1")
    return {"status": "ok"}
