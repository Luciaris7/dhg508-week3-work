# 课堂演示（5 分钟）· Week 5

要讲清四件事（就是 Week 5 "Bring to class" 那四条）：
**① 应用在跑，答了一个真问题 ② fixture 原来在哪、被什么替换了 ③ skill 的索引与文件 ④ 提交历史**

---

## 课前 2 分钟

```powershell
chcp 65001                          # 中文乱码时才需要（PowerShell 5.1 默认 cp936）
cd "C:\Users\28301\Desktop\dhg508 week3\week5"

python code\set_key.py --verify     # 粘贴密钥（不回显）→ 存进环境变量 → 立刻真调用验证一次
python code\check_app.py            # 应打印「通过 67 项，失败 0 项」
python app\server.py                # 横幅应写 model deepseek-flash
```

`set_key.py --verify` 跑通就说明第 ① 条"答一个**真**请求"已经成立；
它失败时会明确告诉你是 401（抄错）还是 402（余额不足）。

横幅是第一个卖点，念出来：

```
  archive   ...\dhg508 week3\history.db  (223 rows)
  model     deepseek-flash  (DEEPSEEK_API_KEY found)      ← 有密钥时
  model     offline fixture (not a model)                 ← 没密钥时会写这句
```

**掉链子预案**：网络不通就把 `$env:WEEK5_MODE` 设成 `fixture` 重开，
页面会亮黄条明说"回答来自预设答案，不是模型"——**念出来，这本身就是演示内容**。
断网时真正能救场的正是那条黄条：它证明这个应用不会假装。
（`WEEK5_MODE=fixture` 需在**同一个窗口**里设，再启动服务器。）

---

## 第 1 幕 · 应用在跑，答一个真问题（约 2 分钟）

1. 打开 <http://localhost:8000>，念页面上的说明。
2. 点示例题「加州人号（Californian）的船长是谁？当晚他做了什么？」→ 呈上问题。
3. 结果出来后，**从上往下**讲：

   - **结论条**："卷宗有此记载，查得 7 行"——先说清是有据还是拒答。
   - **回答**："船长 **Stanley Lord** [24]；该船属 Leyland 公司、6,223 总吨，
     属 IMM，与泰坦尼克同一母公司 [94]；晚 7:30 报冰情 [95]；10:20 因浮冰停车，
     所报位置被法庭判为不准确 [96]；约 11 时见来船而船长不在驾驶台 [97]；
     12:30–1:40 见 8 枚火箭未施救，法庭裁定本可赶到 [25][30]。"
     念一句关键的："**这些行号，通用知识给不出来。**"
   - **依据表**："这是唯一允许它使用的材料——回答里每一句都在这张表里。"
   - **检索过程**（展开）："这条 SQL 是模型写的，服务器检查过它只有一条只读查询，
     然后**真的**在 1912 年卷宗上跑了。"
   - **页脚**："两次调用、耗时、tokens，都在这儿。"

4. 再点「泰坦尼克号残骸是哪一年被发现的？」——**0 行**：
   "这本卷宗里没有。它没有给我 1985 那个年份，因为卷宗只到 1912 年 7 月。"
   一句收束："**它宁可说没有，也不编。**"

## 第 2 幕 · fixture 原来在哪，被什么替换了（约 1 分钟）

打开示例与自己的代码对照（提前开好两个窗口）：

```
..\..\dhg508-workspace-main\508-coursework\week-05\demo-building-app\server.py   第 20-30 行
```

念示例里那段：

```python
def ask_model(image: bytes) -> dict:
    """THE ONE SPOT TO REPLACE. ... This demo does not call any model."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))
```

- "示例自己写着 **It looks smart. It is a fixture.**——每张照片都是同一个答案，
  页面上只有角落一个 `model: fixture` 徽章。**这是最容易翻车的地方**：
  演示时断网、密钥过期，观众看不出来。"
- 切到本项目 `app/model.py` 顶部：**同一个位置，现在是真调用**：

  ```
  POST https://api.deepseek.com/chat/completions
  Authorization: Bearer $DEEPSEEK_API_KEY
  {"model": "deepseek-flash", "messages": [...], "response_format": {"type": "json_object"}}
  ```

  "标准库 `urllib` 手写，官网文档的契约逐字段对过（`python code\check_app.py` 的 F 段 18 项）。"
- 再说替身："我也有替身（`app/fixtures/offline-answers.json`），但它**永远自报身份**：
  `model.source=fixture`、页面顶黄条、命令行横幅写明、只认 5 道题，问别的直接
  `409 fixture_miss`。**没有任何一条路径能让它冒充模型。**"

