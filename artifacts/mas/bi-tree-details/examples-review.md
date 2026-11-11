# Active memo020002.b example review

## Scope and result

PASS: reviewed current002.a/003 and memo019002.b's structure, then checked
continuous integer intervals with an independent standalone sequential model.
This model follows the CURRENT note-based tree: one route, initialization
extreme tracking, failed candidates continue, submitted R is append-only,
EOF preserves an open cached stroke. It does not enumerate alternate routes,
restore checkpoints or kill a route on failed extension. No production Bi,
CC, broad random suite or new confirmation rule was used.

Executed4 full fixtures,4 prefix/resume snapshots and2 one-shot comparisons.
Every exact complete-fractal list was independently scanned by four strict
comparisons; all adjacent intervals have joint strict movement/no inclusion.
Each accepted pair was checked again against the full six-condition predicate.
Extension suffix decisions were compared with full-pair checks. Append-only
R and incremental/one-shot equivalence passed in the supplied continuation.
Only this delegated review file was written.

## Recommended concise example set for002.b

1. Move/reuse the existing19-bar complete trace as the sole main example,
   with one merged-center/sourceFX mapping table and reduced-check details.
2. Retain a short21-bar open-EOF example or cross-reference003's existing
   full array/table. Highlight why extension scans after CURRENT B rather
   than after the latest rejected candidate. Do not call this input blocked.
3. Two short rows for stage-specific equality, including their arrays.
4. A prefix/resume table based on the same19-bar main input covers zeroFX,
   oneFX, normal continuation and immutable R, avoiding extra unrelated data.

The19-bar normal illustration would be useful if needed: solid submitted5->13,
dashed cached13->17, all ranges/complete fractals visible. Do not reuse the old
cached-recovery graphic as if it demonstrated this sequential algorithm.
No new figure is necessary for equality or the prefix table.

## Main19-bar input and exact positions

All bars=[low,low+1], low values:

    9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7

| SourceFX position | Kind | Merged center | Center interval | Merged window |
|---:|---|---:|---|---|
| 0 | top | 1 | [10,11] | [0,3) |
| 1 | bottom | 2 | [0,1] | [1,4) |
| 2 | top | 3 | [9,10] | [2,5) |
| 3 | bottom | 4 | [1,2] | [3,6) |
| 4 | top | 5 | [12,13] | [4,7) |
| 5 | bottom | 9 | [2,3] | [8,11) |
| 6 | top | 11 | [7,8] | [10,13) |
| 7 | bottom | 13 | [0,1] | [12,15) |
| 8 | top | 17 | [8,9] | [16,19) |

SourceFX position is not feature ID, merged center or raw anchor. Current
Fenxing center is source_start+1; its three-bar source window points into
the exact merged sequence. The synthetic intervals do not define OHLC or
raw anchors.

### Sequential actions and reduced arithmetic

Start at top1. Bottom2 is gap1 away and fails. Top3.high10 is weaker than
top1.high11, so the local initialization rule keeps1. Bottom4 has gap3 and
fails; the full predicate also detects the earlier bottom2.low0<bottom4.low1.
Top5.high13 is more extreme than11, so pending start updates1->5.

First pair5->9: gap4; endpoint bottom9.low2 is the minimum over[5,9].
Initialization already guarantees top5 is the maximum. Independent full
range is[min2,max13]; top[12,13],bottom[2,3] also satisfy13>3 and2<12.
Cache5->9, Bi001S=9, R remains empty.

Reverse9->11 fails gap2. It does not move the current cached endpoint9.

Extension to bottom13: new bounds[0,13], scan ONLY after old endpoint9:

    half-open suffix[10,14): [4,5],[7,8],[3,4],[0,1]
    suffix minimum=0, maximum=8

The suffix fits the new bounds. The inherited prefix[5,9] still fits because
the bottom bound relaxes from2 to0; distance cannot shrink. Update cached
endpoint9->13 and Bi001S=13. Full-pair oracle gives gap8,min0,max13.

Reverse13->17: gap4; full center range[13,17] has min0,max9. Both endpoint
extrema pass; top[8,9],bottom[0,1] give9>1 and0<8. First append a COPY of
old cache5->13 to R, then rotate cache to13->17, Bi001S=17, E unset.

EOF is NORMAL:

| Field | Merged-center representation | Stored sourceFX positions |
|---|---|---|
| Final R | [(5,13)] | [(4,7)] |
| Unfinished Bi002 | (13,17) | (7,8) |
| Bi001S | 17 | 8 |
| Bi001E | unset | unset |
| Next complete-FX position | after last source candidate | 9 |

Head merged[0,5) and tail[18,19) lie outside the connected stroke centers.
Bar18 is nevertheless top17's right evidence neighbor. EOF neither appends
cached13->17 to R nor fabricates another complete fractal.

## Open21-bar input: failed candidates remain ordinary continuation

All bars=[low,low+1], low values:

    8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1

