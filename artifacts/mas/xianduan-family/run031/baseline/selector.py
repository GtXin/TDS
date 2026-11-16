"""XD030-E adjacent-pair DP; legacy files are event caches, never selected routes."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "memo030-four"


def solve(
    data: dict[str, Any], pens: list[Any], limit: int = 6000000
) -> dict[str, Any]:
    """Finalize S only through its actual T, with actual U required for gaps."""
    n = len(pens)
    p = [pens[0]["start"]["price"]] + [x["end"]["price"] for x in pens]
    mode = data["xd_mode"]

    def shape(a, b):
        if b - a < 3 or (b - a) % 2 == 0:
            return False
        d = 1 if p[a + 1] > p[a] else -1
        return (
            d * (p[b] - p[a]) > 0
            and (mode == "weak" or d * (p[b] - p[a + 1]) > 0)
            and max(min(p[k], p[k + 1]) for k in range(a, a + 3))
            <= min(max(p[k], p[k + 1]) for k in range(a, a + 3))
        )

    ends = {a: [b for b in range(a + 3, n + 1, 2) if shape(a, b)] for a in range(n)}
    # Cached event h is the earliest valid event for the same geometry/kind/gap turn.
    direct = {}
    gap = {}
    events = {}
    for q in data["nodes"]:
        if not q["root"]:
            continue
        a, b = q["i"], q["j"]
        c = q["certificate"]
        events.setdefault((a, b), []).append(c)
        if c["kind"] == "gap":
            k = (a, b, c["reverse_end"])
            old = gap.get(k)
            if old is None or c["dep_endpoint"] < old["dep_endpoint"]:
                gap[k] = c
        else:
            k = (a, b)
            old = direct.get(k)
            if old is None or c["dep_endpoint"] < old["dep_endpoint"]:
                direct[k] = c

    def pair(a, b, c):
        w = direct.get((a, b))
        if w and w["dep_endpoint"] <= c:
            return ("confirmed", w)
        w = gap.get((a, b, c))
        return ("gap", w) if w else (None, None)

    for start in (None,):
        buckets = [{} for _ in range(n + 1)]
        records = []
        best_terminal = None
        generated = 0

        def save(
            a, b, c, count, prev, witness, buckets=buckets, records=records, start=start
        ):
            nonlocal generated
            key = (a, b, c)
            bucket = buckets[c]
            old = bucket.get(key)
            if old is None or count > records[old]["count"]:
                rec = {
                    "a": a,
                    "b": b,
                    "c": c,
                    "count": count,
                    "prev": prev,
                    "witness": witness,
                }
                records.append(rec)
                bucket[key] = len(records) - 1
                generated += 1
                if generated > limit:
                    raise RuntimeError(
                        f"Explicit pair-state budget {limit} exceeded at start {start}"
                    )

        for origin in range(n-2):
            for b in ends[origin]:
                for c in ends.get(b, []):
                    if pair(origin,b,c)[0]:save(origin,b,c,0,None,None)
        for frontier in range(n + 1):
            for rid in list(buckets[frontier].values()):
                q = records[rid]
                a, b, c = q["a"], q["b"], q["c"]
                kind, w = pair(a, b, c)
                if kind == "confirmed":
                    score = (q["count"] + 1, b)
                    if best_terminal is None or score > best_terminal[0]:
                        best_terminal = (score, rid, w, None)
                for e in ends.get(c, []):
                    if kind == "gap" and w["dep_endpoint"] > e:
                        continue
                    if kind is None:
                        continue
                    # S/T is now verified using exactly T=(b,c), U=(c,e).
                    score = (q["count"] + 1, b)
                    if best_terminal is None or score > best_terminal[0]:
                        best_terminal = (score, rid, w, e)
                    if pair(b, c, e)[0]:
                        save(b, c, e, q["count"] + 1, rid, w)
        if best_terminal:
            score, rid, last_w, u = best_terminal
            chain = []
            witnesses = []
            current = rid
            while current is not None:
                q = records[current]
                chain.append((q["a"], q["b"]))
                if q["witness"]:
                    witnesses.append(q["witness"])
                current = q["prev"]
            chain.reverse()
            witnesses.reverse()
            witnesses.append(last_w)
            q = records[rid]
            tail = [(q["b"], q["c"])] + ([(q["c"], u)] if u else [])
            assert len(chain) == score[0]
            full = chain + tail
            for i, w in enumerate(witnesses):
                s, t = full[i : i + 2]
                assert (w["i"], w["j"]) == s and s[1] == t[0]
                assert shape(*s) and shape(*t)
                if w["kind"] == "gap":
                    v = full[i + 2]
                    assert (
                        w["reverse_end"] == t[1]
                        and v[0] == t[1]
                        and w["dep_endpoint"] <= v[1]
                    )
                else:
                    assert w["dep_endpoint"] <= t[1]
            return {
                "bi_mode": data["bi_mode"],
                "xd_mode": mode,
                "count": len(chain),
                "confirmed": chain,
                "tail": tail,
                "witnesses": witnesses,
                "state_records": generated,
                "fx_bounds": [
                    pens[chain[0][0]]["start"]["fx_position"],
                    pens[chain[-1][1] - 1]["end"]["fx_position"],
                ],
                "adjacent_binding_pass": True,
            }
    return {
        "bi_mode": data["bi_mode"],
        "xd_mode": mode,
        "count": 0,
        "confirmed": [],
        "tail": [],
        "witnesses": [],
        "adjacent_binding_pass": True,
    }


def main():
    source = json.loads((OLD / "results.json").read_text())
    out = {}
    for key, data in source["modes"].items():
        t = perf_counter()
        pens = json.loads(
            (OLD / "input" / ("bi-" + data["bi_mode"] + ".json")).read_text()
        )["pens"]
        print("Running", key, flush=True)
        result = solve(data, pens)
        result["seconds"] = perf_counter() - t
        out[key] = result
        (ROOT / "results.json").write_text(json.dumps(out, indent=2))
        print(
            key,
            result["count"],
            result.get("fx_bounds"),
            result.get("state_records"),
            flush=True,
        )


if __name__ == "__main__":
    main()
