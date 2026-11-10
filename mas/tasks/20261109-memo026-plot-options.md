# Preferred overlay and gap-free plot API
## Task
- **ID:**20261109-memo026-plot-options
- **Goal:**Make approved interactive overlay/gap-free view available and default in MergedKlineSeries.plot;retain panels/calendar/legacy choices and update026.
- **Inputs:**current026,two-class implementation,approved40raw/26merged screenshots and raw plot API.
- **Allowed changes:**merged series plot wrapper/renderer,plot tests,current sample generators/new generated outputs,backed-up026/new sibling pictures,task/memory/log. No domain fields/classes,inclusion rules,source data or dependencies.
- **Acceptance checks:**overlay default/show_gaps=False,panels and explicit legacy ranges/calendar,raw40 viewport versus merged-position slicing,full-data source-preserving bounds/coverage,interactive HTML/legend,optional volume,invalid options/no display/no mutation;focused/regression/type/style checks;production-method samples rendered/inspected,doc examples/links/images verified.
- **Assignment:**root owns wrapper/renderer/docs/generators/task/log;plot_option_tests owns only new tests/test_merged_kline_plot_options.py. No simultaneous writes to same files.
- **Status:**done
## Contracts
style='overlay'|'panels'|'ranges',defaultoverlay;show_gaps=False default;existing start/stop meanmergedpositions;raw_start/raw_stop optionally selectrawpositions and cannot mix with start/stop. No recalculation/clipped-result record creation for viewport;hover retains fullsource ranges. Returned Figure is interactive;caller owns show/write_html. Optional volume=True retained. No new classes.
## Result and handoff
- **Outcome:**Class plot API now defaults to interactive gap-free overlay,with panels/calendar/legacy options and exact raw viewport selection;264tests pass;026 and current method-generated PNG/HTML samples updated.
- **Evidence:**artifacts/mas/merged-kline-plot-options/.
- **Blockers:**none.
- **Next action:**none.

## Actual checks and evidence
- Independent author plot_option_tests added31cases in owned newfile only;root inspected them. Tests cover default overlay/source UTC+OHLC/no auto output,fullraw[-40:]exact40/26,merged slicing,clipped group bounds without recomputation,singletons,panels/volume/calendar,15invalid requests,legend and offlineHTML. No source defects found by author.
- `PYTHONPATH=src .venv/bin/python -m pytest tests -q`:264passed. Focused core/table/newplot suite:63passed,no skips. Coverage342/344 combinedstatements(99.42%);renderer75/75(100%).
- Strict mypy2changed source files with explicit-package-bases/follow-imports=silent passed;scoped Black/Ruff pass. Only importsorting/formatting corrections needed. Earlier source-alignment test now explicitly requests style=ranges/show_gaps=True and locates traces bykind,so its historical contract remains checked without pinning new defaults.
- Production-method generator exports exact40raw/26merged overlay/panels/calendar HTML+PNG from full10060raw/6200merged source. Export via authorized localChrome;all3PNGs visually inspected for bounds/labels/clipping. Source hashes/OHLC unchanged. Sample generators delegate to the single public-method runner;older error-mark snapshots/runners pinned explicitly to legacy style.
- Saved pre-API approved PNG/HTML/renderer/generators under before/. Backed up026 before each text edit,and prior memoPNGcopies before replacing with actual public-method renderings;newcalendar image copied beside memo. Original legacy reports tagged historical with archivedPNG/currentreport pointers.
- Updated026002.i,003signature/options/examples/pictures and Appendix;defaultoverlay listed/shown first. AST still2classes/8+6fields;allpublic/private methods documented;4Pythonexamples execute;links/tablecolumns/index/picturebytes/diffcheck pass. Two-class/inclusion/data adapters unchanged.
- New download package artifacts/exports/memo026_plot_options.zip contains exact memo,5pictures and3standaloneHTML pages;archivebytes/testzip/PlotlyJS checks pass. Previous packages preserved.
## Notes
Existing merged start/stop semantics remain unchanged. New raw_start/raw_stop are alternate selectors and reject mixed usage. Calendar band edges use observed-bar-width visual padding;raw candle timestamps/hover remain original. Each mergedrange retains fullbound/source metadata even if clipped on screen. This changes rendering defaults intentionally at user request;other raw plot defaults/dependencies and domain rules remain unchanged.