**这一段的收束句**：
"区别不在于用不用 fixture，而在于**用户能不能一眼看出来**。"

## 第 3 幕 · skill 的索引与它的文件（约 1 分钟）

```powershell
notepad skills\mersey-clerk\SKILL.md
```

- 只打开 `SKILL.md`："这是**索引**，一页，只说一件事——**哪件事读哪份文件**。"
- 依次点开（不用细讲，展示"一份只干一件事"）：
  - `answers.md` —— 我怎么作答（选行 → 读行 → 落笔）
  - `maintenance.md` —— 怎么加料（六步，重建校验）
  - `principles.md` —— 七条永远成立的规矩
- "细节不在这四份里，在 `reference/` 三份，**按需加载**——`answers.md` 会告诉你什么时候翻。"
- 指 `mersey-registrar/SKILL.md`："它现在只有十行，因为加料的步骤只有一份，
  **指过去而不是抄一遍**。"
- 关键一句："`app/clerk.py` 顶上写着注释：`principles.md` 里的规则在这里是**代码**——
  第 3 条'无卷不答'就是 `verdict = not_in_archive`；第 1 条'只用卷宗'就是
  **落笔那一步只拿到查出来的行**，第 4 行不在其中。这不是口号，是自检里断言过的。"

**收束句**（沿用上周那句，但要升级）：
"上周是「一本有出处的卷宗 + 一套不许越界的规矩」；
这周多了一句——**规矩已经变成代码，而且可执行地检查过了**。"

## 第 4 幕 · 提交历史（约 30 秒）

```powershell
git log --oneline -8
git show --stat HEAD
```

- "每个提交只做一件事，信息里写**改了什么、为什么**：先重构 skill，再加应用，
  最后补文档与自检——所以你能看出这个文件夹是怎么长出来的。"
- "密钥从来没进过 Git：`.gitignore` 里有 `.env`，而代码只从环境变量读密钥，
  连 `.env` 都没有。"

---

## 可能被问到

**Q：怎么证明不是模型背的？**
A：两处。① 页面上"依据"表就是全部材料，落笔那一步看不到别的东西——
`python code\check_app.py` 的 C 段用桩替身断言过「未被检索到的行不在提示里」；
② 问它 1985 年残骸，它必然答"这本卷宗里没有"。

**Q：模型写的 SQL 万一是 `DROP TABLE` 呢？**
A：三层防线（`app/archive.py`）：只许单条 `SELECT`/`WITH` → 禁词表 →
连接本身就是 `mode=ro`。自检 A 段**真的去执行** `INSERT/UPDATE/DELETE/DROP`，
四次都被 SQLite 挡回，所以卷宗改不坏。

**Q：模型会不会编一个不存在的行号？**
A：会，所以要核对。服务器检查 `cited_ids` 是否都在返回行里，不在就把标签标红并在结论条警告。
自检 C2 段用一个故意编 `[999]` 的桩替身验证这条能抓到。**但它不会替模型改话**——
改了就没人知道模型原本写了什么。

**Q：没有密钥能演示吗？**
A：能，页面会亮黄条说明自己处于离线替身模式，并且只认 5 道示例题。
这正是我对示例那个 fixture 的批评：**用替身没关系，装成模型不行。**

**Q：数据要怎么加？**
A：`skills/mersey-clerk/maintenance.md`——新建 `..\code\data\events_03_*.json`，
再跑 `build_db.py`、`validate_db.py`、`verify_sample.py`。数据库和应用都不用改：
应用每次请求都重新只读打开卷宗，重建后刷新页面即可。

---

## 一页速查

```
课前：  python code\set_key.py --verify   → 粘贴密钥（不回显），自动跑一次真调用验证
        python code\check_app.py          → 通过 67 项，失败 0 项
        python app\server.py              → 横幅写 deepseek-flash，开 http://localhost:8000
演示：  ① 问「加州人号船长」→ 结论条 / 回答 / 依据表 / SQL / 页脚
        ② 问「残骸哪一年发现」→ 0 行，拒答
        ③ 对照 demo-building-app/server.py 的 ask_model() → app/model.py 的真调用
        ④ skills\mersey-clerk\SKILL.md → 索引 + 三份文档 + reference
        ⑤ git log --oneline -8
兜底：  $env:WEEK5_MODE="fixture" → 黄条自报替身，照样能讲
```
