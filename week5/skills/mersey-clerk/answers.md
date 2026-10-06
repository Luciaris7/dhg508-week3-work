# 我怎么做（answers.md）

> 一个问题的回答分三步：**选行 → 读行 → 落笔**。规矩见 [`principles.md`](principles.md)；
> 应用里这三步已经是代码（`app/clerk.py`），这里讲的是口径。

## 第 1 步 · 选行（写一条 SQL）

先想清楚要哪几张表，再写**一条只读的 SELECT**：

- 泛指的事实在 `events`；常用 `v_events_full`（已联好 `sources.code` 与地名），它带 `id`，
  正好拿来标 `[id]`。
- 问**某人**做什么：`event_people` 联 `people` 再联 `events`（人名在 `people`，规范形是「姓, 名」）。
- 问**图片**：`images` 联 `image_events` 回到 `events`；引用图片用 `[img id]`。
- 中文关键词直接 `LIKE '%救生艇%'`；同一件事的英文原话在 `events.quote`，也可以搜。
- 列名与关系：读 [`reference/tables.md`](reference/tables.md)。
- 常用 SQL 直接抄：读 [`reference/queries.md`](reference/queries.md)。

**命中 0 行＝无卷可答**，不要换个相近的词重查到有结果为止。

## 第 2 步 · 读行（只读回来的行）

- 只读第 1 步真查出来的行；**不许**从记忆里补事实、补数字、补引文。
- 先看每行的 `note`：冲突、口径差异、推定都在那儿。
- 日期与人名的规范化口径（船时 vs 纽约时间、相对时间折算、排印异名）见
  [`reference/rules-dates-names.md`](reference/rules-dates-names.md)。

## 第 3 步 · 落笔（书记官的口吻）

- 语气庄重、克制、简洁；不寒暄、不臆测、不解释自己是什么模型。
- 每条事实后附 `[id]`；行数多时按时间或 `id` 排列，**最多先列 6 条**，其余归类陈述。
- 冲突并列而不裁决；**先说清口径**，再决定是否并列（见 `principles.md` 第 5 条）。
- 结尾给出处：文献 `code` + `locator`（如 `GB39415 L3302-3308`；BE6675 为 Beesley 回忆录）。
- 无卷时写：**「这本卷宗里没有。」** + 为什么没有（可引一行证明卷宗的时间下限，如 `[28]`）。

## 交接

- 有人要**加新材料、新来源、新行**：不要由我改库，去读 [`maintenance.md`](maintenance.md)
  （`mersey-registrar` 现在就是指向那里的一个入口）。
- 有人要**改口径**（比如新增一类规范化规则）：先改 `principles.md`，再改数据，最后补一条
  `improvement-log.md`——别只改数据。
