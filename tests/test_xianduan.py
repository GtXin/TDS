"""XD030-E default modes, source binding, corruption and persistence checks."""

from dataclasses import replace
import pytest
from test_bi import source
from chanlab.algo.bi import BiSeries
from chanlab.algo.xianduan import XianduanSeries, recognize
from chanlab.algo.chan_table import ChanTable


def sample():
    values = []
    # Multi-scale oscillation yields enough legal source strokes and segments.
    import random

    rng = random.Random(31)
    levels = [0.0]
    for k in range(60):
        levels.append(levels[-1] + (1 if k % 2 == 0 else -1) * rng.randint(5, 30))
    for level in levels:
        if not values:
            values.append(level)
            continue
        start = values[-1]
        values.extend(start + (level - start) * k / 8 for k in range(1, 9))
    return BiSeries.derive_from(source(values), {}, "029")


def test_defaults_and_snapshot():
    bi = sample()
    assert bi.config["distance_mode"] == "weak"
    s = XianduanSeries.derive_from(bi)
    assert s.config["xd_mode"] == "weak"
    with pytest.raises(ValueError):
        XianduanSeries.derive_from(bi, False)
    with pytest.raises(ValueError):
        XianduanSeries.derive_from(None)
    with pytest.raises(ValueError):
        replace(s, rule_tree_ref=None)
    with pytest.raises(ValueError):
        replace(s[0], confirmed_at=123)
    assert len(s) > 0
    assert s.source_series is bi and tuple(s) == s[:]
    assert s.get_by_id(0) is s[0]
    assert s.unresolved_ranges()
    with pytest.raises(ValueError):
        s.get_by_id(True)
    assert s.explain(0)["bi_distance_mode"] == "weak"
    with pytest.raises(KeyError):
        s.get_by_id(999)
    with pytest.raises(ValueError):
        replace(s, trace=())
    with pytest.raises(ValueError):
        replace(s, tail=())
    with pytest.raises(ValueError):
        replace(s[0], confirmed_at=None)
    with pytest.raises(ValueError):
        replace(s[0], status="unconfirmed")
    with pytest.raises(ValueError):
        XianduanSeries.derive_from(bi, {"xd_mode": "bad"})


def test_tables(tmp_path):
    s = XianduanSeries.derive_from(sample())
    raw = s.source_series.source_series.source_series.source_series
    table = s.to_chan_table(ChanTable.from_source_series(raw, {}), "xd:weak")
    assert XianduanSeries.from_chan_table(table, "xd:weak") is s
    table.write_csv(tmp_path / "data.csv", tmp_path / "context.csv")
    restored = ChanTable.read_csv(tmp_path / "data.csv", tmp_path / "context.csv")
    assert restored.feature_series["xd:weak"].items == s.items
    assert s.to_dataframe().shape[0] == len(s)
    assert any(t.name.startswith("XD") for t in s.plot(volume=False).data)


@pytest.mark.parametrize("p", [[], [1], [1, 2], [1, 2, 1]])
def test_empty(p):
    assert recognize(p)["count"] == 0


@pytest.mark.parametrize("p", [[1, 1], [1, float("nan")], [1, 2, 3]])
def test_invalid(p):
    with pytest.raises(ValueError):
        recognize(p)


def test_known_direct_and_mirror():
    p = [10, 18, 14, 20, 12, 17, 9]
    a = recognize(p)
    b = recognize([-x for x in p])
    assert a["confirmed"] == b["confirmed"] == [(0, 3)]
    assert a["tail"] == [(3, 6)]


def test_persistence_rejects_corruption_and_wrong_upstream():
    import json
    from chanlab.data import xianduan_table
    from chanlab.data.fenxing_table import fingerprint

    s = XianduanSeries.derive_from(sample())
    with pytest.raises(ValueError):
        xianduan_table.encode_features({"xd": s})
    upstream = {"bi": s.source_series}
    payload = json.loads(xianduan_table.encode_features({**upstream, "xd": s}))
    for mutation in ("version", "upstream", "class", "record"):
        data = json.loads(json.dumps(payload))
        if mutation == "version":
            data["xd"]["result_version"] = "bad"
        else:
            if mutation == "upstream":
                data["xd"]["upstream_digest"] = "bad"
            elif mutation == "class":
                data["xd"]["class_name"] = "bad"
            else:
                data["xd"]["records"][0]["end_price"] += 100
            check = dict(data["xd"])
            check.pop("result_version")
            data["xd"]["result_version"] = fingerprint(check)
        with pytest.raises(ValueError):
            xianduan_table.decode_features(json.dumps(data), upstream)
    with pytest.raises(ValueError):
        XianduanSeries.from_chan_table(
            s.to_chan_table(
                ChanTable.from_source_series(
                    s.source_series.source_series.source_series.source_series, {}
                ),
                "xd",
            ),
            "xd:source",
        )


def test_record_and_series_validation():
    s = XianduanSeries.derive_from(sample())
    for changes in (
        {"source_stop": s[0].source_start + 2},
        {"direction": "bad"},
        {"id": -1},
    ):
        with pytest.raises(ValueError):
            replace(s[0], **changes)
    for changes in (
        {"rule_tree_ref": ""},
        {"items": (s[0], s[0])},
        {"tail": ((0, 3),)},
        {"trace_by_point": ((9,),)},
    ):
        with pytest.raises(ValueError):
            replace(s, **changes)
    trace = [dict(x) for x in s.trace]
    trace[0]["T"] = (999, 1002)
    with pytest.raises(ValueError):
        replace(s, trace=tuple(trace))


def test_mode_shape_boundaries():
    from chanlab.algo._xianduan_events import scanner

    for p, strong in [
        ([10, 18, 14, 20], True),
        ([10, 18, 14, 18], False),
        ([10, 18, 14, 17], False),
    ]:
        assert scanner(p, "weak")[1](0, 3)
        assert scanner(p, "strong")[1](0, 3) == strong
        assert scanner([-x for x in p], "strong")[1](0, 3) == strong
    assert not scanner([1, 2, 1], "weak")[1](0, 2)
    assert not scanner([1, 2, 1], "weak")[1](-1, 3)


def test_shape_only_candidate_remains_unconfirmed():
    r = recognize([10, 18, 14, 20])
    assert r["count"] == 0 and r["pending_candidates"] == [(0, 3)]
    s = XianduanSeries.derive_from(sample())
    assert isinstance(s.pending_candidates(), tuple)
