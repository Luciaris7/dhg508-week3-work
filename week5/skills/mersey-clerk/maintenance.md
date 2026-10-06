# 怎么维护（maintenance.md）

> 加一份新材料＝把同一套步骤再跑一遍，**旧行一个都不动**。规矩见 [`principles.md`](principles.md)
> 第 3、6、7 条；口径见 [`answers.md`](answers.md)。

卷宗本体与构建脚本都在项目根（本文件所在的 `week5/` 只是应用与 skill，不改数据库）：

```
../../../history.db          # 生成的数据库（相对本文件；即 week3 根目录）
../../../code/build_db.py    # 从 code/data/*.json 重建
../../../code/validate_db.py # 引文回原文 + 外键 + 完整性 + 日期格式
../../../code/verify_sample.py
```

## 步骤

0. **先决定要不要加。** 新材料能不能补上卷宗缺口（见 `../../../questions.md`）？
   会不会引入与现有行冲突的数字？冲突要并存，不要覆盖。
1. **登记新来源**：在 `../../../code/data/sources.json` 追加一条（`id` 取现有最大 + 1，
   `code` 用短码，如 `USINQ`），原文逐字放进 `../../../sources/raw/`，**一个字节都不改**。
2. **抽事实为行**：新建 `../../../code/data/events_03_<来源>.json`
   （`events_` 前缀会被自动合并）；每条必须有
   `id`（现有最大 + 1，**不复用**）、`source_id`、`locator`（如 `L123-145`）、
   `quote`（能在该行段内**逐字**命中的英文原句）、`note`（存疑/冲突），
   以及 `date_original` + `date_normalized` + `date_conversion`。
   新人物加进 `people.json`，事件—人物关系加进 `event_people.json`，图片加 `images.json` + `image_events.json`。
3. **重建与校验**（三条都要跑，任一失败先修，不要「先交后修」）：

   ```powershell
   python ../../../code/build_db.py        # 应打印各表行数与 foreign_key_check: clean
   python ../../../code/validate_db.py     # 应打印 All checks passed
   python ../../../code/verify_sample.py   # 随机 20 行回原文对照
   ```

   注意行数会变，`research/database-design.md`、`skills/` 里写死的行数要一起更新——
   否则下一次读的人会以为数据丢了。

4. **抽查**：发现问题按「现象 / 原因 / 修法」记入 `../../../research/verification.md`；
   若改动了已入库的数据，再记一条 `../../../improvement-log.md`。
5. **提交**：只提交小而耐久的文件（数据 JSON、脚本、文档）；密钥、大文件、临时产物不入 Git。
   提交信息写清**改了什么、为什么**。
6. **交回作答**：料备齐、`validate_db.py` 全绿后，回到 [`answers.md`](answers.md) 依卷宗作答。

## 如果应用读不到新行

应用每次请求都**重新只读打开** `history.db`，所以重建后不必重启服务器；
若页面仍显示旧行，先确认第 3 步真的重建成功（看 `build_db.py` 打印的行数）。
