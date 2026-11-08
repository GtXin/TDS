# Design Pattern for Chan Features
## 000 — Scope
To Set up class members for the different Chan Theory features.
## 001 — Design principles
### 001.a — Typical members for Kline and KlineTSeries
Decision: keep `KlineTSeries` a classic OHLCV series; indicator calculations and results stay outside `Kline` and `KlineTSeries`.
Proposal based on proj009: store the raw data once and calculate the remaining properties from it.[1][2]

| Members               | Kline — one bar                                                                                                 | KlineTSeries — ordered bars                                                |
| --------------------- | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stored fields         | `symbol`, `period`, `source`: `str`; `timestamp`: `datetime`; `open`, `high`, `low`, `close`, `volume`: `float` | `klines: tuple[Kline, ...]`                                                |
| Calculated properties | `body_size`, `upper_shadow`, `lower_shadow`, `is_bullish`, `is_bearish`, `is_flat`                              | `symbol`, `period`, `sources`, `count`, `start_timestamp`, `end_timestamp` |
| Core methods          | `validate()`, `to_dict()`                                                                                       | `validate()`, `timestamps()`, `closes()`, `slice_by_count()`               |

- Validate finite OHLCV, `low <= open <= high`, `low <= close <= high`, and nonnegative volume. Require a nonempty series with one symbol/period and strictly increasing timestamps; mixed sources are allowed.[1][2]
- Proposed time convention: use timezone-aware UTC bar-start timestamps; define volume units before implementation.[3]
- Keep raw objects immutable. File I/O, plotting, and Chan-feature results belong in separate components; calculated properties should not duplicate stored data.
## 002 — Implementation
## References

1. [references/proj009Memo/memo0009_class_kline.md](../../references/proj009Memo/memo0009_class_kline.md)
2. [references/proj009Memo/memo0010_class_kline_t_series.md](../../references/proj009Memo/memo0010_class_kline_t_series.md)
3. Python documentation. [Aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects).
