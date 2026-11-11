### 002.c — Helper Functions

以下8个拟议私有辅助函数用于同一条主路线。主过程持有工作状态、推进FX位置并保存依据；辅助函数不提交笔、不改上游数据。Q只是002.a定义的普通快照，不据此新增领域类、公开接口或DecisionStep字段。

#### 输入与续读前提：_validate_input

**接口：** `_validate_input(source, previous_state=None)`。

先校验确切来源链：merged非空、有效且相邻无包含；逐窗核对全部完整严格分型，含顺序、三根窗口、kind、price、原始锚点与来源，拒绝漏报、误报、错源。M为0也须先校验来源，不能把空FX与非法空merged混为一谈。

续读另检查Q由本过程在同一规则及输出约定下正常返回、未被改写，保存的整个原始／合并／FX前缀与长度仍兼容，稳定上下文不变。新source不必与旧对象同一身份。检查Q中的引用、读取位置与状态一致；局部几何合法不足以接收任意手造S，因为首笔简化还依赖它的初始化历史。前缀修订报输入修订；不静默清空R或重选起点。previous_state必须是None或完整有效Q，空字典不能当成初次运行；距离档位兼容性另由下面的_resolve_distance_mode检查，均通过后才能读新FX。

#### 解析距离档位：_resolve_distance_mode

**接口：** `_resolve_distance_mode(distance_mode, previous_state=None) → (mode, min_gap)`。

1. 显式值仅接受`"strong"`或`"weak"`；其他字符串、数字、布尔值及容差替代值报错。None只表示省略。
2. 初次previous_state为None：省略取strong；按固定映射strong→4、weak→3派生门槛。
3. 续读：旧Q必须显式保存合法mode及与之相符的min_gap；缺失或不一致即报错，不从旧笔中心距猜测档位。省略则继承；显式值必须等于旧mode，否则拒绝续用，即使尚无笔。

只返回有效值，不推进位置、不改Q，也不允许独立指定min_gap。

#### 同型强弱：_compare_same_kind

**接口：** `_compare_same_kind(fx, X, F) → MORE／EQUAL／LESS`。

F晚于X且同型；顶price更高、底更低返回MORE，严格同价返回EQUAL，其余LESS。不设容差，不检查距离。初始化仅MORE更新S；延伸的EQUAL须进入新增段检查。

#### 首笔检查：_check_first

**接口：** `_check_first(merged, fx, S, F, min_gap) → (ok, evidence)`。

仅在无缓存、F与S异型且所有早先分型已按初始化规则处理时使用。先查`c(F)-c(S)≥min_gap`，再查F为顶时high是两中心闭区间最高，F为底时low是最低。S侧极值已由初始化保证。不将这个函数用作任意两点的通用成笔检查；失败不更换S。

#### 缓存终点延伸：_check_extension

**接口：** `_check_extension(merged, fx, A, B, F) → (ok, evidence)`。

旧A→B在同一距离档位下合格，F晚于B、同型且同价或更极端，LESS已由主过程排除。F为顶时新界为`[L_A,H_F]`，F为底时为`[L_F,H_A]`。只遍历`k=c(B)+1..c(F)`，检查low不低于下界、high不高于上界；不重查距离或旧前缀。起点是当前缓存B之后，包含其间所有曾被略过的分型和K线，不能从上一个失败候选之后算。失败保留旧缓存，MORE也继续读。

#### 下一反向笔：_check_reverse

**接口：** `_check_reverse(merged, fx, B, F, min_gap) → (ok, evidence)`。

F晚于B且异型；查中心距至少min_gap，再查顶high、底low分别是两中心闭区间最高、最低。两侧都要查；此前延伸失败的候选仍可能破坏B侧极值。两端区间关系由完整严格分型与两侧极值推出，不再重复检测。

#### 局部连接断言：_check_state

**接口：** `_check_state(fx, R, Bi002, S, E, next_position)`。

不重扫K线。E未定，读取位置在`[0,M]`；S和当前缓存／R末笔的引用属于已读FX前缀。有缓存时其终点=S；R非空时末笔终点=缓存起点且方向相反。无缓存时R为空；尚无FX时允许S未定。全部历史端点及几何条件留给输出验收。失败报内部状态错误。

#### 按001独立验收：_validate_output

**接口：** `_validate_output(source, Q, R_before, mode, min_gap)`。

1. 核对Q中的mode／min_gap与本次解析结果完全相同，且符合strong→4、weak→3的映射。直接按001本档检查R及缓存各笔：时间与异型、中心距、两端区间关系、闭区间全部high／low界；不用三个简化谓词代替完整检查。再查连接端点及交替方向。
2. 调用_check_state；正常EOF要求`next_position=M`、E为None。M=0时S未定；M>0时S引用已读分型；无缓存时R为空。
3. 要求`len(Q.R)≥len(R_before)`且原有前缀逐项同值。R_before是本次入口R的不可变值副本，这只是“不改已提交笔”的断言，不新增选笔策略。
4. 核对Q保存当前整个来源上下文；未决范围按当前N和端点计算，空范围省略。依据与新读FX对应且不重复，当前约定每个已读FX一条，EOF不增记。完全相同快照的重复调用不制造新记录。

返回None或报内部状态错误。验收不因未提交末笔而失败，不把缓存加入R，不填造确认时间。

