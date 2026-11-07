# memo0017_class_kline_t_series_chart

[class design]

## 0. Scope

> [purpose] Design the first plotting class for `KlineTSeries`.
>
> - Plot a `KlineTSeries` as a reproducible K-line chart.
> - Keep the design OOP-first, not pipeline-first.
> - Use a known plotting package instead of hand-drawing candlesticks.
> - Allow an optional local chart window for human inspection.
> - Keep the x-axis date-focused by default for dense intraday data.
> - Support a fixed-K-bar-width output mode for readable sliced charts.
> - Keep first-round scope to one class.

> [decision] First-round class name:
>
> ```text
> KlineTSeriesChart
> ```

> [decision] `KlineTSeriesChart` belongs to the visualization layer.
>
> `KlineTSeries` remains a domain object. It should not import pandas,
> matplotlib, mplfinance, Plotly, TradingView, or any chart library.

> [decision] Experiment first, then promote to `src`.
>
> First trial:
>
> ```text
> experiments/visualization_trials/kline_t_series_chart/
> ```
>
> Later stable source location:
>
> ```text
> src/tradinglab/visualization/kline_t_series_chart.py
> ```

## 1. Package Decision

### 1.a Use A Known Plotting Package

> [decision] Use `mplfinance` for the first experiment.

> [reason] `mplfinance` is already listed in this repo's visualization optional
> dependencies through:
>
> ```text
> pyproject.toml
> visualization = ["pandas", "matplotlib", "mplfinance"]
> ```

> [reason] The first chart should be a static, reproducible artifact.
>
> That matches the current Project 009 evidence habit: read known input,
> generate a chart under `artifacts/`, record the command, and compare later.

> [decision] File output is the default verification path.
>
> A local plot window is useful for human inspection, but it should be optional
> because automated tests and headless runs should not depend on GUI behavior.

> [source] Official package references:
>
> - `mplfinance`: https://github.com/matplotlib/mplfinance
> - Plotly candlestick: https://plotly.com/python/reference/candlestick/
> - TradingView Lightweight Charts: https://tradingview.github.io/lightweight-charts/

### 1.b Later Packages

> [future] Plotly can be useful later for interactive HTML artifacts.

> [future] TradingView Lightweight Charts can be useful later for a browser UI.
>
> It should not be the first Python experiment because it moves the problem into
> frontend integration before the K-line data path is stable.

## 2. Class Design

### 2.a `KlineTSeriesChart`

> [concept] `KlineTSeriesChart` is a visual object for one `KlineTSeries`.
>
> It answers:
>
> > How should this K-line time series be seen?

> [decision] `KlineTSeriesChart` owns the visual view.
>
> It can know about chart title, whether volume is shown, whether a local
> window should be opened, and which plotting backend is used. It should not
> own market-data validation, CSV reading, strategy logic, or Chanlun structure
> detection.

### 2.b Members

> [proposal] First-round members:
>
> - `series: KlineTSeries`
> - `title: str`
> - `show_volume: bool`
> - `date_format: str = "%Y-%m-%d"`
> - `output_mode: str = "fit"`
> - `min_kbar_width_px: int = 3`
> - `height_px: int = 575`
> - `dpi: int = 100`
> - `open_window: bool = False`
> - `backend: str = "mplfinance"`

> [decision] `open_window` defaults to `False`.
>
> Saving a chart artifact should work in scripts, tests, remote shells, and
> future CI. Opening a GUI window is a local, human-facing option.

> [decision] `date_format` defaults to `%Y-%m-%d`.
>
> The first full-record chart is intraday 15-minute data, but the most useful
> overview axis is calendar date. The chart object passes this setting to the
> `mplfinance` backend as its internal axis formatter.

> [decision] `output_mode` supports two first-round choices.
>
> ```text
> fit                 # normal overview chart; mplfinance chooses default width
> fixed_kbar_width    # image width grows from K-line count
> ```

> [decision] `fixed_kbar_width` means readable chart-space budget per K bar.
>
> The chart computes:
>
> ```text
> width_px = max(800, series.count * min_kbar_width_px + 160)
> ```
>
> This keeps sliced charts from compressing too many candles into an 800-pixel
> canvas. It does not change the domain data, timestamp precision, or candle
> values.

> [decision] Keep y-axis scaling automatic.
>
> The fixed-width mode changes figure width only. It does not pass manual
> `ylim` or `volume_ylim` values to `mplfinance`, so price and volume ranges are
> still derived from the plotted `KlineTSeries`.

