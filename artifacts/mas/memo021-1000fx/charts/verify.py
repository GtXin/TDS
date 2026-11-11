"""Check every rendered atlas trace against the saved source coordinates."""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
EXPERIMENT = ROOT.parent


def read(path: Path) -> Any:
    """Read a local JSON artifact."""
    return json.loads(path.read_text())


def endpoint(pens: list[dict[str, Any]], position: int) -> dict[str, Any]:
    """Resolve a source endpoint without loop-captured mutable state."""
    return pens[position]["start"] if position < len(pens) else pens[-1]["end"]


def main() -> None:
    """Audit source-array equality, coverage, annotation uniqueness and PNGs."""
    manifest = read(ROOT / "manifest.json")
    bars = read(EXPERIMENT / "input/bars.json")
    fractals = read(EXPERIMENT / "input/fractals.json")
    results = read(EXPERIMENT / "results.json")
    totals = {}
    for mode in ("strong", "weak"):
        pens = read(EXPERIMENT / f"input/bi-{mode}.json")["pens"]
        selected = results["modes"][mode]["selected"]

        mode_pages = [page for page in manifest if page["mode"] == mode]
        for page in mode_pages:
            a, b = page["raw"]
            figure = read(ROOT / page["figure_json"])
            traces = figure["data"]
            raw_trace = next(
                t for t in traces if t.get("meta", {}).get("kind") == "raw"
            )
            assert raw_trace["x"] == list(range(a, b))
            for key in ("open", "high", "low", "close"):
                assert raw_trace[key] == [bar[key] for bar in bars["raw"][a:b]]
            fx_ids = []
            for trace in traces:
                if trace.get("meta", {}).get("kind") != "fx":
                    continue
                for x, y, metadata in zip(trace["x"], trace["y"], trace["customdata"]):
                    index = metadata[0]
                    source = fractals[index]
                    assert (x, y) == (source["anchor_raw_index"], source["price"])
                    assert metadata[1:] == [
                        source["merged_center"],
                        source["anchor_utc"],
                    ]
                    fx_ids.append(index)
            assert sorted(fx_ids) == page["fx_positions"]
            bi_trace = next(t for t in traces if t.get("meta", {}).get("kind") == "bi")
            expected_x = []
            expected_y = []
            for index in page["bi_positions"]:
                pen = pens[index]
                expected_x.extend(
                    [
                        pen["start"]["anchor_raw_index"],
                        pen["end"]["anchor_raw_index"],
                        None,
                    ]
                )
                expected_y.extend([pen["start"]["price"], pen["end"]["price"], None])
            assert bi_trace["x"] == expected_x and bi_trace["y"] == expected_y
            actual_xd = []
            for trace in traces:
                if trace.get("meta", {}).get("kind") != "xd":
                    continue
                role = trace["meta"]["role"]
                ids = [
                    index
                    for index in page["xd_positions"]
                    if selected[index].get("role", "primary") == role
                ]
                expected_x, expected_y = [], []
                for index in ids:
                    state = selected[index]
                    left, right = endpoint(pens, state["i"]), endpoint(pens, state["j"])
                    expected_x.extend(
                        [left["anchor_raw_index"], right["anchor_raw_index"], None]
                    )
                    expected_y.extend([left["price"], right["price"], None])
                assert trace["x"] == expected_x and trace["y"] == expected_y
                actual_xd.extend(ids)
            assert sorted(actual_xd) == page["xd_positions"]
            annotations = [
                item
                for item in figure["layout"].get("annotations", [])
                if item.get("yref") != "paper"
            ]
            positions = [(item["x"], item["y"]) for item in annotations]
            assert len(positions) == len(set(positions)), (
                "Shared endpoint labels collide"
            )
            png = (ROOT / page["png"]).read_bytes()
            assert png[:8] == b"\x89PNG\r\n\x1a\n"
            assert struct.unpack(">II", png[16:24]) == (1800, 900)
            assert (ROOT / page["html"]).is_file()
        detail = [page for page in mode_pages if page["kind"] == "detail"]
        raw_coverage = {i for page in detail for i in range(*page["raw"])}
        merged_coverage = {i for page in detail for i in range(*page["merged"])}
        fx_coverage = {i for page in detail for i in page["fx_positions"]}
        assert raw_coverage == set(range(3244))
        assert merged_coverage == set(range(2040))
        assert fx_coverage == set(range(1000))
        totals[mode] = {
            "all_pages": len(mode_pages),
            "details": len(detail),
            "raw_coverage": 3244,
            "merged_coverage": 2040,
            "fx_coverage": 1000,
            "source_arrays_and_endpoints_exact": True,
            "unique_shared_endpoint_annotations": True,
        }
    report = {
        "pages": len(manifest),
        "modes": totals,
        "png_dimensions": [1800, 900],
        "all_pass": True,
        "scope": "Atlas source coordinates/coverage and rendered artifacts, not recognizer correctness.",
    }
    (ROOT / "chart-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
