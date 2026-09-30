# 常用查询（reference/queries.md）

仅在需要写 SQL 时读本文件。全部用 Python 标准库 `sqlite3`，并跑真实查询。

```python
import sqlite3
conn = sqlite3.connect("history.db")
conn.row_factory = sqlite3.Row
```

## 1. 关键词命中（只答库里的行）

```python
for r in conn.execute(
    "SELECT id, date_normalized, event, source_id, locator "
    "FROM events WHERE event LIKE ? OR note LIKE ? ORDER BY id",
    ("%救生艇%", "%救生艇%"),
):
    print(r["id"], r["date_normalized"], r["event"], r["source_id"], r["locator"])
```

## 2. 跨表：带出处（文献 code + 行号）的完整回答

```python
for r in conn.execute("""
    SELECT e.id, e.date_normalized, e.event, e.locator,
           s.code AS src, p.name_normalized AS place
    FROM events e
    JOIN sources s ON s.id = e.source_id
    LEFT JOIN places p ON p.id = e.place_id
    WHERE e.event LIKE ? ORDER BY e.id
""", ("%Californian%",)):
    print(f"[{r['id']}] {r['event']}  ({r['src']} {r['locator']})")
```

## 3. 跨三表：某人牵涉的事件

```python
for r in conn.execute("""
    SELECT e.id, e.event, ep.role
    FROM event_people ep
    JOIN events e ON e.id = ep.event_id
    JOIN people p ON p.id = ep.person_id
    WHERE p.name_normalized LIKE ? ORDER BY e.id
""", ("%Rostron%",)):
    print(f"[{r['id']}] {r['event']}  — {r['role']}")
```

## 4. 按年份或时间范围

```python
for r in conn.execute(
    "SELECT id, event FROM events "
    "WHERE date_normalized >= ? AND date_normalized < ? ORDER BY id",
    ("1912-04-15", "1912-04-16"),
):
    print(r["id"], r["event"])
```

## 5. 图片与其相关事件

```python
for r in conn.execute("""
    SELECT i.id, i.caption, i.commons_url, ie.event_id
    FROM images i
    LEFT JOIN image_events ie ON ie.image_id = i.id
    WHERE i.caption LIKE ? OR i.note LIKE ? ORDER BY i.id
""", ("%救生艇%", "%救生艇%")):
    print(f"[img {r['id']}]", r["caption"], "相关事件", r["event_id"], r["commons_url"])
```

## 6. 存在性判断（决定「无卷不答」）

命中 0 行即答「这本卷宗里没有」。切勿用相似常识替代。
