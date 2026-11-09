# Task

- **ID:** 20261109-memo015-helper-functions
- **Goal:** Fill memo015002.c with necessary helper-function contracts supporting the current tree and examples.
- **Inputs:** User request “now do 2.c any helper functions?”; memo015001/002.a/b; memo006; memo009 MergedKline/MergedKlineSeries design; actual Kline/KlineTSeries and ChanTable interfaces; computer-scientist skill.
- **Allowed changes:** Only memo015002.c and its required backup, this task, project memory and event log. Preserve001,002.a/b/d, appendices, source/figures and production code.
- **Acceptance checks:** Proposed function names, inputs/outputs, preconditions and side effects explicit; inclusion symmetric; direction helper enforces noninclusion; aggregate merge preserves direction and half-open contiguous source; outer merge retains None; main loop exclusively owns counters/appends/ID allocation; no invented initialization/warning/status default; immutable raw preserved. Read-only contract review, exact outside-section preservation, backup/index/format checks and git diff --check.
- **Assignment:** Root owns all writes; review_002c_contracts independently audits contracts and interface boundaries read-only.
- **Status:** running.

## Result and handoff

- **Outcome:** Drafting a small set of geometry, source-construction and result-validation helpers. No implementation requested.
- **Evidence:** Read current tree/examples and actual raw/table classes; review pending.
- **Blockers:** None for documenting contracts. Default initialization, warning comparison and confirmation/status rules remain undefined/unselected.
- **Next action:** Review the draft, back up and insert only002.c, then record checks.
