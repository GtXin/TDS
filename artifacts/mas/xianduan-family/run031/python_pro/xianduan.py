"""Memo030 XD030-E fixed-snapshot segments; interfaces from memo009002.j/k."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from itertools import pairwise
from types import MappingProxyType
from typing import Any, cast, overload

from chanlab.algo._xianduan_events import scanner
from chanlab.algo._xianduan_select import solve
from chanlab.algo.bi import Bi, BiSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries


def recognize(prices: list[float], mode: str = "weak") -> dict[str, Any]:
    """Rebuild events from prices and select the count/endpoint optimum."""
    from chanlab.algo._xianduan_features import _validate_prices

    prices = list(_validate_prices(prices))
    if mode not in ("weak", "strong"):
        raise ValueError("xd_mode must be weak/strong")
    events, shape = scanner(prices, mode)
    nodes = []
    for a in range(max(0, len(prices) - 3)):
        for b in range(a + 3, len(prices), 2):
            minimal: dict[tuple[str, int | None], dict[str, Any]] = {}
            for w in events(a, b):
                key = (
                    ("gap", w["reverse_end"])
                    if w["kind"] == "gap"
                    else ("direct", None)
                )
                old = minimal.get(key)
                if old is None or w["dep_endpoint"] < old["dep_endpoint"]:
                    minimal[key] = w
            for w in minimal.values():
                nodes.append({"root": True, "i": a, "j": b, "certificate": w})
    cast(Any, events).clear()
    pens = [
        {
            "start": {"price": a, "fx_position": k},
            "end": {"price": b, "fx_position": k + 1},
        }
        for k, (a, b) in enumerate(pairwise(prices))
    ]
    result = solve({"xd_mode": mode, "bi_mode": "source", "nodes": nodes}, pens)
    result["pending_candidates"] = (
        [
            (a, b)
            for a in range(max(0, len(prices) - 3))
            for b in range(a + 3, len(prices), 2)
            if shape(a, b)
        ]
        if not result["count"]
        else []
    )
    return result


@dataclass(frozen=True, slots=True)
class Xianduan:
    """One currently confirmed segment; confirmation is revisable on new snapshots."""

    id: int
    source_start: int
    source_stop: int
    start_price: float
    end_price: float
    direction: str
    status: str = "confirmed"
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Check range, numeric fields and UTC evidence label."""
        Bi(
            self.id,
            self.source_start,
            self.source_stop,
            self.start_price,
            self.end_price,
            self.direction,
        )
        if (
            self.source_stop - self.source_start < 3
            or (self.source_stop - self.source_start) % 2 != 1
        ):
            raise ValueError("odd member count >=3 required")
        if self.status != "confirmed":
            raise ValueError("only confirmed prefix records belong in items")
        if (
            not isinstance(self.confirmed_at, datetime)
            or self.confirmed_at.utcoffset() is None
            or self.confirmed_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("UTC evidence time required")


@dataclass(frozen=True, slots=True)
class XianduanSeries:
    """Immutable selected prefix and separately retained candidate evidence tail."""

    source_series: BiSeries
    items: tuple[Xianduan, ...]
    config: Mapping[str, Any]
    rule_tree_ref: str
    trace: tuple[Mapping[str, Any], ...]
    trace_by_point: tuple[tuple[int, ...], ...]
    tail: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "config", self._config(self.config))
        object.__setattr__(
            self, "trace", tuple(MergedKlineSeries._freeze_data(x) for x in self.trace)
        )
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point)
        )
        object.__setattr__(self, "tail", tuple(tuple(x) for x in self.tail))
        self.validate()

    @staticmethod
    def _config(config: Mapping[str, Any] | None) -> Mapping[str, Any]:
        if config is not None and not isinstance(config, Mapping):
            raise ValueError("config must be a mapping")
        c = dict(config or {})
        if set(c) - {"xd_mode"} or c.get("xd_mode", "weak") not in ("weak", "strong"):
            raise ValueError("only xd_mode=weak/strong supported")
        return MappingProxyType({"xd_mode": c.get("xd_mode", "weak")})

    @staticmethod
    def _prices(source: BiSeries) -> list[float]:
        return (
            [source[0].start_price] + [x.end_price for x in source]
            if len(source)
            else []
        )

    @staticmethod
    def _time(source: BiSeries, end: int) -> datetime:
        fx = source.source_series
        # A fractal is available only after its right merged neighbour is known.
        merged = fx.source_series
        right = merged[fx[source[end - 1].end_fenxing_index].source_stop - 1]
        return merged.source_series[right.source_stop - 1].timestamp

    @classmethod
    def derive_from(
        cls,
        source_series: BiSeries,
        config: Mapping[str, Any] | None = None,
        rule_tree_ref: str = "memo030:XD030-E:001,002",
    ) -> XianduanSeries:
        """Derive using exact upstream mode; no silent stroke recalculation."""
        if not isinstance(source_series, BiSeries):
            raise ValueError("BiSeries required")  # noqa: TRY004
        source_series.validate()
        c = cls._config(config)
        result = recognize(cls._prices(source_series), c["xd_mode"])
        full = result["confirmed"] + result["tail"]
        traces = []
        items = []
        for i, (a, b) in enumerate(result["confirmed"]):
            w = result["witnesses"][i]
            traces.append(
                {
                    "S": (a, b),
                    "T": full[i + 1],
                    "U": full[i + 2] if w["kind"] == "gap" else None,
                    "certificate": w,
                }
            )
            items.append(
                Xianduan(
                    i,
                    a,
                    b,
                    source_series[a].start_price,
                    source_series[b - 1].end_price,
                    source_series[a].direction,
                    "confirmed",
                    cls._time(source_series, w["dep_endpoint"]),
                )
            )
        return cls(
            source_series,
            tuple(items),
            c,
            rule_tree_ref,
            tuple(traces),
            tuple((i,) for i in range(len(items))),
            tuple(result["tail"]),
        )

    def validate(self) -> None:
        """Rebuild selected events from the original pens, checking actual S/T/U."""
        if not isinstance(self.source_series, BiSeries):
            raise ValueError("BiSeries required")  # noqa: TRY004
        self.source_series.validate()
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule reference required")
        prices = self._prices(self.source_series)
        events, shape = scanner(prices, self.config["xd_mode"])
        full = [(x.source_start, x.source_stop) for x in self] + list(self.tail)
        if len(self.trace) != len(self) or self.trace_by_point != tuple(
            (i,) for i in range(len(self))
        ):
            raise ValueError("trace alignment")
        if len({x.id for x in self}) != len(self):
            raise ValueError("duplicate ID")
        for i, (a, b) in enumerate(full):
            if not shape(a, b) or (i and full[i - 1][1] != a):
                raise ValueError("invalid shape/continuity")
        for i, x in enumerate(self):
            x.validate()
            a, b = full[i]
            if i + 1 >= len(full):
                raise ValueError("actual successor required")
            t = self.trace[i]
            w = t["certificate"]
            expected = {
                "S": (a, b),
                "T": full[i + 1],
                "U": full[i + 2] if w["kind"] == "gap" and i + 2 < len(full) else None,
                "certificate": w,
            }
            if not self.source_series.source_series._same_evidence(
                t, MergedKlineSeries._freeze_data(expected)
            ):
                raise ValueError("actual successor identity mismatch")
            if not any(
                self.source_series.source_series._same_evidence(
                    w, MergedKlineSeries._freeze_data(v)
                )
                for v in events(a, b)
            ):
                raise ValueError("event mismatch")
            c = full[i + 1][1]
            if w["kind"] == "gap":
                if (
                    i + 2 >= len(full)
                    or w["reverse_end"] != c
                    or w["dep_endpoint"] > full[i + 2][1]
                ):
                    raise ValueError("gap binding")
            elif w["dep_endpoint"] > c:
                raise ValueError("pair binding")
            if (x.start_price, x.end_price, x.direction, x.confirmed_at) != (
                self.source_series[a].start_price,
                self.source_series[b - 1].end_price,
                self.source_series[a].direction,
                self._time(self.source_series, w["dep_endpoint"]),
            ):
                raise ValueError("source fields mismatch")

        cast(Any, events).clear()

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[Xianduan]:
        return iter(self.items)

    @overload
    def __getitem__(self, key: int) -> Xianduan: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[Xianduan, ...]: ...
    def __getitem__(self, key: int | slice) -> Xianduan | tuple[Xianduan, ...]:
        return self.items[key]

    def get_by_id(self, feature_id: int) -> Xianduan:
        """Resolve a result-local integer ID."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for x in self:
            if x.id == feature_id:
                return x
        raise KeyError(feature_id)

    def pending_candidates(self) -> tuple[tuple[int, int], ...]:
        """Expose unconfirmed Shape candidates; none are counted as confirmed."""
        p = self._prices(self.source_series)
        _, shape = scanner(p, self.config["xd_mode"])
        starts = (
            range(max(0, len(p) - 3)) if not self.items else (self[-1].source_stop,)
        )
        return tuple(
            (a, b) for a in starts for b in range(a + 3, len(p), 2) if shape(a, b)
        )

    def unresolved_ranges(self) -> tuple[tuple[int, int], ...]:
        """Return nonempty half-open source-Bi ranges outside confirmed geometry."""
        n = len(self.source_series)
        if not self.items:
            return ((0, n),) if n else ()
        return tuple(
            (a, b)
            for a, b in ((0, self[0].source_start), (self[-1].source_stop, n))
            if a < b
        )

    def explain(self, point_index: int) -> Mapping[str, Any]:
        """Return immutable rule, upstream mode and actual destruction evidence."""
        return MappingProxyType(
            {
                "rule": self.rule_tree_ref,
                "segment": self.items[point_index],
                "evidence": self.trace[point_index],
                "bi_distance_mode": self.source_series.config["distance_mode"],
                "xd_mode": self.config["xd_mode"],
                "tail": self.tail,
                "unresolved_ranges": self.unresolved_ranges(),
            }
        )

    def to_dataframe(self) -> Any:
        """Return compact independent records with explicit rule/mode context."""
        import pandas as pd  # type: ignore[import-untyped]

        frame = pd.DataFrame(
            [asdict(x) for x in self], columns=list(Xianduan.__dataclass_fields__)
        )
        from chanlab.data.fenxing_table import fingerprint

        frame.attrs.update(
            source_fingerprint=fingerprint(
                {
                    "records": [asdict(x) for x in self.source_series],
                    "config": dict(self.source_series.config),
                    "rule": self.source_series.rule_tree_ref,
                }
            ),
            config=dict(self.config),
            rule_tree_ref=self.rule_tree_ref,
            bi_distance_mode=self.source_series.config["distance_mode"],
        )
        return frame

    def to_chan_table(self, table: Any, series_key: str) -> Any:
        """Register exact source chain and segment result."""
        from chanlab.data.feature_table import register

        return register(self, table, series_key)

    @classmethod
    def from_chan_table(cls, table: Any, series_key: str) -> XianduanSeries:
        """Read the exact registered result after validation."""
        table.validate()
        result = table.feature_series[series_key]
        if not isinstance(result, cls):
            raise ValueError("XianduanSeries required")  # noqa: TRY004
        return result

    def plot(self, **options: Any) -> Any:
        """Show source prices, every fractal/stroke and confirmed/candidate segments."""
        from chanlab.visualization.xianduan_plot import plot

        return plot(self, **options)
