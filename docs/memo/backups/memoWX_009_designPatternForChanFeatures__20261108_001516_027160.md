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

`derive_from()` builds the results, trace and point mapping together, then freezes the collections into tuples. For example, `trace_by_point[5] = (12, 13, 18)` means result 5 is explained by trace entries 12, 13 and 18. Decisions producing no result remain in `trace`.
## 002 — Implementation
## References

1. [references/proj009Memo/memo0009_class_kline.md](../../references/proj009Memo/memo0009_class_kline.md)
2. [references/proj009Memo/memo0010_class_kline_t_series.md](../../references/proj009Memo/memo0010_class_kline_t_series.md)
3. Python documentation. [Aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects).
