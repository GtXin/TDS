"""Raw Kline CSV adapters without timestamp shifts or volume conversions."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Final

from chanlab.algo.chan_table import COLUMNS
from chanlab.algo.kline import Kline, KlineTSeries

RAW_COLUMNS: Final[tuple[str, ...]] = (
    "timestamp",
    "symbol",
    "period",
    "source",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def _error(path: Path, row: int, field: str, message: str) -> ValueError:
    """Describe a validation failure using its file, row and field."""
    return ValueError(f"{path}: row {row}, field {field}: {message}")


def _read_context(path: Path) -> Mapping[str, str]:
    """Read exact key/value columns into an immutable string mapping."""
    context: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            if next(reader, None) != ["key", "value"]:
                raise _error(path, 1, "header", "expected key,value")
            for pair in reader:
                row = reader.line_num
                if len(pair) != 2:
                    field = ("key", "value")[len(pair)] if len(pair) < 2 else "row"
                    raise _error(path, row, field, "expected two context fields")
                key, value = pair
                if not key.strip():
                    raise _error(path, row, "key", "must be nonblank")
                if key in context:
                    raise _error(path, row, "key", f"duplicate key {key!r}")
                context[key] = value
        except csv.Error as exc:
            raise _error(path, reader.line_num or 1, "row", str(exc)) from exc
    return MappingProxyType(context)


def _parse_bar(raw: Mapping[str, str], path: Path, row: int) -> Kline:
    """Parse raw values and add file/row context to domain validation errors."""
    try:
        timestamp = datetime.fromisoformat(raw["timestamp"])
    except ValueError as exc:
        raise _error(path, row, "timestamp", "invalid ISO datetime") from exc
    numeric: dict[str, float] = {}
    for field in ("open", "high", "low", "close", "volume"):
        try:
            numeric[field] = float(raw[field])
        except ValueError as exc:
            raise _error(path, row, field, "invalid number") from exc
    try:
        return Kline(
            symbol=raw["symbol"],
            period=raw["period"],
            source=raw["source"],
            timestamp=timestamp,
            open=numeric["open"],
            high=numeric["high"],
            low=numeric["low"],
            close=numeric["close"],
            volume=numeric["volume"],
        )
    except ValueError as exc:
        field, _, message = str(exc).partition(":")
        raise _error(path, row, field, message.strip()) from exc


def read_kline_csv(
    path: str | Path,
    context_path: str | Path | None = None,
) -> tuple[KlineTSeries, Mapping[str, str]]:
    """Read raw-nine or master41 CSV and optional string context.

    Args:
        path: Input CSV with one exact supported header, including column order.
        context_path: Optional sidecar CSV with exact key,value columns.

    Returns:
        A validated series and an immutable mapping of unchanged context strings.

    Raises:
        ValueError: Schema, row, bar, chronology, or context is invalid. Validation
            messages identify the file, row and field.
        OSError: An input file cannot be read.
    """
    data_path = Path(path)
    sidecar = Path(context_path) if context_path is not None else None
    if sidecar is not None:
        same_target = data_path.resolve() == sidecar.resolve() or (
            data_path.exists() and sidecar.exists() and data_path.samefile(sidecar)
        )
        if same_target:
            raise _error(data_path, 1, "context_path", "must differ from data path")
    bars: list[Kline] = []
    with data_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = tuple(next(reader, ()))
            if header not in (RAW_COLUMNS, COLUMNS):
                raise _error(
                    data_path, 1, "header", "expected exact raw-nine or master41 schema"
                )
            for values in reader:
                row = reader.line_num
                if len(values) != len(header):
                    field = header[len(values)] if len(values) < len(header) else "row"
                    raise _error(
                        data_path,
                        row,
                        field,
                        f"expected {len(header)} fields, got {len(values)}",
                    )
                bar = _parse_bar(dict(zip(header, values, strict=True)), data_path, row)
                if bars:
                    if bar.symbol != bars[0].symbol:
                        raise _error(
                            data_path, row, "symbol", "must match the first bar"
                        )
                    if bar.period != bars[0].period:
                        raise _error(
                            data_path, row, "period", "must match the first bar"
                        )
                    if bar.timestamp <= bars[-1].timestamp:
                        raise _error(
                            data_path, row, "timestamp", "must strictly increase"
                        )
                bars.append(bar)
        except csv.Error as exc:
            raise _error(data_path, reader.line_num or 1, "row", str(exc)) from exc
    if not bars:
        raise _error(data_path, 2, "klines", "at least one Kline is required")
    context = _read_context(sidecar) if sidecar is not None else MappingProxyType({})
    return KlineTSeries(bars), context


def write_kline_csv(
    series: KlineTSeries,
    path: str | Path,
    context_path: str | Path | None = None,
    *,
    context: Mapping[str, str] | None = None,
) -> None:
    """Write raw-nine CSV and optionally preserve context strings in a sidecar.

    Args:
        series: Validated bars to serialize without time or volume conversion.
        path: Output CSV path; an existing file is replaced.
        context_path: Sidecar destination, required when context is nonempty.
        context: Optional string mapping retained without trimming or conversion.

    Raises:
        ValueError: Series, context, or output paths are invalid. All validation
            occurs before opening either output file.
        OSError: An output file cannot be written.
    """
    # Validation consistently raises ValueError under the execution contract.
    if not isinstance(series, KlineTSeries):
        raise ValueError("series: a KlineTSeries is required")  # noqa: TRY004
    series.validate()
    if context is not None and not isinstance(context, Mapping):
        raise ValueError("context: a string mapping is required")
    saved_context: dict[str, str] = dict(context) if context is not None else {}
    for key, value in saved_context.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("context key: must be a nonblank string")
        if not isinstance(value, str):
            raise ValueError(  # noqa: TRY004
                f"context value for {key!r}: must be a string"
            )
    if saved_context and context_path is None:
        raise ValueError("context_path: required for nonempty context")
    data_path = Path(path)
    sidecar = Path(context_path) if context_path is not None else None
    if sidecar is not None:
        same_target = data_path.resolve() == sidecar.resolve() or (
            data_path.exists() and sidecar.exists() and data_path.samefile(sidecar)
        )
        if same_target:
            raise ValueError("context_path: must differ from data path")
    with data_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(RAW_COLUMNS)
        for bar in series:
            writer.writerow(
                (
                    bar.timestamp.isoformat(),
                    bar.symbol,
                    bar.period,
                    bar.source,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    bar.volume,
                )
            )
    if sidecar is not None:
        with sidecar.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(("key", "value"))
            writer.writerows(saved_context.items())
