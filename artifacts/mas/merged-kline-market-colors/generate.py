"""Render palette-matched US/China samples with the public merged plot method."""

from pathlib import Path
from hashlib import sha256
from datetime import UTC, datetime, timedelta
import json
import runpy

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

root = Path(__file__).resolve().parents[3]
runpy.run_path(
    str(root / "artifacts/mas/merged-kline-plot-options/generate.py"),
    run_name="__main__",
)
out = root / "artifacts/merged-kline"
raw = KlineTSeries.read_csv(
    next((root / "samples/chan_table").glob("*chan_table*.csv")),
    next((root / "samples/chan_table").glob("*context*.csv")),
)
merged = MergedKlineSeries.derive_from(
    raw, {"initialization": "UP"}, "memo015:palette-check"
)
assert isinstance(merged, MergedKlineSeries)
intervals = [
    (1, 3),
    (2, 4),
    (1, 5),
    (3, 5),
    (3, 6),
    (1, 5),
    (2, 4),
    (0, 6),
    (0, 4),
    (0, 5),
]
worked = KlineTSeries(
    Kline(
        "Worked",
        "1m",
        "memo015",
        datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
        lo,
        hi,
        lo,
        hi,
        1,
    )
    for i, (lo, hi) in enumerate(intervals)
)
result = MergedKlineSeries.derive_from(
    worked, {"initialization": "UP"}, "memo015:002.b"
)
assert isinstance(result, MergedKlineSeries)
for stem, fig, height in (
    (
        "worked-example",
        result.plot(
            volume=False,
            style="panels",
            title="Memo015 worked example · 10 raw bars → 3 merged intervals · US colors",
        ),
        850,
    ),
    ("cc-last40-merged", merged.plot(start=-40, style="ranges", show_gaps=True), 820),
):
    fig.write_html(out / f"{stem}.html", include_plotlyjs=True)
    fig.write_image(out / f"{stem}.png", width=1440, height=height, scale=1.5)

report = json.loads(
    (root / "artifacts/mas/merged-kline-plot-options/verification.json").read_text()
)
report["market_default"] = "US"
report["presets"] = {
    "US": {"up": "#16a34a", "down": "#dc2626"},
    "China": {"up": "#dc2626", "down": "#16a34a"},
}
# Same data/geometry for both presets; only palette and descriptive metadata differ.
us = merged.plot(raw_start=-40, volume=False)
cn = merged.plot(raw_start=-40, volume=False, market="China")
for a, b in zip(us.data, cn.data, strict=True):
    assert tuple(a.x) == tuple(b.x)
    if a.type == "candlestick":
        for name in ("open", "high", "low", "close", "customdata"):
            assert tuple(getattr(a, name)) == tuple(getattr(b, name))
    else:
        assert tuple(a.y) == tuple(b.y)
protected = json.loads(
    (
        root / "artifacts/mas/merged-kline-market-colors/protected-hashes.json"
    ).read_text()
)
assert all(
    sha256((root / k).read_bytes()).hexdigest() == v for k, v in protected.items()
)
report["protected_hashes_unchanged"] = True
report["same_geometry_ohlc_both_presets"] = True
report["all_png_hashes"] = {
    p.name: sha256(p.read_bytes()).hexdigest() for p in out.glob("*.png")
}
(root / "artifacts/mas/merged-kline-market-colors/verification.json").write_text(
    json.dumps(report, indent=2)
)
print(
    "Palette assertions, shared-geometry and protected-data checks passed; six PNG/HTML pairs exported."
)
