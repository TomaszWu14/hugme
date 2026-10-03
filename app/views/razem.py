"""Moduł „Razem z ZD” – dla osób z zespołem Downa i ich rodzin.

Plan według etapu życia, wizyty (tylko w przeglądarce), prawa, pisma, rodzic-przewodnik, wytchnienie,
Dzień Specjalistów, przyjazne miejsca, sprzęt, wydarzenia i „Moje sprawy” w tekście łatwym do czytania.
Na serwer nie trafiają dane o zdrowiu ani dane dziecka."""
from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from core import ai, db, notify
from core.domain import POWIATY
from core.privacy import mask
from data import razem as R

bp = Blueprint("razem", __name__, url_prefix="/razem")
STAGE_COOKIE = "razem_etap"


def current_stage():
    return R.stage(request.cookies.get(STAGE_COOKIE, ""))


def innovations_by_title(titles):
    rows = {r["title"]: r for r in db.query("SELECT * FROM innovations")}
    return [rows[t] for t in titles if t in rows]


@bp.route("")
def start():
    events = db.query("SELECT * FROM events WHERE date >= date('now') ORDER BY date LIMIT 3")
    return render_template("razem/start.html", stages=R.stages(), chosen=current_stage(), events=events)


@bp.post("/etap")
def choose_stage():
    s = R.stage(request.form.get("etap", ""))
    if s is None:
        abort(400)
    resp = redirect(url_for("razem.stage_plan", slug=s["slug"]))
    # Etap życia (nie data urodzenia) – wystarczy do planu, nie identyfikuje dziecka.
    resp.set_cookie(STAGE_COOKIE, s["slug"], max_age=365 * 24 * 3600, httponly=True, samesite="Lax")
    return resp


@bp.route("/etap/<slug>")
def stage_plan(slug):
    s = R.stage(slug)
    if s is None:
        abort(404)
    experts = db.query("SELECT * FROM users WHERE role = 'ekspert' AND areas LIKE '%rodziny-zd%'")
    return render_template("razem/etap.html", s=s, stages=R.stages(), innovations=innovations_by_title(s["innovations"]),
                           experts=experts, disclaimer=R.DISCLAIMER, powiaty=POWIATY)


@bp.route("/wizyty")
def visits():
    return render_template("razem/wizyty.html", s=current_stage(), disclaimer=R.DISCLAIMER)


@bp.route("/prawa")
def rights():
    answers = {k: {"tak": True, "nie": False}.get(request.args.get(k)) for k, _ in R.RIGHTS_QUESTIONS}
    asked = any(v is not None for v in answers.values())
    return render_template("razem/prawa.html", questions=R.RIGHTS_QUESTIONS, answers=answers,
                           result=R.rights_result(answers) if asked else None)


@bp.route("/szkoly")
def schools():
    return render_template("razem/szkoly.html", schools=R.SCHOOLS)


@bp.route("/rodzenstwo")
def siblings():
    events = db.query("SELECT * FROM events WHERE title LIKE '%rodzeństwa%'")
    return render_template("razem/rodzenstwo.html", tips=R.SIBLINGS, events=events)


@bp.route("/co-po-nas")
def future():
    return render_template("razem/co_po_nas.html", items=R.FUTURE, innovations=innovations_by_title(
        ["Kawiarnia Treningowa „Po Szkole”", "Mapa Wsparcia Rodzin"]))


# ── Prośby (jedna tabela, rodzaj w polu kind) ─────────────────────────────────
REQUEST_PAGES = {"przewodnik-szukam": "przewodnik", "przewodnik-oferuje": "przewodnik", "wytchnienie": "wytchnienie",
                 "dzien-specjalistow": "start", "miejsce": "miejsca", "sprzet-oddam": "sprzet", "sprzet-przyjme": "sprzet"}
NEEDS_BODY = {"przewodnik-szukam", "przewodnik-oferuje", "wytchnienie", "miejsce", "sprzet-oddam", "sprzet-przyjme"}
NEEDS_TITLE = {"miejsce", "sprzet-oddam", "sprzet-przyjme"}


