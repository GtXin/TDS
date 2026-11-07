## 000 — Purpose
Combine the project structure, shared MAS core, and Codex connection now. Support the three-day Chan theory feasibility sprint and future development.
## 001 — Current combined structure
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
│   ├── roles/                 # Shared responsibilities, chosen through experiments
│   ├── skills/                # Shared procedures, chosen through experiments
│   ├── contracts.md           # Common task and result format
│   └── tasks/                 # Assignments and handoffs
├── AGENTS.md                  # Codex entry point to the shared workflow
├── .codex/
│   ├── config.toml            # Subagent support enabled
│   └── agents/                # Native definitions; no agents chosen yet
├── .agents/
│   └── skills → ../mas/skills  # Shared skill discovery
├── artifacts/                 # Generated charts, reports, and results
│   └── mas/                   # MAS run outputs
└── docs/memo/                 # Discussions and decisions
```
## 002 — Essential boundaries
- The backend and experiments use the same algorithm code; the static website displays backend results.
- Preserve original references and raw data with source information; keep generated results in `artifacts/`.
- Keep MAS instructions and task records separate from application code; choose specific agents, roles, and skills through experiments.
## 003 — Codex connected now
`AGENTS.md` directs Codex to the shared workflow and contracts; `.codex/config.toml` enables subagent support without selecting models or changing permissions. `.agents/skills` links to `mas/skills`, while `.codex/agents/` remains available for native definitions when agents are chosen.
The project scaffold, shared MAS core, and Codex connection are set up together. Specific agents and skills remain unselected, and the core stays portable to other runtimes.
Sources: [002 — MAS](memoWX_002_MAS.md), [003 — Folder Decision](memoWX_003_folderDecision.md).
