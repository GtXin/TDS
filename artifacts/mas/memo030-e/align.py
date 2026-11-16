"""Prepare four-mode figures with matching scales per compact page."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
m = json.loads((ROOT / "charts/manifest.json").read_text())
dest = ROOT / "compact-sources"
dest.mkdir(exist_ok=True)
for stem in ["overview"] + [f"detail-{i:03d}" for i in range(1, 8)]:
    pages = [p for p in m if Path(p["png"]).stem == stem]
    figures = [
        json.loads((ROOT / "charts" / p["figure_json"]).read_text()) for p in pages
    ]
    lo = min(f["layout"]["yaxis"]["range"][0] for f in figures)
    hi = max(f["layout"]["yaxis"]["range"][1] for f in figures)
    for p, f in zip(pages, figures):
        f["layout"]["yaxis"]["range"] = [lo, hi]
        (dest / p["figure_json"]).parent.mkdir(parents=True, exist_ok=True)
        (dest / p["figure_json"]).write_text(json.dumps(f))
(dest / "manifest.json").write_text(json.dumps(m))
