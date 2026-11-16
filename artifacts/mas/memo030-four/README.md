# XD030-B four-mode full data run

Input: all10060raw/6200merged/3027completeFX, copied exact JSON exports from memo030-full/input. Source provenance/hashes/environment in input/summary.json. One global solve for each Bi distance × XD mode; display windows never restart selection.

Modes: bi-strong_xd-strong, bi-strong_xd-weak, bi-weak_xd-strong, bi-weak_xd-weak. The first mode controls upstream fractal-center minimum gap4/3; second applies7a/7b to every main segment, derived segment and certificate support interval. Strict same-direction comparison with firstpen endpoint in XDstrong; XDweak removes only this extra predicate. Direct071 branch still requires its own breakthrough.

Implementation: local.py newly enumerates feature events after earlier failed events, calls historical source-preserving normalization primitives only, never historical first-candidate selector. Candidate outputs compared using two distinct normalization implementations (stack versus full-list reduction); event-control logic is shared, so this is NOT an independent complete recognition algorithm. Saved graph is additionally checked by reverse objective recursion and direct mode/dependency checks.

Continuation dominance: after comparing every raw certificate, group by(start,end,kind,C-if-gap). Keep the earliest h; an earlier watermark admits a superset of later-watermark successor endpoints, with identical geometry/count/root role. Gap derived geometry and parent group remain identical. Therefore a removed certificate cannot improve earliest-start/latest-end/max-count objective under these finite graph rules. This is objective-preserving dominance, not equivalence of all original-theory future contexts. Counts before/after saved. No arbitrary cap or silent pruning. Full certificates reproducible from local.py.

Reproduce from repository root:
```
.venv/bin/python artifacts/mas/memo030-four/run.py
.venv/bin/pytest -q artifacts/mas/memo030-four/test_local.py
.venv/bin/python artifacts/mas/memo030-four/plot.py
swift -module-cache-path /tmp/tds-swift-module-cache artifacts/mas/memo030-four/charts/render.swift artifacts/mas/memo030-four/charts
.venv/bin/python artifacts/mas/memo030-four/verify.py
```

The four results are trial profile outcomes. Complex absorption, skipped interior completion boundaries, fixed-direction inclusion and full original-author equivalence remain unproved. Strong mode on all supports is a project convention. No production implementation or permanent-confirmation claim.
