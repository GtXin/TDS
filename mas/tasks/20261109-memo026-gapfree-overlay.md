# Gap-free raw and merged overlay
## Task
- **ID:**20261109-memo026-gapfree-overlay
- **Goal:**Add a readable overlay of40 original bars and their merged intervals,keeping the approved two-panel chart.
- **Inputs:**current026,full raw sample and merged implementation,gap-free40 chart.
- **Allowed changes:**new sample generator/PNG/HTML/evidence,backed-up026/new sibling picture,new memo package,memory/log/task. No domain/API/data/dependency changes.
- **Acceptance checks:**same40raw/26merged full-data output,translucent low/high coverage bands behind unchanged candles,gap-free shared axis,no fabricated merged OHLC,visual inspection,embedded memo picture and package byte checks.
- **Assignment:**Codex.
- **Status:**done
## Result and handoff
- **Outcome:**Readable gap-free overlay generated/inspected;embedded in026003.f alongside approved two-panel chart;new memo+4images package produced.
- **Evidence:**artifacts/mas/merged-kline-gapfree/generate_overlay.py and overlay-verification.json;artifacts/merged-kline/cc-last40-overlay-gapfree.*.
- **Blockers:**none.
- **Next action:**none.

## Verification
Same raw[10020:10060]40bars and26 full-data merged intervals as approved two-panel chart;source/context hashes unchanged.10%opacity merged blocks drawn first,original candles last;equal consecutive positions and price axis. Geometry/trace arrays checked against source/results;no fabricated merged OHLC. Direction groups toggle together in interactive legend. LocalChrome PNG export succeeded with authorized broader permission;image visually inspected,no clipping/occlusion. Backed up026 before embedding exactPNGcopy;caption distinguishes directional bounds from outer envelope. Memo links/table widths/copy/archive bytes/testzip/diffcheck passed. Newpackage artifacts/exports/memo026_with_overlay.zip preserves prior package. No domain/API/data/dependency/test changes or regressionrerun.
