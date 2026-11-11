# Task

- **ID:** 20261110-bi-start-reselection-discussion
- **Goal:** Assess the user's A→C reselection and concern about two cache levels, preserving continuous shared endpoints and immutable submitted R.
- **Inputs:** ActualFX145/148–151 source context; current020 originalnote/commit rule; prior fixed-cache proof and numeric audit; Computer Scientist skill.
- **Allowed changes:** Discussion/review artifacts, this task, relevant memory/log only. Root owns task/memory/log; reviewers own named files. No memo/code/data changes or adoption of a new rule.
- **Acceptance checks:** Check actual predecessorP→C and C→D against all six conditions; identify whetherP→A is already submitted and the consequences of changingA. Distinguish one complete cached stroke+start from two complete pending strokes. Do not claim a fixed number of cache levels sufficient or minimal without proof; identify the commit invariant still needed.
- **Assignment:** Root synthesizes; bi_contract_review owns framework-review.md; check_diagram owns pair-review.md under artifacts/mas/bi-start-reselection/.
- **Status:** done

# Result and handoff

- **Outcome:** A→C is geometrically feasible for this actual case only when the preceding stroke also becomesP→C and the next cacheC→D. CurrentP→A is already submitted, so direct reset conflicts with shared endpoints/finalR immutability. Suggested discussion framework retains a mutable unsubmitted suffix and derives commit conditions before fixing cache depth; no rule adopted.
- **Evidence:** Independent numeric reviewer ran one read-only upstream pipeline, noBi.scan: P145center293[2778,2788],C150center306[2815,2824],D151center310[2794,2806]. Full checksP→C gap13/min2778/max2824;C→D gap4/min2794/max2824 pass with zero violating bars. Independent framework review confirms the preceding-endpoint dependency and distinguishes one full cached stroke+start from two full pending strokes. Reviews/README/hashes under artifacts/mas/bi-start-reselection. No memo/code/data edits or broad tests.
- **Blockers:** None.
- **Next action:** Discuss pending-suffix transitions and a justified commit condition; do not select a fixed cache depth or update020/code until the framework is agreed.
