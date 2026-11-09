"""Immutable supplied Chan features; rule-based detection remains deferred."""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, cast

from .chan_table import KlineTSeries, MergedKlineSeries


class Record:
    status: str
    confirmed_at: datetime | None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        d = vars(self)
        for k, v in d.items():
            if (
                (
                    k == "id"
                    or k.endswith("_index")
                    or k in ("source_start", "source_stop")
                )
                and v is not None
                and (type(v) is not int or v < 0)
            ):
                raise ValueError("nonnegative integer required: " + k)
            if k in (
                "price",
                "start_price",
                "end_price",
                "lower",
                "upper",
            ) and not math.isfinite(v):
                raise ValueError("finite price required")
            if k.endswith("_indices") and (
                not isinstance(v, tuple)
                or any(type(i) is not int or i < 0 for i in v)
                or tuple(sorted(set(v))) != v
            ):
                raise ValueError("ordered unique index tuple required")
        for a, b in (
            ("source_start", "source_stop"),
            ("start_fenxing_index", "end_fenxing_index"),
        ):
            if a in d and d[a] >= d[b]:
                raise ValueError("ordered nonempty source range required")
        if "start_raw_index" in d and d["start_raw_index"] > d["end_raw_index"]:
            raise ValueError("ordered raw extent required")
        if "lower" in d and d["lower"] > d["upper"]:
            raise ValueError("ordered center bounds required")
        for key, allowed in (
            ("direction", ("up", "down")),
            ("side", ("buy", "sell")),
            ("category", (1, 2, 3)),
        ):
            if key in d and (
                d[key] not in allowed or key == "category" and type(d[key]) is not int
            ):
                raise ValueError("invalid " + key)
        if isinstance(self, Fenxing) and self.kind not in ("top", "bottom"):
            raise ValueError("invalid fractal kind")
        if isinstance(self, Zoushi) and self.kind not in (
            "up",
            "down",
            "consolidation",
        ):
            raise ValueError("invalid movement kind")
        if (
            not self.status
            or ("level" in d and not d["level"])
            or ("kind" in d and not d["kind"])
        ):
            raise ValueError("nonempty labels required")
        if self.confirmed_at is not None and self.confirmed_at.utcoffset() != timedelta(
            0
        ):
            raise ValueError("UTC confirmation required")


@dataclass(frozen=True)
class Fenxing(Record):
    id: int
    kind: str
    price: float
    anchor_raw_index: int
    source_start: int
    source_stop: int
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class Bi(Record):
    id: int
    start_fenxing_index: int
    end_fenxing_index: int
    start_price: float
    end_price: float
    direction: str
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class Xianduan(Record):
    id: int
    source_start: int
    source_stop: int
    start_price: float
    end_price: float
    direction: str
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class Zhongshu(Record):
    id: int
    level: str
    lower: float
    upper: float
    member_indices: tuple[int, ...]
    start_raw_index: int
    end_raw_index: int
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class Zoushi(Record):
    id: int
    level: str
    kind: str
    source_start: int
    source_stop: int
    zhongshu_indices: tuple[int, ...]
    start_raw_index: int
    end_raw_index: int
    start_price: float
    end_price: float
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class Beichi(Record):
    id: int
    level: str
    kind: str
    zoushi_index: int
    entry_index: int
    exit_index: int
    anchor_raw_index: int
    status: str
    confirmed_at: datetime | None = None


@dataclass(frozen=True)
class BuySellPoint(Record):
    id: int
    level: str
    side: str
    category: int
    price: float
    anchor_raw_index: int
    zoushi_index: int
    center_index: int | None
    beichi_index: int | None
    status: str
    confirmed_at: datetime | None = None


def raw_source(series: Any) -> KlineTSeries:
    while not isinstance(series, KlineTSeries):
        series = series.source_series
    return series


