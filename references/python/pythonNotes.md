---
title: pythonNotes
tags:
  - python
  - qlib
  - quant
  - study-notes
status: active
---

# pythonNotes

## 1. Session Overview

### 1.a Purpose

- Catch up Python min less than 5 hours; 
- 20-80 rule 
- provide a knowledge tree for quick checking
- anything python new in the future goes here
### 1.b Assumed Background

-  C++ - 5 yr
-  OOP - 15 yr
-  Mid-level software engineering experience - 3 yr
-  AI tool fluent - 2 yr
-  Passionate - 46 yr
### 1.c Target Outcome

- Vibe coding is a must
- accountable at each class level 
- able to publish interesting repos   
- support the software engineering needs for Eyegorithm and Quant 

### 1.d Suggested Timebox

- 20 80 rule 
- 5 hours condense
### 1.e What Ready For Qlib Means

- Can read a Qlib example repo without getting blocked by Python syntax.
- Can explain the flow: raw data -> features -> labels -> model -> prediction -> strategy -> backtest.
- Can use Pandas to check date index, missing values, rolling windows, shift, and joins.
- Can spot basic leakage risk before trusting a result.
- Can run an existing Qlib example, inspect outputs, and know where to modify config.
- Can debug import, environment, data path, and DataFrame shape issues in VS Code.
- Can incorporate the learned patterns into a new package or repo without copying blindly.

### 1.f Key Rules And Tags

> [decision] This document stays as one living Markdown note. Do not split into multiple notes unless explicitly requested.

> [workflow] Note-taking style
>
> - Step 1: write compact notes.
>   - System: Obsidian Markdown note.
>   - Path: `C:\pythonCatchup\pythonNotes.md`.
>   - Verify: bullets stay short and easy to scan.
>
> - Step 2: prefer concrete material.
>   - System: learning record.
>   - Path: current section being edited.
>   - Verify: commands, runnable examples, mistakes, decisions, or open questions are present.
>
> - Step 3: remove filler.
>   - System: documentation style.
>   - Path: current section being edited.
>   - Verify: no long explanation unless it directly helps execution or understanding.

> [concept] **Note tags**
>
> - `[concept]`: definition or mental model.
> - `[decision]`: chosen tool, convention, default, or tradeoff.
> - `[workflow]`: executable step-by-step process.
> - `[execution]`: command run, check performed, output observed, or next verification step.
> - `[note]`: contextual reminder, caveat, gotcha, or short observation.
> - `[new filetype]`: file format purpose, syntax, and repo usage.
> - `[example]`: compact sample code, config, command, or data.
> - `[convention]`: naming, style, layout, or team-agreed coding/documentation convention.
> - `[function]`: function purpose, input/output behavior, and minimal call example.

> [concept] **Live session**
>
> - A live session is the current Codex-user interaction where commands are actually run against this local repo or machine.
> - If a command is executed during the live session, record what happened in a nearby `[execution]` block.
> - Execution summaries are facts from this machine, not generic instructions.

> [concept] **First-appearance rule**
>
> - Define important terms where they first appear.
> - Later sections should refer back or add only new context.
> - Avoid scattering duplicate definitions across the document.

> [concept] **Workflow shape**
>
> - Workflow steps are numbered.
> - Each step should include impacted system, relevant path, and verification.
> - Add a blank quoted line between steps.
>
> > [example] Standard workflow step shape
> >
> > ```md
> > > - Step 1: action.
> > >   - System: impacted tool or runtime.
> > >   - Path: relevant file, folder, executable, or environment path.
> > >   - Verify: expected result or check.
> > ```

> [concept] **Example nesting**
>
> - Put examples inside the tag they explain when useful.
> - Use `> > [example]` inside parent blocks like `[new filetype]`.
> - Filetype examples should show file contents or syntax only.
> - Commands that act on files belong in `[workflow]` or `[execution]`.

> [concept] **Tag recursion**
>
> - Tags are independent building blocks.
> - Tags may be nested recursively when useful.
> - Nesting is optional; use it only when it makes the note clearer.
> - Avoid forcing a rigid hierarchy between tags.

## 2. Environment Setup

### 2.a Tool Choice

> [concept] **`uv`** is a fast Python project tool: Python version manager, virtual environment creator, package installer, and command runner.

> [decision] Environment tool choice
>
> - Primary: `uv`
> - Fallback: `python -m venv` + `pip`
> - Reason: faster install, cleaner workflow, reproducible setup.

> [workflow] Choose environment tool
>
> - Step 1: use `uv` for normal setup.
>   - System: package manager and Python environment tooling.
>   - Path: `C:\Users\xinwe\.local\bin\uv.exe`.
>   - Verify: `uv --version` prints a version after shell restart.
>
> - Step 2: use `python -m venv` + `pip` only if `uv` is unavailable.
>   - System: built-in Python tooling.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: `.venv` exists and `python --version` works inside the activated environment.

### 2.b Install uv

> [concept] **`cmd` and PowerShell** are both Windows shells. A shell is a program that takes user commands and asks the operating system to run programs, manage files, and set environment variables. PowerShell is newer and better for scripting.

> [workflow] Install `uv`
>
> - Step 1: open PowerShell from the Start Menu.
>   - System: Windows shell.
>   - Path: `PowerShell`.
>   - Verify: terminal window is open and accepts commands.
>
> - Step 2: run `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
>   - System: PowerShell installer process.
>   - Path: installer URL `https://astral.sh/uv/install.ps1`.
>   - Verify: installer prints `everything's installed!`.
>
> > [syntax] `powershell` starts a PowerShell process; `-ExecutionPolicy ByPass` allows this installer script for that process; `-c` runs the quoted command; `irm` downloads the script; `| iex` executes it.
>
> - Step 3: close and reopen PowerShell if `uv` is not found.
>   - System: Windows user PATH refresh.
>   - Path: `C:\Users\xinwe\.local\bin\`.
>   - Verify: `uv --version` prints version text with no error.
>
> - Step 4: find the executable path.
>   - System: Windows command lookup.
>   - Path: `C:\Users\xinwe\.local\bin\uv.exe`.
>   - Verify: `Get-Command uv` in PowerShell, or `where uv` in `cmd`.

> [note] If VS Code was already open before installing `uv`, close and reopen VS Code so the integrated terminal reloads the updated PATH.

> [execution] `uv` installed successfully.
>
> - Version: `uv 0.12.5`
> - Path: `C:\Users\xinwe\.local\bin\uv.exe`
> - Also installed: `uvx.exe`, `uvw.exe`
> - Current shell did not find `uv` on PATH yet.
> - User PATH contains `C:\Users\xinwe\.local\bin`.
> - If VS Code was open before install, close and reopen VS Code so its terminal sees the updated PATH.
> - Next check after reopening PowerShell: `uv --version`

### 2.c Python Version

> [concept] **Python version** matters because package compatibility, Qlib examples, and local tooling can behave differently across versions.

> [decision] Python version choice
>
> - Target: Python 3.11
> - Minimum: Python 3.10
> - Reason: modern enough for current tooling, conservative enough for library compatibility.

> [workflow] Install Python and confirm project interpreter
>
> - Step 1: install target Python with `uv python install 3.11`.
>   - System: `uv` Python manager.
>   - Path: `C:\Users\xinwe\AppData\Roaming\uv\python\`.
>   - Verify: install finishes with a `CPython 3.11.x` message.
>
> - Step 2: list available Python versions with `uv python list`.
>   - System: `uv` Python manager.
>   - Path: `uv` managed Python registry.
>   - Verify: `cpython-3.11.x-windows-x86_64-none` appears.
>
> - Step 3: find the installed Python path with `uv python find 3.11`.
>   - System: `uv` Python resolver.
>   - Path: returned `python.exe` path under `C:\Users\xinwe\AppData\Roaming\uv\python\`.
>   - Verify: command prints a concrete `python.exe` path.
>
> - Step 4: run Python inside this repo with `uv run python --version`.
>   - System: repo environment and `uv` command runner.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: output is `Python 3.11.x`; if `.venv` does not exist, `uv run` may create it.

> [concept] **A virtual environment**, usually `.venv`, is a project-local Python environment that keeps this repo's packages separate from global Python and other repos. Summary: `.venv` is a folder containing this repo's Python executable, installed packages, and activation scripts. Installing a new global Python elsewhere on `C:\` should not affect this repo as long as VS Code, terminal commands, and scripts use `.venv` or `uv run`.

> [execution] Python 3.11 installed and verified with `uv`.
>
> - Installed: `CPython 3.11.16`
> - Interpreter path: `C:\Users\xinwe\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`
> - Check: `uv python find 3.11`
> - Result: found the Python 3.11 interpreter above.
> - Check: `uv run python --version`
> - Result: `Python 3.11.16`
> - Side effect: `uv run` created the project virtual environment at `.venv`.
> - PATH note: `uv` warned that `C:\Users\xinwe\.local\bin` was not active in the current shell PATH yet.

### 2.d Create Virtual Environment (optional if already created)

> [concept] **Creating `.venv`** makes the repo-local Python environment explicit. In this repo, `.venv` may already exist because `uv run python --version` created it during `2.c`.

> [workflow] Create `.venv`
>
> - Step 1: create `.venv` only if missing with `uv venv --python 3.11`.
>   - System: `uv` virtual environment creator.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: command creates `.venv` with a Python 3.11 environment.

> [workflow] Verify `.venv`
>
> - Step 1: check whether `.venv` exists.
>   - System: filesystem.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: folder exists in repo root.
>
> - Step 2: check the repo Python version with `uv run python --version`.
>   - System: `uv` command runner.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: output is `Python 3.11.x`.

> [workflow] Activate `.venv`
>
> - Step 1: activate `.venv` only when running manual terminal commands.
>   - System: PowerShell session.
>   - Path: `C:\pythonCatchup\.venv\Scripts\Activate.ps1`.
>   - Command: `.venv\Scripts\Activate.ps1`
>   - Verify: terminal prompt shows `(pythonCatchup)`, or `python --version` prints `Python 3.11.x`.
>
> - Step 2: skip manual activation when using `uv run`.
>   - System: `uv` command runner.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Command: `uv run python --version`
>   - Verify: command runs inside the project environment.

> [note] Use the next workflow only when the activated terminal prompt shows an old repo/project name.

> [workflow] Rename `.venv` prompt by recreating environment
>
> - Step 1: recreate `.venv` with `uv venv --python 3.11 --clear --prompt pythonCatchup`.
>   - System: `uv` virtual environment creator.
>   - Path: `C:\pythonCatchup\.venv\`.
>   - Verify: command prints `Creating virtual environment at: .venv`.
>
> - Step 2: reinstall dependencies with `uv pip install -r requirements.txt`.
>   - System: `uv` pip-compatible installer.
>   - Path: `C:\pythonCatchup\requirements.txt`.
>   - Verify: packages install into `.venv`.
>
> - Step 3: verify prompt metadata in `.venv\pyvenv.cfg`.
>   - System: venv metadata.
>   - Path: `C:\pythonCatchup\.venv\pyvenv.cfg`.
>   - Verify: file contains `prompt = pythonCatchup`.
>
> - Step 4: verify runtime and pandas.
>   - System: `.venv` Python runtime.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: `uv run python` uses `.venv` and pandas imports.

> [execution] Recreated `.venv` with repo prompt name
>
> - Command: `uv venv --python 3.11 --clear --prompt pythonCatchup`
> - Result: `.venv` recreated with `CPython 3.11.16`.
> - Command: `uv pip install -r requirements.txt`
> - Result: reinstalled `pandas==3.0.5` and transitive packages including `numpy==2.4.6`.
> - Check: `.venv\pyvenv.cfg`
> - Result: contains `prompt = pythonCatchup`.
> - Check: `uv run python -c "import pandas as pd; print(pd.__version__)"`
> - Result: `3.0.5`.

### 2.e Install Dependencies

> [concept] **Runtime** is the program that actually runs code. For this repo, the Python runtime should be `C:\pythonCatchup\.venv\Scripts\python.exe` or `uv run python`.

> [concept] **Dependencies** are packages or tools the project environment needs. Runtime dependencies are imported by project code, like `pandas`. Developer dependencies are used by engineers and tools, like `ruff` for formatting/linting or `pytest` for tests. In this repo, both kinds can start in `requirements.txt` and install into `.venv`.

> [note] `pandas` and `ruff` are both dependencies in the broad sense. Difference: `pandas` is usually imported by Python code; `ruff` is usually run as a command-line executable from `.venv\Scripts\ruff.exe`.

> [new filetype] TOML is a human-readable config format made of sections like `[project]` and key-value settings like `name = "python-notes"`. In this repo, `pyproject.toml` stores Python project metadata, dependency config, and tool settings such as `[tool.ruff]`.
>
> > [example] Minimal `pyproject.toml` shape
> >
> > ```toml
> > # Project metadata and runtime requirements.
> > [project]
> > name = "python-notes"
> > version = "0.1.0"
> > requires-python = ">=3.11"
> > # Packages needed when the project code runs.
> > dependencies = ["pandas", "numpy"]
> >
> > # Packages needed by engineers while developing.
> > [dependency-groups]
> > dev = ["pytest", "ruff"]
> >
> > # Tool-specific config.
> > [tool.ruff]
> > line-length = 88
> > ```

> [new filetype] `requirements.txt` is a plain text dependency list used by `pip`-style installers. In this repo, it is the simple starter place for runtime packages before moving dependency metadata into `pyproject.toml`.
>
> > [example] Minimal `requirements.txt` shape
> >
> > ```text
> > # Runtime packages imported by repo code.
> > pandas
> > numpy
> >
> > # Testing / tooling packages can start here, then move to dev dependency groups later.
> > pytest
> > ruff
> > ```

> [workflow] Simple path: install dependencies from `requirements.txt`
>
> - Step 1: check `requirements.txt` has package names, not only comments.
>   - System: dependency manifest.
>   - Path: `C:\pythonCatchup\requirements.txt`.
>   - Verify: file contains packages such as `pandas`, `numpy`, `pytest`, or `ruff`.
>
> - Step 2: run `uv pip install -r requirements.txt`.
>   - System: `uv` pip-compatible installer.
>   - Path: `C:\pythonCatchup\requirements.txt`.
>   - Verify: packages install into `C:\pythonCatchup\.venv\Lib\site-packages\`.
>
> - Step 3: verify imports with `uv run python -c "import pandas, numpy; print('ok')"`.
>   - System: Python import system.
>   - Path: `C:\pythonCatchup\.venv\Lib\site-packages\`.
>   - Verify: command prints `ok`.

> [execution] Dependency install from `requirements.txt`
>
> - File update: added `pandas` to `requirements.txt`.
> - Command: `uv pip install -r requirements.txt`
> - Result: installed `pandas==3.0.5` and transitive packages including `numpy==2.4.6`.
> - Command: `uv run python -c "import pandas, numpy; print('ok')"`
> - Result: `ok`
> - Installed packages observed: `pandas`, `numpy`, `python-dateutil`, `six`, `tzdata`.

### 2.f Run Commands

> [workflow] Run project commands with `uv run`
>
> - Step 1: check the repo Python runtime with `uv run python --version`.
>   - System: `uv` command runner and `.venv` Python runtime.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: output is `Python 3.11.x`.
>
> - Step 2: run tests with `uv run pytest`.
>   - System: test runner.
>   - Path: `C:\pythonCatchup\tests\`.
>   - Verify: pytest starts and reports pass/fail results.
>
> - Step 3: run lint checks with `uv run ruff check .`.
>   - System: Ruff linter.
>   - Path: `C:\pythonCatchup\`.
>   - Verify: Ruff reports no issues or lists files to fix.
>
> - Step 4: format code with `uv run ruff format .`.
>   - System: Ruff formatter.
>   - Path: `C:\pythonCatchup\`.
>   - Verify: Ruff formats files or reports they are unchanged.

> [execution] `2.f` command run summary
>
> - Command: `uv run python --version`
> - Result: `Python 3.11.16`
> - Command: `uv run pytest`
> - Result: failed because `pytest` is not installed in `.venv`.
> - Command: `uv run ruff check .`
> - Result: failed because `ruff` is not installed in `.venv`.
> - Command: `uv run ruff format .`
> - Result: failed because `ruff` is not installed in `.venv`.
> - Next step: install dev tools before rerunning tests/lint/format.

### 2.g Fallback Without uv

> [note] Use this only when `uv` is unavailable or blocked. Normal repo workflow should prefer `uv` and `uv run`.

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2.h VS Code PowerShell Terminal Verification

> [workflow] Verify repo environment from VS Code PowerShell terminal
>
> - Step 1: open VS Code integrated terminal with PowerShell.
>   - System: VS Code terminal.
>   - Path: `C:\pythonCatchup\`.
>   - Verify: terminal starts in repo root, or `pwd` prints `C:\pythonCatchup`.
>
> - Step 2: check `uv` is visible from VS Code with `uv --version`.
>   - System: VS Code process PATH.
>   - Path: `C:\Users\xinwe\.local\bin\uv.exe`.
>   - Verify: command prints `uv 0.12.5` or newer.
>
> - Step 3: check repo Python with `uv run python -c "import sys; print(sys.executable); print(sys.version)"`.
>   - System: `uv` command runner and `.venv` Python runtime.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: executable path points inside `.venv` and version is `Python 3.11.x`.
>
> - Step 4: check pandas import and version with `uv run python -c "import pandas as pd; print(pd.__version__)"`.
>   - System: Python import system.
>   - Path: `C:\pythonCatchup\.venv\Lib\site-packages\`.
>   - Verify: command prints installed pandas version.
>
> - Step 5: check no hardcoded local path is required.
>   - System: repo portability.
>   - Path: `C:\pythonCatchup\`.
>   - Verify: commands work from repo root using relative project files and `.venv`.

> [execution] Pandas verification
>
> - Command: `uv run python -c "import pandas as pd; print(pd.__version__)"`
> - Result: `3.0.5`

## 3. VS Code IDE Setup And Code Standards

### 3.a Recommended VS Code Extensions

> [concept] **A VS Code extension** is an add-on that teaches the editor new behavior, such as Python language support, linting, formatting, notebooks, Git tools, or better file navigation.

> [concept] **Linting** is static code checking: a tool reads code before it runs and flags likely bugs, unused imports, style issues, unsafe patterns, or inconsistent structure.

> [decision] Minimal VS Code extension set
>
> - Required: `ms-python.python`
> - Strongly recommended: `charliermarsh.ruff`
> - Optional for notebooks: `ms-toolsai.jupyter`
>
> > [note] Extension function
> >
> > - `ms-python.python`: Python language support, interpreter selection, debugging, test discovery, and environment awareness.
> > - `charliermarsh.ruff`: linting, formatting, import cleanup, and fast code-quality feedback.
> > - `ms-toolsai.jupyter`: notebook editing and interactive Python exploration when `.ipynb` is useful.

> [note] Keep the extension set small. Add extensions only when they support the current Python/Qlib workflow.

> [workflow] Install recommended VS Code extensions
>
> - Step 1: install Python extension `ms-python.python`.
>   - System: VS Code extension marketplace.
>   - Path: VS Code Extensions panel.
>   - Verify: Python interpreter selection and Python language features are available.
>
> - Step 2: install Ruff extension `charliermarsh.ruff`.
>   - System: VS Code extension marketplace.
>   - Path: VS Code Extensions panel.
>   - Verify: Ruff lint/format integration appears for Python files.
>
> - Step 3: install Jupyter extension `ms-toolsai.jupyter` only if using notebooks.
>   - System: VS Code extension marketplace.
>   - Path: VS Code Extensions panel.
>   - Verify: `.ipynb` files open with notebook support.

> [workflow] Alternative: install VS Code extensions from command line
> >![[Pasted image 20260823132542.png]]
>
> - Step 1: check VS Code CLI with `code --version`.
>   - System: VS Code command-line interface.
>   - Path: `C:\Users\xinwe\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd`.
>   - Verify: command prints VS Code version.
>
> - Step 2: install Python extension with `code --install-extension ms-python.python`.
>   - System: VS Code extension installer.
>   - Path: VS Code user extensions folder.
>   - Verify: command reports installed or already installed.
>
> - Step 3: install Ruff extension with `code --install-extension charliermarsh.ruff`.
>   - System: VS Code extension installer.
>   - Path: VS Code user extensions folder.
>   - Verify: command reports installed or already installed.
>
> - Step 4: list relevant installed extensions with `code --list-extensions --show-versions | Select-String "ms-python.python|charliermarsh.ruff|ms-toolsai.jupyter"`.
>   - System: VS Code extension registry.
>   - Path: VS Code user extensions folder.
>   - Verify: expected extension IDs and versions appear.

> [execution] VS Code extension installation
>
> - Command: `code --version`
> - Result: VS Code CLI available.
> - Command: `code --install-extension ms-python.python`
> - Result: already installed, `ms-python.python@2026.4.0`.
> - Command: `code --install-extension charliermarsh.ruff`
> - Result: installed, `charliermarsh.ruff@2026.74.0`.
> - Jupyter: not installed because it is optional until notebooks are needed.

### 3.b Interpreter Selection

> [concept] **VS Code interpreter selection** means choosing which `python.exe` VS Code uses for running files, debugging, resolving imports, discovering tests, and powering Python editor features.

> [decision] VS Code should use the repo interpreter, not global Python.
>
> - Repo interpreter: `C:\pythonCatchup\.venv\Scripts\python.exe`
> - Base Python came from `uv`: `C:\Users\xinwe\AppData\Roaming\uv\python\...`
> - Repo environment lives at: `C:\pythonCatchup\.venv\`
> - Reason: keeps VS Code aligned with the same Python and packages used by `uv run`.
>
> > [note] `2.c` and `2.d` created or confirmed the interpreter. `3.b` is only about telling VS Code to use it.

> [note] If running plain `python` in the VS Code PowerShell terminal, activate `.venv` first with `.venv\Scripts\Activate.ps1`. If using `uv run python`, manual activation is not required.

> [workflow] Select repo interpreter in VS Code
>
> - Step 1: open the Command Palette with `Ctrl + Shift + P`.
>   - System: VS Code command palette.
>   - Path: VS Code UI.
>   - Verify: command search box opens.
>
> - Step 2: run `Python: Select Interpreter`.
>   - System: Python extension.
>   - Path: `ms-python.python`.
>   - Verify: interpreter list opens.
>
> - Step 3: choose `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - System: VS Code Python environment selection.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: VS Code status bar shows the `.venv` Python interpreter.
>
> - Step 4: verify from VS Code PowerShell terminal after activation with `python -c "import sys; print(sys.executable)"`.
>   - System: VS Code integrated terminal and selected interpreter.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: printed path points to `.venv\Scripts\python.exe`.
>   - >![[Pasted image 20260823134428.png]]

