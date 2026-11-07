# memo0020_class_merged_kline_series

[class design] [chan] [merged kline] [series first]

## 0. Scope And Purpose

> [purpose] Define `MergedKlineSeries`, the first Chan derivation operation in
> Project 009.

The first Chan operation is:

```text
KlineTSeries + KlineMergeConfig -> MergedKlineSeries
```

> [scope] This memo focuses on inclusion merge / 合并K线 only.

It covers:

- `MergedKline` as one original raw K-line row plus merge annotation fields;
- `MergedKlineSeries` as the derivation boundary;
- `KlineMergeConfig` as the stage rule profile;
- trace, checkpoint, and display anchors needed by later Chan steps.

> [non-goal] This memo does not design `FenxingSeries`, `BiSeries`,
> `XianduanSeries`, `ZhongShuSeries`, `ZouShiSeries`, trading signals, chart
> overlays, or multi-timeframe mapping.

> [source] This memo is based on `memo0015_oop_trading_architecture.md`,
> `memo0019_InterfaceChan.md`, the CC record checkpoint in
> `records/cc/kline-to-zoushi-001/`, and reference/experiment behavior from
> `experiments/chan_theory/legacy/kline_combiner.py`.

> [theory wording] Original Chan wording checked against
> [教你炒股票62：分型、笔与线段](https://baiyunju.cc/1874).

Chinese wording anchor:

```text
向上时：把两K线的最高点当高点；低点中的较高者当成低点。
向下时：把两K线的最低点当低点；高点中的较低者当成高点。
```

> [interpretation] Project 009 should read this as a derived-view operation:
> raw K-lines are not changed; the merge creates visible merged structures plus
> raw-index evidence.

### 0.a Top Operation Rule

> [decision] `MergedKlineSeries` derives directly from `KlineTSeries` and
> preserves raw-index group markers.

The raw `KlineTSeries` should not be mutated. The merge result is a derived
view over the original sequence.

Group marker:

```text
is_group_first = True   this raw K-line starts / anchors a visible merged unit
is_group_first = False  this raw K-line is absorbed into another merged unit
```

Minimum raw-aligned evidence:

```text
klines: tuple[MergedKline, ...]
```

Rules:

- `MergedKlineSeries.klines` has the same length as the source
  `KlineTSeries.klines`.
- Each `MergedKline` row keeps the raw K-line fields plus Chan merge fields:
  `raw_index`, `merged_tag`, `merged_low`, `merged_high`,
  `merged_direction`, `merge_state`, `is_group_first`, and
  `is_group_extreme`.
- `merged_tags`, `merged_lows`, `merged_highs`, `merged_directions`,
  `merge_states`, `raw_to_merged_index`, `group_first_flags`, and
  `group_extreme_flags` should be derived properties from `klines`, not
  duplicate stored tuples.
- Every raw K-line belongs to exactly one merged unit.
- A group-first raw K-line anchors a merged unit and points to its merged-unit
  index through `merged_tag`.
- `klines[i].is_group_first is True` means raw K-line `i` is the first raw bar
  inside its merged unit.
- `klines[i].is_group_extreme is True` means raw K-line `i` contributes the
  direction-important price extreme for its merged unit.
- An absorbed raw K-line has `is_group_first is False` and still points to the
  merged unit that owns it through `merged_tag`.
- Raw K-lines are evidence. They are not edited.
- A `MergedKline` keeps its original `high` and `low`; only `merged_high` and
  `merged_low` reflect the merged group after absorption.

> [warning] `is_group_first` is not the whole result. The row still needs
> `merged_tag`, `merged_low`, `merged_high`, `merged_direction`, `merge_state`,
> and raw-index evidence. `True` does not mean the raw bar's OHLC survives
> unchanged as the merged interval.

Merge state:

```text
merge_state = "resolved"              processed and direction is up/down
merge_state = "direction_unresolved"  processed, but no strict direction
                                       appeared inside this data window
```

> [visualization boundary] Do not store draw style here. Solid/hollow, color,
> width, opacity, and label placement belong to a chart or overlay adapter.
> `MergedKline` rows store semantic evidence only.

### 0.b Two-Table Example

Always start from the whole raw series:

| Raw K | Interval |
| --- | --- |
| K0 | `[5,10]` |
| K1 | `[6,9]` |
| K2 | `[7,8]` |
| K3 | `[9,12]` |
| K4 | `[10,11]` |
| K5 | `[11,14]` |
| K6 | `[8,13]` |
| K7 | `[9,12]` |
| K8 | `[7,10]` |
| K9 | `[6,9]` |

Operation flow:

| Step | New | Compare With | Relation / Direction | Action | Dir |
| --- | --- | --- | --- | --- | --- |
| 0 | K0 | none | undecided | put in lead | none |
| 1 | K1 | K0 | contained | keep in lead | none |
| 2 | K2 | K1 | contained | keep in lead | none |
| 3 | K3 | K2 | strict up: high up, low up | collapse K0-K2; create K3 | up |
| 4 | K4 | M1 `[9,12]` | contained under up | merge into M1 by max/max | up |
| 5 | K5 | M1 `[10,12]` | non-contained, strict up | create M2 | up |
| 6 | K6 | M2 `[11,14]` | non-contained, strict down | create M3 | down |
| 7 | K7 | M3 `[8,13]` | contained under down | merge into M3 by min/min | down |
| 8 | K8 | M3 `[8,12]` | non-contained, strict down | create M4 | down |
| 9 | K9 | M4 `[7,10]` | non-contained, strict down | create M5 | down |

Final `MergedKlineSeries` raw-aligned fields:

| Raw K | kLow | kHigh | MergedTag | mergedLow | mergedHigh | isGroupFirst | isGroupExtreme | Trace |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| K0 | 5 | 10 | M0 | 7 | 10 | True | True | K0,K1,K2 |
| K1 | 6 | 9 | M0 | 7 | 10 | False | False | K0,K1,K2 |
| K2 | 7 | 8 | M0 | 7 | 10 | False | False | K0,K1,K2 |
| K3 | 9 | 12 | M1 | 10 | 12 | True | True | K3,K4 |
| K4 | 10 | 11 | M1 | 10 | 12 | False | False | K3,K4 |
| K5 | 11 | 14 | M2 | 11 | 14 | True | True | K5 |
| K6 | 8 | 13 | M3 | 8 | 12 | True | True | K6,K7 |
| K7 | 9 | 12 | M3 | 8 | 12 | False | False | K6,K7 |
| K8 | 7 | 10 | M4 | 7 | 10 | True | True | K8 |
| K9 | 6 | 9 | M5 | 6 | 9 | True | True | K9 |

> [reading note] `is_group_first` marks the time anchor.
> `is_group_extreme` marks the price anchor. In an upward merged unit, extreme
> means the raw bar that contributes `mergedHigh`; in a downward merged unit,
> extreme means the raw bar that contributes `mergedLow`.

Formula summary:

```text
undecided lead: wait
first strict pair: establishes direction
contained under up:   high = max, low = max
contained under down: high = min, low = min
non-contained: create new merged unit and update direction
```

### 0.c One Merged Bar, Many Raw Rows

> [example] A contained group eventually becomes one visible merged bar, while
> the raw-time evidence still keeps every original row.

Whole raw series:

| Raw K | Interval |
| --- | --- |
| K0 | `[9,12]` |
| K1 | `[10,11]` |
| K2 | `[11,11.5]` |

Assume the active direction is up.

Step view:

| Step | Compare | Result |
| --- | --- | --- |
| 0 | start with K0 | active merged bar is `M0 = [9,12]` |
| 1 | K1 against `M0 = [9,12]` | contained; merge by up rule |
| 2 | after K1 | `M0 = [10,12]`, trace `(0,1)` |
| 3 | K2 against updated `M0 = [10,12]` | contained again; merge by up rule |
| 4 | after K2 | `M0 = [11,12]`, trace `(0,1,2)` |

Semantic Chan view:

| Merged | mergedLow | mergedHigh | Direction | Trace |
| --- | ---: | ---: | --- | --- |
| M0 | 11 | 12 | up | K0,K1,K2 |

Raw-time aligned fields:

| Raw K | kLow | kHigh | MergedTag | mergedLow | mergedHigh | isGroupFirst | isGroupExtreme |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| K0 | 9 | 12 | M0 | 11 | 12 | True | True |
| K1 | 10 | 11 | M0 | 11 | 12 | False | False |
| K2 | 11 | 11.5 | M0 | 11 | 12 | False | False |

> [operation rule] After every merge, the next raw K-line compares against the
> updated latest merged bar. The merged bar may keep absorbing more raw rows,
> but it remains one visible Chan structure.

### 0.d Numeric Recipe

> [recipe] Treat each raw K-line as an indexed interval:
>
> ```text
> K_i = [L_i, H_i]
> ```

1. Read raw K-lines from oldest to newest:

```text
i = 0, 1, 2, ...
```

2. Convert each raw K-line into a one-bar candidate:

```text
M = [L_i, H_i]
trace = (i,)
```

3. If no direction exists yet, keep candidates in a pending buffer until two
   neighboring candidates create strict direction.

4. Strict up direction:

```text
H_i > H_{i-1}
and
L_i > L_{i-1}
```

5. Strict down direction:

```text
H_i < H_{i-1}
and
L_i < L_{i-1}
```

6. Containment check between latest merged interval `A = [L_a, H_a]` and new
   interval `B = [L_b, H_b]`:

```text
A contains B: H_a >= H_b and L_a <= L_b
B contains A: H_b >= H_a and L_b <= L_a
```

7. If contained under up direction, merge as:

```text
H_new = max(H_a, H_b)
L_new = max(L_a, L_b)
```

8. If contained under down direction, merge as:

```text
H_new = min(H_a, H_b)
L_new = min(L_a, L_b)
```

9. If contained before direction exists, collapse pending as wide range:

```text
H_new = max(all pending highs)
L_new = min(all pending lows)
```

10. For every raw index consumed by one merged interval, update evidence:

```text
merged unit label        -> merged_tags[i] = "M0"
merged interval          -> merged_lows[i], merged_highs[i]
first raw row            -> group_first_flags[i] = True
absorbed raw row         -> group_first_flags[i] = False
price-anchor raw row     -> group_extreme_flags[i] = True
```

11. Continue comparing the newly merged interval against the next raw K-line
    until no containment remains.

> [implementation note] The recipe is chronological. Even when the idea feels
> recursive, implement it as a left-to-right pass so direction context is not
> rewritten by future bars.

## 1. Design Ideas

### 1.a Position In The Chan Chain

> [decision] `MergedKlineSeries` is the first Chan derivation unit.

The chain starts here:

```text
KlineTSeries
-> MergedKlineSeries
-> FenxingSeries
-> BiSeries
-> XianduanSeries
-> ZhongShuSeries
-> ZouShiSeries
```

`KlineTSeries` is still domain fact. It records ordered market bars.

`MergedKlineSeries` is the first Chan interpretation. It removes inclusion
ambiguity before turning structures are detected.

> [boundary] Do not detect Fenxing on raw included K-lines. Merge first, then
> detect turning points.

### 1.b Structure And Series

> [decision] `MergedKline` is one original K-line row with Chan merge marks.
> `MergedKlineSeries` is the derivation boundary.

Meaning:

```text
MergedKline        one raw K-line row plus merge annotation fields
MergedKlineSeries  managed sequence derived from one KlineTSeries
```

`MergedKline` should record:

```text
symbol
period
source
timestamp
open
high
low
close
volume
raw_index
merged_tag
merged_low
merged_high
merged_direction
merge_state
is_group_first
is_group_extreme
```

`MergedKlineSeries` should record:

```text
klines: tuple[MergedKline, ...]
config: KlineMergeConfig
source_series: KlineTSeries | None
```

> [series rule] The merge algorithm belongs to `MergedKlineSeries` or its
> Chan-only internal worker. A single `MergedKline` records one original K-line
> row plus its M0/M1/M2 assignment; it does not govern the full merge procedure.

### 1.c Config

> [decision] `KlineMergeConfig` is the stage config for
> `MergedKlineSeries`.

Initial config can be small:

```text
allow_equal_containment: bool
direction_requires_strict_high_low: bool
undirected_collapse_policy: str
extreme_tie_policy: str
```

Current default interpretation:

```text
allow_equal_containment = true
direction_requires_strict_high_low = true
undirected_collapse_policy = "wide_range"
extreme_tie_policy = "first"
```

Implemented knobs:

```text
allow_equal_containment = true only
direction_requires_strict_high_low = true only
undirected_collapse_policy = "wide_range" only
extreme_tie_policy = "first" or "last"
```

> [decision] Keep most options locked for now. The internet check and Appendix
> A both support equal-edge containment and strict high/low direction as the
> normal Chan merge profile. `extreme_tie_policy` is the only current runtime
> variation because it changes evidence marking without changing the merged
> interval itself.

Possible future knobs, not implemented now:

```text
initial_direction_policy     wait / candle body / default up / empty output
output_shape                 compact merged bars / raw rows with tags
open_close_policy            high-low only / preserve raw OHLC / adjusted OHLC
stability_policy             full recompute / incremental with provisional tail
```

> [config rule] `ChanConfig.merge` and `MergedKlineSeries.config` should be
> equal when `MergedKlineSeries` is assembled into `ChanStudy`.

### 1.d Operation

> [decision] `MergedKlineSeries` derives directly from `KlineTSeries`.

The raw `KlineTSeries` should not be mutated. The merge result should be a
derived view over the original sequence.

Recommended public operation:

```python
merged = MergedKlineSeries.derive_from(
    source_series=kline_series,
    config=config.merge,
)
```

Internal state option:

```text
_ChanKlineMergeSession
```

> [redesign rule] Do not promote `KlineCombiner` as the Project 009 public
> source class. Treat it as reference/experiment vocabulary from another code
> path. The Project 009 public object is `MergedKlineSeries`; if the algorithm
> needs mutable working state, keep that state in a private Chan-specific helper
> such as `_ChanKlineMergeSession`.

### 1.e Direction Rule

> [rule] Direction is established only from strict movement.

Up:

```text
right.high > left.high
and
right.low > left.low
```

Down:

```text
right.high < left.high
and
right.low < left.low
```

Equality, containment, and ambiguity do not establish direction.

### 1.f Inclusion Rule

> [rule] Containment is interval containment and includes equal boundaries.

Containment:

```text
left.high >= right.high and left.low <= right.low
```

or:

```text
right.high >= left.high and right.low <= left.low
```

Once direction exists, a contained or containing new K-line is merged into the
latest merged structure.

### 1.g Merge Rule

> [rule] The merge calculates `merged_low` and `merged_high` appropriate to the
> active direction. It does not overwrite the raw row's `low` and `high`.

Up context:

```text
high = max(highs)
low  = max(lows)
```

Down context:

```text
high = min(highs)
low  = min(lows)
```

No direction yet:

```text
high = max(highs)
low  = min(lows)
```

> [meaning] The undirected case is only a bootstrap collapse. It should not
> become the normal Chan merge path once trend direction is known.

### 1.h Algorithm Direction

> [rule] Merge oldest to newest.

The algorithm is chronological:

```text
left to right
```

When a merged structure still contains, or is contained by, the next raw
K-line, compare the newly merged structure with that next raw K-line and keep
going.

> [note] The behavior may be described recursively, but Project 009 should
> implement it as an iterative left fold or stack pass so time context remains
> explicit.

> [boundary] Do not merge right-to-left. It changes direction context.

### 1.i Bootstrap Rule

> [rule] Before direction is known, keep a leading buffer.

Procedure:

```text
1. Add raw K-lines to pending.
2. Wait until a strict up/down pair appears.
3. Use that first strict direction to collapse earlier included pending units.
4. Start the merged sequence.
```

If direction never appears:

```text
mark all pending raw rows as one wide-range merged group
```

### 1.j Trace And Evidence

> [decision] `MergedKline` must preserve raw K-line values and add merge
> evidence.

Minimum row evidence:

```text
raw_index
merged_tag
merged_low
merged_high
is_group_first
is_group_extreme
```

Why:

- `FenxingSeries` needs stable merged-K indices.
- `BiSeries` later needs interval extremes, gaps, and raw support.
- Display needs both raw timestamps and merged group boundaries.
- Checkpoints must explain where every merged group came from.

> [trace rule] Group trace is derived from `MergedKlineSeries.klines` by reading
> consecutive rows with the same `merged_tag`. Private `_MergeUnit` may keep
> `trace`, `start_index`, and `end_index` during calculation, but the public
> row object should stay raw-row shaped.

### 1.k Checkpoint

> [checkpoint] The CC tutorial record currently verifies:

```text
10060 raw K-lines -> 6200 merged K-lines
```

Source:

```text
records/cc/kline-to-zoushi-001/dce-kqm-m-15m-manifest.json
```

Current experiment:

```text
experiments/chan_theory/legacy/kline_combiner.py
experiments/chan_theory/legacy/test_kline_combiner.py
```

> [boundary] These files are checkpoint evidence and redesign input. They are
> not the final class boundary.

## 2. First Class Shape

### 2.a `MergedKline`

```python
MergeState = Literal["resolved", "direction_unresolved"]

@dataclass(frozen=True)
class MergedKline:
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
```

Members:

```text
symbol             raw K-line symbol
period             raw K-line period
source             raw K-line source
timestamp          raw K-line timestamp
open/high/low/close/volume
                   raw K-line OHLCV fields
raw_index          raw position in the original KlineTSeries
merged_tag         M0/M1/M2 label for the merged group
merged_low         merged low repeated on this raw row
merged_high        merged high repeated on this raw row
merged_direction   Chan direction for this merged group
merge_state        resolved or direction_unresolved
is_group_first     True if this row is the first raw row of the merged group
is_group_extreme   True if this row contributes the direction-important extreme
```

Methods / properties:

```text
from_kline(...) -> MergedKline
k_low -> float
k_high -> float
validate() -> None
to_raw_kline() -> Kline
```

> [boundary] `MergedKline` is a row object, not the compact semantic M0/M1
> unit. It should not read files, detect Fenxing, build Bi, or render charts.

> [extreme rule] Under up direction, `is_group_extreme is True` marks the row
> that contributes `merged_high`. Under down direction, it marks the row that
> contributes `merged_low`. Tie handling belongs to `KlineMergeConfig`.

> [state rule] `merge_state` answers whether the row was processed into a group
> with resolved direction. `direction_unresolved` means the group was processed,
> but this finite data window ended before a strict up/down pair appeared.

### 2.b `MergedKlineSeries`

```python
@dataclass(frozen=True)
class MergedKlineSeries:
    klines: tuple[MergedKline, ...]
    config: KlineMergeConfig
    source_series: KlineTSeries | None = None
```

Members:

```text
klines                  KlineTSeries-like row sequence
config                  exact merge rule profile
source_series           optional original KlineTSeries evidence
```

> [correction] Keep the `KlineTSeries` shape: a series has `klines`. The row
> type changes from raw `Kline` to `MergedKline`, and each row carries raw
> OHLCV plus merged tag/min/max/group-first/group-extreme flags.

Properties:

```text
symbol -> str
period -> str
count -> int
raw_count -> int
is_empty -> bool
merged_tags -> tuple[str, ...]
merged_lows -> tuple[float, ...]
merged_highs -> tuple[float, ...]
merged_directions -> tuple[ChanDirection | None, ...]
merge_states -> tuple[MergeState, ...]
group_first_flags -> tuple[bool, ...]
group_extreme_flags -> tuple[bool, ...]
merged_count -> int
start_timestamp -> datetime
end_timestamp -> datetime
trace -> tuple[tuple[int, ...], ...]
raw_to_merged_index -> tuple[int, ...]
absorbed_count -> int
group_first_indices -> tuple[int, ...]
group_extreme_indices -> tuple[int, ...]
```

Methods:

```python
@classmethod
def derive_from(
    cls,
    source_series: KlineTSeries,
    config: KlineMergeConfig,
) -> "MergedKlineSeries":
    ...

def validate(self) -> None:
    ...

def merged_for_raw_index(self, raw_index: int) -> MergedKline:
    ...

def raw_indices_for_merged_index(self, merged_index: int) -> tuple[int, ...]:
    ...

def to_list(self) -> list[MergedKline]:
    ...

def timestamps(self) -> tuple[datetime, ...]:
    ...

def closes(self) -> tuple[float, ...]:
    ...

def raw_klines(self) -> tuple[Kline, ...]:
    ...

def evidence_table(self) -> tuple[dict[str, object], ...]:
    ...
```

Method intent:

```text
derive_from(...)
  public constructor for the derivation:
  KlineTSeries + KlineMergeConfig -> MergedKlineSeries.
  It owns the stage boundary and delegates mutable scan state to the private
  session.

validate()
  protects the row-aligned contract:
  non-empty rows, one symbol, one period, strict timestamp order, contiguous
  M0/M1 tags, one group-first row per group, and one group-extreme row per
  group.

merged_for_raw_index(raw_index)
  answers: which enriched row belongs to this original raw K-line position?
  Because output row count equals input row count, this is direct indexing.

raw_indices_for_merged_index(merged_index)
  answers: which original raw K-lines are members of M0, M1, M2...?
  This is the main bridge from compact merged-unit thinking back to raw rows.

to_list()
  gives callers a normal mutable list copy for inspection or display without
  mutating the frozen series.

timestamps() / closes()
  preserve the familiar KlineTSeries convenience shape for simple plotting,
  logging, and smoke checks.

raw_klines()
  strips the Chan merge fields and reconstructs the original Kline sequence.
  This proves the derivation did not mutate source market data.

evidence_table()
  returns the human-audit view: raw index, timestamp, original high/low,
  merged tag, merged interval, direction, state, first flag, and extreme flag.
```

> [boundary] `MergedKlineSeries` may use a private merge session internally,
> but the public result should be a KlineTSeries-like object whose `klines`
> are enriched rows, not a raw tuple and not parallel stored columns.

> [visualization boundary] Do not add `draw_style` to `MergedKlineSeries`.
> A visualization adapter may later translate `group_first_flags` and
> `group_extreme_flags` into solid/hollow bars, colors, labels, opacity, or
> exported 0/1 columns.

### 2.c `_MergeUnit`

```python
@dataclass(frozen=True)
class _MergeUnit:
    direction: ChanDirection | None
    low: float
    high: float
    start_index: int
    end_index: int
    trace: tuple[int, ...]
    extreme_index: int
```

> [boundary] `_MergeUnit` is private calculation state. It exists only so the
> public `MergedKline` name can mean the raw-aligned row the user reads and
> plots.

### 2.d `KlineMergeConfig`

```python
@dataclass(frozen=True)
class KlineMergeConfig:
    allow_equal_containment: bool = True
    direction_requires_strict_high_low: bool = True
    undirected_collapse_policy: UndirectedCollapsePolicy = "wide_range"
    extreme_tie_policy: str = "first"
```

Members:

```text
allow_equal_containment          equal interval edge counts as containment
direction_requires_strict_high_low
                                  up/down requires both high and low to move
undirected_collapse_policy       what to do if no direction ever appears
extreme_tie_policy               first/last rule when multiple raw rows share
                                  the direction-important extreme
```

Current option status:

```text
allow_equal_containment          locked true
direction_requires_strict_high_low
                                  locked true
undirected_collapse_policy       locked "wide_range"
extreme_tie_policy               active: "first" or "last"
```

> [implementation note] The current experiment supports only the default
> equal-containment and strict-direction policies. Unsupported policy changes
> fail during config validation instead of being silently ignored.

> [small-first rule] Do not add parameters before a rule needs to vary.
> Defaults should reproduce the CC checkpoint first.

### 2.e `_ChanKlineMergeSession`

```python
@dataclass
class _ChanKlineMergeSession:
    source_series: KlineTSeries
    config: KlineMergeConfig
```

Methods:

```text
run() -> MergedKlineSeries
_bootstrap(pending, merged_units, unit) -> ChanDirection | None
_append_with_direction(merged_units, unit, direction) -> ChanDirection
_strict_direction(left, right) -> ChanDirection | None
_collapse_pending(direction) -> _MergeUnit
_collapse_without_direction(pending) -> tuple[_MergeUnit, ...]
_build_series(merged_units) -> MergedKlineSeries
```

Method intent:

```text
run()
  scans source K-lines left to right and returns the final row-aligned result.

_bootstrap(...)
  holds early bars until the first strict up/down pair appears, then collapses
  the leading contained chain using that first direction.

_append_with_direction(...)
  compares the next raw unit against the latest merged unit. If contained, it
  updates that merged unit; if not contained, it creates the next M tag and
  updates direction.

_strict_direction(...)
  returns up only when high and low both rise; returns down only when high and
  low both fall; otherwise returns none.

_collapse_pending(...)
  turns the pre-direction lead chain into the first resolved merged unit after
  direction appears.

_collapse_without_direction(...)
  handles finite windows that never produce strict direction. Current policy:
  one wide-range group with `merge_state = "direction_unresolved"`.

_build_series(...)
  expands private compact merge units back into raw-aligned `MergedKline`
  rows, repeating the merged interval and M tag on every member row.
```

> [boundary] This class is private implementation detail only. It can disappear
> if `MergedKlineSeries.derive_from()` stays readable without it.

## 3. Implementation Result

> [status] The first `MergedKlineSeries` redesign is implemented as
> experiment-only code.

Files:

```text
experiments/chan_theory/merged_kline_series.py
experiments/chan_theory/test_merged_kline_series.py
```

Implemented classes:

```text
KlineMergeConfig
MergedKline
MergedKlineSeries
_MergeUnit
_ChanKlineMergeSession
```

Implemented `MergedKline` row storage:

```text
symbol, period, source, timestamp
open, high, low, close, volume
raw_index
merged_tag
merged_low
merged_high
merged_direction
merge_state
is_group_first
is_group_extreme
```

Implemented `MergedKlineSeries` storage:

```text
klines: tuple[MergedKline, ...]
config: KlineMergeConfig
source_series: KlineTSeries | None
```

Implemented derived properties:

```text
symbol
period
count
raw_count
merged_count
start_timestamp
end_timestamp
raw_to_merged_index
group_first_flags
group_extreme_flags
absorbed_count
group_first_indices
group_extreme_indices
trace
merged_tags
merged_lows
merged_highs
merged_directions
merge_states
```

Implemented methods:

```text
derive_from(source_series, config=None)
validate()
merged_for_raw_index(raw_index)
raw_indices_for_merged_index(merged_index)
to_list()
timestamps()
closes()
raw_klines()
evidence_table()
```

Verification:

```text
Latest verification refresh: 2026-09-04 04:55
MergedKlineSeries tests: 12 passing
all Chan experiment tests: 20 passing
source baseline tests: 42 passing
py_compile: passing
line-length scan: passing
git diff --check: passing
CC checkpoint: 10060 raw K-lines -> 6200 merged K-lines
```

> [boundary] This is still experiment code. Do not promote it to
> `src/tradinglab/market_views/chan/` until the next source-promotion decision.

## 4. Test Session

> [test intent] The test suite protects one idea: after Chan inclusion merge,
> Project 009 still reads the market as K0, K1, K2, ... on the original time
> axis. Merge meaning is added as fields on each row.

Test file:

```text
experiments/chan_theory/test_merged_kline_series.py
```

### 4.a Shape

The first protection is shape. `MergedKlineSeries.klines` must keep the same
length and time order as the original `KlineTSeries`. Each element is still a
row on the original K-line timeline; it simply carries extra merge fields:
`merged_tag`, `merged_low`, `merged_high`, `merged_direction`,
`is_group_first`, and `is_group_extreme`.

This is the test that prevents the class from drifting back into a compact
`M0, M1, M2`-only structure.

### 4.b Derived Views

The series properties are convenience views over `klines`, not separate stored
truth. `merged_tags`, `merged_lows`, `merged_highs`, `group_first_flags`,
`group_extreme_flags`, `raw_to_merged_index`, and `trace` must all be
reconstructable from the row sequence.

This keeps one source of truth: the row object.

### 4.c Merge Rule

Containment must compare the next raw K-line against the latest updated merged
interval. If K1 absorbs K2, then K3 compares against the updated M1, not the
old K2.

Direction also matters. Under downward merge, the extreme row is the one that
contributes `merged_low`; under upward merge, it is the one that contributes
`merged_high`.

### 4.d Bootstrap

Before strict up/down direction appears, the leading rows are ambiguous. If
they never establish direction, the current rule collapses them into one
wide-range group with:

```text
merged_direction = None
merge_state = "direction_unresolved"
```

This protects the beginning of a chart, where many Chan errors start.

### 4.e Raw Evidence

Raw K-line values must survive exactly. `raw_klines()` should reconstruct the
original `Kline` sequence, and `to_list()` should return the enriched row
objects.

This is the project boundary: merge adds meaning, it does not rewrite market
data.

### 4.f Validation

The series rejects rows that are not `MergedKline`. Each merged group must have
exactly one `is_group_first` row, and that row must be the first raw row in the
group.

`is_group_first` and `is_group_extreme` must be real booleans. Numeric 0/1 is an
adapter/export concern, not the domain shape.

`merge_state` must agree with `merged_direction`: resolved rows need up/down
direction; direction-unresolved rows must have `merged_direction = None`.

### 4.g Reference Checkpoint

The external CC record remains the regression checkpoint:

```text
10060 raw K-lines -> 6200 merged groups
```

This is the main regression guard against drifting away from the absorbed
KWX/CC reference behavior.

### 4.h Display Boundary

The evidence table exposes semantic fields such as `k_low`, `k_high`,
`merged_tag`, `merged_low`, and boolean flags. It must not store chart-specific
`draw_style`.

Chart rendering can decide later which rows are solid, hollow, colored, faded,
or labeled.

### 4.i Test Name Map

```text
shape:
  test_derive_returns_kline_series_like_rows_with_merge_fields

derived views:
  test_series_properties_are_derived_from_kline_rows

merge rule:
  test_next_raw_bar_compares_against_updated_latest_merged_bar
  test_down_direction_is_group_extreme_marks_low_contributor

bootstrap:
  test_all_included_without_direction_uses_wide_range_rows

raw evidence:
  test_to_list_and_raw_klines_preserve_raw_market_data

validation:
  test_validation_rejects_wrong_row_type
  test_validation_rejects_missing_group_is_group_first
  test_validation_rejects_integer_group_flags
  test_validation_rejects_inconsistent_merge_state

reference:
  test_reproduces_cc_merged_count_checkpoint

display boundary:
  test_evidence_table_exposes_fields_without_draw_style
```

## 5. Current Experiment Delta

The current experiment already has:

```text
MergedKline
KlineCombiner.combine(series) -> tuple[MergedKline, ...]
```

This is useful as evidence, but it is not the desired source design.

The redesign experiment now also has:

```text
KlineMergeConfig
MergedKlineSeries.derive_from(...) -> MergedKlineSeries
_ChanKlineMergeSession as private working state
```

> [migration note] Do not rush promotion to `src/tradinglab/market_views/chan/`.
> First make the experiment express the series-first interface and keep the
> `10060 -> 6200` checkpoint green.

## 6. Open Questions

> [open] Should `MergedKlineSeries.derive_from()` own the merge algorithm
> directly, or should it delegate mutable state to `_ChanKlineMergeSession`?

Current leaning:

```text
keep the public API on MergedKlineSeries; use a private merge session only if
the pending-buffer and trace bookkeeping become too noisy inside derive_from()
```

> [open] Should `trace` stay as raw integer indices only, or become structured
> references later?

Current leaning:

```text
start with tuple[int, ...]
later introduce ChanConceptRef only for cross-timeframe mapping
```

> [open] Should `direction` live on each `MergedKline`, or only on transitions?

Current leaning:

```text
keep direction on MergedKline during the experiment because it helps explain
merge context and debug checkpoints
```

## Appendix A. Code From kwx

> [source] Pasted external reference code from the user's attachment on
> 2026-09-03:
> `/Users/coder/.codex/attachments/fcaf4458-2a3c-45f4-b835-b7c2f655b1fb/pasted-text.txt`

> [boundary] This is reference code from another codebase. It is not Project
> 009 source code. Do not copy it into `src/` directly. Its imports, trace
> classes, rule IDs, and incremental-only API belong to the source codebase and
> must be adapted through the Project 009 memo and milestone process.

```python
"""K 线合并（包含关系处理）— 增量实现 (算法说明卡 kline-merge-v1)。

口径来源（decision-0001 v1.4 §12.3：缠论原文 > 用户确认的本项目口径 > 本项目自主实现；参考项目无固定优先级）：
- 第 65 课：包含合并取值（向上 max/max、向下 min/min）；顺序原则（逐根与末端单元比，
  非包含才新建）；方向「同时严格高低，去等号」。
- 用户确认（kline-merge-v1 §16）：首段方向顺延到首个可定向处（rule `merge.init`）；
  等价极值默认按包含合并（不启用 allow_top_equal 变体）；一字 K 退化为点区间。

增量纪律（§1.3 / §3.3）：本类**只暴露增量 append / 同 ts 末端更新 pop+append**，
不暴露任何全量重算入口；批量参照实现只在 `tests/`。

trace（§1.7）：每个合并单元落轻量 `StructTrace`（rule_id + 来源原始 K 线 ts 范围）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from manual_rebuild.algo.models import KlineDir, MergedKline
from manual_rebuild.algo.trace import (
    RULE_MERGE_CONTAINS,
    RULE_MERGE_DIR_DOWN,
    RULE_MERGE_DIR_UP,
    RULE_MERGE_INIT,
    StructTrace,
)
from manual_rebuild.data import Kline

_ALGO_CARD_ID = "kline-merge-v1"


def _direction(a_high: float, a_low: float, b_high: float, b_low: float) -> KlineDir | None:
    """相邻非包含两单元方向：同时严格抬高→UP，同时严格降低→DOWN（第65课，去等号）。

    返回 None 表示「包含 / 等价 / 无法唯一判定」（含相等极值）——此时不构成方向判据。
    注：非包含必然落入 UP / DOWN 之一；包含或任一边相等都返回 None。
    """
    if b_high > a_high and b_low > a_low:
        return KlineDir.UP
    if b_high < a_high and b_low < a_low:
        return KlineDir.DOWN
    return None


def _contains(a_high: float, a_low: float, b_high: float, b_low: float) -> bool:
    """a 是否包含 b（区间互含，方向无关；含相等边界 → 视为包含，对应 §16-2/§16-4）。"""
    return a_high >= b_high and a_low <= b_low


@dataclass(slots=True)
class _Unit:
    """内部可变合并单元（输出时转 MergedKline）。"""

    high: float
    low: float
    dir: KlineDir
    rule_id: str  # 该单元形成规则（merge.init / merge.dir.up / merge.dir.down）
    start_index: int  # 原始 K 线序列起始下标
    members: list[Kline] = field(default_factory=list)

    @property
    def end_index(self) -> int:
        return self.start_index + len(self.members) - 1


class KlineCombiner:
    """单 ``period`` 的增量 K 线合并器（串行喂数据）。

    首段方向「顺延」：在方向确立前，原始 K 线缓冲在 ``_lead``，不产合并单元；一旦出现
    首个非包含且同时高低的相邻对，确立方向 d，把之前的包含链坍缩成首个单元（rule
    `merge.init`），并以 d 起算后续。
    """

    def __init__(self, period: str) -> None:
        self.period = period
        self._units: list[_Unit] = []
        self._lead: list[Kline] = []  # 方向未定的前导缓冲
        self._established = False
        self._total = 0  # 已消费原始 K 线根数（= 下一根的全局下标）

    # ── 增量入口 ─────────────────────────────────────────────────────────
    def append(self, k: Kline) -> None:
        """末端追加一根新 K 线（timestamp 严格更大，由 engine 保证）。"""
        if self._established:
            self._append_established(k, self._total)
        else:
            self._lead.append(k)
            self._try_establish()
        self._total += 1

    def pop_last_kline(self) -> None:
        """回退最近一根原始 K 线（供同 ts 末端更新：pop 后 engine 再 append 新值）。"""
        if self._total == 0:
            return
        self._total -= 1
        if not self._established:
            self._lead.pop()
            return
        last = self._units[-1]
        last.members.pop()
        if last.members:
            self._recompute_unit(last)
            return
        self._units.pop()  # 单元清空 → 丢弃
        # 跨 establishment 边界回退（顺延口径 §16-1）: 若只剩首段 merge.init 单元, 说明被弹出的
        # 正是确立方向的那根, 方向依据已消失 → 恢复到方向未定的前导期, 由后续 append 重判。
        if len(self._units) == 1 and self._units[0].rule_id == RULE_MERGE_INIT:
            blob = self._units[0]
            self._lead = list(blob.members)
            self._units = []
            self._established = False
        elif not self._units:  # 防御: 全部弹空 → 回初始
            self._lead = []
            self._established = False

    # ── 输出 ─────────────────────────────────────────────────────────────
    def stable_index(self) -> int:
        """末端稳定点（§10）：倒数第 2 个合并单元的原始 K 线结束下标；不足返回 -1。

        最后一个合并单元为 provisional（新根可能改写），其余 confirmed。O(1)。
        """
        if len(self._units) < 2:
            return -1
        return self._units[-2].end_index

    def merged_count(self) -> int:
        """当前合并单元数量（O(1)）。"""
        return len(self._units)

    def to_merged_klines(self) -> list[MergedKline]:
        """当前合并单元序列（含轻量 trace）。方向未定前导期返回空。"""
        out: list[MergedKline] = []
        for u in self._units:
            trace = StructTrace(
                algo_card_id=_ALGO_CARD_ID,
                rule_id=self._derive_rule_id(u),
                source_from_ts=u.members[0].timestamp,
                source_to_ts=u.members[-1].timestamp,
            )
            out.append(
                MergedKline(
                    period=self.period,
                    dir=u.dir,
                    high=u.high,
                    low=u.low,
                    start_ts=u.members[0].timestamp,
                    end_ts=u.members[-1].timestamp,
                    start_index=u.start_index,
                    end_index=u.end_index,
                    trace=trace,
                )
            )
        return out

    # ── 内部 ─────────────────────────────────────────────────────────────
    def _try_establish(self) -> None:
        """前导期：检查最新相邻对是否确立方向。"""
        n = len(self._lead)
        if n < 2:
            return
        a, b = self._lead[-2], self._lead[-1]
        d = _direction(a.high, a.low, b.high, b.low)
        if d is None:
            return
        # 确立：lead[0..n-2] 必为包含链（更早的可定向对会更早触发），坍缩成首个单元。
        blob = self._lead[: n - 1]
        unit0 = self._merge_blob(blob, d, start_index=0)
        unit1 = _Unit(
            high=b.high, low=b.low, dir=d,
            rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
            start_index=n - 1, members=[b],
        )
        self._units = [unit0, unit1]
        self._lead = []
        self._established = True

    def _merge_blob(self, blob: list[Kline], d: KlineDir, start_index: int) -> _Unit:
        """把方向未定的包含链按确立方向 d 坍缩成首个单元（rule `merge.init`）。"""
        if d is KlineDir.UP:
            high = max(x.high for x in blob)
            low = max(x.low for x in blob)
        else:
            high = min(x.high for x in blob)
            low = min(x.low for x in blob)
        return _Unit(
            high=high, low=low, dir=d, rule_id=RULE_MERGE_INIT,
            start_index=start_index, members=list(blob),
        )

    def _append_established(self, k: Kline, idx: int) -> None:
        last = self._units[-1]
        contained = _contains(last.high, last.low, k.high, k.low) or _contains(
            k.high, k.low, last.high, last.low
        )
        if contained:  # 包含 → 按方向合并取值（rule_id 输出时按成员数派生, 见 _derive_rule_id）
            if last.dir is KlineDir.UP:
                last.high = max(last.high, k.high)
                last.low = max(last.low, k.low)
            else:
                last.high = min(last.high, k.high)
                last.low = min(last.low, k.low)
            last.members.append(k)
            return
        # 非包含 → 必为同时高低之一，新建单元（rule merge.dir.*）
        d = _direction(last.high, last.low, k.high, k.low)
        assert d is not None  # 非包含必可定向
        self._units.append(
            _Unit(
                high=k.high, low=k.low, dir=d,
                rule_id=RULE_MERGE_DIR_UP if d is KlineDir.UP else RULE_MERGE_DIR_DOWN,
                start_index=idx, members=[k],
            )
        )

    def _derive_rule_id(self, u: _Unit) -> str:
        """按单元**当前状态**派生 trace rule_id（§13「最近一次操作」）。

        形成规则 (u.rule_id) 始终保留不变 (merge.init / merge.dir.*)；输出时:
        - 首段 blob → merge.init;
        - 形成后吸收了包含根 (成员 > 1) → merge.contains;
        - 单根方向单元 → 其形成方向 merge.dir.up/down。
        派生而非 mutate, 故 pop/append 回退后 rule_id 自动正确, 无需恢复 (Codex r2 ⚠)。
        """
        if u.rule_id == RULE_MERGE_INIT:
            return RULE_MERGE_INIT
        if len(u.members) > 1:
            return RULE_MERGE_CONTAINS
        return u.rule_id  # 形成时的 merge.dir.up/down

    def _recompute_unit(self, u: _Unit) -> None:
        """从单元剩余 members 按其方向重算极值（pop 末端 K 线后用）。"""
        if u.dir is KlineDir.UP:
            u.high = max(x.high for x in u.members)
            u.low = max(x.low for x in u.members)
        else:
            u.high = min(x.high for x in u.members)
            u.low = min(x.low for x in u.members)
```
