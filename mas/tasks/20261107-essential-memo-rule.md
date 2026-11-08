## Task
- **ID:** 20261107-essential-memo-rule
- **Goal:** Keep conversation in chat and memos essential; remove the unsolicited memo009 research expansion and add the rule to the memo writing guide too.
- **Inputs:** User correction; AGENTS.md; memo006; memo009 and its pre-research backup.
- **Allowed changes:** AGENTS.md, memos006/009 and their backups, CodexMemory.md, this record, logXW.md. Review agent is read-only.
- **Acceptance checks:** One clear agent rule, one essential-only sentence in memo006; memo009 matches its pre-research content; scope and empty implementation preserved; backups, links, whitespace checked.
- **Assignment:** Codex; independent read-only verification.
- **Status:** done
## Result and handoff
- **Outcome:** Added essential-only rules to AGENTS.md and memo006; restored memo009 to its pre-research version and aligned memory. Subsequent design explanations remain in chat.
- **Evidence:** Memo009 byte-identical to backup `__20261107_202702_379101`; pre-restoration backup `__20261107_203004_695049` retained. Memo006 differs from backup `__20261107_203035_470821` by exactly one sentence. Independent read-only review and local checks confirmed scope, empty implementation, backups, actual links, index and `git diff --check`. A broad link check initially treated a preexisting guide example as a real file; corrected the check without changing the example.
- **Blockers:** None.
- **Next action:** none.
