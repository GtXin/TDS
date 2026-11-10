"""Optional rendering of merged intervals over unchanged source candles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from chanlab.visualization.kline_plot import plot_kline_series

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-untyped]

    from chanlab.algo.merged_kline import MergedKlineSeries


def plot_merged_kline_series(
    series: MergedKlineSeries,
    *,
    start: int | None = None,
    stop: int | None = None,
    volume: bool = True,
    title: str | None = None,
) -> Figure:
    """Select merged positions without recalculation and return an undisplayed Figure."""
    series.validate()
    bars = series[start:stop]
    if not bars:
        raise ValueError("start/stop: selected merged slice is empty")
    figure = plot_kline_series(
        series.source_series,
        start=bars[0].source_start,
        stop=bars[-1].source_stop,
        volume=volume,
        title=title,
    )
    from plotly import graph_objects as go  # type: ignore[import-untyped]

    for direction, color in (("up", "#2563eb"), ("down", "#ea580c"), (None, "#64748b")):
        x = []
        y = []
        labels = []
        for bar in bars:
            if bar.direction != direction:
                continue
            timestamp = series.source_series[bar.source_start].timestamp
            label = (
                f"MK{bar.id} · raw[{bar.source_start}:{bar.source_stop}] "
                f"· {bar.direction} · {bar.status}"
            )
            x.extend([timestamp, timestamp, None])
            y.extend([bar.low, bar.high, None])
            labels.extend([label, label, label])
        if x:
            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    text=labels,
                    mode="lines+markers",
                    line={"color": color, "width": 4},
                    marker={"size": 5},
                    name=f"Merged {direction}",
                    hovertemplate="%{text}<br>%{y}<extra></extra>",
                ),
                row=1,
                col=1,
            )
    figure.update_layout(showlegend=True)
    return figure
