"""Immutable raw OHLCV bars, independent of I/O and feature calculations."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime, timedelta
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, Self, overload

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-not-found]


@dataclass(frozen=True, slots=True)
class Kline:
    """One raw bar with source-defined timestamp labels and volume units.

    Construction validates provenance, an aware UTC timestamp, finite OHLCV,
    price bounds and nonnegative volume. Values are retained without conversion.
    """

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
        """Validate the newly constructed bar."""
        self.validate()

    def validate(self) -> None:
        """Validate all raw fields without modifying their values.

        Raises:
            ValueError: A required field is invalid; the message names the field.
        """
        for field, label in (
            ("symbol", self.symbol),
            ("period", self.period),
            ("source", self.source),
        ):
            if not isinstance(label, str) or label.strip() in ("", "NA"):
                raise ValueError(f"{field}: a nonblank provenance string is required")

        # Validation consistently raises ValueError under the execution contract.
        if not isinstance(self.timestamp, datetime):
            raise ValueError(  # noqa: TRY004
                "timestamp: a timezone-aware UTC datetime is required"
            )
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() != timedelta(0):
            raise ValueError("timestamp: a timezone-aware UTC datetime is required")

        for field, value in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
            ("volume", self.volume),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(  # noqa: TRY004
                    f"{field}: a finite float or int is required"
                )
            try:
                finite = isfinite(value)
            except OverflowError as exc:
                raise ValueError(f"{field}: value exceeds finite float range") from exc
            if not finite:
                raise ValueError(f"{field}: must be finite")
            if isinstance(value, int) and int(float(value)) != value:
                raise ValueError(
                    f"{field}: integer cannot be represented exactly as float"
                )

        if self.low > self.high:
            raise ValueError("low/high: low must not exceed high")
        if not self.low <= self.open <= self.high:
            raise ValueError("open: must be between low and high")
        if not self.low <= self.close <= self.high:
            raise ValueError("close: must be between low and high")
        if self.volume < 0:
            raise ValueError("volume: must be nonnegative")


@dataclass(frozen=True, slots=True, init=False)
class KlineTSeries:
    """A snapshot of ordered bars sharing one symbol and period.

    Args:
        klines: A nonempty iterable of valid bars. Mixed sources are allowed.
        context: Optional provenance strings, copied into an immutable snapshot.

    Raises:
        ValueError: Input is empty, invalid, mixed in identity, or out of order.
    """

    klines: tuple[Kline, ...]
    context: Mapping[str, str] = dataclass_field(hash=False)

    def __init__(
        self,
        klines: Iterable[Kline],
        *,
        context: Mapping[str, str] | None = None,
    ) -> None:
        """Snapshot the bars and provenance, then validate both without changes."""
        try:
            bars = tuple(klines)
        except TypeError as exc:
            raise ValueError(
                "klines: an iterable of Kline objects is required"
            ) from exc
        if context is not None and not isinstance(context, Mapping):
            raise ValueError("context: a string mapping is required")
        copied_context: dict[str, str] = dict(context) if context is not None else {}
        object.__setattr__(self, "klines", bars)
        object.__setattr__(self, "context", MappingProxyType(copied_context))
        self.validate()

    def validate(self) -> None:
        """Check every bar, common metadata, and strictly increasing UTC time.

        Raises:
            ValueError: A series or bar field is invalid; its position is named.
        """
        for key, value in self.context.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("context key: must be a nonblank string")
            if not isinstance(value, str):
                raise ValueError(  # noqa: TRY004
                    f"context value for {key!r}: must be a string"
                )
        if not self.klines:
            raise ValueError("klines: at least one Kline is required")
        first = self.klines[0]
        previous: datetime | None = None
        for index, bar in enumerate(self.klines):
            if not isinstance(bar, Kline):
                raise ValueError(  # noqa: TRY004
                    f"klines[{index}]: a Kline object is required"
                )
            try:
                bar.validate()
            except ValueError as exc:
                raise ValueError(f"klines[{index}].{exc}") from exc
            if bar.symbol != first.symbol:
                raise ValueError(f"klines[{index}].symbol: must match the first bar")
            if bar.period != first.period:
                raise ValueError(f"klines[{index}].period: must match the first bar")
            if previous is not None and bar.timestamp <= previous:
                raise ValueError(f"klines[{index}].timestamp: must strictly increase")
            previous = bar.timestamp

    def __len__(self) -> int:
        """Return the number of bars."""
        return len(self.klines)

    def __iter__(self) -> Iterator[Kline]:
        """Iterate over the bars in source chronology."""
        return iter(self.klines)

    @overload
    def __getitem__(self, key: int) -> Kline: ...

    @overload
    def __getitem__(self, key: slice) -> tuple[Kline, ...]: ...

    def __getitem__(self, key: int | slice) -> Kline | tuple[Kline, ...]:
        """Return a bar or tuple slice with standard Python indexing behavior."""
        return self.klines[key]

    @classmethod
    def read_csv(
        cls,
        path: str | Path,
        context_path: str | Path | None = None,
    ) -> Self:
        """Read raw-nine or master41 CSV and own its optional provenance.

        Args:
            path: Input CSV with one exact supported header.
            context_path: Optional key/value provenance sidecar.

        Returns:
            A validated series of this class with an immutable context snapshot.

        Raises:
            ValueError: CSV, bars, chronology, or provenance is invalid.
            OSError: An input file cannot be read.
        """
        from chanlab.data.kline_csv import read_kline_csv

        series, context = read_kline_csv(path, context_path)
        return cls(series.klines, context=context)

    def write_csv(
        self,
        path: str | Path,
        context_path: str | Path | None = None,
    ) -> None:
        """Write raw-nine CSV together with this series's owned provenance.

        Args:
            path: Output CSV destination.
            context_path: Sidecar destination, required for nonempty context.

        Raises:
            ValueError: Data, context, or destinations are invalid, or nonempty
                provenance has no sidecar destination.
            OSError: An output file cannot be written.
        """
        from chanlab.data.kline_csv import write_kline_csv

        write_kline_csv(self, path, context_path, context=self.context)

    def plot(
        self,
        *,
        start: int | None = None,
        stop: int | None = None,
        volume: bool = True,
        title: str | None = None,
        show_gaps: bool = False,
        market: Literal["US", "China"] = "US",
    ) -> Figure:
        """Return a Plotly candlestick figure through the optional plot adapter.

        Args:
            start: Inclusive bar index, using normal Python slice semantics.
            stop: Exclusive bar index, using normal Python slice semantics.
            volume: Include an aligned panel in source-defined volume units.
            title: Optional chart title; defaults to symbol, period and color preset.
            show_gaps: Use elapsed calendar time instead of consecutive bars.
            market: Candle colors: US green-up/red-down; China red-up/green-down.

        Returns:
            A figure with consecutive bars by default and unchanged UTC/OHLCV.

        Raises:
            ValueError: The selected slice is empty or market is unsupported.
            ImportError: Plotly is unavailable; install with uv sync --extra plot.
        """
        from chanlab.visualization.kline_plot import plot_kline_series

        return plot_kline_series(
            self,
            start=start,
            stop=stop,
            volume=volume,
            title=title,
            show_gaps=show_gaps,
            market=market,
        )
