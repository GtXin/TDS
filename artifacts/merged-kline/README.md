# Merged Kline samples
Current figures use the public MergedKlineSeries.plot method. Default options are style="overlay",show_gaps=False,market="US". The US preset uses green-up/red-down;market="China" reverses it. Raw candle line/body and merged border/10%fill use the same palette. Candles compare their own close/open;merged boxes use stored merge direction. Unresolved merged direction and raw volume remain gray.

## Samples
- cc-last40-overlay-gapfree.html/.png:40 original bars with26 merged ranges,defaultUS colors.
- cc-last40-overlay-china.html/.png:the identical40 bars/ranges withChina colors.
- cc-last40-raw-and-merged-gapfree.html/.png:same40 bars in separate price panels,US colors.
- cc-last40-overlay-calendar.html/.png:same40 bars with calendar gaps,US colors.
- worked-example.html/.png:memo015 synthetic10raw→3merged comparison panels,US colors.
- cc-last40-merged.html/.png:last40merged records and their raw extent,earlier vertical-mark style/calendaraxis,US colors.

All6 PNGs inspected for palette/data/labels/clipping. HTML files are standalone interactive charts with hover,zoom/pan andlegendgroup toggles. `merged.plot(raw_start=-40,volume=False)` selects exact40raw bars;start=-40 insteadselects40merged records. These selectors cannot be mixed. Full-data inclusion results are never recalculated for a viewport;directional merged bounds need not enclose everyraw wick.

Reproduce all6 with `PYTHONPATH=src python artifacts/mas/merged-kline-market-colors/generate.py` in an environment withPlotly,Kaleido andlocalChrome. OnlyPlotly is required forplot()/interactiveHTML;temporaryPNGtools are notprojectdependencies. Current evidence:artifacts/mas/merged-kline-market-colors/verification.json. PrepalettePNG/HTML/code arepreserved under artifacts/mas/merged-kline-market-colors/before/. Earlier plot-only checkpoint evidence remains under artifacts/mas/merged-kline-plot-options/.
