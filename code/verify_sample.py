"""Challenge 2: compare N random database rows with the original text.

Usage:
    python code/verify_sample.py          # 20 random rows, seed 1912
    python code/verify_sample.py 20 7     # 20 rows, seed 7
    python code/verify_sample.py 5 15 21  # specific event ids
"""

import os
import random
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


def original(source_id, locator):
    m = re.match(r"L(\d+)-(\d+)$", locator or "")
    if not m or source_id not in RAW:
        return "(非文本行范围，见 locator)"
    a, b = int(m.group(1)), int(m.group(2))
    with open(RAW[source_id], encoding="utf-8") as f:
        lines = f.readlines()
    if a < 1 or b > len(lines):
        return "(行号越界)"
    return "".join(lines[a - 1:b]).rstrip()


def main(argv):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    ids = [int(x) for x in argv]
    if len(argv) >= 1 and len(argv[0]) <= 4 and len(argv) == 2 and argv[0].isdigit():
        n, seed = int(argv[0]), int(argv[1])
        all_ids = [r[0] for r in conn.execute("SELECT id FROM events")]
        ids = sorted(random.Random(seed).sample(all_ids, n))
    elif not ids:
        all_ids = [r[0] for r in conn.execute("SELECT id FROM events")]
        ids = sorted(random.Random(1912).sample(all_ids, 20))

    for rid in ids:
        r = conn.execute("""
            SELECT e.*, s.code AS source_code, p.name_normalized AS place
            FROM events e
            JOIN sources s ON s.id = e.source_id
            LEFT JOIN places p ON p.id = e.place_id
            WHERE e.id = ?""", (rid,)).fetchone()
        print("=" * 92)
        print("[%d] %s | %s | 出处 %s %s"
              % (r["id"], r["date_original"], r["place"] or "-",
                 r["source_code"], r["locator"]))
        print("DB   :", r["event"])
        print("quote:", r["quote"] or "(无)")
        print("note :", r["note"] or "(无)")
        print("-" * 92)
        print(original(r["source_id"], r["locator"]))
    conn.close()


if __name__ == "__main__":
    main(sys.argv[1:])
