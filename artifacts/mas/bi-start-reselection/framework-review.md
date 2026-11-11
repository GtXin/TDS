# Start reselection and pending-boundary review

## Initial judgment

Reselecting the cached start can resolve the demonstrated local obstruction only if the preceding stroke can share the new start. It is not merely replacing one cached point.

Use `P(bottom) → A(top) → B(bottom)`, with later `C(top)` and `D(bottom)`. In the audited run, P→A is already the last submitted stroke (FX145→FX148), while A→B is the unfinished cache (FX148→FX149). The proposed replacement of A by C requires the continuous chain to become `P→C→D`: discard old A→B, replace P→A by P→C, and form C→D. Both replacement pairs require full geometric checks, including their complete interior merged ranges. The numeric reviewer is independently checking those actual pairs; this report does not assume they pass.

If P→A remains in immutable R, starting a new cache at C breaks the shared-endpoint invariant. Modifying its endpoint A to C changes a submitted stroke and conflicts with the user's fixed final-result constraint. Therefore this repair must be considered before P→A is submitted, not implemented by resetting the start after the fact.

## What two complete pending strokes would change

Current Bi001 generally contains only `S=B`, with E unset; Bi002 contains one complete qualified A→B. It is not two complete pending strokes. This follows directly from memo020 lines42–44 and51.

A different, still provisional framework could retain both `P→A` and `A→B` as unsubmitted strokes and inspect arriving C/D. If P→C and C→D pass all six conditions, that local pending suffix can be rewritten without changing the earlier final R. Thus two complete pending strokes provide a capability that the current one-pair-plus-start state lacks.

This is a framework possibility, not an adopted transition, proof of sufficient depth, or prescription to modify current R. A full proposal would still need explicit candidate handling, replacement and tie rules, and—most importantly—a justified boundary for when the oldest pending stroke becomes immutable.

## Why no fixed depth follows from this example

The local rewrite may itself fail. For example, if the intervening bottom B is below P, then P→C necessarily violates its fixed lower bound even when P→A, A→B and C→D are individually valid. Moving P would then affect its predecessor stroke as well. This is a conditional dependency argument; no numerical inevitability or universal unbounded-buffer theorem is asserted here.

Consequently the audited case can establish that the existing state cannot perform this particular reselection. It cannot establish that exactly two complete strokes, three levels, or any other fixed minimum is sufficient for every valid input. Extra storage alone supplies no commit proof.

The essential unresolved invariant is: **what evidence permits a pending stroke to cross into immutable R, while retaining the intended ability to build a continuous legal suffix later?** Its guarantee must be stated explicitly; permitting an open tail alone does not prove eventual progress, and geometrically legal current pairs alone do not prove a permanently safe commit boundary.

## Source and scope

* `docs/memo/memoWX_020_Chan_bi.md:13` — adjacent strokes must share the same endpoint.
* `docs/memo/memoWX_020_Chan_bi.md:16` — every pair must satisfy full-range endpoint extremes.
* `docs/memo/memoWX_020_Chan_bi.md:42` — Bi001 is a working start with normally unset E.
* `docs/memo/memoWX_020_Chan_bi.md:44` — R is append-only and immutable.
* `docs/memo/memoWX_020_Chan_bi.md:118` — current reversal commits old cache immediately, before rotating.
* `artifacts/mas/bi-feedback-audit/numeric-review.md` — actual FX149 commits FX145→FX148 and installs cache FX148→FX149.

No memo, code, dataset, production API, or final-result rule was changed. This review does not adopt rollback, reset, a deeper buffer, or a new confirmation policy.
