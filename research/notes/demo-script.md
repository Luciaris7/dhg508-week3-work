# 课堂演示操作卡（5 分钟）

## 课前 3 分钟准备

```powershell
cd "C:\Users\28301\Desktop\dhg508 week3"
python --version
Test-Path history.db
python code/build_db.py        # 确认 223 行、外键 clean
python code/validate_db.py     # 确认全部通过
python code/demo_run.py        # 空跑一遍，确认无报错
```

## 演示流程（照着念）

### 第 1 幕 · 数据从哪来（约 1 分钟）
```powershell
python code/demo_run.py 1
```
说：
- "两份 1912 年公共领域原文，放在 `sources/raw/`，一个字节都没改。"
- "抽成 7 张关系表、共 **223 行**：资料源、地名、人物、事件、事件-人物、图片、图片-事件。"
- "每张表都有出处列和存疑列；`date`/`name` 都留了 original 原词和 conversion 转换说明。"

### 第 2 幕 · 跨表问答（约 2 分钟）
```powershell
python code/demo_run.py 2
```
说：
- 问一卖点："Californian 船长 **Stanley Lord** 是谁、当晚做了什么——人名在 `people`、
  事件在 `events`、出处联 `sources`，**三张表 JOIN 出来**，通用知识给不出这些行号和口供。"
- 问二卖点："艇总容量 **1,178** 人，却只救 **711** 人；原因写在 `note` 里，不替史料圆场。"
- 问三卖点："Californian 与泰坦尼克**同属 IMM**——这个关系是库里的，不是背的。"

### 第 3 幕 · 反证：库外问题必须拒答（约 40 秒）
```powershell
python code/demo_run.py 3
```
说："问它 1985 年残骸发现——**全部 0 行命中**。它只会答『这本卷宗里没有』，绝不用常识硬凑。"

### 第 4 幕 · 逐字回溯 + 自动校对（约 1 分钟）
```powershell
python code/demo_run.py 4
```
说："库里第 24 行的出处指向原文 **L3302-3308**。左边是库，右边是 1912 年原文，
最后一行显示本行的 `quote` **逐字命中原文：True**——引文可信是自动校验的。"

### 收尾（约 20 秒）
打开 `skills/mersey-clerk/SKILL.md`：
- frontmatter（何时触发）→ "卷宗是什么"（数据库）→ "硬性规则"（只用库、无卷不答、存疑照转、带出处）
  → "需要时再读"（`reference/` 三份按需加载）→ "交接"（加数据交给 `mersey-registrar`）。
- 收束句："**一本有出处的卷宗 + 一套不许越界的规矩，它说的每句话都能被拉回原始某一行。**"

## 两个 corner case（必演）

| 情况 | 演示 | 预期 |
|---|---|---|
| 库外问题 | 问 1985 年残骸 | 「这本卷宗里没有。」 |
| 假前提 | 问「17 道船体舱壁对吗」 | 纠正：船体 15 道 [4]，双层底 17 道 [91]，非矛盾 |
| 姓名陷阱 | 问 Edward John Smith | 卷上排印作 Edward Charles Smith [7]，note 已注明，不擅改 |
| 让人编引文 | 要船长原话 | 拒编；改引 Murdoch 转述 [15][85] |

## 一句话口诀

> 一跑（build+validate）二问（跨表三问）三拒（1985）四对（quote 命中）

## 意外兜底

| 情况 | 处理 |
|---|---|
| 中文乱码 | 先执行 `chcp 65001`，或用 Windows Terminal |
| 命令报错 | 改跑 `python code/query_history_db.py` 打印全表，口述答案 |
| 被问"是不是模型背的" | 跑 `python code/verify_sample.py 24 25 94` 展示库行 ↔ 原文逐字对照 |
| 想看全部行 | `python code/query_history_db.py` |
