# Fixed-cache nonprogress review

Scope: read-only reasoning against current memo020; numeric witnesses were independently checked by the separate actual-data reviewer and delivered by the parent. No rule, recovery, production, or memo changes are proposed.

## Verdict

Reading all 3,027 FX proves traversal reached EOF. It does not prove that the selected cache can ever advance. Conversely, an open EOF by itself is permitted and is not an algorithm error.

If the reported witnesses are confirmed—cache `A=TOP FX148`, `B=BOTTOM FX149`; later `U=TOP FX150` has `H_U>H_A`; later `D=BOTTOM FX151` has `L_D<L_B`; neither event changed the cache—then the current rules admit a permanent nonprogress state under every future input preserving that history. This is stronger than merely observing an unfinished finite tail.

The parent has now relayed the independent numeric confirmation: A center301/high2818; B center305/low2802; U center306/high2824, rejected as a reversal with distance1; D center310/low2794, rejected as an extension because of the upper bound. Thus both strict witness inequalities hold, and the conditional theorem applies to the reported run. This report did not rerun the production scan.

## Proof

After D, assume A/B remain the current cache endpoints. Every future complete FX F is either a bottom or a top.

* **F is a bottom.** If weaker than B, node2.5 skips it. If equal or more extreme, the checked new suffix `(c(B),c(F)]` contains U. Its upper bound must remain `H_A`, but `H_U>H_A`, so the extension necessarily fails.
* **F is a top.** Node2.6 checks B→F over the complete center-to-center range. That range contains D. Its lower bound must remain `L_B`, but `L_D<L_B`, so the reversal necessarily fails.

Both failures retain A/B and R; therefore induction over all future F preserves the same state. The reading position and evidence can continue growing, while the cache never updates and R never gains another stroke. No future prices or longer distance remove either historical witness. This proof relies on preserved merged/FX history, which is exactly the normal continuation precondition.

## Meaning and limits

* **Traversal:** no scan interruption is established; every FX may still be read normally.
* **Geometry/safety:** the existing R and A→B may remain valid over their own covered intervals. The proof does not identify a violation of any of the six geometric conditions.
* **Eventual progress:** the stated witness falsifies any unconditional claim that a sufficiently long compatible continuation must eventually update this cache. It also shows why “all FX read; ordinary failures continue” is insufficient evidence for that claim.
* **Semantic coverage:** if the intended algorithm must continue producing strokes through later market fluctuations, this is a substantive limitation of the selection/commit protocol. If its only promised output is a geometrically valid prefix plus possibly permanent unresolved tail, the observed behavior is consistent with that weaker contract. User acceptance of an open EOF alone does not settle this stronger progress question.

Current memo020 already declines to guarantee future completion; the review must not turn an allowed open EOF into an assumed requirement that every later candidate succeed. The numeric witnesses, not the number of failed candidates alone, are what support the permanent-nonprogress conclusion.

## Source locations

* `docs/memo/memoWX_020_Chan_bi.md:16` — every merged bar must remain within endpoint extremes.
* `docs/memo/memoWX_020_Chan_bi.md:56` — continuation preserves the entire prior raw/merged/FX prefix.
* `docs/memo/memoWX_020_Chan_bi.md:103` — extension skips weaker candidates; otherwise checks both suffix bounds; failure keeps cache and R.
* `docs/memo/memoWX_020_Chan_bi.md:113` — reversal checks both full-range extremes; failure keeps cache and R; success alone appends to R.
* `docs/memo/memoWX_020_Chan_bi.md:128` — EOF is normal and does not commit cache.
* `docs/memo/memoWX_020_Chan_bi.md:141` — open tail is not a guarantee of future completion.
