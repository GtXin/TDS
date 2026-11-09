# Task

- **ID:** 20261109-memo015-helper-functions
- **Goal:** Fill memo015002.c with necessary helper-function contracts supporting the current tree and examples.
- **Inputs:** User request “now do 2.c any helper functions?” and follow-up “we agree to have mnerged kline to be placed at the the begining?”; memo015001/002.a/b; memo006; memo009 MergedKline/MergedKlineSeries design; actual Kline/KlineTSeries and ChanTable interfaces; computer-scientist skill.
- **Allowed changes:** Only memo015002.c and its required backup, this task, project memory and event log. Preserve001,002.a/b/d, appendices, source/figures and production code.
- **Acceptance checks:** Proposed function names, inputs/outputs, preconditions and side effects explicit; inclusion symmetric; direction helper enforces noninclusion; aggregate merge preserves direction and half-open contiguous source; outer merge retains None; main loop exclusively owns counters/appends/ID allocation; no invented initialization/warning/status default; immutable raw preserved. Position anchored at source_start with display time from the first source bar, separately from extrema/confirmation; read-only contract review, exact outside-section preservation, backup/index/format checks and git diff --check.
- **Assignment:** Root owns all writes; review_002c_contracts independently audits contracts and interface boundaries read-only.
- **Status:** done.

## Result and handoff

- **Outcome:** Filled only002.c with six proposed helper contracts: work_from_raw, has_inclusion, direction_between, merge_included, merge_outer_boundary and validate_merged_result. Explicit inputs/outputs, inclusion/known-direction guards, same-source contiguous ranges, original-start positioning and main-loop state ownership; six illustrative contract checks. No implementation added.
- **Evidence:** Independent read-only reviewer passed contracts, examples, source provenance and actual/proposed interface boundaries. Backup `docs/memo/backups/memoWX_015_Chan_mergedkline__20261109_033225_852753.md` is byte-identical. Exact preservation outside002.c, saved reread, six helper headings, Markdown table consistency, balanced fences, numbered headings/index and empty002.d checks passed. Original001/002.a/b/appendices and all figures/source/code preserved. No runtime helper tests: interfaces are proposed documentation.
- **Decision:** User reaffirmed beginning placement; documented position source_start and derived display time raw[source_start].timestamp, distinct from extrema, knowledge availability and confirmation. Existing002.b centered stroke remains an interval schematic, not a placement anchor.
- **Blockers:** None for this section. Default initialization, warning distance/threshold and status/confirmation/trace rules remain deferred.
- **Next action:** Review002.c;002.d pseudocode remains empty until requested.
