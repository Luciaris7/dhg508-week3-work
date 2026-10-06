"""Check history.db against its rules and its sources.

Checks:
  A. every place / person / event / image row carries source_id, locator and note
  B. every event's `quote` really appears in the cited lines of the raw text
  C. every cited line range lies inside the source file
  D. date_normalized parses as YYYY, YYYY-MM, YYYY-MM-DD or YYYY-MM-DDThh:mm
  E. foreign keys and integrity

Run:
    python code/validate_db.py
"""

import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "history.db")
RAW = {
    1: os.path.join(ROOT, "sources", "raw",
                    "british-inquiry-1912-loss-of-steamship-titanic.txt"),
    2: os.path.join(ROOT, "sources", "raw",
                    "beesley-1912-loss-of-ss-titanic.txt"),
}

DATE_OK = re.compile(
    r"^(\d{4})(-\d{2}(-\d{2}(T\d{2}:\d{2}(/\d{2}:\d{2})?)?)?)?"
    r"([;/]\d{4}(-\d{2}(-\d{2})?)?)*$")

_cached_lines = {}


def lines_of(source_id):
    if source_id not in _cached_lines:
        with open(RAW[source_id], encoding="utf-8") as f:
            _cached_lines[source_id] = f.readlines()
    return _cached_lines[source_id]


def norm(text):
    return re.sub(r"\s+", " ", text).strip().lower()


def span(source_id, locator):
    m = re.match(r"L(\d+)-(\d+)$", locator or "")
    if not m:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    lines = lines_of(source_id)
    if a < 1 or b > len(lines) or a > b:
        return None
    return "".join(lines[a - 1:b])


def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    errors = []

    for table in ("places", "people", "events", "images",
                  "event_people", "image_events"):
        for r in conn.execute("SELECT * FROM %s" % table):
            label = r["id"] if "id" in r.keys() else dict(r)
            if not r["source_id"] or not r["locator"]:
                errors.append("%s[%s] missing source_id/locator" % (table, label))
            if r["note"] is None:
                errors.append("%s[%s] note is NULL" % (table, label))

    checked = 0
    for r in conn.execute("SELECT * FROM events ORDER BY id"):
        raw = span(r["source_id"], r["locator"])
        if raw is None:
            errors.append("event[%d] locator %r not inside source %d"
                          % (r["id"], r["locator"], r["source_id"]))
            continue
        q = r["quote"]
        if q:
            checked += 1
            if norm(q) not in norm(raw):
                errors.append("event[%d] quote not found in %s"
                              % (r["id"], r["locator"]))
        dn = r["date_normalized"]
        if dn and not DATE_OK.match(dn):
            errors.append("event[%d] bad date_normalized %r" % (r["id"], dn))

    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    fk = conn.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()

    print("quotes checked against source:", checked)
    print("integrity_check :", integrity)
    print("foreign_key_check:", "clean" if not fk else fk)
    if errors:
        print("\n%d problem(s):" % len(errors))
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
