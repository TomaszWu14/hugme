"""Program „Jestem potrzebny / potrzebna” – osoby z zespołem Downa pomagają innym.

Zgłoszenia uczestników (rodzic albo sama osoba w łatwym tekście), oferty miejsc (instytucja albo propozycja
rodzica), wolontariusze-buddy, zasady i dzienniczek z odznakami. Łączy Hub (app/views/admin_potrzebny.py)."""
import re

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from core import ai, db, notify
from core.domain import POWIATY
from core.privacy import mask
from data import potrzebny as P

bp = Blueprint("potrzebny", __name__, url_prefix="/razem/jestem-potrzebny")
RE_PHONE = re.compile(r"^\+?[\d\s-]{7,16}$")


def _csv(form, name, allowed):
    return ",".join(v for v in form.getlist(name) if v in allowed)


def _common(form, errors):
    """Pola wspólne uczestnika i buddy: pseudonim, powiat, dni, telefon."""
    alias = form.get("alias", "").strip()
    if not 2 <= len(alias) <= 40:
        errors["alias"] = "Wpisz pseudonim (2–40 znaków) – nie musi to być prawdziwe imię."
    powiat = form.get("powiat", "")
    if powiat not in POWIATY:
        errors["powiat"] = "Wybierz powiat."
    days = _csv(form, "days", {**P.DAYS, **P.TIMES})
    if not days:
        errors["days"] = "Zaznacz, kiedy możesz."
    phone = form.get("phone", "").strip()
    if phone and not RE_PHONE.match(phone):
        errors["phone"] = "Wpisz numer telefonu (cyfry) albo zostaw puste."
    if not form.get("consent"):
        errors["consent"] = "Potrzebujemy zgody, żeby zapisać zgłoszenie."
    return alias, powiat, days, phone


def save_volunteer(form, role, source):
    errors = {}
    alias, powiat, days, phone = _common(form, errors)
    age, interests, companion = "", "", ""
    if role == "uczestnik":
        age = form.get("age_group", "")
        if age not in P.AGE_GROUPS:
            errors["age_group"] = "Wybierz, kim jest uczestnik."
        interests = _csv(form, "interests", P.INTERESTS)
        if not interests:
            errors["interests"] = "Wybierz, co lubisz – choć jedno."
        companion = form.get("companion", "")
        if companion not in P.COMPANIONS:
            errors["companion"] = "Wybierz, kto będzie towarzyszyć."
    if errors:
        return None, errors
    vid = db.execute(
        "INSERT INTO volunteers (user_id, role, alias, powiat, age_group, interests, days, companion, phone, consent, "
        "source, created_at) VALUES (?,?,?,?,?,?,?,?,?,1,?,?)",
        (g.user["id"], role, mask(alias)[0], powiat, age, interests, days, companion, phone, source, db.now()))
    what = "nowy buddy" if role == "buddy" else "nowy uczestnik"
    notify.notify_admins(f"Jestem potrzebny: {what} ({powiat})", "/admin/potrzebny", exclude=g.user["id"])
    return vid, {}


def _offers(powiat=""):
    sql = "SELECT * FROM offers WHERE status = 'zatwierdzone'"
    args = ()
    if powiat:
        sql, args = sql + " AND powiat = ?", (powiat,)
    rows = db.query(sql + " ORDER BY powiat, created_at DESC", args)
    taken = {r["offer_id"]: r["n"] for r in db.query(
        "SELECT offer_id, COUNT(*) AS n FROM missions WHERE status = 'polaczone' GROUP BY offer_id")}
    return [dict(r, free=max(0, r["slots"] - taken.get(r["id"], 0))) for r in rows]


def _ctx(**extra):
    return dict(P=P, powiaty=POWIATY, **extra)


@bp.route("")
def start():
    powiat = request.args.get("powiat", "")
    powiat = powiat if powiat in POWIATY else ""
    mine = db.one("SELECT id FROM volunteers WHERE user_id = ? AND role = 'uczestnik'", (g.user["id"],)) if g.user else None
    stats = db.one("SELECT (SELECT COUNT(*) FROM volunteers WHERE role = 'uczestnik') AS vols, "
                   "(SELECT COUNT(*) FROM offers WHERE status = 'zatwierdzone') AS offers, "
                   "(SELECT COALESCE(SUM(done), 0) FROM missions) AS done")
    return render_template("potrzebny/start.html", **_ctx(offers=_offers(powiat), powiat=powiat, mine=mine, stats=stats))


@bp.route("/zasady")
def rules():
    return render_template("potrzebny/zasady.html", **_ctx())


@bp.route("/zglos", methods=["GET", "POST"])
def signup():
    errors, form = {}, {}
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.demo", next=request.path))
        vid, errors = save_volunteer(request.form, "uczestnik", "rodzic")
        if not errors:
            flash(P.THANKS["uczestnik"], "success")
            return redirect(url_for("potrzebny.diary"))
        form = request.form
    return render_template("potrzebny/zglos.html", **_ctx(errors=errors, form=form)), (422 if errors else 200)


@bp.route("/latwy", methods=["GET", "POST"])
def easy_signup():
    """Zgłoszenie w tekście łatwym do czytania – dorosła osoba z ZD zgłasza się sama."""
    errors, form = {}, {}
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.demo", next=request.path))
        data = request.form.copy()
        data["age_group"] = "dorosly"
        vid, errors = save_volunteer(data, "uczestnik", "latwy-tekst")
        if not errors:
            flash(P.THANKS["latwy"], "success")
            return redirect(url_for("potrzebny.diary"))
        form = request.form
    return render_template("potrzebny/latwy.html", **_ctx(errors=errors, form=form)), (422 if errors else 200)


