"""CSV I/O for raw bars, preserving source labels and volume units."""

# The execution contract requires ValueError for all validation failures.
# ruff: noqa: TRY004

import csv
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from types import MappingProxyType

from chanlab.algo.kline import Kline, KlineTSeries

from chanlab.algo.chan_table import COLUMNS

RAW_COLUMNS = (
    "timestamp", "symbol", "period", "source",
    "open", "high", "low", "close", "volume",
)


def _error(path: Path, row: int, field: str, message: str) -> ValueError:
    return ValueError(f"{path}: row {row}, field {field}: {message}")


def _read_context(path: Path) -> Mapping[str, str]:
    context = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            if next(reader, None) != ["key", "value"]:
                raise _error(path, 1, "header", "expected key,value")
            for pair in reader:
                row = reader.line_num
                if len(pair) != 2:
                    raise _error(path, row, "row", "expected two context fields")
                key, value = pair
                if not key.strip():
                    raise _error(path, row, "key", "must be nonblank")
                if key in context:
                    raise _error(path, row, "key", f"duplicate key {key!r}")
                context[key] = value
        except csv.Error as exc:
            raise _error(path, reader.line_num or 1, "row", str(exc)) from exc
    return MappingProxyType(context)


def read_kline_csv(
    path: str | Path, context_path: str | Path | None = None,
) -> tuple[KlineTSeries, Mapping[str, str]]:
    """Read exact raw-nine or master41 columns without time/unit conversion."""
    data_path = Path(path)
    bars = []
    with data_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = tuple(next(reader, ()))
            if header not in (RAW_COLUMNS, COLUMNS):
                raise _error(data_path, 1, "header", "expected exact raw-nine or master41 schema")
            for values in reader:
                row = reader.line_num
                if len(values) != len(header):
                    field = header[len(values)] if len(values) < len(header) else "row"
                    raise _error(data_path, row, field, f"expected {len(header)} fields, got {len(values)}")
                raw = dict(zip(header, values))
                try:
                    timestamp = datetime.fromisoformat(raw["timestamp"])
                except ValueError as exc:
                    raise _error(data_path, row, "timestamp", "invalid ISO datetime") from exc
                numeric = {}
                for field in ("open", "high", "low", "close", "volume"):
                    try:
                        numeric[field] = float(raw[field])
                    except ValueError as exc:
                        raise _error(data_path, row, field, "invalid number") from exc
                try:
                    bar = Kline(
                        symbol=raw["symbol"], period=raw["period"],
                        source=raw["source"], timestamp=timestamp, **numeric,
                    )
                except ValueError as exc:
                    field, _, message = str(exc).partition(":")
                    raise _error(data_path, row, field, message.strip()) from exc
                if bars:
                    for field in ("symbol", "period"):
                        if getattr(bar, field) != getattr(bars[0], field):
                            raise _error(data_path, row, field, "must match the first bar")
                    if bar.timestamp <= bars[-1].timestamp:
                        raise _error(data_path, row, "timestamp", "must strictly increase")
                bars.append(bar)
        except csv.Error as exc:
            raise _error(data_path, reader.line_num or 1, "row", str(exc)) from exc
    if not bars:
        raise _error(data_path, 2, "klines", "at least one Kline is required")
    series = KlineTSeries(bars)
    context = _read_context(Path(context_path)) if context_path is not None else MappingProxyType({})
    return series, context


def write_kline_csv(
    series: KlineTSeries,
    path: str | Path,
    context_path: str | Path | None = None,
    *,
    context: Mapping[str, str] | None = None,
) -> None:
    """Write raw-nine columns and optional unchanged string context."""
    if not isinstance(series, KlineTSeries):
        raise ValueError("series: a KlineTSeries is required")
    series.validate()
    if context is not None and not isinstance(context, Mapping):
        raise ValueError("context: a string mapping is required")
    saved_context = dict(context) if context is not None else {}
    for key, value in saved_context.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("context key: must be a nonblank string")
        if not isinstance(value, str):
            raise ValueError(f"context value for {key!r}: must be a string")
    if saved_context and context_path is None:
        raise ValueError("context_path: required for nonempty context")
    data_path = Path(path)
    sidecar = Path(context_path) if context_path is not None else None
    if sidecar is not None and data_path.resolve() == sidecar.resolve():
        raise ValueError("context_path: must differ from data path")
    with data_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(RAW_COLUMNS)
        for bar in series:
            writer.writerow((
                bar.timestamp.isoformat(), bar.symbol, bar.period, bar.source,
                bar.open, bar.high, bar.low, bar.close, bar.volume,
            ))
    if sidecar is not None:
        with sidecar.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("key", "value"))
            writer.writerows(saved_context.items())
