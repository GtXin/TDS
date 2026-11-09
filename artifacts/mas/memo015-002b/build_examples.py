"""Reproduce memo015002.b's synthetic arithmetic and figures, not a feature engine.

Run with an existing matplotlib environment and the TDS source on PYTHONPATH.
Outputs stay in this artifact folder; copying reviewed figures into the memo is
a separate documentation action. No production algorithm is implemented here.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from chanlab.algo.kline import Kline, KlineTSeries


OUT = Path(__file__).resolve().parent
MAIN = [(1, 3), (2, 4), (1, 5), (3, 4), (2, 6),
        (1, 5), (2, 4), (0, 6), (0, 4), (0, 5)]
STARTUP = [(2, 5), (3, 4), (2.5, 4.5), (3, 6)]
ORDER = [(0, 2), (1, 4), (2, 3), (0, 3.5)]
COLORS = {"up": "#2463b5", "down": "#c76427", None: "#66717e"}
NAMES = {"up": "向上", "down": "向下", None: "未定"}


def raw_series(bounds: list[tuple[float, float]]) -> KlineTSeries:
    """Bodies, timestamps and volume are explicitly synthetic display inputs."""
    bars = []
    for i, (low, high) in enumerate(bounds):
        a, b = low + (high - low) * 0.3, low + (high - low) * 0.7
        opening, close = (a, b) if i % 2 == 0 else (b, a)
        bars.append(Kline(
            symbol="SYNTHETIC", period="1m", source="memo015002b-synthetic",
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i),
            open=opening, high=high, low=low, close=close, volume=100 + i,
        ))
    return KlineTSeries(bars)


def replay(raw: KlineTSeries, policy: str | None = None) -> dict:
    """Finite example arithmetic under the memo tree; no confirmation semantics."""
    original = tuple(asdict(bar) for bar in raw)
    current = dict(low=raw[0].low, high=raw[0].high, direction=None, start=0, stop=1)
    saved, trace = [], []
    n = 1
    for i in range(1, len(raw)):
        assert current["stop"] == i and len(saved) == n - 1
        before = deepcopy(current)
        bar = raw[i]
        inclusion = ((current["high"] >= bar.high and current["low"] <= bar.low)
                     or (bar.high >= current["high"] and bar.low <= current["low"]))
        if inclusion:
            init_branch = None
            if current["direction"] is None:
                if policy is None:
                    return dict(records=None, pending_i=i, current=current, trace=trace)
                init_branch = {"up": "2.6.a", "down": "2.6.b", "outer": "2.6.d"}[policy]
                if policy != "outer":
                    current["direction"] = policy
            direction = current["direction"]
            if direction == "up":
                current["low"] = max(current["low"], bar.low)
                current["high"] = max(current["high"], bar.high)
                branch = "2.5.a"
            elif direction == "down":
                current["low"] = min(current["low"], bar.low)
                current["high"] = min(current["high"], bar.high)
                branch = "2.5.b"
            else:
                assert policy == "outer"
                current["low"] = min(current["low"], bar.low)
                current["high"] = max(current["high"], bar.high)
                branch = "2.6.d"
            current["stop"] = i + 1
            action = "absorb"
        else:
            init_branch = None
            if bar.high > current["high"] and bar.low > current["low"]:
                direction, branch = "up", "2.4.a"
            else:
                assert bar.high < current["high"] and bar.low < current["low"]
                direction, branch = "down", "2.4.b"
            saved.append(deepcopy(current))
            current = dict(low=bar.low, high=bar.high, direction=direction, start=i, stop=i + 1)
            n += 1
            action = "new"
        assert current["low"] <= current["high"] and current["stop"] == i + 1
        assert len(saved) == n - 1
        trace.append(dict(i=i, before=before, candidate=[bar.low, bar.high],
                          inclusion=inclusion, branch=branch, init_branch=init_branch,
                          action=action, after=deepcopy(current), next_i=i + 1, next_n=n))
    saved.append(deepcopy(current))
    assert len(saved) == n
    assert saved[0]["start"] == 0 and saved[-1]["stop"] == len(raw)
    assert all(a["stop"] == b["start"] for a, b in zip(saved, saved[1:]))
    assert tuple(asdict(bar) for bar in raw) == original
    return dict(records=saved, trace=trace, final_i=len(raw), final_n=n)


def compact(result: dict) -> list[tuple]:
    return [(r["low"], r["high"], r["direction"], r["start"], r["stop"])
            for r in result["records"]]


def axes_style(ax, size: int, title: str, bounds: tuple[float, float]) -> None:
    ax.set_title(title, loc="left", fontsize=12, pad=9, weight="bold")
    ax.set_xlim(-0.55, size - 0.45)
    ax.set_ylim(*bounds)
    ax.set_xticks(range(size))
    ax.set_ylabel("示例价格", fontsize=10)
    ax.grid(axis="y", color="#e1e7ee", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#b6c1cd")
    ax.tick_params(labelsize=10)


def candles(ax, raw: KlineTSeries) -> None:
    for i, bar in enumerate(raw):
        color = "#c84c47" if bar.close >= bar.open else "#238271"
        ax.vlines(i, bar.low, bar.high, color=color, linewidth=1.8)
        bottom, top = sorted((bar.open, bar.close))
        ax.add_patch(Rectangle((i - 0.18, bottom), 0.36, max(top - bottom, 0.015),
                               facecolor=color, edgecolor=color, zorder=3))
        ax.text(i, bar.high + 0.12, f"[{bar.low:g}, {bar.high:g}]",
                ha="center", va="bottom", fontsize=9)


def merged_intervals(ax, records: list[dict]) -> None:
    for k, record in enumerate(records, start=1):
        left, right = record["start"] - 0.32, record["stop"] - 0.68
        low, high = record["low"], record["high"]
        color = COLORS[record["direction"]]
        ax.axvspan(record["start"] - 0.5, record["stop"] - 0.5,
                   color=color, alpha=0.045, zorder=0)
        ax.add_patch(Rectangle((left, low), right - left, high - low,
                               facecolor=color, edgecolor="none", alpha=0.13))
        ax.hlines([low, high], left, right, color=color, linewidth=2)
        ax.vlines((left + right) / 2, low, high, color=color, linewidth=1.4)
        ax.text((left + right) / 2, high + 0.12,
                f"K{k}  {NAMES[record['direction']]}\n[{low:g}, {high:g}]",
                ha="center", va="bottom", color=color, fontsize=10, linespacing=1.3)
        ax.text((left + right) / 2, low - 0.13,
                f"来源 [{record['start']}, {record['stop']})",
                ha="center", va="top", color=color, fontsize=9)


def save_figure(fig, stem: str) -> None:
    folder = OUT / "figures"
    folder.mkdir(exist_ok=True)
    for suffix in ("png", "svg"):
        fig.savefig(folder / f"{stem}.{suffix}", dpi=160, facecolor="white")
    plt.close(fig)


def main() -> None:
    plt.rcParams.update({"font.family": "Arial Unicode MS", "font.size": 11,
                         "axes.unicode_minus": False, "svg.fonttype": "none"})
    main_raw, startup_raw = raw_series(MAIN), raw_series(STARTUP)
    main_result = replay(main_raw)
    starts = {policy: replay(startup_raw, policy) for policy in ("up", "down", "outer")}
    assert compact(main_result) == [(1, 3, None, 0, 1), (3, 6, "up", 1, 5), (0, 4, "down", 5, 10)]
    assert compact(starts["up"]) == [(3, 5, "up", 0, 2), (2.5, 4.5, "down", 2, 3), (3, 6, "up", 3, 4)]
    assert compact(starts["down"]) == [(2, 4, "down", 0, 2), (2.5, 4.5, "up", 2, 3), (3, 6, "up", 3, 4)]
    assert compact(starts["outer"]) == [(2, 5, None, 0, 3), (3, 6, "up", 3, 4)]
    order_result = replay(raw_series(ORDER))
    assert compact(order_result) == [(0, 2, None, 0, 1), (2, 4, "up", 1, 3), (0, 3.5, "down", 3, 4)]
    assert main_result["trace"][7]["before"]["low"] == main_raw[8].low
    assert main_result["trace"][7]["before"]["high"] == main_raw[8].high
    assert replay(startup_raw)["pending_i"] == 1
    assert compact(replay(raw_series([(2, 5)]))) == [(2, 5, None, 0, 1)]
    # Equally priced candles: direction is a policy label, not price movement evidence.
    for policy, direction in [("up", "up"), ("down", "down"), ("outer", None)]:
        assert compact(replay(raw_series([(4, 4), (4, 4)]), policy)) == [(4, 4, direction, 0, 2)]

    fig, axes = plt.subplots(2, 1, figsize=(11, 7.8), layout="constrained", sharex=True)
    fig.suptitle("主例：10根原始K线 → 3个合并区间", fontsize=17, weight="bold")
    axes_style(axes[0], 10, "原始K线｜仅高低点参与包含算法，开收盘与成交量为教学构造", (-0.7, 7.3))
    axes_style(axes[1], 10, "合并结果｜蓝：向上；橙：向下；灰：方向未定", (-0.7, 7.3))
    candles(axes[0], main_raw)
    merged_intervals(axes[1], main_result["records"])
    axes[1].set_xlabel("原始下标 i（两图共用同一横轴；合并区间宽度表示原始来源范围）", labelpad=8)
    save_figure(fig, "algorithm-main-kline")

    fig, axes = plt.subplots(4, 1, figsize=(10, 11.4), layout="constrained", sharex=True)
    fig.suptitle("起始包含：相同原始数据，不同初始化结果", fontsize=17, weight="bold")
    titles = ["原始K线｜价格区间按 [low, high] 标注；实体开收盘为教学构造",
              "向上初始化路径（2.6.a；也是2.6.c的主输出）",
              "向下初始化路径（2.6.b；也是2.6.c的比较路径）",
              "外边界初始化（2.6.d）：首段保持未定，后续新单元可定向"]
    for ax, title in zip(axes, titles):
        axes_style(ax, 4, title, (1.1, 7.4))
    candles(axes[0], startup_raw)
    for ax, policy in zip(axes[1:], ("up", "down", "outer")):
        merged_intervals(ax, starts[policy]["records"])
    axes[-1].set_xlabel("原始下标 i（各路径来源分界独立；竖线/上下边界只表示高低区间）", labelpad=8)
    save_figure(fig, "algorithm-initialization-kline")

    payload = dict(description="Synthetic worked arithmetic, not an implementation/CC-engine test",
                   main_raw=[asdict(bar) for bar in main_raw], main=main_result,
                   startup_raw=[asdict(bar) for bar in startup_raw], startup=starts,
                   sequential_counterexample=order_result)
    (OUT / "examples.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n")
    (OUT / "verification.json").write_text(json.dumps(dict(
        main_transitions=9, initialization_transitions=9, counterexample_transitions=3,
        source_coverage="passed", immutable_raw="passed", single_bar="passed",
        equal_one_price_bars="passed", unspecified_initialization="pending at i=1",
        production_algorithm_test=False, default_policy_selected=False,
        warning_metric_selected=False), ensure_ascii=False, indent=2) + "\n")
    print("Synthetic arithmetic/source invariants passed; two PNG/SVG figures generated.")


if __name__ == "__main__":
    main()
