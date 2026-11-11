"""XD-P1 isolated fixed-snapshot experiment, not an author-unique Chan selector.

The operational policies are supplied by the parent task. No CC implementation
is imported. Geometry uses point indices; evidence uses a separate endpoint
frontier. Certificates and conditional secondary states are serializable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from itertools import pairwise
from math import isfinite
from time import perf_counter
from typing import Any

PROFILE = "XD-P1"
_KIND_ORDER = {"no_gap": 0, "gap": 1, "direct_071": 2}


@dataclass(frozen=True, slots=True)
class Element:
    """One normalized feature interval with all raw source pen positions."""

    low: float
    high: float
    members: tuple[int, ...]


def _validate_prices(prices: Sequence[float]) -> tuple[float, ...]:
    """Require finite, non-flat, alternating input pens."""
    if any(isinstance(p, bool) or not isinstance(p, (int, float)) for p in prices):
        raise ValueError("prices must be finite numeric values")
    values = tuple(float(p) for p in prices)
    if any(not isfinite(p) for p in values):
        raise ValueError("prices must be finite")
    directions = [b - a for a, b in pairwise(values)]
    if any(delta == 0 for delta in directions):
        raise ValueError("flat pens are invalid")
    if any(a * b >= 0 for a, b in pairwise(directions)):
        raise ValueError("pen directions must alternate")
    return values


def _direction(prices: Sequence[float], index: int) -> int:
    return 1 if prices[index + 1] > prices[index] else -1


def _raw(prices: Sequence[float], index: int) -> Element:
    return Element(
        min(prices[index], prices[index + 1]),
        max(prices[index], prices[index + 1]),
        (index,),
    )


def _included(a: Element, b: Element) -> bool:
    return (a.low <= b.low and a.high >= b.high) or (
        b.low <= a.low and b.high >= a.high
    )


def _append(stack: list[Element], element: Element, direction: int) -> None:
    """Normalize on one side only, preserving both enclosure orders and ties."""
    stack.append(element)
    while len(stack) >= 2 and _included(stack[-2], stack[-1]):
        right = stack.pop()
        left = stack.pop()
        choose = max if direction == 1 else min
        stack.append(
            Element(
                choose(left.low, right.low),
                choose(left.high, right.high),
                left.members + right.members,
            )
        )


def normalize(
    prices: Sequence[float], pen_indices: Sequence[int], direction: int
) -> tuple[Element, ...]:
    """Apply the declared fixed-direction inclusion operation chronologically."""
    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or 1")
    stack: list[Element] = []
    for index in pen_indices:
        _append(stack, _raw(prices, index), direction)
    return tuple(stack)


def _anchor(prices: Sequence[float], element: Element, direction: int) -> int:
    """Use earliest raw feature high/low anchor on equal prices."""
    if direction == 1:
        return max(element.members, key=lambda k: _raw(prices, k).high)
    return min(element.members, key=lambda k: _raw(prices, k).low)


def _fx(left: Element, middle: Element, right: Element, direction: int) -> bool:
    if direction == 1:
        return (
            left.high < middle.high > right.high and left.low < middle.low > right.low
        )
    return left.high > middle.high < right.high and left.low > middle.low < right.low


def _intersection(prices: Sequence[float], start: int) -> tuple[float, float]:
    elements = [_raw(prices, k) for k in range(start, start + 3)]
    return max(e.low for e in elements), min(e.high for e in elements)


def basic(prices: Sequence[float], start: int, end: int) -> bool:
    """Check the profile's basic odd-pen, direction, price and closed overlap."""
    if not 0 <= start < end < len(prices):
        return False
    if end - start < 3 or (end - start) % 2 == 0:
        return False
    if (prices[end] - prices[start]) * _direction(prices, start) <= 0:
        return False
    low, high = _intersection(prices, start)
    return low <= high


def _stale(
    prices: Sequence[float], boundary: int, frontier: int, direction: int
) -> bool:
    return any(
        (prices[k] - prices[boundary]) * direction > 0
        for k in range(boundary + 1, frontier + 1)
    )


