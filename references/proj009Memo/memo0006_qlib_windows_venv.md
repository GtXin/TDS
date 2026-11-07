---
title: memo0006_qlib_windows_venv
tags:
  - memo
  - qlib
  - venv
  - python
  - project-009
status: active
source:
  - retired source copied before deletion: kb/kb0001_qlib-venv-installation.md
  - docs/memo/memo0003_memoguidance.md
created: 2026-08-31
---

# memo0006_qlib_windows_venv

## 1. Session Overview

### 1.a Purpose

- Preserve the old `kb0001_qlib-venv-installation.md` knowledge as a project
  memo.
- Record where Qlib was installed during the Windows-based 7.2 setup.
- Keep Qlib behind the Project 009 integration boundary.
- Make the macOS caveat explicit so the old Windows `.venv` does not confuse
  future setup work.

### 1.b Question

> [question] Where was Qlib installed, how was it verified, and what should
> Project 009 assume about that install?

### 1.c Short Answer

> [answer] Qlib was previously installed in a repository-local Windows virtual
> environment at `C:\proj009\.venv`, and the project smoke check detected
> `pyqlib` version `0.9.7`.

> [note] On the current macOS machine, the checked-out `.venv` appears
> Windows-shaped and is not a usable macOS Python environment. Recreate `.venv`
> locally on macOS before expecting `import qlib` to work.

## 2. Recorded Windows Setup

### 2.a Virtual Environment

> [source] Retired KB record copied before deletion:
> `kb/kb0001_qlib-venv-installation.md`.

```text
C:\proj009\.venv
```

### 2.b Qlib Package Location

```text
C:\proj009\.venv\Lib\site-packages\qlib
C:\proj009\.venv\Lib\site-packages\pyqlib-0.9.7.dist-info
```

### 2.c Python Executable

```text
C:\proj009\.venv\Scripts\python.exe
```

## 3. Verification Evidence

### 3.a Environment Creation

```powershell
& 'C:\Users\xinwe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv
```

### 3.b Qlib Installation

```powershell
& 'C:\proj009\.venv\Scripts\python.exe' -m pip install pyqlib
```

### 3.c Smoke Check

```powershell
$env:PYTHONPATH='C:\proj009\src'
& 'C:\proj009\.venv\Scripts\python.exe' -m tradinglab.integrations.qlib.smoke
```

Expected recorded result:

```json
{
  "available": true,
  "error": null,
  "error_type": null,
  "version": "0.9.7"
}
```

## 4. Project Decision

### 4.a Dependency Boundary

> [decision] Qlib is an optional integration dependency, not a core domain
> dependency.

> [decision] Project code should import Qlib only inside
> `src/tradinglab/integrations/qlib/`.

> [decision] Core domain records such as `Kline` and `TimeSeries` must not
> import Qlib.

### 4.b Local Environment Rule

> [decision] `.venv/` is local machine state and must not be treated as portable
> project source.

> [workflow] On macOS, recreate the virtual environment using the macOS setup
> memo rather than trying to run the old Windows `.venv`.

## 5. Commands To Reuse

### 5.a Check Which Python Sees Qlib

```powershell
C:\proj009\.venv\Scripts\python.exe -c "import qlib; print(qlib.__version__); print(qlib.__file__)"
```

Expected shape:

```text
0.9.7
C:\proj009\.venv\Lib\site-packages\qlib\__init__.py
```

### 5.b Run Project Smoke Check

```powershell
$env:PYTHONPATH='C:\proj009\src'
C:\proj009\.venv\Scripts\python.exe -m tradinglab.integrations.qlib.smoke
```

## 6. Open Questions

> [open] Should Qlib remain optional after the first real Qlib workflow is
> approved?

> [open] Should the project use `uv.lock` once the macOS environment is rebuilt?

> [open] Should a pinned Qlib requirements file exist before moving beyond
> import smoke checks?
