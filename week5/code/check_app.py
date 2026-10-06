"""Self-check for Week 5. Runs offline: no API key, no network, no cost.

    python code/check_app.py

It proves four things:

  A. the archive is opened READ-ONLY (a write is attempted and must fail)
  B. the SQL guard refuses writes, multiple statements and empty input
  C. the clerk really is grounded: the composing step is handed *only* the rows
     that the query returned, nothing else — checked with a stub model
  D. the whole thing works over HTTP, including the honest failure of the
     offline fixture when it is asked something it does not know

Exit code 0 = all checks passed.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "app"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(APP))

import console_setup    # noqa: E402
import archive          # noqa: E402
import clerk            # noqa: E402
import model            # noqa: E402

console_setup.setup()

PASS, FAIL = [], []


def check(name, condition, detail=""):
    (PASS if condition else FAIL).append(name)
    print("  %s %s%s" % ("PASS" if condition else "FAIL", name,
                         ("  — " + detail) if detail and not condition else ""))
    return bool(condition)


def section(title):
    print("\n" + title)
    print("-" * len(title))


EXPECTED_COUNTS = {"sources": 3, "places": 17, "people": 26, "events": 97,
                   "event_people": 61, "images": 6, "image_events": 13, "total": 223}


# ---------------------------------------------------------------- A
def check_archive():
    section("A. 卷宗是只读打开的")
    check("history.db 存在", archive.db_path().is_file(), str(archive.db_path()))
    counts = archive.counts()
    check("行数与 Week 3 一致（223 行 7 表）", counts == EXPECTED_COUNTS, str(counts))

    con = archive.connect()
    try:
        con.execute("SELECT COUNT(*) FROM events").fetchone()
        check("能读 events", True)
        for statement, label in (
            ("INSERT INTO events (id, event, source_id, locator) VALUES (9999,'x',1,'L1-1')", "INSERT"),
            ("UPDATE events SET year = 1 WHERE id = 1", "UPDATE"),
            ("DELETE FROM events WHERE id = 1", "DELETE"),
            ("DROP TABLE events", "DROP"),
        ):
            try:
                con.execute(statement)
                con.rollback()
                check("%s 被 SQLite 拒绝（只读连接）" % label, False, "居然执行成功了")
            except Exception:
                check("%s 被 SQLite 拒绝（只读连接）" % label, True)
    finally:
        con.close()


# ---------------------------------------------------------------- B
def check_guard():
    section("B. SQL 守卫")
    bad = {
        "空语句": "",
        "空白": "   ",
        "DROP 语句": "DROP TABLE events",
        "非 SELECT 开头": "EXPLAIN SELECT 1",
        "两条语句": "SELECT 1; DROP TABLE events",
        "WITH 后面接 DELETE": "WITH x AS (SELECT 1) DELETE FROM events",
        "PRAGMA": "SELECT * FROM events WHERE 1=1 PRAGMA table_info(events)",
        "INSERT": "INSERT INTO events VALUES (1)",
        "REPLACE INTO": "REPLACE INTO events (id) VALUES (1)",
    }
    for label, sql in bad.items():
        try:
            archive.guard(sql)
            check("拒绝 %s" % label, False, "守卫放行了")
        except archive.UnsafeQuery:
            check("拒绝 %s" % label, True)

    good = {
        "普通 SELECT": "SELECT * FROM events",
        "WITH 开头": "WITH x AS (SELECT 1 AS a) SELECT * FROM x",
        "结尾带分号": "SELECT id FROM events;",
        "含 replace() 函数": "SELECT replace(event,'a','b') FROM events",
    }
    for label, sql in good.items():
        try:
            archive.guard(sql)
            check("放行 %s" % label, True)
        except archive.UnsafeQuery as exc:
            check("放行 %s" % label, False, str(exc))

    result = archive.run("SELECT id, event FROM events ORDER BY id", max_rows=3)
    check("run() 真查到行", result["returned"] == 3, str(result["returned"]))
    check("run() 标出截断", result["truncated"] is True)
    check("run() 返回列名", result["columns"] == ["id", "event"], str(result["columns"]))


# ---------------------------------------------------------------- C
def check_grounding():
    section("C. 有据：落笔这一步只看到查出来的行")
    seen = {}

    def stub(messages, **kwargs):
        seen.setdefault("prompts", []).append(messages)
        if len(seen["prompts"]) == 1:
            return {"content": json.dumps({
                "sql": "SELECT id, date_normalized, event, source, locator, note "
                       "FROM v_events_full WHERE id = 24",
                "why": "取第 24 行", "out_of_scope": False}),
                "model": "stub", "usage": {"total_tokens": 1}, "seconds": 0.01}
        return {"content": json.dumps({
            "answer": "据卷宗：Californian 号船长为 Stanley Lord [24]。",
            "verdict": "answered", "cited_ids": [24]}),
            "model": "stub", "usage": {"total_tokens": 1}, "seconds": 0.01}

    record = clerk.answer("加州人号的船长是谁？", mode="deepseek", chat=stub)
    check("两次模型调用", record["model"]["calls"] == 2, str(record["model"]["calls"]))
    check("用的是 deepseek 通道", record["model"]["source"] == "deepseek")
    check("查询返回 1 行", record["result"]["returned"] == 1, str(record["result"]["returned"]))
    check("引证核对通过", record["citation_check"]["ok"] is True,
          str(record["citation_check"]))

    compose_prompt = seen["prompts"][1][1]["content"]
    check("落笔提示里含被检索到的行（Stanley Lord）", "Stanley Lord" in compose_prompt)
    check("落笔提示里不含未被检索到的行（15 道横向水密舱壁）",
          "15 道横向水密舱壁" not in compose_prompt,
          "模型看到了不该看到的行")
    plan_prompt = seen["prompts"][0][1]["content"]
    check("写查询的提示里含真实表结构", "CREATE TABLE events" in plan_prompt)
    check("索引是截断的：第 94 行的开头在、结尾不在",
          "Californian 号详情" in plan_prompt and "与泰坦尼克同一母公司" not in plan_prompt,
          "全文泄进了写查询的提示，截断索引失效")

    section("C2. 引证核对会抓出编造的行号")

    def lying_stub(messages, **kwargs):
        if messages[0]["content"] == clerk.PLAN_SYSTEM:
            return {"content": json.dumps({
                "sql": "SELECT id, event, source, locator, note FROM v_events_full WHERE id = 24",
                "why": "取第 24 行", "out_of_scope": False}), "seconds": 0.01}
        return {"content": json.dumps({
            "answer": "据卷宗：……[24][999]。", "verdict": "answered",
            "cited_ids": [24, 999]}), "seconds": 0.01}

    record = clerk.answer("加州人号的船长是谁？", mode="deepseek", chat=lying_stub)
    check("抓到未返回的 [999]", record["citation_check"]["ok"] is False)
    check("指认的正是 999", record["citation_check"]["stray"] == [999],
          str(record["citation_check"]))


# ---------------------------------------------------------------- D
def check_fixtures():
    section("D. 离线替身：真跑 SQL，身份公开，不会的题就说不认识")
    prov = clerk.provider(mode="fixture")
    check("替身自称 fixture", prov.source == "fixture" and "not a model" in prov.name,
          prov.name)

    expected = {
        "californian-captain": (7, "answered"),
        "lifeboats-why-few": (7, "answered"),
        "how-many-saved": (4, "answered"),
        "bulkheads-17": (2, "answered"),
        "wreck-1985": (0, "not_in_archive"),
    }
    data = json.loads(clerk.FIXTURES.read_text(encoding="utf-8"))
    for key, entry in data["answers"].items():
        record = clerk.answer(entry["question"], mode="fixture")
        want_rows, want_verdict = expected[key]
        check("[%s] %s" % (key, entry["question"][:22]),
              record["result"]["returned"] == want_rows
              and record["answer"]["verdict"] == want_verdict
              and record["citation_check"]["ok"],
              "rows=%s verdict=%s cites=%s"
              % (record["result"]["returned"], record["answer"]["verdict"],
                 record["citation_check"]))

    try:
        clerk.answer("随便问一个替身没存档的问题", mode="fixture")
        check("替身拒绝没存档的问题", False, "它居然答了")
    except clerk.FixtureError:
        check("替身拒绝没存档的问题", True)


# ---------------------------------------------------------------- E
def check_http():
    section("E. HTTP 全链路（离线模式，端口 8799）")
    port = 8799
    log = Path(tempfile.gettempdir()) / "week5_server_check.log"
    env = dict(os.environ, WEEK5_MODE="fixture", WEEK5_PORT=str(port),
               PYTHONIOENCODING="utf-8")
    env.pop("DEEPSEEK_API_KEY", None)
    with open(log, "w", encoding="utf-8") as handle:
        proc = subprocess.Popen([sys.executable, str(APP / "server.py")],
                                stdout=handle, stderr=handle, env=env,
                                cwd=str(APP.parent))
    base = "http://127.0.0.1:%d" % port
    try:
        health = None
        for _ in range(40):
            time.sleep(0.25)
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=3) as r:
                    health = json.loads(r.read().decode("utf-8"))
                break
            except Exception:
                continue
        if not check("服务器起来了（/api/health）", health is not None, log.read_text()[-400:] if log.exists() else ""):
            return

        check("health 报告 fixture 模式", health["mode"] == "fixture", str(health))
        check("health 报告 223 行", health["rows"]["total"] == 223, str(health["rows"]))
        check("health 报告数据库路径", health["database"].endswith("history.db"))

        with urllib.request.urlopen(base + "/", timeout=5) as r:
            page = r.read().decode("utf-8")
        check("GET / 返回页面", "向" in page and "卷宗" in page, page[:80])

        body = json.dumps({"question": "泰坦尼克号残骸是哪一年被发现的？"}).encode("utf-8")
        request = urllib.request.Request(base + "/api/ask", data=body,
                                        headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=20) as r:
            answer = json.loads(r.read().decode("utf-8"))
        check("POST /api/ask 返回完整记录",
              {"question", "model", "plan", "result", "answer", "citation_check"} <= set(answer),
              str(sorted(answer)))
        check("拒答题：命中 0 行且 verdict=not_in_archive",
              answer["result"]["returned"] == 0
              and answer["answer"]["verdict"] == "not_in_archive", str(answer["answer"]))
        check("页面能据此亮出替身警告", answer["model"]["source"] == "fixture")

        body = json.dumps({"question": "替身没存档的问题"}).encode("utf-8")
        request = urllib.request.Request(base + "/api/ask", data=body,
                                        headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(request, timeout=20)
            check("没存档的问题返回 409", False, "居然返回了 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            check("没存档的问题返回 409 fixture_miss",
                  exc.code == 409 and payload["error"]["kind"] == "fixture_miss",
                  "%s %s" % (exc.code, payload))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("\n  服务器日志：%s" % log)


def check_deepseek_wire():
    """Verify the request we would send matches the published API contract,
    without touching the network. The real call still needs a real key."""
    section("F. 真实调用的报文形状（假 urlopen 截住，不走网络）")
    import io
    import urllib.error

    captured = {}

    class FakeResponse:
        def __init__(self, payload):
            self._data = json.dumps(payload).encode("utf-8")

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["headers"] = {k.lower(): v for k, v in request.header_items()}
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({
            "id": "chatcmpl-test", "object": "chat.completion", "created": 0,
            "model": "deepseek-flash",
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant",
                                     "content": json.dumps({"sql": "SELECT 1", "why": "t",
                                                            "out_of_scope": False})}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
        })

    original_urlopen = urllib.request.urlopen
    original_key = os.environ.get("DEEPSEEK_API_KEY")
    os.environ["DEEPSEEK_API_KEY"] = "sk-test-not-a-real-key"
    messages = [{"role": "user", "content": "json please"}]
    try:
        urllib.request.urlopen = fake_urlopen
        reply = model.chat(messages, json_mode=True, temperature=0.0, max_tokens=64)
        error = None
    except Exception as exc:                              # noqa: BLE001
        reply, error = None, exc
    finally:
        urllib.request.urlopen = original_urlopen
        if original_key is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = original_key

    if not check("model.chat() 能跑通（用假响应）", reply is not None, str(error)):
        return

    payload = captured["payload"]
    check("端点正确", captured["url"] == "https://api.deepseek.com/chat/completions",
          captured["url"])
    check("带 Bearer 密钥", captured["headers"].get("authorization")
          == "Bearer sk-test-not-a-real-key", str(captured["headers"]))
    check("Content-Type 是 json", captured["headers"].get("content-type") == "application/json")
    check("默认模型 deepseek-flash", payload["model"] == "deepseek-flash", payload["model"])
    check("stream=False", payload["stream"] is False)
    check("非思考模式（thinking.type=disabled）",
          payload["thinking"] == {"type": "disabled"}, str(payload.get("thinking")))
    check("json_mode 会带 response_format",
          payload["response_format"] == {"type": "json_object"}, str(payload.get("response_format")))
    check("原样传 messages", payload["messages"] == messages)
    check("max_tokens 生效", payload["max_tokens"] == 64)
    check("解析出 content", reply["content"].startswith("{"), reply["content"][:40])
    check("解析出 usage", reply["usage"]["total_tokens"] == 18, str(reply["usage"]))
    check("记录耗时", isinstance(reply["seconds"], float))

    # error mapping, per https://api-docs.deepseek.com/quick_start/error_codes
    def failing(code):
        def raiser(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, code, "boom", {},
                                         io.BytesIO(b'{"error":{"message":"x"}}'))
        return raiser

    checks = {401: "密钥", 402: "余额", 429: "过快", 503: "过载"}
    for code, keyword in checks.items():
        os.environ["DEEPSEEK_API_KEY"] = "sk-test-not-a-real-key"
        try:
            urllib.request.urlopen = failing(code)
            model.chat(messages, retries=0)
            check("HTTP %d 被换成 ModelError 并给出去处" % code, False, "没抛错")
        except model.ModelError as exc:
            check("HTTP %d -> %s" % (code, keyword), exc.status == code and keyword in str(exc),
                  str(exc))
        except Exception as exc:                          # noqa: BLE001
            check("HTTP %d 被换成 ModelError" % code, False, repr(exc))
        finally:
            urllib.request.urlopen = original_urlopen
            if original_key is None:
                os.environ.pop("DEEPSEEK_API_KEY", None)
            else:
                os.environ["DEEPSEEK_API_KEY"] = original_key

    os.environ.pop("DEEPSEEK_API_KEY", None)
    try:
        model.chat(messages, retries=0)
        check("没有密钥时拒绝假装有模型", False, "它居然发请求了")
    except model.ModelError as exc:
        check("没有密钥时拒绝假装有模型", "DEEPSEEK_API_KEY" in str(exc), str(exc))
    finally:
        if original_key is not None:
            os.environ["DEEPSEEK_API_KEY"] = original_key


def main():
    print("=" * 72)
    print("Week 5 自检 · 不需要 API key、不联网、不花钱")
    print("=" * 72)
    print("  数据库：%s" % archive.db_path())
    check_archive()
    check_guard()
    check_grounding()
    check_fixtures()
    check_http()
    check_deepseek_wire()

    print("\n" + "=" * 72)
    print("通过 %d 项，失败 %d 项" % (len(PASS), len(FAIL)))
    if FAIL:
        for name in FAIL:
            print("  FAIL  %s" % name)
    print("=" * 72)
    print("真实 API 调用不在这里测（需要密钥）：python code\\check_deepseek.py")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
