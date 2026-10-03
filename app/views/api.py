"""API JSON dla integracji (docelowo baza grantowa ROPS). Bezstanowe: nie korzysta z sesji ani
ciasteczek, dlatego nie podlega CSRF. Matchmaking deterministyczny (bez AI)."""
from flask import Blueprint, abort, jsonify, request, url_for

from core import catalog, db
from core.domain import AREAS, POWIATY, STAGES
from core.match import detect_area
from core.privacy import mask

bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _innovation(i, res=None):
    out = {"id": i["id"], "tytul": i["title"], "streszczenie": i["summary"], "obszar": i["area"],
           "powiat": i["powiat"], "etap": i["stage"], "dla_kogo": i["audience"], "organizacja": i["org"],
           "przyklad": bool(i["is_example"]), "url": url_for("wiedza.innovation", iid=i["id"], _external=True)}
    if res:
        out.update(trafnosc=res.score, etykieta=res.label, dlaczego={"slowa": res.words, "tematy": res.topics})
    return out


@bp.post("/dopasuj")
def match():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Wyślij obiekt JSON, np. {\"opis\": \"...\"} z nagłówkiem Content-Type: application/json."), 400
    text = data.get("opis")
    limit = data.get("limit", 5)
    if not isinstance(text, str) or not 15 <= len(text.strip()) <= 1500:
        return jsonify(error="Pole 'opis' musi być tekstem o długości 15–1500 znaków."), 422
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 20:
        return jsonify(error="Pole 'limit' musi być liczbą 1–20."), 422
    masked, found = mask(text.strip())
    return jsonify(
        opis_zamaskowany=masked, ukryte_dane=sorted(set(found)), obszar=detect_area(masked),
        wyniki=[_innovation(i, r) for i, r in catalog.match_innovations(masked, k=limit)],
    )


@bp.get("/innowacje")
def innovations():
    sql, args = "SELECT * FROM innovations WHERE 1=1", []
    for key, col, allowed in [("obszar", "area", AREAS), ("powiat", "powiat", POWIATY), ("etap", "stage", STAGES)]:
        value = request.args.get(key)
        if value:
            if value not in allowed:
                abort(400)
            sql += f" AND {col} = ?"
            args.append(value)
    rows = db.query(sql + " ORDER BY id", args)
    return jsonify(liczba=len(rows), innowacje=[_innovation(r) for r in rows])
