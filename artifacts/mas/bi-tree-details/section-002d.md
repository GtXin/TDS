### 002.d — Pseudocode

以下为002.a的纯算法伪代码，不是已实现的BiSeries API。保存状态、依据和EOF说明均是算法记号，不据此增加memo009领域类字段。“已有R不改”约束端点值和记录内容，不阻止在R末尾追加新笔。

#### 主过程：初次处理与保持前缀的续读

以下四个短代码块按顺序属于同一个process过程；拆块只为显示，变量和循环作用域连续。

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

```

遍历：每轮先读取并推进位置，然后选择一个分支。

```text
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

```

已有缓存时，以下内容继续处于同一遍历循环内。

```text
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

```

遍历结束后执行一次收尾，不因EOF提交缓存。

```text
    # 正常EOF；退出上面的遍历循环。                  # 2.8
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
    _check_state(source.items,R,Bi002,S,E,next_position)
    要求空分型时S未定，非空时S引用已读分型；无缓存时R为空
    任一不符报内部状态错误；否则返回None
```

本节主循环使用已证明的分支前提减少重复判断，验收仍直接回到001定义。配对失败只推进到下一分型；非法输入、未满足前提的续读状态或内部状态错误才报错。直接扫描范围时最坏仍为O(MN)，来源校验及多批独立复核另计；本节不以“单向读取”推断线性总时间。

