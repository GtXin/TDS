"""Merged plots share the raw-family US/China palette without changing data."""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries


@pytest.fixture
def plotly() -> ModuleType:
    return pytest.importorskip("plotly.graph_objects")


@pytest.fixture
def merged() -> MergedKlineSeries:
    intervals = [
        (1, 3),
        (2, 4),
        (1, 5),
        (3, 5),
        (3, 6),
        (1, 5),
        (2, 4),
        (0, 6),
        (0, 4),
        (0, 5),
    ]
    bars = []
    for i, (low, high) in enumerate(intervals):
        opening, closing = (low, high) if i % 2 == 0 else (high, low)
        if i == len(intervals) - 1:
            opening = closing = (low + high) / 2
        bars.append(
            Kline(
                "TEST",
                "15m",
                "market-fixture",
                datetime(2026, 1, 2, 20, tzinfo=UTC)
                + timedelta(minutes=15 * i, days=3 if i >= 7 else 0),
                opening,
                high,
                low,
                closing,
                100 + i,
            )
        )
    source = KlineTSeries(bars, context={"source_snapshot": "market-fixture:v1"})
    result = MergedKlineSeries.derive_from(
        source, {"initialization": "UP"}, "memo015:market-test"
    )
    assert isinstance(result, MergedKlineSeries)
    assert [bar.direction for bar in result] == [None, "up", "down"]
    return result


def _candles(figure: Any) -> Any:
    return next(trace for trace in figure.data if trace.type == "candlestick")


def test_default_market_is_explicit_us(
    merged: MergedKlineSeries, plotly: ModuleType
) -> None:
    default = merged.plot()
    explicit = merged.plot(market="US")
    assert isinstance(default, plotly.Figure)
    assert default.to_plotly_json() == explicit.to_plotly_json()
    assert default.layout.meta["market"] == "US"
    assert "US colors" in default.layout.title.text
    assert default.layout.meta["style"] == "overlay"
    assert default.layout.meta["show_gaps"] is False


@pytest.mark.parametrize("style", ["overlay", "panels", "ranges"])
@pytest.mark.parametrize("show_gaps", [False, True])
@pytest.mark.parametrize(
    "market,up,down,up_fill,down_fill",
    [
        ("US", "#16a34a", "#dc2626", "rgba(22,163,74,0.10)", "rgba(220,38,38,0.10)"),
        (
            "China",
            "#dc2626",
            "#16a34a",
            "rgba(220,38,38,0.10)",
            "rgba(22,163,74,0.10)",
        ),
    ],
)
def test_candles_and_merged_ranges_match_raw_palette(
    merged: MergedKlineSeries,
    plotly: ModuleType,
    style: str,
    show_gaps: bool,
    market: Literal["US", "China"],
    up: str,
    down: str,
    up_fill: str,
    down_fill: str,
) -> None:
    figure = merged.plot(style=style, show_gaps=show_gaps, market=market)
    raw_figure = merged.source_series.plot(market=market, show_gaps=show_gaps)
    candle = _candles(figure)
    raw_candle = _candles(raw_figure)
    assert candle.increasing.line.color == candle.increasing.fillcolor == up
    assert candle.decreasing.line.color == candle.decreasing.fillcolor == down
    assert candle.increasing.line.color == raw_candle.increasing.line.color
    assert candle.increasing.fillcolor == raw_candle.increasing.fillcolor
    assert candle.decreasing.line.color == raw_candle.decreasing.line.color
    assert candle.decreasing.fillcolor == raw_candle.decreasing.fillcolor
    for field in ("open", "high", "low", "close"):
        assert tuple(getattr(candle, field)) == tuple(
            getattr(bar, field) for bar in merged.source_series
        )
    # The doji remains a zero-height original body, not a reclassified feature.
    assert candle.open[-1] == candle.close[-1]
    ranges = {
        trace.legendgroup: trace for trace in figure.data if trace.type == "scatter"
    }
    assert ranges["merged-up"].line.color == up
    assert ranges["merged-down"].line.color == down
    assert ranges["merged-None"].line.color == "#64748b"
    if style != "ranges":
        assert ranges["merged-up"].fillcolor == up_fill
        assert ranges["merged-down"].fillcolor == down_fill
        assert ranges["merged-None"].fillcolor == "rgba(100,116,139,0.10)"
    volume = next(trace for trace in figure.data if trace.type == "bar")
    assert volume.marker.color == "#64748b"
    assert tuple(volume.y) == tuple(bar.volume for bar in merged.source_series)
    assert figure.layout.meta["market"] == market
    assert f"{market} colors" in figure.layout.title.text


