---
title: memo0007_qlib_data_structure
tags:
  - memo
  - qlib
  - data-structure
  - ohlcv
  - project-009
status: active
source:
  - retired source copied before deletion: kb/kb0002_qlib-data-structure.md
  - src/tradinglab/integrations/qlib/converter.py
  - docs/memo/memo0003_memoguidance.md
created: 2026-08-31
---

# memo0007_qlib_data_structure

## 1. Session Overview

### 1.a Purpose

- Preserve the old `kb0002_qlib-data-structure.md` knowledge as a project memo.
- Clarify whether Qlib already supports OHLCV/Kline-style data.
- Protect Project 009's own domain model from leaking Qlib conventions.

### 1.b Question

> [question] Does Qlib already support OHLCV data points, and should Project
> 009 use Qlib as its core Kline data structure?

### 1.c Short Answer

> [answer] Qlib supports OHLCV-style market data as feature fields, but it does
> not primarily expose a simple Project-009-style `Kline` domain class.

> [decision] Project 009 should keep its own `Kline` and `TimeSeries` records,
> then adapt them into Qlib-compatible tabular data when needed.

## 2. Qlib Shape

### 2.a Mental Model

> [concept] Qlib data is closer to:

```text
instrument + datetime + feature fields
```

Common OHLCV fields are represented as feature names:

```text
$open
$high
$low
$close
$volume
```

### 2.b Returned Data Shape

> [source] The old KB record observed Qlib patterns around `D.features(...)`,
> feature expressions, MultiIndex conventions using `instrument` and
> `datetime`, and local data folders such as `calendars/`, `instruments/`, and
> `features/`.

Example table shape:

```text
instrument  datetime             $open   $high   $low    $close  $volume
rb_main     2026-08-20 09:31:00  3500.0  3512.0  3498.0  3508.0  12345.0
```

## 3. Project 009 Shape

### 3.a Native Record

> [decision] Project 009's native OHLCV unit is `Kline`.

```text
Kline(
  symbol="rb_main",
  period="1m",
  timestamp="2026-08-20 09:31:00",
  open=3500.0,
  high=3512.0,
  low=3498.0,
  close=3508.0,
  volume=12345.0
)
```

### 3.b Adapter Direction

> [workflow] Keep the conversion one-way at the boundary until a later milestone
> needs deeper Qlib workflows.

```text
Ke CSV/OHLCV
  -> Project 009 Kline
  -> TimeSeries[Kline]
  -> validation
  -> Qlib adapter
  -> Qlib feature fields: $open, $high, $low, $close, $volume
```

Current adapter:

```text
src/tradinglab/integrations/qlib/converter.py
```

## 4. Project Decision

### 4.a Ownership Boundary

> [decision] Qlib should not own Project 009's core market-data records.

> [decision] Qlib-specific field names, indexes, and DataFrame conventions
> should stay inside `src/tradinglab/integrations/qlib/`.

> [decision] Domain code should speak in Project 009 terms: `Kline`, symbol,
> period, timestamp, open, high, low, close, and volume.

### 4.b Why Not Use Qlib Directly

> [note] Using Qlib feature fields directly as the domain model would make
> early CSV validation, Chanlun drawing, chart reproduction, and non-Qlib
> experiments depend on Qlib conventions too early.

> [note] Keeping `Kline` first lets the project test simple data, charts, and
> algorithms even when Qlib is not installed on the current machine.

## 5. Open Questions

> [open] Should the first real Qlib adapter write Qlib binary feature files, or
> only produce Qlib-compatible Pandas DataFrames?

> [open] Which Project 009 frequency names should map to Qlib frequency names?

> [open] What exact Ke CSV column names and timezone conventions should become
> formal data contracts?
