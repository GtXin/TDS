### 002.c — Helper Functions

以下7个拟议私有辅助函数沿用002.a的单路线，不新增领域类或公开接口。主过程维护Bi001S／E、Bi002、最终R、下一读取位置和实际依据；辅助函数不推进读取位置、不提交结果，也不改上游数据。正式实现的输入是确切FenxingSeries及其source_series指向的MergedKlineSeries，本节只写纯算法。

**位置约定。** `fx`为输入完整分型序列，`M=len(fx)`；`merged`为其确切合并来源，`N=len(merged)`。S、A、B、F在伪代码里都用fx中的位置引用，既不是特征ID，也不是原始K线锚点；`c(X)=fx[X].source_start+1`才是合并中心。`fx[X].price`为顶的high或底的low。闭区间`[c(X),c(Y)]`含两端；新增段`(c(B),c(F)]`不含旧B、包含新F。

#### 输入与续读前提：_validate_input

**接口：** `_validate_input(source, previous_context=None)`。

首先验证当前输入及确切来源链：合并K线有效、每对相邻high／low同向严格变化；每个分型恰为该来源的完整三根窗口、kind／price／锚点／范围一致、中心按时间严格递增；逐窗核对全部应有分型，拒绝漏报、误报和错源。复用现有来源／分型validate，不把仅检查所给分型的局部字段误当“全部完整分型”验证。输入无效即报错，空分型也先验证来源。

续读只接受由同一算法及规则版本上次正常返回、未被外部修改的可信状态；不能任意拼装一个几何上看似合法的S或缓存。另要求已读原始、合并、分型及其来源／规则上下文保持原前缀，当前序列不得缩短；原读取位置及保存端点仍指向原来的分型，前次返回状态必须一致。可以是保持同一已读前缀的新快照，不能用“价格看起来相同”代替完整来源对应，也不能只检查R涉及的端点。前缀改变报输入修订，不能静默清空或复用旧缓存；如何重算修订另行处理。

#### 同型强弱：_compare_same_kind

**接口：** `_compare_same_kind(fx, X, F) → MORE／EQUAL／LESS`。

要求F晚于X且同型。顶的price更高、底更低返回MORE；严格同价返回EQUAL，其余LESS。不设容差，不检查距离或范围。初始化仅MORE替换起点；缓存延伸中的EQUAL进入新增段检查，两阶段同价政策不同。

#### 首笔检查：_check_first

**接口：** `_check_first(merged, fx, S, F) → (ok, evidence)`。

仅用于Bi002为空且F与当前Bi001S异型的分支；所有更早完整分型已按初始化规则处理，S侧范围极值因而成立。先查`c(F)-c(S)≥4`；通过后，F为顶则要求`H_F=max(high[c(S)..c(F)])`，F为底则要求`L_F=min(low[c(S)..c(F)])`。不重复检查S侧界或两端区间关系。失败返回本次实际依据，不更换S、不删除分型；不能将本函数当成任意两个端点的通用配对器。

#### 缓存终点延伸：_check_extension

**接口：** `_check_extension(merged, fx, A, B, F) → (ok, evidence)`。

前提为旧A→B合格，F晚于B、与B同型且同价或更极端；LESS已由主过程排除，不扫描区间。若A为底、F为顶，新界为`[L_A,H_F]`；若A为顶、F为底，新界为`[L_F,H_A]`。只遍历`k=c(B)+1..c(F)`，要求每根low不低于新下界、high不高于新上界。包括此前所有未采用候选之间的K线；B未更新时不能把扫描起点移动到上一个失败候选。不重扫已合格前缀，不另查类型、距离、区间关系。失败保持原缓存，继续遍历，MORE也不触发提前停止。

#### 下一反向笔：_check_reverse

**接口：** `_check_reverse(merged, fx, B, F) → (ok, evidence)`。

仅用于F晚于B且与B异型的分支。先查中心距离至少4，再在两中心闭区间同时检查：顶端点high为范围最高、底端点low为范围最低。不能只查F的一侧，因为之前延伸失败的分型仍可能破坏B的起点界。两端区间严格关系由完整分型和两侧极值推出，不再重复检测。

#### 局部连接断言：_check_state

**接口：** `_check_state(fx, R, Bi002, Bi001S, Bi001E, next_position)`。

