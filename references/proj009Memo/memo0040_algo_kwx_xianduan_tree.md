# memo0040_algo_kwx_xianduan_tree

[algo] [chan] [xianduan] [KWX source audit] [decision tree]

## 0. Scope And Purpose

**本篇回答：KWX/CC拿到一串笔以后，怎样找线段候选、延长或撤销候选、冻结线段，最后画出结果？** 按[memo0036](memo0036_class_xianduan_series.md)的“范围—对象—流程—验证”组织，以当前源码的执行顺序写树，默认先看`standard`，再看`strong_bi`选项。[1]

```text
已有 Bi 列表 + ChanConfig（CC的配置对象）
└── 每次调用新建 Builder、状态机
    ├── 找能接上反向候选的首段起点
    ├── 反复处理 N0 / N1 / 临时 N2
    └── 冻结列表 + 软 N0 + 最右 forming → Xianduan 列表
```

- **Input：** 按时间排列、已有方向和高低价的`Bi`；这里不重新从K线选笔。入口没有完整验证笔是否连续、交替，下面按正常上游笔序列解释。
- **Scope：** 核心入口、特征元素、包含、分型、候选搜索、状态推进、冻结检查、输出；第2.i说明显示辅助的边界。
- **Source boundary：** 本篇记录**代码实际做什么**，不能据此宣布其每个分支都等于缠中说禅原文。源码中的课号、解释性注释和“先到先判”等说法，也要与实际条件区分。
- **Project consequence：** `kwx`与`options0033memo`继续独立。用户为0032指定的严格分型、正宽度重叠，不能反过来改写KWX的等号行为。0032／0039尚待校准的理论问题也不由本篇自动结案。
- **Verification：** 第3章区分真实入口、局部条件和人工状态检查；本篇不是另一套独立算法的等价证明，也不是原文符合性证明。

**读图约定：** 主例沿用同一组A—Q价格，B1=A→B、B2=B→C；笔编号从1起，代码下标从0起。灰线保留原始笔；青色高亮只表示本步检查的原始笔，不代表新增线段。其余彩线/矩形由各图图例说明。标题标明“独立例”“局部检查”或“人工给定状态”时，不把该图当作主例的下一帧，也不据此推断完整入口可达。28张例图放在相应层旁，[全部例图](../../artifacts/experiments/chan_theory/memo0040_figures/gallery.md)可连续查看。

## 1. Objects And State

### 1.a Bi、特征元素和特征分型

**`Bi`是一笔；特征元素是一笔反向笔或多笔经包含处理后形成的价格区间。** 例如研究上升线段时，只把下降笔喂给特征识别器；研究下降线段时，只喂上升笔。反向笔之间的同向笔仍保存在输入中。

<!-- memo0040-figure:01a_objects -->
![1.a 一笔、特征元素与三元素窗口](../../artifacts/experiments/chan_theory/memo0040_figures/01a_objects.png)

[example] **主例 · 直接调用特征识别器；这是候选搜索窗口，不是最终显示框。** 图1.a：主例前8笔中，下降笔B2/B4先合并为e0；B6、B8分别构成e1/e2。原始笔不删除，派生价格区间用于后续比较。

| 对象 | 保存什么 | 用来回答什么 |
| --- | --- | --- |
| `Bi` | 方向、起终点、`high/low`、时间、可选来源trace | 这一笔在哪里、经过什么价格范围 |
| `_Eigen` | 合并后的`high/low`、原笔下标`idxs`、缺口标记 | 当前特征元素的比较区间及其来源 |
| `_EigenFX` | 最多三个元素`e0/e1/e2`、喂入记录`lst`、证据下标 | 是否出现特征分型，峰谷来自哪一笔 |

**特征分型是三个处理后元素的局部转折条件。** 上升段检查顶，下降段检查底；KWX的精确公式在2.c.4，不是四项全部严格比较。

**本篇的“缺口”是处理后`e0/e1`价格区间不相接。** 上升时`e0.high < e1.low`，如`[110,120]`与`[125,140]`有缺口；`[110,125]`与`[125,140]`只有点接触，却**无缺口**。这不是K线时间缺失，也不是输入笔被删除。

### 1.b 候选、冻结状态和输出对象

**候选是“从哪一笔到哪一笔”的内部假设；冻结对象才进入本次调用的固定结果列表。** N0、N1是状态机中的位置名，N2是本轮找到、尚未交给状态机的后续候选。

<!-- memo0040-figure:01b_state_roles -->
![1.b 同一批输入中，N0 / N1 / N2怎样换位](../../artifacts/experiments/chan_theory/memo0040_figures/01b_state_roles.png)

[example] **主例 · 16笔公开入口的真实状态转换；N2是本轮临时候选。** 图1.b：同一16笔输入中的实际confirm事件。新N2促成原N0冻结；N1和N2换位后仍是未冻结候选。

```text
本次状态机
├── frozen[]：已经冻结的连续线段
├── N0：目前最左边、尚未冻结的候选
├── N1：紧接 N0、方向相反的候选；可以没有
└── N2：局部变量，紧接 N1、方向与 N0 相同；不是长期第三槽位

常规 confirm(N2)
└── 复制原 N0 到 frozen；原 N1 → 新 N0；N2 → 新 N1
```

候选的`start_bi/end_bi`是**含首尾的笔下标**；上升候选的`start_key=首笔.low`、`end_key=末笔.high`，下降候选镜像。`rule`记录来源（`feature_seq/gap/strong_bi/pen_break_absorb`），`dep`记录代码保存的依赖下标。

| 层次 | 对象/标签 | 注意 |
| --- | --- | --- |
| 内部 | `_XianduanCand`，即N0/N1/临时N2 | 可延长、被撤销或换位 |
| 内部 | `_FrozenXianduan` | 保存冻结时的区间和元数据副本 |
| 输出准备 | `_WorkXianduan` | 把内部状态转为`frozen/soft_n0/pending_n1`输出 |
| 最终 | 不可变`Xianduan`及其`StructTrace` | 保留几何区间、规则、依赖和冻结标记 |

**图上`pending_n1`不保证内部存在N1。** 输出函数也能在完全找不到首段时，单独生成一条`forming`尾线；见2.h。

### 1.c 一次计算的寿命与覆盖范围

<!-- memo0040-figure:01c_independent_prefixes -->
![1.c 数据增加后重新计算：四个独立前缀](../../artifacts/experiments/chan_theory/memo0040_figures/01c_independent_prefixes.png)

[example] **主例 · 3 / 8 / 11 / 14笔分别通过公开入口实测。** 图1.c：四幅分别从空状态计算。第8笔已有局部候选仍不足以建立首段；第11笔能接成候选对，第14笔才在本例第一次冻结A→F。

- **一次调用：** 收到当前完整笔列表，重新建状态机；下一次增加数据后，重新计算，不接着上次的N0/N1继续。`frozen`表示本次状态机已冻结，不能据此承诺跨调用身份不变。
- **一轮主循环：** 可以扫描后面多笔、取得候选或改变状态，并非只接收下一笔。候选识别还可能查看当前特征笔后第二笔。
- **三个位置：** 线段端点、当前扫描下标、证据下标可以不同。例如主例端点在B5，识别证据到B8，整段冻结更晚。
- **前缀：** 首段起点失败就逐笔右移；选中较晚起点时，之前的输入可不属于任何输出段。没有删除这些输入。
- **内部：** 正常构造链以`上一段.end_bi+1`接下一段的首笔，没有主动跳笔建内部断档。
- **尾部：** 最右输出选某方向的极值笔，可能早于最后输入；不保证覆盖全部尾笔。

