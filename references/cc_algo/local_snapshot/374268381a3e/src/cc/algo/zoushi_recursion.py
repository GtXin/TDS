"""PR-21 Gate B1：frozen 完成走势递归形成高一级中枢。"""

from __future__ import annotations

from collections.abc import Sequence

from cc.algo.models import (
    LevelBuildResult,
    RecursiveLeg,
    RecursiveOrigin,
    RecursiveZhongShu,
    RecursiveZouShi,
    ZhongShuMode,
    ZhongShuSource,
    ZhongShuState,
    ZouShiBoundaryState,
    ZouShiDirection,
    ZouShiKind,
    ZouShiLevel,
)
from cc.algo.trace import (
    RULE_RECURSIVE_ZOUSHI_EXTEND_SAME_DIRECTION,
    RULE_RECURSIVE_ZOUSHI_FORM_CONSOLIDATION,
    RULE_RECURSIVE_ZOUSHI_FORM_SHARED_TURN,
    RULE_RECURSIVE_ZOUSHI_FREEZE_SHARED_TURN,
    RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION,
    RULE_RECURSIVE_ZOUSHI_UPGRADE_STRICT,
    RULE_RECURSIVE_ZS_EXTEND_OVERLAP,
    RULE_RECURSIVE_ZS_FORM_ENTRY_OVERLAP3,
    StructTrace,
)
from cc.algo.zhongshu_phase import (
    resolve_initial_zhongshu_phase,
    scan_zhongshu_candidate,
)
from cc.algo.zoushi_kernel import (
    ZouShiKernelCenter,
    ZouShiKernelLeg,
    ZouShiKernelRuleIds,
    ZouShiKernelSlice,
    build_zoushi_kernel_slices,
)

RECURSIVE_ZHONGSHU_ALGO_VERSION = 2
RECURSIVE_ZOUSHI_ALGO_VERSION = 4
_ALGO_CARD_ID = "zoushi-recursion-v1"


def _overlap(low_a: float, high_a: float, low_b: float, high_b: float) -> bool:
    """闭区间重叠；相切成立，不使用隐藏 epsilon。"""
    return max(low_a, low_b) <= min(high_a, high_b)


def _continuous(a: RecursiveLeg, b: RecursiveLeg) -> bool:
    return (
        a.origin_level is b.origin_level
        and a.source_depth == b.source_depth
        and a.source_position + 1 == b.source_position
        and a.end.ts == b.start.ts
        and a.end.price == b.start.price
        and a.end.source_index <= b.start.source_index
        and a.direction is not b.direction
    )


