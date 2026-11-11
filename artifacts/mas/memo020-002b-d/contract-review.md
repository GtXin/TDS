# Memo020 002.b–d contract review

Status: final saved memo020 002.b–d reviewed. PASS. Saved block exactly matches the reviewed `sections.md`; complexity qualification is now applied. Root owns its independent byte/hash/link/model checks.

## Scope

Read-only review of memo020 002.a, memo019 002.b–d, memo009 Bi/BiSeries, actual Fenxing/FenxingSeries and the independent cached recursive reference. This review writes only this artifact. No memo, production, task, memory or event-log changes.

## Essential contracts

1. **Three coordinate systems.** A/B/F and route endpoint references are positions in the exact source FenxingSeries. Merged centers are `source_start + 1`, used for spacing and inclusive price extrema. Raw anchors are `anchor_raw_index`, used for mapping/display. Neither raw anchor distance nor distance between Fenxing record positions implements the old-stroke merged-bar gap.
2. **Input completeness and source identity.** Reuse the full existing FenxingSeries validator before short-input exits; validate complete merged/raw provenance without rerunning or modifying upstream transforms. A complete three-bar fractal is not a confirmed market endpoint. Upstream records currently require unconfirmed/None.
3. **Candidate family versus public series.** The current algorithm returns alternative connected routes plus blocked history and unresolved regions. The existing memo009 BiSeries contains one flat ordered route. Keep the research candidate-family result as ordinary internal data; do not concatenate alternatives into one series or invent public classes/fields. A later explicit projection can create one existing-format BiSeries per route with exactly memo009's eight record/six series members.
4. **Working state representation.** Specify whether the stored prefix is committed edge tuples or endpoint tuples. If it is committed edges, its final endpoint is current A; current A→B is separate and provisional. Advancing on a qualified reverse appends only the old A→B and changes the working pair to old B→F.
5. **Immutable postdecision alternatives.** An alternative stores the concrete opposite choice already made, exact input identity/rule context, immutable prefix checkpoint, A/B, stage and cursor after F. Restoration executes that recorded alternative; it must not re-enter the node that would generate the same choice again. Mutable path aliases would corrupt independent equal-price branches.
6. **Phase policy completeness.** SEEK_B forks take/decline valid first ends; a valid strict improvement in WAIT_REVERSE is mandatory; failed strict improvement blocks the branch; a valid equal end forks keep/replace; first qualified reverse is mandatory. These are the approved local policies represented by 002.a, not a claim to enumerate every subset satisfying only the six pair conditions.
7. **Terminal distinctions.** EOF with a valid working pair emits an EOF-provisional route with head/tail unresolved. EOF without B emits no stroke. Mandatory-extension failure preserves diagnostics/history only, not an EOF route covering later prices. Trailing incomplete extrema can exceed a last selected endpoint; they remain outside the selected-center coverage interval.
8. **Result validation scope.** Rechecking every edge and shared endpoint establishes soundness. It does not establish that every policy branch was visited. Completeness needs correct worklist exhaustion/restoration and separate reference comparisons. Grouped uniqueness applies only after endpoint-sequence deduplication, with the same source and exact first/last endpoint positions, under the explicit phase policies.
9. **Trace and failure behavior.** Record actual comparisons, reasons, choices and restores. Invalid input, stale-source restore, invalid cursor/phase/endpoint references, malformed action or broken prefix/working connection must raise an error, not silently drop a branch. Do not infer completion timestamps from anchor times or the data end.
10. **Complexity.** Finite cursor progress and finite choice branching imply termination. Number of states/routes can be exponential; copying snapshots and direct range scans add per-state costs. This is a finite transparent reference algorithm, not an O(N) production detector.

## Source pointers

- `docs/memo/memoWX_009_designPatternForChanFeatures.md`, 002.h–i: exact eight-field Bi and six-field BiSeries; endpoint indices are FenxingSeries positions.
- `src/chanlab/algo/fenxing.py`: Fenxing eight fields, unconfirmed/None constraint; derive_from stores three-merged windows `[i-1,i+2)` and keeps every complete geometric candidate.
- `docs/memo/memoWX_019_Chan_fenxing.md`, 002.c–d: helper contracts, precise scope of validator, fixed source chain, no public extra classes.
- `artifacts/mas/bi-algorithm-study/cached-reference.py` and `.md`: independent recursive baseline for the stated phase rules, including deeper recovery and equal-price forks. This does not replace a full proof of equivalence to original Chan theory.

## Preservation note

The currently saved memo001 includes user-authored material outside 002.b–d, including an empty `7.` and two differently worded version-three passages. Those are outside this task; do not normalize or remove them as part of the algorithm-section edit.

## Draft c/d review

Read the full `sections-cd.md` and the helper-decomposed `pseudocode_model.py`/saved JSON. The model was inspected only; this reviewer did not execute a script that would overwrite root-owned artifacts.

The six helpers cleanly separate geometry, endpoint comparison, immutable branch capture, branch validation, terminal handling and emitted-route validation. The research `search(source)` returns ordinary candidate-family data and explicitly does not redefine the public BiSeries factory. Per-route later projection retains the exact existing eight/six field contracts.

