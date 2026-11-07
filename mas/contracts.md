# Task and result format

Use this format for records in `mas/tasks/`. It is a shared written agreement; validation and execution are not automated yet.

## Task

- **ID:** a unique, stable task identifier.
- **Goal:** the intended result.
- **Inputs:** relevant files, references, and prior decisions.
- **Allowed changes:** permitted paths and scope, including generated outputs.
- **Acceptance checks:** observable conditions and commands used to verify completion.
- **Assignment:** who or what will perform the task; leave unassigned until chosen.
- **Status:** `proposed`, `ready`, `running`, `blocked`, or `done`.

## Result and handoff

- **Outcome:** what was completed and which acceptance criteria remain unmet.
- **Evidence:** changed paths, output locations, actual checks and results, and a commit reference when available.
- **Blockers:** unresolved problems or missing information.
- **Next action:** the concrete step needed to continue, or `none` when complete.

Use repository-relative paths and distinguish planned checks from checks actually run. Mark a task `done` only when its acceptance criteria are met; any required review belongs in those criteria.
