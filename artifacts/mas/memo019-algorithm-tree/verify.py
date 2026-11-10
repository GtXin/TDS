"""Scoped documentation checks and independent finite-model checks, not detector tests."""

import hashlib
import itertools
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
FOLDER = Path(__file__).resolve().parent
MEMO = ROOT / "docs/memo/memoWX_019_Chan_fenxing.md"
START = "### 002.a — Algorithm Tree\n"
END = "### 002.b — Detailed Implementation logic and Numerical Examples\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def outside(text):
    a = text.index(START)
    b = text.index(END, a)
    return text[:a] + text[b:]


def direction(a, b):
    if b[0] > a[0] and b[1] > a[1]:
        return 1
    if b[0] < a[0] and b[1] < a[1]:
        return -1
    return None


def reference(a, b, c):
    if b[1] > a[1] and b[1] > c[1] and b[0] > a[0] and b[0] > c[0]:
        return "top"
    if b[1] < a[1] and b[1] < c[1] and b[0] < a[0] and b[0] < c[0]:
        return "bottom"
    return None


edit = json.loads((FOLDER / "edit.json").read_text())
before = (ROOT / edit["backup"]).read_bytes()
after = MEMO.read_bytes()
assert digest(before) == edit["before_sha256"]
assert digest(after) == edit["after_sha256"]
for backup in edit.get("followup_backups", []):
    assert digest((ROOT / backup["path"]).read_bytes()) == backup["sha256"]
assert outside(before.decode()) == outside(after.decode())
assert digest(outside(before.decode()).encode()) == edit["outside_section_sha256"]
text = after.decode()
section = text[text.index(START) : text.index(END)]
assert section == (FOLDER / "section002a.md").read_text()
assert section.count("```") == 2
definitions = re.findall(r"(?m)^[ │├└─]*(2\.\d+(?:\.[a-z])?)\s", section)
assert len(definitions) == len(set(definitions))
targets = re.findall(r"(?:转|回|进入)(2\.\d+(?:\.[a-z])?)", section)
assert set(targets) <= set(definitions)
record_table = section.split("Fenxing沿用memo009的8个成员", 1)[1].split("FenxingSeries沿用6个成员", 1)[0]
record_fields = re.findall(r"(?m)^\| `([^`]+)`", record_table)
expected_record = ["id", "kind", "price", "anchor_raw_index", "source_start", "source_stop", "status", "confirmed_at"]
assert record_fields == expected_record
series_fields = ["source_series", "items", "config", "rule_tree_ref", "trace", "trace_by_point"]
assert "`" + "、".join(series_fields) + "`" in section
source009 = (ROOT / "docs/memo/memoWX_009_designPatternForChanFeatures.md").read_text()
table009 = source009.split("### 002.f — Fenxing\n", 1)[1].split("**Proposed methods**", 1)[0]
assert re.findall(r"(?m)^\| `([^`]+)`", table009) == record_fields
series009 = source009.split("### 002.g — FenxingSeries\n", 1)[1].split("**Proposed methods**", 1)[0]
assert all(f"`{field}`" in series009 for field in series_fields)
for table in re.findall(r"(?m)(?:^\|.*\n)+", section):
    widths = [len(re.split(r"(?<!\\)\|", row)) for row in table.strip().splitlines()]
    assert len(set(widths)) == 1
links = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
for link in links:
    url = urlsplit(link)
    if not url.scheme and url.path:
        assert (MEMO.parent / unquote(url.path)).exists(), link
index = (ROOT / "docs/memo/README.md").read_text()
assert index.count("(memoWX_019_Chan_fenxing.md)") == 1
protected = json.loads((FOLDER / "protected_before.json").read_text())
for path, value in protected.items():
    if path != str(MEMO.relative_to(ROOT)):
        assert digest((ROOT / path).read_bytes()) == value, path

# All small valid sequences, including one-price intervals, short input,
# overlapping hits, monotone non-hits, and both reversal directions.
pool = [(low, high) for low in range(4) for high in range(low, 4)]
sequences = 0
windows = 0
branches = {"top": 0, "bottom": 0, "up_up": 0, "down_down": 0}
for size in range(1, 6):
    for bars in itertools.product(pool, repeat=size):
        if any(direction(a, b) is None for a, b in zip(bars, bars[1:])):
            continue
        sequences += 1
        results = []
        trace = []
        mappings = []
        expected = []
        i = 1
        while i < size - 1:
            a, b, c = bars[i - 1 : i + 2]
            pair = (direction(a, b), direction(b, c))
            kind = {(1, -1): "top", (-1, 1): "bottom"}.get(pair)
            assert kind == reference(a, b, c)
            branches[kind or ("up_up" if pair == (1, 1) else "down_down")] += 1
            trace.append((i, kind))
            if kind:
                results.append((len(results), kind, i - 1, i + 2))
                mappings.append((len(trace) - 1,))
            i += 1
        for center in range(1, size - 1):
            kind = reference(*bars[center - 1 : center + 2])
            if kind:
                expected.append((len(expected), kind, center - 1, center + 2))
        assert results == expected
        assert len(trace) == max(size - 2, 0)
        assert len(results) == len(mappings)
        assert all(mappings[j] and all(0 <= t < len(trace) for t in mappings[j]) for j in range(len(results)))
        windows += len(trace)
assert all(branches.values())

# A merged center displayed at raw1 has matching highs only at raw2/raw3.
raw = [(0, 3), (2, 5), (1, 6), (3, 6), (1, 4)]
anchors = [j for j in range(1, 4) if raw[j][1] == 6]
assert anchors == [2, 3] and min(anchors) != 1
assert reference((0, 3), (3, 6), (1, 4)) == "top"
mirrored = [(-high, -low) for low, high in raw]
assert [j for j in range(1, 4) if mirrored[j][0] == -6] == [2, 3]
assert reference((-3, 0), (-6, -3), (-4, -1)) == "bottom"
assert [j for j in range(1, 4) if raw[j][1] == 7] == []
assert [j for j in range(1, 3) if raw[j][1] == 6] == [2]

report = {
    "scope": "Documentation preservation, static contracts and independent finite arithmetic model; no production Fenxing code or CC execution",
    "backup_verified": True,
    "backup_count": 1 + len(edit.get("followup_backups", [])),
    "outside_002a_preserved": True,
    "protected_other_files": len(protected) - 1,
    "record_fields": record_fields,
    "series_fields": series_fields,
    "unique_tree_nodes": len(definitions),
    "goto_targets_resolve": True,
    "local_links_checked": len(links),
    "tables_and_fences": "pass",
    "finite_model_valid_sequences": sequences,
    "finite_model_windows": windows,
    "branches": branches,
    "anchor_zero_single_multiple_and_display_distinction": "pass",
}
(FOLDER / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, ensure_ascii=False, indent=2))
