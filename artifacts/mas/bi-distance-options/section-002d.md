### 002.d — Pseudocode

以下是纯算法伪代码。`process`返回002.a中完整的Q，下一次直接把Q作为previous_state传入。所有端点引用均为源FX位置；区间运算才使用合并中心c(X)。保存来源、依据和快照都是普通数据操作，不代表已经实现BiSeries续读接口。

#### 主过程

```text
process(source, distance_mode=None, previous_state=None):
    _validate_input(source, previous_state)           # 2.1，先验来源再看M
    mode,min_gap ← _resolve_distance_mode(distance_mode,previous_state)
    fx,merged ← source.items,source.source_series
    M,N ← len(fx),len(merged)
    若previous_state为None：
        R ← 空序列；Bi002、S、E ← None；next_position ← 0
        evidence ← 空序列
    否则：
        从previous_state复制端点值与标量；R、evidence转为新的可追加工作序列
        恢复Bi002、S、E、next_position，保持端点值不可变
        # 原Q不变；不恢复旧unresolved作为新结果，不清空R
    R_before ← R的不可变端点值副本

    若S未定且next_position<M：
        S ← next_position；next_position ← next_position+1
        evidence追加该FX的初始化依据

    当next_position<M时重复：                        # 2.2
        F ← next_position；next_position ← next_position+1
        cache_changed ← False
        若Bi002为空：                               # 2.3
            若fx[F].kind=fx[S].kind：
                relation ← _compare_same_kind(fx,S,F)
                e ← 本次同型比较及原S的依据
                若relation=MORE：S ← F
                # LESS、EQUAL保留旧S
            否则：
                ok,e ← _check_first(merged,fx,S,F,min_gap)
                若ok：
                    Bi002 ← (旧S,F)；S ← F；E ← None
                    cache_changed ← True
        否则：
            A,B ← Bi002                             # 2.4
            若fx[F].kind=fx[B].kind：                # 2.5
                relation ← _compare_same_kind(fx,B,F)
                若relation=LESS：
                    e ← 本次较弱比较依据             # 不扫描区间
                否则：
                    ok,e ← _check_extension(merged,fx,A,B,F)
                    若ok：
                        Bi002 ← (A,F)；S ← F；E ← None
                        cache_changed ← True
            否则：                                  # 2.6
                ok,e ← _check_reverse(merged,fx,B,F,min_gap)
                若ok：
                    E ← F
                    R追加新建不可变端点值(A,B)       # 只提交旧缓存
                    Bi002 ← (B,E)；S ← E；E ← None
                    cache_changed ← True
        evidence追加本轮F的一条完整依据e             # 成功／失败都只记一次
        若cache_changed：
            _check_state(fx,R,Bi002,S,E,next_position) # 2.7
        # 任一普通失败均继续下一轮；不终止或回退

    若Bi002为空：                                   # 2.8
        unresolved ← [0,N)
    否则：
        first ← R首笔起点（R非空）或Bi002起点
        last ← Bi002终点
        unresolved ← [0,c(first))与[c(last)+1,N)，省略空范围
    # EOF不提交缓存，也不向evidence反复添加EOF说明
    Q ← 以下各项的独立不可变快照：
        R、Bi002、Bi001S=S、Bi001E=E、next_position、evidence、unresolved，
        source_context=当前整个输入及完整来源／长度／稳定上下文，
                       包括distance_mode=mode及min_gap=min_gap
    _validate_output(source,Q,R_before,mode,min_gap) # 2.9
    返回Q
```

第一次仅有0个FX时S未定、位置为0；仅有1个FX时S为FX0、位置为1。以后首次出现完整分型仍由同一入口初始化，随后进入正常循环。EOF的“尚无首笔／存在未提交末笔”展示信息由Q现算，不是持久判断事件。

#### 距离档位解析

```text
_resolve_distance_mode(distance_mode,previous_state=None):
    mapping ← {"strong":4,"weak":3}
    若distance_mode不是None且不是上述两个字符串之一：报错
    若previous_state为None：
        mode ← "strong"（省略时）或distance_mode
    否则：
        要求旧Q.source_context显式保存distance_mode和min_gap
        old_mode ← previous_state.source_context.distance_mode
        old_gap ← previous_state.source_context.min_gap
        若old_mode非法或old_gap≠mapping[old_mode]：报错
        mode ← old_mode（省略时）或distance_mode
        若mode≠old_mode：报错，不能在旧Q上改档
    min_gap ← mapping[mode]
    返回(mode,min_gap)
```

#### 三个分支的数值判断

```text
_check_first(merged,fx,S,F,min_gap):
    i,j ← c(S),c(F)
    若j−i<min_gap：返回(False,实际中心距与本档门槛依据)
    若F为顶：ok ← merged[j].high=max(high[i..j])
    否则：ok ← merged[j].low=min(low[i..j])
    返回(ok,实际中心距、min_gap及F侧范围极值依据)

_check_extension(merged,fx,A,B,F):
    # 旧A→B合格，F同型且同价／更极端，均由调用阶段保证
    若F为顶：lower,upper ← merged[c(A)].low,merged[c(F)].high
    否则：lower,upper ← merged[c(F)].low,merged[c(A)].high
    lo,hi ← +∞,−∞
    对k从c(B)+1到c(F)：
        lo ← min(lo,merged[k].low)
        hi ← max(hi,merged[k].high)
    返回(lo≥lower且hi≤upper,实际新增段及两界比较依据)

_check_reverse(merged,fx,B,F,min_gap):
    i,j ← c(B),c(F)
    若j−i<min_gap：返回(False,实际中心距与本档门槛依据)
    top,bottom ← B,F中对应的顶、底
    ok ← max(high[i..j])=merged[c(top)].high
          且min(low[i..j])=merged[c(bottom)].low
    返回(ok,实际中心距、min_gap及两侧范围极值依据)
```

#### 独立验收

```text
_validate_output(source,Q,R_before,mode,min_gap):
    要求mode合法，min_gap={"strong":4,"weak":3}[mode]
    要求Q.source_context.distance_mode=mode且Q.source_context.min_gap=min_gap
    要求len(Q.R)≥len(R_before)，且原有前缀逐项同值
    要求Q.next_position=len(source.items)，Q.Bi001E=None
    对Q.R每笔及Q.Bi002（若有）：
        要求同源引用、时间递增、一顶一底、中心距离至少min_gap
        要求H顶>H底且L底<L顶
        对两中心闭区间：要求每根high≤H顶且low≥L底
    按Q.R再接Q.Bi002的顺序，检查共享端点与交替方向
    _check_state(source.items,Q.R,Q.Bi002,Q.Bi001S,Q.Bi001E,Q.next_position)
    检查Q的来源上下文、未决范围及每个已读FX恰有一条真实依据
    要求len(source.items)=0时Q.Bi001S=None，否则Q.Bi001S引用已读FX
    要求Q.Bi002为空时Q.R为空
    任一不符报内部状态错误；否则返回None
```

直接反复扫描配对范围时最坏仍为`O(MN)`；输入来源校验、累计依据和多批完整复核的成本另计。单向读FX不意味着整个流程线性，也不意味着只需常量总存储。