## 2. Decision Workflow

### 2.a 总树：从入口到输出

**KWX先找“本方向候选＋紧接的反方向候选”，再进入候选状态机；前三笔重叠是在冻结检查里使用的条件。** 候选搜索不会先照0032的前三笔端点树筛起点。

<!-- memo0040-figure:02a_entry_output -->
![2.a 入口长度检查与完整输出](../../artifacts/experiments/chan_theory/memo0040_figures/02a_entry_output.png)

[example] **主例截断及完整输入 · 均调用build_xianduans。** 图2.a：两笔时入口直接返回[]；主例16笔时经真实完整流程输出一条frozen、一条soft和一条forming。

```text
2.a build_xianduans(bis, cfg)
├── 笔数 < 3 → 返回 []，不进入 Builder
└── 笔数 ≥ 3 → normalize 配置，新建状态机
    └── 2.b 从第一笔起搜索首段起点
        ├── 所有起点都失败 → 2.h 输出兜底 forming
        └── 找到起点 → 重算其候选，放入 N0
            └── 主循环（最多 4 × 笔数轮）
                ├── 没有 N1 → 2.d 延长 N0 或建立 N1
                └── 已有 N1 → 2.e 算出裁决，2.f 执行状态变化
                    ├── 状态改变 → 下一轮主循环
                    └── 停止 / 检查失败 / 达轮数上限 → 2.h 输出

共同子树
├── 2.c 固定起点找一个候选：特征元素 → 分型 → 端点校验
├── 2.g 延长、强势单笔、第二特征序列、冻结检查
└── 2.i 只读特征矩形显示（不参与上面的线段计算）
```

`normalize()`按预设覆盖对应策略字段；单独改一个策略字段不一定改变实际预设行为。`profile_id/config_hash`由调用者传给入口，输出沿用这些字符串。[2]

| 预设 | 强势单笔 | nonstandard / oscillation | 实际核心差别 |
| --- | --- | --- | --- |
| `standard` | 关 | off / off | 默认流程 |
| `standard_strong` | 开 | off / off | 增加2.g.2两个调用点 |
| `practical` | 开 | repair / three_bi | 后两开关被保存，但本版本核心没有执行分支 |

`left_method`也没有在当前Builder中执行独立策略。因此不能从配置枚举名称推断出已经实现的算法。

### 2.b 首段搜索：固定一个起点，能否接成候选对？

**首段起点由“本候选之后能否立刻接上反向候选”选出，单独出现第一个候选还不够。** 每次固定起点`s`及首笔方向；2.c负责在这个起点后搜索，失败才换下一个起点。

<!-- memo0040-figure:02b_candidate_pair -->
![2.b 首段必须能接上反向候选](../../artifacts/experiments/chan_theory/memo0040_figures/02b_candidate_pair.png)

[example] **主例 · 同一起点A，比较8笔与16笔的首段搜索。** 图2.b：A→F单独成立还不够。8笔输入下首段搜索继续换起点并耗尽；16笔输入能紧接F→I，才选择A。

```text
从 s=0 开始，逐笔尝试 s=0,1,2,…,n−1
├── 以 Bi[s].direction 为暂定段方向，调用 2.c 找 c
│   ├── c=None → s 加一，重新调用 2.c
│   └── c 存在 → 固定 c.end+1 为反向候选起点，调用 2.c 找 rev
│       ├── rev=None → s 加一；不保留这次 c，不在原 s 换另一条 c
│       └── rev 存在 → 返回 (s,方向)，首段搜索结束
└── 所有 s 都试完 → 返回 None 给 2.a → 2.h
```

这里只返回起点和方向，**不冻结c，也不保存这对候选**。`run()`随后重算c并放入N0；若重算意外返回None，代码仍转2.h兜底。

主例从B1（代码下标0）选中起点；失败后右移的真实入口例见3.b。

### 2.c 候选搜索：固定起点，找第一个端点合格的特征分型

**候选搜索要找到一个局部转折，并保证它给出的线段起终点确实是该区间两端的极值。** 固定`begin`和段方向；例如主例上升段固定A=100，前三笔是100→130→110→120，仍继续处理后面的下降特征笔，最终候选可以到F=140。

<!-- memo0040-figure:c_candidate -->
![2.c 固定起点：分型端点还要通过整段极值检查](../../artifacts/experiments/chan_theory/memo0040_figures/c_candidate.png)

[example] **主例前8笔／独立失败例，均为真实候选辅助调用。** 上图主例在B8读到分型，返回A100→F140候选；下图虽在D12出现分型峰值，但C2低于固定起点A5，端点校验失败，从B4重建后耗尽，返回None。

```text
2.c _candidate(begin, direction)
├── 新建空识别器；从 begin 按笔下标向右扫描
│   ├── 当前笔不是反向笔 → 跳过这次喂入，扫描下一笔
│   └── 当前笔是反向笔 → add：先把下标追加到lst，再按元素槽位处理
│       ├── 没形成分型 → 扫描下一笔
│       └── 形成分型 → 2.c.5 选端点 end
│           ├── end−begin < 2，或2.g.1端点极值失败
│           │   └── begin不变；清空识别器，从 end+1 重扫
│           └── 两项均通过
│               └── 返回一个候选：begin..end，rule=gap 或 feature_seq，
│                   dep=last_evidence（无值才用end）
└── 扫描到输入末尾仍无合格候选 → 返回 None 给调用者
```

重扫从**被否定端点的后一笔**开始，可能比刚才的扫描笔更靠左；不是简单接着失败证据笔继续。它只重建派生识别器，不裁剪输入。这里不另查奇数笔／首三笔重叠，冻结时才调用2.g.4。

`add`的统一分派是：e0空→2.c.2建立e0；否则e1空→2.c.2处理第二元素；否则e2空→2.c.3。三槽都满后再喂入会抛内部不变量异常，正常调用者在分型成功后已停止喂入或重建识别器。每次喂入，包括2.c.6的重放，都只在`add`入口追加一次`lst`。

下面的元素子树也供2.g.3使用。“返回当前驱动”指回到创建这个识别器的扫描循环：第一序列回2.c，第二序列回2.g.3；它们收到同一个分型结果后，执行的后续检查不同。

#### 2.c.1 包含：先判谁包含谁，再按线段方向合并

**包含处理把相邻特征笔压成一个用于比较的元素，同时保留每根来源笔。** 固定旧元素`E=[L,H]`，新笔为`b=[l,h]`；方括号表示价格范围，不是笔的行进方向。

<!-- memo0040-figure:c1_containment -->
![2.c.1 先判包含方向，再由当前槽位决定是否合并](../../artifacts/experiments/chan_theory/memo0040_figures/c1_containment.png)

[example] **主例局部／独立区间检查。** 旧元素包含新笔时恒合并。新笔包含旧元素时，第二槽保留两项，第三槽通常合并；合并取值跟随研究中的线段方向，原始来源笔保留。

```text
E.test_combine(b, exclude_included, allow_top_equal)
├── H≥h 且 L≤l：旧元素包含新笔（完全相等也在这里）
│   └── combine
├── H≤h 且 L≥l：新笔包含旧元素
│   ├── allow=+1 且 H=h、L>l → down
│   ├── allow=−1 且 L=l、H<h → up
│   ├── 否则 exclude=True → included
│   └── 否则 → combine
├── H>h 且 L>l → down
└── 其余 → up
```

