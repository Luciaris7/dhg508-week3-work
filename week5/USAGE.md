# 使用说明 · Week 5「向卷宗提问」

给要在自己机器上把这套东西跑起来、用起来、出问题能自己查的人。

- 这是什么、每个文件干什么 → [`README.md`](README.md)
- 课堂 5 分钟怎么讲 → [`DEMO.md`](DEMO.md)
- 本文 = 从零到用起来 + 排查

---

## 0. 一分钟版

```powershell
cd "C:\Users\28301\Desktop\dhg508 week3\week5"
python code\set_key.py --verify     # 一次性：粘贴密钥，顺带用一次真调用验证
python app\server.py                # 启动服务器（保持这个窗口开着）
```

然后在浏览器地址栏输入 **<http://localhost:8000>**。

> **唯一必须记住的一条**：地址必须是 `http://localhost:8000`。
> **双击 `app\static\index.html` 是不行的**——那样是 `file://` 协议，浏览器不允许页面访问本地服务器，
> 页面会显示"打不开服务"并给出正确命令。原因见 §7.1。

---

## 1. 环境要求

| 项 | 要求 |
|---|---|
| 系统 | Windows（用户环境变量的写法是 Windows 的） |
| Python | 3.8 或更新（本机实测 3.14.7）；**只用标准库，不需要 pip install** |
| 卷宗 | 上级目录的 `..\history.db`（7 表 223 行），由 Week 3 生成，本文件夹不改它 |
| 网络 | 只有"真模型"模式需要；离线替身模式完全离线 |
| 密钥 | 只有"真模型"模式需要，见 §2 |

自检一下环境（不联网、不花钱）：

```powershell
python code\check_app.py        # 应打印「通过 67 项，失败 0 项」
```

---

## 2. 一次性设置：DeepSeek 密钥

1. 到 <https://platform.deepseek.com/api_keys> 建一个 API key（需要登录；余额不足时按需充值）。
2. 在 `week5` 目录下运行向导：

```powershell
python code\set_key.py --verify
```

它会：提示你**粘贴（输入不回显）** → 存进**用户环境变量**（不写任何文件）→ 立刻用一次真调用验证。

### 向导的几种用法

| 命令 | 作用 |
|---|---|
| `python code\set_key.py` | 存进用户环境变量（新开的窗口才读得到） |
| `python code\set_key.py --verify` | 同上，并立刻跑一次真调用验证（推荐） |
| `python code\set_key.py --session --verify` | **什么都不落盘**，只在本次运行里试一次，适合先试通再决定 |
| `python code\set_key.py --check` | 只看现状：当前进程有没有、用户环境变量有没有 |

### 不用向导也可以

```powershell
$env:DEEPSEEK_API_KEY = "sk-xxxxxxxx"   # 只对当前窗口有效
setx DEEPSEEK_API_KEY "sk-xxxxxxxx"     # 存进用户环境变量（注意：会留在命令行历史里）
```

密钥**只从环境变量读**，代码里没有任何读取文件的路径，也没有 `.env`。
（这就是不用 `.env` 的原因：有 `.env` 就有被误提交的风险。）

---

## 3. 启动与访问

```powershell
cd "C:\Users\28301\Desktop\dhg508 week3\week5"
python app\server.py
```

启动横幅会先告诉你**现在是哪种模式**：

```
  archive   ...\dhg508 week3\history.db  (223 rows)
  model     deepseek-flash  (DEEPSEEK_API_KEY found)   ← 真模型模式
  model     offline fixture (not a model)              ← 离线替身模式（会额外提示怎么设密钥）
  open      http://localhost:8000
```

- 端口被占用时：`$env:WEEK5_PORT = "8765"` 后再启动，然后访问 <http://localhost:8765>。
- 停止服务器：在那个窗口按 `Ctrl+C`。
- **服务器只绑 `127.0.0.1`**，局域网里别的机器访问不到（这是故意的，见 §8）。

