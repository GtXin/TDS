"""Acceptance tests for class-owned merged plot options and readable defaults."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Any, Never

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries


@pytest.fixture
def plotly() -> ModuleType:
    """Figure assertions require the optional plotting extra."""
    return pytest.importorskip("plotly.graph_objects")


@pytest.fixture
def merged() -> MergedKlineSeries:
    """Memo015 intervals with a weekend gap inside a previously merged group."""
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
    raw = KlineTSeries(
        Kline(
            "TEST",
            "15m",
            "plot/fixture",
            datetime(2026, 1, 2, 20, tzinfo=UTC)
            + timedelta(minutes=15 * i, days=3 if i >= 7 else 0),
            low,
            high,
            low,
            high,
            100 + i,
        )
        for i, (low, high) in enumerate(intervals)
    )
    result = MergedKlineSeries.derive_from(
        raw, {"initialization": "UP"}, "memo015:test"
    )
    assert isinstance(result, MergedKlineSeries)
    assert [(b.source_start, b.source_stop) for b in result] == [
        (0, 1),
        (1, 5),
        (5, 10),
    ]
    return result


def _candles(figure: Any) -> Any:
    return next(trace for trace in figure.data if trace.type == "candlestick")


def _bands(figure: Any) -> list[Any]:
    return [trace for trace in figure.data if trace.type == "scatter"]


def _polygon_for(figure: Any, feature_id: int) -> tuple[list[Any], list[float]]:
    """Find one filled result chunk without depending on direction trace order."""
    for trace in _bands(figure):
        chunks: list[tuple[list[Any], list[float], list[str]]] = []
        xs: list[Any] = []
        ys: list[float] = []
        labels: list[str] = []
        for x, y, label in zip(trace.x, trace.y, trace.text, strict=True):
            if x is None:
                if xs:
                    chunks.append((xs, ys, labels))
                xs, ys, labels = [], [], []
            else:
                xs.append(x)
                ys.append(y)
                labels.append(label)
        if xs:
            chunks.append((xs, ys, labels))
        for xchunk, ychunk, labels in chunks:
            if f"MK{feature_id} " in labels[0]:
                assert len(xchunk) == len(ychunk) == 5
                assert xchunk[0] == xchunk[-1] and ychunk[0] == ychunk[-1]
                return xchunk, ychunk
    raise AssertionError(f"No filled interval found for MK{feature_id}")


def test_default_overlay_is_gap_free_and_preserves_source_without_output(
    merged: MergedKlineSeries,
    plotly: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def unexpected_output(*args: object, **kwargs: object) -> Never:
        raise AssertionError("plot() must not display or write files")

    for method in ("show", "write_html", "write_image"):
        monkeypatch.setattr(plotly.Figure, method, unexpected_output)
    monkeypatch.chdir(tmp_path)
    raw = merged.source_series
    before = (raw.klines, merged.klines, dict(merged.config), merged.trace_by_point)

    figure = merged.plot()

    assert isinstance(figure, plotly.Figure)
    assert figure.layout.meta["style"] == "overlay"
    assert figure.layout.meta["show_gaps"] is False
    assert figure.layout.meta["raw_start"] == 0
    assert figure.layout.meta["raw_stop"] == len(raw)
    assert figure.layout.meta["merged_count"] == len(merged)
    candle = _candles(figure)
    assert tuple(candle.x) == tuple(range(len(raw)))
    assert tuple(candle.customdata) == tuple(b.timestamp.isoformat() for b in raw)
    assert any("UTC" in label for label in candle.text)
    for field in ("open", "high", "low", "close"):
        assert tuple(getattr(candle, field)) == tuple(getattr(b, field) for b in raw)
    volumes = next(trace for trace in figure.data if trace.type == "bar")
    assert tuple(volumes.x) == tuple(candle.x)
    assert tuple(volumes.y) == tuple(b.volume for b in raw)
    assert figure.layout.xaxis.type == figure.layout.xaxis2.type == "linear"
    assert "UTC" in figure.layout.xaxis2.title.text
    assert "gaps hidden" in figure.layout.xaxis2.title.text
    assert len(figure.layout.xaxis.ticktext) == len(figure.layout.xaxis.tickvals)
    assert all(trace.fill == "toself" for trace in _bands(figure))
    candle_index = next(
        i for i, trace in enumerate(figure.data) if trace.type == "candlestick"
    )
    assert all(
        i < candle_index
        for i, trace in enumerate(figure.data)
        if trace.type == "scatter"
    )
    assert before == (
        raw.klines,
        merged.klines,
        dict(merged.config),
        merged.trace_by_point,
    )
    assert raw.klines is before[0] and merged.klines is before[1]
    assert list(tmp_path.iterdir()) == []


def test_filled_ranges_represent_bounds_and_member_coverage(
    merged: MergedKlineSeries, plotly: ModuleType
) -> None:
    figure = merged.plot(volume=False)
    for bar in merged:
        xs, ys = _polygon_for(figure, bar.id)
        assert set(ys) == {bar.low, bar.high}
        assert min(xs) <= bar.source_start and max(xs) >= bar.source_stop - 1
        assert min(xs) > bar.source_start - 0.5
        assert max(xs) < bar.source_stop - 0.5
    assert len([t for t in figure.data if t.type == "candlestick"]) == 1
    assert not any(t.type == "bar" for t in figure.data)


def test_merged_bounds_still_select_result_positions(
    merged: MergedKlineSeries, plotly: ModuleType
) -> None:
    figure = merged.plot(start=1, stop=2, volume=False)
    bar = merged[1]
    candle = _candles(figure)
    assert len(candle.x) == bar.source_stop - bar.source_start == 4
    assert tuple(candle.high) == tuple(b.high for b in merged.source_series[1:5])
    assert figure.layout.meta["raw_start"] == 1
    assert figure.layout.meta["raw_stop"] == 5
    assert figure.layout.meta["merged_count"] == 1
    _polygon_for(figure, bar.id)


@pytest.mark.parametrize("bounds", [(2, 7), (-5, None), (None, 3), (7, 8)])
def test_raw_viewport_is_a_slice_of_the_full_computed_result(
    merged: MergedKlineSeries,
    plotly: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    bounds: tuple[int | None, int | None],
) -> None:
    def no_recalculation(*args: object, **kwargs: object) -> Never:
        raise AssertionError(
            "raw viewport selection must not recalculate the algorithm"
        )

    monkeypatch.setattr(MergedKlineSeries, "derive_from", no_recalculation)
    raw_start, raw_stop = bounds
    figure = merged.plot(raw_start=raw_start, raw_stop=raw_stop, volume=False)
    first, stop, _ = slice(raw_start, raw_stop).indices(len(merged.source_series))
    candles = _candles(figure)
    assert tuple(candles.low) == tuple(b.low for b in merged.source_series[first:stop])
    assert len(candles.x) == stop - first
    expected = [b for b in merged if b.source_start < stop and b.source_stop > first]
    assert figure.layout.meta["merged_count"] == len(expected)
    for bar in expected:
        xs, ys = _polygon_for(figure, bar.id)
        assert set(ys) == {bar.low, bar.high}
        assert min(xs) > -0.5 and max(xs) < len(candles.x) - 0.5
        assert any(
            f"raw[{bar.source_start}:{bar.source_stop})" in (label or "")
            for trace in _bands(figure)
            for label in trace.text
        )
    if bounds == (7, 8):
        # This raw bar's high=6 is not the precomputed group's high=4.
        assert list(candles.high) == [6]
        assert set(_polygon_for(figure, merged[2].id)[1]) == {0, 4}
        assert any(
            "clipped" in (label or "").lower()
            for t in _bands(figure)
            for label in t.text
        )


def test_last40_raw_bars_use_exact_source_viewport(plotly: ModuleType) -> None:
    folder = Path(__file__).resolve().parents[1] / "samples/chan_table"
    raw = KlineTSeries.read_csv(
        next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv"))
    )
    result = MergedKlineSeries.derive_from(
        raw, {"initialization": "UP"}, "full-sample:test"
    )
    assert isinstance(result, MergedKlineSeries)
    figure = result.plot(raw_start=-40, volume=False)
    assert len(_candles(figure).x) == 40
    assert tuple(_candles(figure).close) == tuple(b.close for b in raw[-40:])
    assert figure.layout.meta["raw_start"] == len(raw) - 40
    assert figure.layout.meta["raw_stop"] == len(raw)
    assert figure.layout.meta["merged_count"] == 26


@pytest.mark.parametrize("volume", [False, True])
def test_panels_separate_original_merged_and_optional_volume(
    merged: MergedKlineSeries, plotly: ModuleType, volume: bool
) -> None:
    figure = merged.plot(style="panels", volume=volume)
    assert figure.layout.meta["style"] == "panels"
    assert _candles(figure).yaxis == "y"
    assert all(trace.yaxis == "y2" for trace in _bands(figure))
    assert figure.layout.yaxis.range == figure.layout.yaxis2.range
    assert figure.layout.xaxis.type == figure.layout.xaxis2.type == "linear"
    if volume:
        volumes = next(trace for trace in figure.data if trace.type == "bar")
        assert volumes.yaxis == "y3"
        assert figure.layout.xaxis3.type == "linear"
        assert tuple(volumes.y) == tuple(b.volume for b in merged.source_series)
    else:
        assert not any(trace.type == "bar" for trace in figure.data)
        assert "yaxis3" not in figure.layout.to_plotly_json()


@pytest.mark.parametrize("style", ["overlay", "panels", "ranges"])
def test_calendar_option_retains_original_timestamps_and_actual_gap(
    merged: MergedKlineSeries, plotly: ModuleType, style: str
) -> None:
    figure = merged.plot(style=style, show_gaps=True, volume=False)
    candles = _candles(figure)
    assert tuple(candles.x) == tuple(b.timestamp for b in merged.source_series)
    assert candles.x[7] - candles.x[6] > timedelta(days=2)
    assert figure.layout.xaxis.type == "date"
    assert figure.layout.meta["show_gaps"] is True
    for trace in _bands(figure):
        assert all(isinstance(x, datetime) for x in trace.x if x is not None)
    if style == "panels":
        assert figure.layout.xaxis2.type == "date"
    if style == "ranges":
        assert all(trace.fill is None for trace in _bands(figure))
        assert all("markers" in trace.mode for trace in _bands(figure))


@pytest.mark.parametrize("show_gaps", [False, True])
def test_one_raw_bar_still_has_visible_interval_and_valid_ticks(
    plotly: ModuleType, show_gaps: bool
) -> None:
    raw = KlineTSeries(
        [Kline("ONE", "1m", "manual", datetime(2026, 1, 1, tzinfo=UTC), 2, 3, 1, 2, 1)]
    )
    result = MergedKlineSeries.derive_from(
        raw, {"initialization": "UP"}, "singleton:test"
    )
    assert isinstance(result, MergedKlineSeries)
    figure = result.plot(show_gaps=show_gaps, volume=False)
    assert len(_candles(figure).x) == 1
    xs, ys = _polygon_for(figure, result[0].id)
    assert max(xs) > min(xs) and set(ys) == {1, 3}
    if not show_gaps:
        assert tuple(figure.layout.xaxis.tickvals) == (0,)


@pytest.mark.parametrize(
    "options",
    [
        {"start": 0, "stop": 0},
        {"start": 2, "stop": 1},
        {"start": 100},
        {"raw_start": 0, "raw_stop": 0},
        {"raw_start": 8, "raw_stop": 2},
        {"raw_start": 100},
        {"raw_start": -100, "raw_stop": -100},
        {"start": 0, "raw_start": 0},
        {"stop": 2, "raw_stop": 9},
        {"style": "unknown"},
        {"style": None},
        {"show_gaps": "false"},
        {"show_gaps": 0},
        {"volume": 1},
        {"volume": None},
    ],
)
def test_invalid_or_ambiguous_plot_requests_raise_value_error(
    merged: MergedKlineSeries, options: dict[str, Any]
) -> None:
    with pytest.raises(ValueError):
        merged.plot(**options)


def test_interactive_legend_and_standalone_html(
    merged: MergedKlineSeries, plotly: ModuleType, tmp_path: Path
) -> None:
    figure = merged.plot(volume=False)
    assert figure.layout.legend.groupclick == "togglegroup"
    assert figure.layout.showlegend is True
    assert all(trace.legendgroup for trace in _bands(figure))
    assert all("%{text}" in trace.hovertemplate for trace in _bands(figure))
    destination = tmp_path / "overlay.html"
    figure.write_html(destination, include_plotlyjs=True)
    document = destination.read_text()
    assert "Plotly.newPlot" in document and "plotly.js" in document.lower()
    assert "Merged up" in document and "Original K-lines" in document
    assert destination.stat().st_size > 100_000