def save_request(kind, form):
    """Waliduje i zapisuje prośbę. Zwraca (id, {}) albo (None, błędy)."""
    data = {k: form.get(k, "").strip() for k in ("powiat", "stage", "alias", "title", "body", "category")}
    errors = {}
    if data["powiat"] not in POWIATY:
        errors["powiat"] = "Wybierz powiat."
    if data["stage"] and R.stage(data["stage"]) is None:
        errors["stage"] = "Wybierz etap z listy."
    if not 2 <= len(data["alias"]) <= 40:
        errors["alias"] = "Wpisz pseudonim (2–40 znaków) – np. „Mama Ani”. Nie musi to być prawdziwe imię."
    if kind in NEEDS_TITLE and len(data["title"]) < 3:
        errors["title"] = "Wpisz nazwę (co najmniej 3 znaki)."
    if kind in NEEDS_BODY and not 10 <= len(data["body"]) <= 1000:
        errors["body"] = "Napisz kilka słów (10–1000 znaków)."
    if errors:
        return None, errors
    body = mask(data["body"])[0]
    if kind == "miejsce" and data["category"] in R.PLACE_CATEGORIES:
        body = f"{data['category']}: {body}"
    rid = db.execute(
        "INSERT INTO family_requests (user_id, kind, powiat, stage, alias, title, body, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (g.user["id"], kind, data["powiat"], data["stage"] or None, mask(data["alias"])[0], mask(data["title"])[0][:120],
         body, db.now()))
    notify.notify_admins(f"Razem z ZD: {R.REQUEST_KINDS[kind].lower()} ({data['powiat']})", "/admin/razem",
                         exclude=g.user["id"])
    return rid, {}


THANKS = {
    "przewodnik-szukam": "Dziękujemy. Koordynatorka Hubu poszuka rodzica-przewodnika z Twojej okolicy i da znać.",
    "przewodnik-oferuje": "Dziękujemy, że chcesz pomóc! Hub odezwie się, gdy pojawi się rodzina z Twojej okolicy.",
    "wytchnienie": "Prośba wysłana. Hub przekaże ją organizacjom, które prowadzą opiekę wytchnieniową w powiecie.",
    "dzien-specjalistow": "Zapisaliśmy Twój głos. Gdy w powiecie zbierze się więcej rodzin, Hub porozmawia o Dniu Specjalistów z CUS.",
    "miejsce": "Dziękujemy za polecenie. Pojawi się na liście po sprawdzeniu przez Hub.",
    "sprzet-oddam": "Ogłoszenie pojawi się po sprawdzeniu przez Hub. Kontakt odbędzie się przez Hub.",
    "sprzet-przyjme": "Ogłoszenie pojawi się po sprawdzeniu przez Hub. Kontakt odbędzie się przez Hub.",
}


@bp.post("/prosba/<kind>")
def create_request(kind):
    if kind not in R.REQUEST_KINDS:
        abort(404)
    page = REQUEST_PAGES[kind]
    if g.user is None:
        flash("Wybierz konto, żeby wysłać prośbę.", "info")
        return redirect(url_for("auth.demo", next=url_for(f"razem.{page}")))
    back = request.form.get("wroc", "")
    back = back if back.startswith("/razem") and not back.startswith("//") else url_for(f"razem.{page}")
    rid, errors = save_request(kind, request.form)
    if errors and page == "start":  # przycisk na stronie planu – wracamy tam z komunikatem
        flash(next(iter(errors.values())), "error")
        return redirect(back)
    if errors:
        return render_page(page, errors=errors, form=request.form, kind=kind), 422
    flash(THANKS[kind], "success")
    return redirect(back)


def render_page(page, errors=None, form=None, kind=None):
    ctx = {"errors": errors or {}, "form": form or {}, "error_kind": kind, "powiaty": POWIATY, "stages": R.stages()}
    if page == "przewodnik":
        return render_template("razem/przewodnik.html", **ctx)
    if page == "wytchnienie":
        return render_template("razem/wytchnienie.html", **ctx, innovations=innovations_by_title(
            ["Godziny dla rodzica – opieka wytchnieniowa", "Krąg Opiekunów"]))
    if page == "miejsca":
        return render_template("razem/miejsca.html", **ctx, categories=R.PLACE_CATEGORIES, rows=db.query(
            "SELECT * FROM family_requests WHERE kind = 'miejsce' AND status = 'zatwierdzone' ORDER BY powiat, title"))
    if page == "sprzet":
        return render_template("razem/sprzet.html", **ctx, rows=db.query(
            "SELECT * FROM family_requests WHERE kind IN ('sprzet-oddam','sprzet-przyjme') AND status = 'zatwierdzone' "
            "ORDER BY created_at DESC"))
    return start()


