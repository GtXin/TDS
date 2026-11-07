---
title: memo0008_qlib_macos_venv
memo_type: qlib_macos_venv
tags:
  - memo
  - qlib
  - macos
  - venv
  - uv
  - project-009
status: active
source:
  - docs/memo/memo0004_mac_setup.md
  - docs/memo/memo0006_qlib_windows_venv.md
  - docs/memo/memo0007_qlib_data_structure.md
  - pyproject.toml
created: 2026-08-31
---

# memo0008_qlib_macos_venv

## 1. Session Overview

### 1.a Purpose

- Define the Qlib macOS virtual-environment procedure for Project 009.
- Keep this memo narrower than the general macOS setup memo.
- Avoid confusing the recorded Windows Qlib `.venv` with a usable macOS Qlib
  environment.
- Give one clear verification path for `import qlib` on macOS.

### 1.b Scope

> [scope] This memo is only about Qlib inside a macOS Project 009 `.venv`.

> [scope] General machine setup, VS Code setup, Git setup, and non-Qlib Python
> setup belong in `docs/memo/memo0004_mac_setup.md`.

### 1.c Question

> [question] How should Project 009 create, install, and verify a macOS `.venv`
> when the goal is Qlib work?

### 1.d Short Answer

> [answer] Recreate a macOS-native `.venv/`, install the project with the
> `qlib` optional dependency, and verify Qlib through both direct import and the
> Project 009 smoke checker.

> [decision] A Windows `.venv/Scripts/python.exe` cannot be reused as the macOS
> Qlib environment.

## 2. Source Facts

### 2.a Project Dependency

> [source] `pyproject.toml` declares Qlib as an optional dependency:

```toml
[project.optional-dependencies]
qlib = ["pyqlib"]
```

### 2.b Existing Windows Record

> [source] `docs/memo/memo0006_qlib_windows_venv.md` records a previous Windows
> Qlib install where the smoke check detected `pyqlib` version `0.9.7`.

> [note] That record is useful evidence, but not a portable macOS environment.

### 2.c Qlib Data Shape

> [source] `docs/memo/memo0007_qlib_data_structure.md` records the current Qlib
> boundary: Project 009 keeps `Kline` and `TimeSeries`, then adapts to Qlib
> fields like `$open`, `$high`, `$low`, `$close`, and `$volume`.

## 3. macOS Qlib Environment Shape

### 3.a Expected Shape

```text
.venv/
├── bin/
│   ├── python
│   └── pip
├── lib/
└── pyvenv.cfg
```

### 3.b Wrong Shape

```text
.venv/
└── Scripts/
    └── python.exe
```

> [problem] If `.venv/Scripts/python.exe` is the only Python inside `.venv/`,
> the environment is Windows-shaped and should be replaced for macOS Qlib work.

## 4. Procedure

### 4.a Check Project Metadata And `.venv` Compatibility

> [workflow] Check whether the repo can support a macOS Qlib `.venv`
>
> - Step 1: enter Project 009.
>   - Path: `/Users/coder/Public/EngineGit/proj009`.
>   - Verify: `pwd` prints that path.
>
> - Step 2: check `pyproject.toml`.
>   - System: project metadata.
>   - Verify: `requires-python` allows Python 3.11+ and optional dependency
>     group `qlib = ["pyqlib"]` exists.
>
> - Step 3: check current `.venv` shape.
>   - System: local virtual environment.
>   - Verify: macOS-compatible shape has `.venv/bin/python`; Windows shape has
>     `.venv/Scripts/python.exe` and should be replaced.
>
> - Step 4: check whether the current Python can import Qlib.
>   - System: Python runtime.
>   - Verify: either Qlib imports successfully or the failure is recorded before
>     reinstalling.

```zsh
cd /Users/coder/Public/EngineGit/proj009
grep -n 'requires-python\\|qlib = ' pyproject.toml
test -x .venv/bin/python && .venv/bin/python --version
test -f .venv/Scripts/python.exe && echo "Windows-shaped .venv on macOS"
uv run python -c "import qlib; print(qlib.__version__)" || echo "Qlib not ready in current macOS environment"
```