### 3.c Formatting -Ruff and VS Code Extension

> [concept] **Ruff** is a Python code-quality tool with two main functions here: `ruff check` diagnoses code issues, and `ruff format` rewrites code layout. The VS Code Ruff extension is editor integration, while `ruff` installed in `.venv` is the actual project command-line tool. Extension = editor capability; `.venv` dependency = project capability. The extension can run Ruff-like checks in the background while editing, show issues in the VS Code UI, and call formatting/fixes on save or command. Background linting changes UI only; formatting or quick fixes may rewrite `.py` files in place. Ruff normally writes terminal output, not report files, unless explicitly redirected.

> [concept] **VS Code Problems panel** is a structured diagnostic stream from editor-connected tools, not strings printed by project code. Terminal output comes from commands/programs; Problems panel entries come from tools like Ruff, Python extension, or type checker and point to file, line, severity, and message.

> [note] Ruff name origin: likely from "rough prototype" -> "Ruff". Treat this as historical context, not a functional concept.

> [workflow] Simple path: add Ruff through `requirements.txt`
>
> - Step 1: add `ruff` to `requirements.txt`.
>   - System: dependency manifest.
>   - Path: `C:\pythonCatchup\requirements.txt`.
>   - Verify: file contains `ruff`.
>
> - Step 2: install with `uv pip install -r requirements.txt`.
>   - System: `uv` pip-compatible installer.
>   - Path: `C:\pythonCatchup\.venv\Scripts\ruff.exe`.
>   - Verify: `ruff.exe` exists in `.venv\Scripts`.
>
> - Step 3: verify Ruff with `uv run ruff --version`.
>   - System: `.venv` command-line tool.
>   - Path: `C:\pythonCatchup\.venv\Scripts\ruff.exe`.
>   - Verify: command prints Ruff version.

> [workflow] Structured path: add Ruff through `pyproject.toml`
>
> - Step 1: add `ruff` under `[dependency-groups].dev`.
>   - System: Python project metadata.
>   - Path: `C:\pythonCatchup\pyproject.toml`.
>   - Verify: `ruff` appears in the dev dependency group.
>
> - Step 2: run `uv sync`.
>   - System: `uv` dependency synchronizer.
>   - Path: `C:\pythonCatchup\pyproject.toml` and `C:\pythonCatchup\uv.lock`.
>   - Verify: `.venv` matches the locked project dependencies.
>
> - Step 3: verify Ruff with `uv run ruff check .` and `uv run ruff format .`.
>   - System: Ruff linter and formatter.
>   - Path: `C:\pythonCatchup\`.
>   - Verify: Ruff reports issues, formats files, or reports unchanged files.

> [new filetype] JSON is a strict key-value config/data format. In this repo, `.vscode/settings.json` stores workspace-level VS Code settings that connect the editor to `.venv`, Python, and Ruff.
>
> > [example] Minimal VS Code Ruff settings
> >
> > ```json
> > {
> >   "ruff.importStrategy": "fromEnvironment",
> >   "ruff.interpreter": [".venv/Scripts/python.exe"],
> >   "[python]": {
> >     "editor.defaultFormatter": "charliermarsh.ruff",
> >     "editor.formatOnSave": true
> >   }
> > }
> > ```

> [workflow] Connect VS Code Ruff extension to repo Ruff
>
> - Step 1: set Ruff to load from the selected environment.
>   - System: VS Code workspace settings.
>   - Path: `C:\pythonCatchup\.vscode\settings.json`.
>   - Verify: `"ruff.importStrategy": "fromEnvironment"` is present.
>
> - Step 2: point Ruff extension at the repo interpreter.
>   - System: VS Code Ruff extension.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: `"ruff.interpreter": [".venv/Scripts/python.exe"]` is present.
>
> - Step 3: set Ruff as the Python formatter.
>   - System: VS Code formatter selection.
>   - Path: `C:\pythonCatchup\.vscode\settings.json`.
>   - Verify: `[python].editor.defaultFormatter` is `charliermarsh.ruff`.
>
> - Step 4: verify both sides exist.
>   - System: VS Code extension and `.venv` command-line tool.
>   - Path: `charliermarsh.ruff` extension and `C:\pythonCatchup\.venv\Scripts\ruff.exe`.
>   - Verify: `code --list-extensions --show-versions` shows Ruff extension, and `uv run ruff --version` prints Ruff version.

> [workflow] Hello Ruff demo
>
> - Step 1: create a tiny Python file with one intentional lint issue.
>   - System: repo script file.
>   - Path: `C:\pythonCatchup\scripts\hello_ruff.py`.
>   - Verify: file exists and runs.
>
> - Step 2: check the file with `uv run ruff check scripts\hello_ruff.py`.
>   - System: Ruff linter.
>   - Path: `C:\pythonCatchup\scripts\hello_ruff.py`.
>   - Verify: Ruff reports the unused import.
>
> - Step 3: fix the issue with `uv run ruff check scripts\hello_ruff.py --fix`.
>   - System: Ruff linter auto-fix.
>   - Path: `C:\pythonCatchup\scripts\hello_ruff.py`.
>   - Verify: Ruff reports the issue fixed.
>
> - Step 4: format and re-check the file.
>   - System: Ruff formatter and linter.
>   - Path: `C:\pythonCatchup\scripts\hello_ruff.py`.
>   - Verify: `ruff format` reformats if needed and `ruff check` reports all checks passed.

> [execution] Installed Ruff and pytest through `pyproject.toml`
>
> - File update: added `pandas` to `[project].dependencies` in `pyproject.toml`.
> - File update: added `ruff` and `pytest` to `[dependency-groups].dev` in `pyproject.toml`.
> - File update: added `ruff` and `pytest` to `requirements.txt` for the simple path.
> - Command: `uv sync`
> - Result: installed `ruff==0.16.4` and `pytest==9.1.1` into `.venv`.
> - Check: `uv run ruff --version`
> - Result: `ruff 0.16.4`
> - Check: `uv run pytest --version`
> - Result: `pytest 9.1.1`
> - Check: `uv run python -c "import pandas as pd; print(pd.__version__)"`
> - Result: `3.0.5`

> [execution] Connected VS Code Ruff extension to repo Ruff
>
> - File update: added Ruff workspace settings to `.vscode/settings.json`.
> - Setting: `"ruff.importStrategy": "fromEnvironment"`
> - Setting: `"ruff.interpreter": [".venv/Scripts/python.exe"]`
> - Setting: `[python].editor.defaultFormatter = "charliermarsh.ruff"`
> - Check: `.vscode/settings.json` parses as valid JSON.
> - Check: `.venv\Scripts\ruff.exe` exists.
> - Check: `uv run ruff --version`
> - Result: `ruff 0.16.4`
> - Check: `code --list-extensions --show-versions`
> - Result: `charliermarsh.ruff@2026.74.0` and `ms-python.python@2026.4.0`

> [execution] Hello Ruff demo
>
> - File created: `scripts\hello_ruff.py`
> - Command: `uv run ruff check scripts\hello_ruff.py`
> - Result: Ruff reported `F401` for unused `os` import.
> - Command: `uv run ruff format scripts\hello_ruff.py`
> - Result: `1 file left unchanged`.
> - Command: `uv run python scripts\hello_ruff.py`
> - Result: `hello, ruff`
> - Command: `uv run ruff check scripts\hello_ruff.py --fix`
> - Result: `Found 1 error (1 fixed, 0 remaining).`
> - Command: `uv run ruff format scripts\hello_ruff.py`
> - Result: `1 file reformatted`.
> - Command: `uv run ruff check scripts\hello_ruff.py`
> - Result: `All checks passed!`
> - Live edit: typed random invalid Python into `scripts\hello_ruff.py`.
> - Command: `uv run ruff check scripts\hello_ruff.py`
> - Result: Ruff reported `invalid-syntax` errors on the invalid line.

### 3.d Linting

> [concept] **Linting** is static code checking: Ruff reads Python files before they run and reports likely bugs, syntax errors, unused imports, style issues, or fixable code-quality problems.

> [note] No extra linting setup is needed right now. `3.c` already installed Ruff in `.venv`, installed the VS Code Ruff extension, and connected VS Code to the repo Ruff tool. In VS Code, Ruff extension coordinates linting through editor squiggles and the Problems panel; in terminal, use `uv run ruff check .`.

### 3.e Type Checking

> [concept] **Type checking** is static reasoning about value types before code runs. Pylance is the VS Code language server that provides Python intelligence: type checking, autocomplete, hover info, go-to-definition, import analysis, and Problems panel diagnostics. Pylance lives as a VS Code extension under `C:\Users\xinwe\.vscode\extensions\`, not inside `.venv`; it reads the selected interpreter `C:\pythonCatchup\.venv\Scripts\python.exe` to understand repo packages and types.

> [note] Type checking rationale: Ruff checks code quality and formatting, but Pylance checks type logic. It helps catch mistakes like passing `str` where `int` is expected, returning the wrong type, or forgetting to handle `None`. It becomes more useful when functions and variables have type hints.

### 3.f PEP 8

> [concept] **PEP 8** is Python's community style standard. It defines common naming, spacing, import, and layout conventions so Python code looks familiar across projects.

> [convention] Follow PEP 8 naming unless this repo later adopts a stronger local convention.
>
> - Files/modules: `snake_case.py`
> - Functions: `snake_case`
> - Variables: `snake_case`
> - Classes: `PascalCase`
> - Constants: `UPPER_SNAKE_CASE`
> - Private helpers: `_leading_underscore`
> - Tests: `test_*.py`
> - Scripts: `verb_noun_demo.py`
>
> > [example] Naming shape
> >
> > ```python
> > MAX_LOOKBACK_DAYS = 252
> >
> >
> > class FactorCalculator:
> >     pass
> >
> >
> > def calculate_return(close_price: float, previous_close: float) -> float:
> >     return close_price / previous_close - 1
> >
> >
> > def _validate_price(price: float) -> None:
> >     if price <= 0:
> >         raise ValueError("price must be positive")
> > ```

> [convention] PEP 8 essentials for this repo
>
> - Indentation: 4 spaces.
> - Line length: 88 characters, managed by Ruff.
> - Imports: standard library first, then third-party packages, then local project imports.
> - Blank lines: separate top-level functions/classes with two blank lines.
> - Whitespace: use spaces around normal assignment/operators, like `a = 1`; avoid extra spaces inside calls/brackets, like `func(x)` not `func( x )`.
> - Comments: explain why, not obvious what.
> - Docstrings: use for public functions/classes when behavior is not obvious.
> - Comparisons: use `is None` / `is not None` for `None` checks.
> - Exceptions: raise specific exceptions like `ValueError`, not broad generic errors.

> [note] Python comments use `#`. Python does not use `//` or `/* */` for comments. Use `#` for short human notes, and use triple-quoted docstrings `"""..."""` for module, class, or function documentation.

