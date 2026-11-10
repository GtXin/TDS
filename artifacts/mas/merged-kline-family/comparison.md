# MergedKline implementation comparison
Selected core checkpoint: Python Pro continuation in `python_pro/merged_kline.py`. Renderer, table/DataFrame interfaces and the user-directed two-class OOP correction extend the live source; frozen snapshots preserve the original core comparison.

| Check | Frozen baseline | Selected continuation |
|---|---|---|
| Original focused suite |23 passed|23 passed|
| Final common core suite |23 passed /1 failed|24 passed|
| Full10060-row sample, all5 policies |6200 intervals; identical payload hashes|6200 intervals; identical payload hashes|
| Trace map omitting executed events |Accepted (known defect)|Rejected|
| Scoped decision rule/index/source checks |No decision constructor validation|Validated|
| Strict mypy/Black/Ruff |Not claimed|Passed changed source; Black/Ruff also changed tests|
| Active core+plot focused tests |Not part of frozen core|26 passed|
| Existing+new regression |Not deployed|202 passed|
| Changed core/renderer coverage |Not measured|277/278 statements,99.64%|

The same author wrote baseline and then read/applied Python Pro1.1.0 with prior exposure. Continuation incorporates typing, documentation, formatting and validation review; no causal skill-effect or performance claim. Snapshots are evidence, not alternative installed packages. Both variants execute the same final core suite in separate processes and print resolved module paths. Their full-data payload SHA-256 hashes match for every explicit policy. This input does not require initial inclusion policy selection; synthetic tests exercise pending/BOTH paths.

Checks are under `checks/`; `verify.py` regenerates full records, variant checks and charts. Baseline initial test snapshot is named `acceptance_frozen.py` to avoid pytest collecting artifact tests with the live file’s module name. Original hashes.txt records the original filename before this non-content rename. Live tests gained trace/validation/plot regressions afterwards. Final comparison retains the real baseline failure, without xfail.

All records are deliberately unconfirmed/None. MergeDecision is scoped and not a general DecisionStep implementation. Warning scoring and table/DataFrame adapters remain deferred.
