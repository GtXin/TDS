# Skill — Algorithm Development

## 000 — Scope

使用 `computer-scientist` 从概念定义推导算法：明确输入输出、处理步骤、伪代码、数值例子、正确性依据与复杂度。定义不足时列出缺失规则，不自行补定。该Skill提供通用计算机科学方法，并非专门的缠论算法生成器。[1]

- 名称：`computer-scientist`；上游版本：1.0.0；元数据声明许可证：MIT。
- 状态（2026-11-09）：已安装到项目共享目录；文件与发现路径检查通过，独立算法推导试验尚未执行。
- 原候选比较移至Appendix A；当前用户选择安装computer-scientist，其余未安装。

## 001 — 安装过程

1. 使用内置 `skill-installer` 的GitHub安装脚本，指定项目共享目录 `mas/skills/`。
2. 将K-Dense-AI/scientific-agents的main解析为固定提交：`98c7fae46648724e1a43a1f2b207b0c82fcc462e`，从该提交安装 `scientific-agents/computer-scientist/skills/computer-scientist`。[1]
3. 保留下载的原始SKILL.md，不修改上游流程；记录来源与文件SHA-256。
4. 沿用 `.agents/skills → ../mas/skills`，无需个人全局副本或额外依赖。

## 002 — 存放位置

| 项目 | 位置与作用 |
|---|---|
| 共享Skill | [computer-scientist/SKILL.md](../../mas/skills/computer-scientist/SKILL.md) |
| Codex项目发现路径 | `.agents/skills/computer-scientist/SKILL.md` |
| 来源与校验 | [安装来源记录](../../mas/skills/computer-scientist/UPSTREAM.json) |
| 安装与检查记录 | [MAS任务](../../mas/tasks/20261109-computer-scientist-install.md) |

## 003 — 调用方法

安装后下一轮对话可使用以下请求；当前界面实际发现结果仍需确认。以下是本项目调用示例，不是上游Skill原文。

```text
$computer-scientist
阅读 docs/memo/memoWX_015_Chan_mergedkline.md 的001定义。
从定义推导K线包含处理算法，排除特征序列包含。

请给出：
1. 输入、输出、已知条件及假设。
2. 处理步骤，说明每步对应哪条定义。
3. 精确伪代码。
4. 一组连续数值例子，逐步展示状态和输出。
5. 正确性推理、不变量、终止依据及时间/空间复杂度。
6. 相等边界、双向包含和起始方向未知等边界情况。

先推导定义足以支持的部分，再列出缺失规则与可选方案。
不要自行决定初始化策略；区分定义、推论和实现选择。
只在聊天中输出，不写代码、不修改memo。
```

### 未发现Skill时：指定入口文件

```text
先阅读 mas/skills/computer-scientist/SKILL.md 并按其方法执行。
阅读memo015的001定义，推导输入输出、步骤、伪代码及数值例子，
说明正确性和复杂度；未决规则保持未决。
只在聊天中输出，不修改文件。
```

## 004 — 检查结果与后续验证

- GitHub安装脚本成功返回安装路径；下载内容为一个SKILL.md。
- 已检查名称、版本、许可证元数据与共享发现路径，记录文件SHA-256。
- 尚未执行独立算法推导试验，未验证界面技能列表发现；安装成功不代表推导效果已验证。
- 下一步：用003的请求试运行，检查步骤是否源于定义、例子是否一致、缺失规则是否明确。

## 005 — 算法推导中的推理检查

1. 固定输入、处理对象与已知状态，区分原始K线和合并单元。
2. 每个分支列出适用前提，不能从存在包含直接推定合并方向。
3. 定义能支持的结论与额外设计选择分开；初始化选择保持未决。
4. 用具体数值及最小反例检查边界；手算、测试与正确性证明分别表述。

## Appendix A — 候选比较


| Skill | 主要用途 | 缠论开发中的位置 |
|---|---|---|
| computer-scientist [1] | 问题建模、假设、不变量、正确性与复杂度 | 算法设计的总体检查 |
| invariant-guard [2] | 编码前明确契约、循环不变量、终止依据及边界条件 | 先审查规则前提与推理 |
| algorithm-design [3] | 明确输入输出、伪代码与图示 | 整理可执行的算法说明 |
| proptest-praxis [4] | 对照独立模型、生成操作序列、缩减失败反例 | 实现后的性质测试与边界验证 |

社区副本invariant-guard的署名上游在先前调研中返回404；本次未重新核验。其余候选未安装或试运行。原先优先检查invariant-guard的建议已由当前用户选择computer-scientist取代。

## References

[1] [computer-scientist — SKILL.md](https://github.com/K-Dense-AI/scientific-agents/blob/main/scientific-agents/computer-scientist/skills/computer-scientist/SKILL.md)。

[2] [invariant-guard — SKILL.md（社区副本）](https://github.com/sickn33/agentic-awesome-skills/blob/main/plugins/agentic-awesome-skills-claude/skills/invariant-guard/SKILL.md)。

[3] [algorithm-design — SKILL.md](https://github.com/ZeroTokenClaw/agents-skills/blob/main/algorithm-design/SKILL.md)。

[4] [proptest-praxis — SKILL.md](https://github.com/inanna-malick/agent-skills/blob/main/skills/proptest-praxis/SKILL.md)。
