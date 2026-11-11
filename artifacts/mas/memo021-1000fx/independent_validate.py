"""Independent XD-P1 checks from saved prices; never import recognizer helpers.

This validates the declared experiment, not equivalence to every Chan exception.
Normalization is a full-list adjacent reduction rather than the implementation's
incremental stack. All origin/boundary pairs are independently classified before
the descending-origin compatibility policy is applied. Graph paths are enumerated
by DFS, independently of the production DAG DP.
"""

from __future__ import annotations

import json
from collections import Counter
from functools import cache
from hashlib import sha256
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
KIND = {"no_gap": 0, "gap": 1, "direct_071": 2}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class Reference:
    def __init__(self, prices):
        self.p = prices
        self.n = len(prices) - 1
        self.raw = tuple(
            (min(prices[k], prices[k + 1]), max(prices[k], prices[k + 1]), (k,))
            for k in range(self.n)
        )
        self.pairs = 0
        self.reduced = cache(self.reduced)
        self.secondary = cache(self.secondary)

    def direction(self, start):
        return 1 if self.p[start + 1] > self.p[start] else -1

    def intersection(self, start):
        es = self.raw[start : start + 3]
        return [max(e[0] for e in es), min(e[1] for e in es)]

    def basic(self, i, j):
        if not 0 <= i < j <= self.n or j - i < 3 or (j - i) % 2 != 1:
            return False
        if self.direction(i) * (self.p[j] - self.p[i]) <= 0:
            return False
        low, high = self.intersection(i)
        return low <= high

    def reduced(self, indices, direction):
        """Reduce a complete raw list left-to-right, revisiting changed neighbors."""
        es = [self.raw[k] for k in indices]
        position = 0
        while position + 1 < len(es):
            a, b = es[position : position + 2]
            encloses = (
                a[0] <= b[0] and b[1] <= a[1]
            ) or (b[0] <= a[0] and a[1] <= b[1])
            if not encloses:
                position += 1
                continue
            if direction > 0:
                item = (max(a[0], b[0]), max(a[1], b[1]), a[2] + b[2])
            else:
                item = (min(a[0], b[0]), min(a[1], b[1]), a[2] + b[2])
            es[position : position + 2] = [item]
            position = max(0, position - 1)
        return tuple(es)

    def norm(self, start, stop, direction):
        return self.reduced(tuple(range(start, stop, 2)), direction)

    @staticmethod
    def encode(e):
        return {"low": e[0], "high": e[1], "members": list(e[2])}

    def anchor(self, e, direction):
        key = 1 if direction > 0 else 0
        value = (max if direction > 0 else min)(self.raw[k][key] for k in e[2])
        return next(k for k in e[2] if self.raw[k][key] == value)

    @staticmethod
    def turning(es, direction):
        a, b, c = es
        if direction > 0:
            return a[0] < b[0] > c[0] and a[1] < b[1] > c[1]
        return a[0] > b[0] < c[0] and a[1] > b[1] < c[1]

    def stale(self, boundary, h, direction):
        return any(direction * (x - self.p[boundary]) > 0 for x in self.p[boundary + 1 : h + 1])

    def secondary(self, j, direction):
        for h in range(j + 2, self.n + 1, 2):
            if self.stale(j, h, direction):
                break
            es = self.norm(j + 1, h, -direction)
            if len(es) < 3 or not self.turning(es[-3:], -direction):
                continue
            c = self.anchor(es[-2], -direction)
            if not self.basic(j, c):
                continue
            return {
                "reverse_end": c,
                "dep_endpoint": h,
                "elements": [self.encode(e) for e in es[-3:]],
                "all_feature_members": [k for e in es for k in e[2]],
            }
        return None

    def alternatives(self, i, j):
        self.pairs += 1
        if not self.basic(i, j) or j == self.n:
            return []
        d = self.direction(i)
        left = self.norm(i + 1, j, d)
        l = left[-1]
        found = []
        # Independently examine every odd reverse-direction frontier for DIRECT.
        guard = l[1] < self.p[j] if d > 0 else l[0] > self.p[j]
        first_break = d * (self.p[j + 1] - self.p[j - 1]) < 0
        if guard and first_break:
            for h in range(j + 3, self.n + 1, 2):
                if self.stale(j, h, d):
                    break
                if d * (self.p[h] - self.p[j + 1]) < 0 and self.basic(j, h):
                    found.append({
                        "kind": "direct_071", "dep_endpoint": h, "reverse_end": h,
                        "direct": {
                            "first_reverse_pen": j,
                            "broken_last_forward_start": j - 1,
                            "first_reverse_end_price": self.p[j + 1],
                            "breaking_pen": h - 1,
                            "left_feature_guard": self.encode(l),
                        },
                    })
                    break
        # Independently rebuild the complete right feature list at each frontier.
        for h in range(j + 1, self.n + 1, 2):
            if self.stale(j, h, d):
                break
            right_side = self.norm(j, h, d)
            m = right_side[0]
            if self.anchor(m, d) != j:
                break
            if len(right_side) < 2 or not self.turning((l, m, right_side[1]), d):
                continue
            if not self.basic(j, j + 3):
                break
            gap = l[1] < m[0] if d > 0 else l[0] > m[1]
            f1 = {
                "left": self.encode(l), "middle": self.encode(m),
                "right": self.encode(right_side[1]),
                "left_normalized": [self.encode(e) for e in left],
                "event_endpoint": h, "gap": gap,
            }
            if not gap:
                found.append({"kind": "no_gap", "dep_endpoint": h,
                              "reverse_end": None, "f1": f1})
                break
            f2 = self.secondary(j, d)
            if f2 is None:
                break
            end = max(h, f2["dep_endpoint"])
            if self.stale(j, end, d) or not self.basic(f2["reverse_end"], end):
                break
            found.append({"kind": "gap", "dep_endpoint": end,
                          "reverse_end": f2["reverse_end"], "f1": f1, "f2": f2})
            break
        return [{
            "profile": "XD-P1", "i": i, "j": j,
            "direction": "up" if d > 0 else "down", "member_range": [i, j],
            "first3_intersection": self.intersection(i),
            "reverse_first3_intersection": self.intersection(j),
            **c, "dep_pen": c["dep_endpoint"] - 1,
        } for c in found]

    def all_retained(self):
        retained = {}
        raw_count = 0
        compatible_count = 0
        for i in range(self.n - 3, -1, -1):
            candidates = []
            for j in range(i + 3, self.n + 1, 2):
                for c in self.alternatives(i, j):
                    raw_count += 1
                    successor = retained.get(j)
                    if c["kind"] == "gap":
                        rev = c["reverse_end"]
                        after = retained.get(rev)
                        if c["f1"]["event_endpoint"] > rev:
                            continue
                        if successor is not None and successor["j"] != rev:
                            continue
                        if after is not None and after["j"] < c["dep_endpoint"]:
                            continue
                    elif successor is not None and successor["j"] < c["dep_endpoint"]:
                        continue
                    compatible_count += 1
                    candidates.append(c)
            if candidates:
                retained[i] = min(candidates, key=lambda c: (
                    c["dep_endpoint"], c["j"], KIND[c["kind"]]
                ))
        return retained, raw_count, compatible_count


