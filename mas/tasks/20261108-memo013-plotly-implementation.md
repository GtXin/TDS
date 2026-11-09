# Memo013 Plotly implementation and samples
## Task
- **ID:** 20261108-memo013-plotly-implementation
- **Goal:** Implement the documented plot method, generate visible Plotly samples, and update memo013 cohesively including003.
- **Inputs:** memo013 Appendix, existing Kline/CSV source, full CC master/context and official Plotly documentation.
- **Allowed changes:** src/chanlab/algo/kline.py plot wrapper, src/chanlab/visualization/kline_plot.py, tests/test_kline_plot.py, optional plot dependency/lock, artifacts/kline/, backed-up memo013 scope/plan/results/003/Appendix, task/memory/log. Preserve source data, unrelated code and earlier frozen baseline/skill snapshots.
- **Acceptance checks:** Actual Figure returned, raw arrays/order/UTC/volume equal selected source, full/sliced/volume-off/empty/missing dependency cases, no source mutation, original tests and Ruff pass; full HTML plus PNG sample, visually inspected; coherent memo status and runnable003.
- **Assignment:** Plot author owns only wrapper/helper/new tests; root owns dependencies/artifacts/docs/verification. Simultaneous writes separated by path ownership.
- **Status:** done
## Result and handoff
- **Outcome:** Implemented lazy series.plot, optional Plotly/helper, tests and two visually inspected chart samples; memo013 scope/plan/results/003/Appendix updated cohesively.
- **Evidence:** Source wrapper/helper, tests/test_kline_plot.py, artifacts/kline/verification.json, sample-verification.json, HTML/PNG samples and reproducible generator; memo013003.
- **Blockers:** none. Setup/export failures were resolved and recorded below.
- **Next action:** none for this task; feature overlays, DataFrames and ChanTable object conversion remain deferred.
## Exact Python Pro request (verbatim)
```text
$python-pro
Implement memo013 Plotly plotting now: KlineTSeries.plot(*, start=None, stop=None, volume=True, title=None) delegates lazily to plot_kline_series in src/chanlab/visualization/kline_plot.py and returns a Plotly Figure. Preserve source bars, UTC labels, session gaps and values. Use optional Plotly imports with an actionable uv sync --extra plot message; raw/CSV use must work without the extra. Support full/sliced data, optional aligned volume and empty-selection validation. Return the figure without display/export side effects. Add focused tests in tests/test_kline_plot.py. Do not alter dependencies, memos, artifacts or existing unrelated code/tests; root owns installation, sample chart export, records and final review. Read installed Python Pro and relevant references; use typed Python3.11 and existing pytest/Ruff, no additional domain classes.
```

## Dependency/setup evidence
- Cached-only Plotly/Kaleido resolution initially failed; restricted-network retry failed DNS. Escalated temporary uv environment succeeded: Plotly7.1.0 and Kaleido available. Chrome executable exists locally.
- `UV_CACHE_DIR=/tmp/tds-uv-cache uv add --offline --optional plot plotly`: succeeded, locked optional plot extra, installed Plotly7.1.0/narwhals2.28.0. Base runtime dependencies remain empty. Kaleido remains temporary export tooling.
- `uv lock --offline --check`: passed. Added artifact generate_samples.py to call the actual series.plot method and export200-bar volume/40-bar detail charts; data/source assertions included. Script Ruff passed and Black formatted.
- Plot author delegated only the new plot test file to child plot_tests; parent owns wrapper/helper, root still owns artifacts/dependencies/docs.

## Actual implementation and checks
- Implemented lazy KlineTSeries.plot wrapper and separate Plotly helper; focused11 cases pass. Independent read-only source review passed optional imports, slicing, UTC gaps, source preservation and no display/export side effects.
- Root regression:176 passed. Ruff src/tests/generator passed. Strict mypy3 selected source files passed with localized third-party optional-import ignores; Plotly API internals lack typed-package resolution in isolated checker.
- Initial Black check required formatting helper/new tests; formatted and final4-file check passed.
- Coverage first tool environment lacked Plotly and skipped5 plot cases; reran with Plotly:125 core/plot cases passed,no skips;93% statements (221 total,15 missed).
- Actual series.plot generated200-bar volume and40-bar detail charts, self-contained HTML plus PNG. Asserted every timestamp/OHLC/volume field against selected source and all protected data/source hashes unchanged.
- Sandbox Chrome export initially failed BrowserFailedError; same exporter with authorized escalation succeeded. Both PNGs viewed and visually inspected:readable titles/axes/candles/volume,UTC/session gaps retained,no clipping. Kaleido/Chrome are temporary export tooling only.
- Sample export evidence:artifacts/kline/sample-verification.json and verification.json; generator retained for reproduction.

## Documentation and final handoff
- Backed up memo013 before each edit; updated000/001/002/003/Appendix rather than only the appendix.003 includes actual plot method/options, installation and runnable HTML export plus links to both previews. Original raw baseline/skill comparison remains historical and unchanged.
- Executed both current003 examples successfully and confirmed full10060-bar plot trace close values/order match source. Existing raw/CSV example retained; new example saves artifacts/kline/example-last200.html.
- Current source/configuration: optional plot extra locked and installed; raw base dependencies remain empty. Kaleido only temporary preview tooling. All protected source data/ChanTable/raw-adapter hashes unchanged.
- Final samples:200 bars with volume and40-bar price detail, self-contained HTML+PNG, source-value/hash verified and visually inspected. No feature overlay/detection results invented.
