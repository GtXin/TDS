# memo0024_class_csv_file_fenxing_series

[class design] [data_io] [chan] [csv] [fenxing]

## 0. Scope And Purpose

> [purpose] `CsvFileFenxingSeries` follows memo0021's CSV file
> pattern for saving and reloading the raw-aligned Fenxing result.

```text
FenxingSeries <-> CsvFileFenxingSeries <-> basic CSV
FenxingSeries  -> CsvFileFenxingSeries  -> human_table CSV
```

Must preserve every original K row, its merge fields, its `fx_type`, and
both calculation configs. Read returns a complete `FenxingSeries`, including
its `MergedKlineSeries` source and the underlying `KlineTSeries`.

> [decision] Two output profiles; only basic is readable. Use two file
> objects with different paths when keeping both outputs.

> [boundary] No new detection rules, data repair, charting, Bi selection,
> or streaming logic. The file object persists a result; it does not own
> the Chan calculation.

## 1. Design Ideas

### 1.a Class Meaning

One file represents one `FenxingSeries`. One basic CSV row represents one
original K row with merge annotations and its M group's center label.

```text
K2 -> M2 -> top
K3 -> M2 -> top
```

These are two saved raw rows but one Fenxing center. Do not collapse the
file into a sparse list of tops and bottoms.

### 1.b Layer And Location

Experiment first, alongside the current Chan classes:

```text
experiments/chan_theory/csv_file_fenxing_series.py
experiments/chan_theory/test_csv_file_fenxing_series.py
```

Both the file class and its config belong in `csv_file_fenxing_series.py`.
Future source location: `src/tradinglab/data_io/`, after explicit promotion.
Do not add another folder or a separate config module now.

### 1.c Responsibility

The file object owns path, encoding, CSV columns, value parsing/formatting,
row-numbered errors, profile selection, and safe replacement of the file.

The series owns validation, center classification, and evidence. The reader
constructs saved objects directly; it must not call `derive_from()` to replace
bad saved labels with newly calculated ones. Constructor validation may
recheck the rule and reject a mismatch. That is verification, not repair.

### 1.d Three Config Responsibilities

```text
file.config                          CsvFileFenxingSeriesConfig
series.config                        FenxingConfig
series.source_series.config          KlineMergeConfig
```

- File config chooses output shape.
- Fenxing config records strict comparisons and unresolved-window policy.
- Merge config records the upstream merge and extreme-tie rules.

Repeat both calculation configs on every basic row, as memo0021 does for
merge config. The file is self-contained; no JSON sidecar or external source
CSV is needed to reload it. File-output config is not a calculation config.

### 1.e Basic CSV Contract

Keep memo0021's 21 columns in their existing order, then append three:

```text
raw_index
timestamp
symbol
period
source
open
high
low
close
volume
merged_tag
merged_low
merged_high
merged_direction
merge_state
is_group_first
is_group_extreme
config_allow_equal_containment
config_direction_requires_strict_high_low
config_undirected_collapse_policy
config_extreme_tie_policy
fx_type
config_fenxing_strict_extrema
config_fenxing_unresolved_policy
```

Value conventions:

```text
timestamp                              ISO 8601, retain time and UTC offset
merged_direction                       up / down / NA
merge_state                            resolved / direction_unresolved
is_group_first / is_group_extreme       true / false
fx_type                                top / bottom / NA
config_allow_equal_containment         true
config_direction_requires_strict_high_low  true
config_undirected_collapse_policy       wide_range
config_extreme_tie_policy               first / last
config_fenxing_strict_extrema           true
config_fenxing_unresolved_policy        skip_windows
```

`NA` means Python `None` only in the nullable direction/label columns.
Blank required cells are errors, not an alternative spelling of `None`.
Keep finite numeric values without display rounding; reject invalid OHLCV.
ISO timestamps preserve the instant/offset, not an IANA timezone name.

> [decision] Config columns are mandatory and uniform across the file.
> Keep the existing merge column names; the `config_fenxing_` prefix makes
> the added stage explicit. Missing Fenxing columns are an error, not a
> request to derive Fenxing from an older merged-only CSV.

### 1.f Human Table Output

Keep memo0021's inspection columns and append the Fenxing interpretation:

