"""Behavior checks for the isolated Python Pro OOP trial."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest
from price_models import PriceBar, PriceSeries


@pytest.fixture
def bar() -> PriceBar:
    """Return a valid bar with distinct OHLC prices."""
    return PriceBar(
        timestamp=datetime(2026, 11, 8, 12, tzinfo=UTC),
        open=101.0,
        high=105.0,
        low=99.0,
        close=103.0,
    )


def test_bar_preserves_valid_input(bar: PriceBar) -> None:
    assert bar.timestamp == datetime(2026, 11, 8, 12, tzinfo=UTC)
    assert (bar.open, bar.high, bar.low, bar.close) == (101.0, 105.0, 99.0, 103.0)


@pytest.mark.parametrize(
    "prices",
    [
        {"open": 99.0, "close": 105.0},
        {"open": 105.0, "close": 99.0},
        {"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0},
        {"open": -3.0, "high": -1.0, "low": -5.0, "close": -2.0},
    ],
    ids=["boundary-prices", "reversed-boundaries", "flat-bar", "negative-prices"],
)
def test_valid_bounds_are_inclusive(bar: PriceBar, prices: dict[str, float]) -> None:
    result = replace(bar, **prices)
    assert result.low <= result.open <= result.high
    assert result.low <= result.close <= result.high


@pytest.mark.parametrize(
    "prices",
    [
        {"open": 98.0},
        {"open": 106.0},
        {"close": 98.0},
        {"close": 106.0},
        {"low": 106.0, "high": 98.0},
    ],
    ids=["open-below", "open-above", "close-below", "close-above", "inverted-range"],
)
def test_invalid_price_bounds_are_rejected(
    bar: PriceBar, prices: dict[str, float]
) -> None:
    with pytest.raises(ValueError, match="between low and high"):
        replace(bar, **prices)


@pytest.mark.parametrize("field", ["open", "high", "low", "close"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_each_price_must_be_finite(bar: PriceBar, field: str, value: float) -> None:
    with pytest.raises(ValueError, match=f"{field} must be finite"):
        replace(bar, **{field: value})


@pytest.mark.parametrize(
    "timestamp",
    [
        datetime(2026, 11, 8, 12),
        datetime(2026, 11, 8, 12, tzinfo=timezone(timedelta(hours=8))),
        datetime(2026, 11, 8, 12, tzinfo=timezone(timedelta(hours=-8))),
    ],
    ids=["naive", "positive-offset", "negative-offset"],
)
def test_timestamp_must_be_utc_aware(bar: PriceBar, timestamp: datetime) -> None:
    with pytest.raises(ValueError, match="timezone-aware with a zero UTC offset"):
        replace(bar, timestamp=timestamp)


def test_bar_cannot_be_mutated(bar: PriceBar) -> None:
    with pytest.raises(FrozenInstanceError):
        bar.close = 104.0  # type: ignore[misc]


def test_series_preserves_bar_objects_and_input_order(bar: PriceBar) -> None:
    later = replace(bar, timestamp=bar.timestamp + timedelta(minutes=1))
    series = PriceSeries([bar, later])

    assert len(series) == 2
    assert list(series) == [bar, later]
    assert series.bars[0] is bar
    assert series.bars[1] is later


def test_series_defensively_snapshots_a_mutable_container(bar: PriceBar) -> None:
    supplied = [bar]
    series = PriceSeries(supplied)
    supplied.clear()

    assert series.bars == (bar,)
    with pytest.raises(FrozenInstanceError):
        series.bars = ()  # type: ignore[misc]


def test_series_accepts_a_one_pass_iterable(bar: PriceBar) -> None:
    series = PriceSeries(item for item in [bar])
    assert list(series) == [bar]
    assert list(series) == [bar]


def test_empty_series_is_valid() -> None:
    series = PriceSeries([])
    assert len(series) == 0
    assert list(series) == []


def test_series_rejects_duplicate_timestamps(bar: PriceBar) -> None:
    duplicate = replace(bar, close=104.0)
    with pytest.raises(ValueError, match="strictly increasing"):
        PriceSeries([bar, duplicate])


def test_series_rejects_decreasing_timestamps_without_sorting(bar: PriceBar) -> None:
    earlier = replace(bar, timestamp=bar.timestamp - timedelta(minutes=1))
    with pytest.raises(ValueError, match="strictly increasing"):
        PriceSeries([bar, earlier])


def test_series_checks_order_beyond_the_first_pair(bar: PriceBar) -> None:
    later = replace(bar, timestamp=bar.timestamp + timedelta(minutes=1))
    with pytest.raises(ValueError, match="strictly increasing"):
        PriceSeries([bar, later, bar])


def test_series_rejects_items_that_are_not_bars() -> None:
    with pytest.raises(TypeError, match="PriceBar objects"):
        PriceSeries([object()])  # type: ignore[list-item]
