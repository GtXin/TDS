"""Compact fractal projection and lossless versioned metadata."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, fields
from hashlib import sha256
from typing import Any

from chanlab.algo.fenxing import Fenxing, FenxingSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.data.merged_kline_table import (
    encode_features as encode_merged,
)
from chanlab.data.merged_kline_table import (
    source_digest,
)

FEATURE_CONTEXT = "chanlab.fenxing_features.v1"


def plain(value: Any) -> Any:
    """Detach recursively frozen JSON evidence."""
    if isinstance(value, Mapping):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    return value


def fingerprint(value: Any) -> str:
    """Hash canonical JSON metadata."""
    return sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def encode_features(features: Mapping[str, FenxingSeries | MergedKlineSeries]) -> str:
    """Link each fractal to the exact registered upstream key and version."""
    result = {}
    for key, s in features.items():
        if not isinstance(s, FenxingSeries):
            continue
        upstream = next((k for k, v in features.items() if v is s.source_series), None)
        if upstream is None:
            raise ValueError("fractal upstream must be registered")
        data = {
            "class_name": "FenxingSeries",
            "level": "merged",
            "upstream_key": upstream,
            "upstream_version": json.loads(encode_merged({"source": s.source_series}))[
                "source"
            ]["result_version"],
            "source_digest": source_digest(s.source_series.source_series),
            "config": dict(s.config),
            "rule_tree_ref": s.rule_tree_ref,
            "records": [asdict(p) for p in s],
            "trace": plain(s.trace),
            "trace_by_point": plain(s.trace_by_point),
        }
        data["result_version"] = fingerprint(data)
        result[key] = data
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def decode_features(
    payload: str, features: Mapping[str, MergedKlineSeries]
) -> dict[str, FenxingSeries]:
    """Restore and validate records against already restored merged sources."""
    try:
        result = {}
        for key, data in json.loads(payload).items():
            versioned = dict(data)
            version = versioned.pop("result_version")
            if not isinstance(key, str) or not key.strip() or key in features:
                raise ValueError("invalid/duplicate fractal key")
            upstream = features[data["upstream_key"]]
            upstream_version = json.loads(encode_merged({"source": upstream}))[
                "source"
            ]["result_version"]
            if (
                version != fingerprint(versioned)
                or data["class_name"] != "FenxingSeries"
                or data["level"] != "merged"
                or data["upstream_version"] != upstream_version
                or data["source_digest"] != source_digest(upstream.source_series)
            ):
                raise ValueError("fractal version/class/source mismatch")
            result[key] = FenxingSeries(
                upstream,
                tuple(Fenxing(**p) for p in data["records"]),
                data["config"],
                data["rule_tree_ref"],
                tuple(data["trace"]),
                tuple(tuple(t) for t in data["trace_by_point"]),
            )
        return result
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError(f"invalid fractal context: {exc}") from exc


def projection(s: FenxingSeries) -> dict[str, tuple[Any, ...]]:
    """Project overlapping merged windows and actual anchors to raw positions."""
    n = len(s.source_series.source_series)
    cols: dict[str, list[list[int]]] = {
        k: [[] for _ in range(n)]
        for k in ("fx_ids", "fx_start_ids", "fx_end_ids", "fx_anchor_ids")
    }
    kinds: list[str | None] = [None] * n
    for p in s:
        start = s.source_series[p.source_start].source_start
        stop = s.source_series[p.source_stop - 1].source_stop
        for j in range(start, stop):
            cols["fx_ids"][j].append(p.id)
        cols["fx_start_ids"][start].append(p.id)
        cols["fx_end_ids"][stop - 1].append(p.id)
        cols["fx_anchor_ids"][p.anchor_raw_index].append(p.id)
        kinds[p.anchor_raw_index] = p.kind
    return {
        **{k: tuple(tuple(x) for x in values) for k, values in cols.items()},
        "fx_kind": tuple(kinds),
    }


def to_dataframe(s: FenxingSeries) -> Any:
    """Return stable empty/nonempty record columns with UTC confirmation dtype."""
    try:
        import pandas as pd  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "DataFrame export requires pandas; install `uv sync --extra dataframe`."
        ) from exc
    s.validate()
    frame = pd.DataFrame(
        [asdict(p) for p in s], columns=[f.name for f in fields(Fenxing)]
    )
    for key in ("id", "anchor_raw_index", "source_start", "source_stop"):
        frame[key] = frame[key].astype("int64")
    frame["price"] = frame["price"].astype("float64")
    frame["confirmed_at"] = pd.to_datetime(frame["confirmed_at"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    metadata = json.loads(encode_features({"upstream": s.source_series, "fenxing": s}))[
        "fenxing"
    ]
    frame.attrs.update(
        metadata, source_context=dict(s.source_series.source_series.context)
    )
    return frame
