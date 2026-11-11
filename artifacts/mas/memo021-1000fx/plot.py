"""Offline real-data atlas for the isolated XD-P1 experiment, not CC output."""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

import plotly.graph_objects as go  # type: ignore[import-untyped]
from plotly.offline import get_plotlyjs  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "input"
CHARTS = ROOT / "charts"


def read_json(path: Path) -> Any:
    """Read one local experiment artifact."""
    return json.loads(path.read_text())


def point(pens: list[dict[str, Any]], position: int) -> dict[str, Any]:
    """Resolve XD endpoint position to the true source Bi anchor."""
    if not pens or not 0 <= position <= len(pens):
        raise ValueError(f"invalid Bi endpoint position {position}")
    return pens[position]["start"] if position < len(pens) else pens[-1]["end"]


def intersects(start: int, end: int, raw_start: int, raw_stop: int) -> bool:
    """Keep crossing intervals intact; the x-axis clips their display."""
    return end >= raw_start and start < raw_stop


def make_figure(
    bars: dict[str, Any],
    fractals: list[dict[str, Any]],
    pens: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    mode: str,
    merged_start: int,
    merged_stop: int,
    overview: bool,
) -> tuple[Any, dict[str, Any]]:
    """Draw a source-aligned window without recalculating any selected route."""
    merged = bars["merged"]
    raw_start = merged[merged_start]["source_start"]
    raw_stop = merged[merged_stop - 1]["source_stop"]
    raw = bars["raw"][raw_start:raw_stop]
    raw_x = [bar["index"] for bar in raw]
    figure = go.Figure()
    mx: list[float | None] = []
    my: list[float | None] = []
    mtext: list[str | None] = []
    for bar in merged[merged_start:merged_stop]:
        left, right = bar["source_start"] - 0.4, bar["source_stop"] - 0.6
        # Floats are valid axis coordinates; the lists remain explicit JSON arrays.
        mx.extend([left, left, right, right, left, None])
        my.extend([bar["low"], bar["high"], bar["high"], bar["low"], bar["low"], None])
        label = f"MK{bar['index']} raw[{bar['source_start']}:{bar['source_stop']})<br>{bar['low']}–{bar['high']}"
        mtext.extend([label] * 5 + [None])
    figure.add_trace(
        go.Scatter(
            x=mx,
            y=my,
            mode="lines",
            fill="toself",
            fillcolor="rgba(100,116,139,0.10)",
            line={"color": "rgba(100,116,139,0.35)", "width": 0.6},
            name="Merged ranges",
            text=mtext,
            hovertemplate="%{text}<extra></extra>",
            meta={"kind": "merged"},
        )
    )
    figure.add_trace(
        go.Candlestick(
            x=raw_x,
            open=[bar["open"] for bar in raw],
            high=[bar["high"] for bar in raw],
            low=[bar["low"] for bar in raw],
            close=[bar["close"] for bar in raw],
            increasing_line_color="#dc2626",
            decreasing_line_color="#16a34a",
            increasing_fillcolor="#dc2626",
            decreasing_fillcolor="#16a34a",
            name="Raw OHLC (China colors)",
            text=[bar["utc"] for bar in raw],
            hoverinfo="x+y+text",
            meta={"kind": "raw"},
        )
    )
    visible_fx = [p for p in fractals if raw_start <= p["anchor_raw_index"] < raw_stop]
    visible_pens = [
        pen
        for pen in pens
        if intersects(
            pen["start"]["anchor_raw_index"],
            pen["end"]["anchor_raw_index"],
            raw_start,
            raw_stop,
        )
    ]
    visible_xd = [
        (index, state)
        for index, state in enumerate(selected)
        if intersects(
            point(pens, state["i"])["anchor_raw_index"],
            point(pens, state["j"])["anchor_raw_index"],
            raw_start,
            raw_stop,
        )
    ]
    key_fx = {
        pen[side]["fx_position"] for pen in visible_pens for side in ("start", "end")
    }
    key_fx.update(
        point(pens, state[side])["fx_position"]
        for _, state in visible_xd
        for side in ("i", "j")
    )
    for kind, color, symbol, text_position in (
        ("top", "#15803d", "triangle-down", "top center"),
        ("bottom", "#b91c1c", "triangle-up", "bottom center"),
    ):
        subset = [p for p in visible_fx if p["kind"] == kind]
        figure.add_trace(
            go.Scatter(
                x=[p["anchor_raw_index"] for p in subset],
                y=[p["price"] for p in subset],
                mode="markers+text" if not overview else "markers",
                marker={"color": color, "size": 6, "symbol": symbol},
                text=[
                    f"FX{p['fx_position']}" if p["fx_position"] in key_fx else ""
                    for p in subset
                ],
                textposition=text_position,
                textfont={"size": 10, "color": color},
                name=f"{kind.title()} FX (all)",
                customdata=[
                    [p["fx_position"], p["merged_center"], p["anchor_utc"]]
                    for p in subset
                ],
                hovertemplate="FX%{customdata[0]} · MK%{customdata[1]}<br>raw%{x} · %{customdata[2]}<br>%{y}<extra></extra>",
                meta={"kind": "fx", "type": kind},
                cliponaxis=True,
            )
        )
    bx: list[int | None] = []
    by: list[float | None] = []
    bi_data: list[list[Any] | None] = []
    for pen in visible_pens:
        bx.extend(
            [pen["start"]["anchor_raw_index"], pen["end"]["anchor_raw_index"], None]
        )
        by.extend([pen["start"]["price"], pen["end"]["price"], None])
        details = [
            pen["pen_position"],
            pen["start"]["fx_position"],
            pen["end"]["fx_position"],
            pen["direction"],
        ]
        bi_data.extend([details, details, None])
    figure.add_trace(
        go.Scatter(
            x=bx,
            y=by,
            mode="lines",
            line={"color": "#64748b", "width": 1.3},
            name=f"Bi029 {mode} (snapshot)",
            customdata=bi_data,
            hovertemplate="Bi%{customdata[0]} · FX%{customdata[1]}→FX%{customdata[2]} · %{customdata[3]}<br>raw%{x} · %{y}<extra></extra>",
            meta={"kind": "bi"},
        )
    )
    endpoint_labels: dict[int, dict[str, Any]] = {}
    roles = sorted({str(state.get("role", "primary")) for _, state in visible_xd})
    for role in roles:
        sx: list[int | None] = []
        sy: list[float | None] = []
        certificate_data: list[list[Any] | None] = []
        for index, state in visible_xd:
            if str(state.get("role", "primary")) != role:
                continue
            left, right = point(pens, state["i"]), point(pens, state["j"])
            h = state.get("h", state.get("dep_endpoint"))
            h_raw = None if h is None else point(pens, h)["anchor_raw_index"]
            details = [
                index,
                state["i"],
                state["j"],
                state.get("kind", ""),
                role,
                h,
                h_raw,
                state.get("parent_id"),
                state.get("dep_pen"),
            ]
            sx.extend([left["anchor_raw_index"], right["anchor_raw_index"], None])
            sy.extend([left["price"], right["price"], None])
            certificate_data.extend([details, details, None])
            if not overview:
                for endpoint, name in ((left, "start"), (right, "end")):
                    if raw_start <= endpoint["anchor_raw_index"] < raw_stop:
                        label_entry = endpoint_labels.setdefault(
                            endpoint["fx_position"], {"point": endpoint, "labels": []}
                        )
                        label_entry["labels"].append(
                            (index, "S" if name == "start" else "E")
                        )
        figure.add_trace(
            go.Scatter(
                x=sx,
                y=sy,
                mode="lines+markers",
                line={
                    "color": "#7c3aed" if role == "primary" else "#ea580c",
                    "width": 3.5,
                },
                marker={"size": 7, "symbol": "circle-open"},
                name=f"XD-P1 completed · {role}",
                customdata=certificate_data,
                hovertemplate="XD%{customdata[0]} · Bi[%{customdata[1]}:%{customdata[2]})<br>%{customdata[3]} · %{customdata[4]}<br>evidence P%{customdata[5]} / raw%{customdata[6]} / pen%{customdata[8]}<br>parent=%{customdata[7]}<extra></extra>",
                meta={"kind": "xd", "role": role},
            )
        )
    for label_entry in endpoint_labels.values():
        endpoint = label_entry["point"]
        figure.add_annotation(
            x=endpoint["anchor_raw_index"],
            y=endpoint["price"],
            text=" / ".join(
                f"XD{index} {side}" for index, side in sorted(label_entry["labels"])
            ),
            showarrow=False,
            yshift=26 if endpoint["kind"] == "top" else -26,
            font={"size": 11, "color": "#6d28d9"},
            bgcolor="rgba(255,255,255,0.75)",
        )
    if selected:
        last = max(selected, key=lambda state: state["j"])
        tail_start = point(pens, last["j"])["anchor_raw_index"]
    else:
        tail_start = 0
    if tail_start < raw_stop:
        figure.add_vrect(
            x0=max(tail_start, raw_start),
            x1=raw_stop - 0.5,
            fillcolor="rgba(245,158,11,0.08)",
            line_width=0,
            layer="below",
        )
        figure.add_annotation(
            x=max(tail_start, raw_start),
            y=1,
            xref="x",
            yref="paper",
            text="Open tail · no forced XD",
            showarrow=False,
            xanchor="left",
            yshift=8,
            font={"size": 11, "color": "#a16207"},
        )
    # Autoranging against offscreen endpoints would compress a detail page.
    # Include only line values actually intersecting this fixed viewport.
    visible_values = [value for bar in raw for value in (bar["low"], bar["high"])]
    x_min, x_max = raw_start - 0.8, raw_stop - 0.2
    source_lines = [(pen["start"], pen["end"]) for pen in visible_pens]
    source_lines.extend(
        (point(pens, state["i"]), point(pens, state["j"])) for _, state in visible_xd
    )
    for left, right in source_lines:
        left_x, right_x = left["anchor_raw_index"], right["anchor_raw_index"]
        for x in (max(left_x, x_min), min(right_x, x_max)):
            if left_x <= x <= right_x and x_min <= x <= x_max:
                fraction = (x - left_x) / (right_x - left_x)
                visible_values.append(
                    left["price"] + fraction * (right["price"] - left["price"])
                )
    visible_low, visible_high = min(visible_values), max(visible_values)
    padding = max(visible_high - visible_low, 1) * 0.08
    label = "overview" if overview else f"MK[{merged_start}:{merged_stop})"
    figure.update_layout(
        title={
            "text": f"XD-P1 experiment — {mode} input — {label}<br><sup>{len(fractals)} FX / {len(pens)} Bi / {len(selected)} selected XD · fixed snapshot; no permanent confirmation</sup>",
            "x": 0.02,
        },
        width=1800,
        height=900,
        template="plotly_white",
        margin={"t": 140, "b": 130, "l": 70, "r": 40},
        legend={"orientation": "h", "y": -0.13, "x": 0},
        hovermode="closest",
        xaxis={
            "title": "Observed raw-bar index · no calendar gaps",
            "rangeslider": {"visible": False},
            "range": [raw_start - 0.8, raw_stop - 0.2],
        },
        yaxis={
            "title": "Price",
            "fixedrange": False,
            "range": [visible_low - padding, visible_high + padding],
        },
        meta={
            "experiment": "XD-P1",
            "mode": mode,
            "source": "first1000FX fixed prefix",
            "not_cc_output": True,
        },
    )
    entry = {
        "mode": mode,
        "kind": "overview" if overview else "detail",
        "merged": [merged_start, merged_stop],
        "raw": [raw_start, raw_stop],
        "fx_positions": [p["fx_position"] for p in visible_fx],
        "bi_positions": [p["pen_position"] for p in visible_pens],
        "xd_positions": [index for index, _ in visible_xd],
        "open_tail_raw_start": tail_start,
    }
    return figure, entry


