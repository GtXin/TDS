"""Raw-axis ChanTable interchange; detection and feature reconstruction are deferred."""

import csv
import json
import math
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import cast, overload

COLUMNS = (
    "raw_index",
    "timestamp",
    "symbol",
    "period",
    "source",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "mk_ids",
    "mk_direction",
    "mk_start_ids",
    "mk_end_ids",
    "fx_ids",
    "fx_kind",
    "fx_start_ids",
    "fx_end_ids",
    "fx_anchor_ids",
    "bi_ids",
    "bi_direction",
    "bi_start_ids",
    "bi_end_ids",
    "xd_ids",
    "xd_direction",
    "xd_start_ids",
    "xd_end_ids",
    "zs_ids",
    "zs_lower",
    "zs_upper",
    "zs_start_ids",
    "zs_end_ids",
    "zou_ids",
    "zou_kind",
    "zou_start_ids",
    "zou_end_ids",
    "bc_ids",
    "bc_kind",
    "bsp_ids",
    "bsp_side",
    "bsp_category",
)


@dataclass(frozen=True)
class Kline:
    symbol: str
    period: str
    source: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not all(
            isinstance(x, str) and x for x in (self.symbol, self.period, self.source)
        ):
            raise ValueError("required provenance")
        if self.timestamp.utcoffset() != timedelta(0):
            raise ValueError("UTC timestamp required")
        values = (self.open, self.high, self.low, self.close, self.volume)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("finite OHLCV required")
        if (
            not self.low
            <= min(self.open, self.close)
            <= max(self.open, self.close)
            <= self.high
            or self.volume < 0
        ):
            raise ValueError("invalid OHLCV")


@dataclass(frozen=True)
class KlineTSeries:
    klines: tuple[Kline, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "klines", tuple(self.klines))
        self.validate()

    def validate(self) -> None:
        if not self.klines:
            raise ValueError("empty series")
        for i, bar in enumerate(self.klines):
            bar.validate()
            if (bar.symbol, bar.period) != (
                self.klines[0].symbol,
                self.klines[0].period,
            ):
                raise ValueError("mixed instrument/period")
            if i and bar.timestamp <= self.klines[i - 1].timestamp:
                raise ValueError("unordered timestamps")

    def __len__(self) -> int:
        return len(self.klines)

    @overload
    def __getitem__(self, key: int) -> Kline: ...

    @overload
    def __getitem__(self, key: slice) -> tuple[Kline, ...]: ...

    def __getitem__(self, key: int | slice) -> Kline | tuple[Kline, ...]:
        return self.klines[key]

    def __iter__(self) -> Iterator[Kline]:
        return iter(self.klines)


class ChanTable:
    def __init__(
        self,
        rows: Iterable[Mapping[str, str]],
        context: Mapping[str, str] | None = None,
    ) -> None:
        self.rows = tuple(MappingProxyType(dict(r)) for r in rows)
        self.context = MappingProxyType(dict(context or {}))
        self.feature_series: Mapping[str, object] = MappingProxyType({})
        bars = []
        for i, r in enumerate(self.rows):
            if tuple(r) != COLUMNS or r["raw_index"] != str(i):
                raise ValueError("schema/raw index mismatch")
            for name in COLUMNS[10:]:
                value = r[name]
                if name.endswith("_ids") and value != "NA":
                    ids = json.loads(value)
                    if (
                        not isinstance(ids, list)
                        or any(type(v) is not int for v in ids)
                        or len(ids) != len(set(ids))
                    ):
                        raise ValueError("integer ID list required")
            bars.append(
                Kline(
                    r["symbol"],
                    r["period"],
                    r["source"],
                    datetime.fromisoformat(r["timestamp"]),
                    *(float(r[k]) for k in ("open", "high", "low", "close", "volume")),
                )
            )
        self.source_series = KlineTSeries(tuple(bars))
        self.memberships = MappingProxyType(
            {
                k: tuple(self._ids(r[k]) for r in self.rows)
                for k in COLUMNS
                if k.endswith("_ids")
                and not any(x in k for x in ("_start_", "_end_", "_anchor_"))
            }
        )
        for attr, suffix in (
            ("start_ids", "_start_ids"),
            ("end_ids", "_end_ids"),
            ("anchor_ids", "_anchor_ids"),
        ):
            setattr(
                self,
                attr,
                MappingProxyType(
                    {
                        k: tuple(self._ids(r[k]) for r in self.rows)
                        for k in COLUMNS
                        if k.endswith(suffix)
                    }
                ),
            )

    @staticmethod
    def _ids(value: str) -> tuple[int, ...] | None:
        return None if value == "NA" else tuple(cast(list[int], json.loads(value)))

    @classmethod
    def read_csv(
        cls, path: str | Path, context_path: str | Path | None = None
    ) -> "ChanTable":
        context = {}
        if context_path:
            with Path(context_path).open(newline="") as f:
                context = dict(list(csv.reader(f))[1:])
        with Path(path).open(newline="") as f:
            return cls(list(csv.DictReader(f)), context)

    def write_csv(
        self, path: str | Path, context_path: str | Path | None = None
    ) -> None:
        with Path(path).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(self.rows)
        if context_path:
            with Path(context_path).open("w", newline="") as f:
                context_writer = csv.writer(f)
                context_writer.writerow(("key", "value"))
                context_writer.writerows(self.context.items())


