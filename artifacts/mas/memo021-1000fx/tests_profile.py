"""Synthetic tests of the declared XD-P1 profile, not full Chan equivalence."""

from __future__ import annotations

from copy import deepcopy
from itertools import combinations, pairwise
from random import Random
from typing import Any

import pytest
from recognizer import (
    Element,
    _anchor,
    _append,
    _direct,
    _fx,
    _included,
    _intersection,
    _primary_feature,
    _secondary,
    basic,
    candidate_certificates,
    check_certificate,
    normalize,
    recognize,
    select_graph,
)

NO_GAP = [10, 20, 15, 25, 18, 22, 12]
GAP = [10, 18, 14, 24, 19, 22, 16, 20, 12, 17, 14, 21]
DIRECT = [10, 18, 14, 22, 12, 16, 8]
CONTAINED_THIRD = [10, 20, 15, 18, 12, 16, 9]
GAP_SWALLOW = [10, 18, 14, 24, 19, 22, 16, 23, 21, 23.5, 20, 23, 21, 23.8]


def test_no_gap_geometry_and_evidence() -> None:
    result = recognize(NO_GAP)
    assert result["selected_endpoints"] == [0, 3]
    cert = result["selected"][0]["certificate"]
    assert cert["kind"] == "no_gap"
    assert cert["dep_pen"] == 5
    assert cert["dep_endpoint"] == 6
    assert check_certificate(NO_GAP, cert)["passed"]
    assert result["unresolved_pen_ranges"] == [[3, 6]]


def test_gap_is_pending_then_uses_parent_only_secondary() -> None:
    assert not candidate_certificates(GAP[:7], 0, 3)[0]
    result = recognize(GAP)
    assert result["selected_endpoints"] == [0, 3, 8]
    primary, child = result["selected"]
    assert primary["kind"] == "gap"
    assert primary["dep_pen"] == 10
    assert child["kind"] == "secondary_067"
    assert child["parent_id"] == primary["id"]
    assert not child["root"]
    assert child["i"] == 3 and child["j"] == 8
    assert check_certificate(GAP, primary["certificate"])["passed"]


def test_direct_first_pen_break_guard() -> None:
    assert _direct(DIRECT, 0, 3) is not None
    assert recognize(DIRECT)["selected"][0]["kind"] == "direct_071"
    assert _direct(CONTAINED_THIRD, 0, 3) is None
    assert not candidate_certificates(CONTAINED_THIRD, 0, 3)[0]


def test_gap_cannot_swallow_existing_reverse_boundary() -> None:
    result = recognize(GAP_SWALLOW)
    primary = {cert["i"]: cert for cert in result["certificates"]}
    assert primary[3]["j"] == 6
    assert not (0 in primary and primary[0]["j"] == 3 and primary[0]["kind"] == "gap")
    assert result["rejection_stats"].get("compat_reverse_boundary_conflict", 0) >= 1


def test_closed_touch_and_fixed_first3_failure() -> None:
    assert _intersection([10, 20, 5, 10], 0) == (10, 10)
    assert not basic([10, 20, 5, 10], 0, 3)  # Endpoint net move is zero.
    assert not basic([10, 20, 5, 8, 4, 7], 0, 3)
    assert not basic([10, 20, 5, 8, 4, 7], 0, 5)
    assert not basic(NO_GAP, 0, 2)
    assert not basic(NO_GAP, 0, 8)


def test_equal_fractals_are_excluded_and_include_both_orders() -> None:
    left = Element(1, 5, (0,))
    equal_high = Element(2, 5, (1,))
    right = Element(0, 4, (2,))
    assert not _fx(left, equal_high, right, 1)
    outer, inner = Element(0, 10, (0,)), Element(2, 8, (1,))
    assert _included(outer, inner) and _included(inner, outer)
    for ordered in ((outer, inner), (inner, outer)):
        up: list[Element] = []
        down: list[Element] = []
        for element in ordered:
            _append(up, element, 1)
            _append(down, element, -1)
        assert (up[0].low, up[0].high) == (2, 10)
        assert (down[0].low, down[0].high) == (0, 8)
        assert up[0].members == ordered[0].members + ordered[1].members
    assert _included(outer, outer)


def test_anchor_tie_retains_earliest_raw_source() -> None:
    prices = [10, 20, 12, 20, 14, 18]
    merged = normalize(prices, [1, 3], 1)[0]
    assert merged.members == (1, 3)
    assert _anchor(prices, merged, 1) == 1
    assert (
        _anchor(
            [-p for p in prices], Element(-merged.high, -merged.low, merged.members), -1
        )
        == 1
    )
    with pytest.raises(ValueError, match="direction"):
        normalize(prices, [1], 0)


