"""Generate and audit complete atlases using the public ZhongshuSeries.plot API."""

import html
import json

from plotly.offline import get_plotlyjs

from chanlab.algo.chan_table import ChanTable
from chanlab.algo.zhongshu import ZhongshuSeries
from experiments.zhongshu033.validate import MODES, OUT, save


def audit(s, fig, start, stop):
    raw = s.source_series.source_series.source_series.source_series.source_series
    candle = next(t for t in fig.data if t.type == "candlestick")
    assert list(candle.x) == list(range(stop - start))
    for field in ("open", "high", "low", "close"):
        assert list(getattr(candle, field)) == [
            getattr(raw[i], field) for i in range(start, stop)
        ]
    pens = s.source_series.source_series
    fx = pens.source_series
    for kind in ("top", "bottom"):
        trace = next(t for t in fig.data if t.name == kind + " fractal")
        expected = [
            f for f in fx if f.kind == kind and start <= f.anchor_raw_index < stop
        ]
        assert list(trace.x) == [f.anchor_raw_index - start for f in expected]
        assert list(trace.y) == [f.price for f in expected]
    xd = s.source_series
    for segment in xd:
        a = fx[pens[segment.source_start].start_fenxing_index].anchor_raw_index
        b = fx[pens[segment.source_stop - 1].end_fenxing_index].anchor_raw_index
        if b < start or a >= stop:
            continue
        trace = next(t for t in fig.data if t.name == f"XD{segment.id}")
        assert list(trace.x) == [a - start, b - start]
        assert list(trace.y) == [segment.start_price, segment.end_price]
    checked = 0
    expected_shapes = []
    for z in s:
        g = z.geometry
        if g.diagnostics:
            if z.end_raw_index >= start and z.start_raw_index < stop:
                assert any(f"ZS{z.id}:" in a.text for a in fig.layout.annotations)
            continue
        if (
            g.left is None
            or g.left.x >= stop
            or (g.right is not None and g.right.x < start)
        ):
            continue
        shapes = [
            x
            for x in fig.layout.shapes
            if x.name
            and x.name.startswith(f"ZS{z.id} " if not g.closed else f"ZS{z.id}")
        ]
        if g.closed:
            shapes = [x for x in shapes if x.name == f"ZS{z.id}"]
            assert len(shapes) == 1
            shape = shapes[0]
            assert (shape.x0, shape.x1, shape.y0, shape.y1) == (
                g.left.x - start,
                g.right.x - start,
                z.lower,
                z.upper,
            )
            assert shape.type == ("line" if z.lower == z.upper else "rect")
        else:
            assert len(shapes) == len({z.lower, z.upper})
            for shape in shapes:
                assert (
                    shape.type == "line"
                    and shape.y0 == shape.y1
                    and shape.x0 == g.left.x - start
                    and shape.x1 == stop - 1 - start
                )
        expected_shapes.extend(shapes)
        checked += len(shapes)
    assert len(expected_shapes) == len(fig.layout.shapes)
    return checked


def main():
    charts = OUT / "charts"
    charts.mkdir(exist_ok=True)
    (charts / "plotly.min.js").write_text(get_plotlyjs())
    manifest = []
    coverage = {}
    primitives = 0
    for mode in MODES:
        root = OUT / "full" / mode
        table = ChanTable.read_csv(root / "table.csv", root / "context.csv")
        s = ZhongshuSeries.from_chan_table(table, "zs:" + mode)
        n = len(table)
        seen = set()
        windows = [("overview", 0, n)] + [
            (f"page-{i+1:03d}", a, min(n, a + 200))
            for i, a in enumerate(range(0, n, 180))
        ]
        for name, a, b in windows:
            fig = s.plot(
                raw_start=a,
                raw_stop=b,
                market="China",
                volume=False,
                title=f"Memo033 | {mode} | {name} | raw[{a}:{b})",
            )
            fig.update_layout(
                width=1700,
                height=760,
                showlegend=False,
                margin={"l": 60, "r": 35, "t": 65, "b": 55},
            )
            # Dense overview annotations are available on detail pages and hover.
            if name == "overview":
                fig.update_layout(
                    annotations=[x for x in fig.layout.annotations if x.xref == "paper"]
                )
            primitives += audit(s, fig, a, b)
            stem = f"{mode}-{name}"
            fig.write_html(charts / f"{stem}.html", include_plotlyjs="plotly.min.js")
            (charts / f"{stem}.figure.json").write_text(fig.to_json())
            manifest.append(
                {
                    "mode": mode,
                    "window": name,
                    "start": a,
                    "stop": b,
                    "figure": stem + ".figure.json",
                    "html": stem + ".html",
                    "png": stem + ".png",
                }
            )
            if name != "overview":
                seen.update(range(a, b))
            if name == "overview" or name.endswith(("010", "020", "030", "040", "050")):
                print("CHART", mode, name, flush=True)
        assert seen == set(range(n))
        coverage[mode] = len(seen)
    save(
        "chart-audit.json",
        {
            "figures": len(manifest),
            "native_public_method": True,
            "raw_coverage": coverage,
            "center_primitives": primitives,
            "candles_all_FX_XD_crossings_open_missing": "PASS",
        },
    )
    (charts / "manifest.json").write_text(json.dumps(manifest, indent=2))
    links = []
    for name in dict.fromkeys(r["window"] for r in manifest):
        group = [r for r in manifest if r["window"] == name]
        links.append(
            f'<h2>{name}</h2><a href="comparison-{name}.png">Four-mode comparison</a><br>'
            + "".join(
                f'<a href="{r["html"]}">{html.escape(r["mode"])}</a> · <a href="{r["png"]}">PNG</a><br>'
                for r in group
            )
        )
    (charts / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Memo033 complete atlas</title><h1>Memo033 — complete source + center atlas</h1><p>Default weak/weak is the last comparison row. Every mode covers 10060 raw bars; 200-bar windows, 20-bar overlap. Blue: located closed centers; amber dotted: open without fixed right edge; missing crossings: diagnosis only.</p>'
        + "".join(links)
    )


if __name__ == "__main__":
    main()
