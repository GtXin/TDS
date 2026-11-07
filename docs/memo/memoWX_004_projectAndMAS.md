## 000 — Purpose
Combine the project and MAS folder decisions from memos 002 and 003. Support the three-day Chan theory feasibility sprint and future development.
## 001 — Combined structure for now
```text
TDS/
├── src/chanlab/
│   ├── algo/                  # Shared Chan theory calculations
│   ├── data/                  # Market records, loading, and validation code
│   └── api/                   # Backend endpoints
├── web/                       # Static website
├── tests/                     # Rules and regression checks
├── samples/                   # Small test and demonstration inputs
├── experiments/               # Trials and comparisons
├── references/
│   ├── chan_theory/           # Original texts and explanations
│   ├── papers/                # External research
│   └── implementations/       # External code references
├── data/
│   ├── raw/                   # Original datasets
│   └── processed/             # Cleaned or converted datasets
├── mas/
│   ├── README.md              # Workflow overview
│   ├── roles/                 # Responsibilities, defined later
│   ├── skills/                # Procedures, defined later
│   ├── contracts.md           # Common task and result format
│   └── tasks/                 # Assignments and handoffs
├── artifacts/                 # Generated charts, reports, and results
│   └── mas/                   # MAS run outputs
└── docs/memo/                 # Discussions and decisions
```
## 002 — Essential boundaries
- The backend and experiments use the same algorithm code; the static website displays backend results.
- Preserve original references and raw data with source information; keep generated results in `artifacts/`.
- Keep MAS instructions and task records separate from application code; choose specific agents, roles, and skills later.
## 003 — Later: add Codex connections
Add these paths when ready, connecting them to the existing shared MAS core:
```text
TDS/
├── AGENTS.md                  # Entry point to the shared workflow
├── .codex/
│   ├── config.toml            # Runtime settings, when needed
│   └── agents/                # Native agent definitions
└── .agents/skills/            # Links to shared skills in mas/skills/
```
Claude can later use its own native connections to the same core. This memo records the combined plan; MAS implementation and agent selection remain deferred.
Sources: [002 — MAS](memoWX_002_MAS.md), [003 — Folder Decision](memoWX_003_folderDecision.md).
