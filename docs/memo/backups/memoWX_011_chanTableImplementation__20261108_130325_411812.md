# ChanTable implementation plan
## 000 — Scope
First implementation of ChanTable and its supporting classes according to memo 009.[1] First implementation and comparison completed on 2026-11-08; limitations are recorded in section 002.
## 001 — Implementation plan
### 001.a — Scan Project 009 and locate the CC data
1. Find the dataset and its loading code.
2. Check columns, symbol, period and timestamp convention.
### 001.b — Copy the data into references/proj009data
1. Copy the selected original files unchanged.
2. Record original file locations, source version and checksums.
### 001.c — Create sample data using memo 009’s CSV template
1. Store sample files in `samples/chan_table/`.
2. Name data files `<symbol>_<period>_<startDate>_<endDate>_chan_table_v<YYYYMMDD>.csv`. Use `YYYYMMDD` for the data-range dates and creation/version date; today’s version is `v20261108`. Example: `CC_1d_20250101_20250331_chan_table_v20261108.csv`.
3. Name the companion context file with the same prefix and version: `CC_1d_20250101_20250331_context_v20261108.csv`. Record source files, selected rows and conversion notes in `README.md`.
4. Select the complete dataset and map it to the template’s 41 columns.
5. Preserve raw values and UTC timestamps; retain source/version context.
6. Use JSON integer lists for IDs, `[]` for calculated-empty results and `NA` for unavailable results.
### 001.d — Create Python code to read and write the data 
1. Implement ChanTable and the supporting classes, members and source relationships defined in memo 009, as needed for this first implementation.
2. Define the minimal ChanTable methods for construction, validation, reading and writing; memo 009 leaves these methods open.
3. Keep data loading in `src/chanlab/data/` and shared domain logic in `src/chanlab/algo/`.
4. Read and write the sample while preserving raw rows, feature mappings and source/version context. Leave undecided detection rules and DecisionStep definitions for later.
### 001.e — Repeat 001.d using the Python Pro skill
1. Read the installed Python Pro skill at `mas/skills/python-pro/SKILL.md` before the skill implementation.
2. Repeat 001.d with the same memo 009 requirements, data and interface, applying the skill.
3. Preserve both implementations separately for comparison; do not overwrite the 001.d code.
4. Record the exact request used to invoke Python Pro, verbatim, in the task record under `mas/tasks/`; link it from section 002.
### 001.f — Compare the two implementations
1. Run both implementations against the same data and tests.
2. Compare correctness, memo 009 compliance, code structure, readability and dependencies.
3. Save both code versions and a concise comparison under `artifacts/mas/`, recording differences and tradeoffs for reference. Record the skill source/version used.
### 001.g — Test the ChanTable classes
1. Test class validation, source relationships and raw-row feature mappings against memo 009.
2. Check that read→write→read preserves values, IDs, missing values and context; test invalid inputs.
3. Run pytest and Ruff; record actual results and blockers in `mas/tasks/`.
## 002 — Implementation notes and logs
Execution date: 2026-11-08. Each entry below maps to the same letter in section 001.
### 002.a — Locate CC data → 001.a
- **Found:** `proj009/records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv`; loading code in Project 009’s `src/tradinglab/data_io/csv_file_kline_t_series.py`.
- **Data:** 10,060 rows; symbol `dce:KQ.m@m`, period `15m`, dates 2024-10-28–2026-08-19. Source includes epoch, UTC and Shanghai timestamps plus OHLCV.
- **Open:** UTC values are retained; whether source timestamps label bar starts is not yet confirmed.
### 002.b — Preserve originals → 001.b
- **Saved:** [unchanged CSV](../../references/proj009data/dce-kqm-m-15m.csv) and [provenance](../../references/proj009data/provenance.json) in `references/proj009data/`.
- **Recorded:** original location, source Git revision, copy date, row count and SHA256.
- **Checked:** original/copy checksums match. No changes to the Project 009 source.
### 002.c — Create sample → 001.c
- **Saved:** [full sample](../../samples/chan_table/dce-KQ.m-at-m_15m_20241028_20260819_chan_table_v20261108.csv), [context](../../samples/chan_table/dce-KQ.m-at-m_15m_20241028_20260819_context_v20261108.csv) and [conversion notes](../../samples/chan_table/README.md).
- **Checked:** all 10,060 rows, 41 columns; raw OHLCV, symbol and period match the source. UTC values retained; filename encodes the symbol as `dce-KQ.m-at-m`.
- **Feature state:** all feature columns are `NA`; no detection was run. Tests separately check `[]` versus `NA`.
### 002.d — Baseline implementation → 001.d
- **Saved:** [baseline source](../../artifacts/mas/memo011/baseline/chan_table.py) before reading Python Pro.
- **Implemented:** Kline/KlineTSeries validation, ChanTable construction, 41-column CSV/context reading and writing, and ID-list parsing.
- **Checked:** 18 shared CSV tests passed, including the complete-data round trip and invalid inputs.
- **Gap:** baseline does not implement authoritative feature records or generate their raw-row mappings; it is a partial implementation of 001.d.
### 002.e — Python Pro implementation → 001.e
- **Used:** installed Python Pro1.1.0. [Exact invocation requests](../../mas/tasks/20261108-memo011-execution.md#exact-python-pro-request) are retained verbatim.
- **Implemented:** [raw/merged classes and ChanTable](../../src/chanlab/algo/chan_table.py), [seven further feature record/series pairs and mapping adapter](../../src/chanlab/algo/features.py), and [file adapter](../../src/chanlab/data/chan_table_csv.py). Records retain source references; adapters generate interval memberships, start/end markers and event anchors.
- **Preserved:** [skill-version source snapshot](../../artifacts/mas/memo011/python_pro/chanlab/). CSV import restores the table view; callers must supply authoritative feature objects separately.
- **Deferred:** detection algorithms, DecisionStep, selected-rule source/completion/strength checks and DataFrame/plot conveniences. Generic registry typing still uses `Any`.
- **Deviation:** skill content was read before baseline testing and before the initial request was logged, although baseline source was already saved. Followup requests were logged; the comparison is not a controlled skill experiment.
### 002.f — Compare versions → 001.f
- **Compared:** same complete sample and shared CSV tests; both pass those tests. Baseline lacks feature support; the skill continuation adds records, mapping and validation.
- **Tradeoff:** baseline is smaller; the continuation has broader coverage and stricter typing, with more code. Both use only standard-library runtime dependencies.
- **Reference:** [comparison and both code locations](../../artifacts/mas/memo011/comparison.md). Differences reflect added work as well as skill use; they do not establish the skill’s independent effect.
### 002.g — Validate classes and I/O → 001.g
- **Tests:** `PYTHONPATH=src … coverage run --source=src/chanlab -m pytest tests -q` → **31 passed, 1 xfailed**. The expected failure identifies baseline’s missing merged-feature support.
- **Covered:** full CSV/context round trip, invalid schema/OHLCV/timestamps/IDs, empty versus unavailable IDs, source identity, feature relationships and interval/event mapping.
- **Checks:** strict mypy passed for all three source files; Black and Ruff passed. Measured domain coverage **91%**; the thin data adapter was excluded from coverage discovery.
- **Evidence/next:** [verification](../../artifacts/mas/memo011/verification.json) and [task with commands](../../mas/tasks/20261108-memo011-execution.md). Confirm source bar-start labeling and selected rules before relying on detection results.
## 003 — Implemented interfaces and sample use
These interfaces describe the current Python Pro implementation in `src/`, not every proposed method in memo 009. Run examples from the TDS repository root with `PYTHONPATH=src .venv/bin/python <script.py>`.
### 003.a — Class interfaces
Records are frozen dataclasses; construction calls `validate()`. Feature records share integer `id`, `status` and optional UTC `confirmed_at=None`.

| Class | Constructor fields besides shared feature fields |
|---|---|
| `Kline` | `symbol, period, source, timestamp, open, high, low, close, volume`; no feature ID/status |
| `KlineTSeries` | `klines`: ordered tuple of Kline objects |
| `MergedKline` | `low, high, direction, source_start, source_stop` |
| `Fenxing` | `kind, price, anchor_raw_index, source_start, source_stop` |
| `Bi` | `start_fenxing_index, end_fenxing_index, start_price, end_price, direction` |
| `Xianduan` | `source_start, source_stop, start_price, end_price, direction` |
| `Zhongshu` | `level, lower, upper, member_indices, start_raw_index, end_raw_index` |
| `Zoushi` | `level, kind, source_start, source_stop, zhongshu_indices, start_raw_index, end_raw_index, start_price, end_price` |
| `Beichi` | `level, kind, zoushi_index, entry_index, exit_index, anchor_raw_index` |
| `BuySellPoint` | `level, side, category, price, anchor_raw_index, zoushi_index, center_index, beichi_index`; use `None` for unused center/divergence references |

Use keyword arguments to avoid field-order mistakes. Source ranges `[source_start, source_stop)` exclude the stop index; raw start/end extents include both endpoints. Indices refer to positions in the exact source series; IDs are lookup keys, not positions.

| Series | Construction and available methods |
|---|---|
| `KlineTSeries` | `KlineTSeries(klines)`; `validate()`, `len(series)`, iteration, indexing and tuple slicing |
| `MergedKlineSeries` | Required: `source_series, klines, rule_tree_ref, trace_by_point`; optional `trace=(), config=()`; `validate()`, length, indexing/slicing, `get_by_id(id)` |
| `FenxingSeries`, `BiSeries`, `XianduanSeries` | Required: `source_series, items, rule_tree_ref, trace_by_point`; optional `trace=(), config=()`; `validate()`, length, iteration, indexing/slicing, `get_by_id(id)`, `explain(point_index)` |
| `ZhongshuSeries` | Same shared interface plus `level` |
| `ZoushiSeries` | Same shared interface plus `level, zhongshu_series` |
| `BeichiSeries` | Same shared interface plus `level, zhongshu_id, comparison_series` |
| `BuySellPointSeries` | Same shared interface plus `level, beichi_series` |

Pass record tuples and one trace-index tuple per record, even when empty. `explain()` returns stored trace objects; it does not generate explanations or detect features. Supply linked series and levels when required by the records. Rule-dependent source qualification is not fully enforced yet.
### 003.b — ChanTable and adapters

| Interface | Current behavior |
|---|---|
| `ChanTable(rows, context=None)` | Validate ordered string-valued rows against the 41-column schema; construct the raw series and ID maps. No separate public `validate()` method yet. |
| `ChanTable.read_csv(path, context_path=None)` | Read a table and optional key/value context CSV. |
| `table.write_csv(path, context_path=None)` | Write rows and optional context. |
| `read_chan_table(...)`, `write_chan_table(table, ...)` | File-adapter wrappers in `chanlab.data.chan_table_csv`. |
| `register_merged(table, key, series)` | Return a new table with merged interval markers; retain the exact supplied series. |
| `register_features(table, key, series)` | Return a new table with one of the seven other feature groups mapped to raw intervals/anchors. |

Members: `source_series`, `rows`, `context`, `feature_series`, `memberships`, `start_ids`, `end_ids`, `anchor_ids`. ID maps currently use column names as keys, e.g. `memberships["mk_ids"]`; each value is a row-aligned tuple. A row value of `None` means unavailable and `()` means calculated-empty. CSV represents these as `NA` and `[]`.
Registration requires the same raw-series object, permits one result version per feature class, and preserves the original table. Conflicting scalar annotations at one marker are rejected. CSV round trips preserve the view/context but do not reconstruct the feature registry.
### 003.c — Read the complete sample
```python
from pathlib import Path
from chanlab.data.chan_table_csv import read_chan_table, write_chan_table

folder = Path("samples/chan_table")
stem = "dce-KQ.m-at-m_15m_20241028_20260819"
table = read_chan_table(
    folder / f"{stem}_chan_table_v20261108.csv",
    folder / f"{stem}_context_v20261108.csv",
)
assert len(table.source_series) == 10060
assert table.memberships["mk_ids"][0] is None
bar = table.source_series[0]
```
### 003.d — Register example records and export
Continue the preceding example. These are manually supplied demonstration records, not detected or confirmed Chan features.
```python
from chanlab.algo.chan_table import (
    MergedKline, MergedKlineSeries, register_merged,
)
from chanlab.algo.features import Fenxing, FenxingSeries, register_features

merged = MergedKlineSeries(
    source_series=table.source_series,
    klines=(MergedKline(
        id=1, low=bar.low, high=bar.high, direction="up",
        source_start=0, source_stop=1, status="example",
    ),),
    rule_tree_ref="manual-example", trace_by_point=((),),
)
view = register_merged(table, "merged", merged)
assert view.memberships["mk_ids"][:2] == ((1,), ())

fx = FenxingSeries(
    source_series=merged,
    items=(Fenxing(
        id=2, kind="top", price=bar.high, anchor_raw_index=0,
        source_start=0, source_stop=1, status="example",
    ),),
    rule_tree_ref="manual-example", trace_by_point=((),),
)
view = register_features(view, "fractal", fx)
assert view.anchor_ids["fx_anchor_ids"][0] == (2,)
assert view.feature_series["fractal"] is fx

out = Path("artifacts/chan_table_example")
out.mkdir(parents=True, exist_ok=True)
write_chan_table(view, out / "table.csv", out / "context.csv")
loaded = read_chan_table(out / "table.csv", out / "context.csv")
assert loaded.rows == view.rows
assert not loaded.feature_series  # CSV contains the view, not feature objects.
```
Examples verified together on 2026-11-08 with outputs redirected to a temporary folder; repository sample files were unchanged.
## References
1. [Memo 009 — Design pattern for Chan features](memoWX_009_designPatternForChanFeatures.md).
