# Memo020 active continuation and output consistency review

## Scope and verdict

The current active examples agree with the sequential open-tail algorithm.
The19-bar normal and21-bar open outputs match decomposition-checks.json.
Additional directed checks below clarify the exact saved state, return
values and valid prefix snapshots. No memo, production code, tests, prior
artifacts, logs or memory were changed by this reviewer.

The local execution extracted ONLY the function definitions from
check_decomposition.py using AST, without executing its top-level fixtures,
report writer or broad tests.17 local scan calls covered7 staged snapshots,
their7 full-predicate one-shot comparisons,1 unchanged-snapshot replay and
the21-bar reduced/full pair of runs. An independent direction-turn list
agreed with each snapshot's complete strict-fractal list. Existing R values
remained unchanged after later cache extension. All checks passed.

## One continuous example through all meaningful phases

Use MAIN19, with high=low+1:

    9,10,0,9,1,12,11,8,5,2,4,7,3,0,2,4,6,8,7

Its exact sourceFX positions0..8 map to merged centers
top1,bottom2,top3,bottom4,top5,bottom9,top11,bottom13,top17.
Extend the SAME continuous input with lows9,10,12,11 at positions19..22.
Two new complete fractals are bottom18 at sourceFX9 and top21 at sourceFX10.

The table's R/cache/S columns use SOURCE-FX positions; parentheses after
them give merged centers. R=[] remains an empty final result even when a
valid stroke is already present in the unfinished cache.

| Merged length N | Complete FX count | R | Bi002/cache | S | NextFX | Unresolved merged ranges |
|---:|---:|---|---|---|---:|---|
| 2 | 0 | [] | none | unset | 0 | all[0,2) |
| 3 | 1 | [] | none | 0(center1) | 1 | all[0,3) |
| 11 | 6 | [] | (4,5), centers5->9 | 5(center9) | 6 | head[0,5), tail[10,11) |
| 12 | 6 | [] | (4,5), centers5->9 | 5(center9) | 6 | head[0,5), tail[10,12) |
| 15 | 8 | [] | (4,7), centers5->13 | 7(center13) | 8 | head[0,5), tail[14,15) |
| 19 | 9 | [(4,7)], centers5->13 | (7,8), centers13->17 | 8(center17) | 9 | head[0,5), tail[18,19) |
| 23 | 11 | SAME[(4,7)] | (7,10), centers13->21 | 10(center21) | 11 | head[0,5), tail[22,23) |

All7 resumed states equal their full-predicate one-shot states on the same
complete current snapshots, including saved merged/FX prefixes. No batch
reinitializes R or repeats previously read FX. The third phase N=11 makes
the first cached stroke explicit; N=19 distinguishes committed R from the
unfinished reverse cache. N=23 shows that extending that cache leaves the
previously committed endpoint tuple(4,7) unchanged.

At N=15, extension from current cache endpoint center9 to bottom13 scans
merged[10,14), min low0/max high8, within new bounds[0,13]. At N=23,
new bottom18 fails the reverse gap17->18=1. New top21 then extends the
cache by checking merged[18,22), min low7/max high13, within[0,13].
These starts follow CURRENT cached B, not the most recently rejected FX.

The newly complete bottom18 was an incomplete tail position in the previous
N=19 batch. It is read at NEW sourceFX position9; resuming by requiring
all new merged centers>=oldN would incorrectly miss it. Resume by saved FX
cursor with verified complete-FX prefix, as the active tree specifies.

## No new complete FX: core state versus output/context

The N=11->N=12 transition is a precise valid example. Appending merged11
creates no new complete FX because center11 still lacks its right neighbor.
R, cache, S and nextFX remain exactly the same. Nevertheless:

- current N changes11->12;
- saved processed-source context must include the new merged bar;
- unresolved tail changes[10,11)->[10,12).

Thus say "保留R、缓存和FX读取位置，按当前N更新未决范围及来源上下文",
not "整个旧输出原样返回". A repeat call on the IDENTICAL N=12 snapshot
was separately checked: all saved model values and unresolved ranges agree.
That is idempotence for the same snapshot. No-new-FX append is only
idempotent for the core work fields, not the entire returned report/context.
EOF itself never appends the open cache to R.