> [note] Type annotation spacing: use `name: type`, `name: type = value`, and `def f(x: int = 1) -> int:`. No space before `:`, one space after `:`, spaces around `=`, and spaces around `->`. Function call keyword arguments still use no spaces, like `f(x=1)`.

> [note] Prefer names that describe domain role, not implementation trivia: `daily_return`, `future_return`, `lookback_days`, `instrument`, `trade_date`, `signal_score`.

### 3.g Scripts Vs Reusable Code

> [concept] **`scripts/`** is for command-style code: small files you run to do one task, such as checking an environment, downloading data, trying an API call, or running a quick experiment. A script has an entry point and usually starts from "do this now."

> [concept] **Reusable code** belongs under `src/`: functions, classes, and modules that other code can import. Reusable code usually starts from "provide this behavior so many callers can use it."

> [decision] Default split for this repo:
> - Put one-off learning, checks, and local experiments in `scripts/`.
> - Put stable domain logic in `src/catchup/`.
> - Put tests for reusable logic in `tests/`.
> - Do not import important business/domain logic from `scripts/`; promote it into `src/` first.

> [workflow] Promote a script idea into reusable code
> - Step 1: start in `scripts/` when the idea is still exploratory.
>   - System: repo working files.
>   - Path: `C:\pythonCatchup\scripts\`.
>   - Verify: the script can run directly with `uv run python scripts\<name>.py`.
>
> - Step 2: identify the part that should be reused.
>   - System: Python code organization.
>   - Path: current script file.
>   - Verify: the reusable part can be described as a function with clear inputs and outputs.
>
> - Step 3: move reusable behavior into `src/catchup/`.
>   - System: local Python package.
>   - Path: `C:\pythonCatchup\src\catchup\`.
>   - Verify: scripts or tests import it from `catchup`, not from `scripts`.
>
> - Step 4: keep the script as a thin runner.
>   - System: repo command layer.
>   - Path: `C:\pythonCatchup\scripts\`.
>   - Verify: the script mostly parses inputs, calls reusable code, and prints or saves results.

> [example] Shape only
>
> ```text
> scripts/check_env.py          # run directly; command-style
> src/catchup/returns.py        # importable reusable logic
> tests/test_returns.py         # verifies reusable logic
> ```

### 3.h Environment Variables

> [concept] **An environment variable** is a named value supplied by the operating system or shell to a running program. Python code can read it at runtime, so the code does not need to hardcode local paths, API keys, or machine-specific settings.

> [concept] **A `.env` file** is a local text file that stores environment-style key/value pairs for one machine or one developer. It is useful for local settings, but it should usually be ignored by Git.

> [new filetype] `.env.example`
>
> `.env.example` is a committed template. It shows which environment variables the project expects, without storing private values.
>
> > [example] Minimal `.env.example`
> >
> > ```text
> > # Local Qlib data location. Each engineer sets this path for their own machine.
> > QLIB_PROVIDER_URI=C:\path\to\qlib_data
> >
> > # Example only. Real secrets go in `.env`, not in `.env.example`.
> > DATA_API_KEY=
> > ```

> [decision] Use environment variables for values that change by machine, account, dataset, deployment, or secret status. Keep stable code behavior in Python files, and keep local/private settings outside source code.

> [decision] For this repo:
> - Commit `.env.example`.
> - Do not commit `.env`.
> - Use placeholder values in notes and examples.
> - Do not paste real API keys, tokens, passwords, or private data paths into `pythonNotes.md`.

> [workflow] Create or update the environment template
> - Step 1: add variable names to `.env.example`.
>   - System: repo configuration template.
>   - Path: `C:\pythonCatchup\.env.example`.
>   - Verify: names are present, values are blank or fake placeholders.
>
> - Step 2: keep `.env` private.
>   - System: Git ignore rules.
>   - Path: `C:\pythonCatchup\.gitignore`.
>   - Verify: `.env` is ignored by Git.
>
> - Step 3: document what each variable means.
>   - System: study notes.
>   - Path: `C:\pythonCatchup\pythonNotes.md`.
>   - Verify: the variable has a short explanation without exposing private values.

> [workflow] Set a temporary environment variable in PowerShell
> - Step 1: set the variable for the current terminal session.
>   - System: PowerShell process environment.
>   - Path: current VS Code PowerShell terminal only.
>   - Command: `$env:QLIB_PROVIDER_URI = "C:\path\to\qlib_data"`
>   - Verify: `echo $env:QLIB_PROVIDER_URI` prints the same value.
>
> - Step 2: run Python from the same terminal.
>   - System: `.venv` Python runtime.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Command: `uv run python -c "import os; print(os.environ['QLIB_PROVIDER_URI'])"`
>   - Verify: Python prints the value set in Step 1.
>
> - Step 3: open a new terminal if needed.
>   - System: shell session state.
>   - Path: new VS Code PowerShell terminal.
>   - Verify: temporary variables from the old terminal do not automatically carry over.

> [note] Environment variables are runtime inputs. Changing an environment variable changes what the running program sees, but it does not edit Python source files.

### 3.i Section 3 Closeout

> [note] Section 3 closes the repo editing standard: VS Code is the editor, `.venv` is the selected interpreter, Ruff handles formatting/checking, Pylance handles Python intelligence/type analysis, PEP 8 gives naming/style conventions, `scripts/` stays command-style, `src/` holds reusable logic, and environment variables keep local/private settings outside source code.

## 4. Debugging Options

> [concept] **Debugging** is the process of locating why actual program behavior differs from expected behavior. It is not only "fixing errors"; it is building evidence about program state, control flow, data shape, and runtime configuration.

> [decision] Debugging options should escalate from simple to structured:
> - Use `print()` for quick visibility.
> - Read stack traces when Python crashes; the error type, message, and call chain usually point to the failing line and cause.
> - Use REPL/IPython for interactive exploration.
> - Use VS Code breakpoints when state and control flow matter.
> - Use pytest debugging when the behavior should become a repeatable test.
> - Use logging when visibility should stay in long-running scripts or workflows.

### 4.a Print Debugging - quick dirty view

> [concept] **Print debugging** means inserting temporary `print()` calls to expose program state while code runs. It is the fastest way to answer small questions like "did this line run?", "what is this value?", or "what shape is this data?"

> [workflow] Use print debugging
> - Step 1: print the location.
>   - System: Python runtime output.
>   - Path: VS Code PowerShell terminal.
>   - Verify: the message appears when the code reaches that line.
>
> - Step 2: print the value and its type or shape.
>   - System: Python runtime state.
>   - Path: the variable being inspected.
>   - Verify: output answers what the variable is at that exact moment.
>
> - Step 3: remove or replace the print after the question is answered.
>   - System: source code hygiene.
>   - Path: edited Python file.
>   - Verify: temporary debug prints are not left in reusable code.

> [example] Simple value check
>
> ```python
> price = 101.25
> print("debug price:", price, type(price))
> ```

> [example] Pandas shape check
>
> ```python
> print("rows/cols:", df.shape)
> print(df.head())
> ```

> [note] Print debugging is not a serious framework. It is a quick visibility tool. If the same print is useful repeatedly, turn it into logging, a test, or a clearer function boundary.

### 4.b REPL And IPython

> [concept] **A REPL** is an interactive runtime: Read, Evaluate, Print, Loop. It reads one expression or statement, runs it immediately, prints the result when appropriate, then waits for the next input.

> [concept] **IPython** is a richer Python REPL. It adds better display, command history, tab completion, help shortcuts, and friendlier exploration for data work.

> [decision] Use the plain Python REPL first. IPython is optional later. Use REPL when the question is small and interactive: checking syntax, testing one expression, inspecting an object, trying a pandas operation, or exploring a package API before writing code into a file.

> [workflow] Start and use the Python REPL from the repo
> - Step 1: open the VS Code PowerShell terminal in the repo.
>   - System: shell working directory.
>   - Path: `C:\pythonCatchup`.
>   - Verify: prompt shows `PS C:\pythonCatchup>`.
>
> - Step 2: start the repo Python runtime.
>   - System: `.venv` Python runtime through `uv`.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Command: `uv run python`
>   - Verify: the prompt changes to Python's `>>>`.
>
> - Step 3: run small checks interactively.
>   - System: live Python process memory.
>   - Path: current REPL session.
>   - Verify: each line runs immediately and prints results or errors.

> [workflow] Exit the Python REPL
> - Step 1: confirm the prompt is Python's `>>>`.
>   - System: live Python process.
>   - Path: current REPL session.
>   - Verify: terminal prompt starts with `>>>`, not `PS`.
>
> - Step 2: run the Python exit command.
>   - System: Python REPL.
>   - Path: current REPL session.
>   - Command: `exit()`
>   - Verify: Python process closes.
>
> - Step 3: confirm PowerShell is back.
>   - System: VS Code PowerShell terminal.
>   - Path: `C:\pythonCatchup`.
>   - Verify: prompt returns to `PS C:\pythonCatchup>`.

> [example] Plain REPL checks
>
> ```python
> >>> price = 101.25
> >>> price * 1.01
> 102.2625
> >>> type(price)
> <class 'float'>
> ```

> [example] Pandas exploration
>
> ```python
> >>> import pandas as pd
> >>> df = pd.DataFrame({"price": [100, 101, 103]})
> >>> df["return"] = df["price"].pct_change()
> >>> df
> ```

> [note] A REPL session is temporary memory. Useful discoveries should be copied into a script, reusable function, test, or note before closing the session.

### 4.c VS Code Breakpoints

> [concept] **A breakpoint** is a marker on a source-code line where the debugger pauses execution. While paused, the Python process is still alive, and VS Code can inspect variables, call stack, and control flow.

> [concept] **Stepping** means moving through code while paused. Step Over runs the current line and stops at the next line in the same function. Step Into enters a called function. Step Out finishes the current function and returns to the caller.

> [concept] **`debugpy`** is the Python debugger engine used by VS Code. VS Code shows the UI, the Python extension coordinates the session, `debugpy` controls or attaches to the Python process, and the selected interpreter runs the code.

> [new filetype] `.vscode\launch.json`
>
> `launch.json` is a VS Code JSON configuration file that tells VS Code how to start a debug session. It does not store breakpoint lines. It defines the run shape: which debugger type to use, what program to run, and which terminal or console to use.
>
> > [example] Current debug configuration
> >
> > ```json
> > {
> >   "version": "0.2.0",
> >   "configurations": [
> >     {
> >       "name": "Python: Current File",
> >       "type": "debugpy",
> >       "request": "launch",
> >       "program": "${file}",
> >       "console": "integratedTerminal"
> >     }
> >   ]
> > }
> > ```
> >
> > - `"type": "debugpy"` means use the Python debugger engine.
> > - `"request": "launch"` means VS Code starts the Python process.
> > - `"program": "${file}"` means debug the currently open file.
> > - `"console": "integratedTerminal"` means run inside the VS Code terminal.

> [decision] Use VS Code breakpoints when `print()` is not enough: the bug depends on changing state, branches, loops, function calls, or the order in which code runs.

> [workflow] Debug a Python file with VS Code breakpoints
> - Step 1: confirm VS Code uses the repo interpreter.
>   - System: VS Code Python extension.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Verify: selected interpreter points to `.venv`.
>
> - Step 2: open the Python file and place a breakpoint.
>   - System: VS Code editor.
>   - Path: target `.py` file.
>   - Verify: a red dot appears in the left gutter beside the line.
>
> - Step 3: start debugging.
>   - System: VS Code debugger.
>   - Path: `.vscode\launch.json` or current Python file.
>   - Command: press `F5` or use Run And Debug.
>   - Verify: execution pauses on the breakpoint line.
>
> - Step 4: inspect runtime state.
>   - System: paused Python process.
>   - Path: VS Code Variables, Watch, Call Stack, and Debug Console panels.
>   - Verify: variable values match the exact paused line.
>
> - Step 5: continue or step through.
>   - System: VS Code debugger controls.
>   - Path: current debug session.
>   - Verify: Step Over, Step Into, Step Out, and Continue move execution as expected.

> [example] Breakpoint target
>
> ```python
> def calculate_return(today_price: float, yesterday_price: float) -> float:
>     return today_price / yesterday_price - 1
>
>
> result = calculate_return(103.0, 100.0)
> print(result)
> ```

> [note] Breakpoints inspect a live running process. If the file is not being executed, the breakpoint will not be hit.

### 4.d Pytest Debugging

> [concept] **`pytest`** has two related forms in this repo. `pytest.exe` is the command-line entry point that scans for test files, calls test functions, and reports pass/fail results. The `pytest` package is the Python module imported inside tests when helper tools are needed.

> [concept] **Pytest discovery** is naming-based. By default, pytest looks for files like `test_*.py` or `*_test.py`, then functions or methods named `test_*`.

> [concept] **`assert`** is built into Python, not pytest. Pytest runs the test function, lets Python evaluate `assert`, catches `AssertionError` when the assertion fails, then reports the failure clearly.

> [decision] Use pytest debugging when a bug should become repeatable. `print()` and breakpoints help inspect one run; pytest records expected behavior so future edits do not silently break it.

> [example] No `import pytest` needed
>
> ```python
> def test_basic_math():
>     assert 1 + 1 == 2
> ```
>
> Pytest finds this because the file and function follow test naming conventions.

> [example] `pytest.approx()` for floating-point comparison
>
> ```python
> import pytest
>
>
> def test_return_calculation():
>     result = 0.1 + 0.2
>
>     assert result == pytest.approx(0.3)
> ```
>
> Use this because floating-point math can produce tiny representation differences.

> [example] `pytest.raises()` for expected errors
>
> ```python
> import pytest
>
>
> def validate_price(price: float) -> None:
>     if price <= 0:
>         raise ValueError("price must be positive")
>
>
> def test_validate_price_rejects_negative_price():
>     with pytest.raises(ValueError):
>         validate_price(-1.0)
> ```
>
> Python `raise` creates the error path. `pytest.raises(...)` checks that the expected error is raised inside the block.

> [example] `pytest.mark.parametrize()` for repeated cases
>
> ```python
> import pytest
>
>
> def is_positive_price(price: float) -> bool:
>     return price > 0
>
>
> @pytest.mark.parametrize(
>     "price, expected",
>     [
>         (100.0, True),
>         (0.0, False),
>         (-1.0, False),
>     ],
> )
> def test_is_positive_price(price: float, expected: bool):
>     assert is_positive_price(price) is expected
> ```
>
> Use parametrization when the same rule should be checked against several inputs.

> [example] `pytest.fixture()` for reusable test setup
>
> ```python
> import pandas as pd
> import pytest
>
>
> @pytest.fixture
> def sample_prices():
>     return pd.DataFrame({"price": [100.0, 101.0, 103.0]})
>
>
> def test_sample_price_row_count(sample_prices):
>     assert len(sample_prices) == 3
> ```
>
> Fixture essence: replace repeated setup code with a named setup provider. By default, pytest calls the fixture once per test function, so each test receives fresh setup. It is mainly for cleaner tests and independent state, not a performance cache.

> [workflow] Run pytest from PowerShell
> - Step 1: open the VS Code PowerShell terminal in the repo.
>   - System: shell working directory.
>   - Path: `C:\pythonCatchup`.
>   - Verify: prompt shows `PS C:\pythonCatchup>`.
>
> - Step 2: run the pytest executable through `uv`.
>   - System: `.venv` command entry point.
>   - Path: `C:\pythonCatchup\.venv\Scripts\pytest.exe`.
>   - Command: `uv run pytest`
>   - Verify: pytest prints collected tests and pass/fail results.
>
> - Step 3: read failures from top to bottom.
>   - System: pytest report output.
>   - Path: VS Code PowerShell terminal.
>   - Verify: failure output shows test name, failing assertion or exception, and file line.
>
> - Step 4: fix the code or test expectation.
>   - System: source code and tests.
>   - Path: `C:\pythonCatchup\src\`, `C:\pythonCatchup\tests\`.
>   - Verify: rerun `uv run pytest` until the relevant test passes.

> [note] `pytest.exe` can run tests that never import `pytest`. Import `pytest` only when the test code needs helpers like `pytest.approx`, `pytest.raises`, `pytest.mark.parametrize`, or `pytest.fixture`.

> [note] Use verbose mode when you want pytest to show each collected test name and result: `uv run pytest -v`. Clear test function names act like readable messages in the test report.

> [execution] Ran pytest in the repo
> - Command: `C:\Users\xinwe\.local\bin\uv.exe run pytest`
> - Root: `C:\pythonCatchup`
> - Config: `pyproject.toml`
> - Test path: `tests`
> - Result: pytest ran successfully, collected `0` tests, and reported `no tests ran`.
> - Meaning: pytest is installed and callable, but the repo does not yet contain any discoverable `test_*.py` test files.

### 4.e Pandas Inspection

> [concept] **Pandas inspection** is data-form debugging. The critical use: check the actual shape, schema, types, missingness, ordering, and alignment of a table-like object before trusting the analysis.

> [concept] **A `DataFrame`** is a two-dimensional labeled table: rows plus columns. **A `Series`** is a one-dimensional labeled vector, often one column from a `DataFrame`.

> [decision] Use pandas inspection before and after operations that can silently change meaning: `merge`, `groupby`, `sort_values`, `shift`, `pct_change`, `rolling`, `resample`, filtering, and joins.

> [decision] For quant data, inspect instrument/date alignment. Code can run without crashing but still be analytically wrong if returns cross instruments, dates are unsorted, duplicates exist, or future data leaks into earlier rows.

> [workflow] Inspect a pandas DataFrame
> - Step 1: check object type and shape.
>   - System: Python runtime memory.
>   - Path: current `DataFrame` variable.
>   - Command: `print(type(df)); print(df.shape)`
>   - Verify: object is a pandas `DataFrame`, and row/column counts are plausible.
>
> - Step 2: check columns and sample rows.
>   - System: pandas table schema.
>   - Path: `df.columns`, `df.head()`, `df.tail()`.
>   - Command: `print(df.columns); print(df.head()); print(df.tail())`
>   - Verify: expected columns exist and sample rows look sane.
>
> - Step 3: check dtypes and missing values.
>   - System: pandas column metadata.
>   - Path: `df.dtypes`, `df.isna()`.
>   - Command: `print(df.dtypes); print(df.isna().sum())`
>   - Verify: numeric columns are numeric, date columns are date-like when needed, and missingness is understood.
>
> - Step 4: check duplicates.
>   - System: pandas row identity.
>   - Path: row keys such as `instrument` and `trade_date`.
>   - Command: `print(df.duplicated().sum())`
>   - Verify: duplicate rows are expected or explained.
>
> - Step 5: check index and time order.
>   - System: pandas index and sort order.
>   - Path: `df.index`, date columns, or instrument/date keys.
>   - Command: `print(df.index); print(df.index.is_monotonic_increasing)`
>   - Verify: index shape and sort order match the intended workflow.
>
> - Step 6: check summary ranges.
>   - System: pandas descriptive statistics.
>   - Path: numeric columns.
>   - Command: `print(df.describe())`
>   - Verify: min, max, mean, and count do not reveal impossible values.

> [example] Minimal inspection block
>
> ```python
> print("type:", type(df))
> print("shape:", df.shape)
> print("columns:", list(df.columns))
> print(df.head())
> print(df.tail())
> print(df.dtypes)
> print(df.isna().sum())
> print("duplicates:", df.duplicated().sum())
> ```

> [example] Quant-specific inspection
>
> ```python
> print(df[["instrument", "trade_date"]].head())
> print("instruments:", df["instrument"].nunique())
> print("date range:", df["trade_date"].min(), df["trade_date"].max())
> print("duplicate keys:", df.duplicated(["instrument", "trade_date"]).sum())
> print(df.sort_values(["instrument", "trade_date"]).head())
> ```

> [note] Pandas inspection is less about technical crashes and more about awareness of data form/state. A script can run successfully and still be wrong if rows, dates, instruments, or calculated columns are misaligned.

### 4.f Stack Traces

> [concept] **A stack trace** is Python's crash report. The critical use: it shows the error type, error message, failing file/line, and call path that led to the failure. A stack trace is not a random wall of text; it is the runtime path Python followed before it crashed.

> [workflow] Read a Python stack trace
> - Step 1: find the final error line.
>   - System: Python runtime error output.
>   - Path: VS Code PowerShell terminal.
>   - Verify: identify the error type and message, such as `ZeroDivisionError: division by zero`.
>
> - Step 2: find the lowest file/line frame that belongs to your code.
>   - System: Python call stack.
>   - Path: files listed in the traceback.
>   - Verify: this line usually points to the operation that failed.
>
> - Step 3: read upward to understand who called it.
>   - System: function call chain.
>   - Path: stack frames above the failing line.
>   - Verify: the path explains how execution reached the failure.
>
> - Step 4: fix the first real cause, then rerun.
>   - System: source code and runtime.
>   - Path: failing file or caller file.
>   - Verify: the same stack trace no longer appears.
>
> > [example] Stack trace shape
> >
> > ```text
> > Traceback (most recent call last):
> >   File "demo.py", line 8, in <module>
> >     main()
> >   File "demo.py", line 5, in main
> >     divide(10, 0)
> >   File "demo.py", line 2, in divide
> >     return a / b
> > ZeroDivisionError: division by zero
> > ```
> >
> > Read the final line first for the error type/message. Then read the lowest project file line to find where the failure happened.

### 4.g Logging

> [concept] **`logging`** is a built-in Python standard-library module. The critical use: keep durable runtime messages for scripts or workflows that may run repeatedly, without leaving random temporary `print()` calls everywhere.

> [concept] **Logging moving parts**: a logger receives messages, a level decides message importance, a handler sends messages somewhere such as terminal or file, and a formatter controls how the message looks.

> [workflow] Add basic logging to a script
> - Step 1: import the standard-library module.
>   - System: Python standard library.
>   - Path: current Python file.
>   - Command: `import logging`
>   - Verify: no package install is needed.
>
> - Step 2: configure logging once near the script entry point.
>   - System: Python logging module.
>   - Path: current Python process.
>   - Command: `logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")`
>   - Verify: `INFO` and above messages are visible.
>
> - Step 3: replace durable progress prints with logging calls.
>   - System: runtime message stream.
>   - Path: VS Code PowerShell terminal by default.
>   - Command: `logging.info("loaded data")`
>   - Verify: terminal shows a structured log message.
>
> - Step 4: keep temporary inspection as `print()`.
>   - System: source code hygiene.
>   - Path: exploratory script or REPL.
>   - Verify: random debug prints do not remain in reusable `src/` code.

