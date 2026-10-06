"""A page, a small Python server, a real model, and the Week 3 archive.

    python app/server.py                 then open http://localhost:8000
    PORT=8765 python app/server.py       if 8000 is already in use
    WEEK5_MODE=fixture python app/server.py   offline, and it says so on the page

Standard library only. Nothing to install. The server binds 127.0.0.1 only.

Routes
    GET  /              the page
    GET  /api/health    which mode is running, which database, how many rows
    POST /api/ask       {"question": "..."} -> the whole auditable record
"""

import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import archive      # noqa: E402
import clerk        # noqa: E402
import model        # noqa: E402

PORT = int(os.environ.get("WEEK5_PORT") or os.environ.get("PORT") or "8000")
MAX_BODY = 8 * 1024


def health() -> dict:
    counts = archive.counts()
    prov = clerk.provider()
    return {
        "mode": prov.source,
        "model": prov.name,
        "key_present": model.key_present(),
        "database": str(archive.db_path()),
        "rows": counts,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "mersey-clerk/1.0"

    # ---- helpers -------------------------------------------------------
    def send(self, status, body: bytes, kind: str):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, obj):
        self.send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                  "application/json; charset=utf-8")

    def fail(self, status, kind, message, hint=None):
        self.send_json(status, {"error": {"kind": kind, "message": message, "hint": hint}})

    # ---- routes --------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            page = (HERE / "static" / "index.html").read_bytes()
            return self.send(200, page, "text/html; charset=utf-8")
        if path == "/api/health":
            try:
                return self.send_json(200, health())
            except Exception as exc:                      # noqa: BLE001
                return self.fail(500, "archive", str(exc))
        if path == "/favicon.ico":
            return self.send(204, b"", "image/x-icon")
        self.fail(404, "not_found", "no such path: %s" % path)

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/api/ask":
            return self.fail(404, "not_found", "no such path: %s" % path)

        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return self.fail(400, "bad_request", "empty body; send {\"question\": \"...\"}")
        if length > MAX_BODY:
            return self.fail(413, "bad_request", "body too large")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            question = (payload.get("question") or "").strip()
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return self.fail(400, "bad_request", "body must be JSON: %s" % exc)

        try:
            record = clerk.answer(question, mode=os.environ.get("WEEK5_MODE"))
        except ValueError as exc:
            return self.fail(400, "bad_question", str(exc))
        except clerk.FixtureError as exc:
            return self.fail(409, "fixture_miss", str(exc),
                             "设置 DEEPSEEK_API_KEY 后即可自由提问。")
        except archive.UnsafeQuery as exc:
            return self.fail(502, "unsafe_sql",
                             "模型给出的查询被守卫拒绝：%s" % exc,
                             "这是模型没守规矩，不是你的问题；重问一次通常就好。")
        except archive.ArchiveError as exc:
            return self.fail(500, "archive", str(exc))
        except model.ModelError as exc:
            return self.fail(502, "model", str(exc))
        except Exception as exc:                          # noqa: BLE001
            traceback.print_exc()
            return self.fail(500, "unexpected", "%s: %s" % (type(exc).__name__, exc))

        return self.send_json(200, record)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def banner():
    prov = clerk.provider()
    counts = archive.counts()
    print("=" * 72)
    print("The Mersey Clerk  ·  DHG508 Week 5")
    print("=" * 72)
    print("  archive   %s  (%d rows)" % (archive.db_path(), counts["total"]))
    if prov.source == "deepseek":
        print("  model     %s  (DEEPSEEK_API_KEY found)" % prov.name)
    else:
        print("  model     %s" % prov.name)
        print("            DEEPSEEK_API_KEY is not set -> offline, saved answers only.")
        print("            Set it and restart for real answers:")
        print('              $env:DEEPSEEK_API_KEY = "sk-..."')
    print("  open      http://localhost:%d" % PORT)
    print("=" * 72)


if __name__ == "__main__":
    banner()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
