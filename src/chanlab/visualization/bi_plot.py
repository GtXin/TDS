"""Draw one explicitly selected stroke route over its immutable raw snapshot."""

from __future__ import annotations

from typing import Any

from chanlab.algo.bi import BiSeries


def plot_bi_series(series: BiSeries, **options: Any) -> Any:
    """Return an interactive figure, retaining segments crossing the viewport."""
    from plotly import graph_objects as go  # type: ignore[import-untyped]

    series.validate()
    fig = series.source_series.source_series.plot(**options)
    raw = series.source_series.source_series.source_series
    start, stop, _ = slice(options.get("raw_start"), options.get("raw_stop")).indices(
        len(raw)
    )
    gaps = options.get("show_gaps", False)
    up, down = (
        ("#16a34a", "#dc2626")
        if options.get("market", "US") == "US"
        else ("#dc2626", "#16a34a")
    )
    for p in series:
        a = series.source_series[p.start_fenxing_index].anchor_raw_index
        b = series.source_series[p.end_fenxing_index].anchor_raw_index
        if b < start or a >= stop:
            continue
        fig.add_trace(
            go.Scatter(
                x=[raw[i].timestamp if gaps else i - start for i in (a, b)],
                y=[p.start_price, p.end_price],
                mode="lines+markers",
                name=f"Bi{p.id} unconfirmed",
                line={
                    "color": up if p.direction == "up" else down,
                    "width": 3,
                    "dash": "dash" if p is series[-1] else "solid",
                },
            )
        )
    return fig
