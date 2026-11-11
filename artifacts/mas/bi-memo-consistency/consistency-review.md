# Memo020 active-section consistency review

Status: initial audit of current 000–005 complete; integrated revision pending. This reviewer writes only this file. No memo, production, test, task, memory or event-log changes.

## Scope and retained meaning

The active algorithm is a single forward rolling route with immutable submitted R, an optional unfinished Bi002, stage-specific equality, ordinary-failure continuation and normal EOF. Archived appendices describe earlier protocols and must not be read as active instructions. The current 004 original note/prompt is the basis for the traversal; its original wording/numbering should survive a display-only formatting repair.

The reduced predicates, 19-bar and 21-bar states, shared endpoint rotation, independent six-condition geometry check, and normal open-tail EOF are mutually coherent. I found no need to add backtracking, new route selection, a scan-stop rule, new domain classes, or production API synchronization.

## Actual interface gaps

### 1. Returned output is not yet explicitly the accepted continuation state

Current `process(source, previous_state=None)` reads previous_state and its source context, but its final return is an unnamed collection of display/result values. It does not define the exact packing needed for a caller to pass the output back as previous_state. In particular Bi001S/E are not named unambiguously in that return. A reader can infer a reconstruction, but the document should not require that inference.

Minimal fix: define one immutable ordinary algorithm state, or explicitly `report.state`, that includes R endpoint values, optional Bi002, Bi001S, Bi001E=None, next_position, source_context, algorithm/rule revision and retained comparison evidence. Specify exactly which value is the next previous_state. Keep EOF status/unresolved ranges as ordinary output data; no public class or memo009 member expansion is required.

### 2. “待定起点” has two meanings

Before a first pair exists, Bi001S is the pending initial start. Once a cache exists, Bi001S equals that cache's endpoint B and is the next reverse search's start. Calling both merely “待定起点” makes the return and resume behavior ambiguous.

Minimal fix: preserve S in the state unconditionally. A human-facing `initial_pending_start` means S only when Bi002 is absent; otherwise S is explicitly the next-start alias of Bi002's end. A singleton S is never an additional stroke. For the 19-bar final state use sourceFX positions: R=((4,7),), cache=(7,8), S=8, E=None, next_position=9.

### 3. Persistent EOF evidence can grow without new work

The main process preserves existing evidence and then executes “记录尚无合格首笔” again at each EOF. Without a distinction between persistent comparison evidence and an EOF report field, repeatedly processing the identical input can keep appending the same terminal note despite reading no F.

Minimal fix: EOF descriptions are current report status, not duplicate persistent per-F events. If no new complete FX is read, leave the comparison-evidence prefix unchanged. R/cache/S/cursor are unchanged; an extended merged suffix with no new FX may still update source_context and unresolved range normally. This is not a reason to fail or loop at EOF.

## Precise continuation contract

The following is sufficient as a document contract, without imposing a new public API:

- A successful return is from a normally completed finite scan, so its next_position equals the saved complete-FX length M_old. Preserve old raw, merged and complete-FX lengths and full previous snapshot content (or an equivalent immutable source snapshot reference) plus stable source/config/rule context.
- Validate the new full source, then compare the ENTIRE saved raw/merged/FX prefixes, including previous merged bars after the last complete fractal, not just endpoint or cursor-linked records. Current lengths may grow but may not shrink. Stable source/config/rule semantics must be compatible; new object identity itself is not an error. New snapshot extent metadata naturally changes when appending and should not be confused with changing algorithm rules.
- Require a trusted, unmodified state emitted by the same algorithm revision. A geometry-only state check does not reconstruct the initial S record-extreme history needed by the first-pair shortcut. Do not authorize arbitrary S/cursor assembly merely because its indices are in range.
- Restore R/cache/S/E and evidence values; do not clear R or call initial setup again. If S is still None and cache absent, R is empty and the first arriving complete FX initializes S before the ordinary loop. Otherwise continue at M_old. No new FX means no per-F decision is repeated.
- Freeze the checkpoint's outer R/evidence collections as well as individual endpoint values. Resume into fresh mutable working containers, preserving immutable endpoint tuples, so append operations neither mutate the trusted previous checkpoint nor mistakenly append to a tuple. An unsuccessful later call must leave the last successful checkpoint intact. This is inline packing/unpacking; no eighth helper is needed.
- At EOF, validate R plus optional cache directly against001, ensure the old R value prefix is retained, check E=None and next_position=M_new, and return an explicit reusable immutable state. Unresolved ranges are recomputed for the new N; they are not blindly reused from the preceding batch.
- A changed derived prefix is an input-revision problem outside this append-only continuation contract. Raw append alone does not guarantee an unchanged merged/fractal prefix. Reject incompatible reuse rather than silently resetting or revising final R.

## Output assertions and costs

R_before is an immutable copy of the entry R endpoint values. Checking that the current R has the same full prefix proves this call did not rewrite earlier records; it does not create a submission/confirmation policy or prove future market completion. To make truncation rejection explicit, require current len(R) at least len(R_before), then compare every old position.

The independent output checker remains based on the original six conditions and shared-endpoint chain, not reduced predicates. SourceFX positions, merged centers and raw anchors remain separate; raw anchor selection stays upstream. All active helpers can remain the existing seven.

Full source-prefix validation and full historical output verification may cost work even in a batch with no new FX; do not claim constant-cost or “only new F” processing for the entire call. Persistent comparison evidence and R may grow with the processed history even though only two working slots are needed. Total storage is not O(1), and multi-batch validation costs need separate accounting. These are documentation boundaries, not reasons to add an unrequested bounded cache or discard evidence.

