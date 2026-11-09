# Kline family implementation plan
## 000 — Scope
Implement `Kline` and `KlineTSeries` according to memo 009, sections 001.a and 002.b–002.c.[1] Follow memo 011’s plan structure, including baseline and Python Pro implementations.[2] Raw-class/CSV implementation, comparison and Plotly plotting are implemented. Results, public interfaces and sample charts are recorded below; the Appendix summarizes Plotly integration.
## 001 — Implementation plan
Use the existing Project 009 master table and source context prepared for memo 011 in `samples/chan_table/`; no separate data preparation is needed.
### 001.a — Implement the Kline family
1. Keep immutable domain classes in `src/chanlab/algo/` and loading/serialization adapters in `src/chanlab/data/`.
2. Implement `Kline` with symbol, period, source, timestamp and OHLCV; construction automatically validates required metadata, aware UTC timestamps, finite values, price bounds and nonnegative volume.
3. Implement `KlineTSeries` with an immutable tuple of valid bars; require nonempty input, one symbol/period and strictly increasing timestamps. Allow mixed sources.
4. Implement length, iteration and indexing. Integer access returns a Kline; slices return tuples with normal Python indexing behavior.
5. Define minimal raw CSV read/write adapters preserving values and provenance, with row/field context for validation failures.
6. Add `KlineTSeries.plot()` as proposed in memo009, delegating candlestick/optional volume rendering to a separate Plotly helper. Return a figure; keep rendering logic outside the domain classes. See the Appendix for the interface and checks.
7. Keep ChanTable object interchange, DataFrame conversion, indicators and feature detection separate.
### 001.b — Repeat the raw-class/CSV implementation using Python Pro
1. Read the installed `mas/skills/python-pro/SKILL.md` before the second implementation.[3]
2. Repeat the raw-class/CSV work with the same design, interface, data and acceptance tests. The later Plotly extension is recorded separately in002.f.
3. Preserve both versions separately under `artifacts/mas/kline-family/`; do not overwrite the baseline.
4. Record the exact skill invocation request verbatim and the skill source/version in the MAS task; link it from section 002.
### 001.c — Compare the two raw-class/CSV implementations
1. Run both versions against the same fixtures and full dataset.
2. Compare correctness, memo 009 compliance, immutability, error clarity, readability and dependencies.
3. Save both versions and a concise comparison in `artifacts/mas/kline-family/`; record which version is selected for shared source code and why.
### 001.d — Test the Kline family
1. Check valid construction and rejection of missing metadata, naive/non-UTC timestamps, nonfinite OHLCV, invalid price bounds and negative volume.
2. Check empty series, mixed symbols/periods, duplicate/decreasing timestamps, mixed-source acceptance, immutability, iteration, negative indexing and slicing.
3. Check full-dataset loading and read→write→read preservation of raw values, timestamps and provenance.
4. Run pytest and report-only Ruff; record actual commands, results, blockers and deferred integrations under `mas/tasks/`.
5. Verify plotted data against the selected bars, optional volume, empty selections, missing optional dependency, source immutability and HTML export; inspect representative charts visually.
## 002 — Implementation notes and logs
### 002.a — Implement the Kline family → 001.a
Implemented immutable `Kline` and `KlineTSeries` with automatic validation and normal sequence behavior in [kline.py](../../src/chanlab/algo/kline.py). [kline_csv.py](../../src/chanlab/data/kline_csv.py) reads the existing master table's raw fields or a nine-column raw CSV and writes raw CSV plus provenance context. Errors name the file, row and field. No changes to the master table or ChanTable implementation.
### 002.b — Apply Python Pro → 001.b
Baseline code passed its original 109 acceptance cases and was frozen before reading Python Pro1.1.0. The same author then implemented the typed continuation; both versions are retained under `artifacts/mas/kline-family/`. [The task](../../mas/tasks/20261108-memo013-execution.md) preserves the exact invocation request and source version.
### 002.c — Compare and select → 001.c
Selected the Python Pro continuation plus review corrections: explicit types/indexing overloads, float-compatible numeric validation and protection against identical or aliased output files. The final identical 114-case suite gives baseline110 passed/4 failed and selected114 passed; baseline defects remain visible in [the comparison](../../artifacts/mas/kline-family/comparison.md). This is an incremental comparison, not proof of a skill-only effect.
### 002.d — Test → 001.d
Active regression: **165 passed**, including all51 unchanged ChanTable cases. Strict mypy, Black and report-only Ruff passed; new-module statement coverage93%. Complete10,060-row raw export/reload preserved numeric values, UTC instants, metadata and nine context entries. Float/ISO spelling may normalize; original inputs and baseline hashes are unchanged. [Verification and checks](../../artifacts/mas/kline-family/verification.json); [generated raw export and context](../../artifacts/mas/kline-family/roundtrip/).
### 002.e — Handoff and remaining scope
The user confirmed011 ready and released013 execution. Source UTC labels and source-defined volume units were used unchanged; independent provider start-label evidence is not claimed. Plotly plotting is implemented with an optional dependency. ChanTable object interchange, DataFrame conversion, indicators and feature detection remain deferred. [Plot interface, samples and reproduction commands](../../artifacts/kline/README.md).
### 002.f — Plotly implementation and samples
Added lazy `KlineTSeries.plot()` delegating to [kline_plot.py](../../src/chanlab/visualization/kline_plot.py). Optional `plot` extra is locked at Plotly7.1.0; raw/CSV use works without it.11 focused plotting tests and all176 regression tests pass; Ruff, Black and strict mypy checks pass. Core/plot statement coverage93%. Generated and visually inspected200-bar candles/volume and40-bar price detail, verifying every plotted value against source. [Samples and verification](../../artifacts/kline/README.md); [implementation task](../../mas/tasks/20261108-memo013-plotly-implementation.md). The original165-test result and frozen baseline comparison above describe the earlier raw/CSV phase; those snapshots were preserved.
## 003 — Implemented Kline family interface
### 003.a — Kline and KlineTSeries
`Kline` stores nine immutable fields: `symbol`, `period`, `source`, `timestamp`, `open`, `high`, `low`, `close` and `volume`. `KlineTSeries.klines` is an immutable tuple of bars; construction copies an input iterable and validates immediately.

