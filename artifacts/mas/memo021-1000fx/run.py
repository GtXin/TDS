"""Run the documented XD-P1 experiment on the prepared real1000FX inputs."""

from __future__ import annotations

import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from statistics import median
from typing import Any

from recognizer import basic, check_certificate, recognize

ROOT = Path(__file__).resolve().parent


def endpoint(pens: list[dict[str, Any]], pos: int) -> dict[str, Any]:
    """Resolve a shared Bi endpoint into its true upstream source anchor."""
    return pens[pos]["start"] if pos < len(pens) else pens[-1]["end"]


def run() -> None:
    """Run both fixed snapshots, repeat timings and recheck selected witnesses."""
    assert (ROOT / "profile-edit.json").exists(), "Record profile before real execution"
    results: dict[str, Any] = {
        "profile": "XD-P1",
        "modes": {},
        "scope": "Own conservative experiment; no CC execution or author-completeness claim.",
    }
    for mode in ("strong", "weak"):
        data = json.loads((ROOT / "input" / f"bi-{mode}.json").read_text())
        pens = data["pens"]
        prices = [pens[0]["start"]["price"]] + [pen["end"]["price"] for pen in pens]
        runs = [recognize(prices) for _ in range(3)]
        report = runs[0]
        for other in runs[1:]:
            assert other["selection"] == report["selection"]
            assert other["selected_endpoints"] == report["selected_endpoints"]
        previous = None
        for node in report["selected"]:
            assert basic(prices, node["i"], node["j"])
            assert check_certificate(prices, node["certificate"])["passed"]
            if previous is not None:
                assert (
                    previous["j"] == node["i"]
                    and previous["direction"] != node["direction"]
                )
            if node["kind"] == "secondary_067":
                assert previous is not None and previous["id"] == node["parent_id"]
                assert not node["root"]
            node["role"] = "primary" if node["root"] else "derived"
            node["h"] = node["dep_endpoint"]
            node["start_source"] = endpoint(pens, node["i"])
            node["end_source"] = endpoint(pens, node["j"])
            node["evidence_source"] = endpoint(pens, node["dep_endpoint"])
            previous = node
        count_out = Counter(left for left, _ in report["edges"])
        assert max(count_out.values(), default=0) <= 1
        report["timing_runs_seconds"] = [value["seconds"] for value in runs]
        report["median_seconds"] = median(report["timing_runs_seconds"])
        report["selected_kind_counts"] = dict(
            Counter(node["kind"] for node in report["selected"])
        )
        report["max_outdegree"] = max(count_out.values(), default=0)
        report["selected_fx_bounds"] = (
            None
            if not report["selected"]
            else [
                report["selected"][0]["start_source"]["fx_position"],
                report["selected"][-1]["end_source"]["fx_position"],
            ]
        )
        report["fresh_certificate_replays"] = len(report["selected"])
        report["source_input_sha256"] = sha256(
            (ROOT / "input" / f"bi-{mode}.json").read_bytes()
        ).hexdigest()
        results["modes"][mode] = report
    (ROOT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                mode: {
                    "pens": value["pens"],
                    "states": len(value["nodes"]),
                    "edges": len(value["edges"]),
                    "segments": len(value["selected"]),
                    "endpoint_route": value["selected_endpoints"],
                    "fx_bounds": value["selected_fx_bounds"],
                    "median_seconds": value["median_seconds"],
                    "unresolved": value["unresolved_pen_ranges"],
                    "kind_counts": value["selected_kind_counts"],
                }
                for mode, value in results["modes"].items()
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    run()
