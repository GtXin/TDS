"""Acceptance checks for series-owned provenance and public CSV methods."""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import MappingProxyType

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.data.kline_csv import RAW_COLUMNS, read_kline_csv, write_kline_csv

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def bars() -> tuple[Kline, ...]:
    return tuple(
        Kline(
            symbol="TEST",
            period="15m",
            source=f"fixture/source/{index}",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(minutes=15 * index),
            open=11.0,
            high=13.0,
            low=10.0,
            close=12.0,
            volume=20.0,
        )
        for index in range(2)
    )


@pytest.fixture
def series(bars: tuple[Kline, ...]) -> KlineTSeries:
    return KlineTSeries(
        bars,
        context={
            "source_snapshot": "original,revision",
            "note": '原始 "quotes"\nsecond line',
            "empty_value": "",
        },
    )


def test_context_is_an_immutable_snapshot_of_input_mapping(
    bars: tuple[Kline, ...],
) -> None:
    original = {"source_snapshot": "original"}
    series = KlineTSeries(bars, context=MappingProxyType(original))
    original["source_snapshot"] = "changed"
    original["extra"] = "new"
    assert isinstance(series.context, Mapping)
    assert dict(series.context) == {"source_snapshot": "original"}
    with pytest.raises((AttributeError, TypeError)):
        series.context = {}  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        del series.context  # type: ignore[misc]
    with pytest.raises(TypeError):
        series.context["source_snapshot"] = "changed"  # type: ignore[index]
    with pytest.raises(TypeError):
        del series.context["source_snapshot"]  # type: ignore[attr-defined]
    series.validate()
    assert dict(series.context) == {"source_snapshot": "original"}


@pytest.mark.parametrize(
    "context",
    [
        {"": "value"},
        {" \t": "value"},
        {1: "value"},
        {"key": 1},
        {"key": None},
        [],
        [("key", "value")],
        123,
    ],
)
def test_invalid_context_is_rejected_at_construction(
    bars: tuple[Kline, ...], context: object
) -> None:
    with pytest.raises(ValueError, match="context"):
        KlineTSeries(bars, context=context)  # type: ignore[arg-type]


def test_series_equality_includes_context_and_hash_remains_usable(
    bars: tuple[Kline, ...],
) -> None:
    first = KlineTSeries(bars, context={"snapshot": "one", "version": "1"})
    equal = KlineTSeries(bars, context={"version": "1", "snapshot": "one"})
    changed = KlineTSeries(bars, context={"snapshot": "two", "version": "1"})
    assert first == equal
    assert first != changed
    assert hash(first) == hash(equal) == hash(changed)
    assert {first: "stored"}[equal] == "stored"
    assert len({first, equal, changed}) == 2


def test_empty_context_csv_requires_no_sidecar(
    bars: tuple[Kline, ...], tmp_path: Path
) -> None:
    series = KlineTSeries(bars)
    assert dict(series.context) == {}
    path = tmp_path / "raw.csv"
    assert series.write_csv(path) is None
    assert KlineTSeries.read_csv(path) == series
    assert KlineTSeries(bars, context=None) == series
    assert KlineTSeries(bars, context={}) == series


def test_full_master_roundtrip_uses_one_object_with_owned_context(
    tmp_path: Path,
) -> None:
    folder = ROOT / "samples/chan_table"
    master = next(folder.glob("*chan_table*.csv"))
    sidecar = next(folder.glob("*context*.csv"))
    source = ROOT / "references/proj009data/dce-kqm-m-15m.csv"
    manifest = ROOT / "references/proj009data/provenance.json"
    protected = (master, sidecar, source, manifest)
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected}

    series = KlineTSeries.read_csv(master, sidecar)
    assert isinstance(series, KlineTSeries)
    assert len(series) == 10060
    assert series.context["sha256"] == before[source]
    with sidecar.open(newline="", encoding="utf-8") as stream:
        assert dict(series.context) == {
            row["key"]: row["value"] for row in csv.DictReader(stream)
        }
    with master.open(newline="", encoding="utf-8") as stream:
        for bar, row in zip(series, csv.DictReader(stream), strict=True):
            assert bar.timestamp == datetime.fromisoformat(row["timestamp"])
            assert bar.timestamp.utcoffset() == timedelta(0)
            for field in ("symbol", "period", "source"):
                assert getattr(bar, field) == row[field]
            for field in ("open", "high", "low", "close", "volume"):
                assert getattr(bar, field) == float(row[field])

    exported, exported_sidecar = tmp_path / "raw.csv", tmp_path / "context.csv"
    assert series.write_csv(exported, exported_sidecar) is None
    restored = KlineTSeries.read_csv(exported, exported_sidecar)
    assert restored == series
    with exported.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        assert tuple(next(reader)) == RAW_COLUMNS
        assert sum(1 for _ in reader) == 10060
    assert {
        path: hashlib.sha256(path.read_bytes()).hexdigest() for path in protected
    } == before


