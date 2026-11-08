# Design Pattern for Chan Features
## 000 — Scope
To Set up class members for the different Chan Theory features.
## 001 — Design principles
### 001.a — Typical members for Kline and KlineTSeries
Decision: keep `KlineTSeries` a classic OHLCV series; indicator calculations and results stay outside `Kline` and `KlineTSeries`.
Member baseline adapted from proj009.[1][2]

| Members       | Kline — one bar                                                                                                 | KlineTSeries — ordered bars    |
| ------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| Stored fields | `symbol`, `period`, `source`: `str`; `timestamp`: `datetime`; `open`, `high`, `low`, `close`, `volume`: `float` | `klines: tuple[Kline, ...]`    |
| Core methods  | `__init__(...)`, `validate()`                                                                                   | See proposed methods in 002.c. |

- Validate finite OHLCV, `low <= open <= high`, `low <= close <= high`, and nonnegative volume. Require a nonempty series with one symbol/period and strictly increasing timestamps; mixed sources are allowed.[1][2]
- Decision: store timestamps as timezone-aware UTC `datetime` values; `Kline.timestamp` labels bar start.[3] Convert to local time for display; retain the exchange timezone and trading calendar separately for session and daily-bar boundaries.
- Define volume units before implementation.
- Keep raw objects immutable. File I/O, table adapters, chart rendering and Chan-feature calculations belong in separate components; proposed series convenience methods delegate to those components.
### 001.b — Dependencies between features
Decision: derived series keep one-way references to immutable source series instead of copying source data.
Example design: `MergedKlineSeries.source_series: KlineTSeries` refers to the original raw-series object. Each `MergedKline` stores its merged values and a source range `[start, stop)` within that exact series.
The reference keeps the source alive without duplicating its data. Reassigning the raw-series variable does not change this link. Corrected source data requires a new source snapshot and recalculated results.
### 001.c — Rule-based explanations
Decision: every calculated feature point must support a human-readable explanation grounded in the rules actually applied and their source evidence.
The tree lives in a versioned memo. During calculation, record each visited node/branch, source references, decisive values, and action/state change as a `DecisionStep`; retain false and deferred decisions too.
Pseudocode for the immutable result (not implemented):

```python
@dataclass(frozen=True)
class MergedKlineSeries:
    source_series: KlineTSeries
    klines: tuple[MergedKline, ...]
    rule_tree_ref: str  # Memo path and exact version
    trace: tuple[DecisionStep, ...]  # All executed decisions, in order
    trace_by_point: tuple[tuple[int, ...], ...]  # Trace indices per result

    def explain(self, point_index):
        steps = tuple(self.trace[j] for j in self.trace_by_point[point_index])
        return render_explanation(self.rule_tree_ref, steps)
```

`derive_from()` builds the results, trace and point mapping together, then freezes the collections into tuples. For example, the value `(12, 13, 18)` at `trace_by_point[5]` links result 5 to those three trace entries. Decisions producing no result remain in `trace`.
### 001.d — ChanTable and time series
Decision: keep compact feature records as authoritative results; generate a `ChanTable` view aligned to the original `KlineTSeries` time axis.
`XianduanSeries` holds ordered `Xianduan` records: ID, start/end source references and prices, status, confirmation time, and trace indices. `ChanTable` holds membership IDs and endpoint roles; raw OHLCV remains unchanged.
Storage-only example: segment `id=1` (display `XD1`): K1 → K3; segment `id=2` (display `XD2`): K3 → K5.

| Raw row | Segment IDs | Start IDs | End IDs |
|---|---|---|---|
| K1 | `(1,)` | `(1,)` | `()` |
| K2 | `(1,)` | `()` | `()` |
| K3 | `(1, 2)` | `(2,)` | `(1,)` |
| K4 | `(2,)` | `()` | `()` |
| K5 | `(2,)` | `()` | `(2,)` |

Shared endpoints carry both IDs; uncovered rows remain with empty tuples.[4] Each ID column belongs to one exact feature series/result version; IDs and row indices retain that source snapshot context. Store confirmation time separately from endpoint time: a segment ending at K3 may only become confirmed at K6.
### 001.e — Feature ID naming convention
Decision: store feature `id` as an `int` and sort IDs numerically. Prefixes are display-only: `id=12` and `prefix="MK"` give `label=f"{prefix}{id}"` → `MK12`, without zero padding or a fixed digit width.

