"""Panel Hubu (ROPS): skrzynka, wątki bez odpowiedzi, statusy, szybka edycja Biblioteki, import,
nabory, luki, trendy potrzeb (tylko admin), kolejka e-mail, eksport CSV. Rola sprawdzana na serwerze."""
import csv
import io
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone

from flask import Blueprint, Response, abort, flash, g, redirect, render_template, request, url_for

from app.auth import role_required, safe_next
from app.views.wiedza import embed_url
from core import db, notify
from core.domain import AREAS, AUDIENCES, GAP_THRESHOLD, POWIATY, REPORT_STATUSES, STAGES, TEST_KINDS
from data.razem import MODERATION_MESSAGES, PUBLIC_KINDS, REQUEST_KINDS, Status

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@role_required("admin")
def guard():
    """Każdy widok panelu wymaga roli administratora."""


UNANSWERED_SQL = """
SELECT t.*, (SELECT MAX(created_at) FROM messages m WHERE m.thread_id = t.id AND m.hidden = 0) AS last_at,
       (SELECT u.role FROM messages m JOIN users u ON u.id = m.user_id
        WHERE m.thread_id = t.id AND m.hidden = 0 ORDER BY m.created_at DESC, m.id DESC LIMIT 1) AS last_role,
       CASE t.subject_type WHEN 'zgloszenie' THEN (SELECT area FROM reports WHERE id = t.subject_id)
                           WHEN 'pomysl' THEN (SELECT area FROM ideas WHERE id = t.subject_id)
                           ELSE (SELECT area FROM innovations WHERE id = t.subject_id) END AS area
FROM threads t ORDER BY last_at DESC"""

# Ostatnia odpowiedź Hubu (admin albo ekspert) w wątku danego tematu.
HUB_REPLIES_SQL = """
SELECT t.subject_type, t.subject_id, MAX(m.created_at) AS at FROM threads t
JOIN messages m ON m.thread_id = t.id JOIN users u ON u.id = m.user_id
WHERE u.role IN ('admin', 'ekspert') AND m.hidden = 0 GROUP BY t.subject_type, t.subject_id"""


def unanswered():
    return [t for t in db.query(UNANSWERED_SQL) if t["last_role"] not in ("admin", "ekspert", None)]