def graph_from_retained(retained):
    nodes = []
    index = {}
    for i in sorted(retained):
        c = retained[i]
        index[i] = len(nodes)
        nodes.append({
            "id": len(nodes), "i": i, "j": c["j"], "direction": c["direction"],
            "root": True, "kind": c["kind"], "dep_endpoint": c["dep_endpoint"],
            "dep_pen": c["dep_pen"], "certificate": c, "parent_id": None,
        })
    edges = []
    primary_count = len(nodes)
    for position in range(primary_count):
        parent = nodes[position]
        c = parent["certificate"]
        if c["kind"] == "gap":
            derived_id = len(nodes)
            end = c["reverse_end"]
            nodes.append({
                "id": derived_id, "i": c["j"], "j": end,
                "direction": "down" if c["direction"] == "up" else "up",
                "root": False, "kind": "secondary_067",
                "dep_endpoint": c["dep_endpoint"], "dep_pen": c["dep_pen"],
                "certificate": c, "parent_id": parent["id"],
            })
            edges.append([parent["id"], derived_id])
            if end in index and nodes[index[end]]["j"] >= c["dep_endpoint"]:
                edges.append([derived_id, index[end]])
        elif c["j"] in index and nodes[index[c["j"]]]["j"] >= c["dep_endpoint"]:
            edges.append([parent["id"], index[c["j"]]])
    return nodes, edges


