---
title: memo0004_mac_setup
tags:
  - macos
  - machine-setup
  - python
  - vscode
  - uv
  - git
status: active
source:
  - docs/memo/memo0002_pythonNotes.md
  - docs/memo/memo0003_memoguidance.md
created: 2026-08-31
---

# memo0004_mac_setup

## 1. Session Overview

### 1.a Purpose

- Configure a new macOS machine for Project 009 work.
- Check whether an existing macOS machine is ready.
- Keep local runtime state out of Git.
- Make Python, VS Code, Git, and repo commands point at the right places.

### 1.b Question

> [concept] **macOS machine setup** means preparing the operating system,
> terminal, package tools, editor, Git identity, repo checkout, and project
> Python environment so Project 009 commands run reproducibly.

> [note] Main questions:
>
> - How should a new Mac be configured for Project 009?
> - How should we check the setup status of an existing Mac?

### 1.c Target Outcome

- Homebrew or another documented install path exists.
- `git`, `uv`, `python`, and `code` are available where expected.
- Project 009 is checked out locally.
- Project 009 `.venv/` is created from repo metadata.
- VS Code uses the repo-local interpreter.
- Machine-specific files stay local.
- A status check can quickly identify missing pieces.

### 1.d Core Decisions

> [decision] Use `zsh` as the default macOS terminal shell.

> [decision] Use Homebrew as the preferred macOS tool installer when available.

> [decision] Use `uv` as the preferred Python manager, virtual environment
> creator, package installer, and command runner.

> [decision] Use repo-local `.venv/` for Project 009 Python work.

> [decision] Use VS Code local interpreter selection. Do not commit
> machine-specific VS Code interpreter paths.

## 2. Machine Layers

### 2.a Layer Model

> [concept] **Machine layer model** means checking setup from broadest to
> narrowest:
>
> - macOS operating system
> - shell and `PATH`
> - system package manager
> - Git and identity
> - VS Code and extensions
> - Python tooling
> - repo checkout
> - repo-local `.venv`
> - project verification commands

> [note] Debug setup problems from outer layers inward. A broken `PATH` can make
> Python look broken even when Python itself is fine.

### 2.b Local Versus Repo State

> [decision] Commit the environment recipe, not the local environment.

> [note] Commit:
>
> - source code
> - docs and memo files
> - `pyproject.toml`
> - lock files when used
> - tests
> - portable config

> [note] Do not commit:
>
> - `.venv/`
> - `.venv.*`
> - `.env`
> - shell history
> - caches
> - local datasets
> - private account data
> - machine-specific VS Code interpreter paths

> [decision] `.venv/` and `.venv.*` folders are local machine state. They must
> be ignored by Git and must not be committed.

> [workflow] If a virtual environment was accidentally tracked:
>
> - Step 1: keep the local files.
> - Step 2: remove the virtual environment from the Git index only.
> - Step 3: verify `.gitignore` includes `.venv/` and `.venv.*`.

> > [example] Untrack venv without deleting local files
> >
> > ```zsh
> > git rm -r --cached .venv
> > git rm -r --cached .venv.windows-backup
> > ```

## 3. New Mac Setup Workflow

### 3.a Open Terminal

> [workflow] Start in `zsh`
>
> - Step 1: open Terminal.
>   - System: macOS shell.
>   - Path: `Terminal.app`.
>   - Verify: terminal window accepts commands.
>
> - Step 2: confirm shell.
>   - System: shell runtime.
>   - Path: `zsh`.
>   - Verify: `echo $SHELL` prints a path ending in `zsh`.

> > [example] Shell check
> >
> > ```zsh
> > echo $SHELL
> > echo $PATH
> > ```

### 3.b Install Or Confirm Homebrew

> [concept] **Homebrew** is the preferred macOS package manager for command-line
> tools in this memo.

> [workflow] Check Homebrew
>
> - Step 1: check whether `brew` exists.
>   - System: command lookup.
>   - Path: `/opt/homebrew/bin/brew` on Apple Silicon Macs.
>   - Verify: `brew --version` prints a version.
>
> - Step 2: if missing, install Homebrew from the official installer.
>   - System: macOS package manager installation.
>   - Path: Homebrew installer.
>   - Verify: a new terminal can run `brew --version`.

