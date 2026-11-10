"""Isolated finite model of memo020 v2's six conditions, not a detector.

Uses exact Fraction scalar paths and constant-width merged intervals. It does
not execute imported CC code or modify production classes. Run from any cwd.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
import json


@dataclass(frozen=True)
class Interval:
    low: Fraction
    high: Fraction


@dataclass(frozen=True)
class Fractal:
    center: int
    kind: str
    price: Fraction


def input_from_scalar(values: list[int | Fraction]) -> tuple[Interval, ...]:
    result = tuple(Interval(Fraction(v), Fraction(v) + 2) for v in values)
    for i, (a, b) in enumerate(zip(result, result[1:])):
        assert (a.low < b.low and a.high < b.high) or (
            a.low > b.low and a.high > b.high
        ), (i, a, b)
    return result


def interpolate(points: list[tuple[int, int]]) -> list[Fraction]:
    assert points[0][0] == 0
    result: list[Fraction] = []
    for (a, va), (b, vb) in zip(points, points[1:]):
        assert b > a and va != vb
        result.extend(Fraction(va) + Fraction(vb - va, b - a) * (j - a)
                      for j in range(a, b))
    result.append(Fraction(points[-1][1]))
    return result


def scan(bars: tuple[Interval, ...]) -> tuple[Fractal, ...]:
    result: list[Fractal] = []
    for i in range(1, len(bars) - 1):
        a, b, c = bars[i - 1:i + 2]
        if b.low > max(a.low, c.low) and b.high > max(a.high, c.high):
            result.append(Fractal(i, "top", b.high))
        elif b.low < min(a.low, c.low) and b.high < min(a.high, c.high):
            result.append(Fractal(i, "bottom", b.low))
    return tuple(result)


def rejection_reasons(bars: tuple[Interval, ...], a: Fractal,
                      b: Fractal) -> list[str]:
    reasons: list[str] = []
    if a.center >= b.center:
        return ["not_chronological"]
    if a.kind == b.kind:
        return ["same_kind"]
    if b.center - a.center < 4:
        reasons.append("spacing_lt_4")
    top = a if a.kind == "top" else b
    bottom = b if a.kind == "top" else a
    t, q = bars[top.center], bars[bottom.center]
    if not (t.high > q.high and q.low < t.low):
        reasons.append("endpoint_interval_order")
    span = bars[a.center:b.center + 1]
    if max(x.high for x in span) > t.high:
        reasons.append("interior_high_exceeds_top")
    if min(x.low for x in span) < q.low:
        reasons.append("interior_low_below_bottom")
    return reasons


def graph(bars: tuple[Interval, ...], fs: tuple[Fractal, ...]) -> dict[int, list[int]]:
    return {a.center: [b.center for b in fs if not rejection_reasons(bars, a, b)]
            for a in fs}


def longest_path(edges: dict[int, list[int]], start: int,
                 end: int | None = None) -> tuple[int, ...]:
    """One maximum-edge path; lexicographically earliest center tuple breaks ties.

    This tie/objective is an explicitly invented engineering policy, not Chan.
    """
    best = {start: (start,)}
    for u in sorted(edges):
        if u not in best:
            continue
        for v in edges[u]:
            candidate = best[u] + (v,)
            previous = best.get(v)
            if previous is None or (-len(candidate), candidate) < (-len(previous), previous):
                best[v] = candidate
    if end is not None:
        return best.get(end, ())
    return min(best.values(), key=lambda p: (-len(p), p))


def assert_path(bars: tuple[Interval, ...], fs: tuple[Fractal, ...],
                centers: tuple[int, ...]) -> None:
    lookup = {f.center: f for f in fs}
    assert all(not rejection_reasons(bars, lookup[a], lookup[b])
               for a, b in zip(centers, centers[1:])), centers


def describe(values: list[int | Fraction]) -> dict:
    bars = input_from_scalar(values)
    fs = scan(bars)
    return {"bars_low_high": [[x.low, x.high] for x in bars],
            "fractals": [asdict(x) for x in fs], "valid_edges": graph(bars, fs)}


def main() -> None:
    report: dict = {"scope": "six memo020 v2 local conditions; no canonical-policy claim"}
    # Same-kind replacement and useful rejected opposite.
    vals = [14,15,12,9,6,3,0,2,4,6,8,10,4,-2,5,12,11]
    bars = input_from_scalar(vals)
    fs = scan(bars)
    assert [(f.center, f.kind) for f in fs] == [
        (1,"top"),(6,"bottom"),(11,"top"),(13,"bottom"),(15,"top")]
    lookup = {f.center: f for f in fs}
    assert_path(bars, fs, (1, 6, 11))
    assert rejection_reasons(bars, lookup[11], lookup[13]) == ["spacing_lt_4"]
    assert lookup[15].price > lookup[11].price
    assert rejection_reasons(bars, lookup[6], lookup[15]) == ["interior_low_below_bottom"]
    assert_path(bars, fs, (1, 13))
    example = describe(vals)
    example.update({"labels": {"P":1,"Q":6,"R":11,"S":13,"T":15},
                    "valid_initial_path": [1,6,11],
                    "blind_same_kind_replacement": [1,6,15],
                    "replacement_failure": ["interior_low_below_bottom"],
                    "alternative_reaches_S": [1,13]})
    report["replacement_breaks_previous_edge"] = example
    # Arbitrarily deep rollback family, demonstrated at three internal tops.
    points = [(0,99),(1,100),(6,0),(11,10),(16,1),(21,20),(26,2),(31,30),(33,-10),(34,-9)]
    vals2 = interpolate(points)
    bars2 = input_from_scalar(vals2); fs2 = scan(bars2)
    lookup2 = {f.center: f for f in fs2}
    old = (1,6,11,16,21,26,31)
    assert_path(bars2, fs2, old)
    incoming = [f.center for f in fs2 if f.center < 33
                and not rejection_reasons(bars2, f, lookup2[33])]
    assert incoming == [1], incoming
    deep = describe(vals2)
    deep.update({"old_path":old, "target_bottom":33,
                 "valid_predecessors_of_target":[1],
                 "suffix_endpoints_to_remove_if_policy_requires_target":old[1:],
                 "new_path_if_policy_requires_target":[1,33]})
    report["deep_rollback_conditional_on_tail_policy"] = deep
    # Equal tops: choosing latest can block a near-future bottom.
    vals3 = interpolate([(0,1),(1,0),(5,12),(7,6),(9,12),(12,3),(13,4)])
    bars3 = input_from_scalar(vals3); fs3 = scan(bars3)
    assert_path(bars3, fs3, (1,5,12)); assert_path(bars3, fs3, (1,9))
    lookup3 = {f.center:f for f in fs3}
    assert rejection_reasons(bars3,lookup3[9],lookup3[12]) == ["spacing_lt_4"]
    equal_late = describe(vals3)
    equal_late.update({"equal_top_centers":[5,9],"earliest_can_reach":[1,5,12],
                       "latest_cannot_append_12":[1,9]})
    report["equal_latest_can_lose_future_edge"] = equal_late
    # Equal tops: retaining too-close earlier top can lose an incoming edge.
    vals4 = interpolate([(0,1),(1,0),(3,8),(5,4),(7,8),(8,7)])
    bars4 = input_from_scalar(vals4); fs4 = scan(bars4)
    lookup4 = {f.center:f for f in fs4}
    assert rejection_reasons(bars4,lookup4[1],lookup4[3]) == ["spacing_lt_4"]
    assert_path(bars4, fs4, (1,7))
    early = describe(vals4)
    early.update({"equal_top_centers":[3,7],"first_top_too_close":3,
                  "later_top_valid_from_start":[1,7]})
    report["equal_earliest_prefilter_can_lose_incoming_edge"] = early
    # Even fixed first/last endpoints + maximum edge count need a tie policy.
    vals5 = interpolate([(0,1),(1,0),(5,12),(7,6),(9,12),(14,2),(15,3)])
    bars5 = input_from_scalar(vals5); fs5 = scan(bars5)
    assert_path(bars5, fs5, (1,5,14)); assert_path(bars5, fs5, (1,9,14))
    assert len(longest_path(graph(bars5,fs5),1,14)) == 3
    ambiguous = describe(vals5)
    ambiguous.update({"same_first_and_last":[1,14],
                       "distinct_maximum_edge_paths":[[1,5,14],[1,9,14]],
                       "invented_lexicographic_tie_result":longest_path(graph(bars5,fs5),1,14)})
    report["nonuniqueness_even_with_fixed_boundary_and_max_count"] = ambiguous
    # Differential graph DP against complete path enumeration on these cases.
    all_cases = [(bars,fs),(bars2,fs2),(bars3,fs3),(bars4,fs4),(bars5,fs5)]
    enumerated = 0
    for b, f in all_cases:
        g=graph(b,f)
        def walk(path):
            yield path
            for nxt in g[path[-1]]:
                yield from walk(path+(nxt,))
        for start in g:
            paths=list(walk((start,))); enumerated += len(paths)
            want=min(paths,key=lambda p:(-len(p),p))
            assert longest_path(g,start)==want
            for end in g:
                choices=[p for p in paths if p[-1]==end]
                expected=min(choices,key=lambda p:(-len(p),p)) if choices else ()
                assert longest_path(g,start,end)==expected
    report["checks"]={"continuous_examples":5,"all_adjacent_pairs_strict":True,
                       "all_fractals_scanned":True,"DP_matches_enumeration_paths":enumerated,
                       "production_or_CC_execution":False}
    destination=Path(__file__).with_suffix('.json')
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2,
                                    default=lambda x: int(x) if x.denominator==1 else str(x))+'\n')
    print(json.dumps(report["checks"],ensure_ascii=False))
    print(destination)


if __name__ == '__main__':
    main()