> [decision] Keep style small in the first round.
>
> Do not create `KlineTSeriesChartStyle`, `KlineTSeriesChartFrame`, or
> `KlineTSeriesChartArtifact` yet. Add those only after the single class
> becomes too crowded or more than one backend/output shape is real.

### 2.c Methods

> [proposal] First public methods:
>
> ```python
> render_to_file(path: Path) -> Path
> show_window(block: bool = True) -> None
> ```

> [decision] `render_to_file()` creates a reproducible chart artifact.
>
> The returned `Path` is enough for the first experiment. A richer artifact
> result object can come later if the caller needs metadata.

> [decision] `show_window()` displays the chart in a local plotting window.
>
> This is for visual inspection while developing. It may block depending on the
> backend, so the method accepts `block`.

> [decision] If `open_window=True`, `render_to_file()` may save the artifact
> and then call `show_window()`.
>
> Keep this behavior optional and explicit at construction time.

> [note] The class may use a private helper such as
> `_to_mplfinance_dataframe()` internally.
>
> Keep that private in the first round. Do not expose `to_dataframe()` as a
> public `KlineTSeries` method.

### 2.d Boundaries

> [boundary] Do not add chart behavior to `KlineTSeries`.

> [boundary] Do not add CSV loading to `KlineTSeriesChart`.

> [boundary] Do not require GUI access for normal verification.
>
> Window display is optional. Automated tests should verify the method by
> patching or isolating the plotting backend, not by forcing a real desktop
> window to open.

> [boundary] Do not make `mplfinance` the architecture center.
>
> `mplfinance` is the backend detail. `KlineTSeriesChart` is the project
> object.

> [boundary] Do not split into adapter and renderer classes in the first round.
>
> That split may be correct later, but creating several chart classes now makes
> the design feel procedural before the object has earned its shape.

## 3. Object Relationship

### 3.a First-Round Shape

> [design] Keep the first chart path simple:
>
> ```text
> CsvFileKlineTSeries
>   -> KlineTSeries
>   -> KlineTSeriesChart
>   -> PNG artifact
> ```

> [decision] The object boundary is:
>
> ```text
> KlineTSeries   # domain object
> KlineTSeriesChart  # visualization object
> mplfinance         # backend inside KlineTSeriesChart
> PNG file           # generated evidence
> plot window        # optional local inspection
> ```

### 3.b Why This Is More OOP

> [decision] `KlineTSeriesChart` is not just a procedural adapter.
>
> It represents a real visual object: one chart view over one time series. The
> chart owns its display choices and the act of producing a visual artifact.

> [reason] The project should start from objects with responsibilities:
>
> - `Kline` owns one market fact.
> - `KlineTSeries` owns ordered market facts.
> - `CsvFileKlineTSeries` owns file communication.
> - `KlineTSeriesChart` owns visual presentation.

## 4. Sample Use

### 4.a Read Then Plot

> [example] First expected usage:
>
> ```python
> from pathlib import Path
>
> from tradinglab.data_io import CsvFileKlineTSeries
> from tradinglab.visualization import KlineTSeriesChart
>
> series = CsvFileKlineTSeries(
>     Path("data_samples/kline/kline_15m_minimal.csv"),
>     default_source="data_samples_kline",
> ).read()
>
> chart = KlineTSeriesChart(
>     series=series,
>     title="Kline 15m Minimal Sample",
>     show_volume=True,
> )
>
> chart_path = chart.render_to_file(
>     Path("artifacts/charts/kline_t_series/kline_15m_minimal.png")
> )
> print(chart_path)
>
> chart.show_window(block=True)
> ```

> [note] The sample path uses the stable shape-based fixture folder.
>
> Full source-preserving reference cases stay under `records/`.

### 4.b Full Series Fixed-K-Bar-Width Output

> [example] Whole preserved record with one fixed-width K-bar budget:
>
> ```python
> from pathlib import Path
> import warnings
>
> from tradinglab.data_io import CsvFileKlineTSeries
> from tradinglab.visualization import KlineTSeriesChart
>
> series = CsvFileKlineTSeries(
>     Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv"),
>     default_source="records_cc_kline_to_zoushi_001",
> ).read()
>
> chart = KlineTSeriesChart(
>     series=series,
>     title="DCE KQ.m@m 15m | Full series fixed K-bar width",
>     output_mode="fixed_kbar_width",
> )
>
> with warnings.catch_warnings():
>     warnings.simplefilter("ignore", UserWarning)
>     chart_path = chart.render_to_file(
>         Path(
>             "artifacts/charts/kline_t_series/"
>             "dce_kqm_m_15m_all_fixed_kbar_width.png"
>         )
>     )
>
> print(chart_path)
> ```

