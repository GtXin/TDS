---
title: memo0003_memoguidance
tags:
  - memo
  - documentation
  - workflow
  - project-009
status: active
source:
  - docs/memo/memo0002_pythonNotes.md
  - ../pythonCatchup/pythonNotes.1788155588.bak.md
created: 2026-08-31
---

# memo0003_memoguidance

## 1. Session Overview

### 1.a Purpose

- Keep Project 009 memo writing consistent.
- Make long notes easier to split into focused reusable memos.
- Preserve the readable style from `memo0002_pythonNotes.md`.
- Give future agents a concrete memo format to follow.

### 1.b Source Material

> [concept] **Source material** means the notes, repo rules, commands, and local
> facts used to create a memo.

> [note] This guidance is extracted from:
>
> - `docs/memo/memo0002_pythonNotes.md`
> - `../pythonCatchup/pythonNotes.1788155588.bak.md`
> - `AGENTS.md`, Knowledge Memos and Project Memo Files sections

### 1.c Target Outcome

- A memo answers one practical question.
- A memo is short enough to scan.
- A memo records evidence, not only opinion.
- A memo can be used without rereading the whole source note.
- A memo does not hide important commands, paths, decisions, or open questions.

### 1.d Core Decision

> [decision] Project 009 memo files live under `docs/memo/` and use the
> `memo000N_` filename prefix.

> [decision] Use separate focused memos when a topic becomes reusable across
> the project. Keep moved original notes intact unless the user explicitly asks
> to rewrite them.

> [decision] Keep memo style close to `memo0002_pythonNotes.md`: numbered
> chapters, compact bullets, bracket tags, concrete workflows, and short
> examples. Bracket tags are part of the intended human-readable memo style;
> YAML front matter and long metadata headers are not required by default.

## 2. Memo Location And Naming

### 2.a Folder

> [convention] Memo folder
>
> - System: Project 009 documentation.
> - Path: `docs/memo/`.
> - Use: moved source notes, setup memos, workflow guidance, extracted project
>   knowledge, and readable onboarding notes.

### 2.b Filename Rule

> [convention] Memo filename
>
> - Exact shape: `memo000N_name.md`.
> - Prefix: `memo000N_`, with no underscore between `memo` and the number.
> - Number: four digits, starting at `0001`.
> - Separator: one underscore after the four-digit number.
> - Extension: `.md`.
> - Sequence: choose the next stable four-digit number by project importance
>   and dependency order.
> - Skip: if a number is intentionally skipped, record the reason in memo
>   guidance and in the next memo that uses the later number.
> - Default language: lowercase English topic words.
> - Exception: preserve Chinese or original language when moving a source note.
> - Do not use the old form `memo_000N_name.md`.

> > [example] Current memo names
> >
> > ```text
> > docs/memo/memo0001_项目009设想_20260831.md
> > docs/memo/memo0002_pythonNotes.md
> > docs/memo/memo0003_memoguidance.md
> > docs/memo/memo0004_mac_setup.md
> > docs/memo/memo0005_folder_structure.md
> > docs/memo/memo0006_qlib_windows_venv.md
> > docs/memo/memo0007_qlib_data_structure.md
> > docs/memo/memo0008_qlib_macos_venv.md
> > docs/memo/memo0009_class_kline.md
> > docs/memo/memo0010_class_kline_t_series.md
> > docs/memo/memo0011_py_class_system.md
> > docs/memo/memo0012_cc_csv_to_zoushi_reference.md
> > docs/memo/memo0015_oop_trading_architecture.md
> > docs/memo/memo0016_class_csv_file_kline_t_series.md
> > docs/memo/memo0017_class_kline_t_series_chart.md
> > docs/memo/memo0018_first_source_promotion.md
> > docs/memo/memo0019_InterfaceChan.md
> > docs/memo/memo0020_class_merged_kline_series.md
> > ```

> [note] `memo0013` and `memo0014` are intentionally unused as of 2026-08-31 by
> user preference.

### 2.c Naming Smell Check

> [note] If a filename does not explain the topic, rename it before the memo
> spreads into references.

> [note] Prefer `memo0004_mac_setup.md` over `memo_setup.md`, because
> the specific name is easier to search later.

> [note] Prefer `memo0004_mac_setup.md` over `memo_0004_mac_setup.md`, because
> the project convention keeps `memo` and the four-digit number joined.

### 2.d Naming Enforcement

