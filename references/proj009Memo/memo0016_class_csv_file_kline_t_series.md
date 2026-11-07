# memo0016_class_csv_file_kline_t_series

[class design] [data interface]

## 0. Scope

> [purpose] Propose `CsvFileKlineTSeries` as the CSV read/write object for
> Project 009's early K-line experiments.
>
> It should read CSV rows into `Kline` objects, assemble them into a
> `KlineTSeries`, and write a `KlineTSeries` back to CSV.

> [naming] The user draft name was `csvFileKlineTSeries`.
>
> PEP 8 class naming changes this to `CsvFileKlineTSeries`. The matching module
> name should be `csv_file_kline_t_series.py`.

> [naming] The architecture concept is still **Data Interface**, but the Python
> package name should be `data_io`.
>
> `data_io` is shorter and more concrete than `data_interface`: this layer owns
> reading and writing external data formats.

> [boundary] This is not a domain class.
>
> `Kline` and `KlineTSeries` describe market facts. `CsvFileKlineTSeries`
> describes communication with one external file format.

> [decision] Keep read/write behavior outside `Kline` and `KlineTSeries`.
>
> This follows `memo0009`, `memo0010`, and the OOP-first file-interface rule in
> `AGENTS.md`.

## 1. Class Proposal

### 1.a Meaning

> [concept] `CsvFileKlineTSeries` means:
>
> A CSV file interface whose rows map to `Kline` and whose whole file maps to
> `KlineTSeries`.

It answers:

> How does Project 009 communicate between a CSV file and its K-line time
> series object?

### 1.b Layer And Location

> [layer] Target layer:
>
> ```text
> src/tradinglab/data_io/
> ```

> [path] Current source file:
>
> ```text
> src/tradinglab/data_io/csv_file_kline_t_series.py
> ```

> [result] Promoted to source on 2026-09-01 through `memo0018`.

> [path] Previous experiment file:
>
> ```text
> experiments/data_structures/generic/csv_file_kline_t_series.py
> ```

> [path] Current test:
>
> ```text
> tests/data_io/test_csv_file_kline_t_series.py
> ```

> [path] Previous experiment test:
>
> ```text
> experiments/data_structures/generic/test_csv_file_kline_t_series.py
> ```

> [decision] Implement as experiment first, then promote only after tests.
>
> The first implementation has now passed that promotion gate.

### 1.c Responsibility

> [decision] `CsvFileKlineTSeries` owns CSV format details.
>
> It owns:
>
> - file path;
> - encoding;
> - CSV header contract;
> - timestamp parsing and formatting;
> - row-to-`Kline` conversion;
> - `KlineTSeries`-to-row conversion;
> - row number in error messages;
> - safe overwrite behavior on write.

> [boundary] It does not own:
>
> - single-candle OHLCV invariants;
> - sequence ordering rules;
> - Chanlun structure calculation;
> - Qlib conversion;
> - DuckDB or Parquet storage;
> - chart rendering;
> - strategy logic;
> - data repair.

## 2. Members

### 2.a Core Members

> [proposal] Start with a small frozen dataclass:
>
> ```python
> @dataclass(frozen=True)
> class CsvFileKlineTSeries:
>     path: Path
>     encoding: str = "utf-8"
>     default_source: str = "csv_file"
>     timestamp_column: str = "timestamp"
>     timestamp_input: str = "auto"
>     timestamp_output: str = "iso"
>     strict_columns: bool = False
> ```

> [proposal] Use class constants for the stable CSV contract:
>
> ```python
> REQUIRED_COLUMNS = (
>     "symbol",
>     "period",
>     "timestamp",
>     "open",
>     "high",
>     "low",
>     "close",
>     "volume",
> )
> PROJECT_OUTPUT_COLUMNS = (
>     "symbol",
>     "period",
>     "source",
>     "timestamp",
>     "open",
>     "high",
>     "low",
>     "close",
>     "volume",
> )
> KNOWN_HELPER_COLUMNS = (
>     "datetime_utc",
>     "datetime_asia_shanghai",
> )
> ```

> [member] `path`
>
> The CSV file location. The class represents this file, not the whole data
> store.

> [member] `encoding`
>
> Default to `utf-8`.

> [member] `default_source`
>
> Used when a CSV row has no `source` column. This keeps Project 009's
> point-level provenance rule without requiring external CSV files to already
> know Project 009's schema.

