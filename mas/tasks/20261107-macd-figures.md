# MACD teaching figures
## Task
- **ID:** 20261107-macd-figures
- **Goal:** Show MACD components and a price/indicator divergence example.
- **Inputs:** User’s figure request; previously checked StockCharts formulas and local Chan lesson 24.
- **Allowed changes:** `artifacts/macd/`, this task record, memory, and log. Keep memo 008 S7 empty.
- **Acceptance checks:** Actual EMA12/26/9 computation from synthetic closes; warm-up data retained; price higher-high/DIF lower-high comparison verified per upward leg; readable figure legends and simulated-data labels; indicator divergence distinguished from formal Chan背驰.
- **Assignment:** Root renders/verifies; `macd_figure_check` reviews concepts read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Two standalone figures generated, with renderer, full synthetic input/output CSV, and source/formula notes. No memo edits.
- **Evidence:** `artifacts/macd/macd-components.png`, `artifacts/macd/macd-divergence.png`; price peaks119.993→124.979, DIF peaks4.387→2.226, 160 warm-up/141 displayed bars. Numeric assertions and visual checks passed; read-only reviewer confirmed formulas, sign convention, per-leg comparison and Chan framing; both PNGs/local links and `git diff --check` passed.
- **Blockers:** none.
- **Next action:** none; deliver both figures in the chat.
