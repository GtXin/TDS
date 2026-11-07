# memo0023_class_fenxing_series

[class design] [chan] [fenxing] [series first]

## 0. Scope And Purpose

> [purpose] Add Fenxing / 分型 annotations while preserving the original
> K0, K1, K2, ... sequence, following memo0020's raw-row design.

```text
MergedKlineSeries + FenxingConfig -> FenxingSeries
```

It covers:

- `Fenxing`: one original K-line row, its merge fields, and `fx_type`.
- `FenxingSeries`: the complete raw-aligned sequence and its derivation.
- `FenxingConfig`: the strict detection rule profile.

> [decision] Store which M group is a top or bottom. Its left and right
> neighbors follow from the ordered M sequence; no F0/F1 IDs, three-bar
> membership lists, or separate stored structure objects are needed.

> [non-goal] No Bi selection, trading signals, CSV methods, rendering,
> streaming updates, or source promotion.

> [source] Input shape: [memo0020](memo0020_class_merged_kline_series.md).
> Series/config ownership: [memo0019](memo0019_InterfaceChan.md).
> Reference context: [memo0012](memo0012_cc_csv_to_zoushi_reference.md) and
> [memo0015](memo0015_oop_trading_architecture.md). Appendix A preserves the
> supplied KWX code. The user chose the center-tag design on 2026-09-10.

