"""Run full-data table/feature persistence checks from repository root."""

from pathlib import Path
import json
from hashlib import sha256
from chanlab.algo.chan_table import ChanTable
from chanlab.algo.merged_kline import MergedKlineSeries

folder = Path("samples/chan_table")
paths = [next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv"))]
hashes = {str(p): sha256(p.read_bytes()).hexdigest() for p in paths}
table = ChanTable.read_csv(*paths)
series = MergedKlineSeries.derive_from(
    table,
    {"initialization": "UP"},
    "memo015:sha256:"
    + sha256(Path("docs/memo/memoWX_015_Chan_mergedkline.md").read_bytes()).hexdigest(),
)
assert isinstance(series, MergedKlineSeries)
result = series.to_chan_table(table, "merged")
assert result.feature_series["merged"] is series
assert result.source_series is series.source_series is table.source_series
out = Path("artifacts/mas/merged-kline-family/integration")
result.write_csv(out / "chan_table.csv", out / "context.csv")
loaded = ChanTable.read_csv(out / "chan_table.csv", out / "context.csv")
restored = MergedKlineSeries.from_chan_table(loaded, "merged")
assert restored.klines == series.klines and restored.config == series.config
assert restored.rule_tree_ref == series.rule_tree_ref
assert loaded.rows == result.rows
assert all(restored.explain(i) == series.explain(i) for i in range(len(series)))
frame = series.to_dataframe()
assert len(frame) == len(series)
assert frame.attrs["rule_tree_ref"] == series.rule_tree_ref
for before, after in zip(table, result, strict=True):
    assert all(before[k] == after[k] for k in list(before)[:10])
assert hashes == {str(p): sha256(p.read_bytes()).hexdigest() for p in paths}
report = dict(
    raw_count=len(table),
    merged_count=len(series),
    dataframe_count=len(frame),
    source_identity=True,
    raw_columns_unchanged=True,
    context_trace_roundtrip=True,
    explanation_checks=len(series),
    source_hashes=hashes,
    csv_bytes=(out / "chan_table.csv").stat().st_size,
    context_bytes=(out / "context.csv").stat().st_size,
)
(out / "verification.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
