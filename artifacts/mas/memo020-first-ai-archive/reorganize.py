"""Archive memo020's first AI draft while preserving user/source text."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MEMO = ROOT / "docs/memo/memoWX_020_Chan_bi.md"
H2 = "## 002 — Algorithm (How)\n"
H3 = "## 003 — Reasoning (Why)\n"
H4 = "## 004 — Other Notes\n"
HA = "### 002.a — Algorithm Tree\n"
REFS = "## References\n"
INSTRUCTION = "第一轮只给我最小主流程和一个完整例子，先不写代码或修改 memo。"
TITLE = "## Appendix C — 第一轮 AI 方案\n"
LABELS = {
    "002.a": "C.1",
    "002.b": "C.2",
    "002.c": "C.3",
    "002.d": "C.4",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


original = MEMO.read_bytes()
text = original.decode("utf-8")
assert TITLE not in text, "Already reorganized; do not repeat."
before_002, rest = text.split(H2, 1)
body, after_002 = rest.split(H3, 1)
assert body.count(INSTRUCTION) == 1
user_note = body[body.index("一定保留这一段：") : body.index(HA)]
old_algorithm = body[body.index(HA) :]
archived = old_algorithm.replace(INSTRUCTION + "\n\n", "", 1)
for old, new in LABELS.items():
    archived = archived.replace(old, new)
archived = archived.replace("### C.1 — Algorithm Tree\n\n\n\n", "### C.1 — Algorithm Tree\n\n", 1)
archived = archived.strip("\n") + "\n\n"

empty_002 = "".join(
    heading + "\n\n"
    for heading in (
        "### 002.a — Algorithm Tree",
        "### 002.b — Detailed Implementation logic and Numerical Examples",
        "### 002.c — Helper Functions",
        "### 002.d — Pseudocode",
    )
)
assert after_002.count(H4 + "\n") == 1
rest = H3 + after_002.replace(
    H4 + "\n",
    H4 + "\n### 用户算法草案与协作提示词\n\n" + user_note + INSTRUCTION + "\n\n",
    1,
)
archive_intro = (
    TITLE + "\n"
    "本附录归档原002.a–002.d的第一轮AI候选路线方案。以下原稿保留当时的算法、数值、接口和核验记录；"
    "其状态描述属于历史草案，不作为当前正文002的算法规范。下一轮以004保留的用户草案为基础讨论。\n\n"
)
review = """### C.5 — 复盘与下一轮方向

1. **第一轮定位。** 以受选择规则约束的候选路线搜索为核心：固定首个可合格起点，保留首笔终点及同价端点备选，受阻后恢复路径。它不枚举六项定义允许的全部几何子集，也未证明等同于作者的唯一划笔规则。
2. **已知局限。** 一段历史可合法成笔，不保证整条路线能按旧协议处理到输入末尾；旧方案可能只留下阻塞历史而没有可行候选。已有同起点几何路线的样例，也暴露了选择策略与持续画笔目标的差距，见[诊断记录](../../artifacts/mas/bi-algorithm-review/README.md)。
3. **按阶段验证用户草案。** 初始化2.b只判断是否替换当前待定起点；较弱同型点不替换当前起点是自洽的局部策略，不能仅凭另有合法配对就判定该动作错误。下一轮先沿“选起点、缓存首笔、端点延伸、反向成笔后滚动”推演，分别核验5.b的失败处理及6.a记入结果后的撤回条件，再补必要恢复规则。
4. **提案与实现边界。** “合格反向点同时保存采用／跳过两支”是后来提出、尚未采纳的建议，不是下列第一轮原稿已有的分支。现有memo028及Bi实现仍对应已归档的第一轮协议；本次清空002只调整文档，不代表用户新框架已经实现。

"""
assert rest.count(REFS) == 1
new_text = before_002 + H2 + "\n" + empty_002 + rest.replace(
    REFS, archive_intro + archived + review + REFS, 1
)

# Verify all intended transformations before touching the memo.
assert new_text[: new_text.index(H2)] == before_002
assert new_text.split(H2, 1)[1].split(H3, 1)[0].strip() == empty_002.strip()
assert user_note in new_text.split(H4, 1)[1].split("## 005", 1)[0]
assert new_text.count(INSTRUCTION) == 1
assert text.split("## Appendix A", 1)[1].split(REFS, 1)[0] == new_text.split("## Appendix A", 1)[1].split(TITLE, 1)[0]
assert text.split(REFS, 1)[1] == new_text.split(REFS, 1)[1]
assert sorted(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)) == sorted(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", new_text))

protected = [
    "docs/memo/README.md",
    "docs/memo/memoWX_028_biFamily.md",
    "src/chanlab/algo/bi.py",
    "src/chanlab/data/bi_table.py",
    "src/chanlab/visualization/bi_plot.py",
    "tests/test_bi.py",
]
protected_hashes = {path: sha((ROOT / path).read_bytes()) for path in protected}
timestamp = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y%m%d_%H%M%S_%f")
backup = MEMO.parent / "backups" / f"{MEMO.stem}__{timestamp}.md"
with backup.open("xb") as stream:
    stream.write(original)
assert backup.read_bytes() == original
assert MEMO.read_bytes() == original, "Concurrent user edit detected; leave memo untouched."
MEMO.write_bytes(new_text.encode("utf-8"))
assert MEMO.read_text() == new_text
assert all(sha((ROOT / path).read_bytes()) == digest for path, digest in protected_hashes.items())
report = {
    "backup": str(backup.relative_to(ROOT)),
    "before_sha256": sha(original),
    "after_sha256": sha(MEMO.read_bytes()),
    "backup_byte_identical": True,
    "definitions_unchanged": True,
    "user_note_byte_preserved": True,
    "instruction_preserved_once": True,
    "active_002_headings_only": True,
    "appendix_A_B_and_references_unchanged": True,
    "image_targets_and_occurrence_counts_preserved": True,
    "archive_heading_map": LABELS,
    "archive_normalization": "Move user instruction to004; rename heading/self references; trim section-edge blank lines.",
    "protected_hashes": protected_hashes,
}
(HERE / "edit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"backup": report["backup"], "cleared": "002.a–d", "preserved_user_note": "004", "archive": "Appendix C — 第一轮 AI 方案"}, ensure_ascii=False))