@dataclass(frozen=True)
class FeatureSeries:
    source_series: Any
    items: tuple[Any, ...]
    rule_tree_ref: str
    trace_by_point: tuple[tuple[int, ...], ...]
    trace: tuple[object, ...] = ()
    config: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.source_series.validate()
        expected = {
            "FenxingSeries": MergedKlineSeries,
            "BiSeries": FenxingSeries,
            "XianduanSeries": BiSeries,
            "BeichiSeries": ZoushiSeries,
            "BuySellPointSeries": ZoushiSeries,
        }.get(type(self).__name__)
        if expected and not isinstance(self.source_series, expected):
            raise ValueError("invalid source type")
        if not all(
            isinstance(x, tuple)
            for x in (self.items, self.trace, self.trace_by_point, self.config)
        ):
            raise ValueError("immutable tuples required")
        if len({x.id for x in self.items}) != len(self.items) or len(
            self.trace_by_point
        ) != len(self.items):
            raise ValueError("duplicate IDs or trace alignment")
        raw = raw_source(self)
        previous = -1
        for item, indices in zip(self.items, self.trace_by_point):
            if type(item).__name__ + "Series" != type(self).__name__:
                raise ValueError("incorrect record type")
            item.validate()
            if not isinstance(indices, tuple) or any(
                type(i) is not int or not 0 <= i < len(self.trace) for i in indices
            ):
                raise ValueError("invalid trace index")
            if hasattr(item, "source_stop") and item.source_stop > len(
                self.source_series
            ):
                raise ValueError("source range out of bounds")
            position = getattr(
                item,
                "anchor_raw_index",
                getattr(
                    item,
                    "start_raw_index",
                    getattr(
                        item, "source_start", getattr(item, "start_fenxing_index", 0)
                    ),
                ),
            )
            if position < previous:
                raise ValueError("unordered records")
            previous = position
            for k in ("anchor_raw_index", "start_raw_index", "end_raw_index"):
                if hasattr(item, k) and getattr(item, k) >= len(raw):
                    raise ValueError("raw anchor out of bounds")
            if isinstance(item, Fenxing):
                windows = self.source_series.klines[
                    item.source_start : item.source_stop
                ]
                if not any(
                    x.source_start <= item.anchor_raw_index < x.source_stop
                    for x in windows
                ):
                    raise ValueError("anchor outside source window")
            if isinstance(item, Bi):
                if item.end_fenxing_index >= len(self.source_series):
                    raise ValueError("endpoint out of bounds")
                if (item.start_price, item.end_price) != (
                    self.source_series[item.start_fenxing_index].price,
                    self.source_series[item.end_fenxing_index].price,
                ):
                    raise ValueError("endpoint price mismatch")
            if isinstance(item, Xianduan) and (item.start_price, item.end_price) != (
                self.source_series[item.source_start].start_price,
                self.source_series[item.source_stop - 1].end_price,
            ):
                raise ValueError("endpoint price mismatch")
            if hasattr(self, "level") and item.level != self.level:
                raise ValueError("level mismatch")
            if isinstance(item, Zhongshu) and any(
                i >= len(self.source_series) for i in item.member_indices
            ):
                raise ValueError("member out of bounds")
            if isinstance(item, Zoushi) and any(
                i >= len(cast(ZhongshuSeries, cast(ZoushiSeries, self).zhongshu_series))
                for i in item.zhongshu_indices
            ):
                raise ValueError("center out of bounds")
            if isinstance(item, (Beichi, BuySellPoint)) and item.zoushi_index >= len(
                self.source_series
            ):
                raise ValueError("movement out of bounds")
            if isinstance(item, Beichi):
                center = self.source_series.zhongshu_series.get_by_id(
                    cast(BeichiSeries, self).zhongshu_id
                )
                ci = self.source_series.zhongshu_series.items.index(center)
                if ci not in self.source_series[
                    item.zoushi_index
                ].zhongshu_indices or not 0 <= item.entry_index < item.exit_index < len(
                    cast(ZoushiSeries, cast(BeichiSeries, self).comparison_series)
                ):
                    raise ValueError("invalid divergence relationships")
            if isinstance(item, BuySellPoint):
                if (
                    item.center_index is not None
                    and item.center_index
                    not in self.source_series[item.zoushi_index].zhongshu_indices
                ):
                    raise ValueError("invalid center relationship")
                if item.beichi_index is not None and (
                    cast(BuySellPointSeries, self).beichi_series is None
                    or item.beichi_index
                    >= len(
                        cast(BeichiSeries, cast(BuySellPointSeries, self).beichi_series)
                    )
                ):
                    raise ValueError("invalid divergence reference")
        for name in ("zhongshu_series", "comparison_series", "beichi_series"):
            other = getattr(self, name, None)
            if other is not None:
                other.validate()
                if raw_source(other) is not raw:
                    raise ValueError("different raw snapshots")
        if (
            isinstance(self, ZoushiSeries)
            and self.zhongshu_series is not None
            and self.zhongshu_series.level != self.level
        ):
            raise ValueError("center level mismatch")

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, key: int | slice) -> Any:
        return self.items[key]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.items)

    def get_by_id(self, feature_id: int) -> Any:
        for item in self.items:
            if item.id == feature_id:
                return item
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> tuple[object, ...]:
        return tuple(self.trace[i] for i in self.trace_by_point[point_index])


@dataclass(frozen=True)
class FenxingSeries(FeatureSeries):
    pass


