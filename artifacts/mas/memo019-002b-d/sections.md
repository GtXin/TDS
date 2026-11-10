### 002.b — Detailed Implementation logic and Numerical Examples

价格区间写作 `[low,high]`，来源范围写作 `[start,stop)`。以下均为教学构造；合并结果用memo026现有代码核对，分型用四项严格比较独立核算，不表示Fenxing检测器已经实现。

#### 处理逻辑

1. **准备（2.1–2.2）。** 校验完整merged，保留其确切引用；同价锚点默认FIRST（最早），显式LAST取最晚。初始化R、T、P和ID；不足三根则记录原因并返回空结果。
2. **读取三根（2.3–2.4）。** 中心i从1到N−2，取A、B、C，按本轮high／low计算左右方向；仍有包含或等边则报错。
3. **分类（2.5）。** 上→下为顶，price=B.high；下→上为底，price=B.low；同向则不保存分型，但保留判断依据。
4. **定位并保存（2.6）。** 只在B的原始成员中匹配顶的high或底的low；没有匹配报错，有匹配按FIRST／LAST定位。保存8个Fenxing字段及相关依据。
5. **推进（2.7）。** 每轮i只增加1，不能因检出分型而跳过后面的窗口；ID只在保存成功时增加。
6. **结束（2.8）。** 冻结并组装6成员FenxingSeries，校验来源、全部应有结果和trace映射；不额外保存末根，不自动确认。

#### 主例：10根原始K线 → 7个合并单元 → 3个分型

原始输入如下。R0–R9是原始下标标签，M0–M6是合并位置标签，都不能代替分型ID。

| raw下标 | 价格区间 | raw下标 | 价格区间 |
|---|---|---|---|
| 0 | `[0,3]` | 5 | `[0,3]` |
| 1 | `[2,5]` | 6 | `[0,2]` |
| 2 | `[1,6]` | 7 | `[2,5]` |
| 3 | `[3,6]` | 8 | `[3,6]` |
| 4 | `[1,4]` | 9 | `[1,4]` |

首两根不包含，使用显式上游配置 `{"initialization":"UNSET"}` 也能完成合并，无须选定初始方向。结果为：

| merged位置 | 价格区间 | 合并方向 | 原始来源范围 |
|---|---|---|---|
| M0 | `[0,3]` | None | `[0,1)` |
| M1 | `[3,6]` | up | `[1,4)` |
| M2 | `[1,4]` | down | `[4,5)` |
| M3 | `[0,2]` | down | `[5,7)` |
| M4 | `[2,5]` | up | `[7,8)` |
| M5 | `[3,6]` | up | `[8,9)` |
| M6 | `[1,4]` | down | `[9,10)` |

例如M1按向上规则吸收R1–R3，得到 `[max(2,1,3),max(5,6,6)]=[3,6]`；M3按向下规则吸收R5、R6，得到 `[min(0,0),min(3,2)]=[0,2]`。

| 中心i | 左／右方向 | 分支与结果 | 分型merged窗口 | 原始锚点匹配J | 默认锚点 |
|---|---|---|---|---|---|
| 1 | up／down | 2.5.a：FX0，顶，price=6 | `[0,3)` | `{2,3}` | 2 |
| 2 | down／down | 2.5.d：无分型 | — | — | — |
| 3 | down／up | 2.5.b：FX1，底，price=0 | `[2,5)` | `{5,6}` | 5 |
| 4 | up／up | 2.5.c：无分型 | — | — | — |
| 5 | up／down | 2.5.a：FX2，顶，price=6 | `[4,7)` | `{8}` | 8 |

i=1的四项为 `6>3、6>4、3>0、3>1`；i=3为 `0<1、0<2、2<4、2<5`。FX0与FX1共享M2，FX1与FX2共享M4，仍全部保存；本层不进行笔端点取舍。

![原始K线、合并区间与默认最早分型锚点](memoWX_019_Chan_fenxing/algorithm-main-fractals.png)

上下图使用同一原始来源轴。合并竖线位于首个原始成员，框宽表示成员范围；紫色／蓝色符号位于实际顶／底原始锚点。原始开收盘按区间30%／70%位置交替构造，仅供绘图，合并框不表示完整OHLC。

**同价锚点。** M1显示在raw1，但raw1.high=5，不能作为price=6的锚点。默认FIRST取raw2，显式LAST取raw3；底分型相应取raw5或raw6。三条记录的price、kind和merged窗口不变，只有前两条的原始锚点改变。

