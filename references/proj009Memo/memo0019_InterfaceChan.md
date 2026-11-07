# InterfaceChan

[interface design] [class design] [chan] [market view]

## 0. Scope And Purpose

> [purpose] Define the high-level input/output interface for Chan analysis
> before Project 009 implements the full Chan structure chain.

> [scope] This memo is about how Chan analysis should be organized as objects:
> derivation, dependency, configuration, cross-timeframe mapping, and display
> readiness.

> [non-goal] This memo does not implement Fenxing, Bi, Xianduan, ZhongShu,
> ZouShi, trading signals, or a full multi-agent simulator.

> [source] This memo extends `memo0015_oop_trading_architecture.md`, the
> current `experiments/chan_theory/` inclusion-merge experiment, and the design
> conversation around recursive minute/hour/day Chan concept mapping.

> [quote from memo0015]
>
> "Chan theory should be modeled as a deterministic `MarketView`."

> [quote from memo0015]
>
> "A Chan view consumes `KlineTSeries` and emits structure objects plus trace
> evidence."

> [quote from memo0015]
>
> "It should not load CSV files, own agent memory, execute trades, or draw final
> charts directly."

## 1. Design Ideas

### 1.a Chan Analysis As Derivation

> [decision] Chan analysis should be modeled as a derivation system, not as one
> large analyzer method and not as unrelated detector services passing data
> between each other.

The natural shape is:

```text
KlineTSeries
-> MergedKlineSeries
-> FenxingSeries
-> BiSeries
-> XianduanSeries
-> ZhongShuSeries
-> ZouShiSeries
```

Each level is an object because each level has its own meaning:

- what it was derived from;
- what config rules governed it;
- what items it owns;
- what trace proves its ancestry;
- what checkpoint proves it matches the reference.

> [class rule] A constructor assembles known state. A `derive_from()` method
> performs explicit Chan computation.

This should be visible:

```python
merged = MergedKlineSeries.derive_from(kline_series, config.merge)
fenxings = FenxingSeries.derive_from(merged, config.fenxing)
bis = BiSeries.derive_from(fenxings, merged, config.bi)
```

This should be avoided:

```python
view = ChanStudy(kline_series, config)  # Hidden full computation in __init__.
```

### 1.b Single-Timeframe Study

> [decision] Use `ChanStudy` as the single-timeframe assembled Chan market
> view during design.

`ChanStudy` means:

```text
one symbol
one period
one source KlineTSeries
one ChanConfig
one complete or partial derived Chan reading
```

Recommended members:

```text
source_series: KlineTSeries
config: ChanConfig
merged_kline_series: MergedKlineSeries
fenxing_series: FenxingSeries | None
bi_series: BiSeries | None
xianduan_series: XianduanSeries | None
zhongshu_series: ZhongShuSeries | None
zoushi_series: ZouShiSeries | None
checkpoints: ChanCheckpointSet
trace: ChanTrace
```

> [meaning] `ChanStudy` is the object a strategy, agent, report, or chart
> adapter can consume without knowing every internal derivation detail.

> [boundary] `ChanStudy` is still a market view, not a strategy and not an
> agent. It interprets market facts. It does not decide trades.

### 1.c Structure And Series

> [decision] A singular Chan object is a structure. A `Series` object is the
> derivation unit that governs a sequence of structures.

The distinction:

```text
structure = one semantic Chan unit
series    = managed sequence of structures with derivation context
```

Examples:

```text
MergedKline        one inclusion-adjusted K-line structure
MergedKlineSeries  managed sequence derived from one KlineTSeries

Fenxing            one top/bottom turning structure
FenxingSeries      managed sequence derived from one MergedKlineSeries

Bi                 one valid stroke structure
BiSeries           managed sequence derived from Fenxing and merged-K evidence

Xianduan           one higher-level segment structure
XianduanSeries     managed sequence derived from one BiSeries

ZhongShu           one center/overlap structure
ZhongShuSeries     managed sequence derived from segment rules

ZouShi             one trend-structure reading
ZouShiSeries       managed sequence derived from centers and segments
```

