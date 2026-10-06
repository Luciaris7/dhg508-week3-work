"""停止服务器（由 停止网页.bat 调用）。

服务器现在跑在「启动网页.bat」那个窗口里，所以在那个窗口按 Ctrl+C 就能停。
本脚本是给「窗口找不到了 / 想确认到底还有没有在跑」准备的：它按「谁在监听
8000 端口」找到进程并结束，不需要记 PID。
"""

import sys


def say(msg=""):
    print(msg, flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    say("=" * 68)
    say("  Mersey Clerk  停止服务器   DHG508 Week 5")
    say("=" * 68)

    import subprocess

    try:
        import psutil
    except ImportError:
        psutil = None

    if psutil is None:
        # 只用标准库：跑 netstat 找监听 8000 的进程
        try:
            out = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=30
            ).stdout
        except (OSError, subprocess.SubprocessError) as exc:
            say()
            say("  [X] 无法执行 netstat：%s" % exc)
            return 1

        pids = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 4 and parts[0].upper() == "TCP" and parts[3].upper() == "LISTENING":
                if parts[1].endswith(":8000"):
                    pid = parts[-1]
                    if pid.isdigit() and pid not in pids:
                        pids.append(pid)
    else:
        pids = []
        for conn in psutil.net_connections(kind="tcp"):
            if conn.status == "LISTEN" and conn.laddr and conn.laddr.port == 8000:
                if conn.pid and str(conn.pid) not in pids:
                    pids.append(str(conn.pid))

    if not pids:
        say()
        say("  [i] 没有程序在监听 8000 端口 —— 服务器本来就没在跑。")
        say()
        return 0

    say()
    say("  发现 %d 个在 8000 端口上的进程：%s" % (len(pids), ", ".join(pids)))

    killed = 0
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/PID", pid, "/F"],
                           capture_output=True, text=True, timeout=30)
            killed += 1
            say("  [OK] 已结束进程 %s" % pid)
        except (OSError, subprocess.SubprocessError) as exc:
            say("  [X] 结束 %s 失败：%s" % (pid, exc))

    say()
    if killed:
        say("  服务器已停止。页面刷新后会显示「打不开服务」，这是正常的。")
    say()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(1)
