"""Versioned center persistence and integer raw-member table projection."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from datetime import datetime
from typing import Any

from chanlab.algo._zhongshu_scan import Center, Crossing, Decision
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.zhongshu import Zhongshu, ZhongshuSeries
from chanlab.data.fenxing_table import fingerprint
from chanlab.data.merged_kline_table import source_digest

FEATURE_CONTEXT = "chanlab.zhongshu_features.v1"


def jsonable(value: Any) -> Any:
    """Detach nested evidence and encode exact UTC times as ISO labels."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    return value


def source_fingerprint(source: XianduanSeries) -> str:
    """Include full raw provenance and all upstream rule/record/evidence contexts."""
    from chanlab.data.feature_table import contexts

    chain: dict[str, Any] = {}
    current: Any = source
    while hasattr(current, "source_series"):
        chain[f"source{len(chain)}"] = current
        current = current.source_series
    return fingerprint({"contexts": contexts(chain), "raw": source_digest(current)})


def encode_features(features: Mapping[str, Any]) -> str:
    """Link every center result to an exact registered segment snapshot."""
    result = {}
    for key, s in features.items():
        if not isinstance(s, ZhongshuSeries):
            continue
        upstream = next((k for k, v in features.items() if v is s.source_series), None)
        if upstream is None:
            raise ValueError("segment upstream must be registered")
        data = jsonable(
            {
                "class_name": "ZhongshuSeries",
                "upstream_key": upstream,
                "upstream_digest": source_fingerprint(s.source_series),
                "level": s.level,
                "config": dict(s.config),
                "rule_tree_ref": s.rule_tree_ref,
                "records": [asdict(x) for x in s],
                "trace": [asdict(x) for x in s.trace],
                "trace_by_point": s.trace_by_point,
                "unformed": s.unformed,
            }
        )
        data["result_version"] = fingerprint(data)
        result[key] = data
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def decode_geometry(data: Mapping[str, Any]) -> Center:
    """Restore typed immutable intersections and structural evidence."""
    values = dict(data)
    for key in ("left", "right"):
        v = values[key]
        values[key] = (
            None
            if v is None
            else Crossing(**{**v, "time": datetime.fromisoformat(v["time"])})
        )
    for key in ("formation_at", "confirmed_at"):
        values[key] = (
            None if values[key] is None else datetime.fromisoformat(values[key])
        )
    values["diagnostics"] = tuple(values["diagnostics"])
    return Center(**values)


def decode_features(
    payload: str, features: Mapping[str, Any]
) -> dict[str, ZhongshuSeries]:
    """Reject corrupt versions, source mismatches and even rehashed invalid results."""
    try:
        result = {}
        for key, data in json.loads(payload).items():
            checked = dict(data)
            version = checked.pop("result_version")
            if (
                not isinstance(key, str)
                or not key.strip()
                or key in features
                or version != fingerprint(checked)
                or data["class_name"] != "ZhongshuSeries"
            ):
                raise ValueError("invalid center key/version")
            source = features[data["upstream_key"]]
            if not isinstance(source, XianduanSeries):
                raise ValueError("invalid center upstream class")  # noqa: TRY004
            if data["upstream_digest"] != source_fingerprint(source):
                raise ValueError("center upstream fingerprint mismatch")
            result[key] = ZhongshuSeries(
                data["level"],
                source,
                tuple(
                    Zhongshu(
                        **{
                            **r,
                            "confirmed_at": (
                                None
                                if r["confirmed_at"] is None
                                else datetime.fromisoformat(r["confirmed_at"])
                            ),
                            "geometry": decode_geometry(r["geometry"]),
                        }
                    )
                    for r in data["records"]
                ),
                data["config"],
                data["rule_tree_ref"],
                tuple(Decision(**d) for d in data["trace"]),
                tuple(tuple(x) for x in data["trace_by_point"]),
                tuple(tuple(x) for x in data["unformed"]),
            )
        return result
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError) as exc:
        raise ValueError(f"invalid center context: {exc}") from exc


def projection(series: ZhongshuSeries) -> dict[str, tuple[Any, ...]]:
    """Project source-member anchors; fractional rectangle edges stay in context.

    For open structures no terminal marker is emitted. Bounds are scalar start
    annotations, matching memo009. All registrations retain scoped memberships.
    """
    n = len(
        series.source_series.source_series.source_series.source_series.source_series
    )
    cols: dict[str, list[list[int]]] = {
        k: [[] for _ in range(n)] for k in ("zs_ids", "zs_start_ids", "zs_end_ids")
    }
    lower: list[float | None] = [None] * n
    upper: list[float | None] = [None] * n
    for z in series:
        for i in range(z.start_raw_index, z.end_raw_index + 1):
            cols["zs_ids"][i].append(z.id)
        cols["zs_start_ids"][z.start_raw_index].append(z.id)
        if z.status == "closed":
            cols["zs_end_ids"][z.end_raw_index].append(z.id)
        lower[z.start_raw_index], upper[z.start_raw_index] = z.lower, z.upper
    return {
        **{k: tuple(tuple(x) for x in v) for k, v in cols.items()},
        "zs_lower": tuple(lower),
        "zs_upper": tuple(upper),
    }
