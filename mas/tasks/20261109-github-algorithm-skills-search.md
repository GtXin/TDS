# Task

- **ID:** 20261109-github-algorithm-skills-search
- **Goal:** Find GitHub-hosted skills for algorithm development, especially precise assumptions, design, invariants and counterexample-based verification for Chan research.
- **Inputs:** User clarified GitHub search; project skill context; primary GitHub SKILL.md files and repository READMEs.
- **Allowed changes:** This task, project memory and event log only. No installations or changes to memos/skills/code.
- **Acceptance checks:** Open actual candidate SKILL.md; distinguish research/design from document formatting and implementation testing; supply direct source links and assessment limits.
- **Assignment:** Codex root searches design/general algorithm skills; find_algorithm_skills reviewer independently searches verification/specification skills. Read-only; no installs/network execution of third-party code.
- **Status:** done.

## Result and handoff

- **Outcome:** Inspected actual SKILL.md files for computer-scientist, algorithm-design, proptest-praxis, invariant-guard and FSL. Independent reviewer confirmed FSL source-fidelity/assumption-ledger/verification content and heavier native fslc dependency; postfix/z3-verifier-skill appears specification-only rather than a ready skill.
- **Evidence:** Primary GitHub source links below. These are content-based fit assessments, not runtime efficacy evaluations. The invariant-guard community copy is available, but its credited upstream morsechimwai/lemmaly returned404 during inspection. Other algorithm frameworks examined only as scope comparisons.
- **Blockers:** none.
- **Next action:** Report shortlist; installation and a scoped trial require a later user request. No skills installed, no memo/code edits performed.

## Sources inspected

- https://github.com/K-Dense-AI/scientific-agents/blob/main/scientific-agents/computer-scientist/skills/computer-scientist/SKILL.md — explicit models, contracts, invariants, baselines, complexity/evidence; broad CS scope.
- https://github.com/ZeroTokenClaw/agents-skills/blob/main/algorithm-design/SKILL.md — method documentation, LaTeX pseudocode, diagrams and code consistency; less focused on proof/counterexample development.
- https://github.com/inanna-malick/agent-skills/blob/main/skills/proptest-praxis/SKILL.md — independent reference models, stateful generated histories, counterexample shrinking and deterministic regressions; Rust-first, says use equivalent frameworks in other languages.
- https://github.com/sickn33/agentic-awesome-skills/blob/main/plugins/agentic-awesome-skills-claude/skills/invariant-guard/SKILL.md — contract/invariant/termination/edge cases before code; community copy, original linked repository currently unavailable.
- https://github.com/ymm-oss/fsl/blob/main/skills/fsl/SKILL.md — source-faithful formalization, confirmed assumptions, bounded checking/induction and counterexamples; requires FSL/native fslc workflow, not a small standalone instruction set.

No third-party code executed. Branch-tip source inspection only; no revisions pinned or files installed.
