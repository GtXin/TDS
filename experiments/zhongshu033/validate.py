"""Reproducible independent memo033 acceptance checks and real stage timings."""

from __future__ import annotations

import argparse
import gzip
import json
import platform
import random
import resource
import statistics
import sys
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter

from chanlab.algo._zhongshu_scan import scan_zhongshus
from chanlab.algo.bi import BiSeries
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.zhongshu import ZhongshuSeries
from chanlab.data.zhongshu_table import jsonable
from experiments.zhongshu022.reference import rational_crossing, reference_route

OUT = Path("artifacts/mas/zhongshu-family/run033")
MODES = (
    "bi-strong_xd-strong",
    "bi-strong_xd-weak",
    "bi-weak_xd-strong",
    "bi-weak_xd-weak",
)


def save(name, data):
    (OUT / name).write_text(
        json.dumps(jsonable(data), ensure_ascii=False, indent=2, allow_nan=False)
    )


def check(series, prefixes=False):
    seg = series._project(series.source_series)
    route = reference_route(seg)
    assert [
        (z.geometry.start, z.geometry.terminal, z.lower, z.upper) for z in series
    ] == route
    cursor = 0
    unformed = []
    crosses = 0
    for z in series:
        g = z.geometry
        if cursor < g.start:
            unformed.append((cursor, g.start))
        stop = len(seg) if g.terminal is None else g.terminal + 1
        assert z.member_indices == tuple(range(g.start, stop))
        assert (
            z.start_raw_index == seg[g.start].start_x
            and z.end_raw_index == seg[stop - 1].end_x
        )
        assert g.formation_at == max(x.confirmed_at for x in seg[g.start : g.start + 3])
        assert g.confirmation == (None if g.terminal is None else g.terminal + 1)
        assert z.confirmed_at == (
            None
            if g.terminal is None
            else max(x.confirmed_at for x in seg[g.start : g.terminal + 2])
        )
        boundaries = [
            (g.left, seg[g.start], z.lower if seg[g.start].direction == 1 else z.upper)
        ]
        if g.terminal is not None:
            end = seg[g.terminal]
            boundaries.append(
                (g.right, end, z.upper if end.direction == 1 else z.lower)
            )
        expected_diag = []
        for side, (actual, item, bound) in zip(("left", "right"), boundaries):
            expected = rational_crossing(item, bound)
            assert (actual is None) == (expected is None)
            if expected is None:
                expected_diag.append(f"{side}_crossing_missing")
            else:
                assert (
                    abs(actual.x - expected[0]) < 1e-8
                    and abs(actual.fraction - expected[1]) < 1e-12
                )
                assert actual.price == bound and actual.segment_id == item.id
                t = item.start_time + expected[1] * (item.end_time - item.start_time)
                assert abs((actual.time - t).total_seconds()) <= 1e-6
                crosses += 1
        assert g.diagnostics == tuple(expected_diag)
        cursor = stop
    if cursor < len(seg):
        unformed.append((cursor, len(seg)))
    assert series.unformed == tuple(unformed)
    if prefixes:
        for n in range(len(seg) + 1):
            r = scan_zhongshus(seg[:n])
            assert [
                (g.start, g.terminal, g.low, g.high) for g in r.centers
            ] == reference_route(seg[:n])
    return crosses


def raw_case(seed):
    rng = random.Random(seed)
    layer = seed % 6
    n = rng.choice((9, 17, 33, 65, 129))
    v = 100.0
    bars = []
    for i in range(n):
        v += (
            rng.choice((-1, 1, 2, 3))
            if layer == 0
            else rng.choice((-25, -1, 1, 25)) if layer == 2 else rng.randint(-9, 9)
        )
        width = (
            0 if layer == 4 else rng.randint(0, 25) if layer == 3 else rng.randint(1, 5)
        )
        lo, hi = v - width, v + width
        bars.append(
            Kline(
                "SYN",
                "1m",
                f"MC033 seed{seed}",
                datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
                rng.uniform(lo, hi),
                hi,
                lo,
                rng.uniform(lo, hi),
                rng.randint(0, 10000),
            )
        )
    return KlineTSeries(tuple(bars)), layer