@bp.route("/przewodnik")
def przewodnik():
    return render_page("przewodnik")


@bp.route("/wytchnienie")
def wytchnienie():
    return render_page("wytchnienie")


@bp.route("/miejsca")
def miejsca():
    return render_page("miejsca")


@bp.route("/sprzet")
def sprzet():
    return render_page("sprzet")


# ── Wydarzenia ────────────────────────────────────────────────────────────────
@bp.route("/wydarzenia")
def events():
    rows = db.query("SELECT e.*, (SELECT COUNT(*) FROM event_signups s WHERE s.event_id = e.id) AS n FROM events e "
                    "WHERE date >= date('now') ORDER BY date")
    mine = {r["event_id"] for r in db.query("SELECT event_id FROM event_signups WHERE user_id = ?", (g.user["id"],))} \
        if g.user else set()
    return render_template("razem/wydarzenia.html", rows=rows, mine=mine)


@bp.post("/wydarzenia/<int:eid>/zapis")
@login_required
def toggle_signup(eid):
    e = db.one("SELECT * FROM events WHERE id = ?", (eid,))
    if e is None:
        abort(404)
    if db.one("SELECT 1 FROM event_signups WHERE event_id = ? AND user_id = ?", (eid, g.user["id"])):
        db.execute("DELETE FROM event_signups WHERE event_id = ? AND user_id = ?", (eid, g.user["id"]))
        flash(f"Wypisano z wydarzenia „{e['title']}”.", "success")
    else:
        db.execute("INSERT INTO event_signups (event_id, user_id, created_at) VALUES (?,?,?)", (eid, g.user["id"], db.now()))
        notify.notify([g.user["id"]], f"Zapisano: „{e['title']}” – {e['date']}, {e['place']}", "/razem/wydarzenia")
        flash("Zapisano. Przypomnienie znajdziesz w powiadomieniach.", "success")
    return redirect(url_for("razem.events"))


# ── Pisma (POST → wydruk, nic nie zapisujemy) ─────────────────────────────────
@bp.route("/pisma")
def letters():
    return render_template("razem/pisma.html", letters=R.LETTERS)


@bp.route("/pisma/<slug>", methods=["GET", "POST"])
def letter(slug):
    spec = R.LETTERS.get(slug)
    if spec is None:
        abort(404)
    values, text, ai_text, errors = {}, None, None, {}
    if request.method == "POST":
        values = {name: request.form.get(name, "").strip()[:500] for name, *_ in spec["fields"]}
        errors = {name: "To pole jest potrzebne do pisma." for name, *_ in spec["fields"] if not values[name]}
        if not errors:
            if request.form.get("akcja") == "ai":
                # Do AI trafia tylko zamaskowane uzasadnienie – bez imion, nazwisk i nazwy szkoły.
                ai_text = ai.ask("Napisz 2–3 zdania rzeczowego uzasadnienia do pisma rodzica do szkoły/OPS "
                                 f"(„{spec['title']}”). Punkt wyjścia: {mask(values['uzasadnienie'])[0]}. "
                                 "Bez danych osobowych, bez diagnoz, uprzejmie.", max_tokens=300)
                if ai_text:
                    values["uzasadnienie"] = ai_text
            text = spec["template"].format(data=date.today().strftime("%d.%m.%Y"), **values)
    return render_template("razem/pismo.html", spec=spec, slug=slug, values=values, text=text, ai_text=ai_text,
                           errors=errors, ai_enabled=ai.enabled()), (422 if errors else 200)


# ── „Moje sprawy” (ETR) ───────────────────────────────────────────────────────
@bp.route("/moje-sprawy")
def my_matters():
    return render_template("razem/moje_sprawy.html", topics=R.MY_TOPICS, intro=R.MY_INTRO)
