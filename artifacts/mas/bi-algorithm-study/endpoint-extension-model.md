# Endpoint extension before a qualified reverse

This is a local correction model for the user's rule: passing the six pair conditions gives a candidate end B, not a finalized stroke end. Before a qualified reverse C is found, a later more-extreme same-kind B must be considered as the replacement endpoint. All inputs below are complete immutable merged sequences with all complete three-bar fractals. No raw-feed protocol or stable prefix is claimed.

## States and invariant

`SEEK_END(A)` has a chosen seed A and no valid working end. `WAIT_REVERSE(A,B)` retains both A and B, and the complete pair predicate is true on the inclusive center range `[c(A),c(B)]`. The scan cursor is separate from both endpoints. All later actual fractals F are processed chronologically, including those whose windows overlap earlier windows.

In particular, WAIT_REVERSE does **not** mean all bars to the right of B fit between A and B's price bounds. Those bars are the unresolved tail. Keeping A and B is essential: discarding A as soon as A→B passes prevents revalidating a later extension.

For each later F while waiting:

1. If F has B's kind and is strictly more extreme (higher top/lower bottom), propose `B=F`. Revalidate **A→F**, including every interior merged bar. Commit the replacement only if all pair conditions remain true. Otherwise retain the candidate and old geometrically valid pair, and flag the branch as needing alternative-start/rollback handling. This local model does not silently invent that recovery policy.
2. If F has B's kind but is less extreme or equal, do not finalize B. Retain F as evidence/alternative. Equal-price selection is still unspecified; this prototype does not silently choose latest.
3. If F has the opposite kind, test **B→F**. Passing supplies the qualified reverse C for this branch: locally close A→B, then retain `A=B, B=C` as the new working pair and keep waiting for its reverse. Failing leaves A and B unchanged and retains F for potential later recovery.

A transition from SEEK_END to WAIT_REVERSE emits no finalized pair. The prototype starts one branch at the first complete fractal and retains alternative seed candidates; it is not a complete algorithm for choosing all initial starts, resolving rejected-extension branches, or selecting between equal extrema. Closing A→B upon a qualified reverse is a local selection event; it is not a proof that no later global rollback is needed, and does not change any Fenxing.status/confirmed_at fields.

## Continuous directed checks

All synthetic merged intervals are `[v,v+2]`, so every pair of unequal adjacent v values is strictly up or strictly down with no inclusion. The script scans actual complete windows rather than supplying an abstract fractal list.

### B extends before a reverse C qualifies

`v=[1,0,3,6,9,12,10,8,12,16,13,10,7,4,5]`.

Actual extrema: bottom A@1, top B@5, bottom@7, top@9, bottom@13. A→B passes all pair conditions, but is only the working pair. Bottom7 is too close to top5 to qualify as C. Top9 is higher and A→top9 remains valid, so B updates from5 to9. Bottom13 then meets all reverse-pair conditions. The first locally closed pair is therefore `[1,9]`, not `[1,5]`. The new working pair is `[9,13]` and remains in WAIT_REVERSE.

### Unconditional extension can violate A's extreme

`v=[14,15,12,9,6,3,0,9,20,8,-2,-1]`.

A top@1→B bottom@6 passes. Top8 is too close to B to qualify as reverse C, but is higher than A. Later bottom10 is below B; blindly replacing B by10 would make A→10 contain top8 above A. The full revalidation rejects that extension. Merely comparing the new bottom with B, or merely checking distance, is insufficient. The pending alternative/rollback path must preserve this rejected evidence.

### A bar can exceed B before a new B-kind fractal exists

`v=[1,0,3,6,9,12,10,11,13,14]`.

The complete local top B is still center5. The last bars already rise past B's high, but no new complete top window exists at the right edge. It is therefore wrong to call B final; it is also wrong to manufacture a Fenxing at the final bar. Keep the valid historical A→B pair plus an unresolved-tail/breached-bound indication, or a separately labelled provisional bar extreme. This model records `tail_breach=true` without converting that bar into a fractal endpoint. A raw-bar crossing alone is not the same structural claim: the rule bounds merged prices, and directional inclusion may suppress a raw extreme. Raw append first requires inspecting/recomputing the evolving merged tail; this study only asserts the example for supplied immutable merged intervals.

### Equal later top

A fourth example contains equal-price tops at5 and9. The later top is retained, but does not silently replace B or finalize the first stroke. This check separates the endpoint-choice policy from the existing raw-anchor FIRST/LAST policy.

## Mirror and finite checks

Under interval sign reversal `[low,high] -> [-high,-low]`, all top/bottom roles and high/low rejection reasons swap, while endpoint center choices, state phases, acceptance/rejection event types, and tail-breach booleans must remain unchanged. The script checks this for the directed cases and the finite enumeration; rejection-reason sets are compared after swapping high/low labels, rather than incorrectly demanding identical reason strings or list order.

The script enumerates every 11-bar scalar path over `{0,1,2,3}` with unequal adjacent values, and checks its mirrored path. It asserts every stored working pair and every locally closed pair remains valid after each transition. Exact counts and transition coverage are recorded in `endpoint-extension-model.json` by the actual run. These finite checks establish behavior only for this local prototype and bounded synthetic domain; they do not prove a production selector, a confirmation protocol, or equivalence with CC.

Actual execution completed: 236,196 continuous paths and 236,196 sign-reversed mirrors; 163,174 stored-pair checks at final states, plus assertions after each transition. Transition counts include 7,374 accepted extensions, 78 rejected extensions needing recovery, and 10,250 qualified reverse events. All directed examples, state invariants and mirror comparisons passed. The first draft mirror assertion failed because high/low reason names and their ordering were compared literally; the comparator was corrected to swap labels and compare sorted reason sets, and the full final run passed.
