# Memo013 class interface clarity
## Task
- **ID:** 20261109-memo013-class-interface-clarity
- **Goal:** Make003 explicitly show class count and members/methods for each class, with module functions and examples separated.
- **Inputs:** Current memo013, active Kline/domain CSV/plot sources, project/memo instructions.
- **Allowed changes:** Backed-up memo013003 and required subsection cross-reference, this task,memory/log. Preserve code, pictures, examples and other memo content.
- **Acceptance checks:** Exactly2 memo013 classes with complete9+1 stored fields and correct methods/signatures/options, clear internal hook/function/external class distinctions; preserve example code/image links, verify source inventory, links, numbering and diff.
- **Assignment:** Root drafts/verifies; handoff_checklist independently inventories source read-only.
- **Status:** done
## Result and handoff
- **Outcome:** Reorganized003.a class overview,003.b Kline members/methods,003.c KlineTSeries members/methods/plot arguments,003.d module functions,003.e preserved examples and003.f preserved pictures. Verification passed.
- **Evidence:** docs/memo/memoWX_013_klineFamily.md; exact pre-edit backup docs/memo/backups/memoWX_013_klineFamily__20261109_190638_277820.md.
- **Blockers:** none
- **Next action:** none

## Protected source and picture hashes
```json
{
  "src/chanlab/visualization/merged_kline_plot.py": "b63c4cb5de90c66305c827dbbc1d5e23bb18df16881f4f25ef334504ff0db0d0",
  "src/chanlab/visualization/kline_plot.py": "063fc116173114565c9f1404eb9aac48ea6e8305a2f07dd09e4b136e828a47fd",
  "src/chanlab/algo/chan_table.py": "1ed61d3feece76868f550a5c07e9b0e9434e9ad83d825bbf178a30d00b8a0d4d",
  "src/chanlab/algo/merged_kline.py": "9fe35bb6ea21dad13a8efddf6cc2d8e1cd06e9324284ab67f829e6656818ff4b",
  "src/chanlab/algo/kline.py": "3a95e35815e86b9407dd98ebb506916ece0a5951b929be82eabdc03680b87374",
  "src/chanlab/data/chan_table_csv.py": "a0d3fd2ef1b021716e5be11a6cf011c97dee7e31463fea9c0ef3c5bd37cd824f",
  "src/chanlab/data/kline_csv.py": "dc165bcbf20d2967ab2e13176166c80e43ba836db55062094ec4f455c9a37c77",
  "src/chanlab/data/merged_kline_table.py": "d1bf346717b191224606067a1db0f15fccb3be2341bba2791679f9fff965aef0",
  "docs/memo/memoWX_013_klineFamily/cc-last200-calendar-time.png": "44ddf408dd9f18ce5ef44815b6a8debfaf156e4bbb3e74fec9b4c75d2726ff6a",
  "docs/memo/memoWX_013_klineFamily/cc-last40-detail.png": "f8c5635b9348656f5cbbdec62acbc04dc7d05854b2b09c4732f7801230988708",
  "docs/memo/memoWX_013_klineFamily/cc-last200-consecutive-bars.png": "e7b5b3b393ffbe629b8955d324969dbd9d041049413f43807844bf73ffdb000d"
}
```

## Actual verification
- Independent read-only source inventory and rewritten003 review passed after Markdown union-pipe escaping and explicit price-bound refinement.
- Runtime dataclass fields/AST confirmed exactly2 classes,9 Kline members,1 KlineTSeries member and all authored methods. Inspected plot signature/defaults match5 option rows. Supporting functions separated from class methods.
- Both Python examples and all3 image embeds exactly preserved;003 prefix and Appendix/references unchanged except required003.f picture cross-reference. Source/image hashes, table column counts,local links and git diff --check passed.
- Documentation-only; no source/data/image changes or regression-test claims added. Existing automatic dataclass machinery is identified separately from the domain interface.
