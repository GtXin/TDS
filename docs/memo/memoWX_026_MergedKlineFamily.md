# MergedKline family implementation plan
## 000 — Scope
Implement the `MergedKline` and `MergedKlineSeries` feature interfaces from memo009 sections001.b–001.e and002.d–002.e.[1] Use memo015 sections001 and002.a–002.d for inclusion rules, source mapping, helper contracts and control flow.[2] Follow memo013’s process: baseline implementation, Python Pro continuation, common-test comparison, selected-code verification and separate plotting results.[3] **Status: core implementation, baseline/continuation comparison and plotting completed on2026-11-09.** ChanTable/DataFrame adapters, confirmation rules and dual-path warning scoring remain deferred. Section001 retains the execution plan; sections002–003 record the delivered scope and actual interfaces.
## 001 — Implementation plan
Reuse memo013’s implemented `Kline`/`KlineTSeries`, raw CSV loader and existing master/context in `samples/chan_table/`; no new raw-data preparation is needed. Preserve the original files, source labels and volume units. Before execution, record the exact input/configuration/rule version, allowed changes and acceptance checks in a task under `mas/tasks/`.
### 001.a — Implement the MergedKline family
1. **Set the interface contract.** Use the complete member/method inventory in003, including trace, explanation and plotting. Resolve the open contracts in the Appendix before implementing dependent interfaces; retain explicitly deferred integrations in the inventory rather than silently dropping them.
2. **Implement the immutable record.** Store memo009’s eight fields and validate automatically. Keep local record checks separate from owning-series checks against the exact raw source. Integer IDs are result-scoped; `MK12` is a display label, not a stored ID or source index.
3. **Implement the immutable series.** Retain the original `KlineTSeries` object, ordered record tuple, immutable configuration, versioned rule reference, full trace and per-record trace indices. Add sequence operations, ID lookup and validation with the behavior in003.a.
4. **Implement memo015’s six helpers.** Preserve their preconditions and ownership boundaries as mapped in003.b. Mutable work units remain private to calculation; saved records copy/freeze their fields.
5. **Implement the sequential factory.** `derive_from(source_series, config, rule_tree_ref)` validates raw input, initializes the first work unit, compares each next raw bar with the current merged interval, then absorbs or saves/starts a new unit. The main loop owns `i`, `n`, ID assignment, result appends and EOF save. Absorption advances only `i`; starting a new unit advances `i` and `n`.
6. **Implement explicit initialization behavior.** Apply initialization only to inclusion with unresolved direction. `UP`/`DOWN` set the current direction then absorb the same candidate. `OUTER` takes the outer envelope and retains None. `BOTH` copies independent mutable states and evaluates both complete paths, retaining the upward-initialized main output. `UNSET` stops before consuming the ambiguous candidate and preserves a pending outcome. No default is selected; settle the factory’s return contract without disguising pending/dual results as an ordinary complete series.
7. **Validate completed results.** Require nonempty output; unique integer IDs; finite ordered prices; valid directions; and continuous, nonoverlapping half-open source ranges covering the complete raw input. Reject inclusion between adjacent results, including equal boundaries. Allow nonadjacent inclusion. A one-record result passes the empty adjacent-pair check.
8. **Provide source-grounded explanations.** Record all executed decisions, including those producing no saved record. Map each result position to valid trace indices; explain rules, input evidence, direction changes, merges and source coverage using the exact rule version. DecisionStep’s schema remains unresolved; do not substitute fabricated traces or describe this interface as complete before agreement and verification.
9. **Preserve the display/source distinction.** Place a result at `source_start` and the first raw member’s timestamp. Preserve every raw member through `[source_start, source_stop)`; neither placement nor EOF establishes confirmation time.
10. **Keep components separate.** Proposed algorithm location: `src/chanlab/algo/merged_kline.py`; proposed renderer: `src/chanlab/visualization/merged_kline_plot.py`. Keep file/table/DataFrame adapters outside the algorithm. ChanTable interchange and DataFrame conversion remain explicit later integrations, as in memo013; later Chan detectors are outside this family.
11. **Add the plotting extension.** After selecting the core implementation, implement `plot(**options)` through a separate Plotly helper, following the Appendix. Preserve the frozen core comparison and record plotting checks separately in002.f, as memo013 does.
### 001.b — Repeat the core implementation using Python Pro
1. Complete the baseline against the agreed core contract and common tests; freeze its source, checks and hashes under `artifacts/mas/merged-kline-family/baseline/` before the continuation.
2. Record the exact invocation request verbatim in the execution task; read `mas/skills/python-pro/SKILL.md` and record its actual source/version.[4]
3. Repeat001.a’s core scope with identical public interfaces, algorithm options, fixtures, dataset and acceptance tests. Preserve the continuation separately under `artifacts/mas/merged-kline-family/python_pro/`.
4. Record prior skill exposure and later corrections. This is the same sequential engineering comparison used in013; do not claim the author has never read the skill or attribute differences solely to it.
### 001.c — Compare and select the core implementation
1. Run both frozen variants against the same final suite in isolated processes; verify which source each process imports. Retain failures and intermediate diagnostics rather than hiding baseline defects.
2. Compare memo009 interface coverage, memo015 rule compliance, source identity/ranges, immutable state, initialization/pending/dual-path handling, trace/explanation, validation errors, typing, readability and dependencies.
3. Save the comparison, actual commands/results and snapshot hashes under `artifacts/mas/merged-kline-family/`. Select shared source with explicit reasons and identify review corrections separately.
4. Run the selected version with the complete existing dataset and each agreed configuration. Report actual raw/result counts and evidence; do not copy013’s historical test counts or infer correctness from a plausible reduction ratio.
### 001.d — Test the MergedKline family
1. **Records and series:** valid construction, automatic validation, invalid numeric/ID/index/direction values, frozen fields, nonempty output, exact source identity, integer/negative indexing, tuple slices, iteration and ID lookup including missing-ID `KeyError`.
2. **Rules:** both containment orientations, strict upward/downward transitions, equal highs/lows, complete equality, one-price bars and repeated inclusion. Reproduce015’s main example, all initialization examples and its sequential-processing counterexample.
3. **Initialization:** apply policy only when needed; check single-bar EOF and initial noninclusion without forced direction/forking. Check UNSET stops without consuming the candidate, OUTER retains None, and BOTH has independent paths with the upward main result. Warning assertions require an agreed metric/threshold.
4. **Source/result invariants:** reject gaps, overlaps, out-of-bounds ranges, incomplete coverage, duplicate IDs and adjacent inclusion. Accept nonadjacent inclusion and a single result. Confirm display placement remains at the first member after every absorption.
5. **Trace/explanation:** trace coverage of no-output branches, one trace-index tuple per result, in-bounds indices and explanations matching the recorded rule/source context. Check status/UTC confirmation against the agreed rules; EOF must not fabricate confirmation.
6. **Full data and preservation:** load the existing master/context through memo013’s loader; calculate without changing raw values, timestamps, metadata, source files or earlier snapshots. Save compact derived records and configuration/source/rule evidence as verification artifacts, not as a newly standardized interchange format.
7. **Quality checks:** run focused tests and the existing regression suite with `.venv/bin/python -m pytest`; run report-only Ruff. Following013’s selected-version checks, record strict mypy, Black check mode and coverage for the changed modules with actual commands and results. Do not edit unrelated files to satisfy tooling.
8. **Plotting:** verify selected intervals, source timestamps, range/ID hover data, optional raw volume, empty selections, missing optional dependency, no source mutation, Figure return and HTML export; inspect representative charts visually. Record this extension separately from the core comparison.
## 002 — Implementation notes and logs
### 002.a — Implement the MergedKline family → 001.a
Implemented immutable records, explicit configuration, complete/pending/dual outcomes, six helpers, sequential calculation, source/adjacency validation, sequence access, ID lookup and explanations in [merged_kline.py](../../src/chanlab/algo/merged_kline.py). Input uses the existing raw loader; raw objects and ChanTable implementation are unchanged. Execution contracts and evidence are in [the task](../../mas/tasks/20261109-memo026-execution.md).
### 002.b — Apply Python Pro → 001.b
Baseline passed23 initial tests before freezing. Python Pro1.1.0 was then read and applied as a typed continuation, adding scoped decision validation, complete executed-event mapping checks, documentation and formatting. The task preserves the exact invocation. Both source versions remain under [baseline](../../artifacts/mas/merged-kline-family/baseline/) and [python_pro](../../artifacts/mas/merged-kline-family/python_pro/). This was sequential work with prior skill exposure, not a blind comparison.
### 002.c — Compare and select → 001.c
Selected the continuation. On the same final24-case core suite: baseline23 passed/1 failed, selected24 passed. The baseline accepts a trace map that omits executed decisions; the selected version rejects it. Both variants were imported from their recorded snapshot paths in separate processes and checked against the full dataset. Plotting tests are separate from this core comparison. [Comparison](../../artifacts/mas/merged-kline-family/comparison.md); [variant checks and full-data verification](../../artifacts/mas/merged-kline-family/verification.json).
### 002.d — Test → 001.d
**26 focused tests and202 total regression tests pass.** The focused suite includes648 exhaustive three-bar sequences against an independent scalar oracle,015’s main/initialization/counterexample cases, invalid record/result/trace tests, source identity, immutability, plot alignment and missing-dependency behavior. Strict mypy, Black check and report-only Ruff pass for changed source/tests. Changed core/renderer statement coverage is277/278 lines, **99.64%**; it is not a proof of general correctness. [Checks and coverage](../../artifacts/mas/merged-kline-family/checks/).

