# Shared MAS core

This folder keeps workflow and task records independent of the tool used to execute them. Specific agents, responsibilities, and additional skills are chosen through experiments.

## Contents

- `roles/`: shared responsibility descriptions, once defined.
- `skills/`: reusable procedures; Python Pro is installed for the first coding trial.
- [contracts.md](contracts.md): the common task and result format.
- `tasks/`: assignments, progress, evidence, and handoffs.

## Workflow

1. Record the goal, inputs, allowed changes, and acceptance checks in a task file.
2. Choose the assignment and execution method for that task.
3. Perform the work and record the actual checks, evidence, and blockers.
4. Check the result against the acceptance criteria and record the outcome and next action.

Use repository-relative paths. Keep application code in `src/chanlab/`, generated MAS outputs in `artifacts/mas/`, and design discussions in `docs/memo/`.

Task files preserve state and handoffs; they do not automatically schedule work or synchronize concurrent edits.

## Codex connection

- Root [AGENTS.md](../AGENTS.md) directs Codex to this workflow and the task/result format.
- `.codex/config.toml` enables subagent support; model and permission settings remain inherited from the current runtime.
- `.codex/agents/` is reserved for native definitions once agents are chosen.
- `.agents/skills` is a relative directory link to `mas/skills`, keeping one shared source for skill procedures.

Agent definitions and role descriptions remain unselected. [Python Pro](skills/python-pro/SKILL.md) is the first installed skill; its [installation and trial task](tasks/20261108-python-pro-install-and-trial.md) records source and check results. Claude can connect to this same core separately.