def _direct(
    prices: Sequence[float], start: int, boundary: int
) -> dict[str, Any] | None:
    """Monitor the 071 first-pen break, with the declared left-feature guard."""
    count = len(prices) - 1
    direction = _direction(prices, start)
    if boundary >= count:
        return None
    left = normalize(prices, range(start + 1, boundary, 2), direction)[-1]
    if (direction == 1 and left.high >= prices[boundary]) or (
        direction == -1 and left.low <= prices[boundary]
    ):
        return None
    if (prices[boundary + 1] - prices[boundary - 1]) * direction >= 0:
        return None
    for frontier in range(boundary + 2, count + 1):
        if (prices[frontier] - prices[boundary]) * direction > 0:
            return None
        if (
            (frontier - boundary) % 2 == 1
            and frontier - boundary >= 3
            and (prices[frontier] - prices[boundary + 1]) * direction < 0
            and basic(prices, boundary, frontier)
        ):
            return {
                "kind": "direct_071",
                "dep_endpoint": frontier,
                "reverse_end": frontier,
                "direct": {
                    "first_reverse_pen": boundary,
                    "broken_last_forward_start": boundary - 1,
                    "first_reverse_end_price": prices[boundary + 1],
                    "breaking_pen": frontier - 1,
                    "left_feature_guard": asdict(left),
                },
            }
    return None


def _secondary(
    prices: Sequence[float], boundary: int, direction: int
) -> dict[str, Any] | None:
    """Find the first strict reverse fractal; do not recursively classify its gap."""
    count = len(prices) - 1
    stack: list[Element] = []
    for index in range(boundary + 1, count, 2):
        frontier = index + 1
        if _stale(prices, boundary, frontier, direction):
            return None
        _append(stack, _raw(prices, index), -direction)
        if len(stack) < 3 or not _fx(*stack[-3:], -direction):
            continue
        endpoint = _anchor(prices, stack[-2], -direction)
        if basic(prices, boundary, endpoint) and basic(prices, endpoint, frontier):
            return {
                "reverse_end": endpoint,
                "dep_endpoint": frontier,
                "elements": [asdict(e) for e in stack[-3:]],
                "all_feature_members": [
                    k for element in stack for k in element.members
                ],
            }
    return None


def _primary_feature(
    prices: Sequence[float], start: int, boundary: int
) -> tuple[dict[str, Any] | None, str]:
    count = len(prices) - 1
    direction = _direction(prices, start)
    left_stack = normalize(prices, range(start + 1, boundary, 2), direction)
    if not left_stack:
        return None, "no_left_feature"
    left = left_stack[-1]
    right_stack: list[Element] = []
    secondary: dict[str, Any] | None = None
    secondary_scanned = False
    for index in range(boundary, count, 2):
        frontier = index + 1
        if _stale(prices, boundary, frontier, direction):
            return None, "stale_boundary"
        _append(right_stack, _raw(prices, index), direction)
        middle = right_stack[0]
        if _anchor(prices, middle, direction) != boundary:
            return None, "anchor_changed"
        if len(right_stack) < 2:
            continue
        right = right_stack[1]
        if not _fx(left, middle, right, direction):
            continue
        if not basic(prices, boundary, boundary + 3):
            return None, "reverse_first3_invalid"
        gap = left.high < middle.low if direction == 1 else left.low > middle.high
        feature = {
            "left": asdict(left),
            "middle": asdict(middle),
            "right": asdict(right),
            "left_normalized": [asdict(e) for e in left_stack],
            "event_endpoint": frontier,
            "gap": gap,
        }
        if not gap:
            return {
                "kind": "no_gap",
                "dep_endpoint": frontier,
                "reverse_end": None,
                "f1": feature,
            }, "certified"
        if not secondary_scanned:
            secondary = _secondary(prices, boundary, direction)
            secondary_scanned = True
        if secondary is None:
            return None, "gap_secondary_unfinished"
        evidence_end = max(frontier, int(secondary["dep_endpoint"]))
        if _stale(prices, boundary, evidence_end, direction):
            return None, "stale_gap"
        if not basic(prices, int(secondary["reverse_end"]), evidence_end):
            return None, "secondary_right_structure_invalid"
        return {
            "kind": "gap",
            "dep_endpoint": evidence_end,
            "reverse_end": secondary["reverse_end"],
            "f1": feature,
            "f2": secondary,
        }, "certified"
    return None, "feature_unfinished"


