"""Freeze/review comparison in distinct processes; complete scan data, no exclusions."""

import importlib.util
import json
import random
import subprocess
import sys
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from chanlab.data.zhongshu_table import jsonable
from experiments.zhongshu033.validate import MODES, OUT, save


def worker(which):
    if which == "baseline":
        path = OUT / "baseline/scanner.py"
        spec = importlib.util.spec_from_file_location("frozen033", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    else:
        import chanlab.algo._zhongshu_scan as mod
    cases = json.loads((OUT / "comparison-inputs.json").read_text())
    results = []
    for case in cases:
        segments = []
        for row in case:
            values = dict(row)
            for k in ("start_time", "end_time", "confirmed_at"):
                values[k] = datetime.fromisoformat(values[k])
            segments.append(mod.Segment(**values))
        results.append(jsonable(asdict(mod.scan_zhongshus(segments))))
    save(
        f"comparison-{which}.json",
        {"module": str(Path(mod.__file__).resolve()), "results": results},
    )


def main():
    from chanlab.algo._zhongshu_scan import Segment
    from chanlab.algo.chan_table import ChanTable
    from chanlab.algo.zhongshu import ZhongshuSeries

    cases = []
    epoch = datetime(2026, 1, 1, tzinfo=UTC)
    for seed in range(400):
        rng = random.Random(seed)
        price = 100.0
        rows = []
        for i in range(seed % 40):
            end = price + (1 if i % 2 == 0 else -1) * rng.randint(1, 30)
            rows.append(
                asdict(
                    Segment(
                        i * 2,
                        "case",
                        i * 3,
                        (i + 1) * 3,
                        float(i),
                        float(i + 1),
                        epoch + timedelta(hours=i),
                        epoch + timedelta(hours=i + 1),
                        price,
                        end,
                        min(price, end) - rng.randint(0, 4),
                        max(price, end) + rng.randint(0, 4),
                        1 if i % 2 == 0 else -1,
                        epoch + timedelta(hours=i + 3),
                    )
                )
            )
            price = end
        cases.append(rows)
    for mode in MODES:
        folder = Path("artifacts/mas/xianduan-family/run031/full") / mode
        t = ChanTable.read_csv(folder / "table.csv", folder / "context.csv")
        cases.append(
            [asdict(x) for x in ZhongshuSeries._project(t.feature_series[mode])]
        )
    save("comparison-inputs.json", cases)
    for which in ("baseline", "production"):
        subprocess.run([sys.executable, "-m", __spec__.name, which], check=True)
    a = json.loads((OUT / "comparison-baseline.json").read_text())
    b = json.loads((OUT / "comparison-production.json").read_text())
    assert a["module"] != b["module"] and a["results"] == b["results"]
    save(
        "comparison.json",
        {
            "cases": len(cases),
            "baseline": a["module"],
            "production": b["module"],
            "complete_centers_decisions_unformed": "PASS",
            "exclusions": [],
            "baseline_origin": "existing022 scanner frozen before033 domain edits; Python Pro already read before freeze, not an independent new implementation or causal skill test",
        },
    )
    print("Complete independent-process comparison PASS", len(cases))


if __name__ == "__main__":
    worker(sys.argv[1]) if len(sys.argv) > 1 else main()
