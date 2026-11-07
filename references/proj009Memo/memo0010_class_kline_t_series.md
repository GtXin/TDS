# memo0010_class_kline_t_series

[class design]

## 0. Scope

> [purpose] Design `KlineTSeries` after the first `Kline` experiment.
>
> - Define what a series of K-lines owns.
> - Keep single-candle logic inside `Kline`.
> - Keep read/write behavior outside `KlineTSeries`.
> - Keep K-line sequences easy to adapt into linear algebra shapes.

> [purpose] Make `KlineTSeries` adapter-friendly for vector and matrix work.
>
> The domain series should preserve ordered, validated K-lines. Linear algebra
> shapes such as arrays, matrices, tensors, or dataframes should be produced by
> adapters so modeling code can use numeric structures without weakening the
> domain object.

> [decision] `KlineTSeries` is a domain collection, not a loader, repository,
> dataframe wrapper, chart object, or strategy object.

> [decision] `Kline` and `KlineTSeries` belong in the domain layer.
>
> They model market facts and sequence rules. They should not depend on pandas,
> NumPy, Qlib, charting libraries, storage engines, or strategy code.

> [decision] Experiment first, then promote to `src` core.
>
> - The first trial lived under `experiments/data_structures/generic/`.
> - The accepted source now lives under `src/tradinglab/domain/`.
> - Future uncertain series changes should still go through experiments first.

> [source] Dependency from `docs/memo/memo0009_class_kline.md`.
>
> - `Kline` means one OHLCV candle/bar.
> - `Kline` now has a source file:
>   `src/tradinglab/domain/kline.py`.
> - `Kline` now has a focused test file:
>   `tests/domain/test_kline.py`.
> - The current `Kline` source test has 7 passing tests.
> - `KlineTSeries` should use `Kline` as its item type.
> - `Kline` keeps `symbol` and `period` for data-point completeness.
> - `Kline` keeps `source`; empty or whitespace-only source becomes `NA`.

## 1. Class Design

### 1.1 `KlineTSeries` Proposal

#### 1.1.a Meaning

> [concept] `KlineTSeries` means an ordered sequence of complete `Kline`
> objects that should share one market instrument and one period.
>
> It answers:
>
> > What happened to one symbol across many time periods?

> [decision] `Kline` owns single-candle facts.
>
> `KlineTSeries` owns facts that require more than one candle.

> [decision] Keep `KlineTSeries` light.
>
> The series should not copy `symbol`, `period`, `source`, timestamps, or close
> prices into separate stored members. It should derive them from `klines` so
> the stored state has one source of truth.

#### 1.1.b Location

> [path] Current source file:
>
> ```text
> src/tradinglab/domain/kline_t_series.py
> ```

> [result] Promoted to source on 2026-09-01 through `memo0018`.

> [path] Previous experiment target:
>
> ```text
> experiments/data_structures/generic/kline_t_series.py
> ```

> [layer] Target layer map:
>
> ```text
> domain/
>   kline.py              # Kline
>   kline_t_series.py     # KlineTSeries
>
> data_io/
>   csv_file_kline_t_series.py   # CSV file <-> KlineTSeries
>
> adapters/
>   kline_t_series_dataframe_adapter.py
>   kline_t_series_matrix_adapter.py
>   kline_t_series_qlib_adapter.py
>
> features/
>   return_calculator.py
>   moving_average_calculator.py
>
> visualization/
>   kline_t_series_chart.py
> ```

#### 1.1.c Members

> [decision] Core members:
>
> - `klines: tuple[Kline, ...]`

> [proposal] Derived properties from the contained `Kline` objects:
>
> - `symbol`
> - `period`
> - `sources`
> - `has_mixed_sources`
> - `start_timestamp`
> - `end_timestamp`
> - `count`

> [note] Prefer tuple over list for the first experiment so the series cannot
> be mutated accidentally after creation.

#### 1.1.d Methods And Properties

> [proposal] Properties:
>
> - `symbol`
> - `period`
> - `sources`
> - `has_mixed_sources`
> - `start_timestamp`
> - `end_timestamp`
> - `count`
> - `is_empty`

> [proposal] Methods:
>
> - `validate()`
> - `to_list()`
> - `timestamps()`
> - `closes()`
> - `slice_by_count(count: int)`

> [note] `sources` returns the distinct provenance values found across the
> series, such as `("csv_ke",)` or `("csv_ke", "NA")`. Mixed sources are valid
> because a later repair, merge, or partial import may produce a complete series
> from different provenance paths.

> [boundary] Do not add:
>
> - `read()`
> - `write()`
> - `save()`
> - `load()`
> - CSV parsing
> - DuckDB access
> - Qlib conversion
> - chart rendering
> - strategy or indicator calculation

#### 1.1.e Invariants

> [decision] `KlineTSeries` protects sequence-level facts.
>
> - every item is a `Kline`
> - timestamps are strictly increasing
> - no duplicate timestamps
> - all K-lines have the same `symbol`
> - all K-lines have the same `period`
> - the series does not remove `symbol` or `period` from individual K-lines
> - source values are not required to be the same
> - each K-line already normalizes unknown source to `NA`

> [open] Should an empty `KlineTSeries` be allowed?
>
> First experiment recommendation: reject empty series. Add an empty-series use
> case later only if a caller actually needs it.

#### 1.1.f Boundaries

> [boundary] `KlineTSeries` should not read or write files.

