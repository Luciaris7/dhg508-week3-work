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

## 没被验证的，以及为什么

**真实的 HTTP 往返没有在这里跑过：这台机器上没有 `DEEPSEEK_API_KEY`。**
所以下面这件事只有密钥持有者做得了：

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
python code\check_deepseek.py                 # 一次最小调用
python code\check_deepseek.py --ask "到底救了多少人？"   # 完整两步
```

我不打算用"桩替身跑通了所以真调用也没问题"来含糊过去。已经做到的边界是：
**报文形状逐字段符合官方文档**（F 段）、**密钥缺失时明确失败而不是静默降级**（F 段最后一条）、
**两步流水线与后续解析、守卫、引证核对全部用真数据跑通**（A–E 段）。
剩下的一步是网络与账号，需要在有密钥的机器上补跑一次。

补跑后请把输出贴进本文件，替代这一段。

## 顺带修正的一处 Week 3 不一致

Week 3 的 `skills/mersey-clerk/reference/tables.md` 写"外键共 **7** 条"，
而 `research/database-design.md` 与建库脚本 `code/build_db.py` 里都是 **9** 条
（`places.source_id`、`people.source_id`、`events.place_id`、`events.source_id`、
`event_people.event_id`、`event_people.person_id`、`images.source_id`、
`image_events.image_id`、`image_events.event_id`）。

Week 5 的 skill 副本按 9 条更正，并在文件里注明出处。
**Week 3 的原文件未改动**（你要求保持原样），所以那处不一致仍然留在原地——
要不要回改 Week 3，记在 [`../questions.md`](../questions.md) 第 3 条。
