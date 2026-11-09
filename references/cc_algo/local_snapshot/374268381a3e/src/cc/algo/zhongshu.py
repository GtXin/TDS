"""中枢 Gate B：笔/线段共用的闭区间重叠与延伸算法。

只实现成立、ZG/ZD/GG/DD 与第 20 课中心定理一的延伸。扩展、新生、消亡、
高级别中枢与中枢间关系明确留后续 PR。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from cc.algo.bi import bi_confirmed_flags
from cc.algo.config import ChanConfig, XianduanPreset
from cc.algo.models import (
    Bi,
    BiDir,
    LevelBuildResult,
    LevelLeg,
    Xianduan,
    ZhongShu,
    ZhongShuMode,
    ZhongShuSource,
    ZhongShuState,
    ZouShiLevel,
)
from cc.algo.same_level import build_same_level_result
from cc.algo.trace import (
    RULE_ZHONGSHU_EXTEND_OVERLAP,
    RULE_ZHONGSHU_FORM_OVERLAP3,
    RULE_ZHONGSHU_SAME_LEVEL_CLOSE_RIGHT,
    RULE_ZHONGSHU_SAME_LEVEL_OVERLAP3,
    StructTrace,
)
from cc.algo.zhongshu_phase import (
    resolve_initial_zhongshu_phase,
    scan_zhongshu_candidate,
)

ZHONGSHU_ALGO_VERSION = 15
_ALGO_CARD_ID = "zhongshu-v1"
XIANDUAN_DISABLED_REASON = "xianduan_zhongshu_requires_standard_l1_frozen"


@dataclass(frozen=True, slots=True)
class ZsLeg:
    """笔/线段投影成的统一中枢输入。"""

    source_id: str
    source_index: int
    direction: BiDir
    start_ts: int
    end_ts: int
    high: float
    low: float
    start_price: float | None = None
    end_price: float | None = None
    trace: StructTrace | None = None

    def __post_init__(self) -> None:
        if self.low > self.high:
            raise ValueError(f"invalid ZsLeg range: low {self.low} > high {self.high}")


def _leg_from_struct(index: int, item: Bi | Xianduan) -> ZsLeg:
    return ZsLeg(
        source_id=item.id,
        source_index=index,
        direction=item.direction,
        start_ts=item.start_ts,
        end_ts=item.end_ts,
        high=item.high,
        low=item.low,
        start_price=item.start_price,
        end_price=item.end_price,
        trace=item.trace,
    )


def legs_from_bis(bis: Sequence[Bi], n_merged: int) -> list[ZsLeg]:
    """只投影最长 confirmed 笔前缀，遇到首个 provisional 即停止。"""
    legs: list[ZsLeg] = []
    for index, (bi, confirmed) in enumerate(
        zip(bis, bi_confirmed_flags(bis, n_merged), strict=True)
    ):
        if not confirmed:
            break
        legs.append(_leg_from_struct(index, bi))
    return legs


def legs_from_xianduans(
    xianduans: Sequence[Xianduan], cfg: ChanConfig
) -> list[ZsLeg]:
    """只投影默认 standard、L1、frozen 线段的最长前缀。"""
    selected = select_l1_frozen_xianduan_prefix(xianduans, cfg)
    return [_leg_from_struct(index, item) for index, item in enumerate(selected)]


def select_l1_frozen_xianduan_prefix(
    xianduans: Sequence[Xianduan], cfg: ChanConfig
) -> tuple[Xianduan, ...]:
    """选择 standard Engine 的最长 frozen 线段前缀，供段中枢/L1 共用。"""
    if cfg.normalize().xianduan_preset is not XianduanPreset.STANDARD:
        return ()
    selected: list[Xianduan] = []
    for item in xianduans:
        if item.trace is None or item.trace.freeze_state != "frozen":
            break
        selected.append(item)
    return tuple(selected)


def _overlap(low_a: float, high_a: float, low_b: float, high_b: float) -> bool:
    """闭区间重叠；端点相等（相切）仍为 True。"""
    return max(low_a, low_b) <= min(high_a, high_b)


def _restart_index(legs: Sequence[ZsLeg], j: int, zd: float, zg: float) -> int:
    """按离开中枢的价格方向选择下一走势的进入锚点 E。

    ``legs[j]`` 已与 ``[ZD,ZG]`` 无重叠，因此只可能完整位于上方或下方。
    上方离开选向上腿、下方离开选向下腿；该腿可能是旧中枢最后成员
    ``j-2``，也可能是关闭证据前的反向腿 ``j-1``。
    """
    evidence = legs[j]
    exit_direction = BiDir.UP if evidence.low > zg else BiDir.DOWN
    preceding = j - 1
    if legs[preceding].direction is exit_direction:
        return preceding
    return max(0, j - 2)


def _continuous(a: ZsLeg, b: ZsLeg) -> bool:
    return a.end_ts == b.start_ts and a.direction is not b.direction


def _trace_for_rule(
    deps: Sequence[ZsLeg],
    *,
    rule_id: str,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    source_from = [
        leg.trace.source_from_ts
        if leg.trace and leg.trace.source_from_ts is not None
        else leg.start_ts
        for leg in deps
    ]
    source_to = [
        leg.trace.source_to_ts if leg.trace and leg.trace.source_to_ts is not None else leg.end_ts
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
        rule_id=rule_id,
        profile_id=profile_id,
        config_hash=config_hash,
        source_from_ts=min(source_from),
        source_to_ts=max(source_to),
        merged_from_index=min(merged_from) if merged_from else None,
        merged_to_index=max(merged_to) if merged_to else None,
        dep_to_index=max(dep_to) if dep_to else None,
    )


def _trace(
    entry_evidence: ZsLeg,
    members: Sequence[ZsLeg],
    evidence: ZsLeg | None,
    *,
    extended: bool,
    profile_id: str,
    config_hash: str | None,
) -> StructTrace:
    deps = [entry_evidence, *members, *([evidence] if evidence is not None else [])]
    return _trace_for_rule(
        deps,
        rule_id=(RULE_ZHONGSHU_EXTEND_OVERLAP if extended else RULE_ZHONGSHU_FORM_OVERLAP3),
        profile_id=profile_id,
        config_hash=config_hash,
    )


@dataclass(frozen=True, slots=True)
class _SameLevelCore:
    """同级分解的 E+A/B/C 扫描结果；只在本模块内部使用。"""

    entry: ZsLeg
    members: tuple[ZsLeg, ZsLeg, ZsLeg]


def _entry_reaches_core(entry: ZsLeg, zd: float, zg: float) -> bool:
    """进入证据须触及或穿过闭区间 [ZD, ZG]，不得整笔位于区间外。"""
    return _overlap(entry.low, entry.high, zd, zg)


def _build_same_level_run(
    legs: Sequence[ZsLeg],
    *,
    source_type: ZhongShuSource,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[ZhongShu]:
    """从左到右执行无延伸同级分解；核心笔不在相邻中枢间复用。"""
    cores: list[_SameLevelCore] = []
    index = 0
    while index + 3 < len(legs):
        entry = legs[index]
        a, b, c = legs[index + 1], legs[index + 2], legs[index + 3]
        zd = max(a.low, b.low, c.low)
        zg = min(a.high, b.high, c.high)
        if zd > zg:
            # 第一个中枢尚未确定分解相位，可逐笔寻找最早合法 E；一旦已有
            # 中枢，下一走势必须从旧 C 之后沿同一奇偶序向右生长，只能每次
            # 跨两笔寻找下一个同方向 E，禁止按前中枢价格临时跳换相位。
            index += 1 if not cores else 2
            continue
        if not _entry_reaches_core(entry, zd, zg):
            index += 1 if not cores else 2
            continue
        cores.append(_SameLevelCore(entry=entry, members=(a, b, c)))
        # 核心 A/B/C 不复用；旧 C 仅作为下一候选的进入证据 E。
        index += 3

    out: list[ZhongShu] = []
    for core_index, core in enumerate(cores):
        a, b, c = core.members
        right = cores[core_index + 1] if core_index + 1 < len(cores) else None
        # 右中枢只有第三根核心笔完成后才真正成立；因此关闭证据必须指向
        # 右 C 的事件水位，不能指向尚不足以确认结构的右 A。
        close_evidence = right.members[-1] if right is not None else None
        trace_deps = [core.entry, *core.members]
        if right is not None:
            # 右侧中枢必须完整成立后才能冻结左侧，因此 trace 纳入右侧 E+A/B/C，
            # close_evidence_id 指向右侧第三核心成员 C，准确记录结构成立事件。
            trace_deps.extend((right.entry, *right.members))
        out.append(
            ZhongShu(
                period=period,
                source_type=source_type,
                direction=a.direction,
                zg=min(a.high, b.high, c.high),
                zd=max(a.low, b.low, c.low),
                gg=max(a.high, c.high),
                dd=min(a.low, c.low),
                start_ts=a.start_ts,
                core_end_ts=c.end_ts,
                end_ts=c.end_ts,
                start_index=a.source_index,
                end_index=c.source_index,
                core_member_ids=(a.source_id, b.source_id, c.source_id),
                extended_member_ids=(),
                member_count=3,
                extension_state=(
                    ZhongShuState.CLOSED if right is not None else ZhongShuState.OPEN
                ),
                mode=ZhongShuMode.SAME_LEVEL,
                entry_evidence_id=core.entry.source_id,
                entry_evidence_index=core.entry.source_index,
                close_evidence_id=(
                    close_evidence.source_id if close_evidence is not None else None
                ),
                close_evidence_index=(
                    close_evidence.source_index if close_evidence is not None else None
                ),
                trace=_trace_for_rule(
                    trace_deps,
                    rule_id=(
                        RULE_ZHONGSHU_SAME_LEVEL_CLOSE_RIGHT
                        if right is not None
                        else RULE_ZHONGSHU_SAME_LEVEL_OVERLAP3
                    ),
                    profile_id=profile_id,
                    config_hash=config_hash,
                ),
            )
        )
    return out


def _build_run(
    legs: Sequence[ZsLeg],
    *,
    source_type: ZhongShuSource,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[ZhongShu]:
    out: list[ZhongShu] = []
    i = 0
    required_entry_direction: BiDir | None = None
    while i + 3 < len(legs):
        candidate = scan_zhongshu_candidate(legs, i)
        if candidate is None:
            i += 1
            continue
        entry_evidence = legs[candidate.entry_index]
        if (
            required_entry_direction is not None
            and entry_evidence.direction is not required_entry_direction
        ):
            i += 1
            continue
        if required_entry_direction is None:
            candidate = resolve_initial_zhongshu_phase(legs, candidate)
            entry_evidence = legs[candidate.entry_index]

        a, b, c = (legs[index] for index in candidate.core_indexes)
        extended = [legs[index] for index in candidate.extended_indexes]
        members: list[ZsLeg] = [a, b, c, *extended]
        evidence = (
            legs[candidate.close_index]
            if candidate.close_index is not None
            else None
        )

        state = ZhongShuState.CLOSED if evidence is not None else ZhongShuState.OPEN
        out.append(
            ZhongShu(
                period=period,
                source_type=source_type,
                direction=a.direction,
                zg=candidate.zg,
                zd=candidate.zd,
                gg=candidate.gg,
                dd=candidate.dd,
                start_ts=a.start_ts,
                core_end_ts=c.end_ts,
                end_ts=members[-1].end_ts,
                start_index=a.source_index,
                end_index=members[-1].source_index,
                core_member_ids=(a.source_id, b.source_id, c.source_id),
                extended_member_ids=tuple(leg.source_id for leg in extended),
                member_count=len(members),
                extension_state=state,
                mode=ZhongShuMode.EXTEND,
                entry_evidence_id=entry_evidence.source_id,
                entry_evidence_index=entry_evidence.source_index,
                close_evidence_id=evidence.source_id if evidence is not None else None,
                close_evidence_index=evidence.source_index if evidence is not None else None,
                trace=_trace(
                    entry_evidence,
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
        # 用户实图口径：按关闭证据相对 [ZD,ZG] 的价格位置判断向上/向下离开，
        # 再从 j-2/j-1 中选择同方向腿作下一走势 E；其后一腿才是核心 A。
        # 这同时覆盖 bi289→核心 bi290/291/292 与 bi295→核心 bi296/297/298。
        assert candidate.exit_direction is not None
        required_entry_direction = BiDir(candidate.exit_direction)
        assert candidate.close_index is not None
        i = _restart_index(
            legs, candidate.close_index, candidate.zd, candidate.zg
        )
    return out


def build_zhongshus(
    legs: Sequence[ZsLeg],
    *,
    source_type: ZhongShuSource,
    mode: ZhongShuMode = ZhongShuMode.EXTEND,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> list[ZhongShu]:
    """在每个连续、方向交替的输入分段内扫描中枢，绝不跨空洞拼接。"""
    source_type = ZhongShuSource(source_type)
    mode = ZhongShuMode(mode)
    if mode is ZhongShuMode.SAME_LEVEL:
        return list(
            build_same_level_level_result(
                legs,
                source_type=source_type,
                period=period,
                profile_id=profile_id,
                config_hash=config_hash,
            ).zhongshus
        )
    out: list[ZhongShu] = []
    run_start = 0
    for index in range(1, len(legs)):
        if _continuous(legs[index - 1], legs[index]):
            continue
        builder = _build_run if mode is ZhongShuMode.EXTEND else _build_same_level_run
        out.extend(
            builder(
                legs[run_start:index],
                source_type=source_type,
                period=period,
                profile_id=profile_id,
                config_hash=config_hash,
            )
        )
        run_start = index
    builder = _build_run if mode is ZhongShuMode.EXTEND else _build_same_level_run
    out.extend(
        builder(
            legs[run_start:],
            source_type=source_type,
            period=period,
            profile_id=profile_id,
            config_hash=config_hash,
        )
    )
    return out


def build_same_level_level_result(
    legs: Sequence[ZsLeg],
    *,
    source_type: ZhongShuSource,
    period: str,
    profile_id: str,
    config_hash: str | None,
) -> LevelBuildResult:
    """把中枢正式输入适配一次，并返回中枢/走势共享的完整结果。

    Engine 的 ``same_level`` 正式路径只调用本入口一次；两个公开视图随后
    复用同一个不可变 ``LevelBuildResult``，不再各自重扫基础部件。
    """
    resolved_source = ZhongShuSource(source_type)
    level = (
        ZouShiLevel.L0
        if resolved_source is ZhongShuSource.BI
        else ZouShiLevel.L1
    )
    level_legs = tuple(
        LevelLeg(
            period=period,
            level=level,
            source_type=resolved_source,
            source_id=item.source_id,
            source_index=item.source_index,
            direction=item.direction,
            start_ts=item.start_ts,
            end_ts=item.end_ts,
            start_price=(
                item.start_price
                if item.start_price is not None
                else (item.low if item.direction is BiDir.UP else item.high)
            ),
            end_price=(
                item.end_price
                if item.end_price is not None
                else (item.high if item.direction is BiDir.UP else item.low)
            ),
            high=item.high,
            low=item.low,
            trace=item.trace,
        )
        for item in legs
    )
    if not level_legs:
        return LevelBuildResult(
            level=level,
            source_type=resolved_source,
            legs=(),
            zhongshus=(),
            zoushis=(),
        )
    return build_same_level_result(
        level_legs,
        profile_id=profile_id,
        config_hash=config_hash,
    )


# TODO(§5.7 后续): 中枢扩展 / 新生 / 消亡 / 高级别递归与中枢间关系。
