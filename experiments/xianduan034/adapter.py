"""Adapt foreign KWX input to a native raw ChanTable plus comparison archive.

Foreign confirmation policies and structural mappings are deliberately retained
in the comparison archive, rather than relabelled as native algorithm results.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Any

from compare import INPUT, ROOT, foreign

from chanlab.algo.chan_table import ChanTable
from chanlab.algo.kline import KlineTSeries


def adapt(source: Path = INPUT, target: Path = ROOT / "adapted") -> dict[str, Any]:
    """Export a native raw input and losslessly preserve foreign feature data."""
    target.mkdir(parents=True, exist_ok=True)
    raw = KlineTSeries.read_csv(source / "ChanTable.csv", source / "context.csv")
    table = ChanTable.from_source_series(raw, raw.context)
    table.write_csv(target / "table.csv", target / "context.csv")
    loaded = ChanTable.read_csv(target / "table.csv", target / "context.csv")
    assert tuple(loaded.source_series) == tuple(raw)
    assert dict(loaded.context) == dict(raw.context)
    assert not loaded.feature_series
    with (source / "ChanTable.csv").open(newline="") as stream:
        original_rows = list(csv.DictReader(stream))
    raw_keys = (
        "raw_index",
        "timestamp",
        "symbol",
        "period",
        "source",
        "open",
        "high",
        "low",
        "close",
        "volume",
    )
    assert all(
        all(
            (
                float(a[k]) == float(b[k])
                if k in ("open", "high", "low", "close", "volume")
                else a[k] == b[k]
            )
            for k in raw_keys
        )
        for a, b in zip(original_rows, loaded.rows, strict=True)
    )
    # Preserve all foreign fields, including levels beyond the calculation scope.
    for filename in (
        "features.json",
        "cc_native_snapshot.json",
        "import_report.json",
        "comparison.json",
        "verification.json",
    ):
        data = json.loads((source / filename).read_text())
        with gzip.open(target / (filename + ".gz"), "wt") as stream:
            json.dump(data, stream)
        with gzip.open(target / (filename + ".gz"), "rt") as stream:
            assert json.load(stream) == data
    normalized = foreign()
    report = {
        "status": "PASS",
        "native_input": str(target / "table.csv"),
        "raw_rows": len(raw),
        "raw_values_and_context_equal": True,
        "native_ChanTable_roundtrip": True,
        "foreign_feature_archive_roundtrip": True,
        "feature_policy": "Native input has NA feature columns; derive native objects from raw. Foreign features remain external comparisons, with original statuses and source graph preserved.",
        "mapping_span_vs_native_endpoint_differences": {
            kind: sum(
                r.get("mapping_span_differs_from_geometry", False) for r in records
            )
            for kind, records in normalized.items()
        },
        "normalized_comparison": "../kwx-normalized.json.gz",
    }
    (target / "adapter-report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print(json.dumps(adapt(), indent=2))
