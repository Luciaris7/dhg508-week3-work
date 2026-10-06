"""对指定 id 的行，打印数据库内容与原材料被引用处原文，供人工核对。

用法:
    python code/verify_rows.py            # 默认核对几个关键行
    python code/verify_rows.py 5 15 23 34
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


def original(source_id, locator):
    m = re.match(r"L(\d+)-(\d+)$", locator or "")
    if not m or source_id not in RAW:
        return None
    a, b = int(m.group(1)), int(m.group(2))
    with open(RAW[source_id], encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[a - 1:b]).rstrip()


def main(ids):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    for rid in ids:
        r = conn.execute("""
            SELECT e.*, s.code AS source_code, s.title AS source_title,
                   p.name_normalized AS place
            FROM events e
            JOIN sources s ON s.id = e.source_id
            LEFT JOIN places p ON p.id = e.place_id
            WHERE e.id = ?""", (rid,)).fetchone()
        if r is None:
            print("id %s not found" % rid)
            continue
        print("=" * 90)
        print("[%d] date=%s  place=%s  people=%s"
              % (r["id"], r["date_original"], r["place"] or "-",
                 ", ".join(x["name_normalized"] for x in conn.execute(
                     "SELECT p.name_normalized FROM event_people ep "
                     "JOIN people p ON p.id=ep.person_id WHERE ep.event_id=?",
                     (rid,))) or "-"))
        print("event : " + r["event"])
        print("source: %s, %s" % (r["source_code"], r["locator"]))
        print("quote : " + (r["quote"] or "(无)"))
        if r["note"]:
            print("note  : " + r["note"])
        print("-" * 90)
        text = original(r["source_id"], r["locator"])
        print("原始材料（%s）:" % r["source_code"])
        print(text if text else "(非纯文本行范围，见 locator)")
    conn.close()


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [5, 15, 23, 34]
    main(ids)
