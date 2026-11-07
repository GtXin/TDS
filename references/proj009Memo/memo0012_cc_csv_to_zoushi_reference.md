---
title: memo0012_cc_csv_to_zoushi_reference
tags:
  - memo
  - reference
  - cc
  - chanlun
  - project-009
status: active
source:
  - https://www.kwx.me/cc/
created: 2026-08-31
---

# memo0012_cc_csv_to_zoushi_reference

## 1. 会话概览

### 1.a 目的

> [purpose] 识别 KWX/CC 网页中的 key concepts（关键概念）、
> algorithms（算法）和 connections（连接关系），用来指导 Project 009
> 的第一轮 Python experiment（Python 实验）。

> [note] 本 memo 的核心不是保存网页内容，而是把网页拆成 Project 009
> 能理解、能实验、能验证的对象和算法关系。

> [decision] 目标是尽量弄明白细节，不是单纯复制网页。
>
> 吸收时要先理解每一层为什么存在、对象字段为什么这样设计、检查关卡到底
> 在防什么错误、哪些证据决定对象成立，再决定 Project 009 是否采用、改写
> 或延后。

> [source] 网页来源：
>
> - URL: `https://www.kwx.me/cc/`
> - 标题：`完整阅读｜CSV to 走势 复现说明`
> - 访问日期：`2026-08-31`

### 1.b 为什么重要

> [decision] 把这个网页作为第一轮 Python 实验的概念地图和算法地图。

> [note] 该网页描述了一个从 CSV/OHLCV 输入，到缠论结构对象，再到
> 字节级一致 SVG 输出的确定性复现流程。

> [note] Project 009 需要从中弄清楚：
>
> - 有哪些核心对象；
> - 每个对象由哪个算法生成；
> - 上一层对象如何连接到下一层对象；
> - 每一层需要保存哪些字段、状态和证据；
> - 每一层用什么检查证明自己正确。

### 1.c 范围

> [scope] 本 memo 记录第一轮 Python 实验需要理解的概念、算法和连接。

> [scope] 本 memo 不复制网页的完整代码、HTML、SVG 或数据集。
> 如果以后需要精确保留网页产物，应建立独立 reference record
> （参考记录）并记录 provenance（来源）。

> [scope] 后续扩展应优先提炼 rules（规则）、fields（字段）、
> states（状态）、evidence（证据）、failure conditions（失败条件）和
> verification meaning（验证含义）。不要把网页当成代码仓库镜像。

### 1.d 语言规则

> [decision] 本 memo 后续扩展以中文为主。

> [reason] 源网页是中文，缠论概念也适合保留中文表述，方便和原网页对照。

> [decision] Python 实现相关结构使用中英双语。

> [rule] Python-facing structure（面向 Python 的结构）、class（类）、
> method（方法）、field/member（字段/成员）、data type（数据类型）和
> file path（文件路径）应保留英文代码名，同时补充中文含义。

> [example] 推荐写法：
>
> ```text
> Kline（单根K线）
> KlineTSeries（K线时间序列）
> symbol: str（标的代码）
> timestamp: datetime（时间戳）
> klines: tuple[Kline, ...]（按时间排序的K线元组）
> ```

> [note] 代码名保持英文，并遵守 PEP 8。中文负责解释领域含义、业务语义和
> 与网页口径的对应关系。

## 2. 核心概念

### 2.a 概念-算法-连接总图

> [concept] 网页展示的不是一个单独算法，而是一串对象和算法连接：
>
> ```text
> CSV
> -> Kline（原始K线）
> -> MergedKline（合并K线）
> -> Fenxing（分型）
> -> Bi（笔）
> -> Xianduan（线段）
> -> ZhongShu（中枢）
> -> ZouShi（走势）
> -> SVG（最终图形）
> ```

> [decision] 第一轮 Python experiment 不应该先碰整条链路。
>
> 第一轮只需要把前两层做稳：`Kline`（单根K线）和
> `KlineTSeries`（K线时间序列）。后面的合并、分型、笔、线段、中枢、走势
> 先作为下一步算法节点记录下来。

### 2.b 关键对象表

> [concept] 下面是网页中需要识别的核心对象，不是马上全部实现的清单。
>
> | 层 | 概念 | Python-facing name（代码名） | 核心责任 | 输入 | 输出 |
> | --- | --- | --- | --- | --- | --- |
> | 0 | 原始K线 | `Kline` | 保存一根 OHLCV bar（单根K线） | CSV row（CSV行） | 单根合法K线 |
> | 0 | K线序列 | `KlineTSeries` | 保存严格递增的 K线序列 | `tuple[Kline, ...]` | 可验证序列 |
> | 1 | 合并K线 | `MergedKline` | 消除包含关系，保留来源范围 | `KlineTSeries` | 合并后的K线 |
> | 2 | 分型 | `Fenxing` | 三根合并K线确认顶/底 | `MergedKline`序列 | 分型点 |
> | 3 | 笔 | `Bi` | 连接有效分型，处理候选和确认 | `Fenxing`序列 | 笔 |
> | 4 | 线段 | `Xianduan` | 从笔的特征序列冻结线段 | `Bi`序列 | 线段 |
> | 5 | 中枢 | `ZhongShu` | 识别重叠区间、延伸和关闭 | `Xianduan`序列 | 中枢 |
> | 6 | 走势 | `ZouShi` | 消费正式中枢，形成盘整/趋势 | `ZhongShu`序列 | 走势 |
> | 7 | 图形 | `Renderer` / adapter | 把对象画成确定性SVG | 全部对象 | SVG |

> [note] 这张表的用处是确定 object ownership（对象职责归属）。它不是让
> 第一轮实验一次性实现所有类。
