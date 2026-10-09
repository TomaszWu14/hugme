"""Fabryka aplikacji HugMe: konfiguracja, bezpieczeństwo (CSRF, CSP, ciasteczka), blueprinty."""
import hmac
import os
import secrets
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, session

from core import db
from core.domain import AREAS, REPORT_STATUSES, ROLES, heat_level
from core.match import label as score_label

ROOT = Path(__file__).resolve().parent.parent

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "font-src 'self'; frame-src https://www.youtube-nocookie.com; connect-src 'self'; "
    "form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"
)


def create_app(test_config=None):
    app = Flask(__name__, instance_path=str(ROOT / "instance"))
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("DATABASE", str(ROOT / "instance" / "hugme.db")),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        DEMO_MODE=os.environ.get("DEMO_MODE") == "1",  # publiczne demo: ochrona kont demo, ramka dla jury, reset
    )
    if test_config:
        app.config.update(test_config)

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    _ensure_db(app)
    app.teardown_appcontext(db.close_db)

    _security(app)
    _template_globals(app)

    from app import auth, podpowiedzi, scenariusze
    from app.views import admin, admin_potrzebny, admin_users, api, demo, komunikacja, kreator, posrednik, potrzebny, praca, public, razem, wiedza
    app.register_blueprint(auth.bp)
    app.register_blueprint(public.bp)
    app.register_blueprint(komunikacja.bp)
    app.register_blueprint(wiedza.bp)
    app.register_blueprint(kreator.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(posrednik.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(razem.bp)
    app.register_blueprint(potrzebny.bp)
    app.register_blueprint(praca.bp)
    app.register_blueprint(admin_potrzebny.bp)
    app.register_blueprint(admin_users.bp)
    app.register_blueprint(demo.bp)
    auth.init(app)
    podpowiedzi.init(app)
    scenariusze.init(app)

    for code in ERRORS:
        app.register_error_handler(code, _error_page)
    return app


ERRORS = {
    400: ("Coś poszło nie tak z formularzem", "Odśwież stronę i spróbuj jeszcze raz."),
    403: ("Ta strona jest dla innej roli", "Zmień konto w pasku „Tryb demo” na górze strony."),
    404: ("Nie ma takiej strony", "Może adres się zmienił. Wróć na stronę startową."),
    405: ("Tak się nie da", "Wróć na stronę startową."),
    413: ("Za dużo danych", "Spróbuj z mniejszym plikiem (do 2 MB)."),
}


def _error_page(e):
    if e.code == 403 and g.get("just_switched"):  # nowe konto nie ma dostępu do strony, z której przełączano (#20)
        from app.auth import ROLE_HOME
        return redirect(ROLE_HOME.get(g.user["role"] if g.user else None, "/"))
    title, text = ERRORS[e.code]
    if e.code == 400 and e.description and e.description.startswith("Formularz"):
        text = e.description
    if request.path.startswith("/api/"):
        return {"error": title}, e.code
    return render_template("error.html", title=title, text=text), e.code


def _ensure_db(app):
    """Tworzy schemat i ładuje dane przykładowe przy pierwszym starcie (pusta baza)."""
    from data import seed
    con = db.connect(app.config["DATABASE"])
    try:
        db.init_schema(con)
        if con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            seed.run(con)
    finally:
        con.close()


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def _security(app):
    @app.before_request
    def csrf_protect():
        # API JSON jest bezstanowe (bez ciasteczek sesji) – nie podlega CSRF.
        if request.method == "POST" and not request.path.startswith("/api/"):
            sent = request.form.get("_csrf", "")
            if not sent or not hmac.compare_digest(sent, session.get("_csrf", "")):
                abort(400, description="Formularz wygasł. Odśwież stronę i spróbuj ponownie.")

    @app.after_request
    def headers(resp):
        resp.headers["Content-Security-Policy"] = CSP
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "same-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return resp


def plural(n, one, few, many):
    """Polska odmiana po liczbie: 1 wątek, 2–4 wątki (ale 12–14 wątków), 0 i 5+ wątków."""
    if n == 1:
        return one
    return few if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else many


def _template_globals(app):
    app.jinja_env.filters["plural"] = plural
    app.jinja_env.filters["pairs"] = lambda xs: [(x, x) for x in xs]
    app.jinja_env.filters["date"] = lambda s: f"{s[8:10]}.{s[5:7]}.{s[:4]}" if s else ""
    app.jinja_env.globals.update(
        csrf_token=csrf_token, score_label=score_label, heat_level=heat_level, AREAS=AREAS, ROLES=ROLES, REPORT_STATUSES=REPORT_STATUSES,
    )
