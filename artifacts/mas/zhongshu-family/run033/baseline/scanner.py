"""Memo022 sequential centers, independent of tables, charts and API services."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite


@dataclass(frozen=True, slots=True)
class Segment:
    """One completed source segment; low/high include all its source strokes."""

    id: int
    snapshot_id: str
    source_start: int
    source_stop: int
    start_x: float
    end_x: float
    start_time: datetime
    end_time: datetime
    start_price: float
    end_price: float
    low: float
    high: float
    direction: int
    confirmed_at: datetime


@dataclass(frozen=True, slots=True)
class Crossing:
    """A boundary intersection interpolated on the segment endpoint chord."""

    segment_id: int
    fraction: float
    x: float
    time: datetime
    price: float


@dataclass(frozen=True, slots=True)
class Center:
    """Structural center; absent crossings are explicit geometry diagnostics."""

    start: int
    terminal: int | None
    confirmation: int | None
    observed_stop: int
    low: float
    high: float
    formation_at: datetime
    confirmed_at: datetime | None
    left: Crossing | None
    right: Crossing | None
    diagnostics: tuple[str, ...]

    @property
    def closed(self) -> bool:
        """Return whether the adjacent failed return confirms an ending."""
        return self.terminal is not None

    @property
    def drawable(self) -> bool:
        """Return whether both vertical boundaries can be located."""
        return self.closed and self.left is not None and self.right is not None


@dataclass(frozen=True, slots=True)
class Decision:
    """One seed or ending comparison against a fixed core."""

    stage: str
    index: int
    low: float
    high: float
    outcome: str


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Ordered centers, unassigned intervals and replayable decision records."""

    centers: tuple[Center, ...]
    unformed: tuple[tuple[int, int], ...]
    decisions: tuple[Decision, ...]


def validate_segments(segments: Sequence[Segment]) -> None:
    """Reject invalid ranges, mixed snapshots or discontinuous source chains."""
    previous: Segment | None = None
    for item in segments:
        for value in (item.id, item.source_start, item.source_stop):
            if type(value) is not int or value < 0:
                raise ValueError("nonnegative integer source identifiers required")
        if not isinstance(item.snapshot_id, str) or not item.snapshot_id:
            raise ValueError("snapshot_id required")
        if item.source_stop <= item.source_start:
            raise ValueError("source interval must increase")
        values = (
            item.start_x,
            item.end_x,
            item.start_price,
            item.end_price,
            item.low,
            item.high,
        )
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            for value in values
        ):
            raise ValueError("finite numeric coordinates required")
        if item.start_x >= item.end_x:
            raise ValueError("source x coordinates must increase")
        for moment in (item.start_time, item.end_time, item.confirmed_at):
            if not isinstance(moment, datetime) or moment.utcoffset() != timedelta(0):
                raise ValueError("timezone-aware UTC times required")
        if not item.start_time < item.end_time <= item.confirmed_at:
            raise ValueError("invalid geometric/evidence time order")
        if (
            type(item.direction) is not int
            or item.direction not in (-1, 1)
            or item.direction * (item.end_price - item.start_price) <= 0
        ):
            raise ValueError("direction must match unequal endpoint prices")
        if not (
            item.low
            <= min(item.start_price, item.end_price)
            <= max(item.start_price, item.end_price)
            <= item.high
        ):
            raise ValueError("actual range must contain both endpoints")
        if previous is not None and (
            previous.snapshot_id != item.snapshot_id
            or previous.id >= item.id
            or previous.source_stop != item.source_start
            or previous.end_x != item.start_x
            or previous.end_time != item.start_time
            or previous.end_price != item.start_price
            or previous.direction == item.direction
        ):
            raise ValueError("segments must share one continuous alternating snapshot")
        previous = item


def crossing(segment: Segment, boundary: float) -> Crossing | None:
    """Locate a horizontal boundary on an already validated endpoint chord."""
    fraction = (boundary - segment.start_price) / (
        segment.end_price - segment.start_price
    )
    if not 0 <= fraction <= 1:
        return None
    return Crossing(
        segment.id,
        fraction,
        segment.start_x + fraction * (segment.end_x - segment.start_x),
        segment.start_time + fraction * (segment.end_time - segment.start_time),
        boundary,
    )


def ending_reason(segment: Segment, following: Segment, low: float, high: float) -> str:
    """Check actual departure plus the immediately adjacent completed return."""
    if segment.low > high or segment.high < low:
        return "no_core_contact"
    if segment.direction == 1 and segment.end_price > high:
        return "closed_up" if following.low > high else "returned"
    if segment.direction == -1 and segment.end_price < low:
        return "closed_down" if following.high < low else "returned"
    return "no_directional_exit"


def scan_zhongshus(segments: Sequence[Segment]) -> ScanResult:
    """Select earliest closed-interval seed, then its first confirmed departure.

    Zero-height cores are accepted. Missing chord intersections never invent
    coordinates or alter the structural sequence. EOF leaves a single open
    center or an unformed tail. Confirmation segments may seed the next center.
    """
    validate_segments(segments)
    centers: list[Center] = []
    unformed: list[tuple[int, int]] = []
    decisions: list[Decision] = []
    n, cursor = len(segments), 0
    while cursor < n:
        start = cursor
        while start + 2 < n:
            seed = segments[start : start + 3]
            low, high = max(x.low for x in seed), min(x.high for x in seed)
            decisions.append(
                Decision(
                    "seed", start, low, high, "accepted" if low <= high else "disjoint"
                )
            )
            if low <= high:
                break
            start += 1
        else:
            unformed.append((cursor, n))
            break
        if start > cursor:
            unformed.append((cursor, start))
        first = segments[start]
        left = crossing(first, low if first.direction == 1 else high)
        diagnostics: tuple[str, ...] = (
            () if left is not None else ("left_crossing_missing",)
        )
        formation_at = max(x.confirmed_at for x in segments[start : start + 3])
        evidence_at = formation_at
        for end in range(start + 2, n - 1):
            current, following = segments[end], segments[end + 1]
            evidence_at = max(evidence_at, following.confirmed_at)
            reason = ending_reason(current, following, low, high)
            decisions.append(Decision("ending", end, low, high, reason))
            if not reason.startswith("closed_"):
                continue
            right = crossing(current, high if reason == "closed_up" else low)
            if right is None:
                diagnostics += ("right_crossing_missing",)
            centers.append(
                Center(
                    start,
                    end,
                    end + 1,
                    end + 1,
                    low,
                    high,
                    formation_at,
                    evidence_at,
                    left,
                    right,
                    diagnostics,
                )
            )
            cursor = end + 1
            break
        else:
            centers.append(
                Center(
                    start,
                    None,
                    None,
                    n,
                    low,
                    high,
                    formation_at,
                    None,
                    left,
                    None,
                    diagnostics,
                )
            )
            decisions.append(Decision("ending", n - 1, low, high, "open_eof"))
            break
    return ScanResult(tuple(centers), tuple(unformed), tuple(decisions))
