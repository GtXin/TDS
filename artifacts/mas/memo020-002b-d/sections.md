### 002.b — Detailed Implementation logic and Numerical Examples

本节直接使用已处理好的合并K线和全部完整分型，不重复上游包含处理。区间为 `[low,high]`；合并位置与分型位置均从0开始。数值是教学构造，只提供高低价，不编造原始OHLC或原始锚点。

#### 处理逻辑

1. **准备候选起点（2.1）。** 按时间将每个分型作为一个可能的初始A；当前先检查最早者，其余保存为待试分支。已有端点路径起初只有A，B未定。
2. **寻找B（2.2–2.4）。** 顺序读取F，先将游标移至下一分型，再检查A→F。失败只记录本次配对原因；成功则缓存“不选F”的独立备选，当前令B=F。A→B仍为工作笔，不立即固定B。
3. **延伸B（2.5–2.6）。** 同型F更极端时，完整检查A→F，通过才更新B；失败则阻塞当前路线，保存历史片段并恢复备选。同价F通过检查时保留旧B与改取F两支；较弱F不替换B。
4. **等待反向C（2.7）。** 异型F须与当前B重新配对；不合格者保留，首个合格者成为C。将A→B局部暂存，工作对推进为B→C；新终点C仍可延伸，先前路线也允许随备选恢复而重选。
5. **恢复备选（2.8）。** 恢复的是另一种选择已经指定好的路径、A/B及下一未读位置，不重新进入同一选择点再次分叉。阻塞历史不混入可行结果；数据耗尽时的最后工作笔保持暂定，头尾未覆盖范围单独记录。
6. **汇总候选（2.9）。** 完成全部分支后复核连接，按分型位置序列去重，再按相同起终点分组。组内唯一不等于整个输入只有一种划笔；本树不另选最多笔、最早或最晚的一条。

#### 主例：21根合并K线中的阻塞与恢复

依次给定最低价：

```text
位置： 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
low：  8  9  6  4  2  0  2  4  6  7  3 -1  1  3  5  8  5  2  0 -2 -1
```

每根的 `high=low+1`。相邻low均不相等，所以相邻high、low始终共同严格上移或下移，没有相邻包含。逐窗识别得到以下全部分型：

| 分型位置 | 类型 | 合并中心 | 中心区间 | 分型价格 | 合并窗口 |
|---|---|---:|---|---:|---|
| FX0 | 顶 | 1 | `[9,10]` | 10 | `[0,3)` |
| FX1 | 底 | 5 | `[0,1]` | 0 | `[4,7)` |
| FX2 | 顶 | 9 | `[7,8]` | 8 | `[8,11)` |
| FX3 | 底 | 11 | `[-1,0]` | −1 | `[10,13)` |
| FX4 | 顶 | 15 | `[8,9]` | 9 | `[14,17)` |
| FX5 | 底 | 19 | `[-2,-1]` | −2 | `[18,21)` |

这里的FX0–FX5表示源FenxingSeries中的位置，不要求等于其ID。下面用合并中心标记路线，方便对照价格图；算法保存端点时仍使用分型位置。

**第一次尝试。** 初始A为顶1，已有端点路径为 `(FX0,)`，B未定。

| 读到的分型 | 检查与结果 | 当前已有路径／工作对 | 缓存或下一步 |
|---|---|---|---|
| 底5 | 1→5中心距4；范围最低0、最高10，合格 | 已有路径仍为`(1,)`；工作对`1→5` | 缓存“不选底5”；当前B=底5 |
| 顶9 | 5→9中心距4；范围最低0、最高8，合格反向 | 局部暂存`1→5`；工作对`5→9` | A=底5、B=顶9，继续等下一反向 |
| 底11 | 9→11中心距2，不合格 | 保留工作对`5→9` | 记录底11及距离失败依据，不删除它 |
| 顶15 | 顶15的9高于暂定顶9的8，须尝试延伸；但5→15范围最低为−1，低于底5的0 | `5→15`不合格，当前路线阻塞 | 保存历史`1→5→9`与失败依据，恢复备选 |

顶15出现时，当前工作笔的A已经是**底5**，B是**顶9**，因此复查的是 `5→15`。初始顶1已经在此前路径中，不能误用 `1→15` 替代本轮检查。新顶更高并不足以保证延伸合法；完整范围内的底11使底5失去最低端点资格。

**恢复的选择。** 底5第一次合格时保存的备选，表示“本次不选底5”；它的状态已经位于该选择之后：

```text
已有端点路径 = (FX0,)
A = FX0（顶1）
B = 未定
下一分型位置 = 2（FX2，顶9）
```

恢复后既不重读底5并重新生成相同备选，也不沿用阻塞分支已经前进到中心19的游标。

