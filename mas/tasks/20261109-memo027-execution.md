# Task
- **ID:** 20261109-memo027-execution
- **Goal:** Execute027: two-class geometric fractal detector, comparison, table/DataFrame integration and plot.
- **Inputs:** memos009/010/011/012/013/015/019/026/027; existing full sample/context; current immutable merged source.
- **Allowed changes:** new fenxing core/adapter/plot/tests; ChanTable and merged adapter interoperability;027, memory/log and artifacts/mas/fenxing-family. Preserve source datasets and existing work.019 read-only: its002.b–d are now populated and have been reviewed.
- **Acceptance checks:**019 main example/FIRST/LAST/revision; full output/trace validator; exact source and immutable state; common frozen-variant tests in isolated processes; table roundtrip preserving upstream identity and other registrations; compact DataFrame and representative plots; regression, Ruff, strict mypy, Black, >90% changed-module statement coverage; full-data checks and hashes.
- **Assignment:** Codex directly; no delegation.
- **Status:** done

# Frozen implementation premises
019 currently contains completed002.b–d (earlier027 statement was stale). Adopt anchor_tie FIRST(default)/LAST, exactly one evidence mapping per full window or one insufficient-window event; strict source/geometry/output completeness validation; ID uniqueness, IDs allocated from0 by derive_from. No confirmation or pen endpoint selection. Core owns8+6 stored members. Mapping trace is local, not a general DecisionStep class. Table integration preserves v1 merged metadata and adds a versioned fractal payload referencing an exact registered merged key/version. First registration per class supplies visible columns; all registrations remain scoped.

# Skill invocation
Exact user request: `good execute 027 plan as you did for 026 `
Execution instruction for continuation: `Apply mas/skills/python-pro/SKILL.md to repeat the memo027 core with identical public interfaces, algorithm options, fixtures, dataset and acceptance tests; preserve the baseline and record actual checks.`
Python Pro1.1.0 (Jeffallan) and type-system/testing references read. Disclosure: skill was read before baseline in this turn; baseline is not a clean unexposed control. Preserve sequential revisions; no causal skill claim.

# Result and handoff
- **Outcome:** Two-class core, frozen sequential comparison, table/DataFrame/plot extensions and all acceptance checks completed.
- **Evidence:** artifacts/mas/fenxing-family/.
- **Blockers:** none identified.
- **Next action:** User review of027; confirmation/pen/incremental rules remain outside scope.

# Actual results and commands
- `PYTHONPATH=src .venv/bin/python artifacts/mas/fenxing-family/compare.py`: isolated explicit frozen imports; baseline55passed/1failed, continuation56passed. Failed boolean-vs-integer event check retained. Frozen core snapshot SHA256 in comparison.json; active extension fingerprints in selected-hashes.json.
- `PYTHONPATH=src .venv/bin/python -m pytest tests/test_fenxing.py tests/test_fenxing_table_plot.py tests/test_merged_kline_table.py -q`:86passed. Independent randomized four-comparison oracle60synthetic sequences,019 example, overlap/empty/ties/revision, bad records/trace/source and table/plot checks included.
- `PYTHONPATH=src:/tmp/tds-memo026-tools/lib/python3.11/site-packages .venv/bin/python -m coverage run --data-file=artifacts/mas/fenxing-family/.coverage-final -m pytest tests -q`: full regression; exact final result in regression.txt, scoped coverage.json/coverage.txt.
- `MYPYPATH=src /tmp/tds-memo026-tools/bin/python -m mypy --strict --explicit-package-bases --follow-imports=silent` on fenxing.py,chan_table.py,fenxing_table.py,feature_table.py,merged_kline_table.py,fenxing_plot.py:6modules clean (mypy.txt).
- `.venv/bin/python -m ruff check` and temporary tool Python `-m black --check` on those6modules plus2newtests:pass (ruff.txt/black.txt). Ruff import/literal fixes and Black formatting applied only scoped active files; no dependencies changed.
- `PYTHONPATH=src:/tmp/tds-memo026-tools/lib/python3.11/site-packages .venv/bin/python artifacts/mas/fenxing-family/verify_full.py`: full five explicit upstream configurations, FIRST/LAST, independent complete-path oracle, protected source hashes, detached CSV records and table/context roundtrip.10,060raw/6,200merged/3,027fractals(1,514top/1,513bottom),542tie-anchor differences. All five configs produce complete result on this input; no initialization ambiguity was triggered. Counts do not prove alternative policies equivalent in general.
- Figures: artifacts/fenxing/cc-last80{,-china,-calendar}.{html,png}, worked-example.{html,png};4PNGs visually inspected and copied byte-for-byte into027 sibling folder. Worked-example uses `PYTHONPATH=src:tests:/tmp/tds-memo026-tools/lib/python3.11/site-packages .venv/bin/python` with `from test_fenxing import derive; f=derive().plot(volume=False,...); f.write_image(...)`.
- Changed existing ChanTable for mixed family validation/projection/persisted restoration; merged register delegates to mixed adapter. Existing merged metadata format and raw columns preserved. All other pre-existing dirty workspace files left alone; git diff includes prior work and is not an exclusive027 patch.

# Failures and corrections
Initial fixture raw1.low=1 did not generate019’s given merged input; corrected to3 (019 only specifies that raw high), retained initial failures. Root pytest initially collected archived test_fenxing.py twice; renamed archived snapshot to contract_tests.py, no tests suppressed. Initial mypy invocation lacked source/package-base flags; corrected then fixed two actual annotations/imports. Ruff/Black import, literal and noqa placement issues corrected. Plot view originally used absolute anchor x with a local source x axis; changed to anchor-start and regression assertions. PNG export first lacked Kaleido in repo venv, then local Chrome was sandbox-blocked; reused existing temporary tools and approved escalation for local renderer, no install/settings change. No auto-review rejection occurred.

# Scope and provenance
Confirmation remainsunconfirmed/None; trace is a local immutable mapping, not a new DecisionStep class. Pending/dual inputs rejected, not silently selected. Auto upstream key is <fx-key>:source when needed; a conflicting key errors. First registration per family supplies fixed CSV visible columns; all keys retain scoped maps. Source bar-start semantics remain unconfirmed. No algorithm code imported from CC. No speed benchmark or skill causality claim.

Final count clarification: `pytest tests -q` is386passed (regression.txt), while root `pytest -q` is420passed (repository-regression.txt, includes34existing artifact tests). Final coverage is542/556statements(97.48%) from the active tests directory. Earlier references to420 as the active suite are superseded.
