"""Selected stroke-route persistence and raw-anchor projection."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from datetime import datetime
from typing import Any

from chanlab.algo.bi import BiSeries
from chanlab.algo.xianduan import Xianduan, XianduanSeries
from chanlab.data.fenxing_table import fingerprint, plain

FEATURE_CONTEXT = "chanlab.xianduan_features.v1"


def encode_features(features: Mapping[str, Any]) -> str:
    """Serialize routes linked to exact fractal source and upstream evidence."""
    result = {}
    for key, s in features.items():
        if not isinstance(s, XianduanSeries):
            continue
        upstream = next((k for k, v in features.items() if v is s.source_series), None)
        if upstream is None:
            raise ValueError("stroke upstream must be registered")
        fx = s.source_series
        data = {
            "class_name": "XianduanSeries",
            "upstream_key": upstream,
            "upstream_digest": fingerprint(
                {
                    "records": [asdict(p) for p in fx],
                    "trace": plain(fx.trace),
                    "config": dict(fx.config),
                    "rule": fx.rule_tree_ref,
                }
            ),
            "config": plain(s.config),
            "rule_tree_ref": s.rule_tree_ref,
            "records": [
                {
                    **asdict(p),
                    "confirmed_at": (
                        p.confirmed_at.isoformat()
                        if p.confirmed_at is not None
                        else None
                    ),
                }
                for p in s
            ],
            "trace": plain(s.trace),
            "trace_by_point": plain(s.trace_by_point),
            "tail": plain(s.tail),
        }
        data["result_version"] = fingerprint(data)
        result[key] = data
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def decode_features(
    payload: str, features: Mapping[str, Any]
) -> dict[str, XianduanSeries]:
    """Restore selected routes and reject corrupt or mismatched source data."""
    result = {}
    try:
        for key, data in json.loads(payload).items():
            checked = dict(data)
            version = checked.pop("result_version")
            if (
                not isinstance(key, str)
                or not key.strip()
                or key in features
                or version != fingerprint(checked)
                or data["class_name"] != "XianduanSeries"
            ):
                raise ValueError("invalid stroke key/version")
            fx = features[data["upstream_key"]]
            if not isinstance(fx, BiSeries):
                raise ValueError("invalid upstream class")  # noqa: TRY004
            if data["upstream_digest"] != fingerprint(
                {
                    "records": [asdict(p) for p in fx],
                    "trace": plain(fx.trace),
                    "config": dict(fx.config),
                    "rule": fx.rule_tree_ref,
                }
            ):
                raise ValueError("upstream mismatch")
            result[key] = XianduanSeries(
                fx,
                tuple(
                    Xianduan(
                        **{
                            **p,
                            "confirmed_at": datetime.fromisoformat(p["confirmed_at"]),
                        }
                    )
                    for p in data["records"]
                ),
                data["config"],
                data["rule_tree_ref"],
                tuple(data["trace"]),
                tuple(tuple(x) for x in data["trace_by_point"]),
                tuple(tuple(x) for x in data["tail"]),
            )
        return result
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"invalid stroke context: {exc}") from exc


def projection(s: XianduanSeries) -> dict[str, tuple[Any, ...]]:
    """Project raw membership inclusively; direction at the start only."""
    bi = s.source_series
    fx = bi.source_series
    n = len(fx.source_series.source_series)
    cols: dict[str, list[list[int]]] = {
        k: [[] for _ in range(n)] for k in ("xd_ids", "xd_start_ids", "xd_end_ids")
    }
    directions: list[str | None] = [None] * n
    for x in s:
        a = fx[bi[x.source_start].start_fenxing_index].anchor_raw_index
        b = fx[bi[x.source_stop - 1].end_fenxing_index].anchor_raw_index
        for k in range(a, b + 1):
            cols["xd_ids"][k].append(x.id)
        cols["xd_start_ids"][a].append(x.id)
        cols["xd_end_ids"][b].append(x.id)
        directions[a] = x.direction
    return {
        **{k: tuple(tuple(v) for v in values) for k, values in cols.items()},
        "xd_direction": tuple(directions),
    }
