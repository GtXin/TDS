"""Stdlib-only bounded study of memo020 v2; no detector or CC code is run.

Run from any cwd with Python >=3.11. Writes only ambiguity.json/ambiguity.md
beside this script. Every path uses the SAME first/last fractal centers.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
from pathlib import Path

Bar = tuple[int, int]  # low, high
Fractal = tuple[int, str]  # center, kind


def validate_bars(bars: list[Bar]) -> None:
    assert all(low < high for low, high in bars)
    for a, b in zip(bars, bars[1:]):
        assert not ((a[0] <= b[0] and a[1] >= b[1])
                    or (b[0] <= a[0] and b[1] >= a[1]))


def fractals(bars: list[Bar]) -> list[Fractal]:
    result = []
    for i in range(1, len(bars) - 1):
        a, b, c = bars[i - 1:i + 2]
        if all(b[j] > a[j] and b[j] > c[j] for j in (0, 1)):
            result.append((i, "top"))
        elif all(b[j] < a[j] and b[j] < c[j] for j in (0, 1)):
            result.append((i, "bottom"))
    return result


def edge(bars: list[Bar], a: Fractal, b: Fractal) -> bool:
    i, kind_i = a
    j, kind_j = b
    if j - i < 4 or kind_i == kind_j:
        return False
    t, z = (i, j) if kind_i == "top" else (j, i)
    low_t, high_t = bars[t]
    low_b, high_b = bars[z]
    return (
        high_t > high_b and low_b < low_t
        and max(h for _, h in bars[i:j + 1]) <= high_t
        and min(l for l, _ in bars[i:j + 1]) >= low_b
    )


def independent_path_check(bars: list[Bar], path: tuple[int, ...]) -> None:
    """Independent direct check; deliberately does not call edge/fractals."""
    kinds = []
    for i in path:
        before, middle, after = bars[i - 1:i + 2]
        if middle[0] > max(before[0], after[0]) and middle[1] > max(before[1], after[1]):
            kinds.append("top")
        else:
            assert middle[0] < min(before[0], after[0])
            assert middle[1] < min(before[1], after[1])
            kinds.append("bottom")
    for k, (i, j) in enumerate(zip(path, path[1:])):
        assert i + 4 <= j
        assert kinds[k] != kinds[k + 1]
        t = i if kinds[k] == "top" else j
        b = j if t == i else i
        assert bars[t][1] > bars[b][1] and bars[t][0] > bars[b][0]
        for low, high in bars[i:j + 1]:
            assert low >= bars[b][0] and high <= bars[t][1]
    directions = [kinds[k] == "bottom" for k in range(len(path) - 1)]
    assert all(a != b for a, b in zip(directions, directions[1:]))
    # The shared endpoints partition the entire fixed center interval.
    covered = set().union(*(set(range(i, j + 1)) for i, j in zip(path, path[1:])))
    assert covered == set(range(path[0], path[-1] + 1))


def analyze(bars: list[Bar]) -> dict:
    validate_bars(bars)
    fx = fractals(bars)
    assert len(fx) >= 2
    # Check the production contract's direction-turn characterization too.
    directions = [1 if b[0] > a[0] else -1 for a, b in zip(bars, bars[1:])]
    assert fx == [(i, "top" if directions[i - 1] == 1 else "bottom")
                  for i in range(1, len(bars) - 1) if directions[i - 1] != directions[i]]
    adj = {a[0]: [b[0] for b in fx if edge(bars, a, b)] for a in fx}
    start, end = fx[0][0], fx[-1][0]
    paths = []

    def visit(path: tuple[int, ...]) -> None:
        if path[-1] == end:
            independent_path_check(bars, path)
            paths.append(path)
        else:
            for nxt in adj[path[-1]]:
                visit((*path, nxt))

    visit((start,))
    longest = max(map(len, paths), default=0)
    maximal = [p for p in paths if not any(set(p) < set(q) for q in paths)]
    # Because time order is fixed, strict set inclusion exactly means refinement.
    return {
        "bars_low_high": bars, "fractals": fx, "boundaries": [start, end],
        "edges": [[i, j] for i, js in adj.items() for j in js],
        "all_full_paths": paths, "maximal_paths": maximal,
        "maximum_count_paths": [p for p in paths if len(p) == longest],
        "maximum_strokes": max(0, longest - 1),
        "same_kind_endpoint_extrema_ties": any(
            a[1] == b[1] and bars[a[0]][1 if a[1] == "top" else 0]
            == bars[b[0]][1 if b[1] == "top" else 0]
            for a, b in itertools.combinations(fx, 2)
        ),
    }


def bars_from_lows(lows: tuple[int, ...]) -> list[Bar]:
    return [(low, low + 1) for low in lows]


def interpolated(turn_values: tuple[int, ...]) -> list[Bar]:
    """Six strict extrema at 1,5,9,11,15,19; unit width after scale4."""
    centers = (1, 5, 9, 11, 15, 19)
    lows = [4 * turn_values[0] - 1, 4 * turn_values[0]]
    for i in range(5):
        span = centers[i + 1] - centers[i]
        start, delta = 4 * turn_values[i], 4 * (turn_values[i + 1] - turn_values[i])
        assert delta % span == 0
        lows.extend(start + delta * offset // span for offset in range(1, span + 1))
    lows.append(4 * turn_values[-1] + 1)
    return bars_from_lows(tuple(lows))


def main() -> None:
    coarse = analyze(bars_from_lows((8, 9, 8, 7, 6, 3, 4, 5, 6, 7, 6, 4, 2, 0, 1)))
    strong = analyze(bars_from_lows((8, 9, 8, 7, 5, 3, 4, 5, 6, 7, 4, 2, 3, 4, 5, 6, 5, 3, 1, 0, 1)))
    ties = analyze(bars_from_lows((8, 9, 8, 6, 3, 0, 1, 0, 2, 4, 6, 7, 5, 3, 1, -1, 0)))
    assert coarse["all_full_paths"] == [(1, 5, 9, 13), (1, 13)]
    assert strong["all_full_paths"] == [(1, 5, 9, 19), (1, 11, 15, 19), (1, 19)]
    assert len(strong["maximum_count_paths"]) == 2
    assert strong["maximal_paths"] == strong["maximum_count_paths"]
    assert not strong["same_kind_endpoint_extrema_ties"]
    assert len(ties["maximum_count_paths"]) >= 2
    assert ties["same_kind_endpoint_extrema_ties"]

    # Exhaust all 24 distinct-extrema assignments of this fixed small family.
    # This is NOT exhaustive over all interval sequences or all source algorithms.
    searched = []
    for middle in itertools.permutations(range(1, 5)):
        turns = (5, *middle, 0)
        if not all((a > b if i % 2 == 0 else a < b)
                   for i, (a, b) in enumerate(zip(turns, turns[1:]))):
            continue
        result = analyze(interpolated(turns))
        searched.append({"turn_values": turns, "maximum_strokes": result["maximum_strokes"],
                         "maximum_count_paths": result["maximum_count_paths"]})
    ambiguous = [x for x in searched if len(x["maximum_count_paths"]) > 1]
    assert ambiguous
    root = Path(__file__).resolve().parents[3]
    sources = ["docs/memo/memoWX_020_Chan_bi.md", "src/chanlab/algo/fenxing.py",
               "src/chanlab/algo/merged_kline.py", "mas/skills/computer-scientist/SKILL.md"]
    result = {
        "scope": "memo020 version2 six necessary structural rules, fixed first/last fractal centers",
        "python": platform.python_version(),
        "source_sha256": {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sources},
        "counterexamples": {"coarse_vs_refined": coarse, "no_tie_maximum_count": strong,
                            "equal_bottom_tie": ties},
        "bounded_family_search": {"permutations_considered": 24,
                                  "strict_zigzag_families": len(searched),
                                  "ambiguous_maximum_count_families": len(ambiguous),
                                  "results": searched},
        "checks": {"adjacent_noninclusion": True, "two_fractal_characterizations_agree": True,
                   "all_paths_independently_rechecked": True, "fixed_boundary_full_coverage": True,
                   "no_production_or_cc_execution": True},
    }
    folder = Path(__file__).resolve().parent
    (folder / "ambiguity.json").write_text(json.dumps(result, indent=2) + "\n")
    (folder / "ambiguity.md").write_text(REPORT + "\n")
    print(json.dumps({"all_checks": "passed", "strong_paths": strong["all_full_paths"],
                      "strict_families": len(searched), "ambiguous_families": len(ambiguous)}))


REPORT = """# Stroke endpoint-subset ambiguity study

