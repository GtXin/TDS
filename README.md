# TDS — Three-Day Sprint

A feasibility project bringing KWX and WX together to refactor the Chan theory algorithm and establish a foundation for future development. The planned application has a Python backend and a static website.

Current state: project scaffold and shared MAS starter documents are in place. Application code, agent definitions, and tool-specific integrations are deferred.

## Folder structure

```text
TDS/
├── src/chanlab/
│   ├── algo/                  # Shared Chan theory calculations
│   ├── data/                  # Market records, loading, and validation code
│   └── api/                   # Backend endpoints that call the algorithm
├── web/                       # Static HTML, JavaScript, and CSS
├── tests/                     # Algorithm rules and regression cases
├── samples/                   # Small inputs for tests and demonstrations
├── experiments/               # Trials and comparisons during the refactor
├── references/
│   ├── chan_theory/           # Original texts, translations, and explanations
│   ├── papers/                # External papers and technical articles
│   └── implementations/       # External code and implementation references
├── data/
│   ├── raw/                   # Original imported datasets
│   └── processed/             # Cleaned or converted datasets
├── mas/
│   ├── README.md              # Shared workflow overview
│   ├── roles/                 # Responsibilities, defined later
│   ├── skills/                # Reusable procedures, defined later
│   ├── contracts.md           # Common task and result format
│   └── tasks/                 # Assignments and handoffs
├── artifacts/                 # Generated charts, reports, and results
│   └── mas/                   # MAS run outputs
└── docs/
    └── memo/                  # Discussions and agreed decisions
```

## Where things belong

- **Shared code:** keep algorithm logic independent of the API and website. Backend endpoints and experiments should call the same implementation in `src/chanlab/algo/`.
- **Inputs and outputs:** put external knowledge in `references/`, datasets in `data/`, small reproducible examples in `samples/`, and generated results in `artifacts/`. Preserve original documents and raw data, recording their source and version or download date alongside them.
- **Working notes:** develop ideas and record decisions in `docs/memo/`. Agree on sample inputs and expected results before changing the algorithm.
- **MAS:** keep shared workflow, future roles and skills, and task records in `mas/`; generated run outputs belong in `artifacts/mas/`. Choose specific agents and native tool connections later.

## Start here

- [Memo 004 — Combined project and MAS structure](docs/memo/memoWX_004_projectAndMAS.md)
- [Shared MAS workflow](mas/README.md)
- [Task and result format](mas/contracts.md)

Empty folders contain `.gitkeep` placeholders so the scaffold can be versioned. Codex and Claude configuration will be added when integration is chosen.
