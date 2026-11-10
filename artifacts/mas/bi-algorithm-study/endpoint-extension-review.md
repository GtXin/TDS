# Endpoint extension review under memo020's six conditions

## Scope and model

This review applies the explicit temporal correction: after a valid A->B,
before a valid reverse B->C is found, a later, more extreme candidate of B's
kind should extend the current stroke. Downward: lower bottom; upward: higher
top. This is an added temporal selection rule, not implied by the six pair/path
compatibility conditions alone. The Computer Scientist skill was explicitly
read and used. No production detector or CC code was executed.

Bars below are continuous chronological processed price intervals [x,x+1],
not endpoint-price sketches. Every adjacent pair is inclusion-free; strict
three-bar fractals, interval extrema, spacing and both endpoint inequalities
were checked. All indices are zero-based. JSON includes full bar arrays,
exact fractals, legal edges, fixed-boundary full paths and checks. Upward
duals use the exact price reflection [low,high]->[-high,-low].

## Core transition

Maintain A,B as the active stroke's current endpoints while scanning later
candidate F. Type categories are disjoint: F cannot simultaneously be B's
same-kind extension and an opposite-kind reverse endpoint.

- If F has B's kind and is strictly more extreme, propose B'=F and recheck
  the complete six-rule pair predicate A->B'. Commit atomically only if it
  passes. A later location preserves/increases the old gap, but does not
  alone preserve the interior extrema bound.
- If F has A's kind, test B->F. A failed pair does not erase either candidate.
  On success it is a valid reverse candidate; a rule is still needed to say
  whether the first such candidate commits prior structure irrevocably.
- A same-kind, less extreme F does not extend B under this correction.
- Equal extreme prices are outside the strict-more-extreme correction;
  retaining the first, retaining the last, and retaining alternatives are
  distinct policies. Do not silently introduce one.

If A->B' fails, retaining old A,B preserves a valid HISTORICAL prefix, but
does not establish a valid stroke covering the later range. Preserve failed
evidence and alternatives and report the new range as unresolved, or invoke
an explicitly defined recovery/backtracking rule. Reconsidering A is not
licensed by the endpoint-extension rule alone.

## Safe downward extension, with a too-close intervening top

Low values:

    8,9,6,4,2,0,4,7,5,3,1,-1,1,2,3,4,3

Exact fractals: A=top1, B1=bottom5, E=top7, B2=bottom11, C=top15.
A->B1 passes. B1->E fails because center gap2<4. B2 is lower than B1,
and A->B2 passes the entire pair check. B2->C then passes with gap4.
The full path over centers1..15 is (1,11,15). No branch at the earlier,
too-close E is needed to obtain this temporal extension.

## Why the update cannot be unconditional

Low values:

    8,9,6,4,2,0,5,11,8,5,2,-1,1,2,3,4,3

The exact fractal centers/kinds remain A top1, B1 bottom5, E top7,
B2 bottom11, C top15. A.high=10, B1.low=0, E.high=12, B2.low=-1.
A->B1 passes; B1->E still fails gap2. Thus no valid reverse endpoint
was found before the new lower B2. Nevertheless A->B2 FAILS: the
intervening E has high12>A.high10. Merely replacing B1 with B2 would
violate the endpoint-extrema condition. B2->C can be valid even though
A->B2 is invalid. There is no full six-rule path from center1 to center15
in this finite input. This is an unresolved-range case, not proof that the
new candidate's local bottom is invalid.

Sufficient condition: after a valid downward A->B, the update is safe if
B' is the lowest bar over A..B' and every high in that range stays<=A.high.
Strict endpoint-fractal geometry then supplies the two strict interval
inequalities; the gap cannot shrink. The mirrored conditions apply upward.
Maintaining running extrema can accelerate these checks but does not remove
the need to state them.

## First valid reverse endpoint does not prove permanent prefix stability

Low values:

    8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1

Exact fractals: A top1, B1 bottom5, C1 top9, B2 bottom11, C2 top15,
D bottom19. Both A->B1 and B1->C1 initially pass. Later:

- C1->B2 fails gap2.
- C2 is higher than C1, but B1->C2 fails because B2.low=-1<B1.low0.
- C1->D fails because C2.high9>C1.high8.

No full path over the fixed range1..19 retains B1. The valid full paths are
(1,11,15,19) and the coarse (1,19). Thus freezing A->B1 upon the first valid
C1 can preserve locally valid earlier strokes, but cannot be claimed to
guarantee later full coverage under the six conditions. An online policy
may intentionally leave later data unresolved; alternatively it may permit
rollback. Which behavior is intended remains an explicit design choice.
This is a conditional full-coverage counterexample, not a claim that an
unchanged earlier A->B1 interval retroactively violates its own pair checks.

## Equal-price case

Low values:

    8,9,6,4,2,0,4,7,5,3,1,0,1,2,3,4,3

B1 at5 and B2 at11 have the same bottom price0. Both A->B1 and A->B2
pass, but B1->C15 fails the interior maximum while B2->C15 passes.
The full path is (1,11,15). Therefore equality is materially relevant to
later pairing; it should not be treated as an irrelevant formatting tie.
This example does not establish that choosing the latest equal bottom is
universally correct.

## Checks and reproduction

All four cases and their four upward mirrors passed adjacent-noninclusion,
strict-fractal/direction-turn agreement, edge checks and independent full-path
checks using the stdlib baseline in ambiguity.py. The model is finite, fixed-bar,
exact integer arithmetic. It does not settle raw-bar revisions or confirmation.
Only the two endpoint-extension artifact files were written by this review;
the parent task owns repository task/memory/event-log updates.

Recheck the stored model results without writing files:

```sh
python3 - <<'PY'
import json, runpy
from pathlib import Path
p = Path('artifacts/mas/bi-algorithm-study')
model = runpy.run_path(str(p / 'ambiguity.py'))
data = json.loads((p / 'endpoint-extension-cases.json').read_text())
for name, expected in data['cases'].items():
    actual = model['analyze']([tuple(bar) for bar in expected['bars_low_high']])
    actual = json.loads(json.dumps(actual))
    for key, value in actual.items():
        assert value == expected[key], (name, key)
    assert all(expected['checks'].values())
print('8 reflected extension/prefix/equality cases rechecked')
PY
```

Time/space limits remain those of the existing finite enumerator; this review
does not claim a linear-time final stroke-selection algorithm.
