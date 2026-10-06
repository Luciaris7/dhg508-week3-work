# 卷宗结构（reference/tables.md）

仅在需要知道某张表有哪些列时读本文件。行数为 Week 3 建库时的 223 行。

## sources（原始文献，3 行）
`id`、`code`（GB39415 / BE6675 / COMMONS）、`title`、`author`、`year`、
`publisher`、`gutenberg_id`、`url`、`local_path`、`note`。
引用「出处」时用 `code` + `events.locator`。

## places（地名，17 行）
`id`、`name_normalized`、`name_original`、`conversion`、`kind`、
`lat`、`lon`、`source_id`、`locator`、`note`。

## people（人物，26 行）
`id`、`name_normalized`、`name_original`、`conversion`、`role`、
`source_id`、`locator`、`note`。
`name_normalized` 统一为「姓, 名」，例如 `Lord, Stanley`、`Smith (Captain, as printed: Edward Charles)`。
注意 `Lord` 既是姓也是贵族头衔：`Mersey, Lord` 与 `Pirrie, Lord` 是头衔，不是姓。

## events（事实正文，97 行）
`id`、`year`、`date_normalized`、`date_original`、`date_conversion`、
`event`、`place_id → places.id`、`source_id → sources.id`、`locator`、
`quote`（可在原文逐字命中的引文）、`note`。
回答的事实一律以本表为准。`event` 是中文摘述，`quote` 是英文原句。

## event_people（事件—人物，61 行）
`event_id → events.id`、`person_id → people.id`、`role`、`source_id`、`locator`、`note`。
问「某人做了什么」时把 events 与 people 连起来查。
`source_id`/`locator` 由构建脚本从所属事件继承（关系的出处与事件同源）。

## images（图片登记，6 行）
`id`、`file`（本地 `sources/raw/images/`）、`caption`、`author`、
`date_original`、`date_normalized`、`date_conversion`、`license`、`commons_url`、
`source_id → sources.id`、`locator`、`note`。引用图片用 `[img id]`。

## image_events（图片—事件，13 行）
`image_id → images.id`、`event_id → events.id`、`source_id`、`locator`、`note`。

## 视图 v_events_full
把 `events` 与 `sources.code`、`places.name_normalized` 连成一张宽表：
`id`、`year`、`date_normalized`、`event`、`place`、`source`、`source_title`、`locator`、`note`。
回答问题时**首选这张视图**——它已经带好了 `[id]` 需要的行号与出处。
它**不含** `quote`、`date_original`、`date_conversion`；需要引文原文时回到 `events` 取。

## 外键与约束
共 **9 条**外键：`places.source_id`、`people.source_id`、`events.place_id`、`events.source_id`、
`event_people.event_id`、`event_people.person_id`、`images.source_id`、`image_events.image_id`、
`image_events.event_id`；`PRAGMA foreign_keys=ON`，`code/validate_db.py` 会检查。
（Week 3 的同名文件写作「7 条」，与本项目 `research/database-design.md` 的「9 条」不一致；
Week 5 已核对外键清单，此处更正为 9 条。）
