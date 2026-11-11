### 002.c — Helper Functions

以下6个拟议私有辅助函数服务于002.a的候选搜索，不新增领域类，不修改上游数据。入口复用确切`FenxingSeries.validate()`；主过程负责读入位置、备选栈、依据记录与报告组装。多条候选路线不能平铺为同一条`BiSeries.items`；本阶段返回普通研究报告，尚不定义正式`BiSeries.derive_from()`的多解返回接口。

**位置与工作状态。** `source`是本次确切FenxingSeries，`fx=source.items`，`merged=source.source_series`，`M=len(fx)`。A、B、F和路线中的端点均为`fx`的零基位置，不是特征ID、合并K线位置或原始锚点；`c(p)=fx[p].source_start+1`才是合并中心。`prefix`为已有连接的端点元组，其最后一项恒为A；当前工作笔A→B尚未追加到prefix。`cursor`为下一未读分型位置，可等于M表示耗尽。分支保存确切source引用、prefix、A/B、阶段和cursor；这些仅是算法工作数据。

#### 检查完整配对：_check_pair

**接口：** `_check_pair(source, a, b) → (ok, reasons)`。

端点必须是当前source中的合法位置；位置越界或误传ID报错。按002.a的“合格”定义，依次检查时间／类型、`c(b)-c(a)≥4`、两中心区间关系，以及闭区间`[c(a),c(b)]`内全部合并K线的高低界。返回布尔结果及本次实际失败依据；同型或逆序先返回不合格，不能用无意义的方向继续判断。函数不选端点、不推进cursor、不修改分型，也不重跑合并。

#### 比较同型终点：_compare_end

**接口：** `_compare_end(source, b, f) → MORE／EQUAL／LESS`。

要求F晚于B且两者同型。顶比较端点price，较高为MORE；底较低为MORE；严格相等为EQUAL，其余LESS。输入先由source校验保证price与中心高／低一致；不使用原始锚点时间先后代替价格，不设容差。这只决定进入哪条分支，不代替A→F的完整检查。

#### 冻结备选状态：_freeze_branch

**接口：** `_freeze_branch(source, prefix, a, b, cursor) → snapshot`。

保留确切source引用；把路径复制为不可变元组，保存A/B、阶段及下一未读cursor，形成不可变快照，再调用`_validate_branch`。B为空对应SEEK_B，否则WAIT_REVERSE。source本身是不可变输入，保持同一引用，不复制成另一数据版本。调用方随后改变临时列表，不得影响快照；不同分支允许共享不可变值，不共享可变路径。

缓存的是**作出不同选择之后的状态**：首次B备选已经拒绝本次F，故保存B为空及F之后的cursor；同价备选已经改取B=F，也保存F之后的cursor。恢复时不重新生成同一次选择。

#### 校验恢复分支：_validate_branch

**接口：** `_validate_branch(source, snapshot) → None`。

检查snapshot.source与source为同一对象；prefix是非空不可变端点元组且最后一项为A，每项在当前fx范围内，已有各连接重新通过`_check_pair`。SEEK_B时B为空，prefix仅含当前初始A；WAIT_REVERSE时A→B必须合格。cursor为整数，满足`A<cursor≤M`或`B<cursor≤M`，分别对应两阶段；阶段、A/B和路径不一致时报错，不排序、不修补，也不从别的source恢复。

这验证工作状态的结构与几何不变量；时序选择是否符合“必须延伸／首个合格C”，由主过程按输入顺序执行，并用独立递归参考交叉核对，不能声称仅靠几何校验就证明整个协议。

#### 按原因收尾：_finish_branch

**接口：** `_finish_branch(source, snapshot, reason, F=None, reasons=()) → ordinary_data`。

先校验快照，再区分原因。EOF必须有`cursor=M`：B存在时，保存`prefix+(B,)`为候选路线，最后A→B明确标暂定；头部未覆盖范围为`[0,c(first))`，尾部为`[c(B)+1,N)`，均按合并位置计。B不存在时仅保存孤立起点及未决范围，不构造笔。BLOCKED要求F是刚读过的更极端同型分型，且A→F确实不合格；只保存原历史有效连接、原工作对和失败依据，不产生可行路线。

EOF候选可以带有B之后的未决波动，甚至已有合并K线突破B而尚无新完整同型分型；可以记录该事实，但不得据此制造分型或自动确认笔。该报告标记不是对`Bi.status`／`confirmed_at`字段的新定义。

#### 复核候选路线：_validate_candidates

**接口：** `_validate_candidates(source, candidates) → None`。

逐条检查确切来源、至少两个端点、严格时间顺序、全部配对、共享端点和方向交替；最后暂定工作对必须等于路线末两项，未决范围与合并中心一致。候选端点序列完全相同者应已去重，不允许BLOCKED历史混入候选。成功返回None，失败报错；不替用户选定唯一结果，也不改变原Fenxing的状态／锚点。

若后续确定单一路线，其中每个相邻端点对可沿memo009的8字段Bi表达：起止引用仍是该确切FenxingSeries中的位置，价格取对应分型price，方向取一顶一底的先后，ID属于该路线结果；确认字段另按正式规则处理。BiSeries仍保留memo009的6字段，不因当前多解研究报告增加字段或额外类。

### 002.d — Pseudocode

以下为002.a的算法伪代码，不是已实现的生产API。`search(source)`返回普通报告；`记录依据`表示本轮真实比较、来源和选择，不在此新定义DecisionStep字段。全部价格判断使用同一输入精度。

#### 主过程与实际缓存恢复

