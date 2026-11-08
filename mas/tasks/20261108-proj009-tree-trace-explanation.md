## Task
- **ID:** 20261108-proj009-tree-trace-explanation
- **Goal:** Use later proj009 rule trees to explain where specifications, executable decisions and per-point traces live; chat only.
- **Inputs:** User clarification; proj009 memos0036/0040/0041/0042; relevant experiment code; memo009 requirements.
- **Allowed changes:** This record, memory next action and logXW.md. No memo/source edits. Reviewer is read-only.
- **Acceptance checks:** Locate actual tree sections; distinguish spec from implementation and existing summary trace from proposed complete runtime trace; give one concrete tree-node-to-code-to-report example without inventing existing APIs.
- **Assignment:** Root reads tree structure; reviewer checks relevant code and trace limitations.
- **Status:** done
## Result and handoff
- **Outcome:** Located memo0042's actual written tree and separated it from executable code and proposed per-run decision logs. A class needs a reference to the tree/version, an ordered runtime trace and result-to-trace links; it need not contain another full tree.
- **Evidence:** Memo0042 lines124–126 gives DataChecker_001, threshold50 and branch2.1.b; its sample has62 pens. The corresponding example is hypothetical, not current KWX behavior. Memo0040 lines595/662 and live `_kwx_xianduan/algo/trace.py:118–150` show StructTrace is summary metadata, not every visited decision. Independent reviewer checked live `xianduan.py:264–265` (KWX minimum3), trace construction1109–1122, and diagnostic wrappers in `check_memo0040_kwx_tree.py:58–114`. Reused checkers/loop visits need full node location and occurrence/call context.
- **Blockers:** No blocker to explanation. Before implementing memo0042, resolve its reuse-table labels117–118, which reverse main-tree2.2.a/b labels; no rule correction inferred here.
- **Next action:** Discuss the tree/code/log/report mapping; record or implement only when requested.