Single structures matter. But most Chan rules are sequence-dependent, so
Project 009 should design and test Chan logic at the `Series` level.

> [naming rule] Singular classes name semantic structures. `Series` classes
> name the derivation boundary: sequence, config, trace, checkpoints, and
> ancestry.

The series object should not be a thin list wrapper. It should preserve:

```text
derived_from
config
items
trace
checkpoints
period
start_timestamp
end_timestamp
```

### 1.d Dependency And Procedure Management

> [decision] Chan analysis is a series of procedures with dependencies and
> parameters. The dependency order should be explicit, but Project 009 should
> not build a generic workflow engine yet.

First useful dependency chain:

```text
KlineTSeries
-> MergedKlineSeries
-> FenxingSeries
-> BiSeries
-> XianduanSeries
-> ZhongShuSeries
-> ZouShiSeries
```

Each stage should declare:

```text
input type
output type
config section used
trace evidence produced
checkpoint expected
```

Operation responsibility:

```text
Caller chooses ChanConfig.
ChanStudy determines the normal derivation order.
Each Series derives its own structures using its stage config.
Each structure records accepted evidence, not the rulebook.
ChanStudy validates that stage configs match the parent ChanConfig.
```

> [operation rule] A `Series` class may be derived independently for testing
> and study, but only from valid previous Chan series and the correct stage
> config. Normal application callers should prefer `ChanStudy` and read its
> derived series members.

> [small-first rule] Do not introduce `ChanDerivationGraph` or a generic DAG
> runner before the linear chain becomes painful. The first implementation can
> use class-level `derive_from()` methods and explicit tests.

### 1.e Multi-Timeframe Concept Mapping

> [decision] Chan analysis must support concept-level conversion across
> timeframes.

This is not only:

```text
1m KlineTSeries -> 1h KlineTSeries
```

It is also:

```text
1m Chan concept -> 1h Chan concept
1h Chan concept -> lower-timeframe evidence
```

Examples:

```text
1m Bi cluster -> 1h Bi candidate
1m ZhongShu group -> 1h ZhongShu evidence
1h Bi -> contains lower-timeframe Bi / Xianduan / ZhongShu evidence
```

> [split rule] Splitting higher timeframe data means drill-down into existing
> lower-timeframe evidence. It does not mean reconstructing fake minute bars
> from one hourly or daily bar.

> [separation rule] Timeframe aggregation and Chan concept mapping are related
> but separate.

Aggregation:

```text
many lower-period K-lines -> one higher-period K-line
```

Concept mapping:

```text
many lower-period Chan structures -> one higher-period Chan structure or
evidence link
```

Recommended cross-timeframe objects:

```text
MultiTimeframeChanStudy
ChanTimeframeLink
ChanConceptRef
```

`MultiTimeframeChanStudy` owns:

```text
studies_by_period
timeframe_links
base_period
target_periods
config
```

`ChanConceptRef` identifies one concept without copying the full object:

```text
period
concept_type
concept_id
start_timestamp
end_timestamp
```

`ChanTimeframeLink` records a cross-period relationship:

```text
source_period
target_period
source_concepts
target_concept
mapping_rule
confidence_or_status
trace
```

### 1.f Config Governance

> [decision] `ChanConfig` governs the whole study. Stage-level config objects
> govern each derivation level.

Recommended shape:

```text
ChanConfig
-> KlineMergeConfig
-> FenxingConfig
-> BiConfig
-> XianduanConfig
-> ZhongShuConfig
-> ZouShiConfig
-> TimeframeConfig
-> DisplayAnchorConfig
```

Example:

```text
ChanStudy.config                         whole rulebook
MergedKlineSeries.config                 KlineMergeConfig snapshot
FenxingSeries.config                     FenxingConfig snapshot
BiSeries.config                          BiConfig snapshot
MultiTimeframeChanStudy.config           TimeframeConfig included
```

> [reproducibility rule] A derived series must record the exact config section
> that produced it. Later comparison is meaningless if the result cannot prove
> which rule profile generated it.

