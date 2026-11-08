# Design Pattern for Chan Features
## 000 — Scope
To Set up class members for the different Chan Theory features.
## 001 — Design principles
### 001.a — Typical members for Kline and KlineTSeries
Decision: keep `KlineTSeries` a classic OHLCV series; indicator calculations and results stay outside `Kline` and `KlineTSeries`.
Member baseline adapted from proj009.[1][2]

| Members               | Kline — one bar                                                                                                 | KlineTSeries — ordered bars                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stored fields         | `symbol`, `period`, `source`: `str`; `timestamp`: `datetime`; `open`, `high`, `low`, `close`, `volume`: `float` | `klines: tuple[Kline, ...]`                                                |
| Core methods          | `validate()`, `to_dict()`                                                                                       | `validate()`, `timestamps()`, `closes()`, `slice_by_count()`               |

- Validate finite OHLCV, `low <= open <= high`, `low <= close <= high`, and nonnegative volume. Require a nonempty series with one symbol/period and strictly increasing timestamps; mixed sources are allowed.[1][2]
- Proposed time convention: use timezone-aware UTC bar-start timestamps; define volume units before implementation.[3]
- Keep raw objects immutable. File I/O, plotting, and Chan-feature results belong in separate components.
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
### 001.d — Master table and time series
Decision: keep compact feature records as authoritative results; generate a master mapping table aligned to the original `KlineTSeries` time axis.
`XianduanSeries` holds ordered `Xianduan` records: ID, start/end source references and prices, status, confirmation time, and trace indices. The master table holds membership IDs and endpoint roles; raw OHLCV remains unchanged.
Storage-only example: `XD1: K1 → K3`, `XD2: K3 → K5`.

| Raw row | Segment IDs | Start IDs | End IDs |
|---|---|---|---|
| K1 | `("XD1",)` | `("XD1",)` | `()` |
| K2 | `("XD1",)` | `()` | `()` |
| K3 | `("XD1", "XD2")` | `("XD2",)` | `("XD1",)` |
| K4 | `("XD2",)` | `()` | `()` |
| K5 | `("XD2",)` | `()` | `("XD2",)` |

Shared endpoints carry both IDs; uncovered rows remain with empty tuples.[4] IDs and row indices belong to the same source snapshot/result version. Store confirmation time separately from endpoint time: a segment ending at K3 may only become confirmed at K6.
## 002 — Implementation
### 002.a — Overall classes
Implementation outline based on memo008’s objects.[5] Derived series use the source references, rule traces and master mapping defined in001.b–001.d; source code is not implemented yet.

**`Kline`** — One immutable raw OHLCV bar with instrument, period, source and timestamp. It validates single-bar data.

**`KlineTSeries`** — An ordered tuple of Kline records for one instrument and period. It validates chronology and provides basic access and slicing.

**`MergedKline`** — One resulting K-line after 包含处理, storing adjusted high/low, direction and its source-bar range. Original bars remain unchanged.

**`MergedKlineSeries`** — An ordered collection of MergedKline records referencing the original KlineTSeries. Its derive_from() calculates inclusion results and records the decisions used.

**`Fenxing`** — One top or bottom fractal, recording its price anchor and source window. Its identity points back to the relevant processed K-lines.

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

**`MasterTable`** — A generated view aligned to the original KlineTSeries rows. It maps feature IDs and start/end roles to those rows while compact feature records remain authoritative.
## References

1. [references/proj009Memo/memo0009_class_kline.md](../../references/proj009Memo/memo0009_class_kline.md)
2. [references/proj009Memo/memo0010_class_kline_t_series.md](../../references/proj009Memo/memo0010_class_kline_t_series.md)
3. Python documentation. [Aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects).
4. [Project 009: XianduanSeries row mapping and shared endpoints](../../references/proj009Memo/memo0036_class_xianduan_series.md).
5. [Memo008: Chan Large Picture](memoWX_008_ChanLargePicture.md).
