# Kline family implementation comparison

Selected: `python_pro/chanlab/`, copied identically into the two live modules in
`src/chanlab/`. It satisfies the float-field contract with complete public type
annotations, indexing overloads and the review corrections below.

| Check | Frozen baseline | Selected Python Pro continuation + review |
| --- | --- | --- |
| Original independent acceptance suite | 109 passed after missing-column diagnostic correction | 109 passed |
| Final identical acceptance suite | 110 passed, 4 failed | 114 passed |
| Full 10,060-row numeric/UTC/context round trip | Passed | Passed |
| Unsupported Decimal/Fraction inputs | Accepted; may not reload through float CSV | Rejected |
| Integer not exactly representable as float | Accepted; could change on CSV reload | Rejected; exact large integers remain valid |
| Hardlinked data/context output files | Can overwrite raw export | Rejected before opening output |
| Strict mypy | One missing local `bars` annotation | Passed for both selected modules |
| Index typing | Union return annotation | Overloads distinguish integer access from tuple slices |
| Structure | Two modules; inline CSV parsing and dynamic numeric construction | Two modules; typed parsing helper and explicit numeric arguments |
| Readability | Shorter, less documentation | More explicit types/docstrings; slightly longer |
| Runtime dependencies | Standard library | Standard library |

Final active regression suite: **165 passed**, comprising the 51 unchanged ChanTable
cases and 114 Kline-family cases. Ruff and Black checks pass. New-module statement
coverage: **93%**, 194 statements and 13 missed. Full outputs, commands/import paths
and diagnostic failures are retained under `checks/`.

The baseline was authored without reading Python Pro, tested, then frozen before
the exact skill invocation was recorded and read. The same author continued with
Python Pro1.1.0; root and an independent reviewer subsequently added regressions
and corrections. This is an incremental engineering comparison, not evidence that
the skill alone caused the differences. No performance benchmark was run.

The original truncated-row diagnostic failure and final four baseline failures are
retained rather than hidden or marked expected in the acceptance suite. The baseline
is evidence, not the deployed selection. Both variants ran exactly the same final
tests in separate subprocesses with module-import paths verified.

Only raw Kline records and CSV/context functions were added. ChanTable integration
methods, DataFrames, plotting, indicators and feature detection remain deferred.
Exports normalize ISO/float spelling while preserving values and UTC instants;
they do not reproduce the 41-column master or its feature columns. The user released
the source handoff; provider start-label interpretation remains unverified evidence,
and no timestamp shift or volume rescaling was inferred.

Skill: `mas/skills/python-pro/SKILL.md`, version1.1.0, upstream commit
`078a25cc5bfd8011459be7b91d004e900c1d02d3`.
Exact request: `python-pro-request.txt` and
[the execution task](../../../mas/tasks/20261108-memo013-execution.md).
