# Computer Scientist installation

## Task
- **ID:** 20261109-computer-scientist-install
- **Goal:** Install selected skill and restructure memo017 following016, moving old001 to appendix.
- **Inputs:** User request, memo006/016/017, skill-installer.
- **Allowed changes:** mas/skills/computer-scientist/, memo017 and backup, task, memory, log.
- **Acceptance checks:** Installer success; metadata, discovery link, memo sections and preserved candidate table; whitespace check.
- **Assignment:** Codex.
- **Status:** done.

## Result and handoff
- **Outcome:** Installed upstream1.0.0 at commit 98c7fae46648724e1a43a1f2b207b0c82fcc462e; memo017 reorganized into000–005 plus Appendix A and References.
- **Evidence:** Installer returned success; name/version/MIT metadata inspected; .agents/skills resolves to ../mas/skills; SKILL.md SHA-256 a01d128d71edf520d28d5576558699f02bc641fff1f18f0242eac4927c5fd632. Original candidate table preserved exactly; memo backup saved. No third-party code executed or dependencies added.
- **Blockers:** none for installation; UI discovery and behavior not tested.
- **Next action:** Invoke skill next turn with memo017 section003 prompt to evaluate definition-to-algorithm output.
