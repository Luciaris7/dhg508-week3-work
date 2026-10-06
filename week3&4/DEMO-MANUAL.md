# 课堂演示使用手册（5 分钟）

泰坦尼克号（1912）关系型历史数据库 · The Mersey Clerk agent

---

## 0. 一句话讲清你做了什么

> 把两份 1912 年公共领域原文抽成 **7 张关系表、223 行**，
> 写成一个只会照卷宗说话、每句都能回溯到原文的「调查庭书记官」agent。

三个卖点：**关系型且可增长** · **每行有出处、引文自动核对** · **渐进式 skill，无卷不答**。

---

## 1. 课前 5 分钟准备

```powershell
cd "C:\Users\28301\Desktop\dhg508 week3"

python --version                 # 需 Python 3（标准库 sqlite3 即可，无需装依赖）
python code/build_db.py          # 应打印 7 表共 223 行，foreign_key_check: clean
python code/validate_db.py       # 应打印 All checks passed
python code/demo_run.py          # 空跑一遍确认无报错
```

- 中文乱码就先执行 `chcp 65001`，或改用 Windows Terminal。
- 全程**无需联网**：原文已下载在 `sources/raw/`。

**成功判据**（课前自检）：
- `build_db.py` 输出 `TOTAL 223 rows ... (challenge target: >= 200)`；
- `validate_db.py` 输出 `quotes checked against source: 87` 且 `All checks passed`；
- `demo_run.py` 第 4 幕最后一行是 `本行 quote 是否出现在原文: True`。

---

## 2. 命令总览（现场会用到）

| 命令 | 作用 |
|---|---|
| `python code/demo_run.py` | 跑完整 4 幕演示 |
| `python code/demo_run.py 1` | 只跑第 N 幕（1–4） |
| `python code/query_history_db.py` | 打印全表结构与行数，兜底用 |
| `python code/verify_sample.py` | 随机 20 行与原文对照 |
| `python code/verify_rows.py 24 25` | 指定行核对 |
| `python code/build_db.py` / `validate_db.py` | 重建 / 校验（课前已跑） |

---

## 3. 演示脚本（照着念，约 5 分钟）

### 第 1 幕 · 数据从哪来（约 1 分钟）

```powershell
python code/demo_run.py 1
```

**念**：
- "两份 1912 年公共领域原文，放在 `sources/raw/`，我一个字节都没改。"
- "抽成 **7 张关系表、223 行**：sources、places、people、events、event_people、images、image_events。"
- 指着表结构说："`source_id`、`locator`、`note` 每张表都有；`date`、`name` 都留了
  **original 原词 + conversion 转换说明**——规范化时原话不丢。"
- 指 `events` 的 `CHECK` 与 `PRAGMA foreign_keys`："这是有约束的真数据库，不是一张大表。"

### 第 2 幕 · 跨表问答（约 2 分钟）

```powershell
python code/demo_run.py 2
```

**问一**：Californian 号船长是谁？当晚做了什么？
- "人名在 `people`、事件在 `events`、出处联 `sources`——**三张表 JOIN** 出来。"
- "卖点是这些口供和行号：船长 **Stanley Lord**，报位 42°5'N 57°7'W 被法庭判为不准 [96]，
  见 8 枚火箭未施救 [25]。通用知识背不出这些行号。"

**问二**：救生艇容量够，为什么少救那么多人？
- "艇总容量 **1,178** 人 [5]，最终只救 **711/2,201**（32.30%）[27]；
  至少 8 艘未满载，原因写在 `note` 里 [26]。"
- "**我不替史料圆场**，冲突数字照实并列。"

**问三**：Californian 与泰坦尼克是什么关系？
- "**同属 IMM**（International Mercantile Marine Co.）[94]——这个关系是从库里查出来的。"

### 第 3 幕 · 反证：库外问题必须拒答（约 40 秒）

```powershell
python code/demo_run.py 3
```

**念**："问它 1985 年残骸发现——**全部 0 行命中**。它只会答『这本卷宗里没有』，
绝不用常识硬凑。这就是这个 agent 的底线。"

