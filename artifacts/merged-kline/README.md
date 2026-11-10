# Merged Kline samples
Generated from memo015’s10-bar worked example and the existing10060-row sample (6200 merged intervals). Real chart selects the last40 calculated merged intervals and corresponding raw extent without recomputation. Blue/orange/gray range marks mean up/down/unresolved; each mark is positioned at the first raw member’s timestamp. Candles and volume remain raw; session gaps are retained.

- `worked-example.html` / `.png`:10 raw→3 merged.
- `cc-last40-merged.html` / `.png`: real data, UP explicitly requested; optional raw volume.

HTML files are standalone interactive charts. Both PNGs inspected: readable axes/titles, source-aligned range marks and no clipping. Large real-time gaps are intentional. PNG export initially failed under sandbox Chrome, then succeeded with broader execution permission; subsequent sandbox reproduction again reports export failure while preserving the successful PNGs.

Reproduce from repo root with `PYTHONPATH=src python artifacts/mas/merged-kline-family/verify.py` in an environment with pytest/Plotly. Optional PNG export additionally needs Kaleido and local Chrome. These export tools are temporary and are not added to project dependencies. Full evidence: `artifacts/mas/merged-kline-family/verification.json`.
