# Task
- **ID:** 20261108-memo009-chantable-columns
- **Goal:** Summarize proposed ChanTable columns with one row per original Kline timestamp, following memo 009 design principles and marking all existing feature types.
- **Inputs:** User request; memo 009 sections001.a/001.b/001.d/001.e and class fields; CodexMemory.md; memo 006.
- **Allowed changes:** Root owns memo 009 section002.q and necessary cohesion edits, pre-edit backups, CodexMemory.md, this record and logXW.md. Reviewers are read-only; no code, other memos or decision-tree/DecisionStep definitions.
- **Acceptance checks:** Exact original raw time axis and OHLCV/provenance; all six feature types and levels covered; integer tuple memberships and shared endpoints; distinguish fractal anchor/window and confirmation/endpoint time; preserve authoritative compact feature records and exact series/version context; concise complete column summary without new algorithms; source/placeholder/other class sections unchanged; backups, links/index and whitespace verified.
- **Assignment:** Root authors; read-only reviewers check column coverage and time/source semantics.
- **Status:** done
# Result and handoff
- **Outcome:** Replaced only002.q with seven proposed members, followed by an exact original-row contract, ten raw fields and nineteen feature-marker columns. Coverage/endpoints and separate fractal anchors cover all six feature types, with independent groups for additional levels/results. No ChanTable methods or decision-tree/step definitions added.
- **Evidence:** Memo 009 section002.q; byte-verified pre-edit backup `docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_015358_129183.md`; CodexMemory.md updated. Read-only reviewers review_chantable and review_record_methods passed source/time/feature-context review. Root checks passed for exactly seven members, ten raw fields and nineteen unique marker columns, unchanged source/provenance contract, exact preservation outside002.q and references, empty001.c/002.p, fourteen unchanged existing methods tables, headings, local links/index, whitespace and git diff --check. Confirmation remains in authoritative feature records; no invented confirmation-row projection or algorithms.
- **Blockers:** None.
- **Next action:** User reviews the ChanTable member/column summary; design its methods as directed. Keep decision-tree/step placeholders empty.
