"""Independently audit saved graph geometry, compatibility, charts and source hashes."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def main() -> None:
    """Check full outputs without recognizer/selector calls."""
    report: dict[str, Any] = {}
    results = json.loads((ROOT / "results.json").read_text())
    manifest = json.loads((ROOT / "charts/manifest.json").read_text())
    summary = json.loads((ROOT / "input/summary.json").read_text())
    for name, digest in summary["source_hashes"].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest
    for mode, data in results["modes"].items():
        ns = data["nodes"]
        by_start: Any = defaultdict(list)
        for q in ns:
            assert q["j"] - q["i"] >= 3 and (q["j"] - q["i"]) % 2 == 1
            if q["root"]:
                by_start[q["i"]].append(q)
        expected = set()
        for q in ns:
            if not q["root"]:
                assert ns[q["parent_id"]]["kind"] == "gap"
                expected.add((q["parent_id"], q["id"]))
            if q["kind"] == "gap":
                continue
            for r in by_start[q["j"]]:
                if r["direction"] != q["direction"] and r["j"] >= q["dep_endpoint"]:
                    expected.add((q["id"], r["id"]))
        assert expected == {tuple(e) for e in data["edges"]}
        selected = data["selected"]
        for left, right in pairwise(selected):
            assert (left["id"], right["id"]) in expected
        pages = [p for p in manifest if p["mode"] == mode and p["kind"] == "detail"]
        assert [p["fx_positions"] for p in pages] == [
            list(range(a, min(a + 500, 3027))) for a in range(0, 3027, 500)
        ]
        assert {i for p in pages for i in range(*p["raw"])} == set(range(10060))
        assert {i for p in pages for i in p["bi_positions"]} == set(range(data["pens"]))
        assert {i for p in pages for i in p["xd_positions"]} == set(
            range(len(selected))
        )
        report[mode] = {
            "edges_exact": len(expected),
            "selected_connectivity_pass": True,
            "window_fx_counts": [len(p["fx_positions"]) for p in pages],
            "coverage_pass": True,
        }
    (ROOT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
