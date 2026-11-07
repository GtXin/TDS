# TDS — Three-Day Sprint

A feasibility project bringing KWX and WX together to refactor the Chan theory algorithm and establish a foundation for future development. The planned application has a Python backend and a static website.

Current state: folder structure and design memos; implementation has not started.

## Folder structure

```text
TDS/
├── src/chanlab/
│   ├── algo/                  # Reusable Chan theory calculations
│   ├── data/                  # Market records, loading, and validation code
│   └── api/                   # Backend endpoints that call the algorithm
├── web/                       # Static HTML, JavaScript, and CSS
├── tests/                     # Algorithm rules and regression cases
├── samples/                   # Small inputs for tests and demonstrations
├── experiments/               # Trials and comparisons during the refactor
├── artifacts/                 # Generated charts, reports, and results
├── references/
│   ├── chan_theory/           # Original texts, translations, and explanations
│   ├── papers/                # External papers and technical articles
│   └── implementations/       # External code and implementation references
├── data/
│   ├── raw/                   # Original imported datasets
│   └── processed/             # Cleaned or converted datasets
└── docs/
    └── memo/                  # Discussions and agreed decisions
```

## Where things belong

- **Shared code:** keep algorithm logic independent of the API and website. Backend endpoints and experiments should call the same implementation in `src/chanlab/algo/`.
- **Inputs and outputs:** put external knowledge in `references/`, datasets in `data/`, small reproducible examples in `samples/`, and generated results in `artifacts/`. Preserve original documents and raw data, recording their source and version or download date alongside them.
- **Working notes:** develop ideas and record decisions in `docs/memo/`. Agree on sample inputs and expected results before changing the algorithm.

The reasoning behind this layout is recorded in [memo 003 — Folder Decision](docs/memo/memoWX_003_folderDecision.md).
