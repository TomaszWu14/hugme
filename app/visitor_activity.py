"""Aktywność gościa demo po wejściu przez bramkę: liczba obejrzanych ekranów, ostatnia wizyta i sekcje.
Liczymy tylko udane GET-y stron HTML (bez static, /zdrowie, API i samej bramki) od gościa z ważnym, podpisanym
ciasteczkiem niosącym id wpisu. Zapis jednym UPDATE; każdy błąd to ostrzeżenie w logu, odpowiedź bez zmian."""
import contextlib
import json
import logging
import os
import re
from datetime import datetime, timezone

from app.visitor_notify import notify_engaged
from core import db

MAX_SECTIONS = 20
SECTION_LEN = 40
DEFAULT_ENGAGED_VIEWS = 10
_NOT_SECTION = re.compile(r"[^a-z0-9_-]")
log = logging.getLogger(__name__)

# Licznik sekcji: istniejąca sekcja +1 zawsze, nowa tylko poniżej MAX_SECTIONS (20) kluczy – ponad limit ignorowana.
_UPDATE = """
UPDATE demo_visitors SET page_views = page_views + 1, last_seen_at = :now,
    sections = CASE
        WHEN :path IS NULL THEN sections
        WHEN json_type(sections, :path) IS NOT NULL OR (SELECT COUNT(*) FROM json_each(sections)) < 20
            THEN json_set(sections, :path, COALESCE(json_extract(sections, :path), 0) + 1)
        ELSE sections END
WHERE id = :id
RETURNING page_views, first_name, last_name, company
"""


def section_of(path):
    """Pierwszy segment ścieżki jako nazwa sekcji („/palety/12” → „palety”, „/” → „start”); None, gdy nic nie zostaje."""
    first = path.strip("/").split("/", 1)[0]
    if not first:
        return "start"
    return _NOT_SECTION.sub("", first.lower())[:SECTION_LEN] or None


def engaged_threshold():
    """Próg „zaangażowanego gościa” z NTFY_ENGAGED_VIEWS (domyślnie 10; 0 = wyłączone)."""
    try:
        return max(0, int(os.environ.get("NTFY_ENGAGED_VIEWS", DEFAULT_ENGAGED_VIEWS)))
    except ValueError:
        return DEFAULT_ENGAGED_VIEWS


def countable(request, resp, exempt):
    """Czy odpowiedź to obejrzany ekran: GET, sukces (bez przekierowań), strona HTML spoza ścieżek wyłączonych."""
    ok = resp.status_code < 300 or resp.status_code == 304
    return request.method == "GET" and ok and resp.mimetype == "text/html" and not request.path.startswith(exempt)


def track(visitor_id, path):
    """Zlicza ekran gościa; przy dokładnie NTFY_ENGAGED_VIEWS ekranach wysyła jeden push. Nigdy nie rzuca wyjątku."""
    try:
        section = section_of(path)
        con = db.get_db()
        row = con.execute(_UPDATE, {"now": db.now(), "path": f'$."{section}"' if section else None,
                                    "id": visitor_id}).fetchone()
        con.commit()
    except Exception as exc:  # noqa: BLE001 – statystyka jest dodatkiem, nigdy nie psuje odpowiedzi
        log.warning("Aktywność gościa nie zapisana: %s", exc)
        with contextlib.suppress(Exception):  # po nieudanym zapisie nic więcej nie da się zrobić
            db.get_db().rollback()
        return
    threshold = engaged_threshold()
    if row and threshold and row["page_views"] == threshold:
        notify_engaged(row["first_name"], row["last_name"], row["company"], row["page_views"])


def _utc(stamp):
    return datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)  # db.now() zapisuje UTC


def summary(row):
    """Kolumny listy gości: ekrany, czas wizyty („ok. N min” / „—”) i 3 najczęstsze sekcje."""
    try:
        sections = json.loads(row["sections"] or "{}")
    except ValueError:
        sections = {}
    top = sorted(sections.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    duration = "—"
    if row["last_seen_at"]:
        seconds = (_utc(row["last_seen_at"]) - _utc(row["created_at"])).total_seconds()
        duration = f"ok. {max(0, round(seconds / 60))} min"
    return {"views": row["page_views"], "duration": duration, "top": ", ".join(f"{k} ({v})" for k, v in top) or "—"}
