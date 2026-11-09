# Batch Concepts 2–8

## 000 — Scope

协调 memo008 中 S2–S8 的批量处理与独立概念 memo 创建，集中记录目标 memo、进度、批次结果和下一步。[1] 具体定义、算法、原文与代码研究保存在各概念 memo 中。

## 001 — Concept tracking

| 概念 | 目标 memo | 本批次状态 |
|---|---|---|
| S2 分型 | [memo019：Chan_fenxing](memoWX_019_Chan_fenxing.md) | 附录 A/B 已复核补充（静态研究） |
| S3 笔 | [memo020：Chan_bi](memoWX_020_Chan_bi.md) | 附录 A/B 已复核补充（静态研究） |
| S4 线段 | [memo021：Chan_xianduan](memoWX_021_Chan_xianduan.md) | 附录 A/B 已复核补充（静态研究） |
| S5 中枢 | [memo022：Chan_zhongshu](memoWX_022_Chan_zhongshu.md) | 附录 A/B 已复核补充（静态研究） |
| S6 走势 | [memo023：Chan_zoushi](memoWX_023_Chan_zoushi.md) | 附录 A/B 已复核补充（静态研究） |
| S7 背驰 | [memo024：Chan_beichi](memoWX_024_Chan_beichi.md) | 附录 A 已复核补充；B 检测源码缺口 |
| S8 买卖 | [memo025：Chan_buysellpoint](memoWX_025_Chan_buysellpoint.md) | 附录 A 已复核补充；B 检测源码缺口 |

各概念 memo 可参照 memo014 的结构；具体填写范围由各批次任务确定。[2] S1 包含已有 memo015，其未决问题继续保留在原 memo。[3]

创建各概念 memo 时检查最新索引、分配编号，并将上表的“待创建”替换为实际链接；本协调 memo 不预占后续编号。进度按实际完成范围更新，不能将附录整理完成等同于定义、算法或实现完成。

## 002 — Batch create the memo template for S2 to S8
empty template with the right name as 015. 

已完成：创建 memo019–025，保留空白的 000–005、002.a–002.d、Appendix A／B 与 References 章节；此步骤仅创建空模板，后续附录进度见003。

## 003 - Skill_Chan_source_code study 
use memo016 to fill the memo appendix seciton for all memos from s2 to s8. Be thorough

本批结果（2026-11-09）：按 memo016 整理 memo019–025 的附录及必要引用。[4]

- S2–S6：原文与图示、实际 CC 源码逻辑、连续数值手推及金融图已整理；属于静态研究，未执行 CC 引擎。
- S7–S8：理论附录已整理；当前 CC 源码未找到背驰／买卖点检测器，附录 B 记录实际接口、占位行为与待补证据，两项配对研究尚未完成。
- 000–005 主章节保持原样；引文、来源图片、链接及数值说明已检查并交叉复核。缺图与实现差异保留在各自附录中。

[详细任务与检查](../../mas/tasks/20261109-memo018-appendix-study.md)；[批次证据](../../artifacts/mas/memo018-appendix-study/README.md)。

复核补充（2026-11-09）：新增25组来源材料（含已标明的整理者图解）、20份原图副本、2张手工金融图；另核对第104课作者原页并补入短引文与范围说明。

- 原文补齐有效分型修订、固定精度、级别／递归边界、小转大必要条件，以及第二类买点可低于第一类买点等适用条件。
- 代码补齐强势／修正门禁、显示与计算入口差异、OPEN尾部、SAME_LEVEL细分和递归trace边界；关键新增部分已交叉复核。
- S7／S8检测器源码及未恢复的来源图片仍保留为缺口；000–005主章节不变，未执行CC。

[复核覆盖矩阵与最终检查](../../artifacts/mas/memo018-appendix-recheck/README.md)；[复核任务](../../mas/tasks/20261109-memo018-appendix-recheck.md)。

## References

[1] [Memo008：Chan Large Picture](memoWX_008_ChanLargePicture.md)。

[2] [Memo014：Chan Axiom Syntax](memoWX_014_ChanAxiomSyntax.md)。

[3] [Memo015：Chan_mergedkline](memoWX_015_Chan_mergedkline.md)。

[4] [Memo016：Skill—Chan原文与代码研究](memoWX_016_Skill_chan_source_code_study.md)。
