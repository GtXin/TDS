# Memo033 implementation and validation
## Task
- **ID:** 20261118-memo033-implementation
- **Goal:** Implement memo033 Zhongshu/ZhongshuSeries, integration, independent validation and complete charts; report actual results in033.
- **Inputs:** memo009,022,031,033; existing022 scanner/adapter; real031 contexts; Python Pro1.1.0.
- **Allowed changes:** shared Zhongshu implementation/data/visualization, table integration, tests, experiments/zhongshu033, artifacts/mas/zhongshu-family/run033,033 and needed009 contract clarification (backed up), memory/log/task. Preserve022/029/030/031/raw.
- **Acceptance checks:** immutable complete domain/source/trace validation, lossless mixed table/context, independent baseline comparison, >=10000 raw sequences×4 modes, real100/1000/3000FX×4×3 timings, complete PNG/HTML atlas with machine and visual QA; pytest/strict mypy/Black/Ruff, >90% module coverage; memo links/results and protected hashes.
- **Assignment:** Codex, sequential; no delegation.
- **Status:** completed
## Result and handoff
- **Outcome:** Two immutable domain classes, full source/trace replay, scoped mixed table/context persistence and native plotting implemented.009 contract synchronized with backups;033 completed without changing022/029/030/031/raw.
- **Checks:**522 pytest pass; strict mypy7files, Black/Ruff pass;99% aggregate Zhongshu coverage.404 frozen022 comparisons; full four-mode exact022 parity;10000 random raw×4;64 long raw×4;2852 finite paths. Twelve timings×3.228 PNG/HTML plus57 comparison PNG,228 individual pages visually reviewed via38contact sheets; comparison overview sampled.
- **Evidence:** [run README](../../artifacts/mas/zhongshu-family/run033/README.md), [memo033](../../docs/memo/memoWX_033_zhongshuFamily.md), final-audit.json and visual-review.json.
- **Blockers:** none. Known022 default left-crossing-missing preserved; dense chart labels may overlap.
- **Next action:** User review; fixed snapshot segment scope remains. No commit/push requested or performed.
