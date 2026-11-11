# Own experimental recognizer R1 — design review

## Scope and decision

This defines an executable conservative experimental rule profile, not proof of equivalence to every Chan-original case. It does not call CC. Candidate recognition and selector contracts are explicit below. Accepted output is optimal within R1's generated graph; do not label it all-001-global-optimal. In particular R1's strict two-bound feature fractals may reject first-pen-break edge cases that need a separate source-aware rule. This rejection is deliberate experimental scope, not a claim those source patterns are illegal. If the user requires all original cases now, this profile does not meet that stronger goal.

A first-completion rule per origin can make DP degenerate into a chain. Do not manufacture additional segment alternatives just to make DP look useful.

## Exact profile choices

Input: fixed valid alternating connected pens b[k]=P[k]→P[k+1], k=0…N−1. Each pen range is [min(P[k],P[k+1]),max(...)]. Preserve exact source IDs, price precision and version.

1. `basic(i,j)`: 0≤i<j≤N; j−i odd and ≥3; first/last direction agree; up P[j]>P[i], down P[j]<P[i]; first three closed price intervals intersect. Point-only intersection counts in R1 (EXPERIMENTAL explicit choice).
2. Containment is closed containment in either order, including equality. For direction d=up, merge both lows by max and highs by max; for d=down, min/min. Equality merges, no epsilon. Store every original constituent index and earliest source index achieving chosen extreme. These are explicit R1 choices.
3. `norm(indices,d)`: consume indices in time order, push each interval; while the last two stack items contain either way, replace them by the directional merge and continue backward until the last pair is non-containing. Every merge reduces stack length, hence finite. Source membership is preserved in an ordered tuple.
4. Strict top(e0,e1,e2): e1.high>both neighbor highs AND e1.low>both neighbor lows. Strict bottom: both inequalities reversed. Equal feature highs/lows do not form strict fractals. First-three overlap and feature-fractal equality are different tests.
5. R1 never imposes whole-segment endpoint extrema. For an up top witness, the earliest source pen achieving middle.high must start at j (middle.high=P[j]); down mirrors with middle.low. This is a local feature-anchor requirement, not a global range-extremum rule.
6. If several completion events qualify for one origin i, choose minimum (proof_endpoint, geometric_j, gap_next_k, witness_source_tuple). Retain only that geometric j. For no-gap retain all eligible next endpoint k for that chosen j. This first-completion and deterministic tie policy is R1 experimental selection. It avoids knowingly skipping an earlier completed R1 boundary. It may collapse DP choices; report that honestly.

## First feature witness for fixed i,j

Let d be b[i].direction. Extract opposite-direction pens before j, indices i+1,i+3,…,j−2; normalize to L using d. `left=L[-1]` exists because basic(i,j) has ≥3 pens.

For each proof endpoint r=j+3,j+5,…≤N:
- R=norm(j,j+2,…,r−1,d), i.e. reverse-direction pens starting at the proposed boundary through the just-read reverse pen.
- Do NOT normalize across the protected boundary between L and R. This boundary protection is explicit and differs from ordinary same-sequence merge.
- If R has fewer than2 items, continue.
- middle=R[0], right=R[1]; require the corresponding strict top/bottom of (left,middle,right) and local anchor j. Store all constituent indices, including which items are auxiliary on the right.
- Require basic(j,r) so a reverse three-pen-capable structure exists and its initial three overlap.
- Up gap iff left.high<middle.low; down gap iff left.low>middle.high. Equality means no gap.

No-gap completion event: proof=r, geometry i→j. Any proposed next endpoint k≥r with basic(j,k) may support it; certificate requires actual next boundary k and that all first-feature right evidence is before/equal k. No independent third completed segment is required.

## Gap second feature witness

For each boundary j, scan source prefixes h. Opposite candidate direction is −d. Normalize the pens of direction d in [j,h), i.e. indices j+1,j+3,…,h−1, with direction −d. This normalization includes BOTH sides of any candidate second pivot: no protected split at k. Inspect every adjacent strict reverse fractal in that normalized prefix.

For an original up candidate, require a strict bottom; k is the start index of the earliest constituent pen attaining the middle.low. Original down uses strict top / middle.high. Require:
- k≥r, ensuring first-feature evidence belongs within the reverse j→k structure;
- basic(j,k) and basic(k,h);
- for original up, no source endpoint in (j,h] exceeds P[j]; for original down none falls below P[j]. Thus an original-direction new extreme BEFORE gap confirmation invalidates that pending j; equality is not a strict invalidation (R1 tie choice).

Event proof=h, AB geometry i→j, required next endpoint k, and a further no-boundary obligation through h. The second fractal is NOT recursively reclassified by gap. Store its raw source members and normalization trace. Select the earliest eligible event according to the fixed order, not the last/strongest hindsight event.

This witness can certify AB under the secondary rule without automatically putting BC into output. Requiring BC's own ordinary R1 certificate later makes the output a conservative subset. That distinction must remain visible in the result.

## Concrete finite certificate state and pair compatibility

