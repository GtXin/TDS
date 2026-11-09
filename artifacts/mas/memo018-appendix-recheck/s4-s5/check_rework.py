"""Read-only verification of reviewed memos, writing only local recheck evidence."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
MEMO = ROOT / "docs/memo"
old = json.loads((ROOT / "artifacts/mas/memo018-appendix-study/s4-s5/evidence.json").read_text())
new = json.loads((HERE / "write_evidence.json").read_text())
learning = json.loads((HERE / "learning_figure_evidence.json").read_text())
baseline = json.loads((HERE.parent / "baseline.json").read_text())

def normalize(s):
    s = re.sub(r"</?span\b[^>]*>", "", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    return re.sub(r"\s|\*|`", "", s).replace("\\=", "=")

texts = []
for n in [21, 22]:
    p = next(MEMO.glob(f"memoWX_{n:03d}_*.md"))
    s = p.read_text()
    expected = next(row for row in baseline if row["memo"] == str(p.relative_to(ROOT)))
    assert hashlib.sha256(s.split("## Appendix A",1)[0].encode()).hexdigest() == expected["main_prefix_sha256"]
    texts.append(s)
    refs = re.findall(r"^\[(\d+)\] ",s,re.M)
    assert refs == [str(i+1) for i in range(len(refs))]
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)",s):
        if not target.startswith(("http", "#")):
            assert (p.parent/target.split('#')[0]).exists(), target
quoted = normalize("\n".join(line[2:] if line.startswith('> ') else '' for text in texts for line in text.splitlines()))
selections = [*old["quote_selections"], *new["quotes"], learning]
for row in selections:
    lesson = row["lesson"]
    source = ROOT / f"references/chan_theory/{lesson:03d}.md"
    raw = "\n".join(source.read_text().splitlines()[row["start"]-1:row["stop"]])
    assert hashlib.sha256(raw.encode()).hexdigest() == row["raw_sha256"]
    assert normalize(raw) in quoted, (lesson,row["start"],row["stop"])

figures = [*old["original_figures"], *new["figures"], *learning["figures"]]
for row in figures:
    src = ROOT / row["source"]
    dest = ROOT / row.get("copy",row.get("destination", ""))
    assert src.read_bytes() == dest.read_bytes(), row
    assert hashlib.sha256(src.read_bytes()).hexdigest() == row["sha256"]
report = {"memos":["021","022"],"original_and_added_blocks":len(selections),
          "new_blocks":6,"original_image_copies_checked":len(figures),
          "new_image_copies":11,"quote_wording_source_hashes":"passed",
          "main_prefixes_against_recheck_baseline":"passed",
          "links_and_sequential_citations":"passed", "cc_execution":False}
(HERE / "checks.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False))
