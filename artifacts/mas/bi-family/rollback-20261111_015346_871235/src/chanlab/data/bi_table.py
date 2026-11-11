"""Selected stroke-route persistence and raw-anchor projection."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, fields
from typing import Any

from chanlab.algo.bi import Bi, BiSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.data.fenxing_table import fingerprint, plain

FEATURE_CONTEXT = "chanlab.bi_features.v1"


def encode_features(features: Mapping[str, Any]) -> str:
    """Serialize routes linked to exact fractal source and upstream evidence."""
    result = {}
    for key, s in features.items():
        if not isinstance(s, BiSeries):
            continue
        upstream = next((k for k, v in features.items() if v is s.source_series), None)
        if upstream is None:
            raise ValueError("stroke upstream must be registered")
        fx = s.source_series
        data = {
            "class_name": "BiSeries",
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
            "records": [asdict(p) for p in s],
            "trace": plain(s.trace),
            "trace_by_point": plain(s.trace_by_point),
        }
        data["result_version"] = fingerprint(data)
        result[key] = data
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def decode_features(payload: str, features: Mapping[str, Any]) -> dict[str, BiSeries]:
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
                or data["class_name"] != "BiSeries"
            ):
                raise ValueError("invalid stroke key/version")
            fx = features[data["upstream_key"]]
            if not isinstance(fx, FenxingSeries):
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
            result[key] = BiSeries(
                fx,
                tuple(Bi(**p) for p in data["records"]),
                data["config"],
                data["rule_tree_ref"],
                tuple(data["trace"]),
                tuple(tuple(x) for x in data["trace_by_point"]),
            )
        return result
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"invalid stroke context: {exc}") from exc


def projection(s: BiSeries) -> dict[str, tuple[Any, ...]]:
    """Inclusive raw intervals; direction appears only at each start anchor."""
    n = len(s.source_series.source_series.source_series)
    cols: dict[str, list[list[int]]] = {
        k: [[] for _ in range(n)] for k in ("bi_ids", "bi_start_ids", "bi_end_ids")
    }
    directions: list[str | None] = [None] * n
    for p in s:
        a = s.source_series[p.start_fenxing_index].anchor_raw_index
        b = s.source_series[p.end_fenxing_index].anchor_raw_index
        for i in range(a, b + 1):
            cols["bi_ids"][i].append(p.id)
        cols["bi_start_ids"][a].append(p.id)
        cols["bi_end_ids"][b].append(p.id)
        directions[a] = p.direction
    return {
        **{k: tuple(tuple(v) for v in values) for k, values in cols.items()},
        "bi_direction": tuple(directions),
    }


def to_dataframe(s: BiSeries) -> Any:
    """Detached compact records; attrs retain route/rules and raw provenance."""
    import pandas as pd  # type: ignore[import-untyped]

    s.validate()
    frame = pd.DataFrame([asdict(p) for p in s], columns=[f.name for f in fields(Bi)])
    frame["confirmed_at"] = pd.to_datetime(frame["confirmed_at"], utc=True)
    frame.attrs.update(
        config=plain(s.config),
        rule_tree_ref=s.rule_tree_ref,
        trace=plain(s.trace),
        source_context=dict(s.source_series.source_series.source_series.context),
    )
    return frame
