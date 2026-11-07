# memo0022_class_merged_kline_series_chart

[class design] [visualization] [chan] [chart] [merged kline]

## 0. Scope And Purpose

> [purpose] Design `MergedKlineSeriesChart`, the first chart object for
> `MergedKlineSeries`.

The first target operation is:

```text
MergedKlineSeries -> MergedKlineSeriesChart -> PNG artifact
```

> [decision] This memo mimics the `KlineTSeriesChart` pattern from
> `memo0017_class_kline_t_series_chart.md`.
>
> Keep the domain object clean. `MergedKlineSeries` owns Chan merge facts.
> `MergedKlineSeriesChart` owns how those facts are seen.

Must support:

```text
plot raw high/low stems from the row-aligned merged series
keep raw candle view available as an option
plot merged units only when requested
shade merged periods by direction
keep explicit merged high / merged low lines as an opt-in inspection layer
mark group-first and group-extreme rows
show a compact legend for merged overlays
show signed volume by default in the high/low overlay view
keep M midpoint percent change off by default
support fixed chart windows by raw index or timestamp
save a reproducible PNG artifact by default
optionally open a local chart window
support fit and fixed_kbar_width output modes
default to HD output
keep y-axis scaling automatic
```

Do not support yet:

```text
CSV read/write
Chan merge calculation
Fenxing / Bi / Xianduan drawing
interactive browser chart
solid/hollow custom candle renderer
source promotion
```

> [artifact rule] While the class is experiment-only, output generated charts
> under:
>
> ```text
> artifacts/experiments/chan_theory/
> ```

## 1. Design Ideas

### 1.a Same Shape As `KlineTSeriesChart`

> [source] `memo0017_class_kline_t_series_chart.md`

The proven chart path is:

```text
KlineTSeries -> KlineTSeriesChart -> PNG artifact / optional window
```

The merged chart path should stay parallel:

```text
MergedKlineSeries -> MergedKlineSeriesChart -> PNG artifact / optional window
```

> [decision] Use `mplfinance` for the raw candle base, then use matplotlib axes
> overlays for Project 009 merged-K evidence.

Reason:

```text
mplfinance already knows candlestick + volume layout
Project 009 owns merged_tag / merged_high / merged_low semantics
```

### 1.b What The Chart Must Show

> [concept] `MergedKlineSeries` is still row-aligned with the original
> `KlineTSeries`.

Each row keeps:

```text
raw OHLCV
raw_index
merged_tag
merged_low
merged_high
merged_direction
merge_state
is_group_first
is_group_extreme
```

The chart needs two human views:

```text
overlay_on_raw   keep raw candles and overlay merged interpretation
merged_only      compress to one displayed candle per merged tag
```

> [decision] `overlay_on_raw` is the main debugging view.
>
> It answers whether the merge logic respects the original K-line sequence.

> [decision] `merged_only` is the cleaned Chan-reading view.
>
> It answers what the market looks like after inclusion noise is removed.

### 1.c First Visual Encoding

> [decision] First chart modes:
>
> ```text
> chart_mode = "raw"
> chart_mode = "overlay_on_raw"
> chart_mode = "merged_only"
> ```

Visual meaning:

```text
raw                   original high/low stem or optional candle view
overlay_on_raw        raw high/low stems + M-period shading by default
merged_only           one display row per merged tag
M period shading      semi-transparent red/green/gray merged-value rectangle
M range lines         optional merged_high / merged_low boundaries
M midpoint change     explicit percent-change line on volume panel right axis
group-first marker    optional first raw row in a merged unit
group-extreme marker  optional row that supplies the merged extreme
unresolved group      visually muted or dashed evidence
legend                labels enabled overlay meanings
```

> [decision] Default raw display for `overlay_on_raw` is high/low only.
>
> Open and close remain in `MergedKlineSeries`, but they are visually
> irrelevant for the inclusion-merge step. Hiding candle bodies makes the
> merged high/low relationship easier to inspect.

> [decision] Default merged-period display is semi-transparent bounded shading.
>
> Red marks upward M periods, green marks downward M periods, and gray marks
> unresolved M periods when unresolved groups are shown. The shaded rectangle
> spans the M period on the x-axis and `merged_low` to `merged_high` on the
> y-axis.

> [decision] Explicit merged high/low boundary lines are off by default.
>
> The raw high/low stems already carry price extremes. Drawing merged
> boundaries on top is useful for audit, but it can visually duplicate highs
> and lows and make neighboring M periods look overlapped. Use
> `show_merged_range=True` only when exact M boundary evidence needs inspection.

