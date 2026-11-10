"""Verify the two-class memo specification and execute its Python examples."""

import ast
import json
import os
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[3]
memo = root / "docs/memo/memoWX_026_MergedKlineFamily.md"
text = memo.read_text()
section = text.split("## 003 —", 1)[1].split("## Appendix", 1)[0]
tree = ast.parse((root / "src/chanlab/algo/merged_kline.py").read_text())
classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
assert [n.name for n in classes] == ["MergedKline", "MergedKlineSeries"]
assert not any(isinstance(n, ast.FunctionDef) for n in tree.body)
for cls in classes:
    for n in cls.body:
        if isinstance(n, ast.AnnAssign):
            assert f"`{n.target.id}`" in section, n.target.id
        if isinstance(n, ast.FunctionDef):
            reference = text if n.name.startswith("_") and not n.name.startswith("__") else section
            assert n.name in reference, n.name
for name in ("MergeConfig", "Work", "MergeDecision", "PendingMerge", "DualMerge"):
    assert re.search(r"\b" + re.escape(name) + r"\b", section) is None, name
for target in re.findall(r"\]\(([^)]+)\)", text):
    assert (memo.parent / target.split("#")[0]).exists(), target
assert re.findall(r"^## (\d{3})", text, re.M) == ["000", "001", "002", "003"]
assert (memo.parent / "README.md").read_text().count("| WX 026 |") == 1
# Every table has a consistent number of unescaped pipe separators.
width = None
for line in text.splitlines():
    if line.startswith("|"):
        count = len(re.findall(r"(?<!\\)\|", line))
        if width is None:
            width = count
        assert width == count, line
    else:
        width = None
blocks = re.findall(r"```python\n(.*?)```", section, re.S)
run = subprocess.run(
    [str(root / ".venv/bin/python"), "-c", "\n".join(blocks)],
    cwd=root,
    env={**os.environ, "PYTHONPATH": str(root / "src")},
    capture_output=True,
    text=True,
)
(root / "artifacts/mas/merged-kline-two-class/checks/memo-examples.txt").write_text(
    run.stdout + run.stderr
)
assert run.returncode == 0, run.stderr
report = dict(
    classes=[n.name for n in classes],
    member_counts={
        n.name: sum(isinstance(f, ast.AnnAssign) for f in n.body) for n in classes
    },
    all_authored_methods_documented=True,
    no_module_functions=True,
    examples_executed=len(blocks),
    links_and_table_columns=True,
)
(root / "artifacts/mas/merged-kline-two-class/checks/document.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps(report, indent=2))
