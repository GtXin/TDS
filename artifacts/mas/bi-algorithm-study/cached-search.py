"""Executable experimental tree: temporal extension + complete cached recovery.

Not production Bi/CC. Explicit protocol: every seed/initial-end option; mandatory
valid more-extreme extension; branch equal extrema; first valid reverse; EOF
working pair stays provisional; failed mandatory extension kills that branch.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import importlib.util
import json
import random
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bi_oracle", HERE / "oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def run(bars):
    """Return all viable EOF routes, plus blocked historical diagnostics."""
    bars = tuple(tuple(x) for x in bars)
    oracle.validate_input(bars)
    fx = oracle.fractals(bars)
    # Each saved alternative is ALREADY the alternative post-decision state.
    # Restoring it never executes the same fork again at the same input item.
    seeds = [((a,), a, None, a + 1) for a in range(len(fx))]
    pending = list(reversed(seeds))
    routes, blocked, breaches = set(), [], {}
    counts = Counter()

    def pair(a, b):
        return oracle.naive_pair(bars, fx[a], fx[b])

    def invariant(prefix, a, b, cursor):
        assert prefix[-1] == a
        assert all(pair(x, y) for x, y in zip(prefix, prefix[1:]))
        assert cursor > (a if b is None else b)
        assert b is None or pair(a, b)

    while pending:
        prefix, a, b, cursor = pending.pop()
        counts["cache_restore"] += 1
        invariant(prefix, a, b, cursor)
        dead = False
        while cursor < len(fx):
            f = cursor
            cursor += 1
            if b is None:
                if pair(a, f):
                    # Other initial end choices are recoverable even after
                    # several locally closed strokes on the accept branch.
                    pending.append((prefix, a, None, cursor))
                    counts["cache_initial_end_skip"] += 1
                    b = f
                    counts["provisional_end"] += 1
                else:
                    counts["seed_pair_rejected_evidence_retained"] += 1
            elif fx[f][1] == fx[b][1]:
                k = 1 if fx[b][1] == "top" else 0
                value, previous = bars[fx[f][0]][k], bars[fx[b][0]][k]
                better = value > previous if k == 1 else value < previous
                if better:
                    if pair(a, f):
                        b = f
                        counts["mandatory_end_extension"] += 1
                    else:
                        # New lower bottom/higher top is inside EVERY future
                        # reverse from old B, so that old B cannot be kept as
                        # an active endpoint covering the continuing input.
                        blocked.append({"historical_centers": [fx[x][0] for x in prefix + (b,)],
                                        "failed_new_end": fx[f][0]})
                        counts["blocked_extension_restore_alternative"] += 1
                        dead = True
                        break
                elif value == previous:
                    if pair(a, f):
                        pending.append((prefix, a, f, cursor))
                        counts["cache_equal_end_replace"] += 1
                    counts["keep_equal_current_end"] += 1
                else:
                    counts["inferior_end_evidence_retained"] += 1
            else:
                if pair(b, f):
                    prefix = prefix + (b,)
                    a, b = b, f
                    counts["first_qualified_reverse"] += 1
                else:
                    counts["reverse_rejected_evidence_retained"] += 1
            invariant(prefix, a, b, cursor)
        if not dead and b is not None:
            route = tuple(fx[x][0] for x in prefix + (b,))
            routes.add(route)
            center = fx[b][0]
            tail = bars[center + 1 :]
            breaches[route] = bool(tail) and (
                max(x[1] for x in tail) > bars[center][1]
                if fx[b][1] == "top" else
                min(x[0] for x in tail) < bars[center][0]
            )
            counts["eof_provisional_route"] += 1
    return {"routes": routes, "blocked": blocked, "tail_breaches": breaches,
            "counts": counts}


def reflected(bars):
    return tuple((-hi, -lo) for lo, hi in bars)


def main():
    directed = {
        "mandatory_extension": [1,0,3,6,9,12,10,8,12,16,13,10,7,4,5],
        "blocked_then_cached_earlier_choice": [8,9,6,4,2,0,2,4,6,7,3,-1,1,3,5,8,5,2,0,-2,-1],
        "two_viable_no_tie_maximums": [8,9,8,7,5,3,4,5,6,7,4,2,3,4,5,6,5,3,1,0,1],
        "fixed_start_cannot_recover_but_later_seed_can": [6,5,6,7,8,10,9,4,6,8,10,12,11],
        "equal_end_alternative_needed": [8,9,6,4,2,0,4,7,5,3,1,0,1,2,3,4,3],
        "tail_without_new_complete_top": [1,0,3,6,9,12,10,11,13,14],
    }
    examples = {}
    counts = Counter()
    tests = 0
    reference_spec = importlib.util.spec_from_file_location("cached_reference", HERE / "cached-reference.py")
    reference = importlib.util.module_from_spec(reference_spec)
    sys.modules[reference_spec.name] = reference
    reference_spec.loader.exec_module(reference)

    def check(bars):
        nonlocal tests
        result = run(bars)
        assert result["routes"] == reference.run(tuple(bars))
        mirror = run(reflected(bars))
        assert result["routes"] == mirror["routes"]
        assert result["counts"] == mirror["counts"]
        assert result["blocked"] == mirror["blocked"]
        assert result["tail_breaches"] == mirror["tail_breaches"]
        fx = oracle.fractals(tuple(bars))
        lookup = {center: (center, kind) for center, kind in fx}
        for route in result["routes"]:
            assert all(oracle.naive_pair(tuple(bars), lookup[x], lookup[y])
                       for x, y in zip(route, route[1:]))
        counts.update(result["counts"])
        tests += 1
        return result

    for name, values in directed.items():
        width = 2 if name in ("mandatory_extension", "tail_without_new_complete_top") else 1
        bars = tuple((x, x + width) for x in values)
        result = check(bars)
        examples[name] = {"bars_low_high": bars, "routes": sorted(result["routes"]),
                          "blocked": result["blocked"], "counts": dict(result["counts"])}
    assert (1,9,13) in set(map(tuple, examples["mandatory_extension"]["routes"]))
    assert not any(p[:2] == (1,5) for p in map(tuple, examples["mandatory_extension"]["routes"]))
    recovered = set(map(tuple, examples["blocked_then_cached_earlier_choice"]["routes"]))
    assert (1,11,15,19) in recovered and (1,5,9,19) not in recovered
    ambiguity = set(map(tuple, examples["two_viable_no_tie_maximums"]["routes"]))
    assert (1,11,15,19) in ambiguity and (1,5,9,19) in ambiguity
    no_fixed = set(map(tuple, examples["fixed_start_cannot_recover_but_later_seed_can"]["routes"]))
    assert not any(p[0] == 1 for p in no_fixed) and (7,11) in no_fixed
    assert (1,11,15) in set(map(tuple, examples["equal_end_alternative_needed"]["routes"]))
    rng = random.Random(20261110)
    for _ in range(1000):
        values = [rng.randrange(16)]
        for k in range(rng.randrange(2, 31)):
            values.append(rng.choice([x for x in range(16) if x != values[-1]]))
        check(tuple((x, x + 2) for x in values))
    report = {"scope": "complete experimental cached temporal candidate protocol, not production/canonical proof",
              "seed": 20261110, "sequences_and_mirrors": tests,
              "event_counts": dict(counts), "examples": examples}
    (HERE / "cached-search.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"cases_plus_mirrors": tests, "events": dict(counts)}))


if __name__ == "__main__":
    main()