`combine`才修改旧元素；`included/up/down`都是返回分类，后续动作由2.c.2或2.c.3决定，不能从分类名直接推出整个算法分支。

| 合并政策 | 新元素 high | 新元素 low | 来源 |
| --- | --- | --- | --- |
| 研究上升线段 | `max(H,h)` | `max(L,l)` | 旧`idxs`追加当前笔下标 |
| 研究下降线段 | `min(H,h)` | `min(L,l)` | 同上 |

**主例：** 研究上升线段，B2=`[110,130]`包含B4=`[115,120]`，合并为`[115,130]`，来源为`[B2,B4]`。依据是**上升线段方向**，不是两根下降笔的方向。后面必须用115这个新low比较；原B2的110仍保留在输入，不能拿来冒充当前元素的low。

#### 2.c.2 第一、第二元素：保留可以继续形成转折的前两项

<!-- memo0040-figure:c2_second -->
![2.c.2 第二槽：低了就重排，同高先保留](../../artifacts/experiments/chan_theory/memo0040_figures/c2_second.png)

[example] **主例／独立反向笔喂入检查。** 主例B4先合并回e0，B6才成为e1。排除合并并建立e1后，上升方向只在H1<H0时重排；H1=H0会保留两项，并不表示最终分型已经成立。

```text
当前笔已在add入口追加到lst
├── e0为空 → 当前笔成为 e0；返回“无分型”给当前驱动
└── e0存在、e1为空
    └── e0与新笔比较：exclude=True，allow=None
        ├── combine → 合并进 e0；返回“无分型”
        └── included / up / down → 保留 e0，新笔成为 e1
            ├── 上升且 e1.high<e0.high → 2.c.6 重排
            ├── 下降且 e1.low>e0.low → 2.c.6 重排
            └── 其余（包括上述比较相等）→ 保留 e0/e1；返回“无分型”
```

第二元素的方向检查是严格`<`／`>`；注释“不高于／不低于”比实际代码更宽，不能按注释把等号也判失败。

#### 2.c.3 第三元素：先做实际突破，再判三个元素的形状

**第三根喂入笔未必成为e2，它可能继续合并进e1。** e0保持不变；固定当前e1为比较对象。

<!-- memo0040-figure:c3_third -->
![2.c.3 已有e0/e1：新笔先比较包含，未必建立e2](../../artifacts/experiments/chan_theory/memo0040_figures/c3_third.png)

[example] **两个独立连续价格输入；真实_EigenFX喂入。** 上图B6被e1包含，更新e1并继续；下图B6与e1同高但更低，命中上升段第三槽的相等例外，保留为e2，再通过实际突破与顶分型。

<!-- memo0040-figure:c3_lookahead -->
![2.c.3 第一序列前看：扫描B8，证据可以来自B10](../../artifacts/experiments/chan_theory/memo0040_figures/c3_lookahead.png)

[example] **独立输入的8笔前缀与10笔完整输入；候选辅助检查。** B4/B6合并后的e1是[4,11]，末来源B6仍是[1,11]。B8.low=3未低于1；完整输入的B10.low=2低于B8.low=3，前看遂通过，但2仍未低于1。

```text
e0/e1存在，e2为空；last_evidence=当前笔下标
└── e1与新笔比较：exclude=False；上升allow=+1，下降allow=−1
    ├── combine → 合并进 e1；返回“无分型”给当前驱动
    └── 其余分类 → 新笔成为 e2
        └── 检查实际突破
            ├── 不通过 → 2.c.6 重排
            └── 通过 → 2.c.4 分型公式
                ├── 不通过 → 2.c.6 重排
                └── 通过 → 标记 e0/e1 缺口；返回“有分型”
```

**实际突破的比较对象取决于序列角色：**

| 序列角色 | 上升段要求 | 下降段要求 | 不通过后的动作 |
| --- | --- | --- | --- |
| 第一序列`PRIMARY` | `e2.low < e1末来源笔.low` | `e2.high > e1末来源笔.high` | 尝试下面的后第二笔前看 |
| 第二序列`GAP_REVERT` | `e2.low < 合并后e1.low` | `e2.high > 合并后e1.high` | 直接失败，重排 |

第一序列直接比较失败时，令`k=e2第一来源笔下标`。只有`k+2<n`才查看后第二笔：上升段要求`Bi[k]`下降且`Bi[k+2].low < Bi[k].low`；下降段要求`Bi[k]`上升且`Bi[k+2].high > Bi[k].high`。成功就把`last_evidence`改为`k+2`，再执行2.c.4；否则重排。这里没有额外检查`Bi[k+2]`的方向；正常交替由上游保证。

前看不会把后第二笔合并到e2，也不改变候选端点；它只为突破提供证据。`last_evidence`是代码写入的记录，失败的前看不会把水位推进到`k+2`，不要把它当成完整读取日志。

**前看也不要求后第二笔突破e1末来源笔。** 独立局部例：e1由`[4,10]`和`[1,11]`合并为`[4,11]`，e2=`[3,10]`。直接比较`3<1`失败；后第二笔low=2满足`2<3`，就允许继续判分型，虽然2仍高于1。第3.c记录此连续价格例及截断输入检查。

#### 2.c.4 分型与缺口：公式按源码保留等号

<!-- memo0040-figure:c4_fractal -->
![2.c.4 分型公式：允许哪一侧相等，缺少哪一项比较](../../artifacts/experiments/chan_theory/memo0040_figures/c4_fractal.png)

[example] **独立连续输入的真实窗口检查；展示形成分型前的三项。** 上升顶式为H0<H1、H2≤H1、L2<L1，没有另查L0<L1。上图中间低点反而低于左项仍成功；中图H0=H1失败；下图是上图的下降镜像。

<!-- memo0040-figure:c4_gap -->
![2.c.4 分型成功之后：缺口用当前e0/e1价格区间判断](../../artifacts/experiments/chan_theory/memo0040_figures/c4_gap.png)

[example] **三个独立输入；每组均真实形成分型并返回候选。** 三图只改变e1下沿及配套右元素，比较重叠、点接触、严格分离。上升段仅H0<L1算缺口；H0=L1无缺口，缺口不是时间断档。

```text
已通过实际突破
├── 上升段：H0<H1 且 H2≤H1 且 L2<L1
│   ├── 不成立 → 2.c.6 重排
│   └── 成立 → gap=(H0<L1)，返回“有分型”
└── 下降段：H2>H1 且 L0>L1 且 L2≥L1
    ├── 不成立 → 2.c.6 重排
    └── 成立 → gap=(L0>H1)，返回“有分型”
```

`Hi/Li`是处理后`ei`的高低价。顶分型**没有另查`L0<L1`**，底分型**没有另查`H0>H1`**。例如独立局部顶形状`e0=[100,110]、e1=[105,120]、e2=[102,120]`允许`H2=H1`；它还必须通过前面的实际突破处理，才会被调用者接受。不能据此改写为项目的四项严格分型。

两个检查有共同约束：第一序列若直接突破成功，上升合并保证`e1.low≥末来源笔.low`，所以已经推出`L2<L1`；下降镜像也成立。第二序列的突破条件本身就是分型公式中的这一项。**前看成功则不自动推出它**，仍需用原三个元素检验。源码保留完整公式，此处不删重复比较。