> [example] Minimal logging setup
>
> ```python
> import logging
>
> logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
>
> logging.info("starting script")
> logging.warning("missing values detected")
> logging.error("failed to load data")
> ```

> [example] Level name and message mapping
>
> ```python
> import logging
>
> logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
>
> logging.info("starting data load")
> logging.warning("missing values detected")
> logging.error("failed to load price file")
> ```
>
> Output:
>
> ```text
> INFO:starting data load
> WARNING:missing values detected
> ERROR:failed to load price file
> ```
>
> `%(levelname)s` comes from the logging call, such as `logging.warning(...)`. `%(message)s` comes from the text inside the call, such as `"missing values detected"`.

> [note] Common logging levels:
> - `DEBUG`: detailed developer information.
> - `INFO`: normal progress.
> - `WARNING`: suspicious but not fatal.
> - `ERROR`: operation failed.
> - `CRITICAL`: serious failure.

> [note] Common logging keywords:
> - `level`: minimum importance level to show.
> - `format`: text pattern for each log message.
> - `filename`: write logs to a file instead of only terminal.
> - `logger`: named logging object, useful when code grows beyond one script.
> - `handler`: output destination such as terminal or file.
> - `formatter`: controls final message layout.

### 4.h Qlib Troubleshooting

> [concept] **Qlib troubleshooting** means separating environment problems, data-provider problems, config problems, and model/backtest logic problems. The critical use: Qlib failures often look like one stack trace, but the cause may live in Python environment, local data path, dataset config, calendar/instrument setup, or pandas-shaped data.

> [decision] Debug Qlib in layers:
> - Environment layer: Python, `.venv`, installed packages, import path.
> - Data layer: provider URI, calendar, instruments, feature files, date range.
> - Config layer: YAML/Python config keys, paths, model/dataset settings.
> - Runtime layer: stack trace, logging output, pandas inspection, generated artifacts.

> [note] Practical troubleshooting order:
> - Python environment: right interpreter and package environment.
> - Qlib installation: Qlib importable inside `.venv`.
> - Qlib data environment: provider path and config point to real data.
> - Static data sanity: instruments, calendars, dates, columns, missing values, duplicates.
> - Runtime failure: stack trace and logs during execution.
> - Analytical correctness: labels, features, train/test split, leakage, and backtest assumptions.

> [workflow] Triage a Qlib issue
> - Step 1: confirm the repo Python environment.
>   - System: `.venv` Python runtime.
>   - Path: `C:\pythonCatchup\.venv\Scripts\python.exe`.
>   - Command: `uv run python -c "import sys; print(sys.executable)"`
>   - Verify: output points to `C:\pythonCatchup\.venv\Scripts\python.exe`.
>
> - Step 2: confirm Qlib can be imported.
>   - System: installed Python packages.
>   - Path: current `.venv`.
>   - Command: `uv run python -c "import qlib; print(qlib.__version__)"`
>   - Verify: command prints a Qlib version instead of `ModuleNotFoundError`.
>
> - Step 3: confirm the data provider path.
>   - System: environment variable or config value.
>   - Path: `QLIB_PROVIDER_URI` or Qlib config file.
>   - Verify: path exists on disk and contains expected Qlib data files.
>
> - Step 4: read the stack trace bottom-up.
>   - System: Python runtime error output.
>   - Path: VS Code PowerShell terminal.
>   - Verify: identify the first project/Qlib line where the failure becomes specific.
>
> - Step 5: inspect data if the code runs but results look wrong.
>   - System: pandas `DataFrame` or Qlib dataset output.
>   - Path: current data variable.
>   - Verify: shape, columns, date range, instruments, missing values, and duplicates are understood.
>
> - Step 6: add logging for long-running workflows.
>   - System: Python logging module.
>   - Path: current script or reusable workflow.
>   - Verify: output shows which stage failed: init, load data, build dataset, train model, backtest, or save results.

> [example] Fast environment checks
>
> ```powershell
> uv run python -c "import sys; print(sys.executable)"
> uv run python -c "import qlib; print(qlib.__version__)"
> ```

> [example] Fast provider path check
>
> ```powershell
> echo $env:QLIB_PROVIDER_URI
> Test-Path $env:QLIB_PROVIDER_URI
> ```

> [note] Do not start by changing many Qlib config values at once. First locate the layer that is failing, then change one thing and rerun.

## 5. Python Basic For Engineering

### 5.a Data Types And Values

> [concept] **A value** is a concrete piece of data in Python runtime memory. **A data type** is the category that defines what operations the value supports. The critical use: types tell you what a value can do, what errors to expect, and how to design function inputs/outputs.

> [concept] **Core scalar types**:
> - `int`: whole number, like `252`.
> - `float`: decimal number, like `0.035`.
> - `bool`: truth value, `True` or `False`.
> - `str`: text, like `"AAPL"`.
> - `None`: absence of a value.
>
> > [example] Basic values and types
> >
> > ```python
> > instrument = "AAPL"
> > lookback_days = 20
> > signal_score = 0.73
> > is_tradeable = True
> > last_error = None
> >
> > print(type(instrument))
> > print(type(lookback_days))
> > print(type(signal_score))
> > print(type(is_tradeable))
> > print(type(last_error))
> > ```
>
> > [note] In Python, scalar values like `1` are still objects. `1` is an `int` object, and operators call object behavior underneath. Normal code uses `1 + 2`, but the object method exists as `(1).__add__(2)`.
> >
> > ```python
> > print(type(1))
> > print(1 + 2)
> > print((1).__add__(2))
> > ```

> [concept] **Python variables** are names bound to objects. The variable is not the object itself; it is a name pointing to a value in runtime memory.
>
> > [example] Type affects valid operations
> >
> > ```python
> > price = 101.25
> > shares = 10
> > instrument = "AAPL"
> >
> > market_value = price * shares
> > label = instrument + "_close"
> > ```

> [note] For engineering code, do not rely only on memory. Use type annotations to document expected values at function boundaries.
>
> > [example] Type-annotated function boundary
> >
> > ```python
> > def calculate_return(today_price: float, yesterday_price: float) -> float:
> >     return today_price / yesterday_price - 1
> > ```

### 5.b Collections And Data Structures

> [concept] **A collection** stores multiple values under one object. The critical use: collections let code represent real grouped concepts such as instruments, feature names, config values, rows, and lookup tables. A collection is also called a container because it contains other objects.
>
> > [example] Qlib-style container use
> >
> > ```python
> > feature_names = ["close", "volume", "return_5d"]
> > model_params = {"learning_rate": 0.05, "num_leaves": 64}
> > train_period = ("2010-01-01", "2018-12-31")
> > universe = {"AAPL", "MSFT", "NVDA"}
> > ```
> >
> > `feature_names` is a `list`; `model_params` is a `dict`; `train_period` is a `tuple`; `universe` is a `set`.
>
> > [note] Container choice is about the access pattern: index by position, lookup by name, preserve fixed grouping, or test membership.

> [concept] **`list`** is an ordered, mutable sequence. Use it when order matters and items may be added, removed, or changed.
>
> > [example] List: ordered batch
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> >
> > first_instrument = instruments[0]
> > last_instrument = instruments[-1]
> >
> > instruments.append("TSLA")
> > instruments.remove("MSFT")
> >
> > for instrument in instruments:
> >     print(instrument)
> > ```
> >
> > Use a `list` when the order is meaningful or when the collection will change. Access uses integer position: `0` is first, `-1` is last.
>
> > [note] Python allows mixed-type lists, like `["AAPL", 101.25, True]`, but engineering code should usually keep list items the same kind of thing. Homogeneous lists are easier to loop over, type-check, test, and reason about.
>
> > [note] Common list mistake: changing a list while looping over it can skip items or create confusing behavior. Prefer building a new list when filtering.
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> > filtered = [name for name in instruments if name != "MSFT"]
> > ```

> [concept] **`tuple`** is an ordered, usually immutable sequence. Use it for fixed groups of values where the position has meaning.
>
> > [example] Tuple: fixed pair
> >
> > ```python
> > date_range = ("2020-01-01", "2020-12-31")
> >
> > start_date, end_date = date_range
> > print(start_date)
> > print(end_date)
> > ```
> >
> > Use a `tuple` when the group is fixed and position carries meaning. Here, position `0` means start date and position `1` means end date.
>
> > [example] Tuple as a stable key
> >
> > ```python
> > key = ("AAPL", "2020-01-02")
> > price_by_key = {
> >     key: 101.25,
> > }
> >
> > print(price_by_key[("AAPL", "2020-01-02")])
> > ```
> >
> > A tuple can be used as a `dict` key if its contents are immutable. A `list` cannot be used as a `dict` key.
>
> > [note] Dict keys must be hashable. Hashable means Python can compute a stable lookup identity for the key. The object used as a key must not change its hash/equality behavior while stored in the dict. A tuple of strings is stable, so `("AAPL", "2020-01-02")` can be a key. A list is mutable, so `["AAPL", "2020-01-02"]` cannot be a key and raises `TypeError: unhashable type: 'list'`.
>
> > [note] Tuple does not mean "small list." It usually means fixed structure. If you need to append/remove items, use a `list`.