@dataclass(frozen=True)
class MergedKline:
    """An inclusion result referencing a half-open raw interval."""

    id: int
    low: float
    high: float
    direction: str | None
    source_start: int
    source_stop: int
    status: str
    confirmed_at: datetime | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if type(self.id) is not int:
            raise ValueError("integer feature ID required")
        if (
            not math.isfinite(self.low)
            or not math.isfinite(self.high)
            or self.low > self.high
        ):
            raise ValueError("invalid merged bounds")
        if self.direction not in (None, "up", "down"):
            raise ValueError("invalid merged direction")
        if not 0 <= self.source_start < self.source_stop:
            raise ValueError("invalid raw range")
        if not self.status or (
            self.confirmed_at is not None
            and self.confirmed_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("status and UTC confirmation required")


@dataclass(frozen=True)
class MergedKlineSeries:
    """Immutable manually supplied inclusion results; no detection rules implied."""

    source_series: KlineTSeries
    klines: tuple[MergedKline, ...]
    rule_tree_ref: str
    trace_by_point: tuple[tuple[int, ...], ...]
    trace: tuple[object, ...] = ()
    config: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.source_series.validate()
        if not isinstance(self.klines, tuple) or len(
            {x.id for x in self.klines}
        ) != len(self.klines):
            raise ValueError("immutable unique merged results required")
        if len(self.trace_by_point) != len(self.klines):
            raise ValueError("trace alignment mismatch")
        previous_stop = 0
        for item, indices in zip(self.klines, self.trace_by_point):
            item.validate()
            if item.source_start < previous_stop or item.source_stop > len(
                self.source_series
            ):
                raise ValueError("overlapping or out-of-bounds raw range")
            if any(type(i) is not int or not 0 <= i < len(self.trace) for i in indices):
                raise ValueError("invalid trace index")
            previous_stop = item.source_stop

    def __len__(self) -> int:
        return len(self.klines)

    def __getitem__(self, key: int | slice) -> MergedKline | tuple[MergedKline, ...]:
        return self.klines[key]

    def get_by_id(self, feature_id: int) -> MergedKline:
        for item in self.klines:
            if item.id == feature_id:
                return item
        raise KeyError(feature_id)


def register_merged(table: ChanTable, key: str, series: MergedKlineSeries) -> ChanTable:
    """Generate raw-axis markers from exact authoritative inclusion records.

    CSV preserves the derived view only; reconstructing authoritative records
    requires the caller's original feature series and its metadata.
    """
    if series.source_series is not table.source_series:
        raise ValueError("exact raw snapshot reference required")
    if key in table.feature_series:
        raise ValueError("series key already registered")
    if any(isinstance(s, MergedKlineSeries) for s in table.feature_series.values()):
        raise ValueError("one merged result version per table")
    series.validate()
    rows = [dict(r) for r in table.rows]
    for row in rows:
        for column in ("mk_ids", "mk_start_ids", "mk_end_ids"):
            row[column] = "[]"
        row["mk_direction"] = "NA"
    for item in series.klines:
        for i in range(item.source_start, item.source_stop):
            rows[i]["mk_ids"] = json.dumps([item.id])
        rows[item.source_start]["mk_start_ids"] = json.dumps([item.id])
        rows[item.source_stop - 1]["mk_end_ids"] = json.dumps([item.id])
        rows[item.source_start]["mk_direction"] = item.direction or "NA"
    result = ChanTable(rows, table.context)
    result.source_series = table.source_series
    result.feature_series = MappingProxyType({**table.feature_series, key: series})
    return result