> [config consistency] `ChanStudy.config.bi` and
> `ChanStudy.bi_series.config` must be equal. The same rule applies to other
> stages: the parent `ChanConfig` governs the whole study; each derived series
> records the exact stage config it used.

> [state boundary] Output state is not automatically configuration.
> For example, `MergedKline.merge_state` records whether a row belongs to a
> direction-resolved or direction-unresolved merged group. That state is an
> output of `KlineMergeConfig`, not another rule option inside it.

### 1.f.1 `FenxingSeries` Operation Example

> [example] `Fenxing` is one top/bottom structure. `FenxingSeries` is the
> derivation boundary that scans `MergedKlineSeries` under `FenxingConfig`.

Operation:

```text
MergedKlineSeries + FenxingConfig -> FenxingSeries
```

Shape:

```text
FenxingSeries
-> derived_from: MergedKlineSeries
-> config: FenxingConfig
-> items: tuple[Fenxing, ...]
-> trace
-> checkpoints
```

Rule:

```text
FenxingSeries should not derive directly from raw KlineTSeries.
Raw included K-lines can create false turning structures.
```

### 1.f.2 `BiSeries` Operation Example

> [example] `Bi` is one accepted stroke structure. `BiSeries` is the
> derivation boundary that applies `BiConfig` to `FenxingSeries` with
> `MergedKlineSeries` as supporting evidence.

Operation:

```text
FenxingSeries + MergedKlineSeries + BiConfig -> BiSeries
```

Shape:

```text
BiSeries
-> derived_from: FenxingSeries
-> merged_kline_series: MergedKlineSeries
-> config: BiConfig
-> items: tuple[Bi, ...]
-> trace
-> checkpoints
```

Why both inputs matter:

```text
FenxingSeries gives candidate tops and bottoms.
MergedKlineSeries verifies span, interval extremes, gaps, and trace.
BiConfig defines the acceptance and repair rules.
```

> [config rule] `BiConfig` is a member of `BiSeries`, not usually a member of
> each `Bi`. `BiSeries` applies the rule. `Bi` records the accepted stroke and
> its evidence.

> [dependency rule] `BiSeries` should not derive from `MergedKlineSeries`
> alone, and it should not derive from raw `KlineTSeries`. It needs the
> previous Chan concept series plus supporting merged-K evidence.

### 1.g Display Requirement

> [decision] Chan structures must be display-ready, but they must not render
> themselves.

Every displayable Chan structure should expose anchors:

```text
period
concept_type
start_timestamp
end_timestamp
start_price
end_price
high
low
source_refs
trace
```

Visualization should be separate:

```text
ChanStudy
-> ChanOverlayAdapter
-> OverlayLine / OverlayBox / OverlayMarker
-> KlineTSeriesChart or future frontend chart
```

> [boundary] No `Fenxing.draw()`, `Bi.draw()`, or `ZhongShu.draw()` method.
> Chan objects carry meaning and anchors. Visualization objects render them.

### 1.h Chan-Only Semantic Boundary

> [decision] Chan subprocess classes should be semantically locked to Chan.
> They should not look like generic reusable market utilities.

When promoted later, Chan code should live under:

```text
src/tradinglab/market_views/chan/
```

Internal workers should use Chan-specific naming when their role could look
generic:

```text
ChanKlineCombiner
ChanFenxingDetector
ChanBiBuilder
ChanXianduanBuilder
ChanZhongShuBuilder
ChanZouShiBuilder
```

Internal worker modules can use leading underscores:

```text
_merge.py
_fenxing.py
_bi.py
_xianduan.py
_zhongshu.py
_zoushi.py
```

Public exports should favor stable concepts:

```text
ChanConfig
ChanStudy
MultiTimeframeChanStudy
ChanConceptRef
ChanTimeframeLink
MergedKlineSeries
FenxingSeries
BiSeries
XianduanSeries
ZhongShuSeries
ZouShiSeries
```

> [export note] Singular item records may be exported later when external code
> truly needs to type-check or inspect individual structures. The first public
> interface should stay series-first.

