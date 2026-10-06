"""The real DeepSeek call.

**This file is what replaced the demo's fixture.**

In `demo-building-app/server.py` the function `ask_model()` read
`fixtures/model-response.json` and returned the same saved answer for every
photo, while the page merely wore a small "model: fixture" badge.

Here the same spot makes a real HTTPS request to DeepSeek, and the API key is
read from the environment only — it is never written to a file, never logged,
and never sent back to the browser.

Official contract (https://api-docs.deepseek.com/):

    POST https://api.deepseek.com/chat/completions
    Authorization: Bearer $DEEPSEEK_API_KEY
    {"model": "deepseek-flash", "messages": [...], "response_format": {"type": "json_object"}}

Standard library only: urllib. Nothing to install.
"""

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"
DEFAULT_TIMEOUT = 90

# Status code -> what the human should do about it (DeepSeek docs, "Error Codes").
HINTS = {
    400: "请求体格式有误（400）。这是本程序的 bug，不是密钥问题。",
    401: "密钥无效（401）。检查 $env:DEEPSEEK_API_KEY 是否抄漏或含空格。",
    402: "余额不足（402）。到 https://platform.deepseek.com/top_up 充值。",
    422: "参数无效（422）。检查 DEEPSEEK_MODEL 是否是 deepseek-flash / deepseek-v4-pro。",
    429: "请求过快（429）。等几秒再试。",
    500: "DeepSeek 服务端错误（500）。稍后重试。",
    503: "DeepSeek 过载（503）。稍后重试。",
}


class ModelError(Exception):
    """A real model call was attempted and failed."""

    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


def api_key() -> str:
    """The key lives in the environment and nowhere else."""
    return (os.environ.get("DEEPSEEK_API_KEY") or "").strip()


def key_present() -> bool:
    return bool(api_key())


def base_url() -> str:
    return (os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def model_name() -> str:
    return os.environ.get("DEEPSEEK_MODEL") or DEFAULT_MODEL


def thinking_enabled() -> bool:
    """Off by default: the clerk's job is transcription, not deliberation.

    With thinking on, `temperature` is ignored by the API; with it off, it applies.
    """
    return (os.environ.get("WEEK5_THINKING") or "").lower() in ("1", "on", "true", "yes")


def build_payload(messages, *, json_mode=False, temperature=None,
                  max_tokens=None, thinking=None, model=None):
    payload = {
        "model": model or model_name(),
        "messages": messages,
        "stream": False,
        "thinking": {"type": "enabled" if (thinking_enabled() if thinking is None else thinking) else "disabled"},
        "max_tokens": max_tokens or int(os.environ.get("WEEK5_MAX_TOKENS", "2048")),
    }
    if temperature is not None and payload["thinking"]["type"] != "enabled":
        payload["temperature"] = temperature
    if json_mode:
        # Docs: JSON Output requires both response_format and the word "json" in a prompt.
        payload["response_format"] = {"type": "json_object"}
    return payload


def _post_chat(payload, timeout=DEFAULT_TIMEOUT):
    """One HTTPS round trip. Kept separate so tests can replace it."""
    key = api_key()
    if not key:
        raise ModelError("DEEPSEEK_API_KEY is not set; refusing to pretend a model answered")
    request = urllib.request.Request(
        base_url() + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", "replace")[:400]
        except Exception:
            pass
        hint = HINTS.get(exc.code, "未在文档中列出的状态码，见 DeepSeek 错误码页。")
        raise ModelError("%s  %s" % (hint, body), status=exc.code, body=body) from exc
    except urllib.error.URLError as exc:
        raise ModelError("连不上 DeepSeek（%s）。检查网络或代理。" % exc.reason) from exc
    except json.JSONDecodeError as exc:
        raise ModelError("API 返回的不是 JSON：%s" % exc) from exc


def chat(messages, *, json_mode=False, temperature=None, max_tokens=None,
         timeout=DEFAULT_TIMEOUT, thinking=None, retries=1):
    """Call DeepSeek and return {content, model, usage, finish_reason, seconds}."""
    payload = build_payload(messages, json_mode=json_mode, temperature=temperature,
                            max_tokens=max_tokens, thinking=thinking)
    started = time.time()
    last = None
    for attempt in range(retries + 1):
        try:
            raw = _post_chat(payload, timeout=timeout)
        except ModelError as exc:
            # 429/500/503 are worth one more try; anything else is final.
            if exc.status in (429, 500, 503) and attempt < retries:
                last = exc
                time.sleep(2 * (attempt + 1))
                continue
            raise
        choice = (raw.get("choices") or [{}])[0]
        content = (choice.get("message") or {}).get("content") or ""
        finish = choice.get("finish_reason")
        if not content.strip():
            # Docs warn JSON Output can occasionally return empty content.
            if attempt < retries:
                last = ModelError("模型返回了空内容（JSON Output 偶发），已重试")
                continue
            raise ModelError("模型返回了空内容（finish_reason=%r）" % finish)
        return {
            "content": content,
            "model": raw.get("model") or payload["model"],
            "usage": raw.get("usage") or {},
            "finish_reason": finish,
            "seconds": round(time.time() - started, 2),
            "json_mode": bool(json_mode),
        }
    raise last or ModelError("call failed")


def ping(timeout=60):
    """One tiny real call, for checking a key. Used by code/check_deepseek.py."""
    answer = chat(
        [{"role": "user", "content": "Reply with exactly: ok"}],
        temperature=0.0, max_tokens=8, timeout=timeout, thinking=False, retries=0,
    )
    return answer
