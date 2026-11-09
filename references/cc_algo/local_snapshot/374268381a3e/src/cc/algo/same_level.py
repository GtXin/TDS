"""第 38 课同级别分解的 L0/L1 共用、从左到右状态机。"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, replace

from cc.algo.models import (
    BiDir,
    CompletedZouShi,
    LevelBuildResult,
    LevelLeg,
    ZhongShu,
    ZhongShuMode,
    ZhongShuState,
    ZouShiBoundaryState,
    ZouShiDirection,
    ZouShiEndpoint,
    ZouShiKind,
)
from cc.algo.trace import (
    RULE_ZHONGSHU_SAME_LEVEL_CLOSE_RIGHT,
    RULE_ZHONGSHU_SAME_LEVEL_OVERLAP3,
    RULE_ZSL_ACTIVE_EXTEND_STRICT_EXTREME,
    RULE_ZSL_ACTIVE_REANCHOR_EQUAL,
    RULE_ZSL_CLASSIFY_STRICT_DOWN,
    RULE_ZSL_CLASSIFY_STRICT_UP,
    RULE_ZSL_PROBE_CANCEL_EXTREME,
    RULE_ZSL_PROBE_CONFIRM_CENTER,
    RULE_ZSL_PROBE_OPEN,
    RULE_ZSL_PROBE_REANCHOR_EQUAL,
    RULE_ZSL_SEGMENT_REPHASE,
    RULE_ZSL_SPLIT_NON_STRICT,
    RULE_ZSL_TURN_CANCEL_STRICT_EXTREME,
    RULE_ZSL_TURN_CONFIRM,
    StructTrace,
)
from cc.algo.zhongshu_phase import scan_zhongshu_candidate

_ALGO_CARD_ID = "same-level-decomposition-v2"


@dataclass(frozen=True, slots=True)
class SameLevelCenterEvent:
    """与走势极值无关的 E+A/B/C 几何事件及本段延伸状态。"""

    entry_position: int
    a_position: int
    b_position: int
    c_position: int
    zd: float
    zg: float
    gg: float
    dd: float
    extended_positions: tuple[int, ...] = ()
    close_position: int | None = None
    is_formal: bool = False
    run_id: int = 0

    @property
    def member_end_position(self) -> int:
        """最后一个中枢成员；核心 C 后可以包含同一中枢的延伸成员。"""
        return self.extended_positions[-1] if self.extended_positions else self.c_position


_CenterCore = SameLevelCenterEvent


@dataclass(slots=True)
class _Active:
    start_position: int
    travel_direction: BiDir
    extreme_position: int
    centers: list[_CenterCore]
    trend_direction: BiDir | None = None
    core_consumed_to_position: int | None = None
    observed_to_position: int | None = None
    last_rule_id: str = RULE_ZSL_PROBE_OPEN

    @property
    def center_entry_floor(self) -> int:
        if self.core_consumed_to_position is None:
            return self.extreme_position
        return max(self.extreme_position, self.core_consumed_to_position)


@dataclass(frozen=True, slots=True)
class _Frozen:
    active: _Active
    confirmation_center: _CenterCore


@dataclass(frozen=True, slots=True)
class _PendingTurn:
    previous: _Active
    boundary_position: int


def _continuous(left: LevelLeg, right: LevelLeg) -> bool:
    return (
        right.source_index == left.source_index + 1
        and left.end_ts == right.start_ts
        and left.direction is not right.direction
    )


def _endpoint(leg: LevelLeg, *, at_start: bool) -> ZouShiEndpoint:
    return ZouShiEndpoint(
        source_id=leg.source_id,
        source_index=leg.source_index,
        ts=leg.start_ts if at_start else leg.end_ts,
        price=leg.start_price if at_start else leg.end_price,
    )


def _trace(
    legs: Sequence[LevelLeg],
    *,
    rule_id: str,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    traces = [leg.trace for leg in legs if leg.trace is not None]
    source_from = [
        item.source_from_ts for item in traces if item.source_from_ts is not None
    ]
    source_to = [item.source_to_ts for item in traces if item.source_to_ts is not None]
    merged_from = [
        item.merged_from_index
        for item in traces
        if item.merged_from_index is not None
    ]
    merged_to = [
        item.merged_to_index for item in traces if item.merged_to_index is not None
    ]
    dep_to = [item.dep_to_index for item in traces if item.dep_to_index is not None]
    return StructTrace(
        algo_card_id=_ALGO_CARD_ID,
        rule_id=rule_id,
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=(
            min(source_from) if source_from else min(item.start_ts for item in legs)
        ),
        source_to_ts=(
            max(source_to) if source_to else max(item.end_ts for item in legs)
        ),
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=max(merged_to) if merged_to else None,
        dep_to_index=max(dep_to) if dep_to else None,
    )


def _strict_extreme(active: _Active, run: Sequence[LevelLeg], position: int) -> bool:
    current = run[position]
    previous = run[active.extreme_position]
    if current.direction is not active.travel_direction:
        return False
    if active.travel_direction is BiDir.UP:
        return current.end_price > previous.end_price
    return current.end_price < previous.end_price


def _equal_extreme(active: _Active, run: Sequence[LevelLeg], position: int) -> bool:
    current = run[position]
    previous = run[active.extreme_position]
    return (
        current.direction is active.travel_direction
        and current.end_price == previous.end_price
    )


def _directional_extreme(
    run: Sequence[LevelLeg],
    *,
    start_position: int,
    end_position: int,
    direction: BiDir,
) -> int | None:
    positions = [
        position
        for position in range(start_position, end_position + 1)
        if run[position].direction is direction
    ]
    if not positions:
        return None
    if direction is BiDir.UP:
        return max(positions, key=lambda item: (run[item].end_price, item))
    return min(positions, key=lambda item: (run[item].end_price, -item))


def _draft_at(run: Sequence[LevelLeg], c_position: int, floor: int) -> _CenterCore | None:
    entry_position = c_position - 3
    if entry_position < floor:
        return None
    a_position, b_position = entry_position + 1, entry_position + 2
    entry, a, b, c = (
        run[entry_position],
        run[a_position],
        run[b_position],
        run[c_position],
    )
    zd = max(a.low, b.low, c.low)
    zg = min(a.high, b.high, c.high)
    if zd > zg:
        return None
    if max(entry.low, zd) > min(entry.high, zg):
        return None
    return _CenterCore(
        entry_position=entry_position,
        a_position=a_position,
        b_position=b_position,
        c_position=c_position,
        zd=zd,
        zg=zg,
        gg=max(a.high, c.high),
        dd=min(a.low, c.low),
    )


def _scan_center_events(run: Sequence[LevelLeg]) -> list[_CenterCore]:
    """生成只供分解状态机使用的逐前缀几何相位事件。

    这些事件负责决定准分解点是否打开、移动或确认，不能被未来才出现的
    中枢延伸反向改写。最终公开中枢由 ``_scan_extended_center_events`` 在
    已确定的单个走势区间内重扫，两层职责不得再合并。
    """
    out: list[_CenterCore] = []
    core_consumed_to_position = 0
    for c_position in range(3, len(run)):
        draft = _draft_at(run, c_position, 0)
        if draft is None:
            continue
        is_formal = draft.entry_position >= core_consumed_to_position
        out.append(replace(draft, is_formal=is_formal))
        if is_formal:
            core_consumed_to_position = draft.c_position
    return out


def _scan_extended_center_events(run: Sequence[LevelLeg]) -> list[_CenterCore]:
    """在一个已确定走势区间内生成正式中枢，并允许同一中枢延伸。"""
    out: list[_CenterCore] = []
    entry_position = 0
    required_entry_direction: BiDir | None = None
    while entry_position + 3 < len(run):
        candidate = scan_zhongshu_candidate(run, entry_position)
        if candidate is None:
            entry_position += 1
            continue
        entry = run[candidate.entry_index]
        if (
            required_entry_direction is not None
            and entry.direction is not required_entry_direction
        ):
            entry_position += 1
            continue
        a_position, b_position, c_position = candidate.core_indexes
        out.append(
            _CenterCore(
                entry_position=candidate.entry_index,
                a_position=a_position,
                b_position=b_position,
                c_position=c_position,
                zd=candidate.zd,
                zg=candidate.zg,
                gg=candidate.gg,
                dd=candidate.dd,
                extended_positions=candidate.extended_indexes,
                close_position=candidate.close_index,
                is_formal=True,
            )
        )
        if candidate.close_index is None:
            break
        assert candidate.exit_direction is not None
        required_entry_direction = BiDir(candidate.exit_direction)
        preceding = candidate.close_index - 1
        entry_position = (
            preceding
            if run[preceding].direction is required_entry_direction
            else max(0, candidate.close_index - 2)
        )
    return out


def _strict_center_direction(left: _CenterCore, right: _CenterCore) -> BiDir | None:
    if right.dd > left.gg:
        return BiDir.UP
    if right.gg < left.dd:
        return BiDir.DOWN
    return None


def _crossing_center_belongs_to_right(
    core: _CenterCore,
    *,
    right_start_position: int,
) -> bool:
    """E 在共享点左侧、C 严格落在右侧的中心由右 active 消费。"""
    return core.entry_position < right_start_position < core.c_position


def _crossing_center_belongs_to_left(
    core: _CenterCore,
    *,
    right_start_position: int,
) -> bool:
    """E 在共享点左侧、C 恰为右侧起点的中心仍归左 active。"""
    return core.entry_position < right_start_position == core.c_position


def _supports_strict_direction(
    cores: Sequence[_CenterCore],
    direction: BiDir,
) -> bool:
    """正式中枢中至少存在一组按时间同向严格分离关系。"""
    return any(
        _strict_center_direction(left, right) is direction
        for left_index, left in enumerate(cores)
        for right in cores[left_index + 1 :]
    )


def _copy_active(active: _Active) -> _Active:
    return _Active(
        start_position=active.start_position,
        travel_direction=active.travel_direction,
        extreme_position=active.extreme_position,
        centers=list(active.centers),
        trend_direction=active.trend_direction,
        core_consumed_to_position=active.core_consumed_to_position,
        observed_to_position=active.observed_to_position,
        last_rule_id=active.last_rule_id,
    )


def _beyond(
    run: Sequence[LevelLeg],
    *,
    direction: BiDir,
    left_position: int,
    right_position: int,
) -> bool:
    if direction is BiDir.UP:
        return run[right_position].end_price > run[left_position].end_price
    return run[right_position].end_price < run[left_position].end_price


def _has_open_probe(
    active: _Active,
    run: Sequence[LevelLeg],
    position: int,
) -> bool:
    """当前极值事件前是否已有反向完成部件进入私有 probe。"""
    return any(
        item.direction is not active.travel_direction
        for item in run[active.center_entry_floor + 1 : position]
    )


def _scan_run(
    run: Sequence[LevelLeg],
    center_events: Sequence[_CenterCore],
) -> tuple[
    list[_Frozen],
    _Active | None,
    _Active | None,
    list[_CenterCore],
    dict[tuple[int, int, int, int], _CenterCore],
]:
    if not run:
        return [], None, None, [], {}
    frozen: list[_Frozen] = []
    pending: _PendingTurn | None = None
    active = _Active(
        start_position=0,
        travel_direction=run[0].direction,
        extreme_position=0,
        centers=[],
    )
    event_by_c = {item.c_position: item for item in center_events}
    for position in range(1, len(run)):
        # 同一输入上的极值事件与中枢几何事件同时进入 Reducer。中枢事件
        # 只能来自独立 CenterScanner；不得在这里再次按走势极值重扫几何。
        current = run[position]
        draft = event_by_c.get(position)
        # 盘整尾部的准分解点若在“同价重锚”的同一输入完成了右侧 formal C，
        # 该 C 已使第二个盘整具备公开资格，不能再按无中心 probe 撤销。趋势
        # 尾部或严格创新极值仍执行原方向延续；这由状态/价格关系决定，和
        # 品种、周期及来源编号无关。
        draft_confirms_pending_side = (
            pending is not None
            and draft is not None
            and draft.is_formal
            and pending.previous.trend_direction is None
            and current.end_price
            == run[pending.previous.extreme_position].end_price
            and (
                draft.entry_position >= active.start_position
            )
        )
        if (
            pending is not None
            and not draft_confirms_pending_side
            and current.direction is pending.previous.travel_direction
            and (
                _beyond(
                    run,
                    direction=pending.previous.travel_direction,
                    left_position=pending.previous.extreme_position,
                    right_position=position,
                )
                or current.end_price
                == run[pending.previous.extreme_position].end_price
            )
        ):
            # 准分解点之后原方向严格创新极值，或回到同价极值时，反向
            # forming 尚未获得完成资格：撤销该活动尾部，把其中已形成的
            # 正式中枢重新归入延续走势，并把准点移动/重锚到当前位置。
            earlier = pending.previous
            consumed = [
                item
                for item in (
                    earlier.core_consumed_to_position,
                    active.core_consumed_to_position,
                )
                if item is not None
            ]
            is_strict = _beyond(
                run,
                direction=earlier.travel_direction,
                left_position=earlier.extreme_position,
                right_position=position,
            )
            active = _Active(
                start_position=earlier.start_position,
                travel_direction=earlier.travel_direction,
                extreme_position=position,
                centers=[*earlier.centers, *active.centers],
                trend_direction=active.trend_direction or earlier.trend_direction,
                core_consumed_to_position=max(consumed) if consumed else None,
                last_rule_id=(
                    RULE_ZSL_TURN_CANCEL_STRICT_EXTREME
                    if is_strict
                    else RULE_ZSL_PROBE_REANCHOR_EQUAL
                ),
            )
            pending = None
        elif _strict_extreme(active, run, position):
            had_probe = _has_open_probe(active, run, position)
            active.extreme_position = position
            active.last_rule_id = (
                RULE_ZSL_PROBE_CANCEL_EXTREME
                if had_probe
                else RULE_ZSL_ACTIVE_EXTEND_STRICT_EXTREME
            )
        elif _equal_extreme(active, run, position):
            had_probe = _has_open_probe(active, run, position)
            active.extreme_position = position
            active.last_rule_id = (
                RULE_ZSL_PROBE_REANCHOR_EQUAL
                if had_probe
                else RULE_ZSL_ACTIVE_REANCHOR_EQUAL
            )

        if (
            pending is None
            and active.centers
            and current.direction is not active.travel_direction
            and active.extreme_position > max(item.c_position for item in active.centers)
            and position == active.extreme_position + 1
        ):
            # 中枢离开极值后的第一根反向完成部件，当下就建立准分解点，
            # 不等待这条新走势自己的中枢 C。新 forming 暂时可以没有正式
            # 中枢；后续原方向新极值可撤销，formal C 才能确认冻结。
            previous_active = _copy_active(active)
            previous_active.last_rule_id = RULE_ZSL_PROBE_OPEN
            active = _Active(
                start_position=position,
                travel_direction=current.direction,
                extreme_position=position,
                centers=[],
                last_rule_id=RULE_ZSL_PROBE_OPEN,
            )
            pending = _PendingTurn(
                previous=previous_active,
                boundary_position=previous_active.extreme_position,
            )
        if draft is None:
            continue
        # formal 几何事件始终保留给 Projector，Reducer 也必须消费归属于
        # 当前走势的同一事件。同一输入刷新/同价重锚极值并不能抹掉 C：
        # 极值事件更新边界，中心事件仍参与严格关系或“盘整+盘整”分类。
        if draft.entry_position < active.center_entry_floor:
            if pending is not None and _crossing_center_belongs_to_left(
                draft,
                right_start_position=active.start_position,
            ):
                left = pending.previous
                if all(_core_key(item) != _core_key(draft) for item in left.centers):
                    left.centers.append(draft)
                    left.centers.sort(key=lambda item: item.c_position)
                left.core_consumed_to_position = max(
                    left.core_consumed_to_position or draft.c_position,
                    draft.c_position,
                )
                continue
            if not (
                pending is not None
                and _crossing_center_belongs_to_right(
                    draft,
                    right_start_position=active.start_position,
                )
            ):
                continue
        if (
            active.core_consumed_to_position is not None
            and draft.a_position <= active.core_consumed_to_position
            and not (
                pending is not None
                and _crossing_center_belongs_to_right(
                    draft,
                    right_start_position=active.start_position,
                )
            )
        ):
            continue

        if not active.centers:
            active.centers.append(draft)
            active.core_consumed_to_position = draft.c_position
            active.last_rule_id = RULE_ZSL_PROBE_CONFIRM_CENTER
            continue

        previous = active.centers[-1]
        relation = _strict_center_direction(previous, draft)
        if relation is not None and len(active.centers) == 1:
            active.travel_direction = relation
            active.trend_direction = relation
            active.centers.append(draft)
            active.core_consumed_to_position = draft.c_position
            active.last_rule_id = (
                RULE_ZSL_CLASSIFY_STRICT_UP
                if relation is BiDir.UP
                else RULE_ZSL_CLASSIFY_STRICT_DOWN
            )
            extreme = _directional_extreme(
                run,
                start_position=active.start_position,
                end_position=draft.c_position,
                direction=relation,
            )
            assert extreme is not None
            active.extreme_position = extreme
            if pending is not None:
                if (
                    pending.previous.travel_direction is relation
                    and _beyond(
                        run,
                        direction=relation,
                        left_position=pending.previous.extreme_position,
                        right_position=active.extreme_position,
                    )
                ):
                    active = _Active(
                        start_position=pending.previous.start_position,
                        travel_direction=relation,
                        extreme_position=active.extreme_position,
                        centers=[*pending.previous.centers, *active.centers],
                        trend_direction=relation,
                        core_consumed_to_position=active.core_consumed_to_position,
                        last_rule_id=RULE_ZSL_TURN_CANCEL_STRICT_EXTREME,
                    )
                elif draft.is_formal:
                    frozen.append(
                        _Frozen(
                            active=pending.previous,
                            confirmation_center=draft,
                        )
                    )
                    pending = None
            continue
        if relation is active.travel_direction:
            active.trend_direction = relation
            active.centers.append(draft)
            active.core_consumed_to_position = draft.c_position
            active.last_rule_id = (
                RULE_ZSL_CLASSIFY_STRICT_UP
                if relation is BiDir.UP
                else RULE_ZSL_CLASSIFY_STRICT_DOWN
            )
            if pending is not None and draft.is_formal:
                frozen.append(
                    _Frozen(
                        active=pending.previous,
                        confirmation_center=draft,
                    )
                )
                pending = None
            continue

        next_direction = (
            BiDir.DOWN if active.travel_direction is BiDir.UP else BiDir.UP
        )
        next_start = active.extreme_position + 1
        next_extreme = _directional_extreme(
            run,
            start_position=next_start,
            end_position=draft.c_position,
            direction=next_direction,
        )
        # 没有与新行进方向一致的完成终点，draft 仍是私有候选，不能提升。
        if next_extreme is None:
            continue

        previous_active = _copy_active(active)
        split_rule = (
            RULE_ZSL_SPLIT_NON_STRICT
            if relation is None
            else RULE_ZSL_PROBE_CONFIRM_CENTER
        )
        previous_active.last_rule_id = split_rule
        active = _Active(
            start_position=next_start,
            travel_direction=next_direction,
            extreme_position=next_extreme,
            centers=[draft],
            trend_direction=None,
            core_consumed_to_position=draft.c_position,
            last_rule_id=split_rule,
        )

        # 只处理尚在活动尾部、刚出生的“同向 + 反向 + 同向”。若新同向
        # 走势在出生事件内已经严格越过前同向极值，中间反向 probe 尚未
        # 获得稳定前缀资格，必须连同其私有中心一起撤销。更早项此后不再
        # 回看，确保真正 frozen 的历史不会被未来行情改写。
        if (
            pending is not None
            and pending.previous.travel_direction is active.travel_direction
            and _beyond(
                run,
                direction=active.travel_direction,
                left_position=pending.previous.extreme_position,
                right_position=active.extreme_position,
            )
        ):
            earlier = pending.previous
            active = _Active(
                start_position=earlier.start_position,
                travel_direction=active.travel_direction,
                extreme_position=active.extreme_position,
                centers=[*earlier.centers, *active.centers],
                trend_direction=(
                    active.trend_direction or earlier.trend_direction
                ),
                core_consumed_to_position=active.core_consumed_to_position,
                last_rule_id=RULE_ZSL_TURN_CANCEL_STRICT_EXTREME,
            )
            pending = None
        else:
            if pending is not None:
                if not draft.is_formal:
                    # 临时中心可以更新私有 probe，但不能让上一走势正式冻结。
                    # 当前实现只有一层 pending；在正式确认到来前继续保留原
                    # active/pending，避免用临时事件覆盖尚未确认的共享分界。
                    active = previous_active
                    continue
                frozen.append(
                    _Frozen(
                        active=pending.previous,
                        confirmation_center=draft,
                    )
                )
            pending = _PendingTurn(
                previous=previous_active,
                boundary_position=previous_active.extreme_position,
            )

    visible = pending.previous if pending is not None else active
    groups: list[list[_CenterCore]] = [item.active.centers for item in frozen]
    if pending is not None:
        groups.extend((pending.previous.centers, active.centers))
    else:
        groups.append(active.centers)
    promoted = [core for group in groups for core in group]
    close_by_core: dict[tuple[int, int, int, int], _CenterCore] = {}
    for item in frozen:
        group = item.active.centers
        formal_group = [item for item in group if item.is_formal]
        for left_core, right_core in zip(
            formal_group,
            formal_group[1:],
            strict=False,
        ):
            close_by_core.setdefault(_core_key(left_core), right_core)
        if not item.confirmation_center.is_formal:
            raise AssertionError("same-level frozen evidence must be formal")
        if formal_group:
            close_by_core.setdefault(
                _core_key(formal_group[-1]),
                item.confirmation_center,
            )
    pending_active = active if pending is not None else None
    return (
        frozen,
        visible if visible.centers else None,
        pending_active,
        promoted,
        close_by_core,
    )


def scan_same_level_center_events(
    legs: Sequence[LevelLeg],
) -> tuple[SameLevelCenterEvent, ...]:
    """独立返回各正式分解区间内重新定相位后的 formal 中枢事件。

    这里会复用 Reducer 已确定的分解边界，但不会读取最终公开中枢或 owner；
    因而测试仍可用它校验 ``event -> public center -> owner`` 三方守恒。
    """
    source = list(legs)
    if not source:
        return ()
    level = source[0].level
    source_type = source[0].source_type
    if any(
        item.level is not level or item.source_type is not source_type
        for item in source
    ):
        raise ValueError("same-level center events require one level and source_type")

    out: list[SameLevelCenterEvent] = []
    run_start = 0
    run_id = 0
    for index in range(1, len(source) + 1):
        if index < len(source) and _continuous(source[index - 1], source[index]):
            continue
        run = source[run_start:index]
        for segment in _segment_projection_plan(run):
            out.extend(
                SameLevelCenterEvent(
                    entry_position=run_start + item.entry_position,
                    a_position=run_start + item.a_position,
                    b_position=run_start + item.b_position,
                    c_position=run_start + item.c_position,
                    zd=item.zd,
                    zg=item.zg,
                    gg=item.gg,
                    dd=item.dd,
                    extended_positions=tuple(
                        run_start + position for position in item.extended_positions
                    ),
                    close_position=(
                        run_start + item.close_position
                        if item.close_position is not None
                        else None
                    ),
                    is_formal=True,
                    run_id=run_id,
                )
                for item in segment.cores
            )
        run_start = index
        run_id += 1
    return tuple(out)


def _validate_result_invariants(
    centers: Sequence[ZhongShu],
    zoushis: Sequence[CompletedZouShi],
    *,
    legs: Sequence[LevelLeg],
    close_evidence_source_ids: set[str],
) -> None:
    center_by_id = {item.id: item for item in centers}
    if len(center_by_id) != len(centers):
        raise AssertionError("same-level formal center ids must be unique")
    owner_counts = Counter(
        center_id
        for owner in zoushis
        for center_id in owner.zhongshu_ids
    )
    if set(owner_counts) != set(center_by_id) or any(
        count != 1 for count in owner_counts.values()
        ):
            raise AssertionError("same-level formal centers require exactly one owner")
    for owner in zoushis:
        if owner.completion_state is ZouShiBoundaryState.FROZEN and (
            owner.close_evidence_source_id not in close_evidence_source_ids
        ):
            raise AssertionError(
                "same-level frozen zoushi requires a completed opposing exit"
            )
        if owner.completion_state is ZouShiBoundaryState.FROZEN:
            for center_id in owner.zhongshu_ids:
                if center_by_id[center_id].end_ts > owner.end.ts:
                    raise AssertionError(
                        "same-level frozen split ends before its formal center C"
                    )
        if owner.kind is ZouShiKind.TREND:
            owned = [center_by_id[center_id] for center_id in owner.zhongshu_ids]
            direction = owner.trend_direction
            if direction is None:
                raise AssertionError("same-level trend requires a direction")
            supports_direction = any(
                (
                    direction is ZouShiDirection.UP
                    and right.dd > left.gg
                )
                or (
                    direction is ZouShiDirection.DOWN
                    and right.gg < left.dd
                )
                for left_index, left in enumerate(owned)
                for right in owned[left_index + 1 :]
            )
            if not supports_direction:
                raise AssertionError(
                    "same-level trend requires strict formal center relation"
                )
    leg_by_id = {item.source_id: item for item in legs}
    leg_by_index = {item.source_index: item for item in legs}
    position_by_id = {
        item.source_id: position for position, item in enumerate(legs)
    }
    position_by_index = {
        item.source_index: position for position, item in enumerate(legs)
    }
    run_id_by_position: list[int] = []
    run_id = 0
    for position, leg in enumerate(legs):
        if position > 0 and not _continuous(legs[position - 1], leg):
            run_id += 1
        run_id_by_position.append(run_id)
    forming_seen_by_run: set[int] = set()
    for owner in zoushis:
        owner_run_id = run_id_by_position[position_by_index[owner.start.source_index]]
        if owner.completion_state is ZouShiBoundaryState.FORMING:
            forming_seen_by_run.add(owner_run_id)
        elif owner_run_id in forming_seen_by_run:
            raise AssertionError(
                "same-level frozen zoushis must precede the forming tail in each run"
            )
        if owner.completion_state is not ZouShiBoundaryState.FROZEN:
            continue
        if not owner.zhongshu_ids:
            raise AssertionError("same-level frozen zoushi requires a formal center")
        first_center = center_by_id[owner.zhongshu_ids[0]]
        last_center = center_by_id[owner.zhongshu_ids[-1]]
        if first_center.entry_evidence_id is None:
            raise AssertionError("same-level center requires entry evidence")
        entry = leg_by_id[first_center.entry_evidence_id]
        exit_leg = leg_by_index[owner.end.source_index]
        if exit_leg.direction is not entry.direction:
            raise AssertionError("same-level exit direction must match center entry E")
        outside = (
            exit_leg.end_price > last_center.zg
            if entry.direction is BiDir.UP
            else exit_leg.end_price < last_center.zd
        )
        if not outside:
            raise AssertionError("same-level exit must leave the last formal center")
    for left, right in zip(zoushis, zoushis[1:], strict=False):
        left_position = position_by_index[left.end.source_index]
        right_position = position_by_index[right.start.source_index]
        if (
            (left.end.ts, left.end.price) != (right.start.ts, right.start.price)
            or right_position != left_position + 1
            or not _continuous(legs[left_position], legs[right_position])
        ):
            continue
        if not left.zhongshu_ids:
            raise AssertionError(
                "same-level non-tail zoushi requires a formal center"
            )
        first_center = center_by_id[left.zhongshu_ids[0]]
        last_center = center_by_id[left.zhongshu_ids[-1]]
        if first_center.entry_evidence_id is None:
            raise AssertionError("same-level center requires entry evidence")
        entry = leg_by_id[first_center.entry_evidence_id]
        exit_leg = leg_by_index[left.end.source_index]
        outside = (
            exit_leg.end_price > last_center.zg
            if entry.direction is BiDir.UP
            else exit_leg.end_price < last_center.zd
        )
        if exit_leg.direction is not entry.direction or not outside:
            raise AssertionError(
                "same-level published boundary requires an actual exit from the last center"
            )
        for center in centers:
            if center.entry_evidence_id is None:
                raise AssertionError("same-level center requires entry evidence")
            entry_position = position_by_id[center.entry_evidence_id]
            center_end_position = position_by_index[center.end_index]
            if entry_position < left_position < center_end_position:
                raise AssertionError(
                    "same-level confirmed split cannot cut a complete or extended center"
                )
        for center_id in right.zhongshu_ids:
            entry_id = center_by_id[center_id].entry_evidence_id
            if entry_id is None:
                raise AssertionError("same-level center requires entry evidence")
            if position_by_id[entry_id] < right_position:
                raise AssertionError(
                    "same-level right zoushi center must start at or after the split"
                )
    for center in centers:
        if center.extension_state is ZhongShuState.CLOSED and (
            center.close_evidence_id not in close_evidence_source_ids
        ):
            raise AssertionError(
                "same-level closed center requires formal center evidence"
            )


def _core_key(item: _CenterCore) -> tuple[int, int, int, int]:
    return (
        item.entry_position,
        item.a_position,
        item.b_position,
        item.c_position,
    )


def _build_centers(
    run: Sequence[LevelLeg],
    cores: Sequence[_CenterCore],
    close_by_core: dict[tuple[int, int, int, int], int],
    *,
    profile_id: str,
    config_hash: str | None,
) -> list[ZhongShu]:
    out: list[ZhongShu] = []
    for core in cores:
        entry = run[core.entry_position]
        a, b, c = (
            run[core.a_position],
            run[core.b_position],
            run[core.c_position],
        )
        extended = [run[position] for position in core.extended_positions]
        members = [a, b, c, *extended]
        close_position = close_by_core.get(_core_key(core))
        evidence = run[close_position] if close_position is not None else None
        dependency_end = (
            close_position
            if close_position is not None
            else core.member_end_position
        )
        out.append(
            ZhongShu(
                period=a.period,
                source_type=a.source_type,
                direction=a.direction,
                zg=core.zg,
                zd=core.zd,
                gg=core.gg,
                dd=core.dd,
                start_ts=a.start_ts,
                core_end_ts=c.end_ts,
                end_ts=members[-1].end_ts,
                start_index=a.source_index,
                end_index=members[-1].source_index,
                core_member_ids=(a.source_id, b.source_id, c.source_id),
                extended_member_ids=tuple(item.source_id for item in extended),
                member_count=len(members),
                extension_state=(
                    ZhongShuState.CLOSED
                    if close_position is not None
                    else ZhongShuState.OPEN
                ),
                mode=ZhongShuMode.SAME_LEVEL,
                entry_evidence_id=entry.source_id,
                entry_evidence_index=entry.source_index,
                close_evidence_id=evidence.source_id if evidence is not None else None,
                close_evidence_index=(
                    evidence.source_index if evidence is not None else None
                ),
                trace=_trace(
                    run[core.entry_position : dependency_end + 1],
                    rule_id=(
                        RULE_ZHONGSHU_SAME_LEVEL_CLOSE_RIGHT
                        if close_position is not None
                        else RULE_ZHONGSHU_SAME_LEVEL_OVERLAP3
                    ),
                    profile_id=profile_id,
                    config_hash=config_hash,
                ),
            )
        )
    return out


def _build_zoushi(
    run: Sequence[LevelLeg],
    centers: Sequence[ZhongShu],
    formal_cores: Sequence[_CenterCore],
    frozen: Sequence[_Frozen],
    active: _Active | None,
    pending_active: _Active | None,
    *,
    profile_id: str,
    config_hash: str | None,
) -> list[CompletedZouShi]:
    projections: list[
        tuple[
            _Active,
            ZouShiBoundaryState,
            _CenterCore | None,
            int | None,
        ]
    ] = [
        (
            _copy_active(item.active),
            ZouShiBoundaryState.FROZEN,
            item.confirmation_center,
            None,
        )
        for item in frozen
    ]
    if active is not None:
        projections.append(
            (
                _copy_active(active),
                ZouShiBoundaryState.FORMING,
                None,
                (
                    (
                        pending_active.centers[0].c_position
                        if pending_active.centers
                        else pending_active.extreme_position
                    )
                    if pending_active is not None
                    else len(run) - 1
                ),
            )
        )
    if pending_active is not None:
        projections.append(
            (
                _copy_active(pending_active),
                ZouShiBoundaryState.FORMING,
                None,
                len(run) - 1,
                )
            )

    if not projections and formal_cores:
        # 极值与 C 同时发生时，Reducer 可能尚未打开任何公开 active，但
        # Scanner 已经独立确认一个或多个正式中心。每个中心先各自发布一条
        # 可撤销的 forming 盘整；不能把多个非严格中心因兜底逻辑塞进同一
        # owner，更不能仅按数量伪装成趋势。后续严格破新极值仍由 Reducer
        # 的准分解点撤销/延续路径处理。
        for ordinal, core in enumerate(formal_cores):
            travel_direction = run[core.entry_position].direction
            projections.append(
                (
                    _Active(
                        start_position=(
                            core.entry_position
                            if ordinal == 0
                            else core.entry_position + 1
                        ),
                        travel_direction=travel_direction,
                        extreme_position=core.entry_position,
                        centers=[core],
                        core_consumed_to_position=core.c_position,
                        last_rule_id=RULE_ZSL_PROBE_CONFIRM_CENTER,
                    ),
                    ZouShiBoundaryState.FORMING,
                    None,
                    len(run) - 1,
                )
            )

    # CenterScanner 已提升的 formal 中枢必须按 C 所在的真实走势边界唯一
    # 归属。晚于旧走势终点的中心只能转交给后续走势；不能继续挂在旧
    # owner 名下，也不能通过同步删除中心与引用伪造冲突归零。
    assigned: list[list[_CenterCore]] = [[] for _ in projections]
    origin_by_key = {
        _core_key(core): index
        for index, (state, _, _, _) in enumerate(projections)
        for core in state.centers
    }
    owner_floor = 0
    for ordinal, core in enumerate(formal_cores):
        origin_index = origin_by_key.get(_core_key(core))
        if origin_index is not None:
            origin, completion_state, _, _ = projections[origin_index]
            if (
                # Reducer 已提交到 frozen 前缀的 formal center 归属不可再由
                # 未来 projection/极值重新分配。preliminary 只负责提供因果
                # 分界；区间内的最终 center owner 会在后续重定相中重建。
                completion_state is ZouShiBoundaryState.FROZEN
                or origin_index == 0
                or core.c_position <= origin.extreme_position + 1
            ):
                owner_index = origin_index
            else:
                owner_index = next(
                    (
                        index
                        for index, (state, _, _, _) in enumerate(projections)
                        if index > origin_index
                        and state.extreme_position >= core.c_position
                    ),
                    len(projections) - 1,
                )
        else:
            left_boundary = next(
                (
                    index
                    for index in range(len(projections) - 1)
                    if _crossing_center_belongs_to_left(
                        core,
                        right_start_position=(
                            projections[index + 1][0].start_position
                        ),
                    )
                ),
                None,
            )
            right_boundary = next(
                (
                    index
                    for index in range(len(projections) - 1)
                    if _crossing_center_belongs_to_right(
                        core,
                        right_start_position=(
                            projections[index + 1][0].start_position
                        ),
                    )
                ),
                None,
            )
            if left_boundary is not None:
                owner_index = left_boundary
            elif right_boundary is not None:
                owner_index = right_boundary + 1
            elif ordinal == 0:
                owner_index = 0
            else:
                owner_index = next(
                    (
                        index
                        for index, (state, _, _, _) in enumerate(projections)
                        if index >= owner_floor
                        and state.extreme_position >= core.c_position
                    ),
                    len(projections) - 1,
                )
        assigned[owner_index].append(core)
        owner_floor = owner_index

    normalized: list[
        tuple[
            _Active,
            ZouShiBoundaryState,
            _CenterCore | None,
            int | None,
        ]
    ] = []
    for index, (state, completion_state, close_center, horizon) in enumerate(
        projections
    ):
        owned = assigned[index]
        empty_forming_probe = (
            not owned
            and not state.centers
            and completion_state is ZouShiBoundaryState.FORMING
        )
        if not owned and not empty_forming_probe:
            continue
        state.centers = owned
        if empty_forming_probe:
            state.observed_to_position = state.extreme_position
            normalized.append((state, completion_state, close_center, horizon))
            continue
        # 正式中心的 C 只提高“确认/依赖水位”，不能反向改写走势的几何
        # 极值。走势终点只能由与首中心 E 同向的实际离开部件给出；若把
        # latest C 强行提升成 extreme，就会把 C 的起点误画成走势终点，
        # 还会让离开部件被右侧再次当作 E 使用。
        latest_c = max(item.c_position for item in owned)
        state.observed_to_position = max(state.extreme_position, latest_c)
        normalized.append((state, completion_state, close_center, horizon))

    for index in range(1, len(normalized)):
        previous = normalized[index - 1][0]
        current = normalized[index][0]
        # 左侧离开部件 X 完整归左；右侧只复用 X.end 这个价格/时间坐标，
        # 从下一部件开始，不能再次把 X 当作右侧中心 E。
        shared_start = previous.extreme_position + 1
        if shared_start <= current.extreme_position and shared_start < len(run):
            current.start_position = shared_start

    def make(
        state: _Active,
        *,
        completion_state: ZouShiBoundaryState,
        close_center: _CenterCore | None,
        forming_horizon: int | None = None,
    ) -> CompletedZouShi:
        start_leg = run[state.start_position]
        end_leg = run[state.extreme_position]
        center_by_key = {
            (item.entry_evidence_index, item.start_index, item.end_index): item
            for item in centers
        }
        owned = [
            center_by_key[
                (
                    run[item.entry_position].source_index,
                    run[item.a_position].source_index,
                    run[item.c_position].source_index,
                )
            ]
            for item in state.centers
        ]
        public_trend_direction = state.trend_direction
        if public_trend_direction is not None and not _supports_strict_direction(
            state.centers,
            public_trend_direction,
        ):
            public_trend_direction = None
        kind = (
            ZouShiKind.TREND
            if public_trend_direction is not None
            else ZouShiKind.CONSOLIDATION
        )
        direction = (
            ZouShiDirection(public_trend_direction.value)
            if public_trend_direction is not None
            else None
        )
        if state.centers:
            owned_member_end = max(item.c_position for item in state.centers)
            owned_member_start = min(item.entry_position for item in state.centers)
            member_start = min(state.start_position, owned_member_start)
            member_end = max(state.extreme_position, owned_member_end)
        else:
            member_start = state.start_position
            member_end = state.extreme_position
        end = _endpoint(end_leg, at_start=False)
        if close_center is None:
            dependency_end = (
                len(run) - 1 if forming_horizon is None else forming_horizon
            )
            dependency_end = max(dependency_end, member_end)
            evidence_id = None
            rule_id = state.last_rule_id
        else:
            # 真正冻结旧走势的是“后续正式中心 C 到达”这一输入事件。该
            # 中心仍处活动尾部，未来可能因严格突破被撤销，因此关闭证据
            # 固定记录其 C 来源部件，而不引用一个可能消失的中心 ID。
            dependency_end = close_center.c_position
            evidence_id = run[dependency_end].source_id
            rule_id = RULE_ZSL_TURN_CONFIRM
        members = run[member_start : member_end + 1]
        return CompletedZouShi(
            period=start_leg.period,
            level=start_leg.level,
            source_type=start_leg.source_type,
            kind=kind,
            trend_direction=direction,
            start=_endpoint(start_leg, at_start=True),
            end=end,
            start_source_id=start_leg.source_id,
            source_member_ids=tuple(item.source_id for item in members),
            zhongshu_ids=tuple(item.id for item in owned),
            completion_state=completion_state,
            close_evidence_source_id=evidence_id,
            trace=_trace(
                run[member_start : dependency_end + 1],
                rule_id=rule_id,
                profile_id=profile_id,
                config_hash=config_hash,
            ),
        )

    return [
        make(
            state,
            completion_state=completion_state,
            close_center=close_center,
            forming_horizon=horizon,
        )
        for state, completion_state, close_center, horizon in normalized
    ]


@dataclass(slots=True)
class _SegmentProjection:
    start_position: int
    end_position: int
    member_end_position: int
    qualifying_exit_position: int | None
    confirming_exit_position: int | None
    trigger_position: int | None
    cores: list[_CenterCore]
    rule_id: str
    provisional_tail: bool = False
    committed_core_to_position: int | None = None
    core_scan_to_position: int | None = None


def _segment_exit_direction(
    run: Sequence[LevelLeg],
    segment: _SegmentProjection,
) -> BiDir | None:
    """返回完整离开方向；核心 C 只能确认中枢，不能充当走势终点。"""
    if not segment.cores:
        return None
    first_exit = _segment_first_exit_position(run, segment)
    if first_exit is None or first_exit > segment.end_position:
        return None
    entry_direction = run[segment.cores[0].entry_position].direction
    exit_leg = run[segment.end_position]
    if exit_leg.direction is not entry_direction:
        return None
    eligible = [
        item
        for item in segment.cores
        if item.member_end_position < segment.end_position
    ]
    if not eligible:
        return None
    last_core = eligible[-1]
    outside = (
        exit_leg.end_price > last_core.zg
        if entry_direction is BiDir.UP
        else exit_leg.end_price < last_core.zd
    )
    return entry_direction if outside else None


def _segment_first_exit_position(
    run: Sequence[LevelLeg],
    segment: _SegmentProjection,
) -> int | None:
    """返回本段首次以首中心 E 同向有效离开的部件位置。"""
    del run  # 资格已经由左到右 scanner 计算并固化，禁止在投影层二次猜测。
    return segment.qualifying_exit_position


def _segment_projection_plan(
    run: Sequence[LevelLeg],
) -> list[_SegmentProjection]:
    """从左到右提交分界，并在每个区间内部独立重启中枢相位。"""
    if not run:
        return []
    horizon = len(run) - 1
    phase_cores_cache: dict[tuple[int, int], list[_CenterCore]] = {}
    extended_cores_cache: dict[tuple[int, int], list[_CenterCore]] = {}

    def projected_cores(
        start_position: int,
        end_position: int,
        *,
        extended: bool,
    ) -> list[_CenterCore]:
        cache = extended_cores_cache if extended else phase_cores_cache
        cache_key = (start_position, end_position)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        scanner = _scan_extended_center_events if extended else _scan_center_events
        local = scanner(run[start_position : end_position + 1])
        projected = [
            replace(
                item,
                entry_position=item.entry_position + start_position,
                a_position=item.a_position + start_position,
                b_position=item.b_position + start_position,
                c_position=item.c_position + start_position,
                extended_positions=tuple(
                    position + start_position
                    for position in item.extended_positions
                ),
                close_position=(
                    item.close_position + start_position
                    if item.close_position is not None
                    else None
                ),
            )
            for item in local
            if item.is_formal
        ]
        cache[cache_key] = projected
        return projected

    def cores_through(start_position: int, end_position: int) -> list[_CenterCore]:
        """返回只供准分解状态机消费的前缀相位事件。"""
        return projected_cores(start_position, end_position, extended=False)

    def extended_cores_through(
        start_position: int,
        end_position: int,
    ) -> list[_CenterCore]:
        """返回单个候选走势内部允许延伸后的最终中心。"""
        return projected_cores(start_position, end_position, extended=True)

    def first_exit(
        start_position: int,
        end_position: int,
    ) -> tuple[int | None, list[_CenterCore]]:
        cores = extended_cores_through(start_position, end_position)
        if not cores:
            return None, cores
        first_core = cores[0]
        direction = run[first_core.entry_position].direction
        for position in range(first_core.c_position + 1, end_position + 1):
            leg = run[position]
            if leg.direction is not direction:
                continue
            # X 只能读取它出现当下的完整中心状态。中心在该走势内部可以
            # 延伸，但 X 右侧尚未出现的数据绝不能再喂回左侧中心，否则会
            # 用未来行情吞掉已建立的准分解点。
            prefix_cores = extended_cores_through(start_position, position)
            eligible = [
                item
                for item in prefix_cores
                if item.member_end_position < position
            ]
            if not eligible:
                continue
            last_core = eligible[-1]
            outside = (
                leg.end_price > last_core.zg
                if direction is BiDir.UP
                else leg.end_price < last_core.zd
            )
            if outside:
                return position, cores
        return None, cores

    def exit_is_valid_for_final_cores(
        start_position: int,
        position: int,
        observed_to_position: int,
    ) -> bool:
        """按 X 当下的延伸中心验证离开，禁止右侧未来回写左侧分界。

        ``observed_to_position`` 只表示确认依赖水位，不参与 X 的几何判断。
        X 右侧一旦开始新的走势，后续重叠只能在新走势内部形成/延伸中枢；
        不能借未来把左侧准分解点重新解释成旧中枢延伸。准点的撤销或移动只
        能由外层状态机明确观察到原方向新极值或同价重锚触发。
        """
        del observed_to_position
        prefix_cores = extended_cores_through(start_position, position)
        if not prefix_cores:
            return False
        direction = run[prefix_cores[0].entry_position].direction
        leg = run[position]
        if leg.direction is not direction:
            return False
        eligible = [
            item
            for item in prefix_cores
            if item.member_end_position < position
        ]
        if not eligible:
            return False
        last_core = eligible[-1]
        return (
            leg.end_price > last_core.zg
            if direction is BiDir.UP
            else leg.end_price < last_core.zd
        )

    def exit_survives_internal_extension(
        start_position: int,
        position: int,
        observed_to_position: int,
    ) -> bool:
        """右侧候选 X 必须在自身走势的中枢延伸后仍是实际离开。

        这只用于尚未确认的右侧走势。它可以用 ``observed_to_position`` 内
        的后续部件判断早先 X 是否已被右侧自己的中枢延伸吸收；但绝不能
        用同一办法回写已经位于左侧的准分解点。
        """
        observed_cores = extended_cores_through(
            start_position,
            observed_to_position,
        )
        if not observed_cores:
            return False
        direction = run[observed_cores[0].entry_position].direction
        leg = run[position]
        if leg.direction is not direction:
            return False
        if any(
            item.entry_position <= position <= item.member_end_position
            for item in observed_cores
        ):
            return False
        eligible = [
            item
            for item in observed_cores
            if item.member_end_position < position
        ]
        if not eligible:
            return False
        last_core = eligible[-1]
        return (
            leg.end_price > last_core.zg
            if direction is BiDir.UP
            else leg.end_price < last_core.zd
        )

    confirmed_exit_cache: dict[tuple[int, int], int | None] = {}

    def valid_exit_through(
        start_position: int,
        observed_to_position: int,
    ) -> int | None:
        """返回旧保守投影截至当前前缀确认的首个离开点。

        这里保留旧候选的延迟确认，只用于生成不会过早切开的保守基线，
        不再作为最终公开分解规则。最终是否细分由
        ``refine_complete_phase_partitions`` 根据完整相位子走势的正式中枢、
        实际离开和后一 frozen 相位决定，不使用固定部件数量。
        """

        key = (start_position, observed_to_position)
        if key in confirmed_exit_cache:
            return confirmed_exit_cache[key]
        previous = confirmed_exit_cache.get(
            (start_position, observed_to_position - 1)
        )
        if previous is not None:
            confirmed_exit_cache[key] = previous
            return previous

        candidate, _ = first_exit(start_position, observed_to_position)
        if candidate is None:
            confirmed_exit_cache[key] = None
            return None
        confirmed = next(
            (
                position
                for position in range(candidate, observed_to_position + 1)
                if observed_to_position >= position + 2
                and exit_survives_internal_extension(
                    start_position,
                    position,
                    observed_to_position,
                )
            ),
            None,
        )
        confirmed_exit_cache[key] = confirmed
        return confirmed

    def forming_extreme(
        start_position: int,
        cores: Sequence[_CenterCore],
    ) -> int:
        direction = (
            run[cores[0].entry_position].direction
            if cores
            else run[start_position].direction
        )
        extreme = _directional_extreme(
            run,
            start_position=start_position,
            end_position=horizon,
            direction=direction,
        )
        endpoint = start_position if extreme is None else extreme
        if cores:
            # forming 尚无最终离开 X，但公开对象已经拥有这些正式中心。
            # 观察端点至少覆盖最后一个完整/延伸成员，避免线先结束、中枢却
            # 落在其右侧；真正冻结时端点再由符合 E 同向的离开极值确定。
            endpoint = max(endpoint, cores[-1].member_end_position)
        return endpoint

    def project(
        *,
        start_position: int,
        end_position: int,
        observed_to_position: int,
        completed: bool,
        qualifying_exit_position: int | None,
        confirming_exit_position: int | None,
        trigger_position: int | None,
        rule_id: str,
    ) -> _SegmentProjection:
        scan_to_position = max(
            observed_to_position,
            confirming_exit_position or observed_to_position,
            trigger_position or observed_to_position,
        )
        # 已完成左走势的正式中枢只能读取到自身 X；右侧确认部件只扩大
        # dependency/trace 水位，不能参与左侧中枢扫描。否则未来右侧中心会
        # 改变 scanner 相位，把已经成立的分解点和左侧中心一起吞回。
        observed_cores = cores_through(start_position, scan_to_position)
        cores = (
            [
                item
                for item in observed_cores
                if item.member_end_position < end_position
            ]
            if completed
            else observed_cores
        )
        member_end = end_position if completed else observed_to_position
        return _SegmentProjection(
            start_position=start_position,
            end_position=end_position,
            member_end_position=member_end,
            qualifying_exit_position=qualifying_exit_position,
            confirming_exit_position=confirming_exit_position,
            trigger_position=trigger_position,
            cores=cores,
            rule_id=rule_id,
        )

    def finalize_segments(
        segments: list[_SegmentProjection],
    ) -> list[_SegmentProjection]:
        """边界冻结后才发布区间内延伸中枢；任何返回路径都必须经过这里。"""
        segments = refine_complete_phase_partitions(segments)
        for segment in segments:
            # 最终中枢重扫只能读取该走势自身拥有的区间。分界后的第一部件
            # 已属于右走势，不能再作为左中枢延伸成员。关闭证据在投影层
            # 单独处理，不能为取证而把右侧数据重新喂给左侧结构扫描。
            scan_to_position = (
                segment.core_scan_to_position
                if segment.core_scan_to_position is not None
                else segment.member_end_position
            )
            extended = extended_cores_through(
                segment.start_position,
                scan_to_position,
            )
            # 分界后的第一部件只可作为关闭证据。仅当多观察这一部件不会
            # 增加任何延伸成员时，才把它的 close_position 回填到同一个
            # 中枢；若它仍有重叠，则它属于右走势，绝不能延伸左中枢。
            if scan_to_position < horizon:
                with_evidence = {
                    _core_key(item): item
                    for item in extended_cores_through(
                        segment.start_position,
                        scan_to_position + 1,
                    )
                }
                extended = [
                    (
                        replace(item, close_position=observed.close_position)
                        if (
                            (observed := with_evidence.get(_core_key(item)))
                            is not None
                            and observed.extended_positions
                            == item.extended_positions
                            and observed.close_position is not None
                        )
                        else item
                    )
                    for item in extended
                ]
            segment.cores = (
                [
                    item
                    for item in extended
                    if item.member_end_position < segment.end_position
                ]
                if segment.qualifying_exit_position is not None
                else extended
            )

        for left, right in zip(segments, segments[1:], strict=False):
            if right.start_position != left.end_position + 1:
                raise AssertionError(
                    "same-level projected segments must share one boundary coordinate"
                )
        return segments

    def refine_complete_phase_partitions(
        baseline: list[_SegmentProjection],
    ) -> list[_SegmentProjection]:
        """仅用连续且逐段有效的相位走势细分旧稳定区间。

        ``_scan_run`` 负责从左到右产生准分解走势；旧投影负责防止尚未完成
        的局部波动过早切开稳定历史。这里把两者组合成一条保守规则：只有
        两个或以上相位走势从旧区间左缘连续开始，并且每一段在自己的边界内
        都能独立重扫出正式中枢和 E 同向实际离开，才替换该稳定前缀。最后
        一个已成立走势可以保持 forming；它右侧尚不合格的活动尾部仍作为一
        条 forming 保留，但不能反向吞掉已经成立的左侧分界。

        因此不能因某一段只有 E+A/B、没有中心或没有实际离开而留下半截；
        也不会用固定“X2 后再等两部件”吞掉一串已经完整成立的同级走势。
        """

        if len(baseline) < 1:
            return baseline
        phase_frozen, phase_visible, phase_pending, _, _ = _scan_run(
            run,
            _scan_center_events(run),
        )
        phase_actives = [item.active for item in phase_frozen]
        for item in (phase_visible, phase_pending):
            if item is not None and all(
                (item.start_position, item.extreme_position)
                != (known.start_position, known.extreme_position)
                for known in phase_actives
            ):
                phase_actives.append(item)
        phase_actives.sort(key=lambda item: item.start_position)
        if len(phase_actives) < 2:
            return baseline

        phase_by_start = {item.start_position: item for item in phase_actives}
        frozen_by_start = {
            item.active.start_position: item for item in phase_frozen
        }
        validated: dict[tuple[int, int], list[_CenterCore] | None] = {}

        def valid_phase_cores(item: _Active) -> list[_CenterCore] | None:
            start = item.start_position
            end = item.extreme_position
            key = (start, end)
            if key in validated:
                return validated[key]
            if start > end:
                validated[key] = None
                return None
            cores = extended_cores_through(start, end)
            probe = _SegmentProjection(
                start_position=start,
                end_position=end,
                member_end_position=end,
                qualifying_exit_position=end,
                confirming_exit_position=None,
                trigger_position=None,
                cores=cores,
                rule_id=RULE_ZSL_SEGMENT_REPHASE,
            )
            if not cores or _segment_exit_direction(run, probe) is None:
                validated[key] = None
                return None
            validated[key] = cores
            return cores

        refinement_index: int | None = None
        for segment_index, segment in enumerate(baseline):
            if segment.qualifying_exit_position is None:
                continue
            candidates = [
                item
                for item in phase_actives
                if item.start_position >= segment.start_position
                and item.extreme_position <= segment.end_position
            ]
            valid_prefix: list[tuple[_Active, list[_CenterCore]]] = []
            expected_start = segment.start_position
            for item in candidates:
                if item.start_position != expected_start:
                    break
                cores = valid_phase_cores(item)
                if cores is None:
                    break
                valid_prefix.append((item, cores))
                expected_start = item.extreme_position + 1
            if len(valid_prefix) >= 2:
                refinement_index = segment_index
                break
        if refinement_index is None:
            return baseline

        refined = list(baseline[:refinement_index])
        current_start = baseline[refinement_index].start_position
        baseline_by_start = {
            item.start_position: index for index, item in enumerate(baseline)
        }
        while current_start <= horizon:
            item = phase_by_start.get(current_start)
            cores = valid_phase_cores(item) if item is not None else None
            if item is None or cores is None:
                break

            end = item.extreme_position
            next_frozen = frozen_by_start.get(end + 1)
            next_cores = (
                valid_phase_cores(next_frozen.active)
                if next_frozen is not None
                else None
            )
            if next_frozen is None or next_cores is None:
                # 后一相位已经冻结却在自己的区间内仍无完整中枢/实际离开，
                # 说明这里不是合法分解链。该无效性不会再被未来数据改写，
                # 可以安全保留当前位置起的旧活动尾部投影。
                if next_frozen is not None and next_cores is None:
                    baseline_tail = baseline_by_start.get(current_start)
                    if baseline_tail is not None:
                        refined.extend(baseline[baseline_tail:])
                        return refined
                break
            # X2 不是固定等待数量：后一完整走势自己的实际离开才是反向
            # 证据；它被下一 formal C 确认的时点是依赖/trace 水位。
            refined.append(
                _SegmentProjection(
                    start_position=current_start,
                    end_position=end,
                    member_end_position=end,
                    qualifying_exit_position=end,
                    confirming_exit_position=next_frozen.active.extreme_position,
                    trigger_position=next_frozen.confirmation_center.c_position,
                    cores=cores,
                    rule_id=RULE_ZSL_SEGMENT_REPHASE,
                )
            )
            current_start = end + 1

        # 尚未获得稳定 X2 的最右活动部分只能是一条 forming 尾部；它可在
        # 后续前缀内继续更新，但不能改变上面已经提交的 frozen 对象。
        tail_item = phase_by_start.get(current_start)
        tail_item_cores = (
            valid_phase_cores(tail_item) if tail_item is not None else None
        )
        tail_core_horizon = (
            tail_item.extreme_position
            if tail_item is not None and tail_item_cores is not None
            else horizon
        )
        tail_cores = extended_cores_through(current_start, tail_core_horizon)
        committed_core_to = max(
            (
                item.active.extreme_position
                for item in phase_frozen
                if item.active.start_position >= current_start
            ),
            default=None,
        )
        tail_end = (
            tail_item.extreme_position
            if tail_item is not None and tail_item_cores is not None
            else forming_extreme(current_start, tail_cores)
        )
        refined.append(
            _SegmentProjection(
                start_position=current_start,
                end_position=tail_end,
                member_end_position=horizon,
                qualifying_exit_position=None,
                confirming_exit_position=None,
                trigger_position=None,
                cores=tail_cores,
                rule_id=RULE_ZSL_PROBE_OPEN,
                provisional_tail=True,
                committed_core_to_position=committed_core_to,
                core_scan_to_position=tail_core_horizon,
            )
        )
        return refined

    segments: list[_SegmentProjection] = []
    start_position = 0
    # 连续 run 的左缘没有上一走势提供方向。若最早相位始终没有形成与其 E
    # 同向的实际离开，而右移一项的相位已经完成，则按共享首中枢双相位规则
    # 选择右移相位。该选择只允许发生一次，内部正式分界仍从 X 后第一部件
    # 原位重启，不能借此跳过任何右侧部件。
    base_exit, _ = first_exit(0, horizon)
    if base_exit is None and horizon >= 4:
        shifted_exit, _ = first_exit(1, horizon)
        if shifted_exit is not None:
            start_position = 1
    while start_position <= horizon:
        exit_position, current_cores = first_exit(start_position, horizon)
        if exit_position is None:
            segments.append(
                project(
                    start_position=start_position,
                    end_position=forming_extreme(start_position, current_cores),
                    observed_to_position=horizon,
                    completed=False,
                    qualifying_exit_position=None,
                    confirming_exit_position=None,
                    trigger_position=None,
                    rule_id=RULE_ZSL_SEGMENT_REPHASE,
                )
            )
            break

        qualifying_exit_position = exit_position
        segment_rule_id = RULE_ZSL_SEGMENT_REPHASE
        while True:
            right_start = exit_position + 1
            direction = run[current_cores[0].entry_position].direction
            extension = None
            extension_anchor = exit_position
            confirmed_at = None
            confirming_exit_position = None
            for observed_to in range(right_start, horizon + 1):
                leg = run[observed_to]
                if leg.direction is direction:
                    strict_extension = _beyond(
                        run,
                        direction=direction,
                        left_position=extension_anchor,
                        right_position=observed_to,
                    )
                    if (
                        strict_extension
                        or leg.end_price == run[extension_anchor].end_price
                    ):
                        extension = observed_to
                        segment_rule_id = (
                            RULE_ZSL_TURN_CANCEL_STRICT_EXTREME
                            if strict_extension
                            else RULE_ZSL_PROBE_REANCHOR_EQUAL
                        )
                        break

                observed_right_exit = valid_exit_through(right_start, observed_to)
                if (
                    observed_right_exit is not None
                    and observed_to >= observed_right_exit + 2
                ):
                    confirmed_at = observed_to
                    confirming_exit_position = observed_right_exit
                    break

            if extension is not None:
                exit_position = extension
                continue

            validation_horizon = (
                confirmed_at if confirmed_at is not None else horizon
            )
            if not exit_is_valid_for_final_cores(
                start_position,
                exit_position,
                validation_horizon,
            ):
                replacement = next(
                    (
                        position
                        for position in range(exit_position + 1, horizon + 1)
                        if exit_is_valid_for_final_cores(
                            start_position,
                            position,
                            validation_horizon,
                        )
                    ),
                    None,
                )
                if replacement is None:
                    latest_cores = cores_through(start_position, horizon)
                    segments.append(
                        project(
                            start_position=start_position,
                            end_position=forming_extreme(
                                start_position,
                                latest_cores,
                            ),
                            observed_to_position=horizon,
                            completed=False,
                            qualifying_exit_position=None,
                            confirming_exit_position=None,
                            trigger_position=None,
                            rule_id=RULE_ZSL_SEGMENT_REPHASE,
                        )
                    )
                    return finalize_segments(segments)
                exit_position = replacement
                qualifying_exit_position = replacement
                current_cores = cores_through(start_position, horizon)
                segment_rule_id = RULE_ZSL_SEGMENT_REPHASE
                continue

            # 即使 X 恰好位于当前 horizon，仍必须先经过上面的最终中心复核。
            # 该尾部不能走快捷提交，否则同价重锚/新 core 会令旧 X 失效，
            # 并让已 frozen 的前缀在下一部件到来后回退为 forming。
            if right_start > horizon:
                segments.append(
                    project(
                        start_position=start_position,
                        end_position=exit_position,
                        observed_to_position=exit_position,
                        completed=True,
                        qualifying_exit_position=qualifying_exit_position,
                        confirming_exit_position=None,
                        trigger_position=None,
                        rule_id=segment_rule_id,
                    )
                )
                return finalize_segments(segments)

            right_exit, right_cores = first_exit(right_start, horizon)

            segments.append(
                project(
                    start_position=start_position,
                    end_position=exit_position,
                    observed_to_position=exit_position,
                    completed=True,
                    qualifying_exit_position=qualifying_exit_position,
                    confirming_exit_position=confirming_exit_position,
                    trigger_position=(
                        confirmed_at if confirmed_at is not None else right_start
                    ),
                    rule_id=(
                        segment_rule_id
                        if confirmed_at is not None
                        else RULE_ZSL_PROBE_OPEN
                    ),
                )
            )
            if confirmed_at is None and right_exit is None:
                segments.append(
                    project(
                        start_position=right_start,
                        end_position=forming_extreme(right_start, right_cores),
                        observed_to_position=horizon,
                        completed=False,
                        qualifying_exit_position=None,
                        confirming_exit_position=None,
                        trigger_position=right_start,
                        rule_id=RULE_ZSL_PROBE_OPEN,
                    )
                )
                return finalize_segments(segments)
            start_position = right_start
            break

    return finalize_segments(segments)


def _reproject_segment_local(
    run: Sequence[LevelLeg],
    *,
    profile_id: str,
    config_hash: str | None,
) -> tuple[list[ZhongShu], list[CompletedZouShi], set[str]]:
    """按已确定分解区间重启中枢相位，禁止 E+A/B/C 穿越边界。"""
    if not run:
        return [], [], set()
    segments = _segment_projection_plan(run)

    all_cores = [core for segment in segments for core in segment.cores]
    close_by_core: dict[tuple[int, int, int, int], int] = {}
    effective_states: list[ZouShiBoundaryState] = []
    exit_directions = [
        _segment_exit_direction(run, segment) for segment in segments
    ]
    freeze_evidence_positions: list[int | None] = []
    for index, segment in enumerate(segments):
        next_segment = segments[index + 1] if index + 1 < len(segments) else None
        evidence_position = segment.confirming_exit_position
        evidence_direction = (
            run[evidence_position].direction
            if evidence_position is not None
            else None
        )
        # ``confirming_exit_position`` 是后一完整相位走势在自己的历史前缀中
        # 已由 formal C 锁定的实际离开 X2。确认水位来自结构事件，不再使用
        # “X2 后固定再等两部件”；右走势后来继续延伸也不能让已经 frozen
        # 的左走势短暂降级或消失。
        can_freeze = (
            exit_directions[index] is not None
            and evidence_position is not None
            and evidence_direction is not exit_directions[index]
            and bool(segment.cores)
            and next_segment is not None
            and bool(next_segment.cores)
            and (
                index == 0
                or freeze_evidence_positions[index - 1] is not None
            )
        )
        freeze_evidence_positions.append(evidence_position if can_freeze else None)

    for index, segment in enumerate(segments):
        can_freeze = freeze_evidence_positions[index] is not None
        effective_states.append(
            ZouShiBoundaryState.FROZEN
            if can_freeze
            else ZouShiBoundaryState.FORMING
        )
        # 中枢生命周期与走势生命周期分离：已提交区间内，后一 formal C
        # 一出现就关闭前一正式中心。首区间天然已提交；后续区间只有在前一
        # 走势冻结后才提交。仍挂在 provisional 分界右侧的中心可整体撤销，
        # 此时不得提前发布不可回写的 CLOSED。
        segment_is_committed = (
            index == 0
            or effective_states[index - 1] is ZouShiBoundaryState.FROZEN
        ) and not segment.provisional_tail
        if segment_is_committed or segment.committed_core_to_position is not None:
            observed_limit = max(
                segment.member_end_position,
                segment.trigger_position or segment.member_end_position,
                segment.confirming_exit_position or segment.member_end_position,
            )
            for core in segment.cores:
                core_is_committed = segment_is_committed or (
                    segment.committed_core_to_position is not None
                    and core.member_end_position
                    <= segment.committed_core_to_position
                )
                if not core_is_committed:
                    continue
                if (
                    core.close_position is not None
                    and core.close_position <= observed_limit
                ):
                    close_by_core[_core_key(core)] = core.close_position
            # 走势分界的反向确认只冻结走势，不能顺带关闭中枢。中枢是否
            # CLOSED 只能来自它自己的正式离开证据 ``core.close_position``；
            # 两种生命周期必须保持独立，避免未来走势证据改写旧中枢。

    centers = _build_centers(
        run,
        all_cores,
        close_by_core,
        profile_id=profile_id,
        config_hash=config_hash,
    )
    position_by_id = {
        item.source_id: position for position, item in enumerate(run)
    }
    center_by_key: dict[tuple[int, int, int, int], ZhongShu] = {}
    for item in centers:
        if item.entry_evidence_id is None:
            raise AssertionError("same-level center requires entry evidence")
        center_by_key[
            (
                position_by_id[item.entry_evidence_id],
                position_by_id[item.core_member_ids[0]],
                position_by_id[item.core_member_ids[1]],
                position_by_id[item.core_member_ids[2]],
            )
        ] = item
    out: list[CompletedZouShi] = []
    for index, (segment, completion_state) in enumerate(
        zip(segments, effective_states, strict=True)
    ):
        owned = [center_by_key[_core_key(core)] for core in segment.cores]
        strict_directions = {
            direction
            for left_index, left in enumerate(segment.cores)
            for right in segment.cores[left_index + 1 :]
            if (direction := _strict_center_direction(left, right)) is not None
        }
        trend_direction = (
            next(iter(strict_directions)) if len(strict_directions) == 1 else None
        )
        kind = (
            ZouShiKind.TREND
            if trend_direction is not None
            else ZouShiKind.CONSOLIDATION
        )
        zoushi_direction = (
            ZouShiDirection(trend_direction.value)
            if trend_direction is not None
            else None
        )
        close_evidence_position = (
            freeze_evidence_positions[index]
            if completion_state is ZouShiBoundaryState.FROZEN
            else None
        )
        if (
            completion_state is ZouShiBoundaryState.FROZEN
            and close_evidence_position is None
        ):
            raise AssertionError("frozen same-level split requires opposing exit")
        dependency_end = (
            max(
                close_evidence_position,
                segment.trigger_position or close_evidence_position,
            )
            if close_evidence_position is not None
            else max(segment.member_end_position, segment.start_position)
        )
        if (
            close_evidence_position is None
            and segment.trigger_position is not None
        ):
            dependency_end = max(dependency_end, segment.trigger_position)
        rule_id = (
            RULE_ZSL_TURN_CONFIRM
            if completion_state is ZouShiBoundaryState.FROZEN
            else segment.rule_id
        )
        members = run[
            segment.start_position : segment.member_end_position + 1
        ]
        if not members:
            members = [run[segment.start_position]]
        start_leg = run[segment.start_position]
        out.append(
            CompletedZouShi(
                period=start_leg.period,
                level=start_leg.level,
                source_type=start_leg.source_type,
                kind=kind,
                trend_direction=zoushi_direction,
                start=_endpoint(start_leg, at_start=True),
                end=_endpoint(run[segment.end_position], at_start=False),
                start_source_id=start_leg.source_id,
                source_member_ids=tuple(item.source_id for item in members),
                zhongshu_ids=tuple(item.id for item in owned),
                completion_state=completion_state,
                close_evidence_source_id=(
                    run[close_evidence_position].source_id
                    if close_evidence_position is not None
                    else None
                ),
                trace=_trace(
                    run[segment.start_position : dependency_end + 1],
                    rule_id=rule_id,
                    profile_id=profile_id,
                    config_hash=config_hash,
                ),
            )
        )
    evidence = {
        run[item.close_position].source_id
        for item in all_cores
        if item.close_position is not None
    } | {
        run[evidence_position].source_id
        for state, evidence_position in zip(
            effective_states,
            freeze_evidence_positions,
            strict=True,
        )
        if state is ZouShiBoundaryState.FROZEN
        and evidence_position is not None
    }
    return centers, out, evidence


def build_same_level_result(
    legs: Sequence[LevelLeg],
    *,
    profile_id: str,
    config_hash: str | None,
) -> LevelBuildResult:
    """逐项处理全部连续 run；批量只是同一事件函数的顺序重放。"""
    source = list(legs)
    if not source:
        raise ValueError("same-level result requires at least one leg")
    level = source[0].level
    source_type = source[0].source_type
    if any(item.level is not level or item.source_type is not source_type for item in source):
        raise ValueError("same-level legs must share level and source_type")

    all_centers: list[ZhongShu] = []
    all_zoushis: list[CompletedZouShi] = []
    close_evidence_source_ids: set[str] = set()
    run_start = 0
    for index in range(1, len(source) + 1):
        if index < len(source) and _continuous(source[index - 1], source[index]):
            continue
        run = source[run_start:index]
        centers, zoushis, evidence = _reproject_segment_local(
            run,
            profile_id=profile_id,
            config_hash=config_hash,
        )
        all_centers.extend(centers)
        all_zoushis.extend(zoushis)
        close_evidence_source_ids.update(evidence)
        run_start = index

    _validate_result_invariants(
        all_centers,
        all_zoushis,
        legs=source,
        close_evidence_source_ids=close_evidence_source_ids,
    )
    return LevelBuildResult(
        level=level,
        source_type=source_type,
        legs=tuple(source),
        zhongshus=tuple(all_centers),
        zoushis=tuple(all_zoushis),
    )
