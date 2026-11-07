# memo0025_class_fenxing_series_chart

[class design] [visualization] [chan] [chart] [fenxing]

## 0. Scope And Purpose

> [purpose] Design `FenxingSeriesChart`, following memo0022's chart object
> and adding top/bottom markers to the completed Fenxing result.

```text
FenxingSeries -> FenxingSeriesChart -> PNG / optional local window
```

Must support:

- Original raw high/low view, merged shading overlay, and merged-only view.
- One top/bottom marker per marked M group, at its correct price and position.
- HD output, automatic y scaling, fit/fixed-width sizing, and date-focused axes.
- Inclusive raw-index or timestamp windows without recalculating structures.
- Optional volume, compact legends, and the existing merge-inspection toggles.

> [boundary] The chart displays saved facts. It does not read CSV, merge bars,
> detect Fenxing, select Bi, draw a trading signal, or change calculation config.
> No connecting zigzag line in this first version: adjacent centers are not
> automatically valid Bi endpoints.

Generated output stays under `artifacts/experiments/chan_theory/`.

## 1. Design Ideas

### 1.a Same Chart Pattern

```text
MergedKlineSeries -> MergedKlineSeriesChart
FenxingSeries     -> FenxingSeriesChart
```

Reuse the existing matplotlib/mplfinance base through an internal
`MergedKlineSeriesChart` collaborator fed with `series.source_series`.
`FenxingSeriesChart` owns Fenxing marker selection, placement, and legend entries.
Do not copy the entire merged renderer or make the Fenxing chart pretend to
be a `MergedKlineSeries`.

> [implementation note] The existing renderer exposes a figure through its
> private `_build_figure()`, not a stable overlay API. During implementation,
> keep any necessary axes/coordinate-sharing change small and regression-tested.
> One new public chart class; no generic chart framework or new backend.

### 1.b What A Marker Means

`FenxingSeries.klines` retains every original row. A label repeats across
the owning M group; the chart must deduplicate by group before drawing.

```text
Raw row           K0      K1      K2       K3      K4
Original range   [5,10]  [8,12]  [9,14]  [10,13]  [7,11]
M group           M0      M1      M2       M2      M3
fx_type           None    None    top      top     None
```

Draw one top for M2, not two. Its price is 14, contributed by K2.
The theoretical three-group neighborhood is M1/M2/M3; no extra stored
Fenxing structure is required for plotting it.

**Figures 1–3: one shared numerical example**

> [example] These three figures use section 1.d's later-high example, extended
> by K4 to show a bottom. This is independent of the M2/14 example above.
> An M group is one merged price interval that retains its original raw rows.

```text
Raw row          K0      K1      K2      K3      K4
Original range  [1,5]   [3,8]   [2,10]  [1,6]   [3,8]
M group          M0      M1      M1      M2      M3
Merged range    [1,5]   [3,10]  [3,10]  [1,6]   [3,8]
fx_type          None    top     top     bottom  None
```

K0 to K1 establishes the upward merge direction: both high and low rise.
K2 contains K1's price interval, so their upward merge uses
`low=max(3,2)=3`, `high=max(8,10)=10`. M1 therefore spans K1–K2 with
`[3,10]`; the two original intervals remain unchanged.

