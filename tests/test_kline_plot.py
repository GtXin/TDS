"""Focused acceptance checks for optional, side-effect-free Kline plotting."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType
from typing import Never

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.visualization import kline_plot


@pytest.fixture
def series() -> KlineTSeries:
    """Provide distinct UTC bars spanning a weekend session gap."""
    timestamps = (
        datetime(2026, 1, 2, 20, tzinfo=UTC),
        datetime(2026, 1, 2, 20, 15, tzinfo=UTC),
        datetime(2026, 1, 5, 9, tzinfo=UTC),
        datetime(2026, 1, 5, 9, 15, tzinfo=UTC),
    )
    return KlineTSeries(
        Kline(
            symbol="TEST",
            period="15m",
            source=f"fixture/source/{index}",
            timestamp=timestamp,
            open=11.0 + index,
            high=13.0 + index,
            low=10.0 + index,
            close=12.0 + index,
            volume=20.0 + index,
        )
        for index, timestamp in enumerate(timestamps)
    )


@pytest.fixture
def plotly() -> ModuleType:
    """Skip figure checks when the optional plotting extra is absent."""
    return pytest.importorskip("plotly.graph_objects")


def test_full_figure_preserves_values_and_source_without_display_or_export(
    series: KlineTSeries,
    plotly: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def unexpected_output(*args: object, **kwargs: object) -> Never:
        raise AssertionError("plot() must return without displaying or exporting")

    monkeypatch.setattr(plotly.Figure, "show", unexpected_output)
    monkeypatch.setattr(plotly.Figure, "write_html", unexpected_output)
    monkeypatch.chdir(tmp_path)
    original = series.klines
    original_fields = tuple(
        (bar.timestamp, bar.symbol, bar.period, bar.source, bar.volume)
        for bar in series
    )

    figure = series.plot()

    assert isinstance(figure, plotly.Figure)
    assert [trace.type for trace in figure.data] == ["candlestick", "bar"]
    candle, volume = figure.data
    timestamps = tuple(bar.timestamp for bar in series)
    assert tuple(candle.x) == timestamps
    assert tuple(volume.x) == timestamps
    for field in ("open", "high", "low", "close"):
        assert tuple(getattr(candle, field)) == tuple(
            getattr(bar, field) for bar in series
        )
    assert tuple(volume.y) == tuple(bar.volume for bar in series)
    assert candle.x[2] - candle.x[1] > timedelta(days=2)
    assert all(timestamp.tzinfo == UTC for timestamp in candle.x)
    assert figure.layout.xaxis.type == figure.layout.xaxis2.type == "category"
    assert tuple(figure.layout.xaxis.categoryarray) == timestamps
    assert tuple(figure.layout.xaxis2.categoryarray) == timestamps
    assert figure.layout.xaxis.categoryorder == "array"
    assert figure.layout.xaxis.tickvals[0] == timestamps[0]
    assert figure.layout.xaxis.tickvals[-1] == timestamps[-1]
    assert not figure.layout.xaxis.rangebreaks
    assert not figure.layout.xaxis2.rangebreaks
    assert figure.layout.xaxis.matches == "x2" or figure.layout.xaxis2.matches == "x"
    assert "UTC" in figure.layout.xaxis2.title.text
    assert "gaps hidden" in figure.layout.xaxis2.title.text
    assert "source" in figure.layout.yaxis2.title.text.lower()
    assert series[0].symbol in figure.layout.title.text
    assert series[0].period in figure.layout.title.text
    assert series.klines is original
    assert original_fields == tuple(
        (bar.timestamp, bar.symbol, bar.period, bar.source, bar.volume)
        for bar in series
    )
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("volume", [False, True])
def test_calendar_option_keeps_elapsed_time_axis(
    series: KlineTSeries, plotly: ModuleType, volume: bool
) -> None:
    figure = series.plot(volume=volume, show_gaps=True)
    assert figure.layout.xaxis.type == "date"
    assert tuple(figure.data[0].x) == tuple(bar.timestamp for bar in series)
    assert not figure.layout.xaxis.rangebreaks
    assert figure.layout.xaxis.tickmode is None
    if volume:
        assert figure.layout.xaxis2.type == "date"
        assert tuple(figure.data[1].x) == tuple(figure.data[0].x)


def test_one_bar_category_axis_has_valid_ticks(
    series: KlineTSeries, plotly: ModuleType
) -> None:
    single = KlineTSeries([series[0]])
    figure = single.plot(volume=False)
    assert figure.layout.xaxis.type == "category"
    assert tuple(figure.layout.xaxis.categoryarray) == (single[0].timestamp,)
    assert tuple(figure.layout.xaxis.tickvals) == (single[0].timestamp,)


@pytest.mark.parametrize("start,stop", [(1, 3), (-3, -1), (None, 2), (2, None)])
def test_helper_uses_python_slice_bounds_and_can_omit_volume(
    series: KlineTSeries,
    plotly: ModuleType,
    start: int | None,
    stop: int | None,
) -> None:
    figure = kline_plot.plot_kline_series(
        series, start=start, stop=stop, volume=False, title="Raw selection"
    )
    selected = series[start:stop]

    assert isinstance(figure, plotly.Figure)
    assert len(figure.data) == 1
    candle = figure.data[0]
    assert candle.type == "candlestick"
    assert tuple(candle.x) == tuple(bar.timestamp for bar in selected)
    for field in ("open", "high", "low", "close"):
        assert tuple(getattr(candle, field)) == tuple(
            getattr(bar, field) for bar in selected
        )
    assert "yaxis2" not in figure.layout.to_plotly_json()
    assert "UTC" in figure.layout.xaxis.title.text
    assert figure.layout.xaxis.type == "category"
    assert tuple(figure.layout.xaxis.categoryarray) == tuple(
        bar.timestamp for bar in selected
    )
    assert figure.layout.title.text == "Raw selection"


@pytest.mark.parametrize("start,stop", [(0, 0), (3, 1), (100, None), (-100, -100)])
def test_empty_selections_are_rejected(
    series: KlineTSeries, start: int | None, stop: int | None
) -> None:
    with pytest.raises(ValueError, match="start|stop|slice|empty|bars"):
        series.plot(start=start, stop=stop)


def test_series_delegates_all_plot_options(
    series: KlineTSeries, monkeypatch: pytest.MonkeyPatch
) -> None:
    returned = object()
    calls: list[
        tuple[KlineTSeries, int | None, int | None, bool, str | None, bool, str]
    ] = []

    def helper(
        supplied: KlineTSeries,
        *,
        start: int | None = None,
        stop: int | None = None,
        volume: bool = True,
        title: str | None = None,
        show_gaps: bool = False,
        market: str = "US",
    ) -> object:
        calls.append((supplied, start, stop, volume, title, show_gaps, market))
        return returned

    monkeypatch.setattr(kline_plot, "plot_kline_series", helper)

    assert (
        series.plot(
            start=-3,
            stop=-1,
            volume=False,
            title="Detail",
            show_gaps=True,
            market="China",
        )
        is returned
    )
    assert calls == [(series, -3, -1, False, "Detail", True, "China")]


def test_raw_csv_and_helper_import_work_without_plotly(tmp_path: Path) -> None:
    """Exercise missing-extra behavior before any Plotly module can be cached."""
    script = """
