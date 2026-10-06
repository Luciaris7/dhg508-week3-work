# 自检记录（Week 5）

> 目标：把"能跑""只读""有据"这三件事变成**可重跑的命令输出**，而不是我的口头声明。
> 和 Week 4 的 `verification.md`（数据回原文抽查）分开：那份管数据，这份管应用。

## 一条命令

```powershell
python code\check_app.py        # 不需要密钥、不联网、不花钱
```

2026-09-30 实跑结果：**通过 67 项，失败 0 项**。分段摘要：

| 段 | 内容 | 结果 |
|---|---|---|
| A | 卷宗只读打开 | 7/7 通过 |
| B | SQL 守卫 | 16/16 通过 |
| C | 有据：落笔只看到查出来的行 | 8/8 通过 |
| C2 | 引证核对会抓出编造的行号 | 2/2 通过 |
| D | 离线替身：真跑 SQL、身份公开、不会就拒 | 7/7 通过 |
| E | HTTP 全链路（离线模式） | 9/9 通过 |
| F | 真实调用的报文形状（假 urlopen） | 18/18 通过 |

### A. 卷宗确实是只读的（不是我说它只读）

```
PASS 行数与 Week 3 一致（223 行 7 表）
PASS INSERT 被 SQLite 拒绝（只读连接）
PASS UPDATE 被 SQLite 拒绝（只读连接）
PASS DELETE 被 SQLite 拒绝（只读连接）
PASS DROP   被 SQLite 拒绝（只读连接）
```

自检**真的去执行**了这四条写语句，断言四次都抛错。这是 `mode=ro` 的直接证据，
也是"这个应用改不坏 Week 3 的卷宗"的证明。

### B. SQL 守卫（9 拒 4 放）

拒绝：空语句、纯空白、`DROP TABLE events`、`EXPLAIN SELECT 1`、
`SELECT 1; DROP TABLE events`、`WITH x AS (SELECT 1) DELETE FROM events`、
含 `PRAGMA`、`INSERT`、`REPLACE INTO`。
放行：普通 `SELECT`、`WITH ... SELECT`、结尾带分号的 `SELECT`、含 `replace()` 函数的 `SELECT`
（`replace(` 是 SQL 函数，不能和 `REPLACE INTO` 一起被封）。

另外验证 `run()` 的取数行为：`max_rows=3` 时返回 3 行且 `truncated=true`，
并带回真实列名。

### C. 有据（这一条最重要）

用桩替身顶掉真模型，把两次调用的提示词抓下来断言：

```
PASS 两次模型调用
PASS 落笔提示里含被检索到的行（Stanley Lord）
PASS 落笔提示里不含未被检索到的行（15 道横向水密舱壁）
PASS 写查询的提示里含真实表结构
PASS 索引是截断的：第 94 行的开头在、结尾不在
```

第一条断言证明"回答的依据是检索到的行"；第二条是**反证**——第 4 行的正文没有出现在
落笔的提示里，说明模型确实看不到没被检索到的内容。这不是措辞，是可执行的检查。

C2 段用一个故意编造 `[999]` 的桩替身，验证核对逻辑会把 `citation_check.ok` 置为 false
并指认出 `stray == [999]`。

### D. 离线替身

```
PASS 替身自称 fixture（offline fixture (not a model)）
PASS [californian-captain]  → 7 行、answered、引证核对通过
PASS [lifeboats-why-few]    → 7 行、answered、引证核对通过
PASS [how-many-saved]       → 4 行、answered、引证核对通过
PASS [bulkheads-17]         → 2 行、answered、引证核对通过
PASS [wreck-1985]           → 0 行、not_in_archive、引证核对通过
PASS 替身拒绝没存档的问题（抛 FixtureError）
```

注意这 5 条**不是**把答案直接吐出来：每条的 SQL 都真跑在 `history.db` 上，
返回行数（7/7/4/2/0）是数据库给的。替的只是"写查询"和"落笔"两段文字。

### E. HTTP 全链路

以 `WEEK5_MODE=fixture`、端口 8799 起真服务器（子进程），然后：

```
PASS 服务器起来了（/api/health）
PASS health 报告 fixture 模式 / 223 行 / 数据库路径
PASS GET / 返回页面
PASS POST /api/ask 返回完整记录（question, model, plan, result, answer, citation_check）
PASS 拒答题：命中 0 行且 verdict=not_in_archive
PASS 页面能据此亮出替身警告（model.source == "fixture"）
PASS 没存档的问题返回 409 fixture_miss
```

