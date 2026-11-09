"""Insert S6 evidence appendices, preserving every byte before Appendix A."""
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
MEMO=ROOT/'docs/memo/memoWX_023_Chan_zoushi.md'
OLD=MEMO.read_bytes()
PREFIX=OLD.decode().split('## Appendix A —',1)[0]
SOURCE=ROOT/'references/chan_theory'
quote_records=[]

def quote(lesson:int,start:int,stop:int)->str:
    path=SOURCE/f'{lesson:03d}.md'
    raw='\n'.join(path.read_text().splitlines()[start-1:stop])
    # Drop presentational span markup only; retain compiler note text explicitly.
    text=re.sub(r'</?span\b[^>]*>','',raw)
    text=text.replace('==','\\=\\=')
    text=text.replace('(017/image001.jpg)','(memoWX_023_Chan_zoushi/lesson017-image001.jpg)')
    text=text.replace('(020/image005.jpg)','(memoWX_023_Chan_zoushi/lesson020-image005.jpg)')
    quote_records.append({'lesson':lesson,'start_line':start,'stop_line':stop,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_text':raw,'rendered_text':text})
    return '\n'.join('> '+line if line else '>' for line in text.splitlines())

a=f'''## Appendix A — Quotes from ChanOriginal

本附录研究“走势／走势类型”的级别、分类、延续、结束及分解，背驰与买卖只在解释结束条件所需的上下文中出现。已对本地108篇编号课程（001–108）做“走势类型、走势终完美、盘整、趋势、同级别分解、走势分解、递归”关键词扫描，再连续阅读下列核心段落及相邻正文／答疑。扫描清单见[研究证据](../../artifacts/mas/memo018-appendix-study/s6/corpus_keyword_scan.json)；这不等于逐句审阅全部课程或全部图片。

以下为本地整理本摘录，行号按本次保存的 Markdown 文件计算，不宣称已认证作者首发版本。仅移除 HTML `span` 样式标签，保留粗体、原词句及“娇注／注”；答疑分隔符 `==` 仅作显示转义。“娇注”属于整理者，未署名“注”不认定为作者原文。图为整理本所附源图的逐字节副本，图上的后加说明与作者首发图的关系尚未认证。

### A.1 — 第17课：从当下延续问题到盘整／趋势与分解定理

**作者正文与整理者夹注，连续摘录：017.md，37–65行。** 第21行先提出所有走势可分解为趋势与盘整，第29行提出“走势终完美”；下面保留由当下两难到递归中枢、完成走势类型及分解的连续论证，不把“必将完成”改写成“现在已完成”。[1]

{quote(17,37,65)}

### A.2 — 第18课：完成资格不等于延伸已经结束

**作者正文与整理者夹注，连续摘录：018.md，16–58行。** 本段保留基本名词、次级别三段须完成、绝对不重叠、延伸难点及连接级别。第46–48行的“娇注”是整理者对结束条件的解释；第50行括注亦已自署“娇注”，均不能当作作者直接定义。[2]

{quote(18,16,58)}

### A.3 — 第20课：延伸、新生、外围波动重叠与级别扩张

**作者正文与整理者夹注，连续摘录：020.md，30–72行。** 不只比较中枢核心区间，还保留外围波动不得重叠、级别延续和严格上涨／下跌关系。第64行配图已查看并原样复制：图中汇总了正文前后公式，含水印与后加标注，故称“整理本源图”，不认证为作者首发原图。图上编号4、5与第72行比较关系对应。[3]

{quote(20,30,72)}

### A.4 — 第35课：消除循环定义与连接的结合律

**作者正文与整理者夹注，连续摘录：035.md，14–28行。** 保留严格最低级别起点、逐级递归、自然时间周期的方便划分、单个走势类型与走势连接的区别，以及 `a+B+b` 的重组。原文件日期“20007”明显异常，未据此推断日期或修改源文件。[4]

{quote(35,14,28)}

### A.5 — 第38课：同级别分解是一种明确的分解规则

**作者正文与整理者夹注，连续摘录：038.md，20–30行。** 作者明确允许选定级别不定义中枢延伸、允许盘整连接，而下级仍可保留延伸口径。这是核对 CC `extend` 与 `same_level` 两条路径的必要背景，不能混用两种分解所得的中枢数量。[5]

{quote(38,20,30)}

### A.6 — 第33课答疑：为什么不是循环定义

**读者提问＋作者回复：033.md，254–258行。** 前两行标出作者与回复时间，提问保留以限定答复对象；分隔符后的粗体是本地整理本标识的作者回复。[6]

{quote(33,254,258)}

### A.7 — 第17课图例：同形外观不能替代级别确认

**作者正文与整理者夹注，连续摘录：017.md，83–91行。** 源图显示600497日线的“下跌＋盘整＋下跌”及其后上涨；图上已有蓝色解释文字，来源链未认证为作者首发图。此图只能支持原文的级别比较语境，不能当作 CC 程序运行结果。[1]

{quote(17,83,91)}

以上证据支持随后讨论定义与算法，但本次不填写001–005、不选择 TDS 的具体分解口径。尤其不能由“两中枢已出现”直接推出结束时间，不能把结构级别 `L0/L1` 直接替换成固定分钟周期，也不能忽略源文的完成／同级别／外围波动前提。

'''

b='''## Appendix B — Notes from CC's implementation

### B.1 — 实际源码、版本与三个不同的输出层次

本附录基于本机 CC 仓库的只读选定快照，Git HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，2026-11-09复制时工作区 clean；路径、SHA-256与源文件清单见[快照说明](../../references/cc_algo/local_snapshot/374268381a3e/README.md)。它不是先前网站所标的 `b1348795…` 版本，本次没有从网站说明反推当前代码，也未运行 CC 引擎。[7]

先区分三个层次：

1. `ZhongShuRelation` 与 `ZouShiCandidate` 是相邻中枢关系及最大同向结构候选；候选不判定完成。
2. `CompletedZouShi` 是 L0／L1 的生命周期对象，虽名为 Completed，列表里仍同时有 `forming` 和 `frozen`；必须读 `completion_state`。
3. `RecursiveZouShi` 由已冻结的低一级走势投影而来，当前递归接口还有限深度限制。

`engine.py:348–477` 按配置、来源与版本惰性派生并缓存。旧 Gate B 关系只在 `zhongshu_mode=extend` 下发布；`same_level` 由一次共享 `LevelBuildResult` 同时提供中枢和走势，不再让两层各自扫描一份不一致结果。[8]

### B.2 — Gate B：相邻中枢的严格关系

`zoushi.py:72–85` 依次检查四个分支，否则返回 `UNDETERMINED`。以下是实际可执行比较的最小摘录；`DD/GG` 是外围指标，`ZD/ZG` 是核心边界，不可互换。[9]

```python
if right.dd > left.gg:
    return ZhongShuRelationType.UP_TREND
if right.gg < left.dd:
    return ZhongShuRelationType.DOWN_TREND
if right.zd > left.zg and right.dd <= left.gg:
    return ZhongShuRelationType.UP_EXPANSION
if right.zg < left.zd and right.gg >= left.dd:
    return ZhongShuRelationType.DOWN_EXPANSION
```

严格外部分离才是上涨／下跌；仅核心分离而外围相交或相切落入扩张关系。边界相等不算趋势。关系 `stability` 仅由两个中枢是否均 `closed` 决定（87–93行）；这是这份输入中枢快照的稳定标记，不表示两中枢组成的整个走势已经结束。

例如左 A 为 `ZD=9,ZG=12,DD=8,GG=14`，右 B 为 `17,19,16,20`，则 `16>14`，关系为上涨；把 B 的 `DD` 单独改成14且其他几何仍有效，则上涨比较失败而 `17>12 且14<=14` 成立，变为向上扩张。这是一个明确的等号反例，不能写成“碰到边界仍算上涨”。

### B.3 — Gate B 候选：最大同向链、断开与共享转折中枢

`build_zoushi_candidates()`（227–305行）先拒绝非线段中枢、周期不匹配或 `start_ts` 非严格递增的输入；空输入返回空关系／空候选。它不负责重新验证传入中枢所有几何是否合法，须区分本函数验证与 DTO／上游前提。[9]

关系只把 `UP_TREND/DOWN_TREND` 映射为方向。连续同方向关系积成一个候选；扩张或未定关系发布左链后从右中枢重新开始，方向清空。方向反转则发布旧链，并让新链从转折中枢开始，因此两候选共享那个中枢。末尾统一发布最后一链：一中枢为 `consolidation`，至少两中枢为 `trend`，`classification_state` 为 `STRUCTURALLY_QUALIFIED`。

手工分支例：A→B为上涨，B→C为下跌时，结果是趋势候选 `(A,B,up)` 和 `(B,C,down)`，不是直接把 B 从历史中删除。若 B→C 是扩张，旧候选是 `(A,B,up)`，新候选从单独 C 开始。该例只跟踪候选层，不能用来宣称历史走势被冻结。

### B.4 — L0／L1：输入来源、连续 run 与正式中枢口径

`zoushi.py:1030–1109` 将 confirmed 笔的最长前缀适配为 L0，将 standard 配置下 frozen 线段的最长前缀适配为 L1。每个 `LevelLeg` 保留来源 ID／下标、方向、真实端点、生命周期高低点和 trace。L0/L1 是结构来源身份，`period` 是行情周期，两者不是同一字段。[9]

`build_zoushis_from_zhongshus()`（915–1028行）校验部件级别／来源一致，校验中枢来源／周期／顺序，并按下标相邻、端点时间价格相同、方向交替拆出连续 run。中枢跨 run、落在供给前缀之外或模式不匹配都会拒绝。`same_level` 兼容入口重放共享状态机只为逐对象比较正式中枢，若不相等就报错，绝不悄悄替换调用者的正式结果。

`extend` 模式在854–884行把正式部件和中枢适配给中立内核。`build_zoushi_kernel_slices()` 先检查来源位置与中枢位置唯一且有序，将全局位置映射为局部坐标；中枢的进入、核心成立、成员结束、关闭证据位置必须能解析到本 run，输出再还原全局位置（`zoushi_kernel.py:915–1009`）。这里的 `position` 是结构来源位置，不是原始 K 线下标。[10]

### B.5 — extend 内核：从单中枢活动盘整到趋势与冻结

实际状态在 `_build_local_slices()`（660–912行）中：`members` 是当前走势关联中枢，`direction` 是已获严格中枢关系证明的趋势方向，`travel_direction` 是盘整实际离开／行进方向，`next_start_position` 是下一段共享边界，`pending` 保存尚未能冻结的切分。盘整可以有行进方向，但其公开 `trend_direction` 仍为 `None`。[10]

1. 没有中枢就没有切片。首中枢初始化 `members=[first]`、趋势方向未定；普通 L0/L1 用已关闭中枢的证据部件确定离开方向。`_exit_direction()` 要求中枢 closed、有关闭证据且该部件整体严格位于核心上方／下方，光有 `CLOSED` 标签不够（214–226行）。
2. 新中枢到来时，先检查已有趋势是否在它的核心成立事件水位之前已经出现独立的反向部件证据；有就先冻结旧趋势，再用最后边界中枢与新中枢建立后继状态（683–702行）。不能回看未来确认后，把它伪装成旧时刻已经知道。
3. 当前尚非趋势时，同级外围严格分离可建立趋势；非严格关系则保留／扩展活动盘整。若旧行进与新方向冲突，新的中枢尚 open，只保留 `pending`，不把未闭中枢当冻结证据；证据具备后才分段（703–765行）。
4. 已是趋势时，同向严格关系，或边界中枢仍有同向关闭证据，都可继续吸收下一中枢；逆向关系也不一概立即终结。若需要切分而新中枢仍 open，仍先进入 `pending`；closed 后发布旧切片，并从旧极值的下一部件建立后段（767–789行）。
5. 循环结束后单独处理未决切分、没有新中枢但已有反向部件的尾部，以及仅形成候选而无确认的情况。可同时发布两个 `forming` 对象，不能仅看列表长度判历史稳定；源文“随时可完成”与这里具体何时冻结是不同证据层次。

### B.6 — 转折证据、端点、来源成员与 trace 水位是四件事

`_transition()`（374–436行）在最后中枢成员结束后找反向探测：原趋势向上时，先找一条**向上部件整体在核心下方**（`high<ZD`）；原趋势向下时反向对称。这个同旧趋势方向的失败回抽是 probe，不能把第一根向下线就当作完整确认。随后再等反方向部件终点越过 probe 起点，才产生 `source_leg` 确认证据；等待期间若旧趋势方向的结构终点严格超越旧极值，撤销转折。代码明确比较结构终点，不拿生命周期 high/low 的瞬时刷新替代它。[10]

`_make_slice()`（439–543行）按一种证据输出状态：无证据是 `FORMING`；反向中枢事件或部件证据使其 `FROZEN`，两种证据不能同时存在。趋势端点选最后边界中枢以来同方向部件的端点极值；同价时选更晚位置。`FORMING` 的来源成员延伸到当前观察尾部，即使结构端点暂时还在左边；通常 `FROZEN` 成员截到选中的旧极值，而确认事件保留为证据／trace依赖，不混作成员。

`_completed_from_kernel_slice()`（`zoushi.py:790–851`）分别映射 `source_member_ids`、`zhongshu_ids`、端点和关闭证据，并让 trace 包含实际确认所需的依赖。`CompletedZouShi`（`models.py:351–415`）检查盘整不能有趋势方向、趋势必须有方向、frozen恰好一种关闭证据、forming不能声称关闭证据；稳定 ID 锚定 `level/source_type/start_source_id`，不用末端或成员数量。[9][11]

这份 `extend` 路径允许相邻走势共享边界中枢。旧走势确认冻结后，本例的旧／新源部件才在共同价格时间点两侧分别归属；确认前不能据此断言来源成员不重叠。例如观察到L12时，旧趋势与后继盘整都仍为 `FORMING`，旧来源为L0–L12，新来源为L9–L12，L9–L12暂时重叠；这种可修订的观察范围不等于最终冻结分段。一个中枢是否 closed、一个关系是否 stable、一个走势是否 frozen、当前输入窗口是否完整，是四种不同问题。显式更改上游历史／回退重算不在“未来追加不得改历史”的自然前提内；本次没有实测任何稳定性保证。

### B.7 — 连续数值例：先有上涨结构，后确认下行切分

**性质与输入。** 以下是按函数语句逐项核对的手工例，未导入或执行 CC 代码。输入已经是连续、完成的结构部件 `L0…L13`，不是原始 OHLC；教学价格无实际品种／时间含义。仅为解释走势层，正式中枢 A、B 作为已知输入，不声称跑过中枢探测器。部件高低点取端点的 max/min；各端点按表顺序严格递增地赋予时刻，后一根起点等于前一根终点。

| 部件 | 方向与端点 | `low…high` | 作用 |
|---|---|---|---|
| L0 | 上5→14 | 5…14 | A进入证据 |
| L1 | 下14→8 | 8…14 | A核心A段 |
| L2 | 上8→12 | 8…12 | A核心B段 |
| L3 | 下12→9 | 9…12 | A核心C段，成立水位3 |
| L4 | 上9→20 | 9…20 | B进入证据 |
| L5 | 下20→16 | 16…20 | A向上关闭证据；B核心A段 |
| L6 | 上16→19 | 16…19 | B核心B段 |
| L7 | 下19→17 | 17…19 | B核心C段，成立水位7 |
| L8 | 上17→26 | 17…26 | 旧趋势同向最远结构终点 |
| L9 | 下26→22 | 22…26 | B向上关闭证据；后继走势起始部件 |
| L10 | 上22→25 | 22…25 | 未超过旧极值26 |
| L11 | 下25→13 | 13…25 | 进入B核心下方，但方向不符probe |
| L12 | 上13→15 | 13…15 | 上方向失败回抽，`high15<ZD17` |
| L13 | 下15→11 | 11…15 | `end11<probe.start13`，确认切分 |

A核心为L1–L3：`[ZD,ZG]=[9,12]`，`DD=8,GG=14`，进入位置0、核心起点1、事件3、成员尾3、关闭证据5。B核心L5–L7：`[17,19]`，`DD=16,GG=20`，进入4、事件7、成员尾7、关闭证据9。这些数字也符合 `zhongshu_phase.py:53–104` 的三段交集／隔位Z段首个离开比较；这里核对算术，不执行其相位搜索或首相位校正。[12]

上述关闭证据位置描述最终L13快照，不能原样回填较早观察水位。下表各行使用与当时输入前缀一致的中枢状态及证据：L4时A为 `OPEN`、`close_evidence=None`；到L5才可标A为 `CLOSED`、证据5。B在L7成立至L8仍为 `OPEN`、没有关闭证据，到L9才为 `CLOSED`、证据9；B成立以前不传入B。若把最终A的未来证据5传给只有L0–L4的run，坐标映射会因证据位置不在run而拒绝；它不是可用的历史输入。

| 观察水位与判断 | `members / direction` | 公开状态、端点与来源 |
|---|---|---|
| 只收到A（例如尾部L4），只有一个中枢 | `[A] / None` | 一条forming盘整；不能凭A已经成立就报完成 |
| B已成立，A已关闭；`B.DD16>A.GG14` | `[A,B] / up` | 趋势资格成立；尚无结束证据 |
| 观察到L10，B已关闭且向上；没有向上部件整体在B下方 | `[A,B] / up` | 一条forming上涨趋势，结构端点L8.end=26；来源可观察到L10 |
| L12出现：`15<17`；在L4–L12向上部件中最大终点为L8的26 | 旧 `[A,B] / up`；新 `[B] / None` | `_transition`给出start=9/probe=12/evidence=None；旧趋势与后继盘整均forming；旧来源L0–L12、新来源L9–L12，暂时重叠 |
| L13出现：下行终点11严格小于L12.start13 | 旧 `[A,B] / up`；新 `[B] / None` | 旧趋势frozen，来源L0–L8，端点5→26，证据L13；新盘整forming，来源L9–L13，端点26→11，仍共享上下文中枢B |

最后一行中，L13的证据不是旧趋势的成员；`L8.end=L9.start=26` 是共享边界，形成中后段保留B是内核的上下文关联，不意味着B的原始核心部件突然移到L9以后。旧趋势的确认时间在L13之后，而结构端点在L8；不能把两者对齐成同一事件。`ZouShiCandidate` 对这份A/B列表仍只报告上涨候选，因为它不消费L12／L13部件证据。

![手工价格路径与CC走势切分：同一部件／价格轴，旧端点在L8，L13才确认冻结，后继盘整仍形成中](memoWX_023_Chan_zoushi/cc-zoushi-manual-lifecycle.png)

图是代码推导教学图，非股票实盘和 CC 运行输出。上图画完成来源部件价格折线及核心区间，下图叠加手工走势结果；没有完整原始 OHLC，所以不画虚构蜡烛。两图共享价格刻度和来源顺序；横轴是部件端点位置，L8终点对应位置9，L13终点对应位置14。[图脚本与算术记录](../../artifacts/mas/memo018-appendix-study/s6/build_study.py)、[数值清单](../../artifacts/mas/memo018-appendix-study/s6/manual_example.json)。

**独立边界分支。** 保持L0–L12不变，将L13改为下15→14，则14不小于probe.start13，尚无确认；随后L14为上14→27，结构终点27大于旧极值26，`_transition()`撤销转折，恢复单条forming上涨趋势。这个分支在13处从未形成确认；不能先用主例的11确认冻结，再改成27并声称正常追加撤销了已冻结历史。若终点仅等于26，撤销分支的严格 `>` 不成立；若下行仅到13，确认分支的严格 `<` 也不成立。上述数值断言均由独立教学脚本核对，不是内核运行测试。

### B.8 — 相邻中枢改变与递归共享转折，不能简化为固定条数

新中枢本身也能提供冻结证据；内核先以它的核心成立事件水位限制此前部件转折的查找，再按关系与关闭状态决定吸收、切分或 `pending`。因此“再来三部件就完成”“第二中枢完成就趋势完成”均不是源码的一般分支。

递归调用额外开启 `extended_center_shared_turn=True`。`_first_departure_direction()` 根据端点首次严格离开核心确定行进；`_bootstrap_start_position()` 会在明确的连续／方向／触核心前提下保留首相位前相邻进入部件。`_consolidation_shared_turn()`（297–371行）在一个延伸中枢内维护旧方向极值与反向候选，未有确认时只给forming共享转折；确认后旧盘整freeze、新盘整继续forming，避免把整个同一延伸中枢都吞进一条走势。普通L0/L1调用不打开这个开关，不能把递归细则无条件套用到所有路径。[10]

### B.9 — same_level 是另一条共享构建路径

当前正式入口 `build_same_level_result()`（`same_level.py:2237–2282`）将连续run交给 `_reproject_segment_local()`，由 `_segment_projection_plan()` 得出的分解区间重新起中枢相位，禁止 `E+A/B/C` 穿过共享边界。它并不是对extend结果改个模式名称；中枢归属和走势结果必须来自同次状态。[13]

源码保留了分离的中心事件扫描、极值事件与活动／未决转折归约逻辑（193–713行）；当前正式输出还经局部相位重投影（2032–2234行）和一致性验证（770–916行）。只盯 `_scan_run()` 的旧活动状态解释不了最终结果。正式重投影的 `can_freeze` 要求旧段已有离开方向、后一完整相位给出相反方向的实际离开证据、左右均有中枢，且此前冻结链有效（2039–2077行）；注释明确不再“X2后固定再等两部件”。活动尾部的同价重锚、严格新极值可撤销未确认probe，但不能把形成中的反向尾部说成稳定历史。

第38课允许同级别规则下的“盘整＋盘整”，不意味着 CC 当前每个projector细节都已被作者给定。`extend` 内核中的 `direction=None` 盘整对象可能关联多个非严格中枢；它是此项目路径的工作分类，不能冒充第17课“完成走势只含一个同级别中枢”的逐字定义。是否采用某种分解／归属／冻结规则，仍是未来 TDS 的独立决定。[1][5][13]

### B.10 — 递归：从冻结走势升一级，但当前仅 depth=1

`recursive_leg_runs_from_level_result()`（`zoushi_recursion.py:291–400`）只接收匹配origin的构建结果，跳过forming走势；等价起终点价格的走势使递归run中断，不能凭枚举kind给它硬定上／下。每个成员ID必须唯一解析、按序且不跨原始连续run；方向按真实起终点价决定，高低点取来源成员的生命周期极值，保留真实来源映射与trace。[14]

同文件 `_build_run()`（136–231行）在这些已冻结走势上扫描正式递归中枢；`build_recursive_zoushis()`（670–757行）再校验origin、depth、period、mode、顺序与run边界，适配共用走势内核并开启延伸中枢共享转折。接口明确拒绝 `depth != 1` 和非 `extend` 模式。理论可以逐级递归，不等于这一版本已经实现任意深度或各种分解模式的混用。[4][14]

### B.11 — 更新方式、成本与本次验证边界

`engine.py:299–324,348–477,479–556` 使用版本命中缓存与锁保护；版本改变时对应纯函数会重新派生当前前缀，并非每根输入只花固定时间。候选层有一次相邻关系与链扫描，但trace可遍历其成员；生命周期／same_level／递归路径含多次区间扫描、切片及重投影，不能只凭“从左到右”就给所有路径宣称 `O(n)` 或摊销常数更新。保存来源IDs、依赖与输出副本也有空间成本；本次未做复杂度证明或性能测量。[8–14]

实际完成：108课程关键词扫描；上述原文连续范围对照；2张源图查看并逐字节复制；代码入口／关键分支／数据契约静态检查；手工数值算术断言、价格图生成与视觉检查；主章节保存、备份、相对链接和图片哈希检查。未执行：CC引擎／测试、网站与本机版本等价验证、真实行情端到端复现、未来追加／历史回退稳定性或正确性证明。尚需在实际算法讨论中决定采用的分解方式、完成判据、级别映射及TDS接口，不能从这份研究直接默认为已批准规格。

'''

base='../../references/cc_algo/local_snapshot/374268381a3e'
refs=f'''## References

[1] 缠中说禅. [教你炒股票17：走势终完美](../../references/chan_theory/017.md). 本地整理本，正文37–65、83–91行；图 `017/image001.jpg`。

[2] 缠中说禅. [教你炒股票18：不被面首的雏男是不完美的](../../references/chan_theory/018.md). 正文16–58行，含已标明的整理者夹注。

[3] 缠中说禅. [教你炒股票20：缠中说禅走势中枢级别扩张及第三类买卖点](../../references/chan_theory/020.md). 正文30–72行；整理本配图 `020/image005.jpg`。

[4] 缠中说禅. [教你炒股票35：给基础差的同学补补课](../../references/chan_theory/035.md). 正文14–28行；源文件日期保留原状。

[5] 缠中说禅. [教你炒股票38：走势类型连接的同级别分解](../../references/chan_theory/038.md). 正文20–30行。

[6] 缠中说禅. [教你炒股票33：走势的多义性](../../references/chan_theory/033.md). 254–258行，2007-03-02 16:17:53作者答疑及对应读者提问。

[7] CC本机选定源码快照. [README]({base}/README.md)、[文件来源与SHA-256清单]({base}/manifest.json). HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，2026-11-09保存；与[历史网站快照](../../references/cc_algo/README.md)分开。

[8] CC. [engine.py]({base}/src/cc/algo/engine.py). 299–324、348–477、479–556行：版本缓存、来源／模式入口与递归派生。

[9] CC. [zoushi.py]({base}/src/cc/algo/zoushi.py). 72–305行候选；734–1109行适配、来源与正式走势入口。

[10] CC. [zoushi_kernel.py]({base}/src/cc/algo/zoushi_kernel.py). 21–157行契约，185–436行方向／极值／转折，439–1009行切片、事件水位、共享与坐标映射。

[11] CC. [models.py]({base}/src/cc/algo/models.py). 351–415行 `CompletedZouShi`；446–666行递归与极值DTO。

[12] CC. [zhongshu_phase.py]({base}/src/cc/algo/zhongshu_phase.py). 53–104行核心交集、Z段延伸与关闭；仅用于核对教学数字，不冒充完成了相位引擎复现。

[13] CC. [same_level.py]({base}/src/cc/algo/same_level.py). 193–713行事件逻辑；770–916行结果约束；1348–2282行当前局部投影与正式构建路径。

[14] CC. [zoushi_recursion.py]({base}/src/cc/algo/zoushi_recursion.py). 136–231、291–400、670–757行，递归中枢、来源投影与 `depth=1` 走势入口。
'''

stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
backup=ROOT/'docs/memo/backups'/f'{MEMO.stem}__{stamp}.md'
with backup.open('xb') as f:f.write(OLD)
assert backup.read_bytes()==OLD
assert MEMO.read_bytes()==OLD, 'Concurrent edit detected'
MEMO.write_text(PREFIX+a+b+refs)
assert MEMO.read_text().split('## Appendix A —',1)[0].encode()==PREFIX.encode()
(HERE/'quote_manifest.json').write_text(json.dumps(quote_records,ensure_ascii=False,indent=2)+'\n')
evidence={'memo':str(MEMO.relative_to(ROOT)),'backup':str(backup.relative_to(ROOT)),'preserved_prefix_sha256':hashlib.sha256(PREFIX.encode()).hexdigest(),'quotes':len(quote_records),'source_images':2,'manual_financial_chart':1,'checks':'backup identical, original main prefix identical; quote text generated directly from recorded source ranges after disclosed span/display normalization; manual arithmetic assertions passed; all images viewed; no CC execution'}
(HERE/'checks.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(evidence,ensure_ascii=False))
