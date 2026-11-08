# Task
- **ID:** 20261108-beichi-zhongshu-id-reference
- **Goal:** Make BeichiSeries refer explicitly to Zhongshu IDs as requested, with an unambiguous source/result scope.
- **Inputs:** Memo009 sections001.b/001.e/002.l–002.q; current memory; user correction that the reference belongs to BeichiSeries.
- **Allowed changes:** Root owns memo009, exact backup, memory, this task and logXW.md. Reviewer read-only; preserve other classes, CSVs, rules and deferred methods.
- **Acceptance checks:** Zhongshu ID reference appears explicitly in002.q under the selected ownership model; ID resolution uses an exact ZhongshuSeries/result version; selected movement's center membership is checked by resolved position; no duplicated stored relationship, stale Beichi center_index or new algorithms; Markdown tables, scope/links and git diff --check; independent review.
- **Assignment:** Root edits; derived_dependency_review inspects source/ID scope read-only.
- **Status:** done

# Result and handoff
- **Outcome:** User selected one Zhongshu ID per BeichiSeries. Added zhongshu_id to002.q, removed per-item center_index from002.p and aligned class outline/ChanTable description; memory records the confirmed ownership.
- **Evidence:** Exact pre-edit backup docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_031510_222203.md; subsequent table-boundary and001.e convention backups __20261108_031611_943169.md and __20261108_031650_633690.md. Root checks and independent review passed single series-owned ID, exact source/ID namespace, resolved-position membership, aligned outline/ChanTable, nine Beichi fields/six BeichiSeries rows, preserved other class bodies/methods/placeholders/references, unchanged three CSV hashes, local links and git diff --check. Initial parser check caught the resolution paragraph as an extra table row; added its missing blank separator and reran successfully. No algorithms/classes implemented.
- **Blockers:** None.
- **Next action:** none