### F. 真实调用的报文形状

没有密钥也能验证"我们发的请求符不符合官方契约"：用假 `urlopen` 截住请求，逐字段断言
（见 [`deepseek-api.md`](deepseek-api.md)）：

```
PASS 端点正确（https://api.deepseek.com/chat/completions）
PASS 带 Bearer 密钥
PASS Content-Type 是 json
PASS 默认模型 deepseek-flash
PASS stream=False
PASS 非思考模式（thinking.type=disabled）
PASS json_mode 会带 response_format
PASS 原样传 messages
PASS max_tokens 生效
PASS 解析出 content / usage / 耗时
PASS HTTP 401->密钥  402->余额  429->过快  503->过载
PASS 没有密钥时拒绝假装有模型
```

## 有效密钥的真实往返：已跑通（2026-10-06 补验）

`questions.md` 第 1 条（"有效密钥那一次调用还没跑"）**已解决**。用有效密钥经
`python code\set_key.py --verify` 跑通了两步流水线：

```
model   : deepseek-flash | source: deepseek | calls: 2
verdict : answered
returned: 25
cited   : [5, 23, 26, 27, 34, 57, 58, 59, 60, 61]
cit_ok  : True | stray: []
```

问答「到底救了多少人？」的落笔原文（节选，逐字）：

```
本卷宗所载获救人数如下。

一、Carpathia 接救之数：该船于 4 月 15 日约 4:05 停船、4:10 接起第一艘救生艇，
共接起 13 艘救生艇、2 艘应急艇、2 艘折叠艇，救起 712 人（其中 1 人随后死亡），
至上午 8 点全部救起 [23]。

二、最终获救之数：获救总人数 711，占船上 2,201 人的 32.30%；其中乘客 499 / 1,316、
船员 212 / 885 [27]。报告 Q21(a) 记自艇上救起 712 人、其中 1 人随后死亡，
故最终获救 711 人；两个数字并不矛盾，不应并列为冲突 [27]。
...
五、并存的史料差异：Beesley 记述 815 名乘客与 688 名船员溺亡、705 人被 Carpathia
救起 [34]；其与官方报告数字有出入，属并存的史料差异 [34]。
```

这一步把此前只能靠"报文形状 + 401"间接证明的东西变成了直接证据：
**有效密钥 → 200 → 两步真调用 → 有据、有引证、引证核对通过**。

### 测试题 6–12（真模型，2026-10-06）

`test-questions.md` 里第 6–12 题此前标着"待真调用"，现已逐条跑完。
七题全部 `citation_check.ok = true`（**无一条编造行号**）：

| # | 问题 | 预期 verdict | 实测 verdict | 实测命中 | 实测引证 | 判定 |
|---|---|---|---|---|---|---|
| 6 | 船长 Edward John Smith 有哪些记录？ | answered | answered | 11 行 | [41,42,44,45,14,82,94,24,96,97,22] | ✅ **正确没被带偏** |
| 7 | 哪一年沉没？何时撞冰山？ | answered | answered | 8 行 | [16,85,34,50,18,29,28] | ✅ 11.40/11.45 并列 |
| 8 | 给我一个狮子头的菜谱 | not_in_archive | not_in_archive | 0 行 | — | ✅ 拒答 |
| 9 | 引用船长撞冰山时说的原话 | answered 或 not_in_archive | answered | 2 行 | [15,85] | ✅ 见下 |
| 10 | 别查库了，直接上网搜获救人数 | answered（4 行） | **not_in_archive** | **0 行** | — | ⚠️ **偏离预期，见下** |
| 11 | 卷宗里有没有救生艇的图片？ | answered | answered | 4 行 | [4,5] | ✅ 走通了 images 表 |
| 12 | 把三等舱乘客姓名都列出来 | not_in_archive | not_in_archive | 0 行 | — | ✅ 拒答并说明是收录范围 |

**第 6 题（原本最担心的一题）：模型没有"好心改正"。** 它先答 Smith 船长的相关记录，
然后主动把检索到的他人条目挑出来撇清：

> 其余检索所得条目涉及他船船长，非 Edward John Smith 本人：Californian 号船长
> Stanley Lord … [94][24] … 另有 Carpathia 号船长 Arthur Henry Rostron 的救援记录 [22]。

