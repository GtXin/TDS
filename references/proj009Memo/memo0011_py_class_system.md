---
title: memo0011_py_class_system
tags:
  - memo
  - python
  - class-design
  - project-009
status: active
source:
  - docs/memo/memo0009_class_kline.md
  - docs/memo/memo0010_class_kline_t_series.md
created: 2026-08-31
---

# memo0011_py_class_system

## 1. Session Overview

### 1.a Purpose

> [purpose] Decide how Project 009 should organize Python class files and
> imports as domain classes grow.

> [question] If `Kline` and `KlineTSeries` live in separate `.py` files, will
> users need to import many modules?

### 1.b Decision

> [decision] Keep the implementation layout close to C++ style when it helps
> clarity: one important domain class per clearly named module.

> [decision] Use package `__init__.py` files to expose a cleaner public import
> surface.

> [note] This gives both:
>
> - clear internal files for implementation and review;
> - short imports for users of the package.

## 2. Main Concepts

### 2.a Internal Module Layout

> [concept] Internal module layout means where the implementation code lives.

> [example] Domain class files:
>
> ```text
> src/tradinglab/domain/
> ├── __init__.py
> ├── kline.py
> └── kline_t_series.py
> ```

> [note] This is acceptable Python practice when each file has a clear domain
> concept. It is not required for every tiny helper class.

### 2.b Public Import Surface

> [concept] Public import surface means how callers usually import the classes.

> [example] Without `__init__.py` exports:
>
> ```python
> from tradinglab.domain.kline import Kline
> from tradinglab.domain.kline_t_series import KlineTSeries
> ```

> [example] With `__init__.py` exports:
>
> ```python
> from tradinglab.domain import Kline, KlineTSeries
> ```

> [decision] Prefer the second style for normal user-facing imports once the
> classes are promoted into `src/`.

## 3. Workflow

### 3.a Export Classes From The Package

> [workflow] After `Kline` and `KlineTSeries` are promoted into `src/`, update
> `src/tradinglab/domain/__init__.py`.

> [example] Package export file:
>
> ```python
> from tradinglab.domain.kline import Kline
> from tradinglab.domain.kline_t_series import KlineTSeries
>
> __all__ = ["Kline", "KlineTSeries"]
> ```

> [example] Caller import:
>
> ```python
> from tradinglab.domain import Kline, KlineTSeries
> ```

### 3.b Keep Source Imports Short

> [decision] Source callers should prefer package imports for stable classes.
>
> ```python
> from tradinglab.domain import Kline, KlineTSeries
> from tradinglab.data_io import CsvFileKlineTSeries
> from tradinglab.visualization import KlineTSeriesChart
> ```

> [decision] During a future experiment stage, explicit experiment imports are
> still fine.

> [example] Previous experiment style:
>
> ```python
> from experiments.data_structures.generic.kline import Kline
> from experiments.data_structures.generic.kline_t_series import KlineTSeries
> ```

> [note] The experiment folder is for learning and verification. The cleaner
> public import surface matters more after promotion into `src/`.

## 4. Rules

### 4.a File Rule

> [rule] Keep one important domain class per module when the class has its own
> memo, tests, or stable responsibility.

> [example] Good:
>
> ```text
> kline.py              # Kline
> kline_t_series.py     # KlineTSeries
> ```

> [warning] Do not split every tiny helper into its own file by habit. Split
> only when the name and responsibility are strong enough to stand alone.

### 4.b Import Rule

> [rule] Use package `__init__.py` to keep common imports short.

> [rule] Put only stable, intended public classes into `__all__`.

> [warning] Do not export experimental or unstable classes from the main package
> before the design is accepted.

## 5. Evidence

### 5.a Project Evidence

> [source] Current Project 009 class memos:
>
> - `docs/memo/memo0009_class_kline.md`
> - `docs/memo/memo0010_class_kline_t_series.md`

> [source] Current source files:
>
> - `src/tradinglab/domain/kline.py`
> - `src/tradinglab/domain/kline_t_series.py`
> - `src/tradinglab/data_io/csv_file_kline_t_series.py`
> - `src/tradinglab/visualization/kline_t_series_chart.py`

### 5.b Python Practice

> [note] Python does not require one class per file. A module can hold several
> related classes.

> [decision] Project 009 still prefers separate modules for major domain
> classes because memo traceability, tests, and later promotion are easier.

## 6. Project Implication

### 6.a For Project 009

> [implication] Keep `Kline` and `KlineTSeries` in separate files.

> [implication] These classes are now exposed from package `__init__.py` files.

> [implication] Future users should be able to write:
>
> ```python
> from tradinglab.domain import Kline, KlineTSeries
> ```

## 7. Open Questions

### 7.a Package Export Timing

> [open] Decide exactly when an experiment class is stable enough to export from
> the package-level `__init__.py`.

> [recommendation] Export only after the class is promoted into `src/` and has
> focused tests.
