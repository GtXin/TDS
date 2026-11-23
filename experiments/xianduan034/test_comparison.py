"""Regression checks for external-data identity and cross-window geometry."""

from __future__ import annotations

from typing import Any

from charts import geometry, visible, windows
from compare import compare_records, signature


def segment(identity: int = 1, end_price: float = 20.0) -> dict[str, Any]:
    """Build a segment crossing a viewport with endpoints outside it."""
    return {
        "id": identity,
        "start_raw": 10,
        "end_raw": 90,
        "start_price": 10.0,
        "end_price": end_price,
        "direction": "up",
        "status": "unconfirmed",
    }


def test_ids_and_status_do_not_define_geometry() -> None:
    """External IDs and confirmation labels must not cause false mismatches."""
    left, right = segment(1), segment(999)
    right["status"] = "confirmed"
    result = compare_records([left], [right], "xd")
    assert result["exact_geometry_matches"] == 1
    assert result["status_difference_on_matching_geometry"] == 1
    assert not result["only_ours"] and not result["only_kwx"]


def test_price_difference_cannot_be_hidden_by_matching_endpoints() -> None:
    """A price discrepancy at identical source positions remains visible."""
    left, right = segment(), segment(end_price=21)
    assert signature(left, "xd") != signature(right, "xd")
    result = compare_records([left], [right], "xd")
    assert result["exact_geometry_matches"] == 0
    assert result["only_ours"] == [left]
    assert result["only_kwx"] == [right]


def test_crossing_segment_keeps_original_endpoints() -> None:
    """Window clipping must not invent local endpoints or lose crossing lines."""
    point = segment()
    assert visible(point, "xd", 40, 60)
    x, y, ids = geometry([point], "xd", 40, 60)
    assert x == [10, 90, None] and y == [10, 20, None] and ids == [1]
    assert not visible(point, "xd", 91, 100)


def test_window_coverage_including_short_tail() -> None:
    """Every raw index must appear for varied lengths and partial final pages."""
    for n in (1, 20, 399, 400, 401, 760, 761, 44375):
        spans = windows(n)
        assert {i for a, b in spans for i in range(a, b)} == set(range(n))
        assert all(0 <= a < b <= n for a, b in spans)
