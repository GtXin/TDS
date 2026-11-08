# Task
- **ID:** 20261108-memo009-chantable-beichi-completeness
- **Goal:** Complete memo009 with buy/sell-point record/series after Beichi and align ChanTable definitions, visible examples and CSV template with the whole concept sequence.
- **Inputs:** Memo008 S7/S8; memo009 sections002.p–002.s; companion CSVs; memo006 and current memory; prior cohesive-sequence task.
- **Allowed changes:** Root owns memo009, exact backups, three companion CSVs, memory, this task and logXW.md. Reviewers read-only. Preserve existing field semantics/sample values; append unavailable buy/sell columns and defer methods/algorithm rules.
- **Acceptance checks:** Class order continues Zoushi→Beichi→BuySellPoint→DecisionStep→ChanTable; section references agree. ChanTable definitions and displayed example include all feature groups in CSV order; Beichi/buy-sell events use raw anchors; all export columns and guides agree. Preserve prior sample values, empty placeholders and pending rules; links, artifact inspection/rendering and git diff --check pass; independent review.
- **Assignment:** Root edits; derived_dependency_review inspects completeness and essential_memo_check reviews buy/sell members, both read-only.
- **Status:** done

# Result and handoff
- **Outcome:** Added BuySellPoint/BuySellPointSeries at002.r/002.s after Beichi; DecisionStep/ChanTable moved to002.t/002.u. ChanTable now defines Beichi and buy/sell points in sequence and its visible example continues through all eight feature groups. Three CSVs now share41 columns and matching context/meanings; new point samples remain NA.
- **Evidence:** Exact pre-edit backup docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_025612_294459.md and matching three-CSV folder. Root checks passed20 class/section order, preserved existing members and14 method tables, empty001.c/002.t, unchanged original38 sample columns/values,41 matching export names/order,9 ordered contexts, all concepts visible in the example, local links/index and git diff --check. Artifact-tool recalculated/inspected/exported all3 CSVs; three formula-error scans returned zero matches and all3 changed previews visually passed. Both independent reviews passed. Detection/classification rules and new methods remain pending; no classes implemented.
- **Blockers:** None.
- **Next action:** none