def test_class_factory_honors_subclass(series: KlineTSeries, tmp_path: Path) -> None:
    class SpecializedSeries(KlineTSeries):
        pass

    path, sidecar = tmp_path / "raw.csv", tmp_path / "context.csv"
    series.write_csv(path, sidecar)
    restored = SpecializedSeries.read_csv(path, sidecar)
    assert type(restored) is SpecializedSeries
    assert restored.klines == series.klines
    assert restored.context == series.context


def test_legacy_reader_returns_the_same_owned_context(
    series: KlineTSeries, tmp_path: Path
) -> None:
    path, sidecar = tmp_path / "raw.csv", tmp_path / "context.csv"
    series.write_csv(path, sidecar)
    restored, context = read_kline_csv(path, sidecar)
    assert context is restored.context
    assert restored == series


def test_legacy_writer_defaults_to_owned_context(
    series: KlineTSeries, tmp_path: Path
) -> None:
    path, sidecar = tmp_path / "raw.csv", tmp_path / "context.csv"
    write_kline_csv(series, path, sidecar)
    assert KlineTSeries.read_csv(path, sidecar) == series


def test_legacy_explicit_override_does_not_mutate_owned_context(
    series: KlineTSeries, tmp_path: Path
) -> None:
    path, sidecar = tmp_path / "raw.csv", tmp_path / "context.csv"
    before = dict(series.context)
    override = {"source_snapshot": "explicit override"}
    write_kline_csv(series, path, sidecar, context=override)
    restored = KlineTSeries.read_csv(path, sidecar)
    assert restored.klines == series.klines
    assert dict(restored.context) == override
    assert dict(series.context) == before
    write_kline_csv(series, path, context={})
    assert dict(KlineTSeries.read_csv(path).context) == {}
    assert dict(series.context) == before


@pytest.mark.parametrize("legacy", [False, True])
def test_owned_context_requires_sidecar_before_output_is_opened(
    series: KlineTSeries, tmp_path: Path, legacy: bool
) -> None:
    path = tmp_path / "raw.csv"
    path.write_text("original output\n", encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="context_path"):
        if legacy:
            write_kline_csv(series, path)
        else:
            series.write_csv(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_csv_methods_reject_aliased_destinations_before_overwriting(
    series: KlineTSeries, tmp_path: Path, alias: str
) -> None:
    path, sidecar = tmp_path / "raw.csv", tmp_path / "alias.csv"
    KlineTSeries(series.klines).write_csv(path)
    if alias == "same":
        sidecar = path
    elif alias == "symlink":
        sidecar.symlink_to(path)
    else:
        sidecar.hardlink_to(path)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="context_path"):
        series.write_csv(path, sidecar)
    assert path.read_bytes() == sidecar.read_bytes() == before
    with pytest.raises(ValueError, match="context_path"):
        KlineTSeries.read_csv(path, sidecar)


def test_object_csv_works_without_importing_plotly(tmp_path: Path) -> None:
    script = """
import builtins
import sys
from datetime import UTC, datetime
from pathlib import Path

original_import = builtins.__import__
plotly_attempts = []
def without_plotly(name, *args, **kwargs):
    if name == 'plotly' or name.startswith('plotly.'):
        plotly_attempts.append(name)
        raise ModuleNotFoundError('Plotly intentionally unavailable', name=name)
    return original_import(name, *args, **kwargs)
builtins.__import__ = without_plotly

from chanlab.algo.kline import Kline, KlineTSeries

bar = Kline('TEST', '15m', 'fixture', datetime(2026, 1, 1, tzinfo=UTC),
            11.0, 13.0, 10.0, 12.0, 20.0)
series = KlineTSeries([bar], context={'source_snapshot': 'original'})
path = Path(sys.argv[1]) / 'raw.csv'
sidecar = Path(sys.argv[1]) / 'context.csv'
series.write_csv(path, sidecar)
restored = KlineTSeries.read_csv(path, sidecar)
assert restored == series
assert restored.context['source_snapshot'] == 'original'
assert not plotly_attempts
assert not any(name == 'plotly' or name.startswith('plotly.') for name in sys.modules)
"""
    environment = dict(
        os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONDONTWRITEBYTECODE="1"
    )
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