> [note] This output is intentionally extreme wide.
>
> With `10,060` K-lines and the default `min_kbar_width_px=3`, the computed
> figure is about `30,340 x 575` pixels. The warning suppression only hides
> `mplfinance`'s row-count warning; it does not change data, width, or y-axis
> scaling.

## 5. Verification Plan

### 5.a Minimum Checks

> [verification] First implementation should prove:
>
> - a `KlineTSeriesChart` can be created from a valid `KlineTSeries`;
> - `render_to_file()` creates the parent folder if needed;
> - `render_to_file()` writes a non-empty PNG;
> - unsupported backend values are rejected;
> - chart generation does not mutate the source `KlineTSeries`;
> - chart output works with `show_volume=True` and `show_volume=False`;
> - fixed-K-bar-width output expands figure width without manual y-axis limits;
> - `show_window()` is available but not required by automated tests.

### 5.b Visual Check

> [verification] Manual chart review should confirm:
>
> - time axis is ordered;
> - x-axis labels focus on dates rather than intraday time;
> - OHLC candle shape looks plausible;
> - volume panel appears when requested;
> - local plot window can be opened when `open_window=True` or
>   `show_window()` is called;
> - title contains the intended symbol, period, or sample name;
> - artifact path is recorded in the memo or execution log.

## 6. Open Questions

### 6.a Questions To Revisit

> [open] Should a later `KlineTSeriesChart` support multiple output formats,
> such as PNG, SVG, and HTML?

> [open] Should chart styling become a separate `KlineTSeriesChartStyle`
> object?

> [open] Should rendered output become a `KlineTSeriesChartArtifact` object
> instead of returning a `Path`?

> [open] Should interactive Plotly output be a second backend inside
> `KlineTSeriesChart`, or should it become a separate chart class later?

> [open] Should time-window selection become a chart option, or should callers
> slice `KlineTSeries` before creating the chart?

## 7. Current Decision

> [decision] For memo0017, keep the design to one class:
>
> ```text
> KlineTSeriesChart
> ```

> [decision] Place it in the visualization layer, try it in experiments first,
> use `mplfinance` internally, allow optional local window display, and keep
> `KlineTSeries` free of plotting code.

> [result] Promoted to source on 2026-09-01 through `memo0018`.
>
> Current source:
>
> ```text
> src/tradinglab/visualization/kline_t_series_chart.py
> ```

## 8. Implementation And Test Results

### 8.a Source Implementation

> [execution] Original experiment files:
>
> ```text
> experiments/visualization_trials/README.md
> experiments/visualization_trials/kline_t_series_chart/README.md
> experiments/visualization_trials/kline_t_series_chart/kline_t_series_chart.py
> experiments/visualization_trials/kline_t_series_chart/test_kline_t_series_chart.py
> ```

> [execution] Current source files after promotion:
>
> ```text
> src/tradinglab/visualization/kline_t_series_chart.py
> tests/visualization/test_kline_t_series_chart.py
> ```

> [execution] Implemented `KlineTSeriesChart` as a frozen dataclass.
>
> Public members:
>
> - `series: KlineTSeries`
> - `title: str`
> - `show_volume: bool`
> - `date_format: str`
> - `output_mode: str`
> - `min_kbar_width_px: int`
> - `height_px: int`
> - `dpi: int`
> - `open_window: bool`
> - `backend: str`

> [execution] Implemented public methods:
>
> - `render_to_file(path: Path) -> Path`
> - `show_window(block: bool = True) -> None`

> [boundary] `KlineTSeriesChart` reads no CSV files and changes no
> `KlineTSeries` data.
>
> It converts to an `mplfinance` DataFrame privately and keeps plotting out of
> the domain class.

### 8.b Dependency Update

> [execution] Installed the declared visualization backend into the local
> `.venv`:
>
> ```zsh
> uv pip install --python .venv/bin/python mplfinance
> ```

> [verification] Verified package versions:
>
> ```text
> pandas 2.3.3
> matplotlib 3.11.1
> mplfinance 0.12.10b0
> ```

### 8.c Generated Artifact

> [execution] Generated a reproducible minimal sample chart:
>
> ```text
> artifacts/charts/kline_t_series/kline_15m_minimal.png
> ```

