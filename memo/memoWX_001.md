# Project 009 folder structure

## 000 — Background

Project 009 is a trading research project that starts with a small working loop: read CSV/OHLCV data, represent it as Kline records, validate it, and produce reproducible charts. Its folders separate reusable code, research trials, documentation, sample inputs, and generated outputs so that each new file has a clear home. This memo describes the working folder structure checked on November 7, 2026; new folders should be added only when the active milestone needs them.

## 001 — Folder tree and summary

```text
proj009/
├── src/tradinglab/              # Reusable Python code for the project.
│   ├── data_io/                # Reads and validates market data.
│   ├── domain/                 # Defines core records such as Kline.
│   ├── integrations/qlib/      # Connects the project with Qlib.
│   └── visualization/          # Creates charts and drawing overlays.
├── tests/                      # Checks that the project code works correctly.
│   ├── data_io/                # Tests data reading and validation.
│   ├── domain/                 # Tests core records and their behavior.
│   ├── integrations/           # Tests connections with external libraries.
│   └── visualization/          # Tests chart and overlay generation.
├── experiments/                # Holds research trials and exploratory code.
│   ├── chan_theory/            # Investigates Chan theory methods.
│   ├── data_structures/        # Tries different ways to represent data.
│   └── visualization_trials/   # Explores charting approaches.
├── docs/                       # Holds project documentation and plans.
│   ├── memo/                   # Stores ideas and focused notes.
│   ├── phases/                 # Describes stages and milestones.
│   └── backups/                # Keeps saved document copies.
├── data_samples/kline/         # Provides small market-data samples for tests and examples.
├── artifacts/                  # Stores generated outputs.
│   ├── charts/                 # Stores generated charts.
│   └── experiments/            # Stores experiment outputs.
├── configs/                    # Holds reproducible project settings.
├── records/cc/                 # Preserves external reference cases with their context.
├── tools/                      # Contains developer helper scripts.
└── wonderland/                 # Is currently empty with no established purpose.
```

The tree shows the working project folders. Local environments, Git metadata, editor settings, and Python caches are omitted to keep the project structure easy to read.

## 002 — Detailed explanations

### `proj009/`

This is the project root, where the code, research, documentation, and supporting files come together. Start with `README.md` for orientation, `plan.md` for the active roadmap, and `AGENTS.md` for agent instructions.

### `src/`

This folder holds importable project source code. Keeping it in one place gives tests and helper scripts a common implementation to use.

### `src/tradinglab/`

This is the main Python package for reusable project behavior. Code that becomes stable and useful across experiments belongs here.

### `src/tradinglab/data_io/`

This folder handles reading market data and checking that inputs are usable. It keeps file formats and input handling separate from the calculations that consume the data.

### `src/tradinglab/domain/`

“Domain” means the subject the software works with: in this project, market records and trading research concepts. This folder defines those concepts in Python, including their data, their meaning, and the rules that make them valid. It gives data readers, experiments, and charts a shared vocabulary.

The current folder contains two main classes:

- **`Kline` — one market candle.** It stores the symbol, period, source, timestamp, open, high, low, close, and volume. It checks rules such as the high being at least as large as the open and close, the low being at most as small as them, and volume being nonnegative. It also provides candle properties such as body size, upper and lower shadows, and bullish or bearish direction.
- **`KlineTSeries` — an ordered collection of candles.** It requires a nonempty collection with one symbol, one period, and strictly increasing timestamps. It exposes information such as the start and end timestamps, candle count, closing prices, and data sources; mixed sources are allowed and can be identified.

For example, suppose a CSV row says a candle opened at 100, reached a high of 110 and a low of 95, and closed at 105. The reader in `data_io/` interprets the CSV columns and creates a `Kline`; the domain object checks the candle's rules and can report a body size of 5. If the row instead claims a high of 102 with a close of 105, constructing the `Kline` rejects the inconsistent values.

A typical flow is:

```text
CSV file → data_io reads rows → domain objects represent valid candles → visualization draws them
```

