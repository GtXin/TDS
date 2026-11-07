# memo0033_algo_of_bi

## 0. 范围与方法

### 0.a 范围

**本篇研究怎样从顶底分型中画出笔：先找第一笔，再判断原笔延伸，还是反向成笔。** 输入从已处理包含的K线和已识别的分型开始；不展开线段、中枢。

沿用0032的结构：原文依据 → 样图 → 逐层展开的树 → 分支与价格图。0033重新整理[memo0026](memo0026_algo_of_bi.md)，旧稿保留。缠论定义与参考实现的扩展分开标明；本篇未通过独立的完整算法可执行验证。

### 0.b 方法

1. 先看顶、底及中间走势，再写判断条件。
2. 每一步只回答一个问题，编号与树对应。
3. 原笔、候选连接用不同线型；点名与价格保持一致。
4. 用KWX/CC代码核对处理顺序，差异放在相关条件旁；程序细节放第3章。

### 0.c 流程总览

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
│   ├── S3.a 同型且更极端 → 延长原笔，重复S3
│   ├── S3.b 同型但不更极端 → 保留原笔，重复S3
│   └── S3.c 反型 → 固定末端，检查反向候选S4
│       ├── S4.a 反向成笔 → 接出下一笔，回S3
│       └── S4.b 反向暂不成笔 → 保留原画法，进入S5
│           ├── S5.a 强势条件通过［参考扩展］→ 接出反向笔，回S3
│           └── S5.b 未启用或未通过 → S6
│               ├── S6.a 价格、后续证据及严格延长均成立
│               │   → 吸收末笔，延长前笔，回S3［参考扩展］
│               └── S6.b 不修正 → 保留原笔，回S3
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**总结**

笔把顶底之间的一段运动概括为一次上涨或下跌。先处理K线包含、识别分型，再找第一对满足间隔和价格条件的顶底。尚不成笔，就保留分型，继续寻找；已有笔后，先看新分型与末端是否同型。同为顶而更高，或同为底而更低，原笔延伸；否则保留。出现反向分型，再检查这次回落或反弹能否独立成笔，能则接出下一笔。不能时，参考实现还可检查强势例外及反弹修正：前者比较相邻笔振幅，后者结合新极值和后续证据，决定是否吸收末笔、延长前笔。这两项是实现扩展，不能直接当作缠论定义。分型仍存在，不必都画成端点；已经画出的笔也不等于永久定型。判断若用到后续分型，就必须等这些分型出现后才有依据。

## 1. 缠中说禅关于笔的依据

### 1.a 第62课：一顶一底之间的一次运动

> 两个相邻的顶和底之间构成一笔

**笔表达的是顶到底的一次下跌，或底到顶的一次上涨。** 内部的小波动是否需要单独画出来，要看能否形成独立的笔；不能见到一个局部转折就接一笔。原文还要求先处理K线包含，并检查两端分型之间的间隔。[^lesson62]

### 1.b 第65课：分型不一定都保留为端点

> 从分型到笔，必须是一顶一底。

同型转折之间若没有需要独立表达的反向结构，就要重新判断这些转折的取舍。最后画出的笔应首尾相连、上下交替。**分型是局部转折，笔的端点是从这些转折中选出的点。**[^lesson65]

### 1.c 原文与本篇口径

- **理论主线：** 一顶一底、包含处理、成笔间隔，以及同型转折的取舍。
- **参考口径：** 第2章用KWX/CC默认标准检查具体价格；相等怎么处理、先选哪一对，也按保存代码说明。
- **实现扩展：** S5的强势例外和S6的反弹修正单独标出，不把它们写成原文定理。[^source-code]

## 2. 从分型到笔

### 2.0. 样图与符号

![A至E：先看价格与分型，再讨论哪些连接成笔](../../artifacts/experiments/chan_theory/memo0033_2_0.png)

- **M：** 已处理包含的K线；图中竖线表示高低价区间，M下标从0开始。
- **A、B、C、D、E：** 按时间出现的分型；顶取中心K线高点，底取中心K线低点。
- **实线：** 当前已画出的笔；**虚线：** 正在判断的连接，不预先认定成笔。

主例为`A顶20→B底8→C顶17→D底6→E顶19`。中心位置分别是`M1、M5、M9、M11、M15`；每根M对应一根原始K，且没有价格缺口。完整数值见3.a。

