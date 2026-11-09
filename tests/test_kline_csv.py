"""Shared memo013 CSV acceptance tests using temporary generated outputs."""

import csv
import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.data.kline_csv import RAW_COLUMNS, read_kline_csv, write_kline_csv

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COLUMNS = (
    "timestamp",
    "symbol",
    "period",
    "source",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
NUMERIC_COLUMNS = ("open", "high", "low", "close", "volume")


def raw_rows():
    first = dict(
        zip(
            EXPECTED_COLUMNS,
            (
                "2026-01-01T00:00:00Z",
                "TEST",
                "15m",
                "fixture/source",
                "11",
                "13",
                "10",
                "12",
                "20",
            ),
        )
    )
    second = dict(first, timestamp="2026-01-01T00:15:00+00:00", source="other/source")
    return [first, second]


def save_rows(path, rows, columns=EXPECTED_COLUMNS):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def bar_values(bar):
    return tuple(getattr(bar, field) for field in EXPECTED_COLUMNS)


def assert_row_error(path, field, row=3):
    with pytest.raises(ValueError) as caught:
        read_kline_csv(path)
    message = str(caught.value).lower()
    assert field.lower() in message
    assert str(row) in message


def test_raw_schema_and_csv_context_roundtrip(tmp_path):
    assert RAW_COLUMNS == EXPECTED_COLUMNS
    path = tmp_path / "raw.csv"
    save_rows(path, raw_rows())
    series, context = read_kline_csv(path)
    assert isinstance(series, KlineTSeries)
    assert isinstance(context, Mapping)
    assert dict(context) == {}
    assert len(series) == 2
    assert series[0].timestamp == datetime(2026, 1, 1, tzinfo=UTC)
    assert series[1].timestamp - series[0].timestamp == timedelta(minutes=15)
    assert [bar.source for bar in series] == ["fixture/source", "other/source"]
    metadata = {"source": "quoted, source", "note": 'Unicode 原始 "value"\nsecond line'}
    exported = tmp_path / "export.csv"
    context_path = tmp_path / "context.csv"
    write_kline_csv(series, exported, context_path, context=metadata)
    again, again_context = read_kline_csv(exported, context_path)
    assert [bar_values(bar) for bar in again] == [bar_values(bar) for bar in series]
    assert dict(again_context) == metadata
    with exported.open(newline="", encoding="utf-8") as stream:
        assert tuple(next(csv.reader(stream))) == EXPECTED_COLUMNS


def test_write_without_context_path_when_no_metadata(tmp_path):
    bar = Kline(
        symbol="TEST",
        period="15m",
        source="fixture",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        open=-4,
        high=-2,
        low=-6,
        close=-3,
        volume=0,
    )
    path = tmp_path / "raw.csv"
    write_kline_csv(KlineTSeries([bar]), path)
    series, context = read_kline_csv(path)
    assert bar_values(series[0]) == bar_values(bar)
    assert dict(context) == {}


def test_large_exactly_representable_integer_roundtrip(tmp_path):
    value = 2**60
    bar = Kline(
        "TEST",
        "15m",
        "fixture",
        datetime(2026, 1, 1, tzinfo=UTC),
        value,
        value,
        value,
        value,
        value,
    )
    path = tmp_path / "large.csv"
    write_kline_csv(KlineTSeries([bar]), path)
    series, _ = read_kline_csv(path)
    assert series[0] == bar


def test_full_master_to_raw_roundtrip_preserves_values_provenance_and_inputs(tmp_path):
    folder = ROOT / "samples/chan_table"
    master = next(folder.glob("*chan_table*.csv"))
    source_context = next(folder.glob("*context*.csv"))
    source = ROOT / "references/proj009data/dce-kqm-m-15m.csv"
    manifest = ROOT / "references/proj009data/provenance.json"
    protected = (master, source_context, source, manifest)
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}
    assert before[source] == json.loads(manifest.read_text())["sha256"]
    with master.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = tuple(reader.fieldnames)
        rows = list(reader)
    assert len(columns) == 41
    assert len(rows) == 10060
    features = set(columns) - set(EXPECTED_COLUMNS) - {"raw_index"}
    assert all(row[field] == "NA" for row in rows for field in features)
    series, context = read_kline_csv(master, source_context)
    assert len(series) == 10060
    with source_context.open(newline="", encoding="utf-8") as stream:
        assert dict(context) == {
            row["key"]: row["value"] for row in csv.DictReader(stream)
        }
    for bar, row in zip(series, rows, strict=True):
        assert bar.timestamp == datetime.fromisoformat(row["timestamp"])
        assert bar.timestamp.utcoffset() == timedelta(0)
        for field in ("symbol", "period", "source"):
            assert getattr(bar, field) == row[field]
        for field in NUMERIC_COLUMNS:
            assert getattr(bar, field) == float(row[field])
    raw_path, context_path = tmp_path / "raw.csv", tmp_path / "context.csv"
    write_kline_csv(series, raw_path, context_path, context=context)
    again, again_context = read_kline_csv(raw_path, context_path)
    assert [bar_values(bar) for bar in again] == [bar_values(bar) for bar in series]
    assert dict(again_context) == dict(context)
    with raw_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        assert tuple(next(reader)) == EXPECTED_COLUMNS
        assert sum(1 for _ in reader) == 10060
    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected
    } == before


