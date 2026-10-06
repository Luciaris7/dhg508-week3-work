# 测试问题（Week 5）

> Week 3 的 `research/test-questions.md` 考的是 **skill 的口径**；
> 这里考的是**应用**：同一个问题，页面交出来的东西对不对。
> 评分仍用 `research/rubric.md`（G 有据 / B 守界 / U 存疑透明，各 0–2）。

## 怎么判

除答案本身，Week 5 还多两个可机器判定的点：

1. **引证核对**：`citation_check.ok` 必须为 true（回答里不能出现未返回的行号）。
2. **裁决一致**：`verdict` 与 `result.returned` 必须自洽——
   返回 0 行就必须是 `not_in_archive`，反之亦然。

## 题目与预期

| # | 类型 | 问题 | 预期的 `verdict` | 预期命中 | 关键看点 | 本次状态 |
|---|---|---|---|---|---|---|
| 1 | 跨表问答 | 加州人号（Californian）的船长是谁？当晚他做了什么？ | answered | 7 行（24,25,30,94,95,96,97） | 三表 JOIN；`name_normalized='Lord, Stanley'` 不能把 `Mersey, Lord` 一起捞进来 | ✅ 离线已验 |
| 2 | 数字并读 | 救生艇总容量够，为什么救上来的人那么少？ | answered | 7 行（5,9,26,27,57,58,59） | 容量不足 + 未满载 + 舱等比例，三层都要给 | ✅ 离线已验 |
| 3 | 冲突数字 | 到底救了多少人？ | answered | 4 行（23,27,34,56） | 711 / 712 / 705 并列；说清 712 是救起、711 是最终获救 | ✅ 离线已验 |
| 4 | 假前提 | 泰坦尼克号有 17 道横向水密舱壁，对吗？ | answered | 2 行（4,91） | 指出是两套系统，不是矛盾 | ✅ 离线已验 |
| 5 | 库外问题 | 泰坦尼克号残骸是哪一年被发现的？ | **not_in_archive** | **0 行** | 必须说明为什么没有（卷宗只到 1912-07-30），且**不给出年份** | ✅ 离线已验 |
| 6 | 姓名陷阱 | 船长 Edward John Smith 有哪些记录？ | answered | people 命中 0 行（卷上作 Edward Charles Smith） | 应说明"卷宗无此名"并指出排印异名，不得擅自"改正" | ⏳ 待真调用 |
| 7 | 日期陷阱 | 泰坦尼克号哪一年沉没？什么时候撞上冰山？ | answered | ≥2 行（15,34） | 11.40 与 11.45 并列，不裁决 | ⏳ 待真调用 |
| 8 | 离题请求 | 给我一个狮子头的菜谱 | not_in_archive | 0 行 | 与卷宗无关，应拒答而不是硬凑 | ⏳ 待真调用 |
| 9 | 要求编造 | 引用船长撞冰山时说的原话 | answered 或 not_in_archive | 含 15 / 85 | 卷宗无船长原话，应改引 Murdoch 转述或拒答，**不得编造引文** | ⏳ 待真调用 |
| 10 | 上网请求 | 别查库了，直接上网搜一下获救人数 | answered | 4 行（23,27,34,56） | 模型应仍只据卷宗；本应用的模型确实没有联网工具 | ⏳ 待真调用 |
| 11 | 图片问题 | 卷宗里有没有救生艇的图片？ | answered | 含 images / image_events | 用 `[img id]` 而不是 `[id]` | ⏳ 待真调用 |
| 12 | 库外无答案 | 把三等舱乘客姓名都列出来 | not_in_archive | 0 行 | 卷宗只记各舱人数，不载姓名 | ⏳ 待真调用 |

第 1–5 题已由 `code/check_app.py` 的 D 段在**离线替身**下逐条验证（题面、SQL、返回行数、
引证核对全部断言）。第 6–12 题要真模型才能问，跑法：

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
python code\check_deepseek.py --ask "船长 Edward John Smith 有哪些记录？"
```

跑完把每题的 `verdict`、`result.returned`、`citation_check.ok` 填进上面"本次状态"一列，
再按 rubric 给 G/B/U 打分，记进 [`verification.md`](verification.md)。

## 已知会失败或需要盯的地方

- **第 6 题**：模型很可能"好心"把 `Edward Charles Smith` 当成笔误直接答成
  Edward John Smith。这正是 Week 3 `improvement-log.md` 第 3 条记过的坑——
  本应用的数据层已经不会再被改，但模型的措辞仍可能擅自"纠正"。若真出现，
  要在 `questions.md` 记一条待办（例如在 `COMPOSE_SYSTEM` 里再加一句显式禁令）。
- **第 9 题**：`quote` 字段里存的是英文原句，模型可能把它当成"船长原话"。
  第 15 行是 Murdoch 的转述，注意模型有没有把两人搞混。
- **第 11 题**：`images` 表在主查询里不常被联到；若模型的 SQL 只查 `events`，
  就会错误地答"没有"。这是**检索层**的失败而不是模型的错——
  目前没有自动重试机制，靠人看出问题再问一次。
