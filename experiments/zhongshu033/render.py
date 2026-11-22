"""Scientific PNG rendering from the exact native Plotly geometry arrays."""

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw

ROOT = Path("artifacts/mas/zhongshu-family/run033/charts")


def color(value, default="#334155"):
    if not value:
        return default
    if value.startswith("rgb"):
        parts = [float(x) for x in re.findall(r"[\d.]+", value)]
        return tuple(x / 255 for x in parts[:3]) + (
            (parts[3],) if len(parts) > 3 else ()
        )
    return value


def split_xy(x, y):
    paths = []
    path = []
    for a, b in zip(x, y):
        if a is None or b is None:
            if path:
                paths.append(path)
            path = []
        else:
            path.append((a, b))
    if path:
        paths.append(path)
    return paths


def draw(ax, row, compact=False):
    data = json.loads((ROOT / row["figure"]).read_text())
    layout = data["layout"]
    n = row["stop"] - row["start"]
    offset = row["start"]
    for trace in data["data"]:
        if trace.get("visible") == "legendonly":
            continue
        x = trace.get("x", [])
        y = trace.get("y", [])
        name = trace.get("name", "")
        if trace["type"] == "candlestick":
            up = "#dc2626"
            down = "#16a34a"
            cs = [up if c >= o else down for c, o in zip(trace["close"], trace["open"])]
            ax.add_collection(
                LineCollection(
                    [
                        [(a + offset, l), (a + offset, h)]
                        for a, l, h in zip(x, trace["low"], trace["high"])
                    ],
                    colors=cs,
                    linewidths=0.5,
                    alpha=0.65,
                    zorder=2,
                )
            )
            ax.add_collection(
                LineCollection(
                    [
                        [(a + offset, o), (a + offset, c)]
                        for a, o, c in zip(x, trace["open"], trace["close"])
                    ],
                    colors=cs,
                    linewidths=1.8,
                    alpha=0.85,
                    zorder=2,
                )
            )
            continue
        if trace["type"] != "scatter":
            continue
        paths = [[(a + offset, b) for a, b in p] for p in split_xy(x, y)]
        line = trace.get("line", {})
        c = color(line.get("color"))
        if trace.get("fill") == "toself":
            ax.add_collection(
                PolyCollection(
                    paths,
                    facecolors=color(trace.get("fillcolor"), "#dbeafe"),
                    edgecolors=c,
                    linewidths=0.25,
                    zorder=0,
                )
            )
        mode = trace.get("mode", "lines")
        if "lines" in mode:
            ax.add_collection(
                LineCollection(
                    paths,
                    colors=c,
                    linewidths=max(0.4, line.get("width", 1) * 0.6),
                    linestyles="dashed" if line.get("dash") == "dash" else "solid",
                    zorder=3,
                )
            )
        if "markers" in mode and x:
            marker = trace.get("marker", {})
            c = color(marker.get("color"))
            ax.scatter(
                [a + offset for a in x if a is not None],
                [b for b in y if b is not None],
                s=9 if compact else 16,
                c=[c],
                marker="v" if name == "top fractal" else "^",
                zorder=4,
            )
        if "text" in mode and not compact and n < 1000:
            for a, b, text in zip(x, y, trace.get("text", [])):
                if a is not None and 0 <= a < n:
                    ax.annotate(
                        text,
                        (a + offset, b),
                        xytext=(0, 7 if name == "top fractal" else -10),
                        textcoords="offset points",
                        fontsize=5.7,
                        ha="center",
                        clip_on=True,
                        color="#475569",
                    )
    for shape in layout.get("shapes", []):
        x0, x1 = shape["x0"] + offset, shape["x1"] + offset
        y0, y1 = shape["y0"], shape["y1"]
        ln = shape.get("line", {})
        if shape["type"] == "rect":
            ax.add_patch(
                Rectangle(
                    (x0, y0),
                    x1 - x0,
                    y1 - y0,
                    facecolor=(0.23, 0.51, 0.96, 0.13),
                    edgecolor=color(ln.get("color")),
                    linewidth=1.2,
                    zorder=1,
                )
            )
        else:
            ax.plot(
                [x0, x1],
                [y0, y1],
                color=color(ln.get("color")),
                linestyle=":" if ln.get("dash") == "dot" else "-",
                linewidth=1.2,
                zorder=3,
            )
    for ann in layout.get("annotations", []):
        if ann.get("xref") == "paper":
            ax.text(
                0.01,
                0.97,
                ann["text"],
                transform=ax.transAxes,
                va="top",
                fontsize=7,
                color="#b45309",
                bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
            )
        elif not compact and 0 <= ann["x"] < n and n < 1000:
            ax.annotate(
                ann["text"],
                (ann["x"] + offset, ann["y"]),
                xytext=(0, ann.get("yshift", 0) * 0.5),
                textcoords="offset points",
                fontsize=7 if ann["text"].startswith("ZS") else 6,
                ha=(
                    "left"
                    if ann["x"] < 5
                    else "right" if ann["x"] > n - 5 else "center"
                ),
                clip_on=True,
                color=color(ann.get("font", {}).get("color")),
            )
    candles = next(t for t in data["data"] if t["type"] == "candlestick")
    lo, hi = min(candles["low"]), max(candles["high"])
    pad = max((hi - lo) * 0.12, 2)
    ax.set_xlim(row["start"] - 0.5, row["stop"] - 0.5)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_title(
        row["mode"] + " / " + row["window"], loc="left", fontsize=10 if compact else 12
    )
    ax.set_ylabel("Price")
    ax.grid(alpha=0.15)
    ax.tick_params(labelsize=8)


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    for i, row in enumerate(manifest):
        fig, ax = plt.subplots(figsize=(16, 6.6), layout="constrained")
        draw(ax, row)
        ax.set_xlabel("Original raw bar position (calendar gaps compressed)")
        fig.suptitle(
            "Memo033 | raw + merged + all FX + Bi + XD + centers | blue: closed; amber dotted: open",
            fontsize=10,
        )
        fig.savefig(ROOT / row["png"], dpi=110)
        plt.close(fig)
        if i % 30 == 0:
            print("PNG", i, flush=True)
    for window in dict.fromkeys(r["window"] for r in manifest):
        rows = [r for r in manifest if r["window"] == window]
        fig, axes = plt.subplots(
            4, 1, figsize=(16, 12), sharex=True, sharey=True, layout="constrained"
        )
        for ax, row in zip(axes, rows):
            draw(ax, row, True)
        axes[-1].set_xlabel("Original raw bar position (calendar gaps compressed)")
        fig.suptitle(
            "Memo033 — " + window + " — default weak/weak at bottom", fontsize=13
        )
        fig.savefig(ROOT / f"comparison-{window}.png", dpi=110)
        plt.close(fig)
    contacts = ROOT / "contacts"
    contacts.mkdir(exist_ok=True)
    for i in range(0, len(manifest), 6):
        canvas = Image.new("RGB", (1800, 1160), "white")
        d = ImageDraw.Draw(canvas)
        for j, row in enumerate(manifest[i : i + 6]):
            with Image.open(ROOT / row["png"]) as im:
                im.thumbnail((900, 350))
                x = (j % 2) * 900
                y = (j // 2) * 385
                canvas.paste(im, (x, y + 25))
                d.text((x + 5, y + 5), row["mode"] + " " + row["window"], fill="black")
        canvas.save(contacts / f"sheet-{i//6+1:02d}.png")
    print(
        "Rendered",
        len(manifest),
        "individual figures and",
        len({r["window"] for r in manifest}),
        "comparisons",
        flush=True,
    )


if __name__ == "__main__":
    main()