```text
search(source):
    若source不是完整FenxingSeries：报错
    source.validate()
    fx ← source.items
    merged ← source.source_series
    M ← len(fx)
    N ← len(merged)
    pending、candidates、blocked、unresolved、evidence ← 独立空列表

    若M=0：记录整个[0,N)为未决范围
    对a从M−1递减到0：
        pending.push(_freeze_branch(source, (a,), a, None, a+1))
        # 反序入栈，最早初始起点先执行

    当pending不为空时重复：
        snapshot ← pending.pop()             # 最近未执行备选先恢复
        _validate_branch(source, snapshot)
        prefix,A,B,cursor ← snapshot的对应值
        dead ← False
        记录恢复来源、完整路径与下一未读位置

        当cursor<M时重复：
            F ← cursor
            cursor ← cursor+1                # 先移到F之后，再缓存不同选择

            若B为None：
                ok,reasons ← _check_pair(source,A,F)
                若ok：
                    pending.push(_freeze_branch(
                        source,prefix,A,None,cursor))
                        # 此备选已经拒绝本次F；恢复后从下一分型继续找B
                    B ← F
                    记录找到暂定B；保留A，不追加prefix、不确认
                否则：记录F及失败依据

            否则若fx[F].kind=fx[B].kind：
                relation ← _compare_end(source,B,F)
                若relation=MORE：
                    ok,reasons ← _check_pair(source,A,F)
                    若ok：
                        记录旧B与延伸依据
                        B ← F                # 必须更新，不留沿用旧B的备选
                    否则：
                        snapshot ← _freeze_branch(source,prefix,A,B,cursor)
                        blocked.append(_finish_branch(
                            source,snapshot,BLOCKED,F,reasons))
                        dead ← True
                        跳出本分支扫描        # 回到pending恢复更早选择
                否则若relation=EQUAL：
                    ok,reasons ← _check_pair(source,A,F)
                    若ok：
                        pending.push(_freeze_branch(
                            source,prefix,A,F,cursor))
                            # 此备选已经选择同价新B=F
                    记录同价比较；当前保持旧B
                否则：记录较弱F，当前B不变

            否则：
                ok,reasons ← _check_pair(source,B,F)
                若ok：
                    记录本工作状态首个合格反向C=F及路径检查点
                    prefix ← prefix+(B,)
                    A,B ← 旧B,F              # 同时赋值；新B仍可延伸
                否则：记录F及相对B的失败依据

            _validate_branch(source,
                _freeze_branch(source,prefix,A,B,cursor))

        若dead=False：
            outcome ← _finish_branch(source,
                _freeze_branch(source,prefix,A,B,cursor),EOF)
            若outcome是候选：candidates.append(outcome)
            否则：unresolved.append(outcome)
        # 当前分支已收尾；外层while取最近备选。没有任何裸goto跳过恢复。

    按同一source内的完整端点位置元组去除重复候选
    _validate_candidates(source,candidates)
    按首末端点位置分组：一条标单解，多条全部保留标多解
    返回来源、候选／分组、末笔暂定信息、未决范围、blocked及实际依据
    # 无候选时返回相应说明；BLOCKED历史不充当候选路线
```

#### 完整配对与状态校验

```text
_check_pair(source,a,b):
    检查a,b确为当前fx范围内的整数位置；越界则报错
    i,j ← fx[a].source_start+1, fx[b].source_start+1
    若a≥b或i≥j：返回(False, 时间逆序依据)
    若fx[a]与fx[b]同型：返回(False, 同型依据)
    定位顶中心T与底中心D
    reasons ← 空
    若j−i<4：记录距离失败
    若H_T≤H_D或L_D≥L_T：记录端点区间失败
    对k从i到j（含两端）：
        若merged[k].high>H_T：记录范围最高点失败
        若merged[k].low<L_D：记录范围最低点失败
    返回(reasons为空, reasons的不可变副本)

_compare_end(source,b,f):
    检查f晚于b且同型；否则报错
    若fx[f].price=fx[b].price：返回EQUAL
    若同为顶：较高返回MORE，其余LESS
    若同为底：较低返回MORE，其余LESS

_freeze_branch(source,prefix,a,b,cursor):
    snapshot ← 包含同一source、tuple(prefix)、a、b、阶段及cursor的不可变数据
    _validate_branch(source,snapshot)
    返回snapshot

_validate_branch(source,snapshot):
    检查source对象身份、阶段、端点／cursor整数范围
    检查prefix为非空元组且末项=A
    对prefix每个相邻端点对：要求_check_pair通过
    若B为空：要求阶段SEEK_B、prefix=(A,)、A<cursor≤M
    否则：要求阶段WAIT_REVERSE、_check_pair(A,B)通过、B<cursor≤M
    任一不符报错；成功返回None

_finish_branch(source,snapshot,reason,F=None,reasons=()):
    _validate_branch(source,snapshot)
    若reason=BLOCKED：
        复核F=cursor−1、F较B更极端、A→F失败且依据一致
        返回历史片段及阻塞依据，不返回候选
    要求reason=EOF且cursor=M
    若B为空：返回孤立起点及未决范围
    endpoints ← prefix+(B,)
    返回候选endpoints、末笔(A,B)暂定、头尾未决范围及来源

_validate_candidates(source,candidates):
    检查每条候选属于同一确切source，且至少含两端点、无重复路线
    对每条路线的相邻端点对：重新要求_check_pair通过
    检查共享端点与交替方向，最后暂定工作对等于末两项
    检查头尾未决范围对应实际合并中心
    任一不符报错；成功返回None
```

每次读取cursor严格前进，备选保存的是F之后的不同选择，恢复不重新创建同一选择；有限输入故搜索终止。直接配对按跨度扫描，完整搜索可能指数增长；本节不暗加剪枝、最大笔数目标或单解优先策略。依据保留原候选及真实失败原因，恢复重放原始时间顺序，不能把早于新B的缓存分型倒接为其后的C。输入版本改变时重新计算。