| Class | Display prefix | Example label for id=12 |
|---|---|---|
| `MergedKline` | `MK` | `MK12` |
| `Fenxing` | `FX` | `FX12` |
| `Bi` | `BI` | `BI12` |
| `Xianduan` | `XD` | `XD12` |
| `Zhongshu` | `ZS` | `ZS12` |
| `Zoushi` | `ZOU` | `ZOU12` |

IDs are unique within one exact feature series/result version; retain that series and source snapshot/result context with external references. IDs label features independently of tuple positions; series order follows source chronology. Recalculation may assign different IDs. Source lookup uses the owning series's explicit source-series references and stored source indices/ranges.
## 002 — Implementation
### 002.a — Overall classes
Implementation outline based on memo008’s objects.[5] Derived series use the source references, rule traces and ChanTable mapping defined in001.b–001.d; source code is not implemented yet.
**`Kline`** — One immutable raw OHLCV bar with instrument, period, source and timestamp. It validates single-bar data.
**`KlineTSeries`** — An ordered tuple of Kline records for one instrument and period. It validates chronology and provides access and slicing; proposed ChanTable interchange, DataFrame conversion and plotting methods are listed in002.c.
**`MergedKline`** — One resulting K-line after 包含处理, storing adjusted high/low, direction and its source-bar range. Original bars remain unchanged.
**`MergedKlineSeries`** — An ordered collection of MergedKline records referencing the original KlineTSeries. Its derive_from() calculates inclusion results and records the decisions used; validate() checks records, source ranges and trace alignment.
**`Fenxing`** — One top or bottom fractal, recording its price anchor and source window. Its source references point back to the relevant processed K-lines.
**`FenxingSeries`** — An ordered collection of Fenxing records derived from MergedKlineSeries. It retains source references and the rule evidence for each detected fractal.
**`Bi`** — One compact stroke record connecting selected fractal endpoints. It stores endpoint references/prices, direction and calculation status.
**`BiSeries`** — An ordered collection of Bi records calculated using fractals and the required processed-bar context. Shared endpoints retain their source identity.
**`Xianduan`** — One compact line-segment record with endpoint references/prices and status. Its confirmation time is separate from its endpoint time.
**`XianduanSeries`** — An ordered collection of Xianduan records derived from the existing BiSeries. It retains the source sequence, configuration and decision trace.
**`Zhongshu`** — One center with explicit level, time extent and overlapping price bounds. It references the qualifying completed lower-level movements used to establish it.
**`ZhongshuSeries`** — An ordered collection of Zhongshu records at a selected level. Its rules determine center formation and extension from qualified source structures.
**`Zoushi`** — One movement at an explicit level, classified as upward, downward or consolidation. It records its extent, constituent structure references and forming/completed status.
**`ZoushiSeries`** — An ordered collection of Zoushi records at a selected level. It retains source relationships across levels and the decisions establishing each movement.
**`DecisionStep`** — One visited rule-tree node and its branch outcome. It records source references, decisive values and the resulting action/state change.
**`ChanTable`** — A generated view aligned to the original KlineTSeries rows. It maps feature IDs and start/end roles to those rows while compact feature records remain authoritative.
### 002.b — Kline
| Member | Type | Meaning |
|---|---|---|
| `symbol` | `str` | Unambiguous instrument identifier. |
| `period` | `str` | Bar period, such as 1m or 1d. |
| `source` | `str` | Original data source or provenance label. |
| `timestamp` | `datetime` | Timezone-aware UTC bar-start time. |
| `open` | `float` | First price in the bar. |
| `high` | `float` | Highest price in the bar. |
| `low` | `float` | Lowest price in the bar. |
| `close` | `float` | Last price in the bar. |
| `volume` | `float` | Traded quantity in the source-defined units. |

**Methods**

| Method | Purpose |
|---|---|
| `__init__(...)` | Initialize all fields and automatically call `validate()`. |
| `validate()` | Check required fields, timezone-aware UTC timestamp, finite OHLCV, price bounds and nonnegative volume. |
### 002.c — KlineTSeries
| Member | Type | Meaning |
|---|---|---|
| `klines` | `tuple[Kline, ...]` | Original bars in strictly increasing timestamp order. |

**Proposed methods**