> [concept] **`dict`** is a key/value mapping. Use it when values should be looked up by name, such as config, metadata, or parameters.
>
> > [example] Dict: named config
> >
> > ```python
> > config = {
> >     "provider_uri": "C:\\path\\to\\qlib_data",
> >     "benchmark": "SPY",
> >     "lookback_days": 20,
> > }
> >
> > provider_uri = config["provider_uri"]
> > lookback_days = config.get("lookback_days", 10)
> >
> > config["lookback_days"] = 30
> >
> > for key, value in config.items():
> >     print(key, value)
> > ```
> >
> > Use a `dict` when names matter more than position. `config["provider_uri"]` reads a required key; `config.get("lookback_days", 10)` reads a key with a fallback value.
>
> > [example] Dict creation styles
> >
> > ```python
> > # Dict literal: written manually in code.
> > config = {
> >     "benchmark": "SPY",
> >     "lookback_days": 20,
> > }
> >
> > # Build from two lists.
> > instruments = ["AAPL", "MSFT"]
> > prices = [101.25, 220.50]
> > price_by_instrument = dict(zip(instruments, prices))
> >
> > # Fill step by step.
> > sector_by_instrument = {}
> > sector_by_instrument["AAPL"] = "technology"
> > sector_by_instrument["JPM"] = "financials"
> > ```
> >
> > Dicts can be written as literals, built from other collections, filled step by step, or loaded from config/data files such as JSON, TOML, YAML, or CSV-derived data.
>
> > [example] Dict as lookup table
> >
> > ```python
> > sector_by_instrument = {
> >     "AAPL": "technology",
> >     "JPM": "financials",
> > }
> >
> > sector = sector_by_instrument["AAPL"]
> > ```
> >
> > Use a lookup dict when the question is "given this key, what value belongs to it?"
>
> > [note] Common dict mistake: `config["missing_key"]` raises `KeyError` if the key is absent. Use direct indexing for required keys and `.get()` only when a fallback is acceptable.

> [concept] **`set`** is an unordered collection of unique values. Use it for membership checks and duplicate removal.
>
> > [example] Set: uniqueness and membership
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "AAPL"]
> > unique_instruments = set(instruments)
> >
> > has_aapl = "AAPL" in unique_instruments
> > unique_instruments.add("NVDA")
> >
> > print(unique_instruments)
> > ```
> >
> > Use a `set` when duplicate values should collapse and membership checks are the main operation. Do not use a `set` when stable order matters.
>
> > [example] Set operations
> >
> > ```python
> > qlib_universe = {"AAPL", "MSFT", "NVDA"}
> > model_universe = {"MSFT", "NVDA", "TSLA"}
> >
> > overlap = qlib_universe & model_universe
> > only_in_qlib = qlib_universe - model_universe
> > combined = qlib_universe | model_universe
> > ```
> >
> > `&` means intersection, `-` means difference, and `|` means union.
>
> > [note] Set output order is not stable. If you need sorted output, convert after the set operation: `sorted(unique_instruments)`.

> [decision] Default choices:
> - Use `list` for ordered batches.
> - Use `dict` for named config or lookup values.
> - Use `tuple` for fixed pairs/groups.
> - Use `set` for uniqueness and membership checks.

### 5.c Keywords And Operators

> [concept] **Keywords** are reserved words in Python syntax. The critical use: they define language structure, so they cannot be used as variable names.
>
> > [example] Common keywords
> >
> > ```python
> > if is_tradeable:
> >     return signal_score
> > else:
> >     return None
> > ```
> >
> > `if`, `else`, `return`, and `None` are Python keywords.

> [concept] **Operators** are symbols or words that combine, compare, or transform values. The critical use: operators express calculation, comparison, boolean logic, membership, identity, and assignment.
>
> > [example] Operator categories
> >
> > ```python
> > price * shares              # arithmetic
> > price > 0                   # comparison
> > is_tradeable and has_data   # boolean logic
> > "AAPL" in universe          # membership
> > value is None               # identity
> > signal_score = 0.73         # assignment
> > ```

> [concept] **Arithmetic operators** calculate numeric values.
>
> > [example] Arithmetic
> >
> > ```python
> > price = 101.25
> > previous_price = 100.00
> >
> > daily_return = price / previous_price - 1
> > doubled = price * 2
> > remainder = 10 % 3
> > power = 2 ** 3
> > ```
> >
> > Common arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

> [concept] **Comparison operators** produce `True` or `False`.
>
> > [example] Comparison
> >
> > ```python
> > price = 101.25
> >
> > is_positive = price > 0
> > is_exact = price == 101.25
> > is_not_zero = price != 0
> > ```
> >
> > Common comparison operators: `==`, `!=`, `<`, `<=`, `>`, `>=`.

> [concept] **Boolean operators** combine truth values. Use `and`, `or`, and `not` to express conditions.
>
> > [example] Boolean logic
> >
> > ```python
> > has_price = True
> > has_volume = False
> >
> > usable = has_price and has_volume
> > partial = has_price or has_volume
> > blocked = not has_price
> > ```
> >
> > `and` requires both sides true. `or` requires at least one side true. `not` flips a truth value.

> [concept] **Membership operators** test whether a value is inside a container.
>
> > [example] Membership
> >
> > ```python
> > universe = {"AAPL", "MSFT", "NVDA"}
> >
> > if "AAPL" in universe:
> >     print("tradable")
> >
> > if "TSLA" not in universe:
> >     print("not in universe")
> > ```
> >
> > Use `in` and `not in` with `list`, `tuple`, `dict`, `set`, strings, and other containers.

> [concept] **Identity operators** test whether two names point to the same object. The critical use: use `is None` and `is not None` for missing sentinel checks.
>
> > [example] Identity
> >
> > ```python
> > last_error = None
> >
> > if last_error is None:
> >     print("no error")
> >
> > if last_error is not None:
> >     print(last_error)
> > ```
> >
> > Use `==` for value equality. Use `is` mainly for `None`, `True`, and `False` identity checks.
>
> > [note] C++ mental mapping: `==` is value equality; `is` is closer to asking whether two Python names refer to the same object identity. It is not a data-type check. Use `isinstance(x, int)` for type/category checks.
> >
> > ```python
> > a = []
> > b = []
> > c = a
> >
> > print(a == b)  # True: same value/content
> > print(a is b)  # False: different list objects
> > print(a is c)  # True: same list object
> > ```

> [concept] **Assignment operators** bind or update values.
>
> > [example] Assignment
> >
> > ```python
> > count = 0
> > count += 1
> >
> > total_return = 0.05
> > total_return *= 100
> > ```
> >
> > `=` binds a name. `+=`, `-=`, `*=`, and `/=` update from the current value.

> [note] Common mistake: `=` assigns a value, while `==` compares values.
>
> > [example] Assignment vs comparison
> >
> > ```python
> > score = 1.0       # assign
> > score == 1.0      # compare
> > ```

### 5.d Control Flow

> [concept] **Control flow** is the order in which code runs. The critical use: it lets code choose branches, repeat work, stop early, skip cases, and transform collections.
>
> > [example] Control-flow shape
> >
> > ```python
> > if condition:
> >     run_this()
> > else:
> >     run_that()
> > ```
> >
> > Python uses indentation to define the block. There are no `{}` braces for normal control-flow blocks.

> [concept] **`if` / `elif` / `else`** chooses one branch based on conditions.
>
> > [example] Branching
> >
> > ```python
> > signal_score = 0.73
> >
> > if signal_score > 0.8:
> >     action = "strong_buy"
> > elif signal_score > 0.5:
> >     action = "watch"
> > else:
> >     action = "ignore"
> > ```
> >
> > `elif` means "else if." Python checks branches top to bottom and runs the first true branch.

> [concept] **An iterable** is an object Python can give one item at a time. The critical use: `for` loops and comprehensions work on iterables, not only lists.
>
> > [example] Common iterables
> >
> > ```python
> > for item in [1, 2, 3]:      # list
> >     print(item)
> >
> > for item in (1, 2, 3):      # tuple
> >     print(item)
> >
> > for item in {1, 2, 3}:      # set
> >     print(item)
> >
> > for key in {"a": 1, "b": 2}:  # dict loops over keys
> >     print(key)
> >
> > for char in "AAPL":         # string
> >     print(char)
> > ```
> >
> > Iterable means "can be looped over." List is one iterable type, not the only one.
>
> > [note] A `str` is iterable character by character. Looping over `"AAPL"` yields `"A"`, `"A"`, `"P"`, then `"L"`.

> [concept] **`for` loops** repeat code over items from an iterable.
>
> > [example] Loop over instruments
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> >
> > for instrument in instruments:
> >     print(instrument)
> > ```
> >
> > The loop variable `instrument` is rebound on each iteration.

> [concept] **`while` loops** repeat while a condition remains true. Use them when the number of iterations is not naturally known upfront.
>
> > [example] While loop
> >
> > ```python
> > retries = 0
> >
> > while retries < 3:
> >     print("try", retries)
> >     retries += 1
> > ```
> >
> > In data scripts, prefer `for` when iterating over a known collection.

> [concept] **`break` and `continue`** control loop progress. `break` exits the loop. `continue` skips the rest of the current iteration and moves to the next one.
>
> > [example] Stop or skip
> >
> > ```python
> > instruments = ["AAPL", "BAD", "MSFT"]
> >
> > for instrument in instruments:
> >     if instrument == "BAD":
> >         continue
> >
> >     if instrument == "MSFT":
> >         break
> >
> >     print(instrument)
> > ```
> >
> > Use `continue` for invalid cases. Use `break` when the loop's purpose is already finished.

> [concept] **Comprehensions** create collections from existing iterables in one expression.
>
> > [example] List comprehension
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> > lower_names = [name.lower() for name in instruments]
> > ```
> >
> > Use comprehensions for simple transformations or filters. Use normal loops when logic becomes multi-step.
>
> > [example] Filter with comprehension
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> > selected = [name for name in instruments if name != "MSFT"]
> > ```

> [note] Python control flow depends on indentation. A wrong indent changes program meaning or raises `IndentationError`.

### 5.e Frequent Built-In Functions

> [concept] **Built-in functions** are functions available from Python immediately, without importing a module. The critical use: they are the small standard tools used constantly for inspection, conversion, looping, and basic calculation.
>
> > [example] Built-in function call shape
> >
> > ```python
> > result = function_name(input_value)
> > ```