### 第 4 幕 · 逐字回溯 + 自动校对（约 1 分钟）

```powershell
python code/demo_run.py 4
```

**念**："库里第 24 行的出处指向原文 **L3302-3308**。左边是库，右边是 1912 年原文，逐字对得上。
最后一行 `本行 quote 是否出现在原文: True`——**引文可信是自动校验的**，不是我说了算。"

### 收尾（约 20 秒）· 展示渐进式 skill

```powershell
notepad skills\mersey-clerk\SKILL.md
```

**念**：
- frontmatter（何时触发）→ "卷宗是什么" → "硬性规则"（只用库、无卷不答、存疑照转、带出处）
  → "**需要时再读**"（细节拆到 `reference/` 三份，按需加载）→ "交接"（加数据交给 registrar）。
- 收束句："**一本有出处的卷宗 + 一套不许越界的规矩，它说的每句话都能被拉回原始某一行。**"

---

## 4. Corner cases（必须演的两个 + 加分两题）

| 类型 | 现场提问 | 预期回答 |
|---|---|---|
| **库外问题** | 泰坦尼克号残骸哪一年被发现？ | "这本卷宗里没有。卷宗只到 1912 年调查。" |
| **假前提** | 它有 17 道横向水密舱壁，对吧？ | "前提有误：船体 **15 道** [4]，双层底 **17 道分舱** [91]，是两套系统。" |
| 姓名陷阱 | 给我船长 Edward John Smith 的记录 | "卷宗无此名；卷上排印作 **Edward Charles Smith** [7]，note 已注明通行名，我不擅改。" |
| 要求编引文 | 引用船长撞冰山时的原话 | "卷宗未载船长原话，不能编。可引一副 Murdoch 的转述 [15][85]。" |

**现场即席提问**：直接用 opencode 触发 `mersey-clerk` skill 提问即可；
或手动查库证明：

```powershell
python code/verify_rows.py 24 25 94
```

---

## 5. 可能被问到的问题

**Q：怎么证明不是模型背的？**
A：跑 `python code/verify_sample.py 24 25 94`，展示库行与原文逐字对照；
再问一个库外问题（1985），它必然拒答。

**Q：数据库怎么加新材料？**
A：`skills/mersey-registrar/SKILL.md` + `research/how-to-grow-the-database.md`——
只需新建 `code/data/events_03_*.json` 再跑 `build_db.py`、`validate_db.py`，旧行不动。

**Q：规范化会不会丢原话？**
A：不会。日期/人名/地名都有 `*_original` 与 `*_conversion`；例：船长排印异名照原样保留并标存疑。

**Q：冲突数字怎么处理？**
A：照实并存、不裁决。例：船上人数 2,201 [9] vs 2,208 [33]；获救 711 [27] / 712 [23] / 705 [34]。
注意区分「口径不同」（712 救起、711 最终获救）与「史料冲突」。

---

## 6. 故障排除

| 情况 | 处理 |
|---|---|
| 中文乱码 | 先 `chcp 65001`，或用 Windows Terminal |
| 某命令报错 | 改跑 `python code/query_history_db.py` 打印全表，口述答案 |
| 数据库被改坏 | 重跑 `python code/build_db.py` 即从 JSON 重建 |
| 想看全部 97 行 | `python code/query_history_db.py` |
| 网络不通 | 无需网络，全部本地 |

---

## 7. 一页速查卡

```
课前：  python code/build_db.py   → 223 rows, clean
        python code/validate_db.py → All checks passed
演示：  python code/demo_run.py 1  → 7 表 / 有约束 / 原词+转换
        python code/demo_run.py 2  → 跨表三问（Californian / 救生艇 / IMM）
        python code/demo_run.py 3  → 1985 全 0 行，拒答
        python code/demo_run.py 4  → L3302-3308 逐字对照，quote True
收尾：  skills/mersey-clerk/SKILL.md → 渐进加载 + 交接 registrar
防身：  python code/verify_sample.py 24 25 94
```

**口诀**：一跑（build+validate）二问（跨表三问）三拒（1985）四对（quote 命中）。