| Method or operation | Behavior |
| --- | --- |
| `Kline(symbol, period, source, timestamp, open, high, low, close, volume)` | Construct one bar and automatically validate it. |
| `bar.validate()` | Check nonblank provenance, aware UTC datetime, finite OHLCV, price bounds and nonnegative volume. Accept float/int values except bool; integers must be exactly representable as float. |
| `KlineTSeries(klines)` | Materialize a nonempty iterable of Kline objects into a tuple and automatically validate it. |
| `series.validate()` | Check every bar, one symbol/period and strictly increasing timestamps. Mixed sources are allowed. |
| `len(series)` | Number of bars. |
| `series[index]` | One Kline; negative indexing follows Python behavior. |
| `series[start:stop:step]` | A tuple of bars, including an empty tuple when the slice has no matches. |
| `iter(series)` | Iterate over bars in stored order. |
| `series.plot(*, start=None, stop=None, volume=True, title=None)` | Return a Plotly Figure through the separate helper. Slice positions follow Python semantics; empty selections raise `ValueError`. Show optional aligned volume and retain UTC/session gaps. No automatic display/export. |

Invalid construction or validation raises `ValueError`; invalid indexing follows normal Python exceptions. These classes contain no file I/O.
### 003.b — CSV functions
Import file functions from `chanlab.data.kline_csv`; they are separate from the domain classes.

| Function | Behavior |
| --- | --- |
| `read_kline_csv(path, context_path=None)` | Read the exact nine-column raw schema or existing 41-column master header. Return `(KlineTSeries, immutable_context_mapping)`; absent context returns an empty mapping. |
| `write_kline_csv(series, path, context_path=None, *, context=None)` | Validate and write nine raw columns plus an optional `key,value` context file. Nonempty context requires `context_path`; data and context must refer to different files. Existing output files are replaced. |

