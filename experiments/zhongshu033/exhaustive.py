"""Finite exhaustive alternating segment paths and exact-rational geometry oracle."""

from collections import Counter
from datetime import UTC, datetime, timedelta
from itertools import pairwise, product

from chanlab.algo._zhongshu_scan import Segment, scan_zhongshus
from experiments.zhongshu022.reference import rational_crossing, reference_route
from experiments.zhongshu033.validate import save


def main():
    tally = Counter()
    epoch = datetime(2026, 1, 1, tzinfo=UTC)
    for n in range(1, 9):
        for prices in product(range(4), repeat=n):
            diffs = [b - a for a, b in pairwise(prices)]
            if any(d == 0 for d in diffs) or any(
                a * b >= 0 for a, b in pairwise(diffs)
            ):
                continue
            legs = tuple(
                Segment(
                    i,
                    "finite",
                    i * 3,
                    (i + 1) * 3,
                    float(i),
                    float(i + 1),
                    epoch + timedelta(hours=i),
                    epoch + timedelta(hours=i + 1),
                    float(a),
                    float(b),
                    float(min(a, b)),
                    float(max(a, b)),
                    1 if b > a else -1,
                    epoch + timedelta(hours=i + 3),
                )
                for i, (a, b) in enumerate(pairwise(prices))
            )
            actual = scan_zhongshus(legs)
            assert [
                (g.start, g.terminal, g.low, g.high) for g in actual.centers
            ] == reference_route(legs)
            tally.update(
                paths=1,
                centers=len(actual.centers),
                closed=sum(g.closed for g in actual.centers),
                open=sum(not g.closed for g in actual.centers),
                zero=sum(g.low == g.high for g in actual.centers),
            )
            for g in actual.centers:
                pairs = [
                    (
                        g.left,
                        legs[g.start],
                        g.low if legs[g.start].direction == 1 else g.high,
                    )
                ]
                if g.closed:
                    pairs.append(
                        (
                            g.right,
                            legs[g.terminal],
                            g.high if legs[g.terminal].direction == 1 else g.low,
                        )
                    )
                for cross, leg, bound in pairs:
                    expected = rational_crossing(leg, bound)
                    assert (cross is None) == (expected is None)
                    if expected is not None:
                        assert abs(cross.x - expected[0]) < 1e-12
                    tally.update(crossings=1)
    save(
        "exhaustive.json",
        {
            "domain": "every strict alternating endpoint path with 1..8 vertices in {0,1,2,3}; actual range=endpoint range",
            "counts": tally,
            "independent_all_seed_exit_enumeration": "PASS",
            "exact_rational_crossings": "PASS",
        },
    )
    print(tally)


if __name__ == "__main__":
    main()
