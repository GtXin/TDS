"""Compare raw-coordinate geometry rather than unrelated implementation IDs."""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path("artifacts/mas/xianduan-newdata/run034")
INPUT = Path("artifacts/mas/cc-chantable-20261111-134106-27c20343")


def read(name: str) -> Any:
    """Read a detailed compressed run artifact."""
    with gzip.open(ROOT / name, "rt") as stream:
        return json.load(stream)


def signature(record: dict[str, Any], kind: str) -> tuple[Any, ...]:
    """Use source spans, anchor prices and direction as geometric identity."""
    keys = {
        "mk": ("raw_start", "raw_stop", "low", "high", "direction"),
        "fx": ("raw_start", "raw_stop", "anchor", "kind", "price"),
        "bi": ("start_raw", "end_raw", "start_price", "end_price", "direction"),
        "xd": ("start_raw", "end_raw", "start_price", "end_price", "direction"),
    }[kind]
    return tuple(record[key] for key in keys)


def compare_records(
    ours: list[dict[str, Any]], kwx: list[dict[str, Any]], kind: str
) -> dict[str, Any]:
    """Keep complete unmatched records and distinguish status from geometry."""
    our_map = {signature(record, kind): record for record in ours}
    kwx_map = {signature(record, kind): record for record in kwx}
    assert len(our_map) == len(ours) and len(kwx_map) == len(kwx)
    common = our_map.keys() & kwx_map.keys()
    only_ours = [r for r in ours if signature(r, kind) not in common]
    only_kwx = [r for r in kwx if signature(r, kind) not in common]
    return {
        "ours": len(ours),
        "kwx": len(kwx),
        "exact_geometry_matches": len(common),
        "only_ours": only_ours,
        "only_kwx": only_kwx,
        "status_ours": dict(Counter(r["status"] for r in ours)),
        "status_kwx": dict(Counter(r["status"] for r in kwx)),
        "status_difference_on_matching_geometry": sum(
            our_map[k]["status"] != kwx_map[k]["status"] for k in common
        ),
    }


def foreign() -> dict[str, list[dict[str, Any]]]:
    """Extract KWX geometry using native endpoint timestamps and mapped ranges."""
    with (INPUT / "ChanTable.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    timestamps = {
        int(datetime.fromisoformat(row["timestamp"]).timestamp()): i
        for i, row in enumerate(rows)
    }
    data = json.loads((INPUT / "features.json").read_text())
    result: dict[str, list[dict[str, Any]]] = {}
    for series in data["series"]:
        kind = series["kind"]
        if kind not in ("mk", "fx", "bi", "xd"):
            continue
        result[kind] = []
        for source in series["records"]:
            native = source["details"]["cc_native"]
            row = {
                k: source[k]
                for k in (
                    "id",
                    "raw_start",
                    "raw_stop",
                    "status",
                    "confirmed_at",
                    "source_start",
                    "source_stop",
                )
            }
            if kind == "mk":
                row.update(
                    low=native["low"],
                    high=native["high"],
                    direction=source["values"]["direction"],
                )
            elif kind == "fx":
                row.update(
                    anchor=source["anchor_raw_index"],
                    kind=source["values"]["kind"],
                    price=source["details"]["price"],
                )
            else:
                row.update(
                    {k: native[k] for k in ("start_price", "end_price", "direction")}
                )
                row.update(
                    native_structural_start_raw=timestamps[native["start_ts"]],
                    native_structural_end_raw=timestamps[native["end_ts"]],
                    start_raw=source["raw_start"],
                    end_raw=source["raw_stop"] - 1,
                )
                row["mapping_span_differs_from_geometry"] = (
                    row["raw_start"],
                    row["raw_stop"],
                ) != (row["native_structural_start_raw"], row["native_structural_end_raw"] + 1)
            result[kind].append(row)
    with gzip.open(ROOT / "kwx-normalized.json.gz", "wt") as stream:
        json.dump(result, stream)
    return result


def independent_geometry(
    upstream: dict[str, Any], bi: dict[str, Any], xd: dict[str, Any], bm: str, xm: str
) -> dict[str, int]:
    """Check selected geometry directly from exported source ranges and prices."""
    merged, fx = upstream["mk"], upstream["fx"]
    pens = bi["records"]
    for point in pens:
        a, b = point["start_fenxing_index"], point["end_fenxing_index"]
        left, right = fx[a], fx[b]
        i, j = left["source_start"] + 1, right["source_start"] + 1
        assert j - i >= (3 if bm == "weak" else 4)
        assert left["kind"] != right["kind"]
        top = merged[i] if left["kind"] == "top" else merged[j]
        bottom = merged[j] if left["kind"] == "top" else merged[i]
        assert top["high"] > bottom["high"] and bottom["low"] < top["low"]
        assert max(r["high"] for r in merged[i : j + 1]) <= top["high"]
        assert min(r["low"] for r in merged[i : j + 1]) >= bottom["low"]
        assert (point["start_price"], point["end_price"]) == (
            left["price"],
            right["price"],
        )
    route = [(r["source_start"], r["source_stop"]) for r in xd["records"]] + [
        tuple(p) for p in xd["tail"]
    ]
    for i, (a, b) in enumerate(route):
        assert b - a >= 3 and (b - a) % 2 == 1
        assert not i or route[i - 1][1] == a
        direction = 1 if pens[a]["direction"] == "up" else -1
        assert direction * (pens[b - 1]["end_price"] - pens[a]["start_price"]) > 0
        assert (
            xm == "weak"
            or direction * (pens[b - 1]["end_price"] - pens[a]["end_price"]) > 0
        )
        assert max(
            min(p["start_price"], p["end_price"]) for p in pens[a : a + 3]
        ) <= min(max(p["start_price"], p["end_price"]) for p in pens[a : a + 3])
        if i < len(xd["records"]):
            trace = xd["trace"][i]
            assert tuple(trace["S"]) == (a, b)
            assert tuple(trace["T"]) == route[i + 1]
            if trace["certificate"]["kind"] == "gap":
                assert tuple(trace["U"]) == route[i + 2]
    return {
        "bi_selected_pair_checks": len(pens),
        "xd_shape_checks_including_tail": len(route),
        "actual_successor_bindings": len(xd["records"]),
    }


def main() -> None:
    """Write complete differences and concise summaries for all available modes."""
    kwx = foreign()
    upstream = read("upstream.json.gz")
    comparisons = {
        kind: compare_records(upstream[kind], kwx[kind], kind) for kind in ("mk", "fx")
    }
    for bm in ("weak", "strong"):
        path = ROOT / f"bi-{bm}.json.gz"
        if not path.exists():
            continue
        bi = read(path.name)
        comparisons[f"bi-{bm}"] = compare_records(bi["records"], kwx["bi"], "bi")
        for xm in ("weak", "strong"):
            key = f"bi-{bm}_xd-{xm}"
            if not (ROOT / f"{key}.json.gz").exists():
                continue
            xd = read(f"{key}.json.gz")
            comparisons[key] = compare_records(xd["records"], kwx["xd"], "xd")
            comparisons[key]["independent_geometry"] = independent_geometry(
                upstream, bi, xd, bm, xm
            )
    with gzip.open(ROOT / "differences.json.gz", "wt") as stream:
        json.dump(comparisons, stream, indent=2, default=str)
    summary = {
        key: {k: v for k, v in value.items() if k not in ("only_ours", "only_kwx")}
        | {"only_ours": len(value["only_ours"]), "only_kwx": len(value["only_kwx"])}
        for key, value in comparisons.items()
    }
    (ROOT / "comparison-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