The10,060-bar sample produces6,200 merged intervals and10,061 decision events for every explicit policy. It begins without ambiguous inclusion, so BOTH does not fork and UNSET does not stop on this sample; synthetic tests exercise those outcomes. Sample/context SHA-256 checks are unchanged. Generated compact records and exact rule/source context are in [verification artifacts](../../artifacts/mas/merged-kline-family/); they are not a standardized merged CSV API.
### 002.e — Handoff and remaining scope
The scoped implementation is ready for use with explicit configuration. All records retain `status="unconfirmed"` and `confirmed_at=None`; confirmation rules were not inferred. `MergeDecision` is a merge-specific trace and does not define the still-deferred general DecisionStep class. BOTH reports warning evaluation as `not_evaluated`. ChanTable interchange and DataFrame methods are not implemented, matching the plan’s deferred integration boundary. Next work: choose confirmation/warning rules or separately release table integration when needed.
### 002.f — Plotly implementation and samples
Added lazy `series.plot(...)` delegating to [merged_kline_plot.py](../../src/chanlab/visualization/merged_kline_plot.py). Uses the existing optional Plotly extra; no dependency manifest/lock changes. HTML and PNG samples show015’s10-bar→3-unit example and the last40 merged intervals from full data. Interval coordinates and raw candle/volume arrays were checked in tests; both PNGs were visually inspected for labels, placement and clipping. Initial sandbox Chrome export failed; export with broader execution permission succeeded. The real-data chart retains session gaps.
## 003 — Implemented MergedKline family interface
### 003.a — Records, configuration and outcomes
Import from `chanlab.algo.merged_kline`.