### 2.1. step 1 - 初始条件

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
```

**先完成K线包含处理和分型识别，再从最早出现的分型寻找第一笔，进入S2。** 顶、底分型各由相邻三根M构成；中心分别同时具有较高的高低点、较低的高低点。

本篇先走默认标准成笔口径；可选强势与修正分别放S5、S6。“回S3”与“重复S3”都先读下一分型；输入按时间前进：输入已用完，就结束本轮并保留当前画法；没有笔则结果为空。

### 2.2. step 2 - 寻找第一笔

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**找一顶一底，判断中间这段运动能否单独画成一笔。** 首次寻找时，固定新出现的分型，按时间从早到晚尝试之前的分型；先遇到哪一对合格，就选哪一对。

**本篇的标准成笔条件，按下列顺序检查：**

1. **方向相反：** 底→顶向上，顶→底向下；两个顶或两个底不能相连成笔。
2. **间隔足够：** 两分型的三根K线之间至少留一根独立M，即中心相隔至少4；有价格缺口时的参考折算见3.b。
3. **两端价格合格：** 比较起点的“中心＋右邻”和终点的“左邻＋中心”。向下时，起点高价要高于终点这两根的高价，终点低价要低于起点这两根的低价；向上反过来，相等不通过。
4. **终点没有被内部越过：** 向下时，中间没有更低的M；向上时，没有更高的M。内部同价可以通过。这里只检查终点方向的极值。[^standard]

#### 2.2.a. 分支S2.a 顶底成笔

![S2.a：向下和向上的第一笔](../../artifacts/experiments/chan_theory/memo0033_2_2a.png)

- **条件：** 一顶一底通过上述检查。
- **向下例：** `A顶20@M1→B底8@M5`；中心差4，`20>14`、`8<14`，内部低价`14、12、10`均不低于8。
- **向上例：** 将本例价格关于15镜像，得到`A底10→B顶22`；间隔和判断顺序相同。
- **处理：** 画出第一笔；这轮未选中的起点不再参与首笔选择。读取下一分型，进入S3。

#### 2.2.b. 分支S2.b 暂不成笔

![S2.b：独立输入中，两个分型太近，暂不画笔](../../artifacts/experiments/chan_theory/memo0033_2_2b.png)

- **条件：** 当前配对同型，或任一成笔条件不满足。
- **独立例：** 只取主例M8–M12为一份新输入，重新编号；`C顶17@M1→D底6@M3`相隔2，没有缺口，暂不成笔。
- **处理：** 当前分型不动，试下一旧分型；旧分型全部试完仍不成，才留下当前分型，读下一分型重复S2。失败的分型仍可参与后续配对。

首笔不走S5、S6。开头尚未成笔的部分保留原始数据，不强行补一笔。

### 2.3. step 3 - 原笔延伸，还是出现反向候选

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
│   ├── S3.a 同型且更极端 → 延长原笔，重复S3
│   ├── S3.b 同型但不更极端 → 保留原笔，重复S3
│   └── S3.c 反型 → 固定末端，检查反向候选S4
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**已有笔后，比较新分型与末笔终点。** 中间出现过但未成笔的分型，不自动取代这个终点。

#### 2.3.a. 分支S3.a 同型且更极端，原笔延伸

![S3.a：两顶取更高，两底取更低，原笔起点不动](../../artifacts/experiments/chan_theory/memo0033_2_3a.png)

- **条件：** 同为顶且新顶更高，或同为底且新底更低。
- **独立例：** 已有`底8→顶17`，后来出现顶19，则改为`底8→顶19`；向下镜像同理。
- **处理：** 保留末笔起点，替换末笔终点；不重查成笔间隔。读下一分型，重复S3。

#### 2.3.b. 分支S3.b 同型但不更极端，保留原笔

![S3.b：同价或没有创新高低，不移动旧终点](../../artifacts/experiments/chan_theory/memo0033_2_3b.png)

- **条件：** 新顶不高于旧顶，或新底不低于旧底。
- **独立例：** 已有`底8→顶17`，新顶17或16，仍保留旧顶17。
- **处理：** 原笔不变；读下一分型，重复S3。相等也不换点。

#### 2.3.c. 分支S3.c 反型，检查能否独立成笔

- **条件：** 末笔止于顶，新分型是底；或末笔止于底，新分型是顶。
- **主例：** 已有A→B，出现C顶，检查B→C；已有B→C，出现D底，则检查C→D。
- **处理：** 固定末笔终点为反向候选的起点，进入S4；具体价格图见下两支。

### 2.4. step 4 - 反向运动能否成笔

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
│   ├── S3.a 同型且更极端 → 延长原笔，重复S3
│   ├── S3.b 同型但不更极端 → 保留原笔，重复S3
│   └── S3.c 反型 → 固定末端，检查反向候选S4
│       ├── S4.a 反向成笔 → 接出下一笔，回S3
│       └── S4.b 反向暂不成笔 → 保留原画法，进入S5
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**这次回落或反弹能否单独画成下一笔？** 仍用2.2的成笔条件，依次检查间隔、两端价格、内部极值。

#### 2.4.a. 分支S4.a 反向成笔

![S4.a：主例B至C成笔，接在已有A至B之后](../../artifacts/experiments/chan_theory/memo0033_2_4a.png)

- **条件：** 反向候选满足标准成笔条件。
- **主例：** `B底8@M5→C顶17@M9`，中心差4；`8<min(12,13)`、`17>max(12,13)`，内部高价`13、14、16`均不高于17。
- **处理：** 接出B→C，原A→B保留；读下一分型，回S3。

#### 2.4.b. 分支S4.b 反向暂不成笔

![S4.b：C至D跌得更低，但间隔不足，不能据此接笔](../../artifacts/experiments/chan_theory/memo0033_2_4b.png)

- **条件：** 反向候选未通过标准成笔条件。
- **主例：** `C顶17@M9→D底6@M11`只有2个中心间隔，且无缺口；即使D低于B8，也不能直接接C→D。
- **处理：** 暂保留A→B→C，进入S5检查参考实现的可选例外；本步不延长旧笔，也不直接移动起点。

### 2.5. step 5 - 强势运动的成笔例外［参考扩展］

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
│   ├── S3.a 同型且更极端 → 延长原笔，重复S3
│   ├── S3.b 同型但不更极端 → 保留原笔，重复S3
│   └── S3.c 反型 → 固定末端，检查反向候选S4
│       ├── S4.a 反向成笔 → 接出下一笔，回S3
│       └── S4.b 反向暂不成笔 → 保留原画法，进入S5
│           ├── S5.a 强势条件通过［参考扩展］→ 接出反向笔，回S3
│           └── S5.b 未启用或未通过 → S6
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**反向尚未标准成笔时，参考实现可用足够大的振幅接出一笔。** 振幅是两端价格差的绝对值；此项默认关闭，默认主例直接走S5.b。

#### 2.5.a. 分支S5.a 强势条件通过

![S5.a：独立开启强势后，比较候选与前笔的振幅](../../artifacts/experiments/chan_theory/memo0033_2_5.png)

- **先比前笔：** 前笔振幅大于0，候选振幅至少达到前笔的95%，就接出候选笔。
- **前笔未通过：** 固定候选终点，往后找第一条标准成立的反向笔；其振幅大于0，且候选振幅至少达到它的95%，也可接出候选笔。只借后笔作判断，不在此处连画两笔。
- **独立例：** 主例改用强势规则，C17→D6振幅11，前笔B8→C17振幅9；`11≥0.95×9`，接出C→D。
- **处理：** 原有笔保留，追加反向笔；读下一分型回S3，不再检查S6。比例相等也通过。

#### 2.5.b. 分支S5.b 未启用或未通过

- **条件：** 强势关闭；或前笔未通过，后面又没有标准笔、首条后笔振幅为0或比例不够。
- **处理：** 原画法不变，进入S6。

找后笔时，同型跳过，标准不成再试后续分型；第一条标准笔出现就停止，比例失败也不换更有利的一条。后笔本身不能靠强势规则成立。

### 2.6. step 6 - 是否吸收末笔、延长前笔［参考扩展］

```text
S1 初始条件：K线已处理包含，顶底分型按时间排列
├── S2.a 顶底成笔 → 画出第一笔，进入S3
│   ├── S3.a 同型且更极端 → 延长原笔，重复S3
│   ├── S3.b 同型但不更极端 → 保留原笔，重复S3
│   └── S3.c 反型 → 固定末端，检查反向候选S4
│       ├── S4.a 反向成笔 → 接出下一笔，回S3
│       └── S4.b 反向暂不成笔 → 保留原画法，进入S5
│           ├── S5.a 强势条件通过［参考扩展］→ 接出反向笔，回S3
│           └── S5.b 未启用或未通过 → S6
│               ├── S6.a 价格、后续证据及严格延长均成立
│               │   → 吸收末笔，延长前笔，回S3［参考扩展］
│               └── S6.b 不修正 → 保留原笔，回S3
└── S2.b 暂不成笔 → 固定当前分型，试下一旧分型；
    全部试完仍不成，才读下一分型，重复S2
