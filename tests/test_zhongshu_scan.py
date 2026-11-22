"""Independent enumeration, boundary geometry and source-projection checks."""

from __future__ import annotations

import random
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

from chanlab.algo._zhongshu_input import project_xianduans
from chanlab.algo._zhongshu_scan import (
    Segment,
    crossing,
    scan_zhongshus,
    validate_segments,
)
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.xianduan import XianduanSeries
from experiments.zhongshu022.reference import rational_crossing, reference_route


def legs(prices: list[float]) -> tuple[Segment, ...]:
    """Construct illustrative completed segments, without claiming upstream proofs."""
    epoch = datetime(2024, 1, 1, tzinfo=UTC)
    return tuple(
        Segment(
            i,
            "fixture",
            i * 3,
            (i + 1) * 3,
            float(i),
            float(i + 1),
            epoch + timedelta(hours=i),
            epoch + timedelta(hours=i + 1),
            a,
            b,
            min(a, b),
            max(a, b),
            1 if b > a else -1,
            epoch + timedelta(hours=i + 3),
        )
        for i, (a, b) in enumerate(pairwise(prices))
    )


def check_reference(items: tuple[Segment, ...]) -> None:
    """Compare all centers and crossings to separately enumerated exact evidence."""
    result = scan_zhongshus(items)
    assert [
        (z.start, z.terminal, z.low, z.high) for z in result.centers
    ] == reference_route(items)
    previous_end = -1
    for z in result.centers:
        assert z.start > previous_end
        boundary = z.low if items[z.start].direction == 1 else z.high
        expected = rational_crossing(items[z.start], boundary)
        assert (z.left is None) == (expected is None)
        if z.left is not None and expected is not None:
            assert z.left.x == pytest.approx(expected[0])
            assert z.left.fraction == pytest.approx(expected[1])
        if z.terminal is not None:
            previous_end = z.terminal
            assert z.confirmation == z.terminal + 1
            assert z.confirmed_at == max(
                x.confirmed_at for x in items[z.start : z.terminal + 2]
            )
            bound = z.high if items[z.terminal].direction == 1 else z.low
            exp = rational_crossing(items[z.terminal], bound)
            assert (z.right is None) == (exp is None)
            if z.right is not None and exp is not None:
                assert z.right.x == pytest.approx(exp[0])
                assert z.right.fraction == pytest.approx(exp[1])
        else:
            assert z.confirmation is None and z.confirmed_at is None and z.right is None
        assert z.drawable == (z.closed and z.left is not None and z.right is not None)


def test_extension_restart_and_evidence() -> None:
    """A returned departure must not terminate or shrink the established core."""
    items = legs([18, 12, 16, 13, 19, 14, 22, 18, 24, 20])
    result = scan_zhongshus(items)
    a, b = result.centers
    assert (a.start, a.terminal, a.confirmation, a.low, a.high) == (0, 5, 6, 13, 16)
    assert a.left is not None and a.left.x == pytest.approx(1 / 3)
    assert a.right is not None and a.right.x == 5.25
    assert b.start == 6 and not b.closed and (b.low, b.high) == (20, 22)
    check_reference(items)


def test_slide_and_unformed_tail() -> None:
    """Advance one position after a failed triple and reuse the confirming return."""
    items = legs([18, 22, 10, 14, 12, 20, 16])
    result = scan_zhongshus(items)
    assert [(x.start, x.terminal) for x in result.centers] == [(1, 4)]
    assert result.unformed == ((0, 1), (5, 6))
    assert result.decisions[0].outcome == "disjoint"
    check_reference(items)


def test_touch_and_zero_height() -> None:
    """Touching is a return; a singleton core is a valid degenerate rectangle."""
    items = legs([18, 12, 16, 13, 19, 14, 22, 16, 24, 20])
    assert scan_zhongshus(items).centers[0].terminal == 7
    point = legs([10, 20, 0, 10, 5, 12, 11])
    z = scan_zhongshus(point).centers[0]
    assert (z.low, z.high, z.terminal, z.drawable) == (10, 10, 4, True)
    check_reference(point)


def test_missing_chord_crossings_preserve_structure() -> None:
    """Actual internal extrema can create a core absent from an endpoint chord."""
    left = list(legs([20, 30, 22, 28, 23, 35, 32]))
    left[0] = replace(left[0], low=10)
    left[1] = replace(left[1], low=12)
    left[2] = replace(left[2], low=15)
    z = scan_zhongshus(left).centers[0]
    assert z.closed and not z.drawable and z.terminal == 4
    assert z.diagnostics == ("left_crossing_missing",)
    right = list(legs([18, 12, 16, 13, 20, 18, 22, 19]))
    right[4] = replace(right[4], low=14)
    right[5] = replace(right[5], low=14)
    z = scan_zhongshus(right).centers[0]
    assert z.closed and not z.drawable and z.terminal == 5
    assert z.diagnostics == ("right_crossing_missing",)
    check_reference(tuple(left))
    check_reference(tuple(right))


