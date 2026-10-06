"""The Mersey Clerk as a program: question -> SQL -> rows -> grounded answer.

Three steps, and the model never sees the archive except through the middle one:

    1. plan     the model reads the schema + a truncated index and writes ONE
                read-only SQL query
    2. look up  that query really runs against history.db (read-only)
    3. compose  the model sees the question and the rows that came back —
                nothing else — and answers with [id] citations

The rules in ../skills/mersey-clerk/principles.md are implemented here:

    rule 1 (only the archive answers) -> the compose step is handed rows, not a database
    rule 3 (no rows, no answer)       -> verdict "not_in_archive" is a first-class outcome
    rule 4/5 (report uncertainty)     -> the `note` column travels with every row

Two providers, and the difference is always visible in the response:

    DeepSeekProvider  a real API call (see model.py)
    FixtureProvider   saved answers, labelled "fixture" — never passed off as a model

The demo's whole problem was that the fixture was indistinguishable from a model.
Here `provider.source` ends up on the page.
"""

import json
import os
import re
from pathlib import Path

import archive
import model

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures" / "offline-answers.json"

PLAN_SYSTEM = """你是「默西书记官」(The Mersey Clerk) 的档案检索员。你唯一的工作，是把用户的问题
翻译成一条 SQLite 只读查询。

规矩（出自 skills/mersey-clerk/principles.md）：
1. 只认卷宗 history.db 里的行。不要凭记忆回答，也不要在这里回答问题——你只写查询，
   事实由查出来的行提供。
2. 只写一条 SELECT（可用 WITH 开头）。不得出现 INSERT / UPDATE / DELETE / DROP / ALTER /
   CREATE / ATTACH / PRAGMA 等任何写操作，也不要写多条语句。
3. 命不中就是命不中。若问题无法用这些表回答（问卷宗之外的年份、问乘客姓名、问与卷宗无关的事），
   仍然返回一条**会返回 0 行**的查询，并把 out_of_scope 设为 true，在 why 里说明为什么没有。
   不要为了凑出结果而换成不相干的词去查。
4. 列名必须真实存在（见下方表结构）。宁可先查 v_events_full 这张已经联好出处的视图。
5. 尽量把回答问题所需的一切都取出来：v_events_full 的 id、date_normalized、event、
   source、locator、note；需要引文原文或规范化规则时再联 events。

输出必须是 json，格式：
{"sql": "SELECT ...", "why": "一句话：这条查询在找什么", "out_of_scope": false}
"""

COMPOSE_SYSTEM = """你是 1912 年英国沉船调查庭（Lord Mersey 主持）的书记官，人称 The Mersey Clerk。
你面前只有一份查询结果，那就是你此刻全部的卷宗。

规矩（出自 skills/mersey-clerk/principles.md）：
1. 只用给出的行作答。每条事实后附行号 [id]（图片用 [img id]），并且**只许引用给出过的行号**。
2. 行里的 note 是存疑与冲突记录：原样转述，不替史料裁决；数值冲突并列给出。
   先分清「口径不同」与「史料矛盾」（例：712 是自艇上救起、其中 1 人随后死亡，
   711 是最终获救——不是矛盾）。
3. 若结果为空：开头写「这本卷宗里没有。」并说明**为什么**没有（卷宗只到 1912 年 7 月 /
   不载乘客姓名 / 无此原话），verdict 记 not_in_archive。绝不用卷外常识补，也不要编造数字。
4. 语气庄重、克制、简洁；不寒暄、不臆测、不说自己是模型或 AI；用提问者的语言回答。
5. 事实较多时按时间或 id 排列，最多先列 6 条，其余归类陈述。
6. 结尾另起一行给出处：文献 code + locator（如 GB39415 L3302-3308）。

输出必须是 json，格式：
{"answer": "……", "verdict": "answered", "cited_ids": [24, 25]}
（verdict 只取 answered 或 not_in_archive；cited_ids 只列你真的引用过的 [id]，可为空数组。）
"""


# --------------------------------------------------------------------------
# prompts