```text
Raw K, kLow, kHigh, MergedTag, mergedLow, mergedHigh,
mergedDirection, mergeState, isGroupFirst, isGroupExtreme, Trace,
fxType, fenxingPrice, turningRawK, fxOutcome
```

`Trace` lists the raw members of the current M group, not a separate stored
three-group structure. `fxOutcome` comes from `series.evidence_table()`:
`top`, `bottom`, `none`, `edge`, or `unresolved`.

Excerpt from memo0023 section 0.c; other columns omitted here only:

| Raw K | kLow | kHigh | MergedTag | mergedLow | mergedHigh | fxType | fenxingPrice | turningRawK | fxOutcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K2 | 9 | 14 | M2 | 10 | 14 | top | 14 | K2 | top |
| K3 | 10 | 13 | M2 | 10 | 14 | top | 14 | K2 | top |

The center price and anchor repeat because both rows belong to M2.
For unmarked groups, `fxType`, `fenxingPrice`, and `turningRawK` are `NA`;
`fxOutcome` explains whether there was no turn, an edge, or unresolved input.

> [boundary] This is a final raw-row inspection table, not a chronological
> operation log. Full three-group comparison reports remain separate.
> Compute the evidence and trace lookup once per export, not once per row.

### 1.g Sources

- [memo0021](memo0021_class_csv_file_merged_kline_series.md): basic read/write,
  export-only human table, repeated config, and local atomic replacement.
- [memo0023](memo0023_class_fenxing_series.md): actual Fenxing row, config,
  source-chain, evidence, and price-anchor contracts.
- `experiments/chan_theory/csv_file_merged_kline_series.py`: existing CSV
  parser/writer conventions; inspect before implementing, not blindly copy.
- `experiments/chan_theory/fenxing_series.py`: saved labels must pass the
  series constructor's source and neighbor-rule validation.

## 2. Class Proposal

### 2.a `CsvFileFenxingSeriesConfig`

```python
@dataclass(frozen=True)
class CsvFileFenxingSeriesConfig:
    output_profile: Literal["basic", "human_table"] = "basic"
```

`__post_init__()` validates the profile. Keep `NA`, booleans, delimiter,
timestamp formatting, and mandatory config columns fixed in this first
version. Unlike memo0021's broader config shape, no redundant on/off switch
is needed for columns that cannot be omitted.

### 2.b `CsvFileFenxingSeries`

```python
@dataclass(frozen=True)
class CsvFileFenxingSeries:
    path: Path
    encoding: str = "utf-8"
    config: CsvFileFenxingSeriesConfig = field(
        default_factory=CsvFileFenxingSeriesConfig
    )
```

Class constants: `BASIC_FIELDNAMES`, `HUMAN_TABLE_FIELDNAMES`, `NONE_VALUE`,
`TRUE_VALUE`, and `FALSE_VALUE`. The two field-name constants fix export order.

### 2.c Methods

```text
exists() -> bool
read() -> FenxingSeries
write(series: FenxingSeries) -> None
write_human_table(series: FenxingSeries) -> None
```

- `read()`: accepts only basic CSV, regardless of the configured write profile.
- `write()`: validates the series, then writes the selected profile.
- `write_human_table()`: explicitly exports the human profile to this path.
- Calling both write methods on the same file replaces that file; it does
  not automatically create a second artifact.

Private helpers should separate header checks, config parsing, row parsing,
row formatting, and atomic writing. Follow existing CSV conventions without
making Fenxing's file class inherit an unrelated merged-file public API or
creating an unused generic persistence framework.

### 2.d Read Shape

1. Open the file; reject missing/duplicate columns, human-table headers,
   empty data, extra cells, and missing cell values. Header order may vary;
   the initial schema otherwise requires exactly the declared basic columns.
2. Parse both calculation configs and require consistent values on every row.
3. Parse saved rows into `Fenxing` objects, including the saved `fx_type`.
4. Recover raw rows through `to_raw_kline()` and create `KlineTSeries`.
5. Recover merge rows through `to_merged_kline()` and construct
   `MergedKlineSeries(merge_rows, merge_config, raw_series)`.
6. Construct `FenxingSeries(saved_rows, fenxing_config, merged_series)`.
7. Reject source/rule inconsistencies. Report CSV row/column for parsing
   errors and relevant raw/M indices for cross-row validation failures.

