# Python Pro OOP trial

This isolated sample implements memo012 section003. It does not implement or
change TDS's Chan classes.

- **Skill used:** [installed Python Pro](../../../mas/skills/python-pro/SKILL.md),
  version 1.1.0, upstream commit `078a25cc5bfd8011459be7b91d004e900c1d02d3`.
- **Guidance read before coding:** `SKILL.md`, `references/type-system.md`,
  `references/standard-library.md` and `references/testing.md`.
- **Project overrides:** existing Python 3.11/uv/pytest/Ruff only. No dependencies,
  environment settings or source classes changed; Ruff ran without auto-fixes.

## Class responsibilities

1. `PriceBar` owns one bar's validity. A frozen, slotted dataclass prevents normal
   field reassignment. Construction rejects naive timestamps, nonzero UTC offsets,
   nonfinite prices and opening/closing prices outside the inclusive low/high
   interval. A zero UTC offset is accepted; timestamps are not silently converted.
2. `PriceSeries` composes already validated bars. It snapshots any supplied
   iterable into a tuple, preserves the exact bar objects and order, and rejects
   non-bar items or duplicate/decreasing timestamps. Empty input is valid.
   Freezing the container prevents subsequent mutation from breaking its order.

No inheritance hierarchy, asynchronous work or external library is needed for
these two responsibilities. Type hints describe both public interfaces.

## Actual checks

Run from the TDS root:

```zsh
env UV_CACHE_DIR=/private/tmp/tds-uv-cache uv run --locked pytest artifacts/mas/python-pro-trial/ -q
env UV_CACHE_DIR=/private/tmp/tds-uv-cache uv run --locked ruff check artifacts/mas/python-pro-trial/
```

On 2026-11-08, both commands exited 0: **34 tests passed**, and Ruff reported
**All checks passed!** See [pytest output](pytest.txt), [Ruff output](ruff.txt)
and [interpreter evidence](python.txt): project-local Python 3.11.16.

The cases cover valid/boundary/flat bars, invalid OHLC bounds, NaN and both
infinities in every price field, naive/non-UTC timestamps, immutable fields,
preserved object order, defensive copying, one-pass iterable input, empty series,
duplicate/decreasing timestamps and invalid series members.

The initial pytest run also passed 34 cases. The initial Ruff run found an adjacent
pair iteration preference and import grouping issue; both were corrected manually
before rerunning the two checks. [Initial Ruff output](ruff-initial.txt) is retained.

Mypy, Black and coverage measurement were not run. This verifies the isolated
sample's behavior, not the complete upstream skill or future Claude Code behavior.