def candidate_certificates(
    prices: Sequence[float], start: int, boundary: int
) -> tuple[list[dict[str, Any]], str]:
    """Return declared primary/direct certificates for one hypothetical boundary."""
    if not basic(prices, start, boundary):
        return [], "basic_failed"
    if boundary >= len(prices) - 1:
        return [], "no_right_evidence"
    feature, reason = _primary_feature(prices, start, boundary)
    direct = _direct(prices, start, boundary)
    certificates = []
    for item in (feature, direct):
        if item is None:
            continue
        certificate = {
            "profile": PROFILE,
            "i": start,
            "j": boundary,
            "direction": "up" if _direction(prices, start) == 1 else "down",
            "member_range": [start, boundary],
            "first3_intersection": list(_intersection(prices, start)),
            "reverse_first3_intersection": list(_intersection(prices, boundary)),
            **item,
        }
        certificate["dep_pen"] = certificate["dep_endpoint"] - 1
        certificates.append(certificate)
    return certificates, "certified" if certificates else reason


def check_certificate(
    prices: Sequence[float], certificate: dict[str, Any]
) -> dict[str, Any]:
    """Freshly reconstruct a certificate; this replay is not an independent oracle."""
    values = _validate_prices(prices)
    start, boundary = certificate.get("i"), certificate.get("j")
    if not isinstance(start, int) or not isinstance(boundary, int):
        return {"passed": False, "reason": "invalid_certificate_indices"}
    candidates, reason = candidate_certificates(values, start, boundary)
    if certificate in candidates:
        return {"passed": True, "reason": "fresh_replay_equal"}
    return {"passed": False, "reason": reason}


def select_graph(nodes: list[dict[str, Any]], edges: list[list[int]]) -> dict[str, Any]:
    """Apply the 029 objective to a completed context DAG with deterministic ties."""
    by_id = {int(q["id"]): q for q in nodes}
    if len(by_id) != len(nodes):
        raise ValueError("duplicate node id")
    order = sorted(by_id, key=lambda key: (by_id[key]["j"], by_id[key]["i"], key))
    rank = {key: index for index, key in enumerate(order)}
    predecessors: dict[int, list[int]] = {key: [] for key in order}
    for left, right in edges:
        if left not in by_id or right not in by_id:
            raise ValueError("unknown graph node")
        a, b = by_id[left], by_id[right]
        if a["j"] != b["i"] or a["direction"] == b["direction"]:
            raise ValueError("incompatible graph edge")
        if rank[left] >= rank[right]:
            raise ValueError("graph is not temporally ordered")
        predecessors[right].append(left)
    roots = [int(q["i"]) for q in nodes if q["root"]]
    start = min(roots, default=None)
    best = {key: -1 for key in order}
    previous: dict[int, int | None] = dict.fromkeys(order)
    for key in order:
        node = by_id[key]
        if node["root"] and node["i"] == start:
            best[key] = 1
        for pred in sorted(predecessors[key], key=lambda item: rank[item]):
            if best[pred] >= 1 and best[pred] + 1 > best[key]:
                best[key], previous[key] = best[pred] + 1, pred
    end: int | None = None
    for key in order:
        if best[key] >= 1 and (
            end is None or (by_id[key]["j"], best[key]) > (by_id[end]["j"], best[end])
        ):
            end = key
    route: list[int] = []
    cursor = end
    while cursor is not None:
        route.append(cursor)
        cursor = previous[cursor]
    route.reverse()
    return {
        "start": start,
        "end": None if end is None else by_id[end]["j"],
        "count": len(route),
        "node_ids": route,
        "best": best,
        "prev": previous,
        "topological_order": order,
    }