| Type / field | Implemented behavior |
|---|---|
| `MergedKline(id, low, high, direction, source_start, source_stop, status="unconfirmed", confirmed_at=None)` | Frozen validated record; direction is `"up"`, `"down"` or None. Nonnegative integer IDs/indices reject bool. Bounds must be finite and ordered; source range nonempty. Only unconfirmed/None is currently accepted. |
| `MergeConfig(initialization)` | Frozen required policy: `"UP"`, `"DOWN"`, `"BOTH"`, `"OUTER"`, `"UNSET"`. No default. |
| `MergedKlineSeries(source_series, klines, config, rule_tree_ref, trace, trace_by_point)` | Frozen complete result; normalizes record/trace containers to tuples and validates automatically. Retains exact raw object and a nonblank versioned rule reference supplied by caller. |
| `source_series`, `klines`, `config`, `rule_tree_ref` | Exact raw snapshot, nonempty record tuple, immutable policy and rule identifier. IDs are result-scoped and independent of tuple positions. |
| `trace` | Tuple of immutable `MergeDecision(rule, raw_index, before, candidate, after)` events. Work states retain raw identity, bounds, direction and source range. Candidate is None at initialization/EOF. |
| `trace_by_point` | One nonempty tuple per result position; all indices valid and every executed event covered. A boundary transition can explain both neighboring records. |
| `PendingMerge` | Frozen factory outcome holding source/config/rule reference, saved prefix, current/candidate, unconsumed `raw_index` and trace. It is not a complete series and has no plotting interface. |
| `DualMerge` | Frozen `main` upward-initialized series, `comparison` downward-initialized series, original `requested_config`, and `warning_evaluation="not_evaluated"`. Returned only when ambiguous startup actually requires a fork. |

