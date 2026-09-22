"""对指定 id 的行，打印数据库内容与原材料被引用处原文，供人工核对。"""

import os
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "history.db")

RAW = {
    "39415": os.path.join(
        ROOT, "sources", "raw",
        "british-inquiry-1912-loss-of-steamship-titanic.txt"),
    "6675": os.path.join(
        ROOT, "sources", "raw",
        "beesley-1912-loss-of-ss-titanic.txt"),
}


def original_lines(source):
    """从 source 字段解析出 Gutenberg 编号与行号范围，返回原文。"""
    book = re.search(r"#(39415|6675)", source)
    span = re.search(r"L(\d+)-(\d+)", source)
    if not book or not span:
        return None, None
    a, b = int(span.group(1)), int(span.group(2))
    path = RAW[book.group(1)]
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    return book.group(1), "".join(lines[a - 1:b]).rstrip()


def main(ids):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    for rid in ids:
        r = conn.execute("SELECT * FROM events WHERE id=?", (rid,)).fetchone()
        if r is None:
            print("id %s not found" % rid)
            continue
        book, text = original_lines(r["source"])
        print("=" * 90)
        print("[%d] date=%s  place=%s  people=%s" % (r["id"], r["date"], r["place"], r["people"]))
        print("event : " + r["event"])
        print("source: " + r["source"])
        if r["note"]:
            print("note  : " + r["note"])
        print("-" * 90)
        print("原始材料（Gutenberg #%s）:" % book)
        print(text if text else "(无法定位原文)")
    conn.close()


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [5, 15, 23, 34]
    main(ids)
