# Memo019 sections002.b–d

The memo defines examples, five private helper contracts and pseudocode. It does
not implement a production Fenxing detector. Actual existing MergedKlineSeries
was used to verify the synthetic source groups; fractals were checked separately
with a finite arithmetic model and independent four-inequality review.

- `sections.md`: exact inserted sections.
- `build_examples.py`: synthetic numbers, finite witnesses and chart generator.
- `examples.json`: main/FIRST/LAST/tail results and check counts.
- `run_cached.py`: local plotting bootstrap using existing read-only cached wheels.
- `edit.json`, `protected_before.json`: backup, edit/image and protected-file hashes.
- `verify_document.py`, `verification.json`: actual scoped documentation checks.
- `algorithm-*.png`: final reviewed charts, copied identically into the memo folder.
- `history/`: initial figures retained before improving annotation margins.

From the repository root, in an existing environment with matplotlib:

```sh
PYTHONPATH=src python artifacts/mas/memo019-002b-d/build_examples.py
python3 artifacts/mas/memo019-002b-d/verify_document.py
git diff --check
```

The actual local run used `.venv/bin/python .../run_cached.py` with cached
matplotlib3.11.1. No project dependency or environment was installed/changed.
The default uv cache was not writable; the temporary offline cache lacked the
package. Read-only cached wheels resolved this. Initial font-cache warnings were
nonfatal. Final PNGs were inspected after correcting crowded bottom labels.

The 5,188 valid small sequences/14,166 windows and eight rejected corrupt-output
probes are finite design evidence, not a general proof or production test suite.
Task: `mas/tasks/20261109-memo019-002b-d.md`.

A concurrent task added the WX027 index row while this work ran. The first
protected-index check stopped on that change; `concurrent_changes.json` records
the exact observed delta/hash, and the final checker preserves and verifies it.
Seven other protected files and all bytes outside019002.b–d remain unchanged.

Latest002.b presentation starts from given processed input. Current scope checks:
`processed_input_verification.json`; text: `section002b_processed.md`; figure:
`draw_processed.py` / `fractal-window-example.png`. Render with
`.venv/bin/python .../run_cached.py draw_processed.py`. The earlier full-draft
figures/sections/checker remain historical evidence, not the current document.