Exact sourceFX positions0..5 map to centers top1,bottom5,top9,bottom11,
top15,bottom19. After1->5 then legal reverse5->9, R=[(1,5)] and current
cache=(5,9). SourceFX references are R=[(0,1)], cache=(1,2).

- Reverse9->11: gap2, so continue with cache5->9 unchanged.
- Extension9->15: proposed cache5->15 has bounds[0,9]. The correct suffix
  is[10,16): its minimum=-1 at bar11, maximum=9. It fails the lower bound,
  so do NOT replace cached endpoint9 and do NOT stop traversal.
- Crucial wrong-suffix comparison: scanning only AFTER rejected candidate11
  would use[12,16), min1,max9, incorrectly passing. The lower bar11 still
  lies after CURRENT cached endpoint9 and must remain included.
- Reverse9->19: gap10; center interval[9,19] has min-2,max9. Top9.high8
  is not the maximum because top15.high9 is inside; reverse fails.

EOF returns R=[(1,5)], open cache=(5,9), Bi001S=9, E unset, nextFX=6.
Head[0,1), tail[10,21) remain uncovered. Rechecking R/cache themselves
passes; later failed candidates are outside the existing cache's5..9
center range. This is not a failed output merely because the tail is open,
and it is not evidence that future completion is guaranteed.

## Stage-specific equality

| Stage | Low values, high=low+1 | Exact centers/kinds | Checked action |
|---|---|---|---|
| Initial equal keeps old | 9,10,0,10,9 | top1,bottom2,top3 | 1->2 gap1 fails; top1/top3 price11 equal; start stays1, no cache, nextFX3 |
| Pending equal replaces valid end | 1,0,3,6,9,10,8,5,8,10,9 | bottom1,top5,bottom7,top9 | 1->5 passes;5->7 gap2 fails; top5/top9 price11 equal; valid1->9 replaces end5->9, R empty, nextFX4 |

For pending equality, the suffix after current endpoint5 is[6,10), with
min5,max11 inside new bounds[0,11]. The complete1->9 range has min0,max11
and gap8. Its sourceFX cache is(0,3), Bi001S=3. These two equality actions
belong to different stages; raw-anchor FIRST/LAST is unrelated.

## Empty/single complete-FX and prefix-safe resume

Reuse MAIN19's interval prefix. A valid input with ZERO complete fractals
is not an empty/invalid MergedKlineSeries; the2-bar input is valid but has
no complete three-bar window.

| Batch snapshot | Complete sourceFX centers | Final R | Cache / start | NextFX |
|---|---|---|---|---:|
| First2 merged bars, lows9,10 | none | empty | cache empty;S unset | 0 |
| Append low0: first3 bars | top1 | empty | cache empty;S=center1/FX0 | 1 |
| Append remaining MAIN19 | 1,2,3,4,5,9,11,13,17 | [(5,13)] | cache13->17;S=17 | 9 |
| Append lows9,10,12,11 at indices19..22 | previous nine plus bottom18,top21 | SAME [(5,13)] | cache extends13->21;S=21 | 11 |

All old merged bars and complete fractals remain exact prefixes. On the last
append, newly complete bottom18 has sourceFX position9 even though merged
center18 was already in the previous batch as an incomplete tail position.
Reverse17->18 fails gap1. Top21 then extends pending13->17 to13->21:
suffix[18,22) has min7,max13 inside new bounds[0,13]. R's copied pair5->13
is unchanged. Stored sourceFX R stays[(4,7)], cache changes(7,8)->(7,10).
New tail[22,23) remains outside center21 but supplies its right neighbor.

Continuation from zeroFX must initialize S when the first new complete FX
appears, then advance the FX cursor. It must not clear R/work state or try
to pair against an unset S. Continuing the later batches from the saved FX
cursor gave the same complete states as processing the19/23-bar snapshots
in one pass. No new complete FX means normal return with unchanged work
state; no EOF empty loop. Historical input changes violate this example's
append-only assumptions and require a separate revision protocol.

## Limits

This evidence checks arithmetic and the stated sequential policy. It does
not prove unique Chan stroke selection, future completion, safe permanent
confirmation, or prefix stability under upstream revisions. Current028/
production Bi still follow the historical algorithm and were not invoked.

## Final review of assembled section-002b.md

PASS. Read the complete assembled002.b draft. Its19-bar array and all9
strictFX positions match the checked input, including R sourceFX(4,7),
cache(7,8), nextFX9. The normal-extension suffix M10..M13 has min0,max8
inside[0,13]. The21-bar suffix M10..M15 has min-1, while the incorrect
M12..M15 suffix has min1, so the stated missed-boundary explanation is
accurate. First-pair windows[4,7),[8,11) leave exactly M7 independent.
The equality rows preserve their different stage actions. Main-prefix
2->3->19 resume correctly processes zeroFX, oneFX, then8 additionalFX,
without reinitializing R or rereading the firstFX. OpenEOF semantics,
append-only result values and merged-center versus sourceFX positions
are consistent. No numerical or scope mismatch found; no figure needed.
This last pass was a read-only draft comparison, not another model run.
