"""让 Week 5 的三个脚本在「被管道捕获」和「用户自己的终端」下都不乱码。

Windows 上 Python 默认按控制台代码页（中文环境通常是 gbk）编码 stdout，于是：

  * 输出被管道捕获时（本仓库的自检、CI、把结果存文件），捕获方按 UTF-8 解码 → 中文成乱码；
  * 输出到用户自己的 PowerShell 窗口时，保持 gbk 反而显示正常。

同一个设置不可能两头都对，所以按 stdout 是不是终端来决定：

    终端（tty）  → 保持控制台编码，只把个别无法编码的字符降级，避免 UnicodeEncodeError
    管道/重定向  → 一律输出 UTF-8（现代工具链的默认解码方式）

stderr 同样处理，否则异常栈里的中文会乱。
"""

import sys


def setup() -> None:
    for stream in (sys.stdout, sys.stderr):
        if not hasattr(stream, "reconfigure"):
            continue
        try:
            if stream.isatty():
                stream.reconfigure(errors="backslashreplace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass
