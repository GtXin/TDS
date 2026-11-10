import json
from dataclasses import replace

import pytest
from test_merged_kline import raw

from chanlab.algo.chan_table import COLUMNS, ChanTable
from chanlab.algo.merged_kline import MergedKlineSeries


def table_for(source):
    rows = []
    for i, b in enumerate(source):
        row = dict.fromkeys(COLUMNS, "NA")
        row.update(
            raw_index=str(i),
            timestamp=b.timestamp.isoformat(),
            symbol=b.symbol,
            period=b.period,
            source=b.source,
            **{
                k: str(getattr(b, k))
                for k in ("open", "high", "low", "close", "volume")
            },
        )
        rows.append(row)
    return ChanTable(rows, {"source": "test"}, source_series=source)


def test_register_roundtrip(tmp_path):
    source = raw([(1, 3), (2, 4), (1, 5), (0, 3)])
    original = table_for(source)
    merged = MergedKlineSeries.derive_from(
        source, {"initialization": "UP"}, "test:version"
    )
    table = merged.to_chan_table(original, "merged")
    assert original[0]["mk_ids"] == "NA"
    assert MergedKlineSeries.from_chan_table(table, "merged") is merged
    assert table.source_series is source
    assert table.memberships["merged"][2] == (2,)
    assert table.start_ids["merged"][2] == ()
    assert table.end_ids["merged"][2] == (2,)
    assert table[1]["mk_direction"] == "up" and table[2]["mk_direction"] == "NA"
    assert json.loads(table[2]["mk_start_ids"]) == []
    table.write_csv(tmp_path / "data.csv", tmp_path / "context.csv")
    restored = ChanTable.read_csv(tmp_path / "data.csv", tmp_path / "context.csv")
    again = MergedKlineSeries.from_chan_table(restored, "merged")
    assert again.klines == merged.klines
    assert again.config == merged.config and again.rule_tree_ref == merged.rule_tree_ref
    assert again.source_series is restored.source_series
    assert [again.explain(i) for i in range(len(again))] == [
        merged.explain(i) for i in range(len(merged))
    ]
    assert restored.rows == table.rows
    with pytest.raises(ValueError):
        table.write_csv(tmp_path / "bad.csv")
    with pytest.raises(ValueError):
        table.write_csv(tmp_path / "same.csv", tmp_path / "same.csv")
    with pytest.raises(KeyError):
        MergedKlineSeries.from_chan_table(table, "missing")
    with pytest.raises(ValueError):
        merged.to_chan_table(table, "")
    with pytest.raises(ValueError):
        replace(merged, rule_tree_ref="other").to_chan_table(table, "merged")
    with pytest.raises(ValueError):
        merged.to_chan_table(ChanTable(original.rows), "x")
    second = replace(merged, rule_tree_ref="second")
    multi = second.to_chan_table(table, "second")
    assert (
        multi.feature_series["merged"] is merged
        and multi.feature_series["second"] is second
    )
    multi.write_csv(tmp_path / "multi.csv", tmp_path / "multi-context.csv")
    assert (
        len(
            ChanTable.read_csv(
                tmp_path / "multi.csv", tmp_path / "multi-context.csv"
            ).feature_series
        )
        == 2
    )
    rows = [dict(x) for x in table]
    rows[1]["mk_ids"] = "[]"
    with pytest.raises(ValueError):
        ChanTable(rows, table.context)
    with pytest.raises(TypeError):
        table.feature_series["bad"] = merged


def test_dataframe():
    pytest.importorskip("pandas")
    source = raw([(1, 3), (2, 4), (1, 5)])
    merged = MergedKlineSeries.derive_from(source, {"initialization": "UP"}, "test")
    frame = merged.to_dataframe()
    assert list(frame.id) == [b.id for b in merged]
    assert frame.attrs["rule_tree_ref"] == "test"
    assert str(frame.confirmed_at.dtype) == "datetime64[ns, UTC]"
    frame.loc[0, "high"] = 999
    assert merged[0].high == 3


def test_both_source_entries():
    source = raw([(1, 3), (2, 4), (1, 5)])
    table = ChanTable.from_source_series(source, {"snapshot": "sample"})
    direct = MergedKlineSeries.derive_from(source, {"initialization": "UP"}, "v")
    through = MergedKlineSeries.derive_from(table, {"initialization": "UP"}, "v")
    assert direct.klines == through.klines
    assert (
        through.source_series is direct.source_series is source is table.source_series
    )
    assert through.to_chan_table(table, "merged").feature_series["merged"] is through


def test_persisted_source_context_tampering():
    source = raw([(1, 3), (2, 4), (1, 5)])
    table = ChanTable.from_source_series(source)
    merged = MergedKlineSeries.derive_from(table, {"initialization": "UP"}, "v")
    registered = merged.to_chan_table(table, "merged")
    context = dict(registered.context)
    from chanlab.data.merged_kline_table import FEATURE_CONTEXT

    context[FEATURE_CONTEXT] = "{}"
    with pytest.raises(ValueError):
        ChanTable(registered.rows, context)
    context[FEATURE_CONTEXT] = "bad json"
    with pytest.raises(ValueError):
        ChanTable(registered.rows, context)
    rows = [dict(row) for row in registered]
    rows[0]["volume"] = "2"
    with pytest.raises(ValueError):
        ChanTable(rows, registered.context)


def test_missing_dataframe_dependency(monkeypatch):
    import builtins

    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "pandas":
            raise ImportError("blocked")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    series = MergedKlineSeries.derive_from(raw([(1, 2)]), {"initialization": "UP"}, "v")
    with pytest.raises(ImportError, match="dataframe"):
        series.to_dataframe()
