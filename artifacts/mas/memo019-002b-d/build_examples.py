"""Finite design witnesses/figures for memo019, not a production Fenxing detector.

Requires existing matplotlib and TDS source on the Python path. The existing
MergedKlineSeries is executed only to verify example provenance. Fractal results
are a separate finite arithmetic model of the written definition/pseudocode.
"""

from datetime import datetime, timedelta, timezone
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from chanlab.algo.kline import Kline, KlineTSeries
from chanlab.algo.merged_kline import MergedKline, MergedKlineSeries

OUT = Path(__file__).resolve().parent
RAW = [(0, 3), (2, 5), (1, 6), (3, 6), (1, 4),
       (0, 3), (0, 2), (2, 5), (3, 6), (1, 4)]


def source(bounds):
    bars = []
    for i, (low, high) in enumerate(bounds):
        opening, close = low + .3 * (high - low), low + .7 * (high - low)
        if i % 2:
            opening, close = close, opening
        bars.append(Kline(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i),
            symbol="SYNTHETIC", period="1m", source="memo019002b-synthetic",
            open=opening, high=high, low=low, close=close, volume=100 + i,
        ))
    return KlineTSeries(tuple(bars))


def merged(bounds):
    result = MergedKlineSeries.derive_from(
        source(bounds), {"initialization": "UNSET"}, "memo015-example-check"
    )
    assert isinstance(result, MergedKlineSeries)
    return result


def normalize(config):
    if not isinstance(config, dict) or set(config) - {"anchor_tie"}:
        raise ValueError("invalid config")
    policy = config.get("anchor_tie", "FIRST")
    if policy not in ("FIRST", "LAST"):
        raise ValueError("invalid anchor policy")
    return {"anchor_tie": policy}


def direction(a, b):
    if b.low > a.low and b.high > a.high:
        return "up"
    if b.low < a.low and b.high < a.high:
        return "down"
    raise ValueError("inclusion or invalid adjacent relation")


def classify(a, b, c):
    left, right = direction(a, b), direction(b, c)
    if (left, right) == ("up", "down"):
        return "top", b.high, left, right
    if (left, right) == ("down", "up"):
        return "bottom", b.low, left, right
    return None, None, left, right


def resolve(raw, center, kind, price, policy):
    if kind not in ("top", "bottom") or policy not in ("FIRST", "LAST"):
        raise ValueError("invalid anchor request")
    count, first, last = 0, None, None
    for j in range(center.source_start, center.source_stop):
        value = raw[j].high if kind == "top" else raw[j].low
        if value == price:
            if first is None:
                first = j
            last, count = j, count + 1
    if not count:
        raise ValueError("no matching raw price")
    return (first if policy == "FIRST" else last), count, first, last


def scan(series, config):
    """Executed finite counterpart of the proposed loop; records remain plain data."""
    effective = normalize(config)
    records, trace, links = [], [], []
    if len(series) < 3:
        trace.append({"decision": "insufficient_window", "size": len(series)})
    i = 1
    while i < len(series) - 1:
        a, b, c = series[i - 1], series[i], series[i + 1]
        kind, price, left, right = classify(a, b, c)
        event = {"center": i, "left": left, "right": right,
                 "kind": kind, "price": price, "window": [i - 1, i + 2]}
        if kind is not None:
            anchor, count, first, last = resolve(
                series.source_series, b, kind, price, effective["anchor_tie"]
            )
            event["anchor_evidence"] = {
                "count": count, "first": first, "last": last,
                "selected": anchor, "policy": effective["anchor_tie"],
            }
            records.append({"id": len(records), "kind": kind, "price": price,
                            "anchor_raw_index": anchor, "source_start": i - 1,
                            "source_stop": i + 2, "status": "unconfirmed",
                            "confirmed_at": None})
            links.append([len(trace)])
        trace.append(event)
        i += 1
    return {"items": records, "config": effective, "trace": trace,
            "trace_by_point": links}


def oracle(series):
    expected = []
    for i in range(1, len(series) - 1):
        a, b, c = series[i - 1], series[i], series[i + 1]
        top = b.high > a.high and b.high > c.high and b.low > a.low and b.low > c.low
        bottom = b.high < a.high and b.high < c.high and b.low < a.low and b.low < c.low
        if top or bottom:
            expected.append((i, "top" if top else "bottom", b.high if top else b.low))
    return expected


