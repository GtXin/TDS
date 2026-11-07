# Shared MAS core

This folder keeps workflow and task records independent of the tool used to execute them. Specific agents, responsibilities, and skills will be chosen through later experiments.

## Contents

- `roles/`: shared responsibility descriptions, once defined.
- `skills/`: reusable procedures, once defined.
- [contracts.md](contracts.md): the common task and result format.
- `tasks/`: assignments, progress, evidence, and handoffs.

## Workflow

1. Record the goal, inputs, allowed changes, and acceptance checks in a task file.
2. Choose the assignment and execution method for that task.
3. Perform the work and record the actual checks, evidence, and blockers.
4. Check the result against the acceptance criteria and record the outcome and next action.

Use repository-relative paths. Keep application code in `src/chanlab/`, generated MAS outputs in `artifacts/mas/`, and design discussions in `docs/memo/`.

Task files preserve state and handoffs; they do not automatically schedule work or synchronize concurrent edits. Native tool configuration and runtime controls will be added separately.
