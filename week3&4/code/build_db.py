"""Build history.db from the JSON files in code/data/.

Steps (re-runnable, additive):
    1. read every code/data/*.json
    2. create the tables with foreign keys and CHECK constraints
    3. insert the rows
    4. verify with PRAGMA foreign_key_check and integrity_check
    5. export a flat views/records.json for quick reading

Run:
    python code/build_db.py
"""

import glob
import json
import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
DB = os.path.join(ROOT, "history.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    id           INTEGER PRIMARY KEY,
    code         TEXT NOT NULL UNIQUE,
    title        TEXT NOT NULL,
    author       TEXT,
    year         INTEGER,
    publisher    TEXT,
    gutenberg_id INTEGER,
    url          TEXT,
    local_path   TEXT,
    note         TEXT NOT NULL DEFAULT ''
);

CREATE TABLE places (
    id              INTEGER PRIMARY KEY,
    name_normalized TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    conversion      TEXT NOT NULL,
    kind            TEXT,
    lat             REAL CHECK (lat  IS NULL OR lat  BETWEEN -90  AND 90),
    lon             REAL CHECK (lon  IS NULL OR lon  BETWEEN -180 AND 180),
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    locator         TEXT NOT NULL,
    note            TEXT NOT NULL DEFAULT ''
);

CREATE TABLE people (
    id              INTEGER PRIMARY KEY,
    name_normalized TEXT NOT NULL,
    name_original   TEXT NOT NULL,
    conversion      TEXT NOT NULL,
    role            TEXT,
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    locator         TEXT NOT NULL,
    note            TEXT NOT NULL DEFAULT ''
);

CREATE TABLE events (
    id              INTEGER PRIMARY KEY,
    year            INTEGER CHECK (year IS NULL OR year BETWEEN 1800 AND 1950),
    date_normalized TEXT,
    date_original   TEXT,
    date_conversion TEXT,
    event           TEXT NOT NULL,
    place_id        INTEGER REFERENCES places(id),
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    locator         TEXT NOT NULL,
    quote           TEXT NOT NULL DEFAULT '',
    note            TEXT NOT NULL DEFAULT ''
);

CREATE TABLE event_people (
    event_id  INTEGER NOT NULL REFERENCES events(id),
    person_id INTEGER NOT NULL REFERENCES people(id),
    role      TEXT,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    locator   TEXT NOT NULL,
    note      TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (event_id, person_id)
);

CREATE TABLE images (
    id              INTEGER PRIMARY KEY,
    file            TEXT NOT NULL UNIQUE,
    caption         TEXT,
    author          TEXT,
    date_original   TEXT,
    date_normalized TEXT,
    date_conversion TEXT,
    license         TEXT,
    commons_url     TEXT,
    source_id       INTEGER NOT NULL REFERENCES sources(id),
    locator         TEXT NOT NULL,
    note            TEXT NOT NULL DEFAULT ''
);

CREATE TABLE image_events (
    image_id  INTEGER NOT NULL REFERENCES images(id),
    event_id  INTEGER NOT NULL REFERENCES events(id),
    source_id INTEGER NOT NULL REFERENCES sources(id),
    locator   TEXT NOT NULL,
    note      TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (image_id, event_id)
);

CREATE VIEW v_events_full AS
SELECT e.id, e.year, e.date_normalized, e.event,
       p.name_normalized AS place,
       s.code AS source, s.title AS source_title, e.locator, e.note
FROM events e
JOIN sources s ON s.id = e.source_id
LEFT JOIN places p ON p.id = e.place_id;
"""

TABLES = ["sources", "places", "people", "events", "event_people", "images", "image_events"]


def load(name):
    path = os.path.join(DATA, name + ".json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all():
    data = {t: [] for t in TABLES}
    for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.startswith("events_"):
            name = "events"
        if name not in data:
            continue
        with open(path, encoding="utf-8") as f:
            data[name].extend(json.load(f))
    return data


def enrich_junctions(data):
    """Derive source_id/locator for junction rows from their event (the link is
    attested by the same source as the event)."""
    src = {e["id"]: (e["source_id"], e["locator"]) for e in data["events"]}
    for row in data["event_people"]:
        if "source_id" not in row:
            row["source_id"], row["locator"] = src[row["event_id"]]
    for row in data["image_events"]:
        if "source_id" not in row:
            row["source_id"], row["locator"] = src[row["event_id"]]


def build():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.executescript(SCHEMA)
    data = load_all()
    enrich_junctions(data)
    for table in TABLES:
        rows = data[table]
        if not rows:
            continue
        cols = list(rows[0].keys())
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (
            table, ", ".join(cols), ", ".join(":" + c for c in cols))
        conn.executemany(sql, rows)
    conn.commit()
    return conn, data


def verify(conn):
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    return fk, integrity


def export_records(conn):
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM v_events_full ORDER BY id")]
    path = os.path.join(ROOT, "records.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    return path


if __name__ == "__main__":
    conn, data = build()
    fk, integrity = verify(conn)
    counts = {t: conn.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
              for t in TABLES}
    total = sum(counts.values())
    path = export_records(conn)
    conn.close()

    print("history.db ->", DB)
    print("records.json ->", path)
    print("-" * 46)
    for t in TABLES:
        print("  %-14s %4d rows" % (t, counts[t]))
    print("  %-14s %4d rows  (challenge target: >= 200)" % ("TOTAL", total))
    print("-" * 46)
    print("integrity_check :", integrity)
    print("foreign_key_check:", "clean" if not fk else fk)
    sys.exit(1 if fk or integrity != "ok" else 0)
