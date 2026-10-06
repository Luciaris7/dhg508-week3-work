"""启动前检查（由 启动网页.bat 调用）。

分工：

    启动网页.bat   读密钥 -> 调用本脚本做检查 -> 在本窗口里直接运行服务器
    launch.py      只做检查：服务器是不是已经在跑、密钥有没有读到、要不要开浏览器

为什么服务器不再用 `start` 分离出去：

    `start` 分离出来的进程在 DSH 沙箱的 job 对象里会被连带杀掉（实测：
    服务器确实起来了并 LISTENING，但上级命令一结束就没了）。更稳的做法是
    把服务器放在启动器自己的窗口里跑 —— 窗口开着服务器就活着，关窗口即停止，
    这也正是 USAGE.md 里写的用法。

密钥从注册表读的原因：双击 .bat 起的新进程继承的是资源管理器那套环境，
可能是几小时前的旧值；注册表才是权威。读不到密钥服务器会静默退回「离线替身」，
只答 5 道示例题 —— 课堂上那是事故，所以 .bat 会明确警告。
"""

import json
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE / "app" / "server.py"
URL = "http://localhost:8000"
WAIT_SECONDS = 40


def say(msg=""):
    print(msg, flush=True)


def health(timeout=3.0):
    """Return the /api/health body, or None if nothing is listening."""
    try:
        with urllib.request.urlopen(URL + "/api/health", timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError):
        return None


def wait_ready(seconds=WAIT_SECONDS):
    """Poll until the server answers. Returns the health body or None."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        time.sleep(0.5)
        body = health()
        if body:
            return body
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    wait_open = "--wait-open" in sys.argv

    if not SERVER.is_file():
        say("  [X] 找不到服务器程序：%s" % SERVER)
        say("      启动器必须留在 week5 文件夹里。")
        return 1

    # --wait-open：由 .bat 在后台调用，等服务器起来再开浏览器。
    # 页面只在加载时查一次 /api/health（不自动重试），所以浏览器必须等服务器
    # 真的开始应答之后再打开，否则你会看到一个「打不开服务」的页面。
    if wait_open:
        body = wait_ready()
        if body:
            say("  [OK] 服务器已就绪：%s" % body.get("model"))
            webbrowser.open(URL)
            return 0
        say("  [X] 等了 %d 秒服务器仍无应答，未打开浏览器。" % WAIT_SECONDS)
        return 1

    # 已经在跑？那就别再开一个。
    body = health()
    if body:
        say()
        say("  [i] 服务器已经在运行，直接使用它。")
        say("      模式     %s" % body.get("model"))
        say("      卷宗     %s" % body.get("database"))
        say("      行数     %s" % (body.get("rows") or {}).get("total"))
        if body.get("mode") != "deepseek":
            say()
            say("  [!] 注意：现在不是真模型模式，页面上会有黄色警示条。")
        say()
        say("  正在打开浏览器：%s" % URL)
        webbrowser.open(URL)
        return 0

    say()
    say("  服务器还没起来，稍后由后台等待器打开浏览器。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
