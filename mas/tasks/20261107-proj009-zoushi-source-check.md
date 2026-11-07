# Project 009 — locate movement discussion
## Task
- **ID:** 20261107-proj009-zoushi-source-check
- **Goal:** Answer whether Project 009 memos contain details relevant to memo 008 S5 走势.
- **Inputs:** Project 009 memo library and TDS reference snapshots; user clarified repository scope.
- **Allowed changes:** Read-only source inspection; memory/log and this task record. Do not edit memos or original references.
- **Acceptance checks:** Identify precise source sections; distinguish reference architecture from completed project implementation; verify cited snapshots match current originals.
- **Assignment:** Root inspects current originals; `chan_s2_s3` independently checks snapshot coverage read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Details exist in memo 0015’s ZhongShu To ZouShi section and memo 0035 section 1, with an object-chain overview in memo 0012. No standalone movement-algorithm memo was found in the current library.
- **Evidence:** `references/proj009Memo/memo0015_oop_trading_architecture.md:402`, `references/proj009Memo/memo0035_algo_of_zhongshu.md:39`, `references/proj009Memo/memo0012_cc_csv_to_zoushi_reference.md:129`; current originals read and four source/snapshot SHA-256 pairs matched.
- **Blockers:** none for the lookup; complete movement algorithm not established by these memos.
- **Next action:** Report source locations; memo 008 S5 remains unchanged.