@dataclass(frozen=True)
class BiSeries(FeatureSeries):
    pass


@dataclass(frozen=True)
class XianduanSeries(FeatureSeries):
    pass


@dataclass(frozen=True)
class ZhongshuSeries(FeatureSeries):
    level: str = ""


@dataclass(frozen=True)
class ZoushiSeries(FeatureSeries):
    level: str = ""
    zhongshu_series: ZhongshuSeries | None = None


@dataclass(frozen=True)
class BeichiSeries(FeatureSeries):
    level: str = ""
    zhongshu_id: int = 0
    comparison_series: ZoushiSeries | None = None


@dataclass(frozen=True)
class BuySellPointSeries(FeatureSeries):
    level: str = ""
    beichi_series: BeichiSeries | None = None


def raw_extent(series: FeatureSeries | MergedKlineSeries, item: Any) -> tuple[int, int]:
    """Resolve an inclusive raw extent through the retained source chain."""
    if isinstance(series, MergedKlineSeries):
        return item.source_start, item.source_stop - 1
    if isinstance(item, Fenxing):
        members = series.source_series.klines[item.source_start : item.source_stop]
        return members[0].source_start, members[-1].source_stop - 1
    if isinstance(item, Bi):
        return (
            series.source_series[item.start_fenxing_index].anchor_raw_index,
            series.source_series[item.end_fenxing_index].anchor_raw_index,
        )
    if isinstance(item, Xianduan):
        return (
            raw_extent(series.source_series, series.source_series[item.source_start])[
                0
            ],
            raw_extent(
                series.source_series, series.source_series[item.source_stop - 1]
            )[1],
        )
    if isinstance(item, (Zhongshu, Zoushi)):
        return item.start_raw_index, item.end_raw_index
    return item.anchor_raw_index, item.anchor_raw_index


def register_features(table: Any, key: str, series: FeatureSeries) -> Any:
    """Return a raw-axis view while retaining the exact supplied result object.

    Additional versions of the same feature class require a separate table view,
    because the fixed interchange schema has one group per class.
    """
    import json
    from types import MappingProxyType

    from .chan_table import ChanTable

    if not isinstance(key, str) or not key or key in table.feature_series:
        raise ValueError("nonempty unused series key required")
    if raw_source(series) is not table.source_series:
        raise ValueError("exact raw snapshot reference required")
    if any(type(other) is type(series) for other in table.feature_series.values()):
        raise ValueError("one result version per feature class per table")
    series.validate()
    groups = {
        FenxingSeries: ("fx", ("kind",)),
        BiSeries: ("bi", ("direction",)),
        XianduanSeries: ("xd", ("direction",)),
        ZhongshuSeries: ("zs", ("lower", "upper")),
        ZoushiSeries: ("zou", ("kind",)),
        BeichiSeries: ("bc", ("kind",)),
        BuySellPointSeries: ("bsp", ("side", "category")),
    }
    if type(series) not in groups:
        raise ValueError("unsupported feature series")
    prefix, annotations = groups[type(series)]
    rows = [dict(row) for row in table.rows]
    event = isinstance(series, (BeichiSeries, BuySellPointSeries))
    roles: tuple[str, ...] = ("ids",) if event else ("ids", "start_ids", "end_ids")
    if isinstance(series, FenxingSeries):
        roles += ("anchor_ids",)
    ids: dict[str, list[list[int]]] = {role: [[] for _ in rows] for role in roles}
    scalar_markers: dict[int, Any] = {}
    for row in rows:
        for annotation in annotations:
            row[f"{prefix}_{annotation}"] = "NA"
    for item in series:
        start, end = raw_extent(series, item)
        for position in range(start, end + 1):
            ids["ids"][position].append(item.id)
        if not event:
            ids["start_ids"][start].append(item.id)
            ids["end_ids"][end].append(item.id)
        marker = (
            item.anchor_raw_index
            if isinstance(item, (Fenxing, Beichi, BuySellPoint))
            else start
        )
        if isinstance(item, Fenxing):
            ids["anchor_ids"][marker].append(item.id)
        if marker in scalar_markers:
            raise ValueError("multiple annotation markers require an ID-keyed view")
        scalar_markers[marker] = item
    for role, positions in ids.items():
        for row, values in zip(rows, positions):
            row[f"{prefix}_{role}"] = json.dumps(values)
    for marker, item in scalar_markers.items():
        for annotation in annotations:
            rows[marker][f"{prefix}_{annotation}"] = str(getattr(item, annotation))
    result = ChanTable(rows, table.context)
    result.source_series = table.source_series
    result.feature_series = MappingProxyType({**table.feature_series, key: series})
    return result
