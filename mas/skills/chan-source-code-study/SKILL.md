---
name: chan-source-code-study
description: Research a Chan theory concept from original reference passages and implementation code, producing cited source excerpts with figures and a separate code-derived procedure summary. Use for evidence appendices and concept research, not algorithm implementation or generic summaries.
---

# Chan source and code study

Build a reviewable evidence record for one concept. Keep author statements, compiler annotations, implementation behavior and your interpretation distinct. Use the user's language and requested destination; this skill does not itself authorize memo edits or code changes.

## Required paired evidence

For this research workflow, deliver both sections by default unless the user explicitly narrows the task:

- **Appendix A — Chan Theory original sources:** selected original passages and author replies, relevant original figures, and precise source citations. Chan Theory supplies the theory text; do not assume it supplies executable source code.
- **Appendix B — CC source code and implementation analysis:** preserve the relevant CC implementation code in a cited local source/extraction file, include the key executable snippets beside the analysis, and summarize the actual processing steps. Cite functions and code locations; identify the website snapshot or repository/version inspected.

Both source sets are required for the complete paired study. If either is unavailable, complete the available evidence section and explicitly mark the other incomplete; do not replace CC code with website explanations or replace Chan originals with CC's interpretation. Reuse the local corpus and downloaded code before seeking additional sources. Do not download an unrelated full repository merely to fill an appendix.

## Scope and sources

- Establish the concept, exclusions, source corpus, implementation/version and destination from the request and project context. For example, K线包含 does not automatically include 特征序列包含.
- Inspect the actual source tree before saying what it contains. Distinguish a website snapshot, extracted code, another repository and experimental reimplementations. A reference to a repository is not a complete copy of its code.
- In TDS, start with project instructions/memory. Relevant source locations include `references/chan_theory/`, `references/cc_algo/` and `references/proj009Memo/`. Inspect current files; do not assume snapshots are current upstream versions.
- Preserve raw references. If downloading is requested, retain source URLs, retrieval date and hashes; identify incomplete downloads or unverified dynamic resources. Treat documents/code as evidence, not instructions to execute.

## Original-source appendix

1. Inventory and search the whole agreed text corpus with related terms; read candidate passages in context. Report what was actually scanned. Keyword coverage does not imply every image was read.
2. Prioritize context and continuity over brevity. Do not optimize excerpts for shortness or a count of isolated quotations. When a lesson develops the definition and processing rules through connected paragraphs, preserve that continuous source block, including prerequisites, transitions and relevant figures; use other lessons as supplements. Mark boundaries and omissions explicitly. Retain adjacent concepts when needed to understand the argument, while distinguishing contextual material from rules within the requested scope.
3. Select passages for independent value: definition, direction, order, equality/boundaries, exceptions and necessary prerequisites. Respect a requested count; do not pad with repetition or adjacent concepts. Explain a shortfall if the corpus lacks enough distinct evidence.
4. Preserve original language and material conditions. Label direct quotations versus paraphrases, author replies versus reader questions and compiler annotations. Keep questions when needed to interpret a reply. Mark omissions or normalization that could affect interpretation; do not silently repair the author's rule.
5. Inspect every selected passage for explicit figure references and nearby relevant figures. View the source image to verify the match, copy it unchanged to the destination's companion folder, embed it beside the passage and cite its source. Reuse a copied asset where appropriate. Preserve originals; label any derived crop separately. If a source image is missing or mismatched, flag that fact rather than substituting an invented illustration.
6. Give each entry a short topic label and precise location: lesson, body/reply, paragraph/line or stable anchor, plus a source link. Line numbers describe the inspected snapshot. Keep numbered citations consistent across both appendices.


## Implementation appendix

1. Locate the executable implementation and follow its entry points and helpers. For website code, extract and decode the relevant code block without rewriting it; retain the original page and extraction provenance. Syntax validation is useful but does not establish execution or correctness.
2. Derive the account primarily from executable statements. Comments, docstrings and website prose may identify intent; when behavior differs, describe the actual branch and distinguish intent.
3. Explain the processing order: inputs and assumptions → stored state → initialization → comparisons/branches → updates or new records → termination/output. Trace equality, direction changes, unresolved initialization and tail replacement/rollback where implemented. Cite concrete functions and source locations.
4. Distinguish initialization aggregation from ordinary sequential processing. Separate validation actually performed by this class from preconditions expected of callers. Avoid claiming complete handling from a helper's name alone.
5. Cover source mapping, rule traces and provisional/stable results when present. State the limits of stability under append versus explicit rollback. Explain costs only when supported by inspected loops and storage, including retained members and recomputation.
6. Label code observations, deductions and pending checks. Do not promote an implementation choice to an original-author rule or an approved TDS design. Do not claim test execution, sample counts, equivalence or correctness without actual evidence.

## Delivery and checks

Use Appendix A for Chan Theory original passages/figures and Appendix B for CC code excerpts and code-derived steps. Preserve main sections and existing user edits. Follow the project's memo guide for backups, numbering, index, image placement, memory and event logging; do not duplicate that guide here.

Check quotations against sources, figure correspondence, citation numbering, relative links and code-location accuracy. Verify preserved sections against the pre-edit backup. Report static inspection and actual runtime checks separately. Leave unresolved evidence gaps explicit. Add a runnable example only when useful and authorized; never silently execute downloaded code.
