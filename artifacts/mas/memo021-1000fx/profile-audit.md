# Xianduan recognizer profile audit

Read-only source review, with this audit as the only owned output. No CC algorithm was executed and no runtime result is claimed. This is a proposed operational experiment profile, not proof of author-unique segmentation or complete treatment of all historical exceptions.

## Proposed strict anchored profile

Input is one immutable, connected, alternating legal Bi snapshot. `P[0:N+1]` are shared endpoints and `Bi[k]=P[k]→P[k+1]`; all actual pen intervals and provenance are retained. `S(i,j)` owns exactly `Bi[i:j]`.

1. Reject `j-i<3`, even pen counts, wrong endpoint types/direction, or endpoint price order inconsistent with direction. Initial-three overlap uses closed intervals (`max(low) <= min(high)`) as an explicit experiment choice. Do not require endpoints to be full-segment extremes. A failed initial-three intersection for fixed i cannot be repaired by later append.
2. Direction D is the first pen direction. Normalize the opposite-D feature pens in `Bi[i:j]` chronologically within the proposed segment. For this profile, inclusion in either enclosure order (including equal edges) merges using max(high),max(low) for D=up and min(high),min(low) for D=down; repeat the same chronological rule and preserve all member indices. This fixed-direction normalization is a declared profile policy.
3. Let L be the last resulting left-side feature element. At the candidate boundary j, start the first right-side feature element M from `Bi[j]`. Never inclusion-merge L across the hypothesized boundary into M. Within the right side only, process subsequent opposite-D feature pens with the same fixed-D inclusion rule. Keep the earliest price anchor on ties. The middle element anchor must remain exactly P[j]; a different price anchor invalidates this candidate boundary. The first separate right element R must form a strict joint-high-and-low top for up, bottom for down, with L/M. Equal-sided non-strict fractals are deliberately excluded by the strict profile unless a separately named equality policy is implemented.
4. No-gap: L and M overlap/touch under closed interval comparison. Require the reverse structure starting j to have at least three pens and initial-three common intersection as well. Only then emit a first-case certificate, with the real maximum-read evidence index, not the geometry endpoint j.
5. Gap: `L.high < M.low` for up; `L.low > M.high` for down. Build the second sequence from original-D feature pens after j (j+1,j+3,...), now using opposite-D merge direction and ordinary inclusion within that sequence. Its first strict reverse fractal supplies candidate C and evidence; require the reverse S(j,C) basic conditions (including odd >=3 and initial-three overlap). The second fractal does not recurse into another two-case test. Declare a conservative stale-gap rule: a strict new original-direction excursion beyond P[j] before the second evidence invalidates this candidate. This is a restrictive experiment policy; it is not asserted as a complete substitute for every original failure-absorption exception.
6. Every emitted certificate records L/M/R sources, included members, primary gap comparison, reverse-prefix checks, second-sequence sources when applicable, geometric endpoint, and the last source pen actually read. Different provenance must not be erased merely because prices coincide.

## Earlier completed boundaries and the DP consequence

A proposed longer S(i,j) must not silently swallow an earlier already admissible completed boundary S(i,k), i<k<j. For an initial strict profile, compute certificates consistently and retain the earliest admissible completed geometric endpoint for each fixed i; label later ones `rejected_due_to_earlier_boundary`. If the profile instead keeps these longer intervals, it must explicitly disclose a relaxation and must not claim it automatically implements the original segment definition.

This has a structural consequence: source/path-independent certificates plus mandatory earliest boundary give at most one admissible next endpoint per i. The DP graph then has outdegree <=1 by geometry (duplicate proof variants can be deduplicated only when future behavior is identical). Earliest-start/latest-end/max-count DP can still verify/select the resulting chain, but it does not create a nontrivial family of partitions. To obtain several legitimate endpoints per i, carry genuine boundary/confirmation-context hypotheses and prove their compatibility; do not force multiple edges merely to make DP appear useful.

