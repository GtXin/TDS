"""Render scientific PNG figures from the exact interactive-chart coordinates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib  # type: ignore[import-not-found]

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # type: ignore[import-not-found]
from matplotlib.collections import LineCollection  # type: ignore[import-not-found]
from matplotlib.patches import Rectangle  # type: ignore[import-not-found]
from PIL import Image, ImageDraw  # type: ignore[import-not-found]

ROOT = Path("artifacts/mas/memo022-zs")
CHARTS = ROOT / "charts"


def draw(
    ax: Any, info: dict[str, Any], raw: list[dict[str, Any]], compact: bool = False
) -> None:
    """Render each located rectangle and leave an open center's right side absent."""
    a, b = info["start"], info["stop"]
    bars = raw[a:b]
    up = "#b91c1c"
    down = "#15803d"
    wicks = [[(r["x"], r["low"]), (r["x"], r["high"])] for r in bars]
    colors = [up if r["close"] >= r["open"] else down for r in bars]
    ax.add_collection(LineCollection(wicks, colors=colors, linewidths=0.45, alpha=0.45))
    bodies = [
        [
            (r["x"] - 0.25, r["open"]),
            (r["x"] + 0.25, r["open"]),
            (r["x"] + 0.25, r["close"]),
            (r["x"] - 0.25, r["close"]),
        ]
        for r in bars
    ]
    # Vertical close-open strokes remain legible at dense overview scale.
    ax.add_collection(
        LineCollection(
            [[(r["x"], r["open"]), (r["x"], r["close"])] for r in bars],
            colors=colors,
            linewidths=1,
            alpha=0.45,
        )
    )
    del bodies
    for seg in info["segments"]:
        if seg["end_x"] < a or seg["start_x"] >= b:
            continue
        ax.plot(
            [seg["start_x"], seg["end_x"]],
            [seg["start_price"], seg["end_price"]],
            color="#334155",
            linewidth=1.2,
        )
        if not compact and b - a < 3000:
            ax.annotate(
                str(seg["id"]),
                (seg["end_x"], seg["end_price"]),
                xytext=(0, 7 if seg["direction"] == 1 else -10),
                textcoords="offset points",
                fontsize=7,
                ha="center",
                clip_on=True,
            )
    for i, z in enumerate(info["centers"]):
        left, right = z["left"], z["right"]
        if left is None:
            continue
        if z["terminal"] is None:
            if left["x"] >= b:
                continue
            for bound in sorted({z["low"], z["high"]}):
                ax.plot(
                    [left["x"], b - 1],
                    [bound, bound],
                    color="#b45309",
                    linestyle=":",
                    linewidth=1.4,
                )
            ax.annotate(
                f"Z{i} OPEN",
                (max(a, left["x"]), z["high"]),
                xytext=(4, 8),
                textcoords="offset points",
                color="#b45309",
                fontsize=8,
                clip_on=True,
            )
            continue
        if right is None or right["x"] < a or left["x"] >= b:
            continue
        if z["low"] == z["high"]:
            ax.plot(
                [left["x"], right["x"]],
                [z["low"], z["high"]],
                color="#2563eb",
                linewidth=2.5,
            )
        else:
            ax.add_patch(
                Rectangle(
                    (left["x"], z["low"]),
                    right["x"] - left["x"],
                    z["high"] - z["low"],
                    edgecolor="#2563eb",
                    facecolor="#93c5fd",
                    alpha=0.35,
                    linewidth=1.5,
                )
            )
        ax.annotate(
            f"Z{i}",
            ((max(a, left["x"]) + min(b - 1, right["x"])) / 2, z["high"]),
            xytext=(0, 7),
            textcoords="offset points",
            color="#1d4ed8",
            fontsize=8,
            ha="center",
            clip_on=True,
        )
    if info.get("diagnostic"):
        first = info["segments"][0]
        for x0, y0, x1, y1 in info["pens"][
            first["source_start"] : first["source_stop"]
        ]:
            ax.plot([x0, x1], [y0, y1], color="#9333ea", linewidth=1.7)
        center = info["centers"][0]
        for bound in (center["low"], center["high"]):
            ax.axhline(bound, color="#9333ea", linestyle="--", linewidth=1)
        ax.text(
            0.02,
            0.96,
            "Purple: actual source strokes / core bounds\nXD0 chord 3026 -> 3005 cannot reach entry G=3083",
            transform=ax.transAxes,
            va="top",
            fontsize=10,
            bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "none"},
        )
    low = min(r["low"] for r in bars)
    high = max(r["high"] for r in bars)
    pad = max((high - low) * 0.12, 2)
    ax.set_xlim(a - 0.5, b - 0.5)
    ax.set_ylim(low - pad, high + pad)
    ax.grid(alpha=0.15)
    ax.set_ylabel("Price")
    ax.set_title(
        info["mode"] + " / " + info["name"], loc="left", fontsize=10 if compact else 13
    )
    ax.tick_params(labelsize=8)


def run() -> None:
    """Generate all individual and four-row comparison figures, plus contacts."""
    raw = json.loads((ROOT / "chart-source.json").read_text())["raw"]
    manifest = json.loads((CHARTS / "manifest.json").read_text())
    for row in manifest:
        info = json.loads((CHARTS / row["plot"]).read_text())
        fig, ax = plt.subplots(figsize=(16, 6), layout="constrained")
        draw(ax, info, raw)
        ax.set_xlabel("Raw bar position (gaps compressed)")
        fig.suptitle(
            "Memo022 | blue: located center; dotted amber: open; missing crossings omitted",
            fontsize=11,
        )
        fig.savefig(CHARTS / row["png"], dpi=120)
        plt.close(fig)
    for window in dict.fromkeys(row["window"] for row in manifest):
        group = [r for r in manifest if r["window"] == window]
        fig, axes = plt.subplots(
            4, 1, figsize=(16, 12), sharex=True, sharey=True, layout="constrained"
        )
        for ax, row in zip(axes, group):
            draw(ax, json.loads((CHARTS / row["plot"]).read_text()), raw, True)
        axes[-1].set_xlabel("Raw bar position (gaps compressed)")
        fig.suptitle(
            "Memo022 — " + window + " — four upstream configurations", fontsize=14
        )
        fig.savefig(CHARTS / f"comparison-{window}.png", dpi=120)
        plt.close(fig)
    if (CHARTS / "geometry-exception.plot.json").exists():
        info = json.loads((CHARTS / "geometry-exception.plot.json").read_text())
        fig, ax = plt.subplots(figsize=(16, 6), layout="constrained")
        draw(ax, info, raw)
        ax.set_xlabel("Raw bar position (gaps compressed)")
        fig.savefig(CHARTS / "geometry-exception.png", dpi=120)
        plt.close(fig)
    contacts = CHARTS / "contacts"
    contacts.mkdir(exist_ok=True)
    for i in range(0, len(manifest), 4):
        canvas = Image.new("RGB", (1920, 760), "white")
        d = ImageDraw.Draw(canvas)
        for j, row in enumerate(manifest[i : i + 4]):
            im = Image.open(CHARTS / row["png"]).convert("RGB")
            im.thumbnail((960, 340))
            x = (j % 2) * 960
            y = (j // 2) * 380
            canvas.paste(im, (x, y + 25))
            d.text((x + 5, y + 5), row["mode"] + " " + row["window"], fill="black")
        canvas.save(contacts / f"sheet-{i//4+1:02d}.png")
    print("Rendered", len(manifest), "individual, 8 comparison, 8 contact figures")


if __name__ == "__main__":
    run()