```

**新反向运动不成笔后，原来的反弹或回落是否仍应单独保留？** 参考实现允许在条件齐备时撤去末笔、延长前笔；该修正默认开启。以下固定已有两笔A→B→C，新分型为D。

![S6：只有D时保留旧画法，后续E提供许可后才修正](../../artifacts/experiments/chan_theory/memo0033_2_6.png)

#### 2.6.a. 分支S6.a 条件齐备，修正前笔

先看价格，再按时间看D后的分型G，**首个决定性证据决定是否修正**。

| 检查 | 向下修正A→D | 向上修正A→D |
|---|---|---|
| 价格前提 | D≤B，C≤A | D≥B，C≥A |
| 内部极值 | A至D内部没有比D更低的M | A至D内部没有比D更高的M |
| 允许修正 | 先出现高于C的顶G | 先出现低于C的底G |
| 阻止修正 | 先出现能与C标准成笔的底G | 先出现能与C标准成笔的顶G |
| 最终能延长 | D<B | D>B |

- **主例：** `A20→B8→C17`，D6低于B8，C17不高于A20，内部没有低于6的M；后续先见E顶19高于C17，允许修正。
- **处理：** 吸收B→C，把A→B延长为A→D；B、C的原始分型保留。读下一分型回S3，之后E按S4接出D→E。

只根据D还不能修正。这里是后来E出现后，对旧画法的修改；不是在D时就已经知道E。

#### 2.6.b. 分支S6.b 不修正，保留原笔

- **条件：** 修正关闭、已有笔不足两条、价格或内部极值不合格，或后查先遇到阻止证据。
- **尚无决定性证据：** 继续按时间看下一个G；整份输入用完仍无许可，本轮也保留原笔。
- **D与B同价：** 即使取得许可，也不能严格延长；保留A→B→C。
- **处理：** 不接出失败的候选笔；读下一分型，回S3。若已无下一分型，本轮结束。

**讨论：** 后查时固定的是C，检查C→G能否成笔；S5找后笔时固定的是D。二者不能混用。修正成功后不重新做A→D的整套标准检查；它属于参考代码的独立修正规则。

## 3. 补充讨论与实现对照

### 3.a 完整数值与标准比较

```text
M序号   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
高价   19 20 18 16 14 12 13 14 16 17 14 10 11 13 16 19 18
低价   15 16 14 12 10  8  9 10 12 13 10  6  7  9 12 15 14
分型      A           B           C     D           E
```

起终点中心下标为s、e；M的高低价为H、L。默认端点检查称为`half`：

- 向上：`L_s<min(L_{e−1},L_e)`，且`H_e>max(H_s,H_{s+1})`。
- 向下：`H_s>max(H_{e−1},H_e)`，且`L_e<min(L_s,L_{s+1})`。
- 内部只查`s<k<e`：向上各`H_k≤H_e`，向下各`L_k≥L_e`。

先查距离，后查端点，最后查内部极值；任一失败即结束本对判断。S2失败换旧起点，S4失败去S5；S5找后笔、S6查阻止证据时失败，则继续各自的后查。

### 3.b 缺口与其他口径

**这里的缺口是相邻K线价格区间的分离，不是时间中断，也不是0032的特征序列缺口。** 参考实现比较每根M全部原始K成员覆盖的区间：`[10,12]`与`[14,18]`算缺口，`[10,14]`与`[14,18]`只接触，不算。

默认中心间隔不足4时，可把起终点之间的缺口数g加进间隔：`e−s+g≥4`才通过。例如中心差3、缺口1，折算后为4。统计范围仅从M_s到M_e，不包括区间外缺口。这是参考折算规则，不据此改写第62课原文。

| 参考配置 | 与正文的差别 |
|---|---|
| `bi_5k` | 正文默认：中心差4、可折算缺口、half、内部极值及修正开启 |
| `bi_4k` | 两分型三M窗口不能共用M；中心M内原始极值K下标差至少4，同价取最早K；不折算缺口，不查half与内部极值，不修正 |
| `bi_strong` | 在默认基础上启用S5，比例0.95 |
| `bi_secondary` | 当前代码未实现，直接给出空笔列表，不走上述树 |
| `CUSTOM` | 按自定义字段；命名预设会覆盖对应字段，如默认间隔4 |

端点选项还包括`none`（跳过）、`loss`（只比中心）、`strict`（比较范围扩为完整三M窗口）、`totally`（向上时起点中心高价低于终点三M最低价；向下时起点中心低价高于终点三M最高价）；这些价格比较均严格。内部极值可另行关闭，但S6自身的内部极值检查仍执行。[^config]

### 3.c 画出一笔，不等于永不改画

**[mental model] 先决定哪些转折值得单独连成笔，再维护最后的连接；原始走势始终保留。** “值得”指是否满足明确规则，不是主观选漂亮的线。

参考程序每次接收整份输入并重算。S5、S6可以查看这份输入中较后的分型；判断依据出现的时间，可以晚于笔的终点。真实时点复盘应截断原始K线，再重新处理包含和分型，不能只裁切最终成图。

程序另有`confirmed`标记：末笔、依赖缺失或触及最后两根M的笔，以及末笔依赖缺失或位于最后两根M时的倒数第二笔，标为未确认；其他标为确认。这里的“依赖”是该笔用过的最晚分型中心位置，延长时取旧依赖与新终点位置中较晚者，修正还计入许可位置。**这个标记不冻结端点。** 主例只输入到D时A→B可标确认，加入E后仍会被改成A→D。

### 3.d 与代码对应及验证范围

| 正文问题 | 参考代码 |
|---|---|
| S2 首次成笔 | `_try_first_bi` |
| S3 原笔延伸 | `_extend_same_fx` |
| S2／S4 成笔条件 | `_try_standard_form` |
| S5 强势例外 | `_try_strong`、`_lookahead_next_std_bi` |
| S6 反弹修正 | `_repair_sub_peak`、`_confirm_reverse_break` |

输入、配置整理、逐个读取及结果封装不另立价格判断步骤；输入索引与时间关系由调用方保证。空输入或始终未成笔时返回空列表；已经选出的相邻笔共享端点，前后尚未覆盖部分仍保留原数据。

本次已有34项参考检查通过，包含主例、截断输入、镜像及局部边界。它们核对参考程序与例子，**不是从本篇独立实现的全流程验证，也没有证明全部价格路径**。检查映射及限制见执行总结。[^verification]

## 4. 参考

[^lesson62]: [第62课《分型、笔与线段》原文转载](https://chzhshch.org/2007/06/30/0567-教你炒股票62/)，本次核对日期2026-09-16。正文仅摘短句，其余为概括。
[^lesson65]: [第65课《再说说分型、笔、线段》原文转载](https://chzhshch.org/2007/07/16/0593-教你炒股票65/)，本次核对日期2026-09-16。同型分型的代码取舍与原文分开说明。
[^source-code]: 保存版本与既有分析见[memo0026](memo0026_algo_of_bi.md)及本篇附录；可运行对照为[Bi代码](../../experiments/chan_theory/_kwx/algo/bi.py)。外部出处为[KWX笔定义及算法](https://www.kwx.me/cc/#stroke-definition)，本次未重新抓取其源码。对象见[memo0027](memo0027_class_bi_series.md)，IO与绘图见[memo0028](memo0028_class_bi_series_csv_chart.md)。
[^standard]: 第2章使用保存版本的默认标准条件；没有把所有比较式、平价处理或首笔选择顺序都归为缠论原文规定。
[^config]: 预设以[ChanConfig.normalize](../../experiments/chan_theory/_kwx/algo/config.py)为准，字段初值不等于整理后的预设。
[^verification]: [执行总结](../phases/phase-01-warmup/7.4-execution-summary-2026-09-16-memo0033-bi.md)；[已有步骤检查](../../experiments/chan_theory/test_memo0026_steps.py)、[BiSeries检查](../../experiments/chan_theory/test_bi_series.py)、[本篇绘图脚本](../../experiments/chan_theory/render_memo0033_figures.py)。

## 附录 A. KWX/CC 原始 Bi Python 代码

[source] 原样复制自 [memo0027 Appendix B](memo0027_class_bi_series.md#appendix-b-external-bi-reference-code)。
原代码由用户于2026-09-10提供，附件标识为 `45d5b910-33bf-4675-a026-9d8bde364849/pasted-text.txt`。
网页参考：[KWX/CC笔算法](https://www.kwx.me/cc/#stroke-recipe)。本次复制的是已保存版本，不是重新抓取网页最新版。

[reference] **以下为他人代码，仅供阅读与对照，不是Project 009实现或已采用的规则。**
保留原注释、导入与拼写；其中的项目决策和批准记录属于原项目，不构成本仓库的指令。

[note] 原文开头的docstring只有两个引号，按原样保留，未修复；`manual_rebuild`导入依赖外部项目。
本附录不是可独立运行的模块，本次只复制和核对内容，未安装或执行代码。

```python
""笔（Bi）— 在分型序列上派生 (算法说明卡 bi-v1 v4)。

