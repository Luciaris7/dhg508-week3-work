# 课堂演示操作卡（5 分钟）

## 课前 3 分钟准备

```powershell
# 1. 打开项目目录
cd "C:\Users\28301\Desktop\dhg508 week3"

# 2. 确认 python 与数据库都在
python --version
Test-Path history.db

# 3. 空跑一遍，确认无报错（重要！）
python code/demo_run.py
```

若打印中出现 36 行、且第 4 幕有英文原文，即一切就绪。

## 演示流程（照着念）

### 第 1 幕 · 数据从哪来（约 1 分钟）
命令：
```powershell
python code/demo_run.py 1
```
说：
- "两份 1912 年公共领域原文，放在 `sources/raw/`，我一个字节都没改。"
- "抽出 36 行事实，每行带出处，存进 `history.db` 的 `events` 表。"
- 指 `source`、`note` 两列："出处与存疑都留在库里。"

### 第 2 幕 · 三个只有查库才答得出的问题（约 2 分钟）
命令：
```powershell
python code/demo_run.py 2
```
说：
- 问一卖点："救生艇总容量 **1,178 人**，船上 **2,201 人**——这个对照，通用知识给不出。"
- 问二卖点："Californian 只有 **1 名报务员且已睡**；看见 **8 枚火箭**仍未动。"
- 问三卖点："同一件事，官方记 **11:40**、Beesley 记 **11:45**；获救数 **711 / 712 / 705** 三个版本并存——我不替史料选，`note` 里照实转述。"

### 第 3 幕 · 反证：库外问题必须拒答（约 40 秒）
命令：
```powershell
python code/demo_run.py 3
```
说："问它 1985 年残骸发现——**0 行命中**。它只会答『这本卷宗里没有』，绝不用常识硬凑。"

### 第 4 幕 · 逐字回溯原文（约 1 分钟）
命令：
```powershell
python code/demo_run.py 4
```
说："库里第 24 行的出处指向原文第 3302-3308 行。**左边是库，右边是 1912 年原文**，逐字对得上。"

### 收尾（约 20 秒）
打开 `skills/mersey-clerk/SKILL.md`：
- frontmatter（何时触发）→ "卷宗里有什么"（数据库说明）→ "硬性规则"（只用库、无卷不答、存疑照转、带出处）→ "如何自证"。
- 收束句："**给它一本有出处的卷宗 + 一套不许越界的规矩，它说的每句话都能被拉回原始某一行。**"

## 一句话口诀

> 一跑（demo_run）二问（三个问题）三拒（1985）四对（原文）

## 意外兜底

| 情况 | 处理 |
|---|---|
| 命令报错 | 改跑 `python code/query_history_db.py` 打印全表，口述答案 |
| 中文乱码 | 先执行 `chcp 65001`，或改用 Windows Terminal |
| 网络不通 | 无需网络：原文已下载在 `sources/raw/`，全部本地 |
| 被问"是不是模型背的" | 立刻跑 `python code/verify_rows.py 24 25 34`，展示库行 ↔ 原文逐字对照 |
| 想看全部 36 行 | `python code/query_history_db.py` |
