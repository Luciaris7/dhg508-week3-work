"""把 DeepSeek API key 放进环境变量——不放进任何文件。

    python code/set_key.py --check              # 只看现状，什么都不改
    python code/set_key.py                      # 提示粘贴（不回显），存为用户环境变量
    python code/set_key.py --verify             # 设置完立刻用一次真调用验证
    python code/set_key.py --session --verify   # 什么都不落盘，只试这一次

为什么用 Python 而不是 .ps1：本机是 Windows PowerShell 5.1，执行策略为
RemoteSigned，未签名的 .ps1 会被拦下；而且 5.1 读无 BOM 的 UTF-8 脚本会把中文读成乱码。
Python 3 默认按 UTF-8 读源码，也没有执行策略这一层。

为什么不用 .env 文件：有 .env 就有被误提交的风险。环境变量没有这个问题。
密钥全程不打印（只用长度确认），也不作为命令行参数传给子进程——那样会留在进程表和
命令行历史里。
"""

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

NAME = "DEEPSEEK_API_KEY"
HERE = Path(__file__).resolve().parent
CHECK_SCRIPT = HERE / "check_deepseek.py"

sys.path.insert(0, str(HERE))

import console_setup    # noqa: E402

console_setup.setup()


# ---------------------------------------------------------------- Windows 用户环境变量
def user_env() -> str:
    """读 HKCU\\Environment 里的值（即 setx 写进去的那个位置）。"""
    if os.name != "nt":
        return ""
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, NAME)
            return value or ""
    except (FileNotFoundError, OSError):
        return ""


def set_user_env(value: str) -> None:
    """写用户环境变量。等价于 setx，但不会把密钥暴露在命令行里。"""
    if os.name != "nt":
        raise SystemExit("这个脚本目前只处理 Windows 的用户环境变量。")
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        winreg.SetValueEx(key, NAME, 0, winreg.REG_SZ, value)


# ---------------------------------------------------------------- 显示
def describe(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "未设置"
    return "已设置（%d 个字符，开头 %s…，内容不回显）" % (len(value), value[:3])


def report() -> bool:
    process = os.environ.get(NAME, "")
    user = user_env()
    print()
    print("  DeepSeek 密钥现状")
    print("    %-30s %s" % ("当前进程 (os.environ)", describe(process)))
    print("    %-30s %s" % ("用户环境变量 (持久)", describe(user)))
    print()
    return bool(process.strip() or user.strip())


# ---------------------------------------------------------------- 读入
def read_key(explicit: str | None) -> str:
    if explicit:
        print("  提醒：--key 会把密钥写进命令行历史，只建议自动化使用。")
        return explicit
    if not sys.stdin.isatty():
        # 管道进来（自动化用）
        return sys.stdin.readline()
    try:
        return getpass.getpass("  粘贴密钥后回车（输入不回显；Ctrl+C 取消）: ")
    except (KeyboardInterrupt, EOFError):
        print("\n  已取消，什么都没改。")
        raise SystemExit(1)


# ---------------------------------------------------------------- 主流程
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="把 DeepSeek API key 放进环境变量（Week 5）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="只报告现状，不做修改")
    parser.add_argument("--session", action="store_true",
                        help="只在本次运行里使用，不写入用户环境变量（配合 --verify 做无痕测试）")
    parser.add_argument("--verify", action="store_true",
                        help="设置完后立刻跑一次真实 API 调用（消耗几枚 token）")
    parser.add_argument("--ask", default="到底救了多少人？",
                        help="配合 --verify：要问卷宗的问题")
    parser.add_argument("--key", default=None,
                        help="直接给密钥（会留在命令行历史里，慎用）")
    args = parser.parse_args(argv)

    if args.check:
        if report():
            print("  接着可以跑（真调用，花几枚 token）：")
            print('      python code\\check_deepseek.py --ask "到底救了多少人？"')
            print("  提醒：已经在跑的服务器不会读到新密钥，要重启才会生效。")
        else:
            print("  还没有密钥。先在 https://platform.deepseek.com/api_keys 建一个。")
        print()
        return 0

    print()
    print("  DeepSeek API key -> 环境变量")
    print("  建 key: https://platform.deepseek.com/api_keys")
    print()

    key = (read_key(args.key) or "").strip()   # 剪贴板常带空格/换行，这是 401 最常见的原因
    if not key:
        print("  没有读到内容，什么都没改。")
        return 1

    length = len(key)
    looks_right = key.startswith("sk-") and length >= 20

    if args.session:
        os.environ[NAME] = key
        where = "本次运行（不落盘，进程结束即消失）"
    else:
        os.environ[NAME] = key          # 让本次校验立即可用
        set_user_env(key)
        where = "用户环境变量（持久；新开的窗口才读得到）"

    del key                            # 不留住明文
    del args.key

    print()
    print("  已写入 %s：%d 个字符" % (where, length))
    if not looks_right:
        print("  提醒：它不像常见的 sk- 开头格式；抄漏了会得到 401。")

    status = 0
    if args.verify:
        print()
        print("  正在用真调用验证（几枚 token）…")
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        status = subprocess.call(
            [sys.executable, str(CHECK_SCRIPT), "--ask", args.ask], env=env)
        print()
        if status == 0:
            print("  验证通过。接着重启应用服务器：python app\\server.py")
        else:
            print("  验证没通过，看上面的错误提示（401 = 密钥抄错，402 = 余额不足）。")
        return status

    print()
    print("  下一步：")
    print("      1) 验证密钥能真的调用（花几枚 token）")
    print('         python code\\check_deepseek.py --ask "到底救了多少人？"')
    print("      2) 重启应用服务器（已经在跑的那个不会读到新密钥）")
    print("         python app\\server.py")
    print("      3) 打开 http://localhost:8000 —— 顶部黄色警示条应当消失")
    print()
    print("  密钥不在任何文件里，也不会被 git 看见。")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
