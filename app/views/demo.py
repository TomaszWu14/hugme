"""Demo prowadzące jury: wybór scenariusza i przejście do kroku (logowanie na rolę kroku + przekierowanie).
Dane scenariuszy: app/scenariusze.py; pasek kroku: templates/_scenariusz.html (w base.html)."""
from flask import Blueprint, abort, flash, g, redirect, render_template, session, url_for
from werkzeug.datastructures import MultiDict

from app.auth import switch_account
from app.scenariusze import BARTEK, SCENARIUSZE, step
from app.views.potrzebny import save_volunteer
from core import db
from core.domain import ROLES
from core.privacy import mask

bp = Blueprint("demo", __name__, url_prefix="/demo")


@bp.route("")
def index():
    roles = {u["id"]: ROLES[u["role"]] for u in db.query("SELECT id, role FROM users")}
    return render_template("demo.html", scenariusze=SCENARIUSZE, roles=roles)


@bp.post("/<sid>/<int:n>")
def go(sid, n):
    st = step(sid, n)
    if st is None:
        abort(404)
    if (g.user["id"] if g.user else None) != st["uid"]:
        user = db.one("SELECT is_active FROM users WHERE id = ?", (st["uid"],)) if st["uid"] else None
        if st["uid"] and not (user and user["is_active"]):
            flash("Konto z tego kroku jest zablokowane przez Hub – odblokuj je w panelu albo wybierz inny scenariusz.", "error")
            return redirect(url_for("demo.index"))
        switch_account(st["uid"])
    session["scen"] = [sid, n]
    mama = step("rodzic", 2)["uid"]  # konto z formularza kroku 2 (krok 4 jest na koncie Hubu)
    if sid == "rodzic" and n >= 3 and not db.one("SELECT 1 FROM volunteers WHERE user_id = ? AND alias = ?",
                                                  (mama, BARTEK["alias"])):
        g.user = db.one("SELECT * FROM users WHERE id = ?", (mama,))  # jury pominęło formularz z kroku 2
        save_volunteer(MultiDict(BARTEK), "uczestnik", "rodzic")
    opis = SCENARIUSZE[sid].get("opis_problemu")
    # Kroki 1–2 zawsze z opisem gminy (stary szkic z wcześniejszego szukania dałby inne wyniki);
    # dalej szkic zostaje – to już wyniki szukania z kroku 1.
    if opis and (n <= 2 or "draft" not in session):
        masked, found = mask(opis)
        session["draft"] = {"opis": masked, "found": found, "powiat": ""}
    return redirect(st["path"])


@bp.post("/koniec")
def end():
    session.pop("scen", None)
    return redirect(url_for("demo.index"))
