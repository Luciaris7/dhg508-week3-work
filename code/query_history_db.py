import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "history.db")

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

print("== schema ==")
for row in conn.execute("SELECT sql FROM sqlite_master WHERE type='table'"):
    print(row[0])

total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
print("\n== %d rows in events ==" % total)
print("%-3s %-8s %-26s %-7s %s" % ("id", "year", "date", "people", "event"))
print("-" * 100)
for r in conn.execute("SELECT * FROM events ORDER BY id"):
    people = (r["people"] or "")[:24]
    event = r["event"]
    print("%-3d %-8s %-26s %-7s %s" % (r["id"], r["year"], r["date"], people, event))

print("\n== 出处分布 ==")
for src, n in conn.execute(
    "SELECT CASE WHEN source LIKE '%#39415%' THEN 'British Inquiry (#39415)' "
    "WHEN source LIKE '%#6675%' THEN 'Beesley (#6675)' ELSE 'other' END AS s, "
    "COUNT(*) FROM events GROUP BY s"
):
    print("  %-28s %d" % (src, n))

conn.close()