> [theory wording] 缠中说禅《教你炒股票62：分型、笔与线段》：
> “只看K线高低点”。[原文转载](https://chanlun108.cn/chanzhongshuochan108ke/62.html)

### 0.a Top Operation Rule

> [concept] A theoretical Fenxing spans three neighboring merged groups.
> Project 009 records that relationship by marking its middle group.

For left, middle, and right M groups `A, B, C`:

```text
top / 顶分型:
    B.merged_high > A.merged_high and B.merged_high > C.merged_high
    B.merged_low  > A.merged_low  and B.merged_low  > C.merged_low

bottom / 底分型:
    B.merged_high < A.merged_high and B.merged_high < C.merged_high
    B.merged_low  < A.merged_low  and B.merged_low  < C.merged_low
```

All four comparisons must pass. Equality does not qualify. Repeat the middle
group's result on every raw row carrying its `merged_tag`.

```text
fx_type = "top"       this row's M group is a top center
fx_type = "bottom"    this row's M group is a bottom center
fx_type = None        this row's M group has no detected center label
```

> [boundary] Compare distinct M groups using merged bounds. Original
> `high/low` remain raw prices. Three raw rows sharing M0 are one group.

### 0.b Two-Table Example

Whole raw sequence, extending memo0020 by K10 to include a bottom.
Intervals are `[low, high]`; OHLCV, timestamps, source, and other merge fields
are preserved but omitted here to keep the table readable.

| Raw K | Original interval | M tag | Merged interval | Group first | fx_type |
| --- | --- | --- | --- | --- | --- |
| K0 | `[5,10]` | M0 | `[7,10]` | True | None |
| K1 | `[6,9]` | M0 | `[7,10]` | False | None |
| K2 | `[7,8]` | M0 | `[7,10]` | False | None |
| K3 | `[9,12]` | M1 | `[10,12]` | True | None |
| K4 | `[10,11]` | M1 | `[10,12]` | False | None |
| K5 | `[11,14]` | M2 | `[11,14]` | True | top |
| K6 | `[8,13]` | M3 | `[8,12]` | True | None |
| K7 | `[9,12]` | M3 | `[8,12]` | False | None |
| K8 | `[7,10]` | M4 | `[7,10]` | True | None |
| K9 | `[6,9]` | M5 | `[6,9]` | True | bottom |
| K10 | `[8,11]` | M6 | `[8,11]` | True | None |

Window-by-window inference:

| Window | Middle | High comparison | Low comparison | Middle label |
| --- | --- | --- | --- | --- |
| M0, M1, M2 | M1 | `10 < 12 < 14` | `7 < 10 < 11` | None: rising |
| M1, M2, M3 | M2 | `14 > 12,12` | `11 > 10,8` | top |
| M2, M3, M4 | M3 | `14 > 12 > 10` | `11 > 8 > 7` | None: falling |
| M3, M4, M5 | M4 | `12 > 10 > 9` | `8 > 7 > 6` | None: falling |
| M4, M5, M6 | M5 | `9 < 10,11` | `6 < 7,8` | bottom |

`count=11`, `merged_count=7`, `fenxing_count=2`.
M0 and M6 have no complete window; their labels are `None`.

### 0.c One Center Tag, Original Rows

A separate complete example shows a top spanning multiple raw rows.
Each interval below is `[low, high]`.

```text
Raw row          K0       K1       K2       K3       K4
Original range  [5,10]   [8,12]   [9,14]  [10,13]  [7,11]
M tag            M0       M1       M2       M2       M3
Merged range    [5,10]   [8,12]  [10,14]  [10,14]  [7,11]
fx_type          None     None     top      top      None
```

M1/M2/M3 establish the top. Both K2 and K3 carry `fx_type="top"`, but
there is only one detected top: M2. Its price is 14, contributed by K2.

> [decision] A row tag means its M group is the center. It does not mean
> every tagged raw row is a separate top or contributed the extreme.

### 0.d Numeric Recipe

1. Validate the complete `MergedKlineSeries`; retain original row order.
2. Build M-group representatives and raw membership once.
3. Initialize one `None` label per M group.
4. For each interior group `j`, examine `(j-1, j, j+1)`.
5. Skip a window touching `direction_unresolved`; never join across it.
6. Apply the strict comparisons and assign `top`, `bottom`, or `None`
   to group `j`.
7. Create one new `Fenxing` row for every input row, copying all original
   and merge fields and adding its group's label.
8. Return the complete `klines` tuple with its source series and config.

No-turn input still returns every row. No labeled group means
`fenxing_count=0`, not an empty raw sequence.

## 1. Design Ideas

### 1.a Position In The Chan Chain

```text
KlineTSeries -> MergedKlineSeries -> FenxingSeries -> future BiSeries
```

Each stage preserves the raw axis and adds its own interpretation. Which
centers form valid Bi remains a later responsibility.

### 1.b Structure And Series

> [decision] Follow the same storage pattern as memo0020: `klines` is a
> full sequence of enriched rows. The series owns the computation.

```text
Fenxing         raw Kline fields + existing merge fields + fx_type
FenxingSeries   klines + config + source_series
```

In this project, the class name `Fenxing` means a Fenxing-annotated row,
including rows with no detected center. It differs from KWX's singular
three-bar result record in Appendix A.

This supersedes the earlier sparse `items` proposal in this memo. Memo0019
remains a historical architecture snapshot; its sequence/config ownership
still applies.

### 1.c Config

```text
strict_extrema = True                  only supported value
unresolved_policy = "skip_windows"    only supported value
```

Reject other values explicitly. `FenxingSeries.config` records this stage's
profile; `source_series.config` retains the merge profile. Future
`ChanConfig.fenxing` can provide the same config.

No new tie option is needed for detection. A price-anchor lookup follows
the upstream `extreme_tie_policy` when multiple raw rows contributed an
equal extreme.

> [decision] Define `FenxingConfig` in `fenxing_series.py`, following
> `KlineMergeConfig` in `merged_kline_series.py`. It remains a separate
> frozen class, owned once through `FenxingSeries.config`; no separate
> config file and no config copied into individual rows.

### 1.d Operation

Construction validates known state. `derive_from()` performs the scan and
constructs the annotated rows; it never mutates the input.

Group once, scan once, annotate once: O(N + M) work and O(N + M) working/output
storage for N raw rows and M groups. Do not repeatedly regroup the entire
input for each candidate.

### 1.e Time And Display Anchors

> [decision] Every row keeps its original `raw_index` and `timestamp`.
> Neither field is replaced by an M-group or Fenxing timestamp.

- Group identity: `merged_tag`.
- Group-start anchor: the row with `is_group_first=True`.
- Top price: middle group's `merged_high`.
- Bottom price: middle group's `merged_low`.
- Price anchor: a raw row in the middle group that contributed that bound;
  choose first/last according to the existing merge tie rule.

A chart can use raw indices for evenly spaced trading bars, or timestamps
for an elapsed-time axis. Detection does not select the axis or draw markers.

> [note] Repeated center labels must produce one marker per M group, not one
> per raw row. The extreme may occur after the group's first row.

Right-neighbor evidence is required to detect a center. Its timestamp is not
the turning timestamp. Full-history output does not establish live-time
availability; streaming finality remains outside this first design.

### 1.f Trace And Checkpoint

The neighbors of marked Mj are always M(j-1) and M(j+1). Their original
members are available through `source_series.trace`; no duplicate stored
three-group trace is needed.

A group can participate in three overlapping windows, but can be the middle
of only one. Center tagging avoids overlapping membership lists.

```text
Reference target:
10060 raw rows -> 6200 merged groups -> 3027 marked center groups
```

Count only group-first rows with non-None `fx_type`. The 3,027 external
target now matches the experiment result; chapter 4 records its limits.

## 2. First Class Shape

### 2.a `Fenxing`

Frozen row dataclass, with a flat field contract like `MergedKline`.
The implementation inherits `MergedKline` fields and adds only `fx_type`;
the expanded contract below shows all available fields:

```python
@dataclass(frozen=True)
class Fenxing:
    symbol: str
    period: str
    source: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    raw_index: int
    merged_tag: str
    merged_low: float
    merged_high: float
    merged_direction: ChanDirection | None
    merge_state: MergeState
    is_group_first: bool
    is_group_extreme: bool
    fx_type: Literal["top", "bottom"] | None = None
```

Members:

```text
symbol / period / source / timestamp   original raw identity and provenance
open / high / low / close / volume     original raw OHLCV
raw_index                             original K0/K1/K2 position
merged_tag                            owning M0/M1/M2 group
merged_low / merged_high              existing merged bounds
merged_direction / merge_state        existing merge interpretation
is_group_first / is_group_extreme     existing first/extreme annotations
fx_type                               owning group's center classification
```

> [decision] `fx_type` is the only newly stored field. `high/low` continue
> to mean original raw prices, never the three-group range.

Methods / properties:

```text
from_merged_kline(row, fx_type=None) -> Fenxing
validate() -> None
to_merged_kline() -> MergedKline
to_raw_kline() -> Kline
is_top -> bool
is_bottom -> bool
fenxing_price -> float | None
```

- `from_merged_kline()`: preserve every input field exactly; add the label.
- `validate()`: validate inherited field meanings and the label's type/value.
  A row alone cannot prove its neighbors satisfy the rule.
- Conversion methods remove only annotations belonging to later stages.
- `is_top/is_bottom`: derived from `fx_type`, not extra stored booleans.
- `fenxing_price`: `merged_high` for top, `merged_low` for bottom, otherwise
  `None`. This group price is repeated on member rows; it is not necessarily
  the current raw row's high or low.

No detector, read/write, or plotting methods belong to this row object.

### 2.b `FenxingSeries`

```python
@dataclass(frozen=True)
class FenxingSeries:
    klines: tuple[Fenxing, ...]
    config: FenxingConfig
    source_series: MergedKlineSeries
```

Methods / properties:

```text
derive_from(source_series, config=None) -> FenxingSeries
validate() -> None
count / raw_count -> int
merged_count / fenxing_count -> int
is_empty -> bool
symbol / period -> str
start_timestamp / end_timestamp -> datetime
fenxing_merged_indices -> tuple[int, ...]
skipped_middle_indices -> tuple[int, ...]
turning_raw_index(merged_index) -> int | None
evidence_table() -> tuple[dict[str, object], ...]
to_list() -> list[Fenxing]
raw_klines() -> tuple[Kline, ...]
timestamps() -> tuple[datetime, ...]
closes() -> tuple[float, ...]
```

- `derive_from()`: group the input, classify middle groups, expand labels to
  every original row.
- `validate()`: require identical row count, order, raw fields, and merge
  fields versus `source_series`; check group-uniform labels and recompute
  their agreement with the configured rule.
- `count/raw_count`: number of retained raw rows. `fenxing_count`: number of
  marked M groups, never number of tagged rows.
- `is_empty`: raw-row emptiness, not absence of turns. Current merged input
  rejects empty rows, so a valid first-version output is nonempty.
- `start_timestamp/end_timestamp`: original input coverage, even with no turns.
- `fenxing_merged_indices`: ordered marked M indices, derived without storing
  a second result list.
- `skipped_middle_indices`: interior M indices whose windows touch unresolved
  groups. First/last groups are separately identifiable as edges.
- `turning_raw_index()`: for a labeled group, find the raw row contributing
  its relevant merged bound; apply the source merge tie rule. Return `None`
  for an unmarked group; raise `IndexError` for an invalid M index. Do not
  blindly equate the group-start flag with the price anchor.
- `evidence_table()`: one row per M group with its window, bounds,
  comparisons, and outcome: `top`, `bottom`, `none`, `edge`, or
  `unresolved`. Return structured values; file formatting belongs elsewhere.
- `to_list/raw_klines/timestamps/closes`: match the existing merged-series
  convenience methods without changing the original time axis.

> [state] `fx_type=None` is a classification, not proof that a complete
> comparison occurred. Derived evidence distinguishes an ordinary non-turn,
> a missing neighbor, and unresolved merge direction without adding row tags.

### 2.c `FenxingConfig`

```python
@dataclass(frozen=True)
class FenxingConfig:
    strict_extrema: bool = True
    unresolved_policy: Literal["skip_windows"] = "skip_windows"
```

`__post_init__()` validates the supported profile. Config owns no market
data, detection state, plotting settings, or upstream merge rules.

Use:

```python
fenxings = FenxingSeries.derive_from(merged, FenxingConfig())
for row in fenxings.klines:
    if row.is_group_first and row.fx_type is not None:
        print(row.merged_tag, row.fx_type, row.fenxing_price)
```

This prints each detected center once while all raw rows remain accessible.

## 3. Implementation Result

> [status] Implemented and verified on 2026-09-10; experiment-only.

Files:

```text
experiments/chan_theory/fenxing.py
experiments/chan_theory/fenxing_series.py
experiments/chan_theory/test_fenxing_series.py
```

Experiment first. Source promotion follows a later explicit decision after
implementation and boundary tests settle.

### 3.a Class Operation

- `Fenxing` inherits the frozen `MergedKline` fields and adds `fx_type`.
  Conversion uses declared dataclass fields, so original values are copied
  without rebuilding or retiming a candle.
- `FenxingConfig` lives beside `FenxingSeries` in `fenxing_series.py`.
  The default is created when omitted; an explicit config instance is retained.
- `derive_from()` validates/group-checks input, compares distinct M groups,
  then repeats each center label across that group's raw rows.
- `validate()` checks every row against its source and the neighbor rule.
  It also rejects inconsistent upstream group bounds and missing raw price
  contributors. It does not rerun or change the merge algorithm.
- `evidence_table()` returns one dictionary per M group. Comparisons are
  ordered high-vs-left, high-vs-right, low-vs-left, low-vs-right. Edge and
  unresolved windows have no evaluated comparison tuples.
- `turning_raw_index()` looks for the relevant raw high/low contributor,
  using the upstream first/last tie policy. It does not assume the group's
  first row is the turning row.

Derivation and full evidence generation are O(N + M). A single anchor lookup
uses the upstream raw-group lookup, currently O(N); use `evidence_table()`
when inspecting every anchor instead of calling the lookup in a large loop.

### 3.b Sample Use

From the repository root, with `PYTHONPATH=src`:

```python
from pathlib import Path
from tradinglab.data_io import CsvFileKlineTSeries
from experiments.chan_theory import (
    FenxingConfig, FenxingSeries, MergedKlineSeries,
)

raw = CsvFileKlineTSeries(
    Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv")
).read()
merged = MergedKlineSeries.derive_from(raw)
fenxings = FenxingSeries.derive_from(merged, FenxingConfig())
print(fenxings.count, fenxings.merged_count, fenxings.fenxing_count)
print(fenxings.evidence_table()[1])
```

Count output: `10060 6200 3027`. Package exports are in the experiment
`__init__.py`; stable `tradinglab` exports remain unchanged.

## 4. Test Session

> [test intent] Preserve every original K row; classify distinct M groups;
> prove each center label from its immediate neighbors.

> [status] 34 focused tests passed on 2026-09-10. These are executable tests,
> not only a checklist; source and experiment regressions also passed.

Actual test file:

```text
experiments/chan_theory/test_fenxing_series.py
```

### 4.a Shape

Verify one output row per input row, immutable fields, accepted label values,
and exact round trip to merged and raw K-lines.

### 4.b Derived Views

Section 0.b must retain 11 raw rows, seven groups, and two marked centers.
Section 0.c must repeat `top` on K2/K3 while counting M2 only once.
A no-turn series retains its full count and timestamp coverage.

### 4.c Fenxing Rule

Check strict top/bottom, rising/falling, equality rejection, and alternating
turns. Overlapping windows must not overwrite a group's own center label.
Valid changes to raw open/close/volume must not affect classification when
merged bounds remain unchanged.

### 4.d Unresolved And Edges

One/two-group inputs retain all rows with `None` labels. Distinguish edge,
unresolved, and ordinary non-turn evidence; do not bridge skipped groups.

### 4.e Raw Evidence

Preserve every original and merge field, including mixed source labels,
timestamp spacing, and first/extreme flags. Recover a center's neighbors
and their raw membership through the original ordered merged series.

### 4.f Validation

Reject missing/reordered rows, changed OHLCV/merge fields, inconsistent labels
within one M group, unsupported config, and labels that fail the actual
neighbor comparisons.

### 4.g Reference Checkpoint

Run the preserved CC record through the full input chain. Compare 3,027
marked center groups, then inspect their M positions, types, and prices.
Do not compare the number of tagged raw rows to KWX's sparse-result count.

### 4.h Display Boundary

Verify a group's start and price-extreme row may differ, equal extremes obey
first/last policy, and repeated labels yield one anchor per group. No chart
library is needed. Streaming availability needs a separate later test.

### 4.i Concrete Cases

- Section 0.b: expect exactly M2=`top`, M5=`bottom`, 11 retained rows,
  seven merged groups, and two centers. All other labels are `None`.
- Section 0.c: K2 and K3 both carry `top`; count one center, with price 14
  and raw price anchor K2. Keep their different original prices.
- Rising/falling input: no centers; preserve the full raw time coverage.
- Alternating peaks/troughs: classify overlapping windows independently;
  do not filter candidates as though selecting Bi endpoints.
- Equality: reject a candidate if any required strict comparison ties.
  Use a controlled merged-input fixture for detector tests; normal upstream
  merging may absorb equal-boundary raw bars before detection.
- Short/unresolved input: keep all rows, label none, and distinguish missing
  neighbors from skipped unresolved windows in the evidence.
- Preservation: compare every original and merge field against input;
  conversions must round-trip exactly and derivation must not mutate input.
- Invalid state: reject wrong row/config types, changed or reordered rows,
  mixed labels in a group, and fabricated centers without valid neighbors.
- Price anchor: test a non-first contributor and equal extremes under both
  upstream tie policies; reject invalid group indices.
- Reference record: read raw CSV, merge, then derive Fenxing. Expect
  10,060 retained rows, 6,200 groups, and 3,027 centers. Compare every center's
  index, type, and turning price against a separate test-only calculation
  of Appendix A's strict formula, not just the aggregate count.

### 4.j Execution And Results

Commands run from the repository root using the existing Python 3.11.16:

```zsh
PYTHONPATH=src .venv/bin/python -m unittest experiments.chan_theory.test_fenxing_series
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

```text
Fenxing tests:        34 passed in 0.237s
All experiment tests: 98 passed in 1.883s (includes the 34 Fenxing tests)
Source tests:         42 passed in 2.409s
Checkpoint:           10060 raw -> 6200 M groups -> 3027 centers
Fenxing derivation:   0.115s, including construction validation
Verified input chain: 0.230s, including reference comparisons/evidence checks
```

Timings are observations from this machine, not performance guarantees.
All 3,027 center indices/types/prices agree with the independent test-only
formula on the same merged input. The manifest supplies the count, not a
full external center list; this is not a complete KWX golden-output comparison.

> [boundary] This tests raw CSV -> merge -> Fenxing, not Fenxing CSV export
> or plotting. Tests do not establish live-tail finality or all future data
> behavior. No dependencies installed and no environment recreated.

## 5. Current Experiment Delta

> [decision] The user chose raw-row preservation and center tagging instead
> of the earlier sparse three-bar-result design on 2026-09-10.

- Replace stored `items` with `klines`; preserve all original and merge fields.
- Add only `fx_type`; drop stored F IDs, membership roles, triple ranges,
  middle timestamps, and duplicate source traces from the proposed row.
- Derive counts, neighboring evidence, and price anchors when needed.
- Preserve Appendix A's original reference code unchanged.
- Implemented `Fenxing` and `FenxingSeries`, with `FenxingConfig` in the
  series module. Added experiment package exports and 34 tests.
- Verified the real-data count and center-level formula agreement; earlier
  memos remain intact. No Fenxing CSV/chart adapter or source promotion.

## 6. Open Questions

- Decide live-tail confirmation only when replay/streaming becomes scope.
- CSV and chart adapters can consume this row shape in later focused work.

> [source check] KWX's model and detector were read in the browser on
> 2026-09-10, and the user supplied the preserved code below. Its detection
> rule is the reference; Project 009 deliberately uses different storage.
> The external count is also recorded in
> `records/cc/kline-to-zoushi-001/dce-kqm-m-15m-manifest.json`,
> `engine.counts.fenxing`.

## 7. Discussion: Other Turning-Point Methods

> [discussion] Similar-looking top/bottom markers can represent different
> definitions. Distinguish the detection rule, price range, and later Bi
> acceptance before adding an option to `FenxingConfig`.

### 7.a Bill Williams Fractals: Five Bars

The usual pattern examines a middle bar and two bars on each side. A high
fractal compares highs only; a low fractal compares lows only. It does not
require Chan's simultaneous high-and-low comparisons or Chan inclusion merge.

```text
Bar       K0  K1  K2  K3  K4
High      10  12  15  13  11
Low        5   7   6   8   7
```

K2 qualifies as a five-bar high fractal. It fails the strict Chan top test
on the immediate raw triple K1/K2/K3 because its low is below both neighbors.
That raw triple has containment; Chan must merge first before detecting.

> [project consequence] This changes both the comparison and its input
> assumptions. Confirmation requires the two right-hand bars; a marker's
> location must not be confused with when the pattern becomes observable.

[source] [MetaTrader Fractals explanation and implementation article](https://www.mql5.com/en/articles/11620).

### 7.b Adjustable Neighborhood: Local Pivots

TradeStation's Fractals study exposes `HighStrength` and `LowStrength` to
control the number of bars on each side used to identify an extreme.
Increasing the neighborhood can reject smaller local turns and requires
more right-side evidence.

> [project consequence] A configurable radius is a different structural
> scale, not a change from `>` to `>=`. A radius of two requires five bars;
> neighbors can no longer be reconstructed from only M(j-1) and M(j+1).
> Radius is not the same as changing the bar period from minutes to hours.

[source] [TradeStation Fractals study](https://help.tradestation.com/10_00/eng/tradestationhelp/elanalysis/showme/fractals_showme_.htm).

### 7.c Plateau Peaks: Equal Values

SciPy's `find_peaks` handles a flat peak as one plateau. It returns the
middle sample, rounding down for an even-length plateau, rather than labeling
each equal sample independently. Optional filters include prominence,
distance, width, and plateau size.

```text
Sample index     0   1   2   3
Value           10  14  14  11
Peak anchor          1
```

This is a one-dimensional peak detector. Applying it to highs, lows, closes,
or a derived signal creates different meanings; it is not automatically a
Chan Fenxing detector.

> [project consequence] An equal-price policy needs a plateau span and an
> anchor rule. Replacing every strict comparison with an inclusive comparison
> is insufficient. In our current merge profile, adjacent equal high/low
> edges are already containment cases, so an alternative must also specify
> how it interacts with upstream merge.

[source] [SciPy `find_peaks` documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html).

### 7.d Chan Variants: Range And Bi Acceptance

Chanlun-PRO documents different choices for a Fenxing's price range:
the three-bar range versus the middle bar, and original-bar bounds versus
inclusion-adjusted bounds. It also provides inclusion/overlap restrictions
between endpoint Fenxing that affect Bi construction.

`chan.py` likewise exposes `bi_fx_check` choices such as `strict`, `half`,
`loss`, and `totally`. These compare candidate Bi endpoint structures;
they are not four alternative formulas for recognizing one local Fenxing.

> [project consequence] Keep range extraction and Bi qualification separate
> from center detection. Changing a downstream acceptance rule should not
> silently rewrite the raw-aligned `fx_type` labels.

[source] [Chanlun-PRO configuration reference](https://chanlun-pro.readthedocs.io/缠论配置项说明/)
and [chan.py configuration documentation](https://github.com/Vespa314/chan.py).

### 7.e Equal Boundaries In Feature Sequences

`chan.py` has an `allow_top_equal` parameter in its shared combiner. Its
special comparison branch can accept a matching right-hand high or low.
The inspected call sites use this mechanism in segment feature-sequence
analysis, coupled to special inclusion handling. The ordinary K-line path
calls `update_fx()` with the default strict profile.

> [project consequence] This is evidence of a specialized alternative, not
> a reason to expose a general loose K-line Fenxing switch. A feature-sequence
> element represents a different input object from an ordinary merged bar.

[source] [Shared comparison implementation](https://github.com/Vespa314/chan.py/blob/main/Combiner/KLine_Combiner.py),
[feature-sequence caller](https://github.com/Vespa314/chan.py/blob/main/Seg/EigenFX.py),
and [ordinary K-line caller](https://github.com/Vespa314/chan.py/blob/main/KLine/KLine_List.py).

### 7.f Decision For This Experiment

> [decision] Keep the current strict, three-merged-group rule. This discussion
> records alternatives; it does not enable new config values.

Our center-only row tag works because the neighborhood and source series are
fixed. A later alternative must state its input, neighborhood, comparison,
tie handling, and evidence timing before sharing this interface.

One further distinction matters: independent high-only and low-only tests
can both pass on a wide outside bar. Such a detector would need an explicit
dual-label policy; our single `top/bottom/None` field must not arbitrarily
discard one result.

> [verification idea] Compare alternatives on identical input using an equal
> plateau, an outside bar, a monotonic run, and a short reversal. Record both
> marker positions and the last input needed to identify them. These are
> future experiments, not completed tests.

## Appendix A. Reference Code From Kewenxing / KWX-CC

> [source] Kewenxing's older Fenxing code, supplied by the user on 2026-09-10
> as a pasted copy of [KWX/CC](https://www.kwx.me/cc/#fractal).
> The page labels the executable teaching version
> `manual_rebuild/algo/fenxing.py` and identifies its CC counterpart as
> `src/cc/algo/fenxing.py`, lines 26-62. The page's declared source snapshot
> is `e86f2dd92920f9c36678d6b859fd4405dde8df85`.

> [reference only] Preserve these excerpts as supplied, including original
> Chinese comments and procedural organization. They are external reference
> code, not Project 009 implementation or approval of its design.

### A.a Structure Definition

Excerpts from the page's `manual_rebuild/algo/models.py`:

```python
class FxType(StrEnum):
    """分型类型。"""

    TOP = "top"  # 顶分型
    BOTTOM = "bottom"  # 底分型

@dataclass(frozen=True, slots=True)
class Fenxing:
    """分型 — 由三根相邻合并 K 线构成, 取中间一根为代表 (PR-3 填充)。"""

    period: str  # 来源周期码 (§1.5 预留)
    fx_type: FxType
    index: int  # 中间合并 K 线在合并序列中的下标
    timestamp: int  # 中间合并 K 线代表时间 (Unix 秒)
    high: float  # 分型三根区间最高
    low: float  # 分型三根区间最低
    trace: StructTrace | None = None  # 轻量 trace 索引 (§1.7); 默认 overlay 不下发

    @property
    def id(self) -> str:
        """稳定 id (§1.7): ``fx-{timestamp}`` (与 serializer id 对齐)。"""
        return f"fx-{self.timestamp}"
```

> [reading note] One Fenxing represents three neighboring merged bars.
> `index` points to the middle bar; `high/low` cover the whole triple.
> A top's turning price is `high`; a bottom's is `low`. The three bars
> are located through indices and trace, not stored as three nested objects.

### A.b Detection Code

The supplied `manual_rebuild/algo/fenxing.py` block:

```python
"""分型（顶分型 / 底分型）— 在合并 K 线序列上识别 (算法说明卡 fenxing-v1)。

口径来源（口径优先链 §1.1）：
- 第 62 课：顶分型 = 中间 K 线 high 是相邻三 K 线 high 中最高、且 low 也是三者中最高；
  底分型对称。
- 用户确认（fenxing-v1 §16）：本层只产**原始**顶/底分型（取舍 / 最小 K 线数 / 有效性归
  笔层 PR-4）；平台 / 等价极值采**严格**判定（相等致「严格最高且最高」不成立则不构成分型）；
  相邻同型分型如实产出、不取舍。

分型在**合并后**序列上识别（包含已消除，保证三者可比、答案唯一，第65课）。
本模块是合并单元列表的**纯函数**：合并列表由 `KlineCombiner` 增量维护，故逐根增量与批量
结果一致（golden 自洽，§1.4）。

trace（§1.7）：每个分型落 `merged_range`（三根合并单元 index）+ `source_range`
（三根覆盖的原始 K 线 ts 范围）= PR-3 最小 trace 目标。
"""

from __future__ import annotations

from manual_rebuild.algo.models import Fenxing, FxType, MergedKline
from manual_rebuild.algo.trace import RULE_FENXING_BOTTOM, RULE_FENXING_TOP, StructTrace

_ALGO_CARD_ID = "fenxing-v1"


def detect_fenxings(merged: list[MergedKline]) -> list[Fenxing]:
    """识别合并序列中全部顶/底分型（严格，不取舍）。"""
    out: list[Fenxing] = []
    for i in range(1, len(merged) - 1):
        a, b, c = merged[i - 1], merged[i], merged[i + 1]
        is_top = (
            b.high > a.high and b.high > c.high and b.low > a.low and b.low > c.low
        )
        is_bottom = (
            b.low < a.low and b.low < c.low and b.high < a.high and b.high < c.high
        )
        if not (is_top or is_bottom):
            continue
        fx_type = FxType.TOP if is_top else FxType.BOTTOM
        rule_id = RULE_FENXING_TOP if is_top else RULE_FENXING_BOTTOM
        fx_high = max(a.high, b.high, c.high)
        fx_low = min(a.low, b.low, c.low)
        trace = StructTrace(
            algo_card_id=_ALGO_CARD_ID,
            rule_id=rule_id,
            merged_from_index=i - 1,
            merged_to_index=i + 1,
            source_from_ts=a.start_ts,
            source_to_ts=c.end_ts,
        )
        out.append(
            Fenxing(
                period=b.period,
                fx_type=fx_type,
                index=i,  # 中间合并单元下标
                timestamp=b.start_ts,  # 中间合并单元代表时间（§13）
                high=fx_high,
                low=fx_low,
                trace=trace,
            )
        )
    return out
```

### A.c Project 009 Reading

- The reference input is one compact object per M group. Project 009 keeps
  raw-aligned rows, so select distinct groups and use their `merged_high`
  and `merged_low` before applying these comparisons.
- The reference stores one result per three-group turn, with a center index,
  representative timestamp, and full-window bounds. Project 009 preserves
  each raw row's original `datetime`, OHLCV, and merge fields, adding only
  `fx_type`; neighboring membership is derived from the source series.
- `FenxingConfig` and unresolved-window skipping are Project 009 proposals;
  the supplied detection function exposes neither option.
- These excerpts depend on external `MergedKline`, `StructTrace`,
  rule constants, and model imports. They are not a standalone runnable module.
- Original incremental-consistency comments describe the reference system.
  They are not Project 009 test results or a guarantee of live-tail finality.