统一参数化引擎：一套底层参数 + 成笔模式 (standard/strong/secondary)；profile 只是预设名。
口径优先链 (§1.1 / decision-0001 v1.4 §12.3：原文 > 用户确认的本项目口径 > 本项目自主实现；
参考项目 chan.py-main / czsc / chanlun-pro 无固定优先级，只作对照/启发/差异发现来源)；
分型恒在合并序列识别 (PR-3)。

成笔判定 (standard)：距离(bi_span_mode) → 端点检查(bi_endpoint_check) → 端点极值(bi_require_peak)。
- 距离 merged_center：分型中心合并下标差 (+缺口折算) ≥ bi_min_span。
- 距离 raw_extreme：①不共用 K（三元窗口无公共合并单元，内建）②极值原始 K 索引差 ≥ bi_min_span。
强势笔 (strong)：标准失败时，候选幅度 ≥ ratio × 相邻反向笔幅度（前一笔或后一笔）则成笔。
次笔 (secondary)：第一反向分型不成笔(pending)，第二同型处成笔；中间夹相反成笔则回退标准。

**纯函数**：合并/分型由引擎批量重派生 (版本缓存)，本模块无跨调用状态。strong_next「后一笔」
在单次派生内 = 向分型数组后方有界 look-ahead；回补由「dep 依赖水位线 + provisional」承载
(每笔记成笔实际查阅的最大分型下标 dep_to_index，serializer 据此判 confirmed，保证 strong_next
不在 confirmed 区插删笔)。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from manual_rebuild.algo.config import (
    BiEndpointCheck,
    BiFormationMode,
    BiSpanMode,
    ChanConfig,
)
from manual_rebuild.algo.models import Bi, BiDir, Fenxing, FxType, MergedKline
from manual_rebuild.algo.trace import (
    RULE_BI_DOWN_4K,
    RULE_BI_DOWN_5K,
    RULE_BI_DOWN_SECONDARY,
    RULE_BI_DOWN_STRONG_NEXT,
    RULE_BI_DOWN_STRONG_PREV,
    RULE_BI_UP_4K,
    RULE_BI_UP_5K,
    RULE_BI_UP_SECONDARY,
    RULE_BI_UP_STRONG_NEXT,
    RULE_BI_UP_STRONG_PREV,
    StructTrace,
)
from manual_rebuild.data import Kline