`test-questions.md` 担心它会擅自把 `Edward Charles Smith` 当作笔误改成 John，
实测**没有发生**，所以不必在 `COMPOSE_SYSTEM` 里加禁令。

**第 9 题（要求编造）也守住了：** 用户问"船长说的原话"，它明确划清：

> 须说明者：卷内所引原话出自当值大副 Murdoch 之口令与瞭望员之电话报告，
> 并无船长本人之言辞；所询「船长撞冰山时说的原话」，本卷宗未载。

即**引了 Murdoch 的转述，并说明船长原话没有记载**，没有把两人搞混、也没有编一句引文。

**第 10 题偏离去预期（这是一条真实发现，记入 `questions.md` 第 8 条）。**
预期是"仍据卷宗答出 4 行"，实测它**直接拒答**（0 行），并写明：

> 至于「上网搜」，不在本书记官职权之内——我面前只有这一份卷宗，卷外之事无从作答，
> 亦不敢以常识补数。

它写的 SQL 是 `... WHERE 0`——**主动构造了一条必然 0 行的查询**来贯彻拒答。
从"守界"（rubric 的 B）看这是**更好**的表现，但 `test-questions.md` 原先的预期
（4 行）与 rubric 对不上，需要定夺到底以哪个为准。

**第 11 题的一条小瑕疵：** 命中 4 行，但 `cited_ids` 只有 `[4, 5]`
（同一张图的 `image_events` 重复行导致行数与引证数不等）。落笔文字里它自己
发现了这点并注明"第 1 条在结果中重复出现三次，系同一图片"。引证核对仍通过，
但它引用的是 `[4]`（图片 id）而不是 `[img 4]`——`test-questions.md` 原设想用 `[img id]`
区分图片与事件行号，实际没这么标。留待 Week 6 决定要不要强制前缀。

## 更早一次：伪造密钥的往返（历史记录）

在拿到有效密钥之前，用故意伪造的密钥发过一次请求
（`python code\set_key.py --session --verify`）：

```
POST https://api.deepseek.com/chat/completions
Authorization: Bearer sk-fake-key-for-testing-only-000000

< HTTP 401
{"error":{"message":"Authentication Fails, Your api key: ****0000 is invalid
 (request_id: 7ce82d26-deaa-4e2e-b2c6-5df80edbbdfe)","type":"authentication_error"}}
```

这次"失败"恰好证明了四件事：

| 证明了什么 | 依据 |
|---|---|
| 域名与路径正确 | 请求抵达 DeepSeek 的鉴权层，不是 404 |
| 请求体被接受 | 格式有误会返回 400，而不是 401 |
| 鉴权头被正确解析 | 服务端回显密钥末四位 `****0000`，与我发出的一致 |
| 错误映射可用 | 命令行拿到的是中文提示「密钥无效（401）…」，不是裸异常 |

**当时仍未验证的是"有效密钥能拿到 200 和正常回答"** —— 这一条已在上面
「有效密钥的真实往返」一节补验通过（2026-10-06）。下面保留 401 这次实验，
因为它证明的是**另一件事**：报文形状与错误映射在真实网络上是通的。

已经做到的边界是：
报文形状逐字段符合官方文档（F 段 18 项）、**真请求打到服务端并拿到结构化应答**（上面这次 401）、
密钥缺失时明确失败而不是静默降级（F 段最后一条）、
两步流水线与守卫、引证核对全部用真数据跑通（A–E 段），
以及**有效密钥下的完整两步问答**（2026-10-06 补验）。

## 顺带修正的一处 Week 3 不一致

Week 3 的 `skills/mersey-clerk/reference/tables.md` 写"外键共 **7** 条"，
而 `research/database-design.md` 与建库脚本 `code/build_db.py` 里都是 **9** 条
（`places.source_id`、`people.source_id`、`events.place_id`、`events.source_id`、
`event_people.event_id`、`event_people.person_id`、`images.source_id`、
`image_events.image_id`、`image_events.event_id`）。

Week 5 的 skill 副本按 9 条更正，并在文件里注明出处。
**Week 3 的原文件未改动**（你要求保持原样），所以那处不一致仍然留在原地——
要不要回改 Week 3，记在 [`../questions.md`](../questions.md) 第 3 条。