> [member] `timestamp_column`
>
> Default to `timestamp`. The preserved `records/cc` CSV uses this as Unix
> seconds. The helper columns `datetime_utc` and `datetime_asia_shanghai` are
> evidence columns, not the canonical timestamp input.

> [member] `timestamp_input`
>
> Default to `auto`: accept ISO datetime strings and Unix seconds. This covers
> both the local Project 009 sample and the KWX/CC website fixture shape.

> [member] `timestamp_output`
>
> Default to `iso`: write timestamps as ISO 8601 strings for readable project
> CSV output. Use a later option such as `unix_seconds` only when exact KWX/CC
> fixture compatibility is needed.

> [member] `strict_columns`
>
> Default to `False`: accept extra columns such as `datetime_utc` and
> `datetime_asia_shanghai` from preserved reference records. Required OHLCV
> columns are still mandatory.

> [decision] Read extra columns, but do not preserve them in `Kline`.
>
> `CsvFileKlineTSeries` should ignore known helper datetime columns after
> parsing. If a future task needs byte-for-byte CSV preservation, that is a
> separate record/archive concern, not the first domain read/write class.

### 2.b Required Columns

> [decision] Minimum readable CSV columns:
>
> ```text
> symbol,period,timestamp,open,high,low,close,volume
> ```

> [decision] Optional readable column:
>
> ```text
> source
> ```

> [decision] Default writable Project 009 columns:
>
> ```text
> symbol,period,source,timestamp,open,high,low,close,volume
> ```

> [source] The KWX/CC page uses the eight-column fixture contract. Project 009
> adds `source` because `memo0009` decided each `Kline` should carry point-level
> provenance.

> [evidence] The preserved local record CSV uses ten columns:
>
> ```text
> symbol,period,timestamp,datetime_utc,datetime_asia_shanghai,open,high,low,close,volume
> ```
>
> `timestamp` is still the canonical machine field. The two datetime columns
> are readable helper fields and should not force a different domain model.

## 3. Methods

### 3.a Public Methods

> [proposal] Public API:
>
> ```python
> def read(self) -> KlineTSeries: ...
> def write(self, series: KlineTSeries) -> None: ...
> def exists(self) -> bool: ...
> ```

> [method] `read()`
>
> Reads the CSV file, converts every row into `Kline`, and returns one
> `KlineTSeries`.

> [method] `write(series)`
>
> Writes one `KlineTSeries` to the CSV file using the Project 009 output
> columns. Prefer overwrite semantics first; append mode should be a separate
> later decision.

> [method] `exists()`
>
> Small convenience method for caller checks. It does not create the file.

### 3.b Internal Methods

> [proposal] Internal helpers should stay inside the class:
>
> ```python
> def _read_rows(self) -> tuple[dict[str, str], ...]: ...
> def _row_to_kline(self, row: dict[str, str], row_number: int) -> Kline: ...
> def _kline_to_row(self, kline: Kline) -> dict[str, str]: ...
> def _parse_timestamp(self, value: str, row_number: int) -> datetime: ...
> def _format_timestamp(self, value: datetime) -> str: ...
> def _validate_header(self, columns: tuple[str, ...]) -> None: ...
> ```

> [style] Keep helpers as methods, not module-level functions, because the
> object owns the file contract and configuration.

## 4. Workflow

### 4.a Read Flow

> [workflow] CSV file to domain series
>
> - Step 1: open `path`.
>   - System: filesystem.
>   - Path: `CsvFileKlineTSeries.path`.
>   - Verify: file exists and can be decoded as `encoding`.
>
> - Step 2: validate header.
>   - System: CSV schema.
>   - Path: header row.
>   - Verify: required columns exist; extra columns are accepted only when
>     `strict_columns=False`.
>
> - Step 3: convert rows.
>   - System: data interface.
>   - Path: each CSV row.
>   - Verify: each row becomes one `Kline`.
>
> - Step 4: assemble series.
>   - System: domain.
>   - Path: `KlineTSeries`.
>   - Verify: timestamp order, duplicate rejection, symbol consistency, and
>     period consistency are enforced by `KlineTSeries`.

### 4.b Write Flow

