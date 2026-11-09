"""轻量 trace 索引 + rule_id 常量 (stage-05-execution-plan.md §1.7)。

每个结构对象保留**轻量** trace 索引, 让「图上某结构有问题」能快速回溯到:
所用 profile / 命中规则 / 来源 K 线范围 / 说明卡哪节 / 哪条原文。

轻量原则 (§1.7): 默认 overlay 响应**不**下发 trace (避免影响网络/绘图性能);
详细解释链走**按需** trace 端点或调试脚本 (`scripts/trace_explain.py`) 重算, 不进默认图表主路径。

rule_id 在此集中定义 (避免散落字符串); 每条 rule_id 在对应说明卡 §13「规则清单」可回查到
触发条件 + 说明卡节 + 原文依据。
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PROFILE_ID = "default"

# ── rule_id 常量 (映射见各说明卡 §13 规则清单) ──────────────────────────────
# K 线合并 (kline-merge-v1)
RULE_MERGE_CONTAINS = "merge.contains"  # 末端单元包含合并新根 (吸收后单元 rule_id 标此)
RULE_MERGE_DIR_UP = "merge.dir.up"  # 非包含→新建并定向: 高低同时严格抬高 (第65课, 去等号)
RULE_MERGE_DIR_DOWN = "merge.dir.down"  # 非包含→新建并定向: 高低同时严格降低 (第65课, 去等号)
RULE_MERGE_INIT = "merge.init"  # 序列首段方向 (顺延确立, §16-1)
# 分型 (fenxing-v1)
RULE_FENXING_TOP = "fenxing.top.strict"  # 顶分型 (第62课)
RULE_FENXING_BOTTOM = "fenxing.bottom.strict"  # 底分型 (第62课)
# 笔 (bi-v1 v4; rule_id 按**成笔实际规则**派生, 见 bi-v1 §7 规则清单)。
# standard+merged_center=5k / standard+raw_extreme=4k / 强势前后=strong_prev·strong_next /
# 次笔=secondary。profile 标签另存 trace.profile_id; custom 按实际成笔方式派生同名 rule_id。
RULE_BI_UP_5K = "bi.up.5k"  # 老笔: standard + merged_center
RULE_BI_DOWN_5K = "bi.down.5k"
RULE_BI_UP_4K = "bi.up.4k"  # 新笔: standard + raw_extreme
RULE_BI_DOWN_4K = "bi.down.4k"
RULE_BI_UP_STRONG_PREV = "bi.up.strong_prev"  # 强势·前一笔
RULE_BI_DOWN_STRONG_PREV = "bi.down.strong_prev"
RULE_BI_UP_STRONG_NEXT = "bi.up.strong_next"  # 强势·后一笔
RULE_BI_DOWN_STRONG_NEXT = "bi.down.strong_next"
RULE_BI_UP_SECONDARY = "bi.up.secondary"  # 次笔
RULE_BI_DOWN_SECONDARY = "bi.down.secondary"
# 线段 (xianduan-v1; 本项目自主**特征序列法** feature_sequence; rule_id 按线段结束实际命中的
# 缠论「情况」派生, 用本项目缠论语义命名、**不用参考项目名** (decision-0001 §12.3)。
# feature_seq = 特征序列分型确认 (第一种情况, 第67课); gap = 缺口第二种情况反向确认 (第67/77课);
# tail = 末段未闭合 left=peak (provisional)。口径待用户确认前不落生产默认。
RULE_XIANDUAN_UP_FSEQ = "xianduan.up.feature_seq"  # 上升线段: 特征序列顶分型确认 (无缺口第一种情况)
RULE_XIANDUAN_DOWN_FSEQ = "xianduan.down.feature_seq"  # 下降线段: 特征序列底分型确认
RULE_XIANDUAN_UP_GAP = "xianduan.up.gap"  # 上升线段: 缺口第二种情况, 反向特征序列确认
RULE_XIANDUAN_DOWN_GAP = "xianduan.down.gap"
RULE_XIANDUAN_UP_TAIL = "xianduan.up.tail"  # 末段未闭合 (left=peak, provisional)
RULE_XIANDUAN_DOWN_TAIL = "xianduan.down.tail"
# 工程补充规则 (用户确认的项目工程补充, **非原文严格定义**;
# xianduan-v1 §5.7 / decision-0028 §3-bis):
# 端点极值拆段 — 标准特征序列候选的端点不是段内真极值时, 在段内方向极值处拆分 (≥9 笔才拆)。
RULE_XIANDUAN_UP_EXTREME_SPLIT = "xianduan.up.extreme_split"
RULE_XIANDUAN_DOWN_EXTREME_SPLIT = "xianduan.down.extreme_split"
# 内部空缺/笔破坏补齐 — 两条已识别线段之间的 orphan 区间, 用方向极值(笔破坏)法补成合法段。
RULE_XIANDUAN_UP_NONSTANDARD_REPAIR = "xianduan.up.nonstandard_repair"
RULE_XIANDUAN_DOWN_NONSTANDARD_REPAIR = "xianduan.down.nonstandard_repair"
# 末段同向延伸 — 反向 tail 失败但上一段方向有新极值, 把上一段 provisional 延伸到新极值。
RULE_XIANDUAN_UP_TAIL_EXTEND = "xianduan.up.tail_extend"
RULE_XIANDUAN_DOWN_TAIL_EXTEND = "xianduan.down.tail_extend"
# forming — 连续性兜底: 未被 confirmed 覆盖的不确定区/末端, 笔破坏法连续填满 (provisional)。
RULE_XIANDUAN_UP_FORMING = "xianduan.up.forming"
RULE_XIANDUAN_DOWN_FORMING = "xianduan.down.forming"
# 笔破坏失败吸收 (第五种延续, 原文场景; decision-0028 §3-quinquies, 用户 2026-06-30): 反向一笔
# 突破 N0 关键极值但**未演化成合法反向线段**、价格反沿 N0 原方向创新极值 → 该失败笔破坏区被吸收进
# N0 延伸。这类段**允许内部出现比起点/终点更极端的越点** (B5 不作硬闸, 仅查基础约束)。
RULE_XIANDUAN_UP_PEN_BREAK_ABSORB = "xianduan.up.pen_break_absorb"
RULE_XIANDUAN_DOWN_PEN_BREAK_ABSORB = "xianduan.down.pen_break_absorb"
# 强势笔破坏成段 (实战变体 strong_bi, 用户确认非原文严格; xianduan-practical-v1 §16, 用户
# 2026-07-10): 反向**单笔**严格破坏前一段 (N0) 起点关键极值 → 先登记候选不确认; 其后形成对该单笔
# 的**反向标准线段** (N2) 才确认该单笔自成一段。仅 xianduan_break_policy=strong_bi 变体产出;
# 严格 standard (line_only) 绝不出现。单笔段 (≥3/单数/首三重合 B1-B3 均豁免, 显式变体不伪装原文)。
RULE_XIANDUAN_UP_STRONG_BI_BREAK = "xianduan.up.strong_bi_break"
RULE_XIANDUAN_DOWN_STRONG_BI_BREAK = "xianduan.down.strong_bi_break"
# 中枢（zhongshu-v1 Gate B）：成立为第 17 课定义的项目工程映射；延伸为第 20 课中心定理一。
RULE_ZHONGSHU_FORM_OVERLAP3 = "zs.form.overlap3"
RULE_ZHONGSHU_EXTEND_OVERLAP = "zs.extend.overlap"
RULE_ZHONGSHU_SAME_LEVEL_OVERLAP3 = "zs.same_level.overlap3"
RULE_ZHONGSHU_SAME_LEVEL_CLOSE_RIGHT = "zs.same_level.close.right_center"
# 同级别分解活动尾部事件（same-level-decomposition-v1 §13）。单值 rule_id
# 记录当前对象最后一次改变其正式状态/边界的主事件；完整解释链仍按需重放。
RULE_ZSL_PROBE_OPEN = "zsl.probe.open"
RULE_ZSL_ACTIVE_EXTEND_STRICT_EXTREME = "zsl.active.extend.strict_extreme"
RULE_ZSL_ACTIVE_REANCHOR_EQUAL = "zsl.active.reanchor.equal"
RULE_ZSL_PROBE_CANCEL_EXTREME = "zsl.probe.cancel.extreme"
RULE_ZSL_SEGMENT_REPHASE = "zsl.segment.rephase"
RULE_ZSL_PROBE_REANCHOR_EQUAL = "zsl.probe.reanchor.equal"
RULE_ZSL_PROBE_CONFIRM_CENTER = "zsl.probe.confirm.center"
RULE_ZSL_TURN_CONFIRM = "zsl.turn.confirm"
RULE_ZSL_TURN_CANCEL_STRICT_EXTREME = "zsl.turn.cancel.strict_extreme"
RULE_ZSL_TURN_SHARED_COORDINATE = "zsl.turn.shared_coordinate"
RULE_ZSL_SPLIT_NON_STRICT = "zsl.split.non_strict"
RULE_ZSL_CLASSIFY_STRICT_UP = "zsl.classify.strict_up"
RULE_ZSL_CLASSIFY_STRICT_DOWN = "zsl.classify.strict_down"
# 走势类型（zoushi-v1 Gate B）：结构候选不表示完成走势。
RULE_ZOUSHI_ONE_CENTER = "zoushi.one_center.consolidation_candidate"
RULE_ZOUSHI_RELATION_UP = "zoushi.relation.up_strict"
RULE_ZOUSHI_RELATION_DOWN = "zoushi.relation.down_strict"
RULE_ZOUSHI_RELATION_UP_EXPANSION = "zoushi.relation.up_expansion"
RULE_ZOUSHI_RELATION_DOWN_EXPANSION = "zoushi.relation.down_expansion"
RULE_ZOUSHI_RELATION_UNDETERMINED = "zoushi.relation.undetermined"
RULE_ZOUSHI_TREND_QUALIFIED = "zoushi.trend.qualified"
# 走势类型 v2（zoushi-v2）：消费中枢层正式对象 + 用户确认的保守右侧确认。
RULE_ZOUSHI_V2_FORMING = "zoushi.v2.forming"
RULE_ZOUSHI_V2_FREEZE_CONSOLIDATION = "zoushi.v2.freeze.consolidation.right_zhongshu"
RULE_ZOUSHI_V2_FREEZE_TREND = "zoushi.v2.freeze.trend.right_zhongshu"
RULE_ZOUSHI_V2_FREEZE_EXIT_BREAK = "zoushi.v2.freeze.trend.exit_break"
# 高一级中枢递归（zoushi-recursion-v1；用户确认 E+A/B/C 项目口径）。
RULE_RECURSIVE_ZS_FORM_ENTRY_OVERLAP3 = "recursion.zs.form.entry_overlap3"
RULE_RECURSIVE_ZS_EXTEND_OVERLAP = "recursion.zs.extend.overlap"
RULE_RECURSIVE_ZOUSHI_FORM_CONSOLIDATION = "recursion.zoushi.form.consolidation"
RULE_RECURSIVE_ZOUSHI_UPGRADE_STRICT = "recursion.zoushi.upgrade.strict_relation"
RULE_RECURSIVE_ZOUSHI_EXTEND_SAME_DIRECTION = "recursion.zoushi.extend.same_direction"
RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION = "recursion.zoushi.freeze.transition_confirmed"
RULE_RECURSIVE_ZOUSHI_FORM_SHARED_TURN = "recursion.zoushi.form.shared_center_turn"
RULE_RECURSIVE_ZOUSHI_FREEZE_SHARED_TURN = "recursion.zoushi.freeze.shared_center_turn"


@dataclass(frozen=True, slots=True)
class StructTrace:
    """结构对象的轻量 trace 索引 (§1.7)。

    字段均为标识 / 范围, 不含完整解释链; 完整链由 trace 端点 / 调试脚本按需重算。
    """

    algo_card_id: str  # 说明卡 id, 如 "kline-merge-v1" / "fenxing-v1"
    rule_id: str  # 命中规则, 见本模块 RULE_* 常量
    profile_id: str = DEFAULT_PROFILE_ID
    config_hash: str | None = None  # 口径可配置后填; PR-3 恒 None
    source_from_ts: int | None = None  # 来源原始 K 线起始 ts (Unix 秒)
    source_to_ts: int | None = None  # 来源原始 K 线结束 ts
    merged_from_index: int | None = None  # 来源合并 K 线起始 index (若适用)
    merged_to_index: int | None = None  # 来源合并 K 线结束 index
    # 依赖水位线 (bi-v1 §5; strong_next 回补安全): 成笔实际查阅的最大分型/合并下标。
    # standard/strong_prev/secondary = merged_to_index; strong_next = 其后一笔参照分型下标 (更大)。
    # serializer 按此判 confirmed/provisional, 保证 strong_next 不在 confirmed 区插删笔。
    dep_to_index: int | None = None
    # 线段冻结状态 (N0/N1/N2, decision-0028 §3-quater): "frozen" / "soft_n0" / "pending_n1"。
    # **confirmed 当且仅当 freeze_state == "frozen"**; soft_n0 = 准完成软实线(未冻结);
    # pending_n1/forming = provisional。仅线段填; 其它结构 None。
    freeze_state: str | None = None
    # 笔破坏失败吸收段的**内部越点**笔下标 (decision-0028 §3-quinquies)。仅 pen_break_absorb
    # 段填: 该越点比段起点/终点更极端, 是 B5 豁免的依据 (图上排查/解释链用)。其它段 None。
    pen_break_at: int | None = None
    # 缺口第二种反向确认 (xianduan-v1 §16 v10) 的**证据笔 end_ts**: 第二特征序列反向分型完成时刻。
    # 仅 gap_revert 冻结的段填 (N0 前驱 + N1 缺口段); 与几何终点 source_to_ts **分离** (证据水位
    # 晚于几何终点)。其它段 None。``dep_to_index`` 同步指向该证据笔 (不暗示更早已 frozen)。
    confirmation_ts: int | None = None
    # 冻结事件来源: ``"gap_revert"`` = 该段由缺口第二种反向确认事件原子冻结 (前驱 N0 / 缺口 N1);
    # 其它冻结路径 (N2 两滞后 T3 / T6 / T7) 为 ""。供图上/按需 trace 解释"为何在此刻冻结"。
    frozen_by: str = ""
