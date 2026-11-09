import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(
    params=[
        "src/chanlab/algo/chan_table.py",
        "artifacts/mas/memo011/baseline/chan_table.py",
        "artifacts/mas/memo011/python_pro/chan_table.py",
    ]
)
def mod(request):
    spec = importlib.util.spec_from_file_location("subject", request.param)
    module = importlib.util.module_from_spec(spec)
    sys.modules["subject"] = module
    spec.loader.exec_module(module)
    return module


def test_full_roundtrip(mod, tmp_path):
    folder = Path("samples/chan_table")
    table = mod.ChanTable.read_csv(
        next(folder.glob("*chan_table*.csv")), next(folder.glob("*context*.csv"))
    )
    assert len(table) == 10060
    table.write_csv(tmp_path / "rows.csv", tmp_path / "context.csv")
    again = mod.ChanTable.read_csv(tmp_path / "rows.csv", tmp_path / "context.csv")
    assert table.rows == again.rows
    assert table.context == again.context


@pytest.mark.parametrize(
    "field,value",
    [
        ("raw_index", "9"),
        ("volume", "-1"),
        ("high", "0"),
        ("timestamp", "2026-01-01T00:00:00"),
        ("mk_ids", "[true]"),
        ("mk_ids", "[1,1]"),
        ("mk_ids", "{}"),
    ],
)
def test_invalid(mod, field, value):
    import csv

    row = next(
        csv.DictReader(next(Path("samples/chan_table").glob("*chan_table*.csv")).open())
    )
    row[field] = value
    with pytest.raises((ValueError, TypeError)):
        mod.ChanTable([row])


@pytest.mark.parametrize(
    "field,value",
    [
        ("open", "nan"),
        ("close", "inf"),
        ("source", ""),
        ("period", "NA"),
        ("symbol", ""),
        ("mk_ids", "[]"),
        ("fx_kind", "top"),
        ("timestamp", "2026-01-01T00:00:00+01:00"),
    ],
)
def test_more_invalid(mod, field, value):
    import csv

    with next(Path("samples/chan_table").glob("*chan_table*.csv")).open() as stream:
        row = next(csv.DictReader(stream))
    row[field] = value
    with pytest.raises(ValueError):
        mod.ChanTable([row])


def test_order_schema_and_context(mod, tmp_path):
    import csv

    with next(Path("samples/chan_table").glob("*chan_table*.csv")).open() as stream:
        rows = list(csv.DictReader(stream))[:2]
    table = mod.ChanTable(rows, {"source_snapshot": "retained"})
    assert table[0] == next(iter(table))
    table.validate()
    table.write_csv(tmp_path / "rows.csv", tmp_path / "context.csv")
    assert (
        mod.ChanTable.read_csv(tmp_path / "rows.csv", tmp_path / "context.csv").context
        == table.context
    )
    rows[1]["timestamp"] = rows[0]["timestamp"]
    with pytest.raises(ValueError):
        mod.ChanTable(rows)
    rows[1]["timestamp"] = "2000-01-01T00:00:00+00:00"
    with pytest.raises(ValueError):
        mod.ChanTable(rows)
    rows[1]["symbol"] = "other"
    with pytest.raises(ValueError):
        mod.ChanTable(rows)
    with pytest.raises(ValueError):
        mod.ChanTable([])
    rows[0].pop("volume")
    with pytest.raises(ValueError):
        mod.ChanTable(rows[:1])
    (tmp_path / "bad.csv").write_text("bad,header\n")
    with pytest.raises(ValueError):
        mod.ChanTable.read_csv(tmp_path / "bad.csv")
    (tmp_path / "context.csv").write_text("bad,header\n")
    with pytest.raises(ValueError):
        mod.ChanTable.read_csv(tmp_path / "rows.csv", tmp_path / "context.csv")
    (tmp_path / "context.csv").write_text("key,value\nx,1\nx,2\n")
    with pytest.raises(ValueError):
        mod.ChanTable.read_csv(tmp_path / "rows.csv", tmp_path / "context.csv")
