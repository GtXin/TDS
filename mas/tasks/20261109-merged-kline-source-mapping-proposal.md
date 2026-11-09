# Task

- **ID:** 20261109-merged-kline-source-mapping-proposal
- **Goal:** Recast the conversational merge pseudocode against actual Kline/KlineTSeries/ChanTable interfaces, preserving source positions and mapping ownership.
- **Inputs:** src/chanlab/algo/kline.py,chan_table.py; data/kline_csv.py,chan_table_csv.py; memo009002.d/e/u; current discussion.
- **Allowed changes:** This record, project memory/event log only. No code, memo, dataset or skill edits; initialization choices remain unresolved.
- **Acceptance checks:** Distinguish implemented classes from design-only feature records; preserve immutable raw source; use exact source reference and half-open bounds; map end marker at stop-1; do not claim ChanTable accepts feature values today.
- **Assignment:** Root inspects interfaces/proposes pseudocode; review_merge_source_mapping independently audits source/index/table boundaries without writes.
- **Status:** done.

## Result and handoff

- **Outcome:** Current raw classes and planned feature/table mapping inspected; independent reviewer confirmed API/source-index boundaries. Proposal uses KlineTSeries input, transient work state and new immutable feature records with exact source reference and half-open ranges. ChanTable projection remains a future adapter, not current functionality.
- **Evidence:** Kline/KlineTSeries are frozen dataclasses; source indices are tuple positions. ChanTable rows are immutable string mappings with contiguous raw_index and all feature columns forced NA. memo009 proposes exact MergedKlineSeries.source_series and MergedKline.source_start/source_stop.
- **Blockers:** none for proposal. Feature classes/table projection adapter and initialization/output-status semantics are not implemented or settled.
- **Next action:** Discuss/confirm source-aware pseudocode and unresolved initialization/status/trace rules before implementing feature classes or changing ChanTable reservations.

## Review evidence and limits

- Implemented: algo/kline.py (Kline frozen; KlineTSeries tuple/index/validate), algo/chan_table.py (raw string rows, raw_index matches position, feature NA-only), data/kline_csv.py (raw-nine or master41 projection only), data/chan_table_csv.py (file wrappers only).
- Designed, not implemented: memo009002.d/e/u MergedKline/MergedKlineSeries/derive_from/exact source link/feature registration.
- Source mapping: seed i→[i,i+1); absorb i→keep start/set stop=i+1; membership range(start,stop); start marker=start; end marker=stop-1; direction annotation only at start.
- Exact raw snapshot and row alignment required; feature integer IDs are distinct from raw positions. read_kline_csv does not validate master raw_index or feature cells; it is not a ChanTable object adapter.
- Incomplete initialization must retain current work plus next raw index, not imply complete coverage or computed-empty values for unread rows. Two candidate histories require separate result contexts. EOF/source end is not confirmation time; range endpoints are not necessarily extreme-price anchors.
- Interface/static review only, no algorithm implementation or engine tests run. Original source, memos and data unchanged.
