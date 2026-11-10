# Memo026 alignment with updated memo013
## Task
- **ID:**20261109-memo026-interface-alignment
- **Goal:** Reorganize026 around013's updated class-centered interface and owned raw provenance; preserve the two-class implementation.
- **Inputs:** current013/026,009,source/table/merged interfaces,memo006 guide and existing charts.
- **Allowed changes:** backed-up026,new sibling picture copies,documentation verifier/evidence,this task,memory/log. Source/tests/dependencies/raw data/013/original charts protected.
- **Acceptance checks:** exact2 class and8+6 field/public-method inventory; method-only examples using KlineTSeries.read_csv and raw.context; correct table/source/plot boundary;links/table columns/section/index checks;byte-identical chart copies;execute examples and check protected hashes.
- **Assignment:**Codex, direct documentation work.
- **Status:**done
## Result and handoff
- **Outcome:**026 reorganized to match013:class count,per-class members/methods,call options,object workflow,examples and embedded pictures;private implementation/data details moved to Appendix.
- **Evidence:**artifacts/mas/memo026-interface-alignment/.
- **Blockers:**none.
- **Next action:**none for this documentation alignment.

## Actual checks
- Read current013 and raw/merged/table implementation; confirmed013 now owns context and exposes KlineTSeries.read_csv/write_csv. Updated026 examples to use that classfactory and explicit ChanTable.from_source_series(raw,context=raw.context),matching current behavior rather than assuming automatic context propagation.
- Backed up026 before each of two edits. Reorganized003.a–003.f to match013 and condensed000/001/002 to distinguish implemented scope from historical checkpoints. No extra classes/members or functionality added. Merged plot remains date-axis,explicitly distinguished from raw show_gaps default.
- AST confirms2 classes,8+6 members and every authored public/private method documented (public003,privateAppendix). Four Python blocks executed successfully,bothsource entry paths and full10060raw/6200result/table/context/DataFrame workflow included. Links,table widths,section order and uniqueindex passed.
- Copied2 existing inspected PNGs byte-for-byte into026 sibling picture folder and embedded them in003.f;original charts unchanged. verification.json records SHA-256 values.
- Protected22 source/test/config/sample/013/original-image files before work;all hashes unchanged. No implementation test-suite rerun for documentation-only changes. Existing regression counts retained with explicit historical checkpoint labels.
- Updated documentation verifier for private Appendix and word-boundary class-name matching;its initial substring test wrongly matched Work in Worked,then passed after correction. Updated verifier output/document evidence under artifacts/mas/merged-kline-two-class/checks/;new task evidence under artifacts/mas/memo026-interface-alignment/.
- git diff --check passed.
