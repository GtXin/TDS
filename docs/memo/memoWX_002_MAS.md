# memoWX_002_MAS — Long-term multiagent system for Codex and Claude
## 000 — Background
We are working in this folder to build a multi-agent system compatible with both Codex and Claude.
## 001 — Key Codex concepts
### 1. Orchestration
Codex spawns workers, routes follow-up instructions, waits for results, and combines them. Use parallel workers for independent jobs.
**Simple:** The teacher assigns jobs and puts everyone's work together.
### 2. Main agent / lead agent
The main agent coordinates delegated work and produces the final result. Here, lead agent means that coordinating role.
**Simple:** The captain assigns jobs and checks the finished castle.
### 3. Subagents
A subagent is a delegated worker handling a bounded task in its own agent thread. Workers can investigate or implement different parts in parallel.
**Simple:** Give each helper one part of the castle to build.
### 4. Agent threads and lifecycle
Each worker has an agent thread for its work and results. Ask Codex to send follow-up instructions, stop workers, or close completed threads.
**Simple:** Give each helper a notebook and tell them when to stop.
### 5. Custom agent definitions — `.codex/agents/`
Project agents use TOML files in `.codex/agents/`. These define named roles, instructions, and optional model or reasoning settings.
**Simple:** Each helper gets a job card suited to their work.
### 6. Context and handoffs
Delegation keeps lengthy exploration out of the main conversation. Give workers clear scope and ask for findings, evidence, and unresolved issues.
**Simple:** Give a helper their own notebook and ask for the answer.
### 7. Parallel work and file ownership
Separate agent threads do not guarantee separate files. Assign file ownership or use separate Git worktrees to isolate simultaneous edits.
**Simple:** Separate notebooks do not stop two children painting the same wall.
### 8. Execution controls
Subagents inherit the parent's sandbox and approval settings. Configuration under `[agents]` can limit concurrency and set default worker models.
**Simple:** Helpers follow the same house rules, with a limit on helpers.
## 002 — Key Claude concepts
### 1. Orchestration
Orchestration means dividing work, assigning agents, and combining their results. Independent jobs can run together; dependent jobs run in order.
**Simple:** The teacher decides who builds each part of the castle.
### 2. Main agent / lead agent
The main agent delegates work and combines the results. In an agent team, this coordinating session is called the team lead.
**Simple:** The captain gives everyone a job and checks the finished castle.
### 3. Subagents
A subagent handles a focused job in its own context and reports back. Use one for research, coding, or review.
**Simple:** A helper finds the right blocks and brings them back.
### 4. Agent teams and teammates
An agent team has separate Claude sessions called teammates that can communicate directly. Teams are experimental and disabled by default.
**Simple:** Several children build different parts and talk to each other.
### 5. Custom agent definitions — `.claude/agents/`
A custom agent file defines a worker's role, instructions, tools, and model. Store project-specific definitions in `.claude/agents/`.
**Simple:** Give each helper a job card and the right tools.
### 6. Context and handoffs
Agents have their own context; teammates do not inherit the lead's conversation history. Pass the goal, relevant files, constraints, and expected result explicitly.
**Simple:** Give each helper their own picture and explain their part.
### 7. Task ownership and dependencies
Where Task tools are available, a shared task list tracks owners, progress, and dependencies. Agents without those tools coordinate through messages.
**Simple:** The job board says who builds the walls before the roof.
### 8. Agent messaging
Teammates send messages to share findings, ask questions, and coordinate work. Named subagents can also exchange messages.
**Simple:** Tell the other builder when your part is ready.
## 003 — Codex and Claude: three main comparisons
### 1. Coordination: shared delegation, different team models
Both support a main agent delegating bounded work to parallel subagents and combining the results. Codex documents subagent threads with follow-up instructions, waiting, and lifecycle controls. Claude also offers experimental agent teams, disabled by default, with independent teammate sessions, direct messaging, and shared tasks where Task tools are available. For our system, a coordinator with delegated workers is the common starting point.
### 2. Custom roles: shared responsibilities, different configuration
Both support reusable specialist roles, instructions, and model choices. Codex project agents use TOML files in `.codex/agents/`; Claude project agents use Markdown files with YAML frontmatter in `.claude/agents/`. A role's purpose can be shared, but the native configuration files are not interchangeable. Keep the common role description in one document and give each tool its own configuration.
### 3. Execution boundaries: permissions and file isolation
Both need explicit control over tools, permissions, and concurrent edits. Codex subagents inherit parent sandbox and approval settings, while Claude subagents can declare tools and a permission mode subject to parent-mode and managed-policy restrictions. A separate context window in either product does not by itself isolate project files. Give simultaneous writers separate worktrees or clear file ownership, and verify the combined changes.
## 004 — MAS folder structure: now and later
### 1. Now — shared core only
Keep the structure independent of any agent tool, with no specific agents, roles, or skills defined yet.
```text
TDS/
├── mas/
│   ├── README.md              # Workflow overview
│   ├── roles/                 # Future shared responsibilities
│   ├── skills/                # Future reusable procedures
│   ├── contracts.md           # Common task and result format
│   └── tasks/                 # Task and handoff records
├── artifacts/mas/             # Generated run outputs
└── docs/memo/                 # Discussions and decisions
```
### 2. Later — connect Codex to the same core
Add Codex's native files and skill links when ready; keep the shared core in place.
```text
TDS/
├── mas/
│   ├── README.md
│   ├── roles/
│   ├── skills/
│   ├── contracts.md
│   └── tasks/
├── AGENTS.md                  # Entry point to the shared workflow
├── .codex/
│   ├── config.toml            # Runtime settings, when needed
│   └── agents/                # Native definitions, chosen later
├── .agents/skills/            # Links to shared skill folders
├── artifacts/mas/
└── docs/memo/
```
**Note:** These trees show proposed MAS-related paths only; existing project folders remain unchanged. Agent choices and Codex setup are deferred, and Claude can connect to the same core afterward.
## 005 — How the shared MAS works
### 1. One core, two tool connections
- **Workflow:** future `AGENTS.md` and `CLAUDE.md` entry points will point to `mas/README.md`.
- **Roles:** future native agent definitions read shared instructions from `mas/roles/`.
- **Skills:** `.agents/skills/` or `.claude/skills/` link to procedures in `mas/skills/` once defined.
- **Tasks:** both use `mas/tasks/` and the format in `mas/contracts.md`.
### 2. Who does what
Agent identities, responsibilities, and assignments remain open for experimentation. The folder layout provides places to record those choices without deciding them now.
### 3. Hello-world example
This illustrates a task and acceptance check only; it defines no agent or skill:
```text
Task: Produce a text artifact.
Expected content: exactly "Hello, MAS!\n" in UTF-8.
Acceptance: the saved bytes match the expected content.
Result: record the output path, check result, and next action.
```
Choose an agent and procedure when running the experiment, then check and record the result.
### 4. What equivalent means
Codex and Claude connections should apply the same chosen responsibilities, procedures, and acceptance checks. Test that equivalence when introducing Claude.
