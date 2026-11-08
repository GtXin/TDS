# Task
- **ID:** 20261108-memo009-cohesive-sequence
- **Goal:** Place Beichi/BeichiSeries after ZoushiSeries throughout memo009 and align ChanTable documentation/CSV metadata with that sequence.
- **Inputs:** CodexMemory.md; docs/memo/memoWX_009_designPatternForChanFeatures.md and its CSV companion folder; memo006; mas/contracts.md.
- **Allowed changes:** Root owns memo009, exact timestamped backups, companion CSV metadata, CodexMemory.md, this task and logXW.md. Reviewers are read-only. Preserve existing field/method definitions, deferred placeholders and synthetic data values.
- **Acceptance checks:** Sections002.b–002.s follow the002.a class order; all section references resolve to the intended classes; table groups and context follow raw/MK/FX/BI/XD/ZS/ZOU/BC; unchanged raw/sample values and existing definitions; empty001.c/DecisionStep; valid CSVs, local links and git diff --check; independent review.
- **Assignment:** Codex root edits; derived_dependency_review checks sequence, references and CSV coherence read-only.
- **Status:** done

# Result and handoff
- **Outcome:** Moved Beichi/BeichiSeries to002.p/002.q, empty DecisionStep to002.r and ChanTable to002.s. Aligned memo/memory/CSV context references and the FX/BC anchor note. Existing field/method content and deferred definitions retained.
- **Evidence:** Exact baseline at docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_024823_043286.md and matching CSV folder. Root preservation checks passed18 classes in order, all references/local links/index, empty001.c/002.r,38-column/3-row sample and matching group/context order. Data/header CSVs are byte-identical; only two context-note cells changed. Artifact-tool recalculation/inspection returned zero formula errors; rendered context visually passed. Independent read-only derived_dependency_review passed; git diff --check passed. Concurrent MergedKline table alignment retained after comparing all cells unchanged. No source implementation changed.
- **Blockers:** None.
- **Next action:** none
