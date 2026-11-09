"""Check the completed documentation batch without importing reference code."""
from pathlib import Path
import ast
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
MEMOS = ROOT / "docs/memo"
OUT = Path(__file__).parent
records = []
for number, name in [(19, "fenxing"), (20, "bi"), (21, "xianduan"),
                     (22, "zhongshu"), (23, "zoushi"), (24, "beichi"),
                     (25, "buysellpoint")]:
    path = MEMOS / f"memoWX_{number:03d}_Chan_{name}.md"
    text = path.read_text()
    prefix = text.split("## Appendix A —", 1)[0]
    backups = sorted((MEMOS / "backups").glob(path.stem + "__*.md"))
    assert backups, (path, "missing pre-edit backup")
    assert prefix == backups[0].read_text().split("## Appendix A —", 1)[0], path
    assert text.count("## Appendix A —") == 1, path
    assert text.count("## Appendix B —") == 1, path
    assert text.count("## References") == 1, path
    a = text.split("## Appendix A —", 1)[1].split("## Appendix B —", 1)[0]
    b = text.split("## Appendix B —", 1)[1].split("## References", 1)[0]
    assert len(a) > 1000 and len(b) > 1000, (path, "appendix too small")
    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    missing = []
    for target in targets:
        if target.startswith(("http://", "https://", "#")):
            continue
        relative = target.split("#", 1)[0]
        if not (MEMOS / relative).exists():
            missing.append(target)
    assert not missing, (path, missing)
    ids = re.findall(r"^\[(\d+)\]\s", text, re.M)
    assert ids == [str(i) for i in range(1, len(ids) + 1)], (path, ids)
    cited = set(re.findall(r"(?<!!)\[(\d+)\](?!\()", text))
    assert cited <= set(ids), (path, cited - set(ids))
    assert text.count("```") % 2 == 0, (path, "unbalanced code fences")
    images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    for image in images:
        assert image.startswith(path.stem + "/"), (path, image)
    assert f"]({path.name})" in (MEMOS / "README.md").read_text(), path
    records.append({"memo": str(path.relative_to(ROOT)), "appendix_a_characters": len(a),
                    "appendix_b_characters": len(b), "references": len(ids),
                    "image_embeds": len(images), "main_sections_unchanged": True,
                    "backup": str(backups[0].relative_to(ROOT)), "links": "passed"})

snapshot = ROOT / "references/cc_algo/local_snapshot/374268381a3e"
manifest = json.loads((snapshot / "manifest.json").read_text())
for entry in manifest["files"]:
    raw = (snapshot / entry["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    ast.parse(raw)
inventory = json.loads((OUT / "corpus_keyword_inventory.json").read_text())
assert all(item["scanned_lesson_files"] == 108 for item in inventory.values())
report = {"memos": records, "cc_files_hash_and_ast_checked": len(manifest["files"]),
          "scanned_numbered_lessons": 108, "cc_execution": False,
          "limits": "Mechanical checks supplement source/figure/manual-trace reviews; not runtime equivalence or algorithm correctness tests."}
(OUT / "batch_verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False))