def waited(ts, now=None):
    """„czeka od 5 h” / „czeka od 1 dnia” / „czeka od 3 dni” – od daty ostatniej wiadomości (UTC)."""
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    hours = int((now - datetime.fromisoformat(ts)).total_seconds() // 3600)
    if hours < 1:
        return "czeka od niecałej godziny"
    if hours < 24:
        return f"czeka od {hours} h"
    days = hours // 24
    return f"czeka od {days} {'dnia' if days == 1 else 'dni'}"


def gaps():
    """Luki: słabe dopasowanie, same oceny „niepomocne” albo status nadany przez Hub.
    Zgłoszenia zamknięte i połączone z rozwiązaniem nie są luką."""
    rows = db.query("""
        SELECT r.*, SUM(CASE WHEN m.feedback = 1 THEN 1 ELSE 0 END) AS helpful,
               SUM(CASE WHEN m.feedback = -1 THEN 1 ELSE 0 END) AS unhelpful
        FROM reports r LEFT JOIN matches m ON m.report_id = r.id
        WHERE r.status NOT IN ('zamkniete', 'polaczone') GROUP BY r.id ORDER BY r.created_at DESC""")
    out = []
    for r in rows:
        reasons = []
        if r["best_score"] < GAP_THRESHOLD:
            reasons.append("słabe dopasowanie")
        if r["unhelpful"] and not r["helpful"]:
            reasons.append("autor ocenił propozycje jako niepomocne")
        if r["status"] == "luka":
            reasons.append("oznaczone przez Hub")
        if reasons:
            out.append((r, reasons))
    return out


def helpful_rate():
    row = db.one("SELECT SUM(feedback = 1) AS yes, COUNT(feedback) AS n FROM matches WHERE feedback IS NOT NULL")
    return (round(100 * row["yes"] / row["n"]), row["n"]) if row["n"] else (None, 0)


def inbox():
    """Sprawy skrzynki: (rodzaj, data, treść, link, wiersz, czeka_na_odpowiedź), czekające na górze.
    Liczone raz na żądanie – korzysta z nich skrzynka i licznik w menu."""
    if "inbox" in g:
        return g.inbox
    replied = {(r["subject_type"], r["subject_id"]): r["at"] for r in db.query(HUB_REPLIES_SQL)}
    items = []
    for r in db.query("SELECT r.*, u.name FROM reports r LEFT JOIN users u ON u.id = r.user_id "
                      "WHERE r.status = 'nowe' OR r.approved = 0 ORDER BY r.created_at DESC"):
        items.append(("zgloszenie", r["created_at"], r["body"], f"/zgloszenie/{r['id']}", r,
                      r["status"] == "nowe" and ("zgloszenie", r["id"]) not in replied))
    for i in db.query("SELECT * FROM ideas WHERE created_at >= datetime('now', '-30 days') ORDER BY created_at DESC"):
        items.append(("pomysl", i["created_at"], i["title"], f"/pomysly/{i['id']}", i, ("pomysl", i["id"]) not in replied))
    for t in db.query("SELECT t.*, i.title FROM tests t JOIN innovations i ON i.id = t.innovation_id "
                      "WHERE t.created_at >= datetime('now', '-30 days') ORDER BY t.created_at DESC"):
        items.append(("test", t["created_at"], f"{t['title']} – {TEST_KINDS[t['kind']].lower()}",
                      f"/biblioteka/{t['innovation_id']}#tester", t,
                      replied.get(("innowacja", t["innovation_id"]), "") < t["created_at"]))
    # Wnioski, „Razem z ZD” i „Jestem potrzebny” są w skrzynce tylko, dopóki Hub ich nie obsłużył.
    for a in db.query("SELECT a.*, c.title AS call_title FROM applications a JOIN calls c ON c.id = a.call_id "
                      "WHERE a.status = 'zlozony' ORDER BY a.created_at DESC"):
        items.append(("wniosek", a["created_at"], a["call_title"], f"/wnioski/{a['id']}", a, True))
    for r in db.query("SELECT * FROM family_requests WHERE status = 'nowe' ORDER BY created_at DESC"):
        items.append(("razem", r["created_at"], f"{REQUEST_KINDS[r['kind']]} – {r['alias']} ({r['powiat']})",
                      "/admin/razem", r, True))
    for v in db.query("SELECT * FROM volunteers WHERE status = 'nowe' ORDER BY created_at DESC"):
        items.append(("potrzebny", v["created_at"],
                      f"{'Buddy' if v['role'] == 'buddy' else 'Uczestnik'} – {v['alias']} ({v['powiat']})", "/admin/potrzebny", v, True))
    for o in db.query("SELECT * FROM offers WHERE status = 'nowe' ORDER BY created_at DESC"):
        items.append(("potrzebny", o["created_at"], f"Oferta – {o['institution']}: {o['title']}", "/admin/potrzebny", o, True))
    for w in db.query("SELECT * FROM workplaces WHERE status = 'nowe' ORDER BY created_at DESC"):
        items.append(("potrzebny", w["created_at"], f"Miejsce pracy – {w['name']} ({w['city']})", "/admin/potrzebny", w, True))
    items.sort(key=lambda x: (x[5], x[1]), reverse=True)
    g.inbox = items
    return items


@bp.app_template_global()
def admin_counts():
    """Liczniki w menu panelu – liczone tylko tam, gdzie menu się wyświetla."""
    return {"inbox": sum(1 for it in inbox() if it[5]), "threads": len(unanswered())}


@bp.route("")
def panel():
    kind = request.args.get("typ", "")
    every = inbox()
    items = [it for it in every if kind in ("", it[0])]
    rate, rated = helpful_rate()
    t = trend_data()
    stats = {
        "new": db.one("SELECT COUNT(*) FROM reports WHERE status = 'nowe'")[0],
        "ideas": sum(1 for it in every if it[0] == "pomysl" and it[5]),
        "unanswered": len(unanswered()), "gaps": len(gaps()), "rate": rate, "rated": rated,
        "queue": db.one("SELECT COUNT(*) FROM emails WHERE sent_at IS NULL")[0],
        "trends": [(a, t["mom"][a]["now"]) for a in t["order"][:3] if t["mom"][a]["now"]],
    }
    return render_template("admin/panel.html", items=items, kind=kind, stats=stats)


@bp.route("/watki")
def threads():
    from app.views.komunikacja import subject_link
    return render_template("admin/watki.html", rows=[(t, waited(t["last_at"])) for t in unanswered()],
                           link=subject_link)


@bp.post("/zgloszenie/<int:rid>/status")
def set_status(rid):
    r = db.one("SELECT * FROM reports WHERE id = ?", (rid,))
    if r is None:
        abort(404)
    status = request.form.get("status")
    if status not in REPORT_STATUSES:
        abort(400)
    approved = 1 if request.form.get("approved") == "1" else 0
    db.execute("UPDATE reports SET status = ?, approved = ? WHERE id = ?", (status, approved, rid))
    if status != r["status"] or approved != r["approved"]:
        notify.notify([r["user_id"]], f"Status Twojego zgłoszenia: {REPORT_STATUSES[status]}"
                      + (" (opublikowane)" if approved and not r["approved"] else ""), f"/zgloszenie/{rid}")
    flash("Status zapisany – autor dostał powiadomienie.", "success")
    return redirect(url_for("public.report", rid=rid))


INNOVATION_FIELDS = ("title", "summary", "description", "area", "powiat", "stage", "audience", "org", "video_url", "keywords")


def validate_innovation(form):
    errors = {}
    for k, n in (("title", 3), ("summary", 10), ("description", 20), ("org", 3)):
        if len(form.get(k, "").strip()) < n:
            errors[k] = f"To pole musi mieć co najmniej {n} znaki."
    for k, allowed in (("area", AREAS), ("powiat", POWIATY), ("stage", STAGES), ("audience", AUDIENCES)):
        if form.get(k) not in allowed:
            errors[k] = "Wybierz wartość z listy."
    if form.get("video_url") and not embed_url(form["video_url"]):
        errors["video_url"] = "Wklej link do filmu z YouTube (np. https://www.youtube.com/watch?v=...)."
    return errors


def save_innovation(form, iid=None, is_example=0):
    values = [form.get(k, "").strip() or None if k == "video_url" else form.get(k, "").strip() for k in INNOVATION_FIELDS]
    if iid:
        db.execute(f"UPDATE innovations SET {', '.join(f'{k} = ?' for k in INNOVATION_FIELDS)} WHERE id = ?", (*values, iid))
        return iid
    new_id = db.execute(f"INSERT INTO innovations ({', '.join(INNOVATION_FIELDS)}, is_example, created_at) "
                        f"VALUES ({', '.join('?' * len(INNOVATION_FIELDS))}, ?, ?)", (*values, is_example, db.now()))
    notify.notify_followers(form["area"], f"Nowa innowacja w obszarze, który obserwujesz: „{form['title'][:60]}”",
                            f"/biblioteka/{new_id}", exclude=g.user["id"])
    return new_id


@bp.route("/biblioteka")
def library():
    return render_template("admin/biblioteka.html", rows=db.query("SELECT * FROM innovations ORDER BY created_at DESC"))


@bp.route("/biblioteka/nowa", methods=["GET", "POST"], defaults={"iid": None})
@bp.route("/biblioteka/<int:iid>", methods=["GET", "POST"])
def edit_innovation(iid):
    row = db.one("SELECT * FROM innovations WHERE id = ?", (iid,)) if iid else None
    if iid and row is None:
        abort(404)
    form = {k: (row[k] or "") if row else "" for k in INNOVATION_FIELDS}
    errors = {}
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in INNOVATION_FIELDS}
        errors = validate_innovation(form)
        if not errors:
            saved = save_innovation(form, iid, is_example=row["is_example"] if row else 0)
            flash("Zapisane – zmiana jest od razu widoczna w Bibliotece i w dopasowaniach.", "success")
            return redirect(url_for("wiedza.innovation", iid=saved))
    return render_template("admin/innowacja_form.html", form=form, errors=errors, iid=iid,
                           powiaty=POWIATY, stages=STAGES, audiences=AUDIENCES), (422 if errors else 200)


