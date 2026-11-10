# Memo026 table and DataFrame integration
## Task
- **ID:** 20261109-memo026-table-integration
- **Goal:** Implement memo009’s MergedKlineSeries table/DataFrame interfaces, accepting existing raw family or ChanTable as source; update026.
- **Inputs:**009/013/015/026, current raw/merged/table classes and samples.
- **Allowed changes:** merged/table algorithm interfaces, separate data adapter, integration tests/artifacts, optional dataframe dependency/lock, backed-up026, memory/log/task.
- **Acceptance checks:** both source entries/exact identity, immutable registry/new view, column projection, key conflicts/multiple registrations, lossless CSV/context/trace roundtrip, source/version tamper rejection, detached DataFrame, full dataset and regression/quality checks.
- **Assignment:** Codex sequential; Python Pro applied for typing/testing/validation.
- **Status:** done
## Result and handoff
- **Outcome:** Implemented derive_from(raw|table), ChanTable.from_source_series, registered from/to table and compact to_dataframe. Optional pandas extra locked. Updated026 with interfaces and executed examples.
- **Evidence:** src/chanlab/data/merged_kline_table.py; tests/test_merged_kline_table.py; artifacts/mas/merged-kline-family/integration/verification.json and generated CSV/context.210 regression passed; strict mypy,Black,Ruff pass.10060 raw/6200 result/DataFrame rows;all6200 explanations identical after persistence;source/sample hashes unchanged.
- **Blockers:** none in released scope. Confirmation/warning-scoring/general DecisionStep unchanged.
- **Next action:** none; other feature adapters and additional per-key CSV columns are separate future scope.
## Contracts
Registry keys map to exact feature objects; source identity required in memory. Same key with different result rejected; new keys preserve existing registrations. Fixed MK CSV group displays first key; every registered key has keyed role mappings and context payload. Other feature columns remain reserved NA. Full persistence requires context path; rebuilds new source/result snapshots, verifies class/level/source/result digests and projection. Context includes authoritative records/config/rules/full trace; scalar CSV alone is insufficient. DataFrame attrs carry source/config/rule/result metadata and are not preserved by ordinary DataFrame CSV export. Missing pandas yields optional-extra installation message.
## Actual checks and corrections
- Initial regression caught missing-volume KeyError after source materialization; schema validation now precedes it and retains ValueError behavior.
- Offline pandas resolution unavailable; authorized network resolution installed optional pandas3.1.1 and locked dependencies. Existing plot extra retained.
- pandas3 defaults all-missing datetime columns to seconds; export now explicitly uses datetime64[ns,UTC].
- Strict mypy corrected tuple-list inference; pandas missing stubs are handled with localized import-untyped ignore, matching optional Plotly approach. Black/import fixes applied only changed files; final Ruff is report-only.
- Tests cover source entries, exact objects, key conflicts, multiple results, empty marker tuples, source/context/projection tampering, absent dependency, detached DataFrame and required/distinct output destinations. CSV reader temporarily enlarges/restores field limit for large lossless context (full sample context≈4.8MB).
