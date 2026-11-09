# Chan_mergedkline

## 000 — Scope

## 001 — Definition (What)

## 002 — Algorithm (How)

### 002.a — Algorithm Tree

### 002.b — Detailed Implementation Example

### 002.c — Helper Functions

### 002.d — Pseudocode

## 003 — Reasoning (Why)

## 004 — Other Notes

## 005 — Gaps and Pending Items

## Appendix A — Quotes from ChanOriginal

以第62课连续正文为主，保留理解包含处理所需的前后文；再补第65课连续说明及其他课程答疑。引文不以短小为目标，不在论证中间切断。 显示处理仅移除HTML样式标签、转义比较符和问答分隔符，并将区间记号设为行内代码，避免Obsidian误识别；原始参考文件保持不变。补充材料中的正文、问答与编者注分别标明。

### A.1 — 第62课：连续正文与原图

第62课正文，第26–44行。[1] 连续保留从几何定义背景，到分型、笔、包含处理、非包含分类及图8／9说明的正文；未在段落中间删节。图8／9在此属于原文上下文，不作为K线包含规则。分隔线后的编者学习整理不混入作者正文。

> 瞧了一下，有位叫石猴的网友写了帖子来解释什么是线段，他的理解还行，但不够严密。其实，本ID的线段是可以最精确定义的，本ID的理论，本质上是一套几何理论，其有效性就如同几何一般，本ID理论当然有失败不严谨的时候，但这前提是几何的基础失败不严谨，不明白这一点，就不明白本ID的理论。这里，就把本来是后面的课程提前说说。
>
> 下面的定义与图，都适合任何周期的K线图。先看图中的第1、2，图中的小线段代表的是K线，这里不分阳线阴线，只看K线高低点。
>
> ![教你炒股票62：分型、笔与线段](memoWX_015_Chan_mergedkline/lesson062-image001.jpg)
>
> **像图1这种，第二K线高点是相邻三K线高点中最高的，而低点也是相邻三K线低点中最高的，本ID给一个定义叫顶分型**；**图2这种叫底分型，第二K线低点是相邻三K线低点中最低的，而高点也是相邻三K线高点中最低的。**看不明白定义的，看图就明白了，这么直观都不明白，那去和孔男人为伍吧。
>
> **顶分型的最高点叫该分型的顶，底分型的最低点叫该分型的底，**由于顶分型的底和底分型的顶是没有意义的，所以顶分型的顶和底分型的底就可以简称为顶和低。也就是说，**当我们以后说顶和底时，就分别是说顶分型的顶和底分型的底。**
>
> **两个相邻的顶和底之间构成一笔，所谓笔，就是顶和底之间的其他波动，都可以忽略不算，但注意，一定是相邻的顶和底，**隔了几个就不是了。**而所谓的线段，就是至少由三笔组成。**但这里有一个细微的地方要分清楚，因为结合律是必须遵守的，像图3这种，顶和底之间必须共用一个K线，这就违反结合律了，所以这不算一笔，而图4，就光是顶和底了，中间没有其他K线，一般来说，也最好不算一笔，而图5，是一笔的最基本的图形，顶和底之间还有一根K线。在实际分析中，都必须要求顶和底之间都至少有一K线当成一笔的最基本要求。
>
> **当然，实际图形里，有些复杂的关系会出现，就是相邻两K线可以出现如图6这种包含关系，也就是一K线的高低点全在另一K线的范围里，这种情况下，可以这样处理，在向上时，把两K线的最高点当高点，而两K线低点中的较高者当成低点，这样就把两K线合并成一新的K线；反之，当向下时，把两K线的最低点当低点，而两K线高点中的较低者当成高点，这样就把两K线合并成一新的K线。经过这样的处理，所有K线图都可以处理成没有包含关系的图形。**
>
> ![教你炒股票62：分型、笔与线段](memoWX_015_Chan_mergedkline/lesson062-image001.jpg)
>
> 而图7，就给出了经过以上处理，没有包含关系的图形中，三相邻K线之间可能组合的一个完全分类，其中的二、四，就是分别是顶分型和底分型，一可以叫上升K线，三可以叫下降K线。所以，上升的一笔，由结合律，就一定是底分型+上升K线+顶分型；下降的一笔，就是顶分型+下降K线+底分型。注意，这里的上升、下降K线，不一定都是3根，可以无数根，只要一直保持这定义就可以。当然，简单的，也可以是1、2根，这只要不违反结合律和定义就可以。
>
> 至于图8，就是线段的最基本形态，而图9，就是线段破坏，也就是两线段组合的其中一种形态。有人可能要说，这怎么有点像波浪理论，这有什么奇怪的，本ID的理论可以严格地推论出波浪理论的所有结论，而且还可以指出他理论的所有不足，波浪理论和本ID的理论一点可比性都没有。不仅是波浪理论，所有关于股市的理论，只要是关系到图形的，本ID的理论都可以严格推论，因为本ID的理论是关于走势图形最基础的理论，谁都逃不掉。

