# XD-P1 first1000FX atlas

Reproduce HTML/figureJSON from repository root:

```sh
.venv/bin/python artifacts/mas/memo021-1000fx/plot.py
swift -module-cache-path /private/tmp/tds-xd-png-module-cache artifacts/mas/memo021-1000fx/charts/render.swift artifacts/mas/memo021-1000fx/charts
.venv/bin/python artifacts/mas/memo021-1000fx/charts/verify.py
```

Both modes have1overview+12detail pages,200merged bars per full detail window with20bar overlap. Every mode covers3244raw/2040merged/1000FX and allselectedBi/XD. Pages are viewports of one global calculation, not separately recomputed routes. All1000FX markers are retained; detailed text labels useBi/XDendpointFX to limit clutter, with every index/time inHTMLhover.

`index.html` links bothoffline atlases. `manifest.json` lists every page/source range and IDs. `chart-check.json` checks all rawOHLC arrays, FX coordinates, Bi/XDtrue endpoints, unique sharedendpoint annotations and26PNG1800×900 files. `coverage.json`/`render.json` record generation and rendering. `agent-visual-qa.json` records finalcontact inspection and finalPNGhashes; root's independentcritical-page QA is separate.

PNGs use nativeSwift/AppKit rendering of the exact figure source arrays and fixed axes, not browser screenshots; offlineHTML usesPlotly. No source geometry is changed or smoothed. Cross-window lines use true endpoints, clipped at theviewport; y-range includes visibleboundary interpolation. Amber tail isuncompleted, never forcedclosed. Titles andlegends identifyourXD-P1experimentalprofile, notCCor author-unique output.

SharedXDendpoint labels were combined andedge labels movedinsideplot withoutchangingactualpoints. All26finalpages werevisuallychecked atcontact-sheet scale; finalstrongdetail007waschecked fullresolution. Plot.py/verify.pyRuffchecks pass; nativeSwiftcompilation/renderingpasses. Current.venv lacksBlack/mypy/Kaleido/PIL; nonewasinstalled.
