# memo0009_class_kline

[class design]

## 0. Scope

> [purpose] Kick off the source restart with a small first class-design pass.
>
> - Design `Kline`.
> - Keep read/write behavior outside domain classes.

> [decision] This memo focuses only on `Kline`.
>
> `KlineTSeries`, loaders, validators, adapters, repositories, and chart objects
> belong in separate memos or later sections.

> [decision] Keep `symbol` and `period` on each `Kline`.
>
> This repeats data inside a long series, but it keeps each data point complete
> when inspected, logged, tested, exported, or moved without its parent series.
> Future metadata such as `source` can follow the same completeness principle
> if the project needs point-level provenance.

> [decision] Add `source` to each `Kline`.
>
> `source` records point-level provenance, such as `manual_sample`, `csv_ke`,
> or a future vendor/feed name. This follows the completeness principle: one
> data point should carry enough identity to be inspected outside its parent
> container.
>
> Empty or whitespace-only `source` is normalized to `NA`, meaning provenance is
> unknown rather than invalid.

> [decision] Experiment first, then promote to `src` core.
>
> - The first trial lived under `experiments/data_structures/generic/`.
> - The accepted source now lives under `src/tradinglab/domain/`.
> - Future uncertain class changes should still go through experiments first.

## 1. Class Design

### 1.1 `Kline` Proposal

#### 1.1.a Meaning

> [concept] `Kline` means one OHLCV candle/bar.
>
> It answers:
>
> > What happened for one symbol during one time period?

> [decision] `Kline` is not a time series.
>
> A future series class may collect many `Kline` objects, but that is outside
> this memo's scope.

#### 1.1.b Location

> [path] Current source file:
>
> ```text
> src/tradinglab/domain/kline.py
> ```

> [result] Promoted to source on 2026-09-01 through `memo0018`.

> [path] Previous experiment file:
>
> ```text
> experiments/data_structures/generic/kline.py
> ```

> [note] The experiment file was removed after promotion. Keep only useful
> intent comments in the source version.

> [convention] Current naming compliance:
>
> - Class name: `Kline` uses PEP 8 `PascalCase`.
> - Module name: `kline.py` uses PEP 8 `snake_case.py`.
> - Methods and properties use `snake_case`.
> - Members use `snake_case`.
> - The file has a module docstring and class docstring.

#### 1.1.c Members

> [decision] Core members:
>
> - `symbol: str`
> - `period: str`
> - `source: str`
> - `timestamp: datetime`
> - `open: float`
> - `high: float`
> - `low: float`
> - `close: float`
> - `volume: float`

> [note] Possible later metadata:
>
> - `timezone: str`
> - `adjusted: bool`

#### 1.1.d Methods And Properties

> [decision] Keep `Kline` methods small and single-candle only.

> [proposal] Properties:
>
> - `body_size`
> - `upper_shadow`
> - `lower_shadow`
> - `is_bullish`
> - `is_bearish`
> - `is_flat`

> [concept] Candle body means the distance between `open` and `close`.
>
> - `body_size = abs(close - open)`
> - `is_bullish = close > open`
> - `is_bearish = close < open`
> - `is_flat = close == open`

> [example] Direction does not change `body_size`.
>
> ```text
> open = 100, close = 108, body_size = 8, is_bullish = true
> open = 108, close = 100, body_size = 8, is_bearish = true
> ```

> [proposal] Methods:
>
> - `validate()`
> - `to_dict()`

> [boundary] Do not add:
>
> - `read()`
> - `write()`
> - `plot()`
> - `save()`
> - `load()`
> - indicator methods such as `moving_average()`
> - series methods such as `sort()` or `slice()`

#### 1.1.e Invariants

> [decision] `Kline` protects only single-bar facts.
>
> - `high >= open`
> - `high >= close`
> - `low <= open`
> - `low <= close`
> - `high >= low`
> - `volume >= 0`
> - `symbol` is not empty
> - `period` is not empty
> - empty or whitespace-only `source` becomes `NA`
> - `timestamp` is present

#### 1.1.f IO Boundary

> [boundary] `Kline` should not read or write files.

> [boundary] `Kline` should not know about CSV, DuckDB, Qlib, chart libraries,
> or APIs.

> [decision] Reading belongs to loaders or adapters. Writing belongs to
> repositories or exporters.

#### 1.1.g First Implementation Shape

> [example] Prefer a frozen dataclass first:
>
> ```python
> @dataclass(frozen=True)
> class Kline:
>     symbol: str
>     period: str
>     source: str
>     timestamp: datetime
>     open: float
>     high: float
>     low: float
>     close: float
>     volume: float
>
>     @property
>     def body_size(self) -> float:
>         return abs(self.close - self.open)
>
>     @property
>     def is_bullish(self) -> bool:
>         return self.close > self.open
> ```

#### 1.1.h Verification

> [verification] Minimum checks:
>
> - valid OHLCV bar can be created
> - invalid `high < low` is rejected
> - negative volume is rejected
> - empty symbol is rejected
> - candle properties return expected values

> [verification] Historical experiment check:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_kline
> ```

## 2. Implementation And Test Results

### 2.1 Source Implementation

> [execution] Current source files:
>
> - `src/tradinglab/domain/kline.py`
> - `tests/domain/test_kline.py`

> [result] `Kline` is now promoted source.
>
> The old experiment file no longer carries the accepted implementation.

### 2.2 Implemented Members

> [execution] `Kline` currently implements:
>
> - `symbol: str`
> - `period: str`
> - `source: str`
> - `timestamp: datetime`
> - `open: float`
> - `high: float`
> - `low: float`
> - `close: float`
> - `volume: float`

### 2.3 Implemented Properties And Methods

> [execution] Properties:
>
> - `body_size`
> - `upper_shadow`
> - `lower_shadow`
> - `is_bullish`
> - `is_bearish`
> - `is_flat`

> [execution] Methods:
>
> - `validate()`
> - `to_dict()`

### 2.4 Test Result

> [execution] Test command:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_kline
> ```

> [execution] Result on 2026-08-31 07:23:
>
> ```text
> Ran 6 tests in 0.001s
> OK
> ```

> [execution] Result on 2026-08-31 11:19 with compact visible test output:
>
> ```text
> Ran 7 tests in 0.001s
> OK
>
> [run] Kline tests: creation, provenance, invariants, candle properties, and to_dict output
> ```

> [verification] The tests cover:
>
> - valid Kline creation
> - `high < low` rejection
> - negative volume rejection
> - empty symbol rejection
> - empty source fallback to `NA`
> - bullish, bearish, and flat candle properties
> - `to_dict()` output

> [execution] Source promotion test command on 2026-09-01:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.domain.test_kline
> ```
>
> [execution] Source promotion result:
>
> ```text
> Ran 7 tests OK
> ```

### 2.5 Sample Use

> [example] Create one `Kline`:
>
> ```python
> from datetime import datetime
>
> from tradinglab.domain import Kline
>
>
> kline = Kline(
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
> ```

> [example] Read stored members and calculated properties:
>
> ```python
> print(kline.symbol)       # AAPL
> print(kline.close)        # 108.0
> print(kline.body_size)    # 8.0
> print(kline.is_bullish)   # True
> print(kline.to_dict())    # Plain dict of stored members.
> ```

> [note] `body_size` and `is_bullish` are properties, so they do not use
> parentheses. `to_dict()` is a method, so it does use parentheses.
