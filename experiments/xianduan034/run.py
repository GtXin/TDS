"""Execute fixed-snapshot memo034 using production algorithms without changes."""

from __future__ import annotations

import csv
import functools
import gzip
import hashlib
import itertools
import json
import os
import platform
import resource
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from chanlab.algo.bi import BiSeries
from chanlab.algo.chan_table import COLUMNS, ChanTable
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.xianduan import XianduanSeries
from chanlab.data.fenxing_table import plain

ROOT = Path("artifacts/mas/xianduan-newdata/run034")
INPUT = Path("artifacts/mas/cc-chantable-20261111-134106-27c20343")


def save(name: str, data: Any) -> None:
    """Write readable progress or compressed detailed evidence."""
    path = ROOT / name
    payload = json.dumps(data, default=str, ensure_ascii=False, indent=2)
    if name.endswith(".gz"):
        with gzip.open(path, "wt", encoding="utf-8") as stream:
            stream.write(payload)
    else:
        path.write_text(payload)


def digest(path: Path) -> str:
    """Return a file's SHA-256."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(series: Any, kind: str) -> list[dict[str, Any]]:
    """Map production records to raw coordinates without changing geometry."""
    records = []
    for point in series:
        row = asdict(point)
        if kind == "mk":
            row.update(raw_start=point.source_start, raw_stop=point.source_stop)
        elif kind == "fx":
            row.update(
                raw_start=series.source_series[point.source_start].source_start,
                raw_stop=series.source_series[point.source_stop - 1].source_stop,
                anchor=point.anchor_raw_index,
            )
        elif kind == "bi":
            row.update(
                start_raw=series.source_series[
                    point.start_fenxing_index
                ].anchor_raw_index,
                end_raw=series.source_series[point.end_fenxing_index].anchor_raw_index,
            )
        else:
            pens = series.source_series
            fractals = pens.source_series
            row.update(
                start_raw=fractals[
                    pens[point.source_start].start_fenxing_index
                ].anchor_raw_index,
                end_raw=fractals[
                    pens[point.source_stop - 1].end_fenxing_index
                ].anchor_raw_index,
            )
        records.append(row)
    return records


def compatibility() -> KlineTSeries:
    """Test native import, raw projection and lossless archive preservation."""
    ROOT.mkdir(parents=True, exist_ok=True)
    paths = list(INPUT.iterdir()) + [
        Path("docs/memo/memoWX_029_Chan_bi.md"),
        Path("docs/memo/memoWX_030_Chan_xianduan.md"),
    ]
    hashes = {str(p): digest(p) for p in paths if p.is_file()}
    save("source-hashes.json", hashes)
    result: dict[str, Any] = {"python": platform.python_version(), "hashes": hashes}
    try:
        ChanTable.read_csv(INPUT / "ChanTable.csv", INPUT / "context.csv")
        result["native_master_import"] = "PASS"
    except ValueError as exc:
        result["native_master_import"] = {"unsupported": str(exc)}
    raw = KlineTSeries.read_csv(INPUT / "ChanTable.csv", INPUT / "context.csv")
    result["raw_count"] = len(raw)
    with (INPUT / "ChanTable.csv").open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert tuple(reader.fieldnames or ()) == COLUMNS
        rows = list(reader)
    assert all(int(row["raw_index"]) == i for i, row in enumerate(rows))
    result["raw_index_contiguous"] = True
    result["timestamp_utc_ordered"] = all(
        bar.timestamp.utcoffset().total_seconds() == 0 for bar in raw
    ) and all(a.timestamp < b.timestamp for a, b in itertools.pairwise(raw))
    result["missing_by_column"] = {
        key: sum(row[key] in ("", "NA") for row in rows) for key in COLUMNS
    }
    folder = ROOT / "roundtrip"
    folder.mkdir(exist_ok=True)
    raw.write_csv(folder / "raw.csv", folder / "context.csv")
    reread = KlineTSeries.read_csv(folder / "raw.csv", folder / "context.csv")
    assert tuple(raw) == tuple(reread) and raw.context == reread.context
    result["raw_domain_roundtrip"] = "PASS; all bars and context values equal"
    # CSV and JSON envelopes preserve foreign objects without claiming native DTO support.
    with (folder / "foreign-master.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with (folder / "foreign-master.csv").open(newline="") as stream:
        assert list(csv.DictReader(stream)) == rows
    result["foreign_csv_cell_roundtrip"] = "PASS; all 41 string fields equal"
    mapping_checks = []
    features = json.loads((INPUT / "features.json").read_text())
    for series in features["series"]:
        records = series["records"]
        ids = {r["id"] for r in records}
        assert len(ids) == len(records)
        for record in records:
            assert 0 <= record["raw_start"] < record["raw_stop"] <= len(raw)
            anchor = record["anchor_raw_index"]
            assert anchor is None or record["raw_start"] <= anchor < record["raw_stop"]
        mapping_checks.append(
            {"key": series["key"], "kind": series["kind"], "count": len(records)}
        )
    for path in INPUT.glob("*.json"):
        data = json.loads(path.read_text())
        with gzip.open(folder / (path.name + ".gz"), "wt") as stream:
            json.dump(data, stream)
        with gzip.open(folder / (path.name + ".gz"), "rt") as stream:
            assert json.load(stream) == data
    result["foreign_json_roundtrip"] = (
        "PASS; JSON semantic equality; foreign schema retained"
    )
    result["foreign_series_ranges_ids"] = mapping_checks
    save("compatibility.json", result)
    print("compatibility", result["native_master_import"], len(raw), flush=True)
    return raw


def main() -> None:
    """Run all four modes, persisting each completed phase independently."""
    sys.setrecursionlimit(20000)
    compatibility()
    from adapter import adapt

    import chanlab.algo.xianduan as xd_module

    budget = int(os.environ.get("MEMO034_STATE_LIMIT", "40000000"))
    xd_module.solve = functools.partial(xd_module.solve, limit=budget)
    adapt()
    raw = ChanTable.read_csv(
        ROOT / "adapted/table.csv", ROOT / "adapted/context.csv"
    ).source_series
    timings: dict[str, float] = {}
    start = time.perf_counter()
    merged = MergedKlineSeries.derive_from(raw, {"initialization": "UP"}, "memo015")
    timings["merged"] = time.perf_counter() - start
    start = time.perf_counter()
    fx = FenxingSeries.derive_from(merged, {}, "memo019")
    timings["fx"] = time.perf_counter() - start
    save(
        "upstream.json.gz",
        {"raw": len(raw), "mk": normalize(merged, "mk"), "fx": normalize(fx, "fx")},
    )
    print("upstream", len(merged), len(fx), timings, flush=True)
    summary: dict[str, Any] = {
        "raw": len(raw),
        "mk": len(merged),
        "fx": len(fx),
        "timings": timings,
        "modes": {},
        "state_budget": budget,
        "recursion_limit": sys.getrecursionlimit(),
    }
    save("summary.json", summary)
    for bm in ("weak", "strong"):
        start = time.perf_counter()
        bi = BiSeries.derive_from(fx, {"distance_mode": bm}, "memo029")
        timings[f"bi-{bm}"] = time.perf_counter() - start
        save(
            f"bi-{bm}.json.gz",
            {
                "config": dict(bi.config),
                "records": normalize(bi, "bi"),
                "trace": plain(bi.trace),
            },
        )
        print("bi", bm, len(bi), timings[f"bi-{bm}"], flush=True)
        for xm in ("weak", "strong"):
            key = f"bi-{bm}_xd-{xm}"
            start = time.perf_counter()
            try:
                xd = XianduanSeries.derive_from(bi, {"xd_mode": xm})
            except (RuntimeError, RecursionError) as exc:
                summary["modes"][key] = {
                    "bi": len(bi),
                    "status": "incomplete",
                    "error": str(exc),
                    "seconds": time.perf_counter() - start,
                    "peak_rss_bytes": resource.getrusage(
                        resource.RUSAGE_SELF
                    ).ru_maxrss,
                }
                save("summary.json", summary)
                print("incomplete", key, summary["modes"][key], flush=True)
                import gc

                gc.collect()
                continue
            timings[key] = time.perf_counter() - start
            save(
                f"{key}.json.gz",
                {
                    "config": dict(xd.config),
                    "records": normalize(xd, "xd"),
                    "trace": plain(xd.trace),
                    "tail": plain(xd.tail),
                },
            )
            summary["modes"][key] = {
                "bi": len(bi),
                "xd": len(xd),
                "seconds": timings[key],
                "tail": plain(xd.tail),
            }
            save("summary.json", summary)
            print("xd", key, len(xd), timings[key], flush=True)
            # Native production registrations must round-trip their full source chain.
            dest = ROOT / key
            dest.mkdir(exist_ok=True)
            table = xd.to_chan_table(
                ChanTable.from_source_series(raw, raw.context), key
            )
            table.write_csv(dest / "table.csv", dest / "context.csv")
            loaded = ChanTable.read_csv(dest / "table.csv", dest / "context.csv")
            restored = XianduanSeries.from_chan_table(loaded, key)
            assert restored.items == xd.items and restored.tail == xd.tail
            assert plain(restored.trace) == plain(xd.trace)
            assert tuple(loaded.source_series) == tuple(raw)
            summary["modes"][key][
                "native_roundtrip"
            ] = "PASS; raw, selected XD, tail and trace equal"
            for path in (dest / "table.csv", dest / "context.csv"):
                with (
                    path.open("rb") as source,
                    gzip.open(path.with_suffix(path.suffix + ".gz"), "wb") as target,
                ):
                    import shutil

                    shutil.copyfileobj(source, target)
                path.unlink()
            save("summary.json", summary)
            print("roundtrip", key, "PASS", flush=True)
    hashes = json.loads((ROOT / "source-hashes.json").read_text())
    assert all(digest(Path(path)) == value for path, value in hashes.items())
    summary["protected_sources_unchanged"] = True
    save("summary.json", summary)


if __name__ == "__main__":
    main()
