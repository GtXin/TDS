# Strong/weak center-distance option: independent numeric review

## Scope and actual checks

Used a standalone stdin integer-interval model with the current single-route
initialization, stronger/equal end update, first valid reverse, append-only R
and open EOF. Its complete pair predicate uses only one changed parameter:
center gap g=4(strong) or g=3(weak). No other policy, reset or recovery was
added. Valid nonempty continuous interval inputs only; no production imports,
prior report-writer execution, random suite, source/memo/code edits or OHLC.
Only this review file was written.

PASS exactly38 local scan calls:5 full fixtures x2 modes=10;7 sequential
prefix snapshots x2 modes=14;their14 same-mode one-shot comparisons.
All sourceFX lists came from strict three-bar comparisons; adjacent bounds
move strictly together without inclusion. Every accepted pair was checked
against both relative center-interval inequalities and complete interior
extrema. Prior saved model states and committed R values remained unchanged.

## A genuine gap3 example with different sequential results

All11 bars are[low,low+1], low values:

    1,0,2,4,5,4,2,1,3,6,5

| SourceFX position | Kind | Merged center | Center interval | Merged window |
|---:|---|---:|---|---|
| 0 | bottom | 1 | [0,1] | [0,3) |
| 1 | top | 4 | [5,6] | [3,6) |
| 2 | bottom | 7 | [1,2] | [6,9) |
| 3 | top | 9 | [6,7] | [8,11) |

Those are ALL complete strict fractals. For1->4, gap3 and range min0/max6;
6>1 and0<5, both endpoint extrema pass. Only the mode-dependent distance
decides acceptance. Windows[0,3),[3,6) are disjoint but adjacent, with NO
independent merged bar between them. For4->7,gap3,range min1/max6;
6>2 and1<5, again all non-distance checks pass.

Weak mode: accept first1->4, then4->7 at gap3, submitting1->4 to R.
Later7->9 has gap2 and fails even weak mode. Strong mode: reject1->4,
retain original bottom1 over weaker bottom7, then accept1->9 at gap8,
range min0/max7,7>1 and0<6. Thus:

| Mode | R sourceFX(center) | Cache sourceFX(center) | S/sourceFX | NextFX | Unresolved merged ranges |
|---|---|---|---:|---:|---|
| strong g4 | empty | (0,3),centers1->9 | 3 | 4 | [0,1),[10,11) |
| weak g3 | (0,1),centers1->4 | (1,2),centers4->7 | 2 | 4 | [0,1),[8,11) |

The weak-mode R and strong-mode cache follow different intermediate choices.
This is NOT a claim that the whole weak selected path contains the strong
path, that all weak outputs have more strokes, or that any lock is repaired.

## Existing four full examples: same selected work fields in both modes

| Input(low;high=low+1) | Both modes: R sourceFX | Both modes:cache sourceFX | S | NextFX | Unresolved merged |
|---|---|---|---:|---:|---|
| MAIN19 below | [(4,7)] | (7,8) | 8 | 9 | [0,5),[18,19) |
| OPEN21 below | [(0,1)] | (1,2) | 2 | 6 | [0,1),[10,21) |
| Initial tie9,10,0,10,9 | [] | none | 0 | 3 | all[0,5) |
| End tie1,0,3,6,9,10,8,5,8,10,9 | [] | (0,3) | 3 | 4 | [0,1),[10,11) |

MAIN19=[9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7].
ExactFX positions0..8:top1,bottom2,top3,bottom4,top5,bottom9,top11,
bottom13,top17. Merged center routes are R5->13,cache13->17.

OPEN21=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1].
ExactFX positions0..5:top1,bottom5,top9,bottom11,top15,bottom19.
R is1->5,cache5->9. Rejected reverse9->11 gap2 stays below both thresholds;
later extension and reverse fail interior extrema in both modes.

IMPORTANT: equal selected work fields do not imply identical full Q across
modes. Mode/context differs, and actual evidence can differ. MAIN19's
top1->bottom4 has gap3:strong fails distance;weak passes distance but fails
F-side minimum because bottom4.low1>interior bottom2.low0. The same local
start remains in both modes for DIFFERENT failure reasons. Do not claim
that all cross-mode evidence or whole output snapshots are identical.

The actual-data FX149->FX150 reverse has center gap1, so neither g3 nor g4
accepts it. This option does not by itself repair the earlier long-tail lock.
Strong/weak here are project distance modes, not a claim about the author's
raw-count-based new-stroke definition.

## MAIN staged continuation under both modes

Use MAIN19 and append low9,10,12,11 at merged19..22. All listed core work
fields and unresolved ranges match across the two modes; each resumed state
also equals its same-mode one-shot state, including saved interval/FX prefixes.

| N | FX count/NextFX | R sourceFX | Cache sourceFX | S | Unresolved merged ranges |
|---:|---:|---|---|---:|---|
| 2 | 0/0 | [] | none | unset | all[0,2) |
| 3 | 1/1 | [] | none | 0 | all[0,3) |
| 11 | 6/6 | [] | (4,5) | 5 | [0,5),[10,11) |
| 12 | 6/6 | [] | (4,5) | 5 | [0,5),[10,12) |
| 15 | 8/8 | [] | (4,7) | 7 | [0,5),[14,15) |
| 19 | 9/9 | [(4,7)] | (7,8) | 8 | [0,5),[18,19) |
| 23 | 11/11 | SAME[(4,7)] | (7,10) | 10 | [0,5),[22,23) |

At N23,newFX9=bottom18,newFX10=top21. Gap17->18=1 fails both modes;
extension13->21 succeeds in both, without changing committed R.
Changing mode is not the same continuation contract as continuing with
unchanged mode; the old mode belongs in saved state/context. These tests
fix g for each stream. Root separately owns Q-mode inheritance/rejection,
serialization/evidence/idempotence testing and any counts from that model.

## Limits and recommendations

Parameterize first-pair distance, reverse distance and full output checking
consistently; extension does not need a fresh distance check because its
valid inherited pair already met the SAME mode and F is later. Weak gap3
must not retain the wording requiring an independent intervening merged
bar. Use the11-bar difference example to make this visible. Nothing here
changes initialization ties, pending-end ties, output commitment or EOF
rules, or proves uniqueness, permanence or future completion.

## Final numerical draft review

PASS read-only review of section-002b.md and the active draft-memo.md.
The11-bar exactFX mapping, two gap3 ranges, strong/weak sequential results,
MAIN19's mode-dependent failure at bottomM4,7 default-strong prefix stages,
same selected weak states but different whole-Q metadata/evidence, and
strong-labeled OPEN21 with identical weak selected state are all correct.
Distance-mode inheritance and rejecting an explicit change on an old Q
are consistent with the valid-prefix numerical comparisons. No claim that
weak fixes the actual gap1 lock or always contains the strong whole route
was found. No extra arithmetic/model run was needed for this draft pass.

Optional wording precision sent to root: the11-bar fixture has empty strong
R, so the statement that weak final R need not contain strong R is a general
boundary warning, not a noninclusion counterexample established by THIS
R table. The cache/whole endpoint routes already differ, so wording it as
"单对门槛放宽不等于整条路线包含" is directly supported by the shown example.
Root separately owns the forthcoming bounded immutable Q-mode model and
any new counts from it; they are not part of this review's38 prior calls.
