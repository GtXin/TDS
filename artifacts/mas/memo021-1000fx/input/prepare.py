"""Prepare fixed first-1000FX inputs; no xianduan algorithm is executed."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

from chanlab.algo.bi import BiSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[3]
COUNT = 1000


def write_json(name: str, value: Any) -> None:
    """Save evidence in this assigned artifact folder only."""
    (OUTPUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    )


def digest(path: Path) -> str:
    """Return the SHA256 of a preserved input file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_pairs(series: BiSeries, gap: int) -> dict[str, Any]:
    """Check source intervals directly, without the production pair helper."""
    fx = series.source_series
    merged = fx.source_series
    checks = 0
    for position, pen in enumerate(series):
        a, b = pen.start_fenxing_index, pen.end_fenxing_index
        left, right = fx[a], fx[b]
        start, end = left.source_start + 1, right.source_start + 1
        assert a < b and left.kind != right.kind and end - start >= gap
        top, bottom = (
            (merged[start], merged[end])
            if left.kind == "top"
            else (merged[end], merged[start])
        )
        assert top.high > bottom.high and bottom.low < top.low
        assert max(bar.high for bar in merged[start : end + 1]) <= top.high
        assert min(bar.low for bar in merged[start : end + 1]) >= bottom.low
        assert pen.start_price == left.price and pen.end_price == right.price
        assert pen.direction == ("up" if right.price > left.price else "down")
        assert pen.status == "unconfirmed" and pen.confirmed_at is None
        if position:
            previous = series[position - 1]
            assert previous.end_fenxing_index == a
            assert previous.direction != pen.direction
        checks += 1
    return {"selected_pairs_checked": checks, "all_pass": True}


def point_record(fx: FenxingSeries, index: int) -> dict[str, Any]:
    """Map a fractal position to exact merged and raw source coordinates."""
    item = fx[index]
    merged = fx.source_series
    raw = merged.source_series
    center = item.source_start + 1
    center_bar = merged[center]
    return {
        "fx_position": index,
        "fx_id": item.id,
        "kind": item.kind,
        "price": item.price,
        "merged_center": center,
        "merged_window": [item.source_start, item.source_stop],
        "merged_center_raw_range": [center_bar.source_start, center_bar.source_stop],
        "window_raw_range": [
            merged[item.source_start].source_start,
            merged[item.source_stop - 1].source_stop,
        ],
        "anchor_raw_index": item.anchor_raw_index,
        "anchor_utc": raw[item.anchor_raw_index].timestamp.isoformat(),
    }