_ALGO_CARD_ID = "bi-v1"

# rule_kind → (up rule_id, down rule_id)。standard 再按 span_mode 细分 5k/4k (见 _rule_for)。
_RULE_STRONG_PREV = (RULE_BI_UP_STRONG_PREV, RULE_BI_DOWN_STRONG_PREV)
_RULE_STRONG_NEXT = (RULE_BI_UP_STRONG_NEXT, RULE_BI_DOWN_STRONG_NEXT)
_RULE_SECONDARY = (RULE_BI_UP_SECONDARY, RULE_BI_DOWN_SECONDARY)
_RULE_STD_MERGED = (RULE_BI_UP_5K, RULE_BI_DOWN_5K)
_RULE_STD_RAW = (RULE_BI_UP_4K, RULE_BI_DOWN_4K)


def bi_dep_index(bi: Bi) -> int | None:
    """笔依赖水位（与既有 overlay confirmed 判定同一事实来源）。"""
    if bi.trace is None:
        return None
    return bi.trace.dep_to_index if bi.trace.dep_to_index is not None else bi.trace.merged_to_index


def bi_confirmed_flags(bis: Sequence[Bi], n_merged: int) -> list[bool]:
    """返回每笔是否 confirmed；逐字保持 bi-v1 §10 的既有三条末端规则。"""
    n_bis = len(bis)
    last_dep = bi_dep_index(bis[-1]) if n_bis else None
    last_unstable = last_dep is None or last_dep >= n_merged - 2
    flags: list[bool] = []
    for i, bi in enumerate(bis):
        dep = bi_dep_index(bi)
        provisional = (
            i == n_bis - 1
            or dep is None
            or dep >= n_merged - 2
            or (i == n_bis - 2 and last_unstable)
        )
        flags.append(not provisional)
    return flags


