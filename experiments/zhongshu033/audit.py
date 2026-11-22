"""Final source/022 replay, all native-chart arrays, files and raw coverage audit."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from chanlab.algo.chan_table import ChanTable
from chanlab.algo.zhongshu import ZhongshuSeries
from chanlab.data.zhongshu_table import jsonable
from experiments.zhongshu033.validate import MODES, OUT, check, save


def main():
    charts = OUT / "charts"
    manifest = json.loads((charts / "manifest.json").read_text())
    report = {}
    pens_checked = merged_checked = 0
    old = json.loads(Path("artifacts/mas/memo022-zs/results.json").read_text())
    for mode in MODES:
        root = OUT / "full" / mode
        t = ChanTable.read_csv(root / "table.csv", root / "context.csv")
        stored = t.feature_series["zs:" + mode]
        fresh = ZhongshuSeries.derive_from(stored.source_series)
        assert (
            fresh.items == stored.items
            and fresh.trace == stored.trace
            and fresh.unformed == stored.unformed
        )
        got = jsonable(
            {
                "centers": [asdict(z.geometry) for z in fresh],
                "unformed": fresh.unformed,
                "decisions": [asdict(d) for d in fresh.trace],
            }
        )
        assert got == old[mode]["result"]
        original_segments = old[mode]["segments"]
        actual_segments = [
            jsonable(asdict(x)) for x in fresh._project(fresh.source_series)
        ]
        assert len(original_segments) == len(actual_segments)
        for previous, current in zip(original_segments, actual_segments):
            assert {k: v for k, v in previous.items() if k != "snapshot_id"} == {
                k: v for k, v in current.items() if k != "snapshot_id"
            }
        source_validation = json.loads(
            Path("artifacts/mas/memo022-zs/validation.json").read_text()
        )["modes"][mode]
        original = Path("artifacts/mas/xianduan-family/run031/full") / mode
        for file, field in (
            ("table.csv", "table_sha256"),
            ("context.csv", "context_sha256"),
        ):
            assert (
                hashlib.sha256((original / file).read_bytes()).hexdigest()
                == source_validation[field]
            )
        check(fresh, True)
        bi = fresh.source_series.source_series
        fx = bi.source_series
        merged = fx.source_series
        covered = set()
        rows = [r for r in manifest if r["mode"] == mode]
        for row in rows:
            a, b = row["start"], row["stop"]
            data = json.loads((charts / row["figure"]).read_text())
            traces = data["data"]
            for key in ("png", "html", "figure"):
                assert (charts / row[key]).exists(), row[key]
            assert (charts / row["png"]).stat().st_size > 1000
            if row["window"] != "overview":
                covered.update(range(a, b))
            for pen in bi:
                p = fx[pen.start_fenxing_index].anchor_raw_index
                q = fx[pen.end_fenxing_index].anchor_raw_index
                if q < a or p >= b:
                    continue
                trace = next(x for x in traces if x["name"] == f"Bi{pen.id}")
                assert trace["x"] == [p - a, q - a] and trace["y"] == [
                    pen.start_price,
                    pen.end_price,
                ]
                pens_checked += 1
            for direction, label in (("up", "up"), ("down", "down"), (None, "None")):
                xs = []
                ys = []
                for mk in merged:
                    if (
                        mk.direction != direction
                        or mk.source_stop <= a
                        or mk.source_start >= b
                    ):
                        continue
                    left = max(a, mk.source_start) - a - 0.42
                    right = min(b, mk.source_stop) - 1 - a + 0.42
                    xs.extend([left, right, right, left, left, None])
                    ys.extend([mk.low, mk.low, mk.high, mk.high, mk.low, None])
                    merged_checked += 1
                if xs:
                    trace = next(
                        x for x in traces if x["name"] == f"Merged {label} · low–high"
                    )
                    assert trace["x"] == xs and trace["y"] == ys
        assert covered == set(range(len(t)))
        report[mode] = {
            "022_complete_parity": "PASS",
            "source_segment_fields_except_snapshot_label": len(actual_segments),
            "original_031_table_context_hashes": "PASS",
            "fresh_final_source_replay": "PASS",
            "centers": len(fresh),
            "closed": sum(z.status == "closed" for z in fresh),
            "open": sum(z.status == "open" for z in fresh),
            "raw_coverage": len(covered),
            "pages": len(rows),
        }
    for window in {r["window"] for r in manifest}:
        assert (charts / f"comparison-{window}.png").exists()
    protected = json.loads((OUT / "protected-hashes.json").read_text())
    for name, expected in protected.items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
    sources = list(Path("experiments/zhongshu033").glob("*.py")) + [
        Path(p)
        for p in (
            "src/chanlab/algo/zhongshu.py",
            "src/chanlab/algo/_zhongshu_scan.py",
            "src/chanlab/algo/_zhongshu_input.py",
            "src/chanlab/data/zhongshu_table.py",
            "src/chanlab/data/feature_table.py",
            "src/chanlab/algo/chan_table.py",
            "src/chanlab/visualization/zhongshu_plot.py",
            "tests/test_zhongshu.py",
        )
    ]
    save(
        "implementation-hashes.json",
        {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    )
    save(
        "final-audit.json",
        {
            "modes": report,
            "all_Bi_lines_checked": pens_checked,
            "merged_groups_checked": merged_checked,
            "protected_files_unchanged": len(protected),
            "individual_figures": len(manifest),
            "comparison_figures": len({r["window"] for r in manifest}),
            "missing_files": 0,
            "snapshot_label_comparison": "022 external context SHA label versus 033 local projection label excluded; every source value/evidence/ID compared; original031 context SHA and persistent full source fingerprints independently checked",
            "result": "PASS",
        },
    )
    print(
        "Final replay,022 parity and all source-chart arrays PASS", report, flush=True
    )


if __name__ == "__main__":
    main()
