# ChanTable implementation plan
## 000 — Scope
First implementation of ChanTable and its supporting classes according to memo 009.[1] The steps below are planned.
## 001 — Implementation plan
### 001.a — Scan Project 009 and locate the CC data
1. Find the dataset and its loading code.
2. Check columns, symbol, period and timestamp convention.
### 001.b — Copy the data into references/proj009data
1. Copy the selected original files unchanged.
2. Record original file locations, source version and checksums.
### 001.c — Create sample data using memo 009’s CSV template
1. Select a small dataset and map it to the template’s 41 columns.
2. Preserve raw values and UTC timestamps; retain source/version context.
3. Use JSON integer lists for IDs, `[]` for calculated-empty results and `NA` for unavailable results.
### 001.d — Create Python code to read and write the data
1. Implement ChanTable and the supporting classes, members and source relationships defined in memo 009, as needed for this first implementation.
2. Define the minimal ChanTable methods for construction, validation, reading and writing; memo 009 leaves these methods open.
3. Keep data loading in `src/chanlab/data/` and shared domain logic in `src/chanlab/algo/`.
4. Read and write the sample while preserving raw rows, feature mappings and source/version context. Leave undecided detection rules and DecisionStep definitions for later.
### 001.e — Test the ChanTable classes
1. Test class validation, source relationships and raw-row feature mappings against memo 009.
2. Check that read→write→read preserves values, IDs, missing values and context; test invalid inputs.
3. Run pytest and Ruff; record actual results and blockers in `mas/tasks/`.
## References
1. [Memo 009 — Design pattern for Chan features](memoWX_009_designPatternForChanFeatures.md).
