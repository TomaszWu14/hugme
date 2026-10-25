"""Bramka odwiedzających wersji demonstracyjnej: uprzejme, obowiązkowe przedstawienie się (imię, nazwisko, firma)
przed pierwszą stroną HTML. Rejestr (demo_visitors) przeżywa reset demo i jest czyszczony po 90 dniach.
Nie zapisujemy IP ani user-agenta. Włącza ją DEMO_MODE; DEMO_VISITOR_GATE=0 wyłącza."""
import unicodedata
from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from itsdangerous import BadSignature, URLSafeTimedSerializer

from app import portfolio_pass, visitor_activity
from app.auth import role_required, safe_next
from app.visitor_notify import notify_visitor
from core import db
from core.privacy import mask

bp = Blueprint("gate", __name__)

COOKIE = "visitor_ok"
VALID_DAYS = 30
RETENTION_DAYS = 90
EXEMPT = ("/zdrowie", "/static/", "/api/", "/wejscie")
PASS_NAME = "Gość z portfolio"
FIELDS = (("first_name", "Imię"), ("last_name", "Nazwisko"), ("company", "Firma"))


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="demo-visitor")


def _flag():
    """Zawartość ważnego, podpisanego ciasteczka gościa albo None (brak, podrobione, wygasłe)."""
    try:
        return _serializer().loads(request.cookies.get(COOKIE, ""), max_age=VALID_DAYS * 24 * 3600)
    except BadSignature:
        return None


def _admitted():
    return _flag() is not None


def visitor_id():
    """Id wpisu gościa z podpisanego ciasteczka; None dla flag sprzed zapisu aktywności (bez id) i bez flagi."""
    flag = _flag() if request.cookies.get(COOKIE) else None
    value = flag.get("v") if isinstance(flag, dict) else None
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _admit_by_pass():
    """Przepustka z portfolio (ciasteczko gosc): wpis „z portfolio” bez danych osobowych i bez pusha ntfy.
    Ciasteczko demo ustawia after_request; True = gość wpuszczony."""
    if not portfolio_pass.valid(request.cookies.get(portfolio_pass.COOKIE, "")):
        return False
    g.portfolio_visitor = record(PASS_NAME, "", "")
    return True


def init(app):
    @app.before_request
    def visitor_gate():
        if not current_app.config["DEMO_VISITOR_GATE"] or request.path.startswith(EXEMPT) or _admitted():
            return None
        if _admit_by_pass():
            return None
        target = request.full_path.rstrip("?") if request.method == "GET" else "/"
        return redirect(url_for("gate.enter", next=target))

    @app.after_request
    def visitor_activity_count(resp):
        vid = g.get("portfolio_visitor")
        if vid is not None:
            set_flag(resp, vid)
        try:
            if request.cookies.get(COOKIE) and visitor_activity.countable(request, resp, EXEMPT):
                vid = visitor_id()
                if vid is not None:
                    visitor_activity.track(vid, request.path)
        except Exception as exc:  # noqa: BLE001 – statystyka nigdy nie psuje odpowiedzi
            current_app.logger.warning("Aktywność gościa pominięta: %s", exc)
        return resp


def clean(value):
    """Przycięty tekst 2–100 znaków bez znaków sterujących albo None."""
    value = (value or "").strip()
    if not 2 <= len(value) <= 100 or any(unicodedata.category(c).startswith("C") for c in value):
        return None
    return value


def record(first_name, last_name, company):
    """Zapisuje odwiedzającego, usuwa wpisy starsze niż 90 dni i zwraca id nowego wpisu."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    con = db.get_db()
    con.execute("DELETE FROM demo_visitors WHERE created_at < ?", (cutoff,))
    cur = con.execute("INSERT INTO demo_visitors (created_at, first_name, last_name, company) VALUES (?, ?, ?, ?)",
                      (db.now(), first_name, last_name, company))
    con.commit()
    return cur.lastrowid


def set_flag(resp, vid):
    resp.set_cookie(COOKIE, _serializer().dumps({"v": vid}), max_age=VALID_DAYS * 24 * 3600, httponly=True, samesite="Lax",
                    secure=current_app.config["SESSION_COOKIE_SECURE"] or request.is_secure)


@bp.route("/wejscie", methods=["GET", "POST"])
def enter():
    if not current_app.config["DEMO_VISITOR_GATE"]:
        abort(404)
    nxt = safe_next(request.values.get("next"), "/")
    if request.method == "GET":
        if not _admitted() and _admit_by_pass():  # ważna przepustka: bez formularza
            return redirect(nxt)
        return render_template("gate.html", next=nxt, values={}, errors={})
    if request.form.get("website"):  # pułapka na boty (pole ukryte)
        abort(400)
    values = {key: clean(request.form.get(key)) for key, _ in FIELDS}
    errors = {key: f"{label}: wpisz od 2 do 100 znaków, bez znaków sterujących." for key, label in FIELDS if values[key] is None}
    for key, label in FIELDS:  # dane kontaktowe i identyfikatory w tych polach to pomyłka – nie przechowujemy ich
        if values[key] and mask(values[key])[1]:
            errors[key] = f"{label}: wpisz samą nazwę, bez numerów, adresów i e-maili."
    if not request.form.get("consent"):
        errors["consent"] = "Potwierdź, że przeczytano informację o przetwarzaniu danych."
    if errors:
        shown = {key: request.form.get(key, "").strip() for key, _ in FIELDS}
        return render_template("gate.html", next=nxt, values=shown, errors=errors), 422
    vid = record(values["first_name"], values["last_name"], values["company"])
    notify_visitor(values["first_name"], values["last_name"], values["company"])
    resp = redirect(nxt)
    set_flag(resp, vid)
    return resp


@bp.route("/admin/odwiedzajacy")
@role_required("admin")
def visitors():
    rows = db.query("SELECT * FROM demo_visitors ORDER BY created_at DESC, id DESC")
    rows = [{**dict(r), **visitor_activity.summary(r)} for r in rows]
    return render_template("admin/odwiedzajacy.html", rows=rows, days=RETENTION_DAYS)