Raw output columns, in order: `timestamp,symbol,period,source,open,high,low,close,volume`. Reading the master projects only these raw fields; exporting does not recreate its feature columns. Numeric values, UTC instants and provenance are retained, while ISO/float spelling may normalize. Read validation errors identify the file, row and field. ChanTable object-conversion methods and DataFrame conversion remain deferred. Plotting is available through `series.plot()` as documented above and in003.d; see the Appendix for integration details.
### 003.c — Runnable example
Run from the repository root using `.venv/bin/python` with `PYTHONPATH=src`:
```python
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.data.kline_csv import read_kline_csv, write_kline_csv

bar = Kline("EXAMPLE", "15m", "manual", datetime(2026, 1, 1, tzinfo=UTC),
            11.0, 13.0, 10.0, 12.0, 20.0)
single = KlineTSeries([bar])
assert single[0] is bar
assert single[:] == (bar,)

folder = Path("samples/chan_table")
series, context = read_kline_csv(
    next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv"))
)
assert len(series) == 10060
with TemporaryDirectory() as directory:
    output = Path(directory)
    write_kline_csv(series, output / "raw.csv", output / "context.csv", context=context)
    restored, restored_context = read_kline_csv(output / "raw.csv", output / "context.csv")
    assert restored.klines == series.klines
    assert restored_context == context
```
### 003.d — Plotting and sample charts
Install the optional package from the repository root with `uv sync --extra plot`. With `series` loaded as in003.c:
```python
from pathlib import Path

fig = series.plot(start=-200, volume=True, title="CC · 15m · Last 200 bars")
assert len(fig.data[0].x) == 200
assert len(fig.data) == 2
output = Path("artifacts/kline/example-last200.html")
output.parent.mkdir(parents=True, exist_ok=True)
fig.write_html(output, include_plotlyjs=True)
```
Call `fig.show()` to display it. Set `volume=False` for price only, or omit `start`/`stop` to include every bar. HTML export preserves browser interaction.[4] PNG export additionally uses Kaleido and Chrome.[5]

| Generated sample | Interactive chart | PNG preview |
| --- | --- | --- |
| Last200 fifteen-minute bars with volume | [Open HTML](../../artifacts/kline/cc-15m-last200-volume.html) | [View PNG](../../artifacts/kline/cc-15m-last200-volume.png) |
| Last40 bars, price detail | [Open HTML](../../artifacts/kline/cc-15m-last40-detail.html) | [View PNG](../../artifacts/kline/cc-15m-last40-detail.png) |

## Appendix — Plotly plotting
**Status:** Implemented through `KlineTSeries.plot()` and a separate rendering helper; section003 documents the working API.

1. **Purpose.** Use Plotly's candlestick trace for OHLC bars and interactive inspection.[6] Our helper supplies Kline data and labels; Plotly handles rendering. Future Chan overlays remain separate work.
2. **Interface.** `series.plot(*, start=None, stop=None, volume=True, title=None) -> plotly.graph_objects.Figure`. Bounds use Python slice positions; omitted bounds select the full series. Empty selections fail. The caller controls display and export.
3. **Code boundary.** `plot()` lazily delegates to `plot_kline_series(...)` in `src/chanlab/visualization/kline_plot.py`. No rendering implementation in the domain classes, no DataFrame required, and no source mutation.
4. **Chart.** UTC timestamps map directly to OHLC candles. Optional volume bars share the time axis using `make_subplots`.[7] Labels show symbol/period, UTC, price and source-defined volume units. Preserve actual session gaps and values; no resampling or silent truncation. Select a smaller slice for detailed inspection.
5. **Dependency.** Plotly7.1.0 is locked under the optional `plot` extra. Install with `uv sync --extra plot`. Missing Plotly produces that installation instruction; raw classes and CSV continue working without the extra. Base runtime dependencies remain empty.
6. **Display/export.** Use `fig.show()` or `fig.write_html(..., include_plotlyjs=True)` for standalone interactive HTML.[4] Generated samples live in `artifacts/kline/`. PNG previews were exported with temporary Kaleido tooling and local Chrome; those tools are not needed for interactive plotting/HTML.[5]
7. **Checks.**11 plot cases cover traces/source equality, slices, volume on/off, empty selections, delegation, no automatic display/export and raw/CSV use without Plotly. All176 tests pass; core/plot statement coverage93%. Both sample PNGs were visually inspected; trace arrays and protected data hashes match source. See [verification](../../artifacts/kline/verification.json).
## References
1. [Memo 009 — Design pattern for Chan features](memoWX_009_designPatternForChanFeatures.md).
2. [Memo 011 — ChanTable implementation](memoWX_011_chanTableImplementation.md).
3. [Memo 012 — Python Pro skill](memoWX_012_Skill_python_pro.md).
4. Plotly. [Interactive HTML export](https://plotly.com/python/interactive-html-export/).
5. Plotly. [Static image export](https://plotly.com/python/static-image-export/).
6. Plotly. [Candlestick charts](https://plotly.com/python/candlestick-charts/).
7. Plotly. [Subplots](https://plotly.com/python/subplots/).