| 恢复后读取 | 判断 | 行动 |
|---|---|---|
| 顶9 | 与初始A顶1同型 | 本对不能成笔，继续 |
| 底11 | 1→11中心距10；范围最低−1、最高10，合格 | 当前B=底11，另缓存“不选底11” |
| 顶15 | 11→15中心距4；范围最低−1、最高9，合格反向 | 局部暂存`1→11`，工作对变为`11→15` |
| 底19 | 15→19中心距4；范围最低−2、最高9，合格反向 | 局部暂存`11→15`，工作对变为`15→19` |
| 输入耗尽 | 最后工作对仍满足全部条件 | 保留路线`1→11→15→19`；`15→19`仍为暂定工作笔 |

![同一连续输入中的阻塞与缓存恢复](memoWX_020_Chan_bi/algorithm-cached-recovery.png)

上图两幅共用合并位置和价格刻度。蓝色为该分支已局部暂存的笔，橙色虚线为仍可延伸的工作笔；它们均不表示已定义市场确认。灰色矩形只表示合并K线高低区间。路线覆盖中心1至19，位置0、20未纳入几何笔范围；位置20仍参与底分型19的右邻判断。

**全部分支的输出。** 继续恢复剩余备选及其他初始起点，得到恰好四条去重后的可行路线：

| 合并中心路线 | 源分型位置序列 | 最后暂定工作对 |
|---|---|---|
| `1→11→15→19` | `(0,3,4,5)` | FX4→FX5 |
| `1→19` | `(0,5)` | FX0→FX5 |
| `11→15→19` | `(3,4,5)` | FX4→FX5 |
| `15→19` | `(4,5)` | FX4→FX5 |

前两条属于同一起终点组，仍有多解；后两条初始位置不同，不能与前组混称“同一范围内唯一”。阻塞的历史`1→5→9`另列诊断，不作为可行路线返回。

例如第一条路线对应的Bi端点位置将是 `(0,3)`、`(3,4)`、`(4,5)`，方向依次向下、向上、向下；不是把合并中心1、11、15、19直接填入 `start_fenxing_index/end_fenxing_index`。本节不为合成区间编造 `anchor_raw_index`；实际显示复用源Fenxing已有的原始锚点。

#### 补例：B成功延伸后才找到反向C

另给15根合并K线，low依次为 `1,0,3,6,9,12,10,8,12,16,13,10,7,4,5`，每根 `high=low+2`。全部分型为底1、顶5、底7、顶9、底13。

| 事件 | 数值检查 | 工作状态 |
|---|---|---|
| 顶5出现 | 底1→顶5中心距4，范围`[0,14]`，合格 | A=底1、暂定B=顶5，不固定B |
| 底7出现 | 顶5→底7中心距2 | 反向不合格，缓存底7 |
| 顶9出现 | 18>14，且底1→顶9中心距8、范围`[0,18]`，完整复检通过 | 必须更新B=顶9，旧顶5进入历史 |
| 底13出现 | 顶9→底13中心距4、范围`[4,18]`，合格 | 首次局部收下`1→9`；`9→13`成为新工作笔 |

![暂定B从顶5延伸至顶9，再推进为反向工作笔](memoWX_020_Chan_bi/algorithm-endpoint-extension.png)

因此这一分支首次局部收下的是 `1→9`，而不是提前固定的 `1→5`。向下笔完全对称：在合格反向顶出现前，后来的更低底只有通过A→新底完整复检后才能替换B。

**其余边界。** 同价B按2.6.b保留两种合法选择，与一个合并中心内部原始锚点的FIRST／LAST无关。最后合并K线已经越过B、但尚未形成完整新分型时，只标注方向性尾部越界和未决范围，不制造新端点。原始输入或合并尾部修订后，应使用新快照重新计算，不把本次恢复点当成跨版本增量协议。

全部输入、逐步配对和缓存状态见[数值核验](../../artifacts/mas/memo020-002b-d/examples.json)；图表、主例和补例是独立模型的教学核验，不是生产Bi检测器或CC运行结果。

### 002.c — Helper Functions

以下6个拟议私有辅助函数服务于002.a的候选搜索，不新增领域类，不修改上游数据。入口复用确切`FenxingSeries.validate()`；主过程负责读入位置、备选栈、依据记录与报告组装。多条候选路线不能平铺为同一条`BiSeries.items`；本阶段返回普通研究报告，尚不定义正式`BiSeries.derive_from()`的多解返回接口。

**位置与工作状态。** `source`是本次确切FenxingSeries，`fx=source.items`，`merged=source.source_series`，`M=len(fx)`。A、B、F和路线中的端点均为`fx`的零基位置，不是特征ID、合并K线位置或原始锚点；`c(p)=fx[p].source_start+1`才是合并中心。`prefix`为已有连接的端点元组，其最后一项恒为A；当前工作笔A→B尚未追加到prefix。`cursor`为下一未读分型位置，可等于M表示耗尽。分支保存确切source引用、prefix、A/B、阶段和cursor；这些仅是算法工作数据。

#### 检查完整配对：_check_pair

**接口：** `_check_pair(source, a, b) → (ok, reasons)`。

