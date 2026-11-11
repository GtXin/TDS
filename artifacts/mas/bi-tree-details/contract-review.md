# Current Bi tree details: independent contract review

Status: PASS on the integrated section-002a/b/c/d drafts. Root owns final memo insertion, saved-byte/hash/link checks, numeric decomposition replay and live Obsidian inspection.

## Scope

This reviewer owns only this file. No memo, source, test, task, log or memory edits. The current note-based, single-route, nonblocking traversal is the specification being documented. The production Bi implementation and memo028 still describe the archived first-round candidate protocol; do not silently import that protocol into these details.

## Required contracts and pitfalls

1. **Coordinates.** State and stored edge references use zero-based positions in the exact source FenxingSeries. A merged center is `source_start + 1`; raw anchors remain `anchor_raw_index` from that source. Feature IDs, merged positions and raw positions are not interchangeable. An integer ID accidentally within the valid positional range cannot be recognized by intent; the interface accepts positions and does not resolve IDs.
2. **Full upstream input.** Validate the exact completed source chain and all complete strict fractals, including order, uniqueness, windows, prices, anchors and noninclusion. The first-pair shortcut assumes that no interior same-kind extremum has been omitted. Reuse the existing FenxingSeries validator rather than pretending that checking only listed fractals establishes completeness. Normal empty input is distinct from invalid/incomplete source input.
3. **Initialization proof obligation.** Before a first pair exists, S starts at the first complete fractal, retains its kind, updates only on strictly stronger same-kind points, and keeps the older equal point. Thus S is the first occurrence of the strongest seen same-kind extremum. The first-pair one-sided check relies on this invariant; a restored state with an arbitrary weaker S is unsafe even when its index/cursor are in bounds. Either validate this invariant or state that snapshots must originate from the verified traversal and validate their evidence/state accordingly.
4. **Range endpoints.** A half-open range helper should represent first/reverse full center ranges as `[c(start), c(end)+1)` and extension suffix as `[c(current_B)+1, c(F)+1)`. The suffix starts after the CURRENT cache endpoint B, not after the most recent rejected candidate. It includes all skipped fractals' merged bars. Check both new bounds on the suffix.
5. **Predicate scope.** First pair: known chronology/opposite type plus distance and the candidate-end extremum; the start side follows initialization. Extension: known valid old pair, later same kind, immediate weaker rejection; equal/stronger only scans the new suffix and does not repeat the old distance. Reverse: distance and BOTH full-range extrema. Do not generalize one stage's shortcut to all pairs. Independent final validation retains all original six conditions.
6. **Equality.** Initial equal same-kind points keep old S. Equal cache endpoints replace with later F only if the suffix check passes. These are explicit different stage policies. They do not inherit raw-anchor FIRST/LAST or introduce a tolerance.
7. **State and aliasing.** Bi002 is optional; when present it is a geometrically valid pair A→B and Bi001S=B, Bi001E unset outside the atomic rotation. R is append-only and its final endpoint is A if nonempty. On a valid reverse, assign the temporary end F, append an independent immutable copy/value of old Bi002, then rotate to B→F and clear E. No mutation of a work cache may alter a previously committed R edge.
8. **Outcomes.** Ordinary candidate failure records its actual reason and advances the cursor; it is neither a scan stop nor a source error. Invalid source/state raises. EOF normally returns R, a separate uncompleted Bi002, optional pending first-start S, next cursor, evidence and unresolved ranges. A singleton S is not a stroke. Do not append the final cache to R merely because of EOF, duplicate it in both collections, or label an open tail an algorithm failure or future-completion proof.
9. **Continuation.** Zero-FX initialization sets cursor0; first arriving complete FX initializes S and advances before normal reads. Single-FX snapshots continue from cursor1. Other snapshots resume without clearing R. The new immutable source object need not be identical to the old source object: verify the old merged and complete-FX prefixes, raw/source context, configuration and rule context remain compatible. Raw append alone does not establish that derived prefixes stayed fixed. No new complete FX means return normally, not an empty loop. A changed prefix is a separate input-revision error/contract, not permission to reset the final result.
10. **Output/domain boundary.** Keep the pure algorithm's R/cache/resume state as ordinary data, without adding public classes or fields. The current eight-field Bi and six-field BiSeries do not themselves define this new resume report or a completion policy. In particular final R under the user's algorithm is not automatically production `status="confirmed"`; upstream and existing production confirmation fields remain unconfirmed/None. Any later projection must retain exact sourceFX positions and source/version context.
11. **Independent validation.** Recompute every R edge and optional cache against original001, including windows/type, chronology, gap, relative center intervals, inclusive range extrema, shared endpoints and alternating directions. Check cache/R separation, cursor and pending-start semantics, unresolved boundaries, and unchanged submitted R prefixes across batches. Geometric soundness alone does not validate that the sequential choices or resume cursor were generated by the specified protocol.
12. **Complexity and evidence.** Single-pass FX reading does not make direct repeated range scans linear. Bound comparisons by reachable stage checks and inclusive spans; O(MN) remains a safe simple bound, with input/revision validation and multi-batch revalidation stated separately. Finite synthetic comparison results are not production Bi or raw-market-chain execution, nor a theorem of canonical uniqueness, completion or coverage.

## Existing references inspected

- `docs/memo/memoWX_020_Chan_bi.md`: current 002.a and 003 reduced predicates, nonblocking traversal, final-R boundary and open-tail continuation.
- `docs/memo/memoWX_019_Chan_fenxing.md`: 002.c–d helper/validator format and separation of coordinate systems and actual source evidence.
- `docs/memo/memoWX_009_designPatternForChanFeatures.md`: 002.h–i exact Bi/BiSeries fields and endpoint-position contract.