> [decision] M midpoint percent change is not part of the default view.
>
> For each merged unit, midpoint means `(merged_high + merged_low) / 2`.
> Percent change compares the current M midpoint with the previous M midpoint.
> The first M unit has no previous M unit, so the plotted line starts from the
> second M unit. The `0%` line must align vertically with the signed-volume
> `0` line when `show_merged_mid_change=True`.

> [boundary] Draw style does not belong in `MergedKlineSeries`.
>
> Earlier discussion wanted peak bars solid and absorbed bars hollow. That is a
> rendering question, not a merged-series member. The first pass keeps
> first/extreme markers as explicit chart options, off by default.

### 1.d Output Modes

> [decision] Match `KlineTSeriesChart` output modes.

```text
output_mode = "fit"                overview chart
output_mode = "fixed_kbar_width"   image width grows from row count
```

> [decision] Default chart output is HD.
>
> ```text
> width_px = 1920
> height_px = 1080
> dpi = 150
> ```

> [decision] Fixed-K-bar-width changes figure width only.
>
> Price and volume y-axis limits remain automatic, because the chart should
> expose the plotted data rather than force a manual range.

### 1.e Layer And Location

> [layer] Experiment first:

```text
experiments/chan_theory/merged_kline_series_chart.py
```

> [layer] Later stable source location, only after promotion:

```text
src/tradinglab/visualization/merged_kline_series_chart.py
```

> [boundary] Do not put this chart under `data_io`.
>
> `CsvFileMergedKlineSeries` communicates with CSV. `MergedKlineSeriesChart`
> communicates visually.

## 2. Class Proposal

### 2.a `MergedKlineSeriesChart`

> [concept] `MergedKlineSeriesChart` is a visual object for one
> `MergedKlineSeries`.
>
> It answers:
>
> > How should this merged K-line derivation be inspected by eye?

First-round members:

```text
series: MergedKlineSeries
title: str
show_volume: bool
date_format: str = "%Y-%m-%d"
chart_mode: str = "overlay_on_raw"
raw_price_style: str = "high_low"
volume_mode: str = "signed"
output_mode: str = "fit"
min_kbar_width_px: int = 1
width_px: int = 1920
height_px: int = 1080
dpi: int = 150
open_window: bool = False
backend: str = "mplfinance"
window_start_raw_index: int | None = None
window_end_raw_index: int | None = None
window_start_timestamp: datetime | None = None
window_end_timestamp: datetime | None = None
show_merged_shading: bool = True
show_merged_range: bool = False
show_group_first: bool = False
show_group_extreme: bool = False
show_unresolved: bool = True
show_legend: bool = True
show_merged_mid_change: bool = False
merged_timestamp_anchor: str = "group_first"
```

Supported values:

```text
chart_mode: raw | overlay_on_raw | merged_only
raw_price_style: high_low | candle
volume_mode: signed | absolute
output_mode: fit | fixed_kbar_width
backend: mplfinance
merged_timestamp_anchor: group_first | group_extreme | group_end
```

`output_mode`:

```text
fit                keep the base HD width unless the caller changes width_px
fixed_kbar_width   grow width from chart unit count and min_kbar_width_px
```

`min_kbar_width_px`:

```text
default: 1
meaning: keep at least 1 output pixel for each raw K bar in raw/overlay charts
```

> [decision] Keep config as direct chart members in the first round, matching
> `KlineTSeriesChart`.
>
> Do not create `MergedKlineSeriesChartConfig` until the class has more than
> one real backend, style object, or artifact type.

### 2.b Public Methods

First public methods:

```python
render_to_file(path: Path) -> Path
show_window(block: bool = True) -> None
```

`render_to_file()`:

```text
validates .png path
creates the parent folder
builds the raw OHLCV chart frame
draws merged evidence overlay when requested
saves a non-empty PNG
optionally opens a local window
returns the output Path
```

`show_window()`:

```text
uses the same chart construction path
opens a local plotting window
does not become part of automated verification
```

`volume_mode`:

```text
signed     bullish volume above zero, bearish volume below zero
absolute   all volume bars above zero
```

> [decision] Signed volume is a plot transform only.
>
> `MergedKline.volume` remains the original nonnegative value.

`show_merged_mid_change`:

```text
False   default final view; keep signed volume without the percentage curve
True    explicit comparison view; add M midpoint percent change on lower panel
```

Calculation:

```text
M_midpoint = (merged_high + merged_low) / 2
M_midpoint_change_pct = (current_midpoint - previous_midpoint)
                        / previous_midpoint * 100
```

> [boundary] This is not a new Chan structure.
>
> It is a visual diagnostic derived from existing merged high/low evidence.
> The percent axis is scaled from the volume axis zero position, so `0%` and
> `0` volume share the same screen height.

`window_*`:

```text
window_start_raw_index      optional inclusive first raw row to display
window_end_raw_index        optional inclusive last raw row to display
window_start_timestamp      optional inclusive first timestamp to display
window_end_timestamp        optional inclusive last timestamp to display
```

> [decision] Windowing is a chart-view operation.
>
> For Chan work, derive `MergedKlineSeries` from the full available
> `KlineTSeries` first, then let `MergedKlineSeriesChart` choose the visible
> window. Re-merging a raw slice can change the first visible M groups because
> the prior direction context is gone.

Rules:

```text
raw-index window and timestamp window can be used separately
if both are set, the visible rows are their intersection
start and end are inclusive
fixed_kbar_width uses the visible row count, not the full-series row count
M-period spans are clipped to the visible window but keep full merged_low/high
an empty window is rejected
```

### 2.c Private Helpers

Expected private helpers:

```text
_to_mplfinance_dataframe()
_to_raw_dataframe()
_to_merged_only_dataframe()
_plot_with_mplfinance()
_plot_high_low_raw()
_merged_group_spans()
_draw_merged_period_shading()
_draw_merged_range_overlay()
_draw_group_markers()
_draw_legend()
_draw_merged_mid_change()
_merged_mid_change_points()
_merged_midpoint()
_span_anchor_index()
_visible_raw_indices()
_visible_klines()
_visible_merged_group_spans()
_scale_percent_axis()
_figsize_inches()
_fixed_kbar_figsize_inches()
_apply_index_date_axis()
_volume_value()
_show_figure()
_close_figure()
_prepare_plotting_environment()
```

> [decision] `_merged_group_spans()` should derive its view from existing
> `MergedKlineSeries` fields, not re-run Chan merge.

Group span shape:

```text
merged_tag
start_raw_index
end_raw_index
merged_low
merged_high
merged_direction
merge_state
group_first_index
group_extreme_index
```

## 3. Object Relationship

### 3.a First-Round Flow

```text
CsvFileKlineTSeries
  -> KlineTSeries
  -> MergedKlineSeries.derive_from(...)
  -> MergedKlineSeriesChart
  -> PNG artifact
```

> [decision] The chart consumes a finished `MergedKlineSeries`.
>
> It should not know how to read CSV or how to perform the inclusion merge.

### 3.b Relationship To Other Planned Objects

```text
CsvFileMergedKlineSeries       CSV <-> MergedKlineSeries
MergedKlineSeriesChart         MergedKlineSeries -> chart artifact
MergedKlineInferenceReport     MergedKlineSeries -> human audit tables
```

> [boundary] The chart may show visual evidence. It should not replace the
> human-table report.
>
> Charts answer shape and plausibility questions. Tables answer derivation and
> audit questions.

## 4. Sample Use

### 4.a Small Sample Chart

```python
from pathlib import Path

from experiments.chan_theory import KlineMergeConfig, MergedKlineSeries
from experiments.chan_theory.merged_kline_series_chart import (
    MergedKlineSeriesChart,
)
from tradinglab.data_io import CsvFileKlineTSeries

source = CsvFileKlineTSeries(
    Path("data_samples/kline/kline_15m_minimal.csv"),
    default_source="data_samples_kline",
).read()

merged = MergedKlineSeries.derive_from(source, KlineMergeConfig())

chart = MergedKlineSeriesChart(
    series=merged_full,
    title="Merged K-line minimal sample",
    chart_mode="overlay_on_raw",
    raw_price_style="high_low",
)

path = chart.render_to_file(
    Path("artifacts/experiments/chan_theory/merged_kline_chart_sample.png")
)
print(path)
```

### 4.b Merged-Only Chart

```python
chart = MergedKlineSeriesChart(
    series=merged_full,
    title="Merged K-line minimal merged-only",
    chart_mode="merged_only",
    merged_timestamp_anchor="group_first",
)

path = chart.render_to_file(
    Path("artifacts/experiments/chan_theory/merged_kline_chart_merged_only.png")
)
print(path)
```

### 4.c Fixed-K-Bar-Width Index Window

Assume `merged_full` is already derived from the full record.