def _trace_for_center(
    entry: RecursiveLeg,
    members: Sequence[RecursiveLeg],
    evidence: RecursiveLeg | None,
    *,
    extended: bool,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    deps = [entry, *members, *([evidence] if evidence is not None else [])]
    source_from = [
        leg.trace.source_from_ts
        if leg.trace is not None and leg.trace.source_from_ts is not None
        else leg.start.ts
        for leg in deps
    ]
    source_to = [
        leg.trace.source_to_ts
        if leg.trace is not None and leg.trace.source_to_ts is not None
        else leg.end.ts
        for leg in deps
    ]
    merged_from = [
        leg.trace.merged_from_index
        for leg in deps
        if leg.trace is not None and leg.trace.merged_from_index is not None
    ]
    merged_to = [
        leg.trace.merged_to_index
        for leg in deps
        if leg.trace is not None and leg.trace.merged_to_index is not None
    ]
    dep_to = [
        leg.trace.dep_to_index
        for leg in deps
        if leg.trace is not None and leg.trace.dep_to_index is not None
    ]
    return StructTrace(
        algo_card_id=_ALGO_CARD_ID,
        rule_id=(
            RULE_RECURSIVE_ZS_EXTEND_OVERLAP
            if extended
            else RULE_RECURSIVE_ZS_FORM_ENTRY_OVERLAP3
        ),
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=min(source_from),
        source_to_ts=max(source_to),
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=max(merged_to) if merged_to else None,
        dep_to_index=max(dep_to) if dep_to else None,
    )


def _restart_index(
    legs: Sequence[RecursiveLeg], j: int, zd: float, zg: float
) -> tuple[int, ZouShiDirection]:
    evidence = legs[j]
    if evidence.low > zg:
        exit_direction = ZouShiDirection.UP
    elif evidence.high < zd:
        exit_direction = ZouShiDirection.DOWN
    else:  # pragma: no cover - 调用者只会传入与核心不重叠的证据
        raise ValueError("recursive close evidence must be outside the core")
    preceding = j - 1
    if legs[preceding].direction is exit_direction:
        return preceding, exit_direction
    return max(0, j - 2), exit_direction


def _build_run(
    legs: Sequence[RecursiveLeg],
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    zhongshu_mode: ZhongShuMode,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[RecursiveZhongShu]:
    out: list[RecursiveZhongShu] = []
    i = 0
    required_entry_direction: ZouShiDirection | None = None
    while i + 3 < len(legs):
        candidate = scan_zhongshu_candidate(legs, i)
        if candidate is None:
            i += 1
            continue
        entry = legs[candidate.entry_index]
        if (
            required_entry_direction is not None
            and entry.direction is not required_entry_direction
        ):
            i += 1
            continue
        if required_entry_direction is None:
            candidate = resolve_initial_zhongshu_phase(legs, candidate)
            entry = legs[candidate.entry_index]

        a, b, c = (legs[index] for index in candidate.core_indexes)
        extended = [legs[index] for index in candidate.extended_indexes]
        members: list[RecursiveLeg] = [a, b, c, *extended]
        evidence = (
            legs[candidate.close_index]
            if candidate.close_index is not None
            else None
        )

        state = ZhongShuState.CLOSED if evidence is not None else ZhongShuState.OPEN
        out.append(
            RecursiveZhongShu(
                period=period,
                origin_level=origin_level,
                depth=depth,
                logical_level=(
                    f"l{(0 if origin_level is RecursiveOrigin.L0 else 1) + depth}"
                ),
                zhongshu_mode=zhongshu_mode,
                direction=a.direction,
                zg=candidate.zg,
                zd=candidate.zd,
                gg=candidate.gg,
                dd=candidate.dd,
                start_ts=a.start.ts,
                core_end_ts=c.end.ts,
                end_ts=members[-1].end.ts,
                start_index=a.source_position,
                end_index=members[-1].source_position,
                core_member_ids=(
                    a.source_zoushi_id,
                    b.source_zoushi_id,
                    c.source_zoushi_id,
                ),
                extended_member_ids=tuple(
                    leg.source_zoushi_id for leg in extended
                ),
                member_count=len(members),
                entry_evidence_id=entry.source_zoushi_id,
                entry_evidence_index=entry.source_position,
                extension_state=state,
                close_evidence_id=(
                    evidence.source_zoushi_id if evidence is not None else None
                ),
                close_evidence_index=(
                    evidence.source_position if evidence is not None else None
                ),
                trace=_trace_for_center(
                    entry,
                    members,
                    evidence,
                    extended=bool(extended),
                    profile_id=profile_id,
                    config_hash=config_hash,
                ),
            )
        )
        if evidence is None:
            break
        assert candidate.close_index is not None
        i, required_entry_direction = _restart_index(
            legs,
            candidate.close_index,
            candidate.zd,
            candidate.zg,
        )
    return out


def build_recursive_zhongshus(
    legs: Sequence[RecursiveLeg],
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    zhongshu_mode: ZhongShuMode | str,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[RecursiveZhongShu]:
    """从左到右在每个连续 run 内构建 depth=1 递归中枢。"""
    origin = RecursiveOrigin(origin_level)
    mode = ZhongShuMode(zhongshu_mode)
    if depth != 1:
        raise ValueError("Gate B1 only implements recursive depth=1")
    if mode is not ZhongShuMode.EXTEND:
        raise ValueError("recursive zhongshu requires extend mode")
    for leg in legs:
        if leg.origin_level is not origin or leg.source_depth != depth - 1:
            raise ValueError("recursive leg identity does not match requested level key")
        if leg.period != period:
            raise ValueError("recursive leg period does not match requested period")
    out: list[RecursiveZhongShu] = []
    run_start = 0
    for index in range(1, len(legs)):
        if _continuous(legs[index - 1], legs[index]):
            continue
        out.extend(
            _build_run(
                legs[run_start:index],
                origin_level=origin,
                depth=depth,
                zhongshu_mode=mode,
                period=period,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        )
        run_start = index
    out.extend(
        _build_run(
            legs[run_start:],
            origin_level=origin,
            depth=depth,
            zhongshu_mode=mode,
            period=period,
            profile_id=profile_id,
            config_hash=config_hash,
        )
    )
    return out


def _origin_level(origin: RecursiveOrigin) -> ZouShiLevel:
    return ZouShiLevel.L0 if origin is RecursiveOrigin.L0 else ZouShiLevel.L1


def recursive_leg_runs_from_level_result(
    result: LevelBuildResult,
    *,
    origin_level: RecursiveOrigin,
) -> tuple[tuple[RecursiveLeg, ...], ...]:
    """把同次低一级构建结果投影成连续 frozen 递归输入 run。"""
    origin = RecursiveOrigin(origin_level)
    if result.level is not _origin_level(origin):
        raise ValueError("recursive origin does not match level build result")
    expected_source = (
        ZhongShuSource.BI
        if origin is RecursiveOrigin.L0
        else ZhongShuSource.XIANDUAN
    )
    if result.source_type is not expected_source:
        raise ValueError("recursive origin does not match level source type")

    leg_positions: dict[str, list[int]] = {}
    for position, leg in enumerate(result.legs):
        leg_positions.setdefault(leg.source_id, []).append(position)

    source_run: list[int] = []
    run_id = 0
    for position, leg in enumerate(result.legs):
        if position:
            previous = result.legs[position - 1]
            if not (
                previous.source_index + 1 == leg.source_index
                and previous.end_ts == leg.start_ts
                and previous.end_price == leg.start_price
                and previous.direction is not leg.direction
            ):
                run_id += 1
        source_run.append(run_id)

    runs: list[list[RecursiveLeg]] = []
    current: list[RecursiveLeg] = []
    current_source_run: int | None = None
    for source_position, item in enumerate(result.zoushis):
        if item.level is not result.level or item.source_type is not result.source_type:
            raise ValueError("recursive source zoushi does not match level result")
        if item.completion_state is not ZouShiBoundaryState.FROZEN:
            if current:
                runs.append(current)
                current = []
            current_source_run = None
            continue
        positions: list[int] = []
        seen: set[str] = set()
        for member_id in item.source_member_ids:
            if member_id in seen:
                raise ValueError("recursive source member id is duplicated")
            seen.add(member_id)
            matches = leg_positions.get(member_id, [])
            if len(matches) != 1:
                raise ValueError("recursive source member id must resolve exactly once")
            positions.append(matches[0])
        if any(
            left >= right
            for left, right in zip(positions, positions[1:], strict=False)
        ):
            raise ValueError("recursive source members must be strictly increasing")
        if len({source_run[position] for position in positions}) != 1:
            raise ValueError("recursive source members must not cross a source run")
        item_source_run = source_run[positions[0]]
        if item.start.price == item.end.price:
            if current:
                runs.append(current)
                current = []
            current_source_run = None
            continue
        direction = (
            ZouShiDirection.UP
            if item.end.price > item.start.price
            else ZouShiDirection.DOWN
        )
        members = [result.legs[position] for position in positions]
        if any(
            member.level is not result.level
            or member.source_type is not result.source_type
            or member.period != item.period
            for member in members
        ):
            raise ValueError("recursive source member does not match level result")
        projected = RecursiveLeg(
            period=item.period,
            origin_level=origin,
            source_depth=0,
            source_zoushi_id=item.id,
            source_position=source_position,
            start=item.start,
            end=item.end,
            direction=direction,
            high=max(member.high for member in members),
            low=min(member.low for member in members),
            source_member_ids=item.source_member_ids,
            trace=item.trace,
        )
        if current and (
            current_source_run != item_source_run
            or not _continuous(current[-1], projected)
        ):
            runs.append(current)
            current = []
        if not current:
            current_source_run = item_source_run
        current.append(projected)
    if current:
        runs.append(current)
    return tuple(tuple(run) for run in runs)


def build_recursive_zhongshus_from_level_result(
    result: LevelBuildResult,
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    zhongshu_mode: ZhongShuMode,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[RecursiveZhongShu]:
    """复用低一级正式构建结果，不重算笔、线段、中枢或走势。"""
    out: list[RecursiveZhongShu] = []
    for run in recursive_leg_runs_from_level_result(
        result, origin_level=origin_level
    ):
        out.extend(
            build_recursive_zhongshus(
                run,
                origin_level=origin_level,
                depth=depth,
                zhongshu_mode=zhongshu_mode,
                period=period,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        )
    return out


_RECURSIVE_KERNEL_RULES = ZouShiKernelRuleIds(
    forming=RULE_RECURSIVE_ZOUSHI_FORM_CONSOLIDATION,
    freeze_trend=RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION,
    freeze_consolidation=RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION,
    freeze_exit_break=RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION,
    forming_shared_turn=RULE_RECURSIVE_ZOUSHI_FORM_SHARED_TURN,
    freeze_shared_turn=RULE_RECURSIVE_ZOUSHI_FREEZE_SHARED_TURN,
)


def _kernel_recursive_leg(item: RecursiveLeg) -> ZouShiKernelLeg:
    return ZouShiKernelLeg(
        id=item.source_zoushi_id,
        position=item.source_position,
        direction=item.direction,
        start=item.start,
        end=item.end,
        high=item.high,
        low=item.low,
        trace=item.trace,
    )


def _kernel_recursive_center(
    item: RecursiveZhongShu, center_position: int
) -> ZouShiKernelCenter:
    return ZouShiKernelCenter(
        id=item.id,
        position=center_position,
        entry_position=item.entry_evidence_index,
        core_start_position=item.start_index,
        core_event_position=item.start_index + 2,
        member_end_position=item.end_index,
        zg=item.zg,
        zd=item.zd,
        gg=item.gg,
        dd=item.dd,
        extension_state=item.extension_state,
        close_evidence_position=item.close_evidence_index,
        member_ids=item.core_member_ids + item.extended_member_ids,
        trace=item.trace,
    )


def _trace_for_zoushi(
    legs: Sequence[RecursiveLeg],
    centers: Sequence[RecursiveZhongShu],
    item: ZouShiKernelSlice,
    *,
    rule_id: str,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    leg_by_position = {leg.source_position: leg for leg in legs}
    center_by_position = {
        position: center for position, center in enumerate(centers)
    }
    deps: list[RecursiveLeg | RecursiveZhongShu] = [
        *(leg_by_position[position] for position in item.source_positions),
        *(center_by_position[position] for position in item.center_positions),
    ]
    if item.close_evidence is not None:
        if item.close_evidence.kind == "source_leg":
            deps.append(leg_by_position[item.close_evidence.event_position])
        else:
            deps.append(
                next(
                    center
                    for center in centers
                    if center.id == item.close_evidence.id
                )
            )
    traces = [dep.trace for dep in deps if dep.trace is not None]
    selected_legs = [leg_by_position[position] for position in item.source_positions]
    source_from = [
        trace.source_from_ts for trace in traces if trace.source_from_ts is not None
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
    source_to_value = (
        max(source_to) if source_to else max(leg.end.ts for leg in selected_legs)
    )
    merged_to_value = max(merged_to) if merged_to else None
    dep_to_value = max(dep_to) if dep_to else None
    if item.trace_horizon_position is not None:
        # 共享分界的正式成员已经在内核中截到 shared extreme。成员中枢仍可能
        # 继续向右延伸，不能把旧走势自身的 source/merged/dep range 越过最后
        # 一个正式成员；冻结时只有显式 close evidence 可以扩大 dep_to。
        member_source_to = [
            leg.trace.source_to_ts
            if leg.trace is not None and leg.trace.source_to_ts is not None
            else leg.end.ts
            for leg in selected_legs
        ]
        source_to_value = min(source_to_value, max(member_source_to))
        member_merged_to = [
            leg.trace.merged_to_index
            for leg in selected_legs
            if leg.trace is not None and leg.trace.merged_to_index is not None
        ]
        # merged_to 是可选坐标；共享 horizon 下只能由正式成员给出。
        # 成员全部未知时必须诚实返回 None，不能借完整中枢的右侧坐标补齐。
        merged_to_value = max(member_merged_to) if member_merged_to else None
        member_dep_to = [
            leg.trace.dep_to_index
            for leg in selected_legs
            if leg.trace is not None and leg.trace.dep_to_index is not None
        ]
        horizon_dep_to = max(member_dep_to) if member_dep_to else None
        evidence_dep_to: int | None = None
        if item.close_evidence is not None:
            if item.close_evidence.kind == "source_leg":
                evidence_trace = leg_by_position[
                    item.close_evidence.event_position
                ].trace
            else:
                evidence_trace = next(
                    center.trace
                    for center in centers
                    if center.id == item.close_evidence.id
                )
            if evidence_trace is not None:
                evidence_dep_to = evidence_trace.dep_to_index
        bounded_dep_to = [
            value
            for value in (horizon_dep_to, evidence_dep_to)
            if value is not None
        ]
        dep_to_value = max(bounded_dep_to) if bounded_dep_to else None
    return StructTrace(
        algo_card_id=_ALGO_CARD_ID,
        rule_id=rule_id,
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=(
            min(source_from) if source_from else min(leg.start.ts for leg in selected_legs)
        ),
        source_to_ts=source_to_value,
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=merged_to_value,
        dep_to_index=dep_to_value,
    )


def _recursive_rule_id(item: ZouShiKernelSlice) -> str:
    if item.primary_rule_id in {
        RULE_RECURSIVE_ZOUSHI_FORM_SHARED_TURN,
        RULE_RECURSIVE_ZOUSHI_FREEZE_SHARED_TURN,
    }:
        return item.primary_rule_id
    if item.completion_state is ZouShiBoundaryState.FROZEN:
        return RULE_RECURSIVE_ZOUSHI_FREEZE_TRANSITION
    if item.kind is ZouShiKind.CONSOLIDATION:
        return RULE_RECURSIVE_ZOUSHI_FORM_CONSOLIDATION
    if len(item.center_positions) == 2:
        return RULE_RECURSIVE_ZOUSHI_UPGRADE_STRICT
    return RULE_RECURSIVE_ZOUSHI_EXTEND_SAME_DIRECTION


def _recursive_from_kernel_slice(
    legs: Sequence[RecursiveLeg],
    centers: Sequence[RecursiveZhongShu],
    item: ZouShiKernelSlice,
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> RecursiveZouShi:
    leg_by_position = {leg.source_position: leg for leg in legs}
    center_by_position = {
        position: center for position, center in enumerate(centers)
    }
    start_leg = leg_by_position[item.start_position]
    end_leg = leg_by_position[item.end_position]
    source_members = tuple(
        leg_by_position[position].source_zoushi_id for position in item.source_positions
    )
    member_centers = tuple(
        center_by_position[position] for position in item.center_positions
    )
    close_center_id: str | None = None
    close_source_id: str | None = None
    if item.close_evidence is not None:
        if item.close_evidence.kind == "zhongshu":
            close_center_id = item.close_evidence.id
        else:
            close_source_id = item.close_evidence.id
    rule_id = _recursive_rule_id(item)
    return RecursiveZouShi(
        period=period,
        origin_level=origin_level,
        depth=depth,
        logical_level=f"l{(0 if origin_level is RecursiveOrigin.L0 else 1) + depth}",
        zhongshu_mode=ZhongShuMode.EXTEND,
        kind=item.kind,
        trend_direction=item.direction,
        start=start_leg.start,
        end=end_leg.end,
        start_source_position=item.start_position,
        end_source_position=item.end_position,
        high=item.high_point.price,
        low=item.low_point.price,
        high_point=item.high_point,
        low_point=item.low_point,
        start_source_id=start_leg.source_zoushi_id,
        source_member_ids=source_members,
        zhongshu_ids=tuple(center.id for center in member_centers),
        member_count=len(source_members),
        completion_state=item.completion_state,
        close_evidence_zhongshu_id=close_center_id,
        close_evidence_source_id=close_source_id,
        trace=_trace_for_zoushi(
            legs,
            centers,
            item,
            rule_id=rule_id,
            profile_id=profile_id,
            config_hash=config_hash,
        ),
    )


def build_recursive_zoushis(
    legs: Sequence[RecursiveLeg],
    zhongshus: Sequence[RecursiveZhongShu],
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    zhongshu_mode: ZhongShuMode | str,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[RecursiveZouShi]:
    """消费正式递归中枢，使用与 L0/L1 相同的走势状态机。"""
    origin = RecursiveOrigin(origin_level)
    mode = ZhongShuMode(zhongshu_mode)
    if depth != 1:
        raise ValueError("Gate B2 only implements recursive zoushi depth=1")
    if mode is not ZhongShuMode.EXTEND:
        raise ValueError("recursive zoushi requires extend mode")
    if any(
        leg.origin_level is not origin
        or leg.source_depth != depth - 1
        or leg.period != period
        for leg in legs
    ):
        raise ValueError("recursive zoushi leg identity does not match level key")
    if any(
        center.origin_level is not origin
        or center.depth != depth
        or center.period != period
        or center.zhongshu_mode is not mode
        for center in zhongshus
    ):
        raise ValueError("recursive zoushi center identity does not match level key")
    if any(
        right.start_index <= left.start_index
        for left, right in zip(zhongshus, zhongshus[1:], strict=False)
    ):
        raise ValueError("recursive zhongshus must be strictly ordered by start_index")

    out: list[RecursiveZouShi] = []
    center_position = {id(center): index for index, center in enumerate(zhongshus)}
    run_start = 0
    center_index = 0
    for index in range(1, len(legs) + 1):
        if index < len(legs) and _continuous(legs[index - 1], legs[index]):
            continue
        run = list(legs[run_start:index])
        run_centers: list[RecursiveZhongShu] = []
        if run:
            first_position = run[0].source_position
            last_position = run[-1].source_position
            while (
                center_index < len(zhongshus)
                and zhongshus[center_index].start_index <= last_position
            ):
                center = zhongshus[center_index]
                if center.start_index < first_position or center.end_index > last_position:
                    raise ValueError("recursive zhongshu crosses a discontinuous source run")
                run_centers.append(center)
                center_index += 1
        kernel_legs = tuple(_kernel_recursive_leg(leg) for leg in run)
        kernel_centers = tuple(
            _kernel_recursive_center(center, center_position[id(center)])
            for center in run_centers
        )
        slices = build_zoushi_kernel_slices(
            kernel_legs,
            kernel_centers,
            rules=_RECURSIVE_KERNEL_RULES,
            extended_center_shared_turn=True,
        )
        out.extend(
            _recursive_from_kernel_slice(
                run,
                zhongshus,
                item,
                origin_level=origin,
                depth=depth,
                period=period,
                profile_id=profile_id,
                config_hash=config_hash,
            )
            for item in slices
        )
        run_start = index
    if center_index != len(zhongshus):
        raise ValueError("recursive zhongshu is outside the source prefix")
    return out


def build_recursive_zoushis_from_level_result(
    result: LevelBuildResult,
    *,
    origin_level: RecursiveOrigin,
    depth: int,
    zhongshu_mode: ZhongShuMode,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[RecursiveZouShi]:
    """从同一低一级正式结果派生递归中枢及递归走势，不重算低层结构。"""
    legs = tuple(
        leg
        for run in recursive_leg_runs_from_level_result(
            result, origin_level=origin_level
        )
        for leg in run
    )
    centers = build_recursive_zhongshus(
        legs,
        origin_level=origin_level,
        depth=depth,
        zhongshu_mode=zhongshu_mode,
        period=period,
        profile_id=profile_id,
        config_hash=config_hash,
    )
    return build_recursive_zoushis(
        legs,
        centers,
        origin_level=origin_level,
        depth=depth,
        zhongshu_mode=zhongshu_mode,
        period=period,
        profile_id=profile_id,
        config_hash=config_hash,
    )
