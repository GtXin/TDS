# Task

- **ID:** 20261110-bi-double-cache-discussion
- **Goal:** Review the user's two-working-stroke side note in memo020002.a, especially initial-start replacement, endpoint extension and the meaning of confirmation; discuss the framework without adopting or implementing rules.
- **Inputs:** User's current proposal; `docs/memo/memoWX_020_Chan_bi.md` definition and side note; prior `mas/tasks/20261110-bi-return-to-002a-review.md`; `mas/skills/computer-scientist/SKILL.md`.
- **Allowed changes:** Root owns this task, the concise result pointer in `CodexMemory.md`, and `logXW.md`; reviewers are read-only. No memo, source, test or algorithm-policy edits.
- **Acceptance checks:** State preconditions for initial-start replacement; identify precise incomplete transitions; check at least one concrete counterexample against the six pair conditions; distinguish local provisional storage from permanent confirmation.
- **Assignment:** Root coordinates; independent read-only reviewers examine initial-start replacement and two-stroke transitions.
- **Status:** done

# Result and handoff

- **Outcome:** Two-working-stroke progression is a useful proposed framework, not yet a complete selector. Initial2.a replacement is sound before accepting any pair: a later more extreme same-kind start lies inside every future old-start pair and invalidates its endpoint bound. Initial2.b cannot permanently discard weaker starts. Full pair checking already excludes a weaker replacement in5.a; equal-price replacement is a policy choice. Failed stronger extension in5.b requires unresolved/recovery handling. First reverse qualification in6.a establishes a locally stored predecessor, not irreversible confirmation under continuous-coverage requirements. No rule adopted.
- **Evidence:** Root and two independent read-only reviewers checked the reasoning. Executed an inline Python six-condition pair checker (no source/test files created). Continuous merged intervals `[x,x+1]`, lows `9,10,0,9,7,5,3,1,2`: exact fractals top1,bottom2,top3,bottom7;1→2 fails distance,1→7 fails interior minimum,3→7 passes. Existing21bar memo example independently rechecked:1→5 and5→9 pass;9→11 fails distance;5→15 fails interior minimum;9→19 fails interior maximum; alternate1→11→15→19 passes all pairs. These are geometric checks and counterexamples, not proof of a complete repaired protocol. Minor flow omissions:3.b needs a continuation;6.a must assignBi001E=C before rotating.
- **Blockers:** None for the review. Initial-start selection, recovery scope, tie behavior and confirmation semantics remain unadopted design choices.
- **Next action:** Discuss which endpoints may be discarded and how the two working strokes recover when an extension fails; amend020 only if requested, before any implementation change.
