"""Source-preserving projection from completed memo031 segments to memo022."""

from __future__ import annotations

from chanlab.algo._zhongshu_scan import Segment, validate_segments
from chanlab.algo.xianduan import XianduanSeries


def project_xianduans(series: XianduanSeries, snapshot_id: str) -> tuple[Segment, ...]:
    """Read actual stroke extrema and raw endpoint anchors without reslicing.

    The caller supplies the exact input-context fingerprint. Existing immutable
    XianduanSeries construction validates source identities and completion.
    Unconfirmed upstream tail candidates are deliberately not projected.
    """
    if not isinstance(series, XianduanSeries):
        raise ValueError("completed XianduanSeries required")  # noqa: TRY004
    pens = series.source_series
    fractals = pens.source_series
    raw = fractals.source_series.source_series
    projected: list[Segment] = []
    for segment in series:
        if segment.confirmed_at is None:
            raise ValueError("source segment has no completion evidence")
        members = pens[segment.source_start : segment.source_stop]
        first = fractals[members[0].start_fenxing_index]
        last = fractals[members[-1].end_fenxing_index]
        prices = [p for pen in members for p in (pen.start_price, pen.end_price)]
        projected.append(
            Segment(
                segment.id,
                snapshot_id,
                segment.source_start,
                segment.source_stop,
                float(first.anchor_raw_index),
                float(last.anchor_raw_index),
                raw[first.anchor_raw_index].timestamp,
                raw[last.anchor_raw_index].timestamp,
                segment.start_price,
                segment.end_price,
                min(prices),
                max(prices),
                1 if segment.direction == "up" else -1,
                segment.confirmed_at,
            )
        )
    validate_segments(projected)
    return tuple(projected)