def main() -> None:
    """Generate both-mode offline HTML/JSON atlas and audit source coverage."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=ROOT / "results.json")
    args = parser.parse_args()
    results = read_json(args.results)
    bars = read_json(INPUT / "bars.json")
    fractals = read_json(INPUT / "fractals.json")
    assert len(fractals) == 1000
    CHARTS.mkdir(parents=True, exist_ok=True)
    (CHARTS / "plotly.min.js").write_text(get_plotlyjs())
    manifest = []
    mode_summaries = {}
    started = perf_counter()
    for mode in ("strong", "weak"):
        pens = read_json(INPUT / f"bi-{mode}.json")["pens"]
        selected = results["modes"][mode]["selected"]
        target = CHARTS / mode
        target.mkdir(exist_ok=True)
        windows = [(0, len(bars["merged"]), True)] + [
            (a, min(a + 200, len(bars["merged"])), False)
            for a in range(0, len(bars["merged"]), 180)
        ]
        rows = []
        for page, (a, b, overview) in enumerate(windows):
            stem = "overview" if overview else f"detail-{page:03d}"
            figure, entry = make_figure(
                bars, fractals, pens, selected, mode, a, b, overview
            )
            figure.write_html(
                target / f"{stem}.html", include_plotlyjs="../plotly.min.js"
            )
            (target / f"{stem}.figure.json").write_text(figure.to_json())
            entry.update(
                {
                    "page": page,
                    "html": f"{mode}/{stem}.html",
                    "figure_json": f"{mode}/{stem}.figure.json",
                    "png": f"{mode}/{stem}.png",
                    "visually_checked": False,
                }
            )
            manifest.append(entry)
            rows.append(
                f'<tr><td>{html.escape(stem)}</td><td>MK[{a}:{b})</td><td>raw[{entry["raw"][0]}:{entry["raw"][1]})</td><td><a href="{stem}.html">interactive</a> · <a href="{stem}.png">PNG</a></td></tr>'
            )
        (target / "index.html").write_text(
            '<!doctype html><meta charset="utf-8"><title>XD-P1 '
            + mode
            + "</title><h1>XD-P1 experiment — "
            + mode
            + " input</h1><p>Our isolated experimental profile, not CC output or proof of the original author’s unique division. Solid XD overlays are snapshot-completed within XD-P1; amber area is open tail. Every detail page is a viewport of one global calculation.</p><table>"
            + "".join(rows)
            + "</table><p>All FX markers are retained; details label Bi/XD endpoint FX only. Hover reveals every FX index and source time.</p>"
        )
        pages = [p for p in manifest if p["mode"] == mode and p["kind"] == "detail"]
        raw_coverage = {i for page in pages for i in range(*page["raw"])}
        merged_coverage = {i for page in pages for i in range(*page["merged"])}
        fx_coverage = {i for page in pages for i in page["fx_positions"]}
        bi_coverage = {i for page in pages for i in page["bi_positions"]}
        xd_coverage = {i for page in pages for i in page["xd_positions"]}
        assert raw_coverage == set(range(len(bars["raw"])))
        assert merged_coverage == set(range(len(bars["merged"])))
        assert fx_coverage == set(range(len(fractals)))
        assert bi_coverage == set(range(len(pens)))
        assert xd_coverage == set(range(len(selected)))
        for page in [p for p in manifest if p["mode"] == mode]:
            fig = read_json(CHARTS / page["figure_json"])
            actual_fx = {
                int(row[0])
                for trace in fig["data"]
                if trace.get("meta", {}).get("kind") == "fx"
                for row in trace["customdata"]
            }
            assert actual_fx == set(page["fx_positions"])
        mode_summaries[mode] = {
            "overview": 1,
            "detail_pages": len(pages),
            "raw_coverage": len(raw_coverage),
            "merged_coverage": len(merged_coverage),
            "fractal_coverage": len(fx_coverage),
            "bi_coverage": len(bi_coverage),
            "xd_coverage": len(xd_coverage),
            "xd_roles": dict(Counter(str(x.get("role", "primary")) for x in selected)),
        }
    (CHARTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (CHARTS / "coverage.json").write_text(
        json.dumps(
            {
                "modes": mode_summaries,
                "seconds": perf_counter() - started,
                "source_results": str(args.results),
                "png_rendered": False,
                "visual_qa": "pending",
            },
            indent=2,
        )
        + "\n"
    )
    (CHARTS / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><h1>XD-P1 experiment — first1000FX</h1><p>One fixed input snapshot; complete200merged windows with20merged overlap. Our experimental profile, not CC output. Each atlas retains raw OHLC, merged ranges, all1000FX, input Bi and selected XD.</p><p><a href="strong/index.html">Strong input atlas</a> · <a href="weak/index.html">Weak input atlas</a></p>'
    )
    print(json.dumps(mode_summaries, ensure_ascii=False))


if __name__ == "__main__":
    main()
