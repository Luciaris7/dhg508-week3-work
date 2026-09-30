"""课堂演示一键脚本：原始材料 → 关系数据库 → agent 回答证据。

用法:
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
    1: os.path.join(ROOT, "sources", "raw",
                    "british-inquiry-1912-loss-of-steamship-titanic.txt"),
    2: os.path.join(ROOT, "sources", "raw",
                    "beesley-1912-loss-of-ss-titanic.txt"),
}
TABLES = ["sources", "places", "people", "events", "event_people", "images", "image_events"]


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


def original(source_id, locator):
    m = re.match(r"L(\d+)-(\d+)$", locator or "")
    if not m or source_id not in RAW:
        return None
    with open(RAW[source_id], encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[int(m.group(1)) - 1:int(m.group(2))]).rstrip()


def act1():
    banner("第 1 幕 · 数据从哪来（关系型，有约束）")
    print("原始材料（sources/raw/，未改动）:")
    for name in sorted(os.listdir(os.path.join(ROOT, "sources", "raw"))):
        p = os.path.join(ROOT, "sources", "raw", name)
        if os.path.isfile(p):
            print("  %-52s %6.1f KB" % (name, os.path.getsize(p) / 1024))
    print("\n数据库 history.db（7 表，外键开启）:")
    total = 0
    for t in TABLES:
        n = rows("SELECT COUNT(*) AS n FROM %s" % t)[0]["n"]
        total += n
        print("  %-14s %4d rows" % (t, n))
    print("  %-14s %4d rows" % ("TOTAL", total))
    print("\n表结构（以 events 为例）:")
    print(rows("SELECT sql FROM sqlite_master WHERE name='events'")[0][0])


def act2():
    banner("第 2 幕 · 跨表问答：只有查库才答得出")
    print("\n问一：Californian 号的船长是谁？当晚他做了什么？")
    for r in rows("""
        SELECT e.id, e.event, s.code, e.locator
        FROM event_people ep
        JOIN events e ON e.id = ep.event_id
        JOIN people p ON p.id = ep.person_id
        JOIN sources s ON s.id = e.source_id
        WHERE p.name_normalized LIKE 'Lord, Stanley%' ORDER BY e.id"""):
        print("  [%d] %s  (%s %s)" % (r["id"], r["event"], r["code"], r["locator"]))

    print("\n问二：为什么救生艇总容量够、却少救那么多人？")
    for r in rows("""
        SELECT id, event, source_id, locator FROM events
        WHERE id IN (5,26,27,57,58,59) ORDER BY id"""):
        print("  [%d] %s" % (r["id"], r["event"]))

    print("\n问三：Californian 号与泰坦尼克号是什么关系？")
    for r in rows("""
        SELECT e.id, e.event, s.code FROM events e
        JOIN sources s ON s.id = e.source_id
        WHERE e.id IN (24,94) ORDER BY e.id"""):
        print("  [%d] %s  (%s)" % (r["id"], r["event"], r["code"]))


def act3():
    banner("第 3 幕 · 反证：库外问题必须拒答")
    print("问：沉船残骸是哪一年被发现？（库中只到 1912 年）")
    for kw in ("%1985%", "%残骸%", "%wreck%", "%discovered%"):
        rs = rows("SELECT id FROM events WHERE event LIKE ?", (kw,))
        print("  查询 %-14s -> 命中 %d 行" % (kw, len(rs)))
    print("  => 全为 0 行。agent 应回答：『这本卷宗里没有。』")


def act4():
    banner("第 4 幕 · 逐字回溯原文（quote 自动核对）")
    r = rows("""SELECT e.*, s.code FROM events e
                JOIN sources s ON s.id=e.source_id WHERE e.id=24""")[0]
    print("数据库 [%d]: %s" % (r["id"], r["event"]))
    print("出处: %s, %s" % (r["code"], r["locator"]))
    print("-" * 78)
    print("来源 %s 原文:" % r["code"])
    print(original(r["source_id"], r["locator"]))
    print("-" * 78)
    print("本行 quote 是否出现在原文:", r["quote"] in original(r["source_id"], r["locator"]))


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
