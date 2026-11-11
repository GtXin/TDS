"""Immutable strokes and the current memo020 rolling scan.

Every route is a separate series. No canonical route or market confirmation is
inferred. Resource exhaustion raises rather than returning truncated success.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, cast, overload

if TYPE_CHECKING:
    from chanlab.algo.chan_table import ChanTable

from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries


@dataclass(frozen=True, slots=True)
class Bi:
    """One unconfirmed stroke with positions in its exact fractal source."""

    id: int
    start_fenxing_index: int
    end_fenxing_index: int
    start_price: float
    end_price: float
    direction: str
    status: str = "unconfirmed"
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Reject invalid IDs, prices, chronology and invented confirmation."""
        for key in ("id", "start_fenxing_index", "end_fenxing_index"):
            MergedKline._validate_integer(getattr(self, key), key)
        if self.start_fenxing_index >= self.end_fenxing_index:
            raise ValueError("endpoints must increase")
        for value in (self.start_price, self.end_price):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError("finite endpoint price required")
        if (
            self.direction not in ("up", "down")
            or (self.end_price > self.start_price) != (self.direction == "up")
            or self.end_price == self.start_price
        ):
            raise ValueError("price/direction mismatch")
        if self.status != "unconfirmed" or self.confirmed_at is not None:
            raise ValueError("confirmation undefined: unconfirmed/None required")


