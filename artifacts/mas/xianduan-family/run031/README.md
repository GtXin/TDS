# Memo031 execution evidence

Production implements memo030 XD030-E operational rules on fixed snapshots. Defaults: Bi distance_mode=weak (gap3), Xianduan xd_mode=weak (no7a endpoint restriction). Explicit modes remain independent. Theoretical completeness for complex absorption remains unproved; this run does not reinterpret unresolved original examples.

| Contract | Implementation / independent check |
|---|---|
| memo030001 Shape,7a/7b;002.c2.2 | src/chanlab/algo/_xianduan_events.py; tests/test_xianduan.py |
| 002.c2.4–2.7 fixed containment, strict fractals, direct/gap, actual S/T/U | _xianduan_features.py / _xianduan_events.py; reference_events.py with independent full-list normalization |
| 002.c2.8–2.11 multi-source(count,endpoint), stable ties | _xianduan_select.py; validate.py full-chain enumeration / reverse suffix DP |
| memo009002.j/k immutable record/source/trace APIs | src/chanlab/algo/xianduan.py; tests/test_xianduan.py |
| memo009002.u raw-axis mapping and context | data/xianduan_table.py / feature_table.py / algo/chan_table.py; CSV/context roundtrip |
| memo031001.a–f | production; baseline/ vs frozen Python Pro continuation; comparison.json; coverage/regression; monte-carlo.json; scaling/full-result; charts/ |

Run from repository root with PYTHONPATH=src .venv/bin/python and the script path: validate.py, compare.py, real.py, full.py, charts.py. Charts use a native Swift/AppKit renderer derived from memo030-e/charts/render.swift; source arrays and IDs are checked before visual review. All generated data belong to this run; originals remain unchanged.

Baseline selector/events are byte-for-byte frozen historical implementations. baseline-instrumented.py only adds the same SHA256 traversal digest over(a,b,c,count,prev), enabling independent-process verification of all generated DP records. Profile-label differences are excluded from witness comparison. The continuation is sequential engineering using Python Pro1.1.0; prior skill exposure is disclosed, no causal skill-performance inference.

Optimizations preserve the operational rule: first strict crossing lookup replaces repeated invalidation scans; normalized prefixes extend cached prior reductions; second-sequence events depend on(b,d) and are reused while filtering h1<=c. Their normalized middle is strictly before h2, hence h1<=c implies max(h1,h2)=h2. Baseline400cases and independent random/full checks verify these transformations. Temporary feature caches are cleared before DP. Initial interrupted 3k run retained in initial-slow-run.txt. failure.json is the resolved initial historical-profile-label assertion, not a remaining geometry counterexample.

Evidence time is the raw timestamp label of the right merged neighbour required by the event endpoint fractal. It is distinct from geometric endpoint time, and does not claim permanent streaming availability or immutable future confirmation. Candidate evidence tail remains separate from confirmed items. No cross-batch resume.

References: [memo031](../../../../docs/memo/memoWX_031_xianduanFamily.md), [memo030001/002](../../../../docs/memo/memoWX_030_Chan_xianduan.md), [memo029](../../../../docs/memo/memoWX_029_Chan_bi.md), [memo009002.j/k/u](../../../../docs/memo/memoWX_009_designPatternForChanFeatures.md), [Python Pro1.1.0](../../../../mas/skills/python-pro/SKILL.md), [task](../../../../mas/tasks/20261111-memo031-implementation.md).


Cost: with N source pens, up to O(N²) shape candidates and O(N³) adjacent-pair states; all successors can yield O(N⁴) transition attempts. Local event/feature enumeration adds its own cost (not hidden inside O(V+E)); normalized tuple/member caches can require cubic storage. DP retains successful relaxation records for reconstruction, bounded by an explicit six-million-record budget; overflow raises and does not publish a truncated optimum. This is not the quadratic Bi algorithm. A later evidence frontier for fixed geometry/type is dominated by the earliest one with the same actual reverse boundary, because future eligibility is only an endpoint threshold under this local contract. Native candidate compaction applies only that equivalence, not arbitrary historical states.

`real-progress.txt` includes periodic faulthandler “Timeout” stack snapshots for profiling; they do not interrupt or count as failed validation. Independent full-list reduction and backward suffix objective checking are intentionally outside measured pipeline timings. `initial-slow-run.txt` / `second-slow-run.txt` retain actual interrupted development attempts.


Rebuild atlas from repository root (full.py or real.py first writes production contexts):
```sh
PYTHONPATH=src .venv/bin/python artifacts/mas/xianduan-family/run031/charts.py
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/xianduan-family/run031/charts/render.swift artifacts/mas/xianduan-family/run031/charts
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/xianduan-family/run031/charts/comparison/compact.swift artifacts/mas/xianduan-family/run031/charts
PYTHONPATH=src .venv/bin/python artifacts/mas/xianduan-family/run031/atlas_check.py
```
`real.py` independently checks every repetition before saving scaling.json. `timing_final.py` repeats final-version timings with deterministic route agreement and previously independently validated objective counts, saving scaling-final.json. `usage.py` is the executed default example. Preserve source-hashes.json and implementation-hashes.json when comparing runs. Visual review is a separate human/agent step; rendering alone does not create a visual acceptance result.

Final checks:439activepytest,14directedtests,96%combinednew-modulecoverage (each >90%), strictmypy9sourcefiles,Black10files,RuffPASS. Snapshot guards reject invalid config/source/evidence-time types. Empty confirmed output retains an explicit unresolved source range and queryable Shape-only pending candidates. final-checks.json and the task record contain the completed handoff. Existing unrelated logXW merge conflict remains unchanged.