A prior prefix must not change how `S(i,j)` is judged if the experiment uses a scalar endpoint DP. Under this declared local profile, certificate membership and all future evidence are fixed-source facts. Adjacent graph edges still require shared boundary and opposite direction. If any decision depends on an earlier selected boundary or unresolved certificate, use an expanded state instead and do not merge by endpoint.

## Acceptance checks for root implementation

- Enumerate all basic intervals, record exactly which shape check rejects them, and preserve input/source hashes.
- Run both strict no-inclusion teaching examples from memo021; verify no-gap at geometry P3/evidence Bi5 and gap at P3/evidence Bi10.
- Independently scan initial-three intersections and endpoint direction/price for every selected segment and reverse witness.
- Check each selected certificate by replay from original Bi members, not by trusting graph metadata.
- Verify no selected long interval crosses an earlier retained completed boundary for its own start.
- Verify evidence pen >= geometric boundary and < N, member ranges are half-open and consecutive, and final geometry is not moved to evidence time.
- Label unconfirmed suffix normally; no missing end segment is forced into the completed route. Do not call a stale gap or an unknown equality case a successful certificate.
- Compare graph DP objective with exhaustive short-graph enumeration. Separately test detector inclusion/equality/failure cases; graph-only agreement does not verify the detector.
- Report the profile's strictness and outdegree/branching statistics with the 1000-FX charts. Do not claim CC-output equivalence, author uniqueness, constant memory or permanent confirmation.

## Source boundaries

- Chan067:20–38 defines opposite-pen feature sequences, the two cases and no recursive classification of the second sequence.
- Chan071:30–54 distinguishes same-sequence inclusion and hypothesized-boundary sides; its wording does not license blindly merging the two sides.
- Chan077:73–85 gives odd >=3 pens, initial-three overlap, opposite segment destruction and the second-sequence simplification.
- Chan078:62 makes the prior-segment confirmation premise explicit; 64 describes a failed second-fractal situation collapsing provisional A/B/C; 70–72 distinguishes raw endpoints from later standardization.
- Memo029's scalar DP is valid only for path-independent outgoing legality. Its objective priorities can be reused independently of that state compression.

## Review of concrete XD-P1: derived-state consistency counterexample

Root supplied a concrete profile adding a 071-direct completion branch and gap-derived completed states. Inline arithmetic assertions pass on the following immutable continuous pen endpoints (no CC execution):

`10,18,14,24,19,22,16,23,21,23.5,20,23,21,23.8`.

- Parent S(0,3), 10→24, has primary top `[14,18],[19,24],[16,22]` with gap18<19.
- Reverse start j=3 has a 071-direct certificate for S(3,6), 24→16, at evidence Bi8: first reverse pen at P6 is16→23 and breaks the preceding22; the third reverse-direction pen21→23.5 exceeds23. Before that evidence, no original-down excursion breaks16. The reverse segment basic initial-three intersection is[19,22].
- The ordinary second-sequence upward elements after j are `[19,22],[16,23],[21,23.5],[20,23],[21,23.8]`. Down-direction inclusion merges the first two to[16,22], so the strict ordinary-F2 detector misses the direct boundary16. Its first later strict bottom is `[21,23.5],[20,23],[21,23.8]`, giving C=10 (price20), evidence Bi12. No later price in this example reaches parent boundary24, so the stale-gap rejection does not save this case.
- A derived D_i=S(3,10), 24→20, therefore crosses the already certified direct S(3,6) boundary. It is seven pens and passes basic endpoint/overlap checks; basic checks alone cannot reject the contradiction.

The parent-only graph edge is a useful proof-role restriction, but does not by itself establish consistency of the completion evidence. Under a no-earlier-completed-boundary policy, either reject the parent gap certificate as well as its derived state, or modify gap confirmation to choose the earliest reverse completion among ordinary strict F2 and the nonrecursive 071-direct branch. The latter gives parent S(0,3) plus derived S(3,6), both evidenced by Bi8. Do not recursively invoke arbitrary primary gap confirmation inside the second sequence.