# Kolumny importu: nazwa w pliku → pole w bazie (CSV albo JSON z Biblioteki ROPS).
IMPORT_COLUMNS = {
    "tytul": "title", "title": "title", "streszczenie": "summary", "summary": "summary",
    "opis": "description", "description": "description", "obszar": "area", "area": "area",
    "powiat": "powiat", "etap": "stage", "stage": "stage", "odbiorcy": "audience", "audience": "audience",
    "organizacja": "org", "org": "org", "film": "video_url", "video_url": "video_url",
    "slowa_kluczowe": "keywords", "keywords": "keywords",
}
AREA_BY_NAME = {a["name"].lower(): s for s, a in AREAS.items()} | {a["short"].lower(): s for s, a in AREAS.items()}


def parse_import(filename, raw):
    text = raw.decode("utf-8-sig")
    if filename.lower().endswith(".json"):
        data = json.loads(text)
        rows = data if isinstance(data, list) else data.get("innowacje") if isinstance(data, dict) else None
        if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
            raise ValueError("JSON musi być listą obiektów albo {\"innowacje\": [...]}")
    else:
        sample = text[:2000]
        dialect = csv.Sniffer().sniff(sample, delimiters=",;") if sample else csv.excel
        rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    out = []
    for row in rows:
        mapped = {IMPORT_COLUMNS[k.strip().lower()]: str(v or "").strip()
                  for k, v in row.items() if k and k.strip().lower() in IMPORT_COLUMNS}
        area = mapped.get("area", "")
        mapped["area"] = area if area in AREAS else AREA_BY_NAME.get(area.lower(), area)
        mapped.setdefault("audience", "cała społeczność")
        mapped.setdefault("keywords", "")
        out.append(mapped)
    return out


