import itertools
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta

import pytest

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import (
    MergedKline,
    MergedKlineSeries,
)

direction_between = MergedKlineSeries._direction_between

has_inclusion = MergedKlineSeries._has_inclusion

merge_included = MergedKlineSeries._merge_included

merge_outer_boundary = MergedKlineSeries._merge_outer_boundary

validate_merged_result = MergedKlineSeries._validate_result

work_from_raw = MergedKlineSeries._work_from_raw


def raw(intervals):
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
        for i, (lo, hi) in enumerate(intervals)
    )


def derive(intervals, policy="UP"):
    return MergedKlineSeries.derive_from(
        raw(intervals), {"initialization": policy}, "memo015:test"
    )


def values(s):
    return [(x.low, x.high, x.direction, x.source_start, x.source_stop) for x in s]


def test_worked_initialization():
    data = [(2, 5), (3, 4), (2.5, 4.5), (3, 6)]
    assert values(derive(data)) == [
        (3, 5, "up", 0, 2),
        (2.5, 4.5, "down", 2, 3),
        (3, 6, "up", 3, 4),
    ]
    assert values(derive(data, "DOWN")) == [
        (2, 4, "down", 0, 2),
        (2.5, 4.5, "up", 2, 3),
        (3, 6, "up", 3, 4),
    ]
    assert values(derive(data, "OUTER")) == [(2, 5, None, 0, 3), (3, 6, "up", 3, 4)]
    both = derive(data, "BOTH")
    assert both["kind"] == "dual"
    assert both["main"].klines == derive(data).klines
    assert both["comparison"].klines == derive(data, "DOWN").klines
    assert both["warning_evaluation"] == "not_evaluated"
    pending = derive(data, "UNSET")
    assert pending["kind"] == "pending"
    assert pending["raw_index"] == 1 and pending["current"]["source_stop"] == 1
    assert pending["candidate"]["source_start"] == 1 and not pending["saved"]


def test_sequential_counterexample():
    assert values(derive([(0, 2), (1, 4), (2, 3), (0, 3.5)])) == [
        (0, 2, None, 0, 1),
        (2, 4, "up", 1, 3),
        (0, 3.5, "down", 3, 4),
    ]


def test_main_example():
    s = derive(
        [(1, 3), (2, 4), (1, 5), (3, 5), (3, 6), (1, 5), (2, 4), (0, 6), (0, 4), (0, 5)]
    )
    assert values(s) == [(1, 3, None, 0, 1), (3, 6, "up", 1, 5), (0, 4, "down", 5, 10)]


@pytest.mark.parametrize("policy", ["UP", "DOWN", "OUTER", "BOTH", "UNSET"])
def test_single_and_noninclusion(policy):
    s = derive([(1, 2)], policy)
    assert values(s) == [(1, 2, None, 0, 1)]
    assert isinstance(derive([(1, 2), (2, 3)], policy), MergedKlineSeries)


@pytest.mark.parametrize(
    "field,value",
    [
        ("id", True),
        ("id", -1),
        ("low", float("nan")),
        ("high", float("inf")),
        ("low", True),
        ("direction", "bad"),
        ("source_start", -1),
        ("source_stop", 0),
        ("status", "confirmed"),
        ("confirmed_at", datetime.now(UTC)),
    ],
)
def test_invalid_record(field, value):
    args = {
        "id": 1,
        "low": 1,
        "high": 2,
        "direction": None,
        "source_start": 0,
        "source_stop": 1,
    }
    args[field] = value
    with pytest.raises(ValueError):
        MergedKline(**args)


def test_access_trace_immutability():
    s = derive([(1, 3), (2, 4), (1, 5), (0, 3)])
    assert s.get_by_id(s[-1].id) is s[-1]
    assert s[:] == tuple(s) and s[0:0] == ()
    with pytest.raises(KeyError):
        s.get_by_id(99)
    with pytest.raises(FrozenInstanceError):
        s.klines = ()
    assert "memo015:test" in s.explain(1) and "2.5.a" in s.explain(1)
    assert all(x.status == "unconfirmed" and x.confirmed_at is None for x in s)
    for change in [
        {"trace_by_point": ()},
        {"trace_by_point": ((999,),) * len(s)},
        {"rule_tree_ref": ""},
        {"klines": ()},
        {"config": None},
    ]:
        with pytest.raises(ValueError):
            replace(s, **change)
    with pytest.raises(ValueError):
        validate_merged_result(raw([(1, 3)]), s)


