# Recursive reference for cached recovery

Scope: independent reference for the root's proposed explicit cache DFS, using the specified local phase policies. This is not merely enumeration of the six-rule pair graph: a strictly more-extreme end must update when valid, a failed mandatory update blocks the branch, and the first qualified reverse cannot be skipped. Equal valid ends branch into keep/replace. Different initial seeds and initial valid B choices are all considered. These are explicit selection policies, not a uniqueness proof from the six conditions.

## API and restoration model

`run(bars)` returns a set of tuples of merged-center indices for viable EOF routes. Bars are chronological `(low, high)` intervals with strict common-direction neighboring prices, no adjacent inclusion. `solve(bars)` returns the same routes plus actual complete fractals, blocked-branch diagnostics and event counters. Implementation is independent: no production, CC, `oracle.py`, or the root's iterative model is imported.

Recursive calls carry immutable `A`, `B`, next-fractal cursor and `prefix` values. Thus each return restores the full predecision state without sharing mutable endpoint lists. This is an intentionally different implementation from an explicit stack of cached states.

- SEEK_B scans each subsequent complete fractal F. On a valid A→F it first runs the accepted-first-B branch and, after it returns, independently explores the branch that declines this first B and continues searching from the unchanged A.
- WAIT_REVERSE checks every next F. A strict same-kind improvement updates B only if A→F passes; failure terminates this branch as BLOCKED. A valid equal-price F explores keep and replace as separate recursive calls, both starting after F. A less-extreme or invalid equal F simply advances. Opposite-kind F triggers the first reverse transition exactly when B→F passes; there is no skip-qualified-reverse branch.
- EOF in WAIT_REVERSE emits `prefix + (A,B)`; the final working pair is provisional. EOF without B emits no route. Initial seeds are subsequently tried independently.

All retained edges are directly rechecked on emission. `prefix` contains left endpoints of locally closed strokes, so its length can be less than the center path length. At a BLOCKED update, diagnostics preserve both `historical_prefix=prefix+(A,)` and the old working pair `(A,B)`, plus F; these diagnostics are not counted as viable EOF routes.

This reference does not claim that EOF routes cover all bars through the data boundary. EOF means no further complete input fractal remains; the last pair stays provisional and may leave unresolved tail bars. Blocked historical prefixes are explicitly distinguished from EOF routes. No Fenxing.status or stable-prefix property is inferred.

## Directed cases and observed routes

Every case uses synthetic continuous merged intervals `[v,v+1]`; JSON preserves every numeric interval and every actual complete fractal. Mirror transformation is `[low,high] -> [-high,-low]`.

### Safe extension

The 17-bar case with extrema at `1 top,5 bottom,7 top,11 bottom,15 top` extends the old bottom5 to lower bottom11 before a reverse qualifies. Routes are `(1,11,15)`, `(7,11,15)`, `(11,15)`.

### Unsafe 13-bar extension

Low sequence: `8,9,6,4,2,0,5,11,8,5,2,-1,1`.

The branch starting at1 accepts bottom5, rejects the too-close top7 as reverse, then blocks at lower bottom11 because top7 exceeds top1's maximum. There is no viable EOF route starting at1. Trying the later initial seed7 yields `(7,11)`. Treating failed extension as an ordinary skip would incorrectly preserve the blocked route.

### Recovery to an earlier first-B choice, 21 bars

Low sequence: `8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1`.

The first branch from A1 accepts B5, finds qualified C9 and locally stores A1→B5. Its next working pair is `(5,9)`. Bottom11 is too close to top9 to be a reverse; higher top15 then fails the mandatory `(5,15)` extension, because bottom11 is below bottom5. This branch is BLOCKED with historical prefix `(1,5)` and old working pair `(5,9)`.

Returning to the earlier SEEK_B decision, the recursive reference restores seed A1 and declines B5. It later accepts B11, then reverse15, then reverse19. Thus `(1,11,15,19)` is produced. Other viable EOF routes are `(1,19)`, `(11,15,19)`, `(15,19)`. No route `(1,5,9,19)` is produced.

This verifies actual cache recovery across an already locally stored stroke; merely recording rejected candidates without restoring the earlier decision does not achieve this result.

### Equal-price fork restoration

The equal-bottom17 case yields `(1,11,15)` but also provisional `(1,5)` from the keep-old-equal branch: that branch never finds a qualified reverse by EOF. This is expected under the supplied EOF policy and is not full-tail coverage.

The equal-top15 case yields both `(1,5,13)` and `(1,9,13)` along with later-start routes. This verifies that the two equal-price branches restore independent B and cursor state rather than mutating one shared path.

## Actual finite checks

Executed `python3 artifacts/mas/bi-algorithm-study/cached-reference.py` successfully. Checks include:

- All 26,244 length-nine scalar paths over four values with unequal adjacent values, and all 26,244 sign mirrors.
- 2,000 reproducible variable-width input paths with strict comparable adjacent intervals (seed `20261110`), and their 2,000 sign mirrors.
- Complete mirror equality of viable endpoint-path sets.
- All directed route and blocked-prefix assertions above, including qualified-reverse and failed-mandatory-extension behavior beyond the short exhaustive domain.
- Complete pair validation for every emitted path, including exact spacing, endpoint-interval and inclusive interior-extrema checks.

The finite scalar family observed 25,032 first-B choice forks, 1,320 equal forks, 180 mandatory valid updates and 26,352 EOF emissions before set deduplication; full event counts are in JSON. The direct recovery21 case supplies the deeper restoration and blocked-extension event evidence.

An initial random generator attempt allowed the enclosing interval `(-4,8)`, which has no strictly comparable neighbor inside the finite pool and therefore produced an empty sampling set. The pool was corrected to exclude that isolated interval; all final checks above passed. This generator correction did not alter the selector or pair rules.

Recursion depth is bounded by the number of complete input fractals; each call advances its cursor and branch inputs are finite. The number of equal-choice routes can be exponential, as can the explicit DFS's output volume. This transparent reference is a small-input oracle, not a production-scale implementation or a proof that these selection policies match all original-source edge cases.