State e=(i,j,k,h,w): completed segment i→j; required next geometric endpoint k; actual proof endpoint h; complete raw witness w. For no-gap h=r≤k. For gap h>k. In both cases basic(j,k) holds, and the gap case also has basic(k,h). Do not use an undefined sigma.

Transition e→f allowed EXACTLY when:
- f.i=e.j and f.j=e.k (actual next segment is the one e assumed);
- f.k≥e.h (the next boundary after f does not split e's right-side confirmation evidence);
- segment directions alternate;
- both certificates independently pass the exact R1 recognizer, including first-completion policy.

Why sufficient for this deliberately restricted profile: every certificate's route obligations are only the next exact boundary k and no further boundary before h. The next state fixes the first obligation and its own declared next boundary discharges the second. It stores no more distant or path-specific obligations. Induction over adjacent states proves all certificates remain compatible. If the implementation adds any extra witness assumption, it must be represented here; this proof no longer covers it otherwise.

All states may be roots for this fixed-window experiment. Select earliest root i with at least one certificate; DP sorted(j,i,k,h,id), each node weight1, edges strict increasing j. Optimize latest geometric j then count at fixed earliest i; same score keeps fixed first order. `tail[e]` includes the required basic j→k; gap right evidence k→h is retained as an additional open structure, not counted. Source before first i and after last j is unrepresented by completed segments even if used for evidence. No empty/open tail failure, no permanent append promise.

## Finite execution and practical acceleration

- Enumerate every basic i,j pair. Generate its first-feature prefix events, and possible second-feature events, then retain first completion per origin as specified. No candidate accepts via a hidden boolean theorem.
- Cache L-last for i,j, R-prefix normalizations for j,r, and second-fractal event tables per j. G witness checks are independent of i once j,d,r are fixed.
- For each j precompute valid second events (k,h,w), sorted by h,k. A suffix-min table by k answers earliest event with k≥r; reject events after the first invalidating original-direction extreme. This avoids restarting a full G search for every i,j,r.
- Expand no-gap k only after selecting the winning geometric j per origin. Build adjacency by the shared pair (f.i,f.j)=(e.j,e.k), then filter f.k≥e.h.
- Every normalization consumes a finite prefix and each merge shortens its stack. Every source scan increases its endpoint. Every graph edge increases geometric endpoint. Termination is therefore unconditional for finite input.
- Count actual candidate / event / graph state sizes and timing; do not quote O(N²) for the entire recognizer without an implementation analysis.

## Essential validation

Existing no-gap and gap examples must reproduce j=3, proof endpoints6 and11 respectively, with gap next k=8. Add mirror versions. Check containment both ways, exactly equal intervals, same high / same low, single-point initial overlap, origin-new-extreme before gap proof, and open suffixes. Assert no earlier R1 completion event exists for a retained origin. Independently replay each output witness from the exact source indices. Compare the state-graph DP against brute graph paths for short generated graphs; this validates the selector, not full Chan equivalence. For the real1000FX run, disclose R1, numbers of raw/Bi/certified segments, unrepresented tail, and this profile's known conservative exclusions.

## Review of root-selected XD-P1 (supersedes choosing R1 above)

Root selected a different executable profile: one primary winner per origin; no-gap/direct primary goes to the next origin primary, while a gap primary can be followed by its own parent-restricted derived segment certified via the second feature; derived is not a root and then advances to the next primary. This is a finite explicit proof-role grammar. Its fixed-node DP can degenerate into deterministic chains per origin, which should be reported.

Two issues must be decided explicitly before source-equivalence claims:

1. Direct071 supplement cannot silently identify arbitrary basic-shape candidates with an already established original-direction segment. Example `10,20,15,18,12,16,9` has basic initial AB10→18, first reverse endpoint12<previous start15, reverse initial-three common[12,16], and third reverse ends9<12 without a later endpoint above18. A naive direct rule accepts AB10→18. Yet its first characteristic elements [15,20],[12,18],[9,16] simply descend; the initial third upstroke lies inside the first. Thus the claimed application premise is unproved. Suggested conservative fix: require last normalized pre-j reverse element.high<P[j] for upward AB (low>P[j] downward), a LOCAL feature test, not whole-segment endpoint extrema. Then the example is rejected and protected cross-boundary first-break cases can still qualify. Otherwise call it a new experimental P1 rule, not a proved literal source071 implementation.
2. A gap-derived segment j→C is certified by right-side G evidence through h>C. If that evidence is assumed to lie inside the actual next segment from C, derived→primary(C) must enforce the latter endpoint≥h (also respect actual merged-source frontier). Parent ID alone does not encode that obligation. Alternatively P1 can explicitly treat those right elements as auxiliary raw evidence independent of later chosen cuts; then graph-role sufficiency is by construction, but original ownership adequacy remains unproved. Do not hide this behind an opaque global compatibility boolean.

All reports should separate: arithmetic/selected grammar consistency; optimum within the produced finite graph; and any unproved equivalence/completeness against original001. This file is a design review only; no source/memo/production algorithm was edited by the reviewer.