默认结果的3条记录均为 `status="unconfirmed"、confirmed_at=None`；ID为0、1、2。本例伪代码每窗合并记录一条依据，因此trace有5条，`trace_by_point=((0,),(2,),(4,))`；两条无分型依据仍留在trace中。

#### 边界与末端修订

| 场景 | 应有处理 |
|---|---|
| 只有1或2个有效合并单元 | 空items、空trace_by_point；trace记录不足三根。 |
| `[1,3]→[2,4]→[3,5]`，或完全反向 | 检查1个窗口但无分型；trace保留同向判断。 |
| 手工输入相邻 `[1,5]、[3,5]` | 等高构成包含，输入校验拒绝，不能当作普通无分型。 |
| 手工把主例M1.high改成7，其余不变 | 结构校验可能通过，但raw1–3中没有high=7；J为空，报来源异常。这不是正常合并输出。 |
| config缺少同价策略 | 采用并记录FIRST；非法策略或未知选项报错。 |

将raw9从 `[1,4]` 修订为 `[4,7]` 后，对新快照重新合并／扫描：原中心i=5变为连续上升，旧FX2消失；raw9仍是末根，不能自己形成新顶。再追加raw10=`[2,5]`，合并数为8，新中心i=6构成顶，price=7、anchor_raw_index=9、merged窗口 `[5,8)`。

![同一末根修订与追加右邻后的分型变化](memoWX_019_Chan_fenxing/algorithm-tail-revision.png)

新顶标在raw9，但要到raw10出现才具备三根判断依据；这仍不等于本项目已经定义确认时间。不同结果版本可重用整数ID，不能把新旧FX2当成同一个结果对象。

### 002.c — Helper Functions

以下5个拟议辅助函数均为FenxingSeries的私有方法，不新增类或修改原始数据。入口复用现有 `merged.validate()`；主循环负责i、ID、R、T、P和结果组装。具体DecisionStep结构仍不在本节定义。

#### 规范化本层配置：_normalize_config

**接口：** `_normalize_config(config)`。

config为映射；本版仅接受可选键 `anchor_tie`，值为FIRST或LAST。缺少该键时补FIRST；未知键、None或非法值报错，不以默认值掩盖错误。返回独立、不可变的有效配置，例如 `{"anchor_tie":"FIRST"}`；不修改调用方或上游merged.config。

#### 判断相邻方向：_direction_between

**接口：** `_direction_between(a, b)`；a在前、b在后。

输入已校验、按来源相邻的两个合并单元。b的high、low均严格较大返回up，均严格较小返回down；其余关系报错。函数不读取或覆盖单元direction，不设价格容差，不推进扫描位置。

#### 分类三根窗口：_classify_window

**接口：** `_classify_window(a, b, c)`。

调用_direction_between得到左右方向，返回普通数据元组 `(kind, price, d_left, d_right)`。up／down返回 `(top,b.high,up,down)`；down／up返回 `(bottom,b.low,down,up)`；两种同向情况的kind、price均为None，仍返回方向供trace使用。函数不定位原始锚点、不构造Fenxing。

#### 定位原始锚点：_resolve_anchor

**接口：** `_resolve_anchor(raw, center, kind, price, policy)`。

raw必须是当前merged的确切原始来源；center来自当前窗口，要求 `0≤source_start<source_stop≤len(raw)`。kind为top／bottom，price分别等于center.high／low，policy必须为已规范化的FIRST／LAST。

按原始下标递增遍历center来源范围：顶比较raw[j].high，底比较raw[j].low，使用严格相等。只累计匹配数量、首个及最后匹配下标，不创建raw切片或完整匹配列表。没有匹配报错；否则返回 `(anchor_raw_index, count, first, last)`，其中锚点按policy取first或last。即使FIRST已经找到，也完成本组扫描，以保存完整匹配数量和首尾依据。

#### 校验本层完整结果：_validate_result

**接口：** `_validate_result(merged, result)`。

这是拟议 `FenxingSeries.validate()` 的本层校验核心；不再次调用result.validate，避免递归。merged已通过入口校验，本函数不重跑上游合并。

1. 检查确切source_series引用、有效配置（已含anchor_tie）／规则版本、8字段记录的局部合法性、唯一整数ID及unconfirmed／None。窗口必须有3根且在merged范围内；原始锚点位于中心原始范围。
2. 按i=1…N−2顺序重检窗口，用一个结果指针逐项核对全部应有分型、kind、price和窗口，拒绝漏报、误报、多报及乱序；每次命中再用_resolve_anchor核对选定锚点。允许窗口重叠，不要求分型覆盖全部原始K线。
3. 本伪代码每个完整窗口恰有一条逻辑依据，按中心顺序核对数量与内容，拒绝缺失、重复或虚假事件；不足三根时恰有一条原因依据。trace_by_point与items等长，每条结果关联自己的窗口依据，并复核匹配数量、首尾、所选锚点和策略；无输出依据无需关联结果。

