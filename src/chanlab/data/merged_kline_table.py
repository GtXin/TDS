"""Lossless merged-feature context and raw-time table projection adapters."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict
from hashlib import sha256
from typing import TYPE_CHECKING, Any

from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries

if TYPE_CHECKING:
    from chanlab.algo.chan_table import ChanTable

FEATURE_CONTEXT = "chanlab.merged_features.v1"


def source_digest(raw: KlineTSeries) -> str:
    """Fingerprint every raw value and provenance label for persisted source checks."""
    payload = [
        [
            b.timestamp.isoformat(),
            b.symbol,
            b.period,
            b.source,
            float(b.open),
            float(b.high),
            float(b.low),
            float(b.close),
            float(b.volume),
        ]
        for b in raw
    ]
    return sha256(
        json.dumps(payload, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def encode_features(features: dict[str, MergedKlineSeries]) -> str:
    """Serialize records and scoped traces without copying raw bars."""

    def work(w: Mapping[str, Any] | None) -> dict[str, Any] | None:
        if w is None:
            return None
        return {
            k: w[k] for k in ("low", "high", "direction", "source_start", "source_stop")
        }

    result = {}
    for key, series in features.items():
        result[key] = {
            "class_name": "MergedKlineSeries",
            "level": "raw",
            "source_digest": source_digest(series.source_series),
            "config": dict(series.config),
            "rule_tree_ref": series.rule_tree_ref,
            "records": [asdict(x) for x in series],
            "trace_by_point": series.trace_by_point,
            "trace": [
                {
                    "rule": t["rule"],
                    "raw_index": t["raw_index"],
                    "before": work(t["before"]),
                    "candidate": work(t["candidate"]),
                    "after": work(t["after"]),
                }
                for t in series.trace
            ],
        }
        result[key]["result_version"] = sha256(
            json.dumps(
                result[key], sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def decode_features(payload: str, raw: KlineTSeries) -> dict[str, MergedKlineSeries]:
    """Restore exact saved result fields against the loaded raw snapshot."""
    try:
        objects = json.loads(payload)
        result = {}
        for key, data in objects.items():
            versioned = dict(data)
            version = versioned.pop("result_version")
            if (
                version
                != sha256(
                    json.dumps(
                        versioned,
                        sort_keys=True,
                        separators=(",", ":"),
                        allow_nan=False,
                    ).encode()
                ).hexdigest()
            ):
                raise ValueError("feature result version mismatch")
            if not isinstance(key, str) or not key.strip():
                raise ValueError("invalid feature key")
            if (
                data["class_name"] != "MergedKlineSeries"
                or data["level"] != "raw"
                or data["source_digest"] != source_digest(raw)
            ):
                raise ValueError("feature class/level/source digest mismatch")
            steps = []
            for t in data["trace"]:
                steps.append(
                    {
                        "rule": t["rule"],
                        "raw_index": t["raw_index"],
                        "before": dict(raw=raw, **t["before"]),
                        "candidate": (
                            None
                            if t["candidate"] is None
                            else dict(raw=raw, **t["candidate"])
                        ),
                        "after": dict(raw=raw, **t["after"]),
                    }
                )
            result[key] = MergedKlineSeries(
                raw,
                tuple(MergedKline(**x) for x in data["records"]),
                data["config"],
                data["rule_tree_ref"],
                tuple(steps),
                tuple(tuple(x) for x in data["trace_by_point"]),
            )
        return result
    except (TypeError, KeyError, AttributeError, ValueError) as exc:
        raise ValueError(f"invalid merged feature context: {exc}") from exc


def projection(series: MergedKlineSeries) -> dict[str, tuple[Any, ...]]:
    """Generate ID tuples and start-only direction on the raw time axis."""
    n = len(series.source_series)
    ids: list[tuple[int, ...]] = [() for _ in range(n)]
    starts: list[tuple[int, ...]] = [() for _ in range(n)]
    ends: list[tuple[int, ...]] = [() for _ in range(n)]
    directions: list[str | None] = [None] * n
    for bar in series:
        for i in range(bar.source_start, bar.source_stop):
            ids[i] = (bar.id,)
        starts[bar.source_start] = (bar.id,)
        ends[bar.source_stop - 1] = (bar.id,)
        directions[bar.source_start] = bar.direction
    return {
        "mk_ids": tuple(ids),
        "mk_start_ids": tuple(starts),
        "mk_end_ids": tuple(ends),
        "mk_direction": tuple(directions),
    }


def register(series: MergedKlineSeries, table: ChanTable, key: str) -> ChanTable:
    """Return a new table retaining source/object identity and prior registrations."""
    from chanlab.data.feature_table import register as register_feature

    return register_feature(series, table, key)


def to_dataframe(series: MergedKlineSeries) -> Any:
    """Return a detached compact DataFrame with provenance stored in attrs."""
    try:
        import pandas as pd  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "DataFrame export requires pandas; install `uv sync --extra dataframe`."
        ) from exc
    series.validate()
    frame = pd.DataFrame([asdict(bar) for bar in series])
    frame["confirmed_at"] = pd.to_datetime(frame["confirmed_at"], utc=True).astype(
        "datetime64[ns, UTC]"
    )
    frame.attrs.update(
        source_digest=source_digest(series.source_series),
        result_version=json.loads(encode_features({"merged": series}))["merged"][
            "result_version"
        ],
        config=dict(series.config),
        rule_tree_ref=series.rule_tree_ref,
        source_context=[
            {
                "symbol": b.symbol,
                "period": b.period,
                "source": b.source,
                "timestamp": b.timestamp.isoformat(),
            }
            for b in series.source_series
        ],
        trace_by_point=series.trace_by_point,
    )
    return frame
