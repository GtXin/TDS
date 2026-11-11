"""Immutable strokes and complete memo020 temporal candidate enumeration.

Every route is a separate series. No canonical route or market confirmation is
inferred. Resource exhaustion raises rather than returning truncated success.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import Any, overload

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
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError("finite endpoint price required")
        if self.direction not in ("up", "down") or (self.end_price > self.start_price) != (self.direction == "up") or self.end_price == self.start_price:
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
        object.__setattr__(self, "trace", tuple(MergedKlineSeries._freeze_data(x) for x in self.trace))
        object.__setattr__(self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point))
        self.validate()

    @staticmethod
    def _check_pair(source: FenxingSeries, a: int, b: int) -> bool:
        x, y = source[a], source[b]
        i, j = x.source_start + 1, y.source_start + 1
        if i >= j or j - i < 4 or x.kind == y.kind:
            return False
        top, bottom = (source.source_series[i], source.source_series[j]) if x.kind == "top" else (source.source_series[j], source.source_series[i])
        return top.high > bottom.high and bottom.low < top.low and all(bottom.low <= bar.low and bar.high <= top.high for bar in source.source_series[i:j+1])

    @staticmethod
    def _options(config: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(config, Mapping) or set(config) - {"max_states", "route"}:
            raise ValueError("supported options: max_states, route")
        limit = config.get("max_states", 100000)
        if type(limit) is not int or limit < 1:
            raise ValueError("max_states must be positive integer")
        return {"max_states": limit}

    @classmethod
    def derive_candidates(cls, source_series: FenxingSeries, config: Mapping[str, Any], rule_tree_ref: str) -> Mapping[str, Any]:
        """Return every route grouped by identical boundary positions.

        Raises RuntimeError on state budget exhaustion; never silently truncates.
        Reports retain blocked histories and EOF-without-endpoint diagnostics.
        """
        if not isinstance(source_series, FenxingSeries):
            raise ValueError("complete FenxingSeries required")
        source_series.validate()
        if not isinstance(rule_tree_ref, str) or not rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        options = cls._options(config)
        source = source_series
        # prefix ends at A; cached alternatives are post-choice states.
        pending = [((a,), a, None, a + 1, ()) for a in reversed(range(len(source)))]
        routes: dict[tuple[int, ...], tuple[Mapping[str, Any], ...]] = {}
        blocked: list[Mapping[str, Any]] = []
        unresolved: list[tuple[int, ...]] = []
        states = 0
        while pending:
            prefix, a, b, cursor, evidence = pending.pop()
            while cursor < len(source):
                states += 1
                if states > options["max_states"]:
                    raise RuntimeError("candidate state budget exhausted; no complete result")
                f = cursor
                cursor += 1
                before = (prefix, a, b, f)
                action = "reject_initial"
                if b is None:
                    if cls._check_pair(source, a, f):
                        pending.append((prefix, a, None, cursor, evidence + ({"rule": "skip_initial", "state": before},)))
                        b = f
                        action = "accept_initial"
                elif source[f].kind == source[b].kind:
                    value, old = source[f].price, source[b].price
                    better = value > old if source[b].kind == "top" else value < old
                    if better:
                        if cls._check_pair(source, a, f):
                            b = f
                            action = "extend"
                        else:
                            blocked.append({"prefix": prefix + (b,), "failed": f, "evidence": evidence, "state": before})
                            break
                    elif value == old and cls._check_pair(source, a, f):
                        pending.append((prefix, a, f, cursor, evidence + ({"rule": "replace_equal", "state": before},)))
                        action = "keep_equal"
                    else:
                        action = "keep_end"
                elif cls._check_pair(source, b, f):
                    prefix = prefix + (b,)
                    a, b = b, f
                    action = "first_reverse"
                else:
                    action = "reject_reverse"
                evidence += ({"rule": action, "state": before},)
            else:
                if b is not None:
                    routes.setdefault(prefix + (b,), evidence + ({"rule": "EOF_provisional", "working": (a, b)},))
                else:
                    unresolved.append(prefix)
        groups: dict[tuple[int, int], list[BiSeries]] = {}
        for route, trace in sorted(routes.items()):
            records = tuple(Bi(i, x, y, source[x].price, source[y].price, "up" if source[x].kind == "bottom" else "down") for i, (x, y) in enumerate(zip(route, route[1:])))
            series = cls(source, records, {**options, "route": route}, rule_tree_ref, trace, tuple(tuple(range(len(trace))) for _ in records))
            groups.setdefault((route[0], route[-1]), []).append(series)
        return MappingProxyType({"groups": MappingProxyType({k: tuple(v) for k, v in groups.items()}), "blocked": MergedKlineSeries._freeze_data(blocked), "unresolved": tuple(unresolved), "states": states, "source_series": source, "rule_tree_ref": rule_tree_ref})

    @classmethod
    def derive_from(cls, source_series: FenxingSeries, config: Mapping[str, Any], rule_tree_ref: str) -> BiSeries:
        """Select an explicitly requested route, or the sole available route."""
        report = cls.derive_candidates(source_series, config, rule_tree_ref)
        routes = tuple(s for group in report["groups"].values() for s in group)
        selected = config.get("route")
        if selected is not None:
            for series in routes:
                if tuple(selected) == series.config["route"]:
                    return series
            raise ValueError("requested route not in viable candidates")
        if len(routes) != 1:
            raise ValueError("explicit route required: use derive_candidates for all results")
        return routes[0]

    def validate(self) -> None:
        """Check local definition, shared endpoints and trace associations."""
        if not isinstance(self.source_series, FenxingSeries):
            raise ValueError("FenxingSeries required")
        self._options(self.config)
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule_tree_ref required")
        if len(self.trace_by_point) != len(self.items):
            raise ValueError("trace alignment")
        ids: set[int] = set()
        previous: Bi | None = None
        for item, links in zip(self.items, self.trace_by_point):
            if not isinstance(item, Bi):
                raise ValueError("Bi required")
            item.validate()
            if item.id in ids or item.end_fenxing_index >= len(self.source_series):
                raise ValueError("duplicate ID or endpoint out of bounds")
            ids.add(item.id)
            a, b = item.start_fenxing_index, item.end_fenxing_index
            if not self._check_pair(self.source_series, a, b) or (item.start_price, item.end_price) != (self.source_series[a].price, self.source_series[b].price):
                raise ValueError("stroke definition/source mismatch")
            if previous and (previous.end_fenxing_index != a or previous.direction == item.direction):
                raise ValueError("shared endpoints/alternation required")
            if not links or any(type(i) is not int or i < 0 or i >= len(self.trace) for i in links):
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
        a, b = self.source_series[item.start_fenxing_index], self.source_series[item.end_fenxing_index]
        return MappingProxyType({"rule_tree_ref": self.rule_tree_ref, "item": item, "centers": (a.source_start + 1, b.source_start + 1), "raw_anchors": (a.anchor_raw_index, b.anchor_raw_index), "decisions": tuple(self.trace[i] for i in self.trace_by_point[point_index]), "working": item is self.items[-1], "uncovered_merged": ((0, self.source_series[self.items[0].start_fenxing_index].source_start + 1), (self.source_series[self.items[-1].end_fenxing_index].source_start + 2, len(self.source_series.source_series)))})
