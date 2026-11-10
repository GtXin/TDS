"""Integration, persistence and plotting checks for memo027."""

import builtins
import json
from dataclasses import replace

import pytest
from test_fenxing import derive, example, merged

from chanlab.algo.chan_table import ChanTable
from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.merged_kline import MergedKlineSeries
from chanlab.data import fenxing_table as fx
from chanlab.data.feature_table import contexts


def test_registration_roundtrip_and_preservation(tmp_path):
    s = derive()
    m = s.source_series
    raw = m.source_series
    table = ChanTable.from_source_series(raw, {"snapshot": "synthetic"})
    registered = m.to_chan_table(table, "mk")
    out = s.to_chan_table(registered, "fx")
    assert out.feature_series["mk"] is m and out.feature_series["fx"] is s
    assert FenxingSeries.from_chan_table(out, "fx") is s
    assert MergedKlineSeries.from_chan_table(out, "mk") is m
    assert out.source_series is raw and table[0]["fx_ids"] == "NA"
    assert out.memberships["fx"][4] == (0, 1) and out.anchor_ids["fx"][2] == (0,)
    assert out.start_ids["fx"][0] == (0,) and out.end_ids["fx"][4] == (0,)
    assert out[2]["fx_kind"] == "top" and out[1]["fx_kind"] == "NA"
    assert all(tuple(row) == tuple(table[i]) for i, row in enumerate(out))
    assert [dict(row) for row in out] == [
        dict(row) for row in s.to_chan_table(out, "fx")
    ]
    alternate = derive(m, {"anchor_tie": "LAST"})
    out2 = alternate.to_chan_table(out, "last")
    assert out2.anchor_ids["last"][3] == (0,) and out2[2]["fx_kind"] == "top"
    assert out2.feature_series["fx"] is s
    # Register another merged result after fractals: all existing classes survive.
    other = replace(m, rule_tree_ref="another-version")
    out2 = other.to_chan_table(out2, "other")
    assert out2.feature_series["last"] is alternate
    data, context = tmp_path / "table.csv", tmp_path / "context.csv"
    out2.write_csv(data, context)
    restored = ChanTable.read_csv(data, context)
    assert restored.rows == out2.rows
    restored_fx = FenxingSeries.from_chan_table(restored, "fx")
    assert restored_fx.source_series is restored.feature_series["mk"]
    assert restored_fx.items == s.items and restored_fx.trace == s.trace
    assert restored.context["snapshot"] == "synthetic"
    with pytest.raises(ValueError):
        out.write_csv(data)


def test_empty_and_auto_upstream():
    s = derive(merged([(1, 3), (2, 4)]))
    t = s.to_chan_table(
        ChanTable.from_source_series(s.source_series.source_series), "fx"
    )
    assert t.feature_series["fx:source"] is s.source_series
    assert t[0]["fx_ids"] == "[]" and t[0]["fx_kind"] == "NA"
    frame = s.to_dataframe()
    assert len(frame) == 0 and list(frame) == [
        "id",
        "kind",
        "price",
        "anchor_raw_index",
        "source_start",
        "source_stop",
        "status",
        "confirmed_at",
    ]
    assert str(frame["confirmed_at"].dtype) == "datetime64[ns, UTC]"
    assert frame.attrs["config"] == {"anchor_tie": "FIRST"}


def test_dataframe_detached():
    s = derive()
    frame = s.to_dataframe()
    assert list(frame["id"]) == [0, 1, 2] and frame.attrs["source_digest"]
    frame.loc[0, "price"] = 99
    assert s[0].price == 6