@dataclass(frozen=True, slots=True)
class BiSeries:
    """One route, preserving immutable source, rule context and decision evidence."""

    source_series: FenxingSeries
    items: tuple[Bi, ...]
    config: Mapping[str, Any]
    rule_tree_ref: str
    trace: tuple[Mapping[str, Any], ...]
    trace_by_point: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "config", MergedKlineSeries._freeze_data(self.config))
        object.__setattr__(
            self, "trace", tuple(MergedKlineSeries._freeze_data(x) for x in self.trace)
        )
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point)
        )
        self.validate()

    @staticmethod
    def _check_pair(source: FenxingSeries, a: int, b: int) -> bool:
        x, y = source[a], source[b]
        i, j = x.source_start + 1, y.source_start + 1
        if i >= j or j - i < 4 or x.kind == y.kind:
            return False
        top, bottom = (
            (source.source_series[i], source.source_series[j])
            if x.kind == "top"
            else (source.source_series[j], source.source_series[i])
        )
        return (
            top.high > bottom.high
            and bottom.low < top.low
            and all(
                bottom.low <= bar.low and bar.high <= top.high
                for bar in source.source_series[i : j + 1]
            )
        )

    @classmethod
    def scan(
        cls,
        source_series: FenxingSeries,
        rule_tree_ref: str,
        previous: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        """Run memo020 rolling scan; return committed R and separate open cache.

        Continuation accepts only a report emitted for an unchanged source prefix.
        EOF never commits the working stroke or implies market confirmation.
        """
        if not isinstance(source_series, FenxingSeries):
            raise ValueError("complete FenxingSeries required")  # noqa: TRY004
        source_series.validate()
        if not isinstance(rule_tree_ref, str) or not rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        committed: list[tuple[int, int]] = []
        cache: tuple[int, int] | None = None
        start: int | None = None
        cursor = 0
        trace: list[Mapping[str, Any]] = []
        if previous is not None:
            old = previous["series"]
            if not isinstance(old, cls) or old.rule_tree_ref != rule_tree_ref:
                raise ValueError("continuation class/rule mismatch")
            old_source = old.source_series
            old_raw = old_source.source_series.source_series
            new_raw = source_series.source_series.source_series
            if (
                source_series.items[: len(old_source)] != old_source.items
                or tuple(source_series.source_series)[: len(old_source.source_series)]
                != tuple(old_source.source_series)
                or new_raw.klines[: len(old_raw)] != old_raw.klines
                or dict(new_raw.context) != dict(old_raw.context)
                or dict(source_series.config) != dict(old_source.config)
                or dict(source_series.source_series.config)
                != dict(old_source.source_series.config)
                or source_series.rule_tree_ref != old_source.rule_tree_ref
                or source_series.source_series.rule_tree_ref
                != old_source.source_series.rule_tree_ref
            ):
                raise ValueError(
                    "continuation requires unchanged raw/merged/fractal prefix and context"
                )
            committed = [(p.start_fenxing_index, p.end_fenxing_index) for p in old]
            cache = previous["cache_pair"]
            start = previous["pending_start"]
            cursor = previous["next_position"]
            if cursor != len(old_source):
                raise ValueError("invalid continuation cursor")
            trace = list(old.trace)
            # Reject forged resume state by independently rescanning the old input.
            expected = cls.scan(old_source, rule_tree_ref)
            if (
                cache != expected["cache_pair"]
                or start != expected["pending_start"]
                or old.items != expected["series"].items
                or old.trace != expected["series"].trace
            ):
                raise ValueError("invalid continuation state")
        if start is None and cursor < len(source_series):
            start = cursor
            cursor += 1
        while cursor < len(source_series):
            f = cursor
            cursor += 1
            assert start is not None
            before = (tuple(committed), cache, start, f)
            if cache is None:
                if source_series[f].kind == source_series[start].kind:
                    more = cls._compare_same_kind(source_series, start, f) > 0
                    if more:
                        start = f
                    rule = "initial_replace" if more else "initial_keep"
                elif cls._check_first(source_series, start, f):
                    cache = (start, f)
                    start = f
                    rule = "first_cache"
                else:
                    rule = "reject_first"
            else:
                a, b = cache
                if source_series[f].kind == source_series[b].kind:
                    if cls._compare_same_kind(source_series, b, f) < 0:
                        rule = "weaker_end"
                    elif cls._check_extension(source_series, a, b, f):
                        cache = (a, f)
                        start = f
                        rule = "extend"
                    else:
                        rule = "reject_extension"
                elif cls._check_reverse(source_series, b, f):
                    committed.append((a, b))
                    cache = (b, f)
                    start = f
                    rule = "commit_reverse"
                else:
                    rule = "reject_reverse"
            cls._check_state(source_series, committed, cache, start, cursor)
            trace.append(
                {
                    "rule": rule,
                    "before": before,
                    "after": (tuple(committed), cache, start, cursor),
                }
            )
        records = tuple(
            cls._record(source_series, i, a, b) for i, (a, b) in enumerate(committed)
        )
        route = (
            () if not committed else (committed[0][0],) + tuple(b for _, b in committed)
        )
        series = cls(
            source_series,
            records,
            {"protocol": "rolling020", "route": route},
            rule_tree_ref,
            tuple(trace),
            tuple(tuple(range(len(trace))) for _ in records),
        )
        working = (
            None if cache is None else cls._record(source_series, len(records), *cache)
        )
        if cache is not None:
            cls._validate_output(source_series, committed + [cache])
        center_start = (
            0
            if cache is None
            else source_series[
                (committed[0][0] if committed else cache[0])
            ].source_start
            + 1
        )
        center_stop = 0 if cache is None else source_series[cache[1]].source_start + 2
        return MappingProxyType(
            {
                "series": series,
                "working": working,
                "cache_pair": cache,
                "pending_start": start,
                "next_position": cursor,
                "unresolved_merged": (
                    ((0, len(source_series.source_series)),)
                    if cache is None
                    else (
                        (0, center_start),
                        (center_stop, len(source_series.source_series)),
                    )
                ),
                "status": "no_first_stroke" if cache is None else "open_cache",
            }
        )

    @staticmethod
    def _record(source: FenxingSeries, i: int, a: int, b: int) -> Bi:
        return Bi(
            i,
            a,
            b,
            source[a].price,
            source[b].price,
            "up" if source[a].kind == "bottom" else "down",
        )

    @staticmethod
    def _compare_same_kind(source: FenxingSeries, a: int, b: int) -> int:
        delta = source[b].price - source[a].price
        if source[a].kind == "bottom":
            delta = -delta
        return (delta > 0) - (delta < 0)

    @staticmethod
    def _check_first(source: FenxingSeries, a: int, f: int) -> bool:
        i, j = source[a].source_start + 1, source[f].source_start + 1
        bars = source.source_series[i : j + 1]
        return j - i >= 4 and (
            source[f].price
            == (
                max(p.high for p in bars)
                if source[f].kind == "top"
                else min(p.low for p in bars)
            )
        )

    @staticmethod
    def _check_extension(source: FenxingSeries, a: int, b: int, f: int) -> bool:
        left, right = source[a], source[f]
        lower, upper = (
            (left.price, right.price)
            if right.kind == "top"
            else (right.price, left.price)
        )
        return all(
            lower <= bar.low and bar.high <= upper
            for bar in source.source_series[
                source[b].source_start + 2 : source[f].source_start + 2
            ]
        )

    @classmethod
    def _check_reverse(cls, source: FenxingSeries, b: int, f: int) -> bool:
        # The branch guarantees opposite types. Full definition pair check is
        # equivalent to distance plus both range extrema for strict fractals.
        return cls._check_pair(source, b, f)

    @staticmethod
    def _check_state(
        source: FenxingSeries,
        committed: list[tuple[int, int]],
        cache: tuple[int, int] | None,
        start: int | None,
        cursor: int,
    ) -> None:
        if not 0 <= cursor <= len(source) or (
            start is not None and not 0 <= start < cursor
        ):
            raise ValueError("invalid rolling cursor/start")
        if cache is None:
            if committed:
                raise ValueError("committed strokes require working cache")
        elif cache[1] != start or (committed and committed[-1][1] != cache[0]):
            raise ValueError("rolling shared endpoint mismatch")

    @classmethod
    def _validate_output(
        cls, source: FenxingSeries, pairs: list[tuple[int, int]]
    ) -> None:
        for i, (a, b) in enumerate(pairs):
            if not cls._check_pair(source, a, b) or (i and pairs[i - 1][1] != a):
                raise ValueError("independent output definition failure")

    @classmethod
    def derive_from(
        cls, source_series: FenxingSeries, config: Mapping[str, Any], rule_tree_ref: str
    ) -> BiSeries:
        """Return committed R only; use scan for the unfinished stroke/state."""
        if config:
            raise ValueError("rolling020 accepts no route-selection configuration")
        return cast(BiSeries, cls.scan(source_series, rule_tree_ref)["series"])

    def validate(self) -> None:
        """Check local definition, shared endpoints and trace associations."""
        if not isinstance(self.source_series, FenxingSeries):
            raise ValueError("FenxingSeries required")  # noqa: TRY004
        if (
            set(self.config) != {"protocol", "route"}
            or self.config["protocol"] != "rolling020"
        ):
            raise ValueError("rolling020 config required")
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        if len(self.trace_by_point) != len(self.items):
            raise ValueError("trace alignment")
        expected_route = (
            ()
            if not self.items
            else (self.items[0].start_fenxing_index,)
            + tuple(p.end_fenxing_index for p in self.items)
        )
        if tuple(self.config["route"]) != expected_route:
            raise ValueError("route metadata mismatch")
        ids: set[int] = set()
        previous: Bi | None = None
        for item, links in zip(self.items, self.trace_by_point):
            if not isinstance(item, Bi):
                raise ValueError("Bi required")  # noqa: TRY004
            item.validate()
            if item.id in ids or item.end_fenxing_index >= len(self.source_series):
                raise ValueError("duplicate ID or endpoint out of bounds")
            ids.add(item.id)
            a, b = item.start_fenxing_index, item.end_fenxing_index
            if not self._check_pair(self.source_series, a, b) or (
                item.start_price,
                item.end_price,
            ) != (self.source_series[a].price, self.source_series[b].price):
                raise ValueError("stroke definition/source mismatch")
            if previous and (
                previous.end_fenxing_index != a or previous.direction == item.direction
            ):
                raise ValueError("shared endpoints/alternation required")
            if links != tuple(range(len(self.trace))) or any(
                type(i) is not int or i < 0 or i >= len(self.trace) for i in links
            ):
                raise ValueError("trace indices")
            previous = item

    def __len__(self) -> int:
        return len(self.items)

    @overload
    def __getitem__(self, key: int) -> Bi: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[Bi, ...]: ...
    def __getitem__(self, key: int | slice) -> Bi | tuple[Bi, ...]:
        return self.items[key]

    def __iter__(self) -> Iterator[Bi]:
        return iter(self.items)

    def get_by_id(self, feature_id: int) -> Bi:
        """Look up a result-scoped ID."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for item in self.items:
            if item.id == feature_id:
                return item
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> Mapping[str, Any]:
        """Return immutable rule/source evidence, including provisional EOF."""
        item = self.items[point_index]
        a, b = (
            self.source_series[item.start_fenxing_index],
            self.source_series[item.end_fenxing_index],
        )
        return MappingProxyType(
            {
                "rule_tree_ref": self.rule_tree_ref,
                "item": item,
                "centers": (a.source_start + 1, b.source_start + 1),
                "raw_anchors": (a.anchor_raw_index, b.anchor_raw_index),
                "decisions": tuple(
                    self.trace[i] for i in self.trace_by_point[point_index]
                ),
                "working": False,
                "uncovered_merged": (
                    (
                        0,
                        self.source_series[
                            self.items[0].start_fenxing_index
                        ].source_start
                        + 1,
                    ),
                    (
                        self.source_series[
                            self.items[-1].end_fenxing_index
                        ].source_start
                        + 2,
                        len(self.source_series.source_series),
                    ),
                ),
            }
        )

    @classmethod
    def from_chan_table(cls, table: ChanTable, series_key: str) -> BiSeries:
        """Retrieve the exact selected route from its scoped table registration."""
        table.validate()
        result = table.feature_series[series_key]
        if not isinstance(result, cls):
            raise ValueError("registered class mismatch")  # noqa: TRY004
        return result

    def to_chan_table(self, table: ChanTable, series_key: str) -> ChanTable:
        """Register only this explicitly selected route, preserving other keys."""
        from chanlab.data.feature_table import register

        return register(self, table, series_key)

    def to_dataframe(self) -> Any:
        """Export compact records with exact route and provenance metadata."""
        from chanlab.data.bi_table import to_dataframe

        return to_dataframe(self)

    def plot(self, **options: Any) -> Any:
        """Draw this route over raw prices, without selecting alternatives."""
        from chanlab.visualization.bi_plot import plot_bi_series

        return plot_bi_series(self, **options)