This is a concrete contradiction between two rules of the proposed experiment profile, not a proof that the author cannot have a contextual interpretation. A context-specific exception could instead be declared, but must state exactly why the earlier direct certificate is unavailable when nested under this gap parent.

## Final XD-P1 profile/code review — PASS within experiment scope

Inspected `profile-spec.md`, `recognizer.py`, and `tests_profile.py` after the root chose descending-origin compatibility filtering and a normalized-left direct guard. No production or real market input was executed by this reviewer.

The formerly conflicting gap parent is now rejected in full when the already-selected primary from j has a different end C. The derived node is therefore not left with a false parent proof. The counterexample is intentionally omitted at start0 and returns3→6 under this conservative profile; that is a disclosed coverage restriction, not evidence of author-complete detection.

The direct branch checks the normalized last left feature against P[j], rather than requiring the entire earlier interval to have directional extrema. This matches the declared local guard and does not silently add whole-segment endpoint-extreme requirements.

The graph context is concretely restricted: gap-derived nodes are non-root and only reachable from their exact parent; parent F1 evidence is no later than C; S(j,C) and S(C,h) pass basic checks; existing primary at j must end at C; the next primary after C must end at/after evidence h. Ordinary/direct nodes impose the same evidence-inside-next-geometry bound. If no next primary exists, evidence remains in the open raw tail. Together these restrictions keep each stored proof within its declared adjacent geometry/open suffix under the local profile; no undefined opaque context variable is being claimed solved.

Performed eight actual synthetic/mirrored profile calls with bytecode writes disabled:

| Fixture | Selected geometry | Kinds |
|---|---|---|
| Strict no-gap |0→3|no_gap|
| Strict gap |0→3→8|gap, secondary_067|
| 071 direct |0→3|direct_071|
| Earlier-boundary conflict |3→6|direct_071|

All selected segment basic checks, shared endpoints, direction alternation, derived-parent ownership, next-geometry evidence horizon checks, and mirrored endpoint routes passed. This is a focused implementation-contract check using the new recognizer; it is not an independent complete-source oracle or a general proof. Root's independent witness checks and exact profile disclosure remain necessary for the 1000FX charts.

## Independent real-input validation — PASS

`independent_validate.py` imports no recognizer functions and independently reconstructs original pen intervals, full-list inclusion reductions, primary/direct/secondary certificates, descending-origin compatibility filters and first-completion choices. It independently enumerates every odd candidate endpoint pair: strong6889 and weak14161 (21050 total), rather than validating only selected certificates. All324 unique primary certificates and all353 graph nodes (141 strong,212 weak) match in full certificate fields and sources. All327 graph edges (124+203), derived-parent restrictions, geometry/evidence frontiers, selected FX anchors, uncovered pen ranges and open-tail basic candidates match.

DFS enumerated every reachable path prefix from the fixed earliest root (15 strong,26 weak) and reproduced every state best/prev value, traversal order, selected route and objective. These real graphs are nonbranching by profile construction, so this real-data check does not itself exercise a nontrivial tie or a large path family. Both input JSON hashes and all6 prepared upstream source hashes still match.

Independent results: strong15 completed segments, FX0→917, open pen range[147,167); weak26 completed segments, FX0→986, open pen range[234,239). Final script execution completed in0.253s. This is XD-P1 consistency relative to the declared experiment, not author-equivalence or unique segmentation proof; upstream full Bi legality remains preparation evidence rather than a fresh upstream algorithm execution here.

Scoped Ruff initially reported import formatting, method-level unlimited-cache and sorted-min style findings in the new checker. They were fixed manually within this owned script (instance-local caches and min selection); scoped Ruff and the complete independent validation then passed again. Only the allowed validator script, JSON result and this audit were written by this reviewer.