| 002.a node | Pseudocode counterpart |
|---|---|
| 2.1 | source validation; reversed seed insertion; empty-input unresolved range |
| 2.2 | cursor-controlled read loop and EOF finish |
| 2.3 | B-is-None versus WAIT_REVERSE branch |
| 2.4 | initial pair check plus accept/decline-first-B branch |
| 2.5 | same-kind versus opposite-kind F dispatch |
| 2.6 | MORE mandatory update/block, EQUAL immutable alternative, LESS retention |
| 2.7 | first qualifying reverse appends old B to prefix and advances A/B |
| 2.8 | separate BLOCKED/EOF handlers; outer pending-stack restoration |
| 2.9 | full endpoint-sequence deduplication, validation and fixed-boundary grouping |

Checked failure behavior: invalid exact source/provenance is rejected before short-input return; illegal positions raise; ordinary pair failures return reasons; malformed stage/cursor/prefix/restoration raises; blocked causes are rechecked against the actual F and rejected A→F; EOF requires cursor=M; emitted routes must have matching provisional pair and unresolved ranges. No caller input or upstream anchor/status is changed.

The prose and pseudocode explicitly distinguish geometric/result soundness from complete execution of the phase-selection protocol. Finite termination and potentially exponential state/output growth are stated. No stable-prefix, full-tail coverage or global Chan-equivalence claim is introduced.

Recommended small clarification: append to the grouping sentence that single/multiple solutions refer only to the same exact input, same first/last endpoint positions, and deduplicated routes produced under this tree's explicit selection policies. This is already the intended model, but making the scope visible at the output statement avoids a broader uniqueness reading.

Minor diagnostic wording caution: the isolated model's optional `tail_breach` checks the final endpoint's directional extreme (later high beyond a top, or later low beyond a bottom). It is not a universal validation of all unresolved-tail relationships. The current c/d text does not overclaim that field.

## Final assembled b–d review

Read the full final `sections.md` and compared it with saved 002.a, the exact domain/source fields, the numeric reviewer artifact, and the helper-decomposed executable model (static inspection only).

The root incorporated all earlier clarifications: an integer ID accidentally within the valid positional range cannot be recognized by intent; the API accepts positions without resolving IDs; source validation precedes M<2 early return; helpers explicitly bind their source-local variables and restore snapshot values; branch construction performs its own validation without a redundant extra wrapper; grouped single/multiple solution wording is limited to the same input, boundaries and phase policies; finite model comparisons are explicitly candidate-set/state-invariant comparisons, not byte-equality of every diagnostic or production execution.

### Results

- All nine saved 002.a stages are represented, including malformed-input errors, postdecision take/skip-first-B alternatives, mandatory safe extension, mandatory-extension blocking, equal-price forks, first-qualified reverse, LIFO restoration, EOF/no-B distinctions, validation/dedup/grouping and provisional output boundaries.
- The 21-bar example consistently distinguishes sourceFX positions from merged centers and shows an actual rollback across a previously locally stored edge. The blocked prefix and recovered route are not conflated. Its four routes and same-boundary multiple-result interpretation agree with the saved numerical review.
- The supplement correctly postpones local storage until after a safe B extension and qualified reverse; the symmetry statement still requires full pair validation. Equal choices are distinct from raw-anchor FIRST/LAST, and incomplete tail extrema stay unresolved.
- All six helpers have precise ownership and failure behavior; work/checkpoint state is ordinary immutable internal data. The result remains a candidate family rather than an invalid multi-route flattening into one BiSeries. Later per-route projection preserves the exact eight Bi and six BiSeries fields and source position references.
- No production status/confirmation definition, raw anchor synthesis, source mutation, new domain class, stable-prefix guarantee, full-history coverage claim or global uniqueness theorem is introduced.

### Complexity qualification

For one restored/updated state, validating a prefix of valid connected edges plus the current pair costs O(N+M): its merged ranges are disjoint except for shared endpoint bars, so their total scan length is at most N+O(M). A direct current candidate-pair check also costs at most O(N). Consequently O((S+R)(N+M)) is a defensible bound for the complete range/path **recheck work**, where S counts processed/read/restored states and R counts deduplicated routes. Finite branch depth does not make S polynomial; state/output counts can be exponential.

The draft calls that expression a total-time upper bound without separately specifying deduplication/grouping/sorting costs. The isolated model sorts endpoint-tuple keys; a conservative additional comparison-sort term is O(R M log R). Hash-based deduplication also needs an explicit expected-cost assumption for a total-time claim. Recommended minimal correction: say “完整状态与配对复核成本为 O((S+R)(N+M))，去重／分组及可选排序另计”. This preserves the intended focus without claiming an unproven tighter total runtime.

No further algorithm or contract blockers found. This reviewer changed only this review artifact; root owns the memo write, numeric executions, visual inspection, preservation/link checks, task, memory and event log.

## Final saved-content verification

PASS. Read the saved memo020 block from 002.b up to (excluding)003 and compared it with final `sections.md`: exact text equality, including whitespace, passed. The six helper headings are exactly `_check_pair`, `_compare_end`, `_freeze_branch`, `_validate_branch`, `_finish_branch`, `_validate_candidates`, in the reviewed order. Source validation precedes the M<2 shortcut. ID intent cannot be inferred from a valid integer, and the source-position-only interface is now explicit. Source-local helper bindings and snapshot destructuring are present and coherent. Grouped uniqueness remains limited to the same input/boundaries/tree policies.

The saved complexity statement now bounds state/pair recheck work and separately accounts for deduplication, grouping, optional sorting and upstream validation. No remaining contract issue was found; no numerical model was rerun by this reviewer.

Saved block SHA-256: `2394b54810a253c4b4bce9ba74559ad9ea3c79158c35fab634d2edf9789aba2d`. Only this review artifact was updated.
