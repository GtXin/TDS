## Task
- **ID:** 20261107-rule-tree-decision-trace
- **Goal:** Explain a small class design that records every executed rule-tree decision for calculated features, using K-lines after inclusion processing.
- **Inputs:** User’s planned rule-tree memo; memo009 source-reference/explanation decisions; prior structure proposal.
- **Allowed changes:** This record, memory next action, logXW.md; no memo or implementation edits. Reviewer is read-only.
- **Acceptance checks:** Tie executed nodes to an exact tree version, preserve branch outcomes and decisive source/intermediate values, retain per-result trace access and chronological order, and avoid a full rule engine.
- **Assignment:** Root drafts; derived_dependency_review checks trace completeness.
- **Status:** done
## Result and handoff
- **Outcome:** Proposed one chronological series-level tuple of DecisionStep records, with decision indices on each resulting BaohanKline. Pin tree ID/version and configuration on the derived series; keep the original source-series reference.
- **Evidence:** Read current memo009/memory. Independent read-only review confirmed that a central log retains rejected/deferred/no-output decisions, unlike per-surviving-item tuples alone. Steps capture visited node IDs, actual branch outcomes, exact source references and immutable named values including intermediate state. Outcome values may include numbers, booleans, strings and None. Record the original predicate outcome at execution time, respecting short-circuit paths. No rule engine, memo changes or feature implementation added.
- **Blockers:** None for the class recommendation; the actual tree is required before implementing its rules. Example node IDs are illustrative.
- **Next action:** Discuss the proposal; implement only after the user supplies the tree and requests implementation.
