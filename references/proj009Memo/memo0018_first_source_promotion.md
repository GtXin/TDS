# memo0018_first_source_promotion

[source promotion]

## 0. Preparation

### 0.a Code Finished

> [condition] Promote only code that already survived experiment pressure.

Candidate set:

```text
Kline
KlineTSeries
CsvFileKlineTSeries
KlineTSeriesChart
```

These four classes already form the first useful loop:

```text
CSV file -> Kline -> KlineTSeries -> chart artifact
```

### 0.b Major Tests And Boundary Tests

> [condition] Start from a green experiment baseline.

Current evidence:

```text
KlineTSeriesChart focused tests: 15 passing
Combined experiment tests: 42 passing
```

Boundary checks already covered:

- `Kline` validates one candle, not a series.
- `KlineTSeries` validates ordering, symbol, period, and source visibility.
- `CsvFileKlineTSeries` owns CSV read/write, not domain behavior.
- `KlineTSeriesChart` owns chart output, not CSV reading or series repair.
- Fixed-width chart output changes image width, not y-axis scaling.

### 0.c Backup Before Move

> [rule] Preserve the experiment state before moving code.

Minimum backup evidence:

```zsh
git status --short
git diff --check
.venv/bin/python -m unittest \
  experiments.data_structures.generic.test_kline \
  experiments.data_structures.generic.test_kline_t_series \
  experiments.data_structures.generic.test_csv_file_kline_t_series \
  experiments.visualization_trials.kline_t_series_chart.test_kline_t_series_chart
```

> [note] A Git commit would be the cleanest backup if the user wants one.
>
> Without a commit, the master log plus green experiment tests are the minimum
> trace.

## 1. Move Code To Source Folders

### 1.a Domain Set

Move domain facts first:

```text
experiments/data_structures/generic/kline.py
-> src/tradinglab/domain/kline.py

experiments/data_structures/generic/kline_t_series.py
-> src/tradinglab/domain/kline_t_series.py
```

Update import:

```python
from tradinglab.domain.kline import Kline
```

### 1.b Data IO Set

Move file communication next:

```text
experiments/data_structures/generic/csv_file_kline_t_series.py
-> src/tradinglab/data_io/csv_file_kline_t_series.py
```

Update imports:

```python
from tradinglab.domain.kline import Kline
from tradinglab.domain.kline_t_series import KlineTSeries
```

### 1.c Visualization Set

Move chart object last:

```text
experiments/visualization_trials/kline_t_series_chart/kline_t_series_chart.py
-> src/tradinglab/visualization/kline_t_series_chart.py
```

Update import:

```python
from tradinglab.domain.kline_t_series import KlineTSeries
```

> [boundary] Generated PNG files stay under `artifacts/`, not `src/`.

## 2. Update `__init__.py` In Detail

### 2.a Root Package

Create:

```text
src/tradinglab/__init__.py
```

Keep it minimal:

```python
"""Project 009 trading research package."""
```

> [decision] Do not export everything from top-level `tradinglab` yet.

### 2.b Domain Package

Create or update:

```text
src/tradinglab/domain/__init__.py
```

Content:

```python
from tradinglab.domain.kline import Kline
from tradinglab.domain.kline_t_series import KlineTSeries

__all__ = ["Kline", "KlineTSeries"]
```

Normal import:

```python
from tradinglab.domain import Kline, KlineTSeries
```

### 2.c Data IO Package

Create or update:

```text
src/tradinglab/data_io/__init__.py
```

Content:

```python
from tradinglab.data_io.csv_file_kline_t_series import CsvFileKlineTSeries

__all__ = ["CsvFileKlineTSeries"]
```

Normal import:

```python
from tradinglab.data_io import CsvFileKlineTSeries
```

### 2.d Visualization Package

Create or update:

```text
src/tradinglab/visualization/__init__.py
```

Content:

```python
from tradinglab.visualization.kline_t_series_chart import KlineTSeriesChart

__all__ = ["KlineTSeriesChart"]
```

Normal import:

```python
from tradinglab.visualization import KlineTSeriesChart
```

## 3. Move Tests

### 3.a Test Destination

Move accepted tests into source-facing test folders:

```text
experiments/data_structures/generic/test_kline.py
-> tests/domain/test_kline.py

experiments/data_structures/generic/test_kline_t_series.py
-> tests/domain/test_kline_t_series.py

experiments/data_structures/generic/test_csv_file_kline_t_series.py
-> tests/data_io/test_csv_file_kline_t_series.py

experiments/visualization_trials/kline_t_series_chart/test_kline_t_series_chart.py
-> tests/visualization/test_kline_t_series_chart.py
```

### 3.b Test Import Rule

After the move, tests import from `tradinglab`, not `experiments`:

```python
from tradinglab.domain import Kline, KlineTSeries
from tradinglab.data_io import CsvFileKlineTSeries
from tradinglab.visualization import KlineTSeriesChart
```

### 3.c Stale Test Rule

> [warning] Do not preserve old API names just because stale tests mention
> them.

