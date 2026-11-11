# Task

- **ID:** 20261110-memo020-prompt-open-tail
- **Goal:** Add the user's clarified nonblocking traversal, immutable final output and unfinished open-tail behavior to the existing collaboration prompt in memo020004.
- **Inputs:** User's current request and latest EOF clarification; existing004 prompt; memo006.
- **Allowed changes:** Root owns only the004 prompt in memo020, its required full backup, this task, concise memory update and log. Reviewer is read-only. Preserve the original side note, algorithm/reasoning, appendices, References, index,028 and code.
- **Acceptance checks:** Three explicit prompt constraints cover final-versus-pending boundary, continued traversal/EOF and verification scope; do not claim future completion is guaranteed. Adjust the existing pending-rules phrase to refer to submission criteria and changes inside buffers. Full backup first; byte-exact preservation outside prompt; independent wording review and scoped whitespace checks.
- **Assignment:** Root edits; independent reviewer checks meaning/scope.
- **Status:** done

# Result and handoff

- **Outcome:** Added three004 prompt clauses for immutable final output versus adjustable pending buffers, continued traversal/normal EOF open tail, and verification scope without guaranteed future completion. Existing pending-rules phrase now refers to final-submission criteria and adjustments within buffers. Original side note and every byte outside the prompt remain unchanged; no algorithm rewrite.
- **Evidence:** Full pre-edit backup `docs/memo/backups/memoWX_020_Chan_bi__20261110_204404_425591.md`; before SHA256 `56913087a1fc728c86128cbcf9cf67802e72657b8b6278262ca4c7c4eb8c5768`, after `bab10dcf46a4b93d0a2da68e07e48e2d2c71e7dde847bbbe110c9178b908ca09`. Exact prefix/suffix checks prove scope; all three clauses occur once and add no trailing whitespace. Independent wording review PASS; saved text explicitly returns atEOF, so continued traversal is not an infiniteEOF loop. Index filename unchanged. Memory now records the clarified open-tail contract and avoids treating EOF nonclosure alone as proof of failure.
- **Blockers:** None.
- **Next action:** Use the updated prompt for subsequent algorithm discussion; revise002.a/003 only under a separate requested change.
