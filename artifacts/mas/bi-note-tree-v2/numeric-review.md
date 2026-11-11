# Note-based sequential stroke tree: numerical review

## Scope

Computer Scientist review of fixed chronological processed intervals and the
user's note-based sequential working states. This is not all-route enumeration,
not an initial-pair lookahead, not a production Bi run and not a financial or
canonical-theory correctness claim. No OHLC or raw anchor is invented.
Standalone integer arithmetic checked strict three-bar fractals, no adjacent
inclusion, every listed pair's distance, both center-interval inequalities and
all center-to-center interior extrema. Price reflection gives the same pair
accept/reject decisions. Root owns any memo, task, memory or event-log edits.

## One continuous19-bar main example

Let high=low+1, with zero-based merged positions:

```text
index: 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
low:   9 10  0  9  1 12 11  8  5  2  4  7  3  0  2  4  6  8  7
```

Every adjacent low differs, so high and low move strictly together and no
adjacent inclusion occurs. The COMPLETE strict-fractal list is:

| SourceFX position | Kind | Merged center | Center interval | Price | Merged window |
|---:|---|---:|---|---:|---|
| 0 | top | 1 | [10,11] | 11 | [0,3) |
| 1 | bottom | 2 | [0,1] | 0 | [1,4) |
| 2 | top | 3 | [9,10] | 10 | [2,5) |
| 3 | bottom | 4 | [1,2] | 1 | [3,6) |
| 4 | top | 5 | [12,13] | 13 | [4,7) |
| 5 | bottom | 9 | [2,3] | 2 | [8,11) |
| 6 | top | 11 | [7,8] | 8 | [10,13) |
| 7 | bottom | 13 | [0,1] | 0 | [12,15) |
| 8 | top | 17 | [8,9] | 9 | [16,19) |

SourceFX positions are sequence positions, not feature IDs or raw anchors.
All later state tables use merged centers for readability.

### Initialization without lookahead

Start with pending top1(high11). Bottom2 is opposite but1->2 has gap1,
so no stroke. Top3(high10) is weaker and the local initialization rule keeps
top1. Bottom4 has gap3 from top1 and also has an earlier lower interior bar2;
it is not a valid endpoint. Top5(high13) is more extreme than top1(high11),
so the pending start updates to5. No stroke has been accepted at this point.
This example demonstrates the local policy, not a general proof that weaker
initial candidates can always be permanently discarded without losing routes.

### Successful first pair, extension and rotation

| Event | Gap | Inclusive range [min low,max high] | Result |
|---|---:|---|---|
| top1->bottom2 | 1 | [0,11] | Distance fails; other pair checks pass |
| top1->bottom4 | 3 | [0,11] | Distance and lower-extreme bound fail |
| top5->bottom9 | 4 | [2,13] | Pass:13>3 and2<12; both extrema valid |
| bottom9->top11 | 2 | [2,8] | Distance fails; interval/extrema checks pass |
| top5->bottom13 | 8 | [0,13] | Pass:13>1 and0<12; both extrema valid |
| bottom13->top17 | 4 | [0,9] | Pass:9>1 and0<8; both extrema valid |

When bottom9 appears, save pending stroke5->9. Top11 is too close to9
to form a reverse stroke. The lower bottom13 then passes the FULL5->13
recheck and extends the pending endpoint9->13, without changing start5.
Top17 is the first legal reverse endpoint after13. Only then record the
previous5->13 in result R and rotate the pending stroke to13->17.

Using the user's two-buffer names, the required local states are:

| After event | Recorded R | Pending Bi002 | Bi001 start | Bi001 end |
|---|---|---|---|---|
| initialization reaches top5 | empty | empty | 5 | unset |
| first pair5->9 | empty | (5,9) | 9 | unset |
| rejected reverse top11 | empty | (5,9) | 9 | unset |
| extension to bottom13 | empty | (5,13) | 13 | unset |
| legal reverse top17 and rotation | (5,13) | (13,17) | 17 | unset |

During the last rotation, candidate Bi001=(13,17) must first be formed;
record old Bi002, move that new pair into Bi002, then start a fresh Bi001
at17 with its end unset. The post-rotation singleton17 is not another stroke.
EOF leaves R=(5->13), pending13->17, and unresolved tail position18.
Bar18 still supplies the right neighbor needed to establish top17.
Head positions0..4 precede the selected start5 and are outside the stroke
geometry. In sourceFX POSITION terms, R contains(4,7), pending is(7,8),
and the fresh singleton start is8; merged centers must not replace these
source references in stored endpoint fields.
Local recording of R is not a new market-confirmation field or a proof of
permanent prefix stability.

