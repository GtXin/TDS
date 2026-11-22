"""Recompute memo022 centers on validated four-mode real031 source snapshots."""

from __future__ import annotations

import hashlib
import json
import platform
import statistics
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from chanlab.algo._zhongshu_input import project_xianduans
from chanlab.algo._zhongshu_scan import Segment, scan_zhongshus
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.xianduan import XianduanSeries
from experiments.zhongshu022.reference import rational_crossing, reference_route

OUT = Path("artifacts/mas/memo022-zs")
INPUT = Path("artifacts/mas/xianduan-family/run031/full")
MODES = (
    "bi-strong_xd-strong",
    "bi-strong_xd-weak",
    "bi-weak_xd-strong",
    "bi-weak_xd-weak",
)


def json_default(value: object) -> str:
    """Serialize UTC evidence timestamps without changing their meaning."""
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"unsupported JSON value {type(value)}")


def save(path: Path, value: object) -> None:
    """Write a small inspectable artifact with real newlines and finite JSON."""
    path.write_text(
        json.dumps(
            value, ensure_ascii=False, indent=2, default=json_default, allow_nan=False
        )
    )


def digest(path: Path) -> str:
    """Fingerprint exact local source bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(segments: tuple[Segment, ...]) -> dict[str, int]:
    """Check every source-prefix route and every full-run chord independently."""
    for count in range(len(segments) + 1):
        result = scan_zhongshus(segments[:count])
        got = [(z.start, z.terminal, z.low, z.high) for z in result.centers]
        assert got == reference_route(segments[:count]), count
    result = scan_zhongshus(segments)
    crosses = 0
    for z in result.centers:
        left_price = z.low if segments[z.start].direction == 1 else z.high
        checks = [(z.left, segments[z.start], left_price)]
        if z.terminal is not None:
            last = segments[z.terminal]
            checks.append((z.right, last, z.high if last.direction == 1 else z.low))
            assert z.confirmation == z.terminal + 1
            assert z.confirmed_at == max(
                s.confirmed_at for s in segments[z.start : z.terminal + 2]
            )
        for actual, segment, price in checks:
            expected = rational_crossing(segment, price)
            assert (actual is None) == (expected is None)
            if actual is not None and expected is not None:
                assert abs(actual.x - expected[0]) < 1e-8
                assert abs(actual.fraction - expected[1]) < 1e-12
                expected_time = segment.start_time + expected[1] * (
                    segment.end_time - segment.start_time
                )
                assert abs((actual.time - expected_time).total_seconds()) <= 1e-6
                assert (
                    abs(
                        segment.start_price
                        + actual.fraction * (segment.end_price - segment.start_price)
                        - price
                    )
                    < 1e-8
                )
                crosses += 1
    return {"fixed_segment_prefixes": len(segments) + 1, "crossings": crosses}


def run() -> None:
    """Load, source-audit, freshly scan, independently compare and time all modes."""
    OUT.mkdir(parents=True, exist_ok=True)
    raw_path = next(Path("samples/chan_table").glob("*chan_table*.csv"))
    raw_context = next(Path("samples/chan_table").glob("*context*.csv"))
    raw = KlineTSeries.read_csv(raw_path, raw_context)
    saved: dict[str, Any] = {}
    summary: dict[str, Any] = {
        "profile": "ZS022-sequential-rectangle",
        "python": platform.python_version(),
        "policies": {
            "zero_height": True,
            "geometry": "endpoint_chord",
            "missing_crossing": "report_keep_structure",
            "seed_selection": "earliest",
            "core": "source_stroke_extrema",
            "tail": "open",
        },
        "source": {
            "raw": len(raw),
            "utc_start": raw[0].timestamp,
            "utc_end": raw[-1].timestamp,
            "files": {
                str(raw_path): digest(raw_path),
                str(raw_context): digest(raw_context),
            },
        },
        "modes": {},
    }
    for mode in MODES:
        folder = INPUT / mode
        table = ChanTable.read_csv(folder / "table.csv", folder / "context.csv")
        assert tuple(table.source_series) == tuple(raw)
        series = table.feature_series[mode]
        assert isinstance(series, XianduanSeries)
        projected = project_xianduans(series, digest(folder / "context.csv"))
        pens, fx = series.source_series, series.source_series.source_series
        merged = fx.source_series
        for source, segment in zip(series, projected):
            p0, p1 = pens[source.source_start], pens[source.source_stop - 1]
            f0, f1 = fx[p0.start_fenxing_index], fx[p1.end_fenxing_index]
            bars = merged[f0.source_start + 1 : f1.source_start + 2]
            assert (segment.low, segment.high) == (
                min(x.low for x in bars),
                max(x.high for x in bars),
            )
        result = scan_zhongshus(projected)
        independent = audit(projected)
        timings = []
        for _ in range(3):
            begin = perf_counter()
            for _ in range(100):
                repeat = scan_zhongshus(projected)
            timings.append((perf_counter() - begin) * 1000 / 100)
            assert repeat == result
        closed = [z for z in result.centers if z.closed]
        missing = [z for z in result.centers if z.diagnostics]
        pen_lines = []
        for pen in pens:
            f0, f1 = fx[pen.start_fenxing_index], fx[pen.end_fenxing_index]
            pen_lines.append(
                [
                    f0.anchor_raw_index,
                    pen.start_price,
                    f1.anchor_raw_index,
                    pen.end_price,
                ]
            )
        saved[mode] = {
            "segments": [asdict(x) for x in projected],
            "result": asdict(result),
            "pens": pen_lines,
            "upstream_tail": series.tail,
        }
        summary["modes"][mode] = {
            "segments": len(series),
            "pens": len(pens),
            "fractals": len(fx),
            "closed": len(closed),
            "open": sum(not z.closed for z in result.centers),
            "drawable_closed": sum(z.drawable for z in closed),
            "zero_height": sum(z.low == z.high for z in result.centers),
            "geometry_diagnostics": [
                {"start": z.start, "terminal": z.terminal, "reasons": z.diagnostics}
                for z in missing
            ],
            "internal_extrema_segments": sum(
                x.low < min(x.start_price, x.end_price)
                or x.high > max(x.start_price, x.end_price)
                for x in projected
            ),
            "source_extrema_checks": len(projected),
            "independent": independent,
            "scan_ms_repeats": timings,
            "scan_ms_median": statistics.median(timings),
            "seed_checks": sum(d.stage == "seed" for d in result.decisions),
            "ending_checks": sum(d.stage == "ending" for d in result.decisions),
            "unformed_ranges": result.unformed,
            "context_sha256": digest(folder / "context.csv"),
            "table_sha256": digest(folder / "table.csv"),
        }
        print(
            mode, json.dumps(summary["modes"][mode], default=json_default), flush=True
        )
        if mode == MODES[0]:
            chart_source = {
                "raw": [
                    {
                        "x": i,
                        "utc": bar.timestamp,
                        "open": bar.open,
                        "high": bar.high,
                        "low": bar.low,
                        "close": bar.close,
                    }
                    for i, bar in enumerate(raw)
                ],
                "fx": [
                    {
                        "id": f.id,
                        "x": f.anchor_raw_index,
                        "price": f.price,
                        "kind": f.kind,
                    }
                    for f in fx
                ],
            }
            save(OUT / "chart-source.json", chart_source)
    save(OUT / "results.json", saved)
    save(OUT / "validation.json", summary)
    protected = json.loads((OUT / "baseline-hashes.json").read_text())
    for name, expected in protected.items():
        assert digest(Path(name)) == expected, name
    print("Protected-source hashes PASS", len(protected), flush=True)


if __name__ == "__main__":
    run()