```python
chart = MergedKlineSeriesChart(
    series=merged,
    title="Merged K-line index window",
    chart_mode="overlay_on_raw",
    window_start_raw_index=100,
    window_end_raw_index=350,
    output_mode="fixed_kbar_width",
    min_kbar_width_px=1,
)

path = chart.render_to_file(
    Path("artifacts/experiments/chan_theory/merged_kline_chart_index_window.png")
)
print(path)
```

### 4.d Fixed Window With Percentage Curve

```python
chart = MergedKlineSeriesChart(
    series=merged,
    title="Merged K-line with midpoint change",
    chart_mode="overlay_on_raw",
    window_start_raw_index=100,
    window_end_raw_index=350,
    show_merged_mid_change=True,
    output_mode="fixed_kbar_width",
    min_kbar_width_px=1,
)

path = chart.render_to_file(
    Path("artifacts/experiments/chan_theory/merged_kline_chart_mid_change.png")
)
print(path)
```

### 4.e Fixed Window From Full Merged Series

```python
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from experiments.chan_theory import MergedKlineSeries, MergedKlineSeriesChart
from tradinglab.data_io import CsvFileKlineTSeries

source = CsvFileKlineTSeries(
    Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv"),
    default_source="cc_record",
).read()
merged = MergedKlineSeries.derive_from(source)

beijing = ZoneInfo("Asia/Shanghai")
chart = MergedKlineSeriesChart(
    series=merged,
    title="Merged K-line window",
    window_start_timestamp=datetime(2025, 4, 7, 9, 0, tzinfo=beijing),
    window_end_timestamp=datetime(2025, 4, 21, 22, 0, tzinfo=beijing),
    output_mode="fixed_kbar_width",
)

path = chart.render_to_file(
    Path("artifacts/experiments/chan_theory/merged_kline_chart_window.png")
)
print(path)
```

## 5. Verification Plan

### 5.a Minimum Checks

First implementation should prove:

```text
valid MergedKlineSeries can render to a non-empty PNG
raw mode can render without merged overlays
overlay_on_raw mode can render with overlay artists
merged_only mode can render one row per merged tag
fixed_kbar_width expands width without manual y-axis limits
fixed_kbar_width default keeps at least 1 pixel per raw K bar
chart windows can select visible rows by raw index
chart windows can select visible rows by timestamp
chart windows clip visible M spans without re-running Chan merge
fixed_kbar_width uses visible row count when a chart window is active
invalid or empty chart windows are rejected
merged-period shading can be shown or hidden
merged-period shading uses merged_low / merged_high as y bounds
merged high/low boundary lines are explicit and off by default
signed and absolute volume modes both work
M midpoint percent-change points are calculated from merged high/low midpoint
M midpoint percent-change line can be explicitly plotted with the volume panel
M midpoint percent-change zero aligns vertically with zero volume
default overlay keeps the M midpoint percent-change line off
group-first and group-extreme marker options can be toggled
group-first and group-extreme markers are off by default
unresolved groups can be shown or hidden
overlay legends can be shown or hidden
show_volume True and False both work
unsupported chart_mode is rejected
unsupported output_mode is rejected
unsupported backend is rejected
non-.png output path is rejected
chart generation does not mutate MergedKlineSeries
show_window is available but not required by tests
```

### 5.b Human Visual Checks

Visual inspection should confirm:

```text
time axis remains original raw K-line order
raw candles still show original OHLCV
M-period shading aligns with each merged_tag group's merged_low / merged_high
optional merged high / low lines align with each merged_tag group
group-first markers sit at the first row of each merged unit
group-extreme markers sit at the row that supplies the visible extreme
direction_unresolved groups are distinguishable from resolved groups
artifact path is recorded in the execution log
```

## 6. Open Questions

> [open] Should the first implementation plot the full 10,060-row CC record, or
> should it default to slices for human readability?

> [open] Should custom solid/hollow candle styling become a later
> `MergedKlineCandleRenderer` instead of overloading this first chart class?

> [open] Should a future report class output the operation-flow table beside
> the chart, or should chart and report remain separate artifacts?

## 7. Current Decision

> [decision] Create one experiment-first visualization class:
>
> ```text
> MergedKlineSeriesChart
> ```

> [decision] Match `KlineTSeriesChart` where possible:
>
> ```text
> PNG-first
> optional window
> mplfinance backend
> raw / overlay_on_raw / merged_only chart modes
> fit / fixed_kbar_width output modes
> automatic y-axis scaling
> no CSV or Chan calculation inside the chart
> ```

