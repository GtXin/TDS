# Task
- **ID:** 20261108-memo009-remaining-methods
- **Goal:** Add concise proposed methods tables to the remaining feature records and derived series in memo 009 sections002.d–002.o. Leave DecisionStep methods empty and ChanTable methods for later, as the user now specifies.
- **Inputs:** User request; docs/memo/memoWX_009_designPatternForChanFeatures.md; CodexMemory.md; memo 006 writing guide.
- **Allowed changes:** Root owns memo 009 and pre-edit backups, CodexMemory.md, this record and logXW.md. Delegated reviewers are read-only; no source implementation, unrelated memos or original references may change.
- **Acceptance checks:** All fourteen Kline/feature record and series sections002.b–002.o have methods tables; preserve all fields, existing Kline/KlineTSeries tables, class names and source/trace/time/ID decisions. Leave DecisionStep and ChanTable unchanged. Use snake_case/special methods, clear factory/instance semantics, immutable results and tuple slicing. Keep adapters/rendering separate; avoid proposing unknown Chan rules as settled algorithms. Verify headings, links/index, citations, backup equality and whitespace.
- **Assignment:** Root authors; read-only reviewers check individual records and derived-series responsibilities in parallel.
- **Status:** done
# Result and handoff
- **Outcome:** After the earlier stop, user resumed with DecisionStep and ChanTable methods excluded. Added two-method tables to six feature records and expanded/added twelve-method tables to six derived series. Preserved existing Kline/KlineTSeries and both deferred sections.
- **Evidence:** Memo 009 sections002.d–002.o; pre-edit backups ending `20261108_014207_012333.md` and `20261108_014405_156177.md` were byte-verified before edits. Read-only reviewers review_record_methods and review_chantable checked local/source validation, integer IDs, factory/source/trace behavior and unchanged fields/deferred sections; refined chronology and Zoushi source/level wording. Root checks passed: fourteen class method tables, two methods per added record/twelve per derived series, all original member tables/headings/references preserved, exact002.b/c/p/q preservation, ID types, local links/index, citation order, whitespace and git diff --check. Updated CodexMemory.md; no Python implementation changed.
- **Blockers:** None.
- **Next action:** User reviews the proposed feature/series methods. Leave DecisionStep methods empty; save ChanTable methods for the final design discussion.