| Method / operation | Implemented behavior |
|---|---|
| `bar.validate()` | Local field/order/direction and conservative status checks. |
| `series.validate()` | Source/records, unique IDs, complete contiguous source partition, adjacent noninclusion, trace source identity and complete mapping. Does not replay every price derivation or infer confirmation. |
| `MergedKlineSeries.derive_from(source_series, config, rule_tree_ref)` | Returns `MergedKlineSeries | PendingMerge | DualMerge`. Policies apply only at unresolved inclusion. EOF freezes the last record and validates complete results. |
| `len(series)`, `iter(series)` | Stored record count and chronological iteration. |
| `series[index]`, `series[start:stop:step]` | Record or tuple; normal Python indexing including negatives and empty slices. IDs/source/trace indices remain unchanged. |
| `series.get_by_id(feature_id)` | Resolve a nonnegative integer ID; absent valid ID raises `KeyError`. Invalid ID type/value raises `ValueError`. |
| `series.explain(point_index)` | Human-readable ID/range/direction/status, rule version and linked before/after events. Full candidate evidence is available in `trace`. |
| `series.plot(*, start=None, stop=None, volume=True, title=None)` | Return Plotly Figure through the renderer; bounds are merged-record positions. No automatic display/export. |
| `from_chan_table`, `to_chan_table`, `to_dataframe` | Still proposed by009 and explicitly deferred in026; not exposed as working methods. |

### 003.b — Helpers and adapter boundaries
`work_from_raw`, `has_inclusion`, `direction_between`, `merge_included`, `merge_outer_boundary` and `validate_merged_result` implement015’s contracts. Work records are immutable; merge functions return new work states. The main loop owns candidate consumption, IDs, appends and EOF. OUTER selection belongs to the caller; the outer helper checks unresolved direction and contiguous inclusion.

