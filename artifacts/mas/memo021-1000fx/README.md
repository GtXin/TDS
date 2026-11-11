# XD-P1: real first1000FX experiment

The user chose completing our recognizer before validation, rather than substituting CC output. XD-P1 was recorded in memo021 before real execution. It is an explicit conservative experimental profile, not a proof of author-unique or author-complete Chan segmentation. No production algorithm, memo029/028, raw sample or CC code was modified/executed by this experiment.

## Reproduce

From repository root (existing Python3.11 environment):

```sh
PYTHONPATH=src .venv/bin/python artifacts/mas/memo021-1000fx/input/prepare.py
.venv/bin/python artifacts/mas/memo021-1000fx/run.py
.venv/bin/python artifacts/mas/memo021-1000fx/independent_validate.py
.venv/bin/python -m pytest artifacts/mas/memo021-1000fx/tests_profile.py -q
.venv/bin/python artifacts/mas/memo021-1000fx/plot.py
swift -module-cache-path /private/tmp/tds-xd-png-module-cache artifacts/mas/memo021-1000fx/charts/render.swift artifacts/mas/memo021-1000fx/charts
.venv/bin/python artifacts/mas/memo021-1000fx/charts/verify.py
```

A new render requires renewed visual QA. Timing/cache metadata may vary; source identity and selected geometry are deterministic.

## Inputs and results

- Preserved real sample10060raw→6200merged→3027FX. Cut afterFX999's complete window and rebuild:3244raw→2040merged→exactly1000FX, field-exact prefix equality. `input/README.md` and `input/summary.json` retain provenance, raw/source hashes and upstream checks.
- Strong input167Bi→15XD, FX0→917; openBi[147,167). Recognition/graph/selection median0.151s over3warm repetitions.
- Weak input239Bi→26XD, FX0→986; openBi[234,239). Median0.412s. Timing excludes upstream loading/calculation and plotting.
- Own implementation `recognizer.py` uses strict anchoredF1/F2, side-local inclusion, declared point/equality policies, guarded direct-break supplement, source-horizon compatibility and parent-only secondary states. `profile-spec.md` gives exact choices; earlier reviewR1 is not the selected profile.
- One completion winner per origin gives maxoutdegree1: the029DP selector degenerates to a chain baseline. Do not treat the result as a search over every Chan-legal alternative.

## Actual checks

- All406upstream Bi pairs independently interval-scanned valid.
- 20synthetic pytest cases pass, including100random inputs/mirrors, positive transforms, containment/equality/openEOF, two supplied confirmation examples and the conflicting-gap regression. Ruff passes on all7experimentPython files. Optional mypy/Black/coverage modules are absent; none installed. Implementer used stdlibtrace for381/395source-line coverage (96.46%), not branch coverage.
- `independent_validate.py` imports no recognizer functions. Its separate list-reduction implementation examines21050origin/boundary pairs; reconstructs324primary certificates,353states and327edges; verifies allbest/prev/selected geometry by DFS,41selected segments, source maps, tail and6upstream hashes. `independent-validation.json` recordsPASS and exact scope.
- Fresh certificate replay is an additional shared-implementation check, not the independent oracle.
- `results.json` contains full source/proof/graph/selection records; `summary.json` retains compact counts/timing.

## Charts

[Offline atlas](charts/index.html):26HTML/PNG pages, oneoverview+12merged200/20overlap detail windows per mode. Each mode covers all3244raw/2040merged/1000FX and every Bi/XD. Static PNGs are native Swift/AppKit views of the exact plotted source arrays; interactive Plotly pages retain hovers/provenance. No separate browser-interaction test claimed.

All5finalcontact sheets/all26pages were independently inspected, and root viewed the full atlas before label-only corrections plus4final full-resolution memo figures. Clipped left labels and shared-endpoint text collisions were corrected; no price/line geometry changed. `charts/chart-check.json`, `charts/coverage.json`, `charts/agent-visual-qa.json`, `visual-qa.json` and `memo-image-copies.json` preserve source coverage, finalPNG hashes and QA scope. Four inspected PNGs are byte-identical memo-companion copies.

## Limits / next action

The independent checker establishes consistency with XD-P1, not agreement with every original special case. Strict-fractal and conservative compatibility choices can omit valid complex structures. Review the real plots, extend specific counterexamples/rules explicitly in021 before changing the experimental recognizer, and then repeat verification. OpenEOF is reported normally; no permanent confirmation or guaranteed future completion is claimed.
