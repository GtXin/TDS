# Memo019 section002.a verification

Scope: documentation design using Computer Scientist1.0.0. No production detector,
CC engine, dataset, or project dependency was changed or executed for this task.

- `section002a.md`: exact saved section, aligned with memo009/015/019/026.
- `protected_before.json`: task-start hashes; only memo019 is an allowed change.
- `edit.json`: initial byte-preserving backup, follow-up backup and memo hashes.
- `verify.py`: outside-section preservation, backups, 8/6 fields, tree targets,
  local links, Markdown tables/fence, index and protected-file checks.
- `verification.json`: actual check results, including a separate finite arithmetic
  model comparing direction changes with the four strict extrema inequalities.

Run from the repository root:

```sh
python3 artifacts/mas/memo019-algorithm-tree/verify.py
git diff --check
```

The finite model covers 5,188 valid small sequences and 14,166 windows, plus raw
anchor zero/single/repeated matches and the distinction from display placement.
These are design checks, not tests of an implemented Fenxing detector or a general
proof. Same-price anchor selection and confirmation remain explicit open choices.
Task/review record: `mas/tasks/20261109-memo019-algorithm-tree.md`.

Current prose simplification: `essential_verification.json` records the later scoped
edit, byte-identical numbered tree and backups. The original `verify.py` and
`verification.json` are tied to the earlier full draft in `section002a.md`; they
remain historical design evidence rather than a current-document checksum check.
