"""Interactive merged ranges and original candles with optional calendar spacing."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plotly.graph_objects import Figure  # type: ignore[import-untyped]

    from chanlab.algo.merged_kline import MergedKlineSeries


def plot_merged_kline_series(
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
) -> Figure:
    """Return an interactive view of precomputed records without display/export.

    Args:
        series: Completed result retaining its exact immutable raw source.
        start: Inclusive merged-record position (normal Python slicing).
        stop: Exclusive merged-record position.
        raw_start: Optional inclusive raw viewport position, instead of start/stop.
        raw_stop: Optional exclusive raw viewport position.
        volume: Include original raw volume in a separate aligned panel.
        title: Optional chart title.
        style: Overlay filled ranges behind candles, panels, or legacy ranges.
        show_gaps: False for consecutive bars; True for original calendar time.

    Returns:
        Figure with source timestamps on hover and source-aware merged ranges.

    Raises:
        ValueError: Empty selection, conflicting selectors or invalid options.
        ImportError: Plotly is absent; install the existing plot extra.
    """
    series.validate()
    if style not in ("overlay", "panels", "ranges"):
        raise ValueError("style: choose overlay, panels or ranges")
    if type(show_gaps) is not bool or type(volume) is not bool:
        raise ValueError("show_gaps/volume: expected bool")
    raw = series.source_series
    use_raw = raw_start is not None or raw_stop is not None
    if use_raw:
        if start is not None or stop is not None:
            raise ValueError("raw_start/raw_stop cannot be combined with start/stop")
        first, end, _ = slice(raw_start, raw_stop).indices(len(raw))
        selected = tuple(
            b for b in series if b.source_stop > first and b.source_start < end
        )
    else:
        selected = series[start:stop]
        first, end = (
            (selected[0].source_start, selected[-1].source_stop) if selected else (0, 0)
        )
    bars = raw[first:end]
    if not bars or not selected:
        raise ValueError("start/stop: selected slice contains no bars")
    try:
        from plotly import graph_objects as go  # type: ignore[import-untyped]
        from plotly.subplots import make_subplots  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "Merged plotting requires Plotly; install `uv sync --extra plot`."
        ) from exc

    split = style == "panels"
    price_rows = 2 if split else 1
    rows = price_rows + int(volume)
    heights = (
        ([0.43, 0.40, 0.17] if volume else [0.52, 0.48])
        if split
        else ([0.78, 0.22] if volume else [1.0])
    )
    figure: Figure = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.09 if split else 0.035,
        row_heights=heights,
        subplot_titles=(
            (
                f"Original K-lines · {len(bars)} recorded bars",
                f"Merged K-lines · {len(selected)} price intervals",
            )
            if split
            else None
        ),
    )
    timestamps = [b.timestamp for b in bars]
    positions = timestamps if show_gaps else list(range(len(bars)))
    # Calendar bands use a small observed-bar-width padding; source times are unchanged.
    delta = (
        min(
            (b.timestamp - a.timestamp for a, b in zip(raw.klines, raw.klines[1:])),
            default=timedelta(minutes=1),
        )
        if show_gaps
        else timedelta(0)
    )
    raw_hover = [
        f"{b.timestamp:%Y-%m-%d %H:%M:%S UTC}<br>raw[{first+i}]<br>Open {b.open:g} · High {b.high:g}<br>Low {b.low:g} · Close {b.close:g}"
        for i, b in enumerate(bars)
    ]
    merged_row = 2 if split else 1
    for direction, color, fill in (
        ("up", "#2563eb", "rgba(37,99,235,0.10)"),
        ("down", "#ea580c", "rgba(234,88,12,0.10)"),
        (None, "#64748b", "rgba(100,116,139,0.10)"),
    ):
        x: list[Any] = []
        y: list[float | None] = []
        labels: list[str | None] = []
        for bar in selected:
            if bar.direction != direction:
                continue
            left_index, right_index = (
                max(first, bar.source_start),
                min(end, bar.source_stop) - 1,
            )
            clipped = (
                left_index != bar.source_start or right_index + 1 != bar.source_stop
            )
            label = (
                f"MK{bar.id} · raw[{bar.source_start}:{bar.source_stop}) · {bar.direction} · {bar.status}"
                f"<br>Merged low {bar.low:g} / high {bar.high:g}"
                f"<br>{raw[bar.source_start].timestamp:%Y-%m-%d %H:%M UTC} → {raw[bar.source_stop-1].timestamp:%Y-%m-%d %H:%M UTC}"
                + ("<br>Display clipped at viewport edge" if clipped else "")
            )
            if style == "ranges":
                anchor = raw[left_index].timestamp if show_gaps else left_index - first
                x.extend([anchor, anchor, None])
                y.extend([bar.low, bar.high, None])
                labels.extend([label, label, None])
            else:
                left = (
                    raw[left_index].timestamp - delta * 0.42
                    if show_gaps
                    else left_index - first - 0.42
                )
                right = (
                    raw[right_index].timestamp + delta * 0.42
                    if show_gaps
                    else right_index - first + 0.42
                )
                x.extend([left, right, right, left, left, None])
                y.extend([bar.low, bar.low, bar.high, bar.high, bar.low, None])
                labels.extend([label] * 5 + [None])
        if x:
            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    text=labels,
                    mode="lines+markers" if style == "ranges" else "lines",
                    fill=None if style == "ranges" else "toself",
                    fillcolor=fill,
                    line={"color": color, "width": 4 if style == "ranges" else 1.6},
                    marker={"size": 5},
                    name=f"Merged {direction}"
                    + ("" if style == "ranges" else " · low–high"),
                    legendgroup=f"merged-{direction}",
                    hovertemplate="%{text}<extra></extra>",
                ),
                row=merged_row,
                col=1,
            )
    # Draw candles after the bands so raw bodies/wicks stay readable in overlay mode.
    figure.add_trace(
        go.Candlestick(
            x=positions,
            open=[b.open for b in bars],
            high=[b.high for b in bars],
            low=[b.low for b in bars],
            close=[b.close for b in bars],
            text=raw_hover,
            hoverinfo="text",
            customdata=[b.timestamp.isoformat() for b in bars],
            name="Original K-lines",
            increasing={
                "line": {"color": "#15803d", "width": 1.8},
                "fillcolor": "#86d7a2",
            },
            decreasing={
                "line": {"color": "#b91c1c", "width": 1.8},
                "fillcolor": "#efa1a1",
            },
        ),
        row=1,
        col=1,
    )
    if volume:
        figure.add_trace(
            go.Bar(
                x=positions,
                y=[b.volume for b in bars],
                text=raw_hover,
                hovertemplate="%{text}<br>Volume %{y}<extra></extra>",
                name="Raw volume",
                marker_color="#64748b",
            ),
            row=rows,
            col=1,
        )
        figure.update_yaxes(title_text="Volume (source units)", row=rows, col=1)
    low = min(b.low for b in bars + selected)
    high = max(b.high for b in bars + selected)
    margin = max((high - low) * 0.08, 1)
    for row in range(1, price_rows + 1):
        figure.update_yaxes(
            title_text="Price", range=[low - margin, high + margin], row=row, col=1
        )
    if show_gaps:
        figure.update_xaxes(type="date", rangeslider_visible=False)
    else:
        count = min(9, len(bars))
        ticks = (
            [round(i * (len(bars) - 1) / (count - 1)) for i in range(count)]
            if count > 1
            else [0]
        )
        figure.update_xaxes(
            type="linear",
            range=[-0.9, len(bars) - 0.1],
            tickmode="array",
            tickvals=ticks,
            ticktext=[bars[i].timestamp.strftime("%b %d<br>%H:%M") for i in ticks],
            rangeslider_visible=False,
        )
    figure.update_xaxes(
        title_text=(
            "Time (UTC)"
            if show_gaps
            else "Observed bars in source order · UTC labels · time gaps hidden"
        ),
        row=rows,
        col=1,
    )
    figure.update_layout(
        template="plotly_white",
        height=(920 if volume else 850) if split else (820 if volume else 720),
        title_text=(
            title
            if title is not None
            else f"{bars[0].symbol} · {bars[0].period} · Raw and merged K-lines"
        ),
        margin={"l": 85, "r": 40, "t": 125, "b": 100},
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0,
            "y": 1.07,
            "groupclick": "togglegroup",
        },
        meta={
            "style": style,
            "show_gaps": show_gaps,
            "raw_start": first,
            "raw_stop": end,
            "merged_count": len(selected),
        },
    )
    return figure