> [decision] Memo filename numbering is enforced for Markdown files directly
> under `docs/memo/`.

> [convention] Enforced filename pattern:
>
> ```text
> memo[0-9][0-9][0-9][0-9]_*.md
> ```

> [convention] Forbidden filename patterns:
>
> ```text
> memo_000N_*.md
> memo_topic.md
> 000N_topic.md
> ```

> [workflow] Enforce memo filenames
>
> - Step 1: list memo files.
>   - System: filesystem.
>   - Path: `docs/memo/`.
>   - Verify: every direct Markdown file matches `memo000N_`.
>
> - Step 2: check for unnumbered memo files.
>   - System: filename convention.
>   - Path: `docs/memo/*.md`.
>   - Verify: no file remains as `memo_topic.md` when it should be
>     `memo000N_topic.md`.
>
> - Step 3: update references after any rename.
>   - System: project documentation.
>   - Path: `AGENTS.md`, `README.md`, `plan.md`, `docs/status.md`,
>     `docs/phases/**`, and `docs/memo/**`.
>   - Verify: search finds the new path and no live document references the old
>     path.
>
> - Step 4: log the rename or exception.
>   - System: master log.
>   - Path: `docs/master-log.md`.
>   - Verify: latest log entry records the rename or the explicit exception.

> > [example] Filename check command
> >
> > ```zsh
> > find docs/memo -maxdepth 1 -type f -name '*.md' | sort
> > ```

## 3. Memo Structure

### 3.a Front Matter Rule

> [decision] Do not use YAML front matter by default for human-facing memos.
> A memo should open with a normal Markdown title and readable prose. Use front
> matter only when a tool or explicitly requested format needs it.

### 3.b Default Chapter Shape

> [convention] Focused memo chapter shape
>
> - `1. Session Overview`
> - `2. Main Concepts`
> - `3. Workflow`
> - `4. Rules`
> - `5. Evidence`
> - `6. Project Implication`
> - `7. Open Questions`

> [note] This is a default, not a cage. Use the smallest structure that makes
> the memo readable.

### 3.c Minimal Required Content

> [decision] A focused memo should normally include:
>
> - Question or purpose.
> - Conclusion or decision.
> - Concrete guidance.
> - Evidence or source.
> - Project implication.
> - Open questions when something remains undecided.

> [note] A moved original note is different. Preserve original structure unless
> the user asks to refactor it.

### 3.d Later Memo Rule

> [decision] Later memo work should not rewrite earlier memos by default.
>
> Treat earlier memos as historical design snapshots. When thinking changes,
> record the new decision in the later memo and link back to the earlier memo
> when useful.

> [rule] Edit an earlier memo only when:
>
> - the user explicitly asks to change that memo;
> - a broken reference or typo blocks understanding;
> - the user explicitly supersedes an old rule and asks the rulebook to change.

> [workflow] If an earlier memo is changed during later memo work, record why in
> `docs/master-log.md`.

### 3.e PythonNotes Readability Pattern

> [decision] New Project 009 memos should be readable like
> `memo0002_pythonNotes.md`, not like a dense policy document.

> [decision] Memos should be human-readable and essentialist.
>
> If the user gives a sequence, preserve that sequence. Do not replace it with
> a generic AI outline. Compress the memo to decision, procedure, evidence, and
> next action.

> [convention] PythonNotes-style memo readability means:
>
> - use numbered chapters such as `## 1. Session Overview`;
> - use lettered subsections such as `### 1.a Purpose`;
> - use bracket tags such as `[concept]`, `[decision]`, `[source]`,
>   `[evidence]`, `[workflow]`, and `[project consequence]` when they help
>   scanning;
> - keep bullets short enough to scan;
> - place examples near the rule they explain;
> - prefer concrete paths, commands, and verification checks;
> - preserve the user's own checklist when it is already clear;
> - avoid long prose paragraphs unless they clarify a hard idea.

> [workflow] Check memo readability before finishing
>
> - Step 1: scan the headings.
>   - System: Markdown structure.
>   - Path: current memo.
>   - Verify: chapters and subsections show the topic flow without reading all
>     body text.
>
> - Step 2: scan the key statements.
>   - System: note readability.
>   - Path: current memo.
>   - Verify: bracket tags and headings make the main reusable facts visible
>     without reading the whole memo.
>
> - Step 3: scan the examples.
>   - System: memo examples.
>   - Path: current memo.
>   - Verify: examples are close to the rule they explain and do not contain
>     private values.

