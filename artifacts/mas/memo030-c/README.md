# XD030-C actual-successor trial

Full preserved input10060raw/6200merged/3027FX; both Bi029 source routes copied byte-identically from prior full input JSON. No shared production code changed.

The event cache is memo030-four/results.json **root local event certificates only**. Its old selected routes, statuses, derived nodes and edges are never used. Cache grouping keeps earliest h for same(S,kind,gapC); local event/source semantics are unchanged, so for fixed actual T and U an earlier witness remains within the same member bounds whenever a later one is. New selection explicitly binds actual T=(b,c), and gap U=(c,e), exact gap turn c, h1<=c and h<=e. This fixes auto-confirmed derived segments. Selected witnesses are freshly regenerated from original endpoint prices with stack and independent list-reduction normalization. Event control is shared, not a wholly independent original-theory detector.

Pair-state compression proof under these **local** rules: state(a,b,c) fixes actual S=(a,b) and T=(b,c). Every earlier segment is already confirmed by its actual successor; any earlier gap has already bound its actual third candidate. No pending dependency extends beyond the fixed current T. All possible futures depend only on(a,b,c), fixed source/modes, and the next endpoint e. Therefore among same pair states, keep greatest confirmed-prefix count for a fixed earliest start. On extension U, finalize S only if the actual pair/triple predicate passes; advance to(b,c,e), count+1. At termination only no-gap/direct can confirm S without U; a gap requires selected actual U. T/U remain explicit unconfirmed evidence tail. Cost may be large; budget3million record updates, exceeded budget raises. First weak/weak attempt exceeded1million; raised explicitly and completed1156678updates, no pruning.

Results SS52/SW56/WS78/WW87 confirmedsegments. First3finishFX2892,lastFX2933. Max confirmed segment33pens; oldFX2141→2978 derived segment absent. This does not prove every new line follows all original Chan exceptions. Complex absorption/fixed inclusion/guards need further review.

Tests:120deterministic random12pen inputs (60×2modes), full-chain endpoint enumeration versus pairDP objective; selected273witnesses fresh-replayed and exactactualS/T/U/Shapechecked. Fullinput normalizer/cache source hashes recorded below. No claim of exhaustive full-dataset paths or independent complete detector. Plot source coverage per combination and native ID checks in charts/coverage.json and charts/render.json.

Reproduce:
```
.venv/bin/python artifacts/mas/memo030-c/run.py
.venv/bin/pytest -q artifacts/mas/memo030-c/test_engine.py
.venv/bin/python artifacts/mas/memo030-c/prepare_plots.py
.venv/bin/python artifacts/mas/memo030-c/verify.py
.venv/bin/python artifacts/mas/memo030-c/plot.py
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/memo030-c/charts/render.swift artifacts/mas/memo030-c/charts
.venv/bin/python artifacts/mas/memo030-c/align.py
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/memo030-c/charts/render.swift artifacts/mas/memo030-c/compact-sources
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/memo030-c/comparison/compact-atlas.swift artifacts/mas/memo030-c
.venv/bin/python artifacts/mas/memo030-c/charts/build_index.py
```

32individualPNG/HTML plus8compactcomparisons, same page x/y scales. Purple=all confirmed segments; graydashed=unconfirmed evidence tail. Allremaining uncovered data stays open. No orange derived-status category in C.
