"""Source-aligned interactive charts and renderer inputs for memo022."""

from __future__ import annotations

import html
import json
from itertools import pairwise
from typing import Any

import plotly.graph_objects as go  # type: ignore[import-untyped]
from plotly.offline import get_plotlyjs  # type: ignore[import-untyped]

from experiments.zhongshu022.run import MODES, OUT, save


def figure(
    data: dict[str, Any], source: dict[str, Any], title: str, start: int, stop: int
) -> Any:
    """Draw actual candles, endpoint chords and only genuinely located rectangles."""
    bars = source["raw"][start:stop]
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=[b["x"] for b in bars],
            open=[b["open"] for b in bars],
            high=[b["high"] for b in bars],
            low=[b["low"] for b in bars],
            close=[b["close"] for b in bars],
            increasing_line_color="#b91c1c",
            decreasing_line_color="#15803d",
            name="Raw OHLC",
            text=[b["utc"] for b in bars],
            hoverinfo="x+y+text",
        )
    )
    sx: list[float | None] = []
    sy: list[float | None] = []
    labels: list[str | None] = []
    for seg in data["segments"]:
        if seg["end_x"] < start or seg["start_x"] >= stop:
            continue
        sx.extend([seg["start_x"], seg["end_x"], None])
        sy.extend([seg["start_price"], seg["end_price"], None])
        label = f"XD{seg['id']} | source Bi[{seg['source_start']}:{seg['source_stop']}) | actual [{seg['low']},{seg['high']}]"
        labels.extend([label, label, None])
        fig.add_annotation(
            x=seg["end_x"],
            y=seg["end_price"],
            text=str(seg["id"]),
            showarrow=False,
            yshift=10 if seg["direction"] == 1 else -10,
            font={"size": 9, "color": "#334155"},
        )
    fig.add_trace(
        go.Scatter(
            x=sx,
            y=sy,
            mode="lines",
            line={"color": "#334155", "width": 2},
            text=labels,
            hovertemplate="%{text}<extra></extra>",
            name="Completed XD endpoint chords",
        )
    )
    for i, z in enumerate(data["result"]["centers"]):
        left, right = z["left"], z["right"]
        if left is None:
            continue
        if z["terminal"] is None:
            if left["x"] >= stop:
                continue
            # Open centers have no final right vertical border.
            for bound in sorted({z["low"], z["high"]}):
                fig.add_shape(
                    type="line",
                    x0=left["x"],
                    x1=stop - 1,
                    y0=bound,
                    y1=bound,
                    line={"color": "#b45309", "width": 1.5, "dash": "dot"},
                )
            fig.add_annotation(
                x=max(start, left["x"]),
                y=z["high"],
                text=f"Z{i} OPEN: right pending",
                showarrow=False,
                yshift=18,
                font={"color": "#b45309", "size": 10},
            )
            continue
        if right is None or right["x"] < start or left["x"] >= stop:
            continue
        if z["low"] == z["high"]:
            fig.add_shape(
                type="line",
                x0=left["x"],
                x1=right["x"],
                y0=z["low"],
                y1=z["high"],
                line={"color": "#2563eb", "width": 3},
            )
        else:
            fig.add_shape(
                type="rect",
                x0=left["x"],
                x1=right["x"],
                y0=z["low"],
                y1=z["high"],
                line={"color": "#2563eb", "width": 1.5},
                fillcolor="rgba(59,130,246,0.14)",
                layer="below",
            )
        fig.add_annotation(
            x=(max(start, left["x"]) + min(stop - 1, right["x"])) / 2,
            y=z["high"],
            text=f"Z{i}: XD{z['start']}–{z['terminal']}; confirm {z['confirmation']}",
            showarrow=False,
            yshift=16,
            font={"size": 10, "color": "#1d4ed8"},
        )
    fig.update_layout(
        title=title,
        xaxis_title="Raw bar position (gaps compressed)",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        xaxis_range=[start - 0.5, stop - 0.5],
        width=1700,
        height=780,
        template="plotly_white",
        hovermode="closest",
        legend={"orientation": "h", "y": 1.05},
        margin={"t": 110},
    )
    return fig


