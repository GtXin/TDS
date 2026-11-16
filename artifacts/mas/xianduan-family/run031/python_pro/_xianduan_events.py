"""XD030-E local event enumeration with same-mode checks for all support intervals."""

from __future__ import annotations

from collections.abc import Callable
from functools import cache
from typing import Any, cast

from chanlab.algo import _xianduan_features as rec


def scanner(
    prices: list[float], mode: str
) -> tuple[Callable[[int, int], list[dict[str, Any]]], Callable[[int, int], bool]]:
    """Bind immutable input and select stack or independent full-list reduction."""
    n = len(prices) - 1

    def shape(a: int, b: int) -> bool:
        if not 0 <= a < b <= n or b - a < 3 or (b - a) % 2 == 0:
            return False
        d = 1 if prices[a + 1] > prices[a] else -1
        intervals = [
            (min(prices[k : k + 2]), max(prices[k : k + 2])) for k in range(a, a + 3)
        ]
        return (
            max(x[0] for x in intervals) <= min(x[1] for x in intervals)
            and d * (prices[b] - prices[a]) > 0
            and (mode == "weak" or d * (prices[b] - prices[a + 1]) > 0)
        )

    # First strict crossing makes the invalidation guard O(1) per event.
    crossing: dict[tuple[int, int], int] = {}
    for boundary in range(n):
        for direction in (-1, 1):
            crossing[boundary, direction] = next(
                (
                    h
                    for h in range(boundary + 1, n + 1)
                    if direction * (prices[h] - prices[boundary]) > 0
                ),
                n + 1,
            )

    @cache
    def norm(a: int, b: int, d: int) -> Any:
        # Extend a cached prefix instead of re-reducing every earlier element.
        if b - a <= 2:
            return rec.normalize(prices, range(a, b, 2), d)
        stack = list(norm(a, b - 2, d))
        index = a + 2 * ((b - a - 1) // 2)
        rec._append(stack, rec._raw(prices, index), d)
        return tuple(stack)

    def stale(b: int, h: int, d: int) -> bool:
        return crossing[b, d] <= h

    def turn(es: Any, d: int) -> bool:
        l, m, r = es
        return all(
            d * (getattr(m, key) - getattr(x, key)) > 0
            for key in ("high", "low")
            for x in (l, r)
        )

    def anchor(e: Any, d: int) -> int:
        return int(
            (max if d == 1 else min)(
                e.members,
                key=lambda k: (
                    max(prices[k : k + 2]) if d == 1 else min(prices[k : k + 2])
                ),
            )
        )

    @cache
    def second_events(b: int, d: int) -> tuple[tuple[int, int], ...]:
        found = []
        for h2 in range(b + 2, n + 1, 2):
            if stale(b, h2, d):
                break
            second = norm(b + 1, h2, -d)
            if len(second) < 3 or not turn(second[-3:], -d):
                continue
            c = anchor(second[-2], -d)
            if b < c < h2 and shape(b, c) and shape(c, h2):
                found.append((h2, c))
        return tuple(found)

    def candidates(a: int, b: int) -> list[dict[str, Any]]:
        if not shape(a, b) or b == n:
            return []
        d = 1 if prices[a + 1] > prices[a] else -1
        left = norm(a + 1, b, d)[-1]
        out: dict[tuple[str, int | None], dict[str, Any]] = {}

        def add(w: dict[str, Any]) -> None:
            key = ("gap", w["reverse_end"]) if w["kind"] == "gap" else ("direct", None)
            old = out.get(key)
            if old is None or w["dep_endpoint"] < old["dep_endpoint"]:
                out[key] = w

        for h1 in range(b + 1, n + 1, 2):
            if stale(b, h1, d):
                break
            right = norm(b, h1, d)
            if anchor(right[0], d) != b:
                break
            if len(right) < 2 or not turn((left, right[0], right[1]), d):
                continue
            mid = right[0]
            gap = left.high < mid.low if d == 1 else left.low > mid.high
            if not gap:
                if shape(b, b + 3) and shape(b, h1):
                    add(
                        {
                            "kind": "no_gap",
                            "dep_endpoint": h1,
                            "reverse_end": None,
                            "supports": [[b, b + 3], [b, h1]],
                            "h1": h1,
                        }
                    )
            else:
                for h2, c in second_events(b, d):
                    if h1 <= c:
                        add(
                            {
                                "kind": "gap",
                                "dep_endpoint": h2,
                                "reverse_end": c,
                                "supports": [[b, c], [c, h2]],
                                "h1": h1,
                                "h2": h2,
                            }
                        )
        guard = left.high < prices[b] if d == 1 else left.low > prices[b]
        if guard and d * (prices[b + 1] - prices[b - 1]) < 0:
            for h in range(b + 3, n + 1, 2):
                if stale(b, h, d):
                    break
                if d * (prices[h] - prices[b + 1]) < 0 and shape(b, h):
                    add(
                        {
                            "kind": "direct_071",
                            "dep_endpoint": h,
                            "reverse_end": h,
                            "supports": [[b, h]],
                        }
                    )
                    break
        # Distinct event watermarks remain distinct certificates.
        for event in out.values():
            event.update(
                profile="XD030-E",
                i=a,
                j=b,
                direction="up" if d == 1 else "down",
                dep_pen=event["dep_endpoint"] - 1,
                xd_mode=mode,
            )
        return sorted(
            out.values(),
            key=lambda c: (
                {"no_gap": 0, "gap": 1, "direct_071": 2}[c["kind"]],
                c["dep_endpoint"],
                c.get("h1", 0),
                c.get("h2", 0),
            ),
        )

    cast(Any, candidates).clear = norm.cache_clear
    return candidates, shape