@bp.route("/import", methods=["GET", "POST"])
def import_library():
    report = None
    if request.method == "POST":
        f = request.files.get("plik")
        if not f or not f.filename.lower().endswith((".csv", ".json")):
            flash("Wybierz plik CSV albo JSON.", "error")
            return redirect(url_for("admin.import_library"))
        try:
            rows = parse_import(f.filename, f.read())
        except (UnicodeDecodeError, ValueError, csv.Error):  # JSONDecodeError dziedziczy po ValueError
            flash("Nie udało się odczytać pliku. Sprawdź, czy to CSV/JSON w kodowaniu UTF-8.", "error")
            return redirect(url_for("admin.import_library"))
        ok, bad = 0, []
        def key(t):  # tytuł po normalizacji: wielkość liter i białe znaki nie robią nowej innowacji (#23)
            return " ".join(t.split()).casefold()
        seen = {key(r["title"]) for r in db.query("SELECT title FROM innovations")}
        for n, row in enumerate(rows, start=2):
            errors = validate_innovation(row)
            if errors:
                bad.append((n, row.get("title", "?"), "; ".join(f"{k}: {v}" for k, v in errors.items())))
            elif key(row["title"]) in seen:
                bad.append((n, row["title"], "taka innowacja już jest w Bibliotece (ten sam tytuł)"))
            else:
                seen.add(key(row["title"]))
                save_innovation(row, is_example=0)
                ok += 1
        report = {"ok": ok, "bad": bad}
    return render_template("admin/import.html", report=report, columns=sorted(set(IMPORT_COLUMNS)))


@bp.route("/nabory")
def calls():
    return render_template("admin/nabory.html", rows=db.query("SELECT * FROM calls ORDER BY is_open DESC, deadline"))


@bp.post("/nabory/<int:cid>/przelacz")
def toggle_call(cid):
    c = db.one("SELECT * FROM calls WHERE id = ?", (cid,))
    if c is None:
        abort(404)
    new = 0 if c["is_open"] else 1
    db.execute("UPDATE calls SET is_open = ? WHERE id = ?", (new, cid))
    if new:
        n = notify.notify_followers(c["area"], f"Ruszył nabór: „{c['title'][:60]}” – do {c['deadline']}", "/pomysly")
        flash(f"Nabór otwarty. Powiadomiliśmy obserwujących obszar: {n}.", "success")
    else:
        flash("Nabór zamknięty. Generator wniosków jest dla niego nieaktywny.", "success")
    return redirect(url_for("admin.calls"))


@bp.post("/nabory/nowy")
def new_call():
    title, area = request.form.get("title", "").strip(), request.form.get("area")
    desc, deadline = request.form.get("description", "").strip(), request.form.get("deadline", "")
    try:
        date.fromisoformat(deadline)
        valid_date = True
    except ValueError:
        valid_date = False
    if len(title) < 5 or area not in AREAS or len(desc) < 10 or not valid_date:
        flash("Uzupełnij tytuł, obszar, opis i termin naboru.", "error")
    else:
        db.execute("INSERT INTO calls (title, area, description, is_open, deadline, created_at) VALUES (?,?,?,0,?,?)",
                   (title, area, desc, deadline, db.now()))
        flash("Nabór dodany jako zamknięty – otwórz go, gdy będzie gotowy.", "success")
    return redirect(url_for("admin.calls"))


