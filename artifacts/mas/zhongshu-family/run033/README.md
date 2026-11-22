# Memo033 completed run — 2026-11-18

Authority: memo022 current001/002, class contract009, exact031 completed XD sources. No protected specification/raw edits. See protected-hashes.json and final-audit.json.

## Evidence
- regression-final.txt: 522 passed; coverage-final.txt: five Zhongshu modules99% total. mypy-final.txt, black-final.txt, ruff-final.txt: passed.
- comparison.json: 404 separate-process complete022 baseline comparisons, no exclusions. Baseline is existing022 frozen code; Python Pro already read before freeze, no causal skill claim.
- full-validation.json, final-audit.json: all four full real modes, complete022 parity and original031 contexts/table hash parity. Only historical snapshot_id text differs in source projection; actual fields all checked.
- monte-carlo.json / random-inputs.jsonl.gz: 10000 complete raw sequences, four modes, no failures; short inputs yield only open structures.
- long-monte-carlo.json / long-random-inputs.jsonl.gz: 64 long sequences, four modes,470 centers including268closed.
- exhaustive.json: 2852 finite paths,2866centers,276zeroheight,3066crossings independently checked.
- timing.json: 12 real FX-prefix/mode cases×3 fresh upstream runs; warm input files, no result cache; scanner vs full validated factory vs end-to-end separated. Cumulative process maxRSS includes setup/reference, not case increments.
- charts/index.html:228 PNG/HTML/figure JSON,57 comparisons,38 contact sheets; visual-review.json records exact visual QA scope. Native coordinate audit in chart-audit.json and final-audit.json. Static candlesticks use thick open/close lines; HTML retains native figure. Dense labels can overlap.
- usage.py (experiments directory), usage.txt/html: runnable public API example.

## Reproduction
Run from repository root with PYTHONPATH=src:. and .venv/bin/python:

```sh
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/compare.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/validate.py mc
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/validate.py real
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/validate.py timing
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/long_mc.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/exhaustive.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/charts.py
PYTHONPATH=src:. .venv/bin/python experiments/zhongshu033/audit.py
```

Static rendering: experiments/zhongshu033/render.py requires Matplotlib/Pillow; this run used /Users/coder/Public/EngineGit/proj009/.venv/bin/python with MPLCONFIGDIR=/private/tmp/tds033-mpl. Type/style/coverage tooling was available via /private/tmp/tds022-tools. No dependency files changed. See scripts for fixed seeds, source paths and oracle linkage to experiments/zhongshu022/reference.py.

Core scanner O(N); current per-center trace mapping O(CN), plus complete upstream replay cost. Default full weak/weak Z0 retains022 left_crossing_missing; no invented rectangle. Fixed snapshot segment level only; no recursive-level or permanent streaming-confirmation claim.