## Sections without a real contradiction

- 000's scope statement is broad but compatible with this documentation task.
- 001's pair/chain definition and old-stroke distance remain unchanged; source quotations versus the derived lower-interval inequality are already distinguished.
- 002.a/b and003 correctly separate geometric final-R validity from an unproved canonical/permanent-confirmation theorem and future completion.
- 004 permits an unfinished last stroke and does not require full finite-input coverage; this agrees with the open-tail examples.
- Empty005 does not itself break the algorithm contract; do not fill it with unrelated work merely to complete the headings.

Awaiting root's integrated drafts for exact return/restore/format review. No numerical or production model was executed by this reviewer.

## Final integrated revision review

PASS. Read the complete active draft and latest section-002a/b/c/d/003/004/005 files. Confirmed the assembled `draft-memo.md` contains those exact current sections. The original001 definition block and entire AppendixA-through-References tail remain text-identical to the active pre-edit memo. No draft or memo was edited by this reviewer.

### Resolved gaps

1. **One reusable output:** process returns the explicitly defined immutable Q and receives that exact record as previous_state. Q includes R, optional Bi002, S/E, next_position, current complete source context, stable evidence and current unresolved ranges. No public class, extra domain member or production resume API is claimed.
2. **Two meanings of S:** the role is explicit before/after a first cache, and Q always preserves S. A cached endpoint/next-start is not another stroke. The19-bar example correctly maps the final R/cache to sourceFX positions, with S=FX8 and next_position9.
3. **Whole previous input:** the guard covers full previous raw/merged/complete-FX prefixes, source/rule/config/precision context and lengths. A compatible new immutable source object is allowed; shortened/changed history is not. Newly completed FX at the old last merged position are read by saved FX cursor, not filtered by old N.
4. **Immutable checkpoint versus work containers:** resume explicitly copies endpoint/scalar values and restores R/evidence into new appendable working sequences. The old Q is not mutated; cache updates create new endpoint values. R_before has both a length and exact value-prefix assertion.
5. **Idempotent EOF evidence:** each complete FX has exactly one persistent initialization/comparison event. EOF is report information and does not append another persistent event. With no new FX, selection state and decision evidence stay unchanged; new merged suffix data may still update full context and unresolved range. Identical source+Q calls return equal contents rather than growing EOF notes.
6. **Stable event content:** Q's evidence contract now excludes batch IDs, call timestamps, total batch N and source-object identity. Per-F events contain stable source positions, comparisons and actions; full current snapshot context is stored separately. Therefore the stated full-versus-split evidence equality is meaningful, not just equality of selected endpoint pairs.
7. **Self-contained validation:** the final helper pseudocode uses source/Q-qualified names in its terminal checks, removing the formerly implicit M/S/R local bindings. It independently checks all original001 conditions, chain relations, final cursor, pending semantics, context/ranges/evidence, and entry R preservation. These assertions do not add a selection or confirmation policy.

### Why the split-run claim is sound under this contract

At the same consumed FX position, initial or restored working state has identical R/cache/S/E and cursor. A next transition depends only on that state, the next FX and the unchanged price interval ending at that FX center. Both complete-source validation and prefix compatibility ensure those inputs are the same; no future boundary or batch identifier affects selection. The deterministic transition and stable event are therefore identical. Inductively all new FX produce the same selection state and evidence as one shot. EOF only validates/packages; it does not submit the cache or create an event. At a matching final source snapshot, recomputed unresolved ranges and whole source context also match.

This proof is conditional on trusted same-revision state, full unchanged prefixes and complete chronological FX. It does not authorize arbitrary geometric checkpoints, raw-append assumptions, or source revisions. It does not prove original-theory uniqueness, eventual completion or full-market coverage.

### Examples, scope and format

The staged N=2/3/11/12/15/19/23 table is consistent: zero FX then one initial FX; no new FX at11→12 preserves all decisions but extends the unresolved tail; the new bottomM18 at19→23 is read despite center18<oldN19; topM21 extends only the cache, preserving submitted FX4→FX7. The equality and21-bar open-tail examples retain the prior choice policy. Geometric pair checks and distinct sourceFX/merged/raw coordinates remain unchanged.

004's original numbered note is presented in one text fence and the collaboration prompt as a continuous quotation. Original note wording/numbering is kept; active text explains rather than overwrites it. The current single-tree format outside004 is retained except for necessary output/resume consistency changes. 000 now identifies active versus historical scope, and005 records actual production/revision/confirmation boundaries rather than pretending the current code already implements Q.

No further contract issue found. Root owns the finite Q replay, full/split comparisons, checkpoint trust/corruption probes, live Obsidian review, actual backed-up memo edit, and final preservation/link checks. This reviewer executed only read-only draft comparisons and wrote this review artifact.

## Concurrent implementation update: final005 correction

PASS on the revised005 first bullet. While root's pre-edit guard was checking protected files, another chat updated memo028 and the production Bi implementation. Read the current028 summary and `src/chanlab/algo/bi.py`: the latter now documents the rolling scan, keeps committed/cache values separate, and accepts a prior report for guarded continuation. Earlier review references to production still being the archived candidate protocol describe the source snapshot inspected at that earlier time and are superseded by this observation.

The new005 wording accurately acknowledges existing `BiSeries.scan` rolling/prefix continuation while requiring a separate comparison of this memo's newly precise Q packaging, initialization evidence and full-output validation against the actual report. It does not claim that the current production API is literally Q or that those details were already synchronized. The source link resolves. No implementation quality/test result was independently rerun or adopted as this reviewer's own verification; only the current source/status boundary was inspected. No other re-review or production change is required for this correction.
