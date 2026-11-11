# Distance-option contract review

Status: PASS — final integrated draft reviewed, with the initial checklist retained below.

## Required normalized contract

* Exactly two modes: `strong → g=4`, `weak → g=3`; distance remains one of the six conditions, with mutually exclusive alternatives. g is derived, not a separate configurable threshold.
* Fresh omitted/None mode selects strong. On continuation, omitted/None mode inherits the mode recorded in the prior Q. Explicitly selecting the same mode is allowed; selecting the other mode is rejected, including when R/cache are empty. Different distance choices can change prior decisions, not merely validate the final surviving pairs differently.
* Reject unknown mode values, unsupported/old Q with missing mode, malformed normalized mode, and mode/g disagreement. Do not guess a legacy Q mode from observed endpoint distances or silently treat a missing mode as fresh strong. Any compatibility/migration policy would be a separate decision.
* Every valid fresh output, including zero FX, stores normalized mode and derived g in source_context. Repeated calls and all split/resume cases preserve them. New mode metadata must be distinguished from upstream source identity; upstream raw/merged/FX prefix compatibility remains unchanged.

## Integration points

1. 000/001: state six conditions and define the two alternatives; fix weak-mode prose. At gap3, two three-bar windows are disjoint and adjacent; no merged bar lies outside both windows between them. The independent-bar language applies only to strong mode.
2. 002.a: process signature, Q/source_context table, initial/resume entry, input error branch, first/reverse checks, and independent output verification must consistently use the resolved g.
3. 002.b: label the main trace and existing evidence as strong/default where applicable. Explain any unchanged outcomes under weak by the other failed condition, rather than claiming gap3 itself still fails. Add one valid difference fixture, and mode-specific split/zero/single-FX/idempotence coverage.
4. 002.c: update eight-helper count/signatures. `_resolve_distance_mode` must validate all mode information it reads from Q; `_validate_input` still checks normal provenance and state. First/reverse helpers receive the resolved g; full output validation independently uses Q's normalized mode/g.
5. 002.d: main process resolves mode once; all branches and Q construction use that single value. Replace active hardcoded4 checks in first/reverse/full validation. Distance evidence must identify actual gap and the threshold used, stably across batches.
6. 003: reduced checks remain equivalent per fixed mode. Extension reuses a prefix qualified under the same g; because F is later than B, its distance cannot shrink. No mode switch is allowed while reusing that proof. Distinguish strong trace from optional weak differences, and retain safety/liveness limitations.
7. 005: distance option is a document contract, not proof of production synchronization. Original004 note/prompt, appendices and references remain verbatim; active introductory wording can identify historical/default strong-only material without editing it.

## Error and compatibility details

Resolving mode before full source validation is acceptable only if it reads Q defensively and then full validation still runs before state reuse. An unsupported previous Q is an input/compatibility error, never a normal candidate failure or fresh initialization. Persisting g redundantly is safe only with equality checked against the mode-derived value. The two-mode change must not relax raw/merged/FX prefix preservation, R immutability, cache updates, ties, EOF, or resumed cursor semantics.

Use `previous_state is None` semantics: an empty/malformed Q is not an omitted state. Output verification must also establish that Q's stored mode/g equal this call's resolved mode/g, rather than only checking mutual consistency of the stored fields. Weak/3 is this memo's selectable threshold; neither author attribution nor equivalence to the author's new-pen condition or CC's `bi_4k` follows from the numeric threshold alone. Any active version-one independent-bar wording and the source-attribution sentence must be explicitly scoped to strong mode.

No memo, source, test, log, memory, dataset, or other review artifact was modified.

## Final integrated-draft verdict

Read `draft-memo.md` active000–005 and all changed001/002.a–d/003/005 fragments. PASS; no required contract edits remain.

* `process(source, distance_mode=None, previous_state=None)` and all eight helper contracts agree with their pseudocode calls. Mode resolution occurs after input validation and before any new FX is read. Missing/malformed Q is rejected rather than treated as a fresh run.
* Fresh default, inherited resume mode, explicit same-mode resume, explicit change rejection, invalid values and old missing-mode Q have unambiguous behavior. The derived g is never independently configurable. Zero/single-FX states also retain the mode in Q's context.
* First and reverse checks receive min_gap; extension explicitly requires a same-mode legal old cache and keeps its unchanged suffix-only predicate. Final validation receives this call's resolved mode/g and checks the Q fields against both the call and fixed mapping before independently checking all original conditions.
* The six-condition definition has one distance element with two alternatives. Strong-only independent-bar language is scoped, and weak's adjacent disjoint windows are explained correctly. Project weak is not equated with the author's new-pen rule or CC strong behavior.
* Main/default and split examples are labeled strong; the gap3 difference fixture, weak-specific failure-reason distinction and cross-mode Q inequality are consistent with the independent numeric review. Same-mode continuation reasoning remains valid because the mode is part of stable context and evidence records the actual threshold.
* R immutability, one-cache behavior, ties, traversal, open EOF, cursor/source-prefix rules and complexity qualification remain unchanged. 005 expressly treats production distance support as pending and does not claim the previously proven lock was cured.

This is a static contract review, not an extra numerical rerun or production test. Root owns saved-byte/protected-section/hash/link checks and the event log. Only this owned report was updated.