### 4.b Warning: Do Not Repair During Unrelated Tasks

> [warning] If `4.a` shows that the current `.venv` is missing, Windows-shaped,
> or not Qlib-ready, do not automatically repair it while working on an
> unrelated task.

> [decision] Keep the active task independent from Qlib environment repair
> unless the user or active milestone explicitly asks for Qlib setup.

> [workflow] If Qlib is not required for the active task:
>
> - Step 1: record the compatibility result.
> - Step 2: continue the task through Project 009 native structures such as
>   `Kline`, `TimeSeries`, CSV loading, validation, and charting.
> - Step 3: mention that Qlib verification is deferred.
> - Step 4: do not mutate `.venv/`.

> [workflow] If Qlib setup is the active task, use the repair path in section 5.

> > [example] Task-independent note
> >
> > ```text
> > Qlib is not ready in the current macOS .venv, but this task does not require
> > Qlib. Continue with Project 009 native data structures and defer Qlib repair.
> > ```

### 4.c Create Qlib macOS `.venv` Only When In Scope

> [workflow] Create the Qlib-ready macOS `.venv` only when the task is
> explicitly about Qlib setup, Qlib smoke checks, or a milestone requiring Qlib.
>
> - Step 1: install or locate Python 3.11.
>   - System: `uv` Python manager.
>   - Verify: `uv python find 3.11` prints a path.
>
> - Step 2: create `.venv/`.
>   - System: `uv`.
>   - Verify: `.venv/bin/python` exists.

```zsh
uv python install 3.11
uv python find 3.11
uv venv --python 3.11 --prompt proj009
test -x .venv/bin/python
```

### 4.d Install Qlib Extra Directly

> [workflow] Install Project 009 with Qlib support
>
> - System: Python packaging.
> - Source: `pyproject.toml`.
> - Verify: `pyqlib` installs without package-resolution errors.

```zsh
uv pip install -e ".[qlib]"
```

### 4.e Verify Direct Qlib Import

```zsh
uv run python -c "import qlib; print(qlib.__version__); print(qlib.__file__)"
```

Expected shape:

```text
0.9.x
.../.venv/.../site-packages/qlib/__init__.py
```

### 4.f Verify Project Smoke Checker

```zsh
uv run python -m tradinglab.integrations.qlib.smoke
```

Expected shape:

```json
{
  "available": true,
  "error": null,
  "error_type": null,
  "version": "0.9.x"
}
```

## 5. Repair Path

### 5.a If Current `.venv` Is Windows-Shaped

> [decision] Do not debug macOS Qlib import failures inside a Windows-shaped
> `.venv`. Move it aside and create a macOS-native environment.

```zsh
mv .venv .venv.windows-backup
uv venv --python 3.11 --prompt proj009
uv pip install -e ".[qlib]"
uv run python -m tradinglab.integrations.qlib.smoke
```

> [decision] `.venv.windows-backup/` is local machine state and is listed in
> `.gitignore`.

### 5.b If Qlib Install Fails

> [workflow] Capture the failure before changing many variables.
>
> - Step 1: record macOS version and CPU.
> - Step 2: record Python version and path.
> - Step 3: record the exact `uv pip install -e ".[qlib]"` error.
> - Step 4: decide whether to pin, skip, or isolate Qlib for the current
>   milestone.

```zsh
sw_vers
uname -m
uv run python --version
uv run python -c "import sys; print(sys.executable)"
```

## 6. Boundary Rule

> [decision] Even when Qlib works on macOS, Qlib remains behind
> `src/tradinglab/integrations/qlib/`.

> [decision] Do not import Qlib from `src/tradinglab/domain/`.

> [decision] Do not make the current 7.4 Ke drawing-line work depend on Qlib
> unless the active milestone is updated to require it.

## 7. Open Questions

> [open] Does `pyqlib` install cleanly on the current macOS CPU and Python 3.11?

> [open] Should Project 009 pin Qlib after the first successful macOS install?

> [open] Should the macOS Qlib `.venv` include visualization extras by default,
> or should Qlib and visualization remain separate optional installs?
