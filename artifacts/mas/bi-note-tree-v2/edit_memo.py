"""Fill only memo020002.a and003 from reviewed note-based draft sections."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
memo = ROOT / "docs/memo/memoWX_020_Chan_bi.md"
original = memo.read_bytes()
before = original.decode("utf-8")
a = "### 002.a — Algorithm Tree\n"
b = "### 002.b — Detailed Implementation logic and Numerical Examples\n"
why = "## 003 — Reasoning (Why)\n"
notes = "## 004 — Other Notes\n"
ia, ib, iw, ino = (before.index(mark) for mark in (a, b, why, notes))
assert before[ia:ib].strip() == a.strip(), "002.a is no longer empty; inspect user changes."
assert before[iw:ino].strip() == why.strip(), "003 is no longer empty; inspect user changes."
section_a = (HERE / "section-002a.md").read_text()
section_why = (HERE / "section-003.md").read_text()
assert section_a.startswith(a) and section_why.startswith(why)
assert section_a.endswith("\n\n") and section_why.endswith("\n\n")
new_text = before[:ia] + section_a + before[ib:iw] + section_why + before[ino:]
assert new_text[:ia] == before[:ia]
assert new_text.split(b, 1)[1].split(why, 1)[0] == before[ib:iw].split(b, 1)[1]
assert new_text.split(notes, 1)[1] == before[ino:].split(notes, 1)[1]
protected_paths = [
    "docs/memo/README.md",
    "docs/memo/memoWX_028_biFamily.md",
    "src/chanlab/algo/bi.py",
    "src/chanlab/data/bi_table.py",
    "src/chanlab/visualization/bi_plot.py",
    "tests/test_bi.py",
]
hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in protected_paths}
stamp = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
backup = memo.parent / "backups" / f"{memo.stem}__{stamp}.md"
with backup.open("xb") as stream:
    stream.write(original)
assert backup.read_bytes() == original
assert memo.read_bytes() == original, "Concurrent user edit detected; leave memo unchanged."
memo.write_bytes(new_text.encode("utf-8"))
assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value for path, value in hashes.items())
report = {
    "backup": str(backup.relative_to(ROOT)),
    "before_sha256": hashlib.sha256(original).hexdigest(),
    "after_sha256": hashlib.sha256(memo.read_bytes()).hexdigest(),
    "changed_sections": ["002.a", "003"],
    "exact_inserted_sections": [str((HERE / name).relative_to(ROOT)) for name in ("section-002a.md", "section-003.md")],
    "definitions_unchanged": True,
    "002_b_d_unchanged": True,
    "004_and_all_following_content_unchanged": True,
    "protected_hashes": hashes,
}
(HERE / "edit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"backup": report["backup"], "changed_sections": report["changed_sections"]}, ensure_ascii=False))
