## 000 — Purpose
Extract the Obsidian workspace's useful practices for reading sources, writing essential memos, and preserving knowledge. These are recommendations for TDS; this memo does not install tools or change standing instructions.
## 001 — Source → extraction → memo
- Start from the user's question, the exact named source, and the relevant instructions and memory; use canonical files rather than nearby copies. [S1, S2]
- Preserve originals and register source ID, path or URL, title, version/date, and extraction status; retain size and checksum when copying or managing derivatives. [S5]
- Keep extraction separate from interpretation: save readable text or timestamped transcripts, retaining page, slide, sheet, table, or timestamp locators. Record OCR needs, failures, incomplete downloads, and unreadable material. [S3–S5]
- Build the source's knowledge structure before summarizing: definitions, mechanisms, assumptions, rules, exceptions, mistakes, and applications. Link illustrations to the claims they actually support. [S3, S4]
- Distinguish source claims, our interpretations, proposed actions, agreed decisions, and tested results. Indexes and keyword previews support navigation, not full review. [S3, S5, S7]
## 002 — Write the memo
- Start with the current decision or question; include purpose, status, decisions, open questions, and next action only where useful. Develop the requested section and update only changed content. [S1, S3]
- Keep numbered sections compact; remove repeated labels, filler, and unnecessary background. Preserve quantities, units, conditions, citations, and reasoning when shortening. [S1, S7]
- Explain concrete objects first, then their function and an example; introduce context before new claims and connect each addition to the argument. For learning notes, separate a concept, its procedure, one instance, and its relationships. [S1, S4, S8]
- Gather context and refine section by section with the user. Keep detailed extraction and authoring rationale outside the essential reader-facing memo. [S3, S8, S9]
- Follow the destination memo's naming and heading conventions; use the requested number or check the next unused one. Keep spacing tight while allowing Markdown syntax to render correctly in Obsidian. [S2, S8]
## 003 — Route knowledge to the right place
- **Memo:** the focused discussion, evidence, options, and decisions for a topic.
- **Memory:** reusable context, preferences, decisions, and handoff lessons; store task-specific knowledge near the task and repo-wide knowledge centrally, rather than copying raw conversations.
- **AGENTS.md:** knowledge deliberately adopted as a standing rule.
- **Log:** major changes affecting structure, navigation, ownership, or continuity; not every wording edit.
Read relevant instructions and memory when resuming work; reconcile stale memory with current sources, decisions, and actual results. This separation is established in the source workspace; TDS memory filenames and any new log files still need a separate decision. [S1, S2, S6]
## 004 — Check evidence and completion
- Check extraction coverage and meaning, not merely output existence, file length, or a successful command. Empty PDF text, lost table order, noisy transcripts, and conflicting definitions need explicit limitations. [S4, S5]
- Use precise states: retrieved is not read; drafted is not verified; an example is not project evidence; not found in a search does not prove nonexistent. [S5, S7]
- Reopen critical sources to check claims, numbers, units, versions, and links. A fresh reader should be able to identify the purpose, decision, supporting evidence, and next step without our chat. [S7–S9]
- Record input versions, actual checks, outputs, unresolved items, and next action; keep AI-generation details such as skill/model/prompt in a short trace appendix when relevant. [S2, S8]
## 005 — Preserve work and continuity
- Keep edits within the requested scope, preserve user changes, and avoid broad rewrites. The source workflow uses nearby `backups/<epoch-seconds>-<filename>` before edits and task-local `temp/` for scratch work. [S1]
- Preserve linked figures and attachments; after moves or copies, verify contents and repair links. A local checksum match does not establish cloud synchronization. [S2, S7]
- Track durable notes, source indexes, and intentional artifacts; exclude disposable caches and scratch state. Ignoring a source does not preserve it in a clone: record its recovery location and derivative lineage. [S2, S5]
## 006 — Apply selectively to TDS
- Use existing `references/`, `data/raw/`, `docs/memo/`, `mas/tasks/`, and `artifacts/`; do not copy the source workspace's directory tree or create new memory infrastructure from this memo alone.
- For Chan work, distinguish original theory, lecturer claims, Sid's critiques, reference code, and tested results; retain linked charts and rule variants. Algorithm correctness and trading effectiveness need different evidence. [S10]
- Keep TDS's portable `.codex/`, `.agents/`, and shared MAS configuration versionable; the source workspace's blanket ignore rules for those folders do not fit this repo. [S2]
- Borrow the extraction/indexing approach, not hard-coded Windows paths, unrestricted runner settings, fixed note-length ratios, or file-existence-only quality checks. Scripts were inspected, not rerun. [S4–S6]
- The source workspace's 50 MiB guard preserves originals, records exact ignore entries and an inventory, and flags tracked large files without automatic history changes; adopting a TDS guard is a separate decision. [S1, S6]
## 007 — Scan scope and source anchors
Inventoried 1,894 visible files and keyword-screened all 258 indexed Markdown files; read all 20 indexed memory files and five `AGENTS.md` files, plus selected workflows, scripts, manifests, hidden skills, and historical records. This was a text/code review, not a full reading or visual inspection of every PDF, image, or video; no source scripts were executed.
Source paths below are relative to `/Users/coder/Public/EngineGit/obisidianCodex2MD/`.
- **S1:** `AGENTS.md`, lines 7–93 — scope, backups, memory, memo style, large-file policy.
- **S2:** `CodexMemory.md`, lines 3–40, 59–78, 129–148 — layered memory, compact style, Git policy, verified relocations.
- **S3:** `ObisdianKBLab/Obisidan_basic.md`, lines 437–461, 506–517 — source reading, project state, selected output.
- **S4:** `Walle/rules/script2Notes/script2Notes.md`, lines 73–140, 173–228; `LittleSix/Walle_LittleSix.md`, lines 39–77 — extraction, cohesion, visuals, quality limits.
- **S5:** `ODA submission package/extract_sources.py`, lines 23–167; `ODA submission package/build_source_reading_index.py`, lines 49–190; `EyegorithmSBIR/src/reference/README.md`, lines 3–11 — extraction, provenance, indexes, retrieval status.
- **S6:** `Walle/Walle_interface.md`, lines 25–29; `Walle/CodexMemory.md`, line 62; `Walle/memo/memo_006_testRd1.md`, lines 211–272; `ObisidianCodex2MDWorkflow/scan_large_files.py`, lines 15–92 — planned versus actual work and preservation controls.
- **S7:** `ODA QMS/CodexMemory.md`, lines 25–36, 56–66, 89–91; `projDragonFly/AGENTS.md`, lines 3–8; `The Eye Story Book/SourceFileLog.md`, lines 3–48 — evidence status, precision, source recovery.
- **S8:** `multi-agent-system/memo004_thoughts_ScarlettGIT.md`, lines 9–29; `multi-agent-system/memo005_thoughts_ScarlettSkill.md`, lines 8–25 — atomic concepts, review, traceability, naming.
- **S9:** `.claude/skills/doc-coauthoring/SKILL.md`, lines 28–30, 104–106, 242–281 — context, refinement, fresh-reader testing.
- **S10:** `TheoryChan/CodexMemory.md`, lines 20–43, 59–67 — attributed interpretations, chart dependencies, cautious claims.