> [function] `len()`
>
> > [concept] `len()` returns the number of items in a container or iterable-like object.
> >
> > [example]
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> > count = len(instruments)
> > print(count)
> > ```

> [function] `type()`
>
> > [concept] `type()` returns the object's data type/class.
> >
> > [example]
> >
> > ```python
> > price = 101.25
> > print(type(price))
> > ```

> [function] `isinstance()`
>
> > [concept] `isinstance()` checks whether an object belongs to a type/category. Use this for type checks instead of `is`.
> >
> > [example]
> >
> > ```python
> > price = 101.25
> >
> > if isinstance(price, float):
> >     print("price is a float")
> > ```

> [function] `range()`
>
> > [concept] `range()` creates an iterable sequence of integers, usually for looping a fixed number of times.
> >
> > [example]
> >
> > ```python
> > for i in range(3):
> >     print(i)
> > ```

> [function] `enumerate()`
>
> > [concept] `enumerate()` loops over an iterable while also giving the item index.
> >
> > [example]
> >
> > ```python
> > instruments = ["AAPL", "MSFT", "NVDA"]
> >
> > for index, instrument in enumerate(instruments):
> >     print(index, instrument)
> > ```

> [function] `zip()`
>
> > [concept] `zip()` pairs items from multiple iterables by position.
> >
> > [example]
> >
> > ```python
> > instruments = ["AAPL", "MSFT"]
> > prices = [101.25, 220.50]
> >
> > price_by_instrument = dict(zip(instruments, prices))
> > ```

> [function] `sorted()`
>
> > [concept] `sorted()` returns a new sorted list without changing the original iterable.
> >
> > [example]
> >
> > ```python
> > universe = {"MSFT", "AAPL", "NVDA"}
> > ordered = sorted(universe)
> > print(ordered)
> > ```

> [function] `sum()`, `min()`, `max()`
>
> > [concept] `sum()`, `min()`, and `max()` calculate basic aggregate values from numeric or comparable items.
> >
> > [example]
> >
> > ```python
> > returns = [0.01, -0.02, 0.03]
> >
> > print(sum(returns))
> > print(min(returns))
> > print(max(returns))
> > ```

### 5.f Functions

> [concept] **A function** is a named block of reusable behavior. The critical use: functions create clear boundaries around inputs, outputs, and side effects so code can be tested, reused, and moved from `scripts/` into `src/`.
>
> > [example] Define and call a function
> >
> > ```python
> > def calculate_return(today_price: float, yesterday_price: float) -> float:
> >     return today_price / yesterday_price - 1
> >
> >
> > result = calculate_return(103.0, 100.0)
> > print(result)
> > ```
> >
> > `def` defines the function. `return` sends a value back to the caller. `calculate_return(...)` calls the function.

> [concept] **Parameters and arguments** are related but not identical. A parameter is the name in the function definition. An argument is the actual value passed during a call.
>
> > [example] Parameter vs argument
> >
> > ```python
> > def normalize_score(score: float) -> float:
> >     return score / 100
> >
> >
> > normalized = normalize_score(73.0)
> > ```
> >
> > `score` is the parameter. `73.0` is the argument.

> [concept] **Return value** is the object a function sends back to its caller. If a function has no explicit `return`, Python returns `None`.
>
> > [example] Return value
> >
> > ```python
> > def make_label(instrument: str, field: str) -> str:
> >     return instrument + "_" + field
> >
> >
> > label = make_label("AAPL", "close")
> > ```
>
> > [example] Implicit `None`
> >
> > ```python
> > def print_label(label: str) -> None:
> >     print(label)
> >
> >
> > result = print_label("AAPL_close")
> > print(result)
> > ```
> >
> > `print_label(...)` prints text as a side effect and returns `None`.

> [concept] **Default arguments** give a parameter a fallback value when the caller does not provide one.
>
> > [example] Default argument
> >
> > ```python
> > def is_large_move(return_value: float, threshold: float = 0.05) -> bool:
> >     return abs(return_value) > threshold
> >
> >
> > print(is_large_move(0.07))
> > print(is_large_move(0.07, threshold=0.10))
> > ```
> >
> > Defaults are useful for common settings, but important research/config choices should still be visible at call sites.

> [concept] **Pure functions and side effects** are different. A pure function only uses inputs to produce a return value. A side effect changes something outside the function, such as printing, writing a file, mutating a list, or logging.
>
> > [example] Pure function
> >
> > ```python
> > def calculate_market_value(price: float, shares: int) -> float:
> >     return price * shares
> > ```
>
> > [example] Side effect
> >
> > ```python
> > def add_instrument(instruments: list[str], instrument: str) -> None:
> >     instruments.append(instrument)
> > ```
> >
> > Prefer pure functions for reusable logic because they are easier to test. Use side effects at clear boundaries such as scripts, file I/O, logging, or explicit mutation helpers.

> [concept] **Function boundaries** are engineering boundaries. The critical use: a good function name plus typed inputs and outputs makes Qlib-facing code easier to wrap, test, and debug.
>
> > [example] Good boundary
> >
> > ```python
> > def build_feature_names(base_fields: list[str], windows: list[int]) -> list[str]:
> >     names = []
> >
> >     for field in base_fields:
> >         for window in windows:
> >             names.append(f"{field}_{window}d")
> >
> >     return names
> > ```
> >
> > Inputs are explicit, output is explicit, and the function does not depend on hidden global state.

### 5.g Imports, Modules, And Packages

> [concept] **A module** is usually one `.py` file that Python can import. The critical use: modules let reusable code live in one file and be used from another file.
>
> > [example] Module shape
> >
> > ```text
> > src/catchup/returns.py
> > ```
> >
> > If `returns.py` defines `calculate_return`, other code can import that function.

> [concept] **A package** is a folder of importable Python modules. The critical use: packages organize related reusable code under one namespace.
>
> > [example] Package shape
> >
> > ```text
> > src/catchup/
> >   returns.py
> >   features.py
> >   qlib_wrapper.py
> > ```
> >
> > `catchup` is the package namespace. `returns`, `features`, and `qlib_wrapper` are modules inside it.

> [note] Practical import ontology: package = importable folder; module = importable `.py` file; functions/classes/constants = names defined inside a module. Good practice for this repo: put reusable functions/classes in modules under `src/catchup/`, then import those names from scripts or tests. Do not treat the whole repo as one global function search space.

> [concept] **`import`** loads code from a module or package into the current Python file. The critical use: import is how scripts, tests, and modules reuse behavior without copying code.
>
> > [example] Import styles
> >
> > ```python
> > import math
> > from pathlib import Path
> > from catchup.returns import calculate_return
> > ```
> >
> > `import math` loads the module. `from pathlib import Path` imports one name from a module. `from catchup.returns import calculate_return` imports a project function from a package module.
>
> > [note] Python does not search globally for overlapping function names. It finds the module/package path first, then looks for the requested name inside that module. `catchup.returns.calculate_return` and `catchup.math_utils.calculate_return` are different full names. If both are imported as local name `calculate_return`, the later import rebinds that local name.
>
> > [note] When same-name functions/classes exist, keep the module namespace visible. Prefer `import catchup.returns as returns` and call `returns.calculate_return(...)` instead of importing multiple same-name functions into one local name.

> [concept] **Import path** is where Python looks for modules/packages. The critical use: import errors often mean Python is using the wrong environment, wrong working directory, or wrong package layout.
>
> > [example] Check import search paths
> >
> > ```python
> > import sys
> >
> > for path in sys.path:
> >     print(path)
> > ```
> >
> > In this repo, use `uv run python ...` from `C:\pythonCatchup` so Python runs inside the repo environment.

> [concept] **`src` layout** keeps importable project code under `src/`. The critical use: it separates reusable package code from scripts, tests, notes, and data files.
>
> > [example] Repo import boundary
> >
> > ```text
> > scripts/run_demo.py        # runnable command
> > src/catchup/returns.py     # reusable importable code
> > tests/test_returns.py      # tests reusable code
> > ```
> >
> > Scripts should import from `catchup`; reusable logic should not depend on scripts.

> [decision] Import rules for this repo:
> - Use standard-library imports first.
> - Use third-party imports second.
> - Use local `catchup` imports third.
> - Avoid importing from `scripts/`.
> - Move reusable logic into `src/catchup/` before testing or reusing it.

> [note] Common import error: `ModuleNotFoundError` means Python cannot find the requested module/package from the current environment and import path. First check interpreter, `.venv`, working directory, and package location.

### 5.h Errors And Exceptions

> [concept] **An exception** is an error object raised during runtime. The critical use: exceptions let code stop normal flow when something invalid happens and report what went wrong.
>
> > [example] Exception object
> >
> > ```python
> > error = ValueError("price must be positive")
> > raise error
> > ```
> >
> > `ValueError` is an exception class. `ValueError(...)` constructs an exception object. `raise` throws it.

> [concept] **`raise`** starts the error path. Use it when a function detects invalid input or an impossible state.
>
> > [example] Raise on invalid input
> >
> > ```python
> > def validate_price(price: float) -> None:
> >     if price <= 0:
> >         raise ValueError("price must be positive")
> > ```
> >
> > Positive price returns normally. Zero or negative price raises `ValueError`.
>
> > [note] Scope/call-stack insight: the `raise` statement is written inside the function and creates the exception object there, but the exception does not remain local like a normal variable. It exits the function abnormally and travels up the call stack until a matching `except` catches it or the program stops with a stack trace.

> [concept] **`try` / `except`** handles an exception instead of letting it crash the program. The critical use: catch only errors you can handle meaningfully.
>
> > [example] Catch a specific error
> >
> > ```python
> > try:
> >     validate_price(-1.0)
> > except ValueError as exc:
> >     print("invalid price:", exc)
> > ```
> >
> > `exc` is the caught exception object. Catching `ValueError` does not catch every possible error type.

> [concept] **Common exception types** communicate the kind of failure.
>
> > [example] Common built-in exceptions
> >
> > ```python
> > ValueError("bad value")              # valid type, invalid value
> > TypeError("wrong type")              # operation used with wrong type
> > KeyError("missing_key")              # dict key missing
> > IndexError("index out of range")      # list/tuple index missing
> > FileNotFoundError("file missing")     # path does not exist
> > ModuleNotFoundError("module missing") # import failed
> > ```

> [concept] **Fail fast** means raise an error close to the bad input instead of letting wrong state travel deeper into the program. The critical use: in data/QLib workflows, early validation prevents silent bad results.
>
> > [example] Fail fast
> >
> > ```python
> > def calculate_return(today_price: float, yesterday_price: float) -> float:
> >     if yesterday_price <= 0:
> >         raise ValueError("yesterday_price must be positive")
> >
> >     return today_price / yesterday_price - 1
> > ```
>
> > [note] Raise exceptions at the invariant or axiom level: the earliest place where code knows a required truth has been violated. Examples: price must be positive, path must exist, date range must be valid, required config key must exist, DataFrame must contain `trade_date`, or universe must not be empty.

> [concept] **Exception handling boundary** is where code decides whether to recover, log, retry, or stop. Reusable functions should usually raise clear exceptions; scripts may catch them to print/log a clean message.
>
> > [example] Script-level handling
> >
> > ```python
> > def main() -> None:
> >     try:
> >         result = calculate_return(103.0, 0.0)
> >         print(result)
> >     except ValueError as exc:
> >         print("failed:", exc)
> >
> >
> > if __name__ == "__main__":
> >     main()
> > ```

> [note] Avoid broad `except Exception:` unless there is a clear boundary reason, such as logging a top-level script failure before re-raising or exiting. Broad catches can hide real bugs.

### 5.i File I/O And Paths

> [concept] **File I/O** means reading from and writing to files. The critical use: Python workflows need to load configs/data, write artifacts, inspect logs, and pass local paths into tools like Qlib.
>
> > [example] Read text
> >
> > ```python
> > from pathlib import Path
> >
> > path = Path("data/README.md")
> > text = path.read_text(encoding="utf-8")
> > print(text)
> > ```

> [concept] **Read/write modes** define how Python opens a file. The critical use: mode controls whether Python reads existing content, overwrites content, appends content, or fails if the file is missing.
>
> > [example] Common modes
> >
> > ```python
> > with open("data/README.md", "r", encoding="utf-8") as file:
> >     text = file.read()
> >
> > with open("data/processed/summary.txt", "w", encoding="utf-8") as file:
> >     file.write("new summary\n")
> >
> > with open("data/processed/summary.txt", "a", encoding="utf-8") as file:
> >     file.write("append one more line\n")
> > ```
> >
> > `"r"` reads, `"w"` writes and overwrites, `"a"` appends. `with open(...)` closes the file automatically.

> [concept] **String matching after read** checks whether loaded text contains expected content. The critical use: quick validation for config files, logs, notes, and small text outputs.
>
> > [example] Basic string matching
> >
> > ```python
> > from pathlib import Path
> >
> > text = Path("data/README.md").read_text(encoding="utf-8")
> >
> > if "raw" in text:
> >     print("mentions raw data")
> >
> > if text.startswith("#"):
> >     print("markdown heading")
> >
> > for line in text.splitlines():
> >     if "data" in line.lower():
> >         print(line)
> > ```
> >
> > Use `in` for containment, `.startswith()` for prefix checks, `.endswith()` for suffix checks, and `.splitlines()` to inspect line by line.

> [concept] **`pathlib.Path`** is Python's standard-library path object. The critical use: it represents filesystem paths cleanly across Windows/macOS/Linux instead of manually gluing strings together.
>
> > [example] Build paths
> >
> > ```python
> > from pathlib import Path
> >
> > repo_root = Path("C:/pythonCatchup")
> > raw_data = repo_root / "data" / "raw"
> > file_path = raw_data / "prices.csv"
> > ```
> >
> > `/` joins path parts when using `Path` objects. It is not division in this context.

> [concept] **Relative paths and absolute paths** describe where a file lives. Relative paths start from the current working directory. Absolute paths start from a drive/root.
>
> > [example] Relative vs absolute
> >
> > ```python
> > from pathlib import Path
> >
> > relative_path = Path("data/raw/prices.csv")
> > absolute_path = Path("C:/pythonCatchup/data/raw/prices.csv")
> > ```
> >
> > In scripts, know the current working directory before trusting a relative path.

> [concept] **File existence checks** validate an invariant before reading or writing. The critical use: fail early with a clear error instead of crashing deeper with vague data problems.
>
> > [example] Validate path
> >
> > ```python
> > from pathlib import Path
> >
> > path = Path("data/raw/prices.csv")
> >
> > if not path.exists():
> >     raise FileNotFoundError(f"missing file: {path}")
> > ```

> [concept] **Writing files** creates or replaces external state on disk. The critical use: treat writes as side effects and keep output paths explicit.
>
> > [example] Write text
> >
> > ```python
> > from pathlib import Path
> >
> > output_path = Path("data/processed/summary.txt")
> > output_path.parent.mkdir(parents=True, exist_ok=True)
> > output_path.write_text("done\n", encoding="utf-8")
> > ```
> >
> > `parent.mkdir(...)` ensures the containing folder exists before writing the file.

> [decision] Path rules for this repo:
> - Use `pathlib.Path` for path handling.
> - Keep machine-specific paths in environment variables or config, not hardcoded in reusable code.
> - Use `data/raw/` for raw input data and `data/processed/` for generated/intermediate data.
> - Validate paths before passing them into Qlib or pandas.

> [note] Windows accepts backslashes, but Python strings treat `\` as an escape character. Prefer `Path("C:/pythonCatchup/data")`, raw strings like `r"C:\pythonCatchup\data"`, or environment/config values.

### 5.j Classes And OOP

> [concept] **Class sample use**: a class is a blueprint for creating objects that bundle state and behavior. The critical use: use a class when a thing has memory/state plus operations that naturally belong to that state.
>
> > [example] Small complete class
> >
> > ```python
> > class ReturnThreshold:
> >     def __init__(self, threshold: float) -> None:
> >         self.threshold = threshold
> >
> >     def is_large_move(self, return_value: float) -> bool:
> >         return abs(return_value) > self.threshold
> >
> >
> > checker = ReturnThreshold(0.05)
> > print(checker.is_large_move(0.07))
> > ```
> >
> > `ReturnThreshold` is the class. `checker` is an instance/object. `threshold` is object state. `is_large_move(...)` is behavior attached to that state.

> [concept] **Members / attributes** are names stored on an object or class. The critical use: attributes hold state that methods can read or update.
>
> > [example] Instance attributes
> >
> > ```python
> > class QlibDataConfig:
> >     def __init__(self, provider_uri: str, region: str) -> None:
> >         self.provider_uri = provider_uri
> >         self.region = region
> >
> >
> > config = QlibDataConfig("C:/qlib_data", "us")
> > print(config.provider_uri)
> > ```
> >
> > `self.provider_uri` and `self.region` are instance attributes. Each instance can hold different values.
>
> > [example] Class attribute
> >
> > ```python
> > class QlibDataConfig:
> >     default_region = "us"
> >
> >     def __init__(self, provider_uri: str) -> None:
> >         self.provider_uri = provider_uri
> > ```
> >
> > `default_region` belongs to the class object. Use class attributes for shared constants, not per-instance changing state.

> [concept] **Methods** are functions defined inside a class. The critical use: methods operate on object state through `self`.
>
> > [example] Method reads state
> >
> > ```python
> > class FeatureBuilder:
> >     def __init__(self, windows: list[int]) -> None:
> >         self.windows = windows
> >
> >     def names_for_field(self, field: str) -> list[str]:
> >         return [f"{field}_{window}d" for window in self.windows]
> >
> >
> > builder = FeatureBuilder([5, 10, 20])
> > print(builder.names_for_field("return"))
> > ```
> >
> > A method call like `builder.names_for_field("return")` passes `builder` as `self` automatically.
>
> > [note] Method call has parentheses because code runs. Attribute access has no parentheses because it reads stored state: `builder.windows`.

> [concept] **Constructor / `__init__`** initializes a new instance after Python allocates the object. The critical use: put required setup and invariant validation there.
>
> > [example] Constructor validation
> >
> > ```python
> > from pathlib import Path
> >
> >
> > class DataPaths:
> >     def __init__(self, raw_dir: Path, processed_dir: Path) -> None:
> >         if not raw_dir.exists():
> >             raise FileNotFoundError(f"missing raw_dir: {raw_dir}")
> >
> >         self.raw_dir = raw_dir
> >         self.processed_dir = processed_dir
> > ```
> >
> > `DataPaths(...)` calls `__init__`. Python does not use C++-style overloaded constructors; use defaults, class methods, or separate factory functions when needed.

> [concept] **Destructor / cleanup** exists as `__del__`, but it is rarely the right tool. The critical use: clean up external resources explicitly with `with` context managers or explicit `.close()` methods.
>
> > [example] Prefer context manager for files
> >
> > ```python
> > from pathlib import Path
> >
> > path = Path("data/README.md")
> >
> > with path.open("r", encoding="utf-8") as file:
> >     text = file.read()
> > ```
> >
> > The `with` block handles cleanup deterministically. Do not rely on `__del__` for important file/network/resource cleanup.

> [concept] **`self` vs C++ `this`**: `self` is the current instance, but Python makes it explicit as the first method parameter. The critical use: any method that reads or writes instance state needs `self`.
>
> > [example] Explicit `self`
> >
> > ```python
> > class Counter:
> >     def __init__(self) -> None:
> >         self.count = 0
> >
> >     def increment(self) -> None:
> >         self.count += 1
> > ```
> >
> > C++ has implicit `this`; Python writes `self` explicitly by convention.

> [concept] **Public / private** in Python is mostly convention, not compiler enforcement. The critical use: communicate intended API boundaries clearly.
>
> > [example] Visibility conventions
> >
> > ```python
> > class QlibRunner:
> >     def run_backtest(self) -> None:
> >         self._initialize_provider()
> >
> >     def _initialize_provider(self) -> None:
> >         print("internal helper")
> > ```
> >
> > `run_backtest` is public API. `_initialize_provider` is internal by convention. Python will not stop outside code from calling `_initialize_provider`, but the underscore says "do not depend on this."
>
> > [note] Double underscore names like `__secret` trigger name mangling. They are not normal C++-style private members. Use single underscore for most internal implementation details.

> [concept] **Inheritance / base class** lets a subclass reuse or specialize behavior from a parent class. The critical use: use it only when there is a real "is-a" relationship or a shared interface.
>
> > [example] Base class and override
> >
> > ```python
> > class BaseValidator:
> >     def validate(self, value: object) -> None:
> >         if value is None:
> >             raise ValueError("value is required")
> >
> >
> > class PriceValidator(BaseValidator):
> >     def validate(self, value: object) -> None:
> >         super().validate(value)
> >
> >         if not isinstance(value, int | float):
> >             raise TypeError("price must be numeric")
> >
> >         if value <= 0:
> >             raise ValueError("price must be positive")
> > ```
> >
> > `PriceValidator` inherits from `BaseValidator`. `super().validate(value)` calls the base-class method.
>
> > [note] A child class does not need to rewrite every base method. If the child does not define a method, Python searches the base class and uses the inherited method directly. If the child defines the same method name, it overrides the base method; the child can still call the base version with `super()`.
> >
> > ```python
> > class BaseValidator:
> >     def reject_missing(self, value: object) -> None:
> >         if value is None:
> >             raise ValueError("value is required")
> >
> >
> > class PriceValidator(BaseValidator):
> >     # No reject_missing method here; inherited method is used directly.
> >     def validate(self, price: float) -> None:
> >         self.reject_missing(price)
> > ```
>
> > [example] Multiple inheritance and MRO
> >
> > ```python
> > class BaseA:
> >     def setup(self) -> None:
> >         print("BaseA")
> >         super().setup()
> >
> >
> > class BaseB:
> >     def setup(self) -> None:
> >         print("BaseB")
> >         super().setup()
> >
> >
> > class Root:
> >     def setup(self) -> None:
> >         print("Root")
> >
> >
> > class Child(BaseA, BaseB, Root):
> >     def setup(self) -> None:
> >         print("Child")
> >         super().setup()
> >
> >
> > child = Child()
> > child.setup()
> > print(Child.__mro__)
> > ```
> >
> > Python supports multiple inheritance with `class Child(BaseA, BaseB):`. In that case, `super()` means "call the next method in the method resolution order," not simply "call my one parent." Check the order with `Child.__mro__`.

> [concept] **Virtual / polymorphism** in Python is dynamic by default. The critical use: Python does not need a `virtual` keyword; method lookup happens at runtime based on the actual object.
>
> > [example] Runtime dispatch
> >
> > ```python
> > class CsvLoader:
> >     def load(self) -> str:
> >         return "csv data"
> >
> >
> > class QlibLoader:
> >     def load(self) -> str:
> >         return "qlib data"
> >
> >
> > def run_loader(loader) -> None:
> >     print(loader.load())
> >
> >
> > run_loader(CsvLoader())
> > run_loader(QlibLoader())
> > ```
> >
> > `run_loader` only needs an object with a `.load()` method. This is duck typing: if it behaves like the needed interface, Python can use it.

> [concept] **Composition** means one object owns or uses another object. The critical use: prefer composition over inheritance for Qlib wrappers because external systems are dependencies, not parents.
>
> > [example] Composition for workflow
> >
> > ```python
> > class DataLoader:
> >     def load(self) -> list[float]:
> >         return [100.0, 101.0, 103.0]
> >
> >
> > class ResearchWorkflow:
> >     def __init__(self, loader: DataLoader) -> None:
> >         self.loader = loader
> >
> >     def run(self) -> None:
> >         prices = self.loader.load()
> >         print(prices)
> >
> >
> > workflow = ResearchWorkflow(loader=DataLoader())
> > workflow.run()
> > ```
> >
> > `ResearchWorkflow` uses a `DataLoader`; it does not inherit from it.
>
> > [note] Dependency-boundary reason: external tools like Qlib are dependencies, not object identity. Composition keeps Qlib behind a narrow interface you own, makes testing easier with fake runners/loaders, and protects repo code from external API changes.

> [concept] **Dataclasses** are standard-library classes for mostly-data objects. The critical use: use `@dataclass` for typed config or record objects before writing manual constructor boilerplate.
>
> > [example] Dataclass config
> >
> > ```python
> > from dataclasses import dataclass
> > from pathlib import Path
> >
> >
> > @dataclass
> > class DataPaths:
> >     raw_dir: Path
> >     processed_dir: Path
> >
> >
> > paths = DataPaths(
> >     raw_dir=Path("data/raw"),
> >     processed_dir=Path("data/processed"),
> > )
> > ```
> >
> > A dataclass automatically creates a constructor and readable representation for simple data containers.
>
> > [example] Dataclass with defaults
> >
> > ```python
> > from dataclasses import dataclass
> >
> >
> > @dataclass
> > class ModelConfig:
> >     model_name: str
> >     learning_rate: float = 0.05
> >     num_leaves: int = 64
> >
> >
> > config = ModelConfig(model_name="lightgbm")
> > print(config.learning_rate)
> > ```
> >
> > `model_name` is required. `learning_rate` and `num_leaves` have default values.
>
> > [example] Generated representation and equality
> >
> > ```python
> > from dataclasses import dataclass
> >
> >
> > @dataclass
> > class Instrument:
> >     symbol: str
> >     exchange: str
> >
> >
> > a = Instrument("AAPL", "NASDAQ")
> > b = Instrument("AAPL", "NASDAQ")
> >
> > print(a)
> > print(a == b)
> > ```
> >
> > Dataclass generates readable `repr` output and value-style equality by field values.
>
> > [example] Approximate generated constructor
> >
> > ```python
> > @dataclass
> > class DataPaths:
> >     raw_dir: Path
> >     processed_dir: Path
> > ```
> >
> > Roughly becomes:
> >
> > ```python
> > def __init__(self, raw_dir: Path, processed_dir: Path) -> None:
> >     self.raw_dir = raw_dir
> >     self.processed_dir = processed_dir
> > ```
> >
> > `@dataclass` reads annotated class-level fields and turns them into constructor parameters and instance attributes.

> [decision] Class rules for this repo:
> - Use functions first when behavior is stateless.
> - Use dataclasses for config/data objects.
> - Use classes when state and behavior must travel together.
> - Prefer composition over inheritance for Qlib wrappers/workflows.
> - Keep Qlib-specific details behind a small wrapper interface.
> - Avoid large classes that mix config, data loading, model training, backtesting, logging, plotting, and file output.

### 5.k Frequent Standard Library Tools

#### 5.k.1 Standard Library Concept

> [concept] **The standard library** is the set of modules included with Python itself. The critical use: reach for standard-library tools first when they solve the problem cleanly, because they require no extra `uv` or `pip` install.
>
> > [example] Standard-library imports
> >
> > ```python
> > from pathlib import Path  # filesystem paths
> > import json               # JSON read/write
> > import logging            # runtime messages
> > from datetime import date  # dates
> > ```
> >
> > These modules come with Python and do not belong in `requirements.txt`.

#### 5.k.2 `pathlib`

> [concept] **`pathlib`** provides `Path`, a filesystem path class. The critical use: represent paths as objects with methods instead of fragile strings.
>
> > [example] Path object
> >
> > ```python
> > from pathlib import Path
> >
> > repo_root = Path("C:/pythonCatchup")
> > data_file = repo_root / "data" / "raw" / "prices.csv"  # join path parts
> >
> > print(data_file.exists())  # check whether path exists
> > print(data_file.parent)    # containing folder
> > ```

#### 5.k.3 `os`

> [concept] **`os`** exposes operating-system interaction. The critical use: read environment variables and inspect process-level OS state.
>
> > [example] Environment variable
> >
> > ```python
> > import os
> >
> > provider_uri = os.environ.get("QLIB_PROVIDER_URI")  # returns None if missing
> >
> > if provider_uri is None:
> >     raise ValueError("QLIB_PROVIDER_URI is not set")
> > ```
> >
> > Use `os.environ[...]` for required env vars and `os.environ.get(...)` when missing is acceptable.

#### 5.k.4 `json`

> [concept] **`json`** reads and writes JSON text. The critical use: JSON is common for structured config, small metadata, and machine-readable output.
>
> > [example] Write and read JSON
> >
> > ```python
> > import json
> > from pathlib import Path
> >
> > config = {"benchmark": "SPY", "lookback_days": 20}
> > path = Path("data/processed/config.json")
> >
> > path.parent.mkdir(parents=True, exist_ok=True)  # ensure output folder exists
> > path.write_text(json.dumps(config, indent=2), encoding="utf-8")
> >
> > loaded = json.loads(path.read_text(encoding="utf-8"))
> > print(loaded["benchmark"])
> > ```

#### 5.k.5 `logging`

> [concept] **`logging`** provides structured runtime messages. The critical use: replace durable `print()` progress messages in scripts/workflows with level-based logs.
>
> > [example] Basic logging
> >
> > ```python
> > import logging
> >
> > logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
> >
> > logging.info("starting workflow")
> > logging.warning("missing values detected")
> > logging.error("workflow failed")
> > ```
> >
> > Use `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL` to mark severity.

#### 5.k.6 `datetime`

> [concept] **`datetime`** provides date and time objects. The critical use: avoid treating dates as arbitrary strings when logic depends on ordering, ranges, or calendar math.
>
> > [example] Date objects
> >
> > ```python
> > from datetime import date
> >
> > start = date(2020, 1, 1)
> > end = date(2020, 12, 31)
> >
> > print(start < end)
> > print(start.isoformat())
> > ```
> >
> > `date(2020, 1, 1)` creates a date object. `.isoformat()` returns `"2020-01-01"`.

#### 5.k.7 `argparse`

> [concept] **`argparse`** parses command-line arguments for scripts. The critical use: turn hardcoded script settings into explicit terminal inputs.
>
> > [example] Script arguments
> >
> > ```python
> > import argparse
> >
> > parser = argparse.ArgumentParser()
> > parser.add_argument("--provider-uri", required=True)  # required CLI option
> > parser.add_argument("--region", default="us")         # optional CLI option
> >
> > args = parser.parse_args()
> > print(args.provider_uri)
> > print(args.region)
> > ```
> >
> > Run shape: `uv run python scripts/run_demo.py --provider-uri C:/qlib_data`.

#### 5.k.8 `dataclasses`

> [concept] **`dataclasses`** generates boilerplate methods for mostly-data classes. The critical use: make config/record objects explicit without manually writing repetitive constructors.
>
> > [example] Config dataclass
> >
> > ```python
> > from dataclasses import dataclass
> > from pathlib import Path
> >
> >
> > @dataclass
> > class DataConfig:
> >     provider_uri: Path
> >     region: str = "us"
> >
> >
> > config = DataConfig(provider_uri=Path("C:/qlib_data"))
> > print(config)
> > ```
> >
> > `@dataclass` reads annotated fields and generates `__init__`, `__repr__`, and `__eq__` by default.

#### 5.k.9 `typing`

> [concept] **`typing`** provides tools for type hints. The critical use: make function boundaries, config shapes, and wrapper interfaces easier for humans and tools to reason about.
>
> > [example] Type hints
> >
> > ```python
> > from typing import Literal
> >
> >
> > Region = Literal["us", "cn"]
> >
> >
> > def normalize_region(region: Region) -> Region:
> >     return region
> > ```
> >
> > Use built-in generics like `list[str]` and `dict[str, float]` first. Reach for `typing` when you need richer type concepts such as `Literal`, `Protocol`, or `TypedDict`.

### 5.l Pandas Frequent Functions And Use

> [concept] **Pandas frequent functions** are table operations used to inspect, select, clean, combine, and transform `DataFrame` data. The critical use: most quant data bugs are table-form bugs, not syntax bugs.

#### 5.l.1 Inspection Functions

> [function] `head()`, `tail()`, `shape`, `dtypes`, `info()`, `describe()`
>
> > [concept] Inspection functions reveal table form: rows, columns, types, missing values, and value ranges.
> >
> > [example]
> >
> > ```python
> > print(df.head())      # first 5 rows
> > print(df.tail())      # last 5 rows
> > print(df.shape)       # (row_count, column_count)
> > print(df.dtypes)      # column data types
> > print(df.info())      # compact schema/memory summary
> > print(df.describe())  # numeric summary statistics
> > ```
> >
> > Use these before trusting a transformation result.

#### 5.l.2 Selection And Filtering

> [function] Column selection, boolean masks, `loc`, `iloc`
>
> > [concept] Selection chooses columns or rows from a `DataFrame`. The critical use: isolate the data slice you intend before calculating.
> >
> > [example]
> >
> > ```python
> > prices = df["price"]                         # one column as Series
> > subset = df[["instrument", "trade_date"]]    # selected columns
> >
> > mask = df["instrument"] == "AAPL"            # boolean Series
> > aapl_rows = df.loc[mask]                     # rows by label/mask
> >
> > first_row = df.iloc[0]                       # row by integer position
> > ```
> >
> > Use `.loc` for label/mask selection. Use `.iloc` for integer-position selection.

#### 5.l.3 Missing Values

> [function] `isna()`, `notna()`, `dropna()`, `fillna()`
>
> > [concept] Missing-value functions detect or handle absent data. The critical use: missing values can silently change signals, joins, rolling windows, and model inputs.
> >
> > [example]
> >
> > ```python
> > print(df.isna().sum())          # missing count by column
> >
> > clean = df.dropna(subset=["price"])  # remove rows missing price
> > filled = df.fillna({"volume": 0})    # fill missing volume with 0
> > valid = df[df["price"].notna()]      # keep rows with price
> > ```
> >
> > Do not fill missing values mechanically. Decide whether missing means unknown, zero, unavailable, or invalid.

#### 5.l.4 Sorting And Indexing

> [function] `sort_values()`, `set_index()`, `reset_index()`
>
> > [concept] Sorting and indexing define row order and lookup structure. The critical use: time-series operations like `shift`, `pct_change`, and `rolling` depend on correct order.
> >
> > [example]
> >
> > ```python
> > ordered = df.sort_values(["instrument", "trade_date"])
> > indexed = ordered.set_index(["instrument", "trade_date"])
> > flat = indexed.reset_index()
> > ```
> >
> > For quant data, sort by instrument and date before calculating time-based features.

#### 5.l.5 Groupby And Aggregation

> [function] `groupby()`, `agg()`, `transform()`
>
> > [concept] Groupby splits a table into groups, applies logic per group, then combines results. The critical use: calculate per-instrument statistics without mixing instruments.
> >
> > [example]
> >
> > ```python
> > avg_price = df.groupby("instrument")["price"].mean()
> >
> > summary = df.groupby("instrument").agg(
> >     price_mean=("price", "mean"),
> >     row_count=("price", "size"),
> > )
> >
> > df["price_zscore_input"] = df.groupby("instrument")["price"].transform("mean")
> > ```
> >
> > Use `agg()` when the output is one row per group. Use `transform()` when the output should align back to the original rows.

#### 5.l.6 Merge And Join

> [function] `merge()`, `join()`
>
> > [concept] Merge/join combines tables by keys. The critical use: combine features, labels, metadata, and calendars without changing row meaning accidentally.
> >
> > [example]
> >
> > ```python
> > merged = prices.merge(
> >     sectors,
> >     on="instrument",
> >     how="left",
> >     validate="many_to_one",
> > )
> > ```
> >
> > `on` is the key, `how` controls join behavior, and `validate` catches unexpected duplicate-key relationships.
>
> > [note] After every merge, check `shape`, duplicate keys, and missing values in newly joined columns.

#### 5.l.7 Shift, Rolling, And Percent Change

> [function] `shift()`, `rolling()`, `pct_change()`
>
> > [concept] These functions create time-series features and labels. The critical use: they must be applied within the right instrument group and date order.
> >
> > [example]
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > df["return_1d"] = df.groupby("instrument")["price"].pct_change()
> > df["future_return_1d"] = df.groupby("instrument")["price"].shift(-1) / df["price"] - 1
> > df["rolling_mean_5d"] = (
> >     df.groupby("instrument")["price"]
> >     .rolling(5)
> >     .mean()
> >     .reset_index(level=0, drop=True)
> > )
> > ```
> >
> > `pct_change()` calculates percentage change. `shift(-1)` looks forward and is label-like; use carefully to avoid leakage.

