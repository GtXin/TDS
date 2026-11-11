# Bi DP029 execution evidence

Production algorithm: `src/chanlab/algo/bi.py`; fixed-snapshot strong/weak only. Reports follow memo027; contracts009 and algorithm029. Historical rolling/candidate evidence is separate.

- `regression.txt`, `focused.txt`, `coverage.txt`, `mypy.txt`, `black.txt`, `ruff.txt`: actual source checks.
- `comparison.json`: isolated baseline/continuation imports, hashes and400 common outputs.
- `monte-carlo.json`:10000 generated rawOHLCV inputs in both modes, independent all-endpoint reference and5377 exhaustive short inputs per mode. Empty routes reported separately; no differences.
- `scaling.json`: realCC100/1000/3000FX prefixes, three runs per mode, direct independent reference; timings exclude file loading and reference. PeakRSS is process cumulative.
- `full-result.json`:10060raw/6200merged/3027FX; strong480/weak682, both reachFX3026; source hashes and table roundtrip.
- `index.html`:112 HTML/PNG pages, allraw/allFX/all selectedBi covered. `atlas-check.json` machine audit; `visual-review.json` actual all-page review. Dense static labels may overlap; use HTML zoom/hover.

Reproduce from repository root with Python3.11 and project dependencies:

```sh
PYTHONPATH=src .venv/bin/python artifacts/mas/bi-dp029/verify.py
PYTHONPATH=src .venv/bin/python artifacts/mas/bi-dp029/scaling.py
PYTHONPATH=src .venv/bin/python artifacts/mas/bi-dp029/full_atlas.py
python artifacts/mas/bi-dp029/render_png.py
swift -module-cache-path /private/tmp/tds-swift-cache artifacts/mas/bi-dp029/contact_sheets.swift
PYTHONPATH=src .venv/bin/python artifacts/mas/bi-dp029/check_atlas.py
```

PNG rendering requires Plotly/Kaleido and Chrome; the completed run used `/private/tmp/tds-memo026-tools/bin/python`. Swift contact sheets use macOS AppKit. Regeneration resets visual flags until a new visual review. Before-integration files and frozen implementations retained. No commit created.
