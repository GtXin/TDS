## 000 — Purpose
Decide on the folder structure based on the KWX and WX folders. Include the MAS decisions.
## 001 — KWX and WX: three main differences
### 1. Application versus research
KWX (`cc`) organizes a full application with a backend, frontend, APIs, and chart resources. WX (`proj009`) organizes a Python research workflow around market data, domain models, experiments, and charts.
### 2. Code, experiments, and outputs
Both keep reusable code in `src/` and checks in `tests/`. WX separates experiments, sample data, generated outputs, and reference cases; KWX groups research under `docs/research/` and provides specialized diagnostic scripts.
### 3. Documentation structure
KWX organizes documentation around algorithm explanations, design decisions, research, and development stages. WX uses a smaller structure of memos, phases, and backups.
## 002 — Decision: three-day feasibility sprint
Bring KWX and WX together for a three-day feasibility sprint to refactor the Chan theory algorithm and establish a foundation for future development. Use a Python backend and a static website, with algorithm code independent of both.
```text
TDS/
├── src/chanlab/
│   ├── algo/                  # Shared Chan theory calculations
│   ├── data/                  # Market records, loading, and validation code
│   └── api/                   # Backend endpoints calling the shared algorithm
├── web/                       # Static HTML, JavaScript, and CSS
├── tests/                     # Algorithm rules and regression cases
├── samples/                   # Small inputs for tests and demonstrations
├── experiments/               # Refactoring trials and implementation comparisons
├── artifacts/                 # Generated charts, reports, and comparison results
├── references/
│   ├── chan_theory/           # Original texts, translations, and explanations
│   ├── papers/                # External papers and technical articles
│   └── implementations/       # External code and implementation references
├── data/
│   ├── raw/                   # Original imported datasets
│   └── processed/             # Cleaned or converted datasets
└── docs/
    └── memo/                  # Our discussions and agreed decisions
```
The backend and experiments call the same algorithm code; the static website displays backend results. Agree on sample inputs and expected results before changing the algorithm.
References are what we study; data is what we calculate with; memos record our thinking; artifacts show our results. Keep original documents and raw data unchanged, and record source links, versions or download dates, and descriptions alongside them.
