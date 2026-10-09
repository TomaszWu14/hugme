"""Moduł „Razem z ZD” – dla osób z zespołem Downa i ich rodzin.

Plan według etapu życia, wizyty (tylko w przeglądarce), prawa, pisma, rodzic-przewodnik, wytchnienie,
Dzień Specjalistów, przyjazne miejsca, sprzęt, wydarzenia i „Moje sprawy” w tekście łatwym do czytania.
Na serwer nie trafiają dane o zdrowiu ani dane dziecka."""
from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

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
    area = R.GROUPS[R.DEFAULT_GROUP]["area"]
    experts = db.query("SELECT * FROM users WHERE role = 'ekspert' AND areas LIKE ?", (f"%{area}%",))
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
    spec = R.KINDS[kind]
    if spec["title"] and len(data["title"]) < 3:
        errors["title"] = "Wpisz nazwę (co najmniej 3 znaki)."
    if spec["body"] and not 10 <= len(data["body"]) <= 1000:
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


@bp.post("/prosba/<kind>")
def create_request(kind):
    if kind not in R.KINDS:
        abort(404)
    page = R.KINDS[kind]["page"]
    if g.user is None:
        # Szkic formularza czeka na zalogowanie (bez zapisu w bazie, tylko w podpisanej sesji).
        session["razem_draft"] = {"kind": kind, **{k: request.form.get(k, "")[:1000] for k in
                                  ("powiat", "stage", "alias", "title", "body", "category")}}
        flash("Wybierz konto – Twój formularz poczeka.", "info")
        return redirect(url_for("auth.demo", next=url_for(f"razem.{page}")))
    if g.user["role"] != "mieszkaniec":  # prośby rodzin wysyła rodzic/opiekun; instytucje mają własne formularze
        abort(403)
    back = request.form.get("wroc", "")
    back = back if back.startswith("/razem") and not back.startswith("//") else url_for(f"razem.{page}")
    rid, errors = save_request(kind, request.form)
    if errors and page == "start":  # przycisk na stronie planu – wracamy tam z komunikatem
        flash(next(iter(errors.values())), "error")
        return redirect(back)
    if errors:
        return render_page(page, errors=errors, form=request.form, kind=kind), 422
    flash(R.KINDS[kind]["thanks"], "success")
    return redirect(back)


def _public_rows(kinds):
    marks = ",".join("?" * len(kinds))
    return db.query(f"SELECT * FROM family_requests WHERE kind IN ({marks}) AND status = ? ORDER BY powiat, title",
                    (*kinds, R.Status.APPROVED))


# Strona formularza → (szablon, dodatkowy kontekst). Jedno miejsce zamiast łańcucha if.
PAGES = {
    "przewodnik": ("razem/przewodnik.html", lambda: {}),
    "wytchnienie": ("razem/wytchnienie.html", lambda: {"innovations": innovations_by_title(
        ["Godziny dla rodzica – opieka wytchnieniowa", "Krąg Opiekunów"])}),
    "miejsca": ("razem/miejsca.html", lambda: {"categories": R.PLACE_CATEGORIES, "rows": _public_rows(["miejsce"])}),
    "sprzet": ("razem/sprzet.html", lambda: {"rows": _public_rows(["sprzet-oddam", "sprzet-przyjme"])}),
}


def render_page(page, errors=None, form=None, kind=None):
    template, extra = PAGES[page]
    draft = session.get("razem_draft")
    if not errors and draft and g.user and R.KINDS[draft["kind"]]["page"] == page:
        session.pop("razem_draft")
        form, kind = draft, draft["kind"]
    return render_template(template, errors=errors or {}, form=form or {}, error_kind=kind, powiaty=POWIATY,
                           stages=R.stages(), **extra())


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
    powiat = request.args.get("powiat", "")
    powiat = powiat if powiat in POWIATY else ""
    rows = db.query("SELECT e.*, (SELECT COUNT(*) FROM event_signups s WHERE s.event_id = e.id) AS n FROM events e "
                    "WHERE date >= date('now') AND (? = '' OR powiat = ?) ORDER BY powiat, date", (powiat, powiat))
    mine = {r["event_id"] for r in db.query("SELECT event_id FROM event_signups WHERE user_id = ?", (g.user["id"],))} \
        if g.user else set()
    powiaty = [r["powiat"] for r in db.query("SELECT DISTINCT powiat FROM events WHERE date >= date('now') ORDER BY powiat")]
    return render_template("razem/wydarzenia.html", rows=rows, mine=mine, powiat=powiat, powiaty=powiaty)