Input remains `chanlab.data.kline_csv.read_kline_csv`. No merged CSV/DataFrame interchange schema was added. Future ChanTable projection remains: memberships throughout `[source_start,source_stop)`, start at `source_start`, end at `source_stop-1`, direction at start; retain exact source/series/version context and NA versus computed-empty semantics. Existing ChanTable still rejects non-NA feature columns.
### 003.c — Runnable example
Run from the repository root with `PYTHONPATH=src .venv/bin/python`. This example was executed against the existing sample.
```python
from hashlib import sha256
from pathlib import Path
from chanlab.data.kline_csv import read_kline_csv
from chanlab.algo.merged_kline import (
    MergeConfig, MergedKlineSeries, PendingMerge, DualMerge,
)

folder = Path("samples/chan_table")
raw, context = read_kline_csv(
    next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv"))
)
rule_path = Path("docs/memo/memoWX_015_Chan_mergedkline.md")
rule_ref = "memo015:sha256:" + sha256(rule_path.read_bytes()).hexdigest()
outcome = MergedKlineSeries.derive_from(raw, MergeConfig("UP"), rule_ref)
if isinstance(outcome, PendingMerge):
    raise RuntimeError(f"Initialization required at raw[{outcome.raw_index}]")
series = outcome.main if isinstance(outcome, DualMerge) else outcome
series.validate()
assert series.source_series is raw
assert len(raw) == 10060 and len(series) == 6200
assert series[0].source_start == 0 and series[-1].source_stop == len(raw)
record = series.get_by_id(series[0].id)
members = raw[record.source_start:record.source_stop]
assert members[0].timestamp == raw[record.source_start].timestamp
print(series.explain(0))
```
### 003.d — Plotting and sample charts
With `series` from003.c, install the existing optional extra if needed (`uv sync --extra plot`), then:
```python
fig = series.plot(start=-40, volume=True, title="Last 40 merged intervals")
fig.write_html("artifacts/merged-kline/example.html", include_plotlyjs=True)
```
Slicing selects already-calculated merged records and the corresponding raw extent; it does not recompute initialization on a truncated input. Empty selections raise `ValueError`. Missing Plotly gives the installation instruction. Raw candles/volume remain unchanged; merged bounds are vertical range marks at first-member timestamps with IDs/source ranges/direction/status on hover.

| Sample | Interactive HTML | Inspected PNG |
|---|---|---|
| Memo015 worked example | [Open](../../artifacts/merged-kline/worked-example.html) | [Preview](../../artifacts/merged-kline/worked-example.png) |
| Last40 merged intervals | [Open](../../artifacts/merged-kline/cc-last40-merged.html) | [Preview](../../artifacts/merged-kline/cc-last40-merged.png) |

## Appendix — Contracts and reproduction
1. **Initialization:** explicit immutable policy; no project default. BOTH/UNSET return special outcomes only if ambiguous inclusion is encountered.
2. **Confirmation:** only unconfirmed/None supported. EOF completion and first-member display placement are not confirmation evidence.
3. **Trace:** scoped MergeDecision retains rule and before/candidate/after evidence. General DecisionStep remains deferred; callers should not treat this schema as a cross-feature standard.
4. **Warning:** BOTH retains both full paths and original request; source-aware difference scoring/threshold/delivery remain unimplemented and explicitly unevaluated.
5. **Adapters:** table registration/conflicts and DataFrame schema remain separate work. No raw/master schema was changed.
6. **Plotting:** existing optional Plotly extra; UTC/session gaps retained; raw volume only. PNG export uses temporary Kaleido/local Chrome tooling, not a new runtime requirement.
7. **Reproduction:** [verify.py](../../artifacts/mas/merged-kline-family/verify.py) reruns isolated comparisons, full input checks and chart exports. Run with `PYTHONPATH=src` in an environment containing pytest/Plotly; PNG export additionally needs Kaleido/Chrome. Tooling/check commands and limitations are in [the task](../../mas/tasks/20261109-memo026-execution.md).

## References
1. [Memo009 — Design pattern for Chan features](memoWX_009_designPatternForChanFeatures.md), sections001.b–001.e,002.d–002.e and002.u.
2. [Memo015 — Chan_mergedkline](memoWX_015_Chan_mergedkline.md), sections001 and002.a–002.d.
3. [Memo013 — Kline family implementation](memoWX_013_klineFamily.md), sections001–003 and Plotly Appendix; [core execution task](../../mas/tasks/20261108-memo013-execution.md) and [comparison](../../artifacts/mas/kline-family/comparison.md).
4. [Memo012 — Python Pro skill](memoWX_012_Skill_python_pro.md).
