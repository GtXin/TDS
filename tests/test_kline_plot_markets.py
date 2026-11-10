"""Public plotting checks for US and China candle color conventions."""

from __future__ import annotations

from datetime import UTC, datetime
from types import ModuleType
from typing import Literal

import pytest

from chanlab.algo.kline import Kline, KlineTSeries


@pytest.fixture
def series() -> KlineTSeries:
    timestamps = (
        datetime(2026, 1, 2, 20, tzinfo=UTC),
        datetime(2026, 1, 2, 20, 15, tzinfo=UTC),
        datetime(2026, 1, 5, 9, tzinfo=UTC),
        datetime(2026, 1, 5, 9, 15, tzinfo=UTC),
    )
    # The middle bars move opposite to the preceding close comparison.
    # The final bar has equal open/close and stays a native zero-height body.
    prices = ((11.0, 12.0), (10.0, 11.0), (14.0, 13.0), (12.0, 12.0))
    return KlineTSeries(
        (
            Kline(
                symbol="TEST",
                period="15m",
                source=f"fixture/source/{index}",
                timestamp=timestamp,
                open=opening,
                high=max(opening, closing) + 1,
                low=min(opening, closing) - 1,
                close=closing,
                volume=100.0 + index,
            )
            for index, (timestamp, (opening, closing)) in enumerate(
                zip(timestamps, prices, strict=True)
            )
        ),
        context={"source_snapshot": "unchanged fixture"},
    )


@pytest.fixture
def plotly() -> ModuleType:
    return pytest.importorskip("plotly.graph_objects")


@pytest.mark.parametrize(
    "market,up,down",
    [
        (None, "#16a34a", "#dc2626"),
        ("US", "#16a34a", "#dc2626"),
        ("China", "#dc2626", "#16a34a"),
    ],
    ids=["default-US", "explicit-US", "China"],
)
@pytest.mark.parametrize("volume", [False, True])
def test_market_colors_preserve_native_candles_and_neutral_volume(
    series: KlineTSeries,
    plotly: ModuleType,
    market: Literal["US", "China"] | None,
    up: str,
    down: str,
    volume: bool,
) -> None:
    original_bars = series.klines
    fields = (
        "symbol",
        "period",
        "source",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )
    original_fields = tuple(
        tuple(getattr(bar, field) for field in fields) for bar in series
    )
    original_context = dict(series.context)
    figure = (
        series.plot(volume=volume)
        if market is None
        else series.plot(volume=volume, market=market)
    )

    assert isinstance(figure, plotly.Figure)
    assert [trace.type for trace in figure.data] == (
        ["candlestick", "bar"] if volume else ["candlestick"]
    )
    candle = figure.data[0]
    assert candle.increasing.line.color == candle.increasing.fillcolor == up
    assert candle.decreasing.line.color == candle.decreasing.fillcolor == down
    assert tuple(candle.x) == tuple(bar.timestamp for bar in series)
    for field in ("open", "high", "low", "close"):
        assert tuple(getattr(candle, field)) == tuple(
            getattr(bar, field) for bar in series
        )
    assert candle.open[-1] == candle.close[-1] == 12.0
    assert figure.layout.xaxis.type == "category"
    if volume:
        assert figure.data[1].marker.color == "#64748b"
        assert tuple(figure.data[1].x) == tuple(candle.x)
        assert tuple(figure.data[1].y) == tuple(bar.volume for bar in series)
        assert figure.layout.xaxis2.type == "category"

    assert series.klines is original_bars
    assert original_fields == tuple(
        tuple(getattr(bar, field) for field in fields) for bar in series
    )
    assert dict(series.context) == original_context


@pytest.mark.parametrize("show_gaps", [False, True])
def test_switching_market_changes_only_candle_colors(
    series: KlineTSeries, plotly: ModuleType, show_gaps: bool
) -> None:
    us = series.plot(market="US", show_gaps=show_gaps, title="Same viewport")
    china = series.plot(market="China", show_gaps=show_gaps, title="Same viewport")
    assert us.layout.to_plotly_json() == china.layout.to_plotly_json()
    assert us.data[1].to_plotly_json() == china.data[1].to_plotly_json()
    us_candles = us.data[0].to_plotly_json()
    china_candles = china.data[0].to_plotly_json()
    for field in ("increasing", "decreasing"):
        us_candles.pop(field)
        china_candles.pop(field)
    assert us_candles == china_candles
    assert us.layout.xaxis.type == ("date" if show_gaps else "category")


@pytest.mark.parametrize("market", ["UK", "us", "china", "", None, 1])
def test_invalid_market_is_rejected(series: KlineTSeries, market: object) -> None:
    with pytest.raises(ValueError, match="market"):
        series.plot(market=market)  # type: ignore[arg-type]
