"""Memo029 fixed-snapshot dynamic programming, independent of API and charts."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from itertools import pairwise
from math import isfinite
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, overload

from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries

if TYPE_CHECKING:
    from chanlab.algo.chan_table import ChanTable


@dataclass(frozen=True, slots=True)
class Bi:
    """One unconfirmed stroke referencing positions in an exact fractal series."""

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
        """Validate local fields; the owning series checks interval definitions."""
        for key in ("id", "start_fenxing_index", "end_fenxing_index"):
            MergedKline._validate_integer(getattr(self, key), key)
        if self.start_fenxing_index >= self.end_fenxing_index:
            raise ValueError("endpoints must increase")
        for value in (self.start_price, self.end_price):
            try:
                valid = (
                    not isinstance(value, bool)
                    and isinstance(value, (int, float))
                    and isfinite(value)
                )
            except OverflowError:
                valid = False
            if not valid:
                raise ValueError("finite endpoint prices required")
        if (
            self.direction not in ("up", "down")
            or self.start_price == self.end_price
            or (self.end_price > self.start_price) != (self.direction == "up")
        ):
            raise ValueError("direction/price mismatch")
        if self.status != "unconfirmed" or self.confirmed_at is not None:
            raise ValueError("confirmation undefined: unconfirmed/None required")


@dataclass(frozen=True, slots=True)
class BiSeries:
    """One selected fixed-snapshot route; no rolling cache or permanent commit."""

    source_series: FenxingSeries
    items: tuple[Bi, ...]
    config: Mapping[str, Any]
    rule_tree_ref: str
    trace: tuple[Mapping[str, Any], ...]
    trace_by_point: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "config", self._normalize_config(self.config))
        object.__setattr__(
            self, "trace", tuple(MergedKlineSeries._freeze_data(v) for v in self.trace)
        )
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(v) for v in self.trace_by_point)
        )
        self.validate()

    @staticmethod
    def _resolve_distance(mode: Any) -> tuple[str, int]:
        if mode is None or mode == "strong":
            return "strong", 4
        if mode == "weak":
            return "weak", 3
        raise ValueError("distance_mode must be strong/weak")

    @classmethod
    def _normalize_config(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(config, Mapping) or set(config) - {"distance_mode"}:
            raise ValueError("only distance_mode is supported")
        mode, _ = cls._resolve_distance(config.get("distance_mode"))
        return MappingProxyType({"distance_mode": mode})

    @staticmethod
    def _validate_source(source: FenxingSeries) -> None:
        if not isinstance(source, FenxingSeries):
            raise ValueError("complete FenxingSeries required")  # noqa: TRY004
        source.validate()

    @staticmethod
    def _check_pair(
        source: FenxingSeries, p: int, f: int, gap: int
    ) -> tuple[bool, Mapping[str, Any]]:
        """Direct original-range scan, returning first violation or full evidence."""
        for value in (p, f):
            if type(value) is not int or not 0 <= value < len(source):
                raise ValueError("fractal position out of range")
        if p >= f:
            return False, {"reason": "order", "pair": (p, f)}
        x, y = source[p], source[f]
        i, j = x.source_start + 1, y.source_start + 1
        if x.kind == y.kind:
            return False, {"reason": "same_kind", "pair": (p, f)}
        if j - i < gap:
            return False, {
                "reason": "distance",
                "pair": (p, f),
                "actual": j - i,
                "required": gap,
            }
        t, b = (
            (source.source_series[i], source.source_series[j])
            if x.kind == "top"
            else (source.source_series[j], source.source_series[i])
        )
        if t.high <= b.high or b.low >= t.low:
            return False, {
                "reason": "endpoint_intervals",
                "pair": (p, f),
                "top": (t.low, t.high),
                "bottom": (b.low, b.high),
            }
        low, high = float("inf"), float("-inf")
        for k in range(i, j + 1):
            bar = source.source_series[k]
            if bar.high > t.high or bar.low < b.low:
                return False, {
                    "reason": "range",
                    "pair": (p, f),
                    "first_breach": k,
                    "bar": (bar.low, bar.high),
                    "bounds": (b.low, t.high),
                }
            low, high = min(low, bar.low), max(high, bar.high)
        return True, {
            "rule": "memo029.full_pair",
            "pair": (p, f),
            "centers": (i, j),
            "gap": gap,
            "intervals": ((t.low, t.high), (b.low, b.high)),
            "range": (low, high),
        }

    @staticmethod
    def _range_index(
        source: FenxingSeries,
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Sparse tables allow O(1) min/max queries after O(K log K) setup."""
        lows = [[p.low for p in source.source_series]]
        highs = [[p.high for p in source.source_series]]
        width = 2
        while width <= len(source.source_series):
            half = width // 2
            lows.append(
                [
                    min(lows[-1][i], lows[-1][i + half])
                    for i in range(len(source.source_series) - width + 1)
                ]
            )
            highs.append(
                [
                    max(highs[-1][i], highs[-1][i + half])
                    for i in range(len(source.source_series) - width + 1)
                ]
            )
            width *= 2
        return lows, highs

    @classmethod
    def _solve(
        cls, source: FenxingSeries, gap: int
    ) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int | None, ...]]:
        count = len(source)
        best = [-1] * count
        prev: list[int | None] = [None] * count
        centers = [p.source_start + 1 for p in source]
        kinds = [p.kind for p in source]
        lows, highs = cls._range_index(source)

        def good(p: int, f: int) -> bool:
            i, j = centers[p], centers[f]
            if kinds[p] == kinds[f] or j - i < gap:
                return False
            t, b = (i, j) if kinds[p] == "top" else (j, i)
            top, bottom = source.source_series[t], source.source_series[b]
            if top.high <= bottom.high or bottom.low >= top.low:
                return False
            level = (j - i + 1).bit_length() - 1
            right = j - (1 << level) + 1
            return (
                max(highs[level][i], highs[level][right]) <= top.high
                and min(lows[level][i], lows[level][right]) >= bottom.low
            )

        a = cls._find_start(count, good)
        if a is None:
            return (), tuple(best), tuple(prev)
        best[a] = 0
        for f in range(a + 1, count):
            for p in range(a, f):
                if best[p] >= 0 and best[p] + 1 > best[f] and good(p, f):
                    best[f], prev[f] = best[p] + 1, p
        end = next(f for f in range(count - 1, a, -1) if best[f] >= 1)
        return cls._recover(prev, a, end), tuple(best), tuple(prev)

    @staticmethod
    def _find_start(count: int, good: Callable[[int, int], bool]) -> int | None:
        return next(
            (
                a
                for a in range(count - 1)
                if any(good(a, f) for f in range(a + 1, count))
            ),
            None,
        )

    @staticmethod
    def _recover(prev: list[int | None], a: int, end: int) -> tuple[int, ...]:
        route = [end]
        while route[-1] != a:
            p = prev[route[-1]]
            if type(p) is not int or not a <= p < route[-1]:
                raise ValueError("invalid DP predecessor")
            route.append(p)
        return tuple(reversed(route))

    @classmethod
    def derive_from(
        cls, source_series: FenxingSeries, config: Mapping[str, Any], rule_tree_ref: str
    ) -> BiSeries:
        """Select earliest start, latest reachable end, maximum prefix stroke count."""
        cls._validate_source(source_series)
        effective = cls._normalize_config(config)
        _, gap = cls._resolve_distance(effective["distance_mode"])
        route, _, _ = cls._solve(source_series, gap)
        records = tuple(
            Bi(
                i,
                a,
                b,
                source_series[a].price,
                source_series[b].price,
                "up" if source_series[a].kind == "bottom" else "down",
            )
            for i, (a, b) in enumerate(pairwise(route))
        )
        trace = cls._validate_route(source_series, route, gap)
        return cls(
            source_series,
            records,
            effective,
            rule_tree_ref,
            trace,
            tuple((i,) for i in range(len(records))),
        )

    @classmethod
    def _validate_route(
        cls, source: FenxingSeries, route: tuple[int, ...], gap: int
    ) -> tuple[Mapping[str, Any], ...]:
        evidence = []
        for a, b in pairwise(route):
            ok, detail = cls._check_pair(source, a, b, gap)
            if not ok:
                raise ValueError(f"route definition failure: {detail}")
            evidence.append(detail)
        return tuple(evidence)

    def validate(self) -> None:
        """Recheck source, route definitions and exact selected-stroke evidence."""
        self._validate_source(self.source_series)
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        _, gap = self._resolve_distance(self.config["distance_mode"])
        ids: set[int] = set()
        route: list[int] = []
        for item in self.items:
            if not isinstance(item, Bi):
                raise ValueError("Bi record required")  # noqa: TRY004
            item.validate()
            if item.id in ids or item.end_fenxing_index >= len(self.source_series):
                raise ValueError("duplicate ID or out-of-bounds endpoint")
            ids.add(item.id)
            a, b = item.start_fenxing_index, item.end_fenxing_index
            if route and route[-1] != a:
                raise ValueError("route must share endpoints")
            if not route:
                route.append(a)
            route.append(b)
            if (item.start_price, item.end_price) != (
                self.source_series[a].price,
                self.source_series[b].price,
            ):
                raise ValueError("source price mismatch")
        expected = self._validate_route(self.source_series, tuple(route), gap)
        if not FenxingSeries._same_evidence(
            self.trace, MergedKlineSeries._freeze_data(expected)
        ) or self.trace_by_point != tuple((i,) for i in range(len(self.items))):
            raise ValueError("trace/evidence alignment mismatch")

    def _unresolved(self) -> tuple[tuple[int, int], ...]:
        count = len(self.source_series.source_series)
        if not self.items:
            return ((0, count),)
        start = self.source_series[self.items[0].start_fenxing_index].source_start + 1
        stop = self.source_series[self.items[-1].end_fenxing_index].source_start + 2
        return tuple((a, b) for a, b in ((0, start), (stop, count)) if a < b)

    def unresolved_ranges(self) -> tuple[tuple[int, int], ...]:
        """Return nonempty half-open merged ranges outside the selected route."""
        return self._unresolved()

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
        """Get a result-scoped ID; raise KeyError if absent."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for p in self:
            if p.id == feature_id:
                return p
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> Mapping[str, Any]:
        """Expose immutable rule/interval/anchor evidence for one selected stroke."""
        p = self[point_index]
        return MappingProxyType(
            {
                "item": p,
                "rule_tree_ref": self.rule_tree_ref,
                "distance_mode": self.config["distance_mode"],
                "evidence": self.trace[self.trace_by_point[point_index][0]],
                "raw_anchors": (
                    self.source_series[p.start_fenxing_index].anchor_raw_index,
                    self.source_series[p.end_fenxing_index].anchor_raw_index,
                ),
                "unresolved_merged": self._unresolved(),
            }
        )

    @classmethod
    def from_chan_table(cls, table: ChanTable, series_key: str) -> BiSeries:
        """Retrieve the exact registered snapshot."""
        table.validate()
        result = table.feature_series[series_key]
        if not isinstance(result, cls):
            raise ValueError("registered class mismatch")  # noqa: TRY004
        return result

    def to_chan_table(self, table: ChanTable, series_key: str) -> ChanTable:
        """Register selected records while preserving all upstream registrations."""
        from chanlab.data.feature_table import register

        return register(self, table, series_key)

    def to_dataframe(self) -> Any:
        """Return compact records and provenance; not a resume checkpoint."""
        from chanlab.data.bi_table import to_dataframe

        return to_dataframe(self)

    def plot(self, **options: Any) -> Any:
        """Plot raw/merged/all visible fractals and selected stroke IDs."""
        from chanlab.visualization.bi_plot import plot_bi_series

        return plot_bi_series(self, **options)
