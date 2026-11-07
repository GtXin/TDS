# Codex project memory
## 000 — Purpose
Add project memory to TDS so future Codex sessions can continue from the latest decisions and task state.
## 001 — Implementation
- **Where:** [CodexMemory.md](../../CodexMemory.md) is the repository-root project brief.
- **How Codex finds it:** root [AGENTS.md](../../AGENTS.md) instructs Codex to read it when starting work and update it after a confirmed decision, meaningful task result, or handoff.
- **What to record:** decisions and reasons, current status, blockers, and next action; revise stale information and link detailed memos instead of copying them. Keep the event-by-event history in `logXW.md`.
## 002 — Example memory content
Illustrative content; [the live memory file](../../CodexMemory.md) is maintained separately:
```markdown
# TDS project memory
## Purpose
Refactor the Chan theory algorithm through a three-day feasibility sprint involving KWX and WX.
## Confirmed decisions
- Keep the shared algorithm independent of the API and static website.
- Keep portable MAS workflow, roles, skills, and task records in mas/.
- Codex is connected; specific agent identities and skills remain unselected.
- Memo 006 is the authority for memo writing; logXW.md records repository events.
## Current status
Project scaffold and shared MAS documents are in place.
## Next action
Record the next task and its acceptance checks when its scope is agreed.
```
