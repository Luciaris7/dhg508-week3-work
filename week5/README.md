# Week 5 · 向卷宗提问（The Mersey Clerk 有了自己的应用）

> 把 Week 3 的 `history.db`（泰坦尼克号 1912 调查卷宗，7 表 223 行）接上一个**真的** DeepSeek 调用：
> 你在网页上写一个问题，服务器让模型写出 SQL、真的去库里查，再把**查到的行**交给模型，
> 由它以 1912 年调查庭书记官的口吻作答，逐条标 `[id]` 与出处；库里没有，就说「这本卷宗里没有」。

上一周的示例 `demo-building-app` 里，`ask_model()` 是一个 fixture——**每张照片都返回同一个答案**，
而且页面只在角落标一句 "model: fixture"。这个文件夹做的东西相反：**要么真调模型，要么明说自己在用离线替身**，
绝不把替身装成模型。见 [`app/model.py`](app/model.py) 与 [`research/app-design.md`](research/app-design.md)。

## 先决条件

```powershell
# 1) 会用到上级目录里 Week 3 的卷宗与脚本（本文件夹不改动它们）
Test-Path ..\history.db          # True
python --version                 # Python 3，只要标准库，无需 pip install

# 2) 注册一个 DeepSeek API key（https://platform.deepseek.com/api_keys），只放在环境变量里
$env:DEEPSEEK_API_KEY = "sk-xxxxxxxx"      # 仅当前窗口有效
# 或者长期保存在用户环境变量里（新开窗口生效）：
setx DEEPSEEK_API_KEY "sk-xxxxxxxx"
```

密钥**只从环境变量读**，代码里没有任何地方写 key，也没有 `.env` 文件——见 [`app/model.py`](app/model.py)。

## 跑起来

```powershell
cd "week5"
python app\server.py                 # 然后打开 http://localhost:8000
```

页面上写问题（或点示例），按「呈上问题」。约 3–10 秒后你会看到：结论、书记官的回答、
`[id]` 引证、**实际执行的 SQL**、以及**作为唯一依据的那些行**。

先自检（不花 API 额度）：

```powershell
python code\check_app.py             # 只读保证 + SQL 守卫 + 离线全链路 + HTTP 冒烟
python code\check_deepseek.py        # 用你的 key 发一次真实调用，确认密钥与网络可用
```

## 文件

| 路径 | 一件事 |
|---|---|
| `app/archive.py` | 只读打开 `history.db`、SQL 守卫、给模型的档案索引 |
| `app/model.py` | **真实 DeepSeek 调用**（就是替换掉 fixture 的那一处） |
| `app/clerk.py` | 三步流水线：问题 → SQL → 行 → 有出处的中文回答；离线替身也在这里，且**标明身份** |
| `app/server.py` | HTTP：页面、`/api/ask`、`/api/health` |
| `app/static/index.html` | 一个网页（原生 HTML + JavaScript） |
| `app/fixtures/offline-answers.json` | 离线替身的预设答案，每一条都标注 `"source": "fixture"` |
| `skills/mersey-clerk/` | 重构后的 skill：`SKILL.md` 索引 + 三份文档 + 按需加载的 `reference/` |
| `skills/mersey-registrar/` | 只指向 clerk 的 `maintenance.md`，不再重复内容 |
| `code/check_app.py` | 不联网的自检（含只读与守卫的反证） |
| `code/check_deepseek.py` | 用真 key 发一次真调用 |
| `research/` | 应用设计、DeepSeek API 契约、自检记录、测试问题 |
| `DEMO.md` | 课堂 5 分钟演示脚本（从 fixture 讲到真调用） |
| `questions.md` | 本次仍未决的问题 |

## 与 Week 3 的关系

- 卷宗本体、原始材料、构建与校验脚本**都留在原处**：`..\history.db`、`..\code\build_db.py`、
  `..\code\validate_db.py`、`..\sources\raw\`。本文件夹只读取，不修改。
- 本文件夹是**新增**的：Week 3 的东西一个字节都没动（`git log` 里可以看到只多了这个目录）。
- skill 从 Week 3 的「一份长 SKILL.md + 三份 reference」重构成「**一份索引 + 三份按职责分开的文档**」。

## 五分钟演示

见 [`DEMO.md`](DEMO.md)。要讲的三件事：**应用在跑并且答了一个真问题** ·
**fixture 原来在哪、被什么替换了** · **skill 的索引、提交历史**。
