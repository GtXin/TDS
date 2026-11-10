"""Differential old/new inclusion and previous persisted-context compatibility."""

from pathlib import Path
import ast
import importlib.util
import itertools
import json
import random
import sys
from hashlib import sha256
from dataclasses import asdict

from chanlab.algo import merged_kline as new
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.kline import Kline, KlineTSeries
from datetime import UTC, datetime, timedelta

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "old_merged", out / "before/merged_kline.py"
)
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)


def raw(data):
    return KlineTSeries(
        Kline(
            "X",
            "1m",
            "manual",
            datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=i),
            lo,
            hi,
            lo,
            hi,
            1,
        )
        for i, (lo, hi) in enumerate(data)
    )


def work_data(work):
    if work is None:
        return None
    if isinstance(work, old.Work):
        return (
            id(work.raw),
            work.low,
            work.high,
            work.direction,
            work.source_start,
            work.source_stop,
        )
    return (id(work["raw"]),) + (
        tuple(
            work[k] for k in ("low", "high", "direction", "source_start", "source_stop")
        )
    )


def trace_data(trace):
    result = []
    for step in trace:
        if isinstance(step, old.MergeDecision):
            result.append(
                (
                    step.rule,
                    step.raw_index,
                    work_data(step.before),
                    work_data(step.candidate),
                    work_data(step.after),
                )
            )
        else:
            result.append(
                (
                    step["rule"],
                    step["raw_index"],
                    work_data(step["before"]),
                    work_data(step["candidate"]),
                    work_data(step["after"]),
                )
            )
    return result


def normalize(outcome):
    if isinstance(outcome, (new.MergedKlineSeries, old.MergedKlineSeries)):
        return dict(
            kind="complete",
            records=[asdict(b) for b in outcome],
            explanations=[outcome.explain(i) for i in range(len(outcome))],
            mapping=outcome.trace_by_point,
            trace=trace_data(outcome.trace),
        )
    if isinstance(outcome, old.DualMerge):
        return dict(
            kind="dual",
            main=normalize(outcome.main),
            comparison=normalize(outcome.comparison),
            warning=outcome.warning_evaluation,
        )
    if isinstance(outcome, old.PendingMerge):
        return dict(
            kind="pending",
            i=outcome.raw_index,
            current=(
                outcome.current.low,
                outcome.current.high,
                outcome.current.source_start,
                outcome.current.source_stop,
            ),
            saved=[asdict(b) for b in outcome.saved],
            candidate=work_data(outcome.candidate),
            trace=trace_data(outcome.trace),
        )
    if outcome["kind"] == "dual":
        return dict(
            kind="dual",
            main=normalize(outcome["main"]),
            comparison=normalize(outcome["comparison"]),
            warning=outcome["warning_evaluation"],
        )
    return dict(
        kind="pending",
        i=outcome["raw_index"],
        current=tuple(
            outcome["current"][k]
            for k in ("low", "high", "source_start", "source_stop")
        ),
        saved=[asdict(b) for b in outcome["saved"]],
        candidate=work_data(outcome["candidate"]),
        trace=trace_data(outcome["trace"]),
    )


intervals = [(a, b) for a in range(3) for b in range(a, 3)]
data = list(itertools.product(intervals, repeat=3))
rng = random.Random(26009)
for _ in range(300):
    data.append(
        [
            (a := rng.randint(-10, 10), a + rng.randint(0, 12))
            for _ in range(rng.randint(1, 40))
        ]
    )
checked = 0
for sequence in data:
    source = raw(sequence)
    for policy in ("UP", "DOWN", "OUTER", "BOTH", "UNSET"):
        a = old.MergedKlineSeries.derive_from(
            source, old.MergeConfig(policy), "differential:015"
        )
        b = new.MergedKlineSeries.derive_from(
            source, {"initialization": policy}, "differential:015"
        )
        assert normalize(a) == normalize(b), (sequence, policy)
        checked += 1

folder = root / "artifacts/mas/merged-kline-family/integration"
paths = [folder / "chan_table.csv", folder / "context.csv"]
hashes = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in paths}
table = ChanTable.read_csv(*paths)
series = new.MergedKlineSeries.from_chan_table(table, "merged")
assert len(table) == 10060 and len(series) == 6200
assert series.source_series is table.source_series
assert series.config["initialization"] == "UP"
# Save a fresh pair separately, preserving prior schema fixtures.
series.to_chan_table(table, "merged").write_csv(
    out / "roundtrip.csv", out / "roundtrip-context.csv"
)
again = ChanTable.read_csv(out / "roundtrip.csv", out / "roundtrip-context.csv")
restored = new.MergedKlineSeries.from_chan_table(again, "merged")
assert restored.klines == series.klines
assert (out / "roundtrip-context.csv").read_bytes() == paths[1].read_bytes()
assert (out / "roundtrip.csv").read_bytes() == paths[0].read_bytes()
assert [restored.explain(i) for i in range(len(series))] == [
    series.explain(i) for i in range(len(series))
]
frame = series.to_dataframe()
assert len(frame) == 6200
figure = series.plot(start=-40)
assert len(figure.data[0].x) > 0
# Independently compare complete full-data outputs against the old implementation.
for policy in ("UP", "DOWN", "OUTER", "BOTH", "UNSET"):
    previous = old.MergedKlineSeries.derive_from(
        table.source_series, old.MergeConfig(policy), series.rule_tree_ref
    )
    current = new.MergedKlineSeries.derive_from(
        table, {"initialization": policy}, series.rule_tree_ref
    )
    assert normalize(previous) == normalize(current)
assert hashes == {
    str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in paths
}
classes = [
    n.name
    for n in ast.walk(
        ast.parse((root / "src/chanlab/algo/merged_kline.py").read_text())
    )
    if isinstance(n, ast.ClassDef)
]
assert classes == ["MergedKline", "MergedKlineSeries"]
report = dict(
    classes=classes,
    differential_cases=checked,
    seed=26009,
    previous_csv_context_compatible=True,
    previous_persisted_bytes_reproduced=True,
    complete_trace_evidence_equal=True,
    previous_fixture_hashes=hashes,
    raw_count=len(table),
    merged_count=len(series),
    explanations_preserved=6200,
    full_data_policies_equal=5,
    dataframe_rows=len(frame),
    plot_checked=True,
)
(out / "verification.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