The domain classes do not need to know the CSV filename, the charting library, or Qlib's data format. File reading belongs in `data_io/`, external-library conversion belongs in `integrations/`, and chart rendering belongs in `visualization/`. The domain owns rules inherent to the concepts themselves, while the surrounding folders handle how those concepts enter and leave the program.

When deciding whether new code belongs here, ask: “Does this define a shared trading concept or a rule that should hold wherever that concept is used?” If yes, `domain/` is a likely home; if it only supports one experimental approach, keep it in that experiment until the project needs a shared definition.

### `src/tradinglab/integrations/`

This folder holds code that connects the project with external libraries or systems. These adapters translate between external interfaces and the project's own records and workflows.

### `src/tradinglab/integrations/qlib/`

This folder contains the Qlib-specific connection code. Keeping that code together makes Qlib assumptions easier to find and change.

### `src/tradinglab/visualization/`

This folder turns project data into charts and drawing overlays. Reusable chart behavior belongs here so that tools and experiments can produce consistent visual results.

### `tests/`

This folder contains automated checks for project behavior. Small, reproducible cases help reveal regressions when the implementation changes.

### `tests/data_io/`

These tests check data reading and validation. They help establish how valid inputs should be interpreted and how invalid inputs should be handled.

### `tests/domain/`

These tests check core records and their behavior. They protect assumptions that other parts of the project rely on.

### `tests/integrations/`

These tests check the project's connections with external libraries. They help catch mismatches in data conversion and interface expectations.

### `tests/visualization/`

These tests check chart and overlay generation. They help verify that changes preserve the expected visual data and output behavior.

### `experiments/`

This folder holds exploratory work organized around research questions. Once an approach becomes stable and reusable, its shared logic can move into `src/tradinglab/`.

### `experiments/chan_theory/`

This folder groups investigations related to Chan theory. Keeping the trials together makes their assumptions, inputs, and results easier to compare.

### `experiments/data_structures/`

This folder is for trying different ways to represent and organize data. It provides a place to evaluate a structure before adopting it as a shared project concept.

### `experiments/visualization_trials/`

This folder is for exploring chart layouts and drawing approaches. Successful approaches can later become reusable visualization code.

### `docs/`

This folder explains the project's design, plans, and progress. It gives contributors context for understanding the code and deciding what to work on next.

### `docs/memo/`

This folder stores focused ideas, discussion notes, and planning context. These notes preserve the reasoning behind a proposal without requiring immediate implementation.

### `docs/phases/`

This folder describes project stages and milestones. It turns the broader roadmap into concrete scopes and deliverables.

### `docs/backups/`

This folder keeps saved document copies for reference. Consult the active document when deciding what guidance currently applies.

### `data_samples/`

This folder contains small sample inputs that can be shared with the repository. They support reproducible tests and examples without requiring a full market dataset.

### `data_samples/kline/`

This folder groups samples used for Kline-related work. Shared samples let data readers, validation checks, and chart examples work from consistent inputs.

### `artifacts/`

This folder stores outputs produced by project commands and research runs. Keeping generated files here separates results from the code and inputs that produced them.

### `artifacts/charts/`

This folder stores generated charts for inspection and comparison. The producing script and its inputs should make it possible to recreate a chart when needed.

### `artifacts/experiments/`

This folder stores outputs from experimental runs. Keeping results separate from experiment code makes it easier to distinguish an investigation from its generated files.

### `configs/`

This folder holds settings that affect reproducible runs. Use it for parameters needed by existing workflows, and keep credentials and secrets elsewhere.

### `records/`

This folder preserves external reference cases with their supporting context. A complete case can keep its source material, helper scripts, outputs, and explanation together.

### `records/cc/`

This folder holds reference cases associated with the `cc` repository. Treat them as reference material to study and adapt through a planned milestone.

### `tools/`

This folder contains helper scripts for development and local operations. Scripts should call reusable source code when possible so that core behavior has one implementation.

### `wonderland/`

This folder was empty when the structure was checked. Its purpose has not been established, so it does not yet provide guidance on where to place new work.
