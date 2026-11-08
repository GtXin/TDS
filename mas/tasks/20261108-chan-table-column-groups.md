## Task
- **ID:** 20261108-chan-table-column-groups
- **Goal:** Group each concept's IDs, markers and readable annotations together, and add the missing Beichi group as an explicitly undefined/unloaded placeholder following the user's steering.
- **Inputs:** User rework request; current36-column sample/schema; spreadsheet edit workflow.
- **Allowed changes:** Memo009 section002.q and exact backup, all three companion CSVs and backups, memory, this record, logXW.md. Temporary builder/previews stay in tmp; reviewer is read-only.
- **Acceptance checks:** Raw10 first, then MK/FX/BI/XD/ZS/ZOU/Beichi blocks; all original36 field values preserved by name, header order matches, annotations adjacent to own concept; Beichi placeholder cells NA and no invented classification/rules/class implementation; original context/NA/ID/source/version semantics preserved.
- **Assignment:** Root reorders; reviewer checks scope and grouping.
- **Status:** done
## Result and handoff
- **Outcome:** Grouped each concept's IDs, markers and readable fields adjacently; added all-NA bc_ids/bc_kind after Zoushi. Updated CSV header/context and002.q’s grouped column summary. Beichi remains a planned group, not a registered class or calculated result.
- **Evidence:** Exact memo/CSV backups retained. Artifact-tool recalculation/inspection/three changed-view renders passed; independent CSV comparison preserved all36 old field values, ISO UTC strings and seven old context rows. Header covers38 columns in matching order; eight groups including raw are contiguous and the added Beichi context is explicitly undefined. Read-only review confirmed prior memo sections/references/deferred headings unchanged; git diff --check passed.
- **Blockers:** None.
- **Next action:** Review grouping and define Beichi records/classification/rules at the user’s direction; no algorithm implementation added.
