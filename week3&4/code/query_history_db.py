"""Print the schema, table sizes and a joined sample of history.db."""

import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "history.db")

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("== tables ==")
for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"):
    print("  " + row[0])

print("\n== row counts ==")
tables = ["sources", "places", "people", "events", "event_people", "images", "image_events"]
total = 0
for t in tables:
    n = conn.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
    total += n
    print("  %-14s %4d" % (t, n))
print("  %-14s %4d" % ("TOTAL", total))

print("\n== v_events_full (first 15) ==")
print("%-3s %-6s %-10s %-12s %s" % ("id", "year", "date", "source", "event"))
print("-" * 100)
for r in conn.execute("SELECT * FROM v_events_full ORDER BY id LIMIT 15"):
    print("%-3d %-6s %-10s %-12s %s"
          % (r["id"], r["year"], r["date_normalized"] or "", r["source"], r["event"]))

print("\n== 按来源统计 events ==")
for r in conn.execute(
        "SELECT s.code, COUNT(*) n FROM events e JOIN sources s ON s.id=e.source_id "
        "GROUP BY s.code ORDER BY n DESC"):
    print("  %-10s %d" % (r["code"], r["n"]))

conn.close()