@bp.route("/luki")
def gap_list():
    """Luki są sekcją ekranu „Trendy i luki”; stary adres zostaje jako przekierowanie."""
    return redirect(url_for("admin.trends", _anchor="luki"))


def trend_data():
    """Zgłoszenia wg obszaru: razem, ostatnie 30 dni wobec poprzednich 30, mapa powiat × obszar.
    order = obszary malejąco po ostatnich 30 dniach."""
    if "trends" in g:
        return g.trends
    reports = db.query("SELECT area, powiat, created_at, "
                       "CASE WHEN created_at >= datetime('now', '-30 days') THEN 'now' "
                       "WHEN created_at >= datetime('now', '-60 days') THEN 'prev' END AS win FROM reports")
    by_area = Counter(r["area"] for r in reports)
    mom = {a: {"now": 0, "prev": 0} for a in AREAS}
    heat = defaultdict(Counter)
    for r in reports:
        if r["win"] and r["area"] in mom:
            mom[r["area"]][r["win"]] += 1
        if r["powiat"]:
            heat[r["powiat"]][r["area"]] += 1
    order = sorted(AREAS, key=lambda a: (mom[a]["now"], by_area.get(a, 0)), reverse=True)
    g.trends = {"by_area": by_area, "mom": mom, "heat": heat, "order": order, "total": len(reports)}
    return g.trends


@bp.route("/trendy")
def trends():
    t = trend_data()
    rows = gaps()
    rate, rated = helpful_rate()
    return render_template("admin/trendy.html", **t, powiaty=[p for p in POWIATY if p in t["heat"]],
                           rate=rate, rated=rated, rows=rows,
                           gap_areas=Counter(r["area"] or "" for r, _ in rows).most_common())


@bp.route("/poczta")
def mail_queue():
    rows = db.query("SELECT e.*, u.name FROM emails e JOIN users u ON u.id = e.user_id ORDER BY e.id DESC LIMIT 200")
    return render_template("admin/poczta.html", rows=rows,
                           queue=db.one("SELECT COUNT(*) FROM emails WHERE sent_at IS NULL")[0])


def _csv_cell(v):
    """Ochrona przed wstrzyknięciem formuł w Excelu."""
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s


