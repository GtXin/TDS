# Task
- **ID:** 20261108-memo009-chantable-methods
- **Goal:** Rename MasterTable to ChanTable consistently in memo 009 and propose essential KlineTSeries methods covering access, ChanTable interchange, time-indexed tabular conversion and plotting.
- **Inputs:** Active user discussion; docs/memo/memoWX_009_designPatternForChanFeatures.md; CodexMemory.md; memo 006 writing guide.
- **Allowed changes:** Root agent owns memo 009 and its pre-edit backup, CodexMemory.md, this task record and logXW.md. Reviewer is read-only; no source implementation or other memo edits.
- **Acceptance checks:** Consistent ChanTable naming; concise proposed methods with clear inputs/outputs; preserve Kline fields/methods and feature definitions; retain separate adapter/rendering responsibilities; defer detailed ChanTable methods; check local links, index, whitespace and exact backup.
- **Assignment:** Root edits; a read-only reviewer checks naming and design coherence.
- **Status:** done
# Result and handoff
- **Outcome:** Renamed the class and related prose to ChanTable throughout memo 009; added nine proposed Python-style KlineTSeries methods and aligned the overview. Detailed ChanTable read/write/update rules remain deferred.
- **Evidence:** Memo 009 sections001.a/001.d/002.a/002.c/002.q; pre-edit backups `docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_011325_618974.md` and `docs/memo/backups/memoWX_009_designPatternForChanFeatures__20261108_011449_110889.md`; updated CodexMemory.md. Read-only reviewer `review_chantable` confirmed naming/boundaries and identified empty/reversed slicing versus nonempty chronological series. Resolved by returning tuples for slices, preserving Python slicing behavior. Exact backup checks, preserved Kline/feature tables, section numbering, nine snake_case/special methods, local links/index, citation order excluding code, memo whitespace and `git diff --check` passed. Initial citation check falsely counted inline Python index `[5]`; corrected the check to exclude code. No classes implemented.
- **Blockers:** None.
- **Next action:** User reviews the proposed002.c methods; design detailed ChanTable interfaces in002.q later.