def recognize(prices: Sequence[float]) -> dict[str, Any]:
    """Recognize XD-P1 primary/conditional nodes and select a fixed-snapshot route."""
    started = perf_counter()
    values = _validate_prices(prices)
    count = max(0, len(values) - 1)
    certificates: list[dict[str, Any]] = []
    chosen_by_start: dict[int, dict[str, Any]] = {}
    events: list[dict[str, Any]] = []
    rejections: Counter[str] = Counter()
    for start in reversed(range(max(0, count - 2))):
        available: list[dict[str, Any]] = []
        for boundary in range(start + 3, count + 1, 2):
            candidates, reason = candidate_certificates(values, start, boundary)
            rejections[reason] += 1
            for certificate in candidates:
                events.append(
                    {k: certificate[k] for k in ("i", "j", "kind", "dep_endpoint")}
                )
            for certificate in candidates:
                successor = chosen_by_start.get(boundary)
                if certificate["kind"] == "gap":
                    reverse_end = int(certificate["reverse_end"])
                    later = chosen_by_start.get(reverse_end)
                    if int(certificate["f1"]["event_endpoint"]) > reverse_end:
                        rejections["compat_primary_evidence_beyond_reverse_end"] += 1
                        continue
                    if successor is not None and int(successor["j"]) != reverse_end:
                        rejections["compat_reverse_boundary_conflict"] += 1
                        continue
                    if later is not None and int(later["j"]) < int(
                        certificate["dep_endpoint"]
                    ):
                        rejections["compat_secondary_evidence_beyond_next_end"] += 1
                        continue
                elif successor is not None and int(successor["j"]) < int(
                    certificate["dep_endpoint"]
                ):
                    rejections["compat_evidence_beyond_reverse_end"] += 1
                    continue
                available.append(certificate)
        if available:
            chosen = min(
                available,
                key=lambda cert: (
                    cert["dep_endpoint"],
                    cert["j"],
                    _KIND_ORDER[cert["kind"]],
                ),
            )
            certificates.append(chosen)
            chosen_by_start[start] = chosen
            rejections["later_completion_not_retained"] += len(available) - 1
    certificates.sort(key=lambda cert: int(cert["i"]))
    nodes: list[dict[str, Any]] = []
    by_start: dict[int, int] = {}
    for certificate in certificates:
        node_id = len(nodes)
        by_start[int(certificate["i"])] = node_id
        nodes.append(
            {
                "id": node_id,
                "i": certificate["i"],
                "j": certificate["j"],
                "direction": certificate["direction"],
                "root": True,
                "kind": certificate["kind"],
                "dep_endpoint": certificate["dep_endpoint"],
                "dep_pen": certificate["dep_pen"],
                "certificate": certificate,
                "parent_id": None,
            }
        )
    edges: list[list[int]] = []
    for node in tuple(nodes):
        if node["kind"] == "gap":
            certificate = node["certificate"]
            derived_id = len(nodes)
            endpoint = int(certificate["reverse_end"])
            nodes.append(
                {
                    "id": derived_id,
                    "i": node["j"],
                    "j": endpoint,
                    "direction": "down" if node["direction"] == "up" else "up",
                    "root": False,
                    "kind": "secondary_067",
                    "dep_endpoint": node["dep_endpoint"],
                    "dep_pen": node["dep_pen"],
                    "certificate": certificate,
                    "parent_id": node["id"],
                }
            )
            edges.append([int(node["id"]), derived_id])
            if endpoint in by_start:
                next_node = nodes[by_start[endpoint]]
                if int(next_node["j"]) >= int(node["dep_endpoint"]):
                    edges.append([derived_id, by_start[endpoint]])
        elif int(node["j"]) in by_start:
            next_node = nodes[by_start[int(node["j"])]]
            if int(next_node["j"]) >= int(node["dep_endpoint"]):
                edges.append([int(node["id"]), by_start[int(node["j"])]])
    selected = select_graph(nodes, edges)
    by_id = {q["id"]: q for q in nodes}
    route = [by_id[key] for key in selected["node_ids"]]
    if route:
        unresolved = [[0, int(route[0]["i"])], [int(route[-1]["j"]), count]]
        endpoint_route = [int(route[0]["i"])] + [int(q["j"]) for q in route]
        tail_start = endpoint_route[-1]
        tail_candidates = [
            {"i": tail_start, "j": j, "status": "basic_only"}
            for j in range(tail_start + 3, count + 1, 2)
            if basic(values, tail_start, j)
        ]
    else:
        unresolved, endpoint_route, tail_candidates = [[0, count]], [], []
    return {
        "profile": PROFILE,
        "scope": "Experimental strict profile, not author-unique or Chan-complete",
        "prices": list(values),
        "pens": count,
        "nodes": nodes,
        "edges": edges,
        "certificates": certificates,
        "candidate_events": events,
        "rejection_stats": dict(rejections),
        "selection": selected,
        "selected": route,
        "selected_endpoints": endpoint_route,
        "unresolved_pen_ranges": [item for item in unresolved if item[0] < item[1]],
        "tail_candidates": tail_candidates,
        "seconds": perf_counter() - started,
        "recognizer_policy": {
            "first_completion": "earliest evidence endpoint, then earliest geometry, kind order",
            "kind_order": list(_KIND_ORDER),
            "closed_initial_overlap": True,
            "strict_joint_feature_fractals": True,
            "direct_071_normalized_left_feature_guard": True,
            "descending_origins_compatibility_filter": True,
            "same_direction_future_new_extreme_invalidates_pending_boundary": True,
            "conditional_secondary_requires_parent": True,
            "secondary_right_structure_basic_required": True,
            "permanent_confirmation": False,
        },
    }
