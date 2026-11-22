"""Domain/source integrity, persistence corruption and honest geometry display."""

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
from test_xianduan import sample

from chanlab.algo.chan_table import ChanTable
from chanlab.algo.xianduan import XianduanSeries
from chanlab.algo.zhongshu import ZhongshuSeries
from chanlab.data import zhongshu_table as adapter
from chanlab.data.fenxing_table import fingerprint


@pytest.fixture(scope="module")
def centers():
    return ZhongshuSeries.derive_from(XianduanSeries.derive_from(sample()))


@pytest.fixture(scope="module")
def real():
    mode = "bi-weak_xd-weak"
    root = Path("artifacts/mas/xianduan-family/run031/full") / mode
    table = ChanTable.read_csv(root / "table.csv", root / "context.csv")
    return ZhongshuSeries.derive_from(table.feature_series[mode])


def raw(s):
    return s.source_series.source_series.source_series.source_series.source_series


def test_access_and_freeze(centers):
    s = centers
    assert s[:] == tuple(s) and s[-1] is s.items[-1]
    assert s.get_by_id(0) is s[0]
    assert s.explain(0)["source_ids"] == tuple(
        s.source_series[k].id for k in s[0].member_indices
    )
    assert s.unresolved_ranges() == s.unformed
    detached = s.to_dataframe()
    assert detached.shape == (len(s), 10)
    assert detached.attrs["source_fingerprint"] == adapter.source_fingerprint(
        s.source_series
    )
    with pytest.raises(FrozenInstanceError):
        s[0].id = 10
    with pytest.raises(TypeError):
        s.config["x"] = 1
    with pytest.raises(TypeError):
        s.explain(0)["x"] = 1
    with pytest.raises(KeyError):
        s.get_by_id(999)
    with pytest.raises(ValueError):
        s.get_by_id(True)
    renumbered = replace(s, items=tuple(replace(z, id=z.id + 50) for z in s))
    assert renumbered.get_by_id(50) == renumbered[0]


@pytest.mark.parametrize("config", [False, {"mode": "bad"}, {"zero_height": False}])
def test_bad_config(centers, config):
    with pytest.raises(ValueError):
        ZhongshuSeries.derive_from(centers.source_series, config=config)


@pytest.mark.parametrize(
    "changes",
    [
        {"source_series": None},
        {"level": ""},
        {"rule_tree_ref": ""},
        {"trace": ()},
        {"trace_by_point": ()},
        {"unformed": ()},
        {"items": ()},
    ],
)
def test_bad_series(centers, changes):
    with pytest.raises(ValueError):
        replace(centers, **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"id": True},
        {"id": -1},
        {"level": ""},
        {"lower": float("nan")},
        {"upper": float("inf")},
        {"lower": True},
        {"lower": 1000},
        {"member_indices": (1, 2)},
        {"member_indices": (1, 3, 4)},
        {"start_raw_index": 999},
        {"status": "bad"},
        {"geometry": None},
    ],
)
def test_bad_record(centers, changes):
    with pytest.raises(ValueError):
        replace(centers[0], **changes)


def test_source_corruption_and_completeness(real):
    for changes in (
        {"items": tuple(reversed(real.items))},
        {"items": real.items[:-1]},
        {"items": (real[0],) * len(real)},
        {"unformed": ((0, 1),)},
    ):
        with pytest.raises(ValueError):
            replace(real, **changes)
    z = real[1]
    for changes in (
        {"start_raw_index": z.start_raw_index + 1},
        {"geometry": replace(z.geometry, formation_at=raw(real)[0].timestamp)},
    ):
        with pytest.raises(ValueError):
            replace(real, items=(real[0], replace(z, **changes)) + real.items[2:])


def test_tables_roundtrip_and_scoping(centers, tmp_path):
    s = centers
    base = ChanTable.from_source_series(raw(s), {})
    table = s.to_chan_table(base, "zs")
    other = replace(s, items=tuple(replace(z, id=z.id + 20) for z in s))
    table = other.to_chan_table(table, "other")
    assert ZhongshuSeries.from_chan_table(table, "zs") is s
    assert table.memberships["zs"] != table.memberships["other"]
    assert all(not ids for ids in table.end_ids["zs"])  # open has no terminal marker
    assert all(
        row["zs_lower"] == "NA"
        for i, row in enumerate(table)
        if i != s[0].start_raw_index
    )
    table.write_csv(tmp_path / "table.csv", tmp_path / "context.csv")
    restored = ChanTable.read_csv(tmp_path / "table.csv", tmp_path / "context.csv")
    assert restored.feature_series["zs"].items == s.items
    assert (
        restored.feature_series["zs"].source_series
        is restored.feature_series["other"].source_series
    )
    with pytest.raises(ValueError):
        table.write_csv(tmp_path / "bad.csv")
    with pytest.raises(ValueError):
        ZhongshuSeries.from_chan_table(table, "zs:source")
    with pytest.raises(ValueError):
        s.to_chan_table(table, "other")
    with pytest.raises(ValueError):
        s.to_chan_table(base, "")
    with pytest.raises(ValueError):
        s.to_chan_table(
            ChanTable.read_csv(tmp_path / "table.csv", tmp_path / "context.csv"), "new"
        )


