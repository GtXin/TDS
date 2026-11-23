"""Render complete five-level comparison windows from one full computation."""

from __future__ import annotations

import csv
import gzip
import html
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from compare import ROOT, signature
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw
from plotly.offline import get_plotlyjs
from plotly.subplots import make_subplots

DEST = ROOT / "charts"
LEVELS = ("raw", "mk", "fx", "bi", "xd")
COLORS = {"ours": "#2563eb", "kwx": "#d97706", "difference": "#dc2626"}


def load(name: str) -> Any:
    """Read a compressed result."""
    with gzip.open(ROOT / name, "rt") as stream:
        return json.load(stream)


def windows(count: int, width: int = 400, overlap: int = 20) -> list[tuple[int, int]]:
    """Cover every source bar with bounded overlapping viewports."""
    return [
        (a, min(a + width, count))
        for a in range(0, count, width - overlap)
        if a == 0 or a + overlap < count
    ]


def visible(record: dict[str, Any], kind: str, a: int, b: int) -> bool:
    """Include crossing segments even when both endpoints are off-screen."""
    if kind in ("mk", "fx"):
        return bool(record["raw_start"] < b and record["raw_stop"] > a)
    return bool(record["start_raw"] < b and record["end_raw"] >= a)


def geometry(
    records: list[dict[str, Any]], kind: str, a: int, b: int
) -> tuple[list[Any], list[Any], list[int]]:
    """Build exact absolute-source-coordinate paths, never recomputing a window."""
    x: list[Any] = []
    y: list[Any] = []
    ids = []
    for r in records:
        if not visible(r, kind, a, b):
            continue
        ids.append(r["id"])
        if kind == "mk":
            left, right = r["raw_start"] - 0.4, r["raw_stop"] - 0.6
            x.extend([left, right, right, left, left, None])
            y.extend([r["low"], r["low"], r["high"], r["high"], r["low"], None])
        elif kind == "fx":
            x.append(r["anchor"])
            y.append(r["price"])
        else:
            x.extend([r["start_raw"], r["end_raw"], None])
            y.extend([r["start_price"], r["end_price"], None])
    return x, y, ids


def paths(x: list[Any], y: list[Any]) -> list[list[tuple[float, float]]]:
    """Split the exact Plotly coordinate arrays for Matplotlib."""
    result: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    for a, b in zip(x, y, strict=True):
        if a is None:
            if current:
                result.append(current)
            current = []
        else:
            current.append((a, b))
    if current:
        result.append(current)
    return result