## 4. Writing Style

### 4.a Compact Notes

> [workflow] Write compact notes
>
> - Step 1: write the useful fact.
>   - System: memo content.
>   - Path: current memo section.
>   - Verify: the sentence helps a future action or decision.
>
> - Step 2: remove filler.
>   - System: documentation style.
>   - Path: current memo section.
>   - Verify: no long explanation remains unless it improves execution or
>     understanding.
>
> - Step 3: keep scan shape.
>   - System: Markdown readability.
>   - Path: current memo section.
>   - Verify: bullets, bracket tags, and headings make the note easy to skim.

### 4.b Concrete Material First

> [decision] Prefer concrete material over generic advice.

> [note] Good memo material includes:
>
> - command run
> - path inspected
> - local repo fact
> - decision made
> - mistake found
> - example input/output
> - open question
> - verification result

### 4.c First-Appearance Rule

> [concept] **First-appearance rule** means define an important term the first
> time it appears, then refer back to that definition instead of redefining it
> in many places.

> [note] Use this especially for terms like `uv`, `.venv`, `Kline`, `Qlib`,
> `Chanlun`, `artifact`, `record`, `memo`, and `KB`.

### 4.d No-Secrets Rule

> [decision] Do not store secrets or private data in memo files.

> [note] Do not paste:
>
> - API keys
> - tokens
> - passwords
> - broker/account identifiers
> - private market data
> - private data paths that should not be shared
> - large generated outputs

> [workflow] Use placeholders in examples
>
> - Step 1: replace private values with obvious placeholders.
>   - System: memo examples.
>   - Path: current memo.
>   - Verify: no real secret or account value remains.
>
> > [example] Placeholder shape
> >
> > ```text
> > QLIB_PROVIDER_URI=/path/to/local/qlib_data
> > API_KEY=<your-api-key>
> > ```

### 4.e Paper Review Style

> [decision] Paper review sections should be written for humans first. Do not use comparison tables by default, and do not force every sentence into a tag block.

> [convention] Review one paper at a time.
>
> - Start with the paper title, author/year, or short topic name.
> - Do not sub-index paper headings like `1.a.1` or `Paper 1` unless the user explicitly asks for ranking labels.
> - Put the AMA-style citation directly under the paper heading.
> - Use labels that match the reader and memo level.
> - For serious research or architecture memos, prefer graduate-level labels such as `Core argument:`, `Mechanism:`, `Evidence:`, and `Project consequence:`.
> - Avoid elementary labels such as `What it says:` and `Why it matters here:` unless the memo is intentionally introductory.
> - Keep the note short enough that a human can read it without decoding a template.
> - Add citation-count evidence only when the user asks for ranking or "most cited" support.

> > [example] Paper review shape
> >
> > ```md
> > #### Short Topic Name
> >
> > Author A, Author B. Paper title. Journal. Year;volume(issue):pages. doi:...
> >
> > Core argument:
> >
> > - Main idea.
> > - Result worth remembering.
> >
> > Project consequence:
> >
> > - Project implication.
> > ```

## 5. Tag Blocks

### 5.a Tag Meanings

> [concept] **Tag blocks** are quoted blocks that label the role of a note.
> They make dense technical notes easier to scan when used intentionally.

> [concept] Common note tags:
>
> - `[concept]`: definition or mental model.
> - `[decision]`: chosen tool, convention, default, or tradeoff.
> - `[source]`: source note, website, code path, paper, command, or repo rule.
> - `[evidence]`: concrete observed fact, citation evidence, test result, or
>   local output.
> - `[workflow]`: executable step-by-step process.
> - `[execution]`: command run, check performed, output observed, or next
>   verification step.
> - `[note]`: contextual reminder, caveat, gotcha, or short observation.
> - `[example]`: compact sample code, config, command, or data.
> - `[project consequence]`: implication for Project 009 design or execution.

### 5.b Tag Use Rule

> [decision] Bracket tags are wanted in Project 009 memos. Use them to improve
> scan readability. Do not remove them as "metadata" unless the user explicitly
> asks to remove bracket tags.

> [decision] Remove YAML front matter or long metadata headers when the user
> asks to remove meta information. Keep useful bracket tags unless specifically
> told otherwise.

> [note] A good memo often uses a mix:
>
> - normal headings for navigation
> - bracket tags for reusable facts, decisions, sources, and consequences
> - fenced code blocks for examples
> - short bullets for scan speed

