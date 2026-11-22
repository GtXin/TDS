# Memo022 algorithm problem and overview
## Task
- **ID:** 20261118-memo022-algorithm-ab.
- **Goal:** Draft022002.a algorithm problem statement and002.b overview using030's section structure and022001's current rectangle definition.
- **Inputs:** 022001/005; 030002.a/b structure; 031 fixed-snapshot confirmed-segment contract; user decisions on outer crossing times, actual departure segment as terminal, no reused terminal/start segment, and chronological earliest-center selection.
- **Allowed changes:** 022002.a/b plus empty002.c–f headings to match030, required full memo backup, memory, this task and event log. Preserve022001/005/appendices,029/030/031, source data and algorithms.
- **Acceptance checks:** Preserve protected sections byte-for-byte; define input/output, earliest seed, fixed core, first valid departure/adjacent failed return, actual departure member endpoint, restart after endpoint, open tail and unresolved policies. Distinguish structural confirmation from rectangle geometry and confirmation time from boundary time. Read through a small chronological example; verify heading/index/links and scoped whitespace.
- **Assignment:** Codex root applying computer-scientist skill; no delegation.
- **Status:** done.
## Result and handoff
- **Outcome:** Completed002.a/b with input/output contracts, chronological earliest-seed scanning, one-segment advance on no overlap, fixed core during extension, first actual departure plus adjacent completed failed-return confirmation, restart at e+1, rectangle/confirmation separation and open/pending outputs. Empty002.c–f now match030. No algorithm code added.
- **Evidence:** Full backups `docs/memo/backups/memoWX_022_Chan_zhongshu__20261118_090046_271963.md` and `docs/memo/backups/memoWX_022_Chan_zhongshu__20261118_090212_637082.md`. Protected sections byte-equal;029/030/031 hashes unchanged; a–f headings, empty c–f, new links/fragments and index verified. Scoped `git diff --check` passed.
- **Blockers:** No blocker to002.a/b drafting. 005 retains point-center and segment geometry/standardization questions; design must expose these without silently deciding them.
- **Next action:** User review; then develop002.c–f when requested. Resolve005 policies before claiming a general executable geometry algorithm.
- **Input SHA-256:** `docs/memo/memoWX_022_Chan_zhongshu.md` = `7d38613fd08ed26cc893da3973aa5e0d632ea9e015d327d1fad1ab545b35edba`.
- **Input SHA-256:** `docs/memo/memoWX_029_Chan_bi.md` = `8b7f0c9cf374fb26aac139edde49f15ca1e56c8dc5d13ac9d596ff45acfbab97`.
- **Input SHA-256:** `docs/memo/memoWX_030_Chan_xianduan.md` = `ca113192e41b370572b0a8e684c72b39332a921b120c7ecda086823608db8eec`.
- **Input SHA-256:** `docs/memo/memoWX_031_xianduanFamily.md` = `39792daa1ab3d6f30d3e243ecc567282379c5f9c20067d45297a5097bafbcd07`.

## Manual design checks
These use illustrative straight-segment endpoints, not source-backed031 runs or implementation tests. Indices are zero-based; all price intervals below come from these illustrative endpoints only.
- **Extension, closure and restart:** Endpoints `18,12,16,13,19,14,22,18,24,20` give earliest seed s=0 with core[13,16]. Departure3 returns via4=[14,19], so does not close. Departure5 is confirmed by6=[18,22] outside; e=5, q=6, next k=6. The next seed6/7/8 has core[20,22] and remains open at EOF. Core of the first center never shrinks. Under this illustrative linear geometry, left crossing is T0+(T1−T0)/3, right crossing T5+(T6−T5)/4; neither is the confirmation segment's ending time.
- **Sliding past no overlap:** Endpoints `18,22,10,14,12,20,16` give seed0 D=18>G=14, so advance exactly one. Seed1 has[12,14]; departure4 is confirmed by5=[16,20], then k=5 leaves one unformed segment. No forced center at the tail.
- **Boundary touch:** In the first example replace endpoint18 after22 with16. Return6=[16,22] touches G=16, so departure5 is not terminal. Departure7 is then confirmed by8=[20,24]; e=7, q=8. Closed-interval touch is consistently treated as return.
- **Complexity scope:** O(N) describes a single route with resolved policies and constant-cost segment queries; internal-source/standardization work and unresolved alternative branches are not silently included in that bound.