> [verification] Artifact check:
>
> ```text
> exists: true
> size: 32899 bytes
> ```

> [verification] Source promotion artifact check on 2026-09-01:
>
> ```text
> source import path: tradinglab.visualization.KlineTSeriesChart
> exists: true
> size: 33445 bytes
> ```

> [visual check] The PNG shows two K-line candles, date-focused x-axis labels,
> and a volume panel from the tiny
> `data_samples/kline/kline_15m_minimal.csv` fixture.
>
> Repeated x-axis labels are expected for this two-row minimal sample.

> [execution] Generated a full-record chart from preserved CC evidence:
>
> ```text
> artifacts/charts/kline_t_series/dce_kqm_m_15m_all.png
> ```

> [verification] Full-record artifact check:
>
> ```text
> rows: 10060
> start: 2024-10-28T05:45:00+00:00
> end: 2026-08-19T06:45:00+00:00
> exists: true
> size: 72356 bytes
> ```

> [visual check] The full-record chart uses date-focused x-axis labels such as
> `2024-10-28`, `2025-03-10`, `2025-07-17`, `2025-11-25`, `2026-04-09`, and
> `2026-08-17`.

> [note] `mplfinance` warned that this is too much data to inspect individual
> candles clearly.
>
> That is expected for a full 10,060-row candle chart. The full chart is useful
> for high-level shape inspection; detailed candle inspection should use a
> smaller sliced `KlineTSeries`.

> [execution] Generated a requested Asia/Shanghai time-window chart:
>
> ```text
> artifacts/charts/kline_t_series/dce_kqm_m_15m_20250407_0900_20250421_2200.png
> ```

> [verification] Time-window artifact check:
>
> ```text
> requested window: 2025-04-07 09:00 to 2025-04-21 22:00 Asia/Shanghai
> UTC filter: 2025-04-07T01:00:00+00:00 to 2025-04-21T14:00:00+00:00
> rows: 250
> exists: true
> size: 40276 bytes
> ```

> [visual check] The sliced chart title fits, the x-axis uses calendar dates,
> and the chart is readable enough for candle-level inspection.

> [execution] Generated a second requested-window chart using fixed-K-bar-width
> output:
>
> ```text
> artifacts/charts/kline_t_series/dce_kqm_m_15m_20250407_0900_20250421_2200_fixed_kbar_width.png
> ```

> [verification] Fixed-width artifact check:
>
> ```text
> output_mode: fixed_kbar_width
> min_kbar_width_px: 6
> rows: 250
> figsize: 16.6 x 5.75 inches
> pixel size: 1660 x 575
> size: 49960 bytes
> y-axis: automatic, no manual ylim or volume_ylim
> ```

> [visual check] The fixed-width chart keeps the same sliced data but gives the
> 250 K bars more horizontal room than the normal 800-pixel chart.

> [execution] Generated a full-series fixed-K-bar-width chart:
>
> ```text
> artifacts/charts/kline_t_series/dce_kqm_m_15m_all_fixed_kbar_width.png
> ```

> [verification] Full-series fixed-width artifact check:
>
> ```text
> output_mode: fixed_kbar_width
> min_kbar_width_px: 3
> rows: 10060
> figsize: 303.4 x 5.75 inches
> pixel size: 30339 x 575
> size: 347698 bytes
> y-axis: automatic, no manual ylim or volume_ylim
> ```

> [visual note] This is an intentionally extreme-wide PNG.
>
> It is useful as a stress test for chart width behavior, not as the default
> human inspection artifact.

### 8.d Test Result

> [execution] Focused test command:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.visualization.test_kline_t_series_chart
> ```

> [execution] Focused test output:
>
> ```text
> Ran 15 tests in 2.648s
> OK
> [run] KlineTSeriesChart tests: render PNG artifact, support window call, date axis format, output modes, and preserve source series
> ```

> [execution] Related source test command:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.domain.test_kline tests.domain.test_kline_t_series tests.data_io.test_csv_file_kline_t_series tests.visualization.test_kline_t_series_chart
> ```

> [execution] Related source test output after promotion:
>
> ```text
> Ran 42 tests in 2.750s
> OK
> ```

### 8.e Current Limitations

> [note] This is now promoted source.
>
> The old experiment file no longer carries the accepted implementation.

> [note] `show_window()` was verified through a patched backend in automated
> tests.
>
> A real local GUI window was not opened during automated verification.