> > [example] Homebrew check
> >
> > ```zsh
> > which brew
> > brew --version
> > ```

> [note] If Homebrew is newly installed, open a fresh terminal before continuing
> so `PATH` is updated.

### 3.c Install Core Tools

> [workflow] Install Project 009 baseline tools
>
> - Step 1: install Git if missing.
>   - System: version control.
>   - Path: `git`.
>   - Verify: `git --version` prints a version.
>
> - Step 2: install `uv`.
>   - System: Python environment tooling.
>   - Path: `/opt/homebrew/bin/uv`.
>   - Verify: `uv --version` prints a version.
>
> - Step 3: confirm Python is available.
>   - System: macOS or `uv` Python runtime.
>   - Path: `python3`.
>   - Verify: `python3 --version` prints a version.

> > [example] Core tool commands
> >
> > ```zsh
> > brew install git
> > brew install uv
> > git --version
> > uv --version
> > python3 --version
> > ```

### 3.d Configure Git Identity

> [workflow] Set Git identity
>
> - Step 1: check current Git name and email.
>   - System: Git config.
>   - Path: global Git config.
>   - Verify: commands print the intended user identity.
>
> - Step 2: set missing identity values.
>   - System: Git config.
>   - Path: global Git config.
>   - Verify: `git config --global --get ...` returns the values.

> > [example] Git identity commands
> >
> > ```zsh
> > git config --global --get user.name
> > git config --global --get user.email
> > git config --global user.name "Your Name"
> > git config --global user.email "you@example.com"
> > ```

> [note] Use a real Git identity, but do not put private account credentials in
> memo files.

### 3.e Install VS Code

> [workflow] Configure VS Code
>
> - Step 1: install Visual Studio Code if missing.
>   - System: editor.
>   - Path: `/Applications/Visual Studio Code.app`.
>   - Verify: VS Code opens.
>
> - Step 2: install the `code` shell command.
>   - System: VS Code command-line integration.
>   - Path: `code`.
>   - Verify: `code --version` prints a version.
>
> - Step 3: install core extensions.
>   - System: VS Code extension host.
>   - Path: user extensions folder.
>   - Verify: extension list includes Python and Ruff.

> > [example] VS Code commands
> >
> > ```zsh
> > code --version
> > code --install-extension ms-python.python
> > code --install-extension charliermarsh.ruff
> > code --list-extensions | rg 'ms-python.python|charliermarsh.ruff'
> > ```

> [note] If `code` is missing, open VS Code, press `Cmd + Shift + P`, run
> `Shell Command: Install 'code' command in PATH`, then open a new terminal.

### 3.f Prepare Workspace Folder

> [workflow] Create or enter workspace folder
>
> - Step 1: choose a stable local workspace root.
>   - System: filesystem.
>   - Path: `/Users/coder/Public/EngineGit`.
>   - Verify: folder exists.
>
> - Step 2: clone or enter Project 009.
>   - System: Git checkout.
>   - Path: `/Users/coder/Public/EngineGit/proj009`.
>   - Verify: `git status --short` works in the repo.

> > [example] Workspace commands
> >
> > ```zsh
> > mkdir -p /Users/coder/Public/EngineGit
> > cd /Users/coder/Public/EngineGit
> > cd proj009
> > git status --short
> > ```

> [note] Clone commands depend on the real remote URL and should not be guessed
> in this memo.

## 4. Project 009 Python Setup

### 4.a Install Python 3.11 With uv

> [workflow] Install or confirm Python 3.11
>
> - Step 1: install Python 3.11.
>   - System: `uv` Python manager.
>   - Path: `uv` managed Python directory.
>   - Verify: `uv python install 3.11` finishes successfully.
>
> - Step 2: find Python 3.11.
>   - System: `uv` Python resolver.
>   - Path: resolved Python executable.
>   - Verify: `uv python find 3.11` prints a path.

