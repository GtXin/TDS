"""Center rectangles over the complete native source visualization."""

from __future__ import annotations

from typing import Any

from chanlab.algo.zhongshu import ZhongshuSeries


def plot(series: ZhongshuSeries, **options: Any) -> Any:
    """Keep genuine chord crossings; never invent missing or open right edges."""
    raw = series.source_series.source_series.source_series.source_series.source_series
    # Normalize raw windows once for upstream overlays and center coordinates.
    n = len(raw)
    start, stop = options.get("raw_start"), options.get("raw_stop")
    for value in (start, stop):
        if value is not None and type(value) is not int:
            raise ValueError("raw bounds must be integers")
    start = 0 if start is None else max(0, n + start) if start < 0 else min(n, start)
    stop = n if stop is None else max(0, n + stop) if stop < 0 else min(n, stop)
    if start >= stop:
        raise ValueError("nonempty raw window required")
    options = {**options, "raw_start": start, "raw_stop": stop}
    fig = series.source_series.plot(**options)
    gaps = options.get("show_gaps", False)

    def coord(cross: Any) -> Any:
        return cross.time if gaps else cross.x - start

    for z in series:
        g = z.geometry
        left, right = g.left, g.right
        if g.diagnostics:
            if z.end_raw_index >= start and z.start_raw_index < stop:
                fig.add_annotation(
                    x=0.01,
                    y=0.98
                    - 0.055
                    * sum(1 for a in fig.layout.annotations if a.xref == "paper"),
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    text=f"ZS{z.id}: {', '.join(g.diagnostics)}",
                    font={"color": "#b45309", "size": 10},
                )
            continue
        if left is None or left.x >= stop or (right is not None and right.x < start):
            continue
        if g.closed:
            assert right is not None
            fig.add_shape(
                type="line" if z.lower == z.upper else "rect",
                x0=coord(left),
                x1=coord(right),
                y0=z.lower,
                y1=z.upper,
                line={"color": "#2563eb", "width": 2},
                fillcolor="rgba(59,130,246,0.13)",
                layer="below",
                name=f"ZS{z.id}",
            )
        else:
            for bound in sorted({z.lower, z.upper}):
                fig.add_shape(
                    type="line",
                    x0=coord(left),
                    x1=raw[stop - 1].timestamp if gaps else stop - 1 - start,
                    y0=bound,
                    y1=bound,
                    line={"color": "#b45309", "dash": "dot", "width": 2},
                    name=f"ZS{z.id} open",
                )
        fig.add_annotation(
            x=coord(left) if left.x >= start else raw[start].timestamp if gaps else 0,
            y=z.upper,
            text=f"ZS{z.id} {z.status}",
            showarrow=False,
            yshift=14,
            font={"size": 10, "color": "#2563eb" if g.closed else "#b45309"},
        )
    return fig