### 5.c Nested Examples

> [concept] **Example nesting** means placing an example directly under the
> rule it explains.

> > [example] Nested example shape
> >
> > ````md
> > `.env.example` stores placeholder environment variable names.
> >
> > Minimal `.env.example`:
> >
> > ```text
> > QLIB_PROVIDER_URI=/path/to/local/qlib_data
> > ```
> > ````

## 6. Workflow Blocks

### 6.a Workflow Shape

> [concept] **Workflow shape** means each action step says what to do, what
> system it affects, what path is involved, and how to verify it.

> [workflow] Standard workflow step shape
>
> - Step 1: action.
>   - System: impacted tool, runtime, file, or process.
>   - Path: relevant file, folder, executable, URL, or environment path.
>   - Verify: expected result or check.
>
> - Step 2: next action.
>   - System: impacted tool, runtime, file, or process.
>   - Path: relevant file, folder, executable, URL, or environment path.
>   - Verify: expected result or check.

### 6.b Command Placement

> [decision] Commands that act on files belong in workflow or execution
> sections, not loose prose.

> > [example] Good command placement
> >
> > ```md
> > Verify memo file:
> >
> > - Step 1: check the memo exists.
> >   - System: filesystem.
> >   - Path: `docs/memo/memo0003_memoguidance.md`.
> >   - Verify: `test -f docs/memo/memo0003_memoguidance.md` exits with `0`.
> > ```

## 7. Execution Records

### 7.a Live Session

> [concept] **Live session** means the current Codex-user interaction where
> commands are actually run against this local repo or machine.

> [decision] If a command is executed during the live session, record what
> happened in a nearby execution section or in `docs/master-log.md`.

### 7.b Execution Record Shape

> [execution] Execution records should include:
>
> - command run
> - file changed
> - output observed
> - verification result
> - blocker, limitation, or next check

> [note] Execution summaries are facts from this machine, not generic
> instructions.

### 7.c Master Log Relationship

> [convention] `docs/master-log.md` records chronological project activity. Memo
> files record reusable knowledge.

> [decision] After creating or changing a memo, append a short master-log entry
> before reporting the work as complete.

## 8. Memo Home

### 8.a Memo Folder

> [concept] **`docs/memo/`** is for readable project memos, moved source notes,
> setup guidance, working conventions, extracted reusable guidance, and durable
> project knowledge.

### 8.b Retired KB Folder

> [decision] The old `kb/` folder has been retired. Durable knowledge now lives
> in numbered `docs/memo/memo000N_name.md` files.

> [reference] The old KB files were migrated on 2026-08-31:
>
> - `kb/kb0001_qlib-venv-installation.md` ->
>   `docs/memo/memo0006_qlib_windows_venv.md`
> - `kb/kb0002_qlib-data-structure.md` ->
>   `docs/memo/memo0007_qlib_data_structure.md`

### 8.c Boundary Rule

> [decision] Use `docs/memo/` for the current memo family and for reusable
> project knowledge.

> [note] Do not duplicate memo material into another knowledge folder unless a
> future cleanup plan explicitly reintroduces that structure.

## 9. Evidence

### 9.a Python Notes Evidence

> [execution] Source read
>
> - File: `docs/memo/memo0002_pythonNotes.md`.
> - Section: `1.f Key Rules And Tags`.
> - Observed: compact notes, concrete material, no filler, note tags,
>   live-session execution records, first-appearance rule, workflow shape,
>   example nesting, and optional tag recursion.

> [execution] Backup source read
>
> - File: `../pythonCatchup/pythonNotes.1788155588.bak.md`.
> - Section: `1.f Key Rules And Tags`.
> - Observed: same source guidance before the note was moved into Project 009.

### 9.b Project Rule Evidence

> [execution] Repo rule source
>
> - File: `AGENTS.md`.
> - Section: `Knowledge Memos`.
> - Observed: durable knowledge memos should record question, conclusion,
>   evidence/source, project implication, open questions, and simple examples.

## 10. Project Implication

> [decision] Future Project 009 memo work should create small, named,
> source-backed Markdown files under `docs/memo/`.

> [note] The goal is not to rewrite original notes into a polished manual. The
> goal is to extract reusable project knowledge while preserving provenance and
> readability.

## 11. Open Questions

> [note] Possible future improvements:
>
> - Add `docs/memo/README.md` as a memo index.
> - Decide whether moved original notes should keep original capitalization or
>   be normalized after import.
