"""Independent full-chain enumeration checks the pair-state DP objective."""

import importlib.util
import random
import sys
from pathlib import Path

from run import solve

ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


rec = load("c_rec", ROOT.parent / "memo021-1000fx/recognizer.py")
ref = load("c_ref", ROOT.parent / "memo021-1000fx/independent_validate.py")
local = load("c_local", ROOT.parent / "memo030-four/local.py")


def fixture(p, mode):
    candidate, shape = local.scanner(p, mode, rec, ref.Reference(p))
    nodes = []
    events = {}
    for a in range(len(p) - 3):
        for b in range(a + 3, len(p), 2):
            cs = candidate(a, b)
            events[a, b] = cs
            for c in cs:
                nodes.append({"root": True, "i": a, "j": b, "certificate": c})
    pens = [
        {
            "start": {"price": p[k], "fx_position": k},
            "end": {"price": p[k + 1], "fx_position": k + 1},
        }
        for k in range(len(p) - 1)
    ]
    return {"bi_mode": "test", "xd_mode": mode, "nodes": nodes}, pens, events, shape


def test_pair_dp_against_full_chain_enumeration():
    nonempty = 0
    rng = random.Random(30333)
    for trial in range(60):
        p = [10.0]
        for k in range(12):
            p.append(p[-1] + (1 if k % 2 == 0 else -1) * rng.randint(1, 12))
        for mode in ("strong", "weak"):
            data, pens, events, shape = fixture(p, mode)
            actual = solve(data, pens, 100000)
            scores = []

            def visit(chain, events=events, scores=scores, p=p, shape=shape):
                count = 0
                for index in range(len(chain) - 1):
                    a, b = chain[index]
                    _, c = chain[index + 1]
                    valid = any(
                        (w["kind"] != "gap" and w["dep_endpoint"] <= c)
                        or (
                            w["kind"] == "gap"
                            and w["reverse_end"] == c
                            and index + 2 < len(chain)
                            and w["dep_endpoint"] <= chain[index + 2][1]
                        )
                        for w in events[a, b]
                    )
                    if not valid:
                        break
                    count += 1
                if count:
                    scores.append(-count)
                end = chain[-1][1]
                for nxt in range(end + 3, len(p), 2):
                    if shape(end, nxt):
                        visit(chain + [(end, nxt)])

            for a in range(len(p) - 3):
                for b in range(a + 3, len(p), 2):
                    if shape(a, b):
                        visit([(a, b)])
            expected = min(scores) if scores else None
            observed = -actual["count"] if actual["count"] else None
            nonempty += observed is not None
            assert observed == expected, (trial, mode, p, observed, expected)

    assert nonempty > 0
