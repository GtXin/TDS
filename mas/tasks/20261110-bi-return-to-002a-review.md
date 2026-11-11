# Task

- **ID:** 20261110-bi-return-to-002a-review
- **Goal:** Advise whether to return to memo020002.a after memo028's observed Bi failures; separate specification feasibility, selection-policy adequacy and implementation conformance.
- **Inputs:** User's recommendation/opinion request; current020/028, current Bi code/tests, saved seed50/restart evidence, current fixed-earliest-A and020-first decisions, existing non-normative recovery studies.
- **Allowed changes:** Only `artifacts/mas/bi-algorithm-review/`, this task, concise memory and event log. No memo, production code, tests, rule or configuration changes.
- **Acceptance checks:** Read current rules rather than old multistart history; inspect code/tree branches and saved verification scope; reproduce targeted failures; independently check geometric feasibility; preserve protected sources; recommend next decision steps without silently adopting a new policy.
- **Assignment:** Root owns all writes and targeted reproduction. check_diagram and bi_contract_review audit read-only; no shared source writes.
- **Status:** done.

## Result and handoff

- **Outcome:** Recommend returning to020002.a while retaining028 as an executable baseline. Empty output is reproduced under the current tree/code. Two distinct situations need different treatment: seed50 and a compact9bar example have no six-rule continuation from the fixed initialA; the full sample has a same-initialA definition-valid witness excluded by the current temporal protocol. More caching alone cannot repair the first case, while temporal acceptance/recovery should be reviewed for the second.
- **Evidence:** `artifacts/mas/bi-algorithm-review/reproduce.py` and `diagnosis.json`; root ran current production chain on saved49raw seed50, compact9raw example and full10060raw sample. Seed50:31merged/16FX, fixedA=FX1 has only legal successorFX4, FX4 has no legal successor; outputblocked/empty. Compact9bar: exactcenters1top/5bottom/6top/7bottom; onlylegaledge1→5, outputempty. Full sample:6200merged/3027FX, currentcode3177states/zero routes/blockedFX151; independently rechecked all480stroke pairs in the existing same-A witness reaching lastFX3026. First differing choice near failure is current145→148 versus witness145→150. The witness satisfies six pair rules only, not the present temporal protocol, and is not adopted as the correct market route.
- **Checks/limits:** Independent read-only reviewers agree code matches fixed-A/firstreverse/extensionblock policy. Protected020/028/bi.py/test_bi.py hashes unchanged. No broad test or Monte Carlo rerun; the three targeted chains and480witness-edge checks were executed. Prior zero-reference-difference results demonstrate protocol conformance; coverage/continuous-drawing adequacy remains an independent criterion. Existing restart190figures count configurations, not a direct failure-rate denominator. Guessed artifact README/plot.py paths were absent; existing JSON/PNG/source scripts supplied the actual evidence.
- **Blockers:** No blocker to the opinion/recommendation. No new rule has been chosen; a revised policy requires020-first discussion and edit before implementation.
- **Next action:** Review0202.6–2.8 on the compact no-path case and the real-sample divergent choice; decide reverse-choice rollback and blocked-prefix/unresolved output semantics, then synchronize020b–d and028/code/tests.
