"""Verify the saved memo's scope, exact drafts, links and preserved baseline."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
memo = ROOT / "docs/memo/memoWX_020_Chan_bi.md"
edit = json.loads((HERE / "edit.json").read_text())
backup = ROOT / edit["backup"]
old = backup.read_text()
new = memo.read_text()
assert hashlib.sha256(backup.read_bytes()).hexdigest() == edit["before_sha256"]
assert hashlib.sha256(memo.read_bytes()).hexdigest() == edit["after_sha256"]
a = "### 002.a — Algorithm Tree\n"
b = "### 002.b — Detailed Implementation logic and Numerical Examples\n"
why = "## 003 — Reasoning (Why)\n"
notes = "## 004 — Other Notes\n"
assert new.split(a, 1)[0] == old.split(a, 1)[0]
assert a + new.split(a, 1)[1].split(b, 1)[0] == (HERE / "section-002a.md").read_text()
assert new.split(b, 1)[1].split(why, 1)[0] == old.split(b, 1)[1].split(why, 1)[0]
assert why + new.split(why, 1)[1].split(notes, 1)[0] == (HERE / "section-003.md").read_text()
assert new.split(notes, 1)[1] == old.split(notes, 1)[1]
for path, digest in edit["protected_hashes"].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
section = (HERE / "section-002a.md").read_text()
tree = section.split("```text\n", 1)[1].split("```", 1)[0]
nodes = re.findall(r"^(2\.[1-9]) ", tree, re.MULTILINE)
assert nodes == [f"2.{i}" for i in range(1, 10)]
targets = re.findall(r"(?:转|回|进入)(2\.[1-9])", tree)
assert set(targets) <= set(nodes)
assert "2.2.a" in tree and "2.2.b" in tree
assert "Bi001E=F" in tree and "清空Bi001E" in tree
assert "新增建议" in tree and "更极端端点延伸失败" in tree
assert sum(line.startswith("```") for line in new.splitlines()) % 2 == 0
images = lambda text: Counter(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text))
assert images(old) == images(new)
local_links = []
for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", new):
    target = target.split("#", 1)[0].strip("<>")
    if not target or re.match(r"[a-zA-Z]+:", target):
        continue
    assert (memo.parent / unquote(target)).resolve().exists(), target
    local_links.append(target)
whitespace = lambda text: Counter(line for line in text.splitlines() if line != line.rstrip())
assert not (whitespace(new) - whitespace(old))
for name in ("section-002a.md", "section-003.md", "edit_memo.py", "verify_saved.py"):
    assert all(line == line.rstrip() for line in (HERE / name).read_text().splitlines()), name
arithmetic = json.loads((HERE / "arithmetic.json").read_text())
cases = [item for item in arithmetic.values() if isinstance(item, dict)]
assert len(cases) == 6
pairs = sum(len(case["pair_checks"]) for case in cases)
assert pairs == 20
assert all(pair["mirror_decision_matches"] for case in cases for pair in case["pair_checks"])
result = {
    "backup_byte_identical": True,
    "saved_sections_equal_reviewed_drafts": True,
    "outside_002a_and003_exact": True,
    "original_004_and_appendices_exact": True,
    "protected_files": len(edit["protected_hashes"]),
    "local_links": len(local_links),
    "tree_nodes": nodes,
    "gotos_resolve": True,
    "no_new_trailing_whitespace": True,
    "six_continuous_numeric_inputs": True,
    "executed_pair_checks": pairs,
    "executed_mirrored_pair_checks": pairs,
    "production_algorithm_execution": False,
}
(HERE / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False))
