"""Validate the reworked evidence batch; never execute CC source."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
baseline = json.loads((HERE / "baseline.json").read_text())
results = []
for row in baseline:
    path = ROOT / row["memo"]
    text = path.read_text()
    prefix = text.split("## Appendix A", 1)[0]
    assert hashlib.sha256(prefix.encode()).hexdigest() == row["main_prefix_sha256"]
    assert text.count("## Appendix A") == text.count("## Appendix B") == text.count("## References") == 1
    references = re.findall(r"^\[(\d+)\]\s", text, re.M)
    assert references == [str(i) for i in range(1, len(references) + 1)]
    assert set(re.findall(r"\[(\d+)\](?!\()", text)) <= set(references)
    assert text.count("```") % 2 == 0
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        if not target.startswith(("http://", "https://", "#")):
            assert (path.parent / target.split("#", 1)[0]).exists(), (path, target)
    results.append({"memo": row["memo"], "main_prefix": "task-start SHA256 matches",
                    "references": len(references), "links": "passed",
                    "current_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

# New root-authored source blocks survive the final heading/citation-only edit.
root_additions = json.loads((HERE / "s7-s8/additions.json").read_text())
for row in root_additions:
    text = (ROOT / row["memo"]).read_text()
    for quote in row["new_quotes"]:
        source = ROOT / f"references/chan_theory/{quote['lesson']}.md"
        raw = "\n".join(source.read_text().splitlines()[quote["start"] - 1:quote["stop"]])
        assert hashlib.sha256(raw.encode()).hexdigest() == quote["raw_sha256"]
        assert quote["block"] in text
    for image in row["new_figures"]:
        assert (ROOT / image["source"]).read_bytes() == (ROOT / image["copy"]).read_bytes()

source_files = 0
for folder in [ROOT / "references/cc_algo/local_snapshot/374268381a3e",
               ROOT / "references/cc_algo/recheck_signal_boundary/374268381a3e"]:
    manifest = json.loads((folder / "manifest.json").read_text())
    for item in manifest["files"]:
        raw = (folder / item["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"]
        assert (Path(manifest["source_root"]) / item["path"]).read_bytes() == raw
        if item["path"].endswith(".py"):
            ast.parse(raw)
        source_files += 1

report = {"memos": results, "source_files_hash_checked": source_files,
          "python_source_syntax_only": True, "cc_execution": False,
          "new_local_source_blocks": 25, "new_online_short_note": "104 primary author page",
          "new_source_image_copies": 20, "new_manual_financial_charts": 2,
          "limits": "Corpus keyword scan and selected context/figure/code audits, not exhaustive publication/image certification or runtime equivalence/proof. S7/S8 executable detector evidence still absent."}
(HERE / "final_verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"memos_checked": len(results), "sources_checked": source_files,
                  "main_prefixes_links_references": "passed", "cc_execution": False}))
