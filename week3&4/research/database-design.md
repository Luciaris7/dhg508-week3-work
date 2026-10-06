# 数据库设计（history.db）

> 目标（Week 4 挑战 1）：关系型、有约束、可增长。

## 表与关系

```
sources ─┬─< places ──────< events >────── people ──< event_people
         ├─< people                  (place_id)        (event_id,person_id)
         ├─< events                  source_id
         └─< images ──< image_events >── events
```

| 表 | 行数 | 说明 |
|---|---|---|
| `sources` | 3 | 两份原始文献 + Wikimedia Commons 图库 |
| `places` | 17 | 地名，含经纬度与『原文 → 规范名』转换说明 |
| `people` | 26 | 人物，含原名、规范名、转换规则、职衔 |
| `events` | 97 | 事实行，含年份、双份日期、引文、出处 |
| `event_people` | 61 | 事件与人物多对多（谁在场、做什么） |
| `images` | 6 | 公共领域图片登记 |
| `image_events` | 13 | 图片与事件多对多 |
| **合计** | **223** | 超过 200 行 |

**外键（9 条）**：`places.source_id`、`people.source_id`、`events.place_id`、`events.source_id`、
`event_people.event_id`、`event_people.person_id`、`images.source_id`、`image_events.image_id`、
`image_events.event_id`。`PRAGMA foreign_keys=ON`，构建时校验通过。

## 每行都有出处与备注

**每张表**都有 `source_id`（哪份文献）与 `locator`（文献内位置，如 `L3220-3237`、Commons 文件页），
并有 `note` 列记录存疑：

- `sources` 行本身就是文献，其 `code` + `local_path` 即出处，`note` 说明材料性质；
- `event_people`、`image_events` 两个多对多表也带 `source_id`/`locator`：由构建脚本从所属
  事件自动继承（关系的出处与事件同源），不会出现无出处的行；
- `events.quote` 存一段可在原文逐字命中的引文，由 `validate_db.py` 自动核对。

## 规范化：原词与转换并列

- 日期：`date_original`（照原文）→ `date_normalized`（YYYY-MM-DD / ISO），
  `date_conversion` 写明规则（月名转数字、a.m./p.m. 转 24 小时、相对时间如何折算）。
- 人名：`name_original` 照原文 → `name_normalized` 统一为「姓, 名」，
  `conversion` 写明规则，异名/存疑写进 `note`。
- 地名：`name_original` → `name_normalized`，并记经纬度与转换说明。

## 设计取舍

- **数值冲突保留**：官方 2,201 与 Beesley 2,208 并存，各带出处，不替史料裁决。
- **两套「舱数」不混**：船体 15 道水密舱壁（`events[4]`）与双层底 17 道分舱（`events[91]`）
  是不同系统，note 中已说明。
- **视图 `v_events_full`**：把 events 与 sources、places 连成一张宽表，方便回答与导出
  `records.json`。
