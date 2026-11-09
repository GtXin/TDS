# Python Setup
## 000 — Scope
Define the Python environment procedure for TDS and preserve Project009’s setup summary in the appendix. Baseline: `uv`, Python 3.11 and a repo-local `.venv`, following Project009’s approach.[1]
## 001 — Procedure for this repository
**Completed 2026-11-08:** `uv 0.12.7`, Python `3.11.16`, pytest `9.2.0` and Ruff `0.17.4`. TDS now has `pyproject.toml`, `.python-version`, `uv.lock` and an ignored local `.venv`. The commands and results below record the executed setup.
### 001.a — Enter TDS and verify uv
```zsh
cd /Users/coder/Public/EngineGit/TDS
uv --version
```
On another Mac, install `uv` with `brew install uv` if needed.[1]
### 001.b — Define the environment recipe
Created root `pyproject.toml` with this configuration. Runtime dependencies are empty until implementation requires them; `pytest` and `ruff` are development tools.[2]
```toml
[project]
name = "tds"
version = "0.0.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = ["pytest", "ruff"]
```
### 001.c — Create and synchronize the local environment
```zsh
uv python find 3.11
uv python pin 3.11
uv venv --python 3.11 --prompt tds
uv sync --group dev
```
The existing uv-managed Python 3.11 was reused. Setup commands used `env UV_CACHE_DIR=/private/tmp/tds-uv-cache` as a prefix for a writable temporary cache. On a machine without Python 3.11, run `uv python install 3.11` first.
`.python-version` selects Python 3.11; `.venv` holds this machine’s interpreter and packages; `uv.lock` records resolved dependencies. On subsequent checkouts, use `uv sync --locked --group dev` with the committed lockfile.[2]
### 001.d — Verify and use it
```zsh
uv run --locked python -c "import sys; print(sys.executable); print(sys.version)"
uv run --locked pytest --version
uv run --locked ruff --version
```
Verified Python `3.11.16` runs from `TDS/.venv/bin/python3`; pytest/Ruff report the versions above. Package compatibility, `uv lock --check --offline` and `uv sync --locked --group dev --offline` passed. `.venv` is ignored and untracked. No project tests exist yet. A temporary unused-import probe confirmed Ruff reports `F401` without modifying the file.
The first dependency sync failed under sandbox DNS restrictions; the network-enabled retry installed six development-tool packages. [Verification evidence](../../artifacts/mas/20261108-tds-python-environment-setup/verification.json).
Use `uv run python ...` for project commands. In VS Code, use `Python: Select Interpreter` to choose `.venv/bin/python`; manual terminal activation is unnecessary with `uv run`.[1][2]
### 001.e — Keep the recipe portable
Track `pyproject.toml`, `.python-version` and `uv.lock`; keep `.venv`, caches and machine-specific interpreter settings local. Windows and macOS create their own environments from the same recipe.[1][2]
## Appendix — Project009 setup summary
Project009’s Mac workflow uses Homebrew/`uv`, Python 3.11 and a local `.venv` with prompt `proj009`. VS Code selects that environment; Git retains the configuration rather than copying the environment between operating systems.[1]
The Python study notes also contain earlier `pythonCatchup` training workflows: `requirements.txt`, then `pyproject.toml` with `pytest`/`ruff` development tools. That history is separate from Project009’s own dependency configuration.[3]
Its `pyproject.toml` defines optional `visualization` dependencies (`pandas`, `matplotlib`, `mplfinance`) and a `qlib` extra (`pyqlib`). The documented editable installs are `uv pip install -e ".[visualization]"` and `uv pip install -e ".[qlib]"`; source edits then take effect without reinstalling the project.[1][4]
The Qlib memo describes replacing a Windows-shaped environment with a Mac-native one and verifying Qlib import with the project smoke checker. Installed-package metadata alone does not establish that those checks pass.[4]
## References

1. [Project009 memo0004: Mac setup](../../references/proj009Memo/memo0004_mac_setup.md), sections4–5.
2. Astral. [Working on projects](https://docs.astral.sh/uv/guides/projects/) and [Managing dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/).
3. [Project009 memo0002: Python notes](../../references/proj009Memo/memo0002_pythonNotes.md), sections2–3.
4. [Project009 memo0008: Qlib macOS environment](../../references/proj009Memo/memo0008_qlib_macos_venv.md), sections4–6.
