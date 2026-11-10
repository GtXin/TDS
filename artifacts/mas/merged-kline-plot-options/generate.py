"""Reproduce approved figures using the public class method (no duplicate renderer)."""

from pathlib import Path
from hashlib import sha256
import json

from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

root = Path(__file__).resolve().parents[3]
sample = root / "samples/chan_table"
paths = [next(sample.glob("*chan_table*.csv")), next(sample.glob("*context*.csv"))]
hashes = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in paths}
raw = KlineTSeries.read_csv(*paths)
rule = root / "docs/memo/memoWX_015_Chan_mergedkline.md"
merged = MergedKlineSeries.derive_from(
    raw,
    {"initialization": "UP"},
    "memo015:sha256:" + sha256(rule.read_bytes()).hexdigest(),
)
assert isinstance(merged, MergedKlineSeries)
out = root / "artifacts/merged-kline"
report = {
    "source_hashes": hashes,
    "raw_count": len(raw),
    "merged_count": len(merged),
    "samples": {},
}
for stem, options in (
    ("cc-last40-overlay-gapfree", {}),
    ("cc-last40-raw-and-merged-gapfree", {"style": "panels"}),
    ("cc-last40-overlay-calendar", {"show_gaps": True}),
    ("cc-last40-overlay-china", {"market": "China"}),
):
    fig = merged.plot(raw_start=-40, volume=False, **options)
    candle = next(t for t in fig.data if t.type == "candlestick")
    assert list(candle.high) == [b.high for b in raw[-40:]]
    assert fig.layout.meta["merged_count"] == 26 and len(candle.x) == 40
    assert len(raw.context) == 9
    market = options.get("market", "US")
    up, down = ("#16a34a", "#dc2626") if market == "US" else ("#dc2626", "#16a34a")
    assert candle.increasing.line.color == candle.increasing.fillcolor == up
    assert candle.decreasing.line.color == candle.decreasing.fillcolor == down
    for trace in fig.data:
        if trace.type == "scatter":
            expected = (
                up
                if trace.legendgroup == "merged-up"
                else down if trace.legendgroup == "merged-down" else "#64748b"
            )
            assert trace.line.color == expected
    fig.write_html(out / f"{stem}.html", include_plotlyjs=True)
    fig.write_image(
        out / f"{stem}.png",
        width=1440,
        height=720 if options.get("style") != "panels" else 920,
        scale=1.5,
    )
    report["samples"][stem] = {
        "options": dict(raw_start=-40, volume=False, **options),
        "metadata": fig.layout.meta,
        "png_sha256": sha256((out / f"{stem}.png").read_bytes()).hexdigest(),
    }
assert hashes == {
    str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in paths
}
(root / "artifacts/mas/merged-kline-plot-options/verification.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps(report, indent=2))