成功返回None，失败报错；不排序、不修补、不分配新ID。记录构造校验局部字段，序列构造自动执行本层完整校验；主循环不再重复校验刚构造好的序列。

### 002.d — Pseudocode

以下是算法伪代码，不是已实现的Python接口。使用002.c的5个私有辅助函数；“记录依据”表示保存本轮实际比较及来源的逻辑动作，不规定DecisionStep的新字段。

#### 主过程

```text
FenxingSeries.derive_from(source_series, config, rule_tree_ref):
    若source_series不是完整MergedKlineSeries：报错
    merged ← source_series
    merged.validate()
    若rule_tree_ref不是非空规则位置／版本：报错
    effective ← _normalize_config(config)       # 缺省anchor_tie=FIRST
    raw ← merged.source_series
    N ← len(merged)
    R、T、P ← 三个独立空列表
    next_id ← 0
    i ← 1

    若N<3：
        将“不足三根”的来源依据追加到T

    当i<N−1时重复：
        断言len(R)=len(P)=next_id
        A ← merged[i−1]
        B ← merged[i]
        C ← merged[i+1]
        kind, price, left, right ← _classify_window(A, B, C)
        anchor_evidence ← None

        若kind不是None：
            anchor, count, first, last ← _resolve_anchor(
                raw, B, kind, price, effective["anchor_tie"])
            anchor_evidence ← 所选锚点、数量、首尾匹配及实际策略

        e ← len(T)
        将本轮i、窗口、来源、左右方向、kind、price及anchor_evidence追加到T

        若kind不是None：
            point ← Fenxing(
                id=next_id, kind=kind, price=price,
                anchor_raw_index=anchor,
                source_start=i−1, source_stop=i+2,
                status="unconfirmed", confirmed_at=None)
            将point追加到R                   # 构造时校验局部字段
            将(e,)追加到P
            next_id ← next_id+1

        i ← i+1                            # 包括无分型分支

    返回FenxingSeries(
        source_series=merged,
        items=tuple(R), config=effective, rule_tree_ref=rule_tree_ref,
        trace=T的深度不可变副本, trace_by_point=tuple(P))
        # 构造时自动调用validate → _validate_result；失败则报错
```

#### 原始锚点扫描

```text
_resolve_anchor(raw, center, kind, price, policy):
    检查002.c规定的范围、kind、price与policy前提
    count ← 0
    first、last ← None
    对j从center.source_start到center.source_stop−1：
        value ← raw[j].high（top）或raw[j].low（bottom）
        若value=price：
            若first为None：first ← j
            last ← j
            count ← count+1
    若count=0：报来源异常
    anchor ← first（FIRST）或last（LAST）
    返回(anchor, count, first, last)
```

#### 完整性校验的顺序

```text
_validate_result(merged, result):
    检查002.c的引用、配置、局部字段和trace映射长度
    若len(merged)<3：
        检查items及trace_by_point为空，trace恰有一条对应“不足三根”的依据
        返回None
    检查len(result.trace)=len(merged)−2
    p ← 0                                  # 结果位置，不是特征ID
    对i从1到len(merged)−2：
        kind, price, left, right ← _classify_window(
            merged[i−1], merged[i], merged[i+1])
        e ← i−1
        核对result.trace[e]的中心、窗口、方向、kind及price与本轮一致
        若kind为None：
            检查该依据没有锚点记录；继续下一中心
        若p=len(result.items)：报漏报
        point ← result.items[p]
        核对point的kind、price及窗口[i−1,i+2)
        anchor, count, first, last ← _resolve_anchor(
            merged.source_series, merged[i], kind, price, result.config["anchor_tie"])
        核对point.anchor_raw_index，以及依据中的count、first、last和实际策略
        检查result.trace_by_point[p]=(e,)
        p ← p+1
    若p≠len(result.items)：报多报／乱序
    返回None
```

窗口依据按中心索引核对，不为每个窗口遍历整份trace或items。计算与本层校验各顺序扫描一次；原始锚点范围互不重叠，故各为O(N+M)，M为原始K线数。上游校验开销另计；辅助函数不推进i、追加R／T／P或读写文件。

