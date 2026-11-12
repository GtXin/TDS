"""XD030-A all-candidate graph trial, with independent local and objective checks."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "memo021-1000fx"


def load(name: str, path: Path) -> Any:
    """Load a preserved helper without executing its command-line entrypoint."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run() -> None:
    """Enumerate all local witnesses, build a branching graph and select by DP."""
    rec = load("old_local", OLD / "recognizer.py")
    reference = load("old_reference", OLD / "independent_validate.py")
    results: dict[str, Any] = {"profile": "XD030-A", "modes": {}}
    for mode in ("strong", "weak"):
        started = perf_counter()
        data = json.loads((ROOT / "input" / f"bi-{mode}.json").read_text())
        pens = data["pens"]
        prices = [pens[0]["start"]["price"]] + [p["end"]["price"] for p in pens]
        ref = reference.Reference(prices)
        nodes: list[dict[str, Any]] = []
        pair_count = 0
        for i in range(len(pens)):
            for j in range(i + 3, len(pens) + 1, 2):
                cs, _ = rec.candidate_certificates(prices, i, j)
                independent = ref.alternatives(i, j)
                assert sorted(json.dumps(c, sort_keys=True) for c in cs) == sorted(
                    json.dumps(c, sort_keys=True) for c in independent
                )
                pair_count += 1
                for c in cs:
                    if (
                        c["kind"] == "gap"
                        and c["f1"]["event_endpoint"] > c["reverse_end"]
                    ):
                        continue
                    nodes.append(
                        {
                            "id": len(nodes),
                            "i": i,
                            "j": j,
                            "direction": c["direction"],
                            "root": True,
                            "kind": c["kind"],
                            "dep_endpoint": c["dep_endpoint"],
                            "dep_pen": c["dep_pen"],
                            "certificate": c,
                            "parent_id": None,
                            "role": "primary",
                        }
                    )
        primary = list(nodes)
        edges: list[list[int]] = []
        for q in primary:
            if q["kind"] == "gap":
                c = q["certificate"]
                r = {
                    "id": len(nodes),
                    "i": q["j"],
                    "j": c["reverse_end"],
                    "direction": "down" if q["direction"] == "up" else "up",
                    "root": False,
                    "kind": "secondary_067",
                    "dep_endpoint": c["dep_endpoint"],
                    "dep_pen": c["dep_pen"],
                    "certificate": c,
                    "parent_id": q["id"],
                    "role": "derived",
                }
                nodes.append(r)
                edges.append([q["id"], r["id"]])
        for q in nodes:
            if q["kind"] == "gap":
                continue
            for r in primary:
                if (
                    q["j"] == r["i"]
                    and q["direction"] != r["direction"]
                    and r["j"] >= q["dep_endpoint"]
                ):
                    edges.append([q["id"], r["id"]])
        outgoing: dict[int, list[int]] = {q["id"]: [] for q in nodes}
        for a, b in edges:
            assert nodes[a]["j"] == nodes[b]["i"] and nodes[a]["j"] < nodes[b]["j"]
            outgoing[a].append(b)
        earliest = min((q["i"] for q in primary), default=None)
        order = sorted(
            range(len(nodes)), key=lambda k: (nodes[k]["j"], nodes[k]["i"], k)
        )
        best = [-1] * len(nodes)
        prev: list[int | None] = [None] * len(nodes)
        for q in primary:
            if q["i"] == earliest:
                best[q["id"]] = 1
        for a in order:
            if best[a] < 0:
                continue
            for b in outgoing[a]:
                if best[a] + 1 > best[b]:
                    best[b], prev[b] = best[a] + 1, a
        reachable = [a for a in order if best[a] > 0]
        winner = (
            max(reachable, key=lambda a: (nodes[a]["j"], best[a], -a))
            if reachable
            else None
        )
        route = []
        current = winner
        while current is not None:
            route.append(current)
            current = prev[current]
        route.reverse()
        # Independent reverse DAG value recursion; no forward best/prev reuse.
        from functools import cache
        @cache
        def suffix(a: int) -> tuple[int, int]:
            return max([(nodes[a]["j"], 1)] + [(suffix(b)[0], suffix(b)[1] + 1) for b in outgoing[a]])
        independent_score = max((suffix(q["id"]) for q in primary if q["i"] == earliest), default=None)
        assert independent_score == ((nodes[winner]["j"], best[winner]) if winner is not None else None)
        path_count = None

        def point(index: int, pens: Any = pens) -> dict[str, Any]:
            return pens[index]["start"] if index < len(pens) else pens[-1]["end"]

        selected = [dict(nodes[a]) for a in route]
        for q in selected:
            assert ref.basic(q["i"], q["j"])
            q.update(
                start_source=point(q["i"]),
                end_source=point(q["j"]),
                evidence_source=point(q["dep_endpoint"]),
                h=q["dep_endpoint"],
            )
        end = selected[-1]["j"] if selected else 0
        results["modes"][mode] = {
            "pens": len(pens),
            "nodes": nodes,
            "edges": edges,
            "selected": selected,
            "selected_endpoints": ([selected[0]["i"]] + [q["j"] for q in selected])
            if selected
            else [],
            "unresolved_pen_ranges": [[0, selected[0]["i"]]]
            * (bool(selected) and selected[0]["i"] > 0)
            + ([[end, len(pens)]] if end < len(pens) else []),
            "pair_checks": pair_count,
            "independent_local_all_equal": True,
            "dfs_paths": path_count,
            "independent_reverse_dag_pass": True,
            "objective_exhaustive_pass": False,
            "max_outdegree": max(map(len, outgoing.values()), default=0),
            "seconds": perf_counter() - started,
        }
    (ROOT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(
        json.dumps(
            {
                m: {
                    k: (len(v) if k in ("nodes", "edges", "selected") else v)
                    for k, v in r.items()
                    if k not in ("selected_endpoints",)
                }
                for m, r in results["modes"].items()
            }
        )
    )


if __name__ == "__main__":
    run()
