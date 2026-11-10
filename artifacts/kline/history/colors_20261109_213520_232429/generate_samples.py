"""Generate memo013 preview charts from the unchanged CC master sample."""

import hashlib
import json
from pathlib import Path

from chanlab.algo.kline import KlineTSeries


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    output = Path(__file__).resolve().parent
    folder = root / "samples/chan_table"
    master = next(folder.glob("*chan_table*.csv"))
    context_path = next(folder.glob("*context*.csv"))
    series = KlineTSeries.read_csv(master, context_path)
    context = series.context
    reports = []
    for count, volume, show_gaps, stem in (
        (200, True, False, "cc-15m-last200-volume"),
        (40, False, False, "cc-15m-last40-detail"),
        (200, True, True, "cc-15m-last200-calendar"),
    ):
        bars = series[-count:]
        figure = series.plot(
            start=-count,
            volume=volume,
            show_gaps=show_gaps,
            title=f"{bars[0].symbol} · 15-minute candles · Last {count} bars",
        )
        candle = figure.data[0]
        assert candle.type == "candlestick"
        assert figure.layout.xaxis.type == ("date" if show_gaps else "category")
        assert tuple(candle.x) == tuple(bar.timestamp for bar in bars)
        for field in ("open", "high", "low", "close"):
            assert tuple(getattr(candle, field)) == tuple(
                getattr(bar, field) for bar in bars
            )
        assert len(figure.data) == (2 if volume else 1)
        if volume:
            assert tuple(figure.data[1].y) == tuple(bar.volume for bar in bars)
        figure.update_layout(
            template="plotly_white",
            width=1400,
            height=780 if volume else 600,
            font={"family": "Arial", "size": 14, "color": "#243449"},
            title={"x": 0.055, "font": {"size": 22}},
            margin={"l": 80, "r": 45, "t": 90, "b": 70},
            showlegend=False,
            hovermode="x",
        )
        figure.update_traces(
            increasing_line_color="#0d9488",
            decreasing_line_color="#dc5964",
            selector={"type": "candlestick"},
        )
        figure.update_xaxes(
            showgrid=True,
            gridcolor="#edf0f4",
            tickfont={"size": 12},
            hoverformat="%Y-%m-%d %H:%M UTC",
        )
        figure.update_yaxes(showgrid=True, gridcolor="#edf0f4", tickfont={"size": 12})
        html_path, image_path = output / f"{stem}.html", output / f"{stem}.png"
        figure.write_html(
            html_path, include_plotlyjs=True, config={"displaylogo": False}
        )
        figure.write_image(image_path, scale=1.5)
        reports.append(
            {
                "html": str(html_path.relative_to(root)),
                "png": str(image_path.relative_to(root)),
                "bars": count,
                "volume": volume,
                "show_gaps": show_gaps,
                "first_utc": bars[0].timestamp.isoformat(),
                "last_utc": bars[-1].timestamp.isoformat(),
                "trace_values_match_source": True,
                "png_bytes": image_path.stat().st_size,
            }
        )
    protected = json.loads((output / "pre-plot-hashes.json").read_text())
    assert all(
        hashlib.sha256((root / path).read_bytes()).hexdigest() == digest
        for path, digest in protected.items()
    )
    report = {
        "source": str(master.relative_to(root)),
        "source_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
        "total_source_rows": len(series),
        "context": dict(context),
        "source_and_protected_files_unchanged": True,
        "charts": reports,
    }
    (output / "sample-verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
