# memo0021_class_csv_file_merged_kline_series

[class design] [data_io] [chan] [csv] [merged kline]

## 0. Scope And Purpose

> [purpose] Design `CsvFileMergedKlineSeries`, the CSV read/write object for
> persisted `MergedKlineSeries` results.

The first target operation is:

```text
MergedKlineSeries <-> CsvFileMergedKlineSeries <-> CSV artifact
```

> [decision] This memo is about CSV persistence for the merged K-line result.
> It does not add new Chan merge rules.

Must support:

```text
write MergedKlineSeries to CSV
read CSV back into MergedKlineSeries
preserve raw K-line fields
preserve merged tags and merged intervals
preserve group-first and group-extreme evidence
preserve the merge config used to create the result
produce a human-readable inspection table
```

> [boundary] Plotting and inference reports are required for the wider IO side,
> but they should not be methods on the CSV file class.

Keep the responsibilities separate:

```text
CsvFileMergedKlineSeries       CSV <-> MergedKlineSeries
MergedKlineSeriesChart         MergedKlineSeries -> chart artifact
MergedKlineInferenceReport     MergedKlineSeries -> human audit tables
```

> [reason] CSV is communication with a file format. Charting is visual
> communication. Inference reports explain the derivation. Mixing them into one
> class would make the IO layer procedural and hard to test.

## 1. Design Ideas

### 1.a Class Meaning

> [concept] `CsvFileMergedKlineSeries` means:
>
> A CSV file interface whose rows map to `MergedKline` and whose whole file maps
> to `MergedKlineSeries`.

It answers:

```text
How does Project 009 save and reload a Chan merged K-line result?
```

### 1.b Layer And Location

> [layer] Target layer:

```text
src/tradinglab/data_io/
```

> [path] Future source file:

```text
src/tradinglab/data_io/csv_file_merged_kline_series.py
```

> [path] Future test:

```text
tests/data_io/test_csv_file_merged_kline_series.py
```

> [decision] Implement as experiment first if the merged K-line logic remains
> under `experiments/chan_theory/`. Promote only after the class passes
> round-trip and human-evidence checks.

### 1.c Responsibility

`CsvFileMergedKlineSeries` owns:

```text
file path
encoding
CSV header contract
timestamp formatting and parsing
row-to-MergedKline conversion
MergedKlineSeries-to-row conversion
config column parsing
row number in error messages
safe overwrite behavior
```

It does not own:

```text
Chan inclusion merge calculation
Fenxing / Bi / Xianduan calculation
chart rendering
step-by-step inference trace generation
data repair
strategy logic
Qlib / DuckDB / Parquet conversion
```

> [boundary] The class reads and writes a derived result. It should not call
> `MergedKlineSeries.derive_from(...)` unless a future helper method explicitly
> says it is generating a fresh result from raw `KlineTSeries`.

### 1.d CSV Output Options

> [decision] `CsvFileMergedKlineSeries` should have its own file-output config.
> This is not `KlineMergeConfig`.

Two configs exist for different responsibilities:

```text
KlineMergeConfig                    governs Chan merge calculation
CsvFileMergedKlineSeriesConfig      governs CSV artifact shape
```

First CSV output options:

```text
output_profile = "basic"        machine-friendly row-aligned persistence
output_profile = "human_table"  memo0020-style inspection table
```

> [default] Use `basic` for read/write round trips.

> [option] Use `human_table` when the user wants a readable table for manual
> inspection. This profile is write/export first; do not make it the only
> readable format for `read()` until tests prove round-trip behavior.

### 1.e Basic CSV Contract

> [decision] The first CSV shape should be row-aligned with the original
> `KlineTSeries`.

One CSV row equals one original raw K-line row plus its merged interpretation.
This is the simple durable form.

Required columns:

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
```

Value conventions:

```text
timestamp                         ISO 8601 string
merged_direction                  up / down / NA
merge_state                       resolved / direction_unresolved
is_group_first                    true / false
is_group_extreme                  true / false
config_allow_equal_containment    true
config_direction_requires_strict_high_low
                                  true
