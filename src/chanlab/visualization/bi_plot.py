"""Memo029 selected route over raw/merged bars and every visible fractal."""

from __future__ import annotations

from typing import Any

from chanlab.algo.bi import BiSeries


def plot_bi_series(series: BiSeries, **options: Any) -> Any:
    """Draw exact endpoint positions, clipping the viewport without re-solving."""
    from plotly import graph_objects as go  # type: ignore[import-untyped]

    series.validate()
    fig = series.source_series.plot(**options)
    raw = series.source_series.source_series.source_series
    start, stop, _ = slice(options.get("raw_start"), options.get("raw_stop")).indices(
        len(raw)
    )
    gaps = options.get("show_gaps", False)
    colors = (
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
                mode="lines",
                name=f"Bi{p.id}",
                line={"color": colors[0 if p.direction == "up" else 1], "width": 2},
                customdata=[[p.id, p.start_fenxing_index, p.end_fenxing_index, a, b]]
                * 2,
                hovertemplate="Bi%{customdata[0]} FX%{customdata[1]}→FX%{customdata[2]}<br>raw[%{customdata[3]},%{customdata[4]}]<extra></extra>",
                showlegend=False,
            )
        )
    # Fractal labels use source positions; hover retains the upstream integer ID.
    for t in fig.data:
        if t.name in ("top fractal", "bottom fractal"):
            kind = "top" if t.name == "top fractal" else "bottom"
            points = [
                (i, f)
                for i, f in enumerate(series.source_series)
                if f.kind == kind and start <= f.anchor_raw_index < stop
            ]
            t.update(
                mode="markers+text",
                text=[f"FX{i}" for i, _ in points],
                textposition=[
                    ("top " if kind == "top" else "bottom ")
                    + (
                        "right"
                        if f.anchor_raw_index - start < 6
                        else "left" if stop - f.anchor_raw_index <= 6 else "center"
                    )
                    for _, f in points
                ],
                cliponaxis=False,
                textfont={"size": 9},
            )
    # Label stroke midpoints without moving true endpoint coordinates.
    for p in series:
        a = series.source_series[p.start_fenxing_index].anchor_raw_index
        b = series.source_series[p.end_fenxing_index].anchor_raw_index
        left, right = max(a, start), min(b, stop - 1)
        if left > right:
            continue
        mid = (left + right) / 2
        price = p.start_price + (p.end_price - p.start_price) * (mid - a) / (b - a)
        x = raw[int(mid)].timestamp if gaps else mid - start
        fig.add_annotation(
            x=x,
            y=price,
            text=f"Bi{p.id}",
            showarrow=False,
            font={"size": 10, "color": "#4338ca"},
            bgcolor="rgba(255,255,255,.7)",
            yshift=8,
        )
    fig.update_layout(
        title=options.get("title")
        or f'Bi DP — {series.config["distance_mode"]} — snapshot, unconfirmed'
    )
    return fig
