# fixtures/ — 这里的替身，和示例里的替身有什么不同

Week 5 的示例 `demo-building-app/` 里有一个 fixture：

```python
# demo-building-app/server.py
def ask_model(image: bytes) -> dict:
    """THE ONE SPOT TO REPLACE. ... This demo does not call any model."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))   # 每张照片都返回同一个答案
```

它的问题不在"用了 fixture"，而在**看不出来**：任何照片都得到同一句 惺亭，
页面只在角落挂一个 `model: fixture` 徽章，响应的其余部分与真模型毫无区别。

本文件夹里的 `offline-answers.json` 是 Week 5 版本的替身，规则变了三条：

1. **它有名有姓。** 一旦用到它，响应里的 `model.source` 就是 `"fixture"`，
   `model.name` 是 `offline fixture (not a model)`，页面顶部亮黄条，命令行启动横幅也写明。
2. **它只替模型，不替数据库。** 文件里保存的是两段本该由模型产出的内容（写查询、落笔），
   `sql` 仍然**真的**跑在 `history.db` 上——页面下方那些行是真档案行，不是抄来的。
3. **它认得多少，就说多少。** 只有 5 道示例题有存档；问别的，服务器直接回
   `409 fixture_miss`「离线替身里没有这一题的预设答案」，绝不拿最相近的一条糊弄你。

设置 `DEEPSEEK_API_KEY` 后重启服务器即可离开这个模式（默认 `WEEK5_MODE=auto` 会自动切换）。
想强制任一模式：

```powershell
$env:WEEK5_MODE = "deepseek"    # 强制真调用；没有密钥就直接报错，不会偷偷退回替身
$env:WEEK5_MODE = "fixture"     # 强制离线，用来排练演示
```

## 这些存档答案是谁写的

模型的角色是两件事：**写查询**、**把查到的行写成书记官的话**。
所以存档里的 `plan` 与 `compose` 由我按 `skills/mersey-clerk/principles.md` 的规矩撰写，
并用 `code/check_app.py` 逐条核对过：每条引用的 `[id]` 都必须真的在查询返回的行里，
否则自检不通过。这不是"模型跑出来的输出"，我也不把它当作模型输出——
它只是没有密钥时用来排练和自检的替身。