### A.2 — 第65课：连续包含、顺序原则与方向判定

第65课正文，第27–43行。[2] 连续保留；以下“娇注”及“注：应去掉等于号”为本地参考文本中的插注，保留其标记，不认作作者原话。

> 如果真明白了前面的，这课就不必再说了。本ID反复强调，本ID理论的关键是一套几何化的思维，因此，你需要从最基本的定义出发，而在实际操作的辨认中，这一点更重要。所有复杂的情况，其实，从最基本的定义出发，都没有任何的困难可言。
>
> 例如，对于分型，里面最大的麻烦，就是所谓的前后K线间的包含关系，其次，有点简单的几何思维，根据定义，任何人都可以马上得出以下的一些推论：
>
> 1、用`[di,gi]`记号第i根K线的最低和最高构成的区间，当向上时，顺次n个包含关系的K线组，等价于`[maxdi,maxgi]`(娇：取最大值）的区间对应的K线，也就是说，这n个K线，和最低最高的区间为`[maxdi,maxgi]`的K线是一回事情；向下时，顺次n个包含关系的K线组，等价于`[mindi,mingi]`（娇注：取最小值）的区间对应的K线。
>
> 2、结合律是有关本ID这理论中最基础的，在K线的包含关系中，当然也需要遵守，**而包含关系，不符合传递律，**也就是说，第1、2根K线是包含关系，第2、3根也是包含关系，但并不意味着第1、3根就有包含关系。因此在K线包含关系的分析中，还要遵守顺序原则，就是先用第1、2根K线的包含关系确认新的K线，然后用新的K线去和第三根比，如果有包含关系，继续用包含关系的法则结合成新的K线，如果没有，就按正常K线去处理。
>
> 3、有人可能还要问，什么是向上？什么是向下？其实，这根本没什么可说的，任何看过图的都知道什么是向上，什么是向下。当然，本ID的理论是严格的几何理论，对向上向下，也可以严格地进行几何定义，只不过，这样对于不习惯数学符号的人，头又要大一次了。
>
> **假设，第n根K线满足第n根与第n+1根的包含关系，而第n根与第n-1根不是包含关系，那么如果gn&gt;=gn-1，那么称第n-1、n、n+1根K线是向上的；如果dn&lt;=dn-1，那么称第n-1、n、n+1根K线是向下的。(注：应去掉等于号)**
>
> **有人可能又要问，如果gn&lt;gn-1且dn&gt;dn-1，算什么？那就是一种包含关系，这就违反了前面第n根与第n-1根不是包含关系的假设。同样道理，gn&gt;=gn-1与dn&lt;=dn-1不可能同时成立。**（娇注：同时成立则为包含关系）
>
> 上面包含关系的定义已经十分清楚，就是一些最精确的几何定义，只要按照定义来，没有任何图是不可以精确无误地、按统一的标准去找出所有的分型来。注意，这种定义是唯一的，有统一答案的，就算是本ID，如果弄错了，也就是错，没有任何含糊的地方，是可以在当下或任何时候明确无误地给出唯一答案的，这答案与时间无关，与人无关，是客观的，不可更改的，唯一的要求就是被分析的K线已经走出来。
>
> 从这里，本ID理论的当下性也就有了一个很客观的描述。为什么要当下的？因为如果当下那些K线还没走出来，那么具体的分型就找不出来，相应的笔、线段、最低级别中枢、高级别走势类型等就不可能划分出来，这样就无从分析了。而一旦当下的K线走出来，就可以当下按客观标准唯一地找出相应的分型结构，当下的分析和事后的分析，是一样的，分析的结果也是一样的，没有任何的不同。因此，当下性，其实就是本ID的客观性。

### A.3 — 反向包含、连续处理与相等边界（答疑）

第69课，答疑，本地源文件第329行。[3]

> [匿名] 天眼 删除此人所有评论   2007-08-14 16:21:55  老大,有几个问题我比较模糊, A.关于k线的包含关系. 一.如果第n-1根K线的高低点全在第n根K线的范围里,那么n-1和n是不是包含关系? \=\=  这当然是，难道还有什么疑问的？对于连续包含关系，必须按时间顺序，一个个合并下去。  二.下列情况是不是包含关系? 假设n和n-1 k线的高低点为gn.,dn, gn-1,dn-1 . 1.gn=gn-1且dn&gt;dn-1; 2. dn=dn-1.且gn&lt;gn-1; 3. dn=dn-1.且gn=gn-1;  \=\= 当然是。

### A.4 — 一端／两端相等：完整问答

第75课，原问题与作者回答，第80–80行。[4] `==` 前为提问，后为作者回答；问题中的定义或推测不自动视为作者结论。保留源文本的排版与措辞。

> 老实念佛 删除此人所有评论  2007-08-30 16:15:09  老大，在分型上：相邻两根K线，只要有一端数值相同，就必定是包含关系？相邻两根K线的高低点完全相同是不是可以不算是包含？或者包含只能是一根‘完全’在另一根的范围之内，即高点小于高点，低点大于低点？请明示，谢谢！ \=\= **只要有一端相同，那必然是包含，两端相同那更是了，所以如果不是包含关系的，都必然不需要考虑相等关系。**

### A.5 — 绝对相等与方向前提：完整问答

第75课，原问题与作者回答，第142–142行。[4] `==` 前为提问，后为作者回答；问题中的定义或推测不自动视为作者结论。保留源文本的排版与措辞。

> 逍遥往2007-08-30 16:53:05  疑惑：刚才姐姐回答问题时说到“等于”时属于包含关系，是否跟65课里面的“假设，第n根K线满足第n根与第n+1根的包含关系，而第n根与第n-1根不是包含关系，那么如果gn&gt;=gn-1，那么称第n-1、n、n+1根K线是向上的；如果dn&lt;=dn-1，那么称第n-1、n、n+1根K线是向下的。”矛盾 \=\= **&gt;=，其实应该读作不小于，当然包括等于的情况，但不是说一定有这种情况，既然不包含是前提，那自然就没有这种情况，这有什么矛盾的？ 另外，必须注意，包含关系中的相等，必须是绝对相等，也就是说必须在软件上最后一位小数都相等。一般来说，很少出现这种情况。**

### A.6 — 第68课：数据来源、连续性与包含判断

第68课，第99–109行。[5] 连续保留从检查软件数据差异，到同一数据源要求，再到两根K线的具体价格比较及原图。

> 今天这雨下的不是地方，停得不是时候，最后换来一首五律，也算这腐败没白腐败。本ID三教九流都交往，难免腐败活动多。本周还有一个法国人的腐败活动在君悦，白酒是喝不上了。喝红酒没有任何写古诗的感觉，古诗总是白酒的。
>
> 今天走的时候发现小丸子、大道等指出原来的分段有问题，因为本ID平时是用别的系统，写帖子才用同花顺，没注意这两个系统数据上的细微差别，就对着标上了。仔细检查同花顺系统里的数据，确实原来的分段有问题，所以马上改了，然后在车上还上来打了一个招呼。新浪的刷新似乎很慢，一般本ID发完帖子，出来也看不到自己发的帖子，要等上一阵，但在“我的所有文章”里能马上看到，只是在首页以及最新文章列表不显示，不知道各位是否也有这个问题。
>
> 刚才回来看到有人说别的软件和同花顺的数据不同，那不算的一笔在别的软件上是一笔。这个问题其实很正常，在课程里本ID已经说过，每个软件对数据的反应或处理可能都有点不同，所以，数据有差异是很正常的。这就像同样倍数的显微镜，即使同一厂家都不可能绝对一样。所以，看的时候，坚持用同一显微镜就可以。本ID看盘时用的软件和同花顺不同，以后也注意点，不能照抄过来。但这些细微的地方，并不大影响整体的判断。而且这个分段，比原来的更简单清晰，更美。
>
> 因此，各位必须注意，在一个具体的分析中，一定要坚持用同一套软件的同一个数据源，这样，数据的连续性是保持在同一规范下的。不同软件的数据不同导致的不同划分，不会实质影响大的级别划分，站在实际操作层面，至少要在1分钟级别上讨论操作问题，所以这样的测量误差，是在可接受范围内的。测量误差，是不影响理论的统一性与严谨性的。
>
> 那么，这样的分歧，究竟有多细微的程度，各位可以看下图。关键是绿箭头指着的两个K线，第一根范围是[4594.91，4597.57],第二根范围是[4595.19，4597.44]，由于第一根是最高收的，而4597.57与4597.44相差极为细微，所以可能就是0.1秒的数据收集差异，就导致在同花顺中的包含关系，在别的软件中就是第二根的高点比第一根的高一点点，就不是包含关系了，第二根才是分型的顶，这样，笔自然就成立了。如果这里的笔成立，那么整个分段就有一定的变化了。不过，这并不实质影响整个走势的分析，由于各位也应该明白，为什么在实际的分类中，必须要从分型和笔开始，最后由线段构成最小级别的中枢，其中一个原因，就是这样，到了最小级别的中枢的层次，这种微小测量误差造成的差异就可以尽量地抹平了。而到了更大级别的中枢，这些就不再存在。当然，这不是分型、笔、线段的主要功用，但也是其中之一。
>
> ![](memoWX_015_Chan_mergedkline/lesson068-image001.jpg)

图文核对：本地源文件确实在该段后链接此图，但图中未清楚显示4594.91／4597.57等数值及相应绿箭头。图文对应仍待核对；不以重绘替代原始证据。原图来源：[068/image001.jpg](../../references/chan_theory/068/image001.jpg)。

### A.7 — 第82课：分型形成的心理过程与包含的含义

第82课正文，第32–36行。[6] 连续保留买卖力量三次较量的说明，再读包含与观望的关系。“娇注”是本地参考文本的编者插注，不认作作者原话。

> 显然，一个顶分型之所以成立，是卖的分力最终战胜了买的分力，而其中，买的分力有三次的努力，而卖的分力，有三次的阻击。用最标准的已经过包含处理的三K线模型：第一根K线的高点，被卖分力阻击后，出现回落，这个回落，出现在第一根K线的上影部分或者第二根K线的下影部分，而在第二根K线，出现一个更高的高点，但这个高点，显然与第一根K线的高点中出现的买的分力，一定在小级别上出现力度背驰，从而至少制造了第二根K线的上影部分。最后，第三根K线，会再次继续一次买的分力的攻击，但这个攻击，完全被卖的分力击败，从而不能成为一个新高点，在小级别上，大致出现一种第二类卖点的走势。
>
> 由上可见，一个分型结构的出现，如同中枢，都是经过一个三次的反复心理较量过程，只是中枢用的是三个次级别。所谓一而再、再而三，三而竭，所以一个顶分型就这样出现了，而底分型的情况，反过来就是。
>
> 现在，我们可以深入分析这三根K线的不同情况。首先，一个完全没有包含关系的分型结构，意味着市场双方都是直截了当，没有太多犹豫。包含关系（娇注：只要不是直接把阳线以长阴线吃掉）意味着一种犹豫，一种不确定的观望等，一般在小级别上，都会有中枢延伸、扩展之类的东西。

### A.8 — 包含处理不能因笔数不足而省略：完整问答

第66课，原问题与作者回答，第207–209行。[7] `==` 前为提问，后为作者回答；问题中的定义或推测不自动视为作者结论。保留源文本的排版与措辞。

> [匿名] 新浪网友 2007-07-31 16:44:03  请问老大，有时，大盘的“一笔”可能就5～6根K线，走得比较平，其中存在包含关系，如果包含掉，则不能形成一笔，请问要看包含吗？  \=\=
>
> **有包含的一定要非包含化处理。严格按定义来。**

### A.9 — 一字涨停与等号问题：完整问答

第75课，原问题与作者回答，第122–124行。[4] `==` 前为提问，后为作者回答；问题中的定义或推测不自动视为作者结论。保留源文本的排版与措辞。

> 快乐vs菜虫 删除此人所有评论   2007-08-30 16:40:45  缠姐，我由刚才你的回答给出相邻两K线的包含定义： 相邻两K线K1和K2，K1的高点为G1低点为D1,K2的高点为G2低点为D2,若 D1&lt;=D2,G1&gt;=G2则说明K1包含K2 D1&gt;=D2,G1&lt;=G2则说明K2包含K1
>
> 另外，课程65当中“第n根K线满足第n根与第n+1根的包含关系，而第n根与第n-1根不是包含关系，那么如果gn&gt;=gn-1，那么称第n-1、n、n+1根K线是向上的；”这段话应该也是有问题的，应该把 "gn&gt;=gn-1改成 "gn&gt;gn-1"。 不知道这样说对吗？ 还有例如一只股票开盘就封涨停并且全天没打开过以涨停报收，是否可以把当天所有的K线依次全部合并为一根K线，也就是说当天的走势就可以看成是一个跳空缺口加一根K线？？ \=\= **其实是一个意思，不包含就自然没有相等，但注意，这里包含的相等，指的是绝对相等，而后面的相等，还包含测量相等的情况。 另外，一字涨停当然可以这样看，所以最开始时就说，这只形成最小级别的中枢。而站在用分型开始构造最小级别中枢的角度，那就连分型都算不上，更不说笔了。**

## Appendix B — CC 的K线包含处理：连续代码与处理步骤

依据下载网站发布的 `manual_rebuild` 版 `KlineCombiner`，核对日期：2026-11-08。[8] 下文保留相关函数的完整代码，不在函数中间用省略号截断；仅按调用关系重排，方法代码块去除类外层缩进以便阅读。完整文件仍以[提取源码](../../references/cc_algo/extracted/combiner.py)为准。代码中的注释／docstring属于实现者说明；各节解释核对的是实际执行语句。

整体路径是：`append → 前导缓冲／初始化 → 末单元包含判断 → 吸收或新建 → 输出`；末根修订经 `pop_last_kline → 重算或恢复前导期 → append`。初始化口径、输出状态及回退都是CC实现行为，不自动成为TDS已确认规则。

### B.1 — 比较判据、合并单元与入口状态

源码第32–42行，`_direction`。[8]

```python
def _direction(a_high: float, a_low: float, b_high: float, b_low: float) -> KlineDir | None:
    """相邻非包含两单元方向：同时严格抬高→UP，同时严格降低→DOWN（第65课，去等号）。

    返回 None 表示「包含 / 等价 / 无法唯一判定」（含相等极值）——此时不构成方向判据。
    注：非包含必然落入 UP / DOWN 之一；包含或任一边相等都返回 None。
    """
    if b_high > a_high and b_low > a_low:
        return KlineDir.UP
    if b_high < a_high and b_low < a_low:
        return KlineDir.DOWN
    return None
```

源码第45–47行，`_contains`。[8]

```python
def _contains(a_high: float, a_low: float, b_high: float, b_low: float) -> bool:
    """a 是否包含 b（区间互含，方向无关；含相等边界 → 视为包含，对应 §16-2/§16-4）。"""
    return a_high >= b_high and a_low <= b_low
```

源码第50–63行，`_Unit`。[8]

```python
@dataclass(slots=True)
class _Unit:
    """内部可变合并单元（输出时转 MergedKline）。"""

    high: float
    low: float
    dir: KlineDir
    rule_id: str  # 该单元形成规则（merge.init / merge.dir.up / merge.dir.down）
    start_index: int  # 原始 K 线序列起始下标
    members: list[Kline] = field(default_factory=list)

    @property
    def end_index(self) -> int:
        return self.start_index + len(self.members) - 1
```

源码第74–79行，`__init__`。[8]

```python
def __init__(self, period: str) -> None:
    self.period = period
    self._units: list[_Unit] = []
    self._lead: list[Kline] = []  # 方向未定的前导缓冲
    self._established = False
    self._total = 0  # 已消费原始 K 线根数（= 下一根的全局下标）
```

源码第82–89行，`append`。[8]

```python
def append(self, k: Kline) -> None:
    """末端追加一根新 K 线（timestamp 严格更大，由 engine 保证）。"""
    if self._established:
        self._append_established(k, self._total)
    else:
        self._lead.append(k)
        self._try_establish()
    self._total += 1
```

阅读顺序先从比较判据到状态，再到入口。`_contains(a,b)` 是单向区间包含；是否存在包含关系，要由调用方检查两个方向。等号允许包含，方向则要求高低点同时严格移动，不能由收盘价或单独一个高点决定。

`append()` 的分流依赖 `_established`。未定向时保留原始K线到 `_lead`；定向后才走 `_append_established()`。`_total` 在处理后递增，传给常规追加函数的是当前原始索引。`append()` 本身没有检查时间戳、周期或OHLC有效性；注释所述时间顺序是调用方前提。[8]

### B.2 — 初始化：等待第一对方向，再处理整个前导链

源码第156–175行，`_try_establish`。[8]

```python
def _try_establish(self) -> None:
    """前导期：检查最新相邻对是否确立方向。"""
    n = len(self._lead)
    if n < 2:
        return
    a, b = self._lead[-2], self._lead[-1]
    d = _direction(a.high, a.low, b.high, b.low)
    if d is None:
        return
    # 确立：lead[0..n-2] 必为包含链（更早的可定向对会更早触发），坍缩成首个单元。
    blob = self._lead[: n - 1]
    unit0 = self._merge_blob(blob, d, start_index=0)
    unit1 = _Unit(
        high=b.high, low=b.low, dir=d,
        rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
        start_index=n - 1, members=[b],
    )
    self._units = [unit0, unit1]
    self._lead = []
    self._established = True
```

源码第177–188行，`_merge_blob`。[8]

```python
def _merge_blob(self, blob: list[Kline], d: KlineDir, start_index: int) -> _Unit:
    """把方向未定的包含链按确立方向 d 坍缩成首个单元（rule `merge.init`）。"""
    if d is KlineDir.UP:
        high = max(x.high for x in blob)
        low = max(x.low for x in blob)
    else:
        high = min(x.high for x in blob)
        low = min(x.low for x in blob)
    return _Unit(
        high=high, low=low, dir=d, rule_id=RULE_MERGE_INIT,
        start_index=start_index, members=list(blob),
    )
```

两段函数必须一起读：先比较 `_lead` 最后的两根原始K线，无法严格定向就不输出。首次找到方向后，`blob = _lead[:n-1]` 保留此前全部成员；`_merge_blob()` 用这个新方向对前导组整体取max/max或min/min。触发方向的最新K线单独成为第二单元。

这里没有把触发K线再与聚合后的首单元进行一次常规包含判断；代码直接设置两个单元。它与下节逐根比较末端单元的路径不同。此处说明实际执行顺序，不据此宣称两条路径对所有输入等价。若窗口一直未定向，`_units` 为空，输出也为空。[8]

### B.3 — 已定向：与当前末单元比较，包含则吸收，否则新建

源码第190–213行，`_append_established`。[8]

```python
def _append_established(self, k: Kline, idx: int) -> None:
    last = self._units[-1]
    contained = _contains(last.high, last.low, k.high, k.low) or _contains(
        k.high, k.low, last.high, last.low
    )
    if contained:  # 包含 → 按方向合并取值（rule_id 输出时按成员数派生, 见 _derive_rule_id）
        if last.dir is KlineDir.UP:
            last.high = max(last.high, k.high)
            last.low = max(last.low, k.low)
        else:
            last.high = min(last.high, k.high)
            last.low = min(last.low, k.low)
        last.members.append(k)
        return
    # 非包含 → 必为同时高低之一，新建单元（rule merge.dir.*）
    d = _direction(last.high, last.low, k.high, k.low)
    assert d is not None  # 非包含必可定向
    self._units.append(
        _Unit(
            high=k.high, low=k.low, dir=d,
            rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
            start_index=idx, members=[k],
        )
    )
```

函数先取已经合并后的 `last`，再检查两个方向的包含。进入包含分支后，沿用 `last.dir`：向上max/max，向下min/min；追加成员后立即返回。因此新K线即使是包住旧单元的一方，也不在该分支重新定向。

只有非包含分支才调用 `_direction()`，由当前末单元和新K线建立新单元，方向可延续或反转。下一次输入将与这个更新后的末单元比较，而不是固定与上一根原始K线比较。直接数值比较未引入近似相等容差。[8]

### B.4 — 撤回与重算：尾部更新怎样恢复到正确阶段

源码第91–114行，`pop_last_kline`。[8]

```python
def pop_last_kline(self) -> None:
    """回退最近一根原始 K 线（供同 ts 末端更新：pop 后 engine 再 append 新值）。"""
    if self._total == 0:
        return
    self._total -= 1
    if not self._established:
        self._lead.pop()
        return
    last = self._units[-1]
    last.members.pop()
    if last.members:
        self._recompute_unit(last)
        return
    self._units.pop()  # 单元清空 → 丢弃
    # 跨 establishment 边界回退（顺延口径 §16-1）: 若只剩首段 merge.init 单元, 说明被弹出的
    # 正是确立方向的那根, 方向依据已消失 → 恢复到方向未定的前导期, 由后续 append 重判。
    if len(self._units) == 1 and self._units[0].rule_id == RULE_MERGE_INIT:
        blob = self._units[0]
        self._lead = list(blob.members)
        self._units = []
        self._established = False
    elif not self._units:  # 防御: 全部弹空 → 回初始
        self._lead = []
        self._established = False
```

源码第230–237行，`_recompute_unit`。[8]

```python
def _recompute_unit(self, u: _Unit) -> None:
    """从单元剩余 members 按其方向重算极值（pop 末端 K 线后用）。"""
    if u.dir is KlineDir.UP:
        u.high = max(x.high for x in u.members)
        u.low = max(x.low for x in u.members)
    else:
        u.high = min(x.high for x in u.members)
        u.low = min(x.low for x in u.members)
```

更新已有时间戳末根时，需要调用方先pop再append；这个类没有按时间戳自动辨别替换。撤回发生在前导阶段，只弹出 `_lead`；定向后先去掉末单元最后成员，若还有成员，就按保存方向重算极值，不能只反向减掉旧极值。

若末单元被删空，则删单元。只剩 `merge.init` 时，说明建立方向的那根也被撤掉：把首单元的成员恢复为 `_lead`，清空单元并取消定向，等待后续输入重新判断。回退能改变初始化状态，因此不能只把它理解成价格修正。[8]

### B.5 — 输出：范围映射、规则标记与稳定边界

源码第130–153行，`to_merged_klines`。[8]

```python
def to_merged_klines(self) -> list[MergedKline]:
    """当前合并单元序列（含轻量 trace）。方向未定前导期返回空。"""
    out: list[MergedKline] = []
    for u in self._units:
        trace = StructTrace(
            algo_card_id=_ALGO_CARD_ID,
            rule_id=self._derive_rule_id(u),
            source_from_ts=u.members[0].timestamp,
            source_to_ts=u.members[-1].timestamp,
        )
        out.append(
            MergedKline(
                period=self.period,
                dir=u.dir,
                high=u.high,
                low=u.low,
                start_ts=u.members[0].timestamp,
                end_ts=u.members[-1].timestamp,
                start_index=u.start_index,
                end_index=u.end_index,
                trace=trace,
            )
        )
    return out
```

源码第215–228行，`_derive_rule_id`。[8]

```python
def _derive_rule_id(self, u: _Unit) -> str:
    """按单元**当前状态**派生 trace rule_id（§13「最近一次操作」）。

    形成规则 (u.rule_id) 始终保留不变 (merge.init / merge.dir.*)；输出时:
    - 首段 blob → merge.init;
    - 形成后吸收了包含根 (成员 > 1) → merge.contains;
    - 单根方向单元 → 其形成方向 merge.dir.up/down。
    派生而非 mutate, 故 pop/append 回退后 rule_id 自动正确, 无需恢复 (Codex r2 ⚠)。
    """
    if u.rule_id == RULE_MERGE_INIT:
        return RULE_MERGE_INIT
    if len(u.members) > 1:
        return RULE_MERGE_CONTAINS
    return u.rule_id  # 形成时的 merge.dir.up/down
```

源码第117–124行，`stable_index`。[8]

```python
def stable_index(self) -> int:
    """末端稳定点（§10）：倒数第 2 个合并单元的原始 K 线结束下标；不足返回 -1。

    最后一个合并单元为 provisional（新根可能改写），其余 confirmed。O(1)。
    """
    if len(self._units) < 2:
        return -1
    return self._units[-2].end_index
```

源码第126–128行，`merged_count`。[8]

```python
def merged_count(self) -> int:
    """当前合并单元数量（O(1)）。"""
    return len(self._units)
```

输出保留方向、高低点、首尾原始索引与时间戳；来源区间由成员序列构造，依赖原始数据按序连续输入。没有把合并后高低点写回原始K线。这里的 `MergedKline` 输出也没有合成open/close/volume；不能仅因称作K线而假定它有完整OHLCV。

规则ID由当前成员状态派生：首组优先 `merge.init`，普通多成员组 `merge.contains`，单成员组保留形成方向。这样撤回成员后可重新得到对应标记，无需把包含标记永久写死。

`stable_index()` 取倒数第二单元的结束索引，不足两个单元则为-1；它区分正常追加下可改变的末单元与更早单元。显式撤回仍能改变更早状态，不能将此值当作任意历史回退后的永久承诺。[8]

### B.6 — 静态阅读结论与后续核验

本次按完整函数核对两条主路径及回退／输出，没有运行完整CC引擎，也未验证所有输入下的正确性。后续重点是：前导链整体聚合后直接建立两个单元是否满足期望边界、全包含窗口的空输出、相等极值、以及跨初始化边界的末根替换。这些疑问不能用网站介绍文字或样本结果代替验证。[8]

## References

[1] 缠中说禅. 教你炒股票62：分型、笔与线段. [本地参考文本](../../references/chan_theory/062.md)。

[2] 缠中说禅. 教你炒股票65：再说说分型、笔、线段. [本地参考文本](../../references/chan_theory/065.md)。

[3] 缠中说禅. 教你炒股票69：月线分段与上海大走势分析、预判. [本地参考文本](../../references/chan_theory/069.md)（含课后答疑）。

[4] 缠中说禅. 教你炒股票75：逗庄家玩的一些杂史1. [本地参考文本](../../references/chan_theory/075.md)（含课后答疑）。

[5] 缠中说禅. 教你炒股票68：走势预测的精确意义. [本地参考文本](../../references/chan_theory/068.md)。

[6] 缠中说禅. 教你炒股票82：分型结构的心理因素. [本地参考文本](../../references/chan_theory/082.md)。

[7] 缠中说禅. 教你炒股票66. [本地参考文本及课后答疑](../../references/chan_theory/066.md)。

[8] KWX/CC. 网站发布的 `KlineCombiner` Python实现. [原始网页快照](../../references/cc_algo/original.html#merge-recipe)；[提取代码](../../references/cc_algo/extracted/combiner.py)；[提取说明与校验值](../../references/cc_algo/extracted/README.md)。
