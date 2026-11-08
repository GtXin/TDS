## Task
- **ID:** 20261108-chan-table-annotations
- **Goal:** Add readable kind/direction/center-bound annotations for all six concepts and document NA/NaN behavior in memo009 and its CSV sample/guide/context.
- **Inputs:** User approval; latest memo009/CSV schema; spreadsheet edit workflow; pandas missing-data docs.
- **Allowed changes:** Memo009 section002.q, companion CSVs and exact backups, memory, this record, logXW.md. Builder/previews remain in tmp; reviewer is read-only. No source implementation or deferred tree/DecisionStep definitions.
- **Acceptance checks:** fx_kind=top only at sample anchor; missing scalar annotations are NA in CSV; numeric NaN/nullable pandas NA explained; ID [] versus unavailable NA preserved; other concept columns grounded in existing record fields; explicit annotation marker semantics; original29 columns/values preserved, updated guide/context and source checks.
- **Assignment:** Root edits; derived_dependency_review checks annotation semantics and exported files.
- **Status:** done
## Result and handoff
- **Outcome:** Added seven derived scalar annotation columns (mk/bi/xd direction, fx kind, center bounds, movement kind), bringing the sample/guide to36 columns. Updated002.q annotation/missing-value note and example, CSV context and memory. FX kind is NA/top/NA; other unloaded concepts remain NA. Existing ID []/NA meanings are preserved.
- **Evidence:** Exact memo/CSV backups recorded in tmp annotation_backup.json and repository log. Bundled artifact-tool authored/recalculated/inspected/rendered all changed views. Independent review and CSV comparison confirmed all original29 columns/values, including ISO UTC timestamp text, unchanged. Initial export coerced timestamps to localized JavaScript dates; corrected serializer and rebuilt from backups, then reran checks. Pandas tests verified nullable pd.NA and ordinary floating NaN; six computed-empty ID cells remain distinct from36 unavailable ID cells. Guide/context, marker placement/multiple-ID contract, prior memo sections/References and deferred definitions checked; git diff --check passed.
- **Blockers:** None.
- **Next action:** Review readable annotations and specify ChanTable methods when requested; no implementation added.
