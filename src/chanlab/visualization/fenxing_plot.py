"""Fractal anchors on the existing source-preserving merged/raw visualization."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-untyped]

    from chanlab.algo.fenxing import FenxingSeries


def plot_fenxing_series(
    series: FenxingSeries,
    *,
    raw_start: int | None = None,
    raw_stop: int | None = None,
    volume: bool = True,
    title: str | None = None,
    show_gaps: bool = False,
    market: Literal["US", "China"] = "US",
) -> Figure:
    """Keep actual extreme anchors separate from merged display placement."""
    series.validate()
    fig = series.source_series.plot(
        raw_start=raw_start,
        raw_stop=raw_stop,
        volume=volume,
        title=title or "Geometric fractals — unconfirmed",
        show_gaps=show_gaps,
        market=market,
    )
    raw = series.source_series.source_series
    start, stop, _ = slice(raw_start, raw_stop).indices(len(raw))
    from plotly import graph_objects as go  # type: ignore[import-untyped]

    up_color, down_color = (
        ("#16a34a", "#dc2626") if market == "US" else ("#dc2626", "#16a34a")
    )
    for kind, symbol, color in [
        ("top", "triangle-down", down_color),
        ("bottom", "triangle-up", up_color),
    ]:
        points = [
            p for p in series if p.kind == kind and start <= p.anchor_raw_index < stop
        ]
        fig.add_trace(
            go.Scatter(
                name=f"{kind} fractal",
                mode="markers",
                x=[
                    (
                        raw[p.anchor_raw_index].timestamp
                        if show_gaps
                        else p.anchor_raw_index - start
                    )
                    for p in points
                ],
                y=[p.price for p in points],
                marker={
                    "symbol": symbol,
                    "color": color,
                    "size": 13,
                    "line": {"color": "white", "width": 1},
                },
                customdata=[
                    [
                        p.id,
                        p.anchor_raw_index,
                        p.source_start,
                        p.source_stop,
                        raw[p.anchor_raw_index].timestamp.isoformat(),
                        p.status,
                    ]
                    for p in points
                ],
                hovertemplate="FX%{customdata[0]} "
                + kind
                + "<br>raw anchor=%{customdata[1]}<br>merged window=[%{customdata[2]},%{customdata[3]})<br>%{customdata[4]}<br>price=%{y}<br>%{customdata[5]}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    return fig
