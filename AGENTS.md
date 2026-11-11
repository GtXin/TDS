# TDS project instructions

Read [project memory](CodexMemory.md), [the shared MAS workflow](mas/README.md), [task/result format](mas/contracts.md), and [current folder decision](docs/memo/memoWX_004_projectAndMAS.md) before project work.

- Follow the active user request and recorded decisions; keep discussion notes in `docs/memo/` concise.
- Keep shared algorithm code in `src/chanlab/algo/` independent of the API and website. Backend endpoints and experiments use that same implementation.
- Preserve original references and raw datasets with source information. Put generated outputs in `artifacts/`, including MAS run outputs in `artifacts/mas/`.
- Use `mas/contracts.md` for MAS experiment and delegated-task records in `mas/tasks/`. Record actual checks, evidence, blockers, and the next action.
- Specific agent identities, roles, and skills are not selected yet. Keep the shared directories generic until a task or experiment establishes those choices.
- Native Codex agent definitions belong in `.codex/agents/`; shared role instructions belong in `mas/roles/` and must be explicitly read when used.
- `.agents/skills` points to `mas/skills`. Author shared skills there, with one folder containing `SKILL.md` per skill, and avoid duplicate procedure copies.
- For delegated work, pass the goal, relevant paths, allowed changes, and acceptance checks explicitly. Coordinate simultaneous writes through file ownership or worktrees.
- Runtime permissions and approval settings govern tool access; role instructions do not replace those controls.

## Memo writing

- Memo028 is the implementation and validation plan derived from memo029, the algorithm specification. Work on memo028, its implementation, or validation must follow memo029 and must not modify memo029 unless the user explicitly requests a specification change. Record unresolved conflicts and ask the user instead of silently changing the specification.

Keep exploratory discussion in chat/terminal. Edit memos only when requested; record only essential conclusions, decisions, and necessary references, without conversational commentary, research narration, or repeated explanations.

Before creating or editing memos in `docs/memo/`, read and follow [the memo writing guide](docs/memo/memoWX_006_memoWritingGuide.md). Check [the memo index](docs/memo/README.md) and existing filenames before assigning a number, and update the index when adding or renaming a memo.

## Project memory

Read `CodexMemory.md` at the start of work. Update it after confirmed decisions, meaningful task results, or handoffs; retain current context, reasons, blockers, and next action, and replace stale details with links to evidence. Keep detailed writing rules in memo 006 and event history in `logXW.md`.

## Repository event log

**Every repository update must also be recorded in `logXW.md` before reporting it complete, including code, documentation, configuration, and memory changes.**

Follow [logXW.md](logXW.md) and append a concise entry for each repository work event, including minor edits, decisions, checks, failures, and blockers. Record events before finishing the turn; distinguish observed actions from reported or planned actions.
