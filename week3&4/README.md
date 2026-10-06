# 泰坦尼克号沉没（1912）关系型历史数据库与书记官 agent

来源 → 文本 → 数据 → 关系库 → 渐进式 skill，一条完整链路；数据取材于公开的海事与司法原始材料。

## 文件

| 文件 | 是什么 |
|---|---|
| `sources/raw/british-inquiry-1912-loss-of-steamship-titanic.txt` | 官方一手材料：英国沉船调查庭报告 (1912)，Project Gutenberg #39415 |
| `sources/raw/beesley-1912-loss-of-ss-titanic.txt` | 幸存者 Lawrence Beesley《The Loss of the S. S. Titanic》(1912)，Gutenberg #6675 |
| `sources/raw/images/` | 6 张公共领域史实图片 |
| `code/data/*.json` | 抽取出的数据（sources / places / people / events / event_people / images / image_events） |
| `code/build_db.py` | 建库脚本（标准库 `sqlite3`，含外键与 CHECK 约束） |
| `code/validate_db.py` | 校验：引文回原文、外键、完整性、日期格式 |
| `code/verify_sample.py` | 随机抽行与原文对照 |
| `code/query_history_db.py` / `demo_run.py` | 查库与课堂演示 |
| `history.db` | 生成的 SQLite 数据库 |
| `skills/mersey-clerk/` | 作答 skill（`SKILL.md` + `reference/` 按需加载） |
| `skills/mersey-registrar/` | 加数据 skill（与 clerk 交接） |
| `research/` | 设计、增长步骤、抽查、评分标准、测试题 |
| `improvement-log.md` / `questions.md` | 改进日志与未决问题 |

## 数据库（7 表，223 行）

关系型，9 条外键，`PRAGMA foreign_keys=ON`：

```
sources ─┬─< places ──────< events >────── people ──< event_people
         ├─< people                  (place_id)        (event_id,person_id)
         ├─< events                  source_id
         └─< images ──< image_events >── events
```

- 每张表都有 `source_id + locator`（出处）与 `note`（存疑）。
- 日期/人名/地名都保留 `*_original` 原词，并有 `*_conversion` 记转换规则。
- `events.quote` 存一段能在原文逐字命中的引文，自动校验。
- 详见 `research/database-design.md`。

## 怎么用

```powershell
python code/build_db.py         # 从 code/data/*.json 重建 history.db
python code/validate_db.py      # 校验引文与外键
python code/verify_sample.py    # 随机 20 行对照原文
python code/demo_run.py         # 课堂演示（4 幕）
```

```python
import sqlite3
conn = sqlite3.connect("history.db")
conn.row_factory = sqlite3.Row
for r in conn.execute("SELECT * FROM v_events_full WHERE event LIKE '%救生艇%'"):
    print(r["id"], r["date_normalized"], r["event"], r["source"], r["locator"])
```

## 智能体

- **mersey-clerk**：以 1912 年调查庭书记官口吻作答，只用库中的行，逐条标注 `[id]` 与出处；
  库中没有就说「这本卷宗里没有」。`SKILL.md` 很短，细节在 `reference/` 里按需加载。
- **mersey-registrar**：负责把新材料追加进库并重建校验，然后把控制权交回 clerk。

## 备注

- 数值冲突照实并存（如船上人数 2,201 vs 2,208；获救 711 / 712 / 705），见各行 `note`。
- 原始材料保持原样存放于 `sources/raw/`，未作改动。
- 加料步骤见 `research/how-to-grow-the-database.md`。
