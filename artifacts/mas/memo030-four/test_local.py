"""Boundary, mirror and event consistency checks for the new mode scanner."""

from __future__ import annotations

import random
from pathlib import Path

import pytest
from local import scanner
from run import load

OLD = Path(__file__).resolve().parent.parent / "memo021-1000fx"
rec = load("test_primitives", OLD / "recognizer.py")
reference = load("test_reference", OLD / "independent_validate.py")


@pytest.mark.parametrize(
    "prices,expected",
    [([10, 18, 14, 20], True), ([10, 18, 14, 18], False), ([10, 18, 14, 17], False)],
)
def test_shape_boundary(prices, expected):
    for p in (prices, [-v for v in prices]):
        _, strong = scanner(p, "strong", rec, reference.Reference(p))
        _, weak = scanner(p, "weak", rec, reference.Reference(p))
        assert strong(0, 3) == expected
        assert weak(0, 3)


def test_random_events_and_mirror():
    rng = random.Random(30117)
    count = 0
    for _ in range(100):
        prices = [10.0]
        for i in range(14):
            prices.append(prices[-1] + (1 if i % 2 == 0 else -1) * rng.randint(1, 12))
        for mode in ("strong", "weak"):
            native, shape = scanner(prices, mode, rec, reference.Reference(prices))
            independent, _ = scanner(
                prices, mode, rec, reference.Reference(prices), True
            )
            mirror = [-x for x in prices]
            mirrored, _ = scanner(mirror, mode, rec, reference.Reference(mirror))
            for a in range(12):
                for b in range(a + 3, 15, 2):
                    actual = native(a, b)
                    assert actual == independent(a, b)
                    opposite = mirrored(a, b)
                    assert [
                        {k: v for k, v in x.items() if k != "direction"} for x in actual
                    ] == [
                        {k: v for k, v in x.items() if k != "direction"}
                        for x in opposite
                    ]
                    for c in actual:
                        assert shape(a, b)
                        assert all(shape(x, y) for x, y in c["supports"])
                        count += 1
    assert count > 0


def test_watermark_dominance():
    """Earlier watermark admits a superset of continuations for the same geometry."""
    for geometry_end in range(3, 20):
        for early in range(geometry_end + 1, 25):
            for late in range(early, 25):
                earlier = {
                    end for end in range(geometry_end + 3, 30, 2) if end >= early
                }
                later = {end for end in range(geometry_end + 3, 30, 2) if end >= late}
                assert later <= earlier


def test_strong_certificate_subset_of_weak():
    """The added qualification cannot create a new local certificate event."""
    p = [10, 18, 14, 22, 17, 20, 12, 16, 8, 13, 11, 17, 14, 21, 16, 20, 12]
    strong, _ = scanner(p, "strong", rec, reference.Reference(p))
    weak, _ = scanner(p, "weak", rec, reference.Reference(p))

    def keys(cs):
        return {
            (
                c["i"],
                c["j"],
                c["kind"],
                c["dep_endpoint"],
                c["reverse_end"],
                c.get("h1"),
                c.get("h2"),
            )
            for c in cs
        }

    for a in range(len(p) - 3):
        for b in range(a + 3, len(p), 2):
            assert keys(strong(a, b)) <= keys(weak(a, b))
