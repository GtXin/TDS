# Memo026 execution
## Task
- **ID:** 20261109-memo026-execution
- **Goal:** Execute memo026 core, comparison, verification and plotting; update memo with actual results.
- **Inputs:** memos009/013/015/026; existing raw classes, sample/context and plotting helper.
- **Allowed changes:** new merged algorithm/renderer/tests, artifacts/mas/merged-kline-family/, artifacts/merged-kline/, backed-up026, this task, memory/log.
- **Acceptance checks:** memo015 examples and initializers, immutable interfaces/source coverage/trace, common baseline/continuation suite, regression/quality checks and full-data plot inspection.
- **Assignment:** Codex, sequential implementation; no delegation.
- **Status:** done
## Implementation contracts
Explicit config with UP/DOWN/BOTH/OUTER/UNSET; complete series versus immutable PendingMerge/DualMerge wrappers. All records unconfirmed/None pending a confirmation rule. MergeDecision is a scoped trace, not the deferred general DecisionStep design. BOTH warning_evaluation='not_evaluated'. Table/DataFrame adapters remain absent/deferred.
## Result and handoff
- **Outcome:** Selected immutable core and Plotly extension implemented; memo026 updated with actual interfaces, runnable examples and results. Deferred integrations remain as scoped.
- **Evidence:** artifacts/mas/merged-kline-family/.
- **Blockers:** none for scoped calculation; confirmation/warning/adapters deferred.
- **Next action:** none for this execution; confirmation/warning rules and table/DataFrame integration require separate scope.
## Exact Python Pro invocation request
```text
$python-pro
Execute memo026 step001.b using the frozen baseline contract and identical acceptance suite. Read mas/skills/python-pro/SKILL.md and relevant typing/testing references. Continue the immutable MergedKline family with explicit initialization/pending/dual outcomes and scoped merge traces; preserve baseline, raw data, existing code and dependencies. Record typing/validation corrections and run strict mypy, Black, Ruff and tests. Plotting follows as a separate extension. This is a sequential continuation with prior skill exposure, not a blind skill experiment.
```
Skill read: installed Python Pro1.1.0; source pin as recorded in memo012. Baseline initial acceptance:23 passed, including648 scalar-oracle sequences.

## Actual checks and results
- Initial baseline: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_merged_kline.py -q`:23 passed;648 scalar-oracle sequences embedded in3 parametrized cases.
- Common final core comparison via verify.py subprocess imports:baseline23 passed/1 failure; selected24 passed,2 plot cases deselected. Both full-data payloads match6200 intervals for all5 explicit policies. Module paths and hashes printed in checks/.
- `PYTHONPATH=src .venv/bin/python -m pytest tests -q`:202 passed.
- `PYTHONPATH=src /tmp/tds-memo026-tools/bin/python -m coverage run --data-file=artifacts/mas/merged-kline-family/checks/.coverage --source=chanlab.algo.merged_kline,chanlab.visualization.merged_kline_plot -m pytest tests/test_merged_kline.py -q`:26 passed; coverage JSON277/278 statements (99.64%).
- `MYPYPATH=src /tmp/tds-memo026-tools/bin/python -m mypy --strict --explicit-package-bases --follow-imports=silent src/chanlab/algo/merged_kline.py src/chanlab/visualization/merged_kline_plot.py`:passed. Optional untyped Plotly imports have localized ignores.
- Black check of new source/renderer/tests and report-only Ruff:passed. Formatting/import fixes were applied only to new files during continuation.
- verify.py:10060 raw rows,9 context entries;6200 merged/10061 trace events,all5 policies. Master/context hashes unchanged. No config/dependency or existing algorithm/adapters changed.
- Both HTML/PNG charts generated,PNG inspection completed; source-array alignment tested. Memo003 examples executed successfully; local links,backup bytes,selected snapshot identity and git diff --check passed.
## Tooling and failures
- Repo venv lacked mypy/Black/coverage. Created an offline temporary tool environment in /tmp/tds-memo026-tools using cached packages; no project manifest changes. Initial uv run executable was ephemeral and unavailable afterwards; persistent temp venv fixed this.
- Initial mypy package mapping failed; explicit-package-bases fixed it. Plotly lacks typing markers; localized import-untyped ignores added. Initial Ruff/Black issues corrected in new files.
- Root pytest initially collected the frozen artifact test under the same name as live tests. Renamed its unchanged contents to acceptance_frozen.py; normal tests regression then passed. hashes.txt retains the pre-rename filename with unchanged content hash.
- Chrome PNG export failed in sandbox, succeeded with authorized broader execution permission; later sandbox verification failed to re-export but preserved successfully exported/inspected PNGs. verification.json retains failures and separately records inspected PNG hashes.
- Baseline's final trace-map failure is intentionally preserved. No claim of skill-only causality or performance benchmark.
## Remaining limitations
Unconfirmed/None is the only supported record status; full confirmation semantics remain undefined. Warning scoring is explicitly not_evaluated. Scoped MergeDecision does not implement general DecisionStep. Table/DataFrame methods are absent/deferred, not no-op stubs. Complete structural validation does not establish arbitrary hand-constructed traces as a correct replay; factory output is checked against examples/oracle. No resumable pending-state API is promised.
