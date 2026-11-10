"""Generate memo013 preview charts from the unchanged CC master sample."""

import hashlib
import json
from pathlib import Path
from typing import Literal

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
    samples: list[tuple[int, bool, bool, Literal["US", "China"], str]] = [
        (200, True, False, "US", "cc-15m-last200-volume"),
        (40, False, False, "US", "cc-15m-last40-detail"),
        (200, True, True, "US", "cc-15m-last200-calendar"),
        (40, False, False, "China", "cc-15m-last40-china"),
    ]
    for count, volume, show_gaps, market, stem in samples:
        bars = series[-count:]
        figure = series.plot(
            start=-count,
            volume=volume,
            show_gaps=show_gaps,
            market=market,
            title=f"{bars[0].symbol} · 15m · Last {count} bars · {market} colors",
        )
        candle = figure.data[0]
        assert candle.type == "candlestick"
        expected_up, expected_down = (
            ("#16a34a", "#dc2626") if market == "US" else ("#dc2626", "#16a34a")
        )
        assert (
            candle.increasing.line.color == candle.increasing.fillcolor == expected_up
        )
        assert (
            candle.decreasing.line.color == candle.decreasing.fillcolor == expected_down
        )
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
                "market": market,
                "up_color": expected_up,
                "down_color": expected_down,
                "first_utc": bars[0].timestamp.isoformat(),
                "last_utc": bars[-1].timestamp.isoformat(),
                "trace_values_match_source": True,
                "png_bytes": image_path.stat().st_size,
            }
        )
    protected = json.loads((output / "market-color-protected-hashes.json").read_text())
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
        "protected_hash_baseline": "market-color-protected-hashes.json",
        "charts": reports,
    }
    (output / "sample-verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
