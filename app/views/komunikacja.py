"""Komunikacja: wątki (zgłoszenie, pomysł, innowacja), powiadomienia, obserwowanie obszarów, widok eksperta."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required, role_required, safe_next
from core import db, notify
from core.domain import AREAS
from core.privacy import mask

bp = Blueprint("komunikacja", __name__)

SUBJECT_TABLE = {"zgloszenie": "reports", "pomysl": "ideas", "innowacja": "innovations"}


def short(text, n=60):
    """Skrót na granicy słowa, bez wiszącego myślnika: „…do lekarza…”, nie „…do lekarza –”."""
    return text if len(text) <= n else text[:n + 1].rsplit(" ", 1)[0].rstrip(" –-,;:") + "…"


def subject_link(stype, sid):
    return {"zgloszenie": f"/zgloszenie/{sid}", "pomysl": f"/pomysly/{sid}", "innowacja": f"/biblioteka/{sid}"}[stype]


def ensure_thread(stype, sid, title, first_message=None):
    t = db.one("SELECT id FROM threads WHERE subject_type = ? AND subject_id = ?", (stype, sid))
    if t:
        return t["id"]
    tid = db.execute("INSERT INTO threads (subject_type, subject_id, title, created_at) VALUES (?,?,?,?)",
                     (stype, sid, title, db.now()))
    if first_message:
        db.execute("INSERT INTO messages (thread_id, user_id, body, created_at) VALUES (?,?,?,?)",
                   (tid, first_message[0], first_message[1], db.now()))
    return tid


def thread_view(stype, sid):
    t = db.one("SELECT * FROM threads WHERE subject_type = ? AND subject_id = ?", (stype, sid))
    msgs = db.query("SELECT m.*, u.name, u.role FROM messages m JOIN users u ON u.id = m.user_id "
                    "WHERE m.thread_id = ? AND (m.hidden = 0 OR ?) ORDER BY m.created_at, m.id",
                    (t["id"], bool(g.user and g.user["role"] == "admin"))) if t else []
    return {"thread": t, "messages": msgs, "subject_type": stype, "subject_id": sid}


def can_post(stype, subject):
    if g.user is None:
        return False
    if stype == "zgloszenie":
        return g.user["id"] == subject["user_id"] or g.user["role"] in ("admin", "ekspert")
    return True


@bp.post("/watek/<stype>/<int:sid>")
@login_required
def post_message(stype, sid):
    table = SUBJECT_TABLE.get(stype)
    if table is None:
        abort(404)
    subject = db.one(f"SELECT * FROM {table} WHERE id = ?", (sid,))  # table z białej listy
    if subject is None:
        abort(404)
    if not can_post(stype, subject):
        abort(403)
    text = request.form.get("tresc", "").strip()
    link = subject_link(stype, sid) + "#watek"
    if not 2 <= len(text) <= 2000:
        flash("Wiadomość powinna mieć od 2 do 2000 znaków.", "error")
        return redirect(link)
    body, found = mask(text)
    title = {"zgloszenie": "Zgłoszenie", "pomysl": "Pytania do pomysłu", "innowacja": "Pytania o innowację"}[stype]
    label = subject["title"] if "title" in subject.keys() else short(subject["body"])
    tid = ensure_thread(stype, sid, f"{title}: {label}")
    db.execute("INSERT INTO messages (thread_id, user_id, body, created_at) VALUES (?,?,?,?)",
               (tid, g.user["id"], body, db.now()))

    # Kogo powiadomić: uczestników wątku i autora tematu; Hub, gdy pisze ktoś spoza Hubu;
    # ekspertów obszaru, gdy pytanie zadaje nie-ekspert w wątku pomysłu/innowacji.
    participants = {r["user_id"] for r in db.query("SELECT DISTINCT user_id FROM messages WHERE thread_id = ?", (tid,))}
    if "user_id" in subject.keys():
        participants.add(subject["user_id"])
    participants.discard(g.user["id"])
    notify.notify(participants, f"Nowa wiadomość: {short(label)}", link)
    if g.user["role"] != "admin":
        notify.notify_admins(f"Nowa wiadomość w wątku: {short(label)}", link, exclude=g.user["id"])
    if stype != "zgloszenie" and g.user["role"] != "ekspert" and subject["area"]:
        notify.notify_experts(subject["area"], f"Pytanie do ekspertów: {short(label)}", link, exclude=g.user["id"])
    nxt = ("" if g.user["role"] in ("admin", "ekspert")
           else " Odpowie Hub albo ekspert, zwykle w ciągu 3 dni roboczych – zobaczysz to w Powiadomieniach.")
    flash("Wiadomość wysłana." + nxt + (" Ukryliśmy dane osobowe, które się w niej znalazły." if found else ""), "sekcja")
    return redirect(link)


@bp.route("/powiadomienia")
@login_required
def notifications():
    rows = db.query("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 100",
                    (g.user["id"],))
    return render_template("powiadomienia.html", rows=rows)


@bp.post("/powiadomienia/przeczytane")
@login_required
def mark_read():
    db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (g.user["id"],))
    flash("Wszystkie powiadomienia oznaczone jako przeczytane.", "success")
    return redirect(url_for("komunikacja.notifications"))


@bp.post("/obserwuj/<area>")
@login_required
def toggle_follow(area):
    if area not in AREAS:
        abort(404)
    exists = db.one("SELECT 1 FROM follows WHERE user_id = ? AND area = ?", (g.user["id"], area))
    if exists:
        db.execute("DELETE FROM follows WHERE user_id = ? AND area = ?", (g.user["id"], area))
        flash(f"Nie obserwujesz już obszaru „{AREAS[area]['name']}”.", "success")
    else:
        db.execute("INSERT INTO follows (user_id, area) VALUES (?, ?)", (g.user["id"], area))
        flash(f"Obserwujesz obszar „{AREAS[area]['name']}”. Damy znać o nowych innowacjach i naborach.", "success")
    return redirect(safe_next(request.form.get("next"), f"/wiedza/obszar/{area}"))


@bp.route("/ekspert")
@role_required("ekspert")
def expert_inbox():
    areas = [a for a in g.user["areas"].split(",") if a]
    marks = ",".join("?" * len(areas)) or "''"
    # Wątki pomysłów i innowacji z moich obszarów, w których ostatnie słowo nie należy do eksperta.
    rows = db.query(f"""
        SELECT t.*, (SELECT u.role FROM messages m JOIN users u ON u.id = m.user_id
                     WHERE m.thread_id = t.id AND m.hidden = 0 ORDER BY m.created_at DESC, m.id DESC LIMIT 1) AS last_role,
               (SELECT MAX(created_at) FROM messages m WHERE m.thread_id = t.id AND m.hidden = 0) AS last_at,
               COALESCE(i.area, n.area, r.area) AS area
        FROM threads t
        LEFT JOIN ideas i ON t.subject_type = 'pomysl' AND i.id = t.subject_id
        LEFT JOIN innovations n ON t.subject_type = 'innowacja' AND n.id = t.subject_id
        LEFT JOIN reports r ON t.subject_type = 'zgloszenie' AND r.id = t.subject_id
        WHERE COALESCE(i.area, n.area, r.area) IN ({marks}) AND COALESCE(i.hidden, 0) = 0
        ORDER BY last_at DESC""", areas)
    waiting = [r for r in rows if r["last_role"] not in ("ekspert", "admin")]
    return render_template("ekspert.html", waiting=waiting, others=[r for r in rows if r not in waiting],
                           link=subject_link)