> > [example] Python version commands
> >
> > ```zsh
> > uv python install 3.11
> > uv python list
> > uv python find 3.11
> > ```

### 4.b Create Repo `.venv`

> [workflow] Create Project 009 virtual environment
>
> - Step 1: enter repo root.
>   - System: filesystem.
>   - Path: `/Users/coder/Public/EngineGit/proj009`.
>   - Verify: `pwd` prints the repo path.
>
> - Step 2: create `.venv`.
>   - System: `uv` virtual environment creator.
>   - Path: `.venv/`.
>   - Verify: `.venv/bin/python` exists.

> > [example] `.venv` commands
> >
> > ```zsh
> > cd /Users/coder/Public/EngineGit/proj009
> > uv venv --python 3.11 --prompt proj009
> > test -x .venv/bin/python
> > ```

### 4.c Install Project Dependencies

> [execution] Current Project 009 dependency facts
>
> - File: `pyproject.toml`.
> - Python target: `>=3.11`.
> - Optional extra: `visualization`.
> - Optional extra: `qlib`.

> [workflow] Install dependencies for current work
>
> - Step 1: install visualization dependencies when chart work is needed.
>   - System: Python package installer.
>   - Path: `pyproject.toml`.
>   - Verify: pandas, matplotlib, and mplfinance are importable.
>
> - Step 2: install Qlib only when Qlib smoke checks are needed.
>   - System: Python package installer.
>   - Path: `pyproject.toml`.
>   - Verify: `import qlib` works.

> > [example] Dependency commands
> >
> > ```zsh
> > uv pip install -e ".[visualization]"
> > uv pip install -e ".[qlib]"
> > ```

### 4.d Activate Only When Needed

> [decision] Prefer `uv run ...` over manual activation.

> [note] Use activation only when running plain `python`, `pip`, or shell tools
> that expect the virtual environment to be active.

> > [example] Manual activation
> >
> > ```zsh
> > source .venv/bin/activate
> > python --version
> > ```

## 5. VS Code Project Setup

### 5.a Open Project

> [workflow] Open Project 009 in VS Code
>
> - Step 1: open the repo folder.
>   - System: VS Code workspace.
>   - Path: `/Users/coder/Public/EngineGit/proj009`.
>   - Verify: Explorer shows Project 009 files.

> > [example] Open command
> >
> > ```zsh
> > code /Users/coder/Public/EngineGit/proj009
> > ```

### 5.b Select Interpreter

> [workflow] Select the repo Python interpreter
>
> - Step 1: open Command Palette.
>   - System: VS Code UI.
>   - Path: `Cmd + Shift + P`.
>   - Verify: command search box opens.
>
> - Step 2: run `Python: Select Interpreter`.
>   - System: Python extension.
>   - Path: `ms-python.python`.
>   - Verify: interpreter list opens.
>
> - Step 3: select Project 009 `.venv`.
>   - System: VS Code interpreter selection.
>   - Path: `/Users/coder/Public/EngineGit/proj009/.venv/bin/python`.
>   - Verify: VS Code status bar points to `.venv`.

### 5.c Interpreter Rule

> [decision] Do not commit `python.defaultInterpreterPath` when it points to one
> machine-specific path.

> [decision] Do not commit `ruff.interpreter` when it points to one local
> `.venv` path.

> [note] Interpreter selection should happen locally on each machine.

## 6. Machine Status Check Procedure

### 6.a Status Check Purpose

> [concept] **Machine status check** means running a small set of read-only
> commands to determine whether the Mac is ready for Project 009 work.

> [decision] Prefer status checks before changing a machine. Check first, then
> install or edit only the missing layer.

### 6.b Operating System And Shell

> [workflow] Check OS and shell status
>
> - Step 1: check macOS version.
>   - System: operating system.
>   - Path: macOS.
>   - Verify: `sw_vers` prints product name and version.
>
> - Step 2: check CPU architecture.
>   - System: hardware/runtime architecture.
>   - Path: local machine.
>   - Verify: `uname -m` prints `arm64` or `x86_64`.
>
> - Step 3: check shell and `PATH`.
>   - System: shell runtime.
>   - Path: `zsh`.
>   - Verify: shell path and `PATH` look expected.