@bp.post("/wydarzenia/<int:eid>/zapis")
@login_required
def toggle_signup(eid):
    e = db.one("SELECT * FROM events WHERE id = ?", (eid,))
    if e is None:
        abort(404)
    if db.one("SELECT 1 FROM event_signups WHERE event_id = ? AND user_id = ?", (eid, g.user["id"])):
        db.execute("DELETE FROM event_signups WHERE event_id = ? AND user_id = ?", (eid, g.user["id"]))
        flash(f"Wypisano z wydarzenia „{e['title']}”.", "success")
    elif e["date"] < date.today().isoformat():  # lista nie ma przycisku, ale bezpośredni POST przechodził (#22)
        flash(f"Wydarzenie „{e['title']}” już się odbyło – zapisy są zamknięte.", "error")
    else:
        # ON CONFLICT: dwa równoczesne kliknięcia nie kończą się błędem (SQLite i PostgreSQL).
        db.execute("INSERT INTO event_signups (event_id, user_id, created_at) VALUES (?,?,?) "
                   "ON CONFLICT (event_id, user_id) DO NOTHING", (eid, g.user["id"], db.now()))
        notify.notify([g.user["id"]], f"Zapisano: „{e['title']}” – {e['date']}, {e['place']}", "/razem/wydarzenia")
        flash("Zapisano. Przypomnienie znajdziesz w powiadomieniach.", "success")
    powiat = request.form.get("powiat", "")
    return redirect(url_for("razem.events", powiat=powiat) if powiat in POWIATY else url_for("razem.events"))


# ── Pisma (POST → wydruk, nic nie zapisujemy) ─────────────────────────────────
@bp.route("/pisma")
def letters():
    return render_template("razem/pisma.html", letters=R.LETTERS)


def letter_justification(spec, text):
    """Uzasadnienie od AI (tylko zamaskowany tekst) albo zdanie szablonowe. Zwraca (tekst, by_ai)."""
    answer = ai.ask("Napisz 2–3 zdania rzeczowego uzasadnienia do pisma rodzica do szkoły/OPS "
                    f"(„{spec['title']}”). Punkt wyjścia rodzica jest w danych zewnętrznych. "
                    "Bez danych osobowych, bez diagnoz, uprzejmie. Odpowiedz samym tekstem uzasadnienia.",
                    data=mask(text)[0], max_tokens=300)
    if answer:
        return answer, True
    if R.LETTER_FALLBACK in text:  # ponowne kliknięcie nie dokleja zdania drugi raz
        return text, False
    return f"{text.rstrip(' .')}. {R.LETTER_FALLBACK}", False


@bp.route("/pisma/<slug>", methods=["GET", "POST"])
def letter(slug):
    spec = R.LETTERS.get(slug)
    if spec is None:
        abort(404)
    ctx = {"spec": spec, "slug": slug, "values": {}, "text": None, "helper": None, "errors": {}, "ai_enabled": ai.enabled()}
    if request.method == "GET":
        return render_template("razem/pismo.html", **ctx)
    values = {name: request.form.get(name, "").strip()[:500] for name, *_ in spec["fields"]}
    errors = {name: "To pole jest potrzebne do pisma." for name, *_ in spec["fields"] if not values[name]}
    ctx.update(values=values, errors=errors)
    if errors:
        return render_template("razem/pismo.html", **ctx), 422
    if request.form.get("akcja") == "ai":
        values["uzasadnienie"], by_ai = letter_justification(spec, values["uzasadnienie"])
        ctx["helper"] = {"by_ai": by_ai}
    ctx["text"] = spec["template"].format(data=date.today().strftime("%d.%m.%Y"), **values)
    return render_template("razem/pismo.html", **ctx)


# ── „Moje sprawy” (ETR) ───────────────────────────────────────────────────────
@bp.route("/moje-sprawy")
def my_matters():
    return render_template("razem/moje_sprawy.html", topics=R.MY_TOPICS, intro=R.MY_INTRO)