@pytest.mark.parametrize(
    "field,value",
    [
        ("timestamp", "invalid"),
        ("timestamp", "2026-01-01T00:15:00"),
        ("timestamp", "2026-01-01T00:15:00+01:00"),
        ("symbol", ""),
        ("period", "NA"),
        ("source", " \t"),
        ("open", "not-a-number"),
        ("open", "nan"),
        ("high", "inf"),
        ("low", "14"),
        ("close", "9"),
        ("volume", "-1"),
        ("volume", ""),
    ],
)
def test_bad_csv_field_reports_row_and_field(tmp_path, field, value):
    rows = raw_rows()
    rows[1][field] = value
    path = tmp_path / "bad.csv"
    save_rows(path, rows)
    assert_row_error(path, field)


@pytest.mark.parametrize(
    "field,value",
    [
        ("symbol", "OTHER"),
        ("period", "1m"),
        ("timestamp", "2026-01-01T00:00:00Z"),
        ("timestamp", "2025-12-31T23:45:00Z"),
    ],
)
def test_bad_series_csv_reports_row_and_field(tmp_path, field, value):
    rows = raw_rows()
    rows[1][field] = value
    path = tmp_path / "bad.csv"
    save_rows(path, rows)
    assert_row_error(path, field)


@pytest.mark.parametrize(
    "header",
    [
        (),
        ("bad", "header"),
        EXPECTED_COLUMNS[:-1],
        EXPECTED_COLUMNS + ("extra",),
        EXPECTED_COLUMNS[::-1],
        EXPECTED_COLUMNS[:-1] + ("open",),
    ],
)
def test_rejects_noncontract_csv_headers(tmp_path, header):
    path = tmp_path / "bad.csv"
    with path.open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream).writerow(header)
    with pytest.raises(ValueError):
        read_kline_csv(path)


@pytest.mark.parametrize("extra", [False, True])
def test_rejects_rows_with_wrong_number_of_fields(tmp_path, extra):
    path = tmp_path / "bad.csv"
    rows = raw_rows()
    second = [rows[1][field] for field in EXPECTED_COLUMNS]
    second = second + ["extra"] if extra else second[:-1]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(EXPECTED_COLUMNS)
        writer.writerow([rows[0][field] for field in EXPECTED_COLUMNS])
        writer.writerow(second)
    with pytest.raises(ValueError) as caught:
        read_kline_csv(path)
    assert "3" in str(caught.value)
    if not extra:
        assert "volume" in str(caught.value).lower()


def test_rejects_empty_series_csv(tmp_path):
    path = tmp_path / "empty.csv"
    save_rows(path, [])
    with pytest.raises(ValueError):
        read_kline_csv(path)


@pytest.mark.parametrize(
    "text",
    ["bad,header\nx,y\n", "key,value\nx,1\nx,2\n", "key,value\nx\n"],
)
def test_rejects_malformed_context_and_duplicate_keys(tmp_path, text):
    path, context_path = tmp_path / "raw.csv", tmp_path / "context.csv"
    save_rows(path, raw_rows())
    context_path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        read_kline_csv(path, context_path)


def test_nonempty_context_requires_context_path(tmp_path):
    path = tmp_path / "raw.csv"
    save_rows(path, raw_rows())
    series, _ = read_kline_csv(path)
    with pytest.raises(ValueError):
        write_kline_csv(series, tmp_path / "export.csv", context={"source": "retained"})


def test_data_and_context_paths_must_resolve_to_different_files(tmp_path):
    path = tmp_path / "raw.csv"
    alias = tmp_path / "alias.csv"
    save_rows(path, raw_rows())
    alias.symlink_to(path)
    series, _ = read_kline_csv(path)
    for context_path in (path, alias):
        with pytest.raises(ValueError):
            read_kline_csv(path, context_path)
        with pytest.raises(ValueError):
            write_kline_csv(series, path, context_path, context={"key": "value"})


def test_hardlinked_output_paths_are_rejected_before_overwriting(tmp_path):
    path = tmp_path / "raw.csv"
    sidecar = tmp_path / "context.csv"
    save_rows(path, raw_rows())
    sidecar.hardlink_to(path)
    before = path.read_bytes()
    series, _ = read_kline_csv(path)
    with pytest.raises(ValueError, match="context_path"):
        write_kline_csv(series, path, sidecar, context={"source": "retained"})
    assert path.read_bytes() == sidecar.read_bytes() == before
