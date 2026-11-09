"""走势类型 Gate B：严格中枢关系与结构候选（不判断完成）。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any

from cc.algo.bi import bi_confirmed_flags
from cc.algo.config import ChanConfig
from cc.algo.models import (
    Bi,
    BiDir,
    CompletedZouShi,
    LevelBuildResult,
    LevelLeg,
    Xianduan,
    ZhongShu,
    ZhongShuMode,
    ZhongShuRelation,
    ZhongShuRelationType,
    ZhongShuSource,
    ZhongShuState,
    ZouShiBoundaryState,
    ZouShiCandidate,
    ZouShiClassificationState,
    ZouShiDirection,
    ZouShiEndpoint,
    ZouShiKind,
    ZouShiLevel,
    ZouShiStability,
)
from cc.algo.same_level import build_same_level_result
from cc.algo.trace import (
    RULE_ZOUSHI_ONE_CENTER,
    RULE_ZOUSHI_RELATION_DOWN,
    RULE_ZOUSHI_RELATION_DOWN_EXPANSION,
    RULE_ZOUSHI_RELATION_UNDETERMINED,
    RULE_ZOUSHI_RELATION_UP,
    RULE_ZOUSHI_RELATION_UP_EXPANSION,
    RULE_ZOUSHI_TREND_QUALIFIED,
    RULE_ZOUSHI_V2_FORMING,
    RULE_ZOUSHI_V2_FREEZE_CONSOLIDATION,
    RULE_ZOUSHI_V2_FREEZE_EXIT_BREAK,
    RULE_ZOUSHI_V2_FREEZE_TREND,
    StructTrace,
)
from cc.algo.zhongshu import select_l1_frozen_xianduan_prefix
from cc.algo.zoushi_kernel import (
    ZouShiKernelCenter,
    ZouShiKernelLeg,
    ZouShiKernelRuleIds,
    ZouShiKernelSlice,
    build_zoushi_kernel_slices,
)

ZOUSHI_ALGO_VERSION = 2
ZOUSHI_V2_ALGO_VERSION = 21
ZOUSHI_DISABLED_REASON = "zoushi_requires_standard_l1_frozen_xianduan_zhongshu"
_ALGO_CARD_ID = "zoushi-v1"
_V2_ALGO_CARD_ID = "zoushi-v2"


@dataclass(frozen=True, slots=True)
class ZouShiBuildResult:
    """同一次纯函数派生的相邻关系与结构候选。"""

    relations: tuple[ZhongShuRelation, ...]
    candidates: tuple[ZouShiCandidate, ...]


def classify_zhongshu_relation(
    left: ZhongShu, right: ZhongShu
) -> ZhongShuRelationType:
    """按第 20 课中心定理二分类；严格不等号，等号不算趋势。"""
    if right.dd > left.gg:
        return ZhongShuRelationType.UP_TREND
    if right.gg < left.dd:
        return ZhongShuRelationType.DOWN_TREND
    if right.zd > left.zg and right.dd <= left.gg:
        return ZhongShuRelationType.UP_EXPANSION
    if right.zg < left.zd and right.gg >= left.dd:
        return ZhongShuRelationType.DOWN_EXPANSION
    return ZhongShuRelationType.UNDETERMINED


def _stability(items: Sequence[ZhongShu]) -> ZouShiStability:
    return (
        ZouShiStability.STABLE
        if all(item.extension_state is ZhongShuState.CLOSED for item in items)
        else ZouShiStability.PROVISIONAL
    )


def _trace(
    items: Sequence[ZhongShu],
    *,
    rule_id: str,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    traces = [item.trace for item in items if item.trace is not None]
    source_from = [
        trace.source_from_ts
        for trace in traces
        if trace.source_from_ts is not None
    ]
    source_to = [
        trace.source_to_ts for trace in traces if trace.source_to_ts is not None
    ]
    merged_from = [
        trace.merged_from_index
        for trace in traces
        if trace.merged_from_index is not None
    ]
    merged_to = [
        trace.merged_to_index
        for trace in traces
        if trace.merged_to_index is not None
    ]
    dep_to = [
        trace.dep_to_index for trace in traces if trace.dep_to_index is not None
    ]
    return StructTrace(
        algo_card_id=_ALGO_CARD_ID,
        rule_id=rule_id,
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=min(source_from) if source_from else min(item.start_ts for item in items),
        source_to_ts=max(source_to) if source_to else max(item.end_ts for item in items),
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=max(merged_to) if merged_to else None,
        dep_to_index=max(dep_to) if dep_to else None,
    )


_RELATION_RULES = {
    ZhongShuRelationType.UP_TREND: RULE_ZOUSHI_RELATION_UP,
    ZhongShuRelationType.DOWN_TREND: RULE_ZOUSHI_RELATION_DOWN,
    ZhongShuRelationType.UP_EXPANSION: RULE_ZOUSHI_RELATION_UP_EXPANSION,
    ZhongShuRelationType.DOWN_EXPANSION: RULE_ZOUSHI_RELATION_DOWN_EXPANSION,
    ZhongShuRelationType.UNDETERMINED: RULE_ZOUSHI_RELATION_UNDETERMINED,
}


def _relation(
    left: ZhongShu,
    right: ZhongShu,
    left_index: int,
    *,
    profile_id: str,
    config_hash: str | None,
) -> ZhongShuRelation:
    relation = classify_zhongshu_relation(left, right)
    return ZhongShuRelation(
        period=left.period,
        source_type=ZhongShuSource.XIANDUAN,
        relation=relation,
        stability=_stability((left, right)),
        left_zhongshu_id=left.id,
        right_zhongshu_id=right.id,
        left_index=left_index,
        right_index=left_index + 1,
        start_ts=left.start_ts,
        end_ts=right.end_ts,
        left_zg=left.zg,
        left_zd=left.zd,
        left_gg=left.gg,
        left_dd=left.dd,
        right_zg=right.zg,
        right_zd=right.zd,
        right_gg=right.gg,
        right_dd=right.dd,
        trace=_trace(
            (left, right),
            rule_id=_RELATION_RULES[relation],
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def _direction(relation: ZhongShuRelationType) -> ZouShiDirection | None:
    if relation is ZhongShuRelationType.UP_TREND:
        return ZouShiDirection.UP
    if relation is ZhongShuRelationType.DOWN_TREND:
        return ZouShiDirection.DOWN
    return None


def _candidate(
    centers: Sequence[ZhongShu],
    relations: Sequence[ZhongShuRelation],
    start: int,
    end: int,
    direction: ZouShiDirection | None,
    *,
    profile_id: str,
    config_hash: str | None,
) -> ZouShiCandidate:
    members = centers[start : end + 1]
    member_relations = relations[start:end]
    kind = ZouShiKind.TREND if len(members) >= 2 else ZouShiKind.CONSOLIDATION
    rule_id = RULE_ZOUSHI_TREND_QUALIFIED if kind is ZouShiKind.TREND else RULE_ZOUSHI_ONE_CENTER
    return ZouShiCandidate(
        period=members[0].period,
        kind=kind,
        trend_direction=direction,
        classification_state=ZouShiClassificationState.STRUCTURALLY_QUALIFIED,
        stability=_stability(members),
        start_ts=members[0].start_ts,
        end_ts=members[-1].end_ts,
        start_zhongshu_index=start,
        end_zhongshu_index=end,
        zhongshu_ids=tuple(item.id for item in members),
        relation_ids=tuple(item.id for item in member_relations),
        member_count=len(members),
        trace=_trace(
            members,
            rule_id=rule_id,
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def build_zoushi_candidates(
    zhongshus: Sequence[ZhongShu],
    *,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> ZouShiBuildResult:
    """从正式段中枢构建关系与最大同向局部候选；不判断走势完成。"""
    centers = list(zhongshus)
    for index, item in enumerate(centers):
        if item.source_type is not ZhongShuSource.XIANDUAN:
            raise ValueError("formal zoushi candidates require xianduan zhongshu input")
        if item.period != period:
            raise ValueError(f"zhongshu period {item.period!r} != requested {period!r}")
        if index and item.start_ts <= centers[index - 1].start_ts:
            raise ValueError("zhongshu inputs must be strictly ordered by start_ts")
    if not centers:
        return ZouShiBuildResult(relations=(), candidates=())

    relations = tuple(
        _relation(
            centers[index],
            centers[index + 1],
            index,
            profile_id=profile_id,
            config_hash=config_hash,
        )
        for index in range(len(centers) - 1)
    )
    candidates: list[ZouShiCandidate] = []
    chain_start = 0
    chain_direction: ZouShiDirection | None = None
    for index, relation in enumerate(relations):
        next_direction = _direction(relation.relation)
        if next_direction is None:
            candidates.append(
                _candidate(
                    centers,
                    relations,
                    chain_start,
                    index,
                    chain_direction,
                    profile_id=profile_id,
                    config_hash=config_hash,
                )
            )
            chain_start = index + 1
            chain_direction = None
        elif chain_direction is None:
            chain_direction = next_direction
        elif chain_direction is not next_direction:
            candidates.append(
                _candidate(
                    centers,
                    relations,
                    chain_start,
                    index,
                    chain_direction,
                    profile_id=profile_id,
                    config_hash=config_hash,
                )
            )
            # Gate B 是局部结构候选而非完成走势分解；反转关系共享转折中枢。
            chain_start = index
            chain_direction = next_direction
    candidates.append(
        _candidate(
            centers,
            relations,
            chain_start,
            len(centers) - 1,
            chain_direction,
            profile_id=profile_id,
            config_hash=config_hash,
        )
    )
    return ZouShiBuildResult(relations=relations, candidates=tuple(candidates))

# ── v2：L0/L1 共用的同级别分解内核 ──────────────────────────────────────


def _level_endpoint(leg: LevelLeg, *, at_start: bool) -> ZouShiEndpoint:
    return ZouShiEndpoint(
        source_id=leg.source_id,
        source_index=leg.source_index,
        ts=leg.start_ts if at_start else leg.end_ts,
        price=leg.start_price if at_start else leg.end_price,
    )


def _level_continuous(left: LevelLeg, right: LevelLeg) -> bool:
    return (
        right.source_index == left.source_index + 1
        and left.end_ts == right.start_ts
        and left.direction is not right.direction
    )


def _leg_position(
    source_position: dict[int, int],
    source_index: int | None,
    *,
    role: str,
) -> int:
    """把正式中枢保存的来源下标解析到当前连续部件序列。"""
    if source_index is None:
        raise ValueError(f"official zhongshu is missing {role}")
    try:
        return source_position[source_index]
    except KeyError as exc:
        raise ValueError(f"official zhongshu {role} is outside the supplied leg run") from exc


def _direction_extreme_leg(
    run: Sequence[LevelLeg],
    *,
    start_position: int,
    end_position: int,
    direction: ZouShiDirection,
) -> LevelLeg:
    """取中枢生命周期内同方向离开尝试的极值终点；同价取最后一次。"""
    bi_direction = BiDir.UP if direction is ZouShiDirection.UP else BiDir.DOWN
    attempts = [
        leg
        for leg in run[start_position : end_position + 1]
        if leg.direction is bi_direction
    ]
    if not attempts:
        raise ValueError("zoushi lifecycle has no directional exit-attempt leg")
    if direction is ZouShiDirection.UP:
        return max(attempts, key=lambda leg: (leg.end_price, leg.source_index))
    return min(attempts, key=lambda leg: (leg.end_price, -leg.source_index))


def _trace_from_dependencies(
    dependencies: Sequence[Any],
    *,
    rule_id: str,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    traces = [item.trace for item in dependencies if item.trace is not None]
    source_from = [
        trace.source_from_ts
        for trace in traces
        if trace.source_from_ts is not None
    ]
    source_to = [
        trace.source_to_ts for trace in traces if trace.source_to_ts is not None
    ]
    merged_from = [
        trace.merged_from_index
        for trace in traces
        if trace.merged_from_index is not None
    ]
    merged_to = [
        trace.merged_to_index
        for trace in traces
        if trace.merged_to_index is not None
    ]
    dep_to = [
        trace.dep_to_index for trace in traces if trace.dep_to_index is not None
    ]
    return StructTrace(
        algo_card_id=_V2_ALGO_CARD_ID,
        rule_id=rule_id,
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=(
            min(source_from)
            if source_from
            else min(item.start_ts for item in dependencies)
        ),
        source_to_ts=(
            max(source_to)
            if source_to
            else max(item.end_ts for item in dependencies)
        ),
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=max(merged_to) if merged_to else None,
        dep_to_index=max(dep_to) if dep_to else None,
    )


def _zhongshu_strict_direction(
    left: ZhongShu, right: ZhongShu
) -> ZouShiDirection | None:
    if right.dd > left.gg:
        return ZouShiDirection.UP
    if right.gg < left.dd:
        return ZouShiDirection.DOWN
    return None


def _make_level_zoushi(
    run: Sequence[LevelLeg],
    member_zhongshus: Sequence[ZhongShu],
    *,
    direction: ZouShiDirection | None,
    evidence: ZhongShu | None,
    source_evidence: LevelLeg | None = None,
    exit_direction_override: ZouShiDirection | None,
    start_position_override: int | None,
    profile_id: str,
    config_hash: str | None,
) -> CompletedZouShi:
    if evidence is not None and source_evidence is not None:
        raise ValueError("zoushi close evidence must be zhongshu or source leg, not both")
    source_position = {leg.source_index: index for index, leg in enumerate(run)}
    first_center = member_zhongshus[0]
    last_center = member_zhongshus[-1]
    natural_start_position = _leg_position(
        source_position,
        first_center.entry_evidence_index,
        role="entry_evidence_index",
    )
    start_position = (
        natural_start_position
        if start_position_override is None
        else start_position_override
    )
    if not 0 <= start_position < len(run):
        raise ValueError("shared zoushi start is outside the supplied leg run")
    start_leg = run[start_position]
    if evidence is None and source_evidence is None:
        boundary_position = None
        completion_state = ZouShiBoundaryState.FORMING
        close_evidence_id = None
        close_evidence_source_id = None
        observed_members = list(run[start_position:])
        dependencies: list[Any] = [*observed_members, *member_zhongshus]
        rule_id = RULE_ZOUSHI_V2_FORMING
    elif evidence is not None:
        boundary_position = _leg_position(
            source_position,
            evidence.start_index,
            role="close_evidence_start_index",
        )
        boundary_end_position = _leg_position(
            source_position,
            evidence.end_index,
            role="close_evidence_end_index",
        )
        completion_state = ZouShiBoundaryState.FROZEN
        close_evidence_id = evidence.id
        close_evidence_source_id = None
        dependencies = [
            *run[start_position : boundary_end_position + 1],
            *member_zhongshus,
        ]
        rule_id = (
            RULE_ZOUSHI_V2_FREEZE_TREND
            if direction is not None
            else RULE_ZOUSHI_V2_FREEZE_CONSOLIDATION
        )
    else:
        assert source_evidence is not None
        boundary_position = source_position[source_evidence.source_index]
        boundary_end_position = boundary_position
        completion_state = ZouShiBoundaryState.FROZEN
        close_evidence_id = None
        close_evidence_source_id = source_evidence.source_id
        dependencies = [
            *run[start_position : boundary_end_position + 1],
            *member_zhongshus,
        ]
        rule_id = RULE_ZOUSHI_V2_FREEZE_EXIT_BREAK
    last_center_start = max(
        start_position,
        _leg_position(
            source_position,
            last_center.entry_evidence_index,
            role="last_member_entry_evidence_index",
        ),
    )
    # 右侧中枢只是确认“旧走势不再延续”的证据，不属于旧走势成员。
    # 旧走势的极值仍可出现在最后成员中枢结束之后、右证据核心开始之时，
    # 因此 frozen 搜索到 evidence.start_index（含）即可；完整 evidence 只进 trace。
    if evidence is None and source_evidence is None:
        lifecycle_end = len(run) - 1
    else:
        assert boundary_position is not None
        lifecycle_end = boundary_position
    if exit_direction_override is not None:
        exit_direction = exit_direction_override
    elif direction is not None:
        exit_direction = direction
    elif evidence is None:
        exit_direction = (
            ZouShiDirection.UP
            if run[-1].direction is BiDir.UP
            else ZouShiDirection.DOWN
        )
    else:
        raise ValueError("frozen consolidation requires an explicit exit direction")
    end_leg = _direction_extreme_leg(
        run,
        start_position=last_center_start,
        end_position=lifecycle_end,
        direction=exit_direction,
    )
    end = _level_endpoint(end_leg, at_start=False)
    end_position = source_position[end_leg.source_index]
    # frozen 的共享中枢极值之后属于下一走势；forming 尚无右侧分界，
    # 因而保留当前已观察到的全部部件作为可变成员。
    source_members = (
        observed_members
        if boundary_position is None
        else list(run[start_position : end_position + 1])
    )
    kind = ZouShiKind.TREND if direction is not None else ZouShiKind.CONSOLIDATION
    return CompletedZouShi(
        period=start_leg.period,
        level=start_leg.level,
        source_type=start_leg.source_type,
        kind=kind,
        trend_direction=direction,
        start=_level_endpoint(start_leg, at_start=True),
        end=end,
        start_source_id=start_leg.source_id,
        source_member_ids=tuple(item.source_id for item in source_members),
        zhongshu_ids=tuple(item.id for item in member_zhongshus),
        completion_state=completion_state,
        close_evidence_zhongshu_id=close_evidence_id,
        close_evidence_source_id=close_evidence_source_id,
        trace=_trace_from_dependencies(
            dependencies,
            rule_id=rule_id,
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def _make_same_level_consolidation(
    run: Sequence[LevelLeg],
    center: ZhongShu,
    *,
    evidence: ZhongShu | None,
    start_position: int,
    profile_id: str,
    config_hash: str | None,
) -> CompletedZouShi:
    """构造同级分解中的单中枢盘整。

    第 38 课口径下，相邻重叠中枢不是延伸，而是“盘整 + 盘整”。右中枢
    三核心成立时，左盘整固定结束在自身核心 C 终点；最右活动盘整则继续
    画到当前已确认部件末端，等待下一中枢决定最终边界。
    """
    source_position = {leg.source_index: index for index, leg in enumerate(run)}
    core_end_position = _leg_position(
        source_position,
        center.end_index,
        role="same_level_center_end_index",
    )
    if not 0 <= start_position <= core_end_position:
        raise ValueError("same-level consolidation start is outside its center")
    start_leg = run[start_position]
    if evidence is None:
        end_position = len(run) - 1
        completion_state = ZouShiBoundaryState.FORMING
        close_evidence_id = None
        dependencies: list[Any] = [*run[start_position:]]
        rule_id = RULE_ZOUSHI_V2_FORMING
    else:
        end_position = core_end_position
        completion_state = ZouShiBoundaryState.FROZEN
        close_evidence_id = evidence.id
        evidence_end_position = _leg_position(
            source_position,
            evidence.end_index,
            role="same_level_close_evidence_event_index",
        )
        # 依赖水位锁在右中枢核心 C 的确认笔；不要嵌套 evidence.trace，
        # 因为右中枢未来由 open→closed 时其自身 trace 仍会增长。
        dependencies = [*run[start_position : evidence_end_position + 1]]
        rule_id = RULE_ZOUSHI_V2_FREEZE_CONSOLIDATION
    end_leg = run[end_position]
    source_members = run[start_position : end_position + 1]
    return CompletedZouShi(
        period=start_leg.period,
        level=start_leg.level,
        source_type=start_leg.source_type,
        kind=ZouShiKind.CONSOLIDATION,
        trend_direction=None,
        start=_level_endpoint(start_leg, at_start=True),
        end=_level_endpoint(end_leg, at_start=False),
        start_source_id=start_leg.source_id,
        source_member_ids=tuple(item.source_id for item in source_members),
        zhongshu_ids=(center.id,),
        completion_state=completion_state,
        close_evidence_zhongshu_id=close_evidence_id,
        trace=_trace_from_dependencies(
            dependencies,
            rule_id=rule_id,
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def _build_same_level_zoushis_for_run(
    run: Sequence[LevelLeg],
    zhongshus: Sequence[ZhongShu],
    *,
    profile_id: str,
    config_hash: str | None,
) -> list[CompletedZouShi]:
    """第 38 课同级分解：重叠中枢切成盘整+盘整，严格同向才升级趋势。"""
    if not zhongshus:
        return []
    out: list[CompletedZouShi] = []
    source_position = {leg.source_index: index for index, leg in enumerate(run)}
    member_zhongshus: list[ZhongShu] = [zhongshus[0]]
    direction: ZouShiDirection | None = None
    start_position = _leg_position(
        source_position,
        zhongshus[0].entry_evidence_index,
        role="same_level_first_entry_index",
    )

    for item in zhongshus[1:]:
        strict_direction = _zhongshu_strict_direction(member_zhongshus[-1], item)
        if direction is None and strict_direction is not None:
            member_zhongshus.append(item)
            direction = strict_direction
            continue
        if direction is not None and strict_direction is direction:
            member_zhongshus.append(item)
            continue

        if direction is None:
            completed = _make_same_level_consolidation(
                run,
                member_zhongshus[0],
                evidence=item,
                start_position=start_position,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        else:
            completed = _make_level_zoushi(
                run,
                member_zhongshus,
                direction=direction,
                evidence=item,
                exit_direction_override=direction,
                start_position_override=start_position,
                profile_id=profile_id,
                config_hash=config_hash,
            )
            evidence_end_position = _leg_position(
                source_position,
                item.end_index,
                role="same_level_trend_close_event_index",
            )
            completed = replace(
                completed,
                trace=_trace_from_dependencies(
                    run[start_position : evidence_end_position + 1],
                    rule_id=RULE_ZOUSHI_V2_FREEZE_TREND,
                    profile_id=profile_id,
                    config_hash=config_hash,
                ),
            )
        out.append(completed)
        start_position = source_position[completed.end.source_index] + 1
        if start_position >= len(run):
            return out
        member_zhongshus = [item]
        direction = None

    if direction is None:
        out.append(
            _make_same_level_consolidation(
                run,
                member_zhongshus[0],
                evidence=None,
                start_position=start_position,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        )
    else:
        out.append(
            _make_level_zoushi(
                run,
                member_zhongshus,
                direction=direction,
                evidence=None,
                exit_direction_override=direction,
                start_position_override=start_position,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        )
    return out


_LEVEL_KERNEL_RULES = ZouShiKernelRuleIds(
    forming=RULE_ZOUSHI_V2_FORMING,
    freeze_trend=RULE_ZOUSHI_V2_FREEZE_TREND,
    freeze_consolidation=RULE_ZOUSHI_V2_FREEZE_CONSOLIDATION,
    freeze_exit_break=RULE_ZOUSHI_V2_FREEZE_EXIT_BREAK,
)


def _kernel_level_leg(item: LevelLeg) -> ZouShiKernelLeg:
    direction = (
        ZouShiDirection.UP if item.direction is BiDir.UP else ZouShiDirection.DOWN
    )
    return ZouShiKernelLeg(
        id=item.source_id,
        position=item.source_index,
        direction=direction,
        start=_level_endpoint(item, at_start=True),
        end=_level_endpoint(item, at_start=False),
        high=item.high,
        low=item.low,
        trace=item.trace,
    )


def _kernel_level_center(
    item: ZhongShu,
    center_position: int,
    source_position: dict[int, int],
) -> ZouShiKernelCenter:
    close_position = (
        None
        if item.close_evidence_index is None
        else _leg_position(
            source_position,
            item.close_evidence_index,
            role="kernel_close_evidence_index",
        )
    )
    return ZouShiKernelCenter(
        id=item.id,
        position=center_position,
        entry_position=_leg_position(
            source_position, item.entry_evidence_index, role="kernel_entry_index"
        ),
        core_start_position=_leg_position(
            source_position, item.start_index, role="kernel_core_start_index"
        ),
        core_event_position=_leg_position(
            source_position, item.start_index + 2, role="kernel_core_event_index"
        ),
        member_end_position=_leg_position(
            source_position, item.end_index, role="kernel_member_end_index"
        ),
        zg=item.zg,
        zd=item.zd,
        gg=item.gg,
        dd=item.dd,
        extension_state=item.extension_state,
        close_evidence_position=close_position,
        member_ids=item.core_member_ids + item.extended_member_ids,
        trace=item.trace,
    )


def _completed_from_kernel_slice(
    run: Sequence[LevelLeg],
    centers: Sequence[ZhongShu],
    center_positions: Sequence[int],
    item: ZouShiKernelSlice,
    *,
    profile_id: str,
    config_hash: str | None,
) -> CompletedZouShi:
    leg_by_position = {leg.source_index: leg for leg in run}
    local_by_position = {
        leg.source_index: position for position, leg in enumerate(run)
    }
    center_by_position = dict(zip(center_positions, centers, strict=True))
    start_leg = leg_by_position[item.start_position]
    end_leg = leg_by_position[item.end_position]
    member_centers = [center_by_position[position] for position in item.center_positions]
    evidence_center: ZhongShu | None = None
    evidence_leg: LevelLeg | None = None
    if item.close_evidence is not None:
        if item.close_evidence.kind == "zhongshu":
            evidence_center = next(
                center for center in centers if center.id == item.close_evidence.id
            )
        else:
            evidence_leg = leg_by_position[item.close_evidence.event_position]
    if evidence_center is not None:
        dependency_end = local_by_position[evidence_center.end_index]
    elif evidence_leg is not None:
        dependency_end = local_by_position[item.close_evidence.event_position]  # type: ignore[union-attr]
    else:
        dependency_end = len(run) - 1
    dependency_start = local_by_position[item.start_position]
    dependencies: list[Any] = [
        *run[dependency_start : dependency_end + 1],
        *member_centers,
    ]
    return CompletedZouShi(
        period=start_leg.period,
        level=start_leg.level,
        source_type=start_leg.source_type,
        kind=item.kind,
        trend_direction=item.direction,
        start=_level_endpoint(start_leg, at_start=True),
        end=_level_endpoint(end_leg, at_start=False),
        start_source_id=start_leg.source_id,
        source_member_ids=tuple(
            leg_by_position[position].source_id for position in item.source_positions
        ),
        zhongshu_ids=tuple(center.id for center in member_centers),
        completion_state=item.completion_state,
        close_evidence_zhongshu_id=(
            evidence_center.id if evidence_center is not None else None
        ),
        close_evidence_source_id=(evidence_leg.source_id if evidence_leg is not None else None),
        trace=_trace_from_dependencies(
            dependencies,
            rule_id=item.primary_rule_id,
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def _build_extend_zoushis_with_kernel(
    run: Sequence[LevelLeg],
    zhongshus: Sequence[ZhongShu],
    center_positions: Sequence[int],
    *,
    profile_id: str,
    config_hash: str | None,
) -> list[CompletedZouShi]:
    if len(zhongshus) != len(center_positions):
        raise ValueError("kernel center positions must match official zhongshus")
    source_position = {leg.source_index: leg.source_index for leg in run}
    kernel_legs = tuple(_kernel_level_leg(leg) for leg in run)
    kernel_centers = tuple(
        _kernel_level_center(center, position, source_position)
        for position, center in zip(center_positions, zhongshus, strict=True)
    )
    return [
        _completed_from_kernel_slice(
            run,
            zhongshus,
            center_positions,
            item,
            profile_id=profile_id,
            config_hash=config_hash,
        )
        for item in build_zoushi_kernel_slices(
            kernel_legs,
            kernel_centers,
            rules=_LEVEL_KERNEL_RULES,
        )
    ]


def _build_zoushis_for_run(
    run: Sequence[LevelLeg],
    zhongshus: Sequence[ZhongShu],
    center_positions: Sequence[int],
    *,
    profile_id: str,
    config_hash: str | None,
) -> list[CompletedZouShi]:
    if not zhongshus:
        return []
    modes = {item.mode for item in zhongshus}
    if len(modes) != 1:
        raise ValueError("official zhongshus must share one decomposition mode")
    if ZhongShuMode.SAME_LEVEL in modes:
        return _build_same_level_zoushis_for_run(
            run,
            zhongshus,
            profile_id=profile_id,
            config_hash=config_hash,
        )
    return _build_extend_zoushis_with_kernel(
        run,
        zhongshus,
        center_positions,
        profile_id=profile_id,
        config_hash=config_hash,
    )

def build_zoushis_from_zhongshus(
    legs: Sequence[LevelLeg],
    zhongshus: Sequence[ZhongShu],
    *,
    level: ZouShiLevel,
    source_type: ZhongShuSource,
    profile_id: str,
    config_hash: str | None,
    zhongshu_mode: ZhongShuMode | None = None,
) -> LevelBuildResult:
    """从中枢层正式结果构建走势，不允许静默替换正式中枢。

    ``same_level`` 的 Engine 正式路径复用一次共享构建结果；本兼容纯函数
    入口只重放同一状态机以逐对象校验传入中枢，任何差异都显式拒绝。
    当正式中枢可能为空时，调用方必须显式传入 ``zhongshu_mode``，避免
    空列表丢失其口径身份。
    """
    resolved_level = ZouShiLevel(level)
    resolved_source = ZhongShuSource(source_type)
    source = list(legs)
    centers = list(zhongshus)
    resolved_mode = ZhongShuMode(zhongshu_mode) if zhongshu_mode is not None else None
    if any(
        item.level is not resolved_level or item.source_type is not resolved_source
        for item in source
    ):
        raise ValueError("level legs must share the requested level and source_type")
    if any(
        item.source_type is not resolved_source
        or (source and item.period != source[0].period)
        for item in centers
    ):
        raise ValueError("zoushis must consume matching official zhongshus")
    if any(
        right.start_index <= left.start_index
        for left, right in zip(centers, centers[1:], strict=False)
    ):
        raise ValueError("official zhongshus must be ordered by start_index")

    inferred_modes = {item.mode for item in centers}
    if resolved_mode is not None and any(item.mode is not resolved_mode for item in centers):
        raise ValueError("official zhongshus do not match the requested mode")
    if resolved_mode is None and len(inferred_modes) == 1:
        resolved_mode = next(iter(inferred_modes))

    if resolved_mode is ZhongShuMode.SAME_LEVEL:
        # 兼容纯函数入口会重放同一状态机，但只用于验证调用方传入的正式
        # 中枢逐对象完全一致；不一致必须显式拒绝，绝不静默替换。Engine
        # 正式路径直接缓存同一个 LevelBuildResult，不会走这里二次扫描。
        canonical = build_same_level_result(
            source,
            profile_id=profile_id,
            config_hash=config_hash,
        )
        if canonical.zhongshus != tuple(centers):
            raise ValueError(
                "same-level official zhongshus do not match the shared state result"
            )
        return canonical

    all_zoushis: list[CompletedZouShi] = []
    same_level_mode = resolved_mode is ZhongShuMode.SAME_LEVEL
    center_index = 0
    run_start = 0
    for index in range(1, len(source) + 1):
        if index < len(source) and _level_continuous(source[index - 1], source[index]):
            continue
        run = source[run_start:index]
        run_centers: list[ZhongShu] = []
        run_center_positions: list[int] = []
        if run:
            first_source_index = run[0].source_index
            last_source_index = run[-1].source_index
            while (
                center_index < len(centers)
                and centers[center_index].start_index <= last_source_index
            ):
                center = centers[center_index]
                if (
                    center.start_index < first_source_index
                    or center.end_index > last_source_index
                ):
                    raise ValueError("official zhongshu crosses a discontinuous leg run")
                run_center_positions.append(center_index)
                run_centers.append(center)
                center_index += 1
        run_zoushis = _build_zoushis_for_run(
            run,
            run_centers,
            run_center_positions,
            profile_id=profile_id,
            config_hash=config_hash,
        )
        for left, right in zip(run_zoushis, run_zoushis[1:], strict=False):
            if (
                not same_level_mode
                and left.zhongshu_ids[-1] != right.zhongshu_ids[0]
            ):
                raise ValueError("adjacent zoushis must share one boundary zhongshu")
            if (left.end.ts, left.end.price) != (right.start.ts, right.start.price):
                raise ValueError("adjacent zoushis must share one boundary coordinate")
        all_zoushis.extend(run_zoushis)
        run_start = index
    if center_index != len(centers):
        raise ValueError("official zhongshu is outside the supplied leg prefix")
    all_zoushis.sort(key=lambda item: (item.start.source_index, item.end.source_index, item.id))
    return LevelBuildResult(
        level=resolved_level,
        source_type=resolved_source,
        legs=tuple(source),
        zhongshus=tuple(centers),
        zoushis=tuple(all_zoushis),
    )


def build_l0_zoushis(
    bis: Sequence[Bi],
    n_merged: int,
    zhongshus: Sequence[ZhongShu],
    *,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> LevelBuildResult:
    """把最长 confirmed 笔前缀适配为 L0，并消费中枢层正式结果。"""
    legs: list[LevelLeg] = []
    for index, (bi, confirmed) in enumerate(
        zip(bis, bi_confirmed_flags(bis, n_merged), strict=True)
    ):
        if not confirmed:
            break
        legs.append(
            LevelLeg(
                period=period,
                level=ZouShiLevel.L0,
                source_type=ZhongShuSource.BI,
                source_id=bi.id,
                source_index=index,
                direction=bi.direction,
                start_ts=bi.start_ts,
                end_ts=bi.end_ts,
                start_price=bi.start_price,
                end_price=bi.end_price,
                high=bi.high,
                low=bi.low,
                trace=bi.trace,
            )
        )
    return build_zoushis_from_zhongshus(
        legs,
        zhongshus,
        level=ZouShiLevel.L0,
        source_type=ZhongShuSource.BI,
        profile_id=profile_id,
        config_hash=config_hash,
    )


def build_l1_zoushis(
    xianduans: Sequence[Xianduan],
    zhongshus: Sequence[ZhongShu],
    *,
    cfg: ChanConfig,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> LevelBuildResult:
    """把 standard Engine 的最长 frozen 线段前缀适配为 L1。"""
    selected = select_l1_frozen_xianduan_prefix(xianduans, cfg)
    legs = [
        LevelLeg(
            period=period,
            level=ZouShiLevel.L1,
            source_type=ZhongShuSource.XIANDUAN,
            source_id=item.id,
            source_index=index,
            direction=item.direction,
            start_ts=item.start_ts,
            end_ts=item.end_ts,
            start_price=item.start_price,
            end_price=item.end_price,
            high=item.high,
            low=item.low,
            trace=item.trace,
        )
        for index, item in enumerate(selected)
    ]
    return build_zoushis_from_zhongshus(
        legs,
        zhongshus,
        level=ZouShiLevel.L1,
        source_type=ZhongShuSource.XIANDUAN,
        profile_id=profile_id,
        config_hash=config_hash,
    )