### Endpoint-window distance check

The first pair's windows are[4,7) and[8,11), with independent bar7.
The rejected reverse9->11 has overlapping windows[8,11),[10,13).
The successful extended pair5->13 uses[4,7),[12,15), with bars7..11
belonging to neither window. The reverse13->17 uses[12,15),[16,19),
with independent bar15. All extrema checks use the inclusive CENTER range,
not the endpoint windows' outward flanks.

## Existing15-bar extension example also remains numerically valid

For low=[1,0,3,6,9,12,10,8,12,16,13,10,7,4,5], high=low+2,
all strict fractals are bottom1,top5,bottom7,top9,bottom13.
1->5 passes gap4/range[0,14]. Reverse5->7 fails gap2. New top9 has
high18>old top5.high14;1->9 passes gap8/range[0,18]. Reverse9->13
passes gap4/range[4,18]. The local result is R=(1->9), pending9->13,
with a fresh singleton start13 and no accepted end for that next stroke.

## Existing7-bar initialization example

For low=[9,10,0,9,1,12,11], high=low+1, exact strict fractals are
top1,bottom2,top3,bottom4,top5. No pair has yet been accepted:1->2 fails
gap1,1->4 fails gap3 (and the interior low bound). Weaker top3 is ignored
locally; stronger top5 updates the pending start. There is no C or Bi002.

##21-bar input is an invalid-extension boundary, not a normal main trace

For low=[8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1],
high=low+1, exact fractals are top1,bottom5,top9,bottom11,top15,bottom19.
1->5 passes gap4/range[0,10],5->9 passes gap4/range[0,8]. Reverse9->11
fails gap2. The higher top15 triggers an attempted5->15 extension, but
its center range has min low-1<bottom5.low0. Distance10, relative intervals
and upper extreme all pass; only the lower extreme fails. A transition
must not install invalid5->15. This arithmetic does not select a recovery
policy or turn the old5->9 into a stroke covering all later input.

## Check result

PASS: all four continuous inputs' exact fractal lists, listed pair decisions,
range values and source-window distances checked; mirrored pair decisions
agree. No broad Monte Carlo, production Bi or CC execution. Only this review
file was created by the delegated check.

## Additional stage-specific equality fixtures

These two targeted checks distinguish equality at initialization from equality
of a pending stroke end. They illustrate the specified local actions, not a
new all-route policy or a general completeness proof. Both use high=low+1,
strict complete three-bar fractals and adjacent inclusion-free intervals.

### Pending end: equal-price latest valid replacement

Low values:[1,0,3,6,9,10,8,5,8,10,9].
Exact fractals:bottom1,top5,bottom7,top9. Their windows are respectively
[0,3),[4,7),[6,9),[8,11).

- 1->5: center gap4, inclusive range[0,11], top[10,11], bottom[0,1];
  both strict interval inequalities and endpoint extrema pass.
- 5->7: center gap2, range[5,11]; the interval and extrema checks pass,
  but the reverse stroke fails the required distance.
- Top5 and top9 both have price11. The proposed1->9 has gap8 and
  range[0,11], again satisfying both inequalities and extrema bounds.
  The specified pending-end rule therefore updates end5->9. Bi002 becomes
  (1,9), Bi001's fresh start follows to9, and its end remains unset.
  No reverse stroke has yet been accepted, so R remains empty.

### Initialization: equal-price start keeps the old point

Low values:[9,10,0,10,9].
Exact fractals:top1,bottom2,top3, with windows[0,3),[1,4),[2,5).
1->2 has gap1 and range[0,11]; interval/extrema conditions pass but
distance fails. Top1 and top3 both have price11. Under the stated
initialization rule, top3 is not MORE, so pending start stays1. No first
pair or Bi002 exists. This local keep-old action is distinct from the
pending-end fixture's valid equal-price replacement; do not silently
apply one equality action to both stages.

Additional execution result:PASS exactly2 targeted equality fixtures,
4 opposite-kind pair checks,2 endpoint-price equality checks. Their exact
fractal lists and adjacent-noninclusion were checked. No broad suite,
production model or extra mirror batch was run for this addition.
