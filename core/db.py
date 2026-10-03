"""Warstwa bazy danych. SQLite w prototypie; schemat trzyma się typów zgodnych z PostgreSQL
(TEXT, INTEGER, REAL, TIMESTAMP). Przy migracji na PostgreSQL: `INTEGER PRIMARY KEY` →
`INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY`, placeholder `?` → `%s`."""
import sqlite3
from datetime import datetime, timezone

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('mieszkaniec','ngo','gmina','ekspert','admin')),
    org TEXT,
    areas TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL,
    bio TEXT NOT NULL DEFAULT '',
    is_demo INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS innovations (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    description TEXT NOT NULL,
    area TEXT NOT NULL,
    powiat TEXT NOT NULL,
    stage TEXT NOT NULL,
    audience TEXT NOT NULL,
    org TEXT NOT NULL,
    video_url TEXT,
    keywords TEXT NOT NULL DEFAULT '',
    is_example INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    body TEXT NOT NULL,
    area TEXT,
    powiat TEXT,
    status TEXT NOT NULL DEFAULT 'nowe',
    approved INTEGER NOT NULL DEFAULT 0,
    best_score REAL NOT NULL DEFAULT 0,
    is_example INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS matches (
    report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    innovation_id INTEGER NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    score REAL NOT NULL,
    feedback INTEGER CHECK (feedback IN (-1, 1)),
    PRIMARY KEY (report_id, innovation_id)
);
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    area TEXT NOT NULL,
    kind TEXT NOT NULL,
    summary TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    area TEXT NOT NULL,
    description TEXT NOT NULL,
    is_open INTEGER NOT NULL DEFAULT 0,
    deadline TEXT,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    essence TEXT NOT NULL,
    audience TEXT NOT NULL,
    stage TEXT NOT NULL,
    area TEXT,
    canvas TEXT NOT NULL DEFAULT '{}',
    is_example INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY,
    idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
    call_id INTEGER NOT NULL REFERENCES calls(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    fields TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'szkic' CHECK (status IN ('szkic','zlozony')),
    created_at TIMESTAMP NOT NULL,
    UNIQUE (idea_id, call_id)
);
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY,
    innovation_id INTEGER NOT NULL REFERENCES innovations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL CHECK (kind IN ('zgloszenie','ocena','usprawnienie')),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    body TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY,
    subject_type TEXT NOT NULL CHECK (subject_type IN ('zgloszenie','pomysl','innowacja')),
    subject_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    UNIQUE (subject_type, subject_id)
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    thread_id INTEGER NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    link TEXT NOT NULL DEFAULT '/',
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS follows (
    user_id INTEGER NOT NULL REFERENCES users(id),
    area TEXT NOT NULL,
    PRIMARY KEY (user_id, area)
);
CREATE TABLE IF NOT EXISTS broker_cards (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    context TEXT NOT NULL,
    card TEXT NOT NULL,
    by_ai INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS family_requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL CHECK (kind IN ('przewodnik-szukam','przewodnik-oferuje','wytchnienie',
        'dzien-specjalistow','miejsce','sprzet-oddam','sprzet-przyjme')),
    powiat TEXT NOT NULL,
    stage TEXT,
    alias TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'nowe' CHECK (status IN ('nowe','zatwierdzone','odrzucone','polaczone','zamkniete')),
    matched_with INTEGER REFERENCES family_requests(id),
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    powiat TEXT NOT NULL,
    date TEXT NOT NULL,
    place TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS event_signups (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (event_id, user_id)
);
-- Program „Jestem potrzebny” (uczestnicy i buddy w jednej tabeli, rola w polu role) i mapa pracy.
CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL CHECK (role IN ('uczestnik','buddy')),
    alias TEXT NOT NULL,
    powiat TEXT NOT NULL,
    age_group TEXT NOT NULL DEFAULT '',
    interests TEXT NOT NULL DEFAULT '',
    days TEXT NOT NULL DEFAULT '',
    companion TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    consent INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'rodzic',
    status TEXT NOT NULL DEFAULT 'nowe' CHECK (status IN ('nowe','polaczone','zamkniete')),
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    source TEXT NOT NULL DEFAULT 'instytucja' CHECK (source IN ('instytucja','rodzic')),
    institution TEXT NOT NULL,
    mission_kind TEXT NOT NULL CHECK (mission_kind IN ('psy','hospicjum','dzieci','inne')),
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    body_easy TEXT NOT NULL DEFAULT '',
    easy_by_ai INTEGER NOT NULL DEFAULT 0,
    powiat TEXT NOT NULL,
    days TEXT NOT NULL DEFAULT '',
    slots INTEGER NOT NULL DEFAULT 1,
    for_whom TEXT NOT NULL DEFAULT '',
    provides TEXT NOT NULL DEFAULT '',
    requirements TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'nowe' CHECK (status IN ('nowe','zatwierdzone','odrzucone','zamkniete')),
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(id),
    offer_id INTEGER NOT NULL REFERENCES offers(id),
    buddy_id INTEGER REFERENCES volunteers(id),
    done INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'polaczone' CHECK (status IN ('polaczone','zamkniete')),
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS workplaces (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('otwarty','spoleczne','zaz','wtz')),
    city TEXT NOT NULL,
    voivodeship TEXT NOT NULL,
    powiat TEXT,
    url TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    checked_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'nowe' CHECK (status IN ('nowe','zatwierdzone','odrzucone')),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS admin_log (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
CREATE TABLE IF NOT EXISTS ai_usage (
    day TEXT PRIMARY KEY,
    calls INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_reports_created ON reports(created_at);
CREATE INDEX IF NOT EXISTS ix_notifications_user ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS ix_messages_thread ON messages(thread_id);
"""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def get_db():
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE"])
    return g.db


def close_db(_exc=None):
    con = g.pop("db", None)
    if con is not None:
        con.close()


def init_schema(con):
    con.executescript(SCHEMA)
    # Migracja istniejących baz (wolumen na produkcji): kolumny dodane po pierwszym wdrożeniu.
    for table, column in (("users", "is_active INTEGER NOT NULL DEFAULT 1"), ("ideas", "hidden INTEGER NOT NULL DEFAULT 0"),
                          ("messages", "hidden INTEGER NOT NULL DEFAULT 0")):
        if column.split()[0] not in {r[1] for r in con.execute(f"PRAGMA table_info({table})")}:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {column}")
    con.commit()


def query(sql, args=()):
    return get_db().execute(sql, args).fetchall()


def one(sql, args=()):
    return get_db().execute(sql, args).fetchone()


def execute(sql, args=()):
    con = get_db()
    cur = con.execute(sql, args)
    con.commit()
    return cur.lastrowid
