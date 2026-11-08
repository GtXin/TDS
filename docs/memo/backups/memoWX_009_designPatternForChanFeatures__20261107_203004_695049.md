# Design Pattern for Chan Features
## 000 — Scope
To Set up class members for the different Chan Theory features.
## 001 — Design principles
### 001.a — Typical members for Kline and KlineTSeries
Proposal based on proj009: store the raw data once and calculate the remaining properties from it.[1][2]

| Members | Kline — one bar | KlineTSeries — ordered bars |
|---|---|---|
| Stored fields | `symbol`, `period`, `source`: `str`; `timestamp`: `datetime`; `open`, `high`, `low`, `close`, `volume`: `float` | `klines: tuple[Kline, ...]` |
| Calculated properties | `body_size`, `upper_shadow`, `lower_shadow`, `is_bullish`, `is_bearish`, `is_flat` | `symbol`, `period`, `sources`, `count`, `start_timestamp`, `end_timestamp` |
| Core methods | `validate()`, `to_dict()` | `validate()`, `timestamps()`, `closes()`, `slice_by_count()` |

- Validate finite OHLCV, `low <= open <= high`, `low <= close <= high`, and nonnegative volume. Require a nonempty series with one symbol/period and strictly increasing timestamps; mixed sources are allowed.[1][2]
- Proposed time convention: use timezone-aware UTC bar-start timestamps; define volume units before implementation.[3]
- Keep raw objects immutable. File I/O, plotting, and Chan-feature results belong in separate components; calculated properties should not duplicate stored data.
#### Analysis-package compatibility — research proposal
Reviewed 2026-11-07. vn.py provides bar objects with OHLCV and trading fields; mplfinance expects an OHLC DataFrame with a DatetimeIndex; pandas provides time slicing, rolling windows and resampling.[4][5][6] My recommendation is to keep our small domain objects and give analysis packages a standard table through a separate adapter.
Proj009 explicitly calls for dataframe/matrix adapters outside its domain classes.[2] Inspection of its current source confirms the tuple-based series; UTC-aware timestamps are a new TDS proposal, not an existing proj009 guarantee.
Assuming “KK” means KWX’s cc project, its model specification adds market-qualified symbols, bar-open UTC Unix seconds, and optional amount/open_interest/settlement fields.[7] Its time decision makes aggregation boundaries explicit.[8]

- Keep the members above. Use an unambiguous symbol such as `binance:BTCUSDT`; add optional `amount`, `open_interest`, `settlement` only as the markets require. Unknown values should remain missing, not zero.
- Add iteration, length, indexing and time-range slicing to the series. Put indicators and Chan results in separate calculators.
- Provide external `to_dataframe()` / `from_dataframe()` adapters: UTC-aware `DatetimeIndex` named `timestamp`, numeric `open, high, low, close, volume` columns, and explicit symbol/period/source metadata. Preserve per-bar source when mixed; map column capitalization for mplfinance.[5][6]
- Provide a NumPy adapter with explicit column order and a separate timestamp array. Avoid storing another mutable copy inside the series.
- Define volume units, adjustment basis, source timezone, trading calendar and bar-start labeling. Convert cc timestamps with explicit seconds units. Map domain `1m` to pandas `1min`; do not assume frequency strings are interchangeable.
- Distinguish market closures from missing observations; avoid automatic OHLCV forward-fill. For higher bars use first open, maximum high, minimum low, last close and summed volume, with explicit session boundaries and incomplete-bar policy. UTC storage alone does not define those boundaries.[6][8]

These are proposals; no adapters or new fields have been implemented.
## 002 — Implementation
## References

1. [references/proj009Memo/memo0009_class_kline.md](../../references/proj009Memo/memo0009_class_kline.md)
2. [references/proj009Memo/memo0010_class_kline_t_series.md](../../references/proj009Memo/memo0010_class_kline_t_series.md)
3. Python documentation. [Aware and naive datetime objects](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects).

4. vn.py. [BarData source](https://github.com/vnpy/vnpy/blob/master/vnpy/trader/object.py).
5. mplfinance. [DataFrame input](https://github.com/matplotlib/mplfinance).
6. pandas. [Time series functionality](https://pandas.pydata.org/docs/user_guide/timeseries.html).
7. KWX/cc. [Data model specification](../../../cc/docs/stages/stage-04-data-model-spec.md), neighboring repository inspected 2026-11-07.
8. KWX/cc. [Time convention decision](../../../cc/docs/decisions/decision-0026-kline-time-convention.md), neighboring repository inspected 2026-11-07.
