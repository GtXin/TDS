"""XD030-B event enumeration with same-mode checks for all support intervals."""

from __future__ import annotations

from functools import cache
from typing import Any


def scanner(
    prices: list[float], mode: str, rec: Any, reference: Any, independent: bool = False
) -> Any:
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

    @cache
    def norm(a: int, b: int, d: int) -> Any:
        if independent:
            return tuple(
                rec.Element(e[0], e[1], tuple(e[2]))
                for e in reference.reduced(tuple(range(a, b, 2)), d)
            )
        return rec.normalize(prices, range(a, b, 2), d)

    def stale(b: int, h: int, d: int) -> bool:
        return any(d * (prices[t] - prices[b]) > 0 for t in range(b + 1, h + 1))

    def turn(es: Any, d: int) -> bool:
        l, m, r = es
        return all(
            d * (getattr(m, key) - getattr(x, key)) > 0
            for key in ("high", "low")
            for x in (l, r)
        )

    def anchor(e: Any, d: int) -> int:
        return (max if d == 1 else min)(
            e.members,
            key=lambda k: max(prices[k : k + 2]) if d == 1 else min(prices[k : k + 2]),
        )

    def candidates(a: int, b: int) -> list[dict[str, Any]]:
        if not shape(a, b) or b == n:
            return []
        d = 1 if prices[a + 1] > prices[a] else -1
        left = norm(a + 1, b, d)[-1]
        out = []
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
                    out.append(
                        {
                            "kind": "no_gap",
                            "dep_endpoint": h1,
                            "reverse_end": None,
                            "supports": [[b, b + 3], [b, h1]],
                            "h1": h1,
                        }
                    )
            else:
                for h2 in range(b + 2, n + 1, 2):
                    if stale(b, h2, d):
                        break
                    second = norm(b + 1, h2, -d)
                    if len(second) < 3 or not turn(second[-3:], -d):
                        continue
                    c = anchor(second[-2], -d)
                    h = max(h1, h2)
                    if (
                        b < c < h
                        and h1 <= c
                        and not stale(b, h, d)
                        and shape(b, c)
                        and shape(c, h)
                    ):
                        out.append(
                            {
                                "kind": "gap",
                                "dep_endpoint": h,
                                "reverse_end": c,
                                "supports": [[b, c], [c, h]],
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
                    out.append(
                        {
                            "kind": "direct_071",
                            "dep_endpoint": h,
                            "reverse_end": h,
                            "supports": [[b, h]],
                        }
                    )
                    break
        # Distinct event watermarks remain distinct certificates.
        for c in out:
            c.update(
                profile="XD030-B",
                i=a,
                j=b,
                direction="up" if d == 1 else "down",
                dep_pen=c["dep_endpoint"] - 1,
                xd_mode=mode,
            )
        return sorted(
            out,
            key=lambda c: (
                {"no_gap": 0, "gap": 1, "direct_071": 2}[c["kind"]],
                c["dep_endpoint"],
                c.get("h1", 0),
                c.get("h2", 0),
            ),
        )

    return candidates, shape