缺口在分型成立后用**当前合并值**判断；等于边界就是无缺口。`gap`只给候选来源分类，尚未冻结。

#### 2.c.5 候选端点：回到中间元素的来源笔找峰谷

**线段端点取e1里真正提供极值的反向笔的前一笔。** 它不是e1最后一个来源下标，也不是当前证据笔。

<!-- memo0040-figure:c5_peak_sources -->
![2.c.5 端点回到e1原始来源：同价选先出现者](../../artifacts/experiments/chan_theory/memo0040_figures/c5_peak_sources.png)

[example] **两个独立连续输入；来源笔编号不重编。** 两图的e1均保留B4/B6来源。上图两来源high同为10，选先来的B4，端点是B3末端D；下图B6.high=11更高，改选B6，端点是B5末端F。

```text
e1.idxs按加入顺序排列
├── 上升：选来源笔 high 最大的第一笔 p → end=p−1
└── 下降：选来源笔 low 最小的第一笔 p → end=p−1

端点返回调用者
├── 第一序列：回2.c检查候选长度和端点极值
└── 第二序列：回2.g.3，直接把peak=end作为返回值的一部分
```

同价并列时，Python的`max/min`保留序列中**第一个**达到该值的来源。主例e1为B6=`[125,140]`，`p=B6`，故段端点是B5末端F=140；识别e2需要B8，B8不属于这个候选区间。

#### 2.c.6 重排：丢掉最早喂入记录，再重放其余原笔

**重排重新寻找局部三元素，不改变外层候选起点。** 它删除的是当前识别器`lst`中第一根原始特征笔的记录，不是把整个合并e0丢掉。

<!-- memo0040-figure:c6_reset -->
![2.c.6 重排按原始笔重放：合并过的B4仍会再参与](../../artifacts/experiments/chan_theory/memo0040_figures/c6_reset.png)

[example] **独立_EigenFX喂入检查；没有宣称完整入口选择此起点。** B2/B4先合并为e0=[4,10]；B6.high=8使拟建第二项失败。重排先去掉B2并重放B4/B6，仍失败再去掉B4，最后仅保留B6作为新e0；原始六笔全在。

```text
rest=lst[1:]，按原时间顺序保留
└── 清空 e0/e1/e2 和 lst；逐根重新 add(rest中的笔)
    ├── 某次add形成分型 → 立即返回True给原调用者，停止重放
    └── 全部重放完仍无分型 → 返回False，当前驱动继续外层扫描
```

例如`lst=[B2,B4,B6,B8]`，即使e0曾由B2/B4合并，重排仍重放`B4,B6,B8`，不是只剩B6/B8。重放里可再次发生重排；输入`bis`始终未删。源码不在`_reset()`中显式清空`last_evidence`，后续第三元素处理会写它；调用者只在分型成功时取证据值。

### 2.d 只有N0：先给N0延长机会，再建立N1

**此时要决定N0能否接着向原方向生长，还是可以保留一个紧接的反向候选。** 起点保持固定；所有搜索都从N0末笔之后开始。

<!-- memo0040-figure:d_no_n1 -->
![2.d 只有N0：先查原方向新高，再登记反向N1](../../artifacts/experiments/chan_theory/memo0040_figures/d_no_n1.png)

[example] **主例入口轨迹。** 主例N0为A100→F140。反向候选rev为F140→I120；限定在B6..B8内，唯一上升笔B7的high=135未超过140，所以N0不延长，rev登记为N1。下一轮进入2.e。

<!-- memo0040-figure:d_extend_absorb -->
![2.d 相同的新高16：普通延长与越起点吸收](../../artifacts/experiments/chan_theory/memo0040_figures/d_extend_absorb.png)

[example] **人工给定状态。** 两个独立输入都先给定N0=B1..B3、上升0→15，且rev=None、首个新高为B5的16。上例新增范围最低8≥0，ep=None，普通延长；下例B4跌到−2<0，ep=start，满足T7并标pen_break_absorb。两支都保持起点0，改终点为16，再回主循环。

先调用2.c找反向标准候选`rev`；随后在“下一笔到rev末笔”内找N0方向首个新极值，若无rev则扫描到输入末尾。记其为`ext`；存在时用2.g.1检查延长后的整段，得到`ep=None/start/end`。若ext不存在，代码令ep=None，不调用这次极值检查。

```text
N0存在，N1为空（按下面顺序裁决）
├── N0不是strong，ext存在，ep=None
│   └── 只改 N0.end/end_key → 下一轮2.a
├── N0不是strong，rev=None，ext存在，ep=start
│   └── 延长 N0；rule改pen_break_absorb；更新越点标记 → 下一轮2.a
├── rev=None
│   └── 停止主循环 → 2.h（不会再试下面的strong分支）
└── rev存在
    ├── strong选项开且2.g.2成功 → 将strong单笔候选放N1 → 下一轮2.a
    └── strong关闭或失败 → 将rev放N1 → 下一轮2.a
```

`pen_break_absorb`表示把一次越过起点、未形成反向候选的过程纳入原段；起点不移动，原输入保留。`pen_break_at`在“旧N0末笔之后到ext”中，取上升时最低low／下降时最高high的严格越界者，同价取第一笔；**若新增范围没有越界者，代码回退到该范围第一笔，并覆盖旧标记**。例如重复吸收时，整段的`ep=start`可能来自旧区间，不能断言每次标记都是真越界笔。冻结时走2.g.4的特殊检查。

延长操作只改代码列出的字段：不会重算`dep`，普通延长也不清除原`rule/pen_break_at`。因此不能把候选的旧`dep`解释为这次延长已重新核算的全部依赖。

### 2.e 已有N0/N1：先算后续候选，再按固定优先级裁决

**这里决定保留N1、延长N1，还是让N0跨过失败的反向尝试继续生长。** N1起点被某笔越过，并不立即撤销N1。

<!-- memo0040-figure:e_priority -->
![2.e 双候选裁决：本轮confirm，换位后下一轮none](../../artifacts/experiments/chan_theory/memo0040_figures/e_priority.png)

[example] **主例入口轨迹。** 主例先算N2=I120→L133；N1=F140→I120在限定B9..B11内没有新低，因而不延长，标准N2使本轮返回confirm。2.f换位后，新N1为I120→L133：后续没有新高，没有跌破起点120，也没有后继候选，最终返回none并转输出。这不是把全部证据按时间排序。

首先调用2.c，从`N1.end+1`按N0方向算标准N2。随后按下树裁决：**计算N2在前，优先采用N1延长在前**，两者不能混为一件事。

```text
已算 standard N2（可能None）
├── N1非strong；在下一笔..N2.end（无N2则到末尾）找到N1新极值
│   且延长后的N1通过2.g.1
│   └── 返回 extend_n1 → 2.f
└── 未命中上项
    └── 从N1之后到输入末尾，分别计算 brk、rev
        ├── strong开且2.g.2(N1)成功 → confirm(strong N2) → 2.f
        ├── 否则 standard N2存在 → confirm(N2) → 2.f
        ├── 否则 brk和rev都存在
        │   └── 调用_extend_extreme(N0,rev.index)，在旧N0.end..rev.index
        │       按2.g.1选延长目标，再检查延长后整段
        │       ├── 端点极值有问题 → rollover → 2.f
        │       └── 端点极值通过 → break(新末笔,价位) → 2.f
        └── 否则
            ├── N1.rule=gap → 运行2.g.3取得rc
            │   ├── rc存在，且 brk不存在或rc证据下标≤brk → gap_revert → 2.f
            │   └── 不满足 → none → 2.f
            └── N1不是gap → none → 2.f
```

