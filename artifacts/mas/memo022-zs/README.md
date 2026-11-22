# Memo022 sequential Zhongshu validation

This run implements the user's memo022 rules: earliest consecutive three completed-segment overlap, fixed actual-source price core, first directional departure whose immediately adjacent completed reverse segment does not return, then restart at that confirming segment. Boundary touch is return. Zero-height centers are accepted. Geometry uses original endpoint chords; absent intersections are reported without changing the structural sequence or inventing coordinates.

Source: 10,060 raw 15-minute bars, 2024-10-28 05:45 through 2026-08-19 06:45 UTC. The four memo031 completed Xianduan contexts are reloaded and source-validated; new Zhongshu results are recomputed. This is not a claim that upstream selection was freshly rerun, nor an online walk-forward backtest. `baseline-hashes.json` preserves exact raw/context/spec/source hashes.

| Bi / XD | Segments | Closed structures | Located rectangles | Open | Geometry exceptions |
|---|---:|---:|---:|---:|---:|
| strong / strong | 53 | 8 | 8 | 0 | 0 |
| strong / weak | 57 | 8 | 8 | 0 | 0 |
| weak / strong | 79 | 11 | 11 | 1 | 0 |
| weak / weak | 89 | 14 | 13 | 1 | 1 |

Weak/weak Z0: actual core[3005,3083], start XD0, terminal XD2, confirmation XD3. XD0's full source range is[2952,3116], while its endpoint chord is3026→3005. It cannot intersect required entry3083. `left_crossing_missing` is retained; this closed structure is not counted as a located rectangle. See the [diagnostic](charts/geometry-exception.html).

[Interactive atlas](charts/index.html) contains32 regular PNG/HTML charts (overview+7 complete windows per mode),8 four-row comparison PNGs and one exception PNG/HTML. Every mode covers all10,060 raw rows. Open-core horizontal lines do not invent a final right border. Diagram x uses raw-bar positions with calendar gaps compressed; UTC intersection times are geometric interpolation between endpoints, not observed trades or new K-lines.

## Implementation and evidence

- Shared scanner: [core](../../../src/chanlab/algo/_zhongshu_scan.py), [source adapter](../../../src/chanlab/algo/_zhongshu_input.py).
- `results.json`: projected source segments, s/e/q, cores, crossings, evidence times, all seed/ending decisions and unformed ranges.
- `validation.json`: four-mode counts,278 source-extrema checks,282 fixed-completed-segment-prefix independent comparisons,83 exact-rational crossing checks and3×100-call scan timings. The timings exclude source restoration, upstream selection, independent audit and plotting.
- `chart-audit.json`:32 serialized figures,112 geometric primitives, candle/chord equality, full coverage and absent open right borders.
- `coverage.json`: scanner100%, adapter95%, combined159/160 statements; `regression.txt`:472active tests pass; `focused-tests.txt`:33directed/random/source tests pass. Random verification uses500fixed-seed paths and their reflection/positive affine transformations,1500routes total.
- `quality.json`, `implementation-hashes.json`, `visual-review.json`: completed check metadata and exact reviewed artifacts.
- Zero-height behavior is tested synthetically; no zero-height center occurred in this real sample. Source segment completion is a fixed-snapshot statement; no permanently frozen future labels are asserted.

## Reproduce from repository root

Python3.11+, repository `.venv` with pytest/Plotly; scientific PNG rendering additionally needs Matplotlib/Pillow. This run reused `/Users/coder/Public/EngineGit/proj009/.venv/bin/python` for Matplotlib/Pillow. Black/mypy/coverage were installed into isolated `/private/tmp/tds022-tools` without changing project dependencies.

```sh
PYTHONPATH=src:. .venv/bin/python -m pytest -q tests/test_zhongshu_scan.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu022/run.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu022/plot.py
MPLCONFIGDIR=/private/tmp/tds022-mpl /Users/coder/Public/EngineGit/proj009/.venv/bin/python experiments/zhongshu022/render.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu022/audit_charts.py
PYTHONPATH=src:. .venv/bin/python -m pytest -q tests
```

Validation source: `experiments/zhongshu022/reference.py` enumerates all seeds and endings before selecting the route and solves chord intersections using rational line equations. The scanner does not call that reference. `run.py` also compares every projected actual range against its source merged-bar interval and checks original sample OHLC equality.

No existing source module, raw dataset, memo029/030/031 or original/CC appendix was changed. Only the new scanner/adapter are shared algorithm code; there is no new API, ChanTable registration or website integration in this task.