@pytest.mark.parametrize(
    "mode",
    [
        "key",
        "collision",
        "source",
        "upstreamcollision",
        "class",
        "projection",
        "context",
        "trace",
        "upstreamversion",
        "payload",
        "unregistered",
    ],
)
def test_invalid_integration(mode):
    s = derive()
    raw = s.source_series.source_series
    t = ChanTable.from_source_series(raw)
    out = s.to_chan_table(t, "fx")
    with pytest.raises((ValueError, KeyError)):
        if mode == "key":
            s.to_chan_table(t, " ")
        if mode == "collision":
            derive(s.source_series).to_chan_table(out, "fx")
        if mode == "source":
            s.to_chan_table(ChanTable.from_source_series(example().source_series), "fx")
        if mode == "upstreamcollision":
            s.to_chan_table(
                replace(s.source_series, rule_tree_ref="other").to_chan_table(
                    t, "fx:source"
                ),
                "fx",
            )
        if mode == "class":
            FenxingSeries.from_chan_table(out, "fx:source")
        if mode == "projection":
            rows = [dict(r) for r in out]
            rows[2]["fx_kind"] = "bottom"
            ChanTable(rows, out.context)
        if mode == "context":
            context = dict(out.context)
            context[fx.FEATURE_CONTEXT] = "{}"
            ChanTable(out.rows, context)
        if mode in ("trace", "upstreamversion"):
            payload = json.loads(out.context[fx.FEATURE_CONTEXT])
            d = payload["fx"]
            d["trace"][0]["center"] = 99 if mode == "trace" else d["trace"][0]["center"]
            if mode == "upstreamversion":
                d["upstream_version"] = "bad"
            d["result_version"] = fx.fingerprint(
                {k: v for k, v in d.items() if k != "result_version"}
            )
            context = dict(out.context)
            context[fx.FEATURE_CONTEXT] = json.dumps(payload)
            ChanTable(out.rows, context)
        if mode == "payload":
            fx.decode_features("bad json", {})
        if mode == "unregistered":
            fx.encode_features({"fx": s})


@pytest.mark.parametrize("market", ["US", "China"])
@pytest.mark.parametrize("gaps", [False, True])
def test_plot_anchors_and_html(market, gaps, tmp_path):
    s = derive()
    fig = s.plot(raw_start=1, raw_stop=9, market=market, show_gaps=gaps, volume=True)
    points = [
        trace for trace in fig.data if trace.name in ("top fractal", "bottom fractal")
    ]
    assert sum(len(t.x) for t in points) == 3
    raw = s.source_series.source_series
    for t in points:
        up, down = ("#16a34a", "#dc2626") if market == "US" else ("#dc2626", "#16a34a")
        assert t.marker.color == (down if t.name == "top fractal" else up)
        for x, y, custom in zip(t.x, t.y, t.customdata):
            p = s.get_by_id(custom[0])
            assert y == p.price
            assert x == (
                raw[p.anchor_raw_index].timestamp if gaps else p.anchor_raw_index - 1
            )
            assert custom[5] == "unconfirmed"
    fig.write_html(tmp_path / "plot.html", include_plotlyjs=True)
    assert (tmp_path / "plot.html").stat().st_size > 1000
    assert len(s.plot(volume=False).data) > 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"raw_start": 5, "raw_stop": 5},
        {"market": "bad"},
        {"show_gaps": "yes"},
        {"volume": 1},
    ],
)
def test_invalid_plot(kwargs):
    with pytest.raises(ValueError):
        derive().plot(**kwargs)


@pytest.mark.parametrize("module", ["pandas", "plotly"])
def test_missing_optional_dependency(module, monkeypatch):
    original = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == module or name.startswith(module + "."):
            raise ImportError("blocked")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(ImportError):
        derive().to_dataframe() if module == "pandas" else derive().plot()


def test_reject_persisted_version_and_key_tamper():
    s = derive()
    features = {"up": s.source_series, "fx": s}
    payload = json.loads(fx.encode_features(features))
    payload["fx"]["result_version"] = "wrong"
    with pytest.raises(ValueError):
        fx.decode_features(json.dumps(payload), {"up": s.source_series})
    payload = json.loads(fx.encode_features(features))
    payload["up"] = payload.pop("fx")
    with pytest.raises(ValueError):
        fx.decode_features(json.dumps(payload), {"up": s.source_series})
    assert len(contexts(features)) == 2
