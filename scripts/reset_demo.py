"""Odnawia publiczne demo: czyści dane i ładuje seed – ale tylko po >= 20 min bez nowych wpisów, żeby nie
skasować oglądającemu tego, co przed chwilą zapisał. Licznik AI (ai_usage) zostaje.

Uruchom (Coolify → Scheduled Tasks, co godzinę):  python scripts/reset_demo.py [--force]"""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import db  # noqa: E402
from data import seed  # noqa: E402

QUIET = timedelta(minutes=20)
KEEP = {"ai_usage"}


def last_write(con):
    """Najnowszy created_at we wszystkich tabelach.
    ponytail: same UPDATE-y (np. zmiana statusu) nie mają znacznika czasu – nie wstrzymują resetu."""
    stamps = []
    for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"):
        if "created_at" in {r[1] for r in con.execute(f"PRAGMA table_info({table})")}:
            stamps.append(con.execute(f"SELECT MAX(created_at) FROM {table}").fetchone()[0])
    latest = max((s for s in stamps if s), default=None)
    return datetime.strptime(latest[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) if latest else None


def reset(con, force=False, now=None):
    """Zwraca True, gdy demo odnowiono."""
    now = now or datetime.now(timezone.utc)
    latest = last_write(con)
    if not force and latest and now - latest < QUIET:
        return False
    tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
              if t not in KEEP]
    con.execute("PRAGMA foreign_keys = OFF")
    for table in tables:
        con.execute(f"DELETE FROM {table}")
    seed.run(con)  # te same identyfikatory kont (1–5), więc zalogowani zostają na swoich rolach
    return True


if __name__ == "__main__":
    path = os.environ.get("DATABASE", str(ROOT / "instance" / "hugme.db"))
    con = db.connect(path)
    db.init_schema(con)
    done = reset(con, force="--force" in sys.argv)
    print("Demo odnowione." if done else "Pominięte – ktoś niedawno coś zapisał.")