Old pre-reset names to remove, rewrite, or quarantine:

```text
TimeSeries
CsvKlineLoader
KlineValidator
MplfinanceChartAdapter
QlibKlineConverter
```

Accepted first-source names:

```text
Kline
KlineTSeries
CsvFileKlineTSeries
KlineTSeriesChart
```

## 4. Rerun Tests

### 4.a Source Import Smoke Test

Run:

```zsh
PYTHONPATH=src .venv/bin/python - <<'PY'
from tradinglab.domain import Kline, KlineTSeries
from tradinglab.data_io import CsvFileKlineTSeries
from tradinglab.visualization import KlineTSeriesChart

print(Kline.__name__)
print(KlineTSeries.__name__)
print(CsvFileKlineTSeries.__name__)
print(KlineTSeriesChart.__name__)
PY
```

Expected output:

```text
Kline
KlineTSeries
CsvFileKlineTSeries
KlineTSeriesChart
```

### 4.b Promoted Test Suite

Run:

```zsh
PYTHONPATH=src .venv/bin/python -m unittest \
  tests.domain.test_kline \
  tests.domain.test_kline_t_series \
  tests.data_io.test_csv_file_kline_t_series \
  tests.visualization.test_kline_t_series_chart
```

Expected result:

```text
OK
```

### 4.c Artifact Check

Regenerate at least one small chart through source imports:

```text
data_samples/kline/kline_15m_minimal.csv
-> artifacts/charts/kline_t_series/kline_15m_minimal.png
```

## 5. Check Whether Interaction Tests Are Needed

### 5.a Interaction Test Candidate

> [question] Do we need one real end-to-end interaction test?

Recommended interaction:

```text
CsvFileKlineTSeries.read()
-> KlineTSeries
-> KlineTSeriesChart.render_to_file()
-> non-empty PNG
```

### 5.b Judgment

> [decision] Yes, keep one small interaction test after promotion.

Use:

```text
data_samples/kline/kline_15m_minimal.csv
```

> [boundary] Do not put the 10,060-row extreme-wide chart in normal source CI.
>
> It is a stress artifact, not a daily confidence test.

## 6. Conclude

### 6.a Promotion Is Complete When

Checklist:

- source files live under `src/tradinglab/`;
- package `__init__.py` exports work;
- tests import from `tradinglab`;
- stale pre-reset API tests are gone or quarantined;
- promoted tests pass;
- one small interaction test passes;
- one chart artifact can still be generated;
- `docs/classDesign.md`, `docs/status.md`, and `docs/repo-structure.md` are
  updated;
- `docs/distilled-memory.md` and `docs/master-log.md` are updated.

### 6.b Actual Completion

> [result] Completed on 2026-09-01.

Promoted source:

```text
src/tradinglab/domain/kline.py
src/tradinglab/domain/kline_t_series.py
src/tradinglab/data_io/csv_file_kline_t_series.py
src/tradinglab/visualization/kline_t_series_chart.py
```

Promoted tests:

```text
tests/domain/test_kline.py
tests/domain/test_kline_t_series.py
tests/data_io/test_csv_file_kline_t_series.py
tests/visualization/test_kline_t_series_chart.py
```

Retired stale pre-reset tests:

```text
tests/data_io/test_csv_loader.py
tests/data_io/test_validation.py
tests/integrations/test_qlib_converter.py
tests/integrations/test_qlib_smoke.py
tests/visualization/test_mplfinance_chart.py
```

Verification:

```text
source import smoke: passed
focused promoted suite: 42 tests OK
test discovery under tests/: 42 tests OK
source chart artifact: artifacts/charts/kline_t_series/kline_15m_minimal.png, 33445 bytes
```

### 6.c Promotion Is Not

> [boundary] This is not the moment to build the whole architecture.

Do not add these folders only because they exist in the long-term map:

```text
market_views/
features/
strategies/
agents/
simulation/
evaluation/
```

Do not promote Qlib converter code unless a fresh Qlib milestone asks for it.

## 7. Remove Settled Experiment Code

### 7.a Removal Timing

> [rule] Remove settled experiment implementation only after source tests are
> green.

Order:

```text
promote source
update imports
move tests
run tests
confirm interaction test
update docs/log
then remove settled experiment code
```

### 7.b What To Keep

Keep lightweight experiment history if it helps future readers:

```text
experiments/data_structures/README.md
experiments/visualization_trials/README.md
```

Possible note:

```text
These classes were promoted to src/tradinglab/ in milestone 7.R.
```

### 7.c What To Remove

Remove duplicate settled implementation after promotion:

```text
experiments/data_structures/generic/kline.py
experiments/data_structures/generic/kline_t_series.py
experiments/data_structures/generic/csv_file_kline_t_series.py
experiments/visualization_trials/kline_t_series_chart/kline_t_series_chart.py
```

Remove or move duplicate experiment tests after the promoted tests pass.

> [principle] One accepted implementation should live in one place.
>
> After promotion, `src/` owns stable code. `experiments/` returns to being a
> sandbox.