config_undirected_collapse_policy wide_range
config_extreme_tie_policy         first / last
```

> [decision] Repeat config columns on each row for the first CSV artifact.
> This is redundant, but it makes the file self-contained and easy to inspect
> without opening a sidecar JSON.

> [future] If config repetition becomes noisy, introduce a record-level
> manifest later. Do not add that before the first CSV round trip works.

### 1.f Human Table Output

> [decision] Human output should use a table shape close to `memo0020`.

Human-table columns:

```text
Raw K
kLow
kHigh
MergedTag
mergedLow
mergedHigh
mergedDirection
mergeState
isGroupFirst
isGroupExtreme
Trace
```

Example row shape:

```text
K0,5,10,M0,7,10,up,resolved,True,True,"K0,K1,K2"
K1,6,9,M0,7,10,up,resolved,False,False,"K0,K1,K2"
K2,7,8,M0,7,10,up,resolved,False,False,"K0,K1,K2"
```

This is the same final mapping idea as:

```text
memo0020 section 0.b Final MergedKlineSeries raw-aligned fields
```

> [warning] Do not fake the step-by-step operation flow from the final CSV.
> A real operation-flow table needs trace events from the merge session, such
> as compare target, containment result, action, and direction after the step.

Future report boundary:

```text
MergedKlineInferenceReport
  Table 1: operation flow
  Table 2: final raw-aligned mapping
  Table 3: config/options used
  Table 4: unresolved-direction rows
```

### 1.g Relationship To Earlier Memos

> [source] `memo0016_class_csv_file_kline_t_series.md`
>
> CSV read/write belongs in a file-interface class, not in the domain series.

> [source] `memo0017_class_kline_t_series_chart.md`
>
> Plotting belongs in a visualization object, with file artifact as the default
> and optional local window display.

> [source] `memo0020_class_merged_kline_series.md`
>
> `MergedKlineSeries` is a KlineTSeries-like sequence whose rows carry
> `merged_tag`, `merged_low`, `merged_high`, `merged_direction`, `merge_state`,
> `is_group_first`, and `is_group_extreme`.

## 2. Class Proposal

### 2.a `CsvFileMergedKlineSeriesConfig`

```python
CsvOutputProfile = Literal["basic", "human_table"]

@dataclass(frozen=True)
class CsvFileMergedKlineSeriesConfig:
    output_profile: CsvOutputProfile = "basic"
    include_merge_config_columns: bool = True
    direction_none_value: str = "NA"
```

Members:

```text
output_profile
  "basic" for durable row-aligned read/write
  "human_table" for memo0020-style inspection output

include_merge_config_columns
  repeat KlineMergeConfig fields on every basic row

direction_none_value
  how None direction is written in CSV
```

> [small-first rule] Do not add timestamp, boolean, delimiter, or quoting
> options yet. Use ISO timestamps, lowercase true/false in basic CSV, and the
> standard Python CSV writer.

### 2.b `CsvFileMergedKlineSeries`

```python
@dataclass(frozen=True)
class CsvFileMergedKlineSeries:
    path: Path
    encoding: str = "utf-8"
    config: CsvFileMergedKlineSeriesConfig = field(
        default_factory=CsvFileMergedKlineSeriesConfig
    )
```

Members:

```text
path       CSV artifact path
encoding   text encoding for read/write
config     file-output options, not Chan merge rules
```

Class constants:

```text
BASIC_FIELDNAMES           durable read/write columns
HUMAN_TABLE_FIELDNAMES     memo0020-style inspection columns
TRUE_VALUE                 "true"
FALSE_VALUE                "false"
```

### 2.c Methods

```python
def exists(self) -> bool: ...

def read(self) -> MergedKlineSeries: ...

def write(self, series: MergedKlineSeries) -> None: ...

def write_human_table(self, series: MergedKlineSeries) -> None: ...
```

Method intent:

```text
exists()
  checks whether the CSV path exists.

read()
  reads rows, validates the header, parses config columns, converts each row to
  MergedKline, reconstructs source K-lines, and returns one MergedKlineSeries.