- **`brk`是起点破坏证据：** 顺时扫描全部后续笔；上升N1找第一笔`low < N1.start_key`，下降找`high > N1.start_key`；等号不算。此函数不筛笔方向。
- **`rev`是N1方向再创新极值的证据：** 2.g.1找第一根同向笔，上升`high > N1.end_key`／下降`low < N1.end_key`；它不是上节的反向候选`rev`。
- **顺序边界：** 代码要求两项都存在，却没有再检查`brk<rev.index`；也没有将所有证据按出现时间排序。完整N2优先于`gap_revert`，不能把注释“先到先判”当成全局规则。
- **`none`的出口：** 本次停止主循环并输出；等新数据再次调用时重算整串笔，不保存一个暂停执行点。

### 2.f 执行裁决：改变哪些对象，然后去哪里？

**2.e只返回裁决，真正的冻结、换位和撤销在本节执行。** 下表的“下一轮”始终指2.a主循环；“输出”指2.h。

<!-- memo0040-figure:f_confirm -->
![2.f confirm只冻结旧N0，N1与N2各向左换位](../../artifacts/experiments/chan_theory/memo0040_figures/f_confirm.png)

[example] **主例入口轨迹。** 主例候选依次为A100→F140、F140→I120、I120→L133。旧N0通过冻结检查后，T3复制它进入frozen，旧N1原对象成为新N0，临时N2成为新N1。几何不变，只改变角色；N2不是本轮冻结对象。

<!-- memo0040-figure:f_break -->
![2.f break撤销的是N1候选，输入笔仍保留](../../artifacts/experiments/chan_theory/memo0040_figures/f_break.png)

[example] **人工给定状态。** 给定N0=B1..B3（0→15）、N1=B4..B6（15→6）。B7.high=16>15破N1起点，B8.low=4<6又给出N1方向新低；后继N2搜索失败。按rev所在B8限定范围，N0同向最高点在B7=16，延长后的起点仍为最低0，因此返回break，清N1并把N0延到B7；下一轮从B8重找反向候选。

| 裁决 | 本步执行的检查与变更 | 下一步 |
| --- | --- | --- |
| `extend_n1` | 只改N1末笔和`end_key`；起点、rule、dep保留 | 下一轮 |
| `confirm(N2)` | 对N0执行2.g.4；通过则复制N0到frozen，N1升N0，N2放N1 | 通过→下一轮；失败→输出 |
| `break(end,key)`，N0非strong | 撤销N1；延长N0到指定末笔，更新end/key；其他元数据保留 | 下一轮 |
| `break`，N0为strong | 不延长单笔；对N0执行2.g.4，通过则冻结N0，N1升N0，清空N1 | 通过→下一轮；失败→输出 |
| `rollover` | 对N0执行2.g.4，通过则冻结N0，N1升N0，清空N1 | 通过→下一轮；失败→输出 |
| `none` | 不改候选或frozen | 输出 |

这里撤销的是N1候选对象，输入笔仍在。`confirm`本轮冻结的是**原N0**，不是新来的N2；原N1换位后仍是未冻结N0。

**`gap_revert(evidence,peak)`额外有以下完整出口：**

```text
先查 N0与N1都通过2.g.4、方向相反、N1.start=N0.end+1
├── 任一不满足 → 不做原子冻结，停止主循环 → 2.h
└── 全部满足
    ├── 记 next_begin=N1.end+1，next_dir=反N1方向
    ├── 将N0和N1一起复制到frozen；两者dep=evidence，
    │   confirmation_ts=证据笔.end_ts，frozen_by=gap_revert
    └── 清空N0/N1，尝试建立下一个seed候选
        ├── peak−next_begin≥2，且首末笔都与next_dir同向
        │   └── N0=next_begin..peak，rule=feature_seq，dep=peak → 下一轮
        └── 不满足 → 保留刚冻结的两段，停止主循环 → 2.h
```

seed是第二序列的峰谷给出的下一段初始候选；这里没有另跑2.c，也没有当场执行完整2.g.4／端点极值检查。后续是否冻结，继续受主循环约束。

### 2.g 共同检查：极值、强势单笔、第二序列与冻结

#### 2.g.1 极值：固定起点和终点，检查整段是否越界

**端点极值检查比较整段与候选两端，不比较“前三笔形状”。** 主例A=100至F=140允许中间反复，只要求这一范围没有低于100的low或高于140的high。

<!-- memo0040-figure:02g1_endpoint_extremes -->
![2.g.1 整段极值检查：通过、起点失败、终点失败](../../artifacts/experiments/chan_theory/memo0040_figures/02g1_endpoint_extremes.png)

[example] **第一幅为主例候选；后两幅为独立局部helper输入。** 图2.g.1a：A→F通过；100→130→90→140因90<100返回start；100→130→110→120因130>120返回end。这里仅验证极值helper，不宣称独立例已由入口生成候选。

<!-- memo0040-figure:02g1_first_or_highest -->
![2.g.1 第一次创新高，与范围内最高点](../../artifacts/experiments/chan_theory/memo0040_figures/02g1_first_or_highest.png)

[example] **独立局部helper例 · 人工给定N0=代码0..2，未证明入口会生成该N0。** 图2.g.1b：固定同一个旧N0，第一创新高返回150；指定范围的方向极值返回160。两个helper结果均由当前源码直接核对。

```text
_extreme_problem(start,end,direction)，遍历含首尾的整段笔
├── 上升：任一low < 首笔.low → start
│         否则任一high > 末笔.high → end
├── 下降：任一high > 首笔.high → start
│         否则任一low < 末笔.low → end
└── 均无越界 → None（通过）；等于端点允许
```

起点失败优先于终点失败。2.c据此否定局部分型并重建序列；2.d决定普通延长／吸收；2.e决定延长／转接；2.g.4用它控制一般段冻结，各调用者出口不同。

两种“找新末笔”也不同：

- **`_first_new_extreme(seg,begin,limit)`：** 固定`seg.end_key`，从begin至limit逐笔扫描，只看同方向笔，取**第一笔**严格创新高／低者；没有则None。等价不更新，区间右界截到输入末尾。被调用多次时，上一轮延长已改变比较端点。
- **`_extend_extreme(N0,limit)`：** 当N1失败时，在**旧N0末笔到limit**内取同向笔的最高high／最低low；同价取最早者。无同向笔才退回比较该范围全部笔。所得末笔交2.e检查，再由2.f改变对象；不是直接把N0延到limit。

#### 2.g.2 strong_bi：强势单笔必须有紧接的反向标准候选作证据

**此选项尝试把前段之后的第一根反向笔单独作为一段；仅越过前段起点还不够。** 例如独立示意：前段上升100→130，紧接一笔130→90越过100，仍须从90开始找到紧接的上升标准候选，才返回这根下降单笔候选。

<!-- memo0040-figure:g_strong -->
![2.g.2 越起点单笔：紧接反向候选出现后才由helper返回](../../artifacts/experiments/chan_theory/memo0040_figures/g_strong.png)