@pytest.mark.parametrize(
    "mutation",
    ["version", "class", "upstream", "digest", "record", "trace", "geometry", "key"],
)
def test_corrupt_persistence(centers, mutation):
    s = centers
    table = s.to_chan_table(ChanTable.from_source_series(raw(s), {}), "zs")
    upstream = {k: v for k, v in table.feature_series.items() if k != "zs"}
    payload = json.loads(adapter.encode_features(table.feature_series))
    d = payload["zs"]
    if mutation == "version":
        d["result_version"] = "bad"
    else:
        if mutation == "class":
            d["class_name"] = "bad"
        if mutation == "upstream":
            d["upstream_key"] = "zs:source:source"
        if mutation == "digest":
            d["upstream_digest"] = "bad"
        if mutation == "record":
            d["records"][0]["start_raw_index"] += 1
        if mutation == "trace":
            d["trace"] = []
        if mutation == "geometry":
            d["records"][0]["geometry"]["left"]["time"] = "bad"
        if mutation == "key":
            payload[""] = payload.pop("zs")
        check = dict(d)
        check.pop("result_version")
        d["result_version"] = fingerprint(check)
    with pytest.raises(ValueError):
        adapter.decode_features(json.dumps(payload), upstream)
    with pytest.raises(ValueError):
        adapter.encode_features({"zs": s})


def test_empty_and_wrong_source(centers):
    with pytest.raises(ValueError):
        ZhongshuSeries.derive_from(None)
    # A valid empty selected source is possible only with its own matching trace/tail.
    from test_bi import source as fx_source

    from chanlab.algo.bi import BiSeries

    empty = ZhongshuSeries.derive_from(
        XianduanSeries.derive_from(BiSeries.derive_from(fx_source(), {}, "memo029"))
    )
    assert not empty and empty.to_dataframe().shape == (0, 10)


def test_native_plot(centers, real):
    s = centers
    fig = s.plot(volume=False)
    assert any(x.name.startswith("ZS") for x in fig.layout.shapes)
    assert all(
        x.type == "line"
        for x in fig.layout.shapes
        if x.name and x.name.startswith("ZS")
    )
    for opts in (
        {"show_gaps": True},
        {"raw_start": -100},
        {"raw_start": 100, "raw_stop": 200},
    ):
        assert s.plot(volume=False, **opts).data
    for opts in ({"raw_start": False}, {"raw_start": 10, "raw_stop": 10}):
        with pytest.raises(ValueError):
            s.plot(volume=False, **opts)
    chart = real.plot(raw_start=0, raw_stop=500, volume=False)
    assert any("left_crossing_missing" in a.text for a in chart.layout.annotations)
    chart = real.plot(raw_start=1000, raw_stop=2000, volume=False)
    assert any(x.type == "rect" for x in chart.layout.shapes)


@pytest.mark.parametrize(
    "kind", ["source", "item", "decision", "trace_bool", "range_bool", "level"]
)
def test_series_type_guards(centers, kind):
    changes = {
        "source": {"source_series": None},
        "item": {"items": (None,)},
        "decision": {"trace": (None,)},
        "trace_bool": {"trace_by_point": ((True,),)},
        "range_bool": {"unformed": ((False, 1),)},
        "level": {"level": None},
    }[kind]
    with pytest.raises(ValueError):
        replace(centers, **changes)


@pytest.mark.parametrize(
    "kind",
    [
        "start",
        "confirmation",
        "time",
        "diagnostic",
        "fraction",
        "coordinate",
        "segment_id",
        "cross_time",
    ],
)
def test_geometry_local_guards(real, kind):
    z = real[1]
    g = z.geometry
    if kind == "start":
        g = replace(g, start=True)
    elif kind == "confirmation":
        g = replace(g, confirmation=g.terminal + 2)
    elif kind == "time":
        g = replace(g, formation_at=g.formation_at.replace(tzinfo=None))
    elif kind == "diagnostic":
        g = replace(g, diagnostics=("wrong",))
    elif kind == "fraction":
        g = replace(g, left=replace(g.left, fraction=2))
    elif kind == "coordinate":
        g = replace(g, left=replace(g.left, x=float("nan")))
    elif kind == "segment_id":
        g = replace(g, left=replace(g.left, segment_id=True))
    else:
        g = replace(g, left=replace(g.left, time=g.left.time.replace(tzinfo=None)))
    with pytest.raises(ValueError):
        replace(z, geometry=g)


def test_closed_confirmation_consistency(real):
    z = real[1]
    from datetime import timedelta

    for changes in (
        {"confirmed_at": None},
        {"confirmed_at": z.confirmed_at.replace(tzinfo=None)},
        {
            "geometry": replace(
                z.geometry, confirmed_at=z.geometry.formation_at - timedelta(seconds=1)
            ),
            "confirmed_at": z.geometry.formation_at - timedelta(seconds=1),
        },
    ):
        with pytest.raises(ValueError):
            replace(z, **changes)