> [boundary] `KlineTSeries` should not know about CSV, DuckDB, Qlib, chart
> libraries, APIs, strategies, or indicators.

> [decision] Loaders create `KlineTSeries`. Repositories store `KlineTSeries`.
> Adapters convert `KlineTSeries`. The series itself owns ordering and collection
> behavior.

> [decision] Put conversion adapters outside this class.
>
> Do not add `to_dataframe()`, `to_numpy()`, `to_matrix()`, `to_qlib()`, or
> `to_chart()` as `KlineTSeries` methods in the first design. Prefer separate
> adapter or visualization classes:
>
> - `KlineTSeriesDataFrameAdapter`
> - `KlineTSeriesMatrixAdapter`
> - `KlineTSeriesQlibAdapter`
> - `KlineTSeriesChart`

> [boundary] `KlineTSeries` should not repair malformed candles.
>
> If a `Kline` has bad OHLCV facts, fix that at `Kline` creation, loader, or
> adapter level. The series only verifies sequence consistency among already
> constructed `Kline` objects.

#### 1.1.g First Implementation Shape

> [example] Prefer a frozen dataclass first:
>
> ```python
> @dataclass(frozen=True)
> class KlineTSeries:
>     klines: tuple[Kline, ...]
>
>     def __post_init__(self) -> None:
>         self.validate()
>
>     @property
>     def count(self) -> int:
>         return len(self.klines)
>
>     @property
>     def sources(self) -> tuple[str, ...]:
>         return tuple(sorted({kline.source for kline in self.klines}))
> ```

#### 1.1.h Verification

> [verification] Minimum checks:
>
> - valid ordered series can be created
> - empty series is rejected
> - duplicate timestamps are rejected
> - descending timestamps are rejected
> - mixed symbols are rejected
> - mixed periods are rejected
> - mixed sources are allowed and visible through `sources`
> - derived properties return expected values

#### 1.1.i Sample Use

> [example] Create a `KlineTSeries` from existing `Kline` objects:
>
> ```python
> series = KlineTSeries((kline_day_1, kline_day_2))
>
> print(series.symbol)
> print(series.period)
> print(series.sources)
> print(series.count)
> print(series.closes())
> ```

> [note] The series receives `Kline` objects that already passed single-candle
> validation. It should not re-own each candle's OHLC rules.

## 2. Implementation And Test Results

### 2.1 Source Implementation

> [execution] Current source files:
>
> - `src/tradinglab/domain/kline_t_series.py`
> - `tests/domain/test_kline_t_series.py`

> [result] `KlineTSeries` is now promoted source.
>
> The old experiment file no longer carries the accepted implementation.

### 2.2 Implemented Members

> [execution] `KlineTSeries` currently implements:
>
> - `klines: tuple[Kline, ...]`

> [note] `klines` is normalized to a tuple during initialization so callers
> cannot keep list-style mutation inside the series.

### 2.3 Implemented Properties And Methods

> [execution] Properties:
>
> - `symbol`
> - `period`
> - `sources`
> - `has_mixed_sources`
> - `start_timestamp`
> - `end_timestamp`
> - `count`
> - `is_empty`

> [execution] Methods:
>
> - `validate()`
> - `to_list()`
> - `timestamps()`
> - `closes()`
> - `slice_by_count(count: int)`

### 2.4 Test Result

> [execution] Test command:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_kline_t_series
> ```

> [execution] Result on 2026-08-31 11:29 with compact visible test output:
>
> ```text
> Ran 10 tests in 0.000s
> OK
>
> [run] KlineTSeries tests: creation, sequence invariants, derived properties, mixed sources, and count slicing
> ```

> [verification] The tests cover:
>
> - valid ordered series creation
> - empty series rejection
> - duplicate timestamp rejection
> - descending timestamp rejection
> - mixed symbol rejection
> - mixed period rejection
> - mixed source allowance
> - non-`Kline` item rejection
> - derived properties and accessors
> - `slice_by_count()` result and invalid count rejection

> [execution] Source promotion test command on 2026-09-01:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.domain.test_kline_t_series
> ```
>
> [execution] Source promotion result:
>
> ```text
> Ran 10 tests OK
> ```

### 2.5 Sample Use

> [example] Create one `KlineTSeries`:
>
> ```python
> from datetime import datetime
>
> from tradinglab.domain import Kline, KlineTSeries
>
>
> first = Kline(
>     symbol="AAPL",
>     period="1d",
>     source="manual_sample",
>     timestamp=datetime(2026, 8, 31),
>     open=100.0,
>     high=110.0,
>     low=98.0,
>     close=108.0,
>     volume=1_000_000.0,
> )
>
> second = Kline(
>     symbol="AAPL",
>     period="1d",
>     source="csv_ke",
>     timestamp=datetime(2026, 9, 1),
>     open=108.0,
>     high=112.0,
>     low=106.0,
>     close=111.0,
>     volume=1_200_000.0,
> )
>
> series = KlineTSeries((first, second))
> ```

> [example] Read derived sequence facts:
>
> ```python
> print(series.symbol)            # AAPL
> print(series.period)            # 1d
> print(series.sources)           # ("csv_ke", "manual_sample")
> print(series.has_mixed_sources) # True
> print(series.count)             # 2
> print(series.closes())          # (108.0, 111.0)
> ```

> [note] `sources`, `count`, and timestamp bounds are properties. `closes()`,
> `timestamps()`, `to_list()`, and `slice_by_count()` are methods.
