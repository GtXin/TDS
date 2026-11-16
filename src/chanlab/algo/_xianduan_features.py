"""Fixed-direction feature reduction from memo030002.c; native shared implementation."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from math import isfinite


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