@bp.route("/eksport/<kind>.csv")
def export(kind):
    if kind == "zgloszenia":
        header = ["id", "data", "obszar", "powiat", "status", "opublikowane", "najlepsze_dopasowanie", "tresc"]
        rows = [(r["id"], r["created_at"], r["area"], r["powiat"], r["status"], r["approved"], r["best_score"], r["body"])
                for r in db.query("SELECT * FROM reports ORDER BY created_at DESC")]
    elif kind == "luki":
        header = ["id", "data", "obszar", "powiat", "powody", "tresc"]
        rows = [(r["id"], r["created_at"], r["area"], r["powiat"], ", ".join(why), r["body"]) for r, why in gaps()]
    elif kind == "oceny":
        header = ["zgloszenie", "innowacja", "trafnosc", "ocena_autora"]
        rows = [(r["report_id"], r["title"], r["score"], {1: "pomocne", -1: "niepomocne"}.get(r["feedback"], ""))
                for r in db.query("SELECT m.*, i.title FROM matches m JOIN innovations i ON i.id = m.innovation_id")]
    else:
        abort(404)
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(header)
    w.writerows([[_csv_cell(v) for v in row] for row in rows])
    return Response("﻿" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=hugme-{kind}.csv"})


# ── Moduł „Razem z ZD” ─────────────────────────────────────────────────────────
def guide_pairs():
    """Propozycje par przewodnik ↔ rodzina: ten sam powiat; ten sam etap wyżej."""
    seek = db.query("SELECT * FROM family_requests WHERE kind = 'przewodnik-szukam' AND status = 'nowe'")
    offer = db.query("SELECT * FROM family_requests WHERE kind = 'przewodnik-oferuje' AND status = 'nowe'")
    pairs = [(s, o, s["stage"] == o["stage"]) for s in seek for o in offer if s["powiat"] == o["powiat"]]
    return sorted(pairs, key=lambda p: not p[2])


@bp.route("/razem")
def razem_panel():
    by_kind = db.query("SELECT kind, powiat, COUNT(*) AS n FROM family_requests WHERE status IN ('nowe','zatwierdzone') "
                       "GROUP BY kind, powiat ORDER BY n DESC")
    days = [r for r in by_kind if r["kind"] == "dzien-specjalistow"]
    public = sorted(PUBLIC_KINDS)
    pending = db.query(f"SELECT * FROM family_requests WHERE kind IN ({','.join('?' * len(public))}) "
                       "AND status = ? ORDER BY created_at", (*public, Status.NEW))
    other = db.query("SELECT * FROM family_requests WHERE kind IN ('wytchnienie','przewodnik-szukam','przewodnik-oferuje') "
                     "AND status = 'nowe' ORDER BY created_at DESC")
    return render_template("admin/razem.html", pairs=guide_pairs(), days=days, pending=pending, other=other,
                           kinds=REQUEST_KINDS)


@bp.post("/razem/<int:rid>/status")
def razem_status(rid):
    r = db.one("SELECT * FROM family_requests WHERE id = ?", (rid,))
    if r is None:
        abort(404)
    status = request.form.get("status")
    # Zatwierdzanie dotyczy tylko treści publicznych (miejsca, sprzęt); pozostałe prośby można jedynie zamknąć.
    allowed = tuple(MODERATION_MESSAGES) if r["kind"] in PUBLIC_KINDS else (Status.CLOSED,)
    if status not in allowed:
        abort(400)
    db.execute("UPDATE family_requests SET status = ? WHERE id = ?", (status, rid))
    notify.notify([r["user_id"]], f"{MODERATION_MESSAGES[status]}: „{(r['title'] or r['kind'])[:60]}”", "/razem")
    flash("Zapisane – autor dostał powiadomienie.", "success")
    return redirect(url_for("admin.razem_panel"))


@bp.post("/razem/polacz")
def razem_pair():
    s = db.one("SELECT * FROM family_requests WHERE id = ? AND kind = 'przewodnik-szukam' AND status = 'nowe'",
               (request.form.get("szukam_id", type=int),))
    o = db.one("SELECT * FROM family_requests WHERE id = ? AND kind = 'przewodnik-oferuje' AND status = 'nowe'",
               (request.form.get("oferuje_id", type=int),))
    if s is None or o is None:
        abort(400)
    con = db.get_db()
    con.execute("UPDATE family_requests SET status = 'polaczone', matched_with = ? WHERE id = ?", (o["id"], s["id"]))
    con.execute("UPDATE family_requests SET status = 'polaczone', matched_with = ? WHERE id = ?", (s["id"], o["id"]))
    con.commit()
    notify.notify([s["user_id"]], f"Hub połączył Cię z rodzicem-przewodnikiem „{o['alias']}”. Koordynatorka zadzwoni, "
                                  "żeby umówić pierwszą rozmowę.", "/razem/przewodnik")
    notify.notify([o["user_id"]], f"Hub połączył Cię z rodziną „{s['alias']}”, która szuka przewodnika. Dziękujemy!",
                  "/razem/przewodnik")
    flash(f"Połączono: {s['alias']} ↔ {o['alias']}. Obie strony dostały powiadomienie.", "success")
    return redirect(url_for("admin.razem_panel"))


HIDEABLE = {"pomysl": ("ideas", "pomysł"), "wiadomosc": ("messages", "wiadomość")}


@bp.post("/ukryj/<kind>/<int:oid>")
def toggle_hidden(kind, oid):
    """Moderacja po publikacji: ukryty wpis znika dla wszystkich poza Hubem; da się go przywrócić."""
    if kind not in HIDEABLE:
        abort(404)
    table, label = HIDEABLE[kind]
    row = db.one(f"SELECT user_id, hidden FROM {table} WHERE id = ?", (oid,))
    if row is None:
        abort(404)
    db.execute(f"UPDATE {table} SET hidden = ? WHERE id = ?", (0 if row["hidden"] else 1, oid))
    db.execute("INSERT INTO admin_log (admin_id, user_id, action, created_at) VALUES (?,?,?,?)",
               (g.user["id"], row["user_id"], f"{'przywrócono' if row['hidden'] else 'ukryto'} {label} #{oid}", db.now()))
    flash(f"{label.capitalize()} {'przywrócona' if kind == 'wiadomosc' else 'przywrócony'}." if row["hidden"]
          else f"{label.capitalize()} {'ukryta' if kind == 'wiadomosc' else 'ukryty'} – widzi go tylko Hub.", "success")
    return redirect(safe_next(request.form.get("next"), url_for("admin.panel")))