def test_helpers():
    r = raw([(2, 5), (3, 4), (1, 2)])
    a, b = work_from_raw(r, 0), work_from_raw(r, 1)
    assert has_inclusion(a, b) == has_inclusion(b, a)
    with pytest.raises(ValueError):
        direction_between(a, b)
    with pytest.raises(ValueError):
        merge_included(a, b)
    assert merge_outer_boundary(a, b)["direction"] is None
    assert merge_included(dict(a, direction="up"), b)["low"] == 3
    assert merge_included(dict(a, direction="down"), b)["high"] == 4
    with pytest.raises(ValueError):
        merge_outer_boundary(dict(a, direction="up"), b)
    with pytest.raises(ValueError):
        merge_included(dict(a, direction="up"), work_from_raw(r, 2))
    with pytest.raises(ValueError):
        work_from_raw(r, -1)
    with pytest.raises(ValueError):
        work_from_raw(r, 3)
    with pytest.raises(ValueError):
        derive([(1, 2)], "bad")


@pytest.mark.parametrize("policy", ["UP", "DOWN", "OUTER"])
def test_exhaustive_small_sequences(policy):
    # Independent scalar oracle; every candidate compares with the current merged interval.
    intervals = [(a, b) for a in range(3) for b in range(a, 3)]
    for data in itertools.product(intervals, repeat=3):
        expected = []
        lo, hi = data[0]
        direction = None
        start = 0
        for i, (a, b) in enumerate(data[1:], 1):
            inclusion = (lo <= a and hi >= b) or (a <= lo and b >= hi)
            if not inclusion:
                expected.append((lo, hi, direction, start, i))
                direction = "up" if b > hi else "down"
                lo, hi = a, b
                start = i
            else:
                if direction is None and policy != "OUTER":
                    direction = policy.lower()
                if direction == "up":
                    lo, hi = max(lo, a), max(hi, b)
                elif direction == "down":
                    lo, hi = min(lo, a), min(hi, b)
                else:
                    lo, hi = min(lo, a), max(hi, b)
        expected.append((lo, hi, direction, start, len(data)))
        s = derive(data, policy)
        assert values(s) == expected
        assert len(s.trace_by_point) == len(s)
        assert s.source_series.klines == raw(data).klines


def test_result_validation_regressions():
    s = derive([(1, 5), (3, 7), (2, 4)])
    # Nonadjacent inclusion is permitted; exact same raw values are not source identity.
    assert has_inclusion(s[0], s[2])
    with pytest.raises(ValueError):
        replace(s, klines=(s[0], s[1], replace(s[2], id=s[0].id)))
    with pytest.raises(ValueError):
        replace(s, klines=(replace(s[0], source_start=1),) + s.klines[1:])
    with pytest.raises(ValueError):
        replace(s, klines=s.klines[:-1])
    with pytest.raises(ValueError):
        replace(s, klines=s.klines[:-1] + (replace(s[-1], source_stop=4),))
    with pytest.raises(ValueError):
        replace(s, klines=(s[0], replace(s[1], low=2, high=5), s[2]))
    with pytest.raises(ValueError):
        replace(s, trace_by_point=((),) + s.trace_by_point[1:])
    with pytest.raises(ValueError):
        replace(s, trace_by_point=((True,),) + s.trace_by_point[1:])
    with pytest.raises(ValueError):
        replace(s, trace_by_point=((0,),) * len(s))
    with pytest.raises(ValueError):
        replace(s, trace=(None,) + s.trace[1:])
    with pytest.raises(ValueError):
        replace(s, trace=(dict(s.trace[0], rule="bad"),) + s.trace[1:])
    with pytest.raises(ValueError):
        replace(s, trace=(dict(s.trace[0], raw_index=99),) + s.trace[1:])
    with pytest.raises(ValueError):
        replace(
            s,
            trace=(dict(s.trace[0], after=work_from_raw(raw([(1, 5)]), 0)),)
            + s.trace[1:],
        )
    with pytest.raises(ValueError):
        MergedKline(1, 1, 10**1000, None, 0, 1)
    with pytest.raises(ValueError):
        replace(s, source_series=raw([(1, 5), (3, 7), (2, 4)]))
    with pytest.raises(ValueError):
        replace(
            s,
            trace=(dict(s.trace[0], after=dict(s.trace[0]["after"], source_stop=99)),)
            + s.trace[1:],
        )
    with pytest.raises(ValueError):
        MergedKlineSeries.derive_from(s.source_series, None, "v")
    with pytest.raises(ValueError):
        MergedKlineSeries.derive_from(s.source_series, {"initialization": "UP"}, "")


