# Task
- **ID:** 20261108-memo009-feature-id-convention
- **Goal:** Record integer feature IDs with display-only prefixes in memo 009, align feature fields and ChanTable examples, and add MergedKlineSeries.validate() following user steering.
- **Inputs:** User-approved convention; memo 009; CodexMemory.md; memo 006.
- **Allowed changes:** Root owns memo 009 and backup, CodexMemory.md, this record and logXW.md. Reviewer is read-only; no implementation or resumption of the stopped remaining-methods task.
- **Acceptance checks:** Six feature id fields use int; prefixes are display-only and numeric sorting is explicit; IDs are scoped to exact feature-series/result context; source references/ranges retain their role; ChanTable examples use integer tuples; add only the requested MergedKlineSeries.validate() with source/range/ID/trace checks; existing methods, other fields, references and links preserved; backup and whitespace checked.
- **Assignment:** Root edits; read-only reviewer checks ID consistency.
- **Status:** done
# Result and handoff
- **Outcome:** Added001.e integer feature-ID/display convention, aligned six ID fields and ChanTable integer tuple examples, and added the user-requested MergedKlineSeries.validate() in002.e. Bulk remaining methods remain stopped.
- **Evidence:** Memo 009, CodexMemory.md, and byte-verified pre-edit backups ending `20261108_013703_314923.md` and `20261108_013811_628115.md`. Read-only reviewer review_chantable confirmed ID scope, trace/source separation and focused validation; refined source-reference wording to support multiple explicit source series. Checks passed for six int IDs, preserved Kline/KlineTSeries and DecisionStep methods/fields, unchanged source/trace principles and references, integer tuple examples, headings, local links/index, citation order, whitespace and git diff --check. No implementation changed.
- **Blockers:** None.
- **Next action:** Review MergedKlineSeries validation and continue class design as directed; do not resume the stopped bulk-methods task without instruction.
