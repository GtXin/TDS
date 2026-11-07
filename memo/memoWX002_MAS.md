# memoWX002_MAS — Long-term multiagent system for Codex and Claude

## 000 — Background and recommendation

Date: November 7, 2026. Status: proposal.

A multi-agent system (MAS) is a team of AI agents working toward one goal. Codex and Claude Code can help with different parts of a project, using shared notes to explain the work and pass it to the next agent.

Start with one agent for small tasks. For larger tasks, assign someone to coordinate, someone to build, and someone to check the result. Keep important instructions and decisions in the project so either tool can pick up the work.

**Kindergarten explanation:** A small team builds a castle together: one child plans, one builds, and one checks that it stands.

## 001 — What exists in this repository

TDS currently contains a `memo/` directory and Obsidian configuration, alongside Git metadata. The existing `memoWX_001.md` describes the structure of a separate project, `proj009`; that source tree is not present in this checkout.

Use TDS initially as the design and operating handbook. When applying this workflow to a code repository, place that project's instructions and task records alongside its code. Keep general policy reusable, but let each project own its commands, constraints, and acceptance criteria. Do not make agents depend on an absolute path to this vault.

## 002 — Seven key MAS concepts

These concepts are a practical 80/20 starting point for working with agents; the percentage is a learning guide, not a measured usage statistic. Codex supports delegating tasks to subagents and collecting their results; see the [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

### 1. Agents and roles

An agent is an AI worker that follows instructions and uses tools. Give each agent a clear responsibility, such as researching, building, or reviewing.

**Kindergarten explanation:** One friend draws, one colors, and one checks the picture.

### 2. Task decomposition — break the work into pieces

Split a large goal into small tasks with clear results. Each task should say what to do, what it may change, and how to tell when it is finished.

**Kindergarten explanation:** One child makes the castle walls, and another makes the towers.

### 3. Orchestration — coordinate the team

A coordinator assigns tasks, tracks progress, and brings the results together. Give one coordinator responsibility for deciding whether the whole job is complete.

**Kindergarten explanation:** The teacher gives everyone a job and puts their work together.

### 4. Parallel work and dependencies

Independent tasks can happen at the same time. A task that needs another task's result must wait, so extra agents help most when their jobs can proceed separately.

**Kindergarten explanation:** Two children can gather blocks together, but the roof needs walls first.

### 5. Context and handoffs

Context is the goal, instructions, files, and decisions an agent needs to do its job. A handoff tells the next agent what changed, what was checked, and what still needs work.

**Kindergarten explanation:** Give your friend the right blocks and explain what you have already built.

### 6. Ownership and isolation

Decide which files or parts of the project each agent owns. Separate worktrees give simultaneous writers their own copies, but the team still needs to coordinate changes that overlap.

**Kindergarten explanation:** Each child builds on their own mat, and they agree where the pieces will connect.

### 7. Verification and integration

Check each result, then combine the pieces and check that they work together. A task is complete when the combined result meets the goal and passes the relevant checks.

**Kindergarten explanation:** Join the train tracks, then run the train around to see whether everything connects.

## 003 — Roles and authority

| Role | Responsibility | Expected output |
| --- | --- | --- |
| Coordinator | Clarify scope, divide work, assign ownership, reconcile results | Task plan and integrated result |
| Implementer | Complete a bounded change and run relevant checks | Patch or commit plus validation evidence |
| Reviewer | Independently assess correctness, scope, and evidence | Actionable findings or approval with limitations |

The coordinator is the sole integration owner for a task. Workers should not independently merge competing changes into the integration branch. A reviewer should normally inspect without modifying the implementation; assign repairs explicitly when needed.

Use three roles as responsibilities, not three permanently running processes. Small tasks can use one agent. For substantial changes, a second agent or the other vendor can review independently. Parallelize independent research or separate modules; keep tightly coupled changes sequential.

## 004 — Work isolation and handoffs

Give each simultaneous writing worker its own Git worktree and branch. Assign explicit file or module ownership even with worktrees: isolation prevents overwriting local edits, but does not eliminate conflicting designs or merge conflicts. Read-only research agents can share a checkout when the runtime permits it.

Worktrees share Git metadata. Coordinate branch operations, avoid destructive repository-wide commands, and separate generated outputs, local services, and test resources when concurrent runs would interfere.

Each task record should contain:

```text
Task ID and objective:
Acceptance criteria:
Coordinator and current worker:
Status: proposed | ready | running | review | done | blocked
Base commit, branch, and worktree:
Allowed files or modules:
Dependencies and interface agreements:
Validation commands and actual results:
Changed files and output commit:
Open questions, blockers, and next action:
```

Begin with coordinator-owned updates to task status. Separate worktrees do not provide a live shared Markdown queue: committed records become visible through normal Git integration. If live scheduling later becomes necessary, add an external transactional queue with atomic task claims, leases, and recovery from abandoned workers.

For a Codex-to-Claude handoff, provide the task record, base and output commits, relevant paths, test evidence, and unresolved issues. Chat summaries alone are insufficient. Start with manual handoffs; native subagents in one product should not be assumed to launch or control the other product.

## 005 — Memory and reusable knowledge

Keep four kinds of information distinct:

- Instructions: stable rules and commands in entry points and shared guidance.
- Task state: ownership, progress, and evidence in the task record.
- Decisions: the chosen approach, rationale, and consequences in decision notes.
- Temporary material: logs and generated outputs outside permanent instructions.

Treat chat history and vendor-specific agent memory as convenience layers. Promote useful findings into reviewed repository documents so either tool can resume work. Record a source or commit for important conclusions and update stale guidance when behavior changes. Keep credentials outside tracked documents.

## 006 — Adoption plan

### Phase 1: Manual, small, observable

Create the two entry points, shared operating model, three role descriptions, and one task template in the target code repository. Complete one real task using one implementer and an independent reviewer. Use manual launches and explicit handoffs. This tests whether the protocol is useful before automation adds complexity.

### Phase 2: Native delegation

Add each tool's native subagent configuration for recurring roles. Verify which instructions and tools workers actually receive. Pass task scope, constraints, and required outputs explicitly. Set a small concurrency limit and prevent unbounded delegation. Keep cross-vendor handoffs explicit.

### Phase 3: Lightweight orchestration

After several successful tasks, add helpers for creating worktrees, validating task records, collecting results, and cleaning up completed work. A cross-vendor runner should use supported execution interfaces and handle cancellation, timeouts, retries, logs, authentication, and budgets. Add a database or orchestration framework only when observed scheduling or recovery needs justify it.

## 007 — How to judge success

Track accepted-task completion time, review defects, rework, merge conflicts, human interventions, and usage cost where available. Compare a few similar tasks completed by one agent with tasks completed through the multiagent workflow. Keep delegation where it improves outcomes enough to justify coordination overhead.

For `proj009`, a useful first trial would be one bounded data-validation change with explicit input cases and an independent review. Confirm the actual repository and its existing instructions before implementing anything there. Research claims should preserve dataset version, parameters, and reproducible commands; a reviewer should check evidence as well as code.

## 008 — Documentation basis and limits

The architecture above is a recommendation, not a claim that the two products share a native orchestration protocol. Tool behavior and available settings depend on the installed version and environment.

- [OpenAI customization documentation](https://learn.chatgpt.com/docs/customization/overview): repository instructions and reusable skills.
- [OpenAI subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents): native delegation and custom agents.
- [Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents): native agent definitions, capabilities, and execution behavior.

Before implementation, verify the installed Codex and Claude Code configuration schemas. Do not copy configuration fields between them solely because their roles have the same names.