> > [example] OS and shell commands
> >
> > ```zsh
> > sw_vers
> > uname -m
> > echo $SHELL
> > echo $PATH
> > ```

### 6.c Tool Status

> [workflow] Check tool status
>
> - Step 1: check Homebrew.
>   - System: package manager.
>   - Path: `brew`.
>   - Verify: `brew --version` works.
>
> - Step 2: check Git.
>   - System: version control.
>   - Path: `git`.
>   - Verify: `git --version` works.
>
> - Step 3: check `uv`.
>   - System: Python environment tooling.
>   - Path: `uv`.
>   - Verify: `uv --version` works.
>
> - Step 4: check VS Code CLI.
>   - System: editor CLI.
>   - Path: `code`.
>   - Verify: `code --version` works.

> > [example] Tool commands
> >
> > ```zsh
> > which brew; brew --version
> > which git; git --version
> > which uv; uv --version
> > which code; code --version
> > ```

### 6.d Git Status

> [workflow] Check Git identity and repo status
>
> - Step 1: check global identity.
>   - System: Git config.
>   - Path: global Git config.
>   - Verify: user name and email are set.
>
> - Step 2: check repo remote.
>   - System: Git repository.
>   - Path: Project 009 `.git`.
>   - Verify: `git remote -v` shows the expected remote.
>
> - Step 3: check worktree state.
>   - System: Git worktree.
>   - Path: Project 009 repo.
>   - Verify: `git status --short` output is understood before edits.

> > [example] Git status commands
> >
> > ```zsh
> > git config --global --get user.name
> > git config --global --get user.email
> > cd /Users/coder/Public/EngineGit/proj009
> > git remote -v
> > git status --short
> > ```

### 6.e Python Project Status

> [workflow] Check Project 009 Python status
>
> - Step 1: check project metadata.
>   - System: repo config.
>   - Path: `pyproject.toml`.
>   - Verify: file exists and declares Python `>=3.11`.
>
> - Step 2: check `.venv`.
>   - System: filesystem.
>   - Path: `.venv/bin/python`.
>   - Verify: executable exists.
>
> - Step 3: check runtime.
>   - System: `uv` command runner.
>   - Path: `.venv/bin/python`.
>   - Verify: `uv run python --version` works.
>
> - Step 4: check imports.
>   - System: Python import system.
>   - Path: `.venv`.
>   - Verify: required imports for current work succeed.

> > [example] Python status commands
> >
> > ```zsh
> > test -f pyproject.toml
> > test -x .venv/bin/python
> > uv run python --version
> > uv run python -c "import sys; print(sys.executable)"
> > uv run python -c "import pandas as pd; print(pd.__version__)"
> > ```

### 6.f VS Code Status

> [workflow] Check VS Code status
>
> - Step 1: check CLI.
>   - System: VS Code CLI.
>   - Path: `code`.
>   - Verify: `code --version` works.
>
> - Step 2: check extensions.
>   - System: VS Code extension registry.
>   - Path: user extensions folder.
>   - Verify: Python and Ruff extensions are installed.
>
> - Step 3: check interpreter from VS Code terminal.
>   - System: VS Code integrated terminal.
>   - Path: Project 009 repo.
>   - Verify: Python executable points inside `.venv/`.

> > [example] VS Code status commands
> >
> > ```zsh
> > code --version
> > code --list-extensions | rg 'ms-python.python|charliermarsh.ruff'
> > uv run python -c "import sys; print(sys.executable)"
> > ```

### 6.g Project Verification

> [workflow] Check Project 009 command readiness
>
> - Step 1: run tests.
>   - System: Python test runner.
>   - Path: `tests/`.
>   - Verify: unittest reports pass/fail.
>
> - Step 2: run lint if Ruff is installed.
>   - System: Ruff.
>   - Path: repo root.
>   - Verify: Ruff reports no issues or lists issues.

> > [example] Project verification commands
> >
> > ```zsh
> > uv run python -m unittest discover -s tests
> > uv run ruff check .
> > uv run ruff format --check .
> > ```