def main() -> None:
    """Rebuild a complete 1000FX prefix, derive both Bi routes and scan them."""
    sample = ROOT / "samples/chan_table"
    csv_path = next(sample.glob("*chan_table*.csv"))
    context_path = next(sample.glob("*context*.csv"))
    protected = [
        csv_path,
        context_path,
        ROOT / "src/chanlab/algo/bi.py",
        ROOT / "src/chanlab/algo/fenxing.py",
        ROOT / "src/chanlab/algo/merged_kline.py",
        ROOT / "src/chanlab/algo/kline.py",
    ]
    before = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    started = perf_counter()
    full_raw = KlineTSeries.read_csv(csv_path, context_path)
    full_merged = MergedKlineSeries.derive_from(
        full_raw, {"initialization": "UP"}, "memo015:002"
    )
    full_fx = FenxingSeries.derive_from(full_merged, {}, "memo019:002")
    full_seconds = perf_counter() - started
    assert len(full_fx) >= COUNT
    last = full_fx[COUNT - 1]
    raw_stop = full_merged[last.source_stop - 1].source_stop
    raw = KlineTSeries(tuple(full_raw)[:raw_stop], context=full_raw.context)
    start = perf_counter()
    merged = MergedKlineSeries.derive_from(
        raw, {"initialization": "UP"}, "memo015:002"
    )
    merged_seconds = perf_counter() - start
    start = perf_counter()
    fx = FenxingSeries.derive_from(merged, {}, "memo019:002")
    fx_seconds = perf_counter() - start
    assert len(fx) == COUNT
    assert tuple(fx) == tuple(full_fx)[:COUNT]
    assert tuple(merged) == tuple(full_merged)[: len(merged)]
    assert len(merged) == last.source_stop
    assert last.source_stop - last.source_start == 3
    assert raw_stop == merged[-1].source_stop
    points = [point_record(fx, i) for i in range(COUNT)]
    write_json("fractals.json", points)
    write_json(
        "bars.json",
        {
            "raw": [
                {
                    "index": i,
                    "utc": bar.timestamp.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                }
                for i, bar in enumerate(raw)
            ],
            "merged": [
                {
                    "index": i,
                    "low": bar.low,
                    "high": bar.high,
                    "direction": bar.direction,
                    "source_start": bar.source_start,
                    "source_stop": bar.source_stop,
                }
                for i, bar in enumerate(merged)
            ],
        },
    )
    modes: dict[str, Any] = {}
    for mode, gap in (("strong", 4), ("weak", 3)):
        start = perf_counter()
        series = BiSeries.derive_from(
            fx, {"distance_mode": mode}, "memo029:001,002a-f"
        )
        solve_seconds = perf_counter() - start
        start = perf_counter()
        validation = independent_pairs(series, gap)
        validation_seconds = perf_counter() - start
        route = (
            []
            if not len(series)
            else [series[0].start_fenxing_index]
            + [pen.end_fenxing_index for pen in series]
        )
        pens = []
        for i, pen in enumerate(series):
            a, b = points[pen.start_fenxing_index], points[pen.end_fenxing_index]
            pens.append(
                {
                    "pen_position": i,
                    "pen_id": pen.id,
                    "direction": pen.direction,
                    "low": min(pen.start_price, pen.end_price),
                    "high": max(pen.start_price, pen.end_price),
                    "start": a,
                    "end": b,
                    "merged_member_range": [
                        a["merged_center"],
                        b["merged_center"] + 1,
                    ],
                    "status": pen.status,
                    "confirmed_at": None,
                }
            )
        payload = {
            "mode": mode,
            "min_gap": gap,
            "route_fx_positions": route,
            "pens": pens,
            "unresolved_merged": series.unresolved_ranges(),
            "source_fx_count": len(fx),
            "snapshot_only": True,
            "permanent_confirmation": False,
            "solve_seconds": solve_seconds,
            "independent_validation_seconds": validation_seconds,
            "independent_selected_pair_checks": validation,
        }
        write_json(f"bi-{mode}.json", payload)
        modes[mode] = {
            "pens": len(series),
            "route_first_last_fx": [] if not route else [route[0], route[-1]],
            "route_endpoints": len(route),
            "unresolved_merged": series.unresolved_ranges(),
            "solve_seconds": solve_seconds,
            "independent_validation_seconds": validation_seconds,
            **validation,
        }
    after = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    assert before == after
    summary = {
        "scope": "Input preparation only; no xianduan or CC algorithm executed.",
        "full_source": {
            "raw": len(full_raw),
            "merged": len(full_merged),
            "fractals": len(full_fx),
            "derive_seconds": full_seconds,
        },
        "prefix": {
            "raw": len(raw),
            "merged": len(merged),
            "fractals": len(fx),
            "fx_positions": [0, COUNT - 1],
            "raw_half_open": [0, raw_stop],
            "last_fractal": points[-1],
            "prefix_equal_to_full_snapshot": True,
            "policy": "Use the exact full-snapshot first1000 completeFX. Cut raw input after the complete right member of FX999's three-merged window, then rebuild and assert exact prefix identity; no raw bars after this cut are consumed by either Bi solve.",
            "raw_csv_rows_after_cut_not_consumed": len(full_raw) - raw_stop,
            "raw_utc": [raw[0].timestamp.isoformat(), raw[-1].timestamp.isoformat()],
        },
        "configuration": {
            "merged_initialization": "UP",
            "fractal_anchor_tie": "FIRST",
            "bi_modes": ["strong", "weak"],
            "permanent_confirmation": False,
            "fixed_snapshot": True,
        },
        "upstream_seconds": {"merged": merged_seconds, "fenxing": fx_seconds},
        "modes": modes,
        "source_hashes": before,
        "protected_hashes_unchanged": before == after,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
    }
    write_json("summary.json", summary)
    print(
        json.dumps(
            {
                "prefix": [len(raw), len(merged), len(fx)],
                "modes": modes,
                "protected_hashes_unchanged": before == after,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
