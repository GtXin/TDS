# Task

- **ID:** 20261109-memo015-detailed-logic-examples
- **Goal:** Fill memo015002.b with implementation logic and checked numerical examples following current002.a.
- **Inputs:** User request “now do 002.b”; memo015001/002.a; memo006; memo009 feature/source design; actual Kline/KlineTSeries and ChanTable interfaces; computer-scientist skill.
- **Allowed changes:** Only memo015002.b and its required backup; new illustrations in its companion folder; reproducible synthetic example/figure outputs in artifacts/mas/memo015-002b/; this task, project memory and event log. Preserve002.a,001,002.c/d and appendices. No production implementation or dependency changes.
- **Acceptance checks:** Byte-identical pre-edit backup and exact preservation outside002.b; independently checked main and initialization arithmetic; explicit n/i/direction/source-range updates; aggregate-versus-raw counterexample; labelled synthetic candlesticks and merged intervals with inspected figures; valid image links, section/index preservation and git diff --check.
- **Assignment:** Root owns all writes. review_002b_examples audits arithmetic; review_002b_logic audits scope, state/source semantics and interfaces; both read-only.
- **Status:** done.

## Result and handoff

- **Outcome:** Filled only002.b with six implementation-logic steps, main10→3 trace/final-source tables, a sequential-comparison counterexample, all four initialization choices and equal-bound/single-bar cases. Added two inspected PNGs showing synthetic raw candles and derived high/low intervals on the original index axis. No default, warning metric or production feature implementation added.
- **Evidence:** Backup `docs/memo/backups/memoWX_015_Chan_mergedkline__20261109_032532_675848.md` matches pre-edit bytes. `artifacts/mas/memo015-002b/` retains the generator, synthetic raw/trace JSON, arithmetic and documentation verification, and PNG/SVG originals. Reproduced with the existing Project009 matplotlib3.11.1 environment, without installation/config changes. Actual arithmetic checks:9 main +9 initialization +3 counterexample transitions, source coverage/immutability, single-bar, equal one-price and unspecified-initialization cases. Two independent read-only reviewers passed all numeric tables, states, interfaces and scope. Both PNGs visually inspected: readable labels, aligned source spans, fully populated lower panels. Exact preservation outside002.b, saved reread, headings, table column counts, image links/index and copied-figure SHA-256 checks passed; git diff --check passed before final recording.
- **Rendering notes:** Initial environment probe emitted font-cache permission warnings; task-local cache paths were used for the render. Bold text fell back to regular weight; inspected labels remain legible. No package/environment changes.
- **Blockers:** None for the requested section. Default initialization, warning distance/threshold, confirmation/status and full trace rules remain undefined/unselected as recorded in002.a/b.
- **Next action:** Review002.b;002.c helper functions and002.d pseudocode remain empty pending the user's request.
