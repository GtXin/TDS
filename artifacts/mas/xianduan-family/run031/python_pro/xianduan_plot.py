"""Segment overlays on the complete existing Bi source visualization."""

from typing import Any

from chanlab.algo.xianduan import XianduanSeries


def plot(series: XianduanSeries, **options: Any) -> Any:
    """Keep all source geometry; windows only clip display, never recalculate."""
    import plotly.graph_objects as go  # type: ignore[import-untyped]

    fig = series.source_series.plot(**options)
    bi = series.source_series
    fx = bi.source_series
    raw = fx.source_series.source_series
    for i, (a, b) in enumerate(
        [(x.source_start, x.source_stop) for x in series] + list(series.tail)
    ):
        left = fx[bi[a].start_fenxing_index].anchor_raw_index
        right = fx[bi[b - 1].end_fenxing_index].anchor_raw_index
        confirmed = i < len(series)
        start = options.get("raw_start", 0) or 0
        stop = options.get("raw_stop", len(raw)) or len(raw)
        if right < start or left >= stop:
            continue
        fig.add_trace(
            go.Scatter(
                x=[
                    raw[k].timestamp if options.get("show_gaps", False) else k - start
                    for k in (left, right)
                ],
                y=[bi[a].start_price, bi[b - 1].end_price],
                mode="lines+markers",
                name=f"XD{i}" if confirmed else f"candidate{i-len(series)}",
                line={
                    "color": "#9c27b0" if confirmed else "#777777",
                    "width": 4,
                    "dash": "solid" if confirmed else "dash",
                },
                customdata=[left, right],
            )
        )
    return fig