## Model and scope
Input is a finite chronological series of nonzero integer price intervals [low,high],
with no inclusion between adjacent bars (equal-boundary enclosure also counts).
Every strict three-bar top/bottom is a candidate, including overlapping windows.
A valid directed edge joins opposite candidates with center gap>=4, endpoint
global extrema over their inclusive center-to-center interval, and both strict
center-bar inequalities. A path shares endpoints and alternates direction.
All compared paths have identical first/last candidate centers and cover the
whole center interval, so this is not merely different prefixes or tail handling.
All inputs are synthetic processed bars; this is a mathematical experiment, not
a production stroke implementation, a source-selection algorithm, or a CC run.

## Formalization
For chronological candidate centers i<j, require opposite kinds and j-i>=4.
Let T,B be their top/bottom centers. For every i<=k<=j, require
high[k]<=high[T] and low[k]>=low[B]. Also require high[T]>high[B]
and low[B]<low[T]. Paths are increasing center subsequences with every consecutive
pair passing that edge predicate. Opposite endpoints plus shared endpoints imply
alternating directions. The two strict interval inequalities follow from strict
fractals and endpoint global extrema; they are checked explicitly nevertheless.

## Counterexample without endpoint ties
Use low values (bar high=low+1):
8,9,8,7,5,3,4,5,6,7,4,2,3,4,5,6,5,3,1,0,1.
The exact candidate list is top1,bottom5,top9,bottom11,top15,bottom19.
Two valid full paths are (1,5,9,19) and (1,11,15,19); each has three strokes.
Same-type endpoint extreme prices are distinct. Span19-1=18 and gap>=4 imply
at most four strokes; top-to-bottom alternation requires an odd count, so the
maximum is three, attained by BOTH paths. They are also nonrefinable: inserting
all internal reversals would require the invalid gap9->11=2. Thus maximizing
stroke count or forbidding further endpoint insertion does not ensure uniqueness.
The direct coarse path (1,19) is a third valid path under the bare six rules.

