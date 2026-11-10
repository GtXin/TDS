"""Plot given processed intervals and fractal centers, without preprocessing."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

folder = Path(__file__).resolve().parent
data = json.loads((folder / "examples.json").read_text())
bars = data["merged_groups"]
points = data["default_first"]["items"]
expected = []
for i in range(1, len(bars) - 1):
    a, b, c = bars[i - 1], bars[i], bars[i + 1]
    top = b[0] > max(a[0], c[0]) and b[1] > max(a[1], c[1])
    bottom = b[0] < min(a[0], c[0]) and b[1] < min(a[1], c[1])
    if top or bottom:
        expected.append((i, "top" if top else "bottom", b[1] if top else b[0]))
assert expected == [(p["source_start"] + 1, p["kind"], p["price"]) for p in points]
assert expected == [(1, "top", 6), (3, "bottom", 0), (5, "top", 6)]

fig, ax = plt.subplots(figsize=(11, 5))
for i, (low, high, start, stop) in enumerate(bars):
    ax.add_patch(Rectangle((i - .22, low), .44, high - low,
                           facecolor="#e2e8f0", edgecolor="#64748b", linewidth=1.5))
    ax.vlines(i, low, high, color="#64748b", linewidth=1)
for p in points:
    center, price = p["source_start"] + 1, p["price"]
    top = p["kind"] == "top"
    color = "#7c3aed" if top else "#0369a1"
    ax.scatter(center, price, marker="v" if top else "^", color=color,
               edgecolors="white", linewidth=.7, s=90, zorder=5)
    ax.annotate(f"FX{p['id']} {p['kind']}={price:g}\nraw anchor R{p['anchor_raw_index']}",
                (center, price), xytext=(0, 16 if top else -16),
                textcoords="offset points", ha="center", va="bottom" if top else "top",
                color=color, fontsize=10,
                arrowprops={"arrowstyle": "-", "lw": .8, "color": color})
ax.set_xticks(range(7), [f"M{i}" for i in range(7)])
ax.set_xlim(-.65, 6.65)
ax.set_ylim(-2.25, 8.25)
ax.set_ylabel("Price")
ax.set_xlabel("Processed-bar position (equal spacing; not original time duration)")
ax.set_title("Given 7 processed intervals -> 3 geometric fractals", fontsize=14, pad=15)
ax.grid(axis="y", color="#e2e8f0", zorder=0)
ax.spines[["top", "right"]].set_visible(False)
fig.text(.5, .023, "Markers sit at processed centers M1/M3/M5; raw anchor indices are labels only. Synthetic example.",
          ha="center", fontsize=9, color="#475569")
fig.subplots_adjust(left=.08, right=.98, top=.86, bottom=.16)
fig.savefig(folder / "fractal-window-example.png", dpi=150)
print("Given 7 processed intervals: centers 1/3/5; anchors 2/5/8 verified.")
