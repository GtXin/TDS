"""Adapt verified C results to source-aligned chart arrays, keeping open tails distinct."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "memo030-four"
(ROOT / "input").mkdir(exist_ok=True)
for p in (OLD / "input").glob("*.json"):
    shutil.copyfile(p, ROOT / "input" / p.name)
raw = json.loads((ROOT / "results.json").read_text())
out = {"profile": "XD030-E", "modes": {}}
for key, d in raw.items():
    pens = json.loads((ROOT / "input" / ("bi-" + d["bi_mode"] + ".json")).read_text())[
        "pens"
    ]

    def point(k, pens=pens):
        return pens[k]["start"] if k < len(pens) else pens[-1]["end"]

    selected = []
    for k, ((a, b), w) in enumerate(zip(d["confirmed"], d["witnesses"])):
        selected.append(
            {
                "i": a,
                "j": b,
                "kind": w["kind"],
                "role": "confirmed",
                "h": w["dep_endpoint"],
                "dep_endpoint": w["dep_endpoint"],
                "dep_pen": w["dep_pen"],
                "start_source": point(a),
                "end_source": point(b),
                "evidence_source": point(w["dep_endpoint"]),
                "certificate": w,
            }
        )
    out["modes"][key] = {
        "bi_mode": d["bi_mode"],
        "xd_mode": d["xd_mode"],
        "pens": len(pens),
        "selected": selected,
        "tail": d["tail"],
    }
(ROOT / "plot-results.json").write_text(json.dumps(out, indent=2))
s = (
    (OLD / "plot.py")
    .read_text()
    .replace("XD030-B", "XD030-E")
    .replace('default=ROOT / "results.json"', 'default=ROOT / "plot-results.json"')
)
# Keep individual atlases; unified C gallery is generated separately.
s = s.replace(
    '    runpy.run_path(str(CHARTS / "build_index.py"), run_name="__main__")', ""
).replace("import runpy\n", "")
needle = "            figure.write_html("
s = s.replace(
    needle,
    """            for ta,tb in results["modes"][mode]["tail"]:
                left,right=point(pens,ta),point(pens,tb)
                figure.add_scatter(x=[left["anchor_raw_index"],right["anchor_raw_index"]],y=[left["price"],right["price"]],mode="lines",line={"color":"#64748b","dash":"dash","width":2},name="Unconfirmed evidence tail",meta={"kind":"tail"})
"""
    + needle,
    1,
)
s = s.replace('role == "primary"', 'role == "confirmed"')
(ROOT / "plot.py").write_text(s)
(ROOT / "charts").mkdir(exist_ok=True)
(ROOT / "charts/render.swift").write_text(
    (OLD / "comparison/render.swift")
    .read_text()
    .replace("memo030-four", "memo030-e")
    .replace("XD030-B", "XD030-E")
)
(ROOT / "comparison").mkdir(exist_ok=True)
(ROOT / "comparison/compact-atlas.swift").write_text(
    (OLD / "comparison/compact-atlas.swift")
    .read_text()
    .replace(
        "Purple: primary; orange: derived",
        "Purple: confirmed; gray dashed: unconfirmed tail",
    )
    .replace("Saved trial results", "C trial results")
)
