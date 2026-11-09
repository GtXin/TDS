# ChanTable implementation plan
## 000 — Scope
Implement the first ChanTable CSV reader, writer and validation using memo 009.[1] Feature-detection algorithms remain deferred. All steps below are planned.
## 001 — Steps
1. **Find the data.** Inspect Project 009 for the CC dataset and its loading code. Identify its columns, symbol, period and timestamp convention.
2. **Copy the originals.** Copy the selected files unchanged into `references/proj009data/`. Record their original file locations, source version, copy date and checksums.
3. **Create a sample.** Save a small CSV in `samples/` using memo 009’s 41 columns and source/version context. Preserve raw rows and OHLCV; use UTC bar-start timestamps. Encode IDs as JSON integer lists: `[]` means calculated with no match; `NA` means unavailable. Leave uncalculated features `NA`.
4. **Define the interface.** Specify the minimal ChanTable construction, read, write and validation methods, with required Kline/KlineTSeries support. CSV data alone does not reconstruct authoritative feature-series objects.
5. **Write the code.** Put data loading in `src/chanlab/data/` and shared domain logic in `src/chanlab/algo/`. Validate columns, raw rows, timestamps, OHLCV, IDs and missing values. Retain source/version context.
6. **Test and record.** Add tests in `tests/` for valid and invalid inputs. Check that read→write→read preserves rows, values, IDs, missing values and context. Verify copied-file checksums and sample columns. Run pytest and Ruff; record results and blockers in `mas/tasks/`.
## References
1. [Memo 009 — Chan feature design, section 002.u and CSV files](memoWX_009_designPatternForChanFeatures.md#002u--chantable).
