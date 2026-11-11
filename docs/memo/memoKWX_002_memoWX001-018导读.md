# memoWX001–018 导读

## 000 — 目的与范围

逐篇了解 memoWX001–018 的内容和作用。

## 001 — 逐篇讨论目录

以下依据18篇现行原文整理，作为待逐篇讨论确认的初稿。原文中的环境安装、实现和测试结果按其记录时点理解，不表示本轮重新验证。

内容可分四组：001–007讲项目组织与协作；008–009讲缠论概念与数据设计；010–013讲环境、编码技能及早期实现；014–018讲概念研究、算法推导与批次协调。

| Memo                                                                   | 主要用途                                                      |
| ---------------------------------------------------------------------- | --------------------------------------------------------- |
| [WX 001：Project 009 目录结构](memoWX_001_folderStrucureforProj009.md)      | 参考项目Project 009怎样读取行情、K线、文档和图表。                           |
| [WX 002：多 Agent 系统概念](memoWX_002_MAS.md)                               | 解释并构建Codex与Claude的多Agent系统。                               |
| [WX 003：目录结构决定](memoWX_003_folderDecision.md)                          | 比较 CC 与 Project 009 目录，生成TDS的目录。                          |
| [WX 004：项目与 MAS 合并结构](memoWX_004_projectAndMAS.md)                     | 把项目目录、共享MAS核心和Codex入口合成TDS结构总览。                           |
| [WX 005：信息与研究工作流](memoWX_005_informationWorkflow.md)                   | 整理来源提取、证据核对、memo归纳、知识分流和工作交接的研究。                          |
| [WX 006：Memo 写作指南](memoWX_006_memoWritingGuide.md)                     | 规定memo的命名、结构、表达与引用，以及用户优先。                                |
| [WX 007：Codex 记忆](memoWX_007_codexMemory.md)                           | 为TDS项目记忆，最新、任务状态、异常退出等都可以继续工作。                            |
| [WX 008：缠论整体图景](memoWX_008_ChanLargePicture.md)                        | 用图示和文字简要说明包含、分型、笔、线段、中枢、走势、背驰及买卖点。                        |
| [WX 009：缠论特征设计模式](memoWX_009_designPatternForChanFeatures.md)          | 设计缠论不同类，字段、来源引用、ID、时间及ChanTable原始时间轴映射。                   |
| [WX 010：Python 环境配置](memoWX_010_pythonSetup.md)                        | 规定TDS采用uv、Python 3.11及开发工具配置。                             |
| [WX 011：ChanTable 实现](memoWX_011_chanTableImplementation.md)           | 根据原始数据首次生成并实现ChanTable。                                   |
| [WX 012：Skill_python_pro](memoWX_012_Skill_python_pro.md)              | Python开发的技能指令，对代码进行设计、规范、校验、测试等要求                         |
| [WX 013：Kline 类族实现](memoWX_013_klineFamily.md)                         | 参考009实现了Kline与KlineTSeries、原始CSV读写及可选Plotly绘图的实现结果、接口和示例。 |
| [WX 014：ChanAxiomSyntax](memoWX_014_ChanAxiomSyntax.md)                | 缠论概念的通用模板：定义、算法、原理、缺口和证据附录，并给出检查标准。                       |
| [WX 015：Chan_mergedkline](memoWX_015_Chan_mergedkline.md)              | 根据模版，写 包含                                                 |
| [WX 016：Skill：Chan原文与代码研究](memoWX_016_Skill_chan_source_code_study.md) | chan-source-code-study为缠论概论提供有效依据，从原文和CC项目拉取有效信息并做研究和解释   |
| [WX 017：算法开发技能](memoWX_017_Skill_algoDev.md)                           | computer-scientist为根据研究完成的定义，生成相应的算法                      |
| [WX 018：概念2–8批次协调](memoWX_018_batchConcept2to8.md)                     | 协调008中S2–S8各概念的独立memo创建和附录研究，集中记录目标、进度、批次结果及缺口。           |

## 002 — 单篇讨论范式

- 本次讨论的memo：待选定。
- 原文位置：待选定。
- 它主要解决什么问题：待讨论。
- 在项目中何时需要使用它：待讨论。
- 与其他memo如何衔接：待讨论。
- 尚有疑问或需要纠正的地方：待讨论。
- 已确认的说明：待讨论确认后填写。

## 003 — 逐步写入

每次围绕一篇memo或一个问题讨论，只写入已经确认的内容。尚未讨论或仍有分歧的部分保留占位，不自动补写其余篇目。原memo作为参考保留。