---

## 4. 页面怎么用

1. 在输入框写一个问题（中文即可），或点下面的示例题。
2. 按「呈上问题」（也可以 `Ctrl + Enter`）。
3. 等 3–10 秒，页面自上而下给出：

| 区域 | 内容 | 怎么读 |
|---|---|---|
| **状态条** | 现在是真模型还是离线替身 | 黄色 = 离线替身，回答不是模型给的 |
| **结论条** | "卷宗有此记载，查得 N 行" / "这本卷宗里没有" | 一眼看出是有据还是拒答 |
| **回答** | 书记官的话，逐条带 `[id]` | 交付物本身 |
| **引证** | `[24] [94] [95]` 小标签 | 未在返回行里的行号会**标红** |
| **依据** | 查询真正返回的行（行号/日期/文献/位置/事实/存疑） | **审计**：回答只能来自这张表 |
| **检索过程**（可展开） | 模型写的 SQL + 检索说明 | **审计**：看出它到底查了什么 |
| **页脚** | 模型名、调用次数、耗时、tokens、返回行数 | 证明这是真调用，花了多少 |

**推荐先试这几道**（都能离线跑通）：

| 问题 | 预期 |
|---|---|
| 加州人号（Californian）的船长是谁？当晚他做了什么？ | 查得 7 行，引证 `[24][94][95][96][97][25][30]` |
| 救生艇总容量够，为什么救上来的人那么少？ | 查得 7 行，三层原因 |
| 到底救了多少人？ | 查得 4 行，711/712/705 三个口径并列 |
| 泰坦尼克号有 17 道横向水密舱壁，对吗？ | 查得 2 行，指出是两套系统 |
| 泰坦尼克号残骸是哪一年被发现的？ | **0 行 → "这本卷宗里没有"** |

---

## 5. 两种模式，怎么切换

| 模式 | 什么时候 | 行为 |
|---|---|---|
| `deepseek`（真模型） | 有 `DEEPSEEK_API_KEY` 时自动 | 两次真调用；页面无黄条 |
| `fixture`（离线替身） | 没有密钥时自动，或强制 | 回答来自 `app/fixtures/offline-answers.json`；**页面黄条 + 只认 5 道示例题**；问别的返回 409 |

强制指定（在**同一个窗口**里设好再启动）：

```powershell
$env:WEEK5_MODE = "fixture"     # 强制离线，用来排练
$env:WEEK5_MODE = "deepseek"    # 强制真调用：没密钥就直接报错，绝不偷偷退回替身
```

**切换模式或换了密钥，都必须重启服务器**——进程的环境变量在启动时就固定了。

离线替身模式下：SQL 仍然**真的**跑在 `history.db` 上（依据表里的行是真档案行），
替的只是"写查询"和"落笔"两段文字，而且它**从不假装自己是模型**。

---

## 6. 命令速查

```powershell
# 日常
python app\server.py                                   # 启动
python code\set_key.py --check                         # 密钥现状
python code\check_app.py                               # 自检 67 项（不联网、不花钱）

# 真调用验证（花几枚 token）
python code\check_deepseek.py                          # 一次最小调用
python code\check_deepseek.py --ask "到底救了多少人？"    # 完整两步流水线

# 卷宗（Week 3 的脚本，在本文件夹的上级目录）
python ..\code\build_db.py                             # 从 data/*.json 重建
python ..\code\validate_db.py                          # 引文回原文 + 外键校验
python ..\code\verify_sample.py                        # 随机 20 行对照原文
```

---

## 7. 出问题怎么查

### 7.1 页面显示"打不开服务" / `Failed to fetch`

**九成是这两种情况**：

1. **你双击打开了 HTML 文件**。地址栏如果是 `file:///...`，就是这个问题。
   → 启动服务器，然后访问 <http://localhost:8000>。