No source file lookup, merge rerun, detection rerun to replace labels, or
fallback to defaults for missing calculation config.

### 2.e Write Shape

1. Require a `FenxingSeries`; validate it before touching the existing file.
2. Format all basic rows, or build the human evidence/trace lookup once.
3. Create parent folders if needed; write a temporary file beside the target.
4. Replace the target only after a successful complete write; remove temporary
   output on failure while preserving the existing target.

This provides local atomic replacement, not a crash-durable storage guarantee.
Append mode, partial saves, and automatic read-back are not first-version APIs.

### 2.f Minimal Example

Use with `fenxings`, the result from memo0023:

```python
from pathlib import Path
from experiments.chan_theory.csv_file_fenxing_series import (
    CsvFileFenxingSeries, CsvFileFenxingSeriesConfig,
)

folder = Path("artifacts/experiments/chan_theory")
basic = CsvFileFenxingSeries(folder / "fenxing_series_basic_sample.csv")
basic.write(fenxings)
loaded = basic.read()
assert loaded.klines == fenxings.klines
assert loaded.config == fenxings.config
assert loaded.source_series == fenxings.source_series

human = CsvFileFenxingSeries(
    folder / "fenxing_series_human_sample.csv",
    config=CsvFileFenxingSeriesConfig(output_profile="human_table"),
)
human.write(loaded)
```

## 3. Implementation Result

> [status] Implemented and verified on 2026-09-10 under staged items
> 7.4.45-7.4.50. Experiment-only; no source promotion.

### 3.a Files And Behavior

```text
experiments/chan_theory/csv_file_fenxing_series.py
  CsvFileFenxingSeriesConfig and CsvFileFenxingSeries
experiments/chan_theory/test_csv_file_fenxing_series.py
  35 focused tests
```

Both classes are exported through `experiments.chan_theory`.

- Basic writes preserve 24 columns; reads restore saved rows, both configs,
  and the source chain. Reader validation never calls either `derive_from()`.
- The 15-column human profile is export-only. Group evidence/trace is computed
  once, then repeated across its raw rows; no per-row full-series anchor scan.
- Config, header, value, identity, row-order, and group-flag errors are rejected.
  `FenxingSeries` gained raw-index/M-tag context in label and group-bound errors;
  the detection rules are unchanged.
- Temporary-file replacement preserves the existing target on write or replace
  failures. Invalid input is rejected before opening a temporary output.

If the supplied merged series has `source_series=None`, read reconstructs the
missing `KlineTSeries` from saved raw rows. Row/config equality is preserved;
the loaded source chain is more complete, so whole-object equality is not the
right check for that particular input. Normal derived inputs round-trip whole.

### 3.b Saved Artifacts

Actual output folder:

```text
artifacts/experiments/chan_theory/fenxing_series_basic_sample.csv
artifacts/experiments/chan_theory/fenxing_series_human_sample.csv
artifacts/experiments/chan_theory/fenxing_series_basic_cc.csv
artifacts/experiments/chan_theory/fenxing_series_human_cc.csv
```

| File | Data rows | Bytes |
| --- | --- | --- |
| `fenxing_series_basic_sample.csv` | 2 | 748 |
| `fenxing_series_human_sample.csv` | 2 | 300 |
| `fenxing_series_basic_cc.csv` | 10,060 | 1,961,443 |
| `fenxing_series_human_cc.csv` | 10,060 | 988,752 |

The minimal checked-in sample has only two bars: two M groups and no centers.
Use the full CC file to inspect actual Fenxing. Synthetic tests separately
cover the small numeric top/bottom and multirow-center examples.

First full-record center: K1/K2/K3 belong to top group M1; turning price 2998,
anchor K1. The human output repeats that group annotation on all three rows.

These are generated local artifacts, ignored by Git. Raw inputs remain in
`data_samples/kline/` and `records/cc/kline-to-zoushi-001/`, unchanged.

### 3.c Reproduce The Files

Run this Python snippet from the repository root using the existing `.venv`
with `PYTHONPATH=src`:

```python
from pathlib import Path
from experiments.chan_theory import (
    CsvFileFenxingSeries, FenxingSeries, MergedKlineSeries,
)
from tradinglab.data_io import CsvFileKlineTSeries

folder = Path("artifacts/experiments/chan_theory")
cases = (
    ("sample", Path("data_samples/kline/kline_15m_minimal.csv")),
    ("cc", Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv")),
)
for name, input_path in cases:
    raw = CsvFileKlineTSeries(
        input_path, default_source=f"fenxing_fixture_{name}",
    ).read()
    series = FenxingSeries.derive_from(MergedKlineSeries.derive_from(raw))
    basic = CsvFileFenxingSeries(folder / f"fenxing_series_basic_{name}.csv")
    human = CsvFileFenxingSeries(folder / f"fenxing_series_human_{name}.csv")
    basic.write(series)
    loaded = basic.read()
    assert loaded == series
    human.write_human_table(loaded)
    print(name, loaded.count, loaded.merged_count, loaded.fenxing_count)
```

## 4. Verification

> [test intent] A saved result must reload with the same rows, rules, and
> source chain. Human formatting must not change what the result means.

### 4.a Round Trip

Save/read a small top/bottom example and memo0023's multirow center.
Compare every raw/merge/label field, timestamps, both calculation configs,
source chain, counts, evidence, and first/last anchor behavior.
Include a no-turn result and an unresolved result; neither loses raw rows.

### 4.b Invalid Input

Reject bad headers, missing cells, malformed numbers/timestamps/booleans,
unsupported config, inconsistent repeated configs, bad row order, and
invalid labels. A fabricated top, missing valid top, or mixed labels within
one M group must fail rather than be silently recalculated.

### 4.c Profiles And File Safety

Check fixed column order, basic-only reads, explicit human export, and two
separate output paths. Human rows must preserve original prices, repeat M
labels correctly, and explain `None` through `fxOutcome`. Test failed writes
leave the previous target intact and remove temporary files.

### 4.d Full Input Chain

```text
CC raw CSV -> KlineTSeries -> MergedKlineSeries -> FenxingSeries
          -> basic CSV -> reloaded FenxingSeries -> human_table CSV
```

Verified checkpoint: 10,060 raw rows, 6,200 merged groups, 3,027 centers;
both CSV profiles contain 10,060 data rows. Compare complete reloaded rows,
not only counts. Time raw read, merge, detection, basic write/read, and human
export separately. Rerun existing experiments and source tests.

### 4.e Commands And Results

```zsh
PYTHONPATH=src .venv/bin/python -m unittest experiments.chan_theory.test_csv_file_fenxing_series
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

```text
Fenxing CSV tests:     35 passed in 0.854s (final focused rerun)
All experiment tests: 133 passed in 2.733s (includes the CSV tests)
Source tests:         42 passed in 2.490s
```

Coverage includes exact round trips, missing raw-source reconstruction,
first/last top and bottom anchors, no-turn/unresolved states, source text with
commas/quotes/newlines/Unicode, timezone offsets, reordered headers, damaged
CSV, inconsistent configs, forged/missing labels, and failed writes/replacements.
Tests mock both derivation entry points to prove reads do not regenerate data.

Actual full-record artifact-generation timings:

```text
raw CSV read: 0.0276s
merge:        0.0405s
Fenxing:      0.1272s
basic write:  0.1207s
basic read:   0.1855s
human write:  0.1310s
```

Timings include each operation's validation and are machine-specific, not
benchmarks. Saved basic files were read back and compared with the complete
input result; both human files were checked for row and center counts.

> [boundary] No new Fenxing plotting, comparison-report export, crash-durable
> storage, or streaming behavior was implemented or tested. Existing chart
> tests ran only as regressions. No dependencies installed or environment repaired.

### 4.f Change Record

- Added the file/config classes, experiment exports, and 35 tests.
- Generated and inspected four persistent CSV artifacts in the existing folder.
- Added index context to two Fenxing validation messages; no calculation change.
- Updated class inventory, README, status, roadmap, staged plan, execution
  summary, and master log. Earlier memos remain historical snapshots.

## 5. Open Questions

- Keep full comparison reports separate from this final-mapping CSV; decide
  Markdown/CSV report shape only when that inspection task is requested.
- Keep repeated calculation config for now. A versioned manifest or broader
  schema migration policy can follow once there is a real compatibility need.