def test_plot_source_alignment(tmp_path):
    s = derive([(1, 3), (2, 4), (1, 5), (0, 3), (1, 2)])
    before = s.source_series.klines
    fig = s.plot(
        start=1,
        stop=2,
        volume=True,
        title="Merged test",
        style="ranges",
        show_gaps=True,
    )
    candles = next(t for t in fig.data if t.type == "candlestick")
    volumes = next(t for t in fig.data if t.type == "bar")
    ranges = next(t for t in fig.data if t.type == "scatter")
    assert fig.layout.xaxis.type == fig.layout.xaxis2.type == "date"
    selected = s[1]
    assert list(candles.x) == [
        x.timestamp
        for x in s.source_series[selected.source_start : selected.source_stop]
    ]
    assert list(candles.high) == [
        x.high for x in s.source_series[selected.source_start : selected.source_stop]
    ]
    assert list(volumes.y) == [
        x.volume for x in s.source_series[selected.source_start : selected.source_stop]
    ]
    assert list(ranges.y) == [selected.low, selected.high, None]
    assert ranges.x[0] == s.source_series[selected.source_start].timestamp
    assert "MK" in ranges.text[0]
    assert len(s.plot(volume=False, style="ranges", show_gaps=True).data) == 4
    path = tmp_path / "merged.html"
    fig.write_html(path, include_plotlyjs=True)
    assert path.stat().st_size > 1000
    with pytest.raises(ValueError):
        s.plot(start=1, stop=1)
    assert before is s.source_series.klines


def test_missing_plot_dependency(monkeypatch):
    import builtins

    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "plotly" or name.startswith("plotly."):
            raise ImportError("blocked")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(ImportError, match="uv sync --extra plot"):
        derive([(1, 2)]).plot()


def test_only_two_classes_and_detached_data():
    import ast
    from pathlib import Path

    tree = ast.parse(Path("src/chanlab/algo/merged_kline.py").read_text())
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    assert not any(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body
    )
    assert {n.name for n in classes} == {"MergedKline", "MergedKlineSeries"}
    counts = {
        n.name: sum(isinstance(x, ast.AnnAssign) for x in n.body) for n in classes
    }
    assert counts == {"MergedKline": 8, "MergedKlineSeries": 6}
    config = {"initialization": "UP"}
    source = raw([(1, 3), (2, 4), (1, 5)])
    s = MergedKlineSeries.derive_from(source, config, "v")
    config["initialization"] = "DOWN"
    assert s.config["initialization"] == "UP"
    with pytest.raises(TypeError):
        s.config["initialization"] = "DOWN"
    with pytest.raises(TypeError):
        s.trace[0]["rule"] = "bad"
    with pytest.raises(TypeError):
        s.trace[0]["before"]["low"] = 99
    steps = [dict(t) for t in s.trace]
    steps[0]["before"] = dict(steps[0]["before"])
    detached = replace(s, trace=steps)
    steps[0]["before"]["low"] = 99
    assert detached.trace[0]["before"]["low"] == 1
    pending = derive([(2, 5), (3, 4)], "UNSET")
    with pytest.raises(TypeError):
        pending["raw_index"] = 2
    with pytest.raises(TypeError):
        pending["current"]["low"] = 99
    dual = derive([(2, 5), (3, 4)], "BOTH")
    with pytest.raises(TypeError):
        dual["requested_config"]["initialization"] = "UP"
    assert dual["main"].source_series is dual["comparison"].source_series
    assert dual["main"].config["initialization"] == "UP"
    assert dual["comparison"].config["initialization"] == "DOWN"
    for invalid in (
        {},
        {"initialization": "bad"},
        {"initialization": "UP", "extra": 1},
    ):
        with pytest.raises(ValueError):
            MergedKlineSeries.derive_from(source, invalid, "v")
