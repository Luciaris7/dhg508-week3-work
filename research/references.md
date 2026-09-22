# 引用与检索信息（References）

## 原始材料

1. **英国沉船调查委员会报告（官方一手材料）**
   - 题名：*Loss of the Steamship "Titanic"* — Report of a Formal Investigation into the circumstances attending the foundering on April 15, 1912, of the British steamship *Titanic*, of Liverpool.
   - 出版：Washington, 1912（62d Congress, 2d Session, Senate Document No. 933）。
   - 电子文本：Project Gutenberg eBook #39415，<https://www.gutenberg.org/ebooks/39415>。
   - 本地副本：`sources/raw/british-inquiry-1912-loss-of-steamship-titanic.txt`。
   - 数据库中的 `source` 字段以 `Gutenberg #39415` 加章节名与文本行号定位。

2. **Lawrence Beesley 回忆录（幸存者一手材料）**
   - 题名：*The Loss of the S. S. Titanic: Its Story and Its Lessons* (1912)。
   - 电子文本：Project Gutenberg eBook #6675，<https://www.gutenberg.org/ebooks/6675>。
   - 本地副本：`sources/raw/beesley-1912-loss-of-ss-titanic.txt`。
   - 数据库中的 `source` 字段以 `Gutenberg #6675` 加文本行号定位。

## 交叉核对（未直接进库）

- 维基百科 *Sinking of the Titanic* 时间线：<https://en.wikipedia.org/wiki/Sinking_of_the_Titanic>
- 仅用于比对日期与数字，库中每一行均取自上面两份公共领域原始材料。

## 检索信息

- 抓取日期：2026-09-23
- 抓取方式：`Invoke-WebRequest` 下载 Gutenberg 纯文本（UTF-8）。
- 两份材料均属公共领域（Public domain in the USA）。
