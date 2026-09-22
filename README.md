# 泰坦尼克号沉没（1912）小型历史数据库

来源 → 文本 → 数据 → 小库，一条完整链路；数据取材于公开的海事与司法原始材料。

## 文件

| 文件 | 是什么 |
|---|---|
| `markdown-guide.md` | Markdown 语法速查（作业第 1 项） |
| `sources/raw/beesley-1912-loss-of-ss-titanic.txt` | 一手材料：幸存者 Lawrence Beesley《The Loss of the S. S. Titanic》(1912)，Project Gutenberg #6675（公共领域） |
| `sources/raw/british-inquiry-1912-loss-of-steamship-titanic.txt` | 官方材料：英国沉船调查委员会报告《Loss of the Steamship "Titanic"》(1912)，Project Gutenberg #39415 |
| `records.json` | 从上述材料抽出的 36 条事实，每条带出处与备注 |
| `history.db` | SQLite 数据库，由 `code/build_history_db.py` 生成 |
| `code/build_history_db.py` | 建库脚本（Python 标准库 `sqlite3`） |
| `research/references.md` | 完整引用与检索信息 |

## 数据库结构

表 `events`，每行一个事实（schema 跟随材料，参照 `sources` 里的 extraction skill）：

| 列 | 含义 |
|---|---|
| `id` | 稳定行号，引用时用它 |
| `year` | 起始年份，便于排序 |
| `date` | 按原材料写法的日期 |
| `event` | 一句话事实 |
| `place` | 地点 |
| `people` | 人名，分号分隔 |
| `source` | 该行出处（材料 + 章节 + 原文行号） |
| `note` | 存疑、冲突、来源质量 |

## 怎么用

数据库就是一个 SQLite 文件，无需装工具：

```powershell
python code/build_history_db.py     # 重新生成 records.json 与 history.db
python code/query_history_db.py     # 抽查几行
```

```python
import sqlite3
conn = sqlite3.connect("history.db")
for row in conn.execute("SELECT id, date, event, source FROM events LIMIT 5"):
    print(row)
```

## 备注

- 数值冲突照实保留（如船上人数 2,201 vs 2,208），不替材料选一个，见各行的 `note`。
- 原始材料保持原样存放于 `sources/raw/`，未作改动。