def _without_palette(figure: Any) -> dict[str, Any]:
    document = deepcopy(figure.to_plotly_json())
    document["layout"]["meta"].pop("market")
    for trace in document["data"]:
        if trace["type"] == "candlestick":
            for direction in ("increasing", "decreasing"):
                trace[direction]["line"].pop("color")
                trace[direction].pop("fillcolor")
        elif trace["type"] == "scatter":
            trace["line"].pop("color")
            trace.pop("fillcolor", None)
    return document


@pytest.mark.parametrize("show_gaps", [False, True])
@pytest.mark.parametrize("style", ["overlay", "panels", "ranges"])
def test_market_only_changes_palette_and_label_metadata(
    merged: MergedKlineSeries,
    plotly: ModuleType,
    style: str,
    show_gaps: bool,
) -> None:
    raw = merged.source_series
    bars_before = raw.klines
    merged_before = merged.klines
    config_before = dict(merged.config)
    trace_before = merged.trace
    provenance_before = dict(raw.context)
    options = {
        "raw_start": 2,
        "raw_stop": 9,
        "style": style,
        "show_gaps": show_gaps,
        "title": "Same data and viewport",
    }
    us = merged.plot(market="US", **options)
    china = merged.plot(market="China", **options)
    assert _without_palette(us) == _without_palette(china)
    assert us.layout.title.text == china.layout.title.text == options["title"]
    assert raw.klines is bars_before
    assert merged.klines is merged_before
    assert merged.trace is trace_before
    assert dict(merged.config) == config_before
    assert dict(raw.context) == provenance_before


@pytest.mark.parametrize("market", ["UK", "us", "china", "", None, 1])
def test_invalid_market_is_rejected(merged: MergedKlineSeries, market: object) -> None:
    with pytest.raises(ValueError, match="market"):
        merged.plot(market=market)  # type: ignore[arg-type]


def test_wrapper_forwards_market_and_all_plot_options(
    merged: MergedKlineSeries,
    plotly: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import chanlab.visualization.merged_kline_plot as renderer

    calls: list[dict[str, Any]] = []
    sentinel = plotly.Figure()

    def fake(
        series: MergedKlineSeries,
        *,
        start: int | None = None,
        stop: int | None = None,
        raw_start: int | None = None,
        raw_stop: int | None = None,
        volume: bool = True,
        title: str | None = None,
        style: str = "overlay",
        show_gaps: bool = False,
        market: str = "US",
    ) -> Any:
        calls.append(
            {
                "series": series,
                "start": start,
                "stop": stop,
                "raw_start": raw_start,
                "raw_stop": raw_stop,
                "volume": volume,
                "title": title,
                "style": style,
                "show_gaps": show_gaps,
                "market": market,
            }
        )
        return sentinel

    monkeypatch.setattr(renderer, "plot_merged_kline_series", fake)
    assert (
        merged.plot(
            raw_start=-5,
            raw_stop=-1,
            volume=False,
            title="China viewport",
            style="panels",
            show_gaps=True,
            market="China",
        )
        is sentinel
    )
    assert calls[0] == {
        "series": merged,
        "start": None,
        "stop": None,
        "raw_start": -5,
        "raw_stop": -1,
        "volume": False,
        "title": "China viewport",
        "style": "panels",
        "show_gaps": True,
        "market": "China",
    }
    assert merged.plot() is sentinel
    assert calls[1]["market"] == "US"
    assert calls[1]["style"] == "overlay" and calls[1]["show_gaps"] is False


def test_china_interactive_html_retains_selected_palette(
    merged: MergedKlineSeries, plotly: ModuleType, tmp_path: Path
) -> None:
    figure = merged.plot(market="China", volume=False)
    destination = tmp_path / "china-overlay.html"
    figure.write_html(destination, include_plotlyjs=True)
    html = destination.read_text()
    assert "Plotly.newPlot" in html and "plotly.js" in html.lower()
    assert "China colors" in html and '"market":"China"' in html
    assert "rgba(220,38,38,0.10)" in html and "rgba(22,163,74,0.10)" in html
    assert figure.layout.legend.groupclick == "togglegroup"
