## Task
- **ID:** 20261107-feature-record-structures
- **Goal:** Recommend simple Python structures for feature results, source references and rule evidence, using MergedKlineSeries; chat only.
- **Inputs:** Memo009 sections001.a–001.c; user’s beginner Python context; prior dependency review.
- **Allowed changes:** This record, memory next action if needed, and logXW.md; no memo or implementation edits. Delegated review is read-only.
- **Acceptance checks:** Preserve immutable shared sources, result/source mapping, per-point evidence including intermediate merge values, and numeric export; explain Python structure choices plainly.
- **Assignment:** Root drafts; derived_dependency_review challenges the proposal read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Proposed three composed immutable records: MergedKlineSeries (shared source, result tuple, configuration/ruleset version), MergedKline (values/status/source span and step tuple), and feature-specific MergeStep (rule ID, triggering sources, checked conditions and intermediate values). This remains a chat proposal.
- **Evidence:** Read memo009/memory; checked official Python dataclass/tuple documentation. Independent read-only review supported item-level step tuples initially, pinned ruleset version at series level, immutable nested values, internal mutable builders, and numeric adapters. It stressed preserving direction-establishment context beyond constituent ranges and that frozen dataclasses alone do not freeze nested lists/dicts. No memo or implementation edits.
- **Blockers:** None.
- **Next action:** Discuss the proposed structures with the user before recording a decision.
