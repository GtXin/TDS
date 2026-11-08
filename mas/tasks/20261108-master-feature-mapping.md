## Task
- **ID:** 20261108-master-feature-mapping
- **Goal:** Evaluate a raw-time master mapping table plus compact interval-feature records, using Xianduan/shared endpoints.
- **Inputs:** User proposal; memo009; proj009 memos0019/0027/0036.
- **Allowed changes:** This record, memory next action, logXW.md; no memo/source edits. Reviewer is read-only.
- **Acceptance checks:** Distinguish point/interval objects, preserve shared endpoint membership and explicit endpoint roles, keep a single authoritative result representation, and account for run-local IDs/status/confirmation time.
- **Assignment:** Root evaluates source design; derived_dependency_review reviews boundaries and storage.
- **Status:** done
## Result and handoff
- **Outcome:** Recommend compact Xianduan records as authoritative results and a generated master mapping over the original time axis. Shared pivots have tuple memberships plus separate start/end roles; unassigned rows remain present. This remains a proposal for discussion.
- **Evidence:** Read proj009 memos0019/0027/0036;0036 explicitly preserves raw-row mapping/shared endpoints and run-local tags (lines19,64,68–83,117–128). Independent read-only review supported compact records plus derived mapping, emphasizing point-vs-edge coverage, endpoint prices distinct from raw closes, source/run scope, and confirmation time distinct from endpoint time. Proposed compact records differ from proj009’s repeated per-row endpoint tuples; no equivalence claim.
- **Blockers:** None.
- **Next action:** Discuss the two-table proposal with the user; update001.d when requested.