只检查状态关系，不重新扫描合并K线。Bi001E在一轮动作完成后必须未定；Bi002存在时其终点等于Bi001S，R非空时R末笔终点等于Bi002起点，两笔方向相反；所有保存引用、读取位置合法且位于已读前缀。Bi002为空时R应为空，允许尚无起点或只有待定起点。失败报内部状态错误；不是普通配对失败。局部断言不证明任意手造S具有初始化历史；首笔简化的起点极值保证依赖初次顺序遍历或同版本未改写的可信续读状态。

#### 按001独立验收：_validate_output

**接口：** `_validate_output(source, R, Bi002, Bi001S, Bi001E, next_position, R_before)`。

按001原六条件逐笔复核R和Bi002，不调用三个简化分支函数：时间／异型、距离、两端区间严格关系、两中心闭区间的全部high／low界都独立检查；再查各连接共享端点、方向交替、缓存与下一起点、读取位置。`R_before`是本次入口处已有R的不可变端点值副本；检查R仅在其后追加，原记录未被替换。当前批次读取位置应为M；无笔／空输入时仍检查状态一致。

R每次保存新建不可变端点对，缓存延伸使用新的端点对，不复用可变记录。验收不因末笔未完成而失败，不把Bi002加入R，不填造确认时间，也不证明所选主路线唯一或未来必能完成。

### 002.d — Pseudocode

以下为002.a的纯算法伪代码，不是已实现的BiSeries API。保存状态、依据和EOF说明均是算法记号，不据此增加memo009领域类字段。“已有R不改”约束端点值和记录内容，不阻止在R末尾追加新笔。

#### 主过程：初次处理与保持前缀的续读

```text
process(source, previous_state=None):
    若previous_state存在：
        要求它来自同一算法／规则版本的上次正常返回，且未被外部修改
        # 不接受凭价格、端点和cursor任意拼成的“续读状态”
    previous_context ← previous_state的已读来源上下文，初次为None
    _validate_input(source, previous_context)
    fx ← source.items
    merged ← source.source_series
    M ← len(fx)
    N ← len(merged)

    若previous_state不存在：                         # 2.1
        R ← 空序列
        Bi002 ← None
        Bi001S、Bi001E ← None
        next_position ← 0
        evidence ← 空
    否则：
        保留R端点值、Bi002、Bi001S／E、next_position及既有依据
        # 不再次清空或从首分型重跑；先校验保存状态和前缀一致
        _check_state(fx,R,Bi002,Bi001S,Bi001E,next_position)

    R_before ← 既有R端点对的不可变值副本

    若Bi002为空且Bi001S未定：
        要求R为空
        若next_position<M：
            Bi001S ← next_position                   # 首个可读完整分型
            next_position ← next_position+1
        # 没有完整分型时不制造起点，直接走正常EOF

    当next_position<M时重复：                        # 2.2
        F ← next_position
        next_position ← next_position+1             # 每个候选只读一次

        若Bi002为空：                               # 2.3
            若fx[F].kind=fx[Bi001S].kind：
                relation ← _compare_same_kind(fx,Bi001S,F)
                若relation=MORE：Bi001S ← F
                否则：保留当前Bi001S                 # 较弱、同价都保持旧起点
                记录实际比较
                继续下一轮

            ok,e ← _check_first(merged,fx,Bi001S,F)
            记录e
            若ok=False：继续下一轮
            Bi002 ← (旧Bi001S,F)                     # 首笔进入缓存，R仍为空
            Bi001S ← F
            Bi001E ← None
            _check_state(fx,R,Bi002,Bi001S,Bi001E,next_position)
            继续下一轮

        A,B ← Bi002                                 # 2.4，仅当前缓存的两端
        若fx[F].kind=fx[B].kind：                     # 2.5
            relation ← _compare_same_kind(fx,B,F)
            记录同型强弱
            若relation=LESS：继续下一轮               # 不扫描区间，不替换
            ok,e ← _check_extension(merged,fx,A,B,F)
            记录e
            若ok=False：继续下一轮                   # 同价／更极端失败也继续
            Bi002 ← (A,F)                            # 新建缓存端点对
            Bi001S ← F
            Bi001E ← None
        否则：                                      # 2.6
            ok,e ← _check_reverse(merged,fx,B,F)
            记录e
            若ok=False：继续下一轮
            Bi001E ← F                              # 本轮形成下一反向B→F
            R.append(新建不可变端点对(A,B))           # 只提交旧缓存当时的值
            Bi002 ← (B,Bi001E)                       # 新建缓存，不修改刚提交记录
            Bi001S ← Bi001E
            Bi001E ← None

        _check_state(fx,R,Bi002,Bi001S,Bi001E,next_position)  # 2.7

    # 以下为正常EOF，既不是分支阻塞，也不在此循环等待新数据。 2.8
    若Bi002为空：
        记录“尚无合格首笔”
        unresolved ← 全部[0,N)及待定起点（若有）
    否则：
        保留Bi002及Bi001S，不把Bi002追加到R
        first ← R首笔起点（R非空）或Bi002起点
        last ← Bi002终点
        unresolved ← [0,c(first))与[c(last)+1,N)
        # last右侧仍可有已读但未采用的分型与合并K线，全部留作未决

    _validate_output(                               # 2.9
        source,R,Bi002,Bi001S,Bi001E,next_position,R_before)
    返回R的不可变端点值副本、独立缓存Bi002、待定起点、
        next_position、未决范围、实际依据及续读所需的已读来源上下文
```