def render(
    raw: list[dict[str, Any]],
    own: dict[str, list[dict[str, Any]]],
    foreign: dict[str, list[dict[str, Any]]],
    key: str,
    bounds: tuple[int, int],
    stem: Path,
    levels: tuple[str, ...] = LEVELS,
    unavailable: bool = False,
) -> dict[str, Any]:
    """Write interactive and PNG panels from identical absolute coordinates."""
    a, b = bounds
    overview = b - a > 1000
    titles = [
        f"{level.upper()} — blue: ours; orange dashed: KWX; red: unmatched ours"
        for level in levels
    ]
    if unavailable and "xd" in levels:
        titles[levels.index("xd")] += " — OUR FULL XD INCOMPLETE (resource limit)"
    fig = make_subplots(
        rows=len(levels),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.035,
        subplot_titles=titles,
    )
    static, axes = plt.subplots(
        len(levels), 1, figsize=(18, 2.7 * len(levels)), sharex=True, squeeze=False
    )
    lo = min(r["low"] for r in raw[a:b])
    hi = max(r["high"] for r in raw[a:b])
    pad = max((hi - lo) * 0.06, 0.5)
    proof: dict[str, Any] = {}
    for index, kind in enumerate(levels, 1):
        ax = axes[index - 1, 0]
        ax.set_title(titles[index - 1], fontsize=9, loc="left")
        ax.set_ylim(lo - pad, hi + pad)
        ax.grid(alpha=0.18)
        if kind == "raw":
            bars = raw[a:b]
            xs = list(range(a, b))
            if overview:
                fig.add_trace(
                    go.Scattergl(
                        x=xs,
                        y=[r["close"] for r in bars],
                        name="raw close (OHLC preserved)",
                        mode="lines",
                        line={"color": "#475569", "width": 1},
                    ),
                    row=index,
                    col=1,
                )
                ax.vlines(
                    xs,
                    [r["low"] for r in bars],
                    [r["high"] for r in bars],
                    color="#94a3b8",
                    linewidth=0.3,
                )
                ax.plot(xs, [r["close"] for r in bars], color="#475569", linewidth=0.5)
            else:
                fig.add_trace(
                    go.Candlestick(
                        x=xs,
                        open=[r["open"] for r in bars],
                        high=[r["high"] for r in bars],
                        low=[r["low"] for r in bars],
                        close=[r["close"] for r in bars],
                        name="raw OHLC (identical inputs)",
                        increasing_line_color="#dc2626",
                        decreasing_line_color="#16a34a",
                    ),
                    row=index,
                    col=1,
                )
                cs = ["#dc2626" if r["close"] >= r["open"] else "#16a34a" for r in bars]
                ax.add_collection(
                    LineCollection(
                        [[(x, r["low"]), (x, r["high"])] for x, r in zip(xs, bars)],
                        colors=cs,
                        linewidths=0.5,
                    )
                )
                ax.add_collection(
                    PolyCollection(
                        [
                            [
                                (x - 0.3, r["open"]),
                                (x + 0.3, r["open"]),
                                (x + 0.3, r["close"]),
                                (x - 0.3, r["close"]),
                            ]
                            for x, r in zip(xs, bars)
                        ],
                        facecolors=cs,
                        edgecolors=cs,
                        linewidths=0.5,
                    )
                )
            proof[kind] = {"raw_start": a, "raw_stop": b, "count": b - a}
        else:
            common = {signature(r, kind) for r in foreign[kind]}
            proof[kind] = {}
            for source, records in (("kwx", foreign[kind]), ("ours", own[kind])):
                x, y, ids = geometry(records, kind, a, b)
                color = COLORS[source]
                proof[kind][source] = {
                    "ids": ids,
                    "coordinate_count": sum(v is not None for v in x),
                }
                if kind == "fx":
                    fig.add_trace(
                        go.Scattergl(
                            x=x,
                            y=y,
                            mode="markers",
                            marker={
                                "size": 5 if source == "ours" else 9,
                                "color": color,
                                "symbol": (
                                    "circle" if source == "ours" else "circle-open"
                                ),
                            },
                            name=f"{source} {kind}",
                        ),
                        row=index,
                        col=1,
                    )
                    ax.scatter(
                        x,
                        y,
                        s=7 if source == "ours" else 20,
                        color=color,
                        facecolors="none" if source == "kwx" else color,
                        linewidths=0.6,
                    )
                else:
                    fig.add_trace(
                        go.Scattergl(
                            x=x,
                            y=y,
                            mode="lines",
                            line={
                                "color": color,
                                "width": 1.2,
                                "dash": "dash" if source == "kwx" else "solid",
                            },
                            name=f"{source} {kind}",
                        ),
                        row=index,
                        col=1,
                    )
                    ax.add_collection(
                        LineCollection(
                            paths(x, y),
                            colors=color,
                            linewidths=0.7 if kind == "mk" else 1,
                            linestyles="dashed" if source == "kwx" else "solid",
                            alpha=0.8,
                        )
                    )
            unmatched = [r for r in own[kind] if signature(r, kind) not in common]
            dx, dy, ids = geometry(unmatched, kind, a, b)
            if dx:
                fig.add_trace(
                    go.Scattergl(
                        x=dx,
                        y=dy,
                        mode="markers" if kind == "fx" else "lines",
                        marker={"color": COLORS["difference"], "size": 6},
                        line={"color": COLORS["difference"], "width": 1.5},
                        name=f"unmatched ours {kind}",
                    ),
                    row=index,
                    col=1,
                )
                if kind == "fx":
                    ax.scatter(dx, dy, s=12, color=COLORS["difference"])
                else:
                    ax.add_collection(
                        LineCollection(
                            paths(dx, dy), colors=COLORS["difference"], linewidths=1.1
                        )
                    )
            proof[kind]["unmatched_ours_ids"] = ids
            if kind == "xd" and unavailable:
                ax.text(
                    0.5,
                    0.92,
                    "No full native XD result — resource limit; KWX shown for reference",
                    transform=ax.transAxes,
                    ha="center",
                    fontsize=9,
                    color="#b91c1c",
                )
        fig.update_yaxes(range=[lo - pad, hi + pad], row=index, col=1)
    axes[-1, 0].set_xlim(a - 0.8, b - 0.2)
    axes[-1, 0].set_xlabel("Absolute raw Kline position; trading gaps compressed")
    label = f"{key} | raw [{a}, {b}) | {raw[a]['timestamp']} to {raw[b-1]['timestamp']}"
    static.suptitle(label, fontsize=10)
    static.tight_layout(rect=(0, 0, 1, 0.98))
    static.savefig(stem.with_suffix(".png"), dpi=100)
    plt.close(static)
    fig.update_layout(
        title=label,
        height=300 * len(levels) + 80,
        width=1800,
        showlegend=True,
        hovermode="closest",
        template="plotly_white",
    )
    fig.update_xaxes(range=[a - 0.8, b - 0.2], rangeslider_visible=False)
    fig.write_html(
        stem.with_suffix(".html"), include_plotlyjs="../plotly.min.js", full_html=True
    )
    return {
        "key": key,
        "levels": list(levels),
        "start": a,
        "stop": b,
        "png": str(stem.with_suffix(".png").relative_to(DEST)),
        "html": str(stem.with_suffix(".html").relative_to(DEST)),
        "proof": proof,
    }


