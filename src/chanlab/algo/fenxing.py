"""Immutable geometric fractals from the complete memo019 window algorithm."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, overload

from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-untyped]

    from chanlab.algo.chan_table import ChanTable


@dataclass(frozen=True, slots=True)
class Fenxing:
    """One geometric top/bottom with a merged window and actual raw anchor."""

    id: int
    kind: str
    price: float
    anchor_raw_index: int
    source_start: int
    source_stop: int
    status: str = "unconfirmed"
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Validate local fields; confirmation is intentionally undefined."""
        for key in ("id", "anchor_raw_index", "source_start", "source_stop"):
            MergedKline._validate_integer(getattr(self, key), key)
        if self.kind not in ("top", "bottom"):
            raise ValueError("kind: expected top/bottom")
        try:
            valid = (
                not isinstance(self.price, bool)
                and isinstance(self.price, (int, float))
                and isfinite(self.price)
            )
        except OverflowError:
            valid = False
        if not valid:
            raise ValueError("price: expected finite number")
        if self.source_stop - self.source_start != 3:
            raise ValueError("window: require three merged positions")
        if self.status != "unconfirmed" or self.confirmed_at is not None:
            raise ValueError("confirmation undefined: require unconfirmed/None")


@dataclass(frozen=True, slots=True)
class FenxingSeries:
    """All geometric fractals, preserving exact source and every window decision."""

    source_series: MergedKlineSeries
    items: tuple[Fenxing, ...]
    config: Mapping[str, str]
    rule_tree_ref: str
    trace: tuple[Mapping[str, Any], ...]
    trace_by_point: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "config", self._normalize_config(self.config))
        object.__setattr__(
            self, "trace", tuple(MergedKlineSeries._freeze_data(x) for x in self.trace)
        )
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point)
        )
        self.validate()

    @staticmethod
    def _same_evidence(actual: Any, expected: Any) -> bool:
        """Compare frozen evidence without Python's bool/integer aliasing."""
        if isinstance(expected, Mapping):
            return (
                isinstance(actual, Mapping)
                and set(actual) == set(expected)
                and all(
                    FenxingSeries._same_evidence(actual[k], v)
                    for k, v in expected.items()
                )
            )
        if isinstance(expected, (list, tuple)):
            return (
                isinstance(actual, tuple)
                and len(actual) == len(expected)
                and all(
                    FenxingSeries._same_evidence(a, e) for a, e in zip(actual, expected)
                )
            )
        return type(actual) is type(expected) and bool(actual == expected)

    @staticmethod
    def _normalize_config(config: Mapping[str, str]) -> Mapping[str, str]:
        if not isinstance(config, Mapping) or set(config) - {"anchor_tie"}:
            raise ValueError("config: only anchor_tie supported")
        policy = config.get("anchor_tie", "FIRST")
        if policy not in ("FIRST", "LAST"):
            raise ValueError("anchor_tie: expected FIRST/LAST")
        return MappingProxyType({"anchor_tie": policy})

    @staticmethod
    def _direction_between(a: MergedKline, b: MergedKline) -> str:
        if b.high > a.high and b.low > a.low:
            return "up"
        if b.high < a.high and b.low < a.low:
            return "down"
        raise ValueError("adjacent prices: require strict common direction")

    @staticmethod
    def _classify_window(
        a: MergedKline, b: MergedKline, c: MergedKline
    ) -> tuple[str | None, float | None, str, str]:
        left = FenxingSeries._direction_between(a, b)
        right = FenxingSeries._direction_between(b, c)
        kind = ("top" if left == "up" else "bottom") if left != right else None
        price = (b.high if kind == "top" else b.low) if kind else None
        return kind, price, left, right

    @staticmethod
    def _resolve_anchor(
        raw: KlineTSeries, center: MergedKline, kind: str, price: float, policy: str
    ) -> tuple[int, int, int, int]:
        if (
            not isinstance(raw, KlineTSeries)
            or kind not in ("top", "bottom")
            or policy not in ("FIRST", "LAST")
        ):
            raise ValueError("anchor: invalid source/kind/policy")
        center.validate()
        if center.source_stop > len(raw) or price != (
            center.high if kind == "top" else center.low
        ):
            raise ValueError("anchor: invalid range/price")
        count = 0
        first = last = -1
        for j in range(center.source_start, center.source_stop):
            value = raw[j].high if kind == "top" else raw[j].low
            if value == price:
                if count == 0:
                    first = j
                last = j
                count += 1
        if count == 0:
            raise ValueError("anchor: price not present in original center members")
        return (first if policy == "FIRST" else last), count, first, last

    @staticmethod
    def _window_evidence(
        merged: MergedKlineSeries, i: int, policy: str
    ) -> Mapping[str, Any]:
        a, b, c = merged[i - 1], merged[i], merged[i + 1]
        kind, price, left, right = FenxingSeries._classify_window(a, b, c)
        anchor = None
        if kind is not None:
            assert price is not None
            selected, count, first, last = FenxingSeries._resolve_anchor(
                merged.source_series, b, kind, price, policy
            )
            anchor = {
                "selected": selected,
                "count": count,
                "first": first,
                "last": last,
                "policy": policy,
            }
        rule = {
            ("up", "down"): "2.5.a",
            ("down", "up"): "2.5.b",
            ("up", "up"): "2.5.c",
            ("down", "down"): "2.5.d",
        }[left, right]
        return {
            "rule": rule,
            "center": i,
            "window": (i - 1, i + 2),
            "raw_range": (a.source_start, c.source_stop),
            "bounds": ((a.low, a.high), (b.low, b.high), (c.low, c.high)),
            "left": left,
            "right": right,
            "kind": kind,
            "price": price,
            "anchor": anchor,
        }

    @staticmethod
    def _short_evidence(merged: MergedKlineSeries) -> Mapping[str, Any]:
        return {
            "rule": "2.2.a",
            "reason": "fewer than three merged units",
            "merged_count": len(merged),
            "raw_range": (0, len(merged.source_series)),
        }

    @classmethod
    def derive_from(
        cls,
        source_series: MergedKlineSeries,
        config: Mapping[str, str],
        rule_tree_ref: str,
    ) -> FenxingSeries:
        """Scan every complete window; never perform stroke endpoint selection."""
        if not isinstance(source_series, MergedKlineSeries):
            raise ValueError(  # noqa: TRY004
                "source_series: require complete MergedKlineSeries"
            )
        source_series.validate()
        effective = cls._normalize_config(config)
        if not isinstance(rule_tree_ref, str) or not rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        records: list[Fenxing] = []
        trace: list[Mapping[str, Any]] = []
        links: list[tuple[int, ...]] = []
        if len(source_series) < 3:
            trace.append(cls._short_evidence(source_series))
        for i in range(1, len(source_series) - 1):
            event = cls._window_evidence(source_series, i, effective["anchor_tie"])
            trace.append(event)
            if event["kind"] is not None:
                records.append(
                    Fenxing(
                        len(records),
                        event["kind"],
                        event["price"],
                        event["anchor"]["selected"],
                        i - 1,
                        i + 2,
                    )
                )
                links.append((len(trace) - 1,))
        return cls(
            source_series,
            tuple(records),
            effective,
            rule_tree_ref,
            tuple(trace),
            tuple(links),
        )

    def validate(self) -> None:
        """Recheck completeness, source geometry, anchors and evidence consistency."""
        if not isinstance(self.source_series, MergedKlineSeries):
            raise ValueError(  # noqa: TRY004
                "source_series: require complete MergedKlineSeries"
            )
        self.source_series.validate()
        self._validate_result(self.source_series, self)

    @staticmethod
    def _validate_result(merged: MergedKlineSeries, result: FenxingSeries) -> None:
        if result.source_series is not merged:
            raise ValueError("source identity mismatch")
        FenxingSeries._normalize_config(result.config)
        if (
            not isinstance(result.rule_tree_ref, str)
            or not result.rule_tree_ref.strip()
        ):
            raise ValueError("rule_tree_ref required")
        ids: set[int] = set()
        for point in result.items:
            if not isinstance(point, Fenxing):
                raise ValueError("items: expected Fenxing")  # noqa: TRY004
            point.validate()
            if point.id in ids:
                raise ValueError("duplicate ID")
            ids.add(point.id)
        expected_count = max(1, len(merged) - 2)
        if len(result.trace) != expected_count or len(result.trace_by_point) != len(
            result
        ):
            raise ValueError("trace length mismatch")
        if len(merged) < 3:
            if result.items or not FenxingSeries._same_evidence(
                result.trace[0], FenxingSeries._short_evidence(merged)
            ):
                raise ValueError("invalid short-input result")
            return
        cursor = 0
        for i in range(1, len(merged) - 1):
            event = FenxingSeries._window_evidence(
                merged, i, result.config["anchor_tie"]
            )
            if not FenxingSeries._same_evidence(result.trace[i - 1], event):
                raise ValueError(f"trace mismatch at center {i}")
            if event["kind"] is None:
                continue
            if cursor >= len(result):
                raise ValueError("missing fractal")
            point = result[cursor]
            expected = (
                event["kind"],
                event["price"],
                event["anchor"]["selected"],
                i - 1,
                i + 2,
            )
            if (
                point.kind,
                point.price,
                point.anchor_raw_index,
                point.source_start,
                point.source_stop,
            ) != expected:
                raise ValueError("fractal geometry/anchor/order mismatch")
            indices = result.trace_by_point[cursor]
            if len(indices) != 1 or type(indices[0]) is not int or indices != (i - 1,):
                raise ValueError("trace mapping mismatch")
            cursor += 1
        if cursor != len(result):
            raise ValueError("extra fractal")

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[Fenxing]:
        return iter(self.items)

    @overload
    def __getitem__(self, key: int) -> Fenxing: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[Fenxing, ...]: ...
    def __getitem__(self, key: int | slice) -> Fenxing | tuple[Fenxing, ...]:
        return self.items[key]

    def get_by_id(self, feature_id: int) -> Fenxing:
        """Resolve a result-scoped integer ID."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for point in self:
            if point.id == feature_id:
                return point
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> str:
        """Explain classification, original anchor and versioned source evidence."""
        p = self[point_index]
        e = self.trace[self.trace_by_point[point_index][0]]
        return f"FX{p.id} {p.kind} price={p.price}; merged[{p.source_start}:{p.source_stop}], raw anchor={p.anchor_raw_index}; {e['rule']} {e['left']}->{e['right']}, bounds={e['bounds']}, anchor={dict(e['anchor'])}; {p.status}; rules={self.rule_tree_ref}; upstream={self.source_series.rule_tree_ref}"

    @classmethod
    def from_chan_table(cls, table: ChanTable, series_key: str) -> FenxingSeries:
        """Return the exact registered result, validating its source chain."""
        table.validate()
        result = table.feature_series[series_key]
        if (
            not isinstance(result, cls)
            or result.source_series.source_series is not table.source_series
        ):
            raise ValueError("registered class/source mismatch")
        return result

    def to_chan_table(self, table: ChanTable, series_key: str) -> ChanTable:
        """Register this result and its upstream through the table adapter."""
        from chanlab.data.feature_table import register

        return register(self, table, series_key)

    def to_dataframe(self) -> Any:
        """Export a detached compact record table with versioned provenance."""
        from chanlab.data.fenxing_table import to_dataframe

        return to_dataframe(self)

    def plot(
        self,
        *,
        raw_start: int | None = None,
        raw_stop: int | None = None,
        volume: bool = True,
        title: str | None = None,
        show_gaps: bool = False,
        market: Literal["US", "China"] = "US",
    ) -> Figure:
        """Overlay all selected raw anchors on the existing merged/raw plot."""
        from chanlab.visualization.fenxing_plot import plot_fenxing_series

        return plot_fenxing_series(
            self,
            raw_start=raw_start,
            raw_stop=raw_stop,
            volume=volume,
            title=title,
            show_gaps=show_gaps,
            market=market,
        )
