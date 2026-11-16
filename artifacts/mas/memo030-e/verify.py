"""Recompute selected local events and verify actual selected S/T/U binding."""

import json
from pathlib import Path

from test_engine import local, rec, ref

ROOT = Path(__file__).resolve().parent
raw = json.loads((ROOT / "results.json").read_text())
report = {}
for key, d in raw.items():
    pens = json.loads((ROOT / "input" / ("bi-" + d["bi_mode"] + ".json")).read_text())[
        "pens"
    ]
    prices = [pens[0]["start"]["price"]] + [q["end"]["price"] for q in pens]
    native, shape = local.scanner(prices, d["xd_mode"], rec, ref.Reference(prices))
    independent, _ = local.scanner(
        prices, d["xd_mode"], rec, ref.Reference(prices), True
    )
    chain = d["confirmed"] + d["tail"]
    evidence = []
    for i, w in enumerate(d["witnesses"]):
        a, b = chain[i]
        _, c = chain[i + 1]
        assert w in native(a, b) and w in independent(a, b)
        assert shape(a, b) and shape(b, c)
        if w["kind"] == "gap":
            x, e = chain[i + 2]
            assert (
                x == c
                and w["reverse_end"] == c
                and w["h1"] <= c
                and w["dep_endpoint"] <= e
                and shape(c, e)
            )
            t = [b, c]
            u = [c, e]
        else:
            assert w["dep_endpoint"] <= c
            t = [b, c]
            u = None
        evidence.append(
            {
                "confirmed": chain[i],
                "actual_breaker": t,
                "actual_second_sequence_successor": u,
                "certificate": w,
            }
        )
    assert len(evidence) == d["count"]
    report[key] = {
        "recomputed_selected_certificates": len(evidence),
        "actual_binding_pass": True,
        "confirmed_fx_bounds": d["fx_bounds"],
        "tail": d["tail"],
        "evidence": evidence,
    }
(ROOT / "verification.json").write_text(json.dumps(report, indent=2))
print({k: v["recomputed_selected_certificates"] for k, v in report.items()})
