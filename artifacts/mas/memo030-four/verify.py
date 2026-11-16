"""Saved-output audit using direct price comparisons, mode separation and coverage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def main() -> None:
    """Independently check mode predicates and all saved certificate dependencies."""
    results = json.loads((ROOT / "results.json").read_text())
    manifest = json.loads((ROOT / "charts/manifest.json").read_text())
    output: dict[str, Any] = {}
    for mode, data in results["modes"].items():
        pens = json.loads(
            (ROOT / "input" / ("bi-" + data["bi_mode"] + ".json")).read_text()
        )["pens"]
        p = [pens[0]["start"]["price"]] + [b["end"]["price"] for b in pens]
        checks = 0
        for q in data["nodes"]:
            for a, b in [(q["i"], q["j"])] + q["certificate"]["supports"]:
                assert b - a >= 3 and (b - a) % 2 == 1
                lows = [min(p[k], p[k + 1]) for k in range(a, a + 3)]
                highs = [max(p[k], p[k + 1]) for k in range(a, a + 3)]
                assert max(lows) <= min(highs)
                if p[a + 1] > p[a]:
                    assert p[b] > p[a]
                    if data["xd_mode"] == "strong":
                        assert p[b] > p[a + 1]
                else:
                    assert p[b] < p[a]
                    if data["xd_mode"] == "strong":
                        assert p[b] < p[a + 1]
                checks += 1
        edges = {tuple(e) for e in data["edges"]}
        for a, b in edges:
            q, r = data["nodes"][a], data["nodes"][b]
            assert q["j"] == r["i"] and q["direction"] != r["direction"]
            if not r["root"]:
                assert r["parent_id"] == a
            else:
                assert r["j"] >= q["dep_endpoint"]
        pages = [x for x in manifest if x["mode"] == mode and x["kind"] == "detail"]
        assert [x["fx_positions"] for x in pages] == [
            list(range(a, min(a + 500, 3027))) for a in range(0, 3027, 500)
        ]
        assert {i for x in pages for i in range(*x["raw"])} == set(range(10060))
        assert {i for x in pages for i in x["bi_positions"]} == set(range(len(pens)))
        assert {i for x in pages for i in x["xd_positions"]} == set(
            range(len(data["selected"]))
        )
        output[mode] = {
            "node_and_support_shape_checks": checks,
            "edge_checks": len(edges),
            "coverage_pass": True,
            "fractal_windows": [500] * 6 + [27],
        }
    (ROOT / "verification.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))


if __name__ == "__main__":
    main()
