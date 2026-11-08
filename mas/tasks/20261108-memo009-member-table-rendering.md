# Task
- **ID:** 20261108-memo009-member-table-rendering
- **Goal:** Fix Markdown rendering of002.r and the same adjacent table-boundary defect.
- **Inputs:** Memo009; memo006; current memory and reported rendering failure.
- **Allowed changes:** Root owns memo009 whitespace, exact backup, this task and logXW.md. Reviewer read-only; field content/CSVs unchanged.
- **Acceptance checks:** Member tables parse as three-column tables; exact non-whitespace content preservation; local section scope; git diff --check; independent review.
- **Assignment:** Root edits; essential_memo_check reviews the table boundary fix read-only.
- **Status:** done

# Result and handoff
- **Outcome:** Added the required prose/table separators in002.r and002.p; no cells or other content changed.
- **Evidence:** Exact backup docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_030130_930746.md. Precisely2 blank lines added. Marked GFM parsing passed three-column tables with11/10 data rows respectively; actual Obsidian live-preview accessibility state confirmed both rendered tables, including all11 BuySellPoint rows. Independent reviewer passed minimal scope, unchanged CSV hashes and git diff --check. Parser also accepted the old source, so UI verification supplies the observed final result.
- **Blockers:** None.
- **Next action:** none
