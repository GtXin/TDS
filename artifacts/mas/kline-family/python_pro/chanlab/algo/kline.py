"""Immutable raw OHLCV bars, independent of I/O and feature calculations."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite
from typing import overload


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

    Raises:
        ValueError: Input is empty, invalid, mixed in identity, or out of order.
    """

    klines: tuple[Kline, ...]

    def __init__(self, klines: Iterable[Kline]) -> None:
        """Materialize the iterable once and validate the immutable snapshot."""
        try:
            bars = tuple(klines)
        except TypeError as exc:
            raise ValueError(
                "klines: an iterable of Kline objects is required"
            ) from exc
        object.__setattr__(self, "klines", bars)
        self.validate()

    def validate(self) -> None:
        """Check every bar, common metadata, and strictly increasing UTC time.

        Raises:
            ValueError: A series or bar field is invalid; its position is named.
        """
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