@dataclass(slots=True)
class _WorkBi:
    """构建期可变笔。rule_kind ∈ standard/strong_prev/strong_next/secondary；dep = 依赖水位。"""

    start_fx: Fenxing
    end_fx: Fenxing
    direction: BiDir
    rule_kind: str
    dep_index: int


def build_bis(
    merged: list[MergedKline],
    fenxings: list[Fenxing],
    raw_klines: list[Kline],
    cfg: ChanConfig,
    *,
    profile_id: str,
    config_hash: str,
) -> list[Bi]:
    """从分型序列派生笔序列（纯函数，按 cfg 统一参数 + 成笔模式判定）。"""
    cfg = cfg.normalize()
    builder = _BiBuilder(merged, fenxings, raw_klines, cfg)
    builder.run()
    return builder.finish(profile_id, config_hash)


class _BiBuilder:
    """单次派生的内部状态机（不跨调用持久）。"""

    def __init__(
        self,
        merged: list[MergedKline],
        fenxings: list[Fenxing],
        raw_klines: list[Kline],
        cfg: ChanConfig,
    ) -> None:
        self._merged = merged
        self._fxs = fenxings
        self._raw = raw_klines
        self._cfg = cfg
        self._bis: list[_WorkBi] = []
        self._candidates: list[Fenxing] = []  # standard/strong 首笔候选

    def run(self) -> None:
        if self._cfg.bi_formation_mode is BiFormationMode.SECONDARY:
            # 次笔 = 高一级别一笔 = 老笔的线段(特征序列法)。**暂搁置不输出**(用户 2026-06-17)：
            # 旧"破坏式合并"在长趋势上过度合并 → 已回退；待特征序列法线段草案确认后实现 (§5.8)。
            self._bis = []
        else:
            for i, fx in enumerate(self._fxs):
                self._feed_std_strong(i, fx)

    # ── standard / strong 主循环 ─────────────────────────────────────────
    def _feed_std_strong(self, i: int, fx: Fenxing) -> None:
        if not self._bis:
            self._try_first_bi(fx)
            return
        last = self._bis[-1]
        if fx.fx_type is last.end_fx.fx_type:
            self._extend_same_fx(fx)
            return
        if self._try_standard_form(last.end_fx, fx):
            self._append(last.end_fx, fx, "standard", fx.index)
            return
        # 标准失败 → 强势 (前/后一笔)
        if self._cfg.bi_formation_mode is BiFormationMode.STRONG and self._try_strong(
            i, last.end_fx, fx
        ):
            return
        if self._cfg.bi_fractal_repair:
            self._repair_sub_peak(i, fx)

    def _try_first_bi(self, fx: Fenxing) -> None:
        for cand in self._candidates:
            if cand.fx_type is fx.fx_type:
                continue
            if self._try_standard_form(cand, fx):
                self._append(cand, fx, "standard", fx.index)
                self._candidates = []
                return
        self._candidates.append(fx)

    # ── 强势笔 (前一笔 / 后一笔；前优先) ─────────────────────────────────
    def _try_strong(self, i: int, start_fx: Fenxing, end_fx: Fenxing) -> bool:
        cand_amp = _bi_amplitude(start_fx, end_fx)
        ratio = self._cfg.bi_strength_ratio
        # 前一笔 (实时，已构建的相邻反向笔)
        prev = self._bis[-1]
        prev_amp = _bi_amplitude(prev.start_fx, prev.end_fx)
        if prev_amp > 0 and cand_amp >= ratio * prev_amp:
            self._append(start_fx, end_fx, "strong_prev", end_fx.index)
            return True
        # 后一笔 (有界 look-ahead: 从 end_fx 起首个 standard 反向笔；禁递归强势)
        nxt = self._lookahead_next_std_bi(i, end_fx)
        if nxt is not None:
            next_amp, dep_fx_index = nxt
            if next_amp > 0 and cand_amp >= ratio * next_amp:
                self._append(start_fx, end_fx, "strong_next", dep_fx_index)
                return True
        return False

    def _lookahead_next_std_bi(
        self, i: int, from_fx: Fenxing
    ) -> tuple[float, int] | None:
        """从 from_fx 起，按 standard 规则形成的下一条反向笔的 (幅度, 其端点分型下标)。

        只认 standard（不递归强势，已定 2）；取首个 standard 成笔的反向分型（有界）。
        """
        for q in range(i + 1, len(self._fxs)):
            nf = self._fxs[q]
            if nf.fx_type is from_fx.fx_type:
                continue
            if self._try_standard_form(from_fx, nf):
                return _bi_amplitude(from_fx, nf), nf.index
        return None

    # 次笔(=老笔线段, 特征序列法) 暂搁置, 见 run()。实现待线段草案确认 (用户 2026-06-17)。

    # ── 同型延伸 / sub_peak 修正 (与 standard 共用) ──────────────────────
    def _extend_same_fx(self, fx: Fenxing) -> None:
        # 同型分型永远取更极值 (两顶取更高 / 两底取更低, 第 65 课)。原 first 变体 v7 删除。
        last = self._bis[-1]
        if last.direction is BiDir.UP:
            if fx.high > _top_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)
        else:
            if fx.low < _bottom_value(last.end_fx):
                last.end_fx = fx
                last.dep_index = max(last.dep_index, fx.index)

    def _repair_sub_peak(self, i: int, fx: Fenxing) -> bool:
        """笔破坏修正 (bi_fractal_repair, 项目变体)：反弹笔起点被反向更极值 fx 击穿时，
        仅当**反向确认守卫**通过 (fx 为真极值、反弹是假反弹) 才吸收反弹笔、把前一笔延伸到 fx。
        守卫见 ``_confirm_reverse_break``；吸收笔 dep_index = 确认处下标 (确认前恒 provisional)。
        """
        if len(self._bis) < 2:
            return False
        last, prev = self._bis[-1], self._bis[-2]
        if last.direction is BiDir.DOWN:
            if fx.high < _top_value(last.start_fx):
                return False
            if _bottom_value(last.end_fx) < _bottom_value(prev.start_fx):
                return False
        else:
            if fx.low > _bottom_value(last.start_fx):
                return False
            if _top_value(last.end_fx) > _top_value(prev.start_fx):
                return False
        if not self._is_peak(prev.start_fx, fx, _direction_of(fx)):
            return False
        confirm_index = self._confirm_reverse_break(i, fx, last)
        if confirm_index is None:
            return False
        popped = self._bis.pop()
        before = self._bis[-1].end_fx
        self._extend_same_fx(fx)
        if self._bis[-1].end_fx is before:
            self._bis.append(popped)
            return False
        self._bis[-1].dep_index = max(self._bis[-1].dep_index, confirm_index)
        return True

    def _confirm_reverse_break(self, i: int, fx: Fenxing, last: _WorkBi) -> int | None:
        """反向确认守卫 (bi-v1 笔破坏修正小节，项目变体)。

        fx 击穿反弹笔 ``last`` 起点后，从 fx 在分型序列向后**有界扫描**：
        - 若价格在「从反弹笔顶/底 T 形成有效反向笔」**之前**先**越过 T 的极值** →
          反弹是假反弹、fx 是真极值 → 返回确认处合并下标 (供 dep 水位线，确认前恒 provisional)。
        - 若先形成「T→反向有效笔」 → 反弹是真实摆动、T 成立 → 返回 ``None`` (不吸收)。
        - 扫到末尾两者皆无 (数据不足) → ``None`` (保守不吸收，随回补再判)。
        """
        t = last.end_fx
        up = last.direction is BiDir.UP
        for q in range(i + 1, len(self._fxs)):
            g = self._fxs[q]
            if up:
                if g.fx_type is FxType.TOP and g.high > t.high:
                    return g.index
                if g.fx_type is FxType.BOTTOM and self._try_standard_form(t, g):
                    return None
            else:
                if g.fx_type is FxType.BOTTOM and g.low < t.low:
                    return g.index
                if g.fx_type is FxType.TOP and self._try_standard_form(t, g):
                    return None
        return None

    def _append(
        self, start: Fenxing, end: Fenxing, rule_kind: str, dep_index: int
    ) -> None:
        self._bis.append(_WorkBi(start, end, _direction_of(end), rule_kind, dep_index))

    # ── 标准成笔判定 (距离 → 端点检查 → 端点极值) ───────────────────────
    def _try_standard_form(self, start: Fenxing, end: Fenxing) -> bool:
        if start.fx_type is end.fx_type:
            return False
        if not self._check_distance(start, end):
            return False
        if not self._check_endpoint(start, end):
            return False
        if self._cfg.bi_require_peak and not self._is_peak(
            start, end, _direction_of(end)
        ):
            return False
        return True

    # ── 距离 (bi_span_mode 分派) ─────────────────────────────────────────
    def _check_distance(self, start: Fenxing, end: Fenxing) -> bool:
        if self._cfg.bi_span_mode is BiSpanMode.MERGED_CENTER:
            return self._check_center_span(start, end)
        return self._check_raw_extreme(start, end)

    def _check_center_span(self, start: Fenxing, end: Fenxing) -> bool:
        base_span = end.index - start.index
        if base_span >= self._cfg.bi_min_span:
            return True
        if not self._cfg.bi_gap_as_bar:
            return False
        gap_count = sum(
            1
            for i in range(start.index, end.index)
            if self._has_gap(self._merged[i], self._merged[i + 1])
        )
        return base_span + gap_count >= self._cfg.bi_min_span

    def _check_raw_extreme(self, start: Fenxing, end: Fenxing) -> bool:
        # ① 不共用 K (三元窗口无公共合并单元，内建)
        if start.index + 1 >= end.index - 1:
            return False
        # ② 极值原始 K 索引差 ≥ bi_min_span
        if end.fx_type is FxType.TOP:
            start_raw = self._extreme_raw_index(start, want_high=False)
            end_raw = self._extreme_raw_index(end, want_high=True)
        else:
            start_raw = self._extreme_raw_index(start, want_high=True)
            end_raw = self._extreme_raw_index(end, want_high=False)
        return end_raw - start_raw >= self._cfg.bi_min_span

    def _has_gap(self, a: MergedKline, b: MergedKline) -> bool:
        a_lo, a_hi = self._raw_extremes(a)
        b_lo, b_hi = self._raw_extremes(b)
        return max(a_lo, b_lo) > min(a_hi, b_hi)

    def _raw_extremes(self, u: MergedKline) -> tuple[float, float]:
        members = self._raw[u.start_index : u.end_index + 1]
        return min(k.low for k in members), max(k.high for k in members)

    def _extreme_raw_index(self, fx: Fenxing, *, want_high: bool) -> int:
        u = self._merged[fx.index]
        members = self._raw[u.start_index : u.end_index + 1]
        if want_high:
            best = max(range(len(members)), key=lambda i: (members[i].high, -i))
        else:
            best = min(range(len(members)), key=lambda i: (members[i].low, i))
        return u.start_index + best

    # ── 端点有效性 (bi_endpoint_check；none 跳过) ───────────────────────
    def _check_endpoint(self, start: Fenxing, end: Fenxing) -> bool:
        method = self._cfg.bi_endpoint_check
        if method is BiEndpointCheck.NONE:
            return True
        s_pre, s_mid, s_next = self._fx_units(start)
        e_pre, e_mid, e_next = self._fx_units(end)
        if start.fx_type is FxType.TOP:  # 向下笔: 顶 → 底
            if method is BiEndpointCheck.HALF:
                item2_high = max(e_pre.high, e_mid.high)
                self_low = min(s_mid.low, s_next.low)
            elif method is BiEndpointCheck.LOSS:
                item2_high = e_mid.high
                self_low = s_mid.low
            else:
                item2_high = max(e_pre.high, e_mid.high, e_next.high)
                self_low = min(s_pre.low, s_mid.low, s_next.low)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.low > item2_high
            return s_mid.high > item2_high and e_mid.low < self_low
        else:  # 向上笔: 底 → 顶
            if method is BiEndpointCheck.HALF:
                item2_low = min(e_pre.low, e_mid.low)
                cur_high = max(s_mid.high, s_next.high)
            elif method is BiEndpointCheck.LOSS:
                item2_low = e_mid.low
                cur_high = s_mid.high
            else:
                item2_low = min(e_pre.low, e_mid.low, e_next.low)
                cur_high = max(s_pre.high, s_mid.high, s_next.high)
            if method is BiEndpointCheck.TOTALLY:
                return s_mid.high < item2_low
            return s_mid.low < item2_low and e_mid.high > cur_high

    def _is_peak(self, start: Fenxing, end: Fenxing, direction: BiDir) -> bool:
        if direction is BiDir.UP:
            thr = _top_value(end)
            return all(u.high <= thr for u in self._merged[start.index + 1 : end.index])
        thr = _bottom_value(end)
        return all(u.low >= thr for u in self._merged[start.index + 1 : end.index])

    def _fx_units(self, fx: Fenxing) -> tuple[MergedKline, MergedKline, MergedKline]:
        return (
            self._merged[fx.index - 1],
            self._merged[fx.index],
            self._merged[fx.index + 1],
        )

    # ── 输出 ─────────────────────────────────────────────────────────────
    def finish(self, profile_id: str, config_hash: str) -> list[Bi]:
        out: list[Bi] = []
        for wb in self._bis:
            up = wb.direction is BiDir.UP
            start_price = _bottom_value(wb.start_fx) if up else _top_value(wb.start_fx)
            end_price = _top_value(wb.end_fx) if up else _bottom_value(wb.end_fx)
            rule_id = _rule_for(wb, self._cfg.bi_span_mode)
            trace = StructTrace(
                algo_card_id=_ALGO_CARD_ID,
                rule_id=rule_id,
                profile_id=profile_id,
                config_hash=config_hash or None,
                source_from_ts=self._merged[wb.start_fx.index - 1].start_ts,
                source_to_ts=self._merged[wb.end_fx.index + 1].end_ts,
                merged_from_index=wb.start_fx.index,
                merged_to_index=wb.end_fx.index,
                dep_to_index=wb.dep_index,
            )
            out.append(
                Bi(
                    period=wb.end_fx.period,
                    direction=wb.direction,
                    start_ts=wb.start_fx.timestamp,
                    end_ts=wb.end_fx.timestamp,
                    start_price=start_price,
                    end_price=end_price,
                    high=end_price if up else start_price,
                    low=start_price if up else end_price,
                    trace=trace,
                )
            )
        return out


