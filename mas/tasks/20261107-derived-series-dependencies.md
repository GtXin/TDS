## Task
- **ID:** 20261107-derived-series-dependencies
- **Goal:** Recommend how merged bars and other derived series should refer to their inputs; discuss 001.b in chat before recording a decision.
- **Inputs:** User question, memo009, proj009 memo0020, cc models, prior repository comparison.
- **Allowed changes:** This record, CodexMemory.md next action, and logXW.md only; no memo edits or implementation. Delegated review is read-only.
- **Acceptance checks:** Compare object references, copies and source spans; address ownership, immutability, revisions, lineage and time-series interoperability; state a practical proposal and its limitations.
- **Assignment:** Root investigates sources; `derived_dependency_review` independently challenges the architecture read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Proposed one immutable source-series reference per derived series, with derived values/source spans on compact merged items. Direct immutable object references remain valid; no universal inheritance or nested source-object requirement. This is a recommendation, not an agreed decision.
- **Evidence:** Inspected cc `src/cc/algo/models.py:124` (compact values/spans), live proj009 experiment `experiments/chan_theory/merged_kline_series.py:47,171` and reference memo0020 (raw-aligned enriched rows plus optional source_series), current chan.py combiner and CZSC bars, and Python copy documentation. Independent review agreed, stressing exact-snapshot indexing, source corrections, distinction between constituent lineage and causal context, and retained-source lifetime. No generic provenance framework proposed.
- **Blockers:** None.
- **Next action:** Discuss the recommendation with the user before recording a decision in memo009 section001.b.
