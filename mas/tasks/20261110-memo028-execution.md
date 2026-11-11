# Task
- **ID:** 20261110-memo028-execution
- **Goal:** Execute memo028 including all-route Bi implementation and raw-Kline Monte Carlo validation.
- **Inputs:** memo009/010/011/012/013/015/019/020/026/027/028 and existing source; current working changes preserved.
- **Allowed changes:** Bi algorithm, adapters, visualization, focused tests, artifacts/mas/bi-family, memo028 with backups, memory and log.
- **Acceptance checks:** all routes match independent reference on bounded inputs; definition oracle; 10,000 raw sequences; focused/regression pytest, strict typing/style/coverage, table roundtrip and visual checks.
- **Assignment:** Codex directly; no subagents.
- **Status:** done
# Result and handoff
- **Outcome:** In progress. Mapping: each route is one BiSeries; derive_candidates returns immutable boundary-grouped report containing every route; derive_from requires explicit endpoint route if ambiguous. No default selector or extra domain class.
- **Evidence:** Skill invocation request: “wonderul now exectue”; executing memo028001.b with Python Pro1.1.0. Skill already read before baseline; comparison is sequential, not causal.
- **Blockers:** None yet; exponential enumeration bounded explicitly with failure on resource exhaustion.
- **Next action:** Implement and validate core.

## Execution result
- **Outcome:** Bounded implementation, selected-route table/DataFrame/plot integration and Monte Carlo complete. Full real-data all-route enumeration is incomplete; task remains blocked on candidate growth, not on user permission.
- **Mapping:** Two domain classes only; immutable report groups BiSeries by boundary. derive_from requires explicit route under ambiguity; first registered selected route projects into fixed CSV columns, all keys remain individually accessible.
- **Evidence:** `artifacts/mas/bi-family/`: frozen baseline/continuation hashes and independent-process comparison200 inputs;24 focused tests;410 regressions;93% new-module statement coverage; strict mypy5 source files, Black and Ruff pass. Ten thousand completed raw sequences cover53,927 routes and139,599 strokes with zero definition/reference differences;1000 policy/tie probes and300 transformed-input probes. Initial mixed-policy report and resource failure retained. Two PNGs visually inspected after Chrome rendering succeeded outside sandbox.
- **Actual commands:** `PYTHONPATH=src .venv/bin/python -m pytest tests -q`; focused coverage uses project Python with temporary tools site-packages on PYTHONPATH; `MYPYPATH=src /private/tmp/tds-memo026-tools/bin/mypy --strict --follow-imports=silent --explicit-package-bases` on5 changed modules; Black check and Ruff check on those modules. `verify.py`, `compare.py`, `variant_worker.py`, `full_and_plot.py` preserve experiment entry points. No dependencies/config changed.
- **Limitations:** Full10,060raw/6200merged/3027fractal input exhausted100,000-state budget; no partial output returned. A129-bar single-price seed1216 also exhausted budget; reproducer retained. Random generation lengths reduced to explicit9–65-bar bounded scope; not a claim about arbitrary lengths. Metadata/class trace continuation is an engineering improvement after prior skill exposure, not causal skill evidence. Six helper responsibilities are encapsulated in the candidate loop and pairing method, rather than six identically named methods.
- **Next action:** Design scalable sharing/compression and a feasible full-data output/resource contract without pruning valid routes; rerun full-data acceptance afterward. No unique selector, live confirmation or incremental algorithm added.

## Rerun under confirmed left-to-right start policy
- **Outcome:** Completed revised implementation and full rerun. Earliest fractal admitting a qualifying later endpoint is sole initialA; no later-start fallback. Prior results are historical in artifacts/mas/bi-family/history/.
- **Evidence:** Random raw OHLCV→KlineTSeries→existing MergedKlineSeries→existing FenxingSeries→Bi. Seeds0–9999,10,000 complete inputs;11,368 routes/33,249 strokes, zero independent definition or recursive-reference differences.27 Bi tests and413 regressions pass;93% new-module coverage; strict mypy, Black and Ruff pass. Baseline/continuation agree on200 isolated inputs; continuation adds explicit start/status/unresolved diagnostics. Original invocation for rerun: “重新执行028 另外验证的时候随机产生kline 然后用mergerdK和fenxing处理 然后再来验证bi”. Python Pro1.1.0 already read; sequential comparison only.
- **Full-data result:** Complete in3177 states, initialA source position0, blocked at source position151, zero viable routes. Original CSV hash unchanged. This is a completed empty-result computation, not successful full-market segmentation; no implicit later-start fallback.
- **Next action:** Discuss desired handling after initialA's branches all block; do not add an unstated rule. Live confirmation/incremental handling remain outside scope.
