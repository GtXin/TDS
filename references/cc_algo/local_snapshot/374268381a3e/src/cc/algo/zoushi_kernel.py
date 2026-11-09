"""L0/L1/递归走势共用的类型中立、从左到右状态机。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Literal

from cc.algo.models import (
    ZhongShuState,
    ZouShiBoundaryState,
    ZouShiDirection,
    ZouShiEndpoint,
    ZouShiKernelExtremeRef,
    ZouShiKind,
)
from cc.algo.trace import StructTrace


@dataclass(frozen=True, slots=True)
class ZouShiKernelLeg:
    id: str
    position: int
    direction: ZouShiDirection
    start: ZouShiEndpoint
    end: ZouShiEndpoint
    high: float
    low: float
    high_point: ZouShiKernelExtremeRef | None = None
    low_point: ZouShiKernelExtremeRef | None = None
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.position < 0 or self.low > self.high:
            raise ValueError("invalid zoushi kernel leg")
        if self.start.ts > self.end.ts:
            raise ValueError("kernel leg timestamp range is reversed")
        if not self.low <= self.start.price <= self.high:
            raise ValueError("kernel leg start is outside lifecycle range")
        if not self.low <= self.end.price <= self.high:
            raise ValueError("kernel leg end is outside lifecycle range")
        if self.high_point is None:
            object.__setattr__(
                self,
                "high_point",
                ZouShiKernelExtremeRef(self.id, self.position, self.high),
            )
        if self.low_point is None:
            object.__setattr__(
                self,
                "low_point",
                ZouShiKernelExtremeRef(self.id, self.position, self.low),
            )
        assert self.high_point is not None and self.low_point is not None
        if self.high_point.price != self.high or self.low_point.price != self.low:
            raise ValueError("kernel leg extreme refs must match high/low")

    @property
    def high_ref(self) -> ZouShiKernelExtremeRef:
        assert self.high_point is not None
        return self.high_point

    @property
    def low_ref(self) -> ZouShiKernelExtremeRef:
        assert self.low_point is not None
        return self.low_point


@dataclass(frozen=True, slots=True)
class ZouShiKernelCenter:
    id: str
    position: int
    entry_position: int
    core_start_position: int
    core_event_position: int
    member_end_position: int
    zg: float
    zd: float
    gg: float
    dd: float
    extension_state: ZhongShuState
    close_evidence_position: int | None
    member_ids: tuple[str, ...]
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.position < 0:
            raise ValueError("kernel center position must be non-negative")
        if not (
            self.entry_position < self.core_start_position
            <= self.core_event_position <= self.member_end_position
        ):
            raise ValueError("kernel center coordinates are invalid")
        if self.zd > self.zg or self.dd > self.gg or not self.member_ids:
            raise ValueError("kernel center geometry is invalid")
        # 兼容既有合成/迁移夹具：closed 中枢可能缺少方向证据，此时只是不推断离开方向。
        if (
            self.extension_state is ZhongShuState.OPEN
            and self.close_evidence_position is not None
        ):
            raise ValueError("open kernel center must not claim close evidence")


@dataclass(frozen=True, slots=True)
class ZouShiKernelCloseEvidence:
    kind: Literal["zhongshu", "source_leg"]
    id: str
    event_position: int


@dataclass(frozen=True, slots=True)
class ZouShiKernelRuleIds:
    forming: str
    freeze_trend: str
    freeze_consolidation: str
    freeze_exit_break: str
    forming_shared_turn: str | None = None
    freeze_shared_turn: str | None = None


@dataclass(frozen=True, slots=True)
class ZouShiKernelSlice:
    kind: ZouShiKind
    direction: ZouShiDirection | None
    start_position: int
    end_position: int
    source_positions: tuple[int, ...]
    center_positions: tuple[int, ...]
    completion_state: ZouShiBoundaryState
    close_evidence: ZouShiKernelCloseEvidence | None
    high_point: ZouShiKernelExtremeRef
    low_point: ZouShiKernelExtremeRef
    primary_rule_id: str
    trace_horizon_position: int | None = None

    def __post_init__(self) -> None:
        if not self.source_positions or not self.center_positions:
            raise ValueError("kernel slice requires source and center members")
        if self.source_positions[0] != self.start_position:
            raise ValueError("kernel slice start must be its first source member")
        if self.end_position not in self.source_positions:
            raise ValueError("kernel slice end must belong to its source members")
        if (
            self.trace_horizon_position is not None
            and self.trace_horizon_position != self.source_positions[-1]
        ):
            raise ValueError("kernel trace horizon must be the last source member")
        if self.kind is ZouShiKind.CONSOLIDATION and self.direction is not None:
            raise ValueError("kernel consolidation cannot have trend direction")
        if self.kind is ZouShiKind.TREND and self.direction is None:
            raise ValueError("kernel trend requires direction")
        evidence_count = int(self.close_evidence is not None)
        if self.completion_state is ZouShiBoundaryState.FROZEN and evidence_count != 1:
            raise ValueError("frozen kernel slice requires one close evidence")
        if self.completion_state is ZouShiBoundaryState.FORMING and evidence_count:
            raise ValueError("forming kernel slice cannot claim close evidence")


@dataclass(frozen=True, slots=True)
class _TrendTransition:
    direction: ZouShiDirection
    start_position: int
    probe_position: int
    evidence_position: int | None


@dataclass(frozen=True, slots=True)
class _PendingCenterSplit:
    item: ZouShiKernelCenter
    old_exit_direction: ZouShiDirection
    new_direction: ZouShiDirection | None


@dataclass(frozen=True, slots=True)
class _ConsolidationSharedTurn:
    """延伸中枢内部尚未/已经确认的共享走势转折。"""

    old_direction: ZouShiDirection
    new_direction: ZouShiDirection
    extreme_position: int
    start_position: int
    freeze_evidence_position: int | None


def _extreme_leg(
    run: Sequence[ZouShiKernelLeg],
    *,
    start_position: int,
    end_position: int,
    direction: ZouShiDirection,
) -> ZouShiKernelLeg:
    attempts = [
        leg
        for leg in run[start_position : end_position + 1]
        if leg.direction is direction
    ]
    if not attempts:
        raise ValueError("zoushi lifecycle has no directional exit-attempt leg")
    if direction is ZouShiDirection.UP:
        return max(attempts, key=lambda leg: (leg.end.price, leg.position))
    return min(attempts, key=lambda leg: (leg.end.price, -leg.position))


def _strict_direction(
    left: ZouShiKernelCenter, right: ZouShiKernelCenter
) -> ZouShiDirection | None:
    if right.dd > left.gg:
        return ZouShiDirection.UP
    if right.gg < left.dd:
        return ZouShiDirection.DOWN
    return None


def _exit_direction(
    run: Sequence[ZouShiKernelLeg], center: ZouShiKernelCenter
) -> ZouShiDirection | None:
    if center.extension_state is not ZhongShuState.CLOSED:
        return None
    if center.close_evidence_position is None:
        return None
    evidence = run[center.close_evidence_position]
    if evidence.low > center.zg:
        return ZouShiDirection.UP
    if evidence.high < center.zd:
        return ZouShiDirection.DOWN
    return None


def _opposite(direction: ZouShiDirection) -> ZouShiDirection:
    return (
        ZouShiDirection.DOWN
        if direction is ZouShiDirection.UP
        else ZouShiDirection.UP
    )


def _first_departure_direction(
    run: Sequence[ZouShiKernelLeg],
    center: ZouShiKernelCenter,
    *,
    max_position: int,
) -> ZouShiDirection | None:
    """按端点首次严格离开核心区的方向确认盘整实际行进方向。"""
    last = min(max_position, len(run) - 1)
    for position in range(center.core_event_position, last + 1):
        leg = run[position]
        if leg.direction is ZouShiDirection.UP and leg.end.price > center.zg:
            return ZouShiDirection.UP
        if leg.direction is ZouShiDirection.DOWN and leg.end.price < center.zd:
            return ZouShiDirection.DOWN
    return None


def _bootstrap_start_position(
    run: Sequence[ZouShiKernelLeg],
    center: ZouShiKernelCenter,
    direction: ZouShiDirection,
) -> int:
    """保留正式首中枢相位解析前、已经参与早期走势生长的相邻 E。"""
    entry_position = center.entry_position
    if entry_position <= 0:
        return center.core_start_position
    previous = run[entry_position - 1]
    entry = run[entry_position]
    reaches_core = max(previous.low, center.zd) <= min(previous.high, center.zg)
    if (
        previous.direction is direction
        and previous.end.ts == entry.start.ts
        and previous.end.price == entry.start.price
        and reaches_core
    ):
        return previous.position
    return center.core_start_position


def _initial_travel_direction(
    run: Sequence[ZouShiKernelLeg], center: ZouShiKernelCenter
) -> ZouShiDirection | None:
    """优先保留开放期方向；已关闭普通首相位仍沿既有最终离开规则。"""
    departure = _first_departure_direction(
        run, center, max_position=len(run) - 1
    )
    exit_direction = _exit_direction(run, center)
    if exit_direction is None:
        return departure
    if (
        departure is not None
        and center.entry_position > 0
        and _bootstrap_start_position(run, center, departure)
        == center.entry_position - 1
    ):
        # 正式首中枢后来右移 E 时，不能用最终关闭方向吞掉此前已形成的走势。
        return departure
    return exit_direction


def _consolidation_shared_turn(
    run: Sequence[ZouShiKernelLeg],
    center: ZouShiKernelCenter,
    direction: ZouShiDirection,
    *,
    start_position: int,
    max_position: int,
) -> _ConsolidationSharedTurn | None:
    """按事件水位找共享极值；一旦冻结，未来数据不得回写该边界。"""
    last = min(max_position, len(run) - 1)
    if start_position > last:
        return None
    extreme: ZouShiKernelLeg | None = None
    candidate_extreme: ZouShiKernelLeg | None = None
    candidate_start: int | None = None
    for position in range(start_position, last + 1):
        leg = run[position]
        is_attempt = leg.direction is direction and (
            leg.end.price > center.zg
            if direction is ZouShiDirection.UP
            else leg.end.price < center.zd
        )
        if is_attempt:
            strictly_new = extreme is None or (
                leg.end.price > extreme.end.price
                if direction is ZouShiDirection.UP
                else leg.end.price < extreme.end.price
            )
            equal_before_candidate = (
                extreme is not None
                and candidate_extreme is None
                and leg.end.price == extreme.end.price
            )
            if strictly_new or equal_before_candidate:
                extreme = leg
                candidate_extreme = None
                candidate_start = None
                continue
        if extreme is None:
            continue
        if candidate_extreme is None:
            reversed_now = (
                leg.direction is ZouShiDirection.DOWN
                and leg.end.price < extreme.start.price
                if direction is ZouShiDirection.UP
                else leg.direction is ZouShiDirection.UP
                and leg.end.price > extreme.start.price
            )
            if reversed_now:
                candidate_extreme = extreme
                candidate_start = extreme.position + 1
        if candidate_extreme is None or candidate_start is None:
            continue
        confirmed = _transition(run, center, direction, max_position=position)
        if (
            confirmed is not None
            and confirmed.start_position == candidate_start
            and confirmed.evidence_position is not None
        ):
            return _ConsolidationSharedTurn(
                old_direction=direction,
                new_direction=_opposite(direction),
                extreme_position=candidate_extreme.position,
                start_position=candidate_start,
                freeze_evidence_position=confirmed.evidence_position,
            )
    if candidate_extreme is None or candidate_start is None:
        return None
    return _ConsolidationSharedTurn(
        old_direction=direction,
        new_direction=_opposite(direction),
        extreme_position=candidate_extreme.position,
        start_position=candidate_start,
        freeze_evidence_position=None,
    )


def _transition(
    run: Sequence[ZouShiKernelLeg],
    center: ZouShiKernelCenter,
    direction: ZouShiDirection,
    *,
    max_position: int,
) -> _TrendTransition | None:
    if max_position <= center.member_end_position:
        return None
    probe_position: int | None = None
    for position in range(
        center.member_end_position + 1,
        min(max_position, len(run) - 1) + 1,
    ):
        leg = run[position]
        is_probe = (
            leg.direction is ZouShiDirection.UP and leg.high < center.zd
            if direction is ZouShiDirection.UP
            else leg.direction is ZouShiDirection.DOWN and leg.low > center.zg
        )
        if is_probe:
            probe_position = position
            break
    if probe_position is None:
        return None

    old_extreme = _extreme_leg(
        run,
        start_position=center.entry_position,
        end_position=probe_position,
        direction=direction,
    )
    start_position = old_extreme.position + 1
    if start_position > probe_position:
        return None

    probe = run[probe_position]
    evidence_position: int | None = None
    for position in range(probe_position + 1, min(max_position, len(run) - 1) + 1):
        leg = run[position]
        if direction is ZouShiDirection.UP:
            if leg.direction is ZouShiDirection.DOWN and leg.end.price < probe.start.price:
                evidence_position = position
                break
            # Q16：形成中 high/low 可即时刷新，但撤销转折只比较结构终点。
            if leg.direction is ZouShiDirection.UP and leg.end.price > old_extreme.end.price:
                return None
        else:
            if leg.direction is ZouShiDirection.UP and leg.end.price > probe.start.price:
                evidence_position = position
                break
            if leg.direction is ZouShiDirection.DOWN and leg.end.price < old_extreme.end.price:
                return None
    return _TrendTransition(
        direction=(
            ZouShiDirection.DOWN
            if direction is ZouShiDirection.UP
            else ZouShiDirection.UP
        ),
        start_position=start_position,
        probe_position=probe_position,
        evidence_position=evidence_position,
    )


def _make_slice(
    run: Sequence[ZouShiKernelLeg],
    members: Sequence[ZouShiKernelCenter],
    *,
    direction: ZouShiDirection | None,
    evidence: ZouShiKernelCenter | None,
    source_evidence: ZouShiKernelLeg | None,
    exit_direction_override: ZouShiDirection | None,
    start_position_override: int | None,
    rules: ZouShiKernelRuleIds,
    source_end_position_override: int | None = None,
) -> ZouShiKernelSlice:
    if evidence is not None and source_evidence is not None:
        raise ValueError("kernel close evidence must be center or source leg")
    first, last = members[0], members[-1]
    # 只有连续 run 的第一条走势没有上一条已确认边界（override=None）。
    # 若此时走势已取得严格/离开方向证明：E 与走势同向，E 属于本走势；
    # E 与走势反向，E 是转折前最后一段，本走势从 E.end=A.start 开始。
    # 未取得方向证明时保留 E.start，严格按左到右的 provisional 状态生长。
    confirmed_direction = direction or exit_direction_override
    natural_start_position = first.entry_position
    if (
        start_position_override is None
        and confirmed_direction is not None
        and run[first.entry_position].direction is not confirmed_direction
    ):
        natural_start_position = first.core_start_position
    start_position = (
        natural_start_position
        if start_position_override is None
        else start_position_override
    )
    if not 0 <= start_position < len(run):
        raise ValueError("kernel slice start is outside its run")
    if source_end_position_override is not None and not (
        start_position <= source_end_position_override < len(run)
    ):
        raise ValueError("kernel slice source end is outside its run")

    close_evidence: ZouShiKernelCloseEvidence | None
    if evidence is None and source_evidence is None:
        lifecycle_end = len(run) - 1
        state = ZouShiBoundaryState.FORMING
        close_evidence = None
        rule_id = rules.forming
    elif evidence is not None:
        lifecycle_end = evidence.core_start_position
        state = ZouShiBoundaryState.FROZEN
        close_evidence = ZouShiKernelCloseEvidence(
            "zhongshu", evidence.id, evidence.core_event_position
        )
        rule_id = rules.freeze_trend if direction is not None else rules.freeze_consolidation
    else:
        assert source_evidence is not None
        lifecycle_end = source_evidence.position
        state = ZouShiBoundaryState.FROZEN
        close_evidence = ZouShiKernelCloseEvidence(
            "source_leg", source_evidence.id, source_evidence.position
        )
        rule_id = rules.freeze_exit_break

    if exit_direction_override is not None:
        exit_direction = exit_direction_override
    elif direction is not None:
        exit_direction = direction
    elif evidence is None:
        exit_direction = run[-1].direction
    else:
        raise ValueError("frozen consolidation requires explicit exit direction")
    source_end_position = (
        lifecycle_end
        if source_end_position_override is None
        else source_end_position_override
    )
    last_center_start = max(start_position, last.entry_position)
    end_leg = _extreme_leg(
        run,
        start_position=last_center_start,
        end_position=source_end_position,
        direction=exit_direction,
    )
    if source_end_position_override is not None:
        source_positions = tuple(range(start_position, source_end_position + 1))
    elif state is ZouShiBoundaryState.FORMING:
        source_positions = tuple(range(start_position, len(run)))
    else:
        source_positions = tuple(range(start_position, end_leg.position + 1))
    observed = [run[position] for position in source_positions]
    high_leg = max(observed, key=lambda item: (item.high, item.position))
    low_leg = min(observed, key=lambda item: (item.low, -item.position))
    assert high_leg.high_point is not None and low_leg.low_point is not None
    return ZouShiKernelSlice(
        kind=ZouShiKind.TREND if direction is not None else ZouShiKind.CONSOLIDATION,
        direction=direction,
        start_position=start_position,
        end_position=end_leg.position,
        source_positions=source_positions,
        center_positions=tuple(item.position for item in members),
        completion_state=state,
        close_evidence=close_evidence,
        high_point=high_leg.high_point,
        low_point=low_leg.low_point,
        primary_rule_id=rule_id,
        trace_horizon_position=source_end_position_override,
    )


def _active_consolidation_shared_slices(
    run: Sequence[ZouShiKernelLeg],
    members: Sequence[ZouShiKernelCenter],
    *,
    travel_direction: ZouShiDirection | None,
    start_position_override: int | None,
    rules: ZouShiKernelRuleIds,
    extended_center_shared_turn: bool,
) -> tuple[ZouShiKernelSlice, ZouShiKernelSlice] | None:
    """若命中延伸中枢共享转折，返回旧/新两条盘整切片。"""
    if not extended_center_shared_turn or travel_direction is None:
        return None
    first, boundary = members[0], members[-1]
    provisional_start = max(
        boundary.entry_position,
        start_position_override
        if start_position_override is not None
        else (
            boundary.entry_position
            if run[boundary.entry_position].direction is travel_direction
            else _bootstrap_start_position(run, boundary, travel_direction)
        ),
    )
    shared_turn = _consolidation_shared_turn(
        run,
        boundary,
        travel_direction,
        start_position=provisional_start,
        max_position=len(run) - 1,
    )
    if shared_turn is None:
        return None
    evidence_leg = (
        None
        if shared_turn.freeze_evidence_position is None
        else run[shared_turn.freeze_evidence_position]
    )
    old_start_position = (
        start_position_override
        if start_position_override is not None
        else (
            first.entry_position
            if run[first.entry_position].direction is shared_turn.old_direction
            else _bootstrap_start_position(run, first, shared_turn.old_direction)
        )
    )
    old_slice = _make_slice(
        run,
        members,
        direction=None,
        evidence=None,
        source_evidence=evidence_leg,
        exit_direction_override=shared_turn.old_direction,
        start_position_override=old_start_position,
        rules=rules,
        source_end_position_override=shared_turn.extreme_position,
    )
    if rules.forming_shared_turn is not None and evidence_leg is None:
        old_slice = replace(old_slice, primary_rule_id=rules.forming_shared_turn)
    if rules.freeze_shared_turn is not None and evidence_leg is not None:
        old_slice = replace(old_slice, primary_rule_id=rules.freeze_shared_turn)
    new_slice = _make_slice(
        run,
        [boundary],
        direction=None,
        evidence=None,
        source_evidence=None,
        exit_direction_override=shared_turn.new_direction,
        start_position_override=shared_turn.start_position,
        rules=rules,
    )
    if rules.forming_shared_turn is not None:
        new_slice = replace(new_slice, primary_rule_id=rules.forming_shared_turn)
    return old_slice, new_slice


def _append_active_consolidation(
    out: list[ZouShiKernelSlice],
    run: Sequence[ZouShiKernelLeg],
    members: Sequence[ZouShiKernelCenter],
    *,
    travel_direction: ZouShiDirection | None,
    start_position_override: int | None,
    fallback_exit_direction: ZouShiDirection | None,
    rules: ZouShiKernelRuleIds,
    extended_center_shared_turn: bool,
) -> None:
    """发布一条活动盘整；递归口径可在同一延伸中枢内共享极值转折。"""
    shared = _active_consolidation_shared_slices(
        run,
        members,
        travel_direction=travel_direction,
        start_position_override=start_position_override,
        rules=rules,
        extended_center_shared_turn=extended_center_shared_turn,
    )
    if shared is not None:
        out.extend(shared)
        return

    out.append(
        _make_slice(
            run,
            members,
            direction=None,
            evidence=None,
            source_evidence=None,
            exit_direction_override=fallback_exit_direction,
            start_position_override=start_position_override,
            rules=rules,
        )
    )


def _build_local_slices(
    run: Sequence[ZouShiKernelLeg],
    centers: Sequence[ZouShiKernelCenter],
    *,
    rules: ZouShiKernelRuleIds,
    extended_center_shared_turn: bool,
) -> list[ZouShiKernelSlice]:
    """按事件水位从左到右构造一个连续 run 的走势切片。"""
    if not centers:
        return []
    out: list[ZouShiKernelSlice] = []
    members = [centers[0]]
    direction: ZouShiDirection | None = None
    travel_direction = (
        _initial_travel_direction(run, centers[0])
        if extended_center_shared_turn
        else _exit_direction(run, centers[0])
    )
    next_start_position: int | None = None
    pending: _PendingCenterSplit | None = None

    for item in centers[1:]:
        strict = _strict_direction(members[-1], item)
        boundary = members[-1]
        if direction is not None:
            transition = _transition(
                run, boundary, direction, max_position=item.core_event_position
            )
            if transition is not None and transition.evidence_position is not None:
                out.append(
                    _make_slice(
                        run, members, direction=direction, evidence=None,
                        source_evidence=run[transition.evidence_position],
                        exit_direction_override=direction,
                        start_position_override=next_start_position, rules=rules,
                    )
                )
                next_start_position = transition.start_position
                members = [boundary, item]
                direction = strict if strict is transition.direction else None
                travel_direction = None if direction is not None else transition.direction
                continue
        if direction is None:
            if strict is None:
                boundary_exit = _exit_direction(run, boundary)
                if boundary_exit is not None and travel_direction is None:
                    travel_direction = boundary_exit
                elif (
                    boundary_exit is not None
                    and travel_direction is not None
                    and boundary_exit is not travel_direction
                ):
                    if item.extension_state is not ZhongShuState.CLOSED:
                        pending = _PendingCenterSplit(item, travel_direction, None)
                        break
                    completed = _make_slice(
                        run, members, direction=None, evidence=item,
                        source_evidence=None, exit_direction_override=travel_direction,
                        start_position_override=next_start_position, rules=rules,
                    )
                    out.append(completed)
                    next_start_position = completed.end_position + 1
                    members = [boundary, item]
                    travel_direction = _exit_direction(run, boundary)
                    continue
                members.append(item)
                if item.extension_state is not ZhongShuState.CLOSED:
                    break
                continue
            if len(members) == 1 or travel_direction is strict:
                members.append(item)
                direction = strict
                travel_direction = None
                if item.extension_state is not ZhongShuState.CLOSED:
                    break
                continue
            if item.extension_state is not ZhongShuState.CLOSED:
                old_exit = travel_direction or (
                    ZouShiDirection.DOWN
                    if strict is ZouShiDirection.UP
                    else ZouShiDirection.UP
                )
                pending = _PendingCenterSplit(item, old_exit, strict)
                break
            completed = _make_slice(
                run, members, direction=None, evidence=item, source_evidence=None,
                exit_direction_override=travel_direction or (
                    ZouShiDirection.DOWN if strict is ZouShiDirection.UP else ZouShiDirection.UP
                ),
                start_position_override=next_start_position, rules=rules,
            )
            out.append(completed)
            next_start_position = completed.end_position + 1
            members = [boundary, item]
            direction = strict
            travel_direction = None if direction is not None else _exit_direction(run, boundary)
            continue

        boundary_exit = _exit_direction(run, boundary)
        if strict is direction or boundary_exit is direction:
            members.append(item)
            if item.extension_state is not ZhongShuState.CLOSED:
                break
            continue
        if item.extension_state is not ZhongShuState.CLOSED:
            pending = _PendingCenterSplit(item, direction, strict)
            break
        completed = _make_slice(
            run, members, direction=direction, evidence=item, source_evidence=None,
            exit_direction_override=direction,
            start_position_override=next_start_position, rules=rules,
        )
        out.append(completed)
        next_start_position = completed.end_position + 1
        members = [boundary, item]
        direction = strict
        travel_direction = None if direction is not None else _exit_direction(run, boundary)

    if next_start_position is not None and next_start_position >= len(run):
        return out
    if pending is not None:
        boundary = members[-1]
        if pending.new_direction is None:
            shared = _active_consolidation_shared_slices(
                run,
                members,
                travel_direction=pending.old_exit_direction,
                start_position_override=next_start_position,
                rules=rules,
                extended_center_shared_turn=extended_center_shared_turn,
            )
            if shared is not None:
                old_shared, new_shared = shared
                out.append(old_shared)
                pending_members = [boundary, pending.item]
                new_direction = _opposite(pending.old_exit_direction)
                _append_active_consolidation(
                    out,
                    run,
                    pending_members,
                    travel_direction=new_direction,
                    start_position_override=new_shared.start_position,
                    fallback_exit_direction=new_direction,
                    rules=rules,
                    extended_center_shared_turn=extended_center_shared_turn,
                )
                return out
        old_active = _make_slice(
            run, members, direction=direction, evidence=None, source_evidence=None,
            exit_direction_override=pending.old_exit_direction,
            start_position_override=next_start_position, rules=rules,
        )
        out.append(old_active)
        pending_start = old_active.end_position + 1
        if pending_start >= len(run):
            return out
        pending_members = [boundary, pending.item]
        pending_active = _make_slice(
            run, pending_members, direction=pending.new_direction, evidence=None,
            source_evidence=None, exit_direction_override=pending.new_direction,
            start_position_override=pending_start, rules=rules,
        )
        if pending.new_direction is None:
            boundary_exit = _exit_direction(run, boundary)
            _append_active_consolidation(
                out,
                run,
                pending_members,
                travel_direction=boundary_exit,
                start_position_override=pending_start,
                fallback_exit_direction=boundary_exit,
                rules=rules,
                extended_center_shared_turn=extended_center_shared_turn,
            )
            return out
        transition = _transition(
            run, pending.item, pending.new_direction, max_position=len(run) - 1
        )
        if transition is None or transition.evidence_position is None:
            out.append(pending_active)
        else:
            out.append(
                _make_slice(
                    run, pending_members, direction=pending.new_direction,
                    evidence=None, source_evidence=run[transition.evidence_position],
                    exit_direction_override=pending.new_direction,
                    start_position_override=pending_start, rules=rules,
                )
            )
        if transition is not None:
            _append_active_consolidation(
                out,
                run,
                [pending.item],
                travel_direction=transition.direction,
                start_position_override=transition.start_position,
                fallback_exit_direction=transition.direction,
                rules=rules,
                extended_center_shared_turn=extended_center_shared_turn,
            )
        return out

    confirmed_travel = (
        travel_direction
        if travel_direction is not None
        and any(_exit_direction(run, center) is travel_direction for center in members)
        else None
    )
    if direction is None:
        _append_active_consolidation(
            out,
            run,
            members,
            travel_direction=travel_direction,
            start_position_override=next_start_position,
            fallback_exit_direction=confirmed_travel,
            rules=rules,
            extended_center_shared_turn=extended_center_shared_turn,
        )
        return out
    active = _make_slice(
        run, members, direction=direction, evidence=None, source_evidence=None,
        exit_direction_override=direction or confirmed_travel,
        start_position_override=next_start_position, rules=rules,
    )
    transition = _transition(
        run, members[-1], direction, max_position=len(run) - 1
    )
    if transition is None:
        out.append(active)
        return out
    if transition.evidence_position is None:
        out.append(active)
    else:
        out.append(
            _make_slice(
                run, members, direction=direction, evidence=None,
                source_evidence=run[transition.evidence_position],
                exit_direction_override=direction,
                start_position_override=next_start_position, rules=rules,
            )
        )
    _append_active_consolidation(
        out,
        run,
        [members[-1]],
        travel_direction=transition.direction,
        start_position_override=transition.start_position,
        fallback_exit_direction=transition.direction,
        rules=rules,
        extended_center_shared_turn=extended_center_shared_turn,
    )
    return out


def build_zoushi_kernel_slices(
    run: Sequence[ZouShiKernelLeg],
    centers: Sequence[ZouShiKernelCenter],
    *,
    rules: ZouShiKernelRuleIds,
    extended_center_shared_turn: bool = False,
) -> list[ZouShiKernelSlice]:
    """接受全局坐标，按 run 内局部位置运算，再把输出还原为全局坐标。"""
    if not run or not centers:
        return []
    source_globals = tuple(item.position for item in run)
    center_globals = tuple(item.position for item in centers)
    if (
        len(set(source_globals)) != len(source_globals)
        or tuple(sorted(source_globals)) != source_globals
    ):
        raise ValueError("kernel leg positions must be unique and ordered")
    if (
        len(set(center_globals)) != len(center_globals)
        or tuple(sorted(center_globals)) != center_globals
    ):
        raise ValueError("kernel center positions must be unique and ordered")
    source_local = {value: index for index, value in enumerate(source_globals)}

    try:
        local_centers = tuple(
            replace(
                item,
                position=index,
                entry_position=source_local[item.entry_position],
                core_start_position=source_local[item.core_start_position],
                core_event_position=source_local[item.core_event_position],
                member_end_position=source_local[item.member_end_position],
                close_evidence_position=(
                    None
                    if item.close_evidence_position is None
                    else source_local[item.close_evidence_position]
                ),
            )
            for index, item in enumerate(centers)
        )
    except KeyError as exc:
        raise ValueError("kernel center coordinate is outside its source run") from exc
    local_legs = tuple(
        replace(
            item,
            position=index,
            high_point=(
                None
                if item.high_point is None
                else replace(item.high_point, source_position=index)
            ),
            low_point=(
                None
                if item.low_point is None
                else replace(item.low_point, source_position=index)
            ),
        )
        for index, item in enumerate(run)
    )
    local_items = _build_local_slices(
        local_legs,
        local_centers,
        rules=rules,
        extended_center_shared_turn=extended_center_shared_turn,
    )
    out: list[ZouShiKernelSlice] = []
    for item in local_items:
        evidence = item.close_evidence
        if evidence is not None:
            evidence = replace(
                evidence,
                event_position=source_globals[evidence.event_position],
            )
        out.append(
            replace(
                item,
                start_position=source_globals[item.start_position],
                end_position=source_globals[item.end_position],
                source_positions=tuple(
                    source_globals[position] for position in item.source_positions
                ),
                center_positions=tuple(
                    center_globals[position] for position in item.center_positions
                ),
                close_evidence=evidence,
                high_point=replace(
                    item.high_point,
                    source_position=source_globals[item.high_point.source_position],
                ),
                low_point=replace(
                    item.low_point,
                    source_position=source_globals[item.low_point.source_position],
                ),
            )
        )
    return out


__all__ = [
    "ZouShiKernelCenter",
    "ZouShiKernelCloseEvidence",
    "ZouShiKernelExtremeRef",
    "ZouShiKernelLeg",
    "ZouShiKernelRuleIds",
    "ZouShiKernelSlice",
    "build_zoushi_kernel_slices",
]
