"""Small, isolated value objects for the Python Pro OOP trial."""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import pairwise
from math import isfinite


@dataclass(frozen=True, slots=True)
class PriceBar:
    """An immutable OHLC bar validated at construction.

    Attributes:
        timestamp: An aware datetime whose UTC offset is zero.
        open: Opening price.
        high: Highest price.
        low: Lowest price.
        close: Closing price.

    Raises:
        ValueError: The timestamp is not UTC-aware, a price is nonfinite,
            or the opening/closing price lies outside the low/high interval.
    """

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self) -> None:
        if self.timestamp.utcoffset() != timedelta(0):
            raise ValueError("timestamp must be timezone-aware with a zero UTC offset")

        for name in ("open", "high", "low", "close"):
            if not isfinite(getattr(self, name)):
                raise ValueError(f"{name} must be finite")

        if not (self.low <= self.open <= self.high):
            raise ValueError("open must lie between low and high")
        if not (self.low <= self.close <= self.high):
            raise ValueError("close must lie between low and high")


@dataclass(frozen=True, slots=True, init=False)
class PriceSeries:
    """An immutable snapshot of bars in strictly increasing time order.

    Construction copies the supplied iterable into a tuple without sorting.
    Each bar validates its own prices; this class validates membership and order.

    Attributes:
        bars: The supplied PriceBar objects, retained in their original order.
    """

    bars: tuple[PriceBar, ...]

    def __init__(self, bars: Iterable[PriceBar]) -> None:
        """Snapshot bars and reject invalid members or timestamp order.

        Args:
            bars: An iterable of validated PriceBar objects; empty is allowed.

        Raises:
            TypeError: An item is not a PriceBar.
            ValueError: Timestamps are duplicate or decreasing.
        """
        snapshot = tuple(bars)
        if any(not isinstance(bar, PriceBar) for bar in snapshot):
            raise TypeError("all series items must be PriceBar objects")
        if any(
            current.timestamp <= previous.timestamp
            for previous, current in pairwise(snapshot)
        ):
            raise ValueError("bar timestamps must be strictly increasing")
        object.__setattr__(self, "bars", snapshot)

    def __iter__(self) -> Iterator[PriceBar]:
        """Iterate over the original bars in their supplied order."""
        return iter(self.bars)

    def __len__(self) -> int:
        """Return the number of bars in the snapshot."""
        return len(self.bars)
