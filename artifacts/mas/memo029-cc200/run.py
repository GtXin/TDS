"""Isolated fixed-snapshot DP experiment; no production Bi changes."""

import hashlib
import itertools
import json
import time
from pathlib import Path
from typing import Any

from chanlab.algo.fenxing import FenxingSeries
from chanlab.algo.kline import KlineTSeries
from chanlab.algo.merged_kline import MergedKlineSeries

ROOT = Path(__file__).resolve().parent


def solve(edges: list[list[bool]]) -> list[int]:
    """Select earliest start, latest end, maximum-stroke prefix."""
    n = len(edges)
    start = next((p for p in range(n) if any(edges[p])), None)
    if start is None:
        return []
    best = [-1] * n
    prev = [-1] * n
    best[start] = 0
    for f in range(start + 1, n):
        for p in range(start, f):
            if best[p] >= 0 and edges[p][f] and best[p] + 1 > best[f]:
                best[f], prev[f] = best[p] + 1, p
    end = max(i for i in range(n) if best[i] >= 1)
    route = [end]
    while route[-1] != start:
        route.append(prev[route[-1]])
    return route[::-1]


def main() -> None:
    """Read preserved CC source, validate routes and export plots/evidence."""
    path = next(Path("samples/chan_table").glob("*chan_table_*.csv"))
    context = next(Path("samples/chan_table").glob("*context_*.csv"))
    hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (path, context)
    }
    raw = KlineTSeries.read_csv(path, context)
    merged = MergedKlineSeries.derive_from(raw, {"initialization": "UP"}, "memo015")
    series = FenxingSeries.derive_from(merged, {}, "memo019")
    fx = list(series[:200])
    centers = [p.source_start + 1 for p in fx]
    cutoff = fx[-1].source_stop
    reports: dict[str, Any] = {}
    for mode, gap in [("strong", 4), ("weak", 3)]:
        start_time = time.perf_counter()
        edges = [[False] * 200 for _ in fx]
        for p in range(200):
            for f in range(p + 1, 200):
                if fx[p].kind == fx[f].kind or centers[f] - centers[p] < gap:
                    continue
                t, b = (p, f) if fx[p].kind == "top" else (f, p)
                top, bottom = merged[centers[t]], merged[centers[b]]
                if top.high <= bottom.high or bottom.low >= top.low:
                    continue
                edges[p][f] = all(
                    k.high <= top.high and k.low >= bottom.low
                    for k in merged[centers[p] : centers[f] + 1]
                )
        route = solve(edges)
        evidence = []
        for p, f in itertools.pairwise(route):
            segment = merged[centers[p] : centers[f] + 1]
            maximum, minimum = max(k.high for k in segment), min(k.low for k in segment)
            t, b = (p, f) if fx[p].kind == "top" else (f, p)
            assert maximum == merged[centers[t]].high
            assert minimum == merged[centers[b]].low
            assert centers[f] - centers[p] >= gap
            assert fx[p].kind != fx[f].kind
            evidence.append(
                {
                    "pair": [p, f],
                    "gap": centers[f] - centers[p],
                    "max": maximum,
                    "min": minimum,
                }
            )
        # Independent exhaustive path enumeration for the first 12 real fractals.
        small = [row[:12] for row in edges[:12]]
        candidates = []
        for bits in itertools.product((False, True), repeat=12):
            r = [i for i, v in enumerate(bits) if v]
            if len(r) > 1 and all(small[p][f] for p, f in itertools.pairwise(r)):
                candidates.append(r)
        selected = solve(small)
        if candidates:
            optimum = min(candidates, key=lambda r: (r[0], -r[-1], -len(r)))
            assert (selected[0], selected[-1], len(selected)) == (
                optimum[0],
                optimum[-1],
                len(optimum),
            )
        else:
            assert not selected
        reports[mode] = {
            "route": route,
            "strokes": len(route) - 1 if route else 0,
            "elapsed_seconds": time.perf_counter() - start_time,
            "legal_edges": sum(map(sum, edges)),
            "stroke_checks": evidence,
            "first12_exhaustive_pass": True,
        }
        fig = series.plot(
            raw_stop=fx[-1].anchor_raw_index + 1,
            volume=False,
            title=f"Memo029 DP | first 200 fractals | {mode} | {len(route) - 1} strokes",
        )
        fig.add_scatter(
            x=[fx[i].anchor_raw_index for i in route],
            y=[fx[i].price for i in route],
            mode="lines+markers",
            name="DP selected Bi (provisional)",
            line={"color": "#2563eb", "width": 3},
            customdata=route,
            hovertemplate="FX%{customdata}<br>%{y}<extra></extra>",
            row=1,
            col=1,
        )
        fig.write_html(ROOT / f"bi200-{mode}.html", include_plotlyjs=True)
    assert all(
        hashlib.sha256(Path(p).read_bytes()).hexdigest() == h for p, h in hashes.items()
    )
    result = {
        "source_hashes": hashes,
        "raw_count": len(raw),
        "merged_count": len(merged),
        "all_fractals": len(series),
        "tested_fractals": 200,
        "last_complete_window_stop": cutoff,
        "reports": reports,
        "production_modified": False,
    }
    (ROOT / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                m: {k: v for k, v in r.items() if k != "stroke_checks"}
                for m, r in reports.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
