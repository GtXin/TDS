# Memo reference format
## Task
- **ID:** 20261107-memo-reference-format
- **Goal:** Replace memo 008’s vague citation labels with bracketed numbers and visible source locations; record the convention in memo 006.
- **Inputs:** User’s citation preference; memos 006/008 and existing source links.
- **Allowed changes:** Memos 006/008, their backups, root memory/log, and this task record; preserve figures and technical prose.
- **Acceptance checks:** Four citations in first-use order; four matching reference paths resolve; concise guide rule; original explanations and pictures preserved; backups exist.
- **Assignment:** Root edits; `reference_style_review` checks the proposed format read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Memo 008 uses [1]–[4] with explicit source paths; memo 006 records the convention. Read-only reviewer confirmed matching references and ordinary Markdown/Obsidian compatibility.
- **Evidence:** Memos 006/008 and timestamped backups; Python checks passed for citation order, source mapping, valid paths, preserved technical prose/picture links, and guide-only section 004 changes. `git diff --check` passed.
- **Blockers:** none.
- **Next action:** none; citation-format change complete.