import builtins
import sys
from datetime import UTC, datetime
from pathlib import Path

original_import = builtins.__import__
def without_plotly(name, *args, **kwargs):
    if name == 'plotly' or name.startswith('plotly.'):
        raise ModuleNotFoundError('Plotly intentionally unavailable', name=name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = without_plotly

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.data.kline_csv import read_kline_csv, write_kline_csv
from chanlab.visualization.kline_plot import plot_kline_series

assert not any(name == 'plotly' or name.startswith('plotly.') for name in sys.modules)
bar = Kline('TEST', '15m', 'fixture', datetime(2026, 1, 1, tzinfo=UTC),
            11.0, 13.0, 10.0, 12.0, 20.0)
series = KlineTSeries((bar,))
path = Path(sys.argv[1]) / 'raw.csv'
write_kline_csv(series, path)
restored, context = read_kline_csv(path)
assert restored.klines == series.klines and not context
for call in (lambda: series.plot(), lambda: plot_kline_series(series)):
    try:
        call()
    except ImportError as exc:
        assert 'uv sync --extra plot' in str(exc)
    else:
        raise AssertionError('Plotly absence was not reported')
"""
    root = Path(__file__).resolve().parents[1]
    environment = dict(
        os.environ, PYTHONPATH=str(root / "src"), PYTHONDONTWRITEBYTECODE="1"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