def mc():
    begin = perf_counter()
    counts = {k: Counter() for k in MODES}
    strata = {}
    crosses = 0
    with gzip.open(OUT / "random-inputs.jsonl.gz", "wt") as stream:
        for seed in range(10000):
            raw, layer = raw_case(seed)
            stream.write(
                json.dumps(
                    jsonable(
                        {"seed": seed, "layer": layer, "raw": [asdict(x) for x in raw]}
                    )
                )
                + "\n"
            )
            try:
                merged = MergedKlineSeries.derive_from(
                    raw, {"initialization": "UP"}, "memo015"
                )
                fx = FenxingSeries.derive_from(merged, {}, "memo019")
                for bm in ("strong", "weak"):
                    bi = BiSeries.derive_from(fx, {"distance_mode": bm}, "memo029")
                    for xm in ("strong", "weak"):
                        xd = XianduanSeries.derive_from(bi, {"xd_mode": xm})
                        s = ZhongshuSeries.derive_from(xd)
                        crosses += check(s)
                        key = f"bi-{bm}_xd-{xm}"
                        tally = {
                            "inputs": 1,
                            "segments": len(xd),
                            "centers": len(s),
                            "empty": int(not s),
                            "closed": sum(z.status == "closed" for z in s),
                            "open": sum(z.status == "open" for z in s),
                            "missing": sum(bool(z.geometry.diagnostics) for z in s),
                            "zero": sum(z.lower == z.upper for z in s),
                        }
                        counts[key].update(tally)
                        strata.setdefault(
                            f"{key}|layer{layer}|raw{len(raw)}", Counter()
                        ).update(tally)
            except Exception as exc:
                save(
                    "failure.json",
                    {
                        "seed": seed,
                        "mode": key if "key" in locals() else None,
                        "error": repr(exc),
                        "raw": [asdict(x) for x in raw],
                    },
                )
                raise
            if seed % 1000 == 0:
                print("MC", seed, flush=True)
    save(
        "monte-carlo.json",
        {
            "inputs": 10000,
            "counts": counts,
            "strata": strata,
            "crossings": crosses,
            "seconds": perf_counter() - begin,
            "failures": 0,
            "peak_rss_bytes_macos": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    )


def load_raw():
    return KlineTSeries.read_csv(
        next(Path("samples/chan_table").glob("*chan_table*.csv")),
        next(Path("samples/chan_table").glob("*context*.csv")),
    )


def real():
    report = {}
    begin = perf_counter()
    for mode in MODES:
        root = Path("artifacts/mas/xianduan-family/run031/full") / mode
        table = ChanTable.read_csv(root / "table.csv", root / "context.csv")
        xd = table.feature_series[mode]
        s = ZhongshuSeries.derive_from(xd)
        crosses = check(s, True)
        dest = OUT / "full" / mode
        dest.mkdir(parents=True, exist_ok=True)
        t = s.to_chan_table(table, "zs:" + mode)
        t.write_csv(dest / "table.csv", dest / "context.csv")
        restored = ChanTable.read_csv(dest / "table.csv", dest / "context.csv")
        rs = restored.feature_series["zs:" + mode]
        assert rs.items == s.items and rs.trace == s.trace and rs.unformed == s.unformed
        expected = json.loads(
            Path("artifacts/mas/memo022-zs/results.json").read_text()
        )[mode]["result"]
        actual = jsonable(
            {
                "centers": [asdict(z.geometry) for z in s],
                "unformed": s.unformed,
                "decisions": [asdict(d) for d in s.trace],
            }
        )
        assert actual == expected
        report[mode] = {
            "segments": len(xd),
            "centers": len(s),
            "closed": sum(z.status == "closed" for z in s),
            "open": sum(z.status == "open" for z in s),
            "drawable": sum(z.geometry.drawable for z in s),
            "missing": sum(bool(z.geometry.diagnostics) for z in s),
            "crossings": crosses,
            "prefixes": len(xd) + 1,
            "roundtrip": "PASS",
            "memo022_complete_parity": "PASS",
        }
        print("FULL", mode, report[mode], flush=True)
    save("full-validation.json", {"modes": report, "seconds": perf_counter() - begin})


def timing():
    raw = load_raw()
    m = MergedKlineSeries.derive_from(raw, {"initialization": "UP"}, "memo015")
    fx = FenxingSeries.derive_from(m, {}, "memo019")
    records = []
    for count in (100, 1000, 3000):
        stop = m[fx[count - 1].source_start + 2].source_stop
        prefix = KlineTSeries(tuple(raw)[:stop], context=raw.context)
        for bm in ("strong", "weak"):
            for xm in ("strong", "weak"):
                runs = []
                expected = None
                for repeat in range(3):
                    t = perf_counter()
                    mm = MergedKlineSeries.derive_from(
                        prefix, {"initialization": "UP"}, "memo015"
                    )
                    t1 = perf_counter()
                    ff = FenxingSeries.derive_from(mm, {}, "memo019")
                    t2 = perf_counter()
                    bi = BiSeries.derive_from(ff, {"distance_mode": bm}, "memo029")
                    t3 = perf_counter()
                    xd = XianduanSeries.derive_from(bi, {"xd_mode": xm})
                    t4 = perf_counter()
                    seg = ZhongshuSeries._project(xd)
                    t5 = perf_counter()
                    scan_zhongshus(seg)
                    t6 = perf_counter()
                    s = ZhongshuSeries.derive_from(xd)
                    t7 = perf_counter()
                    check(s)
                    assert len(ff) == count, (count, len(ff))
                    if expected is None:
                        expected = s.items
                    assert s.items == expected
                    runs.append(
                        {
                            "merged": t1 - t,
                            "fenxing": t2 - t1,
                            "bi": t3 - t2,
                            "xd": t4 - t3,
                            "zs_projection": t5 - t4,
                            "zs_core": t6 - t5,
                            "zs_factory": t7 - t6,
                            "end_to_end": t4 - t + t7 - t6,
                        }
                    )
                    print("TIMING", count, bm, xm, repeat, len(xd), len(s), flush=True)
                records.append(
                    {
                        "fx": count,
                        "raw": len(prefix),
                        "bi": bm,
                        "xd": xm,
                        "segments": len(xd),
                        "centers": len(s),
                        "runs": runs,
                        "medians": {
                            k: statistics.median(r[k] for r in runs) for k in runs[0]
                        },
                    }
                )
                save(
                    "timing.json",
                    {
                        "records": records,
                        "python": sys.version,
                        "platform": platform.platform(),
                        "cache": "warm files; no result cache; all upstream rebuilt per repetition; load/oracle excluded",
                        "memory": "process cumulative high-water, including setup/reference; macOS bytes",
                        "peak_rss_bytes_macos": resource.getrusage(
                            resource.RUSAGE_SELF
                        ).ru_maxrss,
                    },
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=("mc", "real", "timing"))
    args = parser.parse_args()
    globals()[args.task]()
