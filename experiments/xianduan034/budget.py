"""Measure exact initialized DP state count without allocating those states."""

from __future__ import annotations

from bisect import bisect_left
from typing import Any


def seed_count(data: dict[str, Any], pens: list[Any]) -> int:
    """Count production solve's initialized (a,b,c) keys with identical tests."""
    if not pens:
        return 0
    p = [float(pens[0]["start"]["price"])] + [float(x["end"]["price"]) for x in pens]
    n = len(pens)
    mode = data["xd_mode"]

    def shape(a: int, b: int) -> bool:
        if b - a < 3 or (b - a) % 2 == 0:
            return False
        d = 1 if p[a + 1] > p[a] else -1
        return (
            d * (p[b] - p[a]) > 0
            and (mode == "weak" or d * (p[b] - p[a + 1]) > 0)
            and max(min(p[k], p[k + 1]) for k in range(a, a + 3))
            <= min(max(p[k], p[k + 1]) for k in range(a, a + 3))
        )

    ends = {a: [b for b in range(a + 3, n + 1, 2) if shape(a, b)] for a in range(n)}
    event_map: dict[tuple[int, int], dict[tuple[str, int | None], Any]] = {}
    for q in data["nodes"]:
        if not q["root"]:
            continue
        a, b = q["i"], q["j"]
        c = q["certificate"]
        key = ("gap", c["reverse_end"]) if c["kind"] == "gap" else ("direct", None)
        values = event_map.setdefault((a, b), {})
        old = values.get(key)
        if old is None or c["dep_endpoint"] < old["dep_endpoint"]:
            values[key] = c
    count = 0
    for (a, b), events in event_map.items():
        if b not in ends[a]:
            continue
        candidates = ends.get(b, [])
        direct = events.get(("direct", None))
        threshold = direct["dep_endpoint"] if direct else n + 1
        count += len(candidates) - bisect_left(candidates, threshold)
        count += sum(
            1
            for kind, turn in events
            if kind == "gap" and turn is not None and turn < threshold and shape(b, turn)
        )
    return count