[example] **人工给定状态。** 给定前段上升100→140，紧接B4下降至90，严格越过起点100。只有这次越界仍不够；当紧接B5起的上升候选90→130形成、证据到B10时，helper才返回只含B4的strong候选（dep=B10）。上图截至B7，尚无足够证据，helper返回None。这里检查helper，不声称主入口必定会调用它。

```text
_try_strong_bi_break(prev_seg)，固定 s=prev_seg.end+1
├── s超出输入 → None
├── Bi[s]不与prev_seg反向 → None
├── 未严格越过prev_seg.start_key → None（触平失败）
└── 调用2.c，从s+1按prev_seg方向找标准候选rev_std
    ├── rev_std=None或其起点不是s+1 → None
    └── 成功 → 返回只含Bi[s]的strong候选，dep=rev_std.dep
```

前段上升时检查`Bi[s].low < start_key`，前段下降时检查`Bi[s].high > start_key`。返回None不是等待指令：2.d在已有标准rev的前提下退回rev；2.e继续试标准N2、双证据、缺口分支。2.d若rev=None会更早退出，根本不调用本子树。

此处返回候选不立即冻结单笔；strong候选在后续处于N0并通过相应冻结事件，才进入frozen。strong作N0或N1时，普通延长被禁止。

代码所谓“反向标准段”实际是2.c返回的候选，可能带`gap`，还没有在本辅助中经过冻结检查。`rev_std.start=s+1`已由2.c固定起点保证，树里仍保留源码的防御检查。

#### 2.g.3 gap_revert：第二特征序列只找反向分型，不递归找第三序列

**本子树用缺口N1之后的反向结构，补充当前没有完整N2的情况。** 它只在2.e前面更高优先级分支都未命中时调用。

<!-- memo0040-figure:g_second -->
![2.g.3 缺口候选之后：第二序列返回证据笔与下一段峰谷](../../artifacts/experiments/chan_theory/memo0040_figures/g_second.png)

[example] **局部检查。** 第一序列产生上升候选B1..B3（0→15），e0.high=10<e1.low=11形成价格缺口。第二序列从B5（端点B3后第二笔）开始，只喂上升笔，研究下降方向：元素为[11,14]、[4,10]、[6,12]。底分型成立，helper返回evidence=B9、peak=B6；B9是证据，B6末价4是下一段seed的候选终点，两者不可互换。第二序列自身也有11>10的缺口，但不会递归寻找第三序列。

```text
固定被检查段方向 seg_dir、端点 peak_end
└── begin=peak_end+2
    ├── begin超出输入，或Bi[begin].direction≠seg_dir → None
    └── 新建反seg_dir方向识别器，role=GAP_REVERT
        └── 从begin到末尾逐笔扫描，只喂seg_dir方向笔
            ├── 尚无分型 → 扫下一笔
            ├── 第一个分型形成
            │   └── 返回(evidence,第二序列峰谷前一笔peak)给2.e
            └── 扫描耗尽 → None给2.e → none裁决
```

识别器共享2.c.1～2.c.6中的元素合并、分型、重排和峰谷定位，但实际突破使用合并e1的严格比较、**没有后第二笔前看**。重排无分型就回本节扫描；一旦有分型，直接返回`peak`和`evidence=last_evidence`（无值才用当前扫描下标），**不转去执行2.c的候选长度／端点极值检查**。这里不再检查第二分型是否有缺口，也不要求它自己形成完整标准候选；`peak`用于2.f的seed，`evidence`用于时间比较和冻结元数据，不能互换。

#### 2.g.4 冻结检查：一般段、吸收段与strong段走不同条件

**冻结检查决定当前N0（gap_revert时还有N1）能否进入固定结果，不负责重新搜索起点。** 检查失败会停止本次主循环并转2.h输出，并非回2.b重新选起点。

<!-- memo0040-figure:g_freeze -->
![2.g.4 冻结gate：同一几何可因rule走不同检查](../../artifacts/experiments/chan_theory/memo0040_figures/g_freeze.png)

[example] **人工给定状态。** 给定三笔0→10→−2→0，首三笔交集只有价格0，因此basic_valid通过；但−2<首点0，普通候选端点检查失败，gate=False。把同一人工候选的rule改为pen_break_absorb，代码豁免端点检查，gate=True。第三图取前图2.g.2已由helper返回的140→90强势单笔；strong分支只查一笔和方向，gate=True。gate成功本身仍不是冻结事件。

```text
_gate_ok(candidate)
├── rule=strong_bi
│   └── 只查 start=end 且这一笔方向等于段方向 → True/False
└── 其他rule → _basic_valid
    ├── 笔数<3或为偶数 → False
    ├── 首笔或末笔与段方向不同 → False
    ├── 首三笔 max(low) > min(high) → False
    └── 基础检查通过
        ├── rule=pen_break_absorb → True，不再查端点极值
        └── 其余 → 2.g.1无问题才True
```

**KWX前三笔重叠允许点接触：** `max(low) ≤ min(high)`。独立局部例`0→10→−2→0`的三笔区间为`[0,10]、[−2,10]、[−2,0]`，交集只有0，`_basic_valid=True`；但上升段内部low=−2低于首笔low=0，端点检查返回`start`。这是两项不同检查，不能从重叠通过推出入口接受此起点，更不能说入口先执行了这个局部基础检查。

这与0032“正宽度才重叠”不同，也与“升—降—升的每次上升必须创新高”不同。strong的破坏／后续证据已经在2.g.2检查，冻结时不重复计算。

### 2.h 输出：内部状态如何变成最终线段列表？

**输出保留已冻结线段，并把右侧尚未确定的部分表示为最多一条forming；forming是显示结果，不新增内部候选。** 主例最终输出A→F、F→I、I→L，L之后仍有输入笔。

<!-- memo0040-figure:02h_output_coverage -->
![2.h 输出状态与没有覆盖的尾笔](../../artifacts/experiments/chan_theory/memo0040_figures/02h_output_coverage.png)

[example] **主例 · 16笔公开入口结果；背景保留所有16笔。** 图2.h：主例输出到L为止，L之后B12—B16仍保留在输入，但没有被线段覆盖。形成中线的规则标签与内部候选来源不同。

```text
_emit(sm)
├── 依次复制 frozen[] → FROZEN输出
├── 若有N0 → 复制其范围/rule/dep/越点标记 → SOFT_N0输出
└── 按顺序选择右侧输出
    ├── 有N1
    │   └── end=max(N1.end, forming_end(N1.start,N1.direction))
    │       输出rule=forming、state=PENDING_N1、dep=N1.dep
    ├── 否则有N0且其后仍有笔
    │   └── 从N0.end+1按反方向画forming，dep=n−1
    ├── 否则N0/N1皆空，但有frozen且其后仍有笔
    │   └── 从最后frozen.end+1按反方向画forming，dep=n−1
    └── 上述均不适用 → 不加尾线

最后检查：若整个out为空且n≥1
└── 从Bi[0]按其方向画一条forming，state=PENDING_N1、dep=n−1
```

`forming_end(start,d)`扫描从start到输入末尾的同向笔，选上升最高high／下降最低low，**同价取第一笔**；无同向笔的防御分支返回start。并非取最后一笔，也不是同价里的最新一笔。公开入口和`Builder.run()`都在笔数<3时返回[]；只有绕过它们直接调用`_emit`，才可能对一两笔生成这里的兜底。

