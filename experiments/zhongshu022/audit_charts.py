"""Check serialized figures against computed results and full source coverage."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path("artifacts/mas/memo022-zs")


def shape_key(shape: dict[str, Any]) -> tuple[object, ...]:
    """Retain only the actual geometric primitive and its four coordinates."""
    return tuple(shape[k] for k in ("type", "x0", "x1", "y0", "y1"))


def run() -> None:
    """Independently audit plotted candles/chords/rectangles and missing borders."""
    charts = ROOT / "charts"
    manifest = json.loads((charts / "manifest.json").read_text())
    raw = json.loads((ROOT / "chart-source.json").read_text())["raw"]
    results = json.loads((ROOT / "results.json").read_text())
    coverage: dict[str, set[int]] = {}
    shape_count = 0
    for entry in manifest:
        a, b = entry["raw_start"], entry["raw_stop"]
        mode = entry["mode"]
        fig = json.loads(
            (charts / entry["html"].replace(".html", ".figure.json")).read_text()
        )
        candles = fig["data"][0]
        assert candles["x"] == list(range(a, b))
        for field in ("open", "high", "low", "close"):
            assert candles[field] == [x[field] for x in raw[a:b]]
        expected_x: list[float | None] = []
        expected_y: list[float | None] = []
        for leg in results[mode]["segments"]:
            if leg["end_x"] >= a and leg["start_x"] < b:
                expected_x += [leg["start_x"], leg["end_x"], None]
                expected_y += [leg["start_price"], leg["end_price"], None]
        assert fig["data"][1]["x"] == expected_x and fig["data"][1]["y"] == expected_y
        expected: list[tuple[object, ...]] = []
        for z in results[mode]["result"]["centers"]:
            left, right = z["left"], z["right"]
            if left is None:
                continue
            if z["terminal"] is None:
                if left["x"] < b:
                    expected.extend(
                        ("line", left["x"], b - 1, v, v) for v in {z["low"], z["high"]}
                    )
            elif right is not None and right["x"] >= a and left["x"] < b:
                expected.append(
                    (
                        "line" if z["low"] == z["high"] else "rect",
                        left["x"],
                        right["x"],
                        z["low"],
                        z["high"],
                    )
                )
        actual = [shape_key(x) for x in fig.get("layout", {}).get("shapes", [])]
        assert Counter(actual) == Counter(expected), entry
        shape_count += len(actual)
        assert (charts / entry["png"]).is_file()
        assert 'src="plotly.min.js"' in (charts / entry["html"]).read_text()
        if entry["window"] != "overview":
            coverage.setdefault(mode, set()).update(range(a, b))
    assert (
        all(x == set(range(len(raw))) for x in coverage.values()) and len(coverage) == 4
    )
    result = {
        "figures": len(manifest),
        "serialized_shapes_checked": shape_count,
        "raw_rows_per_mode": len(raw),
        "coverage": "PASS",
        "candles_chords_shapes": "PASS",
        "missing_crossings_omitted": "PASS",
        "open_right_borders_absent": "PASS",
    }
    (ROOT / "chart-audit.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    run()
