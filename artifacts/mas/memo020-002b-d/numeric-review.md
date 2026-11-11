# Memo020 numerical review for 002.b/c/d

## Scope
Computer Scientist numerical review of four finite synthetic interval examples,
plus their price reflections. No raw OHLC was invented. Bars are [low,high]
intervals on the processed sequence. No production detector or CC execution.
The recursive evidence runner independently implements the cached temporal
protocol and compares routes, blocked histories and tail flags with cached-search.
Full traces and every chronological candidate pair are in examples.json.

## Main21-bar example
Low values, high=low+1:
8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1.
Strict complete fractals at merged centers1,5,9,11,15,19 have sourceFX positions
0,1,2,3,4,5 respectively, with kinds top,bottom,top,bottom,top,bottom.

Start A=FX0(center1). Accept B=FX1(center5): gap4, min0,max10,
top[9,10],bottom[0,1], both interval inequalities pass.
Cache the ALREADY POST-skip alternative:
prefixFX=[0],A_fx=0,B=None,phase=SEEK_B,next_fx=2(center9).

Read FX2(center9): B5->C9 passes gap4,min0,max8,top[7,8],bottom[0,1].
The local history is now1->5; the still-provisional working pair is5->9.
Read FX3(center11):9->11 has gap2<4; extrema and interval comparisons pass,
but this local bottom cannot form the reverse stroke. Retain it as evidence.
Read FX4(center15): it is a higher top than working B=center9 (high9>8).
Mandatory extension tests5->15: gap10,min-1,max9,top[8,9],bottom[0,1].
Both interval inequalities pass; only the lower extreme bound fails because
bar11.low=-1<bottom5.low0. Block this route, retaining historical1->5->9.
Its state is prefixFX=[0,1],A_fx=1,B_fx=2,next_fx=5(center19).

Restore the saved POST-skip5 checkpoint, NOT the blocked state's cursor:
prefixFX=[0],A_fx=0,B=None,next_fx=2(center9). At center9 the candidate
has the same top kind as A1, so skip it. Center11 is a legal first end:
gap10,min-1,max10,top[9,10],bottom[-1,0]. Cache its skip alternative.
Center15 then passes11->15: gap4,min-1,max9; center19 passes15->19:
gap4,min-2,max9. At EOF local history is1->11->15, with working15->19
still provisional. Recovered route:1->11->15->19.

Exhausting all cached choices and seeds gives exactly FOUR distinct routes:
(1,11,15,19),(1,19),(11,15,19),(15,19).
Only the first two share boundaries1..19. Histories(1,5,9) and(5,9)
are blocked diagnostics, not viable EOF routes. Selected center intervals
cover each route's own boundary span; raw-bar/support-window coverage and
market confirmation are not inferred from that fact.

## Safe extension supplement
15 interval lows, high=low+2:
1,0,3,6,9,12,10,8,12,16,13,10,7,4,5.
Exact fractals: bottom1,top5,bottom7,top9,bottom13.
1->5 passes. Reverse5->7 fails gap2. Top9 exceeds top5 and1->9 passes,
so B must update5->9 while A remains1. Reverse9->13 passes gap4.
Output routes are(1,9,13),(9,13);(1,5) is not a viable final alternative
after mandatory extension. The EOF working9->13 remains provisional.

## Equal and tail supplements
The equal-bottom example has equal bottoms at5,11. Both legal keep/replace
states are retained, yielding(1,5),(1,11,15),(7,11,15),(11,15).
The first route has unresolved later movement; it is not a completed
whole-input partition. No universal first/last tie preference is adopted.

The tail example has lows1,0,3,6,9,12,10,11,13,14, width2. Complete
fractals are bottom1,top5,bottom6. Reverse5->6 fails gap1, and no later
complete top exists. Route(1,5) remains provisional even though later
bars have highs above center5.high14 (final bar high16). This is explicit
unresolved-tail evidence, not confirmation or a fabricated final top.

## Checks and source-index semantics
All adjacent intervals have strict joint movement and no inclusion. Strict
four-inequality fractals agree with direction-turn scanning. Each returned
route's pair checks pass, and price reflection gives identical endpoint
routes, event sequence, blocked histories and tail flags. SourceFX positions
are not feature IDs or raw anchors. For existing Fenxing records, a three-
merged-bar window[source_start,source_stop) has center=source_start+1;
the complete FenxingSeries source is retained even when a subset supplies
stroke endpoints. Cache checkpoints store full post-choice state and the
next unread sourceFX position; a replay may move backward in source time,
but does not reopen the same choice at the same input item.

Reproduce: python3 artifacts/mas/memo020-002b-d/examples.py
The runner writes only examples.json and numeric-review.md beside itself.
No unrelated broad suite was rerun. Parent owns memo/task/memory/event logs.