## Additional cases
A 15-bar case has paths (1,13) and (1,5,9,13), showing coarse-vs-refined ambiguity.
A 17-bar case has equal-price bottom candidates at5,7, with distinct maximum-count
paths choosing one or the other. Ties matter, but the 21-bar witness proves that
tie-breaking alone is insufficient. All bar arrays, exact candidates, legal edges,
and enumerated full/maximal/maximum-count paths are in ambiguity.json.

## Search and checks
The script enumerates every fixed-boundary path in each candidate DAG, then checks
every returned path using an independent direct checker. Strict-fractal tests
are also cross-checked against joint-direction changes. It separately enumerates
all 24 assignments of four distinct interior extrema1..4 between fixed outer
extrema5,0 at centers1,5,9,11,15,19, retaining only strict zigzags. This bounded
family search is NOT exhaustive over all continuous bar sequences. JSON records
actual family and ambiguity counts, Python version and source snapshot hashes.
Reproduce: python3 artifacts/mas/bi-algorithm-study/ambiguity.py

## Consequences and limits
The six structural rules are necessary compatibility checks, not a unique subset
selection policy. A source-derived earliest-pair/extension/replacement rule may
choose among these paths or reject them for additional reasons; it must be stated
and analyzed separately. These experiments do not refute a fuller original-source
definition that imposes such additional selection rules. Boundary start/end,
equal extrema, provisional tails and behavior after revisions remain separate
specification choices. Full coverage here means the fixed center interval, not the
unconfirmed flanking bars outside its endpoint centers. Requiring every candidate
to be selected generally conflicts with gap>=4 and is not implied by the memo.

## Complexity
Let n be bars, m<=n-2 candidates, e legal edges. Strict-fractal scan is O(n).
This deliberately simple checker builds its DAG by O(m^2) interval scans, using
O(n*m^2) time and O(m+e) graph storage. Enumerating paths can be exponential in m;
independent validation is O(n) per returned full path. A proposed algorithm can
preprocess range minima/maxima in O(n log n) storage/time, check pairs in O(1),
and build the graph in O(m^2) time. DAG reachability/count capped at2 or a maximum-
count path can then be found in O(m+e), but the objective/tie policy is a NEW design
decision, not a consequence of the six rules. These bounds use the word-RAM model
for bounded integer input; this finite script is not a scalability benchmark.
"""


if __name__ == "__main__":
    main()