> [workflow] Domain series to CSV file
>
> - Step 1: receive `KlineTSeries`.
>   - System: domain object.
>   - Path: caller-provided series.
>   - Verify: object type is correct.
>
> - Step 2: convert each `Kline` into one row.
>   - System: data interface.
>   - Path: in-memory row dictionaries.
>   - Verify: output columns are stable and ordered.
>
> - Step 3: write to a temporary file first.
>   - System: filesystem.
>   - Path: same folder as target CSV.
>   - Verify: full CSV is written before replacing the target.
>
> - Step 4: replace the target file.
>   - System: filesystem.
>   - Path: `CsvFileKlineTSeries.path`.
>   - Verify: re-reading the file returns an equivalent `KlineTSeries`.

### 4.c Manifest Flow

> [boundary] Manifest JSON is outside `CsvFileKlineTSeries`.
>
> `CsvFileKlineTSeries.read()` should not open the JSON sidecar. It should read
> only the CSV file named by `path`.

> [workflow] Future record-level verification can wrap the CSV class:
>
> - Step 1: `KlineTSeriesManifest` reads the JSON sidecar.
>   - System: record metadata.
>   - Path: `records/.../*-manifest.json`.
>   - Verify: schema version, expected CSV path, row count, SHA-256, columns,
>     symbol, period, time range, and related SVG hash.
>
> - Step 2: `CsvFileKlineTSeries` reads the CSV.
>   - System: data IO.
>   - Path: `records/.../*.csv`.
>   - Verify: returns `KlineTSeries`.
>
> - Step 3: `KlineTSeriesRecord` compares both.
>   - System: reference record.
>   - Path: CSV plus manifest, optionally SVG.
>   - Verify: CSV checksum and series facts match the manifest.

## 5. Manifest Boundary

### 5.a Current Decision

> [decision] Do not add JSON support to `CsvFileKlineTSeries`.
>
> The class should be deliberately narrow:
>
> ```text
> CsvFileKlineTSeries
>   CSV <-> KlineTSeries
> ```

> [reason] The JSON sidecar is record evidence. It explains and verifies a CSV
> file, but it is not the CSV row format itself.

### 5.b Future Classes

> [proposal] Add these only when record-level verification becomes active:
>
> ```text
> KlineTSeriesManifest
>   JSON manifest <-> manifest object
>
> KlineTSeriesRecord
>   CSV + manifest JSON + optional SVG -> verified reference record
> ```

> [placement] If implemented, these source classes can live under
> `src/tradinglab/data_io/` because they still communicate with external files.
> The preserved files themselves remain under `records/`.

## 6. Failure Rules

### 6.a No Repair

> [decision] This class must stop on malformed data.
>
> It should not sort rows, remove duplicates, fill missing prices, infer period,
> resample bars, or silently drop bad rows.

> [reason] CSV read/write is the evidence gate before Chanlun or strategy work.
> Repair would hide the input condition that generated later structures.

### 6.b Error Shape

> [proposal] First implementation can raise `ValueError` with row numbers.
>
> Future `src` promotion can introduce a project exception if callers need
> structured recovery.

> [example] Useful error messages:
>
> ```text
> row 17: missing required column close
> row 23: timestamp is not ISO datetime or Unix seconds
> row 44: high must be greater than or equal to close
> ```

## 7. Sample Use

### 7.a Read

> [example] Read a small Project 009 sample:
>
> ```python
> from pathlib import Path
>
> csv_file = CsvFileKlineTSeries(
>     Path("data_samples/kline/kline_15m_minimal.csv"),
>     default_source="data_samples_kline",
> )
> series = csv_file.read()
>
> print(series.symbol)
> print(series.period)
> print(series.count)
> ```

### 7.b Read Preserved Record CSV

> [example] Read the preserved CC record CSV without reading the JSON manifest:
>
> ```python
> from pathlib import Path
>
> csv_file = CsvFileKlineTSeries(
>     Path("records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv"),
>     default_source="cc_record",
> )
> series = csv_file.read()
>
> assert series.symbol == "dce:KQ.m@m"
> assert series.period == "15m"
> assert series.count == 10060
> ```

> [note] This proves CSV compatibility only. It does not prove the CSV matches
> the sidecar manifest hash or the SVG output.

### 7.c Write