> [result] Implemented as experiment-only code on 2026-09-04.

## 8. Implementation And Test Results

### 8.a Experiment Implementation

> [execution] Implemented files:
>
> ```text
> experiments/chan_theory/merged_kline_series_chart.py
> experiments/chan_theory/test_merged_kline_series_chart.py
> ```

Implemented class:

```text
MergedKlineSeriesChart
```

Implemented chart modes:

```text
raw             raw OHLCV candles from MergedKlineSeries rows
overlay_on_raw  raw high/low stems plus shaded M periods by default
merged_only     one plotted row per merged_tag
```

Implemented options:

```text
show_volume
date_format
raw_price_style
volume_mode
output_mode
min_kbar_width_px
width_px
height_px
dpi
open_window
show_merged_shading
show_merged_range
show_group_first
show_group_extreme
show_unresolved
show_legend
show_merged_mid_change
merged_timestamp_anchor
```

> [boundary] The chart consumes a finished `MergedKlineSeries`.
>
> It does not read CSV and does not run Chan merge.

### 8.b Generated Artifacts

> [execution] Generated chart artifacts under the experiment artifact folder:

```text
artifacts/experiments/chan_theory/merged_kline_chart_overlay_sample.png
artifacts/experiments/chan_theory/merged_kline_chart_overlay_mid_change_sample.png
artifacts/experiments/chan_theory/merged_kline_chart_merged_only_sample.png
artifacts/experiments/chan_theory/merged_kline_chart_overlay_20250407_20250421_fixed.png
artifacts/experiments/chan_theory/merged_kline_chart_overlay_mid_change_20250407_20250421_fixed.png
artifacts/experiments/chan_theory/merged_kline_chart_merged_only_20250407_20250421_fixed.png
artifacts/experiments/chan_theory/merged_kline_chart_overlay_full_fixed_1px.png
artifacts/experiments/chan_theory/merged_kline_chart_overlay_mid_change_full_fixed_1px.png
```

Artifact sizes:

```text
overlay sample: 50564 bytes, 1920 x 1080
overlay midpoint-change sample: 65054 bytes, 1920 x 1080
merged-only sample: 63185 bytes, 1920 x 1080
overlay fixed window: 74272 bytes, 1920 x 1080
overlay midpoint-change fixed window: 125815 bytes, 1920 x 1080
merged-only fixed window: 74519 bytes, 1920 x 1080
overlay full fixed 1px: 239136 bytes, 10219 x 1080
overlay midpoint-change full fixed 1px: 305941 bytes, 10219 x 1080
```

Window data:

```text
window: 2025-04-07 09:00 to 2025-04-21 22:00 Asia/Shanghai
raw rows: 250
visible M spans: 169
M midpoint-change points: 168
full fixed raw rows: 10060
full fixed merged rows: 6200
```

### 8.c Verification

> [verification] Test commands:

```zsh
python3 -m py_compile experiments/chan_theory/merged_kline_series_chart.py experiments/chan_theory/test_merged_kline_series_chart.py experiments/chan_theory/__init__.py
PYTHONPATH=src:. .venv/bin/python -m unittest experiments.chan_theory.test_merged_kline_series_chart
PYTHONPATH=src:. .venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
PYTHONPATH=src:. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Results:

```text
MergedKlineSeriesChart tests: 33 passing
all experiment tests: 64 passing
source baseline tests: 42 passing
line-length scan: clean
```

> [visual check] The HD fixed-width overlay slice now uses raw high/low stems,
> not candle bodies. First/extreme markers are hidden by default. M periods are
> shaded by direction inside each M unit's `merged_low` / `merged_high` bounds,
> making merged-group continuity easier to inspect. Explicit merged high/low
> boundary lines default to off because they can visually duplicate raw highs
> and lows; use `show_merged_range=True` for audit views. The volume panel uses
> signed volume by default: bullish rows above zero and bearish rows below zero.
> `show_merged_mid_change=False` is the default final view. It keeps the chart
> clean: price evidence plus signed volume only. Use
> `show_merged_mid_change=True` for the explicit comparison view with the
> right-axis M midpoint percent-change line. The `0%` and `0` volume lines sit
> at the same vertical height when that curve is enabled.
> `output_mode="fixed_kbar_width"` with the default `min_kbar_width_px=1`
> returns to the natural dense view. Raw bars use row-index x positions
> `0, 1, 2...`; matplotlib handles the normal visual spacing and line width.
> The full 10,060-row record renders as `10219 x 1080`.
