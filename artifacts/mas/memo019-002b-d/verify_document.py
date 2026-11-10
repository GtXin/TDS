"""Verify only the authorized memo edit and its frozen arithmetic evidence."""

import hashlib
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlsplit

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
edit = json.loads((FOLDER / "edit.json").read_text())
memo = ROOT / edit["memo"]
backup = ROOT / edit["backup"]
before, after = backup.read_bytes(), memo.read_bytes()
assert hashlib.sha256(before).hexdigest() == edit["before_sha256"]
assert hashlib.sha256(after).hexdigest() == edit["after_sha256"]
start = "### 002.b — Detailed Implementation logic and Numerical Examples\n"
end = "## 003 — Reasoning (Why)\n"
original, current = before.decode(), after.decode()
assert original.split(start, 1)[0] == current.split(start, 1)[0]
assert original.split(end, 1)[1] == current.split(end, 1)[1]
section = start + current.split(start, 1)[1].split(end, 1)[0]
assert section == (FOLDER / "sections.md").read_text()
assert section.count("```") == 6
helper_names = re.findall(r"(?m)^#### .*：(_[a-z_]+)$", section)
expected = ["_normalize_config", "_direction_between", "_classify_window",
            "_resolve_anchor", "_validate_result"]
assert helper_names == expected
calls = set(re.findall(r"\b(_[a-z_]+)\(", section))
assert calls == set(expected)
point = re.search(r"point ← Fenxing\((.*?)将point追加到R", section, re.S).group(1)
assert re.findall(r"([a-z_]+)=", point) == [
    "id", "kind", "price", "anchor_raw_index", "source_start", "source_stop",
    "status", "confirmed_at",
]
series = re.search(r"返回FenxingSeries\((.*?)# 构造时", section, re.S).group(1)
assert re.findall(r"([a-z_]+)=", series) == [
    "source_series", "items", "config", "rule_tree_ref", "trace", "trace_by_point",
]
for heading in [start.rstrip(), "### 002.c — Helper Functions", "### 002.d — Pseudocode"]:
    assert current.count(heading) == 1
for table in re.findall(r"(?m)(?:^\|.*\n)+", section):
    widths = [len(re.split(r"(?<!\\)\|", row)) for row in table.strip().splitlines()]
    assert len(set(widths)) == 1
links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", current)
for link in links:
    url = urlsplit(link)
    if not url.scheme and url.path:
        assert (memo.parent / unquote(url.path)).exists(), link
protected = json.loads((FOLDER / "protected_before.json").read_text())
concurrent = json.loads((FOLDER / "concurrent_changes.json").read_text())
for path, value in protected.items():
    if path != edit["memo"]:
        data = (ROOT / path).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if path in concurrent:
            observation = concurrent[path]
            assert actual == observation["observed_sha256"], path
            assert hashlib.sha256(data.replace(observation["added_line"].encode(), b"")).hexdigest() == value, path
        else:
            assert actual == value, path
images = {}
for path, value in edit["images"].items():
    data = (ROOT / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == value
    assert data == (FOLDER / Path(path).name).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    images[path] = struct.unpack(">II", data[16:24])
assert Path(memo.parent / "README.md").read_text().count("(memoWX_019_Chan_fenxing.md)") == 1
examples = json.loads((FOLDER / "examples.json").read_text())
assert len(examples["raw_bounds"]) == 10 and len(examples["merged_groups"]) == 7
assert [r["anchor_raw_index"] for r in examples["default_first"]["items"]] == [2, 5, 8]
assert [r["anchor_raw_index"] for r in examples["explicit_last"]["items"]] == [3, 6, 8]
assert examples["output_trace_corruption_probes_rejected"] == 8
report = {
    "backup_bytes_verified": True,
    "outside_002b_d_unchanged": True,
    "protected_other_files_unchanged": len(protected) - 1 - len(concurrent),
    "concurrent_changes_preserved": concurrent,
    "private_helper_names": helper_names,
    "pseudocode_record_series_fields": [8, 6],
    "local_links_checked": len(links),
    "headings_tables_fences_index": "pass",
    "image_bytes_and_dimensions": images,
    "visual_inspection": "Both final figures inspected; initial cramped bottom labels preserved under history and corrected before copy",
    "numeric_examples": "10 raw -> 7 merged -> 3 fractals; FIRST 2/5/8, LAST 3/6/8; tail snapshots 10/7/2 and 11/8/3",
    "finite_arithmetic_sequences": examples["finite_model_sequences"],
    "finite_arithmetic_windows": examples["finite_model_windows"],
    "output_trace_corruption_probes_rejected": 8,
    "review": "Independent numerical and helper/pseudocode reviews PASS",
    "scope": "Documentation and finite arithmetic witnesses; no production Fenxing/CC execution or general proof",
}
(FOLDER / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False, indent=2))