## Preservation boundary

Definitions001, original004 note/prompt, all appendices/references, memo028 and production/test files are outside this edit. Root owns the live Obsidian checks and final saved-byte/hash/link verification.

## Integrated draft review

Read the full `section-002a.md`, `section-002b.md`, `section-002c.md` and `section-002d.md`. No draft file was edited, and this reviewer did not execute root-owned evidence generators.

### Verdict

PASS. No algorithm-contract blocker or required edit found.

### Specific checks

- **Heading/tree structure:** a retains the current reduced predicates and all 2.1–2.9 transitions, now using actual H4 subheadings and short fenced bodies. The prior 19-bar worked example moves into b; a points to b/c/d rather than duplicating it. This changes presentation, not traversal choices.
- **Seven helpers:** `_validate_input`, `_compare_same_kind`, `_check_first`, `_check_extension`, `_check_reverse`, `_check_state`, `_validate_output` have consistent responsibilities. None advances the cursor, submits output, mutates upstream data or introduces domain/public API fields.
- **Initial invariant:** the full source/complete-fractal gate is explicit. `_check_first` is restricted to states generated by the chronological initial rule, or trusted unmodified checkpoints from the same algorithm revision. The draft does not accept an arbitrary geometric S/cursor as a sufficient resume state. The maximum/minimum start-side proof is not reused for reversal.
- **Cross-batch provenance:** a new immutable source snapshot is allowed when old raw/merged/complete-FX and rule/source context prefixes remain compatible. Old/new object identity is not required. Changed or shortened prefixes and externally modified checkpoints are rejected rather than clearing R.
- **Coordinate systems:** pseudocode state references are sourceFX positions, centers are `source_start+1`, and raw anchors are not recomputed or substituted. The main example correctly gives R `(4,7)`, cache `(7,8)`, cursor9 for centers5→13→17.
- **Ranges and ties:** first/reverse scans include both centers; extension scans `c(B)+1..c(F)` using the current valid cache endpoint B. Both suffix bounds remain; skipped candidates are not dropped from later range scans. Initial equal S keeps old; a valid equal endpoint takes new. The 21-bar suffix warning correctly identifies the skipped lower bar11 that would be missed by starting after the last rejected candidate.
- **Cursor and empty states:** initialization cursor0, first readable S setup, cursor1 after one FX, and no-new-FX normal returns are coherent. Resume does not reinitialize R. Every ordinary candidate read advances before branch handling; every ordinary failure continues; no EOF loop or artificial missing-right-neighbor fractal is introduced.
- **Commit/aliasing:** a valid reverse assigns the temporary end first, appends an independent immutable old endpoint pair to R, constructs the new cache, follows S to that cache end, then clears E. R_before records value preservation across a resumed batch. The code blocks are explicitly one continuous process/while scope.
- **Output boundary:** EOF returns final R and a separate uncompleted cache, plus pending initial S/cursor/context/evidence/unresolved ranges. No cache is promoted on EOF. A singleton S is not a stroke. The pure algorithm report is explicitly not a new production BiSeries API or confirmation field definition.
- **Independent validation:** the output helper directly restates original001 chronology/type, distance, strict center-interval relationships, inclusive full-range bounds, shared endpoints and alternation, without calling reduced stage predicates. It separately checks old R was not replaced, next_position=M, cache/S/E coherence and normal empty/no-cache cases.
- **Costs and claims:** direct range scans remain O(MN), with source validation and repeated-batch verification separately scoped. No linear-runtime, global uniqueness, canonical-theory, complete-market coverage, future-completion or production-validation claim is made.

### Example/static consistency

The 19-bar sequence, complete FX position map, equal-start/equal-end examples, M0–M1/no-FX then M2/single-FX then full-input continuation, and 21-bar open-tail reference are consistent with earlier reviewed numerical artifacts. The new draft makes the copied endpoint values versus mutable cache distinction explicit. Numerical decomposition execution and rendered heading verification are owned by root, not claimed as this reviewer's actions.

## Follow-up — user-requested single nested tree

The user clarified that 2.1–2.9 are algorithm nodes, not Markdown headings. This supersedes the earlier presentation review of nine H4 nodes; it does not change the reviewed b/c/d contracts.

Read memo015's single fenced, nested condition→action→goto tree and the latest `section-002a.md`/`unified-tree.txt`. PASS: the latest a has exactly one text fence, no numbered Markdown headings, and one visual root “笔算法”. The fenced tree text exactly matches `unified-tree.txt`.

All 2.1–2.9 nodes and prior decisions remain. Initial valid/empty/nonempty branches initialize or reach EOF correctly. Reading F still advances before dispatch. The empty-cache 2.3 and existing-cache 2.4 branches are nested under 2.2.a; same/opposite kinds dispatch to 2.5/2.6. Every normal failure or no-change action returns to 2.2. All successful cache changes reach shared 2.7 and then loop; the shared node is labeled as an explicit goto join. Exhaustion reaches 2.8, then 2.9. The visual root also groups shared joins without turning them into a new branch policy.

The shortened/rewrapped actions preserve strict-greater initial updates, initial equal retention, valid equal endpoint replacement, full suffix bounds, full reverse bounds, independent committed endpoint copies, final-R immutability, EOF-open cache and no EOF busy loop. E is explicitly defined as the Bi001E alias before the tree. Prefix-safe continuation remains outside the tree with its zero-FX first-arrival branch intact. No automatic backtracking, new stop condition, confirmation or output policy was added.

No required changes found. Only this review artifact was appended; draft/production/memo files were not edited and no numerical rerun was performed by this reviewer.
