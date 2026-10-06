# 常用查询（reference/queries.md）

仅在需要写 SQL 时读本文件。全部用 Python 标准库 `sqlite3`，并跑真实查询。

应用里的连接是**只读**的（`file:...?mode=ro`），所以你只能写一条 `SELECT` / `WITH`；
写别的会被守卫拒掉、更会被 SQLite 自己拒掉。手工查库时也建议照做：

```python
import sqlite3
con = sqlite3.connect("file:/path/to/history.db?mode=ro", uri=True)
con.row_factory = sqlite3.Row
```

## 1. 关键词命中（只答库里的行）

```python
for r in con.execute(
    "SELECT id, date_normalized, event, source_id, locator "
    "FROM events WHERE event LIKE ? OR note LIKE ? ORDER BY id",
    ("%救生艇%", "%救生艇%"),
):
    print(r["id"], r["date_normalized"], r["event"], r["source_id"], r["locator"])
```

## 2. 跨表：带出处（文献 code + 行号）的完整回答

```python
for r in con.execute("""
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
for r in con.execute("""
    SELECT e.id, e.date_normalized, e.event, ep.role, s.code
    FROM event_people ep
    JOIN events e ON e.id = ep.event_id
    JOIN people p ON p.id = ep.person_id
    JOIN sources s ON s.id = e.source_id
    WHERE p.name_normalized = ? ORDER BY e.id
""", ("Lord, Stanley",)):
    print(f"[{r['id']}] {r['event']}  — {r['role']} ({r['code']})")
```

人名用**等号**配 `name_normalized`（「姓, 名」）；用 `LIKE '%Lord%'` 会把
`Mersey, Lord`、`Pirrie, Lord` 这些头衔也一起捞进来。

## 4. 按年份或时间范围

```python
for r in con.execute(
    "SELECT id, event FROM events "
    "WHERE date_normalized >= ? AND date_normalized < ? ORDER BY id",
    ("1912-04-15", "1912-04-16"),
):
    print(r["id"], r["event"])
```

## 5. 图片与其相关事件

```python
for r in con.execute("""
    SELECT i.id, i.caption, i.commons_url, ie.event_id
    FROM images i
    LEFT JOIN image_events ie ON ie.image_id = i.id
    WHERE i.caption LIKE ? OR i.note LIKE ? ORDER BY i.id
""", ("%救生艇%", "%救生艇%")):
    print(f"[img {r['id']}]", r["caption"], "相关事件", r["event_id"], r["commons_url"])
```

## 6. 存在性判断（决定「无卷不答」）

命中 0 行即答「这本卷宗里没有」。切勿用相似常识替代。
**先看卷宗的时间下限**，拒答时好说明理由：

```python
con.execute("SELECT MAX(date_normalized) FROM events").fetchone()[0]   # 1912-07-30
```

## 7. 万金油

多数问题直接查视图更快，它已经联好了出处：

```python
for r in con.execute(
    "SELECT id, date_normalized, event, source, locator, note "
    "FROM v_events_full WHERE event LIKE ? ORDER BY id", ("%冰山%",)
):
    print(f"[{r['id']}] {r['event']}  ({r['source']} {r['locator']})")
```
