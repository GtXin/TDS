# Memo 009 — typical K-line members and compact writing rule
## Task
- **ID:** 20261107-memo009-kline-members
- **Goal:** Recommend typical Kline/KlineTSeries members under001.a; add the requested compact-format rule to memo006.
- **Inputs:** User requests; memo009/006; current proj009 Kline and KlineTSeries source; source memos0009/0010; official Python datetime/dataclass documentation.
- **Allowed changes:** Memos009/006 and their backups, memory/log, and this record. Preserve user scope text and empty Implementation002; no application code edits.
- **Acceptance checks:** Compact layout; distinguish stored fields/properties/methods; reflect current source accurately; mark TDS choices as proposals; finite-price/volume and series invariants; timestamp semantics explicit; working references; exact pre-edit backups.
- **Assignment:** Root inspects/drafts; `kline_members_review` independently checks design concerns read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Added a compact three-row comparison table and three design rules under001.a; added one compact-format sentence to memo006. Implementation002 remains empty.
- **Evidence:** Independent read-only review confirmed the proj009 baseline and distinguished proposed time conventions. Checks passed for the single rule-only guide change against its exact backup, preserved scope, empty002, three-column member table, local source/index links, backups, and `git diff --check`. Subsequent package-research additions were preserved.
- **Blockers:** none.
- **Next action:** none; further member design and implementation await user direction.