write(series)
  receives one MergedKlineSeries and writes the configured output profile. In
  the default basic profile, it writes rows in BASIC_FIELDNAMES order, repeats
  the merge config columns, and uses safe overwrite semantics.

write_human_table(series)
  explicit convenience method for memo0020-style inspection output. It writes
  HUMAN_TABLE_FIELDNAMES no matter what the instance config says.
```

Private helpers:

```text
_read_rows() -> tuple[dict[str, str], ...]
_write_rows(rows) -> None
_basic_row_from_merged_kline(series, row) -> dict[str, str]
_human_row_from_merged_kline(series, row) -> dict[str, str]
_merged_kline_from_row(row, row_number) -> MergedKline
_config_from_rows(rows) -> KlineMergeConfig
_parse_bool(value, column, row_number) -> bool
_parse_direction(value, row_number) -> ChanDirection | None
_parse_merge_state(value, row_number) -> MergeState
_parse_float(value, column, row_number) -> float
_parse_int(value, column, row_number) -> int
_parse_timestamp(value, row_number) -> datetime
```

> [style] Keep parsing helpers boring and explicit. CSV errors should tell the
> row number and column name.

### 2.d Read Shape

Read workflow:

```text
1. open CSV
2. validate required header columns
3. read all rows
4. parse and validate repeated config columns
5. convert each row into MergedKline
6. reconstruct source Kline rows from each MergedKline
7. create KlineTSeries from reconstructed raw rows
8. create MergedKlineSeries(klines, config, source_series)
9. let MergedKlineSeries.validate() enforce sequence invariants
```

> [decision] `read()` initially supports only the `basic` profile.

`human_table` is optimized for eyes, not durable reconstruction. Add
human-table read support only if a future task proves it is useful.

> [decision] Basic `read()` should return a full `MergedKlineSeries`, including
> `source_series`, because the CSV preserves raw OHLCV.

### 2.e Write Shape

Write workflow:

```text
1. receive MergedKlineSeries
2. call series.validate()
3. choose output profile from CsvFileMergedKlineSeriesConfig
4. convert each MergedKline into one CSV row for that profile
5. repeat series.config fields on each basic row
6. write to a temporary file beside the target
7. replace the target path after the full file is written
8. optionally read back in tests, not during normal write()
```

> [decision] `write()` should overwrite the target atomically enough for local
> project artifacts. Append mode is not part of the first design.

### 2.f Minimal Example

```python
from pathlib import Path

from experiments.chan_theory import MergedKlineSeries
from tradinglab.data_io import CsvFileKlineTSeries

raw_file = CsvFileKlineTSeries(Path("data_samples/kline/kline_15m_minimal.csv"))
raw_series = raw_file.read()
merged_series = MergedKlineSeries.derive_from(raw_series)

merged_file = CsvFileMergedKlineSeries(
    Path("artifacts/experiments/chan_theory/merged_kline_series.csv")
)
merged_file.write(merged_series)

reread = merged_file.read()
assert reread.klines == merged_series.klines
assert reread.config == merged_series.config
```

> [note] The import path for `MergedKlineSeries` is still experimental. Update
> the sample when the Chan classes move to `src/`.

Human-table export:

```python
human_file = CsvFileMergedKlineSeries(
    Path("artifacts/experiments/chan_theory/merged_kline_series_human.csv"),
    config=CsvFileMergedKlineSeriesConfig(output_profile="human_table"),
)
human_file.write(merged_series)
```

## 3. Implementation Result

> [result] `CsvFileMergedKlineSeries` is now implemented as experiment-only
> code.

Files:

```text
experiments/chan_theory/csv_file_merged_kline_series.py
experiments/chan_theory/test_csv_file_merged_kline_series.py
```

Implemented classes:

```text
CsvFileMergedKlineSeriesConfig
CsvFileMergedKlineSeries
```

Implemented behavior:

```text
basic CSV write
basic CSV read
basic write/read round trip
human_table CSV export
explicit read rejection for human_table CSV
config preservation through repeated basic CSV columns
source_series reconstruction from preserved raw OHLCV
```

Output artifacts generated from `data_samples/kline/kline_15m_minimal.csv`:

```text
artifacts/experiments/chan_theory/merged_kline_series_basic_sample.csv
artifacts/experiments/chan_theory/merged_kline_series_human_sample.csv
```

Large output artifacts generated from the preserved CC record:

```text
artifacts/experiments/chan_theory/merged_kline_series_basic_cc.csv
  10060 rows, about 1.8 MB