> [semantic rule] If a subprocess class only exists for Chan derivation, keep
> it inside the Chan package, use Chan-specific config, and do not export it
> from package `__init__.py` by default.

## 2. Class Shape

### 2.a Conceptual Package

> [placement] During 7.4 incubation, keep unstable Chan implementation under
> `experiments/chan_theory/`.

Future source shape, only after explicit promotion:

```text
src/tradinglab/market_views/
└── chan/
    ├── __init__.py
    ├── config.py
    ├── study.py
    ├── concept_ref.py
    ├── timeframe_link.py
    ├── merged_kline.py
    ├── fenxing.py
    ├── bi.py
    ├── xianduan.py
    ├── zhongshu.py
    ├── zoushi.py
    ├── _merge.py
    ├── _fenxing.py
    ├── _bi.py
    ├── _xianduan.py
    ├── _zhongshu.py
    └── _zoushi.py
```

### 2.b Minimal Public Usage

Single timeframe:

```python
config = ChanConfig.default()

merged = MergedKlineSeries.derive_from(kline_series, config.merge)
fenxings = FenxingSeries.derive_from(merged, config.fenxing)
bis = BiSeries.derive_from(
    fenxing_series=fenxings,
    merged_kline_series=merged,
    config=config.bi,
)

study = ChanStudy(
    source_series=kline_series,
    config=config,
    merged_kline_series=merged,
    fenxing_series=fenxings,
    bi_series=bis,
)
```

Multi-timeframe:

```python
minute_study = ChanStudy.derive_from(minute_series, config)
hour_study = ChanStudy.derive_from(hour_series, config)

multi = MultiTimeframeChanStudy(
    studies_by_period={
        "1m": minute_study,
        "1h": hour_study,
    },
    timeframe_links=links,
    config=config,
)
```

Display:

```python
overlays = ChanOverlayAdapter(study).to_overlays()
chart = KlineTSeriesChart(series)
chart.render_to_file(path, overlays=overlays)  # Future API, not current code.
```

> [note] The display example is future-facing. Current `KlineTSeriesChart`
> does not yet accept overlays.

## 3. First Implementation Boundary

> [current fact] The current Chan experiment has only the first slice:
>
> ```text
> KlineTSeries -> KlineCombiner -> MergedKline
> ```

> [checkpoint] The current verified checkpoint is:
>
> ```text
> 10060 raw K-lines -> 6200 merged K-lines
> ```

For the next 7.4 slice, do not build the full architecture at once.

Recommended next implementation pressure:

```text
MergedKlineSeries
FenxingSeries
```

`Fenxing` may still exist as the item record inside `FenxingSeries`, but the
design pressure should be the series derivation and checkpoint, not the isolated
record.

Update the existing experiment toward the new naming only when it improves the
next test:

```text
KlineCombiner -> ChanKlineCombiner
tuple[MergedKline, ...] -> MergedKlineSeries
```

> [promotion rule] Do not create `src/tradinglab/market_views/chan/` until more
> than one Chan level has stable tests and the staged milestone records the
> promotion decision.

## 4. Open Questions

> [open] Should the single-timeframe public object be named `ChanStudy`,
> `ChanMarketView`, or `InterfaceChan` when it becomes source code?

Current preference:

```text
memo title: InterfaceChan
single-timeframe object: ChanStudy
architecture role: MarketView
```

> [open] Should `ChanStudy.derive_from()` compute the whole available chain, or
> should each stage be derived manually during the first few experiments?

Current preference:

```text
first experiments: derive each stage manually
later convenience: ChanStudy.derive_from(...)
```

> [open] What is the first cross-timeframe checkpoint?

Candidate:

```text
derive 1h K-lines from 15m sample data
derive Chan structures for both periods
prove one higher-period structure can drill down to lower-period evidence
```

> [open] What overlay API should `KlineTSeriesChart` expose later?

Current preference:

```text
chart accepts neutral overlay objects
ChanOverlayAdapter creates those objects
Chan structures do not import chart libraries
```