A top center has **both its high and its low strictly above those of each
neighbor**; a bottom center has both strictly below. All four comparisons
must pass. Figure 1 shows the two overlapping three-group windows of this
same sequence, using the strict rules in [memo0023 §0.a](memo0023_class_fenxing_series.md#0a-top-operation-rule).

![Figure 1: M1 top and M2 bottom, with all four high/low comparisons](../../artifacts/experiments/chan_theory/memo0025_01_top_bottom.png)

> [reading] The horizontal axis here is the ordered **M groups**, not raw
> rows. The pale vertical band identifies the middle group under comparison.
> M0 and M3 have no complete three-group window and receive no center label.
> Equality fails the corresponding strict comparison; an unresolved merge
> direction skips the affected window under the current profile.
> Adjacent top/bottom labels do not establish a Bi.

> [illustration] Figures 1–3 are numeric schematics, with enlarged triangles
> and simplified range stems. They preserve exact marker coordinates, but
> do not demonstrate the renderer's pixel-size rule or synthetic candle bodies.
> Gray bounded bands in figures 2–3 show merged price intervals; their neutral
> color is not the production renderer's direction-color encoding.

### 1.c Visual Encoding

```text
top / 顶分型        filled red upward triangle at merged_high
bottom / 底分型     filled green downward triangle at merged_low
unmarked group     no Fenxing marker
M-period shading   existing bounded red/green/gray shading
legend             Top Fenxing / Bottom Fenxing, once per visible type
optional text      M tag and type, such as "M2 top"
```

Use red (`#D62728`, upward pixel triangle) for top Fenxing and green
(`#2CA02C`, downward pixel triangle) for bottom Fenxing, with solid fill and no outline.
Triangle width follows **80% of the plotted raw/M bar slot**, but its base
must be **at least 5 pixels**. At minimum size it has three centered rows:
1/3/5 pixels for a top, 5/3/1 for a bottom. Size after layout and fixed-width
adjustment, using the export DPI. No outline or smoothing that blurs these
pixel rows. Keep legend symbols readable independently.
Legend symbols must match these same colors and directions.
Shape also distinguishes top from bottom; do not rely on color alone.
Triangle coordinates use the exact price. Optional text uses a display-space
offset, not an invented price above/below the real extreme.

Keep merged high/low lines, group-first/group-extreme markers, text labels,
and midpoint percentage change off by default. Fenxing markers are on.
The default view remains raw high/low stems, bounded M shading, signed volume,
and compact legends. No candle bodies unless explicitly requested.

### 1.d Position And Time

Two Fenxing display anchors:

```text
fenxing_anchor = "price_extreme"   default; original row contributing the bound
fenxing_anchor = "group_first"     inspection option; first raw row of the group
```

`price_extreme` follows memo0023's first/last tie rule from the upstream merge
config. Read the anchor from `series.evidence_table()` once for the complete
chart; do not call an O(N) lookup for each of thousands of centers.

`group_first` changes display position only. It must not claim that the first
raw row contributed the price. Keep the marker y value at the group's actual
Fenxing price for either anchor.

> [decision] Choose the horizontal location independently of the marker price.
> Both options refer to the center M group, not the left neighbor in the
> three-group Fenxing window.

| Anchor | Horizontal position | Top marker price | Bottom marker price |
| --- | --- | --- | --- |
| `group_first` | First original K bar of the center M group | `merged_high` | `merged_low` |
| `price_extreme` | Original K bar contributing the relevant merged bound | `merged_high` | `merged_low` |

Example with a later high contributor; intervals are `[low, high]`:

```text
Raw row          K0      K1      K2      K3
Original range  [1,5]   [3,8]   [2,10]  [1,6]
M group          M0      M1      M1      M2
Merged range    [1,5]   [3,10]  [3,10]  [1,6]
fx_type          None    top     top     None
```

M1 is the top center. `group_first` places its red upward triangle at
`(K1, 10)`; `price_extreme` places it at `(K2, 10)`. K1's original high is
8, but the group-first marker still uses the merged high of 10.
For a bottom, use the same choice of horizontal anchor with `merged_low`
and a green downward triangle. Neither option changes stored data.

> [distinction] `is_group_extreme` describes the merge-direction extreme.
> Fenxing placement must use the relevant top high or bottom low contributor;
> do not substitute that flag without checking its meaning.

![Figure 2: raw bars, merged bounds, one top per group and the two horizontal anchors](../../artifacts/experiments/chan_theory/memo0025_02_anchors.png)

> [reading] Figure 2 continues figure 1's five raw rows. K1 and K2 both carry
> M1's `top` label, but each panel draws only one red top. The default panel
> uses K2, which supplies high 10; the second uses M1's first raw row K1.
> Its original high remains 8, while the marker stays at merged high 10.
> M2 has only K3, so its green bottom remains `(K3,1)` in both panels.
> These x positions locate prices retrospectively: with only K0–K2 there is
> no top yet. K3 supplies the right neighbor for M1; K4 supplies the right
> neighbor for M2. This fixed example does not promise live-time finality.

### 1.e Output Modes And Windows

Keep `fit` and `fixed_kbar_width`, HD `1920 x 1080`, `150` dpi, and default
`min_kbar_width_px=1`. A caller can request 3 pixels per displayed unit.
This controls horizontal spacing, not the painted stem thickness. Triangle
width follows that spacing, capped by `fenxing_marker_size`.
Verify spacing in the actual price axes, not only the outer PNG dimensions.

Derive/load the complete series before selecting a chart window:

- Raw-index and timestamp bounds are inclusive; when combined, use intersection.
- Reject reversed, incompatible-timezone, or empty windows.
- Clip M shading horizontally; preserve full merged bounds and original labels.
- Raw/overlay view: draw a center only if its selected raw anchor is visible.
  Never clamp an off-screen anchor to the first visible member of its group.
- Merged-only view: draw one marker on each visible center-group slot, even
  when only part of that group intersects the raw window. This is a group
  projection, not a claim that the raw turning timestamp is visible.
- Fixed width uses visible raw-row count, or visible M-group count in
  merged-only mode, not the full input count or center count.

The first visible bar may already be a center whose left/right evidence lies
outside the window. Keep the full-history classification; do not redetect on
the visible slice. These are retrospective results, not live-time availability.

![Figure 3: a K1-only window hides the price-extreme anchor but retains the merged group](../../artifacts/experiments/chan_theory/memo0025_03_window.png)

> [reading] Figure 3 uses the same complete five-row result and sets both raw
> window bounds to 1. In the raw/overlay view, `price_extreme` omits the top
> because K2 is outside the window. `group_first` shows `(K1,10)` because K1
> is visible. The merged-only view represents the intersecting M1 as local
> slot 0, preserves its full `[3,10]` bounds and shows the top at 10.
> Only display coordinates and visibility change; M1's classification and
> original K1/K2 rows remain intact. The right panel uses a range stem to
> explain the group projection, rather than reproducing its candle body.

### 1.f Layer And Sources

```text
experiment: experiments/chan_theory/fenxing_series_chart.py
tests:      experiments/chan_theory/test_fenxing_series_chart.py
future:     src/tradinglab/visualization/fenxing_series_chart.py
```

- [memo0022](memo0022_class_merged_kline_series_chart.md): base chart pattern,
  display options, windows, and artifact convention.
- [memo0023](memo0023_class_fenxing_series.md): raw-preserving center labels,
  deduplicated group count, and exact price anchors.
- [memo0024](memo0024_class_csv_file_fenxing_series.md): basic CSV reload as
  a chart input, separate from rendering.
- `experiments/chan_theory/merged_kline_series_chart.py`: actual backend,
  axis-coordinate, window, and volume behavior; inspect before reusing it.

## 2. Class Design

### 2.a `FenxingSeriesChart`

Frozen chart object. Use direct chart members, as in memo0022; no separate
`FenxingSeriesChartConfig`. Calculation configs remain on the input series.

```text
series: FenxingSeries
title: str = ""
show_volume: bool = True
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
show_top: bool = True
show_bottom: bool = True
fenxing_anchor: str = "price_extreme"
show_fenxing_labels: bool = False
fenxing_marker_size: float = 36.0
```

New members govern only the Fenxing layer. `fenxing_marker_size` is the maximum
scatter area in points squared, subject to the 5-pixel minimum base. Actual
size follows 80% of the visible bar slot between that minimum and the area cap.
The minimum takes precedence if the cap itself would be smaller than 5 pixels.
Require a finite positive value.
Use typed `Literal` aliases for finite option sets when implementing.

### 2.b Modes And Option Boundaries

```text
chart_mode: raw | overlay_on_raw | merged_only
raw_price_style: high_low | candle
volume_mode: signed | absolute
output_mode: fit | fixed_kbar_width
merged_timestamp_anchor: group_first | group_extreme | group_end
fenxing_anchor: price_extreme | group_first
```

Here `chart_mode` chooses the base view. Fenxing markers are independent:

- `raw`: raw bars plus selected Fenxing markers; no M shading/range layer.
- `overlay_on_raw`: raw bars, enabled merged evidence, and Fenxing markers.
- `merged_only`: one slot per M group, with its selected Fenxing marker.
- Set `show_top=False, show_bottom=False` for a marker-free comparison.

`merged_timestamp_anchor` labels the merged-only base/group diagnostics;
it does not override `fenxing_anchor`. In merged-only mode the marker x
position is the M slot; the raw-anchor option has no effect on that slot.

> [existing backend limit] Signed volume and the percentage curve are currently
> implemented only in the high/low raw/overlay path. For candle or merged-only
> views with volume, the first proposal requires `volume_mode="absolute"` and
> `show_merged_mid_change=False`. Reject unsupported combinations explicitly;
> do not silently claim they were rendered. With `show_volume=False`, percentage
> change must also be off. Extending these combinations is separate work.

When percentage change is enabled on the supported base, retain memo0022's
M-midpoint meaning and align 0% with zero volume. It is not a Fenxing-to-Fenxing
return curve. Merge group markers and shading options retain their base-mode
meaning; Fenxing top/bottom toggles do not filter the underlying data.

### 2.c Public Methods

```python
render_to_file(path: Path) -> Path
show_window(block: bool = True) -> None
```

`render_to_file()` validates the input/options and PNG path, creates the parent
folder, builds the base view, adds markers/legend, saves, closes the figure,
and returns the path. Optional window display follows file generation.

`show_window()` uses the same figure-building path. Automated tests never
require a GUI; test the display call with a mock.

### 2.d Internal Collaboration

```text
FenxingSeriesChart
  source_series -> existing merged chart base
  evidence_table() -> unique centers and raw anchors
  visible coordinate map -> marker x positions
  markers + text + merged legend -> final figure
```

The existing base uses different x coordinates:

```text
high/low raw base     original raw indices
mplfinance raw base  local visible row positions: 0, 1, 2, ...
merged-only base     local visible M-group positions: 0, 1, 2, ...
```

Use an explicit mapping for the chosen base. Never feed global raw indices
directly into a cropped mplfinance axis. The same mapping must govern any
enabled merged overlays; regression-test this when exposing shared axes.

Suggested private responsibilities:

```text
_base_chart()                 configure the existing merged chart collaborator
_visible_coordinate_map()     map raw rows or M groups to the actual base x axis
_fenxing_points()             select one marker per visible marked group
_draw_fenxing_markers()        batch top/bottom artists and optional text
_draw_legend()                combine enabled meanings without duplicate labels
_build_figure()               assemble one final figure for file/window output
```

Point values are temporary drawing data: M tag, type, raw anchor, x position,
and price. Do not attach pixels, colors, marker symbols, or display timestamps
to `Fenxing` rows. Automatic limits must include visible markers and enough
padding to avoid clipping their glyphs, especially in a partial-group window.

## 3. Object Relationship

### 3.a First-Round Flow

```text
raw CSV -> KlineTSeries -> MergedKlineSeries -> FenxingSeries -> chart
basic Fenxing CSV -> CsvFileFenxingSeries.read() -> FenxingSeries -> chart
```

The caller chooses how to obtain the series. Chart code knows neither CSV
paths nor how the labels were calculated.

### 3.b Neighboring Objects

```text
CsvFileFenxingSeries      persistence and human-table export
FenxingSeries            center facts, source/config, and evidence
FenxingSeriesChart       visual presentation
future report            full comparison tables and narrative
```

No chart method belongs on the domain series. No CSV method belongs on the chart.

## 4. Sample Use

> [status] Implemented and verified on 2026-09-10. Run examples from the repo
> root with `PYTHONPATH=src`; automated rendering uses `MPLBACKEND=Agg`.

### 4.a Reload And Plot

```python
from pathlib import Path
from experiments.chan_theory import CsvFileFenxingSeries
from experiments.chan_theory.fenxing_series_chart import FenxingSeriesChart

folder = Path("artifacts/experiments/chan_theory")
fenxings = CsvFileFenxingSeries(folder / "fenxing_series_basic_cc.csv").read()
chart = FenxingSeriesChart(
    series=fenxings,
    window_start_raw_index=100,
    window_end_raw_index=350,
)
chart.render_to_file(folder / "fenxing_chart_overlay_index_window.png")
```

### 4.b Merged-Only View

```python
chart = FenxingSeriesChart(
    series=fenxings,
    chart_mode="merged_only",
    volume_mode="absolute",
    window_start_raw_index=100,
    window_end_raw_index=350,
)
chart.render_to_file(folder / "fenxing_chart_merged_only_index_window.png")
```

### 4.c Full Series, Fixed Width

```python
chart = FenxingSeriesChart(
    series=fenxings,
    output_mode="fixed_kbar_width",
    min_kbar_width_px=3,
)
chart.render_to_file(folder / "fenxing_chart_full_fixed_3px.png")
```

All centers remain present even when a wide chart is dense. Do not silently
drop markers to improve appearance; use a narrower window for close inspection.

### 4.d Timestamp Window And Optional Curve

```python
from datetime import datetime
from zoneinfo import ZoneInfo

zone = ZoneInfo("Asia/Shanghai")
chart = FenxingSeriesChart(
    series=fenxings,
    window_start_timestamp=datetime(2025, 4, 7, 9, 0, tzinfo=zone),
    window_end_timestamp=datetime(2025, 4, 21, 22, 0, tzinfo=zone),
    output_mode="fixed_kbar_width",
    show_merged_mid_change=True,
)
chart.render_to_file(folder / "fenxing_chart_window_mid_change.png")
```

Default is still no percentage curve. For local inspection, call
`chart.show_window()` explicitly or construct with `open_window=True`.

## 5. Verification Plan

### 5.a Marker Facts

- Memo0023's 11-row example produces exactly M2 top and M5 bottom.
- Its multirow M2 example produces one marker at K2/14, not one per raw row.
- Verify top/bottom prices, non-first contributors, and both extreme-tie policies.
- For the section 1.d example, verify `group_first` gives `(K1, 10)` and
  `price_extreme` gives `(K2, 10)`; changing anchor never changes marker price.
- Verify top markers and legend entries are red upward triangles; bottom
  markers and legend entries are green downward triangles.
- Top-only, bottom-only, no markers, optional labels, and legends work independently.
- No-turn and unresolved input still render a valid base without fabricated centers.

### 5.b Coordinates And Windows

- Compare actual artist coordinates with expected raw/M slots in every base mode.
- Include a nonzero-start window to catch global-versus-local index mistakes.
- Clip a center group before/after its raw extreme; raw view never relocates it.
- Keep full-history labels when either neighbor falls outside the chart window.
- In merged-only mode, retained partial groups get one group-slot marker.
- Verify raw-index/timestamp intersection, invalid bounds, and empty selection.
- Fixed-width spacing uses visible base units, with automatic y limits that
  include the markers; test the actual rendered axes geometry.

### 5.c Output And Regressions

- Nonempty PNG, HD dimensions, valid backend/options, and non-PNG rejection.
- M shading/range/first/extreme toggles retain their documented meaning.
- Volume options respect the supported mode combinations; default curve stays off.
- On the supported curve view, 0% and zero volume align at the same screen height.
- Figure resources close after save; optional window calls are mock-tested.
- Plotting never mutates rows/configs or invokes merge/Fenxing derivation.
- Rerun the existing merged chart, all experiment tests, and source tests.

### 5.d Full IO-To-Chart Check

```text
raw CC CSV -> merge -> Fenxing -> basic CSV write -> read -> chart PNG
```

Test this chain explicitly, not merely the CSV and chart suites separately.
Compare marker identities/prices from fresh and reloaded input. Full-data
counts remain 10,060 raw rows, 6,200 M groups, and 3,027 centers; windowed
marker counts depend on visibility and toggles.

Inspect a small known-turn chart, the April date window, merged-only view,
and full fixed-width output. A nonempty PNG alone does not prove alignment:
check marker locations, clipping, legend readability, and nonblank price data.

## 6. Open Questions

- Full-record markers may look dense even at fixed width. Decide any later
  interactive inspection separately; do not turn downsampling into a hidden rule.
- Full three-group highlights or comparison reports can follow after the
  center-marker view is verified. They are not first-version requirements.

## 7. Current Decision

One experiment-first `FenxingSeriesChart`, parallel to memo0022, using the
existing merged chart base and an explicit Fenxing overlay. Keep direct
chart options, default high/low view, PNG-first output, optional window,
and clean separation from CSV and calculation.

## 8. Implementation And Test Results

> [status] Implemented on 2026-09-10 under approved steps 7.4.52-7.4.58.
> Experiment only. Milestone 7.4 remains active; no source promotion or Bi work.

### 8.a What Changed

- Added `experiments/chan_theory/fenxing_series_chart.py` and its package export.
  Public calls are `render_to_file(path)` and `show_window(block=True)`.
- `_base_chart()` passes the shared display members to `MergedKlineSeriesChart`.
  `_fenxing_points()` reads one evidence table, chooses unique visible centers,
  and maps their anchors to global raw or local candle/M coordinates.
- `_draw_fenxing_markers()` draws each type as one scatter collection. Text is
  optional; triangle prices stay exact. `_build_figure()` combines the layers,
  legends, and padded price limits without changing the time interval.
- `_fit_bar_spacing()` measures the actual price-axis spacing at export DPI
  and grows figure width when necessary. Three pixels means minimum slot
  spacing, not a three-pixel painted stem. Triangle width now follows the
  final bar spacing while respecting the configured maximum area.
- Small shared-renderer fixes: cropped candle overlays now use local slots;
  legend handles are reusable; `show_legend=False` also hides the percentage
  legend; zero axes align even without percentage points; failed overlays close
  their figure. No merge/Fenxing rule or earlier memo changed.

### 8.b What The Tests Establish

`experiments/chan_theory/test_fenxing_series_chart.py`: **40 passing tests**.

- **Marker facts:** the 11-row example yields M2 top/K5/14 and M5 bottom/K9/6.
  Multirow centers draw once. Actual scatter paths, colors, and coordinates
  verify red upward tops and green downward bottoms.
- **Anchors:** the section 1.d top moves from K2 to K1 when choosing group-first,
  but stays at price 10. Both top/bottom ties obey the upstream first/last rule.
- **Windows:** nonzero-start raw, candle, and merged-only views use their correct
  axes. A partial raw group cannot pull an off-screen extreme into view;
  merged-only still represents that group. Bounds intersect inclusively, and
  off-screen neighbors do not erase the full-history classification.
- **Display:** test each marker toggle, labels, legends, signed/absolute volume,
  no-turn/unresolved input, invalid options, and unsupported combinations.
  Zero volume and 0% coincide, including the no-percentage-point case.
- **Output:** verify HD pixels, nonblank images, actual fixed-width axes spacing,
  visible-unit sizing, PNG suffixes, nested folders, frozen input, and cleanup
  after save/overlay failures. GUI calls are mocked; nonblocking display leaves
  its figure open for the caller to close.
- **Integration:** raw CC CSV -> merge -> Fenxing -> basic CSV write/read -> PNG.
  Compare fresh/reloaded marker identities and prices, not just counts. Rendering
  is tested with derivation and per-center raw scans disabled.

Verification commands:

```zsh
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_fenxing_series_chart
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_merged_kline_series_chart
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s experiments -p 'test_*.py'
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

[evidence] All **173 experiment tests** and **42 source tests** passed.
The 33 existing merged-chart tests remain passing. Python 3.11.16,
matplotlib 3.11.1, mplfinance 0.12.10b0, pandas 2.3.3; no dependency changes.

### 8.c Saved Images

Folder: `artifacts/experiments/chan_theory/`. All seven PNGs are 1,080 pixels
high; the six window/example images are 1,920 pixels wide.

| PNG filename | Visible raw rows | Markers | Bytes |
| --- | ---: | ---: | ---: |
| `fenxing_chart_small_price_extreme.png` | 5 | 2 | 59,358 |
| `fenxing_chart_small_group_first.png` | 5 | 2 | 58,825 |
| `fenxing_chart_overlay_index_window.png` | 251 | 83 | 75,336 |
| `fenxing_chart_merged_only_index_window.png` | 251 | 84 | 78,509 |
| `fenxing_chart_window_default.png` | 250 | 87 | 79,324 |
| `fenxing_chart_window_mid_change.png` | 250 | 87 | 129,489 |
| `fenxing_chart_full_fixed_3px.png` | 10,060 | 3,027 | 426,388 |

The index window is K100-K350. Its merged-only count is one higher because
that view retains a partial center group whose raw price anchor is off-screen.
The date window is **2025-04-07 09:00 through 2025-04-21 22:00 Asia/Shanghai**.
Default has no percentage curve; the paired image adds the M-midpoint curve.

The full chart is **33,431 x 1,080 pixels**, with measured axes spacing
**3.0074 pixels per raw slot**. The input retains **6,200 M groups**;
all **3,027 centers** are plotted without downsampling. Rendering took about
5 seconds locally; small/window files took about 0.06-0.3 seconds each in the
initial full regression run. These are observations, not performance guarantees.
`fenxing_chart_verification.json` records the latest sizes, timings, marker
counts, and measured axis spacing whenever the artifact test is rerun.

Regenerate the seven images from the checked-in CC record and numeric fixture:

```zsh
PYTHONPATH=src MPLBACKEND=Agg .venv/bin/python -m unittest experiments.chan_theory.test_fenxing_series_chart.FenxingSeriesChartTest.test_reference_png_examples
```

### 8.d Inspection And Limits

[verification] Inspected both small anchors, the April charts with/without the
curve, the merged-only window, and a native-resolution crop of the full PNG.
Markers meet the merged bounds, the small anchor comparison is explicit,
legends match the symbols, and the default price panel has no candle bodies.

The full PNG is intentionally very wide. At whole-image fit, markers cannot
remain individually legible; inspect at native size or select a window.
No centers are removed to make the image look cleaner. Merged-only retains
the existing synthetic candle display, not a claim of newly traded OHLC bars.
GUI window behavior was mock-tested, not manually verified on a desktop backend.
Signed volume/percentage limits in section 2.b still apply.

[source] Execution record:
`docs/phases/phase-01-warmup/7.4-execution-summary-2026-09-10-fenxing-chart.md`.

### 8.e Triangle Size Correction

[history] First correction; its no-minimum rule is superseded by section 8.f.

[decision] The first full chart used a fixed 36-point-squared marker, about
12.5 pixels wide at 150 DPI, against 3-pixel bar spacing. That covered several
neighboring bars. The screenshot review prompted this correction on 2026-09-10.

`_scale_fenxing_markers()` now runs after layout and width adjustment:

```text
slot_px = price_axis_width_px / visible_x_span
width_pt = 0.8 * slot_px * 72 / dpi
scatter_area = min(fenxing_marker_size, width_pt ** 2)
```

No minimum marker size that could exceed a dense slot. No outline that adds
width outside the triangle. The existing size member is a maximum, not a fixed
request; no new configuration object. Legend symbols stay independently readable.

[verification] Full-chart triangles are now **2.406 pixels wide** against
**3.007-pixel slots**, not 12.5 pixels. All 3,027 markers remain at the same
prices and anchors. Regenerated all seven PNGs under the same filenames.
The JSON report now records `marker_width_px` alongside slot spacing.

Four added tests cover raw/candle/merged-only modes, fit/fixed outputs, 75/150/300
DPI, sparse-chart size caps, unchanged legend size, and window-dependent scaling.
Inspected enlarged full-chart detail: the triangles no longer cover neighboring
bars. At only 2-3 pixels, triangle shape is necessarily coarse; use a wider bar
spacing or a shorter window to inspect the symbol itself.

### 8.f Minimum Five-Pixel Base

[decision] The user requested a minimum readable triangle base on 2026-09-10.
Use a crisp three-row silhouette, interpreted as centered odd-width rows:

```text
Top (red)       Bottom (green)
  #             #####
 ###             ###
#####             #
```

At minimum size, the base is 5 pixels and height is 3 pixels. The geometry
scales up for wider bars. `_triangle_marker()` supplies the stepped outline;
filled paths are pixel-snapped without antialiasing or an outline stroke.
Stored marker prices and raw/M anchors are unchanged.

```text
preferred_width_px = min(0.8 * slot_px, sqrt(fenxing_marker_size) * dpi / 72)
actual_width_px = max(5, preferred_width_px)
scatter_area = (actual_width_px * 72 / dpi) ** 2
```

The minimum wins over the previous 80% cap: a 3-pixel bar slot now has a
**5-pixel-base, 3-pixel-high triangle**. At dense spacing this can extend into
a neighboring slot; that is the explicit readability tradeoff. It is still
much smaller than the original 12.5-pixel marker.

[verification] Added a raster-buffer test at 75/150/300 DPI and fractional
x positions: exactly 1/3/5 colored pixels per top row and 5/3/1 per bottom row.
Updated sizing tests and regenerated all seven PNGs. Full chart still contains
all 3,027 centers with unchanged bar spacing and time/price coordinates.

### 8.g Demonstration Figures And Verification

[evidence] Figures 1–3 were added under documentation slice 7.4.90. The
reproduction test constructs raw Klines, runs the existing merge and Fenxing
entry points, and checks all four merged intervals, raw memberships, labels,
and both centers' four strict comparisons. It also compares expected marker
positions with the actual chart artists in five full/windowed configurations.
Six prefix/boundary cases cover evidence arrival, monotonic input, single-row
input, and empty-input rejection. The independent section 1.b M2/14 example
is checked separately. These bounded checks verify the illustrated behavior;
they are not exhaustive proof of all Fenxing inputs or live-time behavior.

Reproduce all three PNGs and their SVG companions from the repository root:

```zsh
PYTHONPATH=src MPLBACKEND=Agg MPLCONFIGDIR=/tmp/proj009-memo0025-mpl .venv/bin/python -m unittest experiments.chan_theory.test_memo0025_figures
```

[source] [Figure generator and assertions](../../experiments/chan_theory/test_memo0025_figures.py).
The generator is kept with experiment tests. Images follow this memo's existing
`artifacts/experiments/chan_theory/` convention and are Git-ignored local outputs;
run the command after a fresh checkout to restore the embedded pictures.
All three PNGs were visually inspected for readable labels, unclipped layout,
prices, marker orientation and consistent raw/M coordinates.
