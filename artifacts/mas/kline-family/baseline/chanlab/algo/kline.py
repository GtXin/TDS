"""Immutable raw OHLCV bars and their ordered series."""

# The execution contract requires ValueError for all validation failures.
# ruff: noqa: TRY004

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from math import isfinite
from numbers import Real


@dataclass(frozen=True, slots=True)
class Kline:
    """One raw bar; timestamps and volume retain the source convention."""

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
        for field in ("symbol", "period", "source"):
            value = getattr(self, field)
            if not isinstance(value, str) or value.strip() in ("", "NA"):
                raise ValueError(f"{field}: a nonblank provenance value is required")
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp: a timezone-aware UTC datetime is required")
        if (
            self.timestamp.tzinfo is None
            or self.timestamp.utcoffset() != timedelta(0)
        ):
            raise ValueError("timestamp: a timezone-aware UTC datetime is required")
        for field in ("open", "high", "low", "close", "volume"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
                raise ValueError(f"{field}: a finite numeric value is required")
            try:
                finite = value.is_finite() if isinstance(value, Decimal) else isfinite(value)
            except (TypeError, ValueError, OverflowError):
                finite = False
            if not finite:
                raise ValueError(f"{field}: a finite numeric value is required")
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
    """A nonempty immutable tuple for one symbol and period."""

    klines: tuple[Kline, ...]

    def __init__(self, klines: Iterable[Kline]) -> None:
        try:
            bars = tuple(klines)
        except TypeError as exc:
            raise ValueError("klines: an iterable of Kline objects is required") from exc
        object.__setattr__(self, "klines", bars)
        self.validate()

    def validate(self) -> None:
        if not self.klines:
            raise ValueError("klines: at least one Kline is required")
        first = None
        previous = None
        for index, bar in enumerate(self.klines):
            if not isinstance(bar, Kline):
                raise ValueError(f"klines[{index}]: a Kline object is required")
            try:
                bar.validate()
            except ValueError as exc:
                raise ValueError(f"klines[{index}].{exc}") from exc
            if first is not None:
                if bar.symbol != first.symbol:
                    raise ValueError(f"klines[{index}].symbol: mixed symbols")
                if bar.period != first.period:
                    raise ValueError(f"klines[{index}].period: mixed periods")
            else:
                first = bar
            if previous is not None and bar.timestamp <= previous:
                raise ValueError(f"klines[{index}].timestamp: must strictly increase")
            previous = bar.timestamp

    def __len__(self) -> int:
        return len(self.klines)

    def __iter__(self) -> Iterator[Kline]:
        return iter(self.klines)

    def __getitem__(self, key: int | slice) -> Kline | tuple[Kline, ...]:
        return self.klines[key]
