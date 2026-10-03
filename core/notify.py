"""Powiadomienia w aplikacji + kolejka e-mail (tabela `emails`).

Prototyp nie wysyła poczty – kolejkę widać w panelu Hubu. Wdrożenie: worker co minutę
wysyła wiersze z sent_at IS NULL przez SMTP (patrz docs/ARCHITEKTURA.md)."""
from core import db


def notify(user_ids, body, link="/", subject=None):
    ids = {u for u in user_ids if u}
    con = db.get_db()
    for uid in ids:
        con.execute("INSERT INTO notifications (user_id, body, link, created_at) VALUES (?,?,?,?)",
                    (uid, body, link, db.now()))
        con.execute("INSERT INTO emails (user_id, subject, body, created_at) VALUES (?,?,?,?)",
                    (uid, subject or "HugMe: " + body[:60], f"{body}\n\nZobacz: {link}", db.now()))
    con.commit()
    return len(ids)


def admin_ids():
    return [r["id"] for r in db.query("SELECT id FROM users WHERE role = 'admin'")]


def notify_admins(body, link="/admin", exclude=None):
    return notify([u for u in admin_ids() if u != exclude], body, link)


def notify_followers(area, body, link, exclude=None):
    rows = db.query("SELECT user_id FROM follows WHERE area = ?", (area,))
    return notify([r["user_id"] for r in rows if r["user_id"] != exclude], body, link)


def notify_experts(area, body, link, exclude=None):
    rows = db.query("SELECT id, areas FROM users WHERE role = 'ekspert'")
    return notify([r["id"] for r in rows if area in r["areas"].split(",") and r["id"] != exclude], body, link)
