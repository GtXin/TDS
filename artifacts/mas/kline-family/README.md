# Memo013 Kline family

Implementation and verification evidence for [memo013](../../../docs/memo/memoWX_013_klineFamily.md).
The user released the memo011 handoff with “now 011 ready do 013”. Source UTC
labels and source-defined volume quantities are used unchanged. This release is
authorization to proceed, not independent verification of provider timestamp semantics.

## Interface

- `chanlab.algo.kline.Kline`: immutable metadata, UTC timestamp and OHLCV.
- `chanlab.algo.kline.KlineTSeries`: immutable ordered raw bars; integer indexing,
  tuple slicing, iteration, and validation on construction.
- `chanlab.data.kline_csv.read_kline_csv(path, context_path=None)`: returns
  `(series, context)` from either the existing 41-column master or a nine-column
  raw export. This is a raw-field projection, not ChanTable object interchange.
- `write_kline_csv(series, path, context_path=None, *, context=None)`: exports
  nine raw columns and optional key/value context. Nonempty context requires a
  context destination to prevent accidental provenance loss.

Raw export columns: `timestamp,symbol,period,source,open,high,low,close,volume`.
UTC timestamp syntax and float spelling may normalize on export; numeric values,
UTC instants, metadata and context must round trip. No volume rescaling or time
shifting is applied. Master feature columns are not exported or modified.

## Checks

From the repository root, use `.venv/bin/python artifacts/mas/kline-family/run_checks.py`
with `baseline`, `python_pro`, or `active`. The runner verifies both module paths,
runs the same acceptance tests, and saves output in `checks/`.

ChanTable object interchange, DataFrame conversion, plotting, indicators and feature
detection remain outside this implementation. Dataset/provider timestamp and volume
interpretation still depend on the retained source context.

Selected implementation: `python_pro/chanlab/`, identical to the two live source
modules. Active regression:165 passed; final same-suite comparison:baseline110
passed/4 failed, selected114 passed. Strict mypy, Ruff and Black pass; statement
coverage93%. See [comparison](comparison.md), [verification](verification.json)
and [the MAS task](../../../mas/tasks/20261108-memo013-execution.md).

The complete generated raw export and unchanged provenance sidecar are in
`roundtrip/`; [round-trip verification](roundtrip-verification.json) records their
checksums and the source/configuration preservation checks.