@pytest.mark.parametrize("prices", [[], [1], [1, 3], [1, 3, 2], [18, 22, 10, 14]])
def test_empty_short_or_disjoint(prices: list[float]) -> None:
    """No manufactured rectangle on an empty, short or wholly disjoint input."""
    assert not scan_zhongshus(legs(prices)).centers


@pytest.mark.parametrize(
    "mutation",
    [
        {"id": -1},
        {"id": True},
        {"snapshot_id": ""},
        {"source_stop": 0},
        {"start_x": float("nan")},
        {"start_price": True},
        {"end_x": 0},
        {"start_time": datetime(2024, 1, 1)},
        {"confirmed_at": datetime(2023, 1, 1, tzinfo=UTC)},
        {"direction": 0},
        {"direction": True},
        {"direction": -1},
        {"end_price": 1},
        {"low": 2},
        {"high": 1},
    ],
)
def test_invalid_record(mutation: dict[str, Any]) -> None:
    """Invalid endpoint/range/time evidence must fail before scanning."""
    item = legs([1, 3])[0]
    with pytest.raises(ValueError):
        scan_zhongshus([replace(item, **mutation)])


@pytest.mark.parametrize(
    "mutation",
    [
        {"snapshot_id": "other"},
        {"source_start": 2},
        {"start_x": 0.5},
        {"start_time": datetime(2024, 1, 1, 0, 30, tzinfo=UTC)},
        {"start_price": 4, "high": 4},
        {"id": 0},
    ],
)
def test_disconnected_input(mutation: dict[str, Any]) -> None:
    """Cross-snapshot or disconnected series cannot silently produce a center."""
    a, b = legs([1, 3, 2])
    with pytest.raises(ValueError):
        validate_segments([a, replace(b, **mutation)])


def test_evidence_not_endpoint_time() -> None:
    """Use all relevant source confirmation times, including an earlier late proof."""
    data = list(legs([10, 20, 0, 10, 5, 12, 11]))
    later = data[-1].confirmed_at + timedelta(days=10)
    data[0] = replace(data[0], confirmed_at=later)
    assert scan_zhongshus(data).centers[0].confirmed_at == later
    assert crossing(data[0], 99) is None


def test_random_exhaustive_and_transformations() -> None:
    """Compare 500 synthetic paths, with internal extrema and price reflections."""
    rng = random.Random(22018)
    for case in range(500):
        prices = [float(rng.randrange(-100, 100))]
        direction = rng.choice((-1, 1))
        for _ in range(rng.randrange(0, 45)):
            prices.append(prices[-1] + direction * rng.randint(1, 30))
            direction *= -1
        items = legs(prices)
        if case % 3 == 0:
            items = tuple(
                replace(x, low=x.low - rng.randrange(8), high=x.high + rng.randrange(8))
                for x in items
            )
        check_reference(items)
        reflection = tuple(
            replace(
                x,
                start_price=-x.start_price,
                end_price=-x.end_price,
                low=-x.high,
                high=-x.low,
                direction=-x.direction,
            )
            for x in items
        )
        affine = tuple(
            replace(
                x,
                start_price=x.start_price * 3 + 7,
                end_price=x.end_price * 3 + 7,
                low=x.low * 3 + 7,
                high=x.high * 3 + 7,
            )
            for x in items
        )
        original = scan_zhongshus(items)
        for transformed in (reflection, affine):
            check_reference(transformed)
            changed = scan_zhongshus(transformed)
            assert [(z.start, z.terminal, z.diagnostics) for z in original.centers] == [
                (z.start, z.terminal, z.diagnostics) for z in changed.centers
            ]


def test_real_adapter_source_extrema() -> None:
    """Load validated031 source context and verify projected internal prices."""
    folder = Path("artifacts/mas/xianduan-family/run031/full/bi-weak_xd-weak")
    table = ChanTable.read_csv(folder / "table.csv", folder / "context.csv")
    series = table.feature_series["bi-weak_xd-weak"]
    assert isinstance(series, XianduanSeries)
    projected = project_xianduans(series, "real-context")
    assert len(projected) == 89
    for source, item in zip(series, projected):
        values = [
            p
            for pen in series.source_series[source.source_start : source.source_stop]
            for p in (pen.start_price, pen.end_price)
        ]
        assert item.low == min(values) and item.high == max(values)
    with pytest.raises(ValueError):
        project_xianduans(None, "bad")  # type: ignore[arg-type]