def test_direct_equal_or_weak_break_waits() -> None:
    # Initial reverse first-pen break but third pen only touches its first end.
    prices = [10, 18, 14, 22, 12, 16, 12]
    assert _direct(prices, 0, 3) is None
    # Rebound exceeds the old boundary before reverse continuation.
    prices = [10, 18, 14, 22, 12, 23, 8]
    assert _direct(prices, 0, 3) is None


def test_stale_gap_and_open_eof_are_not_completed() -> None:
    stale = [10, 18, 14, 24, 19, 22, 16, 25, 12, 17, 14, 21]
    assert not any(c["kind"] == "gap" for c in candidate_certificates(stale, 0, 3)[0])
    assert recognize([10, 20, 15, 25])["selected"] == []
    assert recognize([])["selected"] == []
    assert recognize([10])["unresolved_pen_ranges"] == []
    assert candidate_certificates(NO_GAP, 0, 2)[1] == "basic_failed"
    assert candidate_certificates(NO_GAP, 3, 6)[1] == "no_right_evidence"


@pytest.mark.parametrize(
    "invalid",
    [[1, 1], [1, 2, 3], [True, 2], [1, float("nan")], [1, float("inf")], ["x", 2]],
)
def test_invalid_inputs(invalid: list[Any]) -> None:
    with pytest.raises(ValueError):
        recognize(invalid)


def test_fresh_replay_detects_certificate_corruption() -> None:
    certificate = recognize(NO_GAP)["selected"][0]["certificate"]
    broken = deepcopy(certificate)
    broken["dep_pen"] = 3
    assert not check_certificate(NO_GAP, broken)["passed"]
    assert not check_certificate(NO_GAP, {"i": "bad", "j": 3})["passed"]


def test_mirror_and_positive_affine_transform() -> None:
    for prices in (NO_GAP, GAP, DIRECT, GAP_SWALLOW, CONTAINED_THIRD):
        original = recognize(prices)
        for transformed in ([-p for p in prices], [3 * p + 17 for p in prices]):
            actual = recognize(transformed)
            assert actual["selected_endpoints"] == original["selected_endpoints"]
            assert [n["kind"] for n in actual["selected"]] == [
                n["kind"] for n in original["selected"]
            ]


def test_deterministic_random_synthetic_replays() -> None:
    random = Random(21011)
    for _ in range(100):
        prices = [50.0]
        for index in range(random.randint(6, 24)):
            prices.append(
                prices[-1] + (1 if index % 2 == 0 else -1) * random.randint(1, 12)
            )
        report = recognize(prices)
        for certificate in report["certificates"]:
            assert check_certificate(prices, certificate)["passed"]
        assert (
            recognize([-p for p in prices])["selected_endpoints"]
            == report["selected_endpoints"]
        )
        for left, right in pairwise(report["selected"]):
            assert left["j"] == right["i"]
            assert left["direction"] != right["direction"]
        for node in report["selected"]:
            assert basic(prices, node["i"], node["j"])


def test_graph_dp_against_exhaustive_subsets() -> None:
    intervals = [(0, 3), (3, 6), (0, 9), (6, 9), (9, 12), (12, 15), (9, 18)]
    nodes = [
        {
            "id": i,
            "i": a,
            "j": b,
            "root": i in (0, 2),
            "direction": "up" if a % 2 == 0 else "down",
        }
        for i, (a, b) in enumerate(intervals)
    ]
    edges = [[0, 1], [1, 3], [2, 4], [3, 4], [4, 5], [2, 6], [3, 6]]
    actual = select_graph(nodes, edges)
    assert actual["node_ids"] == [0, 1, 3, 6]
    order = actual["topological_order"]
    candidates = []
    for size in range(1, len(nodes) + 1):
        for path in combinations(order, size):
            if not nodes[path[0]]["root"] or nodes[path[0]]["i"] != 0:
                continue
            if all([left, right] in edges for left, right in pairwise(path)):
                candidates.append((nodes[path[-1]]["j"], len(path)))
    assert (actual["end"], actual["count"]) == max(candidates)
    assert select_graph([], [])["node_ids"] == []
    with pytest.raises(ValueError, match="duplicate"):
        select_graph(nodes + [nodes[0]], edges)
    with pytest.raises(ValueError, match="unknown"):
        select_graph(nodes, edges + [[0, 99]])
    with pytest.raises(ValueError, match="incompatible"):
        select_graph(nodes, edges + [[0, 3]])


def test_directional_private_boundary_cases() -> None:
    assert _secondary([10, 20, 15, 25], 0, 1) is None
    assert _primary_feature([10, 20, 15, 25], 0, 3)[0] is None
    assert _fx(Element(5, 10, (0,)), Element(1, 6, (1,)), Element(3, 8, (2,)), -1)