> [note] If Ruff is not installed, record that as a setup gap instead of
> treating the whole machine as broken.

## 7. Status Report Shape

### 7.a Short Status Summary

> [convention] Machine status summaries should use this shape:
>
> - OS:
> - Shell:
> - Homebrew:
> - Git:
> - VS Code:
> - `uv`:
> - Python:
> - Project `.venv`:
> - Project imports:
> - Project tests:
> - Gaps:
> - Next action:

### 7.b Example Status Report

> > [example] Status report sketch
> >
> > ```text
> > OS: macOS 15.x, arm64
> > Shell: zsh
> > Homebrew: present
> > Git: present, identity configured
> > VS Code: present, Python/Ruff extensions installed
> > uv: present
> > Python: Project 009 uses .venv/bin/python
> > Project .venv: present
> > Project imports: pandas ok
> > Project tests: unittest command runs
> > Gaps: Ruff not installed in .venv
> > Next action: add or install dev dependencies
> > ```

## 8. Troubleshooting Order

### 8.a Order

> [workflow] Triage machine setup problems
>
> - Step 1: check shell and `PATH`.
>   - System: terminal environment.
>   - Path: `zsh`.
>   - Verify: expected tool paths are visible.
>
> - Step 2: check tool availability.
>   - System: installed command-line tools.
>   - Path: `brew`, `git`, `uv`, `code`.
>   - Verify: each command prints a version.
>
> - Step 3: check repo location and Git status.
>   - System: filesystem and Git.
>   - Path: `/Users/coder/Public/EngineGit/proj009`.
>   - Verify: repo status is understood.
>
> - Step 4: check `.venv`.
>   - System: Python environment.
>   - Path: `.venv/bin/python`.
>   - Verify: `uv run python` uses the repo interpreter.
>
> - Step 5: check VS Code interpreter.
>   - System: VS Code.
>   - Path: selected interpreter.
>   - Verify: status bar and terminal agree on `.venv/bin/python`.

### 8.b Common Setup Gaps

> [note] Common gaps:
>
> - `brew` missing from `PATH`.
> - `uv` installed after VS Code was opened, so VS Code terminal cannot see it.
> - `.venv/` missing.
> - VS Code selected global Python instead of `.venv/bin/python`.
> - Git identity missing.
> - Ruff extension installed but Ruff package missing from `.venv`.
> - local `.env` missing for workflows that need private paths.

## 9. Evidence

### 9.a Source Note Evidence

> [execution] Source read
>
> - File: `docs/memo/memo0002_pythonNotes.md`.
> - Sections: `2.a` through `2.i`, plus `3.b`.
> - Observed: platform-independent repo setup, `uv`, macOS `.venv`, dependency
>   install, `uv run`, VS Code terminal verification, and interpreter selection.

### 9.b Memo Guidance Evidence

> [execution] Guidance read
>
> - File: `docs/memo/memo0003_memoguidance.md`.
> - Section: `3.e PythonNotes Readability Pattern`.
> - Observed: memos should use numbered chapters, `1.a` subsections, quoted tag
>   blocks, compact bullets, nearby examples, concrete paths, and verification
>   checks.

### 9.c Repo Evidence

> [execution] Repo files read
>
> - File: `pyproject.toml`.
> - Observed: `requires-python = ">=3.11"`.
> - File: `.gitignore`.
> - Observed: `.venv/`, `.venv.windows-backup/`, and `.venv.windows-backup*/`
>   are ignored.

## 10. Project Implication

> [decision] Project 009 should treat macOS readiness as a layered setup:
> system tools first, repo checkout second, project environment third, editor
> integration fourth.

> [note] This makes onboarding and troubleshooting repeatable. A future agent
> can run the status check, report exact gaps, and change only the missing
> layer.

## 11. Open Questions

> [note] Possible follow-up decisions:
>
> - Add `.vscode/extensions.json` recommendations.
> - Add dev dependencies for `pytest` and `ruff`.
> - Decide whether `uv sync --dev` should become the default setup command.
> - Decide whether to create a script that runs the status check automatically.
