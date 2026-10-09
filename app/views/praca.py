"""Zakładka „Praca”: mapa miejsc, w których pracują osoby z zespołem Downa (prawdziwe, ze źródłem),
statystyki i „Poznaj ZD”. Mapy to własny SVG bez JS – klik w region = link z filtrem."""
import re

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from core import db, notify
from core.domain import POWIATY
from core.privacy import mask
from data import mapa, praca as W
from data import potrzebny as P

bp = Blueprint("praca", __name__, url_prefix="/razem/praca")
RE_URL = re.compile(r"^https?://[^\s/]+\.[^\s]+$")


def level(n, top):
    """0–4 jak heatmapa trendów: udział w maksimum."""
    if not n:
        return 0
    return 1 + min(3, int(3 * n / max(top, 1)))


def interests_chart():
    counts = {k: 0 for k in P.INTERESTS}
    for r in db.query("SELECT interests FROM volunteers WHERE role = 'uczestnik'"):
        for s in r["interests"].split(","):
            if s in counts:
                counts[s] += 1
    top = max(counts.values()) or 1
    return [(k, P.INTERESTS[k][0], n, round(100 * n / top)) for k, n in sorted(counts.items(), key=lambda kv: -kv[1])]


@bp.route("")
def index(errors=None, form=None):
    woj = request.args.get("woj", "")
    woj = woj if woj in W.VOIVODESHIPS else ""
    powiat = request.args.get("powiat", "")
    powiat = powiat if powiat in POWIATY else ""
    rows = db.query("SELECT * FROM workplaces WHERE status = 'zatwierdzone' ORDER BY voivodeship, kind, name")
    by_woj, by_powiat = {}, {}
    for r in rows:
        by_woj[r["voivodeship"]] = by_woj.get(r["voivodeship"], 0) + 1
        if r["powiat"]:
            by_powiat[r["powiat"]] = by_powiat.get(r["powiat"], 0) + 1
    top_w, top_p = max(by_woj.values(), default=0), max(by_powiat.values(), default=0)
    regions_pl = [(slug, name, path, cx, cy, by_woj.get(slug, 0), level(by_woj.get(slug, 0), top_w))
                  for slug, name, path, cx, cy in mapa.WOJEWODZTWA]
    regions_mp = [(slug, name, path, cx, cy, by_powiat.get(name, 0), level(by_powiat.get(name, 0), top_p))
                  for slug, name, path, cx, cy in mapa.POWIATY_MALOPOLSKA]
    if powiat:
        shown = [r for r in rows if r["powiat"] == powiat]
    elif woj:
        shown = [r for r in rows if r["voivodeship"] == woj]
    else:
        shown = rows
    return render_template("razem/praca.html", W=W, P=P, mapa=mapa, rows=shown, total=len(rows), woj=woj, powiat=powiat,
                           regions_pl=regions_pl, regions_mp=regions_mp, chart=interests_chart(), powiaty=POWIATY,
                           errors=errors or {}, form=form or {})


@bp.post("/zglos")
def propose():
    if g.user is None:
        return redirect(url_for("auth.demo", next=url_for("praca.index") + "#zglos"))
    f = {k: request.form.get(k, "").strip() for k in ("name", "kind", "city", "voivodeship", "powiat", "url", "note")}
    errors = {}
    if len(f["name"]) < 3:
        errors["name"] = "Wpisz nazwę miejsca."
    if f["kind"] not in W.KINDS:
        errors["kind"] = "Wybierz rodzaj miejsca."
    if len(f["city"]) < 2:
        errors["city"] = "Wpisz miejscowość."
    if f["voivodeship"] not in W.VOIVODESHIPS:
        errors["voivodeship"] = "Wybierz województwo."
    if f["powiat"] and (f["powiat"] not in POWIATY or f["voivodeship"] != "malopolskie"):
        errors["powiat"] = "Powiat podajemy tylko dla Małopolski."
    if not RE_URL.match(f["url"]):
        errors["url"] = "Podaj link do źródła (artykuł, strona miejsca) zaczynający się od http."
    if errors:  # formularz z błędami przy polach i wpisanymi danymi, bez przekierowania (#25, WCAG 3.3.1/3.3.3)
        return index(errors, f), 422
    db.execute("INSERT INTO workplaces (name, kind, city, voivodeship, powiat, url, note, checked_at, status, user_id, "
               "created_at) VALUES (?,?,?,?,?,?,?,?, 'nowe', ?, ?)",
               (mask(f["name"])[0][:120], f["kind"], mask(f["city"])[0][:60], f["voivodeship"], f["powiat"] or None,
                f["url"][:300], mask(f["note"])[0][:500], db.now()[:10], g.user["id"], db.now()))
    notify.notify_admins(f"Praca: propozycja miejsca „{f['name'][:40]}” ({W.VOIVODESHIPS[f['voivodeship']]})",
                         "/admin/potrzebny", exclude=g.user["id"])
    flash(P.THANKS["praca"], "success")
    return redirect(url_for("praca.index"))
