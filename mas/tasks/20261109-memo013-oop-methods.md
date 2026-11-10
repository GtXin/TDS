# Memo013 OOP public methods
## Task
- **ID:** 20261109-memo013-oop-methods
- **Goal:** Make public CSV and plot operations discoverable as class methods and update003 cohesively for the user’s OOP-heavy requirement.
- **Inputs:** Current memo009 class/component principles, memo013, raw/CSV/plot code and existing provenance contract.
- **Allowed changes:** KlineTSeries methods/context field in src/chanlab/algo/kline.py; legacy adapter bridging in src/chanlab/data/kline_csv.py; new tests/test_kline_series_io.py; active sample generator/README/verification; backed-up memo013; task/memory/log. No dataset/config/dependency/merged class edits; frozen comparison/history untouched.
- **Acceptance checks:** Factory returns KlineTSeries with immutable owned provenance; object CSV roundtrip (full10060 rows),validation/alias/context guards,optional plotting absent case,backward compatibility,subclass construction/hashability; original regressions,typing/Ruff/Black and coherent examples/member tables/images.
- **Assignment:** Implementation author owns two source files only; independent test author owns new test file only; root owns docs/artifacts/records; read-only reviewer audits design/integration. No simultaneous writes to same paths.
- **Status:** done
## Result and handoff
- **Outcome:** Implemented object-centered read_csv/write_csv/plot API; two domain classes retained. KlineTSeries owns klines and immutable context, with8 main methods. Source/data/images/configuration and legacy call compatibility verified.
- **Evidence:** This task and forthcoming tests/source/memo diff.
- **Blockers:** none established.
- **Next action:** none for this request. Raw ChanTable/DataFrame conversions remain separately deferred.
## Exact Python Pro request (verbatim)
```text
$python-pro
Refactor memo013 to a class-centered public API: KlineTSeries.read_csv(path, context_path=None) is a classmethod returning a series, and series.write_csv(path, context_path=None) writes the series with its owned provenance; series.plot remains the rendering method. Add immutable snapshot context:Mapping[str,str] as a second KlineTSeries field with optional keyword-only constructor context=None, validating nonblank string keys/string values and preserving current series behavior/hashability. Delegate parsing/rendering to existing modules with lazy imports; keep legacy function signatures compatible. Legacy read returns series plus the same owned context; legacy write with context=None uses series.context to prevent silent metadata loss, explicit context remains supported. Preserve two domain classes, raw data, schemas, plot behavior, existing unrelated source and frozen artifacts. Own only src/chanlab/algo/kline.py and src/chanlab/data/kline_csv.py; root owns independent tests/docs/logs. Read installed Python Pro and relevant references. Use typed synchronous APIs, no dependency/config changes; report actual checks and limitations.
```

## Implementation checkpoint
- Author implemented the2owned source files and reports211 existing regression cases pass plus smoke for context copy/freeze/equality/hash,subclass factory,legacy identity/default/override semantics. Scoped strict mypy --follow-imports=silent passes2owned files; broad check follows existing ChanTable→merged modules and reports6 environment-specific optional Plotly ignore-code mismatches outside owned files,not modified. Ruff ownedfiles passes.
- Root migrated active sample generator to KlineTSeries.read_csv/series.context and artifact README to method-based usage. No plot/image regeneration needed for unchanged rendering/data.
- Independent source review and new OOP acceptance tests in progress.

## Final results and handoff
- Root independently ran233 regression cases (all passed); new OOP file22cases passed.150-case core/plot/OOP coverage run passed;94% statement coverage (247 statements,15 missed).
- Ruff allsrc/tests/generator/methoddemo passed. Black initially required formatting the new testfile; formatted and final5-file check passed. Scoped strict mypy2ownedfiles passed with --follow-imports=silent; unfiltered import diagnostics in unrelated merged modules retained in checkpoint,not changed or claimed clean.
- Full10060-row method-only read→write→read preserves object equality,9 provenance entries,UTC/numerics and original export hashes. Method-based plotting trace values equal source. Pre-task data/config/image hashes unchanged; class count2,9 Kline fields,2series fields,8mainseries methods verified via dataclass/AST/signature inspection.
- Independent source/design review passed context immutability/hash/equality,Self factory,lazycycle-safe delegation,legacy identity/default/override and downstream source references.
- Backed up013 before cohesive plan/002.h/003/member/method/example edits. Both current memo examples executed successfully; all table columns/links and3 existing picture embeds checked. git diff --check passed. Active sample generator/README use class methods; old frozen comparisons/history preserved.
- Evidence:artifacts/mas/kline-oop/verification.json,method-verification.json,coverage.json,verify_methods.py and roundtrip/; exact request retained above/python-pro-request.txt.