> [example] Write a series back to CSV:
>
> ```python
> output_file = CsvFileKlineTSeries(Path("artifacts/tmp/kline_t_series.csv"))
> output_file.write(series)
> reread = output_file.read()
>
> assert reread.klines == series.klines
> ```

> [note] Use a temporary test folder for write verification. Do not write large
> market data into `docs/memo/`.

## 8. Verification

### 8.a Minimum Checks

> [verification] Required checks before implementation is considered useful:
>
> - read `data_samples/kline/kline_15m_minimal.csv`;
> - read a CSV with the KWX/CC eight-column shape;
> - read a CSV with extra helper datetime columns;
> - read the preserved record CSV with ten columns and return `10060` K-lines;
> - fill missing `source` from `default_source`;
> - reject missing required columns;
> - reject bad timestamp text;
> - reject bad OHLC rows through `Kline`;
> - reject duplicate or descending timestamps through `KlineTSeries`;
> - write a series to a temporary CSV;
> - read the written CSV and compare it with the original series.

### 8.b Confirmation Command

> [example] Current source test command:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.data_io.test_csv_file_kline_t_series
> ```

## 9. Evidence

### 9.a Source Notes

> [source] `docs/memo/memo0009_class_kline.md`
>
> `Kline` owns one complete OHLCV candle/bar and should not read or write files.

> [source] `docs/memo/memo0010_class_kline_t_series.md`
>
> `KlineTSeries` owns ordered sequence invariants and should not read or write
> files.

> [source] `docs/memo/memo0012_cc_csv_to_zoushi_reference.md`
>
> The KWX/CC website uses an eight-column CSV fixture contract and strict
> no-repair input validation.

> [source] `docs/memo/memo0015_oop_trading_architecture.md`
>
> The approved architecture spine places file communication in `Data Interface`,
> while domain market facts stay in `src/tradinglab/domain/`.

> [source] `AGENTS.md`
>
> OOP-first read/write conversion should be modeled as explicit file/interface
> classes, while domain classes should not know CSV, Parquet, DuckDB, Qlib, or
> vendor formats exist.

### 9.b Local Record Inspection

> [execution] Inspected:
>
> ```text
> records/cc/kline-to-zoushi-001/dce-kqm-m-15m.csv
> records/cc/kline-to-zoushi-001/dce-kqm-m-15m-manifest.json
> ```

> [evidence] Observed:
>
> - CSV columns match the manifest column list.
> - CSV rows: `10060`.
> - Manifest rows: `10060`.
> - CSV SHA-256 matches manifest `csv_sha256`.
> - Unique symbol: `dce:KQ.m@m`.
> - Unique period: `15m`.
> - Timestamps are strictly increasing.
> - First row: `1730094300`, `2024-10-28T05:45:00Z`,
>   `2024-10-28T13:45:00+08:00`.
> - Last row: `1787121900`, `2026-08-19T06:45:00Z`,
>   `2026-08-19T14:45:00+08:00`.

> [project consequence] `CsvFileKlineTSeries` must be permissive enough to read
> the preserved ten-column CSV, but it should not own manifest validation.

## 10. Project Implication

### 10.a Immediate Next Step

> [project consequence] The accepted implementation now lives in source:
>
> ```text
> src/tradinglab/data_io/csv_file_kline_t_series.py
> tests/data_io/test_csv_file_kline_t_series.py
> ```

> [project consequence] Future file-format changes should still be tried in a
> focused experiment first if they change the class contract.

### 10.b Class Boundary

> [decision] Keep this collaboration shape:
>
> ```text
> CsvFileKlineTSeries
>   -> creates Kline
>   -> returns KlineTSeries
>
> Kline
>   -> validates one candle/bar
>
> KlineTSeries
>   -> validates sequence order and consistency
> ```

> [decision] Keep this record-level collaboration for later:
>
> ```text
> KlineTSeriesManifest
>   -> reads JSON sidecar metadata
>
> KlineTSeriesRecord
>   -> verifies CSV + JSON + optional SVG together
> ```

## 11. Open Questions

### 11.a Naming

> [open] If the class name feels awkward during implementation, consider
> `KlineTSeriesCsvFile`.
>
> For now, keep `CsvFileKlineTSeries` because it follows the user's requested
> concept and PEP 8 class naming.

### 11.b Timestamp Output

> [open] Decide later whether Project 009's canonical CSV timestamp should be
> ISO 8601 or Unix seconds.
>
> First recommendation: read both, write ISO by default, and add a
> `unix_seconds` output option only when exact KWX/CC compatibility becomes the
> active task.

### 11.c Record Round Trip

> [open] Decide later whether Project 009 needs byte-for-byte record CSV
> preservation.
>
> First recommendation: no. The first class should preserve semantic
> `KlineTSeries` data, not every helper column from a reference archive.

## 12. Implementation And Test Log

### 12.a Implemented Experiment

> [execution] Original experiment files:
>
> ```text
> experiments/data_structures/generic/csv_file_kline_t_series.py
> experiments/data_structures/generic/test_csv_file_kline_t_series.py
> ```

> [execution] Current source files after promotion:
>
> ```text
> src/tradinglab/data_io/csv_file_kline_t_series.py
> tests/data_io/test_csv_file_kline_t_series.py
> ```

> [execution] Updated support documentation:
>
> ```text
> experiments/data_structures/generic/README.md
> docs/classDesign.md
> ```

> [execution] Implemented public API:
>
> - `exists()`
> - `read()`
> - `write(series: KlineTSeries)`

> [execution] Implemented CSV behavior:
>
> - accepts ISO datetime strings and Unix seconds;
> - parses Unix seconds as UTC-aware `datetime`;
> - fills missing `source` from `default_source`;
> - accepts helper columns when `strict_columns=False`;
> - rejects helper/unknown columns when `strict_columns=True`;
> - ignores `datetime_utc` and `datetime_asia_shanghai` after parsing;
> - writes stable Project 009 columns:
>   `symbol,period,source,timestamp,open,high,low,close,volume`.

> [boundary] JSON sidecar support was intentionally not implemented.
>
> Manifest JSON remains future `KlineTSeriesManifest` /
> `KlineTSeriesRecord` work.

### 12.b Test Result

> [execution] Historical focused experiment test command:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_csv_file_kline_t_series
> ```

