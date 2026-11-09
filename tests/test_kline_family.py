"""Shared memo013 domain acceptance tests, independent of implementation variant."""

from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from fractions import Fraction

import pytest

from chanlab.algo.kline import Kline, KlineTSeries


def make_bar(**changes):
    values = {
        "symbol": "TEST",
        "period": "15m",
        "source": "fixture/source",
        "timestamp": datetime(2026, 1, 1, tzinfo=UTC),
        "open": 11.0,
        "high": 13.0,
        "low": 10.0,
        "close": 12.0,
        "volume": 20.0,
    }
    values.update(changes)
    return Kline(**values)


def test_valid_bar_preserves_all_nine_fields_and_can_be_validated():
    bar = make_bar()
    assert (bar.symbol, bar.period, bar.source) == ("TEST", "15m", "fixture/source")
    assert bar.timestamp == datetime(2026, 1, 1, tzinfo=UTC)
    assert (bar.open, bar.high, bar.low, bar.close, bar.volume) == (11, 13, 10, 12, 20)
    bar.validate()


@pytest.mark.parametrize("field", ["symbol", "period", "source"])
@pytest.mark.parametrize("value", ["", " \t", "NA", None, 123])
def test_metadata_is_required(field, value):
    with pytest.raises(ValueError):
        make_bar(**{field: value})


@pytest.mark.parametrize(
    "value",
    [
        None,
        "2026-01-01T00:00:00Z",
        date(2026, 1, 1),
        datetime(2026, 1, 1),
        datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1))),
    ],
)
def test_timestamp_requires_aware_utc_datetime(value):
    with pytest.raises(ValueError):
        make_bar(timestamp=value)


@pytest.mark.parametrize("field", ["open", "high", "low", "close", "volume"])
@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), -float("inf"), "11", True, None]
)
def test_numeric_fields_reject_nonfinite_nonnumeric_and_bool(field, value):
    with pytest.raises(ValueError):
        make_bar(**{field: value})


@pytest.mark.parametrize("value", [Decimal("1e1000"), Fraction(1, 3)])
def test_values_outside_float_contract_are_rejected(value):
    # Raw exports must reload through the declared float CSV representation.
    with pytest.raises(ValueError, match="volume"):
        make_bar(volume=value)


def test_integer_values_must_be_exactly_representable_as_float():
    value = 2**53 + 1
    with pytest.raises(ValueError, match="open"):
        make_bar(open=value, high=value, low=value, close=value, volume=0)


@pytest.mark.parametrize(
    "changes",
    [
        {"open": 9},
        {"open": 14},
        {"close": 9},
        {"close": 14},
        {"low": 14},
        {"high": 9},
        {"volume": -1},
    ],
)
def test_price_bounds_and_volume_are_validated_at_construction(changes):
    with pytest.raises(ValueError):
        make_bar(**changes)


def test_negative_prices_and_equal_bounds_are_valid():
    make_bar(open=-4, high=-2, low=-6, close=-3, volume=0).validate()
    make_bar(open=0, high=0, low=0, close=0, volume=0).validate()


def test_bar_is_immutable():
    bar = make_bar()
    with pytest.raises((AttributeError, TypeError)):
        bar.close = 11
    with pytest.raises((AttributeError, TypeError)):
        del bar.symbol


def test_series_snapshots_input_and_supports_normal_sequence_operations():
    first = make_bar()
    second = make_bar(timestamp=first.timestamp + timedelta(minutes=15), source="other")
    incoming = [first, second]
    series = KlineTSeries(incoming)
    incoming.clear()
    assert isinstance(series.klines, tuple)
    assert series.klines == (first, second)
    assert len(series) == 2
    assert tuple(iter(series)) == (first, second)
    assert series[0] is first
    assert series[-1] is second
    assert series[:] == (first, second)
    assert isinstance(series[:], tuple)
    assert series[::-1] == (second, first)
    assert series[1:1] == ()
    assert series[100:] == ()
    series.validate()
    generated = KlineTSeries(bar for bar in (first, second))
    assert generated.klines == series.klines


def test_series_and_stored_tuple_are_immutable():
    series = KlineTSeries([make_bar()])
    with pytest.raises((AttributeError, TypeError)):
        series.klines = ()
    with pytest.raises(TypeError):
        series.klines[0] = make_bar()


@pytest.mark.parametrize("key", [1, -2])
def test_out_of_range_integer_access_raises_index_error(key):
    with pytest.raises(IndexError):
        KlineTSeries([make_bar()])[key]


@pytest.mark.parametrize("key", ["0", 0.5, None])
def test_invalid_sequence_key_raises_type_error(key):
    with pytest.raises(TypeError):
        KlineTSeries([make_bar()])[key]


def test_zero_slice_step_raises_value_error():
    with pytest.raises(ValueError):
        KlineTSeries([make_bar()])[::0]


@pytest.mark.parametrize("bars", [[], [None], ["bar"]])
def test_series_requires_nonempty_kline_records(bars):
    with pytest.raises(ValueError):
        KlineTSeries(bars)


@pytest.mark.parametrize("changes", [{"symbol": "OTHER"}, {"period": "1m"}])
def test_series_rejects_mixed_symbols_or_periods(changes):
    first = make_bar()
    second = make_bar(timestamp=first.timestamp + timedelta(minutes=15), **changes)
    with pytest.raises(ValueError):
        KlineTSeries([first, second])


@pytest.mark.parametrize("minutes", [0, -15])
def test_series_requires_strictly_increasing_timestamps(minutes):
    first = make_bar()
    second = make_bar(timestamp=first.timestamp + timedelta(minutes=minutes))
    with pytest.raises(ValueError):
        KlineTSeries([first, second])