#### 5.l.8 Save And Load DataFrames

> [function] `read_csv()`, `to_csv()`, `read_parquet()`, `to_parquet()`
>
> > [concept] Save/load functions move `DataFrame` data between memory and disk. The critical use: make intermediate outputs inspectable and reproducible.
> >
> > [example]
> >
> > ```python
> > import pandas as pd
> > from pathlib import Path
> >
> > path = Path("data/processed/features.csv")
> > path.parent.mkdir(parents=True, exist_ok=True)
> >
> > df.to_csv(path, index=False)       # write DataFrame
> > loaded = pd.read_csv(path)         # read DataFrame
> > ```
> >
> > Use CSV for easy inspection. Use parquet later for larger typed data when dependencies and workflow are ready.

### 5.m Software Engineering Basics

#### 5.m.1 Separation Of Concerns

> [concept] **Separation of concerns** means each module/function/class has one clear responsibility. The critical use: Qlib-facing code stays understandable when data loading, feature building, training, backtesting, logging, and file output are not tangled together.
>
> > [example] Separate responsibilities
> >
> > ```text
> > src/catchup/data_loader.py      # load data
> > src/catchup/features.py         # build features
> > src/catchup/qlib_runner.py      # call Qlib
> > scripts/run_backtest.py         # command-style runner
> > ```
> >
> > A script can orchestrate steps, but reusable logic should live in small modules.

#### 5.m.2 Config Vs Code

> [concept] **Config vs code** means settings should be separated from behavior. The critical use: paths, dates, model names, and parameters should change without editing core Python logic.
>
> > [example] Config shape
> >
> > ```python
> > config = {
> >     "provider_uri": "C:/qlib_data",  # machine-specific setting
> >     "start_date": "2020-01-01",      # experiment setting
> >     "model_name": "lightgbm",        # model choice
> > }
> > ```
> >
> > Keep stable behavior in functions/classes. Keep changing values in config, environment variables, or CLI arguments.

#### 5.m.3 Dependency Boundaries

