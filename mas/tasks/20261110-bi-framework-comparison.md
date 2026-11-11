# Task

- **ID:** 20261110-bi-framework-comparison
- **Goal:** Explain the previous implemented020/028 candidate-search framework versus the user's side-note progression without mixing initialization, cached-pair extension and later proposed reverse alternatives.
- **Inputs:** Current memo020 side note and002.a; `src/chanlab/algo/bi.py:112`; prior discussion clarifications.
- **Allowed changes:** Root owns this task, a concise memory pointer and `logXW.md`; reviewer is read-only. No memo/source/test/policy edits.
- **Acceptance checks:** Compare actual initial-start selection, firstB choices, equal endpoints, invalid stronger extension, qualified reversal, commitment and output. Preserve that both scan forward locally and current production has no skip-qualified-reverse branch. Distinguish conceptual differences from correctness claims.
- **Assignment:** Root reads current note/code; independent read-only reviewer checks comparison claims.
- **Status:** done

# Result and handoff

- **Outcome:** Both use forward local pair checks, provisional endpoints and reversal. Old implemented framework searches a constrained candidate family via initialB-skip/equal-endpoint alternatives and prefix restoration; user's note maintains one rolling main route, an initially empty Bi002 and next-start-only Bi001, with no recovery/EOF semantics yet. Different initial selection, equal-endpoint handling and failed stronger extension policies are explicit. User6.a writes a prior pair to results without defining revocability; no permanence inferred.
- **Evidence:** Current note and production candidate loop read directly; independent conceptual review agrees. Current code does not save a skip-qualified-reverse branch; that is a later unadopted recommendation. No claim of exhaustive geometric enumeration, user-algorithm correctness or linear complexity. No new execution/tests or memo/source changes.
- **Blockers:** None for comparison; complete correctness of user's unfinished transitions remains separate.
- **Next action:** Use the user's staged main progression for subsequent discussion, reviewing added recovery choices separately before any020 change.
