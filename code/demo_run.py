"""课堂演示一键脚本：从原始材料 → 数据库 → agent 回答证据。

用法：
    python code/demo_run.py            # 跑全程
    python code/demo_run.py 1          # 只跑第 1 幕
"""

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


def banner(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def rows(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    out = list(conn.execute(sql, args))
    conn.close()
    return out


def print_rows(rs):
    for r in rs:
        print("  [%d] %s" % (r["id"], r["event"]))
        print("      出处 " + r["source"])
        if r["note"]:
            print("      备注 " + r["note"])


def original(source):
    book = re.search(r"#(39415|6675)", source)
    span = re.search(r"L(\d+)-(\d+)", source)
    if not book or not span:
        return None
    with open(RAW[book.group(1)], encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[int(span.group(1)) - 1:int(span.group(2))]).rstrip()


def act1():
    banner("第 1 幕 · 数据从哪来")
    print("原始材料（sources/raw/，未改动）:")
    raw_dir = os.path.join(ROOT, "sources", "raw")
    for name in sorted(os.listdir(raw_dir)):
        p = os.path.join(raw_dir, name)
        if os.path.isfile(p):
            print("  %-52s %6.1f KB" % (name, os.path.getsize(p) / 1024))
    print("\n中间产物与数据库:")
    for rel in ("records.json", "history.db"):
        p = os.path.join(ROOT, rel)
        print("  %-52s %6.1f KB" % (rel, os.path.getsize(p) / 1024))
    conn = sqlite3.connect(DB)
    n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    schema = conn.execute(
        "SELECT sql FROM sqlite_master WHERE name='events'").fetchone()[0]
    conn.close()
    print("\nevents 表（共 %d 行）:" % n)
    print(schema)


def act2():
    banner("第 2 幕 · 只有查库才答得出的三个问题")
    qs = [
        ("问一：救生艇一共能载多少人？够不够全船用？",
         "SELECT * FROM events WHERE event LIKE '%救生艇%' ORDER BY id"),
        ("问二：Californian 号为什么没来救援？",
         "SELECT * FROM events WHERE event LIKE '%Californian%' "
         "OR people LIKE '%Stanley Lord%' ORDER BY id"),
        ("问三：Beesley 与官方报告在时间和人数上有何出入？",
         "SELECT * FROM events WHERE id IN (15,23,27,31,33,34) ORDER BY id"),
    ]
    for title, sql in qs:
        print("\n--- " + title)
        print_rows(rows(sql))


def act3():
    banner("第 3 幕 · 反证：库外问题必须拒答")
    print("问：沉船残骸是哪一年被发现？（库中只到 1912 年）")
    for kw in ("%1985%", "%残骸%", "%发现%"):
        rs = rows("SELECT * FROM events WHERE event LIKE ?", (kw,))
        print("  查询 %-8s -> 命中 %d 行" % (kw, len(rs)))
    print("  => 0 行。agent 应回答：『这本卷宗里没有。』")


def act4():
    banner("第 4 幕 · 逐字回溯原文")
    r = rows("SELECT * FROM events WHERE id=24")[0]
    print("数据库 [%d]: %s" % (r["id"], r["event"]))
    print("出处: " + r["source"])
    print("-" * 78)
    print("Gutenberg #39415 原文:")
    print(original(r["source"]))


ACTS = {"1": act1, "2": act2, "3": act3, "4": act4}


def main(argv):
    which = argv or list("1234")
    for a in which:
        ACTS.get(a, lambda: None)()
    print("\n" + "=" * 78)
    print("演示结束。")
    print("=" * 78)


if __name__ == "__main__":
    main(sys.argv[1:])