def validate_model(series, result):
    """Finite counterpart of ordered output/trace validation in the pseudocode."""
    assert normalize(result["config"]) == result["config"]
    records, trace, links = result["items"], result["trace"], result["trace_by_point"]
    assert len(records) == len(links)
    ids = [r["id"] for r in records]
    assert all(type(value) is int and value >= 0 for value in ids)
    assert len(set(ids)) == len(ids)
    if len(series) < 3:
        assert records == [] and links == []
        assert trace == [{"decision": "insufficient_window", "size": len(series)}]
        return
    assert len(trace) == len(series) - 2
    p = 0
    for i in range(1, len(series) - 1):
        kind, price, left, right = classify(series[i - 1], series[i], series[i + 1])
        event = trace[i - 1]
        expected = {"center": i, "left": left, "right": right, "kind": kind,
                    "price": price, "window": [i - 1, i + 2]}
        assert all(event.get(k) == value for k, value in expected.items())
        if kind is None:
            assert "anchor_evidence" not in event
            continue
        assert p < len(records)
        point = records[p]
        anchor, count, first, last = resolve(
            series.source_series, series[i], kind, price, result["config"]["anchor_tie"]
        )
        assert point == {"id": point["id"], "kind": kind, "price": price,
                         "anchor_raw_index": anchor, "source_start": i - 1,
                         "source_stop": i + 2, "status": "unconfirmed",
                         "confirmed_at": None}
        assert links[p] == [i - 1]
        assert event["anchor_evidence"] == {
            "count": count, "first": first, "last": last,
            "selected": anchor, "policy": result["config"]["anchor_tie"],
        }
        p += 1
    assert p == len(records)


def expect_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


MAIN = merged(RAW)
groups = [(m.low, m.high, m.source_start, m.source_stop) for m in MAIN]
assert groups == [(0, 3, 0, 1), (3, 6, 1, 4), (1, 4, 4, 5),
                  (0, 2, 5, 7), (2, 5, 7, 8), (3, 6, 8, 9), (1, 4, 9, 10)]
FIRST, LAST = scan(MAIN, {}), scan(MAIN, {"anchor_tie": "LAST"})
validate_model(MAIN, FIRST)
validate_model(MAIN, LAST)
assert [x["anchor_raw_index"] for x in FIRST["items"]] == [2, 5, 8]
assert [x["anchor_raw_index"] for x in LAST["items"]] == [3, 6, 8]
assert [x["kind"] for x in FIRST["items"]] == ["top", "bottom", "top"]
assert [(x["source_start"], x["source_stop"]) for x in FIRST["items"]] == [(0, 3), (2, 5), (4, 7)]
assert FIRST["trace_by_point"] == [[0], [2], [4]]
assert len(FIRST["trace"]) == 5
assert FIRST == scan(MAIN, {"anchor_tie": "FIRST"})
for a, b in zip(FIRST["items"], LAST["items"]):
    assert {k: v for k, v in a.items() if k != "anchor_raw_index"} == {
        k: v for k, v in b.items() if k != "anchor_raw_index"}

for bounds in [[(1, 3)], [(1, 3), (2, 4)],
               [(1, 3), (2, 4), (3, 5)], [(3, 5), (2, 4), (1, 3)]]:
    r = scan(merged(bounds), {})
    assert r["items"] == [] and r["trace_by_point"] == [] and r["trace"]
    validate_model(merged(bounds), r)
expect_error(lambda: direction(MergedKline(0, 1, 5, None, 0, 1),
                               MergedKline(1, 3, 5, "up", 1, 2)))
expect_error(lambda: resolve(MAIN.source_series, MAIN[1], "top", 7, "FIRST"))
expect_error(lambda: normalize({"anchor_tie": "UNSET"}))
expect_error(lambda: normalize({"unexpected": "FIRST"}))

