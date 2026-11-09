# Skill — Chan原文与代码研究

## 000 — Scope

将memo015的研究过程抽象为可复用SOP：围绕一个Chan概念，整理带原图和出处的原文附录A，再按实现代码整理处理步骤附录B。memo保存研究结果，Skill保存可重复执行的方法。[1][2]

- 名称：`chan-source-code-study`。
- 状态（2026-11-08）：已创建，格式验证通过；尚未完成独立任务的使用验证，也未验证当前界面的技能列表发现结果。
- 由Codex使用内置 `skill-creator` 制作；无需额外调用Anthropic或Skill Curator。

默认交付两个附录，除非用户明确缩小范围：

- **Appendix A — Chan Theory原文：** 原文／作者答疑、相关原图及精确出处；理论原文不等于可执行代码。
- **Appendix B — CC源码与实现分析：** 保存并引用相关源码，在分析旁列出关键可执行代码片段，再按实际函数与分支总结步骤。仅有网站说明文字不足以完成此附录。

两套来源缺一时，标明对应附录尚未完成，不用其中一套解释代替另一套证据。

## 001 — 制作过程

1. 从memo015的实际要求提取流程：限定K线包含范围、扫描原文、精选段落、附相关原图、引用来源，再沿CC实际代码总结处理步骤。
2. 阅读 `skill-creator/SKILL.md`，将流程写成单一入口文件，避免另存一份重复SOP。[3]
3. 在原文部分明确区分作者正文、答疑、读者提问与编者注；图片需实际查看，缺失或图文不符要标明。
4. 在代码部分要求核对入口、初始化、状态、比较分支、更新、回退和输出；区分可执行语句、注释意图、推论及待验证问题。
5. 加入交付检查：出处、图片、链接、引用编号、原有内容保护，以及项目备份与日志要求。只描述实际检查，不把静态阅读写成运行验证。

## 002 — 存放位置

| 项目 | 位置与作用 |
|---|---|
| 共享Skill | [mas/skills/chan-source-code-study/SKILL.md](../../mas/skills/chan-source-code-study/SKILL.md)，唯一维护入口 |
| Codex项目发现路径 | `.agents/skills/chan-source-code-study/SKILL.md`；现有 `.agents/skills → ../mas/skills` 链接，无需复制文件 |
| 制作与检查记录 | [MAS任务](../../mas/tasks/20261108-chan-source-code-study-skill.md) |
| 已有研究示例 | [memo015](memoWX_015_Chan_mergedkline.md)，属于制作依据，未作为新Skill的独立试运行结果 |

共享Skill目录按项目约定管理；本次没有创建个人全局副本或Claude专用配置。[2]

## 003 — 调用方法

### 完整研究：生成附录A与B

在TDS项目对话中输入 `$chan-source-code-study`，接着写清研究概念、两套来源、目标memo和修改范围。可直接复制以下示例；将概念与目标memo替换为本次任务的实际值。

```text
$chan-source-code-study
研究概念：K线包含及合并处理；排除特征序列包含。
来源A：references/chan_theory/，扫描全部原文资料。
来源B：references/cc_algo/，查找网站发布的相关CC源码。
目标：docs/memo/memoWX_015_Chan_mergedkline.md。

请生成两个附录：
Appendix A — Chan Theory原文：精选有独立价值的原文及作者答疑，
附相关原图、课号和精确出处；区分读者提问与编者注。
Appendix B — CC源码与实现分析：保存并引用实际源码，
在分析旁列出关键可执行代码片段，按输入、状态、初始化、
条件分支、合并、回退和输出总结处理步骤；主要依据代码，不复述网站介绍。

只修改两个附录及其必要引用，保留主章节和用户修改。
已有资料不要重复添加；缺少来源或图片时明确标记。
按项目要求备份并记录实际检查，区分静态分析与运行验证。
```

### 继续研究：补充已有附录

```text
$chan-source-code-study
继续检查memo015的Appendix A和Appendix B。
A核对 references/chan_theory/ 的原文、答疑与原图；
B核对 references/cc_algo/ 的实际源码、关键代码片段与步骤说明。
只补遗漏、纠正不准确之处，不重复已有材料，不修改主章节。
报告修改依据和仍未解决的问题，并按项目要求备份、记录。
```

不要求固定引文数量时，按独立证据价值选择；需要限定数量，可另写“附录A选取10段”。只需其中一个附录时，明确写“本次只做Appendix A”或“本次只做Appendix B”。

### 未发现Skill时：指定入口文件

```text
请先阅读 mas/skills/chan-source-code-study/SKILL.md，按其中流程执行。
研究概念：[填写概念与排除项]。
原文来源：references/chan_theory/；CC代码来源：references/cc_algo/。
本次只在聊天中输出Appendix A与Appendix B，不修改memo。
```

## 004 — 检查结果与后续验证

- 内置 `quick_validate.py` 返回 `Skill is valid!`，确认名称、前置元数据及基本格式通过。
- 系统Python及TDS环境缺少PyYAML；改用现有Project009 Python环境运行验证器，未安装依赖或修改项目配置。
- 已核对 `.agents/skills` 链接指向共享目录；这不等于已确认当前界面发现新Skill。
- 尚未执行独立研究试验。下次实际使用时，应检查是否守住概念边界、正确配图、按代码而非介绍文字总结，并如实记录未决问题。

## References

[1] [Memo015：Chan_mergedkline](memoWX_015_Chan_mergedkline.md)。

[2] [Memo004：项目与MAS结构](memoWX_004_projectAndMAS.md)；[共享MAS工作流](../../mas/README.md)。

[3] 本机内置 [skill-creator/SKILL.md](/Users/coder/.codex/skills/.system/skill-creator/SKILL.md)，本次制作时读取。