> [concept] **Dependency boundaries** isolate external tools behind code you own. The critical use: Qlib, pandas, and file formats can change; your repo should expose a smaller stable interface.
>
> > [example] Boundary shape
> >
> > ```python
> > class QlibRunner:
> >     def run_backtest(self, config_path: str) -> None:
> >         # Qlib-specific calls stay hidden inside this wrapper.
> >         print("run qlib backtest", config_path)
> > ```
> >
> > Callers depend on `QlibRunner.run_backtest(...)`, not scattered Qlib internals.

#### 5.m.4 Testing Strategy

> [concept] **Testing strategy** decides which behavior deserves automated protection. The critical use: tests preserve meaning when code changes.
>
> > [example] Test reusable logic first
> >
> > ```python
> > def calculate_return(today_price: float, yesterday_price: float) -> float:
> >     return today_price / yesterday_price - 1
> >
> >
> > def test_calculate_return():
> >     # This expected behavior should not silently change later.
> >     assert calculate_return(103.0, 100.0) == 0.03
> > ```
> >
> > Prioritize tests for `src/catchup/` reusable functions before testing exploratory scripts.

#### 5.m.5 Logging And Observability

> [concept] **Observability** means the program leaves enough runtime evidence to understand what happened. The critical use: long Qlib/data workflows need stage-level logs, not only final success/failure.
>
> > [example] Stage logging
> >
> > ```python
> > import logging
> >
> > logging.info("load data")
> > logging.info("build features")
> > logging.info("train model")
> > logging.info("run backtest")
> > ```
> >
> > Log workflow stages, key paths, row counts, and output artifact locations.

#### 5.m.6 Reproducible Scripts

> [concept] **Reproducible scripts** can be rerun with the same inputs and produce understandable outputs. The critical use: Qlib experiments should not depend on hidden terminal state or hand-edited code paths.
>
> > [example] Reproducible script inputs
> >
> > ```powershell
> > uv run python scripts/run_backtest.py --config configs/demo.json
> > ```
> >
> > A good script makes input config, environment, output path, and command visible.

#### 5.m.7 Refactoring Signals

> [concept] **Refactoring signals** are signs code should be reshaped without changing behavior. The critical use: refactor before a script becomes a hard-to-test pile of hidden assumptions.
>
> > [example] Signals
> >
> > ```text
> > repeated code appears in multiple places
> > a function needs many unrelated arguments
> > one script mixes loading, cleaning, modeling, plotting, and saving
> > a local variable would be useful in tests
> > a Qlib-specific call appears in many modules
> > ```
> >
> > Common moves: extract function, extract module, introduce dataclass config, add wrapper, or move logic from `scripts/` to `src/catchup/`.


## 6. NumPy And Pandas For Financial Data

### 6.a Under the hood - Qlib

> [concept] **Financial data in Python** usually moves between two forms: NumPy arrays for numeric matrix-style computation, and pandas `DataFrame` objects for labeled table/time-series work. The critical use: know when you need raw numeric speed versus labeled data safety.
>
> > [example] Mental split
> >
> > ```text
> > NumPy array      -> numeric matrix/vector operations
> > pandas DataFrame -> rows, columns, dates, instruments, labels
> > ```
> >
> > For Qlib prep, pandas is the main inspection/manipulation layer; NumPy is the numeric engine underneath many operations.

### 6.b NumPy Arrays

> [concept] **A NumPy array** is a typed numeric container optimized for vectorized computation. The critical use: use arrays when operations are mostly numeric and shape-based.
>
> > [example] Array and vectorized math
> >
> > ```python
> > import numpy as np
> >
> > prices = np.array([100.0, 101.0, 103.0])
> > returns = prices[1:] / prices[:-1] - 1  # vectorized return calculation
> >
> > print(returns)
> > ```
> >
> > `prices[1:]` means all prices except the first. `prices[:-1]` means all prices except the last.

### 6.c DataFrame Price Tables

> [concept] **A financial `DataFrame`** is usually a table with instrument, date/time, and numeric fields such as price, volume, return, feature, or label. The critical use: preserve the labels that explain what each number means.
>
> > [example] Price table
> >
> > ```python
> > import pandas as pd
> >
> > df = pd.DataFrame(
> >     {
> >         "instrument": ["AAPL", "AAPL", "MSFT"],
> >         "trade_date": ["2020-01-02", "2020-01-03", "2020-01-02"],
> >         "close": [100.0, 101.0, 220.0],
> >         "volume": [1000, 1200, 900],
> >     }
> > )
> > ```
> >
> > `instrument + trade_date` often acts like the row identity for daily market data.

### 6.d Returns

> [concept] **Return** measures relative price change. The critical use: most quant features, labels, and performance metrics are based on returns rather than raw prices.
>
> > [example] Scalar return
> >
> > ```python
> > yesterday_price = 100.0
> > today_price = 103.0
> >
> > daily_return = today_price / yesterday_price - 1
> > print(daily_return)
> > ```
> >
> > `103 / 100 - 1 = 0.03`, meaning the price increased by `3%`.
>
> > [example] Single-instrument pandas return
> >
> > ```python
> > import pandas as pd
> >
> > df = pd.DataFrame(
> >     {
> >         "trade_date": ["2020-01-01", "2020-01-02", "2020-01-03"],
> >         "close": [100.0, 103.0, 101.0],
> >     }
> > )
> >
> > df["return_1d"] = df["close"].pct_change()
> > ```
> >
> > First row return is missing because there is no previous price. `101 / 103 - 1 = -0.0194`.
>
> > [example] One-period return
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > df["return_1d"] = df.groupby("instrument")["close"].pct_change()
> > ```
> >
> > Group by `instrument` before `pct_change()` so one stock's return does not use another stock's previous row.

### 6.e Grouped Time Series

> [concept] **Grouped time-series operations** apply calculations separately per instrument. The critical use: financial panels contain many instruments, and each instrument has its own time sequence.
>
> > [example] Per-instrument previous close
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > df["prev_close"] = df.groupby("instrument")["close"].shift(1)
> > df["return_1d"] = df["close"] / df["prev_close"] - 1
> > ```
> >
> > `shift(1)` looks one row backward inside each instrument group.
>
> > [example] Independent grouped time-series example
> >
> > ```python
> > import pandas as pd
> >
> > # One table has four rows: two AAPL dates and two MSFT dates.
> > # Expected unique instruments: AAPL, MSFT.
> > prices = pd.DataFrame(
> >     {
> >         "instrument": ["AAPL", "MSFT", "AAPL", "MSFT"],
> >         "trade_date": ["2020-01-01", "2020-01-01", "2020-01-02", "2020-01-02"],
> >         "close": [100.0, 200.0, 103.0, 198.0],
> >     }
> > )
> >
> > # Sort inside each instrument's timeline before using time-series operations.
> > # Expected order after sort: AAPL rows together by date, then MSFT rows by date.
> > prices = prices.sort_values(["instrument", "trade_date"])
> >
> > # Shift separately inside each instrument group.
> > # Expected change: first row for each instrument gets prev_close = NaN.
> > prices["prev_close"] = prices.groupby("instrument")["close"].shift(1)
> >
> > # Calculate return using the instrument's own previous close.
> > # Expected values: AAPL second row = 103 / 100 - 1 = 0.03;
> > # MSFT second row = 198 / 200 - 1 = -0.01.
> > prices["return_1d"] = prices["close"] / prices["prev_close"] - 1
> >
> > print(prices)
> > ```
> >
> > Without `groupby("instrument")`, `shift(1)` could cross from one instrument to another and create false returns.

### 6.f Rolling Windows

> [concept] **Rolling windows** calculate statistics over recent history. The critical use: many factors use trailing means, volatility, momentum, or volume averages.
>
> > [example] Five-day moving average
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > df["close_ma_5"] = (
> >     df.groupby("instrument")["close"]
> >     .rolling(5)
> >     .mean()
> >     .reset_index(level=0, drop=True)
> > )
> > ```
> >
> > The `reset_index(...)` step realigns the rolling result back to the original row index.

### 6.g Alignment And Leakage (Future back to yesterday)

> [concept] **Alignment** means features, labels, dates, and instruments refer to the intended same row/event. The critical use: misalignment creates silent wrong results.
>
> > [example] Future return label
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > next_close = df.groupby("instrument")["close"].shift(-1)
> > df["future_return_1d"] = next_close / df["close"] - 1
> > ```
> >
> > `shift(-1)` looks forward and is label-like. Do not use future-looking columns as features.

> [concept] **Leakage** means future information enters the feature side of a model. The critical use: leakage can make backtests look good while being unusable in real trading.

### 6.h Missing Values And Outliers

> [concept] **Missing values and outliers** are data-state problems, not only cleaning chores. The critical use: missing prices, zero volume, bad dates, and extreme values can distort returns and factors.
>
> > [example] Basic checks
> >
> > ```python
> > print(df.isna().sum())                 # missing values by column
> > print(df["close"].describe())          # range and distribution
> > print((df["volume"] <= 0).sum())       # suspicious volume rows
> > ```
> >
> > Decide what missing means before using `fillna()`.

### 6.i Save Intermediate Data

> [concept] **Intermediate data artifacts** are saved tables between workflow stages. The critical use: they make feature/label generation inspectable and reproducible.
>
> > [example] Save feature table
> >
> > ```python
> > from pathlib import Path
> >
> > output_path = Path("data/processed/features.csv")
> > output_path.parent.mkdir(parents=True, exist_ok=True)
> >
> > df.to_csv(output_path, index=False)
> > ```
> >
> > Use CSV first for inspection. Use parquet later when data is large and typed storage matters.

## 7. Quant Research Concepts

### 7.a Instruments

> [concept] **Instrument** means the tradable object being observed or traded. The critical use: most market data rows are keyed by `instrument` plus time.
>
> > [example] Instrument examples
> >
> > ```text
> > AAPL  -> Apple stock
> > MSFT  -> Microsoft stock
> > SPY   -> ETF
> > BTC   -> crypto asset
> > ES    -> futures contract
> > ```
> >
> > In a daily price table, `instrument + trade_date` often identifies one row.

### 7.b Features

> [concept] **Features** are input variables used by a model or rule. The critical use: features represent information known at decision time.
>
> > [example] Feature columns
> >
> > ```text
> > return_5d
> > volume_zscore
> > close_ma_20
> > volatility_20d
> > ```
> >
> > Feature columns should not use future information.

### 7.c Labels

> [concept] **Labels** are target values the model tries to predict. The critical use: labels usually look forward in time, while features must not.
>
> > [example] Future-return label
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> >
> > next_close = df.groupby("instrument")["close"].shift(-1)  # future close
> > df["label_return_1d"] = next_close / df["close"] - 1
> > ```
> >
> > `shift(-1)` is acceptable for labels, but dangerous for features.

### 7.d Factors

> [concept] **Factor** usually means a signal or explanatory variable believed to relate to future returns. The critical use: factors are candidate features or ranked signals used in quant research.
>
> > [example] Simple momentum factor
> >
> > ```python
> > df = df.sort_values(["instrument", "trade_date"])
> > df["momentum_5d"] = df.groupby("instrument")["close"].pct_change(5)
> > ```
> >
> > A factor is not automatically alpha. It must be tested.
>
> > [concept] **Feature vs factor**: a feature is any model input column; a factor is a finance/quant signal with an economic or statistical hypothesis about future returns. A factor used in a model becomes a feature, but not every feature is a meaningful factor.
> >
> > [example] Feature/factor distinction
> >
> > ```text
> > momentum_5d        -> factor and feature if fed into model
> > volume_zscore      -> factor-like feature
> > day_of_week        -> feature, not necessarily a finance factor
> > missing_value_flag -> feature for data quality, not a return factor
> > ```

### 7.e Alpha

> [concept] **Alpha** is useful predictive edge after accounting for benchmark, risk, costs, and implementation constraints. The critical use: alpha is what remains after a signal survives realistic evaluation.
>
> > [example] Practical distinction
> >
> > ```text
> > factor = candidate signal
> > alpha  = signal that appears to add tradable predictive value
> > ```
> >
> > A backtest with no transaction costs or leakage checks does not prove alpha.

### 7.f Universe

> [concept] **Universe** is the set of instruments eligible for research or trading. The critical use: universe choice controls what the model can see, rank, buy, or ignore.
>
> > [example] Universe
> >
> > ```python
> > universe = {"AAPL", "MSFT", "NVDA"}
> >
> > tradable_rows = df[df["instrument"].isin(universe)]
> > ```
> >
> > Universe rules should be explicit because changing the universe changes the research result.

### 7.g Benchmark

> [concept] **Benchmark** is the reference portfolio or index used to judge performance. The critical use: strategy return alone is incomplete; compare against what could have been earned passively.
>
> > [example] Benchmark examples
> >
> > ```text
> > SPY      -> broad US equity ETF benchmark
> > S&P 500  -> large-cap US stock index
> > cash     -> no-risk/no-position reference
> > ```
> >
> > Excess return means strategy return minus benchmark return.

### 7.h Rebalance

> [concept] **Rebalance** means updating portfolio holdings at scheduled times or when rules trigger. The critical use: rebalance frequency affects turnover, costs, risk, and whether signals are implementable.
>
> > [example] Rebalance schedule
> >
> > ```text
> > daily rebalance   -> update holdings every trading day
> > weekly rebalance  -> update once per week
> > monthly rebalance -> update once per month
> > ```
> >
> > More frequent rebalance can react faster but usually increases transaction costs.

### 7.i Transaction Costs

> [concept] **Transaction costs** are the costs of trading, including commissions, bid/ask spread, slippage, taxes, and market impact. The critical use: costs can turn a good-looking signal into an untradable one.
>
> > [example] Cost intuition
> >
> > ```text
> > gross return = before trading costs
> > net return   = after trading costs
> > ```
> >
> > High-turnover strategies need stricter cost assumptions.

### 7.j Drawdown

> [concept] **Drawdown** measures decline from a previous portfolio peak. The critical use: drawdown describes pain/risk that average return alone hides.
>
> > [example] Drawdown intuition
> >
> > ```text
> > portfolio peak = 100
> > current value  = 80
> > drawdown       = 80 / 100 - 1 = -20%
> > ```
> >
> > Maximum drawdown is the worst peak-to-trough decline over a period.

### 7.k Information Coefficient 

> [concept] **Information Coefficient (IC)** measures correlation between a signal and future return. The critical use: IC checks whether higher signal scores tend to correspond to higher future returns.
>
> > [example] IC intuition
> >
> > ```text
> > signal_score high -> future_return tends to be high
> > positive IC       -> signal ranking has predictive direction
> > near-zero IC      -> signal has little rank relationship
> > negative IC       -> signal may be inverted or wrong
> > ```
> >
> > IC is often measured cross-sectionally by date, then averaged over time.

## 8. ML Workflow Basics

### 8.a Features And Labels

### 8.b Train Validation Test

### 8.c Leakage

### 8.d Model Fitting

### 8.e Prediction Scores

### 8.f Metrics

## 9. Qlib Mental Model

### 9.a Data Provider

### 9.b Calendar

### 9.c Instruments

### 9.d Dataset Config

### 9.e Model

### 9.f Recorder

### 9.g Strategy

### 9.h Backtest

### 9.i Experiment Tracking

## 10. Qlib First-Run Lab

### 10.a Install Qlib

### 10.b Initialize Data

### 10.c Run An Existing Example

### 10.d Inspect Outputs

### 10.e Understand What Happened

## 11. Mini Exercises

### 11.a Calculate Returns

### 11.b Create A Rolling Factor

### 11.c Create A Future-Return Label

### 11.d Train A Simple Model

### 11.e Rank Assets By Score

### 11.f Identify Leakage

## 12. Python Software Engineering Patterns

### 12.a Project Architecture

### 12.b Dependency Boundaries

### 12.c Config Design

### 12.d Type-Driven Design

### 12.e Error Design

### 12.f Logging And Observability

### 12.g Testing Strategy

### 12.h CLI Design

### 12.i Data Pipeline Design

### 12.j Wrapper Design For Qlib

### 12.k Notebooks Vs Scripts Vs Package Code

### 12.l Refactoring Patterns

### 12.m Packaging And Distribution

### 12.n Performance And Scaling Basics

## 13. Common Mistakes

## 14. Glossary

## 15. Next Steps
