# 线段新数据验证

## 000 — Scope
Use KWX’s master table to recalculate and plot Xianduan with our Python implementation, then compare results at each level with KWX’s existing results. Use the table’s raw OHLCV columns as calculation inputs; retain KWX’s calculated features as comparison results. Differences must be investigated before being classified as errors.

This memo is a plan only. Execution has not started and requires a subsequent user instruction.

## 001 — Data and validation scope
Use KWX’s 44,375-row, 1-minute dataset for `dce:KQ.m@jm`, covering 2026-04-27 05:32 through 2026-11-09 05:36 UTC. Validate the pipeline from raw Klines through merged Klines, Fenxing, Bi, and Xianduan.

The input package is described in KWX004.[1] Its files are:

| File | Purpose |
|---|---|
| [ChanTable.csv](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/ChanTable.csv) | Master table containing raw market data and KWX feature mappings |
| [context.csv](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/context.csv) | Source, configuration, and selected-series metadata |
| [features.json](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/features.json) | KWX feature records for comparison |
| [cc_native_snapshot.json](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/cc_native_snapshot.json) | Preserved CC results for tracing differences |
| [import_report.json](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/import_report.json) | Import mappings and diagnostics |
| [verification.json](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/verification.json) | Published verification receipt and file hashes |
| [comparison.json](../../artifacts/mas/cc-chantable-20261111-134106-27c20343/comparison.json) | Existing batch comparison evidence |

The original standalone `klines.csv` was outside the published package; use the raw columns preserved in the master table. Keep source files unchanged. Our Bi and Xianduan calculations follow memo029 and memo030, with implementation interfaces documented in memo028 and memo031.[2–5]

## 002 — Configuration and execution plan
### 002.a — Load the master table and check compatibility
1. Record input hashes, code and algorithm versions, source metadata, and selected KWX series.
2. Check schema and Chan-object compatibility: timestamps and timezones, ordering, IDs versus sequence positions, endpoint and source mappings, missing values, and unavailable feature groups.
3. Check read/write round trips for the table and companion data, including preservation of raw values, metadata, and feature mappings. Record unsupported fields or formats explicitly.

### 002.b — Recalculate and plot
1. Starting from the raw Kline columns, calculate merged Klines, Fenxing, Bi, and Xianduan using our Python implementation. Record the effective configuration for all four combinations of Bi strong/weak and Xianduan strong/weak.
2. Save plots for each level and overall views for all four combinations. Include full-range overviews and detailed windows covering the entire dataset; check window coverage and cross-window endpoints.
3. Save generated outputs under a separate run directory in `artifacts/mas/`, with commands, configuration, and an index linking results and charts.

### 002.c — Compare results and visualize differences
1. Compare raw values, then calculated structures at each level using source positions, timestamps, prices, and membership mappings rather than assuming IDs are shared. Report counts, endpoints, confirmation states, and uncovered ranges where applicable.
2. Classify differences as input, rule, implementation, or plotting differences. Keep unresolved cases explicit; a difference from KWX alone does not establish an error in either implementation.
3. Summarize differences by level and configuration, and highlight their locations in comparison charts. Link each finding to its source records and evidence.

## 003 — Execution log and result updates
**Status:** Not started.

Keep concise progress and results here, with detailed execution history in the task record and repository event log. Fill each subsection with the effective configuration, actual checks, results, output links, issues, and next action.

### 003.a — Input and compatibility checks → 002.a
| Item | Record |
|---|---|
| Input versions, hashes, and selected series | Pending |
| Schema, timestamps, IDs, endpoints, and missing values | Pending |
| Read/write round-trip checks | Pending |
| Results and evidence links | Pending |
| Issues and next action | Pending |

### 003.b — Recalculation and plots → 002.b
| Bi mode | Xianduan mode | Configuration and counts by level | Checks and chart coverage | Output links |
|---|---|---|---|---|
| strong | strong | Pending | Pending | Pending |
| strong | weak | Pending | Pending | Pending |
| weak | strong | Pending | Pending | Pending |
| weak | weak | Pending | Pending | Pending |

**Issues and next action:** Pending.

### 003.c — Comparison and difference summary → 002.c
| Level / configuration | Difference and location | Classification / unresolved question | Checks and evidence links | Next action |
|---|---|---|---|---|
| Pending | Pending | Pending | Pending | Pending |

### 003.d — Completion status
| Item | Record |
|---|---|
| Completed checks and acceptance results | Pending |
| Remaining issues and limitations | Pending |
| Result and chart index | Pending |
| Next action | Await user instruction to execute |

## 004 — 问题与待确认项

## 005 — 结论与下一步

## References
[1] [KWX004 — CC data import and ChanTable conversion](memoKWX_004_CCToChanTable.md)

[2] [Memo029 — Bi algorithm](memoWX_029_Chan_bi.md)

[3] [Memo030 — Xianduan algorithm](memoWX_030_Chan_xianduan.md)

[4] [Memo028 — Bi implementation](memoWX_028_biFamily.md)

[5] [Memo031 — Xianduan implementation](memoWX_031_xianduanFamily.md)