##21-bar open tail

For high=low+1 and lows

    8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1

the exact sourceFX list is centers1top,5bottom,9top,11bottom,15top,19bottom.
Output: R=[(0,1)] centers1->5; cache=(1,2) centers5->9; S=2(center9);
nextFX=6; unresolved head[0,1), tail[10,21). These are normal open-EOF
results, not a blocked-search outcome or a whole-input completed partition.
The reduced and full-predicate one-shot states matched the saved artifact.

Extension to top15 checks merged[10,16): min-1/max9 violates lower0.
Starting incorrectly after rejected bottom11 would use[12,16), min1/max9,
and incorrectly pass. Later reverse9->19 has max9 at top15 above cached
top9.high8, so it also fails and traversal continues normally to EOF.

## Model-empty fixture is outside the nonempty source contract

check_decomposition.py:103 explicitly includes empty=[] and its reflected
empty fixture. Its split loop at122 also tests cut0 for MAIN19 and OPEN21.
These are mathematical empty-list control probes, NOT valid nonempty
MergedKlineSeries instances. MergedKlineSeries._validate_result rejects
an empty klines tuple. Normative no-FX examples should use N=1 or N=2
valid merged bars; the table above uses N=2.

Consequently the stored22 fixture count includes2 zero-merged probes;
the42 split points include2 zero-merged prefix probes. The remaining
20 fixtures/40 splits are nonempty interval-model cases, NOT automatically
production source-provenance tests. Keep the original evidence intact but
label these scopes rather than claiming22/42 production-contract inputs.
The model's validate/source code checks geometry, not the real raw->merged
source chain, and view() omits old_v/old_fx and unresolved ranges. Equality
of view() alone cannot establish full-report or provenance-context equality.

## Recommendations for active memo prose

Use the stage table above, or its N=2,3,11,19,23 subset plus the N=11->12
tail note, to make saved/returned state concrete. Always specify whether
an endpoint number is a sourceFX position or merged center. R entries are
immutable copied endpoint values; caches are replaced rather than shared
mutable aliases. Valid resume requires unchanged raw/merged/complete-FX
and rule/source prefixes, not merely matching endpoint prices. A changed
prefix remains a revision error; this review establishes no revision API.
Input count zeroFX is legitimate, but zero merged must not be silently
substituted for the formal source contract. No production execution or
general future-completion claim follows from these directed interval checks.

Status: initial review complete; awaiting the root's assembled draft for
the final consistency pass.

## Assembled draft review

Read section-002b.md and active sections of draft-memo.md. PASS numerical
and state-flow review: all7 stage rows, sourceFX positions, unresolved
ranges, N=11->12 behavior, newly complete FX9 at merged18, appended
cache13->21, unchanged R and21-bar open-EOF behavior match the checks
above. The draft now explicitly requires nonempty merged input while
allowing zeroFX, returns the same complete immutable Q consumed by resume,
copies mutable work lists before appending, refreshes current source
context/unresolved at EOF, and avoids adding repeated EOF evidence.
Each read FX has one evidence item, including initialFX; hence the counts
0,1,6,6,8,9,11 in the stage table are consistent.

One content-equivalence clarification was sent to root: per-FX recording
once proves evidence count/order consistency, but equality of evidence
CONTENT also presupposes deterministic records of stable source/FX
positions, pre-action work values and checked prefix facts. Such records
must not embed call time, batch N or the then-current whole-snapshot object
as part of their comparison semantics. Under that intended local-evidence
contract, the same-state/per-FX induction gives identical evidence and
current-input source-context content after one-shot or resumed execution;
object identity is not required. The draft's current003 dependency argument
supports this intention; an explicit clause would make the boundary clear.

Minor wording recommendation: pending equal-end example should say
"缓存更新为M1->M9" rather than "缓存可更新", since a passed check triggers
the deterministic update rather than an optional candidate branch.
This final draft pass was read-only comparison; the new frozen-Q model
and any additional execution/check counts are owned by root and have not
been claimed as this reviewer's17 prior local scan calls.
