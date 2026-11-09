"""Create source evidence and a manual price illustration; never import CC code."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil

os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/tds-memo018-s6-mpl")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ASSETS = ROOT / "docs/memo/memoWX_023_Chan_zoushi"
ASSETS.mkdir(exist_ok=True)
LESSONS = sorted((ROOT / "references/chan_theory").glob("[0-9][0-9][0-9].md"))
assert len(LESSONS) == 108
terms = re.compile(r"走势类型|走势终完美|盘整|同级别分解|走势分解|趋势|递归")
scan = []
for path in LESSONS:
    hits = [{"line": i, "text": line} for i, line in enumerate(path.read_text().splitlines(), 1) if terms.search(line)]
    scan.append({"path": str(path.relative_to(ROOT)), "hits": hits})
(HERE / "corpus_keyword_scan.json").write_text(json.dumps({"lesson_count": len(LESSONS), "patterns": terms.pattern, "scan": scan}, ensure_ascii=False, indent=2) + "\n")

sources = [("017/image001.jpg", "lesson017-image001.jpg"), ("020/image005.jpg", "lesson020-image005.jpg")]
copied = []
for name, target in sources:
    source = ROOT / "references/chan_theory" / name
    dest = ASSETS / target
    if dest.exists():
        assert dest.read_bytes() == source.read_bytes()
    else:
        shutil.copyfile(source, dest)
    assert dest.read_bytes() == source.read_bytes()
    copied.append({"source": str(source.relative_to(ROOT)), "destination": str(dest.relative_to(ROOT)), "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "visual_inspection": "Viewed source before copying; annotations present, first-publication authorship not authenticated."})

# Synthetic completed source legs. No raw OHLC and no source detector was run.
points = [5, 14, 8, 12, 9, 20, 16, 19, 17, 26, 22, 25, 13, 15, 11]
legs = [{"id": f"L{i}", "position": i, "start": a, "end": b, "high": max(a,b), "low": min(a,b), "direction": "up" if b>a else "down"} for i,(a,b) in enumerate(zip(points,points[1:]))]
a_core = legs[1:4]
b_core = legs[5:8]
def core(items):
    return {"zd":max(x["low"] for x in items),"zg":min(x["high"] for x in items),"gg":max(items[0]["high"],items[2]["high"]),"dd":min(items[0]["low"],items[2]["low"])}
a, b = core(a_core), core(b_core)
assert a == {"zd":9,"zg":12,"gg":14,"dd":8}
assert b == {"zd":17,"zg":19,"gg":20,"dd":16}
assert legs[5]["low"] > a["zg"] and legs[9]["low"] > b["zg"]
assert b["dd"] > a["gg"]
assert legs[12]["direction"] == "up" and legs[12]["high"] < b["zd"]
old_extreme=max((x for x in legs[4:13] if x["direction"]=="up"), key=lambda x:(x["end"],x["position"]))
assert old_extreme["position"] == 8 and old_extreme["end"] == 26
assert legs[13]["end"] < legs[12]["start"]
assert not (14 < legs[12]["start"]) and 27 > old_extreme["end"]
example={"nature":"Manual arithmetic/source-branch trace only; CC code not imported or executed.","points":points,"legs":legs,"centers":{"A":a,"B":b},"frozen_old_source_positions":list(range(9)),"new_forming_source_positions":list(range(9,14)),"old_endpoint_leg":"L8","freeze_evidence_leg":"L13","countercase":"Replace L13 with15->14; add L14=14->27: no evidence at13, original-direction new high cancels transition at14."}
example["prefix_consistent_center_states"] = [
    {"watermark":4,"A":{"state":"OPEN","close_evidence":None},"B":None},
    {"watermark":5,"A":{"state":"CLOSED","close_evidence":5},"B":None},
    {"watermark":7,"A":{"state":"CLOSED","close_evidence":5},"B":{"state":"OPEN","close_evidence":None}},
    {"watermark":8,"A":{"state":"CLOSED","close_evidence":5},"B":{"state":"OPEN","close_evidence":None}},
    {"watermark":9,"A":{"state":"CLOSED","close_evidence":5},"B":{"state":"CLOSED","close_evidence":9}},
]
example["prefix_12_provisional_membership"] = {"old_forming":list(range(13)),"new_forming":list(range(9,13)),"overlap":list(range(9,13))}
for state in example["prefix_consistent_center_states"]:
    for key in ("A", "B"):
        center = state[key]
        if center and center["close_evidence"] is not None:
            assert center["close_evidence"] <= state["watermark"]
assert set(example["prefix_12_provisional_membership"]["old_forming"]) & set(example["prefix_12_provisional_membership"]["new_forming"]) == set(range(9,13))
(HERE / "manual_example.json").write_text(json.dumps(example, ensure_ascii=False,indent=2)+"\n")
(HERE / "figure_provenance.json").write_text(json.dumps(copied,ensure_ascii=False,indent=2)+"\n")

fig, axes=plt.subplots(2,1,figsize=(14,8),sharex=True,sharey=True,layout="constrained")
for ax in axes:
    ax.set_ylim(3,29);ax.set_xlim(-.35,14.65);ax.set_yticks(range(5,30,5))
    ax.grid(alpha=.18);ax.set_ylabel("Price")
    ax.spines[["top","right"]].set_visible(False)
for x, ax in enumerate(axes):
    for i, (start,end) in enumerate(zip(points,points[1:])):
        color="#16846c" if end>start else "#ba4851"
        ax.plot([i,i+1],[start,end],color=color,lw=1.9,alpha=.9 if x==0 else .35)
        ax.plot(i+1,end,"o",color=color,ms=3)
        if x==0:
            ax.text(i+.52,(start+end)/2, f"L{i}",fontsize=8,ha="center",va="center",bbox={"facecolor":"white","edgecolor":"none","alpha":.8,"pad":1})
    ax.add_patch(Rectangle((1,9),3,3,color="#9fcee0",alpha=.3))
    ax.add_patch(Rectangle((5,17),3,2,color="#c5d9a9",alpha=.4))
axes[0].text(2.5,10.5,"A core [9,12]",ha="center",fontsize=10)
axes[0].text(6.5,18,"B core [17,19]",ha="center",fontsize=10)
axes[0].annotate("L12 probe: high15 < B.zd17",xy=(12.5,14),xytext=(9.8,6.0),fontsize=10,arrowprops={"arrowstyle":"->","color":"#555"})
axes[0].set_title("1. Synthetic completed source legs; centers already supplied (no raw OHLC)",loc="left",fontsize=12)
axes[1].plot([0,9],[5,26],color="#195c9d",lw=3,label="Old trend: frozen at event L13; members L0-L8")
axes[1].plot([9,14],[26,11],color="#d27b29",lw=3,ls="--",label="Next consolidation: forming; members L9-L13")
axes[1].axvline(9,color="#195c9d",ls=":",alpha=.7)
axes[1].axvline(14,color="#d27b29",ls=":",alpha=.7)
axes[1].annotate("Shared endpoint26\nL8.end = L9.start",xy=(9,26),xytext=(5.5,26),fontsize=10,arrowprops={"arrowstyle":"->"})
axes[1].annotate("L13 confirms11 < L12.start13\nconfirmation occurs after old endpoint",xy=(14,11),xytext=(8.2,5.3),fontsize=10,arrowprops={"arrowstyle":"->"})
axes[1].set_title("2. Manual kernel trace: shared center B; source members and evidence are distinct",loc="left",fontsize=12)
axes[1].legend(loc="upper left",fontsize=9,framealpha=.95)
axes[1].set_xticks(range(15));axes[1].set_xlabel("Ordered source-leg endpoint position (not timestamps)")
fig.suptitle("CC extend-mode teaching trace — not an executed CC result",fontsize=15)
target=ASSETS/"cc-zoushi-manual-lifecycle.png"
assert not target.exists(), "Preserve prior figure before regeneration"
fig.savefig(target,dpi=150)
plt.close(fig)
print("108-lesson scan, two byte-identical source images, manual arithmetic checks and financial chart generated.")
