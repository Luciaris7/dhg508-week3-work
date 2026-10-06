# DeepSeek API 契约（我们实际实现的那一份）

> Week 5 要求："Give opencode the official DeepSeek API documentation and ask it to write the call with you."
> 这份文件记录**我们照哪一版文档、实现了什么**，以及代码里对应哪几行。实现只用标准库 `urllib`。

来源（2026 年抓取）：

- 首次调用与 base_url：<https://api-docs.deepseek.com/>
- Chat Completions 请求/响应：<https://api-docs.deepseek.com/api/create-chat-completion>
- JSON Output：<https://api-docs.deepseek.com/guides/json_mode>
- 错误码：<https://api-docs.deepseek.com/quick_start/error_codes>

## 1. 端点与鉴权

| 项 | 值 | 代码位置 |
|---|---|---|
| base_url | `https://api.deepseek.com` | `model.DEFAULT_BASE_URL`（可用 `DEEPSEEK_BASE_URL` 覆盖） |
| 路径 | `POST /chat/completions` | `model._post_chat()` 里的 `base_url() + "/chat/completions"` |
| 鉴权 | `Authorization: Bearer $DEEPSEEK_API_KEY` | 同上，头部构造处 |
| 内容类型 | `Content-Type: application/json` | 同上 |

密钥只从 `os.environ["DEEPSEEK_API_KEY"]` 读（`model.api_key()`），不落盘、不入库、
不写进响应，也不回显（`check_deepseek.py` 只打印长度）。

## 2. 模型名

文档当前的取值是 `deepseek-flash` 与 `deepseek-v4-pro`（旧的 `deepseek-chat` /
`deepseek-reasoner` 命名已不在这一版文档里）。本项目默认 `deepseek-flash`，
可用 `DEEPSEEK_MODEL` 覆盖。`check_deepseek.py` 会把实际模型名打印出来。

## 3. 请求体字段（我们发的）

```json
{
  "model": "deepseek-flash",
  "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
  "stream": false,
  "thinking": {"type": "disabled"},
  "max_tokens": 1024,
  "temperature": 0.0,
  "response_format": {"type": "json_object"}
}
```

逐条对应文档：

- `thinking.type` 默认 `enabled`；我们显式发 `disabled`。理由：书记官的活是**转写**不是推理，
  非思考模式更快、更省，而且只有非思考模式下 `temperature` 才生效（文档明确写了
  "Has no effect in thinking mode"）。想开思考模式：`WEEK5_THINKING=1`，
  此时 `model.build_payload()` 会**不发** `temperature`。
- `response_format: {"type": "json_object"}` 只在两步模型调用里使用（`json_mode=True`）。
- `max_tokens`：写查询 1024、落笔 2048。文档要求"设得合理以免 JSON 被截断"。
- `temperature`：写查询 0.0（要确定性），落笔 0.2（要文气但别飘）。
- `stream`：`false`。这个应用不需要逐字输出，一次拿完整 JSON 更好判定。

**JSON Output 的两条硬要求都满足了**：
① `response_format` 已设；② 系统提示里含 "json" 字样并给了输出格式示例
（`PLAN_SYSTEM`／`COMPOSE_SYSTEM` 结尾都是「输出必须是 json，格式：{...}」）。
文档还警告"JSON Output 偶发返回空内容"，`model.chat()` 因此对空内容重试一次，
再空就抛 `ModelError`（`retries` 参数控制）。

## 4. 响应字段（我们用的）

文档的 `chat completion object` 里我们只读这些：

| 字段 | 用途 |
|---|---|
| `choices[0].message.content` | 要解析的 JSON 正文 |
| `choices[0].finish_reason` | 为 `length` 说明被截断；空内容时报错会带上它 |
| `model` | 回显实际服务的模型名，打印在页脚元信息里 |
| `usage.prompt_tokens / completion_tokens / total_tokens` | 页脚显示 token 数 |

`choices[0].message.reasoning_content` 只在思考模式下出现，本项目不读它（关掉思考模式）。

## 5. 错误处理

文档列出的状态码 → `model.HINTS` 里的中文指引，`model.chat()` 转成带 `status` 的
`ModelError`，`server.py` 映射为 HTTP 502 并把原文交给页面：

| 状态码 | 文档含义 | 我们的提示 |
|---|---|---|
| 400 | Invalid Format | 请求体格式有误（本程序的 bug） |
| 401 | Authentication Fails | 检查 `$env:DEEPSEEK_API_KEY` |
| 402 | Insufficient Balance | 去充值页 |
| 422 | Invalid Parameters | 检查 `DEEPSEEK_MODEL` |
| 429 | Rate Limit Reached | 等几秒再试（自动重试一次） |
| 500 | Server Error | 稍后重试（自动重试一次） |
| 503 | Server Overloaded | 稍后重试（自动重试一次） |

`urlopen` 的 `URLError`（断网/代理）也转成 `ModelError`，页面直接显示。

## 6. 官方示例用了 `openai` SDK，我们用标准库

文档的 python 示例用 `from openai import OpenAI`。本项目坚持**只用标准库**（与 Week 3
的脚本、示例应用同一个原则：`python3 server.py` 就能跑，不用 `pip install`）。因此
`model._post_chat()` 用 `urllib.request` 手写这一条请求——报文形状与官方示例完全一致，
并且被 `code/check_app.py` 的 F 段逐字段断言（不联网，用假 `urlopen` 截住请求）。

没被自动断言、只能靠真人跑一次的，是"服务器真的接受这条请求并回话"这件事：
`python code/check_deepseek.py`。