def plan_prompt(question: str, path=None) -> list:
    schema = archive.schema_text(path)
    index = archive.catalogue(path=path)
    counts = archive.counts(path)
    body = [
        "## 卷宗表结构（真实 DDL）",
        "",
        "```sql",
        schema,
        "```",
        "",
        "## 行数",
        "",
        json.dumps(counts, ensure_ascii=False),
        "",
        "## 档案索引（每条事实的 id / 日期 / 出处 / 前 70 字，完整正文要靠 SQL 取）",
        "",
        "```json",
        json.dumps(index, ensure_ascii=False),
        "```",
        "",
        "## 中文关键词提示",
        "",
        "event 是中文摘述，quote 是英文原句。常用词：救生艇、冰山、水密舱壁、瞭望、"
        "火箭、获救、沉没、建议、船长、船员、乘客、Carpathian/Carpathia、Californian、"
        "Lord、Murdoch、Ismay、Smith、Lightoller。人名规范形是「姓, 名」。",
        "",
        "## 问题",
        "",
        question,
    ]
    return [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": "\n".join(body)},
    ]


def compose_prompt(question: str, plan: dict, result: dict) -> list:
    evidence = {
        "sql_run": result["sql"],
        "rows_returned": result["returned"],
        "rows": result["rows"],
    }
    body = [
        "## 问题",
        "",
        question,
        "",
        "## 检索说明",
        "",
        (plan.get("why") or "").strip() or "（模型未给出说明）",
        "",
        "## 查询结果（这就是你全部的卷宗；共 %d 行）" % result["returned"],
        "",
        "```json",
        json.dumps(evidence, ensure_ascii=False, indent=1),
        "```",
    ]
    return [
        {"role": "system", "content": COMPOSE_SYSTEM},
        {"role": "user", "content": "\n".join(body)},
    ]


# --------------------------------------------------------------------------
# parsing


_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


def parse_json(text: str) -> dict:
    """Parse the model's JSON, tolerating code fences and stray prose."""
    cleaned = _FENCE.sub("", (text or "").strip())
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError as exc:
            raise model.ModelError("模型的输出不是可解析的 JSON：%s" % exc) from exc
    raise model.ModelError("模型的输出里找不到 JSON 对象")


# --------------------------------------------------------------------------
# providers


class DeepSeekProvider:
    """A real API call, twice: once to plan the query, once to write the answer."""

    source = "deepseek"

    def __init__(self, chat=None):
        self._chat = chat or model.chat

    @property
    def name(self) -> str:
        return model.model_name()

    def plan(self, question: str, path=None) -> dict:
        reply = self._chat(plan_prompt(question, path), json_mode=True,
                           temperature=0.0, max_tokens=1024)
        data = parse_json(reply["content"])
        return {
            "sql": (data.get("sql") or "").strip(),
            "why": (data.get("why") or "").strip(),
            "out_of_scope": bool(data.get("out_of_scope")),
            "call": reply,
        }

    def compose(self, question: str, plan: dict, result: dict) -> dict:
        reply = self._chat(compose_prompt(question, plan, result), json_mode=True,
                           temperature=0.2, max_tokens=2048)
        data = parse_json(reply["content"])
        verdict = data.get("verdict") or ("answered" if result["returned"] else "not_in_archive")
        return {
            "text": (data.get("answer") or "").strip(),
            "verdict": verdict if verdict in ("answered", "not_in_archive") else "answered",
            "cited_ids": [int(i) for i in (data.get("cited_ids") or []) if str(i).lstrip("-").isdigit()],
            "call": reply,
        }


