"""Panel Hubu dla programu „Jestem potrzebny” i mapy pracy: propozycje par, zatwierdzanie, potwierdzanie misji."""
from flask import Blueprint, abort, flash, g, redirect, request, render_template, url_for

from core import db, notify
from data import potrzebny as P
from data import praca as W

bp = Blueprint("admin_potrzebny", __name__, url_prefix="/admin/potrzebny")


@bp.before_request
def only_admin():
    if g.user is None:
        return redirect(url_for("auth.demo", next=request.full_path))
    if g.user["role"] != "admin":
        abort(403)


def _set(csv):
    return {s for s in csv.split(",") if s}


def pair_proposals():
    """Uczestnik ↔ oferta: ten sam powiat, rodzaj misji wśród zainteresowań, wiek pasuje, wolne miejsca.
    Sortowanie: liczba wspólnych dni malejąco. Do pary z „proszę o buddy” – sugerowany buddy z powiatu."""
    vols = db.query("SELECT * FROM volunteers WHERE role = 'uczestnik' AND status = 'nowe' ORDER BY created_at")
    offers = db.query("SELECT * FROM offers WHERE status = 'zatwierdzone'")
    taken = {r["offer_id"]: r["n"] for r in db.query(
        "SELECT offer_id, COUNT(*) AS n FROM missions WHERE status = 'polaczone' GROUP BY offer_id")}
    buddies = db.query("SELECT * FROM volunteers WHERE role = 'buddy' AND status = 'nowe'")
    out = []
    for v in vols:
        wants = _set(v["interests"])
        for o in offers:
            if o["powiat"] != v["powiat"] or taken.get(o["id"], 0) >= o["slots"]:
                continue
            liked = P.MISSION_KINDS[o["mission_kind"]][2]
            if liked and liked not in wants:
                continue
            if v["age_group"] not in _set(o["for_whom"]):
                continue
            common = len(_set(v["days"]) & _set(o["days"]))
            buddy = None
            if v["companion"] == "buddy":
                buddy = next((b for b in buddies if b["powiat"] == v["powiat"] and _set(b["days"]) & _set(v["days"])), None)
            out.append((v, o, common, buddy))
    return sorted(out, key=lambda t: -t[2])


@bp.route("")
def panel():
    pending_offers = db.query("SELECT * FROM offers WHERE status = 'nowe' ORDER BY created_at")
    pending_places = db.query("SELECT * FROM workplaces WHERE status = 'nowe' ORDER BY created_at")
    active = db.query("SELECT m.*, v.alias, v.powiat, o.title, o.institution, o.mission_kind, b.alias AS buddy "
                      "FROM missions m JOIN volunteers v ON v.id = m.volunteer_id JOIN offers o ON o.id = m.offer_id "
                      "LEFT JOIN volunteers b ON b.id = m.buddy_id WHERE m.status = 'polaczone' ORDER BY m.created_at DESC")
    stats = {
        "vols": db.one("SELECT COUNT(*) FROM volunteers WHERE role = 'uczestnik'")[0],
        "buddies": db.one("SELECT COUNT(*) FROM volunteers WHERE role = 'buddy'")[0],
        "offers": db.one("SELECT COUNT(*) FROM offers WHERE status = 'zatwierdzone'")[0],
        "done": db.one("SELECT COALESCE(SUM(done), 0) FROM missions")[0],
        "places": db.one("SELECT COUNT(*) FROM workplaces WHERE status = 'zatwierdzone'")[0],
    }
    by_powiat = db.query("SELECT v.powiat, o.mission_kind, SUM(m.done) AS n FROM missions m "
                         "JOIN volunteers v ON v.id = m.volunteer_id JOIN offers o ON o.id = m.offer_id "
                         "GROUP BY v.powiat, o.mission_kind HAVING n > 0 ORDER BY n DESC")
    return render_template("admin/potrzebny.html", pairs=pair_proposals(), pending_offers=pending_offers,
                           pending_places=pending_places, active=active, stats=stats, by_powiat=by_powiat, P=P, W=W)


