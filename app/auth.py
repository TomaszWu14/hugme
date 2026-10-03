"""Konta demo (bez haseł), przełącznik ról, ustawienia dostępności, sprawdzanie ról na serwerze.

Docelowo logowanie przez login.gov.pl albo link e-mail – patrz docs/ARCHITEKTURA.md."""
from functools import wraps

from flask import Blueprint, abort, g, redirect, render_template, request, session, url_for

from core import db

bp = Blueprint("auth", __name__)

PREF_COOKIES = {"duzy-tekst": "a11y_size", "kontrast": "a11y_contrast"}


def init(app):
    @app.before_request
    def load_user():
        uid = session.get("uid")
        g.user = db.one("SELECT * FROM users WHERE id = ?", (uid,)) if uid else None
        g.unread = db.one(
            "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (uid,)
        )[0] if g.user else 0

    @app.context_processor
    def prefs():
        return {
            "pref_size": request.cookies.get("a11y_size") == "1",
            "pref_contrast": request.cookies.get("a11y_contrast") == "1",
            "demo_users": db.query("SELECT id, name, role FROM users ORDER BY id"),
        }


def safe_next(target, default="/"):
    """Przekierowanie tylko w obrębie serwisu (chroni przed open redirect)."""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return default


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.demo", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def deco(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("auth.demo", next=request.full_path))
            if g.user["role"] not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return deco


@bp.route("/konto", methods=["GET", "POST"])
def demo():
    if request.method == "POST":
        uid = request.form.get("user_id", type=int)
        user = db.one("SELECT id FROM users WHERE id = ?", (uid,)) if uid else None
        if uid and user is None:
            abort(400)
        session.clear()  # nowa sesja przy zmianie konta (ochrona przed session fixation)
        if user:
            session["uid"] = user["id"]
        return redirect(safe_next(request.form.get("next"), url_for("public.home")))
    return render_template("konto.html", next=safe_next(request.args.get("next"), ""))


@bp.post("/konto/wyloguj")
def logout():
    session.clear()
    return redirect(url_for("public.home"))


@bp.post("/ustawienia")
def toggle_pref():
    name = PREF_COOKIES.get(request.form.get("pref"))
    if name is None:
        abort(400)
    resp = redirect(safe_next(request.form.get("next")))
    if request.cookies.get(name) == "1":
        resp.delete_cookie(name)
    else:
        resp.set_cookie(name, "1", max_age=365 * 24 * 3600, httponly=True, samesite="Lax")
    return resp
