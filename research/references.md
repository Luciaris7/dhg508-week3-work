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

## 史实图片（Public Domain）

均取自 Wikimedia Commons，皆属公共领域；本地副本位于 `sources/raw/images/`，
为控制仓储体积，已由原图缩略至宽 1280 像素。抓取日期 2026-09-23，方式 `Invoke-WebRequest`。

| 本地文件 | 内容 | 作者 / 年代 | 许可 | Commons 来源 |
|---|---|---|---|---|
| `rms-titanic-departing-southampton-1912-04-10.jpg` | 泰坦尼克号 1912 年 4 月 10 日自南安普敦启航 | F. G. O. Stuart，1912 | Public domain | <https://commons.wikimedia.org/wiki/File:RMS_Titanic_3.jpg> |
| `titanic-and-olympic-under-construction-belfast.jpg` | 泰坦尼克号与奥林匹克号在贝尔法斯特 Harland & Wolff 船厂建造中，约 1910 | Robert Welch | Public domain | <https://commons.wikimedia.org/wiki/File:Construction_of_Titanic_and_Olympic.jpg> |
| `iceberg-near-titanic-wreck-site-1912.jpg` | 沉没地点附近的一座冰山，1912-12-14 | Louis Ogden / NARA | Public domain | <https://commons.wikimedia.org/wiki/File:A_Photograph_of_an_Iceberg_Floating_Near_the_Site_of_the_TITANIC_Sinking._-_NARA_-_278334.jpg> |
| `carpathia-with-titanic-lifeboats-1912.jpg` | 泰坦尼克号救生艇靠泊 Carpathia 号，1912-04-18 | The New York Times，1912 | Public domain | <https://commons.wikimedia.org/wiki/File:Carpathia_-_Titanic_lifeboats.jpg> |
| `titanic-survivors-aboard-carpathia-1912.jpg` | 获救者聚集于 Carpathia 号甲板，1912 | Bain News Service，1912 | Public domain | <https://commons.wikimedia.org/wiki/File:Survivors_of_TITANIC_on_CARPATHIA_LCCN2014691298.jpg> |
| `titanic-paperboy-ned-parfett-1912.jpg` | 报童 Ned Parfett 举「泰坦尼克号沉没」号外，1912-04-16 | 佚名，1912 | Public domain | <https://commons.wikimedia.org/wiki/File:Titanic_paperboy_crop.jpg> |

## 交叉核对（未直接进库）

- 维基百科 *Sinking of the Titanic* 时间线：<https://en.wikipedia.org/wiki/Sinking_of_the_Titanic>
- 仅用于比对日期与数字，库中每一行均取自上面两份公共领域原始材料。

## 检索信息

- 抓取日期：2026-09-23
- 抓取方式：`Invoke-WebRequest` 下载 Gutenberg 纯文本（UTF-8）。
- 两份材料均属公共领域（Public domain in the USA）。
