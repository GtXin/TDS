# Memo026 US/China plot palettes
## Task
- **ID:**20261109-memo026-market-colors
- **Goal:**Match013 market color option/default for raw and transparent merged ranges;update026 with real examples.
- **Inputs:**current013 market API/defaultUS;two-class026 plot,approved overlay/panels/calendar samples.
- **Allowed changes:**merged plot wrapper/renderer,palette tests,currentsamplegenerator/artifacts,backed-up026/pictures,newpackage,task/memory/log. No013/rawsource/data/rules/dependencies.
- **Acceptance checks:**market='US'default/'China'opt-in;rawline/fill matches013;mergeup/down border+10%fill matchespalette,Nonegray/volumegray;allstyles/gapmodes,invalidinputs,geometry/OHLCpreservation,sourceidentity,classcount;regression/typing/style;renderedUS/China pictures andmemoexamples/links/hashchecks.
- **Assignment:**root owns source/docs/artifacts;merged_market_tests owns onlynewtests/test_merged_kline_plot_markets.py.
- **Status:**done
## Result and handoff
- **Outcome:**marketUS(default)/China on classplot/renderer;matching candleline/body andmergedborder/10%fill;305tests pass;026option/color table/examples/6pictures andinteractiveexports updated.
- **Evidence:**artifacts/mas/merged-kline-market-colors/.
- **Blockers:**none.
- **Next action:**none.

## Actual checks
- Independent merged_market_tests author ownednewtestfile only:27cases passed,Black/Ruff pass. Tests compare palettes directly with KlineTSeries.plot across2markets×3styles×2gapmodes,grayNone/volume,numericgeometry/source preservation,invalidvalues,forwarding andChinaHTML. No source defects found.
- Full `PYTHONPATH=src .venv/bin/python -m pytest tests -q`:305passed. Focused core/options/palette/table suite90passed,no skips. Renderer79/79statements;combined346/348(99.43%). Strictmypy2changedsourcefiles with explicit-package-bases/follow-imports=silent,scopedBlack/Ruff pass.
- Public-method runner renderedUSoverlay,Chinaoverlay,USpanels,UScalendaroverlay,USworkedpanels andUSlegacyranges as6PNG/HTMLpairs. All6PNGs visuallyinspected. Same40raw/26rangesgeometry/OHLC arrays andtimestamps matchbothpresets;7protectedraw/source/013/config/dependencyhashes unchanged. No classes/domainmembers orrules changed.
- Archivedprior6PNG/HTML/code/generator assets before replacement. Backedup026andits5priorPNGcopies,updated003signature/9thoption/palette table/defaultUSexamples/Chinaimage/currentcaptions and002.j. All6memoimagecopiesmatchgeneratedbytes;4Pythonblocks execute,AST2classes/8+6fields/allmethods,links/tablewidths/index/diffcheckpass. UpdatedartifactREADME andpackage memo026_market_colors.zip withmemo+6pictures+6standaloneHTMLpages;testzip/exactmemo bytecheckpasses;oldpackagespreserved.
## Semantic boundary
market is displayconvention only,notinstrumentregion. Raw colors compareclose/open withPlotlynativedoji stroke;mergedcolor followsstored direction,so a boxmaycontain rawcandles ofbothcolors. None direction staysgray. USdefaultgreen=#16a34a/red=#dc2626;China reversed. MergedfillusesidenticalRGBat0.10alpha. Existing overlay/no-gap/volume/selector defaults unchanged. Raw013source/memo anddata remainuntouched.
