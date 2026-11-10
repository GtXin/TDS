# Memo020 v2: finite endpoint-state model

Scope: algorithm study of the six current version-two conditions only. No CC behavior is imported as a theory rule. No production detector is added. Files `state_model.py` and `state_model.json` contain the isolated exact-arithmetic model and actual checks.

## Input contract and invariant

Read `src/chanlab/algo/fenxing.py`: `_direction_between` and `_classify_window` (lines 113–128) require both prices to move strictly in the same direction in each adjacent pair and scan all three-unit windows. `derive_from` (lines 226–240) retains every classified window; it performs no stroke endpoint selection. Raw candidates can overlap and can be too close to become stroke endpoints. A Fenxing center is `source_start + 1` in its exact merged series, not `anchor_raw_index` in the raw source. The existing `FIRST`/`LAST` option chooses a raw anchor inside one merged center; it does not choose between distinct equal-price fractals.

For selected endpoints `p[0] < ... < p[k]`, every adjacent pair must pass the complete pair predicate:

1. Opposite kinds and center difference at least four.
2. With top-center interval `[LT, HT]` and bottom-center interval `[LB, HB]`, `HT > HB` and `LB < LT`.
3. On the inclusive merged-center range, `max(high) <= HT` and `min(low) >= LB`.

Under the strict actual Fenxing input, the endpoint-interval inequalities are redundant with the extrema bound: the interior neighbor of a bottom has high strictly above HB, so the endpoint maximum HT must exceed HB; the interior neighbor of a top has low strictly below LT, so the endpoint minimum LB must be below LT. The argument uses the neighbor on the side inside the stroke and applies in either direction. Retaining the explicit checks is useful for diagnostics, but condition five adds no tie-selection rule under these premises.

Every pair shares its endpoint with the next pair, so continuity and direction alternation follow. A singleton endpoint is a pending seed, not a stroke. Every stored candidate is scoped to the exact immutable input snapshot. Final/confirmed timing is not defined by the six conditions.

## Safe sequential finite baseline

Construct a chronological DAG: one vertex per actual Fenxing; add edge `u -> v` exactly when the complete pair predicate passes. Process new vertices in increasing center order, inspect all earlier vertices as possible predecessors, and retain a state for each endpoint center. The model is sound and complete for paths satisfying these six conditions: each admitted edge is a legal pair; any legal endpoint chain consists entirely of admitted edges. This is not a proof that one path is the author's unique stroke result.

A new opposite-kind candidate that is too close creates no edge from that particular predecessor. It must remain available as a vertex: it may connect from an earlier predecessor or serve as a later starting endpoint. A same-kind candidate does not connect to its peer and does not automatically delete it. Its incoming edges are evaluated independently. Equal extrema at distinct centers also remain distinct vertices.

Without a selection policy, return the graph/alternative paths as an analysis result. If a proposed engineering policy pins the first endpoint, maximizes the number of edges, then selects the lexicographically earliest sequence of center indices among equal maxima, DAG dynamic programming gives a deterministic result. These objectives and tie choices are additions requiring explicit adoption; they are not consequences of the six conditions. For this additive objective, only the best path *to the same exact vertex* needs to be retained: future choices depend on that vertex and pair edges, and appending the same suffix preserves edge-count and lexicographic ordering. Do not apply this dominance argument to different endpoint centers merely because their price or kind is equal.

Conservative costs for `N` merged bars and `F` fractals: direct scanning of every pair costs `O(F² N)` worst case. Build range-max/range-min sparse tables in `O(N log N)` time/space, then all pair predicates and edges cost `O(F²)`; DAG DP costs `O(F²)` with numeric scores and predecessor pointers. Storing all edges costs `O(F²)`; calculate edges on demand if that memory is undesirable. The tiny Python model instead scans ranges and stores path tuples for transparency, so it is not the optimized implementation and lexicographic tuple handling adds path-length overhead. Enumerating all paths can take exponential output space/time and is only a small-case oracle.

