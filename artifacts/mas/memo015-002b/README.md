# Memo015002.b worked examples

Synthetic teaching data and finite arithmetic supporting the requested memo section. The inputs are not market records or CC outputs. Original Kline/KlineTSeries validate the constructed raw candles; the local replay is a documentation calculation, not the proposed MergedKline implementation or a general correctness test.

- `build_examples.py`: reproduce calculations and figures from fixed low/high intervals. Raw open/close, UTC timestamps and volume are synthetic; only low/high enter the merge arithmetic.
- `examples.json`: exact raw fields, per-step states and results for the main sequence, initialization paths and sequential-comparison counterexample.
- `verification.json`: executed finite checks and their limits; no default initializer, warning metric or confirmation rule selected.
- `documentation-verification.json`: exact memo-scope/backup checks and copied-picture SHA-256 values.
- `figures/`: PNG and SVG originals of the two inspected figures; the matching PNGs are copied beside memo015 for Obsidian.

Executed using the existing neighboring Project009 environment, with no installation or dependency/configuration changes:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src MPLCONFIGDIR=/tmp/tds-memo015-mpl XDG_CACHE_HOME=/tmp/tds-memo015-cache /Users/coder/Public/EngineGit/proj009/.venv/bin/python artifacts/mas/memo015-002b/build_examples.py
```

Run from the TDS repository root. The script writes only this artifact folder; it does not update the memo or its companion pictures. Other Python environments with matplotlib and the TDS source can run it with the same inputs. Rendering used matplotlib3.11.1 and Arial Unicode MS; the renderer fell back to regular weight for bold text. Both PNGs were inspected for readable labels, source alignment and populated lower panels.

The main example checks9 transitions; three initialization paths check9 transitions; the sequential counterexample checks3 transitions. Single-bar, repeated one-price equality and unspecified-initialization cases are checked separately. Source ranges are zero-based half-open intervals, price ranges are closed intervals, and raw input immutability is checked for completed replays. Independent reviewers also check memo arithmetic and state/interface wording in the associated task record.
