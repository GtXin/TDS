from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import re, json, hashlib, shutil
ROOT=Path(__file__).resolve().parents[4]
ART=ROOT/'artifacts/mas/memo018-appendix-study/s4-s5'
CORPUS=ROOT/'references/chan_theory'
SNAP='../../references/cc_algo/local_snapshot/374268381a3e'
records=[]; assets=[]

def excerpt(lesson,start,stop,memo):
    path=CORPUS/f'{lesson:03}.md'
    raw='\n'.join(path.read_text().splitlines()[start-1:stop])
    # Formatting-only normalization; wording/editor annotations are retained.
    txt=re.sub(r'</?span\b[^>]*>','',raw)
    def image(match):
        original=match.group(2); source=CORPUS/original
        target=ROOT/'docs/memo'/memo/f'lesson{lesson:03}-{source.name}'
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists(): assert target.read_bytes()==source.read_bytes()
        else: shutil.copy2(source,target)
        assert target.read_bytes()==source.read_bytes()
        assets.append({'source':str(source.relative_to(ROOT)),'copy':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'viewed':True})
        return f'![{match.group(1) or f"第{lesson}课本地整理本附图"}]({memo}/{target.name})'
    txt=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',image,txt)
    records.append({'lesson':lesson,'start':start,'stop':stop,'raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),'normalization':'span markup removed only; original image paths replaced with byte-identical companion copies'})
    return '\n'.join('> '+line if line else '>' for line in txt.splitlines())+'\n'

def save(stem,a,b,refs):
    p=ROOT/'docs/memo'/f'{stem}.md';old=p.read_bytes();before=old.decode().split('## Appendix A —')[0]
    stamp=datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y%m%d_%H%M%S_%f')
    backup=ROOT/'docs/memo/backups'/f'{stem}__{stamp}.md'
    with backup.open('xb') as f:f.write(old)
    assert backup.read_bytes()==old
    result=before+'## Appendix A — Quotes from ChanOriginal\n\n'+a+'\n## Appendix B — Notes from CC\'s implementation\n\n'+b+'\n## References\n\n'+refs
    assert p.read_bytes()==old
    p.write_text(result)
    assert p.read_bytes().decode().split('## Appendix A —')[0]==before
    return {'memo':str(p.relative_to(ROOT)),'backup':str(backup.relative_to(ROOT)),'main_sections_sha256':hashlib.sha256(before.encode()).hexdigest()}

seg='memoWX_021_Chan_xianduan'
intro='''本附录研究笔之上的线段划分，包含特征序列、两类破坏、包含边界和完成条件；不把笔数凑满直接当作完成线段。检索范围为本地108篇编号课程001–108，另有README；按“线段／特征序列／中枢／重叠”等词扫描后连续阅读下列候选段落，未逐图阅读全部课程。这里引用的是保存于本项目的带注释整理本，不宣称完成作者首发版本认证。原有“娇注”保留并属于整理者；去除HTML span样式，原文措辞与条件不改；图复制自本地来源，图内后加标注不冒充作者原话。

### A.1 — 第67课：从特征序列到两类破坏的连续论述

出处：正文16–46行。[1] 保留从方向、序列、标准化到缺口分类及其逻辑顺序的整段；其中“娇注”是整理者评价，不是作者撤回或修改原定义的证据。

'''
a= intro+excerpt(67,16,46,seg)+'''
配图缺口：该课46行说“前两个图形”，50–60行另列学习图题，但本地067.md没有图片链接，067图片目录也不存在；这里不能补造其缺失原图。后续第71课图片是独立来源，不能称为第67课遗失图片。

### A.2 — 第71课：同一序列前提、假设转折点与两侧包含

出处：正文28–62行。[2] 连续保留特殊的第一笔破坏、三笔方向未定、假设分界、第一／第二元素的缺口，以及何处可以做包含的解释。末尾三张图均来自整理本紧邻正文的配图区，已查看：第一张是四种线段情形示意，后两张是指数分钟图；不能由这些回看标记推断实时确认时刻。

'''+excerpt(71,28,62,seg)+'''
### A.3 — 第77课：至少三笔、首三笔重合与反向线段破坏

出处：正文73–99行。[3] 保留后继线段确认、第二特征序列不再递归分类的理由与80–83实例。该论证里的“线段A／B／C”在破坏关系确认前只是暂称，不能删除这项限定。

'''+excerpt(77,73,99,seg)+'''
### A.4 — 第78课：笔破坏失败、延续与标准化的适用范围

出处：正文28–74行。[4] 此段与第71课衔接，特别保留62行“线段B已经确认破坏前段”的前提，以及第二特征序列必须严格包含处理的说明。两张图含“娇注”或整理者构造解释；最后的标准化仅指把线段作为无内部结构部件用于后续分析，不是抹掉原线段来源或任意改端点。

'''+excerpt(78,28,74,seg)
b='''### B.1 — 版本、入口和输入边界

本附录按实际CC本地仓库的只读快照分析：Git HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，2026-11-09采集时工作区干净；逐文件SHA-256见清单。[5] 这不是较早网站快照 `b1348795…`，也不是TDS已采用的算法。完整执行语句保存在引用文件中；本轮只静态阅读和手工推演，没有导入或执行CC算法。

`build_xianduans()` 在少于三笔时返回空；否则规范化配置，建立一次性的 `_XianduanBuilder`，调用 `run()` 后由 `_finish()`生成对象（xianduan.py247–275行）。输入是已派生的 `Bi` 序列，笔的合法性、先后和方向交替主要由上游保证，不能把这个入口当作任意损坏笔序列的全面校验器。[6]

当前默认线段策略是standard／`LINE_ONLY`，非标准修复与震荡开关为OFF；`strong_bi`单笔成段是可选项目变体，不是第77课“至少三笔”的原文规则（config.py173–182行；xianduan.py733–763、917–930行）。`nonstandard`／`oscillation`虽传入构建器，当前初始化中保存标志、并不等于已执行全部注释所说的补齐或震荡算法；尤其oscillation明确标为TODO。[6][7]

### B.2 — 特征元素怎样生成候选

1. `_first_xianduan()`从左到右尝试起点，要求本向候选及其后的反向候选都能产生，才选定首段；此前可有暖机空白。找不到这对候选时，`_emit()`退回整窗一条forming示意，而不是保证全窗已有正式段（946–961、997–1046行）。
2. `_candidate(begin,direction)`只把反向笔送给 `_EigenFX`。每个 `_Eigen`保存高、低与其全部来源笔下标；第二元素调用`exclude_included=True`，新笔包住旧元素时可另立元素；第三元素允许合并并有相等边界特例。合并按候选段方向取高高或低低，不应与原始K线包含处理的适用场景混为一谈（281–332、374–422行）。
3. `_actual_break()`对第一特征序列使用中间元素的末个原始笔判突破，必要时查看第三元素之后的第2笔，依赖位置可能晚于几何端点。第二特征序列`GAP_REVERT`改用合并后元素的边界严格比较，且不前看。这是实际代码的两种角色，不能仅凭同名“分型”认定条件完全相同（424–456行）。
4. 顶分型比较为`e0.high < e1.high`、`e2.high <= e1.high`、`e2.low < e1.low`；底分型为`e2.high > e1.high`、`e0.low > e1.low`、`e2.low >= e1.low`。`_mark_gap()`以上升段`e0.high < e1.low`／下降段`e0.low > e1.high`作严格缺口判断，边界相等无缺口（458–477行）。这里包含非严格的一边，是CC实现口径，不把它重写成作者原句。[6]
5. 中间特征元素内的极值笔之前一笔是候选几何终点；候选至少三笔，并通过起终极值检查，才能输出。非候选则滑动／重建特征窗口继续扫描。候选带`rule`、`dep`，仍未冻结（479–507、663–693行）。

### B.3 — 候选成立之后，何时冻结、延伸或撤销

状态机维护已冻结历史、准完成`N0`与反向待确认`N1`。它是CC的动态冻结纪律，不能把N0出现就写成第67课意义之外的全部工程确认已完成（126–244、544–661行）。[6]

- 没有N0时，首候选晋升soft N0；反向候选出现后成为pending N1。原方向若又出现严格新极值且起点仍合法，会先延伸N0，不急于冻结。若反向未成段、延伸区曾越过旧起点，代码还可能走`pen_break_absorb`吸收失败笔破坏；这是带规则标签的CC分支，不能省成“只要破起点就换段”。
- 有N0和N1时，`_advance_n0n1()`先查N1能否延伸，再尝试N2。N2若已构成合法候选，冻结N0，N1升为新N0，N2成为新N1。没有N2时，必须同时有“严格破N1起点”和“后来回到N1方向创越其终点”的双证据，才作废N1并延伸N0；只见起点被破还要给N2成长机会（820–888行）。
- 若该延伸会破坏N0起点极值条件，走`rollover`：冻结旧N0、将N1升为新N0，避免把真反向吞掉。`_gate_ok()`冻结时检查笔数为奇数、至少三笔、首尾同向、首三笔闭区间重合与端点极值；`pen_break_absorb`豁免端点极值硬闸，`strong_bi`另有变体豁免（902–993行）。
- 缺口候选的额外反向证据由`_revert_confirm()`从端点后第2笔建立第二特征序列取得。若完整N2尚未形成，且证据早于／不晚于首个破坏，`gap_revert`可原子冻结前驱N0和缺口N1，并以该第二序列中间峰值建立下一soft候选；新候选不会仅因同一证据立即再冻结。第二序列只需反向分型，不递归套另一套“第二种”（220–244、632–657、765–791、881–886行）。

`_emit()`把冻结历史、soft N0、pending N1分别输出；右侧未确认部分按同向真实极值画forming。`_finish()`从来源笔聚合实际high／low、起止价格、来源时间和合并下标，写入规则、依赖和冻结标签。几何终点、读到的证据位置与冻结时刻不能互换：尤其普通N2冻结分支保留原候选`dep`，并未自动补填独立`confirmation_ts`；明确记录该时间的主要是gap_revert分支（997–1148行）。这限制了从普通对象trace重建完整确认事件时间线的能力。[6]

### B.4 — 一组连续笔的手工推演

以下为教学构造的已合法笔输入，端点按时间`P0…P16`，所有笔`Bi=[Pi,Pi+1]`、时间首尾相接、方向交替。**没有原始OHLC，不把笔区间伪画成蜡烛**。价格及来源笔下标与上面代码逐项比较；没有运行CC，不声称这些是引擎日志。这里固定standard、关闭strong_bi等变体。

端点价格：`10,18,14,22,17,20,12,16,8,13,11,17,14,21,16,20,12`。

| 进入的笔 | 起点→终点 | 方向／手工检查 |
|---|---|---|
| B0 |10→18|上；潜在首段起笔 |
| B1 |18→14|下；上段特征e0=[14,18]，来源{1} |
| B2 |14→22|上；首三笔交集[14,18] |
| B3 |22→17|下；e1=[17,22]，来源{3}，与e0无缺口 |
| B4 |17→20|上；不喂入上段反向特征 |
| B5 |20→12|下；e2=[12,20]，来源{5}；18<22、20<=22、12<17，且12<中间原笔低17，形成上候选[0,2]，终点P3=22 |
| B6 |12→16|上；反向下候选的上笔特征{4}=[17,20]、{6}=[12,16]尚未成底 |
| B7 |16→8|下；方向极值降到8 |
| B8 |8→13|上；候选底特征继续下移，尚未反向突破 |
| B9 |13→11|下；下段非特征笔 |
| B10 |11→17|上；特征{6}=[12,16]、{8}=[8,13]、{10}=[11,17]成底：17>13、12>8、11>=8；13<12为假，无缺口；下候选[3,7]，终点P8=8 |
| B11 |17→14|下；上候选从B8起，e0{9}=[11,13]、e1{11}=[14,17]先上移 |
| B12 |14→21|上；新上段极值21，未超过首段22 |
| B13 |21→16|下；序列继续上移，重排为e0{11}=[14,17]、e1{13}=[16,21] |
| B14 |16→20|上；不能仅凭一个反弹峰值决定确认 |
| B15 |20→12|下；e2{15}=[12,20]成顶：17<21、20<=21、12<16，实际突破12<16；上候选[8,12]，终点P13=21 |

内部候选`[0,2]`在读B5后已可找到，但`_first_xianduan()`还要求合法反向候选，所以截至B9的前缀并不能把它当成已选定首段；B10出现反向候选后才取得首对。以当前整组输入手工走主循环：先`N0=[0,2]↑`，再`N1=[3,7]↓`；这期间不存在超过22的新上行极值；B15给出`N2=[8,12]↑`，于是冻结[0,2]、[3,7]升soft、[8,12]为pending。后续没有足够反向候选，停止并输出forming尾部。冻结首段的几何终点在P3，证据远在B15，不能把图上P3的端点标记读成当时已知。

来源范围是本示例的笔下标闭区间：首段包含B0–B2，次段B3–B7，第三候选B8–B12；两个相邻段共享的是端点时间／价格，笔成员不重叠。B13–B15可以是确认前面结构的证据，却不是首段几何成员。CC最终trace还要依赖这些Bi自带的原始／合并K线映射；本例未构造这些上游trace，不提供虚构的raw下标。[6]

![连续笔与候选／冻结段按同一端点轴和价格轴对齐；手工代码推演](memoWX_021_Chan_xianduan/manual-segment-sequence.png)

### B.5 — 同组输入的边界对照与仍需验证的部分

- **相等不是严格击破。** pending下段N1起点关键价22，后来的high=22不触发`is_n1_broken`；22.1才满足`>22`。但严格破坏本身仍不能跳过B.3所述N2／双证据裁决。这是辅助条件演示，不声称从一个数值就得到完整段输出。
- **缺口替代分支。** 另取六笔端点`10,18,14,24,19,22,16`，特征区间为[14,18]、[19,24]、[16,22]，顶形与实际突破成立，18<19有缺口，产生`rule=gap`候选，其几何终点在B2。只有这六笔并不能取得足够反向证据，也不能冻结。若把中间低点改为18，则18<18为假，只说明缺口标志改变；后续确认仍须继续处理，而不是其他规则一概豁免。
- **包含与第二序列不能省略。** 第三特征元素落入中间元素时会合并并等待更多输入；`GAP_REVERT`的严格比较使用合并后边界，不能用末个原始笔或PRIMARY前看偷换。当前只给出了可核对的主序列、相等／缺口补充；复杂的包含、失败吸收、原子缺口冻结和全部变体尚未运行覆盖。
- **复杂度与稳定性。** 入口每次重新构造状态，并非跨调用增量引擎；`_first_xianduan`逐起点重扫、候选查找／滑窗重放／极值检查都有嵌套扫描，不能宣称整层严格O(n)。冻结区“不回改”是一次状态机在正常后续生长下的工程约束；替换上游笔、改变历史或配置后重新调用，不应保证输出仍相同。原文定义、CC项目豁免与TDS未来算法仍须分别评议。
'''
refs='''[1] 缠中说禅. [教你炒股票67：线段的划分标准](../../references/chan_theory/067.md)，正文16–46行；整理本图目50–60行存在，图文件缺失。

[2] 缠中说禅. [教你炒股票71：线段划分标准的再分辨](../../references/chan_theory/071.md)，2007-08-16，正文28–62行及相邻配图。

[3] 缠中说禅. [教你炒股票77：一些概念的再分辨](../../references/chan_theory/077.md)，2007-09-05，正文73–99行。

[4] 缠中说禅. [教你炒股票78：继续说线段的划分](../../references/chan_theory/078.md)，2007-09-06，正文28–74行；带“娇注”与学习者图解的本地整理本。

[5] [CC源码快照说明](../../references/cc_algo/local_snapshot/374268381a3e/README.md)与[文件清单／SHA-256](../../references/cc_algo/local_snapshot/374268381a3e/manifest.json)，HEAD374268381a3eaeee4d220e67d63364b3907405f4，2026-11-09采集。

[6] [CC xianduan.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/xianduan.py)，关键函数及行号见B.1–B.5；完整文件保留供复查。

[7] [CC config.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/config.py)，173–182行默认线段策略与中枢模式。
'''
saved=[save(seg,a,b,refs)]

center='memoWX_022_Chan_zhongshu'
a='''本附录关注中枢成立、核心区间、延伸／扩展的区分及来源级别。对本地108篇编号课程001–108做整库关键词扫描，再对下列定义及补充段落连续核读；README不计作课程，检索命中不等于逐图读完全部原文。引文来自带整理者注释的本地资料，非首发版认证；“娇注”或“注”均按整理文字看待，不直接归给作者。去除HTML span样式，保留原有文字、公式写法与夹注，不擅自把整理者补出的公式参数改成作者原话。

### A.1 — 第17课：递归定义及最低不可分级别

出处：正文45–65行。[1] 从至少三个连续次级别走势类型的重叠，一直保留最低级别例外、盘整／趋势与分解定理，避免把三个普通波动机械等同于严格中枢。这里引用的“原理／定理”是作者论述，不在此附录另作正确性证明。

'''+excerpt(17,45,65,center)+'''
### A.2 — 第18课：完成条件、延伸、维持与破坏的连续论述

出处：正文24–66行。[2] 本段把“次级别前三段都是完成的”放在公式旁；达到最小结构并不等于马上结束，维持与破坏还涉及离开／返回走势的级别。保留作者的类比及原文条件，夹注保留但不作为作者追加定理。

'''+excerpt(18,24,66,center)+'''
### A.3 — 第20课：延伸、扩展与固定中心区间

出处：正文28–74行。[3] 28行独立“注”归属未明，36行等多处“娇注”属于整理者。连续引用区间保留两种后续情形、扩展需满足的重叠、ZG／ZD／GG／DD和中心定理，不把“延伸”改写成核心区间不断取所有成员交集。末尾第三类买卖点定理仅作中枢破坏的邻接语境，具体买卖研究见memo025。

第64行所附image005已查看：含回调／回升、延伸与两个中枢关系示意，并带六项指标说明和网站水印；图内符号说明不据此认定为作者首发图版。该图按本地整理本原样保留。

'''+excerpt(20,28,74,center)+'''
### A.4 — 第20课答疑：日线／30分钟／5分钟的三层对应

出处：读者提问278–284行与作者回复286行，连同附图至292行。[3] 提问中的“低点不升破ZD”是读者转引的表述，不能拿来替换正文第三类卖点的“高点”；作者答复的重点是次级别完成所需的再次级别结构。两张附图均已查看，分别为带解说的30分钟与5分钟工行图。

'''+excerpt(20,278,292,center)+'''
### A.5 — 第28课答疑：连接中枢与完成走势类型不是同一对象

出处：读者问题294行、作者回复298行。[4] 保留提问和答复，避免把连接的低级别走势与包含中枢的整个走势类型混在一起；其中问题里的“娇注”仍为整理者。

'''+excerpt(28,294,298,center)
b='''### B.1 — 版本、来源部件与两个入口

使用实际CC本地源码的只读快照，HEAD `374268381a3eaeee4d220e67d63364b3907405f4`，采集于2026-11-09且工作区干净；原路径及逐文件哈希见清单。[5] 与网站历史版本不同，不把网站旧结果数量当成本版本的运行证据。本轮没有导入或运行CC代码；下面的数字是手工沿执行分支推演，不是引擎测试。

`ZsLeg`是笔／线段投影后的统一输入，只在构造时检查low不得大于high。`legs_from_bis()`取最长confirmed笔前缀；`legs_from_xianduans()`只允许standard配置下从开头连续的frozen线段，遇到没有冻结trace的第一项就停，不是筛出后面零散所有已冻结项（zhongshu.py44–110行）。调用者还要明确这些基础部件与严格原文“已完成次级别走势类型”的层级对应；一个几何段中枢不能自动升级为任意时间级别的理论中枢。[6]

`build_zhongshus()`默认`mode=EXTEND`，并以时间首尾相接、方向交替切成连续run，不跨空洞拼接。`SAME_LEVEL`则直接转到`build_same_level_level_result()`，进一步调用共享`same_level.build_same_level_result()`，不是调用文件中仍保留的旧`_build_same_level_run()`；所以不能按那个旧辅助函数的“无延伸”说明描述当前正式同级入口（382–493行）。[6][8]

### B.2 — EXTEND模式怎样找核心和延伸

1. `_build_run()`从候选进入部件E开始，调用`scan_zhongshu_candidate()`。至少要有E+A/B/C四个部件；方向相邻交替，A/B/C的`ZD=max(low)`不得大于`ZG=min(high)`，且E必须触及核心闭区间。E是成立证据，不计入核心成员。闭区间比较包含等号，相切也算重叠（zhongshu.py298–325；zhongshu_phase.py47–72行）。[6][7]
2. 核心确定后，`ZD/ZG`不随延伸收缩。只检查与A/C同向的后续Z部件：从E之后第5项开始，每次加2；若Z仍与核心重叠，连同前一条连接部件一起加入延伸成员，`GG=max(原GG,Z.high)`、`DD=min(原DD,Z.low)`。外围边界来自同向Z，不是无差别取所有部件的极值（zhongshu_phase.py74–93行）。
3. 某Z全在核心上方或下方时，记作关闭证据并停止，`exit_direction`按价格位置判定。失败Z及其前一连接部件不加入已接受成员；`end_index`仍停在此前最后成员，`close_index`可以更晚。若还未有离开证据，中心是OPEN并停在run末尾（同文件79–108；zhongshu.py327–368行）。
4. 连续run的第一个候选若关闭方向与E方向相反，`resolve_initial_zhongshu_phase()`还会检查右移一项的候选；只有右移候选也已同向关闭且E方向与离开相符，才改用右移相位。开放候选保留最早合法相位；已有前中枢约束的后续中心不再回用这项初始修正。它是CC处理有限左侧历史的项目选择，不是原文初始化定理（zhongshu_phase.py105–128行）。
5. 关闭后，从证据前j−1／j−2选择与价格离开方向一致的下一E，并约束后续E方向，继续找新核心。这样相邻中心可以通过进入证据或连接结构衔接，但不把关闭证据直接偷算进旧中心（zhongshu.py118–130、370–379行）。[6][7]

### B.3 — 当前SAME_LEVEL路径与中枢／走势生命周期

此路径先把输入适配成`LevelLeg`，由共享返回值一次交出中枢与走势；source_type=BI对应L0，XIANDUAN对应L1。空输入返回空结果；非空结果还要检查输入统一level/source_type，不连续来源下标／时间／方向另起run（zhongshu.py433–490；same_level.py100–105、2237–2282行）。[6][8]

`same_level._scan_center_events()`供分解状态机逐前缀产生几何事件，不能让未来延伸改写过去分界；最终公开中心在`_segment_projection_plan()`确定的各单独走势区间里，用`_scan_extended_center_events()`重新扫描。此时E+A/B/C不得跨分解边界；它同样能保存`extended_positions`，因此当前“SAME_LEVEL”不等于所有中心永远恰好三成员（same_level.py193–285、1348–2030、2032–2045行）。

`_reproject_segment_local()`把中枢关闭与走势冻结分开：已提交区间内，只有中心自己的正式离开证据`core.close_position`才关闭中心；不能仅凭后面走势的反向冻结事件顺带把它关掉。仍在可撤销分界右侧的中心也不能提早发布不可回写的CLOSED。`_build_centers()`保留进入证据、核心三ID、延伸ID、成员数、几何末端和单独关闭证据，trace依赖到确认所需的部件（same_level.py928–994、2032–2123行）。本节仅列出中枢相关公共路径与边界；共享分解器完整走势裁决见memo023，而非用中心片段代替整层走势分析。[8]

### B.4 — 一个E+A/B/C及延伸到关闭的连续手工例子

固定输入为**已经正式完成、可按source_index=0…7顺序投影的同一级基础部件**，方向交替，端点时间记为T0…T8。这里以EXTEND模式说明扫描；这些是教学构造部件，没有原始K线OHLC，图用价格折线和区间，不伪画成蜡烛。并不声称该构造满足原文全部递归级别认定，更不是CC实际运行结果。[6][7]

端点价格：`10,18,12,16,13,19,14,22,18`。

| 下标／角色 | 起点→终点；[low,high] | 比较、状态及来源 |
|---|---|---|
| 0 E |10→18；[10,18]，向上|进入证据，非成员 |
| 1 A |18→12；[12,18]，向下|尚不足三个核心部件 |
| 2 B |12→16；[12,16]，向上|仍未有完整A/B/C |
| 3 C=Z2 |16→13；[13,16]，向下|ZD=max(12,12,13)=13；ZG=min(18,16,16)=16；E触及[13,16]，成立；成员{1,2,3}，GG=max(18,16)=18，DD=min(12,13)=12，OPEN |
| 4 连接部件 |13→19；[13,19]，向上|不是下一条同向Z；须等5，暂不单独决定延伸 |
| 5 Z3 |19→14；[14,19]，向下|max(14,13)=14<=min(19,16)=16，重叠；一起加入{4,5}；核心仍[13,16]，GG=19、DD=12，OPEN |
| 6 连接部件 |14→22；[14,22]，向上|尚待7裁决，不能仅凭其碰到核心就永远接受 |
| 7 Z4 |22→18；[18,22]，向下|max(18,13)=18>min(22,16)=16，不重叠；18>ZG，关闭方向up；close_index=7，成员仍{1,2,3,4,5}，end_index=5，CLOSED |

E的方向up与关闭方向up一致，初始相位修正立即保留原候选，不偷偷右移A/B/C。进入证据0和关闭证据7与成员{1…5}明确分开：几何起点A.start=T1，core_end=C.end=T4，几何终点=T6，关闭证据到T8。`_restart_index()`看j−1=6，该连接部件向上，故选择6作为下一候选E；当前数据只剩6、7，不够四部件，扫描结束。此时来源／依赖区间可能覆盖T0…T8，却不表示所有这些输入都是旧中心成员。[6][7]

![同一价格与端点轴：部件输入、核心固定、延伸成员与关闭证据；手工代码推演](memoWX_022_Chan_zhongshu/manual-center-sequence.png)

### B.5 — 相切、断链、更新与解释边界

- **相切替代例。** 仅把主序列最后端点由18改为16，则Z4=[16,22]与核心在16相切；`max(16,13)<=min(22,16)`成立，加入{6,7}，中心保持OPEN，GG更新22、DD仍12，核心仍[13,16]。不能把`<=`口头改成“必须有正宽度”。
- **零宽核心也被接受。** 另取E:10→20、A:20→16、B:16→22、C:22→20，连续反向部件得到ZD=ZG=20；代码只排除ZD>ZG，E也触及20，故几何候选有效。是否将点中枢作为TDS正式约定，需另议，不能因CC支持就写入主定义。
- **输入断开。** EXTEND入口发现前项end_ts不等于后项start_ts或方向未交替，会切断run；SAME_LEVEL还要求source_index连续。`ZsLeg`仅检查high/low而不是整套时间／价格校验，不能泛称所有坏输入都会报错。
- **尾部更新与稳定性。** 所取笔／线段最长确认前缀限制了形成中的上游结构污染；然而构建函数是对输入快照重新扫描，OPEN中心可随新证据增成员或初始相位修正。id由source_type、核心起点时间与C结束时间锚定，延伸本身不换id；相位改变可换核心与id（models.py239–244行）。输入历史修订、参数变化或重建并不在“冻结历史不改”的无条件保证内。[9]
- **范围与成本。** 默认EXTEND核心扫描逐候选、每候选可再次向后扫描延伸，另有相位试探；同级共享分解器还有区间重投影和检查，不能从单个while声称整层O(n)。源码头部“后续PR”的旧注释也不能盖过现在实际存在的分支：本节已区分两种路径；它们并未在本层自动实现原文所有高级别扩展、背驰或买卖点。[6][8]
'''
refs='''[1] 缠中说禅. [教你炒股票17：走势终完美](../../references/chan_theory/017.md)，正文45–65行。

[2] 缠中说禅. [教你炒股票18：不被面首的雏男是不完美的。](../../references/chan_theory/018.md)，2006-12-26，正文24–66行。

[3] 缠中说禅. [教你炒股票20：缠中说禅走势中枢级别扩张及第三类买卖点](../../references/chan_theory/020.md)，2007-01-05，正文28–74行；读者问题／作者回复278–292行。整理本图片保留后加说明，不宣称首发图版认证。

[4] 缠中说禅. [教你炒股票28：下一目标：摧毁基金](../../references/chan_theory/028.md)，答疑294–298行。

[5] [CC源码快照说明](../../references/cc_algo/local_snapshot/374268381a3e/README.md)与[文件／哈希清单](../../references/cc_algo/local_snapshot/374268381a3e/manifest.json)，HEAD374268381a3eaeee4d220e67d63364b3907405f4，2026-11-09采集。

[6] [CC zhongshu.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/zhongshu.py)，输入投影44–110、默认扫描298–430、同级入口433–490行。

[7] [CC zhongshu_phase.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/zhongshu_phase.py)，49–128行：共享候选扫描和初始相位选择。

[8] [CC same_level.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/same_level.py)，193–285、928–994、1348–2123、2237–2282行；本节关注中枢投影与生命周期，完整走势分析见memo023。

[9] [CC models.py](../../references/cc_algo/local_snapshot/374268381a3e/src/cc/algo/models.py)，中枢记录与稳定id定义210–244行。
'''
saved.append(save(center,a,b,refs))
(ART/'evidence.json').write_text(json.dumps({'saved':saved,'quote_selections':records,'original_figures':assets,'corpus_numbered_lessons':108,'scan_hits_file':'corpus_hits.txt','cc_execution':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(saved,ensure_ascii=False))
