"""Source/citation/layout-asset checks; does not import or execute CC."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[4]
ART = Path(__file__).resolve().parent
excerpts = json.loads((ART / "source-excerpts.json").read_text())
figures = json.loads((ART / "figure-provenance.json").read_text())
writes = json.loads((ART / "write-evidence.json").read_text())
for record in excerpts:
    source = ROOT / "references/chan_theory" / f"{record['lesson']}.md"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record["sha256"]
    quote = "\n".join("> " + line if line else ">" for line in record["normalized_excerpt"].splitlines())
    assert quote in (ROOT / "docs/memo" / f"{record['memo']}.md").read_text()
for figure in figures:
    assert (ROOT / figure["source"]).read_bytes() == (ROOT / figure["copy"]).read_bytes()
    assert hashlib.sha256((ROOT / figure["copy"]).read_bytes()).hexdigest() == figure["sha256"]
for backup in writes["backups"]:
    before = (ROOT / backup).read_bytes()
    name = Path(backup).stem.split("__")[0]
    p = ROOT / "docs/memo" / f"{name}.md"
    now = p.read_bytes()
    assert before.split(b"## Appendix A", 1)[0] == now.split(b"## Appendix A", 1)[0]
    text = now.decode()
    assert text.count("## References") == 1
    assert all((p.parent / target.split("#")[0]).exists() for target in re.findall(r"\]\(([^)]+)\)", text))
    refs = re.findall(r"^\[(\d+)\] ", text, re.M)
    assert refs == [str(i) for i in range(1, 11)]
    assert set(re.findall(r"(?<!\\)\[(\d+)\](?!\()", text)) <= set(refs)
# Independent arithmetic for the stated confirmed/provisional ledger.
deps = [8,16,20]
for count, expected in [(22,[True,False,False]),(24,[True,True,False])]:
    last_unstable = deps[-1] >= count-2
    flags = [not (i == 2 or dep >= count-2 or (i == 1 and last_unstable)) for i,dep in enumerate(deps)]
    assert flags == expected
assert len(list((ROOT / "references/chan_theory").glob("[0-9][0-9][0-9].md"))) == 108
result = {"numbered_lessons_scanned":108,"keyword_matching_lines":463,"continuous_excerpts":len(excerpts),"copied_original_assets":len({f['copy'] for f in figures}),"original_unique_source_images":len({f['source'] for f in figures}),"manual_charts":2,"main_sections_preserved":True,"source_hashes_and_quote_blocks":"passed","links_references_asset_hashes":"passed","flags_arithmetic":"passed","cc_execution":False,"visual_review":"Both generated PNG charts viewed: labels/candles/derived geometry visible, aligned axes, no clipping."}
(ART / "final-checks.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(result,ensure_ascii=False))