def check_graph_by_dfs(nodes, edges, selection):
    """Enumerate every path prefix, without using the DP recurrence."""
    by_id = {q["id"]: q for q in nodes}
    order = sorted(by_id, key=lambda k: (by_id[k]["j"], by_id[k]["i"], k))
    rank = {key: pos for pos, key in enumerate(order)}
    out = {key: [] for key in order}
    for a, b in edges:
        require(by_id[a]["j"] == by_id[b]["i"], "disconnected graph edge")
        require(by_id[a]["direction"] != by_id[b]["direction"], "same-direction edge")
        require(rank[a] < rank[b], "non-forward graph edge")
        out[a].append(b)
    earliest = min((q["i"] for q in nodes if q["root"]), default=None)
    paths = []
    def visit(path):
        paths.append(tuple(path))
        for successor in sorted(out[path[-1]], key=lambda k: rank[k]):
            require(successor not in path, "cycle")
            visit(path + [successor])
    for root in order:
        if by_id[root]["root"] and by_id[root]["i"] == earliest:
            visit([root])
    best = {str(key): -1 for key in order}
    prev = {str(key): None for key in order}
    for end in order:
        ending = [p for p in paths if p[-1] == end]
        if ending:
            length = max(map(len, ending))
            winners = [p for p in ending if len(p) == length]
            # The recurrence chooses the earliest processed last predecessor on ties.
            winner = min(winners, key=lambda p: tuple(rank[k] for k in p[-2::-1]))
            best[str(end)] = length
            prev[str(end)] = winner[-2] if length > 1 else None
    require(selection["best"] == best, "all-state DFS best differs")
    require(selection["prev"] == prev, "all-state DFS prev differs")
    require(selection["topological_order"] == order, "graph traversal order differs")
    require(selection["start"] == earliest, "earliest root differs")
    if paths:
        end = min(
            (p[-1] for p in paths),
            key=lambda k: (-by_id[k]["j"], -best[str(k)], rank[k]),
        )
        recovered = []
        cursor = end
        while cursor is not None:
            recovered.append(cursor)
            cursor = prev[str(cursor)]
        recovered.reverse()
        require(selection["node_ids"] == recovered, "DFS-selected route differs")
        require(selection["end"] == by_id[end]["j"], "latest endpoint differs")
        require(selection["count"] == len(recovered), "route count differs")
    else:
        require(not selection["node_ids"], "empty graph has selected route")
    return len(paths)


