# ChanTable implementation plan
## 000 — Scope
First implementation of the ChanTable master table only, using memo009’s raw-row schema.[1] ChanTable is the first and only implemented class in this phase. All feature columns remain NA.
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
6. Set every reserved feature column to `NA`. JSON ID lists and calculated-empty `[]` are deferred until feature classes are implemented.
### 001.d — Create Python code to read and write the data 
1. Implement only ChanTable with 41-column raw rows and provenance context; reserve every feature column as NA and reject non-NA values.
2. Define the minimal ChanTable methods for construction, validation, reading and writing; memo 009 leaves these methods open.
3. Keep data loading in `src/chanlab/data/` and shared domain logic in `src/chanlab/algo/`.
4. Read and write the sample while preserving raw rows, NA feature columns and source/version context. Leave undecided detection rules and DecisionStep definitions for later.
### 001.e — Repeat 001.d using the Python Pro skill
1. Read the installed Python Pro skill at `mas/skills/python-pro/SKILL.md` before the skill implementation.
2. Repeat 001.d with the same memo 009 requirements, data and interface, applying the skill.
3. Preserve both implementations separately for comparison; do not overwrite the 001.d code.
4. Record the exact request used to invoke Python Pro, verbatim, in the task record under `mas/tasks/`; link it from section 002.
### 001.f — Compare the two implementations
1. Run both implementations against the same data and tests.
2. Compare correctness, memo 009 compliance, code structure, readability and dependencies.
3. Save both code versions and a concise comparison under `artifacts/mas/`, recording differences and tradeoffs for reference. Record the skill source/version used.
### 001.g — Test ChanTable
1. Test raw schema, UTC timestamps, strict ordering, OHLCV, provenance and NA feature reservations against memo009.
2. Check that read→write→read preserves raw values, reserved `NA` columns and context; test invalid inputs.
3. Run pytest and Ruff; record actual results and blockers in `mas/tasks/`.
## 002 — Implementation notes and logs
### 002.a — Locate CC data → 001.a
Complete Project009 dataset: `proj009/records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv`, 10,060 rows, `dce:KQ.m@m`, 15m, 2024-10-28–2026-08-19. UTC values are preserved; bar-start labeling remains unconfirmed.
### 002.b — Preserve originals → 001.b
Unchanged source and checksum/version provenance remain in `references/proj009data/`. The correction did not alter raw data.
### 002.c — Create complete sample → 001.c
The full 41-column sample and companion key/value context remain in `samples/chan_table/`; raw OHLCV and UTC strings are retained, all feature columns NA. See its README for conversion/source evidence.
### 002.d — Implement master table → 001.d
Only `ChanTable` is active in `src/chanlab/algo/chan_table.py`. File adapters remain functions in `src/chanlab/data/chan_table_csv.py`. Expanded feature classes/tests and prior comparison are superseded and preserved in `artifacts/mas/memo011/superseded_feature_scope/`. Master-only baseline is frozen separately under `artifacts/mas/memo011/baseline/`.
### 002.e — Apply Python Pro → 001.e
Installed Python Pro1.1.0 was applied to a typed continuation with the same interface, saved under `artifacts/mas/memo011/python_pro/`. The exact request is recorded before continuation in [the execution task](../../mas/tasks/20261108-memo011-execution.md). The skill had already been read during earlier work; this is an iterative comparison, not a clean causal experiment.
### 002.f — Compare → 001.f
All three copies run identical tests. The continuation makes validation state annotations explicit; behavior and dependencies are unchanged. No independent skill benefit is established. See [comparison](../../artifacts/mas/memo011/comparison.md).
### 002.g — Test → 001.g
51 tests pass across active, baseline and skill copies, including the complete 10,060-row roundtrip, invalid schema/index, UTC/order, OHLCV, missing provenance and reserved-feature rejection. Active statement coverage100%; strict mypy, Black and Ruff checks recorded in [verification](../../artifacts/mas/memo011/verification.json). Bar-start semantics remain a separate evidence limitation; feature calculations and other classes are outside this phase.
## 003 — Implemented ChanTable interface
`ChanTable(rows, context=None)` copies raw string mappings into immutable row/context views and validates immediately. `rows` contains the ordered41-column records; `context` retains source/version metadata without interpreting feature records.

| Method | Behavior |
| --- | --- |
| `validate()` | Check exact schema, zero-based contiguous index, one symbol/period, required provenance, strictly increasing aware UTC timestamps, finite consistent OHLCV/nonnegative volume and feature NA reservations. |
| `read_csv(path, context_path=None)` | Read table and optional unique key/value context. |
| `write_csv(path, context_path=None)` | Validate and export table/context. |
| `len(table)` | Number of raw rows. |
| `table[index]` | Read-only raw row by integer index. |
| `iter(table)` | Iterate read-only rows. |

Run from the repository root with `PYTHONPATH=src`:
```python
from pathlib import Path
from tempfile import TemporaryDirectory
from chanlab.algo.chan_table import ChanTable

folder = Path("samples/chan_table")
table = ChanTable.read_csv(next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv")))
assert len(table) == 10060
with TemporaryDirectory() as directory:
    output = Path(directory)
    table.write_csv(output / "rows.csv", output / "context.csv")
    restored = ChanTable.read_csv(output / "rows.csv", output / "context.csv")
    assert restored.rows == table.rows
    assert restored.context == table.context
```
## References
[1] [Memo009: Chan feature design](memoWX_009_designPatternForChanFeatures.md).
