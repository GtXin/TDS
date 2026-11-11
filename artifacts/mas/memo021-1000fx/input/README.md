# Fixed first1000FX input for memo021

Reproduce from repository root:

```sh
PYTHONPATH=src .venv/bin/python artifacts/mas/memo021-1000fx/input/prepare.py
```

- Preserved realCC sample:10060raw→6200merged→3027completeFX. SourceCSV/context and four algorithm files hashed before/after.
- Prefix selection: identify full-snapshot FX999's complete three-merged-bar window, cut raw at that window's final member stop, then independently rebuild. It gives3244raw→2040merged→exactly1000FX, FX0–999. Rebuilt merged and allFX equal the corresponding full-snapshot prefixes byte-field-for-field; neither Bi solve consumes any rawbar beyond3244. This is a fixed-snapshot prefix, not a promise of online/permanent upstream confirmation.
- Strong route:167pens, FX0→999. Weak route:239pens, FX0→999. All406selected pairs passed direct independent original-merged-range scans for the six Bi conditions, continuity and direction. Both exact routes also match historical1000FX scaling evidence.
- `summary.json`:counts, cut rule, timings, environment, protectedSHA256s and limitations.
- `bars.json`:prefix rawOHLCV and merged intervals/source ranges for charting.
- `fractals.json`:all1000FX with merged center/window, raw anchor/time/price and full three-window rawsupport.
- `bi-strong.json`, `bi-weak.json`:selected route plus each pen's source endpoint maps and geometric merged range. Every Bi remains `unconfirmed`, confirmed_at=None; these are selected fixed-snapshot inputs, not permanent final strokes.
- `checks.json`:actual check outcomes. Ruff passes; current .venv lacks mypy and Black, so their attempted checks are explicitly unavailable and no package install was performed.
- No xianduan recognizer or CC algorithm imported/executed. The parent task will determine the source-to-segment profile and chart validation.