空分型输入保持起点未定，读取位置为0；只有一个完整分型时将其作为待定起点，读取位置为1，仍返回“尚无合格首笔”。先前空输入之后首次出现完整分型，也由同一入口初始化，而不跳过新起点。追加后没有新完整分型则不进入主循环，仍正常返回并更新未决范围；不反复读取EOF，不把缺少右邻K线的极值构造为F。

#### 三个分支的数值判断

```text
_check_first(merged,fx,S,F):
    i,j ← c(S),c(F)
    若j−i<4：返回(False,实际距离依据)
    若F为顶：ok ← merged[j].high=max(high[i..j])
    否则：ok ← merged[j].low=min(low[i..j])
    返回(ok,本次端点值及范围极值依据)

_check_extension(merged,fx,A,B,F):
    # 合法旧A→B、F同型且同价／更极端，均由调用阶段保证
    若F为顶：lower,upper ← merged[c(A)].low,merged[c(F)].high
    否则：lower,upper ← merged[c(F)].low,merged[c(A)].high
    lo,hi ← +∞,−∞
    对k从c(B)+1到c(F)：
        lo ← min(lo,merged[k].low)
        hi ← max(hi,merged[k].high)
    返回(lo≥lower且hi≤upper,实际新增段及两界比较依据)

_check_reverse(merged,fx,B,F):
    i,j ← c(B),c(F)
    若j−i<4：返回(False,实际距离依据)
    top,bottom ← B,F中对应的顶、底
    ok ← max(high[i..j])=merged[c(top)].high
          且min(low[i..j])=merged[c(bottom)].low
    返回(ok,实际距离及两侧范围极值依据)
```

#### 独立输出验收的顺序

```text
_validate_output(source,R,Bi002,S,E,next_position,R_before):
    要求R在入口已有记录的范围内与R_before逐项同值
    要求next_position=len(source.items)，E未定
    对R每笔及Bi002（若有）：
        要求起终点引用在同一source中、时间递增且一顶一底
        要求合并中心距离至少4
        要求H顶>H底且L底<L顶
        对两合并中心的闭区间：要求各high≤H顶且low≥L底
    按R的顺序再接上Bi002（若有）：
        要求相邻记录共享端点且方向相反
    检查缓存／S对应关系，以及无缓存时R为空
    任一不符报内部状态错误；否则返回None
```

本节主循环使用已证明的分支前提减少重复判断，验收仍直接回到001定义。配对失败只推进到下一分型；非法输入、未满足前提的续读状态或内部状态错误才报错。直接扫描范围时最坏仍为O(MN)，来源校验及多批独立复核另计；本节不以“单向读取”推断线性总时间。

### 可选的002.b阶段对照表

| 阶段 | 保存内容 | 触发更新 | 不更新的情况 |
|---|---|---|---|
| 首笔形成前 | 待定Bi001S，Bi002为空 | 同型严格更极端更新S；异型距离与F侧极值通过后缓存首笔 | 同价／较弱同型；异型不合格 |
| 缓存终点延伸 | 合法A→B，Bi001S=B | 同价／更极端F的新增段两界均通过 | 较弱F；新增段任何一界失败，均继续遍历 |
| 反向成笔 | 旧缓存与暂定下一起点B | 距离和闭范围两侧极值通过：旧A→B入R，新缓存B→F | 距离或任一侧极值失败 |
| EOF | 追加不改的R、独立Bi002或孤立起点、读取位置 | 不再读取当前批次；保留开放尾部待前缀一致的新数据 | 不强制提交缓存，不制造末端分型，不提前停止普通失败 |
