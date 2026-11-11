# Task
- **ID:**20261111-memo028-return-to-plan
- **Goal:** Roll back activeBi implementation and return028 to planning001, per explicit user selection.
- **Inputs:**028/currentBi and shared table integrations; project instructions.
- **Allowed changes:**Archive then removeBi-specific source/tests; removeBi branches from shared table integration; backup/reset028; memory/log/task.
- **Acceptance checks:**ArchivedSHA256 match; noBi imports in active src/tests; upstream tests pass;028contains000/001only plusreferences; style/whitespace.
- **Assignment:**Codex directly.
- **Status:**done
# Result and handoff
- **Outcome:** Archived4 removedBi-specific files and2 pre-rollback shared integration files; preserved020/029 and all past evidence. Shared table now supports merged/fractal families with reservedBi columns unchanged.028now planning only.
- **Evidence:**artifacts/mas/bi-family/rollback-20261111_015356_562660;386active tests pass,Ruff/Black/shared modules andgitdiff whitespace pass. Archivedhashesverified.
- **Blockers:**none. Initial archive script stopped before source edits due replacement-pattern mismatch; corrected and reran with fresh archive. A preliminary test run before rollback was not used as rollback evidence.
- **Next action:**Planning001only; confirm algorithm/design before authorizing implementation. HistoricalMAS result records do not authorize rerunning removedBi code.
