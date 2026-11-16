# Full-data XD030-A validation

Same trial policy as memo030-500fx/profile.md; no new recognition rules. Full preserved CSV/context rebuilt10060raw/6200merged/3027completeFX. All data used once per mode;500FX charts are viewports of one global solve, never restarted locally. Actual source hashes/environment/configuration in input/summary.json.

Reproduce from repository root:
```
PYTHONPATH=src .venv/bin/python artifacts/mas/memo030-full/input/prepare.py
.venv/bin/python artifacts/mas/memo030-full/run.py
.venv/bin/python artifacts/mas/memo030-full/plot.py
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/memo030-full/charts/render.swift artifacts/mas/memo030-full/charts
.venv/bin/python artifacts/mas/memo030-full/verify.py
```

run.py reuses only historical local recognizer and independent local reference, never old first-completion selectors. All173300pairs compared. Independent reverse DAG value recursion verifies final objective (not exhaustive paths). verify.py reconstructs all240087compatibility edges, checks selected connectivity, immutable source hashes and full chart source unions/exact500FX page membership. Upstream1162Bi independently scanned. Results:strong58XD FX0→2892,weak89XD FX0→2933; tails20/19pens open.

16PNG+16offlineHTML: twooverviews, sevenwindows per mode, FX0–499/500–999/1000–1499/1500–1999/2000–2499/2500–2999/3000–3026. Charts retain all raw OHLC/merged ranges/fractals/Bi/XD. Page sourceID audit in charts/render.json, coverage in charts/coverage.json. All16pages inspected in threecontacts, weakoverview fullresolution.500FX windows contain dense labels; use interactive hover/zoom for details.

Limitations unchanged: original-author equivalence, skipped internal completion boundaries, complex absorption and full context semantics are unresolved. Trial graph objective/certificate equality does not prove complete030algorithm correctness. Snapshot results can change with added data; no permanent confirmation. Ruffpasses; mypy/Black unavailable. No production/029/021/031/raw changes.
