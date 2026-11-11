"""Raw-time table with lossless registered merged-feature views."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chanlab.data.feature_table import Feature

import csv
import math
import sys
from collections.abc import Iterable, Iterator, Mapping
from datetime import datetime, timedelta
from pathlib import Path
from types import MappingProxyType

from chanlab.algo.kline import Kline, KlineTSeries

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


class ChanTable:
    """Immutable master table of raw OHLCV rows and provenance context."""

    def __init__(
        self,
        rows: Iterable[Mapping[str, str]],
        context: Mapping[str, str] | None = None,
        *,
        source_series: KlineTSeries | None = None,
        feature_series: Mapping[str, Feature] | None = None,
    ) -> None:
        self.rows = tuple(MappingProxyType(dict(row)) for row in rows)
        if any(tuple(row) != COLUMNS for row in self.rows):
            raise ValueError("schema mismatch")
        self.context = MappingProxyType(dict(context or {}))
        from chanlab.data.merged_kline_table import (
            FEATURE_CONTEXT,
            decode_features,
        )

        self.source_series = source_series or KlineTSeries(
            Kline(
                row["symbol"],
                row["period"],
                row["source"],
                datetime.fromisoformat(row["timestamp"]),
                *(float(row[k]) for k in ("open", "high", "low", "close", "volume")),
            )
            for row in self.rows
        )
        features = (
            dict(feature_series)
            if feature_series is not None
            else (
                decode_features(self.context[FEATURE_CONTEXT], self.source_series)
                if FEATURE_CONTEXT in self.context
                else {}
            )
        )
        from chanlab.algo.bi import BiSeries
        from chanlab.algo.fenxing import FenxingSeries
        from chanlab.algo.merged_kline import MergedKlineSeries
        from chanlab.data import bi_table, fenxing_table
        from chanlab.data.feature_table import project_one

        all_features: dict[str, Feature] = dict(features)
        if feature_series is None and fenxing_table.FEATURE_CONTEXT in self.context:
            all_features.update(
                fenxing_table.decode_features(
                    self.context[fenxing_table.FEATURE_CONTEXT],
                    {
                        k: v
                        for k, v in features.items()
                        if isinstance(v, MergedKlineSeries)
                    },
                )
            )
        if feature_series is None and bi_table.FEATURE_CONTEXT in self.context:
            all_features.update(
                bi_table.decode_features(
                    self.context[bi_table.FEATURE_CONTEXT], all_features
                )
            )
        self.feature_series = MappingProxyType(all_features)
        projected = {key: project_one(value) for key, value in all_features.items()}
        self.memberships = MappingProxyType(
            {
                key: value[
                    (
                        "bi_ids"
                        if isinstance(all_features[key], BiSeries)
                        else (
                            "fx_ids"
                            if isinstance(all_features[key], FenxingSeries)
                            else "mk_ids"
                        )
                    )
                ]
                for key, value in projected.items()
            }
        )
        self.start_ids = MappingProxyType(
            {
                key: value[
                    (
                        "bi_start_ids"
                        if isinstance(all_features[key], BiSeries)
                        else (
                            "fx_start_ids"
                            if isinstance(all_features[key], FenxingSeries)
                            else "mk_start_ids"
                        )
                    )
                ]
                for key, value in projected.items()
            }
        )
        self.end_ids = MappingProxyType(
            {
                key: value[
                    (
                        "bi_end_ids"
                        if isinstance(all_features[key], BiSeries)
                        else (
                            "fx_end_ids"
                            if isinstance(all_features[key], FenxingSeries)
                            else "mk_end_ids"
                        )
                    )
                ]
                for key, value in projected.items()
            }
        )
        self.anchor_ids: Mapping[str, tuple[tuple[int, ...], ...]] = MappingProxyType(
            {
                key: value["fx_anchor_ids"]
                for key, value in projected.items()
                if "fx_anchor_ids" in value
            }
        )
        self.validate()

    def validate(self) -> None:
        """Reject invalid raw rows and nonempty reserved feature columns."""
        if not self.rows:
            raise ValueError("empty table")
        from chanlab.algo.bi import BiSeries
        from chanlab.algo.fenxing import FenxingSeries
        from chanlab.algo.merged_kline import MergedKlineSeries
        from chanlab.data import bi_table, fenxing_table, merged_kline_table
        from chanlab.data.feature_table import contexts, visible_projection

        self.source_series.validate()
        if len(self.source_series) != len(self.rows):
            raise ValueError("raw source length mismatch")
        for key, feature in self.feature_series.items():
            if (
                not isinstance(key, str)
                or not key.strip()
                or not isinstance(feature, (MergedKlineSeries, FenxingSeries, BiSeries))
            ):
                raise ValueError("invalid feature key/class")
            feature.validate()
            raw = (
                feature.source_series.source_series.source_series
                if isinstance(feature, BiSeries)
                else (
                    feature.source_series.source_series
                    if isinstance(feature, FenxingSeries)
                    else feature.source_series
                )
            )
            if raw is not self.source_series:
                raise ValueError("feature source mismatch")
        expected_context = contexts(self.feature_series)
        for name in (
            merged_kline_table.FEATURE_CONTEXT,
            fenxing_table.FEATURE_CONTEXT,
            bi_table.FEATURE_CONTEXT,
        ):
            if (
                name in expected_context
                and self.context.get(name) != expected_context[name]
            ):
                raise ValueError("feature context mismatch")
            if (
                name not in expected_context
                and name in self.context
                and self.context[name] != "{}"
            ):
                raise ValueError("unexpected feature context")
        projected = visible_projection(self.feature_series)
        previous: datetime | None = None
        instrument: tuple[str, str] | None = None
        for i, row in enumerate(self.rows):
            if tuple(row) != COLUMNS or row["raw_index"] != str(i):
                raise ValueError("schema/raw index mismatch")
            if projected:
                import json

                for key, values in projected.items():
                    expected = (
                        ("NA" if values[i] is None else values[i])
                        if key in ("mk_direction", "fx_kind", "bi_direction")
                        else json.dumps(values[i], separators=(",", ":"))
                    )
                    if row[key] != expected:
                        raise ValueError(f"{key}: projection mismatch at row {i}")
            if any(row[key] != "NA" for key in COLUMNS[10:] if key not in projected):
                raise ValueError("reserved feature columns must be NA")
            if any(
                not row[key].strip() or row[key] == "NA"
                for key in ("symbol", "period", "source")
            ):
                raise ValueError("required provenance")
            identity = (row["symbol"], row["period"])
            if instrument is not None and instrument != identity:
                raise ValueError("mixed instrument/period")
            instrument = identity
            timestamp = datetime.fromisoformat(row["timestamp"])
            if timestamp.utcoffset() != timedelta(0):
                raise ValueError("UTC timestamp required")
            if previous is not None and timestamp <= previous:
                raise ValueError("unordered timestamps")
            previous = timestamp
            o, h, low, c, v = (
                float(row[key]) for key in ("open", "high", "low", "close", "volume")
            )
            bar = self.source_series[i]
            if (
                timestamp,
                row["symbol"],
                row["period"],
                row["source"],
                o,
                h,
                low,
                c,
                v,
            ) != (
                bar.timestamp,
                bar.symbol,
                bar.period,
                bar.source,
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume,
            ):
                raise ValueError("raw source values mismatch")
            if (
                not all(math.isfinite(x) for x in (o, h, low, c, v))
                or not low <= min(o, c) <= max(o, c) <= h
                or v < 0
            ):
                raise ValueError("invalid OHLCV")

    @classmethod
    def from_source_series(
        cls, source_series: KlineTSeries, context: Mapping[str, str] | None = None
    ) -> ChanTable:
        """Build a raw table retaining the exact existing KlineTSeries object."""
        source_series.validate()
        rows = []
        for i, bar in enumerate(source_series):
            row = dict.fromkeys(COLUMNS, "NA")
            row.update(
                raw_index=str(i),
                timestamp=bar.timestamp.isoformat(),
                symbol=bar.symbol,
                period=bar.period,
                source=bar.source,
            )
            for key in ("open", "high", "low", "close", "volume"):
                row[key] = str(getattr(bar, key))
            rows.append(row)
        return cls(rows, context, source_series=source_series)

    @classmethod
    def read_csv(
        cls, path: str | Path, context_path: str | Path | None = None
    ) -> ChanTable:
        """Read a master CSV and optional key/value context CSV."""
        context = {}
        if context_path is not None:
            previous_limit = csv.field_size_limit()
            try:
                csv.field_size_limit(sys.maxsize)
                with Path(context_path).open(newline="") as stream:
                    reader = csv.reader(stream)
                    if next(reader, None) != ["key", "value"]:
                        raise ValueError("context schema mismatch")
                    for pair in reader:
                        if len(pair) != 2 or not pair[0] or pair[0] in context:
                            raise ValueError("invalid context entry")
                        context[pair[0]] = pair[1]
            finally:
                csv.field_size_limit(previous_limit)
        with Path(path).open(newline="") as stream:
            reader2 = csv.DictReader(stream)
            if tuple(reader2.fieldnames or ()) != COLUMNS:
                raise ValueError("schema mismatch")
            return cls(reader2, context)

    def write_csv(
        self, path: str | Path, context_path: str | Path | None = None
    ) -> None:
        """Write validated rows and optional provenance context."""
        self.validate()
        if self.feature_series and context_path is None:
            raise ValueError("feature export requires context_path for lossless reload")
        if context_path is not None and (
            Path(path).resolve() == Path(context_path).resolve()
            or (
                Path(path).exists()
                and Path(context_path).exists()
                and Path(path).samefile(context_path)
            )
        ):
            raise ValueError("data and context output must differ")
        with Path(path).open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)
        if context_path is not None:
            with Path(context_path).open("w", newline="") as stream:
                writer2 = csv.writer(stream)
                writer2.writerow(("key", "value"))
                writer2.writerows(self.context.items())

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[Mapping[str, str]]:
        return iter(self.rows)

    def __getitem__(self, index: int) -> Mapping[str, str]:
        return self.rows[index]
