"""Reproduce frozen-variant comparisons and full-data outputs from repo root."""

from pathlib import Path
from hashlib import sha256
import dataclasses
import json
import os
import subprocess
import sys

from chanlab.algo.merged_kline import (
    MergeConfig,
    MergedKlineSeries,
    DualMerge,
    PendingMerge,
)
from chanlab.data.kline_csv import read_kline_csv

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/mas/merged-kline-family"
CHARTS = ROOT / "artifacts/merged-kline"
CHARTS.mkdir(exist_ok=True)


def main():
    sources = list((ROOT / "samples/chan_table").glob("*.csv"))
    protected = {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources
    }
    data = next(
        p for p in sources if "chan_table" in p.name and "context" not in p.name
    )
    context = next(p for p in sources if "context" in p.name)
    raw, metadata = read_kline_csv(data, context)
    report = {
        "raw_count": len(raw),
        "context_count": len(metadata),
        "protected_hashes": protected,
        "policies": {},
        "variants": {},
    }
    for policy in ("UP", "DOWN", "OUTER", "BOTH", "UNSET"):
        result = MergedKlineSeries.derive_from(
            raw,
            MergeConfig(policy),
            "memo015:sha256:"
            + sha256(
                (ROOT / "docs/memo/memoWX_015_Chan_mergedkline.md").read_bytes()
            ).hexdigest(),
        )
        if isinstance(result, DualMerge):
            report["policies"][policy] = {
                "main_count": len(result.main),
                "comparison_count": len(result.comparison),
                "warning": result.warning_evaluation,
            }
        elif isinstance(result, PendingMerge):
            report["policies"][policy] = {"pending_raw_index": result.raw_index}
        else:
            result.validate()
            assert result.source_series is raw
            report["policies"][policy] = {
                "merged_count": len(result),
                "trace_count": len(result.trace),
            }
            (OUT / f"full-{policy.lower()}.json").write_text(
                json.dumps([dataclasses.asdict(x) for x in result], indent=2)
            )
            if policy == "UP":
                figure = result.plot(
                    start=-40,
                    title="Merged Kline · last 40 merged intervals · UP initialization",
                )
                figure.write_html(
                    CHARTS / "cc-last40-merged.html", include_plotlyjs=True
                )
                # Export is optional tooling, separately reported.
                try:
                    figure.write_image(
                        CHARTS / "cc-last40-merged.png", width=1400, height=800
                    )
                    report["png"] = "exported"
                except Exception as exc:
                    report["png_error"] = f"{type(exc).__name__}: {exc}"
    from datetime import UTC, datetime, timedelta
    from chanlab.algo.kline import Kline, KlineTSeries

    intervals = [
        (1, 3),
        (2, 4),
        (1, 5),
        (3, 5),
        (3, 6),
        (1, 5),
        (2, 4),
        (0, 6),
        (0, 4),
        (0, 5),
    ]
    worked = KlineTSeries(
        Kline(
            "Worked",
            "1m",
            "memo015",
            datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
            lo,
            hi,
            lo,
            hi,
            1,
        )
        for i, (lo, hi) in enumerate(intervals)
    )
    result = MergedKlineSeries.derive_from(worked, MergeConfig("UP"), "memo015:002.b")
    assert isinstance(result, MergedKlineSeries)
    fig = result.plot(
        volume=False, title="Memo015 worked example · 10 raw bars → 3 merged intervals"
    )
    fig.write_html(CHARTS / "worked-example.html", include_plotlyjs=True)
    try:
        fig.write_image(CHARTS / "worked-example.png", width=1200, height=600)
    except Exception as exc:
        report["worked_png_error"] = str(exc)
    for variant in ("baseline", "python_pro"):
        path = OUT / variant / "merged_kline.py"
        code = """import importlib.util,sys,pytest
path=sys.argv[1]
spec=importlib.util.spec_from_file_location('chanlab.algo.merged_kline',path)
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
print('VARIANT_SOURCE='+module.__file__)
from pathlib import Path
import hashlib,json
from chanlab.data.kline_csv import read_kline_csv
folder=Path('samples/chan_table')
raw,_=read_kline_csv(next(folder.glob('*chan_table*.csv')),next(folder.glob('*context*.csv')))
for policy in ('UP','DOWN','OUTER','BOTH','UNSET'):
    result=module.MergedKlineSeries.derive_from(raw,module.MergeConfig(policy),'common-full-data')
    payload=[(x.low,x.high,x.direction,x.source_start,x.source_stop) for x in result]
    print('FULL_DATA',policy,len(result),hashlib.sha256(json.dumps(payload).encode()).hexdigest())
raise SystemExit(pytest.main(['tests/test_merged_kline.py','-q','-k','not plot']))
"""
        run = subprocess.run(
            [sys.executable, "-c", code, str(path)],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
        )
        (OUT / "checks" / f"{variant}-pytest.txt").write_text(run.stdout + run.stderr)
        report["variants"][variant] = {
            "returncode": run.returncode,
            "source": str(path.relative_to(ROOT)),
            "sha256": sha256(path.read_bytes()).hexdigest(),
        }
    assert protected == {
        str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources
    }
    report["protected_inputs_unchanged"] = True
    (OUT / "verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
