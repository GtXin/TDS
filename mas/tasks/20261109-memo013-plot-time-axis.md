# Memo013 plotting time-axis correction
## Task
- **ID:** 20261109-memo013-plot-time-axis
- **Goal:** Investigate the atypical blank intervals, provide consecutive observed-bar spacing and preserve an explicit elapsed-time option; regenerate/inspect samples and update013 coherently.
- **Inputs:** Current raw plot API/helper/generator, existing CC master/original timestamps, Plotly category/date docs, merged renderer dependency and project/memo instructions.
- **Allowed changes:** Raw plot wrapper/helper/tests, generator/sample artifacts with history preserved, backed-up memo013, artifact README/verification, task/memory/log. Minimal merged renderer compatibility pin and regression only; retain026 behavior. No source datasets, dependencies or algorithms changed.
- **Acceptance checks:** Diagnose against original epochs/UTC labels; default category/equal observed-bar spacing, show_gaps=True date axis; source values/order preserved, shared volume alignment, full/sliced/empty/missing-extra/wrapper cases, merged date-mode preservation, regression/Ruff/type/format checks; inspect regenerated PNGs, links/examples.
- **Assignment:** Root implements/verifies; handoff_checklist independently reviewed cause/category compatibility read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Root/independent review confirmed elapsed-time geometry. Last200 bars span18240 minutes with35 intervals above15minutes, including two58h15m jumps. Original epoch/UTC/helper timestamps match. This does not distinguish closures from missing records without a calendar.
- **Evidence:** Source original/master comparisons and plot helper date-axis setting; earlier sample artifacts preserved in artifacts/kline/history/20261109_183242_352802. Generator also forced date axes after plotting and must be corrected.
- **Blockers:** none
- **Next action:** none. Both raw axis modes, updated samples and embedded memo pictures are implemented and verified.
## Design boundary
The x axis becomes an ordered bar sequence for financial-chart inspection, not an elapsed-time measure. No source records are filled, removed or resampled. Keep true UTC timestamps in trace data and labels. Category axes compress every absent interval, including unclassified gaps; no exchange calendar or completeness claim is introduced. Original calendar mode stays available. Python Pro typed/error/test guidance reused; no new tooling/configuration.

## Pictures and coherent memo update
- User requested both options, then pictures in memo013. Added003.e with three embedded sibling PNGs (default200-bar volume, same200 calendar mode,40-bar close-up), each with its command. Complete memo backed up before updating003/API/options,002.g and Appendix; old previews/evidence preserved under artifacts/kline/history/.
- Regenerated actual helper outputs (generator no longer overrides axis type); all three viewed and readable, source-value/protected hashes match.14 raw plotting tests,40 raw+merged focused tests and205 full tests passed. Ruff,Black6files,strict mypy2rawfiles pass; core/plot128-case run passes,225 statements/15missed=93% coverage.
- Independent read-only review passed category/date modes, shared-axis categories, wrapper forwarding, generator and merged compatibility pin.

## Final verification
- Executed both updated memo003 examples; default category and calendar figures retain identical original timestamps.3 embedded sibling images and their copy hashes, protected raw/configuration hashes, all local links,000–003 headings and citations1–8 passed.
- git diff --check passed. Full regression205 passed; scoped Ruff,strict mypy,Black and128-case core/plot coverage(93%,225 statements/15 missed) passed. Calendar-mode merged regression preserved.
- All3 PNGs visually inspected after actual Plotly/Chrome export; charts readable with uniform observed-bar spacing/default or elapsed spacing as selected. Existing pre-change assets retained in history. User’s pictures request is fulfilled in memo013003.e.