@bp.route("/buddy", methods=["GET", "POST"])
def buddy():
    errors, form = {}, {}
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.demo", next=request.path))
        vid, errors = save_volunteer(request.form, "buddy", "buddy")
        if not errors:
            flash(P.THANKS["buddy"], "success")
            return redirect(url_for("potrzebny.start"))
        form = request.form
    return render_template("potrzebny/buddy.html", **_ctx(errors=errors, form=form)), (422 if errors else 200)


def save_offer(form, source):
    data = {k: form.get(k, "").strip() for k in ("institution", "mission_kind", "title", "body", "body_easy", "powiat",
                                                 "requirements")}
    errors = {}
    if len(data["institution"]) < 3:
        errors["institution"] = "Wpisz nazwę miejsca (co najmniej 3 znaki)."
    if data["mission_kind"] not in P.MISSION_KINDS:
        errors["mission_kind"] = "Wybierz rodzaj pomocy."
    if len(data["title"]) < 5:
        errors["title"] = "Napisz krótko, na czym polega pomoc (co najmniej 5 znaków)."
    if not 10 <= len(data["body"]) <= 1500:
        errors["body"] = "Opisz misję (10–1500 znaków)."
    if data["powiat"] not in POWIATY:
        errors["powiat"] = "Wybierz powiat."
    slots = form.get("slots", type=int) or 1
    days = _csv(form, "days", {**P.DAYS, **P.TIMES})
    for_whom = _csv(form, "for_whom", P.AGE_GROUPS)
    if source == "instytucja" and not for_whom:
        errors["for_whom"] = "Zaznacz, kogo zapraszacie."
    if errors:
        return None, errors
    oid = db.execute(
        "INSERT INTO offers (user_id, source, institution, mission_kind, title, body, body_easy, easy_by_ai, powiat, days, "
        "slots, for_whom, provides, requirements, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (g.user["id"], source, mask(data["institution"])[0][:120], data["mission_kind"], mask(data["title"])[0][:160],
         mask(data["body"])[0], mask(data["body_easy"])[0], 1 if form.get("easy_by_ai") == "1" and data["body_easy"] else 0,
         data["powiat"], days, max(1, min(slots, 20)), for_whom, _csv(form, "provides", P.PROVIDES),
         mask(data["requirements"])[0][:300], db.now()))
    notify.notify_admins(f"Jestem potrzebny: {'oferta miejsca' if source == 'instytucja' else 'propozycja miejsca od rodzica'} "
                         f"({data['powiat']})", "/admin/potrzebny", exclude=g.user["id"])
    return oid, {}


@bp.route("/oferta", methods=["GET", "POST"])
def offer():
    source = "rodzic" if request.values.get("jako") == "rodzic" else "instytucja"
    errors, form, easy_info = {}, {}, ""
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("auth.demo", next=request.full_path))
        form = request.form.copy()
        if form.get("action") == "uprosc":
            # Opcjonalne AI: wersja w łatwym tekście do poprawienia przez instytucję i Hub.
            easy = ai.easy_text(form.get("body", "")) if len(form.get("body", "")) >= 10 else None
            if easy:
                form["body_easy"], form["easy_by_ai"] = easy, "1"
                easy_info = "AI zaproponowało łatwy tekst – sprawdź go i popraw, jeśli trzeba."
            else:
                easy_info = "AI jest niedostępne – napisz łatwy tekst sam/sama według wskazówek pod polem."
        else:
            oid, errors = save_offer(form, source)
            if not errors:
                flash(P.THANKS[source], "success")
                return redirect(url_for("potrzebny.start"))
    return render_template("potrzebny/oferta.html", **_ctx(errors=errors, form=form, source=source, easy_info=easy_info,
                                                          ai_on=ai.enabled())), (422 if errors else 200)


def diary_for(user_id):
    """Dane dzienniczka: uczestnicy użytkownika, ich pary i misje, odznaki, umiejętności."""
    vols = db.query("SELECT * FROM volunteers WHERE user_id = ? AND role = 'uczestnik' ORDER BY created_at", (user_id,))
    out = []
    for v in vols:
        missions = db.query("SELECT m.*, o.title, o.institution, o.mission_kind, o.body_easy, b.alias AS buddy "
                            "FROM missions m JOIN offers o ON o.id = m.offer_id LEFT JOIN volunteers b ON b.id = m.buddy_id "
                            "WHERE m.volunteer_id = ? ORDER BY m.created_at", (v["id"],))
        by_kind = {}
        for m in missions:
            by_kind[m["mission_kind"]] = by_kind.get(m["mission_kind"], 0) + m["done"]
        total = sum(by_kind.values())
        out.append({"v": v, "missions": missions, "total": total, "by_kind": by_kind,
                    "badges": P.badges_for(total, by_kind), "skills": P.skills_for(total, by_kind)})
    return out


@bp.route("/dzienniczek")
@login_required
def diary():
    return render_template("potrzebny/dzienniczek.html", **_ctx(entries=diary_for(g.user["id"])))


@bp.route("/dzienniczek/dyplom/<int:vid>")
@login_required
def diploma(vid):
    entry = next((e for e in diary_for(g.user["id"]) if e["v"]["id"] == vid), None)
    if entry is None or entry["total"] == 0:
        abort(404)
    return render_template("potrzebny/dyplom.html", **_ctx(e=entry))