| Method | Purpose |
|---|---|
| `__init__(klines)` | Store bars as an immutable tuple and automatically call `validate()`. |
| `validate()` | Require nonempty valid bars, one symbol/period and strictly increasing UTC timestamps; mixed sources are allowed. |
| `__len__()` | Return the bar count: `len(series)`. |
| `__getitem__(key)` | Return one Kline for an integer key or a tuple of bars for a slice; use standard Python indexing/slicing. |
| `__iter__()` | Iterate over bars: `for bar in series`. |
| `from_chan_table(table)` | Class method returning the raw KlineTSeries referenced by a ChanTable, through its adapter. |
| `to_chan_table()` | Return a new ChanTable referencing this raw series; detailed interchange rules remain for002.q. |
| `to_dataframe()` | Return a separate pandas DataFrame indexed by UTC timestamp, with OHLCV and symbol/period/source columns.[6] |
| `plot(**options)` | Delegate candlestick plotting with optional volume to a plotting helper and return its chart. |

`KlineTSeries` is already the domain time series; `to_dataframe()` changes its representation. ChanTable interchange, conversion and plotting methods are convenience wrappers over separate components. Class names use PascalCase, public methods use snake_case, and Python sequence behavior uses special methods such as `__len__`.
### 002.d — MergedKline
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `low` | `float` | Low after inclusion processing. |
| `high` | `float` | High after inclusion processing. |
| `direction` | `Optional[str]` | Up or down; None while direction is unresolved. |
| `source_start` | `int` | First included raw KlineTSeries position. |
| `source_stop` | `int` | Exclusive end position in that same raw series. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.e — MergedKlineSeries
| Member | Type | Meaning |
|---|---|---|
| `source_series` | `KlineTSeries` | Reference to the exact original raw-series object. |
| `klines` | `tuple[MergedKline, ...]` | Resulting bars after inclusion processing, in time order. |
| `config` | immutable config record | Parameters and rule options used for this calculation. |
| `rule_tree_ref` | `str` | Rule-memo location and exact version used by the code. |
| `trace` | `tuple[DecisionStep, ...]` | All executed decisions in order, including decisions producing no result. |
| `trace_by_point` | `tuple[tuple[int, ...], ...]` | For each result position, indices of its relevant entries in trace. |

**Proposed methods**

| Method | Purpose |
|---|---|
| `validate()` | Validate the source series, merged fields/status, unique integer IDs, ordered in-bounds source ranges and trace-to-result alignment. |

