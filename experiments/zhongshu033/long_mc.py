"""Long raw multiscale oscillations supplement sparse short-sequence MC."""

import gzip
import itertools
import json
import random
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from time import perf_counter

from chanlab.algo.bi import BiSeries
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.zhongshu import ZhongshuSeries
from chanlab.data.zhongshu_table import jsonable
from experiments.zhongshu033.validate import MODES, OUT, check, save


def main():
    begin = perf_counter()
    counts = {m: Counter() for m in MODES}
    with gzip.open(OUT / "long-random-inputs.jsonl.gz", "wt") as stream:
        for seed in range(64):
            rng = random.Random(33000 + seed)
            levels = [100.0]
            for k in range(120):
                levels.append(
                    levels[-1] + (1 if k % 2 == 0 else -1) * rng.randint(5, 30)
                )
            values = [levels[0]]
            for a, b in itertools.pairwise(levels):
                values.extend(a + (b - a) * k / 8 for k in range(1, 9))
            raw = KlineTSeries(
                tuple(
                    Kline(
                        "LONG",
                        "1m",
                        f"long MC033 seed{seed}",
                        datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
                        v,
                        v + 1,
                        v,
                        v + 1,
                        rng.randint(0, 1000),
                    )
                    for i, v in enumerate(values)
                )
            )
            stream.write(
                json.dumps(jsonable({"seed": seed, "raw": [asdict(x) for x in raw]}))
                + "\n"
            )
            merged = MergedKlineSeries.derive_from(
                raw, {"initialization": "UP"}, "memo015"
            )
            fx = FenxingSeries.derive_from(merged, {}, "memo019")
            for bm in ("strong", "weak"):
                bi = BiSeries.derive_from(fx, {"distance_mode": bm}, "memo029")
                for xm in ("strong", "weak"):
                    xd = XianduanSeries.derive_from(bi, {"xd_mode": xm})
                    s = ZhongshuSeries.derive_from(xd)
                    crosses = check(s, True)
                    counts[f"bi-{bm}_xd-{xm}"].update(
                        inputs=1,
                        segments=len(xd),
                        centers=len(s),
                        closed=sum(z.status == "closed" for z in s),
                        open=sum(z.status == "open" for z in s),
                        missing=sum(bool(z.geometry.diagnostics) for z in s),
                        crossings=crosses,
                    )
            if seed % 8 == 0:
                print("LONG", seed, flush=True)
    assert all(c["closed"] > 0 for c in counts.values())
    save(
        "long-monte-carlo.json",
        {
            "inputs": 64,
            "raw_per_input": 961,
            "counts": counts,
            "failures": 0,
            "seconds": perf_counter() - begin,
        },
    )


if __name__ == "__main__":
    main()
