"""Memo022 fixed-snapshot centers with exact memo031 source identity."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from math import isfinite
from types import MappingProxyType
from typing import Any, overload

from chanlab.algo._zhongshu_input import project_xianduans
from chanlab.algo._zhongshu_scan import (
    Center,
    Decision,
    ScanResult,
    Segment,
    scan_zhongshus,
)
from chanlab.algo.merged_kline import MergedKline
from chanlab.algo.xianduan import XianduanSeries


@dataclass(frozen=True, slots=True)
class Zhongshu:
    """A structural center; integer member anchors and fractional geometry differ."""

    id: int
    level: str
    lower: float
    upper: float
    member_indices: tuple[int, ...]
    start_raw_index: int
    end_raw_index: int
    status: str
    confirmed_at: datetime | None
    geometry: Center

    def __post_init__(self) -> None:
        object.__setattr__(self, "member_indices", tuple(self.member_indices))
        if isinstance(self.geometry, Center):
            object.__setattr__(
                self,
                "geometry",
                replace(self.geometry, diagnostics=tuple(self.geometry.diagnostics)),
            )
        self.validate()

    def validate(self) -> None:
        """Validate local values; the owning series replays all source evidence."""
        for value in (self.id, self.start_raw_index, self.end_raw_index):
            MergedKline._validate_integer(value, "identifier/anchor")
        if not isinstance(self.level, str) or not self.level.strip():
            raise ValueError("nonempty structural level label required")
        if (
            any(
                isinstance(x, bool)
                or not isinstance(x, (int, float))
                or not isfinite(x)
                for x in (self.lower, self.upper)
            )
            or self.lower > self.upper
        ):
            raise ValueError("finite ordered bounds required")
        if self.start_raw_index >= self.end_raw_index:
            raise ValueError("increasing member anchors required")
        if (
            len(self.member_indices) < 3
            or any(type(x) is not int or x < 0 for x in self.member_indices)
            or self.member_indices
            != tuple(range(self.member_indices[0], self.member_indices[-1] + 1))
        ):
            raise ValueError("at least three contiguous source positions required")
        if not isinstance(self.geometry, Center):
            raise ValueError("Center geometry required")  # noqa: TRY004
        g = self.geometry
        if (
            self.status not in ("closed", "open")
            or (self.status == "closed") != g.closed
            or (self.lower, self.upper) != (g.low, g.high)
            or self.member_indices != tuple(range(g.start, g.observed_stop))
            or self.confirmed_at != g.confirmed_at
        ):
            raise ValueError("record/geometry mismatch")
        if (
            type(g.start) is not int
            or type(g.observed_stop) is not int
            or g.start < 0
            or g.observed_stop < g.start + 3
            or (
                g.closed
                and (
                    type(g.terminal) is not int
                    or g.terminal != g.observed_stop - 1
                    or type(g.confirmation) is not int
                    or g.confirmation != g.terminal + 1
                )
            )
            or (not g.closed and (g.confirmation is not None or g.right is not None))
        ):
            raise ValueError("invalid local source geometry")
        if (
            not isinstance(g.formation_at, datetime)
            or g.formation_at.utcoffset() != timedelta(0)
            or (
                g.confirmed_at is not None
                and (
                    not isinstance(g.confirmed_at, datetime)
                    or g.confirmed_at.utcoffset() != timedelta(0)
                    or g.confirmed_at < g.formation_at
                )
            )
        ):
            raise ValueError("invalid formation evidence time")
        expected_diagnostics = tuple(
            name
            for cross, name in (
                (g.left, "left_crossing_missing"),
                (g.right, "right_crossing_missing"),
            )
            if cross is None and (name.startswith("left") or g.closed)
        )
        if g.diagnostics != expected_diagnostics:
            raise ValueError("missing crossing diagnostics mismatch")
        for cross in (g.left, g.right):
            if cross is None:
                continue
            MergedKline._validate_integer(cross.segment_id, "crossing segment ID")
            if (
                any(
                    isinstance(v, bool)
                    or not isinstance(v, (int, float))
                    or not isfinite(v)
                    for v in (cross.fraction, cross.x, cross.price)
                )
                or not 0 <= cross.fraction <= 1
                or not self.start_raw_index <= cross.x <= self.end_raw_index
                or not isinstance(cross.time, datetime)
                or cross.time.utcoffset() != timedelta(0)
            ):
                raise ValueError("invalid crossing coordinates")
        if self.confirmed_at is not None and (
            not isinstance(self.confirmed_at, datetime)
            or self.confirmed_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("UTC confirmation required")
        if (self.status == "closed") != (self.confirmed_at is not None):
            raise ValueError("closed/open confirmation mismatch")


@dataclass(frozen=True, slots=True)
class ZhongshuSeries:
    """Complete immutable chronological result; missing geometry retains structure."""

    level: str
    source_series: XianduanSeries
    items: tuple[Zhongshu, ...]
    config: Mapping[str, Any]
    rule_tree_ref: str
    trace: tuple[Decision, ...]
    trace_by_point: tuple[tuple[int, ...], ...]
    unformed: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "config", self._config(self.config))
        object.__setattr__(self, "trace", tuple(self.trace))
        object.__setattr__(
            self, "trace_by_point", tuple(tuple(x) for x in self.trace_by_point)
        )
        object.__setattr__(self, "unformed", tuple(tuple(x) for x in self.unformed))
        self.validate()

    @staticmethod
    def _config(config: Mapping[str, Any] | None) -> Mapping[str, Any]:
        if config is not None and (not isinstance(config, Mapping) or config):
            raise ValueError(
                "memo022 has no configurable rule switches; config must be empty"
            )
        return MappingProxyType({})

    @staticmethod
    def _project(source: XianduanSeries) -> tuple[Segment, ...]:
        # Exact objects remain attached; this label identifies the local immutable projection.
        return project_xianduans(source, "memo022:exact-source")

    @staticmethod
    def _records(
        result: ScanResult, segments: tuple[Segment, ...], level: str
    ) -> tuple[Zhongshu, ...]:
        return tuple(
            Zhongshu(
                i,
                level,
                g.low,
                g.high,
                tuple(range(g.start, g.observed_stop)),
                int(segments[g.start].start_x),
                int(segments[g.observed_stop - 1].end_x),
                "closed" if g.closed else "open",
                g.confirmed_at,
                g,
            )
            for i, g in enumerate(result.centers)
        )

    @staticmethod
    def _mapping(result: ScanResult) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple(
                i
                for i, d in enumerate(result.decisions)
                if (d.stage == "seed" and d.index == g.start)
                or (d.stage == "ending" and g.start + 2 <= d.index < g.observed_stop)
            )
            for g in result.centers
        )

    @classmethod
    def derive_from(
        cls,
        source_series: XianduanSeries,
        level: str = "segment",
        config: Mapping[str, Any] | None = None,
        rule_tree_ref: str = "memo022:001,002:sequential-rectangle",
    ) -> ZhongshuSeries:
        """Derive current line-segment centers, without claiming recursive Chan levels."""
        cls._config(config)
        if not isinstance(source_series, XianduanSeries):
            raise ValueError("completed XianduanSeries required")  # noqa: TRY004
        source_series.validate()
        segments = cls._project(source_series)
        result = scan_zhongshus(segments)
        return cls(
            level,
            source_series,
            cls._records(result, segments, level),
            {},
            rule_tree_ref,
            result.decisions,
            cls._mapping(result),
            result.unformed,
        )

    def validate(self) -> None:
        """Replay the full sequential contract, detecting omitted/reordered results too."""
        if not isinstance(self.source_series, XianduanSeries):
            raise ValueError("XianduanSeries required")  # noqa: TRY004
        if not isinstance(self.level, str) or not self.level.strip():
            raise ValueError("nonempty structural level label required")
        if not isinstance(self.rule_tree_ref, str) or not self.rule_tree_ref.strip():
            raise ValueError("rule reference required")
        self.source_series.validate()
        if any(not isinstance(item, Zhongshu) for item in self.items):
            raise ValueError("Zhongshu records required")
        if any(
            not isinstance(d, Decision)
            or type(d.index) is not int
            or not isinstance(d.stage, str)
            or not isinstance(d.outcome, str)
            or any(
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not isfinite(v)
                for v in (d.low, d.high)
            )
            for d in self.trace
        ):
            raise ValueError("typed decision evidence required")
        if any(
            type(v) is not int or v < 0
            for row in self.trace_by_point + self.unformed
            for v in row
        ):
            raise ValueError("integer trace/range positions required")
        segments = self._project(self.source_series)
        result = scan_zhongshus(segments)
        expected = self._records(result, segments, self.level)
        if len({x.id for x in self.items}) != len(self.items):
            raise ValueError("duplicate ID")
        for item, reference in zip(self.items, expected):
            item.validate()
            # IDs are local identifiers, not positional indices.
            if asdict(item) | {"id": reference.id} != asdict(reference):
                raise ValueError("record/source mismatch")
        if (
            len(self.items) != len(expected)
            or self.trace != result.decisions
            or self.trace_by_point != self._mapping(result)
            or self.unformed != result.unformed
        ):
            raise ValueError("incomplete result/trace/unformed mismatch")

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[Zhongshu]:
        return iter(self.items)

    @overload
    def __getitem__(self, key: int) -> Zhongshu: ...
    @overload
    def __getitem__(self, key: slice) -> tuple[Zhongshu, ...]: ...
    def __getitem__(self, key: int | slice) -> Zhongshu | tuple[Zhongshu, ...]:
        return self.items[key]

    def get_by_id(self, feature_id: int) -> Zhongshu:
        """Look up a result-local integer ID, independently of position."""
        MergedKline._validate_integer(feature_id, "feature_id")
        for item in self:
            if item.id == feature_id:
                return item
        raise KeyError(feature_id)

    def unresolved_ranges(self) -> tuple[tuple[int, int], ...]:
        """Return unformed source positions; open structures are explicit items."""
        return self.unformed

    def explain(self, point_index: int) -> Mapping[str, Any]:
        """Expose exact source members, completion evidence and geometric diagnostics."""
        z = self[point_index]
        return MappingProxyType(
            {
                "rule": self.rule_tree_ref,
                "center": z,
                "source_ids": tuple(self.source_series[i].id for i in z.member_indices),
                "confirmation_index": z.geometry.confirmation,
                "decisions": tuple(
                    self.trace[i] for i in self.trace_by_point[point_index]
                ),
                "unformed": self.unformed,
                "bi_distance_mode": self.source_series.source_series.config[
                    "distance_mode"
                ],
                "xd_mode": self.source_series.config["xd_mode"],
            }
        )

    def to_dataframe(self) -> Any:
        """Detach compact records; persistence uses CSV plus versioned context."""
        import pandas as pd  # type: ignore[import-untyped]

        from chanlab.data.zhongshu_table import source_fingerprint

        frame = pd.DataFrame(
            [asdict(x) for x in self], columns=list(Zhongshu.__dataclass_fields__)
        )
        frame.attrs.update(
            level=self.level,
            rule_tree_ref=self.rule_tree_ref,
            config=dict(self.config),
            source_fingerprint=source_fingerprint(self.source_series),
        )
        return frame

    def to_chan_table(self, table: Any, series_key: str) -> Any:
        """Register exact source chain without replacing other feature results."""
        from chanlab.data.feature_table import register

        return register(self, table, series_key)

    @classmethod
    def from_chan_table(cls, table: Any, series_key: str) -> ZhongshuSeries:
        """Return the exact validated registered center series."""
        table.validate()
        result = table.feature_series[series_key]
        if not isinstance(result, cls):
            raise ValueError("ZhongshuSeries required")  # noqa: TRY004
        return result

    def plot(self, **options: Any) -> Any:
        """Plot all upstream geometry and honest closed/open/diagnostic overlays."""
        from chanlab.visualization.zhongshu_plot import plot

        return plot(self, **options)