REVISED_RAW = RAW[:-1] + [(4, 7)]
REVISED, APPENDED = merged(REVISED_RAW), merged(REVISED_RAW + [(2, 5)])
REVISED_FX, APPENDED_FX = scan(REVISED, {}), scan(APPENDED, {})
validate_model(REVISED, REVISED_FX)
validate_model(APPENDED, APPENDED_FX)
assert len(REVISED_FX["items"]) == 2
assert [(x["source_start"] + 1, x["price"], x["anchor_raw_index"])
        for x in APPENDED_FX["items"]] == [(1, 6, 2), (3, 0, 5), (6, 7, 9)]

corruptions = []
bad = deepcopy(FIRST); bad["trace"].pop(); corruptions.append(bad)
bad = deepcopy(FIRST); bad["trace"][1] = deepcopy(bad["trace"][0]); corruptions.append(bad)
bad = deepcopy(FIRST); bad["trace"][0]["anchor_evidence"]["count"] = 99; corruptions.append(bad)
bad = deepcopy(FIRST); bad["trace_by_point"][0] = [1]; corruptions.append(bad)
bad = deepcopy(FIRST); bad["items"].pop(); bad["trace_by_point"].pop(); corruptions.append(bad)
bad = deepcopy(FIRST); bad["items"][0]["anchor_raw_index"] = 3; corruptions.append(bad)
bad = deepcopy(FIRST); bad["items"][1]["id"] = bad["items"][0]["id"]; corruptions.append(bad)
bad = deepcopy(FIRST); bad["trace"].append(deepcopy(bad["trace"][0])); corruptions.append(bad)
for bad in corruptions:
    try:
        validate_model(MAIN, bad)
    except AssertionError:
        continue
    raise AssertionError("corrupt result/trace accepted")

# Independent bounded enumeration checks the reversal criterion against all four
# strict inequalities; raw=merged singleton groups provide valid anchor witnesses.
pool = [(lo, hi) for lo in range(4) for hi in range(lo, 4)]
sequence_count, window_count = 0, 0
for n in range(1, 6):
    for bounds in product(pool, repeat=n):
        if any(not ((b[0] > a[0] and b[1] > a[1]) or
                    (b[0] < a[0] and b[1] < a[1])) for a, b in zip(bounds, bounds[1:])):
            continue
        bars = tuple(MergedKline(i, lo, hi, None, i, i + 1)
                     for i, (lo, hi) in enumerate(bounds))
        expected = []
        for i in range(1, n - 1):
            result = classify(bars[i - 1], bars[i], bars[i + 1])
            a, b, c = bounds[i - 1 : i + 2]
            top = b[0] > max(a[0], c[0]) and b[1] > max(a[1], c[1])
            bottom = b[0] < min(a[0], c[0]) and b[1] < min(a[1], c[1])
            assert result[0] == ("top" if top else "bottom" if bottom else None)
            if result[0]:
                expected.append(i)
        assert len(expected) <= max(n - 2, 0)
        sequence_count += 1
        window_count += max(n - 2, 0)


def candles(ax, raw):
    for i, bar in enumerate(raw):
        color = "#16a34a" if bar.close >= bar.open else "#dc2626"
        ax.vlines(i, bar.low, bar.high, color=color, linewidth=1.7, zorder=3)
        ax.add_patch(Rectangle((i - .22, min(bar.open, bar.close)), .44,
                               abs(bar.close - bar.open), facecolor=color,
                               edgecolor=color, zorder=4))
    ax.set_xticks(range(len(raw)), [f"R{i}" for i in range(len(raw))])
    ax.set_xlim(-.65, len(raw) - .35)
    ax.set_ylim(-1.8, 8.8)
    ax.set_ylabel("Price")
    ax.grid(axis="y", color="#e2e8f0", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)


def anchors(ax, result):
    for item in result["items"]:
        x, y = item["anchor_raw_index"], item["price"]
        is_top = item["kind"] == "top"
        color = "#7c3aed" if is_top else "#0369a1"
        ax.scatter(x, y, marker="v" if is_top else "^", color=color,
                   s=80, edgecolors="white", linewidth=.7, zorder=8)
        ax.annotate(f"FX{item['id']} {item['kind']}={y:g}", (x, y),
                    xytext=(0, 22 if is_top else -18), textcoords="offset points",
                    ha="center", fontsize=10, color=color,
                    arrowprops={"arrowstyle": "-", "color": color, "lw": .8})


fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
candles(axes[0], MAIN.source_series)
axes[0].set_title("10 original bars: synthetic OHLC; FIRST anchors at R2, R5, R8", loc="left")
anchors(axes[0], FIRST)
for i, bar in enumerate(MAIN):
    color = {"up": "#16a34a", "down": "#dc2626", None: "#64748b"}[bar.direction]
    width = bar.source_stop - bar.source_start - .18
    axes[1].add_patch(Rectangle((bar.source_start - .41, bar.low), width,
                                bar.high - bar.low, facecolor=color + "20",
                                edgecolor=color, linewidth=1.6, zorder=2))
    axes[1].vlines(bar.source_start, bar.low, bar.high, color=color, linewidth=2.2)
    axes[1].text(bar.source_start, bar.high + .15, f"M{i}", fontsize=10,
                 color=color, ha="center")
candles(axes[1], [])
axes[1].set_xticks(range(10), [f"R{i}" for i in range(10)])
axes[1].set_xlim(-.65, 9.65)
anchors(axes[1], FIRST)
axes[1].set_title("7 merged intervals -> 3 geometric fractals (windows may overlap)", loc="left")
axes[1].set_xlabel("Original source position; merged vertical lines remain at the first member")
fig.suptitle("Memo019 worked example - raw members, merged windows and actual price anchors", fontsize=14)
fig.text(.5, .018, "Teaching construction only. Candle bodies do not enter the rule; merged blocks have no invented open/close.", ha="center", fontsize=9, color="#475569")
fig.subplots_adjust(hspace=.3, top=.89, bottom=.1, left=.07, right=.98)
fig.savefig(OUT / "algorithm-main-fractals.png", dpi=150)
plt.close(fig)

fig, axes = plt.subplots(3, 1, figsize=(13, 10.5), sharex=True)
for ax, bars, result, title in zip(
    axes, [MAIN.source_series, REVISED.source_series, APPENDED.source_series],
    [FIRST, REVISED_FX, APPENDED_FX],
    ["Snapshot A: R9=[1,4]; top at merged center M5 / raw anchor R8",
     "Snapshot B: replace R9 with [4,7]; old top disappears, R9 has no right neighbor",
     "Snapshot C: append R10=[2,5]; new top at merged center M6 / raw anchor R9"],
):
    candles(ax, bars)
    anchors(ax, result)
    ax.set_title(title, loc="left", fontsize=11)
axes[-1].set_xticks(range(11), [f"R{i}" for i in range(11)])
axes[-1].set_xlim(-.65, 10.65)
axes[-1].set_xlabel("Original raw position; every row is a different complete source snapshot")
fig.suptitle("Tail revision and right-neighbor evidence - geometry is recomputed per snapshot", fontsize=14)
fig.text(.5, .016, "Result IDs are scoped to each snapshot; all records remain unconfirmed with confirmed_at=None.", ha="center", fontsize=9, color="#475569")
fig.subplots_adjust(hspace=.42, top=.92, bottom=.07, left=.07, right=.98)
fig.savefig(OUT / "algorithm-tail-revision.png", dpi=150)
plt.close(fig)

payload = {
    "scope": "Actual upstream merged calculation; independent finite fractal arithmetic, not production detection or CC execution",
    "raw_bounds": RAW,
    "merged_groups": groups,
    "default_first": FIRST,
    "explicit_last": LAST,
    "revised_bounds": REVISED_RAW,
    "revised_fractals": REVISED_FX,
    "appended_bounds": REVISED_RAW + [(2, 5)],
    "appended_fractals": APPENDED_FX,
    "finite_model_sequences": sequence_count,
    "finite_model_windows": window_count,
    "output_trace_corruption_probes_rejected": len(corruptions),
    "edge_cases": "short/monotone/invalid equal boundary/no raw match/invalid config pass",
    "figure_files": ["algorithm-main-fractals.png", "algorithm-tail-revision.png"],
}
(OUT / "examples.json").write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({"raw": len(RAW), "merged": len(MAIN),
                  "fractals": len(FIRST["items"]), "first_anchors": [2, 5, 8],
                  "last_anchors": [3, 6, 8], "finite_sequences": sequence_count,
                  "finite_windows": window_count}, indent=2))
