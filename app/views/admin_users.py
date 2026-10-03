"""Panel Hubu – użytkownicy i role: lista kont z aktywnością, karta konta (edycja, zmiana roli, blokada),
nowe konto, macierz uprawnień i dziennik działań na kontach."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from core import db
from core.domain import AREAS, ROLES
from core.privacy import mask

bp = Blueprint("admin_users", __name__, url_prefix="/admin")

# Macierz uprawnień – opis tego, co egzekwują dekoratory i warunki w widokach (zmiana tu = zmiana w kodzie).
# (funkcja, {rola: True/False/'opis'}) – 'gosc' to niezalogowany.
ROLE_KEYS = ["gosc", "mieszkaniec", "ngo", "gmina", "ekspert", "admin"]
ROLE_NAMES = {"gosc": "Gość", **ROLES}
PERMISSIONS = [
    ("Szukanie pomocy, wyniki dopasowań, Wiedza, Biblioteka, Pośrednik, API", dict.fromkeys(ROLE_KEYS, True)),
    ("Zapis zgłoszenia, ocena dopasowań, wątki i powiadomienia", {**dict.fromkeys(ROLE_KEYS, True), "gosc": False}),
    ("Kreator pomysłów: fiszka, kanwa, asystent, wniosek w naborze", {**dict.fromkeys(ROLE_KEYS, True), "gosc": False}),
    ("Tester innowacji: zgłoszenie do testu, ocena, usprawnienie", {**dict.fromkeys(ROLE_KEYS, True), "gosc": False}),
    ("Pytania do eksperta – skrzynka „Pytania do mnie”", {**dict.fromkeys(ROLE_KEYS, False), "ekspert": True}),
    ("Razem z ZD: plan, prawa, pisma, wydarzenia (przeglądanie)", dict.fromkeys(ROLE_KEYS, True)),
    ("Razem z ZD: prośby rodzin (przewodnik, wytchnienie, miejsca, sprzęt, Dzień Specjalistów)",
     {**dict.fromkeys(ROLE_KEYS, False), "mieszkaniec": True}),
    ("Jestem potrzebny: zgłoszenie uczestnika (rodzic albo osoba z ZD)", {**dict.fromkeys(ROLE_KEYS, False), "mieszkaniec": True}),
    ("Jestem potrzebny: oferta miejsca (schronisko, hospicjum, świetlica)", {**dict.fromkeys(ROLE_KEYS, False), "ngo": True, "gmina": True}),
    ("Jestem potrzebny: propozycja miejsca od rodzica", {**dict.fromkeys(ROLE_KEYS, False), "mieszkaniec": True}),
    ("Jestem potrzebny: zgłoszenie buddy", {**dict.fromkeys(ROLE_KEYS, True), "gosc": False, "admin": False}),
    ("Praca: zgłoszenie miejsca pracy na mapę", {**dict.fromkeys(ROLE_KEYS, True), "gosc": False}),
    ("Panel Hubu: skrzynka, statusy, Biblioteka, nabory, trendy, luki, pary, użytkownicy", {**dict.fromkeys(ROLE_KEYS, False), "admin": True}),
]
ACTIVITY = {
    "zgloszenia": "SELECT COUNT(*) FROM reports WHERE user_id = ?",
    "pomysly": "SELECT COUNT(*) FROM ideas WHERE user_id = ?",
    "prosby": "SELECT COUNT(*) FROM family_requests WHERE user_id = ?",
    "uczestnicy": "SELECT COUNT(*) FROM volunteers WHERE user_id = ?",
    "oferty": "SELECT COUNT(*) FROM offers WHERE user_id = ?",
    "wiadomosci": "SELECT COUNT(*) FROM messages WHERE user_id = ?",
}


@bp.before_request
def only_admin():
    if g.user is None:
        return redirect(url_for("auth.demo", next=request.full_path))
    if g.user["role"] != "admin":
        abort(403)


def log(user_id, action):
    db.execute("INSERT INTO admin_log (admin_id, user_id, action, created_at) VALUES (?,?,?,?)",
               (g.user["id"], user_id, action, db.now()))


def activity(uid):
    return {k: db.one(sql, (uid,))[0] for k, sql in ACTIVITY.items()}


def _user_or_404(uid):
    u = db.one("SELECT * FROM users WHERE id = ?", (uid,))
    if u is None:
        abort(404)
    return u


def _validate(form):
    data = {k: form.get(k, "").strip() for k in ("name", "role", "org", "bio")}
    data["areas"] = ",".join(a for a in form.getlist("areas") if a in AREAS)
    errors = {}
    if not 3 <= len(data["name"]) <= 80:
        errors["name"] = "Wpisz nazwę konta (3–80 znaków), np. „Anna – mama, powiat wadowicki”."
    if data["role"] not in ROLES:
        errors["role"] = "Wybierz rolę."
    data["bio"] = mask(data["bio"])[0][:600]
    data["org"] = data["org"][:120] or None
    return data, errors


@bp.route("/uzytkownicy")
def users():
    role = request.args.get("rola", "")
    q = request.args.get("q", "").strip()
    sql, args = "SELECT * FROM users WHERE 1 = 1", []
    if role in ROLES:
        sql, args = sql + " AND role = ?", args + [role]
    if q:
        sql, args = sql + " AND (name LIKE ? OR org LIKE ?)", args + [f"%{q}%", f"%{q}%"]
    rows = [dict(u, act=activity(u["id"])) for u in db.query(sql + " ORDER BY role, id", args)]
    by_role = {r["role"]: r["n"] for r in db.query("SELECT role, COUNT(*) AS n FROM users GROUP BY role")}
    blocked = db.one("SELECT COUNT(*) FROM users WHERE is_active = 0")[0]
    return render_template("admin/uzytkownicy.html", rows=rows, role=role, q=q, by_role=by_role, blocked=blocked, ROLES=ROLES)


@bp.route("/uzytkownicy/nowy", methods=["GET", "POST"])
def new_user():
    errors, form = {}, {"role": "mieszkaniec"}
    if request.method == "POST":
        data, errors = _validate(request.form)
        if not errors:
            n = db.one("SELECT COUNT(*) FROM users")[0] + 1
            uid = db.execute("INSERT INTO users (name, role, org, areas, email, bio, is_demo) VALUES (?,?,?,?,?,?,1)",
                             (data["name"], data["role"], data["org"], data["areas"], f"user{n}@przyklad.invalid", data["bio"]))
            log(uid, f"utworzono konto ({ROLES[data['role']]})")
            flash("Konto dodane – pojawi się w pasku „Tryb demo”.", "success")
            return redirect(url_for("admin_users.user", uid=uid))
        form = request.form
    return render_template("admin/uzytkownik.html", u=None, form=form, errors=errors, AREAS=AREAS, ROLES=ROLES, logs=[], act={}), \
        (422 if errors else 200)


@bp.route("/uzytkownicy/<int:uid>", methods=["GET", "POST"])
def user(uid):
    u = _user_or_404(uid)
    errors, form = {}, dict(u)
    if request.method == "POST":
        data, errors = _validate(request.form)
        if not errors and data["role"] != "admin" and u["role"] == "admin" and \
                db.one("SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1")[0] <= 1:
            errors["role"] = "To ostatnie aktywne konto Hubu – nie można odebrać mu roli."
        if not errors:
            db.execute("UPDATE users SET name = ?, role = ?, org = ?, areas = ?, bio = ? WHERE id = ?",
                       (data["name"], data["role"], data["org"], data["areas"], data["bio"], uid))
            changes = [f"rola {ROLES[u['role']]} → {ROLES[data['role']]}"] if data["role"] != u["role"] else []
            changes += ["dane konta"] if (data["name"], data["org"], data["areas"], data["bio"]) != (u["name"], u["org"], u["areas"], u["bio"]) else []
            if changes:
                log(uid, "zmieniono: " + ", ".join(changes))
            flash("Zapisane.", "success")
            return redirect(url_for("admin_users.user", uid=uid))
        form = request.form
    logs = db.query("SELECT l.*, a.name AS admin_name FROM admin_log l JOIN users a ON a.id = l.admin_id "
                    "WHERE l.user_id = ? ORDER BY l.created_at DESC LIMIT 20", (uid,))
    return render_template("admin/uzytkownik.html", u=u, form=form, errors=errors, AREAS=AREAS, ROLES=ROLES, logs=logs,
                           act=activity(uid)), (422 if errors else 200)


@bp.post("/uzytkownicy/<int:uid>/blokada")
def toggle_block(uid):
    u = _user_or_404(uid)
    if uid == g.user["id"]:
        flash("Nie możesz zablokować własnego konta.", "error")
        return redirect(url_for("admin_users.user", uid=uid))
    new = 0 if u["is_active"] else 1
    db.execute("UPDATE users SET is_active = ? WHERE id = ?", (new, uid))
    log(uid, "odblokowano konto" if new else "zablokowano konto")
    flash("Konto odblokowane." if new else "Konto zablokowane – nie można się na nie przełączyć.", "success")
    return redirect(url_for("admin_users.user", uid=uid))


@bp.route("/role")
def roles():
    counts = {r["role"]: r["n"] for r in db.query("SELECT role, COUNT(*) AS n FROM users WHERE is_active = 1 GROUP BY role")}
    logs = db.query("SELECT l.*, a.name AS admin_name, u.name AS user_name FROM admin_log l JOIN users a ON a.id = l.admin_id "
                    "JOIN users u ON u.id = l.user_id ORDER BY l.created_at DESC LIMIT 30")
    return render_template("admin/role.html", perms=PERMISSIONS, role_keys=ROLE_KEYS, role_names=ROLE_NAMES, counts=counts, logs=logs)