@bp.post("/polacz")
def pair():
    v = db.one("SELECT * FROM volunteers WHERE id = ? AND role = 'uczestnik' AND status = 'nowe'",
               (request.form.get("volunteer_id", type=int),))
    o = db.one("SELECT * FROM offers WHERE id = ? AND status = 'zatwierdzone'", (request.form.get("offer_id", type=int),))
    bid = request.form.get("buddy_id", type=int)
    b = db.one("SELECT * FROM volunteers WHERE id = ? AND role = 'buddy' AND status = 'nowe'", (bid,)) if bid else None
    if v is None or o is None or (bid and b is None):
        abort(400)
    con = db.get_db()
    con.execute("INSERT INTO missions (volunteer_id, offer_id, buddy_id, created_at) VALUES (?,?,?,?)",
                (v["id"], o["id"], b["id"] if b else None, db.now()))
    con.execute("UPDATE volunteers SET status = 'polaczone' WHERE id = ?", (v["id"],))
    if b:
        con.execute("UPDATE volunteers SET status = 'polaczone' WHERE id = ?", (b["id"],))
    con.commit()
    link = url_for("potrzebny.diary")
    notify.notify([v["user_id"]], f"Hub połączył Cię z miejscem „{o['institution']}”: {o['title']}. Koordynatorka "
                                  "zadzwoni, żeby umówić pierwszą misję.", link)
    notify.notify([o["user_id"]], f"Hub dobrał uczestnika („{v['alias']}”) do Waszej oferty „{o['title']}”. "
                                  "Koordynatorka zadzwoni, żeby umówić pierwszą misję.", url_for("potrzebny.start"))
    if b:
        notify.notify([b["user_id"]], f"Hub prosi Cię o towarzyszenie w misji: „{o['title']}” ({o['institution']}). "
                                      "Koordynatorka zadzwoni.", url_for("potrzebny.start"))
    flash(f"Połączono: {v['alias']} ↔ {o['institution']}" + (f" (buddy: {b['alias']})" if b else "") + ".", "success")
    return redirect(url_for("admin_potrzebny.panel"))


@bp.post("/oferta/<int:oid>/status")
def offer_status(oid):
    o = db.one("SELECT * FROM offers WHERE id = ?", (oid,))
    status = request.form.get("status")
    if o is None or status not in ("zatwierdzone", "odrzucone", "zamkniete"):
        abort(400)
    db.execute("UPDATE offers SET status = ? WHERE id = ?", (status, oid))
    word = {"zatwierdzone": "Hub opublikował", "odrzucone": "Hub nie opublikował", "zamkniete": "Hub zamknął"}[status]
    notify.notify([o["user_id"]], f"{word}: „{o['title'][:60]}”.", url_for("potrzebny.start"))
    flash("Zapisane – autor dostał powiadomienie.", "success")
    return redirect(url_for("admin_potrzebny.panel"))


@bp.post("/miejsce/<int:wid>/status")
def place_status(wid):
    w = db.one("SELECT * FROM workplaces WHERE id = ?", (wid,))
    status = request.form.get("status")
    if w is None or status not in ("zatwierdzone", "odrzucone"):
        abort(400)
    db.execute("UPDATE workplaces SET status = ?, checked_at = ? WHERE id = ?", (status, db.now()[:10], wid))
    if w["user_id"]:
        notify.notify([w["user_id"]], f"{'Hub dodał na mapę' if status == 'zatwierdzone' else 'Hub nie dodał na mapę'}: "
                                      f"„{w['name'][:60]}”.", url_for("praca.index"))
    flash("Zapisane.", "success")
    return redirect(url_for("admin_potrzebny.panel"))


@bp.post("/misja/<int:mid>/odbyta")
def mission_done(mid):
    m = db.one("SELECT m.*, v.user_id FROM missions m JOIN volunteers v ON v.id = m.volunteer_id "
               "WHERE m.id = ? AND m.status = 'polaczone'", (mid,))
    if m is None:
        abort(400)
    db.execute("UPDATE missions SET done = done + 1 WHERE id = ?", (mid,))
    notify.notify([m["user_id"]], "Hub potwierdził Twoją misję. Zobacz dzienniczek i odznaki!", url_for("potrzebny.diary"))
    flash("Misja policzona – uczestnik dostał powiadomienie.", "success")
    return redirect(url_for("admin_potrzebny.panel"))


@bp.post("/misja/<int:mid>/zamknij")
def mission_close(mid):
    m = db.one("SELECT * FROM missions WHERE id = ? AND status = 'polaczone'", (mid,))
    if m is None:
        abort(400)
    con = db.get_db()
    con.execute("UPDATE missions SET status = 'zamkniete' WHERE id = ?", (mid,))
    con.execute("UPDATE volunteers SET status = 'nowe' WHERE id = ?", (m["volunteer_id"],))
    if m["buddy_id"]:
        con.execute("UPDATE volunteers SET status = 'nowe' WHERE id = ?", (m["buddy_id"],))
    con.commit()
    flash("Para zamknięta – uczestnik wraca do puli.", "success")
    return redirect(url_for("admin_potrzebny.panel"))
