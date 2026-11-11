# Updated open-tail algorithm tree

Only memo020002.a and003 were revised. Ordinary extension/reversal failures keep the working state and read the next fractal, including stronger failed extensions. FinalR only appends; EOF returns pending work and unresolved ranges without submitting the last stroke. The original004 note/prompt and all archived/source appendices are unchanged.

`section-002a.md` and `section-003.md` are the exact reviewed/saved sections. `verification.json` records the full pre-edit backup, hashes, scope preservation,34 resolved local links, goto checks and7 protected file hashes. Independent review required two fixes beforePASS: initialize cursor0 for no-fractal inputs, and explicitly continue2.2 after initializing the first newly appended fractal.

`replay.py` is an isolated processed-interval/fractal/state model, not the production Bi/API or raw-market pipeline. It checks8 fresh inputs(normal, open-tail, equal-start/end, zero/single-fractal and two price reflections),4 continuation scenarios and one changed-merged-prefix rejection:15 successful scans and one rejected scan. Rprefix immutability and noEOF finalization are checked at every step. The input/source-context compatibility requirement is a documented contract; no connected production source-object handling is tested here.

Results: normal19bar input produces final5→13 and pending13→17. The21bar example reads centers1,5,9,11,15,19 and returns final1→5, pending5→9 normally. Its29bar append also reads both new fractals without changing prior final output. These outcomes do not prove future completion, all-route coverage or canonical confirmation.

Reproduce the isolated replay from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python artifacts/mas/bi-open-tail-tree/replay.py
```

No028, production or test changes; no broad regression or Monte Carlo run.