所有尾部forming均标`PENDING_N1`。有内部N1时，它的`gap/strong_bi`等来源rule在输出步骤统一变成`forming`，还可能只在输出中被延长；原N1对象没有因此变化。N1输出不复制`pen_break_at/confirmation_ts/frozen_by`，使用默认None／None／空串；N0输出也没有复制`confirmation_ts/frozen_by`。frozen输出则复制全部相关冻结元数据。

**`_finish`依次把工作结果转换为`Xianduan`：**

- 起终点时间和价格取首末Bi；方向取工作对象；`high/low`取区间成员笔的最大／最小值。
- 来源范围取首末笔trace；缺少对应来源时间时回退首笔`start_ts`／末笔`end_ts`。合并索引缺trace时为None。
- trace保存规则映射、调用者给的profile/hash、`dep`、冻结状态、越点笔和冻结证据；未知rule回退到特征序列规则名。
- 输出列表按工作对象顺序排列；它不再次执行候选／冻结检查，不补齐前缀或尾部未覆盖笔。

### 2.i 图上的特征矩形：单独的显示入口

**特征矩形帮助看到价格区间和来源笔，但普通矩形列表不是2.c运行时识别器窗口的逐帧记录。** `build_feature_sequence_overlays`另建Builder、重新计算，然后生成显示单元。[3]

<!-- memo0040-figure:02i_display_overlays -->
![2.i 最终显示框不是候选搜索窗口的重放](../../artifacts/experiments/chan_theory/memo0040_figures/02i_display_overlays.png)

[example] **主例 · 真实build_feature_sequence_overlays输出；不参与确认。** 图2.i：真实显示接口输出的PRIMARY与TAIL_PROBE。框的范围和算法识别器三槽窗口不同；这些框不修改候选或冻结状态。

```text
显示入口
├── 输入少于3笔 → []
└── 重新算工作线段
    ├── primary：各段取反向笔；最后一段的显示范围延至输入末尾
    │   └── 简单包含合并，exclude=False、allow=None；不做分型重排
    ├── frozen且rule=gap：按2.g.3同源驱动生成第二序列矩形
    │   └── 第一个分型即停；未成分型则返回当前部分元素
    └── 最后工作段之后还有笔：为假设的反向段生成tail_probe
        └── 取与最后段同向的笔，表示探测，不是已确认线段
```

普通primary／tail_probe的合并允许双向包含，不执行实际候选的第二元素排除政策、三元素检查或重排。第二序列显示使用独立识别器实例，不修改算法状态。

[code discrepancy] 当前显示入口构造Builder时**没有传入`strong_bi`**，而主入口会传；因此不能假设`standard_strong/practical`的矩形底层分段总与主入口一致。本篇记录该差异，未改源码。

## 3. Test Session And Examples

### 3.a 固定主例：前三笔没有再创新高，仍从原起点搜索

整章固定以下输入；B1=A→B，B2=B→C，以此类推。**本例B编号从1起，代码笔下标从0起**，不沿用0039真实行情的B0编号。

<!-- memo0040-figure:03a_main_evidence -->
![3.a 同一主例的端点、候选证据和冻结证据](../../artifacts/experiments/chan_theory/memo0040_figures/03a_main_evidence.png)

[example] **主例 · 完整16笔入口调用轨迹；各位置作用不同。** 图3.a：端点F、候选证据B8和促成冻结的N2证据B14位于不同位置。主例trace保留的dep=7并不是冻结发生时所读到的全部右侧数据。

```text
点    A    B    C    D    E    F    G    H    I    J    K    L    M    N    O    P    Q
价  100  130  110  120  115  140  125  135  120  130  123  133  125  132  124  131  122
笔      B1   B2   B3   B4   B5   B6   B7   B8   B9  B10  B11  B12  B13  B14  B15  B16
```

**上升候选固定A=100，D=120低于B=130不会立即放弃A。** 实际第一序列处理如下：

| 喂入 | 特征处理后状态 | 下一步 |
| --- | --- | --- |
| B2 `[110,130]` | e0=B2 | 等下一根下降笔 |
| B4 `[115,120]` | 合并e0=`[115,130]`，来源B2/B4 | 等下一根下降笔 |
| B6 `[125,140]` | e1=B6 | 等第三元素 |
| B8 `[120,135]` | e2=B8；实际突破和顶公式通过；e0/e1无缺口 | 候选B1..B5，A100→F140，dep=B8 |

这里首三笔价格交集是`[110,120]`；KWX没有因此直接宣布B3为线段终点。候选还需后续结构与状态机处理。

**同一次16笔完整输入中的调用顺序：** 下表是函数执行事件，不是逐笔流式更新；`dep=B8`只指代码下标7，不代表当时已冻结。

| 顺序 / 对应树 | 内部事件 | 事件后的状态 |
| --- | --- | --- |
| 1 / 2.b | 找到A→F候选，并从F找到F→I反向候选 | 选中A；重算A→F放入N0，N1仍空 |
| 2 / 2.d | 再找F→I（B6..B8，证据B11）；N0没有新高延长 | N0=A→F；N1=F→I；frozen空 |
| 3 / 2.e | 从I找到I→L候选（B9..B11，证据B14）；N1没有合格延长 | 返回`confirm(N2=I→L)` |
| 4 / 2.f | 原N0通过冻结检查 | frozen=[A→F]；N0=F→I；N1=I→L |
| 5 / 2.e | 从L找下降候选失败；后续没有严格跌破N1起点120，无其他分支命中 | `none`，停止主循环 |
| 6 / 2.h | 复制状态，N1显示rule改forming | A→F frozen；F→I soft_n0；I→L pending_n1 |

最终A→F的trace仍保留原候选`dep=B8`，没有改成促成这次冻结的B14。**候选证据、冻结事件证据、输出trace字段要分开看。** B12..B16在输入中存在，最后一条输出却止于B11，尾部未被线段输出覆盖。[4]

**同一主例仅给前三笔时：** 2.b依次试代码起点0、1、2，全部耗尽失败；内部N0/N1皆空。2.h从第一笔方向选极值，输出A100→B130的`forming/pending_n1`，不是“已经有A→B的N1候选，搜索停在A”。追加后续数据后再次调用，会重新搜索并得到上面的候选链。

### 3.b 独立入口例：首起点失败，怎样右移？

在主例前加两个价格，得到**另一组18笔输入**：`110→150→100→130→110→120→115→140→…→122`。本节全用代码零基笔下标，避免与主例B编号混淆。

<!-- memo0040-figure:03b_failed_start_prefix -->
![3.b 起点0失败后，先试1，再试2](../../artifacts/experiments/chan_theory/memo0040_figures/03b_failed_start_prefix.png)

[example] **独立18笔输入 · 在主例前添加110→150；横轴为零基顶点下标。** 图3.b：独立18笔例确实从入口依次试起点0、1、2，最终选中2；前两笔未归属，输入本身未删除。

```text
2.b尝试begin=0，暂定上升，固定起点价110
├── 2.c找到局部分型端点6、12，但区间内已有100<110
│   └── 两次端点检查均为start；保持begin=0重扫，最终耗尽None
└── 2.b改试begin=1，暂定下降，起点价150
    ├── 2.c找到端点9，其终价120不是区间最低100
    │   └── end失败，保持begin=1重扫，最终耗尽None
    └── 2.b改试begin=2，暂定上升，起点价100
        └── c=2..6（100→140）；紧接rev=7..9（140→120）
            └── 选中begin=2 → 重算c放N0 → 主循环
```

