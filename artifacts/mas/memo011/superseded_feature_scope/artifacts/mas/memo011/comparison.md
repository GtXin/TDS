# ChanTable implementation comparison
| Area | 001.d baseline | 001.e Python Pro continuation |
|---|---|---|
| Same full input | 10,060 rows, 41 columns | Same |
| Common CSV tests | 18 passed | 18 passed |
| Authoritative merged mapping test | Expected failure: no feature records | Passed |
| Domain support | Kline/KlineTSeries and CSV view | Adds eight feature record/series pairs and raw interval/event adapters |
| Typing | Unannotated APIs | Strict mypy passes across live source; generic dynamic feature registry still uses Any |
| Runtime dependencies | Standard library | Standard library |
| Structure | One CSV/domain module | Domain modules plus data adapter; more validation and complexity |
| Validation | CSV checks | 31 total tests passed, 1 expected baseline failure; measured source coverage91%; Ruff/Black/strict mypy passed |

Baseline: `baseline/chan_table.py`. Skill snapshot: `python_pro/chanlab/`. Shared tests: repository `tests/`. Exact skill requests and commands: `../../../mas/tasks/20261108-memo011-execution.md`.

Python Pro1.1.0 was read after baseline source was preserved but before baseline testing and initial request logging. The request was subsequently preserved and followup requests logged. This is an iterative comparison, not a controlled measure of the skill’s effect. Added functionality also explains code differences.

Limits: source bar-start labeling is unconfirmed; CSV import restores the derived view, not authoritative feature objects. Detection factories, selected-rule completeness/strength checks, DataFrame/plot conveniences and DecisionStep remain deferred. The synchronous CSV API was retained for the same-interface comparison. Rule-dependent Zhongshu/Zoushi source qualification remains permissive and must be tightened when rules are selected. Real CC features remain NA; manually constructed test records exercise mappings. Coverage above applies to discovered domain modules; the thin data adapter is not included in that report.
