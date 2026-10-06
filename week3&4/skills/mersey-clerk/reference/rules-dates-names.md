# 日期、人名与口径（reference/rules-dates-names.md）

仅在需要处理日期、人名、地名或疑似冲突数字时读本文件。

## 日期

- 每行都有一对：`date_original`（照原文）与 `date_normalized`（便于排序/比较）。
- 规范格式：`YYYY`、`YYYY-MM`、`YYYY-MM-DD`、`YYYY-MM-DDThh:mm`；时段用 `T00:30/01:40`。
- 转换规则写在 `date_conversion`：月名转数字、a.m./p.m. 转 24 小时、相对时间如何折算。
- **相对时间**（如「事故后约 15–20 分钟」）会折算成绝对时刻，但必须在 `note` 声明「本文推定」。
- 时刻均为**船时**（ship's time, 约 GMT−2:58 以东）——报告中的无线电表另注 New York time，
  回答时不要与船时混用。

## 人名

- `name_original` 照原文；`name_normalized` 统一为「姓, 名」。
- 异名照实并存，写进 `note`。例：船长排印作 **Edward Charles Smith**（L1785），
  通行史料作 Edward John Smith；库里保留排印名并标记存疑。
- 同人异拼照转：`Murdock` / `Murdoch`（一副）、`Victualing` / `Victualling`。
- 只给姓氏的（如 Evans、Groves）不做补全，note 说明「报告只给姓氏」。

## 地名

- `name_original` → `name_normalized`，并记 `kind`、经纬度、`conversion`。
- 历史称法保留：Queenstown 今名 Cobh，规范名仍用 Queenstown。

## 冲突与口径（重要）

- 数值冲突照实并存，不替史料选一个：
  - 船上人数：官方 **2,201**（`events[9]`）vs Beesley **2,208**（`events[33]`）。
  - 撞击时刻：官方 **11.40**（`events[15]`）vs Beesley **11.45**（`events[34]`）。
- 但要注意**口径不同并非矛盾**：
  - 获救 **712** 人是「自艇上救起」；**711** 人是「最终获救」——其中 1 人随后死亡
    （`events[27]`、`events[56]`）。
- 回答疑似矛盾前，先看两行的 `note` 与 `locator`，确认是「同一口径的冲突」还是「不同口径」。
