# Zhongshu definition discussion
## Task
- **ID:** 20261118-zhongshu-definition-discussion.
- **Goal:** Review established merged-Kline, fractal, stroke and segment definitions; propose a compatible Zhongshu definition in chat.
- **Inputs:** memo015/019/029/030 section001; memo031 completion boundary; memo022 Appendix A/B; original lessons018/020/078/084.
- **Allowed changes:** This task record, CodexMemory.md and logXW.md. Discussion only; no memo or algorithm edits.
- **Acceptance checks:** Identify active definitions; preserve actual segment extrema and confirmed/candidate distinction; separate lowest-level construction from higher-level recursion; label new boundary choices as proposals.
- **Assignment:** Codex root; no delegation.
- **Status:** done.
## Result and handoff
- **Outcome:** Active specifications are015/019/029/030; 031 implements fixed-snapshot confirmed segments with candidate tails separate. Proposed lowest-level segment center: first three consecutive completed alternating segments have a common price interval, fixed during extension. Use full segment high/low rather than raw geometric endpoints. Higher-level centers require completed lower-level movement types.
- **Evidence:** Read the four section001 definitions, 030 closed-interval convention and actual-extrema note, 022 original-definition/extension/recursion/equality notes, 031 snapshot limits, and local078 standardization passage. Web original-text reproductions: https://eczsc.com/originals/78 and https://chanlun108.cn/chanzhongshuochan108ke/84.html . Relevant memo SHA-256 values remained unchanged.
- **Checks:** Confirmed022 main definition still empty; 030 allows closed-interval touch as a project convention, while022 B.5 explicitly leaves zero-width centers undecided. No algorithm execution or completeness claim.
- **Blockers:** None for a discussion proposal. Equality policy, starting phase, candidate grouping and full lifecycle/member boundaries are not adopted specifications.
- **Next action:** Discuss the proposed lowest-level definition and equality convention with the user before recording a formal022 definition or implementing it.

## Follow-up — Segment auxiliary concepts, 2026-11-18
- **Goal:** Apply the user's correction from strokes to segments and add starting/ending segment auxiliary concepts in022 version one.
- **Allowed changes:** User now authorizes the022 auxiliary-definition block, its required full backup, memory, this record and log; preserve the remaining memo and algorithms.
- **Outcome:** Replaced three-stroke overlap with three-segment overlap using actual price ranges. Added starting segment and a provisional ending-segment convention: the segment before departure, confirmed by the subsequent completed return segment remaining outside the fixed interval. Departure/failed return are excluded from that member range. Full Zhongshu definition remains unwritten; the endpoint convention is explicitly provisional.
- **Evidence:** Pre-edit full backup `docs/memo/backups/memoWX_022_Chan_zhongshu__20261118_083053_951883.md`; byte equality and all memo content outside the version-one block verified unchanged.
- **Acceptance checks:** Read back revised text; verify closed-interval touch is still overlap, ending segment differs from confirmation segment, and filename/index stay valid. Scoped `git diff --check` passed; filename/index verified. No algorithm tests required or run for this text-only edit.
- **Status:** done.
- **Blockers:** None for this edit; final membership/boundary convention remains a discussion item.
- **Next action:** Discuss the provisional endpoint convention and formal Zhongshu definition.

- **User clarification:** The next center's starting segment must not be the previous center's ending segment. Added this explicit same-level version-one constraint; it does not prescribe that the immediately following segment must be selected. Backed up022 before the one-bullet edit and verified all other memo text unchanged.

## Follow-up — Rectangle definition and corrected ending segment, 2026-11-18
- **Goal:** Define the center's four sides from price bounds and starting/ending segment intersections, as requested by the user.
- **Allowed changes:** 022 version-one definitions and necessary005 pending items, full backups, memory, this task and log. Preserve algorithms and original/CC appendices.
- **Outcome:** User chose outer crossing times: first entry of the starting segment for the left vertical, last exit of the ending segment for the right vertical. Upper/lower bounds remain fixed by the initial three completed continuous segments. User then corrected the missing-exit case: the actual departure segment is the ending segment, superseding the earlier pre-departure convention. A completed following return outside the core confirms it; that return is not a member. Departure may be the initial third segment or a later one. The next center cannot reuse the preceding ending segment as its start.
- **Evidence:** Full pre-edit backups `docs/memo/backups/memoWX_022_Chan_zhongshu__20261118_083952_247314.md` and `docs/memo/backups/memoWX_022_Chan_zhongshu__20261118_084115_001464.md`. Readback verified four corners use two shared time coordinates. Manual application to Appendix B.4: this version ends on departure segment6 (14→22), confirmed by segment7 (22→18) remaining above core[13,16]; unchanged CC history still reports its own end_index5.
- **Acceptance checks:** Both full backups byte-verified; algorithm sections and appendices preserved, index valid, final text read back. Scoped `git diff --check` passed. No algorithm implementation/testing claimed.
- **Status:** done.
- **Blockers:** None for recording the selected geometric definition. Actual segment extrema versus plotted/standardized intersection geometry and zero-height centers remain explicit005 questions.
- **Next action:** Continue the remaining definition details at user direction.
