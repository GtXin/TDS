"""Optional Plotly rendering of raw Kline bars without modifying their values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chanlab.algo.kline import KlineTSeries

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-not-found]


def plot_kline_series(
    series: KlineTSeries,
    *,
    start: int | None = None,
    stop: int | None = None,
    volume: bool = True,
    title: str | None = None,
) -> Figure:
    """Build an interactive raw candlestick figure without display or export.

    Args:
        series: Immutable source bars with aware UTC timestamps.
        start: Inclusive bar index; negative indices follow Python slicing.
        stop: Exclusive bar index; omitted bounds select the full series.
        volume: Add a shared-time panel showing source-defined volume units.
        title: Optional title, defaulting to the symbol and period.

    Returns:
        A Plotly figure with unchanged OHLCV and a date axis retaining gaps.

    Raises:
        ValueError: The source is invalid or the selected slice is empty.
        ImportError: Plotly is unavailable; install with uv sync --extra plot.
    """
    series.validate()
    bars = series[start:stop]
    if not bars:
        raise ValueError("start/stop: the selected slice contains no bars")

    try:
        from plotly import graph_objects as go  # type: ignore[import-not-found]
        from plotly.subplots import make_subplots  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError(
            "Kline plotting requires Plotly; install it with `uv sync --extra plot`."
        ) from exc

    timestamps = [bar.timestamp for bar in bars]
    figure: Figure = make_subplots(
        rows=2 if volume else 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25] if volume else [1.0],
    )
    figure.add_trace(
        go.Candlestick(
            x=timestamps,
            open=[bar.open for bar in bars],
            high=[bar.high for bar in bars],
            low=[bar.low for bar in bars],
            close=[bar.close for bar in bars],
            name="OHLC",
        ),
        row=1,
        col=1,
    )
    figure.update_yaxes(title_text="Price", row=1, col=1)
    if volume:
        figure.add_trace(
            go.Bar(
                x=timestamps,
                y=[bar.volume for bar in bars],
                name="Volume",
                marker_color="#64748b",
            ),
            row=2,
            col=1,
        )
        figure.update_yaxes(title_text="Volume (source units)", row=2, col=1)

    # Date coordinates retain real elapsed time, including unfilled session gaps.
    figure.update_xaxes(type="date", rangeslider_visible=False)
    figure.update_xaxes(title_text="Time (UTC)", row=2 if volume else 1, col=1)
    figure.update_layout(
        title_text=(
            title if title is not None else f"{bars[0].symbol} · {bars[0].period}"
        ),
        template="plotly_white",
        height=700 if volume else 500,
        hovermode="x unified",
        showlegend=False,
    )
    return figure
