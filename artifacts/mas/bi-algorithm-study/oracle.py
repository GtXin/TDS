"""Isolated specification model, not the TDS Bi detector or a CC execution."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
Bar = tuple[int, int]
Fractal = tuple[int, str]


def validate_input(bars: tuple[Bar, ...]) -> None:
    assert all(lo <= hi for lo, hi in bars)
    for (la, ha), (lb, hb) in zip(bars, bars[1:]):
        assert (la < lb and ha < hb) or (la > lb and ha > hb)


def fractals(bars: tuple[Bar, ...]) -> tuple[Fractal, ...]:
    result = []
    for k in range(1, len(bars) - 1):
        a, b, c = bars[k - 1 : k + 2]
        if b[0] > a[0] and b[0] > c[0] and b[1] > a[1] and b[1] > c[1]:
            result.append((k, "top"))
        elif b[0] < a[0] and b[0] < c[0] and b[1] < a[1] and b[1] < c[1]:
            result.append((k, "bottom"))
    return tuple(result)


def naive_pair(bars: tuple[Bar, ...], a: Fractal, b: Fractal) -> bool:
    """Direct six-rule pair predicate, scanning every interior merged bar."""
    i, ka = a
    j, kb = b
    if j - i < 4 or ka == kb:
        return False
    top, bottom = (i, j) if ka == "top" else (j, i)
    lt, ht = bars[top]
    lb, hb = bars[bottom]
    if not (ht > hb and lb < lt):
        return False
    return all(low >= lb and high <= ht for low, high in bars[i : j + 1])


def graph(bars: tuple[Bar, ...], fx: tuple[Fractal, ...]) -> tuple[tuple[int, ...], ...]:
    """Build edges with incremental range bounds; O(n*m) time, O(m+E) space."""
    center_to_fx = {center: k for k, (center, _) in enumerate(fx)}
    adjacency = [[] for _ in fx]
    for a, (start, kind) in enumerate(fx):
        minimum, maximum = bars[start]
        for stop in range(start + 1, len(bars)):
            low, high = bars[stop]
            minimum = min(minimum, low)
            maximum = max(maximum, high)
            if stop not in center_to_fx or stop - start < 4:
                continue
            b = center_to_fx[stop]
            if fx[b][1] == kind:
                continue
            top, bottom = (start, stop) if kind == "top" else (stop, start)
            # Under strict fractals, these extrema equalities imply both
            # center-interval strict inequalities; deliberately do not reuse
            # naive_pair here so the comparison checks that implication too.
            if maximum == bars[top][1] and minimum == bars[bottom][0]:
                adjacency[a].append(b)
    return tuple(tuple(row) for row in adjacency)


def enumerate_paths(adjacency: tuple[tuple[int, ...], ...], source: int, sink: int):
    if source == sink:
        yield (source,)
        return
    for nxt in adjacency[source]:
        if nxt <= sink:
            for suffix in enumerate_paths(adjacency, nxt, sink):
                yield (source,) + suffix


def summary_dp(adjacency: tuple[tuple[int, ...], ...], source: int, sink: int):
    """Count all paths and longest-path multiplicity for FIXED boundaries.

    Longest-path preference is an experiment only, not a selected Bi rule.
    Lexicographic witness selection is only deterministic evidence formatting.
    """
    count = [0] * len(adjacency)
    length = [-1] * len(adjacency)
    best_count = [0] * len(adjacency)
    witness: list[tuple[int, ...] | None] = [None] * len(adjacency)
    count[source], length[source], best_count[source] = 1, 0, 1
    witness[source] = (source,)
    for i in range(source, sink + 1):
        if not count[i]:
            continue
        for j in adjacency[i]:
            if j > sink:
                continue
            count[j] += count[i]
            candidate = length[i] + 1
            if candidate > length[j]:
                length[j], best_count[j] = candidate, best_count[i]
                witness[j] = witness[i] + (j,)
            elif candidate == length[j]:
                best_count[j] += best_count[i]
                witness[j] = min(witness[j], witness[i] + (j,))
    return count[sink], length[sink], best_count[sink], witness[sink]


def check_case(bars: tuple[Bar, ...], counts: dict[str, int]) -> None:
    validate_input(bars)
    fx = fractals(bars)
    adjacency = graph(bars, fx)
    counts["sequences"] += 1
    counts["fractals"] += len(fx)
    for a, b in itertools.combinations(range(len(fx)), 2):
        counts["pair_comparisons"] += 1
        assert naive_pair(bars, fx[a], fx[b]) == (b in adjacency[a])
    if len(fx) <= 12:
        for a, b in itertools.combinations(range(len(fx)), 2):
            paths = list(enumerate_paths(adjacency, a, b))
            count, length, ways, witness = summary_dp(adjacency, a, b)
            assert count == len(paths)
            if paths:
                best = max(len(p) - 1 for p in paths)
                longest = [p for p in paths if len(p) - 1 == best]
                assert (length, ways, witness) == (best, len(longest), min(longest))
                for path in paths:
                    for i, j in zip(path, path[1:]):
                        assert naive_pair(bars, fx[i], fx[j])
            else:
                assert (length, ways, witness) == (-1, 0, None)
            counts["path_dp_comparisons"] += 1


def main() -> None:
    protected = [
        "docs/memo/memoWX_020_Chan_bi.md",
        "docs/memo/memoWX_019_Chan_fenxing.md",
        "src/chanlab/algo/fenxing.py",
        "src/chanlab/algo/merged_kline.py",
        "docs/memo/memoWX_009_designPatternForChanFeatures.md",
    ]
    before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in protected}
    counts = {"sequences": 0, "fractals": 0, "pair_comparisons": 0, "path_dp_comparisons": 0}
    # Exhaust all nonflat equal-width interval sequences over four levels,
    # lengths3..9, including nonadjacent equal extreme prices.
    for n in range(3, 10):
        def walk(prefix):
            if len(prefix) == n:
                yield tuple((x, x + 2) for x in prefix)
                return
            for value in range(4):
                if not prefix or value != prefix[-1]:
                    yield from walk(prefix + (value,))
        for bars in walk(()):
            check_case(bars, counts)
    rng = random.Random(20261110)
    for _ in range(1200):
        vals = [rng.randrange(20)]
        for i in range(rng.randrange(14, 45)):
            options = [x for x in range(20) if x != vals[-1]]
            vals.append(rng.choice(options))
        check_case(tuple((v, v + 2) for v in vals), counts)
    # Variable-width bars: both bounds strictly move together, range validity
    # checked after each move; no synthetic OHLC values used by this model.
    for _ in range(400):
        bars = [(0, 10)]
        for i in range(rng.randrange(14, 40)):
            low, high = bars[-1]
            direction = rng.choice((-1, 1))
            candidates = [(low + direction*a, high + direction*b)
                          for a in range(1, 5) for b in range(1, 5)
                          if low + direction*a <= high + direction*b]
            bars.append(rng.choice(candidates))
        check_case(tuple(bars), counts)
    # No equal same-kind endpoint prices, same fixed boundaries, still two
    # maximum-stroke paths. The intervening C->D move is too short to be a Bi.
    values = (8,9,8,7,5,3,4,5,6,7,4,2,3,4,5,6,5,3,1,0,1)
    bars = tuple((v, v + 1) for v in values)
    check_case(bars, counts)
    fx = fractals(bars)
    assert fx == ((1,"top"),(5,"bottom"),(9,"top"),(11,"bottom"),(15,"top"),(19,"bottom"))
    adjacency = graph(bars, fx)
    paths = list(enumerate_paths(adjacency, 0, 5))
    longest = max(len(p)-1 for p in paths)
    best = [p for p in paths if len(p)-1 == longest]
    assert (0,1,2,5) in best and (0,3,4,5) in best and longest == 3
    after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in protected}
    assert before == after
    result = {
        "scope": "independent finite model; no production Bi/CC execution",
        "seed": 20261110, "checks": counts,
        "protected_sha256": before, "protected_files_unchanged": True,
        "counterexample": {"bars_low_high":bars,"fractals_center_kind":fx,
                           "all_fixed_boundary_paths_fx_positions":paths,
                           "maximum_stroke_count":longest,
                           "maximum_paths_merged_centers":[[fx[k][0] for k in p] for p in best]},
    }
    (HERE / "oracle-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks":counts,"maximum_paths_merged_centers":result["counterexample"]["maximum_paths_merged_centers"],"protected_files_unchanged":True}))


if __name__ == "__main__":
    main()
