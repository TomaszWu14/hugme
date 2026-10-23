"""Bramka odwiedzających wersji demonstracyjnej: uprzejme, obowiązkowe przedstawienie się (imię, nazwisko, firma)
przed pierwszą stroną HTML. Rejestr (demo_visitors) przeżywa reset demo i jest czyszczony po 90 dniach.
Nie zapisujemy IP ani user-agenta. Włącza ją DEMO_MODE; DEMO_VISITOR_GATE=0 wyłącza."""
import unicodedata
from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from itsdangerous import BadSignature, URLSafeTimedSerializer

from app.auth import role_required, safe_next
from core import db
from core.privacy import mask

bp = Blueprint("gate", __name__)

COOKIE = "visitor_ok"
VALID_DAYS = 30
RETENTION_DAYS = 90
EXEMPT = ("/zdrowie", "/static/", "/api/", "/wejscie")
FIELDS = (("first_name", "Imię"), ("last_name", "Nazwisko"), ("company", "Firma"))


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="demo-visitor")


def _admitted():
    try:
        _serializer().loads(request.cookies.get(COOKIE, ""), max_age=VALID_DAYS * 24 * 3600)
        return True
    except BadSignature:
        return False


def init(app):
    @app.before_request
    def visitor_gate():
        if not current_app.config["DEMO_VISITOR_GATE"] or request.path.startswith(EXEMPT) or _admitted():
            return None
        target = request.full_path.rstrip("?") if request.method == "GET" else "/"
        return redirect(url_for("gate.enter", next=target))


def clean(value):
    """Przycięty tekst 2–100 znaków bez znaków sterujących albo None."""
    value = (value or "").strip()
    if not 2 <= len(value) <= 100 or any(unicodedata.category(c).startswith("C") for c in value):
        return None
    return value


def record(first_name, last_name, company):
    """Zapisuje odwiedzającego i usuwa wpisy starsze niż 90 dni."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    con = db.get_db()
    con.execute("DELETE FROM demo_visitors WHERE created_at < ?", (cutoff,))
    con.execute("INSERT INTO demo_visitors (created_at, first_name, last_name, company) VALUES (?, ?, ?, ?)",
                (db.now(), first_name, last_name, company))
    con.commit()


@bp.route("/wejscie", methods=["GET", "POST"])
def enter():
    if not current_app.config["DEMO_VISITOR_GATE"]:
        abort(404)
    nxt = safe_next(request.values.get("next"), "/")
    if request.method == "GET":
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
    record(values["first_name"], values["last_name"], values["company"])
    resp = redirect(nxt)
    resp.set_cookie(COOKIE, _serializer().dumps(1), max_age=VALID_DAYS * 24 * 3600, httponly=True, samesite="Lax",
                    secure=current_app.config["SESSION_COOKIE_SECURE"] or request.is_secure)
    return resp


@bp.route("/admin/odwiedzajacy")
@role_required("admin")
def visitors():
    rows = db.query("SELECT * FROM demo_visitors ORDER BY created_at DESC, id DESC")
    return render_template("admin/odwiedzajacy.html", rows=rows, days=RETENTION_DAYS)
