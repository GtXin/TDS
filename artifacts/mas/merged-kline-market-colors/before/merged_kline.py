"""Two immutable domain classes implementing memo009 and memo015 inclusion rules."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from chanlab.algo.kline import KlineTSeries

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-untyped]

    from chanlab.algo.chan_table import ChanTable
Direction = Literal["up", "down"] | None
Policy = Literal["UP", "DOWN", "BOTH", "OUTER", "UNSET"]


@dataclass(frozen=True, slots=True)
class MergedKline:
    """One immutable interval and raw range; confirmation rules remain deferred."""

    id: int
    low: float
    high: float
    direction: Direction
    source_start: int
    source_stop: int
    status: str = "unconfirmed"
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """Check local fields without inferring confirmation or changing values."""
        for name in ("id", "source_start", "source_stop"):
            MergedKline._validate_integer(getattr(self, name), name)
        for value in (self.low, self.high):
            if isinstance(value, bool) or not isinstance(value, (float, int)):
                raise ValueError("bounds: expected finite numbers")  # noqa: TRY004
            try:
                if not isfinite(value):
                    raise ValueError("bounds: expected finite numbers")
            except OverflowError as exc:
                raise ValueError("bounds: outside float range") from exc
        if self.low > self.high or self.source_start >= self.source_stop:
            raise ValueError("bounds/source range: invalid order")
        if self.direction not in ("up", "down", None):
            raise ValueError("direction: invalid")
        if self.status != "unconfirmed" or self.confirmed_at is not None:
            raise ValueError("confirmation rule is undefined; require unconfirmed/None")

    @staticmethod
    def _validate_integer(value: int, name: str) -> None:
        if type(value) is not int or value < 0:
            raise ValueError(f"{name}: expected nonnegative integer")


@dataclass(frozen=True, slots=True)
class MergedKlineSeries:
    """Completed inclusion result with source references and scoped rule evidence."""

    source_series: KlineTSeries
    klines: tuple[MergedKline, ...]
    config: Mapping[str, str]
    rule_tree_ref: str
    trace: tuple[Mapping[str, Any], ...]
    trace_by_point: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "config", MergedKlineSeries._validate_config(self.config)
        )
        object.__setattr__(self, "klines", tuple(self.klines))
        object.__setattr__(
            self,
            "trace",
            tuple(MergedKlineSeries._freeze_data(step) for step in self.trace),
        )
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point)
        )
        self.validate()

    def validate(self) -> None:
        """Check raw identity, result invariants and complete trace mapping."""
        self.source_series.validate()
        MergedKlineSeries._validate_config(self.config)
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule_tree_ref: required")
        MergedKlineSeries._validate_result(self.source_series, self)
        if len(self.trace_by_point) != len(self):
            raise ValueError("trace mapping length mismatch")
        for indices in self.trace_by_point:
            if not indices:
                raise ValueError("trace mapping must explain each record")
            for i in indices:
                MergedKline._validate_integer(i, "trace index")
                if i >= len(self.trace):
                    raise ValueError("trace index: out of bounds")
        covered = {i for indices in self.trace_by_point for i in indices}
        if covered != set(range(len(self.trace))):
            raise ValueError("trace mapping must cover every executed decision")
        for step in self.trace:
            MergedKlineSeries._validate_step(step, self.source_series)

    def __len__(self) -> int:
        return len(self.klines)

    def __iter__(self) -> Iterator[MergedKline]:
        return iter(self.klines)

    @overload
    def __getitem__(self, key: int) -> MergedKline: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[MergedKline, ...]: ...
    def __getitem__(self, key: int | slice) -> MergedKline | tuple[MergedKline, ...]:
        return self.klines[key]

    def get_by_id(self, feature_id: int) -> MergedKline:
        """Resolve an integer feature ID; raise KeyError when it is absent."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for bar in self:
            if bar.id == feature_id:
                return bar
        raise KeyError(feature_id)

    def explain(self, point_index: int) -> str:
        """Explain a stored result position from its versioned calculation trace."""
        bar = self[point_index]
        steps = (self.trace[i] for i in self.trace_by_point[point_index])
        detail = "; ".join(
            f"{s['rule']} at raw[{s['raw_index']}]: "
            f"[{s['before']['low']},{s['before']['high']}] -> "
            f"[{s['after']['low']},{s['after']['high']}]"
            for s in steps
        )
        return (
            f"MK{bar.id} raw[{bar.source_start}:{bar.source_stop}] "
            f"{bar.direction}, {bar.status}; rules={self.rule_tree_ref}; {detail}"
        )

    @classmethod
    def from_chan_table(cls, table: ChanTable, series_key: str) -> MergedKlineSeries:
        """Return the exact registered result after source/class validation."""
        table.validate()
        result = table.feature_series[series_key]
        if (
            not isinstance(result, cls)
            or result.source_series is not table.source_series
        ):
            raise ValueError("registered class/source mismatch")
        return result

    def to_chan_table(self, table: ChanTable, series_key: str) -> ChanTable:
        """Return a new registered table view through the separate adapter."""
        from chanlab.data.merged_kline_table import register

        return register(self, table, series_key)

    def to_dataframe(self) -> Any:
        """Return a detached compact DataFrame through the optional adapter."""
        from chanlab.data.merged_kline_table import to_dataframe

        return to_dataframe(self)

    def plot(
        self,
        *,
        start: int | None = None,
        stop: int | None = None,
        raw_start: int | None = None,
        raw_stop: int | None = None,
        volume: bool = True,
        title: str | None = None,
        style: str = "overlay",
        show_gaps: bool = False,
    ) -> Figure:
        """Return an interactive gap-free overlay by default.

        start/stop select merged positions; raw_start/raw_stop instead select an
        original-bar viewport, retaining full-data merged bounds. style='panels'
        separates raw/merged prices; style='ranges' retains earlier range marks.
        show_gaps=True restores calendar spacing. The caller owns display/export.
        """
        from chanlab.visualization.merged_kline_plot import plot_merged_kline_series

        return plot_merged_kline_series(
            self,
            start=start,
            stop=stop,
            raw_start=raw_start,
            raw_stop=raw_stop,
            volume=volume,
            title=title,
            style=style,
            show_gaps=show_gaps,
        )

    @classmethod
    def derive_from(
        cls,
        source_series: KlineTSeries | ChanTable,
        config: Mapping[str, str],
        rule_tree_ref: str,
    ) -> MergedKlineSeries | Mapping[str, Any]:
        """Calculate015 with two domain classes and tagged read-only special outcomes."""
        from chanlab.algo.chan_table import ChanTable

        if isinstance(source_series, ChanTable):
            source_series.validate()
            source_series = source_series.source_series
        source_series.validate()
        config = MergedKlineSeries._validate_config(config)
        if not isinstance(rule_tree_ref, str) or not rule_tree_ref.strip():
            raise ValueError("rule_tree_ref: required")
        return MergedKlineSeries._advance(
            source_series,
            config,
            rule_tree_ref,
            MergedKlineSeries._work_from_raw(source_series, 0),
            1,
            (),
            (),
            (),
        )

    @staticmethod
    def _freeze_data(value: Any) -> Any:
        """Detach and recursively freeze plain configuration/evidence data."""
        if isinstance(value, Mapping):
            return MappingProxyType(
                {
                    key: MergedKlineSeries._freeze_data(item)
                    for key, item in value.items()
                }
            )
        if isinstance(value, (list, tuple)):
            return tuple(MergedKlineSeries._freeze_data(item) for item in value)
        return value

    @staticmethod
    def _validate_config(config: Mapping[str, str]) -> Mapping[str, str]:
        if not isinstance(config, Mapping) or set(config) != {"initialization"}:
            raise ValueError("config: require an initialization mapping")
        if config["initialization"] not in ("UP", "DOWN", "BOTH", "OUTER", "UNSET"):
            raise ValueError("initialization: unsupported policy")
        return MappingProxyType(dict(config))

    @staticmethod
    def _work(
        raw: KlineTSeries,
        low: float,
        high: float,
        direction: Direction,
        source_start: int,
        source_stop: int,
    ) -> Mapping[str, Any]:
        MergedKline(0, low, high, direction, source_start, source_stop)
        if source_stop > len(raw):
            raise ValueError("work source range: out of bounds")
        return MappingProxyType(
            {
                "raw": raw,
                "low": low,
                "high": high,
                "direction": direction,
                "source_start": source_start,
                "source_stop": source_stop,
            }
        )

    @staticmethod
    def _change(work: Mapping[str, Any], **changes: Any) -> Mapping[str, Any]:
        return MergedKlineSeries._work(**{**work, **changes})

    @staticmethod
    def _work_from_raw(
        raw: KlineTSeries, i: int, direction: Direction = None
    ) -> Mapping[str, Any]:
        """Create private interval data from one valid nonnegative raw position."""
        MergedKline._validate_integer(i, "raw index")
        if i >= len(raw):
            raise ValueError("raw index: out of bounds")
        return MergedKlineSeries._work(
            raw, raw[i].low, raw[i].high, direction, i, i + 1
        )

    @staticmethod
    def _has_inclusion(
        a: Mapping[str, Any] | MergedKline, b: Mapping[str, Any] | MergedKline
    ) -> bool:
        """Symmetric inclusive containment; record or private mapping inputs."""
        al, ah = (
            (a.low, a.high) if isinstance(a, MergedKline) else (a["low"], a["high"])
        )
        bl, bh = (
            (b.low, b.high) if isinstance(b, MergedKline) else (b["low"], b["high"])
        )
        return (ah >= bh and al <= bl) or (bh >= ah and bl <= al)

    @staticmethod
    def _direction_between(
        a: Mapping[str, Any] | MergedKline, b: Mapping[str, Any] | MergedKline
    ) -> Direction:
        """Strict direction between nonincluded chronological intervals."""
        if MergedKlineSeries._has_inclusion(a, b):
            raise ValueError("direction requires noninclusion")
        ah = a.high if isinstance(a, MergedKline) else a["high"]
        bh = b.high if isinstance(b, MergedKline) else b["high"]
        return "up" if bh > ah else "down"

    @staticmethod
    def _check_pair(current: Mapping[str, Any], candidate: Mapping[str, Any]) -> None:
        if (
            current["raw"] is not candidate["raw"]
            or current["source_stop"] != candidate["source_start"]
            or candidate["source_stop"] != candidate["source_start"] + 1
            or not MergedKlineSeries._has_inclusion(current, candidate)
        ):
            raise ValueError(
                "merge requires same source, contiguous single candidate and inclusion"
            )

    @staticmethod
    def _merge_included(
        current: Mapping[str, Any], candidate: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Return directed bounds without changing either input mapping."""
        MergedKlineSeries._check_pair(current, candidate)
        if current["direction"] is None:
            raise ValueError("merge requires known direction")
        operation = max if current["direction"] == "up" else min
        return MergedKlineSeries._change(
            current,
            low=operation(current["low"], candidate["low"]),
            high=operation(current["high"], candidate["high"]),
            source_stop=candidate["source_stop"],
        )

    @staticmethod
    def _merge_outer_boundary(
        current: Mapping[str, Any], candidate: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Use an explicitly selected OUTER envelope with unresolved direction."""
        MergedKlineSeries._check_pair(current, candidate)
        if current["direction"] is not None:
            raise ValueError("outer boundary requires unresolved direction")
        return MergedKlineSeries._change(
            current,
            low=min(current["low"], candidate["low"]),
            high=max(current["high"], candidate["high"]),
            source_stop=candidate["source_stop"],
        )

    @staticmethod
    def _validate_step(step: Mapping[str, Any], raw: KlineTSeries) -> None:
        if not isinstance(step, Mapping) or set(step) != {
            "rule",
            "raw_index",
            "before",
            "candidate",
            "after",
        }:
            raise ValueError(
                "trace: expected rule/index/before/candidate/after mapping"
            )
        MergedKline._validate_integer(step["raw_index"], "decision raw_index")
        if step["rule"] not in (
            "2.1.b",
            "2.4.a",
            "2.4.b",
            "2.6.UNSET",
            "2.6.c",
            "2.6.d",
            "2.6.a",
            "2.6.b",
            "2.5.a",
            "2.5.b",
            "2.2.a.EOF",
        ):
            raise ValueError("decision rule: unsupported")
        if step["raw_index"] > len(raw):
            raise ValueError("decision raw_index: out of bounds")
        for field in ("before", "after", "candidate"):
            work = step[field]
            if field == "candidate" and work is None:
                continue
            if not isinstance(work, Mapping) or set(work) != {
                "raw",
                "low",
                "high",
                "direction",
                "source_start",
                "source_stop",
            }:
                raise ValueError("trace work: invalid fields")
            if work["raw"] is not raw:
                raise ValueError("decision source mismatch")
            MergedKlineSeries._work(**work)

    @staticmethod
    def _validate_result(raw: KlineTSeries, result: MergedKlineSeries) -> None:
        """Reject broken source partitions, duplicate IDs and adjacent inclusion."""
        if result.source_series is not raw or not result.klines:
            raise ValueError("result must be nonempty and retain exact raw source")
        end = 0
        ids: set[int] = set()
        previous: MergedKline | None = None
        for j, bar in enumerate(result.klines):
            bar.validate()
            if bar.id in ids or bar.source_start != end or bar.source_stop > len(raw):
                raise ValueError(
                    f"result[{j}]: duplicate ID or invalid source coverage"
                )
            if previous is not None and MergedKlineSeries._has_inclusion(previous, bar):
                raise ValueError(
                    f"adjacent inclusion at {j-1},{j}: "
                    f"[{previous.source_start},{previous.source_stop}), "
                    f"[{bar.source_start},{bar.source_stop})"
                )
            ids.add(bar.id)
            end = bar.source_stop
            previous = bar
        if end != len(raw):
            raise ValueError("source coverage incomplete")

    @staticmethod
    def _advance(
        raw: KlineTSeries,
        config: Mapping[str, str],
        ref: str,
        current: Mapping[str, Any],
        i: int,
        saved: tuple[MergedKline, ...],
        trace: tuple[Mapping[str, Any], ...],
        mappings: tuple[tuple[int, ...], ...],
        active: tuple[int, ...] = (),
    ) -> MergedKlineSeries | Mapping[str, Any]:
        # Lists are private to each invocation; immutable prefixes can be shared.
        records = list(saved)
        events = list(trace)
        links = list(mappings)
        relevant = list(active)

        def record(
            rule: str,
            before: Mapping[str, Any],
            candidate: Mapping[str, Any] | None,
            after: Mapping[str, Any],
        ) -> None:
            relevant.append(len(events))
            events.append(
                MergedKlineSeries._freeze_data(
                    {
                        "rule": rule,
                        "raw_index": i,
                        "before": before,
                        "candidate": candidate,
                        "after": after,
                    }
                )
            )

        def save() -> None:
            records.append(
                MergedKline(
                    len(records) + 1,
                    current["low"],
                    current["high"],
                    current["direction"],
                    current["source_start"],
                    current["source_stop"],
                )
            )
            links.append(tuple(relevant))

        if not events:
            record("2.1.b", current, None, current)
        while i < len(raw):
            candidate = MergedKlineSeries._work_from_raw(raw, i)
            before = current
            if not MergedKlineSeries._has_inclusion(current, candidate):
                candidate = MergedKlineSeries._change(
                    candidate,
                    direction=MergedKlineSeries._direction_between(current, candidate),
                )
                rule = "2.4.a" if candidate["direction"] == "up" else "2.4.b"
                record(rule, current, candidate, current)
                save()
                # The transition is relevant to both the closed and new record.
                relevant = [len(events) - 1]
                current = candidate
                i += 1
                continue
            if current["direction"] is None:
                policy = config["initialization"]
                if policy == "UNSET":
                    record("2.6.UNSET", before, candidate, current)
                    return cast(
                        Mapping[str, Any],
                        MergedKlineSeries._freeze_data(
                            {
                                "kind": "pending",
                                "source_series": raw,
                                "config": config,
                                "rule_tree_ref": ref,
                                "saved": tuple(records),
                                "current": current,
                                "candidate": candidate,
                                "raw_index": i,
                                "trace": tuple(events),
                            }
                        ),
                    )
                if policy == "BOTH":
                    record("2.6.c", before, candidate, current)
                    paths = []
                    choices: tuple[tuple[Policy, Direction], ...] = (
                        ("UP", "up"),
                        ("DOWN", "down"),
                    )
                    for selected, direction in choices:
                        path = MergedKlineSeries._advance(
                            raw,
                            {"initialization": selected},
                            ref,
                            MergedKlineSeries._change(current, direction=direction),
                            i,
                            tuple(records),
                            tuple(events),
                            tuple(links),
                            tuple(relevant),
                        )
                        assert isinstance(path, MergedKlineSeries)
                        paths.append(path)
                    return cast(
                        Mapping[str, Any],
                        MergedKlineSeries._freeze_data(
                            {
                                "kind": "dual",
                                "main": paths[0],
                                "comparison": paths[1],
                                "requested_config": config,
                                "warning_evaluation": "not_evaluated",
                            }
                        ),
                    )
                if policy == "OUTER":
                    current = MergedKlineSeries._merge_outer_boundary(
                        current, candidate
                    )
                    record("2.6.d", before, candidate, current)
                    i += 1
                    continue
                current = MergedKlineSeries._change(
                    current, direction="up" if policy == "UP" else "down"
                )
                record(
                    "2.6.a" if policy == "UP" else "2.6.b", before, candidate, current
                )
            before = current
            current = MergedKlineSeries._merge_included(current, candidate)
            record(
                "2.5.a" if current["direction"] == "up" else "2.5.b",
                before,
                candidate,
                current,
            )
            i += 1
        record("2.2.a.EOF", current, None, current)
        save()
        return MergedKlineSeries(
            raw, tuple(records), config, ref, tuple(events), tuple(links)
        )