def run() -> None:
    """Write four-mode overview/detail atlases plus an exception table."""
    results = json.loads((OUT / "results.json").read_text())
    source = json.loads((OUT / "chart-source.json").read_text())
    charts = OUT / "charts"
    charts.mkdir(exist_ok=True)
    (charts / "plotly.min.js").write_text(get_plotlyjs())
    count = len(source["raw"])
    fx = source["fx"]
    cuts = [0] + [fx[i]["x"] for i in range(500, len(fx), 500)] + [count]
    windows = [("overview", 0, count)] + [
        (f"detail-{i+1:03d}", a, b) for i, (a, b) in enumerate(pairwise(cuts))
    ]
    manifest = []
    rows = []
    for mode in MODES:
        data = results[mode]
        for name, a, b in windows:
            title = f"{mode} | {name} | raw [{a},{b}) | ZS022 sequential rectangles"
            fig = figure(data, source, title, a, b)
            stem = f"{mode}_{name}"
            payload = {
                "mode": mode,
                "name": name,
                "start": a,
                "stop": b,
                "title": title,
                "segments": data["segments"],
                "centers": data["result"]["centers"],
            }
            save(charts / f"{stem}.plot.json", payload)
            fig.write_html(charts / f"{stem}.html", include_plotlyjs="plotly.min.js")
            (charts / f"{stem}.figure.json").write_text(fig.to_json())
            manifest.append(
                {
                    "mode": mode,
                    "window": name,
                    "raw_start": a,
                    "raw_stop": b,
                    "html": f"{stem}.html",
                    "png": f"{stem}.png",
                    "plot": f"{stem}.plot.json",
                }
            )
        for i, z in enumerate(data["result"]["centers"]):
            rows.append(
                f"<tr><td>{mode}</td><td>Z{i}</td><td>{z['start']}</td><td>{z['terminal']}</td>"
                f"<td>{z['confirmation']}</td><td>{z['low']}–{z['high']}</td>"
                f"<td>{html.escape(', '.join(z['diagnostics']) or ('located' if z['terminal'] is not None else 'open'))}</td></tr>"
            )
    special = results["bi-weak_xd-weak"]
    exception = special["result"]["centers"][0]
    diag = figure(
        special,
        source,
        "Geometry exception: XD0 chord cannot reach required entry G",
        0,
        400,
    )
    pen_x: list[float | None] = []
    pen_y: list[float | None] = []
    first_segment = special["segments"][0]
    for x0, y0, x1, y1 in special["pens"][
        first_segment["source_start"] : first_segment["source_stop"]
    ]:
        pen_x.extend([x0, x1, None])
        pen_y.extend([y0, y1, None])
    diag.add_scatter(
        x=pen_x,
        y=pen_y,
        mode="lines",
        line={"color": "#9333ea", "width": 2},
        name="XD0 actual source strokes",
    )
    for bound in (exception["low"], exception["high"]):
        diag.add_hline(y=bound, line_dash="dash", line_color="#9333ea")
    diag.write_html(
        charts / "geometry-exception.html", include_plotlyjs="plotly.min.js"
    )
    save(
        charts / "geometry-exception.plot.json",
        {
            "mode": "bi-weak_xd-weak",
            "name": "XD0 missing left crossing",
            "start": 0,
            "stop": 400,
            "segments": special["segments"],
            "centers": special["result"]["centers"],
            "diagnostic": True,
            "pens": special["pens"],
        },
    )
    save(charts / "manifest.json", manifest)
    links = "".join(
        f"<li><a href='{r['html']}'>{r['mode']} / {r['window']}</a></li>"
        for r in manifest
    )
    (charts / "index.html").write_text(
        """<!doctype html><meta charset="utf-8"><title>Memo022 real-data atlas</title>
<style>body{font:15px system-ui;max-width:1400px;margin:40px auto;padding:0 20px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #ddd}img{max-width:100%}</style>
<h1>Memo022 — real-data Zhongshu rectangles</h1><p>Fixed 031 segment snapshots; actual stroke extrema determine core prices. Straight segment chords locate borders. Missing intersections are reported, never filled in. Open centers have no final right border.</p>
<img src="comparison-overview.png"><p><a href="geometry-exception.html">Inspect the missing-left-crossing example</a></p><h2>Interactive charts</h2><ul>"""
        + links
        + """</ul><h2>Centers and geometry diagnostics</h2><table><tr><th>Mode</th><th>Center</th><th>Start</th><th>Terminal</th><th>Confirmation</th><th>Core</th><th>Geometry</th></tr>"""
        + "".join(rows)
        + "</table>"
    )
    for mode in MODES:
        covered: set[int] = set()
        for row in manifest:
            if row["mode"] == mode and row["window"] != "overview":
                covered.update(range(row["raw_start"], row["raw_stop"]))
        assert covered == set(range(count))
    print("Charts:", len(manifest), "all four mode raw coverage PASS", flush=True)


if __name__ == "__main__":
    run()