def validate_mode(mode, report):
    path = ROOT / "input" / f"bi-{mode}.json"
    payload = json.loads(path.read_text())
    require(sha256(path.read_bytes()).hexdigest() == report["source_input_sha256"], "input hash differs")
    pens = payload["pens"]
    source_points = [pens[0]["start"]] + [p["end"] for p in pens]
    prices = [point["price"] for point in source_points]
    require(report["prices"] == prices, "price snapshot differs")
    require(len(pens) == report["pens"], "pen count differs")
    for k, p in enumerate(pens):
        require(p["start"] == source_points[k], "non-shared original endpoints")
        require(p["low"] == min(prices[k:k+2]) and p["high"] == max(prices[k:k+2]), "pen interval differs")
        require(p["direction"] == ("up" if prices[k+1] > prices[k] else "down"), "pen direction differs")
        if k:
            require((prices[k+1] - prices[k]) * (prices[k] - prices[k-1]) < 0, "pen sequence does not alternate")
    ref = Reference(prices)
    retained, alternatives, compatible = ref.all_retained()
    expected_certificates = [retained[i] for i in sorted(retained)]
    require(report["certificates"] == expected_certificates, "retained certificate/first-event policy differs")
    nodes, edges = graph_from_retained(retained)
    require(len(nodes) == len(report["nodes"]), "node count differs")
    for expected, actual in zip(nodes, report["nodes"]):
        for key, value in expected.items():
            require(actual[key] == value, f"node {expected['id']} field {key} differs")
        require(ref.basic(prices_start := actual["i"], actual["j"]), "node basic shape failed")
        require(actual["j"] < actual["dep_endpoint"] <= ref.n, "bad geometry/evidence frontier")
        if not actual["root"]:
            require(actual["parent_id"] is not None, "derived node has no parent")
            incoming = [a for a, b in edges if b == actual["id"]]
            require(incoming == [actual["parent_id"]], "derived node escaped its parent context")
        if "start_source" in actual:
            require(actual["start_source"] == source_points[prices_start], "selected start source mismatch")
            require(actual["end_source"] == source_points[actual["j"]], "selected end source mismatch")
            require(actual["evidence_source"] == source_points[actual["dep_endpoint"]], "selected evidence source mismatch")
    require(report["edges"] == edges, "graph edge set or fixed order differs")
    paths = check_graph_by_dfs(nodes, edges, report["selection"])
    selected_ids = report["selection"]["node_ids"]
    require([q["id"] for q in report["selected"]] == selected_ids, "selected node list differs")
    by_id = {q["id"]: q for q in nodes}
    chosen = [by_id[key] for key in selected_ids]
    endpoints = [chosen[0]["i"]] + [q["j"] for q in chosen] if chosen else []
    require(report["selected_endpoints"] == endpoints, "endpoint route differs")
    unresolved = [[0, endpoints[0]], [endpoints[-1], ref.n]] if endpoints else [[0, ref.n]]
    require(report["unresolved_pen_ranges"] == [r for r in unresolved if r[0] < r[1]], "uncovered ranges differ")
    tail = [
        {"i": endpoints[-1], "j": j, "status": "basic_only"}
        for j in range(endpoints[-1]+3, ref.n+1, 2) if ref.basic(endpoints[-1], j)
    ] if endpoints else []
    require(report["tail_candidates"] == tail, "open tail differs")
    require(report["selected_kind_counts"] == dict(Counter(q["kind"] for q in chosen)), "selected kind counts differ")
    return {
        "status": "PASS", "input_sha256": report["source_input_sha256"],
        "pens": ref.n, "origin_boundary_pairs_independently_examined": ref.pairs,
        "raw_completion_alternatives": alternatives, "compatible_alternatives": compatible,
        "primary_certificates_fully_reconstructed": len(expected_certificates),
        "nodes_independently_reconstructed_and_checked": len(nodes),
        "edges_independently_reconstructed_and_checked": len(edges),
        "dfs_all_path_prefixes_from_earliest_roots": paths,
        "all_best_prev_and_tie_rules": "PASS", "selected_segments": len(chosen),
        "selected_endpoints": endpoints, "selected_fx_bounds": report["selected_fx_bounds"],
        "unresolved_pen_ranges": report["unresolved_pen_ranges"],
        "independent_list_reduction_cache": ref.reduced.cache_info()._asdict(),
    }


def main():
    start = perf_counter()
    report = {"status": "RUNNING", "modes": {}, "scope": "XD-P1 profile consistency only, not author-complete or unique Chan segmentation", "recognizer_imported": False}
    try:
        results = json.loads((ROOT / "results.json").read_text())
        for mode, payload in results["modes"].items():
            report["modes"][mode] = validate_mode(mode, payload)
        source_hashes = json.loads((ROOT / "input" / "summary.json").read_text())["source_hashes"]
        for path, expected in source_hashes.items():
            require(sha256((REPO / path).read_bytes()).hexdigest() == expected, f"source changed: {path}")
        report["upstream_source_hashes_unchanged"] = len(source_hashes)
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        report["seconds"] = perf_counter() - start
        report["limitations"] = [
            "The declared experimental rules are independently reimplemented; agreement does not prove author equivalence.",
            "Upstream Bi legality was checked by input preparation; this script checks its fixed pen/source identity, not reruns upstream algorithm.",
            "Candidate completeness is relative to XD-P1's finite odd endpoint enumeration and declared strict policies.",
        ]
        (ROOT / "independent-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
