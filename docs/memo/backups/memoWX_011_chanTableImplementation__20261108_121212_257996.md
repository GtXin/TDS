# ChanTable implementation plan
## 000 — Scope
Plan the first ChanTable implementation using memo 009’s raw-row contract and CSV format.[1] Start with source-data inspection, a preserved data snapshot, a representative CSV sample, and Python import/export with validation. Feature-detection algorithms and decision tracing remain outside this first stage. The steps below are proposed, not completed.
## 001 — Implementation plath 
### 001.a — Locate and inspect Project 009 data
Inspect the neighboring `proj009` repository to locate the CC dataset and its loading code. Identify the exact files, symbol, period, timestamp convention, OHLCV fields and existing feature columns; record any differences from memo 009 before conversion.
### 001.b — Preserve a source snapshot
Copy the selected source files unchanged into `references/proj009data/`. Add a short provenance record with original paths, source revision when available, copy date, checksums and relevant data conventions. Keep converted data separate from these originals.
### 001.c — Prepare a ChanTable sample
Create a small sample under `samples/` using memo 009’s 41-column CSV template and accompanying source/version context.[1] Preserve the selected raw rows, UTC bar-start timestamps, OHLCV and provenance. Encode ID tuples as JSON integer lists; distinguish unavailable `NA` from computed-empty `[]`. Leave uncalculated feature groups `NA`; label any synthetic feature examples explicitly. Document timestamp conversion and any incompatible source fields.
### 001.d — Implement CSV import, export and validation
First define the minimal ChanTable construction and I/O interface: memo 009 proposes members but defers its methods. Establish the required Kline/KlineTSeries support and how CSV context is retained. A CSV alone must not be treated as sufficient to reconstruct authoritative feature-series objects.
Keep raw-data loading in `src/chanlab/data/` and shared ChanTable/domain logic in `src/chanlab/algo/`, independent of API and website code. Validate column order, raw-row consistency, UTC timestamps, OHLCV, integer-ID lists and missing-value semantics. Preserve source/version context during export.
### 001.e — Test the first implementation
Add focused tests under `tests/` for valid input, invalid schema/raw data, malformed IDs and the distinction between unavailable and computed-empty results. Verify a CSV read→write→read round trip preserves row order, raw values, ID lists, missing values and context. Check source-copy hashes and sample/template column agreement. Run the relevant pytest tests and Ruff checks; record actual results and unresolved issues in a task record under `mas/tasks/`.
## References
1. [Memo 009 — Chan feature design, section 002.u and linked CSV files](memoWX_009_designPatternForChanFeatures.md#002u--chantable).