def _rule_for(wb: _WorkBi, span_mode: BiSpanMode) -> str:
    """rule_id 按成笔实际规则派生 (bi-v1 §7)。standard 再按 span_mode 分 5k/4k。"""
    up = wb.direction is BiDir.UP
    if wb.rule_kind == "strong_prev":
        return _RULE_STRONG_PREV[0 if up else 1]
    if wb.rule_kind == "strong_next":
        return _RULE_STRONG_NEXT[0 if up else 1]
    if wb.rule_kind == "secondary":
        return _RULE_SECONDARY[0 if up else 1]
    # standard
    pair = _RULE_STD_MERGED if span_mode is BiSpanMode.MERGED_CENTER else _RULE_STD_RAW
    return pair[0 if up else 1]


def _bi_amplitude(start_fx: Fenxing, end_fx: Fenxing) -> float:
    """笔幅度 = abs(端点价差)（绝对价差，本轮锁定）。方向由 end_fx 决定。"""
    if end_fx.fx_type is FxType.TOP:  # 向上笔: 底→顶
        return abs(_top_value(end_fx) - _bottom_value(start_fx))
    return abs(_bottom_value(end_fx) - _top_value(start_fx))  # 向下笔: 顶→底


def _direction_of(end_fx: Fenxing) -> BiDir:
    return BiDir.UP if end_fx.fx_type is FxType.TOP else BiDir.DOWN


def _top_value(fx: Fenxing) -> float:
    return fx.high


def _bottom_value(fx: Fenxing) -> float:
    return fx.low
```
