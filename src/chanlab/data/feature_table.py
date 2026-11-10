"""Coordinate mixed merged/fractal table registrations without changing v1 formats."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.data import fenxing_table as fx
from chanlab.data import merged_kline_table as mk

if TYPE_CHECKING:
    from chanlab.algo.chan_table import ChanTable

Feature = MergedKlineSeries | FenxingSeries


def contexts(features: Mapping[str, Feature]) -> dict[str, str]:
    """Generate independent versioned payloads for each registered family."""
    merged = {k: v for k, v in features.items() if isinstance(v, MergedKlineSeries)}
    result = {mk.FEATURE_CONTEXT: mk.encode_features(merged)} if merged else {}
    if any(isinstance(v, FenxingSeries) for v in features.values()):
        result[fx.FEATURE_CONTEXT] = fx.encode_features(features)
    return result


def project_one(series: Feature) -> dict[str, tuple[Any, ...]]:
    """Project a single scoped result."""
    return (
        fx.projection(series)
        if isinstance(series, FenxingSeries)
        else mk.projection(series)
    )


def visible_projection(features: Mapping[str, Feature]) -> dict[str, tuple[Any, ...]]:
    """First registration in each family supplies the fixed CSV columns."""
    projected = {}
    for cls in (MergedKlineSeries, FenxingSeries):
        series = next((s for s in features.values() if isinstance(s, cls)), None)
        if series is not None:
            projected.update(project_one(series))
    return projected


def register(series: Feature, table: ChanTable, key: str) -> ChanTable:
    """Preserve all registrations; auto-register a missing exact upstream."""
    from chanlab.algo.chan_table import ChanTable

    if not isinstance(key, str) or not key.strip():
        raise ValueError("series_key required")
    series.validate()
    table.validate()
    raw = (
        series.source_series.source_series
        if isinstance(series, FenxingSeries)
        else series.source_series
    )
    if raw is not table.source_series:
        raise ValueError("table and feature must reference exact same raw snapshot")
    features = dict(table.feature_series)
    if key in features and features[key] is not series:
        raise ValueError("series_key already registered with a different result")
    if isinstance(series, FenxingSeries) and not any(
        s is series.source_series for s in features.values()
    ):
        upstream_key = f"{key}:source"
        if upstream_key in features or upstream_key == key:
            raise ValueError("upstream key collision")
        features[upstream_key] = series.source_series
    features[key] = series
    context = dict(table.context)
    context.update(contexts(features))
    rows = [dict(row) for row in table]
    for column, values in visible_projection(features).items():
        for i, value in enumerate(values):
            rows[i][column] = (
                ("NA" if value is None else value)
                if column in ("mk_direction", "fx_kind")
                else json.dumps(value, separators=(",", ":"))
            )
    return ChanTable(rows, context, source_series=raw, feature_series=features)