> [execution] Focused test output:
>
> ```text
> Ran 10 tests in 0.030s
> OK
> [run] CsvFileKlineTSeries tests: read CSV shapes, reject bad rows, and write/read round trip
> ```

> [execution] Related experiment test command:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_kline experiments.data_structures.generic.test_kline_t_series experiments.data_structures.generic.test_csv_file_kline_t_series
> ```

> [execution] Related experiment test output:
>
> ```text
> Ran 27 tests in 0.033s
> OK
> ```

> [execution] Source promotion test command on 2026-09-01:
>
> ```zsh
> PYTHONPATH=src .venv/bin/python -m unittest tests.data_io.test_csv_file_kline_t_series
> ```
>
> [execution] Source promotion result:
>
> ```text
> Ran 10 tests OK
> ```

### 12.c Current Limitations

> [note] This implementation is now promoted source.
>
> It does not yet include manifest JSON validation or byte-for-byte CSV
> preservation.

> [note] Write/read round trip preserves semantic `KlineTSeries` data.
>
> It does not preserve ignored helper datetime columns or byte-for-byte record
> CSV layout.

### 12.d Sample Data Relocation

> [execution] Stable sample data was moved to a shape-based folder:
>
> ```text
> data_samples/README.txt
>   -> data_samples/README.md
>
> data_samples/ke/
>   -> data_samples/kline/
>
> data_samples/ke/kline_15m_sample.csv
>   -> data_samples/kline/kline_15m_minimal.csv
> ```

> [decision] `data_samples/kline/` is the stable checked-in fixture location
> for small K-line/OHLCV examples.

> [decision] Full source-preserving cases stay under `records/`, for example:
>
> ```text
> records/cc/kline-to-zoushi-001/
> ```

> [execution] Updated active references in sample READMEs, repo-structure docs,
> memo0015, memo0016, distilled memory, the 7.2 milestone note, and the
> `CsvFileKlineTSeries` tests.

> [verification] Reran related experiment tests after the relocation:
>
> ```zsh
> .venv/bin/python -m unittest experiments.data_structures.generic.test_kline experiments.data_structures.generic.test_kline_t_series experiments.data_structures.generic.test_csv_file_kline_t_series
> ```

> [verification] Output:
>
> ```text
> Ran 27 tests in 0.033s
> OK
> ```
