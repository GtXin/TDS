"""各层级中枢共用的 E+A/B/C 扫描与最左端相位确认。"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, cast


class ZhongShuScanLeg(Protocol):
    """笔、线段和低一级完成走势都能提供的最小中枢几何。"""

    @property
    def direction(self) -> object: ...

    @property
    def high(self) -> float: ...

    @property
    def low(self) -> float: ...


PriceDirection = Literal["up", "down"]


@dataclass(frozen=True, slots=True)
class ZhongShuScanCandidate:
    """与具体输出模型无关的中枢扫描结果。"""

    entry_index: int
    core_indexes: tuple[int, int, int]
    extended_indexes: tuple[int, ...]
    end_index: int
    zd: float
    zg: float
    gg: float
    dd: float
    close_index: int | None
    exit_direction: PriceDirection | None


def _direction_value(direction: object) -> PriceDirection:
    value = getattr(direction, "value", direction)
    if value not in {"up", "down"}:
        raise ValueError("zhongshu leg direction must be up or down")
    return cast(PriceDirection, value)


def _overlap(low_a: float, high_a: float, low_b: float, high_b: float) -> bool:
    return max(low_a, low_b) <= min(high_a, high_b)


def scan_zhongshu_candidate(
    legs: Sequence[ZhongShuScanLeg], entry_index: int
) -> ZhongShuScanCandidate | None:
    """从指定 E 向右扫描一个延伸口径候选，不读取候选以后的走势关系。"""
    if entry_index < 0 or entry_index + 3 >= len(legs):
        return None
    entry = legs[entry_index]
    a, b, c = legs[entry_index + 1 : entry_index + 4]
    if not (
        entry.direction != a.direction
        and a.direction != b.direction
        and b.direction != c.direction
    ):
        return None

    zd = max(a.low, b.low, c.low)
    zg = min(a.high, b.high, c.high)
    if zd > zg or not _overlap(entry.low, entry.high, zd, zg):
        return None

    extended_indexes: list[int] = []
    gg = max(a.high, c.high)
    dd = min(a.low, c.low)
    close_index: int | None = None
    exit_direction: PriceDirection | None = None
    z_index = entry_index + 5
    while z_index < len(legs):
        z_leg = legs[z_index]
        if not _overlap(z_leg.low, z_leg.high, zd, zg):
            close_index = z_index
            exit_direction = "up" if z_leg.low > zg else "down"
            break
        extended_indexes.extend((z_index - 1, z_index))
        gg = max(gg, z_leg.high)
        dd = min(dd, z_leg.low)
        z_index += 2

    end_index = extended_indexes[-1] if extended_indexes else entry_index + 3
    return ZhongShuScanCandidate(
        entry_index=entry_index,
        core_indexes=(entry_index + 1, entry_index + 2, entry_index + 3),
        extended_indexes=tuple(extended_indexes),
        end_index=end_index,
        zd=zd,
        zg=zg,
        gg=gg,
        dd=dd,
        close_index=close_index,
        exit_direction=exit_direction,
    )


def resolve_initial_zhongshu_phase(
    legs: Sequence[ZhongShuScanLeg], base: ZhongShuScanCandidate
) -> ZhongShuScanCandidate:
    """只解析连续 run 首中枢因缺少左侧方向而产生的相邻相位歧义。

    开放候选没有离开证据，继续保留最早合法相位。候选关闭后，若 E 与价格
    离开方向相反，且右移一项的候选也已按同方向关闭，则选择右移相位。后续
    中枢已有前一中枢离开方向约束，不得调用本函数事后改写历史。
    """
    if base.exit_direction is None:
        return base
    if _direction_value(legs[base.entry_index].direction) == base.exit_direction:
        return base

    shifted = scan_zhongshu_candidate(legs, base.entry_index + 1)
    if shifted is None or shifted.exit_direction is None:
        return base
    if (
        _direction_value(legs[shifted.entry_index].direction)
        == shifted.exit_direction
        == base.exit_direction
    ):
        return shifted
    return base
