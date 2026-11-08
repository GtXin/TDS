## Task
- **ID:** 20261107-bar-merge-repo-comparison
- **Goal:** Explain raw/merged bar series and indicator responsibilities using established repository sources, in chat only.
- **Inputs:** User questions; official CZSC, chan.py, vn.py, TA-Lib, Backtrader, vectorbt and QuantConnect LEAN code/docs.
- **Allowed changes:** This record and logXW.md only. Research agent is read-only; no memo edits.
- **Acceptance checks:** Cite actual bar/merge/indicator boundaries; distinguish observations from recommendations.
- **Assignment:** Root checks general quant toolboxes; `essential_memo_check` checks chan.py and CZSC read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Verified distinct raw/merged types in Chan repositories and separate indicator APIs in general toolboxes. Indicators are optional design choices, not defining bar fields. Recommendation remains a proposal for chat; no memo edits.
- **Evidence:** Inspected official [TA-Lib API](https://github.com/TA-Lib/ta-lib-python), [Backtrader concepts](https://www.backtrader.com/docu/concepts/), [vectorbt MA](https://vectorbt.dev/api/indicators/basic/), [LEAN indicators](https://www.quantconnect.com/docs/v2/writing-algorithms/indicators/manual-indicators) and [consolidators](https://www.quantconnect.com/docs/v2/writing-algorithms/consolidating-data/getting-started), vn.py trader object.py/utility.py. BarData has market fields; ArrayManager combines arrays and indicators. Agent verified [chan.py units](https://github.com/Vespa314/chan.py/blob/main/KLine/KLine_Unit.py), [list](https://github.com/Vespa314/chan.py/blob/main/KLine/KLine_List.py), [merged combiner](https://github.com/Vespa314/chan.py/blob/main/Combiner/KLine_Combiner.py), and [CZSC bars](https://github.com/waditu/czsc/blob/master/crates/czsc-core/src/objects/bar.rs). Caveats: chan.py attaches indicator outputs to raw units; CZSC exposes caches and limits stored constituents in its merge implementation. No universal cache-free separation claimed.
- **Blockers:** None.
- **Next action:** Discuss which optional members the user wants; change memos only when requested.