最终输出从下标2开始，前两笔`0/1`未归属；并非所有输入都被线段覆盖，也不是起点0一失败就删除第一笔。之后输出三段仍相邻。[4]

### 3.c Commands And Checks

验证程序在内存中观察当前CC原函数的调用和状态，再执行断言；没有改CC文件，也没有把算法重新写一遍。

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  experiments/chan_theory/check_memo0040_kwx_tree.py
```

**结果：passed；9组真实入口、8组局部helper、4组人工状态检查。** “组”包含多个输入或断言，不是21条穷尽测试。下面是文档与证据的对应关系；JSON保留主合成例的输入与完整调用轨迹，普通fixture的结果、计数和代表事件，以及fixture路径和hash。[4]

| 检查层次 / JSON位置 | 对应树 | 实际确认内容 |
| --- | --- | --- |
| 入口`empty / two_bis / three_bis_lower_D` | 2.a/b/h | 空、两笔返回[]；三笔全起点耗尽后才生成forming |
| 入口`main_up / main_down_mirror` | 2.b～2.h | 主例及价格取负镜像，候选链、换位冻结、最终输出和尾部留空 |
| 入口`failed_start_advances_to_next_bi` | 2.b/c | 上节失败起点的实际检查、重扫、后移及留空前缀 |
| 入口`fixture_runs`，另附局部门对照 | 2.d/e/f/g | 真实笔fixture及镜像中观察到confirm、extend_n1、none、rollover；jm例真实输出含吸收段226..248、越点235。额外构造该区间候选，直接调用门检查：一般rule拒绝、absorb rule通过；后两次调用属于局部证据 |
| 入口`gap_atomic_cutoffs` | 2.e/f/g.3 | 同一fixture取104、105、106笔：84..92先pending；随后原子冻结，dep=104，93..101成为seed；再延至105。下标均零基 |
| 入口`strong_overlay_builder_mismatch` | 2.g.2/i | 455笔fixture、standard_strong：主入口有strong段；显示Builder不开strong，实际工作分段不同 |
| helper`primary_lookahead_up/down` | 2.c.3 | 独立连续例`0,8,2,10,4,11,1,10,3,8,2`及镜像：10笔得到端点下标4、dep9；只有前8笔不能得到该候选 |
| helper包含／合并／分型／重排／尾极值组 | 2.c/g.4/h | 相等边界、按段方向合并、保留来源、原笔重放、缺少第四项分型条件、点接触不等于端点有效、同价尾极值取早 |
| 人工`gap_touch_vs_strict_separation` | 1.a/2.c.4 | 给定e0/e1两个元素，缺口严格分离与点接触不同；不声称此人工窗口由入口到达 |
| 人工`no_internal_n1_but_pending_output` | 2.h | 内部无N1，输出仍可有pending_n1尾线 |
| 人工`n2_failure_break_up/down` | 2.e/f | 直接给定N0/N1，验证break及撤销N1、延长N0；**未证明该状态由这组输入的入口到达** |

默认真实入口fixture的裁决观察次数为`confirm=241、extend_n1=26、none=5、rollover=2、gap_revert=2`；这是选定运行的事件计数，不是独立分支数量。`break`在这些入口样本中没有出现，只在人工状态测试中验证。

**分层例图核对（7.4.122）：** 新增28张PNG、63个面板，覆盖1.a—1.c、2.a—2.i及2.c/2.g的具体子步骤，以及3.a/3.b。保留上述既有证据，不把局部例提升为入口证据。图中数值由当前CC入口或helper断言核对；生成器还验证源文件SHA256、笔/端点索引及图层覆盖。

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python \
  experiments/chan_theory/render_memo0040_figures.py
```

[生成器](../../experiments/chan_theory/render_memo0040_figures.py)使用[主例/入口规格](../../experiments/chan_theory/memo0040_core_figure_specs.py)、[特征规格](../../experiments/chan_theory/memo0040_feature_figure_specs.py)、[状态规格](../../experiments/chan_theory/memo0040_state_figure_specs.py)，输出[图清单与数值](../../artifacts/experiments/chan_theory/memo0040_figures/manifest.json)。例图覆盖每个解释层，不表示穷举每条分支、配置或全部输入。

### 3.d Limits And Next Questions

- **已经完成：** 核心执行路径的源码审读、正文分支顺序复核、上述有限入口与局部证据核对。按2.a声明的范围记录正常控制流、等号、失败、耗尽和输出出口。
- **尚未证明：** 全部输入等价、所有状态可达、所有配置组合、异常Bi契约、运行性能、实时增量安全或原文符合性。源码的断言只作为内部不变量检查；本篇未穷举错误输入引起的异常。
- **未做：** 从文档独立实现另一算法并与CC全路径比对。因此不将本篇标为已通过独立规格到实现的完整验证。
- **下一步讨论：** 依据本篇的具体分支对照原文，特别是首段后移、非全严格分型、前看、吸收和strong单笔；再决定0032应修哪条规则。显示入口遗漏strong开关可另立修复项。本次两套算法保持原样。

## Appendix A. Reference Map

1. **核心基线（2026-09-17读取）：** CC commit `374268381a3eaeee4d220e67d63364b3907405f4`；读取时工作区干净。`xianduan.py` SHA256为`57bb272443c2fff35e859d53389f709c154666eef00354e6b272583b6ec55766`。当前核心文件与项目固定副本仅导入命名空间不同；不是将PDF记录的旧commit当成本次基线。
2. **配置与模型：** 当前CC的`config.py / models.py / trace.py`；与项目固定副本的差异为配置注释、无关中枢/走势类型注解、未使用import及空行，Bi/Xianduan模型和本篇相关执行条件未变。
3. **源码定位：** 以下链接以项目固定副本为可复查位置；行号与当前CC核心对应。
4. **可复现证据：** [检查程序](../../experiments/chan_theory/check_memo0040_kwx_tree.py)、[完整JSON报告](../../artifacts/experiments/chan_theory/memo0040_kwx_tree_checks.json)。程序用当前CC整套依赖执行；报告另与`records/cc/xianduan-study-20260912/reference/manual_rebuild`保存版本比较字段及配置，不混搭运行时。另已核对`experiments/chan_theory/_kwx_xianduan`核心仅有导入路径差异。

| 本篇 | 核心源码位置 |
| --- | --- |
| 对象/状态转换、入口 | [`xianduan.py:84`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L84)，入口247 |
| 2.c.1～2.c.6 | [`xianduan.py:281`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L281) |
| 2.a、2.d、2.f主驱动 | [`xianduan.py:526`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L526) |
| 2.c候选、2.g.1新极值 | [`xianduan.py:663`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L663) |
| 2.g.2 strong、2.g.3第二序列 | [`xianduan.py:733`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L733) |
| 2.e裁决、2.g.4冻结 | [`xianduan.py:820`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L820) |
| 2.b首段、基础/极值 | [`xianduan.py:946`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L946) |
| 2.h输出与转换 | [`xianduan.py:997`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L997) |
| 2.i显示辅助 | [`xianduan.py:1167`](../../experiments/chan_theory/_kwx_xianduan/algo/xianduan.py#L1167) |

相关项目文档：[0036类接口](memo0036_class_xianduan_series.md)、[0032项目规则及校准限制](memo0032_algo_of_xianduan_2nd.md)、[0039校准讨论](memo0039_xianduan_calibration.md)。本篇遵循[0034 memo指导](memo0034_memoguidance.md)；本次没有改写这些历史memo。
