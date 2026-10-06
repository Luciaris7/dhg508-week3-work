"""Read-only access to the Mersey archive (history.db), plus the SQL guard.

One job: hand out rows. Nothing in this file writes, and nothing calls a model.

The archive is Week 3's database and is opened with SQLite's own read-only mode,
so the app cannot damage it even if the guard below were bypassed:

    layer 1  the statement must start with SELECT or WITH, and be a single statement
    layer 2  no data-changing keyword anywhere in the statement
    layer 3  the connection is opened as file:...?mode=ro (SQLite refuses writes)

Rows are read with fetchmany(), so the SQL text is never rewritten to add a LIMIT.
"""

import os
import re
import sqlite3
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
# Where Week 3's database may live, relative to week5/app/. The first hit wins,
# so the archive is still found after the Week 3/4 coursework was moved into a
# subfolder ("week3&4/"), and in the older flat layout too.
DB_CANDIDATES = (
    HERE.parent / "history.db",                       # week5/history.db
    HERE.parent.parent / "week3&4" / "history.db",    # <root>/week3&4/history.db
    HERE.parent.parent / "history.db",                # <root>/history.db (flat layout)
)
# Kept for compatibility: the first candidate, used when nothing is found.
DEFAULT_DB = DB_CANDIDATES[0]


def _default_db() -> Path:
    """First existing candidate, else the preferred path (so errors name a real path)."""
    for candidate in DB_CANDIDATES:
        if candidate.is_file():
            return candidate
    return DEFAULT_DB

MAX_ROWS = int(os.environ.get("WEEK5_MAX_ROWS", "60"))

SELECT_LIKE = re.compile(r"^\s*(?:SELECT|WITH)\b", re.IGNORECASE)
FORBIDDEN = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|VACUUM|REINDEX|TRIGGER|PRAGMA)\b"
    r"|\bREPLACE\s+INTO\b",
    re.IGNORECASE,
)


class ArchiveError(Exception):
    """The archive could not be opened or read."""


class UnsafeQuery(ArchiveError):
    """The model (or a human) handed us SQL we refuse to run."""


def db_path() -> Path:
    return Path(os.environ.get("WEEK5_DB") or _default_db()).expanduser().resolve()


def connect(path=None) -> sqlite3.Connection:
    """Open the archive read-only. SQLite enforces the read-only part."""
    p = Path(path) if path else db_path()
    if not p.is_file():
        raise ArchiveError(
            "archive not found: %s  (looked for Week 3's history.db; "
            "set WEEK5_DB to point elsewhere, or run: python code/build_db.py)" % p
        )
    con = sqlite3.connect("file:%s?mode=ro" % quote(p.as_posix()), uri=True)
    con.row_factory = sqlite3.Row
    return con


def guard(sql: str, max_rows: int = None) -> str:
    """Return the SQL if it is a single read-only statement, else raise UnsafeQuery."""
    text = (sql or "").strip()
    if not text:
        raise UnsafeQuery("the model returned no SQL")
    if text.endswith(";"):
        text = text[:-1].rstrip()
    if ";" in text:
        raise UnsafeQuery("more than one statement is not allowed")
    if not SELECT_LIKE.match(text):
        raise UnsafeQuery("only a single SELECT / WITH statement is allowed")
    hit = FORBIDDEN.search(text)
    if hit:
        raise UnsafeQuery("refusing SQL containing %r" % hit.group(0))
    return text


def run(sql: str, path=None, max_rows: int = None) -> dict:
    """Guard the SQL, run it read-only, and return columns + rows."""
    statement = guard(sql, max_rows)
    limit = max_rows or MAX_ROWS
    con = connect(path)
    try:
        cursor = con.execute(statement)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows = [dict(r) for r in cursor.fetchmany(limit)]
    except sqlite3.Error as exc:
        raise ArchiveError("SQLite refused the query: %s" % exc) from exc
    finally:
        con.close()
    return {"sql": statement, "columns": columns, "rows": rows,
            "returned": len(rows), "truncated": len(rows) == limit}


def counts(path=None) -> dict:
    tables = ["sources", "places", "people", "events",
              "event_people", "images", "image_events"]
    con = connect(path)
    try:
        out = {t: con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0] for t in tables}
    finally:
        con.close()
    out["total"] = sum(out.values())
    return out


def schema_text(path=None) -> str:
    """The CREATE statements, so the model knows the real columns."""
    con = connect(path)
    try:
        rows = con.execute(
            "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    finally:
        con.close()
    return "\n\n".join(r[0].strip() for r in rows)


def catalogue(head=70, path=None) -> list:
    """A bounded index of the archive: id, date, source, and the first `head`
    characters of each fact.

    The model gets this to know what vocabulary exists and which ids look
    relevant. It is deliberately a *truncated index*: the full text of a row
    reaches the model only as the result of a real SQL query.
    """
    con = connect(path)
    try:
        rows = con.execute(
            "SELECT id, date_normalized, source, event FROM v_events_full ORDER BY id"
        ).fetchall()
    finally:
        con.close()
    out = []
    for r in rows:
        text = (r["event"] or "").replace("\n", " ")
        out.append({
            "id": r["id"],
            "date": r["date_normalized"] or "",
            "source": r["source"],
            "head": text[:head] + ("…" if len(text) > head else ""),
        })
    return out


def sample_columns(path=None) -> list:
    """Column names of the two tables a question usually needs."""
    con = connect(path)
    try:
        cols = {}
        for table in ("v_events_full", "events", "people", "event_people",
                      "images", "image_events", "places", "sources"):
            cols[table] = [r[1] for r in con.execute("PRAGMA table_info(%s)" % table)]
    finally:
        con.close()
    return cols