artifacts/experiments/chan_theory/merged_kline_series_human_cc.csv
  10060 rows, about 775 KB
```

Basic sample shape:

```text
raw_index,timestamp,symbol,period,source,...,merged_tag,merged_low,merged_high,...
0,2024-10-28T13:30:00+08:00,dce:KQ.m@m,15m,data_samples_kline,...,M0,2978.0,2990.0,...
1,2024-10-28T13:45:00+08:00,dce:KQ.m@m,15m,data_samples_kline,...,M1,2985.0,2992.0,...
```

Human-table sample shape:

```text
Raw K,kLow,kHigh,MergedTag,mergedLow,mergedHigh,mergedDirection,mergeState,isGroupFirst,isGroupExtreme,Trace
K0,2978.0,2990.0,M0,2978.0,2990.0,up,resolved,True,True,K0
K1,2985.0,2992.0,M1,2985.0,2992.0,up,resolved,True,True,K1
```

## 4. Verification

Minimum tests:

```text
write and read one small MergedKlineSeries
round-trip preserves every MergedKline row
round-trip preserves KlineMergeConfig
round-trip reconstructs source_series
blank/NA merged_direction becomes None
boolean columns parse only true/false
missing required column fails with column name
bad raw_index fails through MergedKlineSeries validation
mixed config columns fail before object creation
write uses stable FIELDNAMES order
large CC record exports basic and human_table CSV
large CC record basic CSV reads back
```

Implemented test result:

```text
CsvFileMergedKlineSeries tests: 11 passing
all experiment tests: 31 passing
source baseline tests: 42 passing
```

Large CC timing on 2026-09-04:

```text
raw rows: 10060
merged groups: 6200
raw read: 0.030s
merge: 0.045s
basic write: 0.064s
basic read: 0.089s
human_table write: 0.037s
total large test: 0.287s
```

> [implementation note] The first large run exposed a trace/validation hot
> path. `MergedKlineSeries` now groups raw indices by merged tag in one pass
> during trace and group-flag validation.

### 4.a Change Record

> [change] 2026-09-04 large CSV pass

What changed:

```text
Code:
  added CsvFileMergedKlineSeriesConfig
  added CsvFileMergedKlineSeries
  exported both through experiments.chan_theory

CSV behavior:
  basic profile writes and reads MergedKlineSeries
  human_table profile writes inspection CSV only
  read() rejects human_table CSV explicitly

Large-record test:
  added CC record test with 10060 raw rows and 6200 merged groups
  verifies basic CSV writes, reads back, and preserves the merged series
  verifies human_table CSV writes 10060 inspection rows

Performance fix:
  replaced repeated full-series trace scans with one-pass tag grouping
  moved large test from about 55.9s to about 0.287s

Artifacts:
  moved small sample basic/human CSV outputs to experiment artifact folder
  moved large CC basic/human CSV outputs to experiment artifact folder

Docs:
  updated memo0021 with implementation, artifacts, timing, and test result
  updated classDesign, status, distilled memory, 7.4 phase doc, README, log
```

Human artifact check:

```text
open artifacts/experiments/chan_theory/merged_kline_series_basic_cc.csv
confirm K0/K1/K2 rows show original high/low beside merged high/low
confirm M tags are readable
confirm config columns explain the rule profile
```

## 5. Open Questions

> [open] Should the first implementation live under `experiments/chan_theory/`
> or go directly to `src/tradinglab/data_io/`?

Current leaning:

```text
experiment first, because MergedKlineSeries itself is still experiment-only
```

> [open] Should a future report write Markdown, CSV, or both?

Current leaning:

```text
Markdown for human narrative
CSV for final row-aligned data
```

> [open] Should config columns stay repeated forever?

Current leaning:

```text
repeat now for self-contained inspection; move to manifest later if needed
```
