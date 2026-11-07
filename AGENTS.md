# TDS project instructions

Read [the shared MAS workflow](mas/README.md), [task/result format](mas/contracts.md), and [current folder decision](docs/memo/memoWX_004_projectAndMAS.md) before project work.

- Follow the active user request and recorded decisions; keep discussion notes in `docs/memo/` concise.
- Keep shared algorithm code in `src/chanlab/algo/` independent of the API and website. Backend endpoints and experiments use that same implementation.
- Preserve original references and raw datasets with source information. Put generated outputs in `artifacts/`, including MAS run outputs in `artifacts/mas/`.
- Use `mas/contracts.md` for MAS experiment and delegated-task records in `mas/tasks/`. Record actual checks, evidence, blockers, and the next action.
- Specific agent identities, roles, and skills are not selected yet. Keep the shared directories generic until a task or experiment establishes those choices.
- Native Codex agent definitions belong in `.codex/agents/`; shared role instructions belong in `mas/roles/` and must be explicitly read when used.
- `.agents/skills` points to `mas/skills`. Author shared skills there, with one folder containing `SKILL.md` per skill, and avoid duplicate procedure copies.
- For delegated work, pass the goal, relevant paths, allowed changes, and acceptance checks explicitly. Coordinate simultaneous writes through file ownership or worktrees.
- Runtime permissions and approval settings govern tool access; role instructions do not replace those controls.
