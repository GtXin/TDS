"""Independent exhaustive candidate table used only for verification."""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction

from chanlab.algo._zhongshu_scan import Segment


def reference_route(
    segments: Sequence[Segment],
) -> list[tuple[int, int | None, float, float]]:
    """Enumerate every seed/exit pair before selecting a chronological route."""
    table: dict[int, tuple[int | None, float, float]] = {}
    for start in range(len(segments) - 2):
        first_three = segments[start : start + 3]
        lower = sorted(item.low for item in first_three)[2]
        upper = sorted(item.high for item in first_three)[0]  # noqa: FURB192
        if lower > upper:
            continue
        eligible: list[int] = []
        for end in range(start + 2, len(segments) - 1):
            leg, ret = segments[end : end + 2]
            contact = not (leg.high < lower or upper < leg.low)
            above = ret.low > upper and ret.high > upper
            below = ret.high < lower and ret.low < lower
            if contact and (
                (leg.end_price > leg.start_price and ret.start_price > upper and above)
                or (
                    leg.end_price < leg.start_price
                    and ret.start_price < lower
                    and below
                )
            ):
                eligible.append(end)
        table[start] = (min(eligible) if eligible else None, lower, upper)
    result: list[tuple[int, int | None, float, float]] = []
    boundary = 0
    while choices := sorted(start for start in table if start >= boundary):
        start = choices[0]
        selected_end, lower, upper = table[start]
        result.append((start, selected_end, lower, upper))
        if selected_end is None:
            break
        boundary = selected_end + 1
    return result


def rational_crossing(segment: Segment, price: float) -> tuple[float, float] | None:
    """Solve y=m*x+b with exact decimal fractions, independently of interpolation."""
    x0, x1 = Fraction(str(segment.start_x)), Fraction(str(segment.end_x))
    y0, y1 = Fraction(str(segment.start_price)), Fraction(str(segment.end_price))
    slope = (y1 - y0) / (x1 - x0)
    intercept = y0 - slope * x0
    x = (Fraction(str(price)) - intercept) / slope
    if not x0 <= x <= x1:
        return None
    return float(x), float((x - x0) / (x1 - x0))