For live raw append, upstream merging can revise a tail. Reusing an old DAG without a proven unchanged merged prefix is invalid. A full recomputation on the next complete immutable FenxingSeries snapshot is the safe baseline; a bounded incremental protocol and stable-prefix claim need a separate proof.

## Verified continuous examples

All examples use intervals `[v, v+2]` and exact arithmetic. Adjacent scalar values are never equal, so every adjacent interval pair has both high and low strictly up or strictly down: no adjacent inclusion. All actual strict three-window extrema are scanned, not hand-selected abstract points. Indices below are zero-based merged centers.

### Blind same-kind replacement breaks an existing pair

The continuous scalar sequence is:

`[14,15,12,9,6,3,0,2,4,6,8,10,4,-2,5,12,11]`.

Its exact extrema are top `P@1=17`, bottom `Q@6=0`, top `R@11=12`, bottom `S@13=-2`, top `T@15=14` (top prices are `v+2`, bottom prices are `v`). `P -> Q -> R` is a valid chain. `R -> S` fails only distance: centers differ by two. If a greedy algorithm discards S, then replaces R by the higher same-kind T, the resulting `Q -> T` fails the minimum invariant: S's low -2 is below Q's low 0. `P -> S` is a valid alternative edge. Thus a skipped too-close opposite cannot be forgotten merely because it failed against the most recent endpoint.

This does not mean the six conditions themselves force deleting the old `P -> Q -> R` path. That old prefix remains locally valid. Replacing it requires an additional tail/coverage/selection policy.

### Rollback can extend past a fixed number of suffix endpoints

The second continuous example is obtained by exact monotone interpolation through scalar control points:

`(0,99),(1,100),(6,0),(11,10),(16,1),(21,20),(26,2),(31,30),(33,-10),(34,-9)`.

The old endpoint path `[1,6,11,16,21,26,31]` is valid. For the new bottom at33, the only valid incoming top is center1. The last top31 is too close; earlier tops21 and11 are lower than a later intervening top, so their proposed downward pairs fail the maximum invariant. If the policy requires reaching bottom33 from the original start, it must replace the entire six-endpoint suffix with `[1,33]`. Repeating the construction with more progressively higher internal tops makes the necessary rollback depth unbounded by any fixed suffix constant. This is a conditional result under the stated tail policy, not a claim that every selector must perform that rollback.

### Distinct equal extrema need more than a raw FIRST/LAST flag

- Equal tops at5 and9: path `[1,5,12]` is valid, whereas choosing9 makes the later bottom12 too close. Globally preferring the latest equal top can lose an outgoing edge.
- Equal tops at3 and7: the first is too close to bottom1, while `[1,7]` is valid. Prefiltering all equal tops to the earliest one can lose an incoming edge.
- Even pinning both boundaries and maximizing edge count does not ensure uniqueness. In the fifth example, `[1,5,14]` and `[1,9,14]` are distinct valid maximum-edge paths with the same first and last endpoints. Both top5 and top9 have the same price. Choosing one needs an extra policy.

The JSON contains every interval, every exact fractal and every valid pair for all five examples.

## Actual checks and next decision

Executed `python3 artifacts/mas/bi-algorithm-study/state_model.py`: all five continuous examples pass strict adjacent-direction checks and asserted exact extrema/pair/path expectations. DAG longest-path results match exhaustive enumeration for all possible starts and endpoints over 76 enumerated paths. These are finite checks of the stated model, not a proof that a greedy production selector is correct, not a run of CC, and not a comparison with the market dataset.

A proposed stack implementation must validate the entire affected path before committing replacement. If revalidation fails, keep the old valid candidate and preserve the new raw candidate for other possible predecessors; popping only one endpoint is not generally sufficient. The DAG model is the reference oracle until a more efficient selector is specified and proven equivalent under explicit first-endpoint, tail-coverage, objective and equal-extreme policies. The six conditions alone do not decide those policies.
