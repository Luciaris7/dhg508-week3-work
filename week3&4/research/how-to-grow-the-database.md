# 如何给数据库加料（可重复的步骤）

> Week 4 要求：加新材料＝把同一套步骤再跑一遍，且不破坏旧行。

## 0. 原则

- 只**追加**，不原地改写旧行；改行必须留下原因（见 `improvement-log.md`）。
- 每行都要有 `source_id + locator`，不确定处写 `note`。
- 新来源放 `sources/raw/`，**不改动原文**。

## 1. 登记新来源

在 `code/data/sources.json` 追加一条：

```json
{"id": 4, "code": "USINQ", "title": "...", "author": "...", "year": 1912,
 "publisher": "...", "gutenberg_id": null, "url": "...",
 "local_path": "sources/raw/xxx.txt", "note": ""}
```

## 2. 抽事实为行

新建 `code/data/events_03_<来源>.json`（文件名 `events_` 前缀会被自动合并），每条：

- `id`：取现有最大 id + 1，**不要复用旧 id**；
- `date_original` / `date_normalized` / `date_conversion`：见规范化规则；
- `place_id` / `source_id`：指向已有行；没有的地名先加进 `places.json`；
- `locator`：原文行号 `L123-145` 或文件页；
- `quote`：一段能在 `locator` 行段内逐字命中的英文引文（用于自动核对）；
- `note`：存疑、冲突、口径差异。

其他表同理：新人物加到 `people.json`，事件—人物关系加到 `event_people.json`，
图片加到 `images.json` 与 `image_events.json`。

## 3. 重建并校验

```powershell
python code/build_db.py        # 读全部 data/*.json，重建 history.db，打印各表行数
python code/validate_db.py     # 引文回原文核对 + 外键 + 完整性 + 日期格式
```

- `build_db.py` 用 `PRAGMA foreign_keys=ON`，任何悬空外键会当场报错。
- `validate_db.py` 会逐条检查 `quote` 是否真的出现在所引行段；任一失败即非零退出。

## 4. 定期抽查

```powershell
python code/verify_sample.py          # 20 行随机对照原文
python code/verify_sample.py 5 42     # 指定 id 定点核对
```

发现问题按「现象 / 原因 / 修法」记入 `research/verification.md`，
若改动已入库的数据，再记入 `improvement-log.md`。

## 5. 提交

只提交小而耐久的文件（数据 JSON、脚本、文档）。大文件、密钥、实时数据库不入 Git。