2. **服务器没在跑**（窗口关了、崩了）。→ 重新 `python app\server.py`。

自查：`Test-NetConnection 127.0.0.1 -Port 8000`，或浏览器直接开 <http://127.0.0.1:8000/api/health>，
能看到一段 JSON 就说明服务器是活的。

### 7.2 其它常见情况

| 现象 | 原因 | 处理 |
|---|---|---|
| 启动横幅写 `offline fixture (not a model)` | 没读到密钥 | `python code\set_key.py --verify` |
| 页面顶部黄条 | 同上，正在用离线替身 | 设密钥后**重启**服务器 |
| 409 `fixture_miss` | 离线替身只认 5 道题 | 设密钥走真模型，或改用示例题 |
| 502 `密钥无效（401）` | 密钥抄错/含空格 | 重新 `set_key.py`；向导已自动去掉首尾空格 |
| 502 `余额不足（402）` | 账户没钱了 | <https://platform.deepseek.com/top_up> |
| 502 `请求过快（429）`/`过载（503）` | 限流或服务端忙 | 程序已自动重试一次；再等等 |
| 502 `unsafe_sql` | 模型写出了非只读语句，被守卫拒 | 重问一次通常就好；连卷宗都没碰到 |
| 500 `SQLite refused the query` | 模型写的列名/表名不存在 | 重问一次；这属于检索层失败，见 `questions.md` 第 2 条 |
| 端口被占用 | 8000 被别的程序占了 | `$env:WEEK5_PORT = "8765"` 后重启 |
| 控制台中文乱码 | PowerShell 5.1 默认 cp936 | 一般不用管（脚本会自适应）；实在乱就先 `chcp 65001` |
| 改了数据但页面还是旧行 | 没重建数据库 | 跑 `python ..\code\build_db.py`（应用每次请求都重新只读打开卷宗，不必重启服务器） |

### 7.3 想确认"到底谁在答"

- 页面**页脚**：`model deepseek-flash` = 真调用；`⚠ offline fixture (not a model)` = 替身。
- 页面**状态条**：黄条就是替身。
- 命令行：`python code\check_deepseek.py` 会打印实际模型名与 token 用量。

---

## 8. 安全与边界（别踩的几条）

- **卷宗改不坏。** 数据库以 `mode=ro` 打开；模型写的 SQL 还要过两道守卫（单条 `SELECT`/`WITH`、禁词表）。
  `check_app.py` 的 A 段会**真的去执行** `INSERT/UPDATE/DELETE/DROP` 并断言四次都被拒绝。
- **密钥不落盘。** 只在环境变量里；不进 Git；不打印；不作为命令行参数传给子进程。
- **不要往外网暴露。** 服务器没有鉴权，只绑 `127.0.0.1`；对外开等于把 API 额度借给任何人。
- **上限 60 行。** 单次检索最多返回 60 行（`WEEK5_MAX_ROWS`），超出会在响应里标 `truncated`。
- **只支持单轮提问。** 每次都是全新的两步调用，不保留上下文（见 `questions.md` 第 4 条）。
- **没有有效密钥时不会假装。** `WEEK5_MODE=deepseek` 而密钥缺失会直接报错。

---

## 9. 往里加数据

完整步骤在 [`skills/mersey-clerk/maintenance.md`](skills/mersey-clerk/maintenance.md)，速记：

1. 新来源登记进 `..\code\data\sources.json`，原文逐字放进 `..\sources\raw\`（不改原文）；
2. 新建 `..\code\data\events_03_<来源>.json`（`events_` 前缀会被自动合并），每条都要有
   `id`（最大 + 1，不复用）、`source_id`、`locator`、`quote`（能在原文逐字命中）、`note`；
3. 重建与校验：`python ..\code\build_db.py` → `validate_db.py` → `verify_sample.py`。

**应用与数据是解耦的**：不用改一行代码，也不用重启服务器，刷新页面就能查到新行。
