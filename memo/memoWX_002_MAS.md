# memoWX_002_MAS — Long-term multiagent system for Codex and Claude

## 000 — Background

We are working in this folder to build a multi-agent system compatible with both Codex and Claude.

## 001 — Key Codex concepts

### 1. Agent and task

Codex is an AI helper that can read, edit, and check code. Give it one clear goal.

**Simple:** Tell your helper which toy to build.

### 2. Context

Context is the information Codex uses for a task. Include the relevant files, decisions, and limits.

**Simple:** Show your helper the picture and the right blocks.

### 3. Project instructions — `AGENTS.md`

`AGENTS.md` stores lasting project instructions. Put common rules and commands here.

**Simple:** Put the classroom rules on the wall.

### 4. Tools and connections

Tools let Codex read files, edit code, and run commands. MCP connects it to additional tools and services.

**Simple:** Your helper gets pencils, scissors, and a library card.

### 5. Skills

A skill is a reusable set of instructions for a job. Use it for tasks that follow the same process.

**Simple:** Follow the same recipe to make cookies again.

### 6. Permissions and approvals

Permissions control what Codex can access or change. Approval settings decide when it must ask first.

**Simple:** Ask before using supplies from the locked cupboard.

### 7. Git worktrees

A Git worktree gives an agent its own working copy. Separate copies help keep simultaneous edits apart.

**Simple:** Each helper builds on their own mat.

### 8. Review and verification

Check the changes and run relevant tests. Ask what passed, failed, or remains unverified.

**Simple:** Try the toy before calling it finished.

## 002 — Key Claude concepts

### 1. Agent and task

Claude Code is an AI helper that can read, edit, and check code. Give it one clear goal.

**Simple:** Tell your helper which toy to build.

### 2. Context

Context is the information Claude uses for a task. Include the relevant files, decisions, and limits.

**Simple:** Show your helper the picture and the right blocks.

### 3. Project instructions — `CLAUDE.md`

`CLAUDE.md` stores lasting project instructions. Put common rules and commands here.

**Simple:** Put the classroom rules on the wall.

### 4. Tools and connections

Tools let Claude read files, edit code, and run commands. MCP connects it to additional tools and services.

**Simple:** Your helper gets pencils, scissors, and a library card.

### 5. Skills

A skill stores reusable instructions in a `SKILL.md` file. Claude can load it when needed, or you can invoke it directly.

**Simple:** Follow a recipe instead of explaining every step again.

### 6. Permissions and approvals

Permissions control which actions Claude may take. Approval settings decide when it must ask first.

**Simple:** Ask before using supplies from the locked cupboard.

### 7. Git worktrees

A Git worktree gives a Claude session its own working copy. Separate copies help keep simultaneous edits apart.

**Simple:** Each helper builds on their own mat.

### 8. Review and verification

Check the changes and run relevant tests. Ask what passed, failed, or remains unverified.

**Simple:** Try the toy before calling it finished.
