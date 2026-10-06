"""Check a real DeepSeek key, then optionally run one real question end to end.

    python code/check_deepseek.py
    python code/check_deepseek.py --ask "到底救了多少人？"

This is the only script here that talks to the network and spends API credit.
It makes one minimal call (a few tokens) and, with --ask, two more.

Why this file exists: the app's real call cannot be verified without a key, so
this is the one-command way for the human who owns the key to verify it.
"""

import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "app"
sys.path.insert(0, str(APP))

import archive      # noqa: E402
import clerk        # noqa: E402
import model        # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main(argv):
    question = None
    if "--ask" in argv:
        index = argv.index("--ask")
        question = argv[index + 1] if index + 1 < len(argv) else "到底救了多少人？"

    print("=" * 72)
    print("真实 DeepSeek 调用自检")
    print("=" * 72)
    print("  base_url : %s" % model.base_url())
    print("  model    : %s" % model.model_name())
    print("  thinking : %s" % ("on" if model.thinking_enabled() else "off"))
    print("  key      : %s" % ("已从环境变量读到（长度 %d，不回显）" % len(model.api_key())
                               if model.key_present() else "**没有找到**"))
    print("  archive  : %s" % archive.db_path())

    if not model.key_present():
        print()
        print("没有 DEEPSEEK_API_KEY，未发起任何请求。")
        print("先在 https://platform.deepseek.com/api_keys 建一个 key，然后：")
        print()
        print('  $env:DEEPSEEK_API_KEY = "sk-xxxxxxxx"     # 仅当前窗口')
        print('  setx DEEPSEEK_API_KEY "sk-xxxxxxxx"        # 长期保存，新开窗口生效')
        print()
        print("密钥只从环境变量读，不要写进任何会被提交的文件。")
        return 2

    print("\n[1/2] 最小调用（几枚 token）…")
    started = time.time()
    try:
        reply = model.ping()
    except model.ModelError as exc:
        print("\n失败：%s" % exc)
        return 1
    print("  成功。耗时 %.2fs，服务端报告模型 %s" % (time.time() - started, reply["model"]))
    print("  回复内容：%r" % reply["content"].strip()[:60])
    usage = reply.get("usage") or {}
    if usage:
        print("  tokens：prompt %s / completion %s / total %s"
              % (usage.get("prompt_tokens"), usage.get("completion_tokens"),
                 usage.get("total_tokens")))

    if not question:
        print("\n[2/2] 跳过完整问答（加 --ask \"你的问题\" 可以跑一遍）")
        print("\n密钥可用。启动应用：python app\\server.py")
        return 0

    print("\n[2/2] 完整问答：%s" % question)
    try:
        record = clerk.answer(question, mode="deepseek")
    except (model.ModelError, archive.ArchiveError, archive.UnsafeQuery) as exc:
        print("\n失败：%s" % exc)
        return 1

    print("  model.source = %s（%s）" % (record["model"]["source"], record["model"]["name"]))
    print("  调用次数 = %s，总耗时 = %ss" % (record["model"]["calls"],
                                             record["model"].get("seconds_total")))
    print("\n  SQL（模型写的，被守卫放行后真跑了）：")
    for line in (record["result"]["sql"] or record["plan"]["sql"]).splitlines():
        print("    " + line)
    print("\n  命中 %d 行" % record["result"]["returned"])
    print("\n  书记官说：")
    for line in record["answer"]["text"].splitlines():
        print("    " + line)
    print("\n  引证 %s；引证核对 %s"
          % (record["answer"]["cited_ids"],
             "通过" if record["citation_check"]["ok"] else
             "未通过，出现了未返回的行号 %s" % record["citation_check"]["stray"]))
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