端点必须是当前source中的整数序列位置；非法类型或越界报错，不做ID解析。数值恰好落在位置范围内的ID误用，不能仅凭整数检查识别，调用方必须按源序列位置传参。按002.a的“合格”定义，依次检查时间／类型、`c(b)-c(a)≥4`、两中心区间关系，以及闭区间`[c(a),c(b)]`内全部合并K线的高低界。返回布尔结果及本次实际失败依据；同型或逆序先返回不合格，不能用无意义的方向继续判断。函数不选端点、不推进cursor、不修改分型，也不重跑合并。

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

    若M<2：
        记录“不足两个完整分型”及整个[0,N)为未决范围
        返回同一来源、空候选／分组／阻塞记录、未决范围及本次依据
        # 输入先校验；不构造孤立笔，也不进入分支循环

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

            _freeze_branch(source,prefix,A,B,cursor)
                # 仅核对本轮状态，不另入缓存；构造时已调用_validate_branch

        若dead=False：
            outcome ← _finish_branch(source,
                _freeze_branch(source,prefix,A,B,cursor),EOF)
            若outcome是候选：candidates.append(outcome)
            否则：unresolved.append(outcome)
        # 当前分支已收尾；外层while取最近备选。没有任何裸goto跳过恢复。

    按同一source内的完整端点位置元组去除重复候选
    _validate_candidates(source,candidates)
    按首末端点位置分组：一条标单解，多条全部保留标多解
    # 单解只指同一输入、相同边界、按本树策略得到的一条去重路线
    返回来源、候选／分组、末笔暂定信息、未决范围、blocked及实际依据
    # 无候选时返回相应说明；BLOCKED历史不充当候选路线
```

#### 完整配对与状态校验

```text
_check_pair(source,a,b):
    fx ← source.items；merged ← source.source_series
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
    fx ← source.items
    检查f晚于b且同型；否则报错
    若fx[f].price=fx[b].price：返回EQUAL
    若同为顶：较高返回MORE，其余LESS
    若同为底：较低返回MORE，其余LESS

_freeze_branch(source,prefix,a,b,cursor):
    snapshot ← 包含同一source、tuple(prefix)、a、b、阶段及cursor的不可变数据
    _validate_branch(source,snapshot)
    返回snapshot

_validate_branch(source,snapshot):
    fx ← source.items；M ← len(fx)
    prefix,A,B,cursor ← snapshot的对应值
    检查source对象身份、阶段、端点／cursor整数范围
    检查prefix为非空元组且末项=A
    对prefix每个相邻端点对：要求_check_pair通过
    若B为空：要求阶段SEEK_B、prefix=(A,)、A<cursor≤M
    否则：要求阶段WAIT_REVERSE、_check_pair(A,B)通过、B<cursor≤M
    任一不符报错；成功返回None

_finish_branch(source,snapshot,reason,F=None,reasons=()):
    _validate_branch(source,snapshot)
    prefix,A,B,cursor ← snapshot的对应值
    M ← len(source.items)；N ← len(source.source_series)
    若reason=BLOCKED：
        复核F=cursor−1、F较B更极端、A→F失败且依据一致
        返回历史片段及阻塞依据，不返回候选
    要求reason=EOF且cursor=M
    若B为空：返回孤立起点及未决范围
    endpoints ← prefix+(B,)
    返回候选endpoints、末笔(A,B)暂定、头尾未决范围及来源

_validate_candidates(source,candidates):
    fx ← source.items；merged ← source.source_series
    检查每条候选属于同一确切source，且至少含两端点、无重复路线
    对每条路线的相邻端点对：重新要求_check_pair通过
    检查共享端点与交替方向，最后暂定工作对等于末两项
    检查头尾未决范围对应实际合并中心
    任一不符报错；成功返回None
```

每次读取cursor严格前进，备选保存的是F之后的不同选择，恢复不重新创建同一选择；有限分型、有限初始起点及有限深度选择树保证终止。令N为合并K线数、M为分型数、S为实际检查／恢复步数、R为去重路线数；本参考方案的完整状态与配对复核成本为O((S+R)(N+M))；候选去重、分组和可选排序另计，上游校验亦另计。S与输出数量都可能指数增长，保存候选所需空间至少与全部端点序列总长度成正比，完整依据和阻塞历史另计；本节不暗加剪枝、最大笔数目标或单解优先策略。依据保留原候选及真实失败原因，恢复重放原始时间顺序，不能把早于新B的缓存分型倒接为其后的C。输入版本改变时重新计算。

**核验边界。** 该伪代码的辅助函数分解已用独立可执行模型对照递归参考：1010组输入及1010个价格镜像，包含1000组变宽合并区间；另有12项损坏状态／短输入探针和路径别名检查。对照的是候选端点集合与局部状态不变量，不把它写成全部trace或诊断字段逐字一致的证明。入口的合成适配器仅验证本实验使用的字段，不替代真实FenxingSeries的完整来源校验；生产Bi、确认协议和CC均未在本任务运行。[伪代码模型核验](../../artifacts/mas/memo020-002b-d/pseudocode_model.json)