Require `len(trace_by_point) == len(klines)` and every trace index to be in bounds. Source ranges resolve within the exact `source_series`; validation preserves stored data.
### 002.f — Fenxing
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `kind` | `str` | Top or bottom fractal. |
| `price` | `float` | Selected fractal anchor price. |
| `anchor_raw_index` | `int` | Anchor position in the original raw series. |
| `source_start` | `int` | First processed-bar position in the source MergedKlineSeries window. |
| `source_stop` | `int` | Exclusive end of that processed-bar window. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.g — FenxingSeries
| Member | Type | Meaning |
|---|---|---|
| `source_series` | `MergedKlineSeries` | Reference to the source series, without copying its data. |
| `items` | `tuple[Fenxing, ...]` | Calculated records in time order. |
| `config`, `rule_tree_ref`, `trace`, `trace_by_point` | See 002.e | Shared calculation settings, rule-tree reference and decision tracing. |
### 002.h — Bi
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `start_fenxing_index` | `int` | Starting endpoint position in the source FenxingSeries. |
| `end_fenxing_index` | `int` | Ending endpoint position in the same FenxingSeries. |
| `start_price` | `float` | Selected starting endpoint price. |
| `end_price` | `float` | Selected ending endpoint price. |
| `direction` | `str` | Up or down. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.i — BiSeries
| Member | Type | Meaning |
|---|---|---|
| `source_series` | `FenxingSeries` | Reference to the source series, without copying its data. |
| `items` | `tuple[Bi, ...]` | Calculated records in time order. |
| `config`, `rule_tree_ref`, `trace`, `trace_by_point` | See 002.e | Shared calculation settings, rule-tree reference and decision tracing. |
### 002.j — Xianduan
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `source_start` | `int` | First included Bi position in the source BiSeries. |
| `source_stop` | `int` | Exclusive end of the member Bi range. |
| `start_price` | `float` | Selected starting endpoint price. |
| `end_price` | `float` | Selected ending endpoint price. |
| `direction` | `str` | Up or down. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.k — XianduanSeries
| Member | Type | Meaning |
|---|---|---|
| `source_series` | `BiSeries` | Reference to the source series, without copying its data. |
| `items` | `tuple[Xianduan, ...]` | Calculated records in time order. |
| `config`, `rule_tree_ref`, `trace`, `trace_by_point` | See 002.e | Shared calculation settings, rule-tree reference and decision tracing. |
### 002.l — Zhongshu
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `level` | `str` | Chan level of the center; distinct from bar period. |
| `lower` | `float` | Lower boundary of the center overlap. |
| `upper` | `float` | Upper boundary of the center overlap. |
| `member_indices` | `tuple[int, ...]` | Positions of qualifying completed lower-level movements in the source series. |
| `start_raw_index` | `int` | First time-axis anchor in the original raw series. |
| `end_raw_index` | `int` | Last time-axis anchor in the original raw series, included. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.m — ZhongshuSeries
| Member | Type | Meaning |
|---|---|---|
| `level` | `str` | Chan level represented by this collection; distinct from bar period. |
| `source_series` | rule-qualified series | Reference to qualifying completed lower-level movements. |
| `items` | `tuple[Zhongshu, ...]` | Calculated records in time order. |
| `config`, `rule_tree_ref`, `trace`, `trace_by_point` | See 002.e | Shared calculation settings, rule-tree reference and decision tracing. |
### 002.n — Zoushi
| Member | Type | Meaning |
|---|---|---|
| `id` | `int` | Numeric identifier within this feature series/result version; display prefix in001.e. |
| `level` | `str` | Chan level of the movement. |
| `kind` | `str` | Upward, downward or consolidation. |
| `source_start` | `int` | First included lower-level constituent position in the source series. |
| `source_stop` | `int` | Exclusive end of that constituent range. |
| `zhongshu_indices` | `tuple[int, ...]` | Positions of constituent centers in the same-level ZhongshuSeries. |
| `start_raw_index` | `int` | First time-axis anchor in the original raw series. |
| `end_raw_index` | `int` | Last time-axis anchor in the original raw series, included. |
| `start_price` | `float` | Selected starting endpoint price. |
| `end_price` | `float` | Selected ending endpoint price. |
| `status` | `str` | Calculation or confirmation state under the selected rules. |
| `confirmed_at` | `Optional[datetime]` | Source evidence time of confirmation; None while unconfirmed. |
### 002.o — ZoushiSeries
| Member | Type | Meaning |
|---|---|---|
| `level` | `str` | Chan level represented by this collection; distinct from bar period. |
| `source_series` | rule-qualified series | Reference to lower-level structures selected by the movement rules. |
| `zhongshu_series` | `ZhongshuSeries` | Reference to the center collection at this movement level. |
| `items` | `tuple[Zoushi, ...]` | Calculated records in time order. |
| `config`, `rule_tree_ref`, `trace`, `trace_by_point` | See 002.e | Shared calculation settings, rule-tree reference and decision tracing. |
### 002.p — DecisionStep
| Member | Type | Meaning |
|---|---|---|
| `node_id` | `str` | Full node location in the versioned rule tree, including call location. |
| `branch` | `str` | Actual branch selected during this visit. |
| `source_refs` | `tuple[tuple[str, int], ...]` | Source-series keys and item positions used by this decision. |
| `checked_values` | immutable named facts | Actual checked values; numbers, strings, booleans or None. |
| `action` | `str` | Action actually taken for this branch. |
| `state_before` | immutable named facts | Relevant intermediate state before the action. |
| `state_after` | immutable named facts | Relevant intermediate state after the action. |
### 002.q — ChanTable
Initial member outline; detailed read/write, feature registration and update rules will be designed later.

| Member | Type | Meaning |
|---|---|---|
| `source_series` | `KlineTSeries` | Exact raw series defining the row/time axis. |
| `feature_series` | read-only mapping | Feature names/levels mapped to exact authoritative series/result versions. |
| `memberships` | read-only column mapping | Per exact feature-series/result-version key, one integer-ID tuple per raw row; shared endpoints may carry two IDs. |
| `start_ids` | read-only column mapping | Per feature-series key and raw row, integer IDs whose starting anchor is at that row. |
| `end_ids` | read-only column mapping | Per feature-series key and raw row, integer IDs whose ending anchor is at that row. |
## References

1. [references/proj009Memo/memo0009_class_kline.md](../../references/proj009Memo/memo0009_class_kline.md)
2. [references/proj009Memo/memo0010_class_kline_t_series.md](../../references/proj009Memo/memo0010_class_kline_t_series.md)
3. Python documentation. [Aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects).
4. [Project 009: XianduanSeries row mapping and shared endpoints](../../references/proj009Memo/memo0036_class_xianduan_series.md).
5. [Memo008: Chan Large Picture](memoWX_008_ChanLargePicture.md).
6. pandas documentation. [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) and [DatetimeIndex](https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html).