def contacts(manifest: list[dict[str, Any]]) -> list[str]:
    """Make readable contact sheets for exhaustive page review."""
    files = []
    for start in range(0, len(manifest), 12):
        chunk = manifest[start : start + 12]
        sheet = Image.new("RGB", (1800, 1700), "white")
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(chunk):
            with Image.open(DEST / row["png"]) as source:
                source.thumbnail((590, 390))
                x, y = (i % 3) * 600, (i // 3) * 420
                sheet.paste(source, (x, y + 22))
                draw.text(
                    (x + 4, y + 3),
                    f"{row['key']} [{row['start']},{row['stop']})",
                    fill="black",
                )
        name = f"contact-{start // 12 + 1:03}.jpg"
        sheet.save(DEST / name, quality=85)
        files.append(name)
    return files


def main() -> None:
    """Build full-range and complete-window comparison atlases."""
    DEST.mkdir(exist_ok=True)
    (DEST / "plotly.min.js").write_text(get_plotlyjs())
    with (ROOT / "roundtrip/raw.csv").open() as stream:
        raw = list(csv.DictReader(stream))
    for row in raw:
        for field in ("open", "high", "low", "close", "volume"):
            row[field] = float(row[field])
    kwx, upstream = load("kwx-normalized.json.gz"), load("upstream.json.gz")
    manifest = []
    all_windows = [(0, len(raw))] + windows(len(raw))
    for bm in ("strong", "weak"):
        bi = load(f"bi-{bm}.json.gz")["records"]
        for xm in ("strong", "weak"):
            key = f"bi-{bm}_xd-{xm}"
            path = ROOT / f"{key}.json.gz"
            xd = load(path.name)["records"] if path.exists() else []
            own = {"mk": upstream["mk"], "fx": upstream["fx"], "bi": bi, "xd": xd}
            folder = DEST / key
            folder.mkdir(exist_ok=True)
            for i, bounds in enumerate(all_windows):
                name = "overview" if i == 0 else f"page-{i:03}"
                row = render(
                    raw,
                    own,
                    kwx,
                    key,
                    bounds,
                    folder / name,
                    unavailable=not path.exists(),
                )
                manifest.append(row)
                if i % 10 == 0:
                    print(key, i, "/", len(all_windows), flush=True)
                (DEST / "manifest.json").write_text(json.dumps(manifest))
            for level in LEVELS:
                manifest.append(
                    render(
                        raw,
                        own,
                        kwx,
                        key,
                        (0, len(raw)),
                        folder / f"level-{level}-overview",
                        levels=(level,),
                        unavailable=not path.exists(),
                    )
                )
            pages = "".join(
                f'<li><a href="{Path(r["html"]).name}">raw [{r["start"]},{r["stop"]}) — {html.escape("/".join(r["levels"]))}</a> · <a href="{Path(r["png"]).name}">PNG</a></li>'
                for r in manifest
                if r["key"] == key
            )
            (folder / "index.html").write_text(
                f"<h1>{key}</h1><p>Exact full-snapshot geometry clipped to windows; no window recomputation. Blue=ours, orange dashed=KWX, red=unmatched ours. Confirmation policies differ.</p><ul>{pages}</ul>"
            )
    sheets = contacts(manifest)
    (DEST / "manifest.json").write_text(json.dumps(manifest))
    (DEST / "contacts.json").write_text(json.dumps(sheets))
    links = "".join(
        f'<p><a href="bi-{bm}_xd-{xm}/index.html">Bi {bm} / XD {xm}</a></p>'
        for bm, xm in (
            ("strong", "strong"),
            ("strong", "weak"),
            ("weak", "strong"),
            ("weak", "weak"),
        )
    )
    (DEST / "index.html").write_text(
        "<h1>Memo034 — full KWX dataset comparison</h1><p>44,375 raw bars; default weak/weak is last. Per-level overviews and complete 400-bar / 20-overlap detail windows. Counts and limitations are in the run report.</p>"
        + links
    )
    print("completed", len(manifest), "PNG/HTML pairs", flush=True)


if __name__ == "__main__":
    main()
