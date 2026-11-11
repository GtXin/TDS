# Memo029 DP: first 200 CC-derived fractals

Run from repository root: `PYTHONPATH=src .venv/bin/python artifacts/mas/memo029-cc200/run.py`.

Uses preserved samples/chan_table CSV/context (CC provenance: references/proj009data/provenance.json), existing memo015 merged initialization UP and memo019 fractals. Only FX0–199 participate in optimization. Full history supplies upstream derivation; no later fractal participates in DP. Plots stop at FX199 raw anchor; its complete three-bar confirmation window extends beyond that anchor. Blue strokes are provisional DP geometry, not permanent confirmations or CC algorithm output. Existing raw/merged/fractal layers remain visible.

Strong: FX0→FX198,34 strokes; weak: FX0→FX198,48 strokes. Every selected stroke independently rechecked against raw merged-interval extrema; first12 real FX objective compared with all4096 endpoint subsets in each mode. This small-prefix comparison reuses the edge matrix and is not an independent implementation of pair legality. Source hashes unchanged; production untouched. result.json stores route positions, selected-pair evidence, provenance hashes and approximate local timings (not a benchmark). HTML plots embed Plotly for offline interaction.

Ruff check/format pass. Initial lint findings corrected then experiment rerun. Black and mypy were attempted but unavailable in .venv; no dependency installation or environment change. No visual screenshot QA or broad randomized/coverage test claimed. Full-source loading/derivation and plotting excluded from per-mode timing; edge enumeration,selected-route validation and small exhaustive check included.