class FixtureProvider:
    """Saved answers, used when there is no key or WEEK5_MODE=fixture.

    It is a **fixture** and says so: `source` is "fixture", the name is
    "offline fixture (not a model)", and the page shows a warning band. The
    SQL in the fixture is still really executed against history.db, so the rows
    on screen are genuine archive rows.
    """

    source = "fixture"
    name = "offline fixture (not a model)"

    def __init__(self, path=None):
        self.path = Path(path) if path else FIXTURES
        self.data = json.loads(self.path.read_text(encoding="utf-8"))

    def _find(self, question: str):
        target = _norm(question)
        for key, entry in self.data["answers"].items():
            candidates = [entry.get("question", "")] + list(entry.get("aliases", []))
            if any(_norm(c) == target for c in candidates):
                return key, entry
        return None, None

    def plan(self, question: str, path=None) -> dict:
        key, entry = self._find(question)
        if entry is None:
            raise FixtureError(
                "离线替身里没有这一题的预设答案（它只认识 %d 道示例题）。"
                "设置 DEEPSEEK_API_KEY 后即可自由提问。"
                % len(self.data["answers"])
            )
        return dict(entry["plan"], call=None, fixture_key=key)

    def compose(self, question: str, plan: dict, result: dict) -> dict:
        key = plan.get("fixture_key")
        entry = self.data["answers"][key]
        composed = dict(entry["compose"])
        composed["text"] = composed.pop("answer", "")
        composed["call"] = None
        composed["cited_ids"] = [int(i) for i in composed.get("cited_ids", [])]
        return composed


class FixtureError(Exception):
    """Asked the offline fixture something it has no saved answer for."""


# --------------------------------------------------------------------------
# the pipeline


def _norm(text: str) -> str:
    return re.sub(r"[\s？?。.，,！!、：:；;\"'“”‘’]+", "", (text or "").lower())


def check_citations(cited, rows) -> dict:
    """Every cited id must be an id that the query actually returned."""
    available = {r.get("id") for r in rows}
    cited = list(dict.fromkeys(cited))
    stray = [i for i in cited if i not in available]
    return {"ok": not stray, "cited": cited, "stray": stray,
            "available": sorted(i for i in available if isinstance(i, int))}


def provider(mode: str = None, chat=None):
    """Pick a provider. Never silently: the choice is reported in the response."""
    mode = (mode or os.environ.get("WEEK5_MODE") or "auto").lower()
    if mode == "deepseek":
        return DeepSeekProvider(chat=chat)
    if mode == "fixture":
        return FixtureProvider()
    if mode == "auto":
        return DeepSeekProvider(chat=chat) if model.key_present() else FixtureProvider()
    raise ValueError("WEEK5_MODE must be auto, deepseek or fixture (got %r)" % mode)


def answer(question: str, mode: str = None, chat=None, path=None) -> dict:
    """Run the whole pipeline and return everything the page needs to audit it."""
    question = (question or "").strip()
    if not question:
        raise ValueError("empty question")
    if len(question) > 500:
        raise ValueError("question is too long (500 characters max)")

    prov = provider(mode=mode, chat=chat)
    record = {
        "question": question,
        "model": {"source": prov.source, "name": prov.name, "calls": 0},
        "plan": None,
        "result": None,
        "answer": None,
        "citation_check": None,
    }

    plan = prov.plan(question, path)
    if plan.get("call"):
        _add_usage(record, plan["call"])
    record["plan"] = {"sql": plan.get("sql", ""), "why": plan.get("why", ""),
                      "out_of_scope": bool(plan.get("out_of_scope"))}

    if not plan.get("sql"):
        # Nothing to run: the model decided this is outside the archive.
        result = {"sql": "", "columns": [], "rows": [], "returned": 0, "truncated": False}
    else:
        result = archive.run(plan["sql"], path=path)
    record["result"] = result

    composed = prov.compose(question, plan, result)
    if composed.get("call"):
        _add_usage(record, composed["call"])
    record["answer"] = {"text": composed["text"], "verdict": composed["verdict"],
                        "cited_ids": composed["cited_ids"]}
    record["citation_check"] = check_citations(composed["cited_ids"], result["rows"])
    return record


def _add_usage(record: dict, call: dict) -> None:
    record["model"]["calls"] += 1
    record["model"]["last_seconds"] = call.get("seconds")
    record["model"].setdefault("seconds_total", 0.0)
    record["model"]["seconds_total"] = round(
        record["model"]["seconds_total"] + (call.get("seconds") or 0.0), 2)
    record["model"]["model_reported"] = call.get("model")
    usage = call.get("usage") or {}
    if usage:
        record["model"]["usage"] = usage
